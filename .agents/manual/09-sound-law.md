# Sound law — four slots, one voice

> Part of the engine manual. Index, read order and precedence: [AGENTS.md](../../AGENTS.md).

One engine, one voice, nothing that competes with a word. **Four slots, always**, and the kit
names the recording for each: `sound/kit.json` is the menu, the film's `audio/build_final.py` is
the order. The site of every number below is `sound/README.md` and `python3 tools/sound.py list`.

1. **Start, at the head, before the first word** — the engine catching while nothing else is
   happening, so it is the first thing the viewer hears. `start` slot: default
   `engine-start-idle-rev_nhumphrey` `0.10–2.60 s`, level-matched to `−20 dBFS` RMS (that
   recording measures `−33 dBFS`; measure and normalise, never guess a multiplier). **The angle
   picks the variant**: `start/no-start` (`Car Engine Failure`, cranks and never catches) for *Why
   It Failed*, `start/modern` for 1980s and later. It ends as the first word starts: `LEAD` in
   both `scenes.py` and `build_final.py`, and scene 1 is longer than its picture needs. The
   handoff is two-stage, not a stop: `START_FULL` holds full level, then a cosine fade
   (`START_FADE_LEN`) takes it down *under* the first words while the bed (`BED_IN`) grows up
   through that decay — the start is never cut off on a word, and the two never leave a gap.
2. **Bed, low, all the way through** — `bed` slot: default `hot-rod-idle-573183` `0.60–6.60 s`
   (6.0 s of the evenest idle in the library), looped with a `0.30 s` equal-power crossfade,
   highpass `42 Hz`, lowpass `2.2 kHz`, compressed flat, level-matched to about `−29 dBFS` RMS. It
   fades in under the decaying start so it grows out of it instead of fighting it, and it never
   stops for the rest of the film. `bed/quiet-idle` for a luxury car, `bed/diesel` for a truck,
   `bed/classic` is the flat `14.00–16.00 s` idle the first three films used.
3. **Roar, `2.0 s`, after the last word, with no voice over it** — the car answers and nothing
   talks across it. `roar` slot: default `car-engine-roaring-376881` `0.20–2.20 s`, which is
   front-loaded and gone in the two seconds; `roar/two-revs` for throttle response,
   `roar/loud-pass` for a car pulling away. Give the last scene that two extra seconds of picture
   with a camera shake on the hit. The roar starts on the frame the closing card lands, after the
   final word has finished, and the tail fades out clean. `ROAR_RATE` pitches the slice with
   `asetrate` (the Cutlass takes `0.86` — a heavier, slower car), which lengthens it too, so the
   scene end is computed from `roar_len / ROAR_RATE`, never from the slice length alone.
4. **One hit, under the closing card** — `hit` slot: default is **generated**, not recorded:
   `58→40 Hz`, `0.26 s`, at `−34 dBFS` RMS, drawn by `tools/sound.py` from the numbers in
   `kit.json`, so it lands *with* the card and there is no source to clear. It is the only hit in
   the film. `hit/cinematic` (`mixkit-space-impact-774`, `0.00–1.30 s`) is the bigger, colder boom
   for *Size / Looks*. **Never** `tight-thud` or `universe`, however good they measure: they are
   in the numbered pack whose source could not be established, so their licence is `unclearable`.

**The kit is a menu, not a dependency.** A build copies its slot's slice and target RMS into the
film's own knobs — the same car may want a longer start than the last one — so nothing reads
`kit.json` at render time and a film keeps rendering if the library changes.
`tools/sound.py cut <slot> --variant <id>` prints exactly the numbers to paste. `tools/score.py`
fails a film whose `build_final.py` names a recording that is not in `sound/`, and
`tools/sound.py check` fails if a slice no longer fits its file.

