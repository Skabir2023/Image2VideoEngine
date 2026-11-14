#!/usr/bin/env python3
"""Queue finished films for a page, book them on BrightBean, and keep the books.

Workflow this implements (one BrightBean page, one folder per film, no copies):

    video-projects/<page>/                 <- the channel, e.g. vintage-motor-house
      data.csv         the queue: one row per film waiting to go out
      uploaded.csv     the ledger: every film whose slot was booked
      *.xlsx           the page's workbooks (Car List, Tracker)
      <film>/          one film: meta.json, renders/, audio/, compositions/, plan/
                        (point the commands at the film; the CSVs are the page's)

A row carries everything the post needs — title, description, hashtags, click-
ready caption — and the path of the finished film in `video`. Nothing is copied
and nothing is moved: `queue` points the row at the render in `renders/`, and
`schedule` uploads straight from there. Only the row travels, from data.csv to
uploaded.csv, after its slot is booked.

No film is uploaded twice. Every row records `video_sha`, a fingerprint of the
file, and `schedule` refuses a row whose fingerprint is already booked — before
anything is sent — so a re-run, a re-queued render or a second entry for the
same cut cannot post the same film again. A re-rendered film has a different
fingerprint and is allowed through, and an interrupted run resumes its own post
by caption instead of uploading again.

Commands (run from the engine root):

    pick      the next cars to film, from the page's Car List (read-only)
    queue     add a finished film to data.csv with its title/description/hashtags
    schedule  upload each queued film, book a slot, move the row, update Excel
    status    what is queued, what is booked, when the next slot is
    sync      refresh booked films from BrightBean (published? url?) + Excel

Examples:

    python3 tools/publish.py pick video-projects/vintage-motor-house
    python3 tools/publish.py queue video-projects/vintage-motor-house/1969-ford-mustang-boss-429 \
        --title "The Rarest 1969 Ford Mustang Boss 429 Ever Made" \
        --description "Ford built just 1,359 of them, and every one carried a NASCAR engine with \
plates. The 429 was so wide that Ford had to rework the shock towers by hand. Today a good one \
costs more than a house. Would you take it over a Hemi Cuda?" \
        --hashtags "#Ford #Mustang #ClassicCars #Boss429 #1969" \
        --car "1969 Ford Mustang Boss 429" --angle "Price / Rarity"

    python3 tools/publish.py schedule video-projects/vintage-motor-house/1969-ford-mustang-boss-429 --dry-run
    python3 tools/publish.py schedule video-projects/vintage-motor-house/1969-ford-mustang-boss-429
    python3 tools/publish.py sync video-projects/vintage-motor-house/1969-ford-mustang-boss-429

Slots: the first film goes out 60-120 minutes from now (or 4-5 hours after the
page's last booked slot), and each following film is 4-5 hours after the one
before, which is the cadence the image engine uses. `--interval` overrides the
gap with a fixed number of minutes; `--start-at` books an absolute first slot.

Re-running is safe: a row whose film is already uploaded resumes at its post
instead of uploading twice, and a row already booked is never touched.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import re
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import brightbean  # noqa: E402
import caption as caption_rules  # noqa: E402
from excel import Workbook  # noqa: E402

ENGINE = Path(__file__).resolve().parents[1]

# One row = one film. `video` is the finished render where it lies (no copy),
# `video_sha` is its fingerprint and what stops a double upload; `caption` is
# what Facebook receives (title, blank line, description, blank line, hashtags)
# and the three parts are kept so the text can be edited without re-parsing it.
COLUMNS = [
    "id", "video", "video_sha", "status", "car", "angle", "title", "description",
    "hashtags", "caption", "duration_s", "fps", "rendered_at", "scheduled_at",
    "published_at", "post_id", "post_url", "error",
]

DONE = ("scheduled", "published")


# -- small helpers -------------------------------------------------------
def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso(stamp: datetime) -> str:
    return stamp.astimezone(timezone.utc).isoformat(timespec="seconds")


def read_rows(path: Path):
    if not path.exists():
        return [], []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        header = [c for c in (reader.fieldnames or []) if c]
        rows = [{k: (v or "") for k, v in row.items() if k}
                for row in reader]
    return header, rows


def write_rows(path: Path, header, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    with temp.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=header, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({c: row.get(c, "") for c in header})
    os.replace(temp, path)


def append_row(path: Path, header, row) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=header, extrasaction="ignore")
        writer.writerow({c: row.get(c, "") for c in header})


def parse_utc(value):
    return brightbean.parse_utc(value)


def fingerprint(path: Path) -> str:
    """Short content hash of a film: the same bytes never get posted twice."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()[:16]


