#!/usr/bin/env python3
"""Final audio for the Boss 429 reel — 18.600 s.

Voice: one Kokoro call at speed 1.2 (17.138 s), placed 0.30 s in, so speech runs
0.35 – 17.18 s. Word timings come from the transcript in
paragraph/transcript.json, which is what the picture and text are cut to.

Sound: the big-block V8 is the only engine in the film. Its sustained section is
looped with equal-power crossfades into a steady, quiet bed that sits under the
whole read and is ducked hard whenever a word is spoken, so nothing roars over the
narration. The one real rev comes after the last word, where the car answers
"Would you drive it?" and rings through the closing hold.

Picture (1116 frames = 18.600 s): 256 | 311 | 218 | 95 | 98 | 138
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
TOTAL = 18.60
TARGET_LUFS = -14.2

SPEECH_IN = ROOT / "paragraph" / "line-01-v120.wav"
VOICE_OUT = ROOT / "final-voice.wav"
MIX_OUT = ROOT / "final-audio.wav"

def _engine_root(start):
    """The engine root: the folder holding sound/ and assets/, however deep the film sits."""
    for parent in start.parents:
        if (parent / "sound" / "engines").is_dir():
            return parent
    raise SystemExit("cannot find the engine root above %s" % start)


LIB = _engine_root(ROOT) / "sound" / "engines"   # shared engine recordings
REV = LIB / "big-block-v8-rev_henaway_pixabay-90919.mp3"
BIG_SLICE = (0.45, 1.55)   # the even, sustained part of the rev — the loop source
LOOP_XFADE = 0.30          # equal-power crossfade so the loop has no seam
BED_GAIN = 0.72            # quiet: a distant big block, never a roar
BED_LEVEL = 1.00
FADE_FROM = 17.30

LEAD = 0.30
FRAMES = [256, 311, 218, 95, 98, 138]
CUTS = [sum(FRAMES[:i]) / 60 for i in range(1, 6)]

# (start, gain, playback rate, length) — only where nobody is speaking
ACCENTS = [
    (17.10, 0.92, 1.00, 3.40),  # after the last word: the car answers the question
]


def ff(args):
    subprocess.run(["ffmpeg", "-y", "-v", "error", *args], check=True)


def rdur(p: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


read = rdur(SPEECH_IN)
speech_end = LEAD + read
print(f"read {read:.3f}s at speed 1.2 -> speech {LEAD:.2f}-{speech_end:.3f}s")

ff(["-i", str(SPEECH_IN),
    "-af", f"aresample={SR},adelay={int(LEAD * 1000)}:all=1,"
           f"afade=t=out:st={FADE_FROM}:d=0.50:curve=tri,apad",
    "-t", f"{TOTAL}", "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(VOICE_OUT)])

def read_wav(p: Path) -> bytes:
    with wave.open(str(p)) as w:
        return w.readframes(w.getnframes())


def write_wav(p: Path, data: bytes):
    with wave.open(str(p), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data)


# the big block, on its own, decoded once
src = SFX / "big-src.wav"
ff(["-i", str(REV), "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(src)])

raw = read_wav(src)
samples = [int.from_bytes(raw[i:i + 2], "little", signed=True) for i in range(0, len(raw), 2)]
start_n, end_n = int(BIG_SLICE[0] * SR), int(BIG_SLICE[1] * SR)
slice_n = samples[start_n:end_n]
n = len(slice_n)
xf = int(LOOP_XFADE * SR)
need = int(TOTAL * SR)

# loop the sustained section with an equal-power crossfade on every join
looped = list(slice_n)
while len(looped) < need:
    tail = looped[-xf:]
    for i in range(xf):
        t = i / (xf - 1)
        looped[len(looped) - xf + i] = int(tail[i] * math.cos(t * math.pi / 2)
                                           + slice_n[i] * math.sin(t * math.pi / 2))
    looped.extend(slice_n[xf:n])
looped = looped[:need]

big_bed = SFX / "big-bed.wav"
write_wav(big_bed, b"".join(max(-32768, min(32767, s)).to_bytes(2, "little", signed=True)
                            for s in looped))
print(f"big-block bed: {n / SR:.2f}s loop, {LOOP_XFADE:.2f}s crossfade, {TOTAL:.2f}s")

# bed: deep and even, and ducked hard the moment the voice speaks
bed = SFX / "engine-bed.wav"
ff(["-i", str(big_bed), "-i", str(VOICE_OUT),
    "-filter_complex",
    f"[0:a]aformat=channel_layouts=mono,aresample={SR},highpass=f=32,lowpass=f=1200,"
    f"lowshelf=f=95:g=3,equalizer=f=420:width_type=o:width=1.2:g=-3,"
    f"acompressor=threshold=0.020:ratio=8:attack=10:release=220:makeup=1,"
    f"volume={BED_GAIN},afade=t=in:st=0:d=0.30[eng];"
    f"[eng][1:a]sidechaincompress=threshold=0.018:ratio=16:attack=12:release=260:makeup=1[bed]",
    "-map", "[bed]", "-t", f"{TOTAL}", "-ar", str(SR), "-ac", "1",
    "-c:a", "pcm_s16le", str(bed)])


def add(track: bytearray, data: bytes, at: float, gain: float):
    off = int(at * SR) * 2
    end = min(off + len(data), len(track))
    for i in range(off, end, 2):
        j = i - off
        src = int.from_bytes(data[j:j + 2], "little", signed=True)
        cur = int.from_bytes(track[i:i + 2], "little", signed=True)
        v = max(-32768, min(32767, cur + int(src * gain)))
        track[i:i + 2] = v.to_bytes(2, "little", signed=True)


# three revs, each cut down to its attack and tail
accents = bytearray(b"\x00\x00" * int(TOTAL * SR))
for start, gain, rate, length in ACCENTS:
    seg = SFX / f"rev-{start:.2f}.wav"
    ff(["-i", str(REV), "-af",
        f"asetrate=44100*{rate},aresample={SR},aformat=channel_layouts=mono,"
        f"atrim=0:{length},afade=t=out:st={max(0.0, length - 0.5)}:d=0.5,"
        f"highpass=f=40,lowpass=f=9000",
        "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(seg)])
    add(accents, read_wav(seg), start, gain)
    print(f"  rev at {start:.2f}s  gain {gain:.2f}  rate {rate:.2f}  {length:.1f}s")

voice_data = read_wav(VOICE_OUT)
bed_data = read_wav(bed)
n = min(len(voice_data), len(bed_data), len(accents))
summed = bytearray(n)
for i in range(0, n, 2):
    v = int.from_bytes(voice_data[i:i + 2], "little", signed=True)
    b = int.from_bytes(bed_data[i:i + 2], "little", signed=True)
    a = int.from_bytes(accents[i:i + 2], "little", signed=True)
    out = v + int(b * BED_LEVEL) + a
    summed[i:i + 2] = max(-32768, min(32767, out)).to_bytes(2, "little", signed=True)

premix = SFX / "premix.wav"
with wave.open(str(premix), "w") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(bytes(summed))

ff(["-i", str(premix), "-af", f"afade=t=out:st={TOTAL - 0.10}:d=0.10,loudnorm=I=-14.2:TP=-1.3:LRA=14,aresample=48000",
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
