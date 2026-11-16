#!/usr/bin/env python3
"""The sound kit: list the slots, measure a recording, cut a slot to a wav.

Every reel is built from four sound slots, in this order and no others:

  start  the engine catching, alone, before the first word
  bed    the running engine under the whole film, ducked beneath every word
  roar   the closing two seconds, after the last word
  hit    one low hit under the closing card

`sound/kit.json` names the recording, the slice and the target level for each slot, plus
the alternates an angle can swap in. This tool reads that file, measures any recording in
the two folders, and can cut a slot out at its target level so it can be auditioned.

A slot can also be `"kind": "synth"`: no file at all, just the numbers that draw it. The
hit is one of these - a 0.26 s thud generated here, so it has no source to clear.

Run from the engine root:

  python3 tools/sound.py list                        # every slot, its slice, measured state
  python3 tools/sound.py probe "01 Boom.wav"         # duration, RMS, peak, 0.25 s envelope
  python3 tools/sound.py probe hot-rod-idle           # a fragment of the name is enough
  python3 tools/sound.py check                       # kit.json vs the folders, exit 1 on rot
  python3 tools/sound.py cut hit --out /tmp/hit.wav  # the slot, levelled, ready to listen to
  python3 tools/sound.py snippet bed --variant diesel # the constants for build_final.py

Measuring rule: decode the file and read the samples. Never trust a filename, never trust
an ffprobe frame count for the envelope — decode to 48 kHz mono and block it yourself.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np

ENGINE_ROOT = Path(__file__).resolve().parent.parent
SOUND = ENGINE_ROOT / "sound"
KIT = SOUND / "kit.json"
SR = 48000


# ---------------------------------------------------------------- loading

def load_kit() -> dict:
    if not KIT.is_file():
        raise SystemExit(f"no kit at {KIT}")
    return json.loads(KIT.read_text())


def resolve(name: str, kit: dict) -> Path:
    """A path, a kit-relative name, or a fragment of a filename -> the file."""
    p = Path(name)
    if p.is_file():
        return p.resolve()
    direct = SOUND / name
    if direct.is_file():
        return direct
    files = [f for sub in ("engines", "SFX Sound Effects") for f in sorted((SOUND / sub).glob("*"))
             if f.is_file()]
    low = name.lower()
    hits = [f for f in files if low in f.name.lower()]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        raise SystemExit(f"no recording matches {name!r}")
    raise SystemExit(f"{name!r} is ambiguous: " + ", ".join(h.name for h in hits[:8]))


def decode(path: Path) -> np.ndarray:
    """48 kHz mono float32, straight from the decoder."""
    out = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR),
         "-f", "f32le", "-"],
        capture_output=True, check=True)
    return np.frombuffer(out.stdout, dtype="<f4")


# ---------------------------------------------------------------- measuring

def db(x: float) -> float:
    return 20 * math.log10(max(float(x), 1e-9))


def rms_db(x: np.ndarray) -> float:
    if x.size == 0:
        return -120.0
    return db(math.sqrt(float(np.mean(np.square(x, dtype=np.float64)))))


def envelope(x: np.ndarray, step: float) -> np.ndarray:
    n = int(step * SR)
    if x.size < n:
        return np.array([rms_db(x)])
    m = x.size // n
    return np.array([rms_db(b) for b in x[:m * n].reshape(m, n)])


def shape(x: np.ndarray, step: float) -> dict:
    """Where the sound actually is: its transient and the length worth keeping."""
    env = envelope(x, step)
    if env.size == 0:
        return {"dur": 0.0, "peak_at": 0.0, "tail": 0.0, "peak_db": -120.0}
    peak = int(np.argmax(env))
    floor = env[peak] - 20.0
    tail = peak
    for i in range(peak, env.size):
        if env[i] >= floor:
            tail = i
    return {
        "dur": round(x.size / SR, 3),
        "peak_at": round(peak * step, 2),
        "tail": round((tail + 1) * step, 2),
        "peak_db": round(float(env[peak]), 1),
    }


def describe(path: Path, step: float = 0.25, bars: bool = True) -> dict:
    x = decode(path)
    info = shape(x, step)
    info.update({"file": str(path.relative_to(SOUND)) if SOUND in path.parents else str(path),
                 "rms_db": round(rms_db(x), 1),
                 "peak_db": round(db(float(np.max(np.abs(x)))), 1) if x.size else -120.0})
    if bars:
        env = envelope(x, step)
        top = float(np.max(env)) if env.size else -120.0
        print(f"{info['file']}  {info['dur']:.2f}s  rms {info['rms_db']:.1f} dB  "
              f"peak {info['peak_db']:.1f} dB  transient at {info['peak_at']:.2f}s  "
              f"worth {info['tail']:.2f}s")
        for i, e in enumerate(env):
            width = max(0, int(round((e - (top - 48.0)) / 48.0 * 48)))
            print(f"  {i * step:5.2f}s {e:7.1f}  {'#' * width}")
    return info


# ---------------------------------------------------------------- slots

def slot_specs(kit: dict, slot: str) -> list[dict]:
    """The default plus every alternate, each as a flat {id, kind, file, slice, target}."""
    s = kit["slots"][slot]
    out = [{"id": "default", "kind": s.get("kind", "file"),
            "file": s.get("file"), "synth": s.get("synth"),
            "slice": s.get("slice"), "licence": s.get("licence", "unknown"),
            "target_rms_db": s["target_rms_db"], "why": s.get("why") or s.get("role", "")}]
    for v in s.get("alternates", []):
        out.append({"kind": "file", **v})
    return out


def is_synth(spec: dict) -> bool:
    return spec.get("kind") == "synth"


def find_spec(kit: dict, slot: str, variant: str | None) -> dict:
    specs = slot_specs(kit, slot)
    if variant is None:
        return specs[0]
    for spec in specs:
        if spec["id"] == variant:
            return spec
    raise SystemExit(f"{slot} has no variant {variant!r}: " +
                     ", ".join(s["id"] for s in specs))


def cut(path: Path, start: float, end: float, target_db: float,
        rate: float = 1.0, out: Path | None = None) -> np.ndarray:
    """The slice, resampled by `rate`, normalised to the slot's target RMS."""
    x = decode(path)
    a, b = int(start * SR), int(end * SR)
    if a >= x.size:
        raise SystemExit(f"slice starts {start:.2f}s into a {x.size / SR:.2f}s file")
    seg = x[a:min(b, x.size)].astype(np.float64)
    if rate != 1.0:
        n = int(seg.size / rate)
        seg = np.interp(np.arange(n) * rate, np.arange(seg.size), seg)
    gain = 10 ** ((target_db - rms_db(seg)) / 20)
    seg = seg * gain
    peak = float(np.max(np.abs(seg)))
    if peak > 0.98:  # never hand a clipped slice to a mix
        seg *= 0.98 / peak
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR),
                        "-ac", "1", "-i", "-", "-c:a", "pcm_s16le", str(out)],
                       input=seg.astype("<f4").tobytes(), check=True)
    return seg


