#!/usr/bin/env python3
"""The story gate — MASTER PROMPT.md as code.

Before this file existed, only the caption was checked by a machine. The 80 gate, the fact
sheet, the five beats, the word budget and the plate count were promises the model made to
itself. This runs them as assertions, and exits 1 on any failure, so a film cannot reach a
render (or a queue row) while it fails one.

    python3 tools/score.py video-projects/<page>/<film>
    python3 tools/score.py video-projects/<page>/<film> --quiet

Checks, in the order `## Verification gates` lists them:

  score     plan/VIRAL.md totals 80 or more
  angle     VIRAL.md names one of the page's six Tracker angles
  future    VIRAL.md offers 3 future stories about the same car (master §11.9)
  facts     plan/FACTCHECK.md exists, has sourced rows, and verdicts 0 invented facts
  beats     plan/SCRIPT.md carries HOOK, SETUP, TURN, REVELATION, ENDING — no "PROOF" beat 4
  words     the narration's real word count against the measured voice (1.7–2.7 words/s)
  frames    scenes.py frame counts sum to the film's duration x 60
  plates    ceil(seconds / 3) distinct stills, none on screen past 3.25 s
  reveals   every card time lands on a word or in a pause, inside its own scene, never mid-word
  sound     every recording the mix takes from sound/ still exists
  caption   the three parts exist and the caption scored 80 or more

Exit codes: 0 pass, 1 a check failed, 2 the film folder or a required file is missing.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

PAGE_ANGLES = [
    "Size / Looks",
    "Price / Rarity",
    "Engine / Speed",
    "Secret Story",
    "Why It Failed",
    "Why It Became Legend",
]

SCORE_GATE = 80
MIN_FUTURE_ANGLES = 3
MIN_FACT_ROWS = 4
# MASTER PROMPT.md's word budgets are a rate in disguise: 30-45 words per 15 s and 60-90 per
# 30 s both come out at 2.0-3.0 words per spoken second. That is what is checked here, so the
# count is measured against the real WAV instead of a duration someone typed.
WORD_RATE_MIN, WORD_RATE_MAX = 2.0, 3.0
MAX_STILL_SECONDS = 3.25
REQUIRED_BEATS = ["HOOK", "SETUP", "TURN", "REVELATION", "ENDING"]

# Scene-edge slack: the times are copied from the transcript and rounded to 3 decimals.
REVEAL_EPS = 0.020
# A card this close to a word's onset is on that word. Whisper's own timing error is tens of
# milliseconds, so a tighter window would fail cards that were placed by hand, correctly.
REVEAL_ON_WORD = 0.100
# Past this much into a word, and nowhere near its onset, the card is changing mid-word.
REVEAL_INSIDE = 0.050
# A card that enters with less picture than this left is a blink the viewer never reads.
REVEAL_MIN_MARGIN = 0.150


class Report:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str]] = []   # status, name, detail
        self.failed = 0

    def ok(self, name: str, detail: str) -> None:
        self.rows.append(("PASS", name, detail))

    def bad(self, name: str, detail: str) -> None:
        self.rows.append(("FAIL", name, detail))
        self.failed += 1

    def warn(self, name: str, detail: str) -> None:
        self.rows.append(("WARN", name, detail))

    def show(self, quiet: bool) -> None:
        width = max(len(n) for _, n, _ in self.rows) if self.rows else 8
        for status, name, detail in self.rows:
            if quiet and status == "PASS":
                continue
            print(f"{status:<4}  {name:<{width}}  {detail}")
        if self.failed:
            print(f"\n{self.failed} check(s) failed — this film is not built and not queued.")
        else:
            print("\nPASS — the film may be built.")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def section(text: str, *needles: str) -> str:
    """Everything under the first heading that contains any needle, up to the next heading.

    A heading is a line in column 0 that starts with 1-6 '#' and a space. A caption's hashtag
    line starts with a single leading space on purpose, so it is not a heading.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if re.match(r"^#{1,6}\s", line) and any(n.lower() in line.lower() for n in needles):
            out = []
            for later in lines[i + 1:]:
                if re.match(r"^#{1,6}\s", later):
                    break
                out.append(later)
            return "\n".join(out)
    return ""