**Measure, never infer.** Decode the file at 48 kHz mono and block it (`python3 tools/sound.py
probe <name>`); a filename and a waveform picture both lie. `01 Boom.wav` opens at `−3 dB` and is
40 dB down by six seconds — a long decaying boom, not the quarter-second hit its name promises;
**113 of the pack's 223 files peak above 0 dBFS** (`+0.1` to `+5.2`), so normalise down to the
slot and guard the peak. The `sound/engines/` recordings are the opposite trap — the nine measure
**`−33.4` to `−11.2 dBFS` RMS**, a 22 dB spread inside one folder, so a fixed multiplier is wrong
twice over: too quiet for the default start, too loud for the bed. Level-match every slice to its
target RMS in the build script, and print the measured level in the pauses and under speech. What
must never be in a reel — music, risers, whooshes, cartoon and platform sounds, anything with a
living being — is listed with a reason in `sound/kit.json` under `banned`.

**A filename is not a source, and `SFX Sound Effects/` is not one pack.** It is a compilation from
at least four vintages: a numbered Logic Pro X set with an empty originator and no licence
(`unclearable`), seven Heavyocity EVOLVE patch names from a paid library (banned), a set of Adobe
Audition one-shots numbered `001–010`, and one ffmpeg-remuxed download. Only the `mixkit-*` and
Pixabay-id files have a traceable licence. `sound/kit.json` → `provenance` records how each group
is identified; a new file whose source cannot be named gets `licence: "unclearable"` and stays out
of a slot. When the choice is a better-measuring unclearable recording or a generated one, the
engine generates: nothing to clear, and it can be tuned tighter than the recording was.

**Ducking is built from the transcript, not from a compressor guessing.** Read the word times, set
the bed to `0.100` (−20 dB) across every spoken word and `1.0` in the gaps, then smooth with
`20 ms` attack and `220 ms` release. The gap level is what the viewer hears; the moment a word
begins the bed drops far below it — measured result to keep: about **−35 dB in the pauses** and
**−52 dB under speech**, 35 dB+ below the voice, so the car is felt under the words and never
heard over one.

- **No revs under speech.** Accents live in gaps only; the two allowed ones are the start and the
  closing roar.
- **The hit lands on the closing card, and nowhere else** — a beat after the roar opens, so the
  close has weight: `28.02 s` on the 30 s AMC, `19.46 s` on the 21.5 s Cutlass. The published
  Boss 429 was mixed without one, which is why its timeline ends “no low hits, no whooshes”.
- `0.10 s` fade-out at the tail. **No whooshes on the cuts, no hits under the numbers, no music**
  — the change of picture is a blur cut and needs no sound; a whoosh on every seam is the fastest
  way to make a reel feel cheap.
- **The mix is written `0.03 s` longer than the picture** — `TAIL = 0.030` beside `TOTAL`. The mux
  (`tools/render-all.sh`) uses `-shortest`, so the audio must never be the shorter stream:
  measured on a 1800-frame picture, 30.000 s of audio keeps 1800 frames and 29.983 s (one frame
  short) keeps **1798** — the close loses two frames for a one-frame deficit. Every `TOTAL` in
  `build_final.py` becomes `TOTAL + TAIL`, including `afade=t=out:st={TOTAL + TAIL - 0.12}`. Never
  set `TOTAL` to a rounded `frames / 60`; that is how the deficit starts.
- Master: **−14.2 LUFS integrated, true peak no higher than −1.3 dBFS**. The speech section alone
  must measure about −14.2 LUFS, so the voice is loud enough on its own. Get there with a
  **peak-guarded loop**, not one `loudnorm` pass: measure `I` and true peak on the mix and apply
  `volume = min(target − I, −3.2 − peak)`, repeating until within `0.2 LU` — the loudness is
  corrected without the limiter eating the roar.
- **The mux adds true-peak overshoot.** `tools/render-all.sh` encodes the mix to AAC 192k, which
  lifts inter-sample peaks about **1.8 dB** above the WAV's sample peak — a mix that measures
  `−2.2 dBFS` as a WAV can arrive at `−0.1 dBTP` in the MP4 and fail the gate. Set `loudnorm` to
  `TP=-4.5` in the film's `build_final.py`, leave the headroom, and measure
  `loudnorm=print_format=summary` on the **delivered MP4**, not the WAV.
- A `2.0 s` roar means the film is `2 s` longer than the voice: extend the **last** scene, keep
  the others, and re-render — never squeeze the roar in under the final words.
- All knobs live in the first 40 lines of that film's `audio/build_final.py`. Change numbers, not
  structure.
