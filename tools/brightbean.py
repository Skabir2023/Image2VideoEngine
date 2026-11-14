#!/usr/bin/env python3
"""BrightBean client for video: upload a film, make the post, book the slot.

Only what the scheduler needs, and only the REST API (the same BrightBean
account also exposes an MCP server; both front the same backend, and the API is
what a cron job or a shell command can call unattended).

The key is read from ``BRIGHTBEAN_API_KEY`` — set it in the engine's ``.env`` or
in ``~/.env_brightbean`` (``BRIGHTBEAN_API_KEY=...``), never in a project folder.

    import brightbean
    key = brightbean.get_key()
    account = brightbean.resolve_account(key, "Vintage Motor House")
    asset = brightbean.upload_video(key, Path("film.mp4"))
    post = brightbean.create_post(key, account["id"], caption, asset)
    brightbean.schedule_post(key, post, when)
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = os.getenv("BRIGHTBEAN_BASE", "https://api-platform.brightbean.xyz/api/v1")
KEY_ENV = "BRIGHTBEAN_API_KEY"
ENGINE = Path(__file__).resolve().parents[1]

USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36")

VIDEO_TYPES = {
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".webm": "video/webm",
    ".m4v": "video/x-m4v",
}


# -- config --------------------------------------------------------------
def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip().strip('"').strip("'")
        if name and name not in os.environ:
            os.environ[name] = value


def get_key() -> str:
    _load_env_file(ENGINE / ".env")
    _load_env_file(Path.home() / ".env_brightbean")
    key = os.getenv(KEY_ENV, "").strip()
    if not key:
        raise SystemExit(
            "Missing BRIGHTBEAN_API_KEY. Put 'BRIGHTBEAN_API_KEY=...' in %s/.env or "
            "~/.env_brightbean." % ENGINE)
    return key


# -- transport -----------------------------------------------------------
def http(method, url, headers=None, data=None, timeout=300):
    merged = {"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"}
    merged.update(headers or {})
    request = urllib.request.Request(url, data=data, method=method, headers=merged)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, dict(response.headers), response.read()
    except urllib.error.HTTPError as error:
        return error.code, dict(error.headers), error.read()


def _header(headers, name):
    for key, value in headers.items():
        if key.lower() == name.lower():
            return value
    return ""


def api(method, path, key, body=None, idempotency=None):
    headers = {"Authorization": "Bearer " + key, "Accept": "application/json"}
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if idempotency:
        headers["Idempotency-Key"] = idempotency
    status, _, raw = http(method, BASE + path, headers, data)
    text = raw.decode("utf-8", errors="replace")
    if status >= 300:
        raise RuntimeError("%s %s -> %s %s" % (method, path, status, text[:600]))
    return json.loads(text) if text.strip() else {}


def unwrap(payload):
    if isinstance(payload, dict):
        if isinstance(payload.get("data"), dict):
            return payload["data"]
        if isinstance(payload.get("post"), dict):
            return payload["post"]
    return payload


def _items(payload):
    data = payload.get("data", payload) if isinstance(payload, dict) else payload
    if isinstance(data, dict):
        data = data.get("items", data.get("posts", data.get("accounts", [])))
    return list(data or [])


# -- accounts ------------------------------------------------------------
def accounts(key):
    return _items(api("GET", "/accounts", key))


def resolve_account(key, name):
    """The one connected channel whose handle matches *name* (exact, then partial)."""
    listing = accounts(key)
    exact = [a for a in listing if str(a.get("handle", "")).lower() == name.lower()]
    if len(exact) == 1:
        return exact[0]
    partial = [a for a in listing if name.lower() in str(a.get("handle", "")).lower()]
    if len(partial) == 1:
        return partial[0]
    known = ", ".join("%s (%s)" % (a.get("handle"), a.get("platform")) for a in listing)
    if not partial:
        raise SystemExit("No BrightBean channel matches %r. Available: %s" % (name, known))
    raise SystemExit("Ambiguous channel %r: %s" % (
        name, ", ".join("%s (%s)" % (a.get("handle"), a.get("platform")) for a in partial)))


# -- media ---------------------------------------------------------------
def _content_type(path: Path) -> str:
    return VIDEO_TYPES.get(path.suffix.lower(), "video/mp4")


def upload_video(key, path: Path, alt_text: str = "") -> str:
    """Multipart upload straight from disk; returns the media asset id."""
    size = path.stat().st_size
    nonce = hashlib.sha256(os.urandom(16)).hexdigest()[:32]
    body = {"mediaType": "video", "sizeBytes": size}
    if alt_text:
        body["altText"] = alt_text[:1000]
    init = unwrap(api("POST", "/media/uploads", key, body, nonce + "-init"))
    asset_id = init["mediaAssetId"]
    part_size = int(init.get("partSize") or size)
    part_count = int(init.get("partCount") or 1)
    urls = init.get("urls") or []
    parts = []
    with path.open("rb") as handle:
        for item in urls:
            number = int(item.get("partNumber", 1)) if isinstance(item, dict) else 1
            url = item.get("url") if isinstance(item, dict) else item
            if part_count == 1:
                handle.seek(0)
                chunk = handle.read()
            else:
                handle.seek((number - 1) * part_size)
                chunk = handle.read(part_size)
            status, headers, raw = http("PUT", url, {"Content-Type": _content_type(path)}, chunk)
            if status >= 300:
                raise RuntimeError("upload part %s -> %s %s" % (number, status, raw[:300]))
            etag = _header(headers, "ETag").strip().strip('"') or hashlib.md5(chunk).hexdigest()
            parts.append({"etag": etag, "partNumber": number})
    if len(parts) != part_count:
        raise RuntimeError("expected %d upload parts, got %d" % (part_count, len(parts)))
    api("POST", "/media/uploads/%s/complete" % asset_id, key, {"parts": parts}, nonce + "-complete")
    return asset_id


# -- posts ---------------------------------------------------------------
def find_post_by_caption(key, account_id, caption):
    """A draft/scheduled post already carrying this caption on this channel.

    A retried upload produces a new media asset, so replaying the old idempotency
    key fails; matching the caption lets the retry adopt the earlier post instead
    of scheduling the film twice.
    """
    wanted = caption.strip()
    if not wanted:
        return None
    for status in ("draft", "scheduled"):
        for item in _items(api("GET", "/posts?status=%s&limit=100" % status, key)):
            if (item.get("caption") or "").strip() != wanted:
                continue
            channels = item.get("channels") or []
            if account_id and account_id not in [c.get("accountId") for c in channels]:
                continue
            return item
    return None


def create_post(key, account_id, caption, asset_id, idempotency=None, title=""):
    body = {"accounts": [account_id], "caption": caption, "mediaAssetIds": [asset_id]}
    if title:
        body["title"] = title
    if not idempotency:
        idempotency = hashlib.sha256((caption + "|" + asset_id).encode()).hexdigest()[:32]
    last = None
    for _ in range(8):
        try:
            return unwrap(api("POST", "/posts", key, body, idempotency))["id"]
        except RuntimeError as error:
            last = error
            if "idempotency_mismatch" in str(error):
                existing = find_post_by_caption(key, account_id, caption)
                if existing is not None:
                    return existing["id"]
            if "haven't finished" not in str(error):
                raise
            time.sleep(3)
    raise last


def schedule_post(key, post_id, when):
    response = unwrap(api("POST", "/posts/%s/schedule" % post_id, key, {
        "mode": "at",
        "at": when.isoformat(timespec="seconds"),
        "timezone": "UTC",
    }))
    status = response.get("status")
    if status and status != "scheduled":
        raise RuntimeError("post %s did not schedule (status=%s)" % (post_id, status))
    return response


def post(key, post_id):
    return unwrap(api("GET", "/posts/%s" % post_id, key))


def latest_booked(key, account_id=None):
    """Newest scheduledAt on the account; only used when the ledger is empty."""
    latest = None
    cursor = None
    while True:
        path = "/posts?status=scheduled&limit=100" + ("&cursor=%s" % cursor if cursor else "")
        page = api("GET", path, key)
        body = page.get("data", page)
        items = body.get("items", body.get("posts", [])) if isinstance(body, dict) else body
        for item in items or []:
            for channel in item.get("channels") or []:
                if account_id and channel.get("accountId") != account_id:
                    continue
                stamp = parse_utc(channel.get("scheduledAt"))
                if stamp and (latest is None or stamp > latest):
                    latest = stamp
        cursor = page.get("nextCursor") or (body.get("nextCursor") if isinstance(body, dict) else None)
        if not cursor:
            return latest


def parse_utc(value):
    from datetime import datetime, timezone
    if not value:
        return None
    try:
        stamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return stamp if stamp.tzinfo else stamp.replace(tzinfo=timezone.utc)
