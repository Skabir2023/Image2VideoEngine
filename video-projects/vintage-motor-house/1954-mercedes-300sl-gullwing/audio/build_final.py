#!/usr/bin/env python3
"""Final audio for the Mercedes 300SL Gullwing reel — 18.8 s.

The car is on the whole time, and it never covers a word.

  0.00 – 1.00   the engine catching: cranking, firing, settling to idle — alone
  1.00          the first word lands, and the car drops behind it at once
  1.05 – 18.40  a low idle bed, ducked hard the moment any word is spoken
  16.60 – 18.61 the payoff: two seconds of the engine roaring, after the last word
  18.68 – 18.80 the tail fades out, engine gone

The duck is not a compressor guessing at speech: it is built from the transcript's
word times, so the bed is already down before each word starts. Voice sits at about
−14 LUFS; the bed sits 25+ dB below it while words are spoken and only comes back up
in the pauses.

On top of the car and the voice there are two effect layers, both synthesised here
from noise and sine tones so the film needs no extra audio files:

  * one low hit at 16.80 s, under the closing card only
  * nothing else: no whooshes on the cuts, no hits under the numbers, no music
  * a low impact under the big numbers and the closing card

Both sit well under the voice on purpose: they mark a cut, they never mask a word.

Picture (1128 frames = 18.8 s): 150 | 132 | 86 | 180 | 89 | 128 | 144 | 85 | 134
Scene 1 carries the extra second of engine start; scene 9 holds the closing roar.
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
TOTAL = 18.8
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
ENGINE = LIB / "engine-start-idle-rev_nhumphrey_pixabay-33510.mp3"

# --- the car ------------------------------------------------------------------
# The start owns the whole first second, before a word is spoken, so it plays at full
# level there: START_DUCK_FLOOR only trims it if a word ever begins inside the window.
START_SLICE = (0.10, 1.10)   # 1.00 s of cranking, firing, settling
START_RMS_DB = -20.0
START_DUCK_FLOOR = 0.90
BED_SLICE = (14.00, 16.00)
BED_RMS_DB = -29.0
BED_GAIN = 1.00
LOOP_XFADE = 0.30
BED_IN = (1.05, 0.80)        # grows out of the start as the voice begins

ROAR_AT = 16.60              # the last word ("legend?") ends 16.51 — the roar answers it
ROAR_SLICE = (27.72, 29.45)  # one clean rev, taken whole
ROAR_RATE = 0.86
ROAR_GAIN = 1.00

# --- the voice ----------------------------------------------------------------
LEAD = 1.00                  # one second of engine start before the first word
DUCK = 0.100                 # -20 dB: the bed must sit clearly lower under speech
DUCK_ATTACK = 0.020
DUCK_RELEASE = 0.220

# --- one low hit, under the closing card, and nothing else ---------------------
# No whooshes on the cuts and no hits under the numbers. The single exception is the
# card that asks the question: one low hit lands with it, on top of the roar, so the
# close has weight without decorating every seam.
THUMP_AT = 16.80
THUMP_RMS_DB = -33.0

FRAMES = [150, 132, 86, 180, 89, 128, 144, 85, 134]
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
    "-t", f"{TOTAL}", "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(VOICE_OUT)])

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
pauses = [i for i in range(int(1.8 * SR), n_total) if not speech_mask[i]]
speaking = [i for i in range(n_total) if speech_mask[i]]

# ---- source, decoded once ----------------------------------------------------
src = SFX / "engine-src.wav"
ff(["-i", str(ENGINE), "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(src)])
raw = read_wav(src)
src_s = [int.from_bytes(raw[i:i + 2], "little", signed=True) for i in range(0, len(raw), 2)]

# ---- start -------------------------------------------------------------------
a, b = int(START_SLICE[0] * SR), int(START_SLICE[1] * SR)
start_s = src_s[a:b]
start_rms = rms_db(start_s)
start_gain = 10 ** ((START_RMS_DB - start_rms) / 20)
start_n = len(start_s)
print(f"start {START_SLICE[1] - START_SLICE[0]:.2f}s  rms {start_rms:.1f} dB  "
      f"gain {start_gain:.2f} ({20 * math.log10(start_gain):+.1f} dB) -> {START_RMS_DB:.0f} dB")

start_track = [0] * n_total
for i in range(min(start_n, n_total)):
    fade = min(1.0, i / (0.020 * SR), (start_n - i) / (0.150 * SR))
    ducked = START_DUCK_FLOOR + (1 - START_DUCK_FLOOR) * curve[i]
    start_track[i] = int(start_s[i] * start_gain * fade * ducked)

# ---- bed ---------------------------------------------------------------------
a, b = int(BED_SLICE[0] * SR), int(BED_SLICE[1] * SR)
slice_s = src_s[a:b]
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
    f"highpass=f=42,lowpass=f=2200,"
    f"equalizer=f=170:width_type=o:width=1.2:g=-3,equalizer=f=820:width_type=o:width=1.5:g=1.5,"
    f"acompressor=threshold=0.020:ratio=8:attack=10:release=220:makeup=1,"
    f"volume={bed_norm * BED_GAIN:.3f},afade=t=in:st={fade_in_at}:d={fade_in_len},"
    f"afade=t=out:st={TOTAL - 0.40}:d=0.40",
    "-t", f"{TOTAL}", "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(bed_wav)])
print(f"engine bed: {n / SR:.2f}s loop, {LOOP_XFADE:.2f}s crossfade, "
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

# ---- roar --------------------------------------------------------------------
roar_len = ROAR_SLICE[1] - ROAR_SLICE[0]
roar_out = ROAR_AT + roar_len / ROAR_RATE
roar_seg = SFX / "roar.wav"
ff(["-i", str(ENGINE), "-af",
    f"atrim=start={ROAR_SLICE[0]}:end={ROAR_SLICE[1]},asetpts=PTS-STARTPTS,"
    f"asetrate=44100*{ROAR_RATE},aresample={SR},aformat=channel_layouts=mono,"
    f"afade=t=in:st=0:d=0.020,afade=t=out:st={roar_len / ROAR_RATE - 0.30}:d=0.30,"
    f"highpass=f=40,lowpass=f=11000,volume={ROAR_GAIN}",
    "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(roar_seg)])
roar_data = read_wav(roar_seg)
roar_track = [0] * n_total
off = int(ROAR_AT * SR)
for i in range(0, len(roar_data), 2):
    k = off + i // 2
    if k >= n_total:
        break
    roar_track[k] = int.from_bytes(roar_data[i:i + 2], "little", signed=True)
print(f"roar at {ROAR_AT:.2f}s for {roar_len / ROAR_RATE:.2f}s (rate {ROAR_RATE}) -> ends {roar_out:.2f}s")

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
    f"afade=t=out:st={TOTAL - 0.12}:d=0.12,loudnorm=I=-14.2:TP=-1.3:LRA=14,aresample=48000",
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
    safe = min(delta, -1.0 - tp)
    ff(["-i", str(MIX_OUT), "-af", f"volume={safe:.2f}dB",
        "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", str(tmp)])
    tmp.replace(MIX_OUT)
    print(f"  loudness {got:.1f} -> {safe:+.2f} dB")

print(f"final {loud(MIX_OUT):.1f} LUFS, peak {peak(MIX_OUT):.1f} dBFS, {rdur(MIX_OUT):.3f}s")
print("cuts at", ", ".join(f"{c:.3f}" for c in CUTS))
