#!/usr/bin/env python3
"""Shoot a film's plates: one Meta AI chat per prompt, downloaded straight into stills/.

    python3 tools/shoot_plates.py video-projects/<page>/<film>
    python3 tools/shoot_plates.py video-projects/<page>/<film> --only 04_wing.png

The prompts are the film's own: `plan/PLATES.md` holds the car identity block and a table of
`| # | File | Framing clause | Scene |`. Every prompt repeats the identity block verbatim so
the plates read as one car.

**One session for the whole film — strict.** Every plate is generated in the *same* meta.ai chat
tab: `pick_tab` opens it once, the loop sends into it and nothing closes it between plates. Never a
new chat per image, never a fresh session to make a download unambiguous — the new picture is
identified against `seen`, the image URLs already on the page. Inside the session it is one prompt
at a time: send once, wait for *that* plate, download it, then send the next. A prompt is never
re-sent because its image is late.

It drives Browser MCP in the person's signed-in **default Chrome** (where the extension lives).
A closed default window is reported as a closed window, not a missing install (PROVIDERS.md).
`eval` only works on a selected tab, so the tool picks one meta.ai tab and keeps it for the whole
shoot; commands are one line each
and eval payloads are flattened for that reason. The image is fetched the way the page would
fetch it (`download <url> --path`), falling back to a plain GET, then scaled once to 1080×1920
with lanczos — Meta AI hands back 1152×2048 (9:16), so nothing is cropped.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PREFIX = "Create one photorealistic photograph, vertical portrait 9:16: "

# Every plate is shot OUTSIDE, in a different real place. A car photographed against the same
# studio wall ten times reads as a catalogue scan; the same car on a beach, a ridge and an empty
# road reads as a car. The list is ordered so the six fixed angles each land somewhere that suits
# them (hero on a road, engine bay on a clean forecourt), and `n` chooses the location, so a
# re-shot plate goes back to the same place as the take it replaces.
SETTINGS = (
    "on a long empty road through green hills, soft morning sun",
    "on a wide open park lawn under mature trees, warm afternoon light",
    "on a packed-sand beach track with the sea and surf behind it, low bright sun",
    "on a clean concrete forecourt under a deep blue sky, bright midday sun",
    "on a quiet boulevard lined with palms, bright late-afternoon sun",
    "in a gravel lay-by at the edge of a pine forest, dappled sunlight",
    "on a mountain overlook above a wide valley, clear evening light",
    "on a coastal road with the ocean behind it, golden-hour glare",
    "on a winding mountain pass with rock faces and pines, crisp cool light",
    "on a quiet lakeside road with still water and reeds, soft evening sun",
)

# The look never moves: nothing on this page is a barn find unless the story says so. Fresh paint,
# deep reflections, spotless chrome - a car that just came out of the showroom, whatever year it
# was built. The last clause is the rule that must survive every rewrite.
TAIL = ("restored to showroom condition, glass-glossy paint with deep mirror reflections, "
        "spotless chrome and trim, clean tyres, every panel polished, rich saturated colour, "
        "bright clean light, 35mm, no people, no animals, no text, no watermark.")


def setting_for(n: int) -> str:
    """The outdoor location for plate `n` (1-based), stable across re-shoots."""
    return SETTINGS[(n - 1) % len(SETTINGS)]


def plate_prompt(identity: str, sh: dict) -> str:
    return f"{PREFIX}{identity}. {sh['framing']}, {setting_for(sh['n'])}. {TAIL}"
META_URL = "https://www.meta.ai/"
COMPOSER = "div[contenteditable=true]"
NO_BROWSER = "No browser is connected"
CHROME_HELP = (
    "browser-mcp: no Chrome window is connected.\n"
    "The Browser MCP extension is installed in the default Chrome profile; the window is "
    "simply not open.\n"
    "Start it, then re-run:\n"
    "  /opt/google/chrome/chrome --no-first-run --no-default-browser-check https://meta.ai/\n"
    "This is not an install, sign-in or API-key problem. Do not switch to a paid route."
)
# The cadence inside the one chat: Meta normally finishes inside 20 s, so the first check is at
# 22 s and every plate after that is checked every 10 s. A slow plate is waited for, never
# re-prompted — a prompt goes into the chat exactly once.
FIRST_CHECK = 22
POLL = 10
WAIT_MAX = 150
SETTLE = 8     # seconds of quiet before the newest image is believed (avatars/gallery pop in late)
IMG_JS = ("() => { const a = Array.from(document.querySelectorAll('img'))"
          ".filter(i => (i.naturalWidth||0) >= 900)"
          ".map(i => i.src).filter(s => /scontent|blob:|\\/d\\//.test(s))"
          "; return a.length ? a[a.length-1] : '' }")

# Every image already on the page, so a `--only` re-shoot cannot mistake the plate it is replacing
# (or any earlier one) for the new generation. The single-newest query above is not enough: a fresh
# run only knows about the newest image, and while Meta is drawing, the newest image is the old one.
# Width >= 900 also drops the 0×0 placeholders Meta inserts the instant a prompt is sent, and the
# 240 px avatars/logo that made an earlier run download a stale picture at +0 s.
IMG_ALL_JS = ("() => { const a = Array.from(document.querySelectorAll('img'))"
              ".filter(i => (i.naturalWidth||0) >= 900)"
              ".map(i => i.src).filter(s => /scontent|blob:|\\/d\\//.test(s))"
              "; return a.join('\\n') }")


class Bridge:
    def __init__(self, cmd=None, timeout_hello=120):
        self.cmd = cmd or ["npx", "-y", "@browsermcp/mcp@latest"]
        self.p = subprocess.Popen(self.cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL, text=True, bufsize=1)
        self.n = 0
        self._req("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                 "clientInfo": {"name": "plate-shoot", "version": "1.0"}},
                  timeout=timeout_hello)
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def _send(self, obj):
        self.p.stdin.write(json.dumps(obj) + "\n")
        self.p.stdin.flush()

    def _req(self, method, params, timeout=120):
        self.n += 1
        want = self.n
        self._send({"jsonrpc": "2.0", "id": want, "method": method, "params": params})
        end = time.time() + timeout
        while time.time() < end:
            ready, _, _ = __import__("select").select([self.p.stdout], [], [], max(0, end - time.time()))
            if not ready:
                break
            line = self.p.stdout.readline()
            if not line:
                break
            try:
                msg = json.loads(line)
            except Exception:
                continue
            if msg.get("id") == want:
                return msg
        raise SystemExit(f"browser mcp: no reply for id {want}")

    def run(self, commands, timeout=180):
        r = self._req("tools/call", {"name": "browser", "arguments": {"commands": commands}}, timeout)
        if "error" in r:
            raise RuntimeError(r["error"].get("message", str(r["error"])))
        res = r.get("result", {})
        text = "\n".join(c.get("text", "") for c in res.get("content", []))
        return text, bool(res.get("isError"))

    def close(self):
        try:
            self.p.terminate()
            self.p.wait(timeout=5)
        except Exception:
            try:
                self.p.kill()
            except Exception:
                pass


def payload(out: str) -> str:
    """The eval result, without the ✓ line, the Page: line or its JSON quotes."""
    lines = [l for l in out.splitlines()
             if l.strip() and not l.startswith(("✓", "✗", "Page:", "…", "Step "))]
    body = lines[-1].strip() if lines else ""
    if body.startswith('"') and body.endswith('"') and len(body) > 1:
        body = body[1:-1]
    return body


def js(bridge, expr, timeout=60):
    """Run one JS expression on the selected tab. The command layer is one line per command."""
    flat = " ".join(expr.split())
    out, err = bridge.run(f'eval "{flat}"', timeout)
    if err:
        raise RuntimeError(payload(out) or out.strip())
    return payload(out)


def pick_tab(bridge):
    """The one meta.ai chat tab for the whole shoot.

    It reuses a tab that is already open — preferring the active one — and never closes the others:
    one session stays put for every plate of the film, and no tab is opened or closed per image.
    """
    out, err = bridge.run("tab list", 60)
    if err or NO_BROWSER in out:
        raise SystemExit(CHROME_HELP)
    ids = re.findall(r'(\d+)\s+"[^"]*Meta AI[^"]*"\s+—\s+https://(?:www\.)?meta\.ai/[^\n]*', out)
    active = [m.group(1) for m in re.finditer(
        r'(\d+)\s+"[^"]*Meta AI[^"]*"\s+—\s+https://(?:www\.)?meta\.ai/[^\n]*\(active\)', out)]
    if ids:
        keep = active[0] if active else ids[-1]
        bridge.run(f"tab select {keep}\nwait 1200", 60)
        return keep
    out, err = bridge.run(f"tab new {META_URL}\nwait 6000", 120)
    if err:
        raise SystemExit("browser-mcp is connected, but opening meta.ai failed: %s"
                         % (payload(out) or out.strip())[:300])
    for _ in range(20):
        try:
            if js(bridge, f"() => !!document.querySelector('{COMPOSER}')"):
                return "new"
        except Exception:
            pass
        time.sleep(2)
    raise SystemExit("the meta.ai tab is open but the composer is not there — sign in to Meta AI "
                     "once in that Chrome window, or check that the page loaded.")


def send(bridge, prompt):
    clean = " ".join(prompt.split()).replace('"', "'").replace("\\", "/")
    out, err = bridge.run(f'fill {COMPOSER} "{clean}"', 180)
    if err:
        raise RuntimeError(payload(out) or out.strip())
    held = js(bridge, f"() => {{ const e=document.querySelector('{COMPOSER}'); "
                      f"return e ? (e.innerText || '').length : -1 }}")
    if not held.isdigit() or int(held) < max(20, len(clean) // 2):
        raise RuntimeError(f"the composer holds {held} characters, not the prompt — nothing sent")
    bridge.run("press Enter", 60)
    time.sleep(3)


def find_image(bridge):
    """The URL of the newest generated image, or '' while it is still drawing."""
    return js(bridge, IMG_JS).strip()


def find_images(bridge):
    """Every image URL already on the page, so a re-shoot waits for a genuinely new one."""
    return [s for s in js(bridge, IMG_ALL_JS).splitlines() if s.strip()]


def fetch_image(bridge, src, out: Path) -> None:
    """Save the generated image byte-for-byte, the way the page would fetch it."""
    if src.startswith("http"):
        got, err = bridge.run(f'download "{src}" --path "{out}"', 180)
        if out.exists() and out.stat().st_size > 4000:
            return
        subprocess.run(["curl", "-sS", "-L", "--max-time", "90", "-A", "Mozilla/5.0",
                        "-e", META_URL, "-o", str(out), src], capture_output=True)
        if out.exists() and out.stat().st_size > 4000:
            return
        raise RuntimeError(f"no bytes for {src[:60]}… ({payload(got)[:120]})")
    raise RuntimeError("the image is a blob: URL — nothing to fetch")


def to_still(raw: Path, plate: Path) -> tuple[int, int]:
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                            "-show_entries", "stream=width,height", "-of", "csv=p=0", str(raw)],
                           capture_output=True, text=True)
    w, h = (int(x) for x in probe.stdout.strip().split(",")[:2])
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(raw),
                    "-vf", "scale=1080:1920:flags=lanczos", "-frames:v", "1", str(plate)], check=True)
    raw.unlink(missing_ok=True)
    return w, h


def parse_plates(film: Path):
    md = (film / "plan" / "PLATES.md").read_text(encoding="utf-8")
    m = re.search(r"\n## Car identity block\n((?:(?!\n## The ).)+)", md, re.S)
    if not m:
        sys.exit(f"{film}/plan/PLATES.md: no `## Car identity block`")
    identity = " ".join(m.group(1).split())
    rows = re.findall(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", md, re.M)
    shots = [{"n": int(n), "file": f.strip().strip("`"), "framing": fr.strip(), "scene": sc.strip()}
             for n, f, fr, sc in rows]
    if not shots:
        sys.exit(f"{film}/plan/PLATES.md: no plate table")
    return identity, shots


def main() -> None:
    ap = argparse.ArgumentParser(description="One Meta AI chat per plate, saved into stills/.")
    ap.add_argument("film", help="video-projects/<page>/<film>")
    ap.add_argument("--only", help="re-shoot just this file (e.g. 04_wing.png)")
    ap.add_argument("--prompts", action="store_true", help="print the prompts and stop")
    args = ap.parse_args()

    film = (ROOT / args.film).resolve()
    if not film.is_dir():
        sys.exit(f"no such film folder: {args.film}")
    identity, shots = parse_plates(film)
    stills = film / "stills"
    stills.mkdir(exist_ok=True)

    todo = []
    for sh in shots:
        plate = stills / sh["file"]
        prompt = plate_prompt(identity, sh)
        if args.only and sh["file"] != args.only:
            continue
        if plate.exists() and not args.only:
            print(f"  have {sh['file']}")
            continue
        todo.append((sh, plate, prompt))

    if args.prompts:
        for sh, plate, prompt in todo:
            print(f"\n--- {sh['file']} ({len(prompt)} chars)\n{prompt}")
        return
    if not todo:
        print("every plate is already on disk")
        return

    bridge = Bridge()
    tab = pick_tab(bridge)
    print(f"shooting {len(todo)} plate(s) in one meta.ai chat ({tab})", flush=True)
    seen = set(find_images(bridge))
    old_bytes = {p.read_bytes() for p in stills.glob("*.png")}
    log = []
    for sh, plate, prompt in todo:
        print(f"\n  s{sh['n']:02d} {sh['file']} — prompt in the same chat", flush=True)
        try:
            send(bridge, prompt)
            t0, src, raw = time.time(), "", stills / (plate.stem + ".src.webp")
            time.sleep(FIRST_CHECK)
            while time.time() - t0 < WAIT_MAX and not src:
                fresh = [s for s in find_images(bridge) if s not in seen]
                if fresh:
                    # The generated picture is the last new <img>, but the page also drops in
                    # avatars, 0×0 placeholders and gallery thumbnails right after a send, and
                    # some of those URLs refuse a download. Wait for the DOM to go quiet, then
                    # try the newest candidates from the bottom up until one yields new bytes.
                    time.sleep(SETTLE)
                    for cand in reversed([s for s in find_images(bridge) if s not in seen] or fresh):
                        seen.add(cand)
                        try:
                            fetch_image(bridge, cand, raw)
                        except Exception:
                            continue
                        if raw.read_bytes() in old_bytes:
                            raw.unlink(missing_ok=True)
                            continue
                        src = cand
                        break
                if src:
                    break
                print(f"    not finished at +{time.time()-t0:.0f}s — checking again in {POLL}s "
                      f"(not re-sending)", flush=True)
                time.sleep(POLL)
            if not src:
                raise RuntimeError(f"no downloadable new image within {WAIT_MAX}s")
            print(f"    image at +{time.time()-t0:.0f}s", flush=True)
            if raw.read_bytes() in old_bytes:
                raw.unlink(missing_ok=True)
                raise RuntimeError("the page handed back a picture already in stills/ — "
                                   "Meta had not drawn the new one yet")
            w, h = to_still(raw, plate)
            (stills / (plate.stem + ".images.json")).write_text(json.dumps({
                "engine": "meta-ai/browser-mcp",
                "prompt": prompt,
                "source": [w, h],
                "size": [1080, 1920],
                "files": [plate.name],
                "scene": sh["scene"],
                "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            }, indent=1) + "\n", encoding="utf-8")
            print(f"    {plate.name} {plate.stat().st_size // 1024} kB "
                  f"({w}×{h} → 1080×1920)", flush=True)
            log.append({"shot": plate.name, "status": "ok", "source": [w, h]})
        except Exception as e:
            print(f"    {plate.name} — stopped: {e}", flush=True)
            log.append({"shot": plate.name, "status": "error", "reason": str(e)})
    bridge.close()
    (film / "plan" / "plates.log.json").write_text(json.dumps(log, indent=1) + "\n", encoding="utf-8")
    ok = sum(1 for r in log if r["status"] == "ok")
    print(f"\n{ok}/{len(log)} plates shot — log at plan/plates.log.json", flush=True)


if __name__ == "__main__":
    main()
