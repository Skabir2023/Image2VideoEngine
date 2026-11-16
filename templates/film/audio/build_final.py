#!/usr/bin/env python3
"""Final audio for the 1969 AMC SC/Rambler reel — 30.0 s.

The car owns the first two seconds and then hands over to the narrator without a
hard cut. The start plays at full level through 2.00 s, then a 0.60 s cosine tail
runs under the first words while the big-block idle bed grows in behind it.

  0.00 – 2.00   the engine catching: cranking, firing, settling — alone
  2.00 – 2.60   the start decays under the first words
  2.05 – 29.50  the strong big-block idle bed, ducked hard whenever a word is spoken
  28.00 – 30.00 the payoff: two seconds of the strong big-block roar, after the last word
  29.88 – 30.00 the tail fades out

The duck is built from the transcript's word times, so the bed is already down before
each word starts. Voice sits at about −14 LUFS; the bed sits 25+ dB below it while
words are spoken and only comes back up in the pauses.

Measurements, 2026-11-16: read 26.007 s, last word ends 26.000 → 28.000 absolute.

Picture (1800 frames = 30.0 s): 122 | 184 | 195 | 184 | 166 | 160 | 132 | 90 | 192 | 182 | 193
Scene 1 carries the two seconds of engine start; scene 11 holds the closing roar.
"""
import math
import re
import json
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
SFX = ROOT / "sfx"
SFX.mkdir(exist_ok=True)
SR = 48000
TOTAL = 30.0
# The mix must outlast the picture by more than a frame: `render-all.sh` muxes with
# `-shortest`, and audio cut to exactly the frame count silently drops the closing frame.
TAIL = 0.030
TARGET_LUFS = -14.2

SPEECH_IN = ROOT / "paragraph" / "line-01-v120.wav"
TRANSCRIPT = ROOT / "paragraph" / "transcript.json"
VOICE_OUT = ROOT / "final-voice.wav"
MIX_OUT = ROOT / "final-audio.wav"


def _engine_root(start):
    for parent in start.parents:
        if (parent / "sound" / "engines").is_dir():
            return parent
    raise SystemExit("cannot find the engine root above %s" % start)


LIB = _engine_root(ROOT) / "sound" / "engines"
START_ENGINE = LIB / "engine-start-idle-rev_nhumphrey_pixabay-33510.mp3"
BIG_BLOCK = LIB / "big-block-v8-rev_henaway_pixabay-90919.mp3"

# --- the car ------------------------------------------------------------------
START_SLICE = (0.10, 2.60)   # 2.50 s of cranking, firing and settling
START_FULL = 2.00            # full level until here, then the tail
START_RMS_DB = -20.0
START_ATTACK = 0.020
START_FADE_LEN = 0.60        # cosine tail: 2.00 -> 2.60

BED_SLICE = (0.45, 1.55)     # the even, sustained part of the big-block rev
BED_RMS_DB = -29.0
BED_GAIN = 7.50            # make-up after the compressor; measured pause ≈ -35 dBFS
LOOP_XFADE = 0.30
BED_IN = (2.05, 1.60)        # grows in under the decaying start and the first words

ROAR_AT = 28.00              # the last word ("badge?") ends 28.00 — the roar answers it
ROAR_SLICE = (0.55, 2.55)    # 2.00 s of the strong big-block recording, no pitch-down
ROAR_RATE = 1.00
ROAR_GAIN = 1.35

# --- the voice ----------------------------------------------------------------
LEAD = 2.00                  # two seconds of engine start before the first word
DUCK = 0.100                 # -20 dB: the bed must sit clearly lower under speech
DUCK_ATTACK = 0.020
DUCK_RELEASE = 0.220

# --- one low hit, under the closing card, and nothing else ---------------------
THUMP_AT = 28.02
THUMP_RMS_DB = -33.0

FRAMES = [122, 184, 195, 184, 166, 160, 132, 90, 192, 182, 193]
CUTS = [sum(FRAMES[:i]) / 60 for i in range(1, len(FRAMES))]


def ff(args):
    subprocess.run(["ffmpeg", "-y", "-v", "error", *args], check=True)


