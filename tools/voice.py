#!/usr/bin/env python3
"""The engine's voice: one Kokoro call per film, transcribed, kept in the film folder.

    python3 tools/voice.py video-projects/<page>/<film>                      # the page default
    python3 tools/voice.py video-projects/<page>/<film> --voice am_adam      # another voice
    python3 tools/voice.py video-projects/<page>/<film> --text "one paragraph" --force

It writes `audio/paragraph/line-01-v120.wav` (the same filename every film's
`audio/build_final.py` reads) and its word times as `audio/paragraph/transcript.json`,
plus `audio/paragraph/voice.json` recording which voice, speed and text made that take.

The paragraph comes from `plan/SCRIPT.md` — the text under `## The read` — unless `--text`
gives one. `speed` is always set in the request, never applied afterwards with `atempo`.

Voices are a fixed list here, not a free string: the page has one sound, and a new voice is
added in this file so every film can use it. `am_michael` is the page default; `am_adam` was
added for the Dodge Charger Daytona build and is how that film, and every film after it that
asks for it, is read.
"""
import argparse
import json
import re
import subprocess
import sys
import wave
from datetime import datetime
from pathlib import Path

ENGINE = Path(__file__).resolve().parent.parent
KOKORO = "http://localhost:8880/v1/audio/speech"

# The page's voices. `default` is what a film gets when it does not ask.
VOICES = {
    "am_michael": {
        "default": True,
        "speed": 1.2,
        "note": "the page voice from the first film on — warm, steady, reads numbers well",
    },
    "am_adam": {
        "default": False,
        "speed": 1.2,
        "note": "added 2026-11-15 for the 1969 Dodge Charger Daytona — lower and harder",
    },
}

OUT_NAME = "line-01-v120.wav"      # what every build_final.py expects
SR = 48000


def read_paragraph(film: Path) -> str:
    """The spoken paragraph: the line under `## The read` in plan/SCRIPT.md."""
    script = film / "plan" / "SCRIPT.md"
    if not script.exists():
        sys.exit(f"no script to read: {script} (pass --text instead)")
    text = script.read_text(encoding="utf-8")
    m = re.search(r"^##[^\n]*The read[^\n]*\n(.+?)(?:\n\s*\n|\Z)", text, re.S | re.M)
    if not m:
        sys.exit(f"{script}: no `## The read` paragraph (pass --text instead)")
    para = " ".join(m.group(1).split())
    if len(para.split()) < 10:
        sys.exit(f"{script}: the read is only {len(para.split())} words — that is not a script")
    return para


def wav_seconds(p: Path) -> float:
    """ffprobe, not the WAV header: Kokoro's header length field is not the real one."""
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def main() -> None:
    ap = argparse.ArgumentParser(description="One Kokoro take per film, transcribed.")
    ap.add_argument("film", help="video-projects/<page>/<film>")
    ap.add_argument("--voice", default=None, help=" / ".join(VOICES))
    ap.add_argument("--text", help="the paragraph, instead of plan/SCRIPT.md")
    ap.add_argument("--speed", type=float, default=None)
    ap.add_argument("--force", action="store_true", help="re-take over an existing WAV")
    args = ap.parse_args()

    film = (ENGINE / args.film).resolve()
    if not film.is_dir():
        sys.exit(f"no such film folder: {args.film}")

    voice = args.voice or next(v for v, c in VOICES.items() if c["default"])
    if voice not in VOICES:
        sys.exit(f"unknown voice {voice!r} — the page uses {' / '.join(VOICES)}; "
                 f"add a new one in tools/voice.py")
    speed = args.speed or VOICES[voice]["speed"]

    para = args.text or read_paragraph(film)
    words = len(para.split())

    outdir = film / "audio" / "paragraph"
    outdir.mkdir(parents=True, exist_ok=True)
    wav = outdir / OUT_NAME
    if wav.exists() and not args.force:
        print(f"re-using the existing take {wav} — pass --force to record a new one")
    else:
        payload = json.dumps({"model": "kokoro", "input": para, "voice": voice,
                              "response_format": "wav", "speed": speed})
        r = subprocess.run(["curl", "-sS", "--fail-with-body", "-m", "180",
                            KOKORO, "-H", "Content-Type: application/json", "-d", payload,
                            "-o", str(wav)], capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"kokoro refused the take: {r.stderr.strip() or r.stdout.strip()}\n"
                     f"is the local server up?  curl {KOKORO}")

    secs = wav_seconds(wav)

    # the word times, measured on that exact file. hyperframes writes its sidecar beside
    # the input as `transcript.json`; accept its older `<stem>.json` shape too.
    t = subprocess.run(["npx", "hyperframes", "transcribe", str(wav)],
                       cwd=str(ENGINE), capture_output=True, text=True)
    sidecar = next((p for p in (outdir / "transcript.json", wav.with_suffix(".json"))
                    if p.exists() and p.stat().st_mtime >= wav.stat().st_mtime - 1), None)
    if sidecar is None:
        sys.exit(f"transcribe wrote no sidecar: {(t.stdout + t.stderr).strip()[-400:]}")
    words_measured = json.loads(sidecar.read_text(encoding="utf-8"))

    (outdir / "voice.json").write_text(json.dumps({
        "engine": "kokoro",
        "voice": voice,
        "speed": speed,
        "words": words,
        "seconds": round(secs, 3),
        "wav": OUT_NAME,
        "at": datetime.now().isoformat(timespec="seconds"),
        "text": para,
    }, indent=1) + "\n", encoding="utf-8")

    per = secs / max(1, words)
    print(f"{film.name}: {voice} @ {speed}, {words} words -> {secs:.3f} s "
          f"({per:.3f} s/word) -> {outdir / OUT_NAME}")
    print(f"transcript: {len(words_measured)} timed words in {outdir / 'transcript.json'}")
    print(f"a 30 s film at this rate holds about {int(28.0 / per)} words of speech "
          f"(28 s of read inside 30 s)")


if __name__ == "__main__":
    main()