# -- the workbooks -------------------------------------------------------
class Workbooks:
    """The project's Tracker and Car List, updated in place and saved once."""

    def __init__(self, project: "Project"):
        self.tracker = None
        self.car_list = None
        files = [p for d in (project.path, project.page) for p in sorted(d.glob("*.xlsx"))
                 if not p.name.startswith("~$")]
        for path in files:
            name = path.name.lower()
            if "tracker" in name:
                self.tracker = Workbook(path)
            elif "car" in name and "list" in name:
                self.car_list = Workbook(path)

    @staticmethod
    def _column(wb: Workbook, sheet: str, header_text: str) -> str:
        if wb is None:
            return ""
        rows = wb.rows(sheet)
        if not rows:
            return ""
        wanted = header_text.lower()
        for column, value in rows[0][1].items():
            if (value or "").strip().lower() == wanted:
                return column
        for column, value in rows[0][1].items():
            if wanted in (value or "").strip().lower():
                return column
        return ""

    @staticmethod
    def _sheet(wb: Workbook, name: str) -> str:
        if wb is None:
            return ""
        names = wb.sheet_names()
        for candidate in names:
            if candidate.lower() == name.lower():
                return candidate
        return names[0] if names else ""

    def mark(self, row, state: str) -> list[str]:
        """Record a scheduled/published film in both workbooks. Returns notes."""
        notes: list[str] = []
        car = (row.get("car") or "").strip()
        stamp = parse_utc(row.get("published_at") or row.get("scheduled_at"))
        day = stamp.strftime("%Y-%m-%d") if stamp else ""
        angle = (row.get("angle") or "").strip()
        if not car:
            return ["no car on the row — workbooks left alone"]

        if self.tracker is not None:
            sheet = self._sheet(self.tracker, "Tracker")
            car_col = self._column(self.tracker, sheet, "car (year make model)") or "C"
            hits = self.tracker.find(sheet, car_col, car)
            if not hits:
                notes.append("no Tracker row for %r — add it by hand" % car)
            for number in hits:
                date_col = self._column(self.tracker, sheet, "date") or "A"
                script_col = self._column(self.tracker, sheet, "script done") or "F"
                images_col = self._column(self.tracker, sheet, "images done") or "G"
                posted_col = self._column(self.tracker, sheet, "posted") or "H"
                if day:
                    existing = dict(self.tracker.rows(sheet)).get(number, {}).get(date_col, "")
                    if not existing.strip():
                        self.tracker.set(sheet, "%s%d" % (date_col, number), day)
                self.tracker.set(sheet, "%s%d" % (script_col, number), "Yes")
                self.tracker.set(sheet, "%s%d" % (images_col, number), "Yes")
                self.tracker.set(sheet, "%s%d" % (posted_col, number),
                                 "Yes" if state == "published" else "Scheduled")
                notes.append("Tracker row %d -> %s" % (number, state))

        if self.car_list is not None:
            sheet = self._sheet(self.car_list, "Car List")
            year_col = self._column(self.car_list, sheet, "year") or "B"
            brand_col = self._column(self.car_list, sheet, "brand") or "C"
            model_col = self._column(self.car_list, sheet, "model") or "D"
            used_col = self._column(self.car_list, sheet, "used") or "E"
            angle_col = self._column(self.car_list, sheet, "angle used") or "F"
            date_col = self._column(self.car_list, sheet, "date used") or "G"
            match = re.match(r"(\d{4})\s+(\S+)\s+(.+)$", car)
            if not match:
                notes.append("could not read year/make/model from %r" % car)
            else:
                year, brand, model = match.group(1), match.group(2), match.group(3).strip().lower()
                # Exact model first: "Mustang Boss 429" must not land on the
                # 1969 Boss 302 sitting a few rows above it. Among repeats of the
                # same car the newest unused row wins, which is the row a repeat
                # after 90 days is supposed to use.
                exact, loose = [], []
                for number, values in self.car_list.rows(sheet)[1:]:
                    if (values.get(year_col, "").strip() != year
                            or values.get(brand_col, "").strip().lower() != brand.lower()):
                        continue
                    text = (values.get(model_col, "") or "").strip().lower()
                    if not text:
                        continue
                    if text == model:
                        exact.append((number, values))
                    elif text.startswith(model):
                        loose.append((number, values))

                def unused(items):
                    return [i for i in items if (i[1].get(used_col) or "").strip().lower() != "yes"]

                pool = unused(exact) or exact or unused(loose) or loose
                target = max(pool, key=lambda item: item[0])[0] if pool else None
                if target is None:
                    notes.append("no Car List row for %r" % car)
                else:
                    self.car_list.set(sheet, "%s%d" % (used_col, target), "Yes")
                    if angle:
                        self.car_list.set(sheet, "%s%d" % (angle_col, target), angle)
                    if day:
                        self.car_list.set(sheet, "%s%d" % (date_col, target), day)
                    notes.append("Car List row %d -> used" % target)

        return notes

    def save(self) -> None:
        for wb in (self.tracker, self.car_list):
            if wb is not None:
                wb.save()


