#!/usr/bin/env python3
"""Lay down a new film from a template: the folder, its meta.json and its scene table.

    python3 tools/new_film.py --list
    python3 tools/new_film.py video-projects/<page>/<slug>
    python3 tools/new_film.py video-projects/<page>/<slug> --template "Classic Card Reel"

Every template carries its own `name` in `template.json`; that name is what `--template` takes and
what `--list` prints. `--template` also accepts the folder, since that is how a template is found
on disk, but a template without a name — or a second one using the same name — is refused.

Step 2 of `AGENTS.md` used to be `mkdir` plus `cp` from a sibling film, which meant the skeleton was
whatever the last film happened to look like. It now comes from `templates/<name>/`, and the
structure is stated once.

What is copied is the shape, not the content: `meta.json` and `scenes.py` are rendered with this
film's names and carry **no numbers** (a scene table with somebody else's measurements is a film
that is out of sync on every cut). `audio/build_final.py` is copied from the reference build named
in the template, so the current sound law travels with every new film instead of being retyped.

The template cannot supply the film's content. Plates, the voice, the facts, the score and the
caption are still steps 1 and 3-8, and `plan/` starts empty because a plan is written, never
scaffolded.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parent.parent
TEMPLATES = ENGINE / "templates"

NEXT_STEPS = """\
next, in the order of `## The working procedure`:

  3. voice      one Kokoro take, speed 1.2 → audio/paragraph/line-01-v120.wav, then transcribe it
  4. plates     one still per 3 s into stills/, the six fixed angles first
  5. table      fill LEAD, W and SCENES in scenes.py from that transcript, then
                python3 tools/scene_builder.py {rel}
  6. mix        set the numbers at the top of audio/build_final.py, then run it
  7. gates      npm run render -- {rel} ; npm run lint -- {rel} ; npm run check -- …
  8. caption    write it, score it, then queue it

`meta.json` still holds a placeholder `output`: it becomes the caption's first line, so it is set
when the caption is written, never before."""


def templates() -> list[dict]:
    """Every template, each carrying its own name — the name is what a person selects."""
    out, seen = [], {}
    for d in sorted(p for p in TEMPLATES.iterdir() if p.is_dir()):
        manifest = d / "template.json"
        if not manifest.is_file():
            continue
        spec = json.loads(manifest.read_text(encoding="utf-8"))
        name = (spec.get("name") or "").strip()
        if not name:
            sys.exit(f"templates/{d.name}/template.json has no \"name\" — every template is named")
        if name.lower() in seen:
            sys.exit(f"two templates are called {name!r}: templates/{seen[name.lower()]}/ "
                     f"and templates/{d.name}/")
        seen[name.lower()] = d.name
        spec["folder"] = d.name
        out.append(spec)
    return out


def choose(available: list[dict], wanted: str | None) -> dict:
    """Select by name (case-insensitive) or by folder; no name and one template means that one."""
    if wanted is None:
        if len(available) == 1:
            return available[0]
        sys.exit("more than one template, so name one: "
                 + ", ".join(t["name"] for t in available))
    for t in available:
        if wanted.lower() in (t["name"].lower(), t["folder"].lower()):
            return t
    sys.exit(f"no template {wanted!r}. Available: "
             + "; ".join(f"{t['name']} (templates/{t['folder']})" for t in available))


def page_project(page: Path) -> str:
    """The channel's name, taken from a film that already exists in this page."""
    for meta in sorted(page.glob("*/meta.json")):
        try:
            project = json.loads(meta.read_text(encoding="utf-8")).get("project")
        except (OSError, json.JSONDecodeError):
            continue
        if project:
            return project
    return page.name.replace("-", " ").title()


def escape(value: str) -> str:
    """Safe inside a JSON string and a Python double-quoted string."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Scaffold a film folder from templates/.")
    ap.add_argument("film", nargs="?", help="video-projects/<page>/<slug>")
    ap.add_argument("--template", default=None, help="a template name (or its folder) under templates/")
    ap.add_argument("--title", default=None, help="working title; the delivery title is set with the caption")
    ap.add_argument("--list", action="store_true", help="show the templates and stop")
    ap.add_argument("--force", action="store_true", help="write into a slug folder that already exists")
    args = ap.parse_args(argv)

    available = templates()
    if args.list or not args.film:
        for t in available:
            w, h = t.get("canvas", [0, 0])
            print(f"{t['name']:<24} {w}x{h}  templates/{t['folder']}")
            print(f"{'':<24} {t.get('description', '')}")
        if not args.list:
            print("\nname a film folder: python3 tools/new_film.py video-projects/<page>/<slug>")
        return 0

    wanted = choose(available, args.template)

    rel = Path(args.film)
    if rel.parts[0] == "video-projects" and len(rel.parts) == 3:
        page, slug = rel.parts[1], rel.parts[2]
    else:
        sys.exit("the film goes at video-projects/<page>/<slug> — two levels, page then film")
    page_dir = ENGINE / "video-projects" / page
    if not page_dir.is_dir():
        sys.exit(f"no page folder {page_dir} — the page exists first, its films second")
    film = page_dir / slug
    if film.exists() and not args.force:
        sys.exit(f"{film} already exists; a film folder is never overwritten")

    title = args.title or "TODO - title this film before it is shown"
    fills = {
        "PROJECT": escape(page_project(page_dir)),
        "PAGE": escape(page),
        "SLUG": escape(slug),
        "FILM": escape(title),
        "ID": escape(slug + "-reel"),
        "DIR": str(film.relative_to(ENGINE)),
    }

    src = TEMPLATES / wanted["folder"]
    for d in wanted.get("dirs", []):
        (film / d).mkdir(parents=True, exist_ok=True)

    written = []
    for target, source in wanted.get("render", {}).items():
        text = (src / source).read_text(encoding="utf-8")
        for key, value in fills.items():
            text = text.replace("{{" + key + "}}", value)
        leftover = [k for k in fills if "{{" + k + "}}" in text]
        if leftover:
            sys.exit(f"{source}: unfilled placeholder(s) {', '.join(leftover)}")
        (film / target).write_text(text, encoding="utf-8")
        written.append(target)

    for target, source in wanted.get("copy_from", {}).items():
        origin = ENGINE / source
        if not origin.is_file():
            sys.exit(f"{wanted['name']} copies {target} from {source}, which is missing")
        (film / target).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origin, film / target)
        written.append(target)

    print(f"{rel} from templates/{wanted['folder']} — {wanted['name']}")
    for f in written:
        print(f"  + {f}")
    print(f"  + {', '.join(d + '/' for d in wanted.get('dirs', []))}")
    print()
    print(NEXT_STEPS.format(rel=rel))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
