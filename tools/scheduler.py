#!/usr/bin/env python3
"""The scheduler — the one command that books queued films on a page.

    python3 tools/scheduler.py video-projects/vintage-motor-house --dry-run
    python3 tools/scheduler.py video-projects/vintage-motor-house
    python3 tools/scheduler.py video-projects/vintage-motor-house --interval 60 --limit 3
    python3 tools/scheduler.py video-projects/vintage-motor-house --start-at 2026-11-17T09:00:00Z

This is a door, not a second scheduler. It resolves the target and forwards every flag to
`tools/publish.py schedule`, so the person and the agent run the same code, and no batch ever
gets a private scheduling script written for it.

The target may be:
  * a page folder  — books everything queued on that page, in data.csv order
  * a film folder  — the same page queue; the film only supplies the channel

Every flag of `publish.py schedule` works here: `--limit N`, `--start-at ISO`,
`--start-delay MIN`, `--start-min` / `--start-max`, `--gap-min` / `--gap-max`,
`--interval MIN`, `--dry-run`, `--no-excel`.

Booking is a public, external action: run `--dry-run` first, and run it for real only after
an explicit yes on those films.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGINE = HERE.parent
sys.path.insert(0, str(HERE))

import publish  # noqa: E402  (same folder, after sys.path)


def resolve(target: str) -> str:
    """The film whose channel a page-level booking runs on.

    `publish.py` takes a film because that is where `meta.json` and the render live. The
    scheduling itself is page-wide — the queue, the ledger and the workbooks are the page's —
    so a page target is resolved to one of its films, and the films must agree on the channel.
    """
    path = Path(target)
    if not path.is_absolute():
        path = ENGINE / path
    path = path.resolve()
    if (path / "meta.json").is_file():
        return str(path)
    if not path.is_dir():
        raise SystemExit("no such folder: %s" % path)

    films = sorted(p for p in path.iterdir() if (p / "meta.json").is_file())
    if not films:
        raise SystemExit("%s is neither a film (no meta.json) nor a page holding films." % path)

    channels: dict[tuple[str, str], list[str]] = {}
    for film in films:
        social = (json.loads((film / "meta.json").read_text(encoding="utf-8")).get("social") or {})
        channels.setdefault((social.get("platform") or "facebook",
                             social.get("account") or ""), []).append(film.name)
    if len(channels) > 1:
        raise SystemExit("the films on this page disagree about the channel: %s" % "; ".join(
            "%s / %s -> %s" % (platform, account or "(none)", ", ".join(names))
            for (platform, account), names in channels.items()))
    return str(films[-1])


def main(argv) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        print()
        sys.argv = [sys.argv[0], "schedule", "--help"]
        publish.main()          # argparse prints the schedule flags and exits
        return 0
    sys.argv = [sys.argv[0], "schedule", resolve(argv[0]), *argv[1:]]
    publish.main()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