def first_paragraph(block: str) -> str:
    """The first contiguous run of non-blank lines — the read itself, not our notes on it."""
    out, started = [], False
    for line in block.splitlines():
        if line.strip():
            out.append(line)
            started = True
        elif started:
            break
    return "\n".join(out)


# -- individual checks ----------------------------------------------------------------

def check_viral(viral: str, rep: Report) -> None:
    if not viral:
        rep.bad("score", "plan/VIRAL.md is missing — the master's §3 gate cannot be read")
        rep.bad("angle", "no VIRAL.md")
        rep.bad("future", "no VIRAL.md")
        return

    hit = re.search(r"\*\*Total\*\*\s*\|\s*\*\*(\d+)\s*/\s*100", viral) \
        or re.search(r"(\d{1,3})\s*/\s*100", viral)
    if not hit:
        rep.bad("score", "no total found — write '**Total** | **NN / 100**'")
    else:
        value = int(hit.group(1))
        if value >= SCORE_GATE:
            rep.ok("score", f"{value}/100 (gate {SCORE_GATE})")
        else:
            rep.bad("score", f"{value}/100 — under the gate of {SCORE_GATE}, "
                             "the car is not built (master §3)")

    declared = re.search(r"\*\*Angle:?\*\*\s*\|?\s*([A-Za-z][^|\n]{2,30})", viral)
    named = [a for a in PAGE_ANGLES if a.lower() in viral.lower()]
    if declared and any(a.lower() in declared.group(1).lower() for a in PAGE_ANGLES):
        chosen = next(a for a in PAGE_ANGLES if a.lower() in declared.group(1).lower())
        rep.ok("angle", chosen)
    elif named:
        rep.ok("angle", named[0])
    else:
        rep.bad("angle", "none of the six page angles is named — the Tracker cannot read it")

    block = section(viral, "future", "story opportunities", "next stories")
    if not block:
        rep.bad("future", "no future-stories section — master §11.9 asks for 3 angles "
                          "on the same car, and they are what stops a Part 2 repeating this one")
        return
    items = [ln for ln in block.splitlines()
             if re.match(r"^\s*(?:[-*]|\d+[.)])\s+\S", ln)]
    if len(items) >= MIN_FUTURE_ANGLES:
        rep.ok("future", f"{len(items)} future stories recorded")
    else:
        rep.bad("future", f"{len(items)} future angle(s) — master §11.9 asks for "
                          f"{MIN_FUTURE_ANGLES}, none repeating the selected angle")


def check_facts(facts: str, rep: Report) -> None:
    if not facts:
        rep.bad("facts", "plan/FACTCHECK.md is missing — 'no invented facts' is unverified")
        return

    rows = []
    for line in facts.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
            continue
        if cells[0].lower() in ("claim", "**claim**"):
            continue
        rows.append(cells)

    if len(rows) < MIN_FACT_ROWS:
        rep.bad("facts", f"{len(rows)} claim row(s) — the film's numbers are not on record")
        return

    unsourced = [r[0] for r in rows if len(r) < 3 or not r[2]]
    if unsourced:
        rep.bad("facts", f"{len(unsourced)} row(s) carry no source: {unsourced[0][:48]}")
        return

    verdict = re.search(r"(\d+)\s+invented facts", facts, re.I) or re.search(r"no invented facts", facts, re.I)
    if not verdict:
        rep.bad("facts", "no verdict line — write '0 invented facts' after the rows")
        return
    if verdict.group(0).strip().startswith("0") or "no invented" in verdict.group(0).lower():
        rep.ok("facts", f"{len(rows)} sourced claims, 0 invented")
    else:
        rep.bad("facts", f"the verdict admits invented facts: {verdict.group(0)}")