def synth(params: dict, target_db: float) -> np.ndarray:
    """The generated hit: a sine sliding 58 -> 40 Hz, gone in a quarter second.

    `glide` is how fast the pitch falls (1/e seconds), `decay` how fast the body dies,
    `harmonic` a little second harmonic for edge. Drawn, not recorded, so it is
    deterministic: the same numbers give the same samples on every machine.
    """
    dur = float(params["dur"])
    n = max(1, int(round(dur * SR)))
    t = np.arange(n) / SR
    k = np.exp(-t * float(params.get("glide", 2.2)))
    hz = float(params["hz_from"]) * k + float(params["hz_to"]) * (1.0 - k)
    phase = 2 * math.pi * np.cumsum(hz) / SR
    seg = np.sin(phase) * np.exp(-t / float(params["decay"]))
    harm = float(params.get("harmonic", 0.0))
    if harm:
        seg += harm * np.sin(2 * phase) * np.exp(-t / float(params.get("harmonic_decay", 0.045)))
    attack = max(1e-4, float(params.get("attack_ms", 2.0)) / 1000.0)
    seg = seg * np.minimum(1.0, t / attack)
    gain = 10 ** ((target_db - rms_db(seg)) / 20)
    seg = seg * gain
    peak = float(np.max(np.abs(seg)))
    if peak > 0.98:
        seg *= 0.98 / peak
    return seg


