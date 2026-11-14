#!/usr/bin/env python3
"""Final audio for the Eldorado Brougham reel — 20.000 s.

The film opens on the engine: 2.40 s of it starting and settling to idle, nobody
talking, and the hood shut. The voice (one Kokoro call at speed 1.2, 15.046 s)
comes in at 2.40; the last word lands at 17.20.

It does not stop there. At 17.35 the idle hands over — 0.35 s equal-power crossfade —
to the throttle run at the end of the same recording (34.20 – 38.00 of the source).
At 17.72, on the end card, a second Kokoro take asks the viewer something over that
rev — "Roof, or glove box, which would you keep?". The roar is not turned down for it:
that recording sits below 400 Hz and 30 dB under the voice in the speech band, so the
close stays at full throttle to the fade with the question mixed on top.

Sound is one recording, not a stack: `engine-start-idle-rev_nhumphrey_pixabay-33510`
plays in full from 0 to 8.60 s — the actual start — and from there the even idle
section (3.10 – 8.60) is looped with equal-power crossfades so the car keeps
ticking under the rest of the read. The bed is sidechain-ducked by the voice; the
closing roar is not ducked at all — the ask is placed above it instead.

Picture (1200 frames = 20.000 s): 354 | 95 | 94 | 33 | 170 | 295 | 159
"""
import math
import re
import subprocess
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SFX = ROOT / "sfx"
SFX.mkdir(exist_ok=True)
SR = 48000
TOTAL = 20.00
TARGET_LUFS = -14.2

SPEECH_IN = ROOT / "paragraph" / "line-01-v120.wav"
CTA_IN = ROOT / "cta" / "cta-01-v120.wav"
CTA_AT = 17.72             # the spoken ask lands on the end card, over the revs
CTA_OUT = ROOT / "final-cta.wav"
VOICE_OUT = ROOT / "final-voice.wav"
MIX_OUT = ROOT / "final-audio.wav"

def _engine_root(start):
    """The engine root: the folder holding sound/ and assets/, however deep the film sits."""
    for parent in start.parents:
        if (parent / "sound" / "engines").is_dir():
            return parent
    raise SystemExit("cannot find the engine root above %s" % start)


LIB = _engine_root(ROOT) / "sound" / "engines"   # shared engine recordings
START = LIB / "engine-start-idle-rev_nhumphrey_pixabay-33510.mp3"
TAKE = (0.00, 8.60)        # the real start, played once
LOOP = (3.10, 8.60)        # the even idle inside it — the loop source
LOOP_XFADE = 0.50          # equal-power crossfade so the join has no seam
ENGINE_GAIN = 0.94         # present at the top, never a roar
START_LIFT = 1.28          # the first 2.2 s sit up: the start is the hook, it should be heard
START_HOLD = 2.25          # where the lift begins to fall away
START_FALL = 0.45
DUCK = "sidechaincompress=threshold=0.020:ratio=12:attack=18:release=450:makeup=1"
BED_OUT_AT = 17.10         # the idle gets out of the way of the revs
BED_END = 17.40

REV = (34.20, 37.90)       # the throttle run at the tail of the same recording
REV_AT = 17.35             # when it takes over in the film — the close
REV_XFADE = 0.35
ROAR_GAIN = 1.45
CTA_GAIN = 1.19            # the ask speaks up over the roar
# The close roars at full level from 17.35 to the fade - no dip, exactly as it ended
# before the ask existed. It needs none: this recording lives below 400 Hz, and in the
# 1.5-4 kHz band where the words live it sits 30 dB under the voice, so the question
# rides on the roar rather than through it.

LEAD = 2.40
FRAMES = [354, 95, 94, 33, 170, 295, 159]
CUTS = [sum(FRAMES[:i]) / 60 for i in range(1, 7)]


def ff(args):
    subprocess.run(["ffmpeg", "-y", "-v", "error", *args], check=True)