def check_beats(script: str, rep: Report) -> None:
    if not script:
        rep.bad("beats", "plan/SCRIPT.md is missing")
        return
    block = section(script, "beat")
    body = block if block else script
    upper = body.upper()

    missing = [b for b in REQUIRED_BEATS if b not in upper]
    # "SATISFYING ENDING" contains ENDING, so ENDING is satisfied either way.
    if missing:
        rep.bad("beats", "missing beat(s): " + ", ".join(missing) +
                          " — master §4 needs HOOK, SETUP, TURN, BIG REVELATION, ENDING")
        return

    # The four beats, in order, and beat 4 is the revelation rather than a stat roll.
    order = []
    for line in body.splitlines():
        for beat in ["HOOK", "SETUP", "TURN", "REVELATION", "ENDING"]:
            if re.search(rf"\b{beat}\b", line.upper()) and beat not in order:
                order.append(beat)
    if order != REQUIRED_BEATS:
        rep.bad("beats", "out of order: " + " > ".join(order))
        return

    if re.search(r"\bPROOF\b\s*\((?:19|20)", body) and "REVELATION" not in upper:
        rep.bad("beats", "beat 4 is labelled PROOF — a statistic is not a revelation (master §4.D)")
        return

    rep.ok("beats", "HOOK > SETUP > TURN > REVELATION > ENDING")


def narration_words(script: str) -> int:
    """The spoken paragraph, measured rather than trusted."""
    for needle in ("read, as one paragraph", "the read", "narration", "voiceover"):
        block = section(script, needle)
        if block.strip():
            text = first_paragraph(block)
            text = re.sub(r"^>\s?", "", text, flags=re.M)
            text = re.sub(r"[*_`]", "", text)
            words = [w for w in re.split(r"\s+", text.strip()) if re.search(r"[A-Za-z0-9$]", w)]
            if len(words) > 10:
                return len(words)
    return 0


def check_words(script: str, speech_seconds: float, rep: Report) -> None:
    words = narration_words(script)
    if not words:
        rep.bad("words", "no narration paragraph found in plan/SCRIPT.md")
        return
    if speech_seconds <= 0:
        rep.bad("words", "audio/paragraph/transcript.json has no measured speech")
        return
    rate = words / speech_seconds
    detail = f"{words} words / {speech_seconds:.3f} s = {rate:.2f} words/s"
    if WORD_RATE_MIN <= rate <= WORD_RATE_MAX:
        rep.ok("words", detail)
    elif rate < WORD_RATE_MIN:
        rep.bad("words", detail + f" — thin: under {WORD_RATE_MIN} words/s the read "
                                  "drags; add a link to the chain (master §4)")
    else:
        rep.bad("words", detail + f" — rushed: over {WORD_RATE_MAX} words/s")


def check_frames_and_plates(proj: Path, meta: dict, rep: Report) -> None:
    duration = float(meta.get("duration") or 0)
    if duration <= 0:
        rep.bad("frames", "meta.json has no duration")
        return

    src = read(proj / "scenes.py")
    block = src.split("SCENES = [", 1)[-1]
    frames = [int(n) for n in re.findall(r"frames=(\d+)", block)]
    stills = re.findall(r'still="([^"]+)"', block)

    if frames:
        total = sum(frames)
        want = round(duration * 60)
        if total == want:
            rep.ok("frames", f"{total} = {duration:.3f} s x 60")
        else:
            rep.bad("frames", f"{total} frames vs {want} wanted for {duration:.3f} s "
                              "(scenes are joined without re-encoding, so the audio drifts)")
    else:
        rep.bad("frames", "no frame counts found in scenes.py")

    if not stills:
        rep.bad("plates", "no stills found in scenes.py")
        return

    need = math.ceil(duration / 3)
    unique = len(set(stills))
    if unique >= need:
        rep.ok("plates", f"{unique} distinct stills for {duration:.1f} s (needs {need})")
    else:
        repeated = sorted({s for s in stills if stills.count(s) > 1})
        rep.bad("plates", f"{unique} distinct stills for {duration:.1f} s, needs {need} — "
                          f"reused: {', '.join(repeated) or 'n/a'} (master §7)")

    if frames and len(frames) == len(stills):
        worst = max(f / 60 for f in frames)
        if worst <= MAX_STILL_SECONDS:
            rep.ok("cadence", f"longest still {worst:.2f} s")
        else:
            rep.bad("cadence", f"a still runs {worst:.2f} s — the plate may not outlive 3 s")


