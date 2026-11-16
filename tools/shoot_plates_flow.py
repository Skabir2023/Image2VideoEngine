#!/usr/bin/env python3
"""Shoot a film's plates through **Google Flow** (flow-mcp), the other free image route.

    python3 tools/shoot_plates_flow.py video-projects/<page>/<film>            # queue + wait
    python3 tools/shoot_plates_flow.py video-projects/<page>/<film> --status   # what Flow says
    python3 tools/shoot_plates_flow.py video-projects/<page>/<film> --collect  # files → stills/

Flow's Agent mode renders a whole batch in parallel and images cost **0 credits**, which is why
this is the route to use while Meta AI is out of image credits. The prompts are the film's own:
the identity block and framing clauses in `plan/PLATES.md`, repeated verbatim so the plates read
as one car in one showroom finish, on a different road each time.

Flow needs a project open in its own Chrome window. `flow_status` says so; this script refuses to
queue anything until `inProject` is true, because a batch queued against no project lands nowhere.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_ROOT = Path("/home/openclaw/flow-mcp-out")
sys.path.insert(0, str(ROOT / "tools"))

from flow_call import Flow  # noqa: E402

PREFIX = "Create one photorealistic photograph, vertical portrait 9:16: "

# Every plate is shot OUTSIDE, in a different real place - a studio wall ten times over reads as
# a catalogue scan. Ordered so the six fixed angles each land somewhere that suits them, and
# keyed to the plate number so a re-shoot returns to the same place. Keep this list identical to
# the one in tools/shoot_plates.py: whichever route shoots a film, the plates must match.
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

TAIL = ("restored to showroom condition, glass-glossy paint with deep mirror reflections, "
        "spotless chrome and trim, clean tyres, every panel polished, rich saturated colour, "
        "bright clean light, 35mm, no people, no animals, no text, no watermark.")


def setting_for(n: int) -> str:
    """The outdoor location for plate `n` (1-based), stable across re-shoots."""
    return SETTINGS[(n - 1) % len(SETTINGS)]


def plate_prompt(identity: str, sh: dict) -> str:
    return f"{PREFIX}{identity}. {sh['framing']}, {setting_for(sh['n'])}. {TAIL}"


def parse_plates(film: Path):
    md = (film / "plan" / "PLATES.md").read_text(encoding="utf-8")
    m = re.search(r"\n## Car identity block\n((?:(?!\n## The ).)+)", md, re.S)
    if not m:
        sys.exit(f"{film}/plan/PLATES.md: no `## Car identity block`")
    identity = " ".join(m.group(1).split())
    rows = re.findall(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", md, re.M)
    shots = [{"n": int(n), "file": f.strip().strip("`"), "framing": fr.strip()}
             for n, f, fr, sc in rows]
    if not shots:
        sys.exit(f"{film}/plan/PLATES.md: no plate table")
    return identity, shots


def prompts_for(film: Path, only: str | None = None):
    identity, shots = parse_plates(film)
    todo = []
    for sh in shots:
        plate = film / "stills" / sh["file"]
        if only and sh["file"] != only:
            continue
        if plate.exists() and not only:
            continue
        todo.append((plate, plate_prompt(identity, sh)))
    return todo


def need_project(f: Flow) -> dict:
    out, err = f.call("flow_status", {})
    if err:
        sys.exit("flow-mcp did not answer. Its server or Chrome profile is not up; this is not "
                 "an install problem. Check /home/openclaw/flow-mcp/dist/index.js, then run "
                 "`python3 tools/brain.py`.")
    m = re.search(r"\{.*\}", out, re.S)
    status = json.loads(m.group(0)) if m else {}
    flow = status.get("flow", {})
    if not flow.get("signedIn"):
        sys.exit("flow-mcp: the Flow Chrome window is open but not signed in to Google — sign in "
                 "once with `npm run login` in /home/openclaw/flow-mcp. This is an account state, "
                 "not a missing installation.")
    if not flow.get("inProject"):
        sys.exit("flow-mcp is connected and signed in; no Flow project is open. That is a normal "
                 "state, not a connection failure.\n"
                 f"  {flow.get('hint', '')}\n"
                 "  Open or create one in Flow's Chrome window (CDP 9333), then run this again. "
                 "Images cost 0 credits in Agent mode.")
    return status


def collect(film: Path, project: str, upscaled: bool = False) -> int:
    """Move Flow's downloads into stills/, scaled once to 1080×1920."""
    _, shots = parse_plates(film)
    src_dir = OUT_ROOT / project
    files = sorted(p for p in src_dir.glob("*") if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"))
    if not files:
        sys.exit(f"no downloads in {src_dir} yet — run the queue and flow_wait first")
    missing = [sh for sh in shots if not (film / "stills" / sh["file"]).exists()]
    if len(files) != len(missing):
        print(f"note: {len(files)} downloaded for {len(missing)} missing plate(s) — pairing by order")
    n = 0
    for sh, raw in zip(missing, files):
        dst = film / "stills" / sh["file"]
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(raw),
                        "-vf", "scale=1080:1920:flags=lanczos", "-frames:v", "1", str(dst)],
                       check=True)
        prompt = plate_prompt(parse_plates(film)[0], sh)
        (film / "stills" / (dst.stem + ".images.json")).write_text(json.dumps({
            "engine": "google-flow/flow-mcp",
            "prompt": prompt,
            "source_file": str(raw),
            "size": [1080, 1920],
            "files": [dst.name],
            "at": __import__("time").strftime("%Y-%m-%dT%H:%M:%S"),
        }, indent=1) + "\n", encoding="utf-8")
        print(f"  {dst.name} ← {raw.name}")
        n += 1
    print(f"collected {n} plate(s) into {film / 'stills'}")
    return n


def main() -> None:
    ap = argparse.ArgumentParser(description="Queue/collect plates through Google Flow.")
    ap.add_argument("film")
    ap.add_argument("--project", help="output folder name (default <film-slug>-plates)")
    ap.add_argument("--status", action="store_true", help="print flow_status and stop")
    ap.add_argument("--collect", action="store_true", help="copy downloads into stills/")
    ap.add_argument("--only", help="one plate file")
    ap.add_argument("--upscaled", action="store_true", help="ask Flow for the upscaled download")
    ap.add_argument("--wait", type=int, default=0, help="seconds to wait for the batch")
    args = ap.parse_args()

    film = (ROOT / args.film).resolve()
    if not film.is_dir():
        sys.exit(f"no such film folder: {args.film}")
    project = args.project or f"{film.name}-plates"

    f = Flow()
    try:
        if args.status:
            out, _ = f.call("flow_status", {})
            print(out)
            return
        status = need_project(f)
        if args.collect:
            collect(film, project, args.upscaled)
            return
        todo = prompts_for(film, args.only)
        if not todo:
            print("every plate is already on disk")
            return
        print(f"queuing {len(todo)} plate(s) into Flow as {project!r} (0 credits, agent mode)")
        out, err = f.call("flow_agent_images", {
            "project": project,
            "scenes": [p for _, p in todo],
            "aspect_ratio": "9:16",
            "download_quality": "upscaled" if args.upscaled else "original",
        }, timeout=300)
        print(out)
        if err:
            sys.exit(1)
        ids = re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", out)
        if args.wait and ids:
            import time
            end = time.time() + args.wait
            while time.time() < end:
                out, _ = f.call("flow_wait", {"job_ids": ids[:1], "timeout_seconds": 40}, 120)
                print(out.strip()[:600], flush=True)
                if '"finished": true' in out or "finished: true" in out:
                    break
                time.sleep(2)
    finally:
        f.close()


if __name__ == "__main__":
    main()