# -- the project ---------------------------------------------------------
class Project:
    def __init__(self, target: str):
        path = Path(target)
        if not path.is_absolute():
            path = (ENGINE / path)
        if not (path / "meta.json").exists():
            raise SystemExit("No meta.json in %s — pass video-projects/<page>/<film>." % path)
        self.path = path.resolve()
        self.meta = json.loads((self.path / "meta.json").read_text(encoding="utf-8"))
        social = self.meta.get("social") or {}
        self.platform = social.get("platform") or "facebook"
        self.account = social.get("account") or self.meta.get("project") or self.path.name
        self.slug = self.meta.get("slug") or self.path.name
        # video-projects/<page>/<film>. The film owns its render and its meta; the page owns
        # the queue, the ledger and the workbooks, because they are what gets posted next.
        page = self.path.parent
        self.page = self.path if page.name == "video-projects" else page
        self.data_csv = self.page / "data.csv"
        self.uploaded_csv = self.page / "uploaded.csv"

    def ensure(self) -> None:
        for path in (self.data_csv, self.uploaded_csv):
            if not path.exists():
                write_rows(path, COLUMNS, [])
            else:
                # keep the file's own header, but never lose a column we rely on
                header, rows = read_rows(path)
                missing = [c for c in COLUMNS if c not in header]
                if missing:
                    write_rows(path, header + missing, rows)

    def render(self) -> Path:
        name = self.meta.get("output") or ""
        return self.path / "renders" / (name + ".mp4")

    def last_booked(self):
        _, rows = read_rows(self.uploaded_csv)
        stamps = [t for t in (parse_utc(r.get("scheduled_at")) for r in rows) if t]
        return max(stamps) if stamps else None