def load_scene_table(proj: Path):
    """`scenes.py` is a data table — loaded exactly as tools/scene_builder.py loads it."""
    table = proj / "scenes.py"
    spec = importlib.util.spec_from_file_location(f"score_{proj.name.replace('-', '_')}", table)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def reveals_of(scene: dict) -> list[tuple[str, float]]:
    """The moment a card **arrives**: its kicker and its first line.

    A second line is the same card still arriving, and the page has always staggered it a beat
    behind the first (the rambler does it by 0.3 s), so it is not judged against the voice —
    only ordered after `b1` and kept inside its scene. The label under a number is deliberately
    later still: the numbers law has it arrive after the roll locks, so it lands inside the
    spoken phrase. The footnote and the red rule are incidental.

    A table also carries dummies for cards a scene does not have (`big=None, b1_at=0`);
    the builder never animates those.
    """
    out = []
    if scene.get("kick"):
        out.append(("kick", scene.get("kick_at")))
    if scene.get("big"):
        out.append(("b1", scene.get("b1_at")))
    return [(name, float(at)) for name, at in out if at is not None]


def check_reveals(proj: Path, rep: Report) -> None:
    """Every card changes picture between words, never on top of one.

    The timing law says a reveal sits on the word it belongs to; the fault it exists to stop is
    a card that flips **inside** a spoken word. That is decidable from the plan alone — the card
    times in `scenes.py` against the measured word spans in `transcript.json` — so it is checked
    here, before a render, rather than only by eye on the sheet afterwards.

    A card is legal when its time is a word start, a pause between words, or the silence after
    the last word while the engine answers (the closing card). It is a fault when it lands
    strictly inside a word, when it is scheduled outside the scene that owns it (so it either
    never appears or is cut off), or when a card's second line precedes its first.
    """
    table, words = proj / "scenes.py", proj / "audio" / "paragraph" / "transcript.json"
    if not table.is_file():
        # `frames` and `plates` already fail a film with no scene table; do not double-count.
        rep.warn("reveals", "no scenes.py — the card times cannot be checked")
        return
    if not words.is_file():
        rep.warn("reveals", "no transcript.json — card times are unchecked against the voice")
        return

    spans = json.loads(words.read_text(encoding="utf-8"))
    if not isinstance(spans, list) or not spans:
        rep.warn("reveals", "transcript.json is empty — card times are unchecked")
        return

    mod = load_scene_table(proj)
    lead = float(getattr(mod, "LEAD", 0.0))
    pad = float(getattr(mod, "PAD", 0.0))
    scenes = list(getattr(mod, "SCENES", []))
    if not scenes:
        rep.bad("reveals", "scenes.py has no SCENES table")
        return

    # absolute film time: the transcript is measured on the take, the voice is placed at LEAD
    spoken = [(str(w.get("text", "?")), float(w.get("start") or 0) + lead,
               float(w.get("end") or 0) + lead) for w in spans]

    starts, t = [], 0.0
    for sc in scenes:
        starts.append(t)
        t += float(sc.get("frames") or 0) / 60.0

    problems, counted, tight = [], 0, []
    for sc, begin in zip(scenes, starts):
        end = begin + float(sc.get("frames") or 0) / 60.0
        where = f"{sc.get('file', '?')}"
        for key, at in reveals_of(sc):
            at += pad
            counted += 1
            if at < begin - REVEAL_EPS or at >= end:
                problems.append(f"{where} {key}={at:.3f}s is outside its scene "
                                f"({begin:.3f}–{end:.3f}) — it never gets a frame on screen")
                continue
            if end - at < REVEAL_MIN_MARGIN:
                tight.append(f"{where} {key}={at:.3f}s has {end - at:.3f}s of picture left")
            if any(abs(at - w0) <= REVEAL_ON_WORD for _, w0, _ in spoken):
                continue                       # on a word (or on its ~65 ms early cut)
            for text, w0, w1 in spoken:
                if w0 + REVEAL_INSIDE <= at <= w1 - REVEAL_INSIDE:
                    problems.append(f"{where} {key}={at:.3f}s is {at - w0:.2f}s into "
                                    f"\"{text}\" ({w0:.3f}–{w1:.3f}) — mid-word")
                    break
        b1, b2 = sc.get("b1_at"), sc.get("b2_at")
        if sc.get("big") and b1 is not None and b2 is not None and len(sc["big"]) > 1 \
                and sc["big"][1][0] and float(b2) <= float(b1):
            problems.append(f"{where} b2_at={float(b2):.3f}s does not follow b1_at={float(b1):.3f}s")

    if problems:
        rep.bad("reveals", "; ".join(problems[:4]) +
                (f" (+{len(problems) - 4} more)" if len(problems) > 4 else ""))
        return
    if not counted:
        rep.warn("reveals", "no card times in scenes.py — nothing to check")
        return

    detail = f"{counted} card times, none mid-word, all inside their scene"
    if tight:
        rep.warn("reveals", detail + "; short of picture: " + ", ".join(tight[:3]))
    else:
        rep.ok("reveals", detail)