def write(seg: np.ndarray, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR),
                    "-ac", "1", "-i", "-", "-c:a", "pcm_s16le", str(out)],
                   input=seg.astype("<f4").tobytes(), check=True)


# ---------------------------------------------------------------- commands

def cmd_list(args, kit):
    print(f"kit {KIT.relative_to(ENGINE_ROOT)}  ({len(kit['slots'])} slots)\n")
    bad = 0
    for slot, spec in kit["slots"].items():
        print(f"{slot:<6} {spec.get('role', '')}")
        for v in slot_specs(kit, slot):
            if is_synth(v):
                mark, name = "ok  ", "(generated here, no file)"
                span = f"{v['synth']['dur']:.2f}s"
            else:
                path = SOUND / v["file"]
                mark = "ok  " if path.is_file() else "MISS"
                bad += 0 if path.is_file() else 1
                name = v["file"]
                span = f"{v['slice'][0]:.2f}-{v['slice'][1]:.2f}s"
            print(f"  {mark} {v['id']:<24} {name:<62} {span:>12}  "
                  f"{v['target_rms_db']:+.0f} dB  {v.get('licence', '?'):<12}")
            if v.get("why"):
                print(f"       {v['why']}")
        print()
    print(f"{bad} missing files" if bad else "every slot resolves")
    return 1 if bad else 0


def cmd_probe(args, kit):
    describe(resolve(args.name, kit), step=args.step)
    return 0


def cmd_cut(args, kit):
    spec = find_spec(kit, args.slot, args.variant)
    out = Path(args.out) if args.out else Path(f"/tmp/{args.slot}-{spec['id']}.wav")
    if is_synth(spec):
        seg = synth(spec["synth"], spec["target_rms_db"])
        write(seg, out)
        origin = f"generated {spec['synth']['hz_from']:.0f}->{spec['synth']['hz_to']:.0f} Hz"
    else:
        path = SOUND / spec["file"]
        seg = cut(path, spec["slice"][0], spec["slice"][1], spec["target_rms_db"],
                  rate=args.rate, out=out)
        origin = f"{path.name} {spec['slice'][0]:.2f}-{spec['slice'][1]:.2f}s"
    peak = db(float(np.max(np.abs(seg))))
    print(f"{args.slot}/{spec['id']}: {origin} -> {out}  {seg.size / SR:.2f}s "
          f"at {rms_db(seg):.1f} dB RMS, peak {peak:.1f} dB")
    return 0