# -- queue ---------------------------------------------------------------
def queue(project: Project, video=None, title="", description="", hashtags="",
          car="", angle="", caption_file=None, caption_score=None,
          force=False) -> dict:
    project.ensure()
    if caption_file:
        blocks = [b.strip() for b in Path(caption_file).read_text(encoding="utf-8").split("\n\n") if b.strip()]
        if len(blocks) >= 2:
            title = title or blocks[0]
            description = description or (blocks[1] if len(blocks) > 1 else "")
            hashtags = hashtags or (blocks[2] if len(blocks) > 2 else "")

    title = " ".join(title.split())
    description = " ".join(description.split())
    hashtags = " ".join(hashtags.split())
    if not title:
        raise SystemExit("Need --title (or a caption file whose first block is the title).")
    caption = "\n\n".join(part for part in (title, description, hashtags) if part)

    # The caption contract, checked before a row exists. The brain scores the
    # caption (META PROMPT.md); this enforces the counts, the bans, the naming
    # rule and the 80 floor, so a thin caption cannot reach the page. --force
    # queues anyway, and says so in the row's `error` column.
    report = caption_rules.report_for(title, description, hashtags,
                                      caption_score, car)
    print(report.render())
    if not report.passed and not force:
        raise SystemExit("Caption did not pass: rewrite it, or queue with --force.")

    source = Path(video) if video else project.render()
    source = source if source.is_absolute() else ENGINE / source
    if not source.is_file():
        raise SystemExit("No film at %s — render it first, or pass --video." % source)
    source = source.resolve()
    sha = fingerprint(source)

    _, queued = read_rows(project.data_csv)
    _, booked = read_rows(project.uploaded_csv)
    for row in queued + booked:
        saved = Path(row["video"]) if row.get("video") else None
        same_file = (row.get("video_sha") or "") == sha or (
            saved is not None and saved.exists() and saved.resolve() == source)
        if same_file:
            raise SystemExit("That exact film is already %s as %r (row %s) — nothing to do." % (
                row.get("status") or "queued", row.get("title") or row.get("id"), row.get("id")))
        if (row.get("caption") or "").strip() == caption:
            raise SystemExit("That caption is already in %s (row %s, %s)." % (
                project.slug, row.get("id"), row.get("status")))

    row_id = uuid.uuid4().hex[:12]
    row = {
        "id": row_id,
        "video": str(source),
        "video_sha": sha,
        "caption": caption,
        "status": "ready",
        "car": car.strip(),
        "angle": angle.strip(),
        "title": title,
        "description": description,
        "hashtags": hashtags,
        "duration_s": str(project.meta.get("duration", "")),
        "fps": str(project.meta.get("fps", "")),
        "rendered_at": iso(datetime.fromtimestamp(source.stat().st_mtime, timezone.utc)),
    }
    if not report.passed:
        row["error"] = "caption forced past the check: " + "; ".join(report.failures)[:300]
        print("  caption: FORCED past %d failed check(s) — recorded in `error`"
              % len(report.failures))
    header, rows = read_rows(project.data_csv)
    header = header or list(COLUMNS)
    append_row(project.data_csv, header, row)
    print("queued %s" % source.name)
    print("  car   : %s%s" % (row["car"] or "(none)",
                              " / " + row["angle"] if row["angle"] else ""))
    print("  title : %s" % title)
    print("  file  : %s" % source)
    print("  id    : %s" % row_id)
    return row


# -- slots ---------------------------------------------------------------
def first_slot(project: Project, key, account_id, start_at=None, start_delay=None,
               start_min=60, start_max=120, gap_min=240, gap_max=300, interval=None):
    now = utcnow()
    if start_at:
        start = parse_utc(start_at)
        if start is None:
            raise SystemExit("--start-at is not an ISO time: %r" % start_at)
        return start, "explicit"
    if start_delay is not None:
        return now + timedelta(minutes=start_delay), "delay"
    last = project.last_booked() or brightbean.latest_booked(key, account_id)
    delay = random.randint(start_min, start_max) + random.randint(0, 59) / 60.0
    if last is None:
        return now + timedelta(minutes=delay), "first film on the page"
    gap = interval if interval else max(random.randint(gap_min, gap_max)
                                        + random.randint(0, 59) / 60.0, 240)
    start = last + timedelta(minutes=gap)
    if start <= now:
        return now + timedelta(minutes=max(delay, 240 if not interval else interval)), "last slot passed"
    return start, "after %s" % last.strftime("%d %b %H:%M UTC")


def next_slot(when: datetime, interval, gap_min, gap_max) -> datetime:
    if interval:
        return when + timedelta(minutes=interval)
    gap = max(random.randint(gap_min, gap_max) + random.randint(0, 59) / 60.0, 240)
    return when + timedelta(minutes=gap)