def sound_references(src: str) -> list[str]:
    """The recordings a build takes from the engine's library.

    Two shapes, both of them the convention every build_final.py uses: a library variable
    joined to a filename (`LIB / "x.mp3"`, `SOUND / "engines/x.mp3"`), or a literal that
    spells out one of the two folders. Everything else in that file (`SFX / "premix.wav"`)
    is the film's own output and is not a library reference.
    """
    refs = set()
    for var in ("LIB", "SOUND", "ENGINES", "SND", "LIB_ENG", "LIB_SFX", "SFX_LIB"):
        for m in re.finditer(rf"\b{var}\s*/\s*[\"']([^\"']+)[\"']", src):
            refs.add(m.group(1))
    for m in re.finditer(r"[\"']((?:engines|SFX Sound Effects)/[^\"']+)[\"']", src):
        refs.add(m.group(1))
    return sorted(refs)


def check_sound(proj: Path, rep: Report) -> None:
    """A renamed or deleted recording must fail the gate, not the render."""
    build = proj / "audio" / "build_final.py"
    if not build.is_file():
        rep.warn("sound", "no audio/build_final.py — the mix's library references are unchecked")
        return

    lib = Path(__file__).resolve().parent.parent / "sound"
    src = read(build)
    refs = sound_references(src)
    if not refs:
        rep.warn("sound", "build_final.py names no sound/ recording — is the mix reading the library?")
        return

    missing = []
    for ref in refs:
        candidates = [lib / ref] if "/" in ref else [lib / "engines" / ref,
                                                      lib / "SFX Sound Effects" / ref]
        if not any(c.is_file() for c in candidates):
            missing.append(ref)
    if missing:
        rep.bad("sound", f"{len(missing)} recording(s) gone from sound/: " + ", ".join(missing))
        return

    kit = lib / "kit.json"
    note = ""
    if kit.is_file():
        slots = json.loads(kit.read_text(encoding="utf-8")).get("slots", {})
        used = {Path(r).name for r in refs}
        named = [slot for slot, spec in slots.items()
                 if any(Path(v["file"]).name in used
                        for v in [spec] + spec.get("alternates", []) if v.get("file"))]
        if re.search(r"\bHIT_SYNTH\b|\bTHUMP_RMS_DB\b", src):
            named.append("hit (generated in the build)")
        if named:
            note = f" (kit slot{'s' if len(named) > 1 else ''}: {', '.join(named)})"
        else:
            note = " — not one of the kit's four slots; a bespoke recording needs a kit entry"
    rep.ok("sound", f"{len(refs)} library recording(s) resolve{note}")