def rdur(p: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


read = rdur(SPEECH_IN)
speech_end = LEAD + read
print(f"read {read:.3f}s at speed 1.2 -> speech {LEAD:.2f}-{speech_end:.3f}s")

read_cta = rdur(CTA_IN)
ff(["-i", str(SPEECH_IN),
    "-af", f"aresample={SR},adelay={int(LEAD * 1000)}:all=1,"
           f"afade=t=out:st={TOTAL - 0.60}:d=0.55:curve=tri,apad",
    "-t", f"{TOTAL}", "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(VOICE_OUT)])

# the ask sits on its own track, so the roar can duck to it and nothing else
ff(["-i", str(CTA_IN),
    "-af", f"aresample={SR},volume={CTA_GAIN},adelay={int(CTA_AT * 1000)}:all=1,apad",
    "-t", f"{TOTAL}", "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(CTA_OUT)])
print(f"ask {read_cta:.3f}s from {CTA_AT:.2f}s -> ends {CTA_AT + read_cta:.2f}s")


def read_wav(p: Path) -> bytes:
    with wave.open(str(p)) as w:
        return w.readframes(w.getnframes())


def write_wav(p: Path, data: bytes):
    with wave.open(str(p), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data)


# the engine, decoded once
src = SFX / "engine-src.wav"
ff(["-i", str(START), "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(src)])
raw = read_wav(src)


def s(i):                      # int16 little-endian pair -> signed sample
    return int.from_bytes(raw[i:i + 2], "little", signed=True)


def pack(vals):
    return b"".join(max(-32768, min(32767, v)).to_bytes(2, "little", signed=True) for v in vals)


def slice_src(a, b):
    return [s(i) for i in range(int(a * SR) * 2, int(b * SR) * 2, 2)]


need = int(TOTAL * SR)
bed_need = int(REV_AT * SR)
take = slice_src(*TAKE)[:bed_need]
loop = slice_src(*LOOP)
xf = int(LOOP_XFADE * SR)

# continue the take by looping the idle, equal-power on every join
track = list(take)
while len(track) < bed_need:
    tail = track[-xf:]
    for i in range(xf):
        t = i / (xf - 1)
        track[len(track) - xf + i] = int(tail[i] * math.cos(t * math.pi / 2)
                                        + loop[i] * math.sin(t * math.pi / 2))
    track.extend(loop[xf:])
track = track[:bed_need]

# the idle hands over to the throttle run: same recording, equal-power crossfade
rev = slice_src(*REV)
rx = int(REV_XFADE * SR)
for i in range(rx):
    t = i / (rx - 1)
    track[len(track) - rx + i] = int(track[len(track) - rx + i] * math.cos(t * math.pi / 2)
                                     + rev[i] * math.sin(t * math.pi / 2))
track.extend(rev[rx:])
track = track[:need]

engine_raw = SFX / "engine-track.wav"
write_wav(engine_raw, pack(track))
print(f"bed: {TAKE[1] - TAKE[0]:.2f}s take + {LOOP[1] - LOOP[0]:.2f}s idle loop "
      f"({LOOP_XFADE:.2f}s xfade) -> {REV_AT:.2f}s")
print(f"roar: source {REV[0]:.2f}-{REV[1]:.2f} from {REV_AT:.2f}s ({REV_XFADE:.2f}s xfade), "
      f"{TOTAL - REV_AT:.2f}s of engine with no voice")

# the bed: soft, low, and ducked hard the moment the voice speaks
bed = SFX / "engine-bed.wav"
ff(["-i", str(engine_raw), "-i", str(VOICE_OUT),
    "-filter_complex",
    f"[0:a]aformat=channel_layouts=mono,aresample={SR},atrim=0:{BED_END:.2f},"
    f"highpass=f=30,lowpass=f=2600,lowshelf=f=90:g=3,equalizer=f=520:width_type=o:width=1.4:g=-2,"
    f"volume={ENGINE_GAIN},afade=t=in:st=0:d=0.20,"
    f"afade=t=out:st={BED_OUT_AT}:d={BED_END - BED_OUT_AT:.2f}:curve=tri,apad[eng];"
    f"[eng][1:a]{DUCK}[bed]",
    "-map", "[bed]",    "-t", f"{TOTAL}", "-ar", str(SR), "-ac", "1",
    "-c:a", "pcm_s16le", str(bed)])

# the start is the first thing anyone hears, so it gets its own lift, gone before the voice
bed_raw = read_wav(bed)
lifted = []
for i in range(len(bed_raw) // 2):
    t = i / SR
    if t < START_HOLD:
        k = START_LIFT
    elif t < START_HOLD + START_FALL:
        k = 1 + (START_LIFT - 1) * 0.5 * (1 + math.cos(math.pi * (t - START_HOLD) / START_FALL))
    else:
        k = 1.0
    v = int.from_bytes(bed_raw[i * 2:i * 2 + 2], "little", signed=True) * k
    lifted.append(int(v))
write_wav(bed, pack(lifted))

# the roar: full band, more low end, its own place in the timeline, at full level from
# the cut to the fade — the question is mixed onto it, it is not turned down for it
roar = SFX / "engine-roar.wav"
rev_len = TOTAL - REV_AT
ff(["-i", str(engine_raw),
    "-af", f"atrim={REV_AT}:{TOTAL},asetpts=N/SR/TB,"
           f"highpass=f=32,lowpass=f=7200,lowshelf=f=70:g=5,lowshelf=f=140:g=2,"
           f"volume={ROAR_GAIN},afade=t=in:st=0:d=0.05,"
           f"afade=t=out:st={rev_len - 0.20:.2f}:d=0.20:curve=tri,"
           f"adelay={int(REV_AT * 1000)}:all=1,apad",
    "-t", f"{TOTAL}", "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(roar)])


def mix(paths, out):
    ins = []
    for p in paths:
        ins += ["-i", str(p)]
    n = len(paths)
    fc = "".join(f"[{i}:a]" for i in range(n)) + f"amix=inputs={n}:normalize=0:duration=longest,alimiter=limit=0.98"
    ff([*ins, "-filter_complex", fc, "-t", f"{TOTAL}", "-ar", str(SR), "-ac", "1",
        "-c:a", "pcm_s16le", str(out)])


premix = SFX / "premix.wav"
mix([VOICE_OUT, CTA_OUT, bed, roar], premix)

ff(["-i", str(premix), "-af",
    f"afade=t=out:st={TOTAL - 0.10}:d=0.10,loudnorm=I={TARGET_LUFS}:TP=-1.3:LRA=14,aresample=48000",
    "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", str(MIX_OUT)])


def loud(p: Path) -> float:
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(p), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[0-9.]+) LUFS", out)[-1])


def peak(p: Path) -> float:
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(p), "-af", "ebur128=peak=true",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"Peak:\s+(-?[0-9.]+) dBFS", out)[-1])


for _ in range(3):
    got, tp = loud(MIX_OUT), peak(MIX_OUT)
    delta = TARGET_LUFS - got
    if abs(delta) < 0.2:
        break
    tmp = MIX_OUT.with_suffix(".gain.wav")
    safe = min(delta, -1.0 - tp)
    ff(["-i", str(MIX_OUT), "-af", f"volume={safe:.2f}dB",
        "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", str(tmp)])
    tmp.replace(MIX_OUT)
    print(f"  loudness {got:.1f} -> {safe:+.2f} dB")

print(f"final {loud(MIX_OUT):.1f} LUFS, peak {peak(MIX_OUT):.1f} dBFS, {rdur(MIX_OUT):.3f}s")
print("cuts at", ", ".join(f"{c:.3f}" for c in CUTS))