# -- schedule ------------------------------------------------------------
def schedule(project: Project, limit=None, start_at=None, start_delay=None,
             start_min=60, start_max=120, gap_min=240, gap_max=300, interval=None,
             dry_run=False, excel=True) -> tuple[int, int]:
    project.ensure()
    key = brightbean.get_key()
    account = brightbean.resolve_account(key, project.account)
    if account.get("status") != "connected":
        raise SystemExit("Channel %r is not connected (%s)." % (
            account.get("handle"), account.get("status")))
    account_id = account["id"]
    print("channel: %s (%s) %s" % (account.get("handle"), account.get("platform"), account_id))

    header, rows = read_rows(project.data_csv)
    header = header or list(COLUMNS)
    pending = [r for r in rows if (r.get("status") or "") not in DONE]
    if limit:
        pending = pending[:limit]
    if not pending:
        print("data.csv has no films waiting.")
        return 0, 0

    when, reason = first_slot(project, key, account_id, start_at, start_delay,
                              start_min, start_max, gap_min, gap_max, interval)
    print("first slot: %s UTC (%s)" % (when.strftime("%Y-%m-%d %H:%M"), reason))

    book = Workbooks(project) if excel else None
    _, booked_rows = read_rows(project.uploaded_csv)
    booked_shas = {r.get("video_sha") for r in booked_rows
                   if (r.get("video_sha") or "").strip()
                   and (r.get("status") or "") in ("scheduled", "publishing", "published")}
    done = failed = placed = 0
    for row in pending:
        path = Path(row["video"]) if row.get("video") else None
        caption = row.get("caption") or ""
        status = row.get("status") or ""
        post_id = (row.get("post_id") or "").strip()
        if not post_id and status.startswith("uploaded:"):
            post_id = status.split(":", 1)[1]
        label = row.get("title") or (path.name if path else row.get("id"))

        # The same film never goes out twice: a row whose bytes are already booked
        # is skipped before anything is uploaded, and stays queued for a human look.
        if not post_id and path and path.is_file():
            sha = row.get("video_sha") or fingerprint(path)
            if sha in booked_shas:
                earlier = next(r for r in booked_rows if r.get("video_sha") == sha)
                message = "same film already %s as %r" % (
                    earlier.get("status"), earlier.get("title") or earlier.get("id"))
                row["video_sha"] = sha
                row["error"] = message
                write_rows(project.data_csv, header, rows)
                print("  SKIP %s: %s" % (label, message))
                continue

        slot = next_slot(when, interval, gap_min, gap_max) if placed else when
        if dry_run:
            print("  [dry] %s -> %s UTC" % (label, slot.strftime("%Y-%m-%d %H:%M")))
            placed += 1
            when = slot
            continue

        try:
            if path is None or not path.is_file():
                raise RuntimeError("film missing: %s" % (path or "(no video on the row)"))
            if post_id:
                print("- resuming post %s for %s" % (post_id, label))
            else:
                existing = brightbean.find_post_by_caption(key, account_id, caption)
                if existing is not None:
                    post_id = existing["id"]
                    row["status"] = "uploaded:" + post_id
                    row["post_id"] = post_id
                    write_rows(project.data_csv, header, rows)
                    print("- adopting existing post %s (%s)" % (post_id, existing.get("status")))
                else:
                    asset = brightbean.upload_video(key, path, row.get("description", "")[:200])
                    post_id = brightbean.create_post(key, account_id, caption, asset,
                                                     title=row.get("title", ""))
                    row["status"] = "uploaded:" + post_id
                    row["post_id"] = post_id
                    write_rows(project.data_csv, header, rows)
                    print("- uploaded %s (%d MB) -> post %s" % (
                        label, path.stat().st_size // (1024 * 1024), post_id))

            brightbean.schedule_post(key, post_id, slot)
            row["scheduled_at"] = iso(slot)
            row["status"] = "scheduled"
            row["error"] = ""
            row["video"] = str(path.resolve())
            booked_shas.add(row.get("video_sha") or "")
            booked_rows.append(row)
            append_row(project.uploaded_csv, header, row)
            rows = [r for r in rows if r is not row]
            write_rows(project.data_csv, header, rows)
            if book is not None:
                for note in book.mark(row, "scheduled"):
                    print("  %s" % note)
            done += 1
            placed += 1
            when = slot
            print("  booked %s -> %s UTC" % (label, slot.strftime("%Y-%m-%d %H:%M")))
        except Exception as error:  # noqa: BLE001 - one bad film must not stop the batch
            failed += 1
            row["status"] = "failed"
            row["error"] = str(error)[:400]
            write_rows(project.data_csv, header, rows)
            print("  FAILED %s: %s" % (label, error))

    if book is not None and not dry_run and done:
        book.save()
    if dry_run:
        print("[dry] nothing uploaded, no row moved, no workbooks touched.")
        return 0, 0
    print("booked %d, failed %d, still queued %d." % (done, failed, len(rows)))
    return done, failed


# -- the car list ---------------------------------------------------------

def find_car_list(folder: Path) -> Path:
    for path in sorted(folder.glob("*.xlsx")):
        name = path.name.lower()
        if "car" in name and "list" in name and not path.name.startswith("~$"):
            return path
    raise SystemExit("No Car List workbook in %s" % folder)


def pick(target: str, count: int = 10, reuse_after: int = 90) -> None:
    """The next cars to film: never-used first, then the ones free again after 90 days."""
    folder = Path(target)
    if not folder.is_absolute():
        folder = ENGINE / folder
    folder = folder.resolve()
    if not (folder / "data.csv").exists() and (folder.parent / "data.csv").exists():
        folder = folder.parent            # pointed at a film: the page owns the Car List
    wb = Workbook(find_car_list(folder))
    sheet = next((s for s in wb.sheet_names() if "car list" in s.lower()), wb.sheet_names()[0])
    rows = wb.rows(sheet)
    if not rows:
        raise SystemExit("%s is empty" % sheet)
    head = rows[0][1]

    def column(*names: str) -> str:
        for name in names:
            for letter, value in head.items():
                if (value or "").strip().lower() == name:
                    return letter
        return ""

    year_col = column("year") or "B"
    brand_col = column("brand") or "C"
    model_col = column("model") or "D"
    used_col = column("used?", "used") or "E"
    angle_col = column("angle used", "angle") or "F"
    date_col = column("date used", "date") or "G"

    today = utcnow().date()
    fresh, again, waiting = [], [], 0
    for number, values in rows[1:]:
        year = (values.get(year_col) or "").strip()
        brand = (values.get(brand_col) or "").strip()
        if not (year and brand):
            continue
        car = " ".join(part for part in (year, brand, (values.get(model_col) or "").strip()) if part)
        if (values.get(used_col) or "").strip().lower() != "yes":
            fresh.append((number, car))
            continue
        stamp = parse_utc((values.get(date_col) or "").strip())
        days = (today - stamp.date()).days if stamp else None
        if days is not None and days >= reuse_after:
            angle = (values.get(angle_col) or "-").strip() or "-"
            again.append((number, car, stamp.date().isoformat(), days, angle))
        else:
            waiting += 1

    total = len(fresh) + len(again) + waiting
    print("%s — %d cars: %d never used, %d free again, %d in recent use." % (
        folder.name, total, len(fresh), len(again), waiting))
    if not fresh and not again:
        print("Nothing free — every car is inside its %d-day rest." % reuse_after)
        return
    if fresh:
        print("\nnext %d (mark Used? = Yes, and fill Angle + Date when you film one):" %
              min(count, len(fresh)))
        for place, (number, car) in enumerate(fresh[:count], 1):
            print("  %2d. %-46s row %d" % (place, car, number))
    if again:
        print("\nfree again — same car, DIFFERENT angle, new row at the bottom of the list:")
        for number, car, day, days, angle in again:
            print("   - %-46s last %s (%d days), was %r" % (car, day, days, angle))
def sync(project: Project, excel=True) -> int:
    project.ensure()
    key = brightbean.get_key()
    book = Workbooks(project) if excel else None
    updated = 0
    for csv_path in (project.uploaded_csv, project.data_csv):
        header, rows = read_rows(csv_path)
        if not rows:
            continue
        header = header or list(COLUMNS)
        changed = False
        for row in rows:
            post_id = (row.get("post_id") or "").strip()
            if not post_id and (row.get("status") or "").startswith("uploaded:"):
                post_id = row["status"].split(":", 1)[1]
            if not post_id:
                continue
            try:
                remote = brightbean.post(key, post_id)
            except RuntimeError as error:
                print("  %s: %s" % (post_id, error))
                continue
            state = (remote.get("status") or "").strip()
            channel = next((c for c in (remote.get("channels") or [])
                            if c.get("accountId")), {})
            url = channel.get("url") or ""
            published = channel.get("publishedAt") or remote.get("publishedAt") or ""
            mapped = {"published": "published", "partially_published": "published",
                      "publishing": "publishing", "failed": "failed",
                      "scheduled": "scheduled", "draft": "draft"}.get(state, state or row.get("status"))
            touched = False
            for column, value in (("status", mapped), ("post_id", post_id),
                                  ("post_url", url), ("published_at", published)):
                if value and (row.get(column) or "") != value:
                    row[column] = value
                    touched = True
            if mapped == "failed":
                message = (channel.get("error") or "failed")[:400]
                if row.get("error") != message:
                    row["error"] = message
                    touched = True
            if touched:
                changed = True
                updated += 1
                print("  %s -> %s%s" % (row.get("title", post_id), mapped,
                                        " " + url if url else ""))
            if book is not None and mapped == "published":
                book.mark(row, "published")
        if changed:
            write_rows(csv_path, header, rows)
    if book is not None:
        book.save()
    print("synced %d row(s)." % updated)
    return updated


# -- status --------------------------------------------------------------
def status(project: Project) -> None:
    project.ensure()
    _, queued = read_rows(project.data_csv)
    _, booked = read_rows(project.uploaded_csv)
    counts = {}
    for row in queued:
        key = (row.get("status") or "ready").split(":")[0]
        counts[key] = counts.get(key, 0) + 1
    print("%s  (%s / %s)" % (project.account, project.page.name, project.path.name))
    print("  queued %d %s" % (len(queued), counts or ""))
    print("  booked %d" % len(booked))
    last = project.last_booked()
    if last:
        print("  last slot %s UTC" % last.strftime("%Y-%m-%d %H:%M"))
    for row in queued:
        note = row.get("error") or ""
        print("    - [%s] %s  (%s)%s" % (
            row.get("status", ""), row.get("title") or row.get("id"),
            Path(row.get("video", "")).name, "  ! " + note if note else ""))
    for row in booked[-5:]:
        print("    - [%s] %s  %s" % (row.get("status", ""), row.get("title") or row.get("id"),
                                     row.get("scheduled_at", "")))


# -- cli -----------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_pick = sub.add_parser("pick", help="the next cars to film, from the Car List")
    p_pick.add_argument("page", help="video-projects/<page> (or any film inside it)")
    p_pick.add_argument("--count", type=int, default=10, help="how many to put in the batch")
    p_pick.add_argument("--reuse-after", type=int, default=90,
                        help="days before the same car may be filmed again (default 90)")

    p_queue = sub.add_parser("queue", help="add a finished film to data.csv")
    p_queue.add_argument("project")
    p_queue.add_argument("--video", help="film to queue (default: the project's finished render)")
    p_queue.add_argument("--title")
    p_queue.add_argument("--description", default="")
    p_queue.add_argument("--hashtags", default="")
    p_queue.add_argument("--car", default="", help='e.g. "1969 Ford Mustang Boss 429"')
    p_queue.add_argument("--angle", default="", help="e.g. 'Price / Rarity'")
    p_queue.add_argument("--caption-file", help="three blocks: title, description, hashtags")
    p_queue.add_argument("--caption-score", type=int,
                         help="the caption score the brain gave it (gate 80)")
    p_queue.add_argument("--force", action="store_true",
                         help="queue a caption that failed the check")

    p_sched = sub.add_parser("schedule", help="upload queued films and book their slots")
    p_sched.add_argument("project")
    p_sched.add_argument("--limit", type=int, help="book at most this many films now")
    p_sched.add_argument("--start-at", help="absolute ISO time for the first slot")
    p_sched.add_argument("--start-delay", type=float, help="minutes from now for the first slot")
    p_sched.add_argument("--start-min", type=int, default=60)
    p_sched.add_argument("--start-max", type=int, default=120)
    p_sched.add_argument("--gap-min", type=int, default=240)
    p_sched.add_argument("--gap-max", type=int, default=300)
    p_sched.add_argument("--interval", type=int, help="fixed minutes between slots")
    p_sched.add_argument("--dry-run", action="store_true", help="show the plan, change nothing")
    p_sched.add_argument("--no-excel", action="store_true", help="leave the workbooks alone")

    p_sync = sub.add_parser("sync", help="refresh statuses and links from BrightBean")
    p_sync.add_argument("project")
    p_sync.add_argument("--no-excel", action="store_true")

    p_status = sub.add_parser("status", help="what is queued and what is booked")
    p_status.add_argument("project")

    args = parser.parse_args()
    if args.command == "pick":
        pick(args.page, args.count, args.reuse_after)
        return
    project = Project(args.project)

    if args.command == "queue":
        queue(project, args.video, args.title, args.description, args.hashtags,
              args.car, args.angle, args.caption_file, args.caption_score,
              args.force)
    elif args.command == "schedule":
        done, failed = schedule(project, args.limit, args.start_at, args.start_delay,
                                args.start_min, args.start_max, args.gap_min, args.gap_max,
                                args.interval, args.dry_run, not args.no_excel)
        if failed:
            sys.exit(1)
    elif args.command == "sync":
        sync(project, not args.no_excel)
    else:
        status(project)


if __name__ == "__main__":
    main()
