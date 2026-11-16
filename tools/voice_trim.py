#!/usr/bin/env python3
"""Refine a Kokoro take: cap every overlong internal silence, keep the breath.

    python3 tools/voice_trim.py video-projects/<page>/<film>

Kokoro's pauses come from punctuation, and a full stop buys a ~0.4 s break. Read back to back into
a 20 s paragraph those breaks are what a viewer hears as "read, stop, read, stop". This tool keeps
the take's delivery and its words, and shortens only the **silence**:

  * every internal pause longer than `MAX_PAUSE` is cut down to `MAX_PAUSE`, half from each end,
    so the word before and the word after keep their own onsets (`--dry-run` shows the table);
  * a 6 ms cosine fade at each splice, so a trimmed pause cannot click;
  * leading silence trimmed to 40 ms, trailing kept at 120 ms (the tail the mix fades).

The original take is copied to `line-01-raw.wav` once (never overwritten by a later run) and the
refined take replaces `line-01-v120.wav`, which is the file every `audio/build_final.py` reads. It
then re-transcribes the refined take, because **the word times of the old take no longer describe
this one** — the transcript is the clock, and the new numbers must be copied into that film's
`scenes.py` and `build_final.py`.

**The re-transcription alone is not enough.** Whisper's word times drift when it hears a short
paragraph: on the 1977 Cutlass take it put "Four years later" *before* the full stop that follows
"could tell", and put the word "have" inside a pause that measured −88 dB. So after transcribing,
the tool re-anchors every word to the **measured speech blocks** — the spans between the pauses it
just capped — stretching each token's start and end inside its own block. Speech blocks are ground
truth (they are energy, not a guess); whisper only decides which word lands where. The raw whisper
output is kept beside it as `transcript-whisper.json`, the aligned table becomes `transcript.json`,
and that is the clock for both the picture and the duck.

Sound law stays intact: this only ever shortens silence between words, never a word, and never
touches the level.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

ENGINE = Path(__file__).resolve().parent.parent
WAV = "line-01-v120.wav"
RAW = "line-01-raw.wav"
FRAME_S = 0.010          # silence is measured in 10 ms frames
SILENCE_DB = -38.0       # the page's pause threshold (same as the cut detector)
MIN_PAUSE = 0.12         # shorter gaps are normal speech rhythm, left alone
MAX_PAUSE = 0.22         # the cap: a natural breath, not a hole
FADE_S = 0.006
LEAD_KEEP = 0.040
TAIL_KEEP = 0.120


def read_wav(p: Path):
    with wave.open(str(p), "rb") as w:
        sr, n, ch, sw = w.getframerate(), w.getnframes(), w.getnchannels(), w.getsampwidth()
        raw = w.readframes(n)
    if sw != 2:
        sys.exit(f"{p}: expected 16-bit PCM, got {sw * 8}-bit")
    a = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
    if ch > 1:
        a = a.reshape(-1, ch).mean(axis=1)
    return a, sr


def write_wav(p: Path, a: np.ndarray, sr: int):
    x = np.clip(a, -1.0, 1.0)
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((x * 32767.0).astype("<i2").tobytes())


def silence_runs(a: np.ndarray, sr: int):
    """[(start_sample, end_sample)] of every silent run at or above MIN_PAUSE."""
    f = max(1, int(FRAME_S * sr))
    n = len(a) // f
    rms = np.sqrt((a[: n * f].reshape(n, f) ** 2).mean(axis=1) + 1e-12)
    quiet = rms < 10 ** (SILENCE_DB / 20.0)
    runs, i = [], 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            if (j - i) * f >= MIN_PAUSE * sr:
                runs.append((i * f, j * f))
            i = j
        else:
            i += 1
    return runs


def speech_blocks(a: np.ndarray, sr: int):
    """[(start_sample, end_sample)] of everything that is not a pause."""
    blocks, cur = [], 0
    for s, e in silence_runs(a, sr):
        if s - cur >= int(0.02 * sr):
            blocks.append((cur, s))
        cur = e
    if len(a) - cur >= int(0.02 * sr):
        blocks.append((cur, len(a)))
    return blocks


def realign(words, blocks, sr):
    """Put every whisker word inside the speech block it is actually spoken in.

    Whisper tells you *which* word is which; the envelope tells you *when* speech happens.
    Each token keeps its order and its share of its block, so a drifted tail snaps back and a
    word whisper placed in silence is pulled onto the sound. Blocks with no token are left as
    the breath they are.
    """
    assigned = [[] for _ in blocks]
    bi = 0
    for w in words:
        mid = (w["start"] + w["end"]) / 2
        while bi < len(blocks) - 1 and mid > blocks[bi][1] / sr:
            bi += 1
        assigned[bi].append(w)

    out = []
    for (bs, be), group in zip(blocks, assigned):
        if not group:
            continue
        t0, t1 = bs / sr, be / sr
        w0, w1 = group[0]["start"], group[-1]["end"]
        span = max(1e-6, w1 - w0)
        for w in group:
            s = t0 + (w["start"] - w0) / span * (t1 - t0)
            e = t0 + (w["end"] - w0) / span * (t1 - t0)
            out.append({"text": w["text"], "start": round(s, 3), "end": round(e, 3)})
    return out


def fade(chunk: np.ndarray, sr: int, at_start: bool) -> np.ndarray:
    k = min(len(chunk), int(FADE_S * sr))
    if k <= 1:
        return chunk
    ramp = 0.5 - 0.5 * np.cos(np.linspace(0.0, np.pi, k))
    if not at_start:
        ramp = ramp[::-1]
    out = chunk.copy()
    out[:k] *= ramp
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Cap overlong silences in a Kokoro take.")
    ap.add_argument("film", help="video-projects/<page>/<film>")
    ap.add_argument("--max-pause", type=float, default=MAX_PAUSE)
    ap.add_argument("--dry-run", action="store_true", help="print the pause table, write nothing")
    ap.add_argument("--no-transcribe", action="store_true", help="skip the re-transcription")
    ap.add_argument("--no-realign", action="store_true", help="keep whisper's word times uncorrected")
    args = ap.parse_args()

    film = (ENGINE / args.film).resolve()
    para = film / "audio" / "paragraph"
    src = para / WAV
    if not src.exists():
        sys.exit(f"no take at {src} — make one with tools/voice.py first")
    raw = para / RAW
    if not raw.exists():
        raw.write_bytes(src.read_bytes())
        print(f"kept the untouched take as {raw.name}")

    # work from the untouched take every time, so a second run cannot trim twice
    a, sr = read_wav(raw)
    total_before = len(a) / sr
    runs = silence_runs(a, sr)
    internal = [r for r in runs if r[0] > 0 and r[1] < len(a)]

    cap = int(args.max_pause * sr)
    keep = []              # (start, end) of every sample range that survives
    cursor = 0
    table = []
    for s, e in internal:
        if e - s <= cap:
            continue
        # half the cap at each end of the pause, so both words keep their onset
        head = s + cap // 2
        tail = e - cap // 2
        keep.append((cursor, head))
        cursor = tail
        table.append(((e - s) / sr, args.max_pause))
    keep.append((cursor, len(a)))

    # leading and trailing silence
    first, last = keep[0][0], keep[-1][1]
    lead_trim = 0
    if runs and runs[0][0] == 0:
        lead_trim = max(0, runs[0][1] - int(LEAD_KEEP * sr))
    tail_trim = 0
    if runs and runs[-1][1] == len(a):
        tail_trim = max(0, runs[-1][1] - runs[-1][0] - int(TAIL_KEEP * sr))

    pieces = []
    for idx, (s, e) in enumerate(keep):
        s = max(s, first + lead_trim) if idx == 0 else s
        e = min(e, last - tail_trim) if idx == len(keep) - 1 else e
        if e > s:
            pieces.append(fade(a[s:e], sr, at_start=True))
    out = np.concatenate(pieces) if pieces else a
    total_after = len(out) / sr

    print(f"take        {src.relative_to(ENGINE)}  {total_before:.3f} s")
    if table:
        print(f"pauses      {len(table)} capped to {args.max_pause:.2f} s "
              f"(was {min(t[0] for t in table):.2f}-{max(t[0] for t in table):.2f} s)")
        for before, after in table:
            print(f"            {before:.3f} s -> {after:.3f} s")
    else:
        print(f"pauses      none over {args.max_pause:.2f} s — already continuous")
    print(f"refined     {total_after:.3f} s  (removed {total_before - total_after:.3f} s of dead air)")

    if args.dry_run:
        return

    write_wav(src, out, sr)

    if not args.no_transcribe:
        side = para / "transcript.json"
        if side.exists():
            side.unlink()          # never read a stale take's timings
        t = subprocess.run(["npx", "hyperframes", "transcribe", str(src)],
                           cwd=str(ENGINE), capture_output=True, text=True)
        if not side.exists():
            sys.exit(f"transcribe wrote no sidecar: {(t.stdout + t.stderr).strip()[-400:]}")
        raw = json.loads(side.read_text())
        (para / "transcript-whisper.json").write_text(json.dumps(raw, indent=1) + "\n")

        blocks = speech_blocks(out, sr)
        words = raw if args.no_realign else realign(raw, blocks, sr)
        side.write_text(json.dumps(words, indent=1) + "\n")
        moved = 0.0 if args.no_realign else max(abs(a["start"] - b["start"])
                                               for a, b in zip(raw, words))
        print(f"transcript  {len(words)} words re-anchored to {len(blocks)} speech blocks "
              f"(whisper was off by up to {moved:.2f} s)")
        print("next        copy those times into the film's scenes.py and audio/build_final.py")


if __name__ == "__main__":
    main()