def cmd_snippet(args, kit):
    """The block to paste into a film's audio/build_final.py, numbers already filled in."""
    spec = find_spec(kit, args.slot, args.variant)
    up = args.slot.upper()
    if is_synth(spec):
        s = spec["synth"]
        print(f'# generated - no file. {spec.get("why", "")}')
        print(f'{up}_SYNTH = dict(dur={s["dur"]}, hz_from={s["hz_from"]}, hz_to={s["hz_to"]}, '
              f'glide={s["glide"]}, decay={s["decay"]}, harmonic={s["harmonic"]}, '
              f'harmonic_decay={s["harmonic_decay"]}, attack_ms={s["attack_ms"]})')
        print(f'{up}_RMS_DB = {spec["target_rms_db"]:.1f}')
        return 0
    name = Path(spec["file"]).name
    a, b = spec["slice"]
    print(f'{up}_FILE = LIB / "{name}"')
    print(f'{up}_SLICE = ({a:.2f}, {b:.2f})   # {b - a:.2f} s')
    print(f'{up}_RMS_DB = {spec["target_rms_db"]:.1f}')
    if args.slot == "hit":
        print('# HIT_AT = the absolute second the closing card lands (~28.02 in a 30 s film).')
        print('# Set it from that film\'s own measurements; never paste this line as a 0.')
    if args.slot == "bed":
        print('LOOP_XFADE = 0.30')
    print(f'# {Path(spec["file"]).parent}  licence: {spec.get("licence", "unknown")}')
    print(f'# {spec.get("why", "")}')
    return 0


def cmd_check(args, kit):
    """The kit cannot rot: every file exists and every slice fits inside it."""
    problems = []
    for slot in kit.get("slots", {}):
        for v in slot_specs(kit, slot):
            if is_synth(v):
                if float(v["synth"].get("dur", 0)) <= 0:
                    problems.append(f"{slot}/{v['id']}: generated slot has no duration")
                continue
            path = SOUND / v["file"]
            if not path.is_file():
                problems.append(f"{slot}/{v['id']}: {v['file']} is missing")
                continue
            dur = decode(path).size / SR if args.deep else None
            if dur is None:
                probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                        "format=duration", "-of", "csv=p=0", str(path)],
                                       capture_output=True, text=True, check=True)
                dur = float(probe.stdout.strip())
            a, b = v["slice"]
            if not (0 <= a < b <= dur + 0.01):
                problems.append(f"{slot}/{v['id']}: slice {a}-{b}s does not fit "
                                f"{dur:.2f}s of {path.name}")
    for b in kit.get("banned", []):
        if not (SOUND / b["file"]).is_file():
            problems.append(f"banned list names a file that is not there: {b['file']}")
    for p in problems:
        print(f"FAIL {p}")
    print(f"kit check: {len(problems)} problem(s)" if problems else
          f"kit check: {sum(len(slot_specs(kit, s)) for s in kit['slots'])} slots resolve")
    return 1 if problems else 0


def main(argv):
    ap = argparse.ArgumentParser(description="the sound kit: list, probe, cut, check")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="every slot, its recording, measured state")
    ap.epilog = "slots: start, bed, roar, hit - the four a reel has, and no others"
    p = sub.add_parser("probe", help="duration, levels and 0.25 s envelope of one recording")
    p.add_argument("name", help="path, kit-relative name, or a fragment of a filename")
    p.add_argument("--step", type=float, default=0.25, help="envelope block, seconds")
    p = sub.add_parser("cut", help="write one slot's slice at its target level")
    p.add_argument("slot", choices=["start", "bed", "roar", "hit"])
    p.add_argument("--variant", default=None, help="an alternate id from the kit")
    p.add_argument("--out", default=None, help="output wav (default /tmp/<slot>-<variant>.wav)")
    p.add_argument("--rate", type=float, default=1.0, help="playback rate, e.g. 0.86")
    p = sub.add_parser("snippet", help="the constants to paste into a build_final.py")
    p.add_argument("slot", choices=["start", "bed", "roar", "hit"])
    p.add_argument("--variant", default=None, help="an alternate id from the kit")
    p = sub.add_parser("check", help="files exist and slices fit; exit 1 on rot")
    p.add_argument("--deep", action="store_true", help="decode to measure, not just ffprobe")

    args = ap.parse_args(argv)
    # probe measures a plain file, so it must work before the kit exists
    kit = {} if args.cmd == "probe" else load_kit()
    return {"list": cmd_list, "probe": cmd_probe, "cut": cmd_cut,
            "snippet": cmd_snippet, "check": cmd_check}[args.cmd](args, kit)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