def check_caption(script: str, rep: Report) -> None:
    block = section(script, "caption")
    if not block.strip():
        rep.bad("caption", "no caption block in plan/SCRIPT.md")
        return

    tags = [ln for ln in block.splitlines() if re.match(r"^\s*#\w", ln.strip())]
    if not tags:
        rep.bad("caption", "no hashtag line in the caption block")
        return
    count = len(re.findall(r"#\w+", tags[0]))
    if 4 <= count <= 5:
        rep.ok("caption", f"{count} hashtags")
    else:
        rep.bad("caption", f"{count} hashtags — the rule is 4 or 5")

    hit = re.search(r"caption score\s*\*\*(\d+)\*\*", script, re.I) \
        or re.search(r"caption score[^\d]{0,8}(\d{1,3})", script, re.I)
    if not hit:
        rep.warn("caption score", "not recorded — `queue` needs --caption-score")
        return

    total = int(hit.group(1))
    if total < SCORE_GATE:
        rep.bad("caption score", f"{total}/100 — under the gate, rewrite it")
        return

    # The score is five judgements, so the plan has to list them and they have to add up.
    marks = re.findall(r"(?:hook shock|relatability|curiosity gap|shareability|visual wow)"
                       r"\s*[:|]?\s*(\d{1,3})\s*/\s*(\d{1,3})", script, re.I)
    if len(marks) < 5:
        rep.bad("caption score", f"{total}/100 but the five weights are not itemised — "
                                  "a total nobody can add up is a number someone typed")
        return
    weights = {"hook shock": 25, "relatability": 20, "curiosity gap": 20,
               "shareability": 15, "visual wow": 20}
    named, over = {}, []
    for name, cap in weights.items():
        mark = re.search(rf"{re.escape(name)}\s*[:|]?\s*(\d{{1,3}})\s*/\s*(\d{{1,3}})",
                         script, re.I)
        if not mark:
            over.append(f"{name} missing")
            continue
        got, stated = int(mark.group(1)), int(mark.group(2))
        named[name] = got
        if stated != cap or got > cap:
            over.append(f"{name} {got}/{stated} (cap {cap})")
    if over:
        rep.bad("caption score", "weight(s) wrong: " + ", ".join(over))
        return
    summed = sum(named.values())
    if summed != total:
        rep.bad("caption score", f"the five weights add to {summed}, the caption says {total}")
        return
    rep.ok("caption score", f"{total}/100 = {'+'.join(str(v) for v in named.values())} "
                             f"(gate {SCORE_GATE})")


# -- entry point ----------------------------------------------------------------------

def evaluate(proj: Path, quiet: bool = False) -> bool:
    rep = Report()

    meta_path = proj / "meta.json"
    if not meta_path.is_file():
        print(f"FAIL  no meta.json in {proj}", file=sys.stderr)
        return False
    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    plan = proj / "plan"
    check_viral(read(plan / "VIRAL.md"), rep)
    check_facts(read(plan / "FACTCHECK.md"), rep)

    script = read(plan / "SCRIPT.md")
    check_beats(script, rep)

    speech = 0.0
    transcript = proj / "audio" / "paragraph" / "transcript.json"
    if transcript.is_file():
        words = json.loads(transcript.read_text(encoding="utf-8"))
        if isinstance(words, list) and words:
            speech = float(words[-1].get("end") or 0)
    check_words(script, speech, rep)

    check_frames_and_plates(proj, meta, rep)
    check_reveals(proj, rep)
    check_sound(proj, rep)
    check_caption(script, rep)

    rep.show(quiet)
    return rep.failed == 0


def main() -> int:
    ap = argparse.ArgumentParser(description="MASTER PROMPT.md as a gate")
    ap.add_argument("project", help="video-projects/<page>/<film>")
    ap.add_argument("--quiet", action="store_true", help="print only failures and warnings")
    args = ap.parse_args()

    proj = Path(args.project)
    if not proj.is_dir():
        print(f"no such film folder: {proj}", file=sys.stderr)
        return 2
    if not (proj / "plan").is_dir():
        print(f"no plan/ in {proj} — the film has no paper trail to check", file=sys.stderr)
        return 2

    return 0 if evaluate(proj, args.quiet) else 1


if __name__ == "__main__":
    sys.exit(main())