def rdur(p: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def read_wav(p: Path) -> bytes:
    with wave.open(str(p)) as w:
        return w.readframes(w.getnframes())


def read_samples(p: Path):
    raw = read_wav(p)
    return [int.from_bytes(raw[i:i + 2], "little", signed=True) for i in range(0, len(raw), 2)]


def write_wav(p: Path, data: bytes):
    with wave.open(str(p), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data)


def rms_db(samples) -> float:
    if not samples:
        return -120.0
    return 20 * math.log10(math.sqrt(sum(s * s for s in samples) / len(samples)) / 32768 + 1e-12)


read = rdur(SPEECH_IN)
print(f"read {read:.3f}s at speed 1.2 -> speech {LEAD:.2f}-{LEAD + read:.3f}s")

# ---- voice -------------------------------------------------------------------
ff(["-i", str(SPEECH_IN),
    "-af", f"aresample={SR},adelay={int(LEAD * 1000)}:all=1,apad",
    "-t", f"{TOTAL + TAIL}", "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(VOICE_OUT)])

voice = read_wav(VOICE_OUT)
n_total = len(voice) // 2

# ---- the duck curve, built from the words themselves -------------------------
words = json.loads(TRANSCRIPT.read_text())
spans = []
for w in words:
    a = int((w["start"] + LEAD) * SR)
    b = int((w["end"] + LEAD) * SR)
    if b > a:
        spans.append((a, b))

target = [1.0] * n_total
for a, b in spans:
    for i in range(max(0, a), min(n_total, b)):
        target[i] = DUCK

ca = 1 - math.exp(-1 / (DUCK_ATTACK * SR))
cr = 1 - math.exp(-1 / (DUCK_RELEASE * SR))
curve = [0.0] * n_total
g = 1.0
for i in range(n_total):
    t = target[i]
    g += (t - g) * (ca if t < g else cr)
    curve[i] = g
print(f"duck: {len(spans)} word spans, floor {DUCK:.3f} ({20 * math.log10(DUCK):.1f} dB)")

speech_mask = [False] * n_total
for a, b in spans:
    for i in range(max(0, a), min(n_total, b)):
        speech_mask[i] = True
pauses = [i for i in range(int(2.8 * SR), n_total) if not speech_mask[i]]
speaking = [i for i in range(n_total) if speech_mask[i]]

# ---- sources, decoded once ---------------------------------------------------
start_src = SFX / "start-src.wav"
ff(["-i", str(START_ENGINE), "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(start_src)])
start_all = read_samples(start_src)

big_src = SFX / "big-src.wav"
ff(["-i", str(BIG_BLOCK), "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(big_src)])
big_all = read_samples(big_src)

# ---- start: two seconds alone, then a slow tail under the voice --------------
a, b = int(START_SLICE[0] * SR), int(START_SLICE[1] * SR)
start_s = start_all[a:b]
start_rms = rms_db(start_s)
start_gain = 10 ** ((START_RMS_DB - start_rms) / 20)
start_n = len(start_s)
print(f"start {START_SLICE[1] - START_SLICE[0]:.2f}s  rms {start_rms:.1f} dB  "
      f"gain {start_gain:.2f} ({20 * math.log10(start_gain):+.1f} dB) -> {START_RMS_DB:.0f} dB")

start_track = [0] * n_total
for i in range(min(start_n, n_total)):
    t = i / SR
    attack = min(1.0, t / START_ATTACK)
    if t < START_FULL:
        fade = 1.0
    elif t < START_FULL + START_FADE_LEN:
        fade = math.cos((t - START_FULL) / START_FADE_LEN * math.pi / 2)
    else:
        fade = 0.0
    start_track[i] = int(start_s[i] * start_gain * attack * fade)

# ---- bed: the strong big-block, looped and ducked ----------------------------
a, b = int(BED_SLICE[0] * SR), int(BED_SLICE[1] * SR)
slice_s = big_all[a:b]
n = len(slice_s)
xf = int(LOOP_XFADE * SR)
need = n_total

looped = list(slice_s)
while len(looped) < need:
    tail = looped[-xf:]
    for i in range(xf):
        t = i / (xf - 1)
        looped[len(looped) - xf + i] = int(tail[i] * math.cos(t * math.pi / 2)
                                           + slice_s[i] * math.sin(t * math.pi / 2))
    looped.extend(slice_s[xf:n])
looped = looped[:need]

bed_raw = SFX / "engine-bed-raw.wav"
write_wav(bed_raw, b"".join(max(-32768, min(32767, s)).to_bytes(2, "little", signed=True)
                            for s in looped))
bed_rms = rms_db(looped)
bed_norm = 10 ** ((BED_RMS_DB - bed_rms) / 20)
bed_wav = SFX / "engine-bed.wav"
fade_in_at, fade_in_len = BED_IN
ff(["-i", str(bed_raw), "-af",
    f"highpass=f=38,lowpass=f=1800,"
    f"lowshelf=f=95:g=2,equalizer=f=420:width_type=o:width=1.2:g=-3,"
    f"acompressor=threshold=0.020:ratio=8:attack=10:release=220:makeup=1,"
    f"volume={bed_norm * BED_GAIN:.3f},afade=t=in:st={fade_in_at}:d={fade_in_len},"
    f"afade=t=out:st={TOTAL - 0.50}:d=0.50",
    "-t", f"{TOTAL + TAIL}", "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(bed_wav)])
print(f"big-block bed: {n / SR:.2f}s loop, {LOOP_XFADE:.2f}s crossfade, "
      f"rms {bed_rms:.1f} dB -> {BED_RMS_DB:.0f} dB")

bed_bytes = read_wav(bed_wav)
bed_track = [0] * n_total
for i in range(n_total):
    j = i * 2
    s = int.from_bytes(bed_bytes[j:j + 2], "little", signed=True)
    bed_track[i] = int(s * curve[i])

bed_lvl_pause = rms_db([bed_track[i] for i in pauses[::13]])
bed_lvl_speech = rms_db([bed_track[i] for i in speaking[::13]])
print(f"bed level: {bed_lvl_pause:.1f} dB in the pauses, {bed_lvl_speech:.1f} dB under speech "
      f"({bed_lvl_pause - bed_lvl_speech:.1f} dB of duck)")

# ---- roar: the strong big-block, after the last word -------------------------
roar_len = ROAR_SLICE[1] - ROAR_SLICE[0]
roar_out = ROAR_AT + roar_len / ROAR_RATE
roar_seg = SFX / "roar.wav"
ff(["-i", str(BIG_BLOCK), "-af",
    f"atrim=start={ROAR_SLICE[0]}:end={ROAR_SLICE[1]},asetpts=PTS-STARTPTS,"
    f"asetrate=44100*{ROAR_RATE},aresample={SR},aformat=channel_layouts=mono,"
    f"afade=t=in:st=0:d=0.020,afade=t=out:st={roar_len / ROAR_RATE - 0.30}:d=0.30,"
    f"highpass=f=35,lowpass=f=12000,volume={ROAR_GAIN},alimiter=limit=0.95",
    "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(roar_seg)])
roar_samples = read_samples(roar_seg)
roar_track = [0] * n_total
off = int(ROAR_AT * SR)
for i, v in enumerate(roar_samples):
    k = off + i
    if k >= n_total:
        break
    roar_track[k] = v
print(f"strong roar at {ROAR_AT:.2f}s for {roar_len / ROAR_RATE:.2f}s "
      f"(rate {ROAR_RATE}) -> ends {roar_out:.2f}s")

# ---- one low hit, under the closing card ------------------------------------
def _norm(sig, target_db):
    rms = math.sqrt(float(np.mean(sig.astype(np.float64) ** 2))) / 32768.0
    return sig * (10 ** ((target_db - 20 * math.log10(max(rms, 1e-9))) / 20))


def thump(seed=7):
    """A short low hit: 58 Hz sliding to 44 Hz with a fast decay."""
    n = int(0.26 * SR)
    t = np.arange(n) / SR
    f = 58 * np.exp(-t * 2.2) + 40 * (1 - np.exp(-t * 2.2))
    sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.085)
    sig += 0.35 * np.sin(4 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.045)
    return _norm(sig, THUMP_RMS_DB)


hit_track = [0] * n_total
seg = thump()
off = int(THUMP_AT * SR)
for i, v in enumerate(seg):
    j = off + i
    if 0 <= j < n_total:
        hit_track[j] += int(v)
print(f"one low hit at {THUMP_AT:.2f}s under the closing card, {THUMP_RMS_DB:.0f} dB")

# ---- sum ---------------------------------------------------------------------
out = [0] * n_total
for i in range(n_total):
    v = int.from_bytes(voice[i * 2:i * 2 + 2], "little", signed=True)
    out[i] = max(-32768, min(32767, v + bed_track[i] + start_track[i] + roar_track[i]
                             + hit_track[i]))

premix = SFX / "premix.wav"
write_wav(premix, b"".join(v.to_bytes(2, "little", signed=True) for v in out))

ff(["-i", str(premix), "-af",
    f"afade=t=out:st={TOTAL + TAIL - 0.12}:d=0.12,loudnorm=I=-14.2:TP=-4.5:LRA=14,aresample=48000",
    "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", str(MIX_OUT)])


def loud(p: Path) -> float:
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(p), "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[0-9.]+) LUFS", o)[-1])


def peak(p: Path) -> float:
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(p), "-af", "ebur128=peak=true",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"Peak:\s+(-?[0-9.]+) dBFS", o)[-1])


for _ in range(3):
    got, tp = loud(MIX_OUT), peak(MIX_OUT)
    delta = TARGET_LUFS - got
    if abs(delta) < 0.2:
        break
    tmp = MIX_OUT.with_suffix(".gain.wav")
    safe = min(delta, -3.2 - tp)
    ff(["-i", str(MIX_OUT), "-af", f"volume={safe:.2f}dB",
        "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", str(tmp)])
    tmp.replace(MIX_OUT)
    print(f"  loudness {got:.1f} -> {safe:+.2f} dB")

print(f"final {loud(MIX_OUT):.1f} LUFS, peak {peak(MIX_OUT):.1f} dBFS, {rdur(MIX_OUT):.3f}s")
print("cuts at", ", ".join(f"{c:.3f}" for c in CUTS))
