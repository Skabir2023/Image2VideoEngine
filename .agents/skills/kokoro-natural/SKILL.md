---
name: kokoro-natural
description: Make a Kokoro narration read as one continuous, natural voice instead of "read, stop, read". Use when writing or re-taking a film's voiceover on this engine — covers what Kokoro actually obeys (punctuation only), the read rules, the mandatory silence-refinement pass, how to verify the pauses, and what to rebuild afterwards.
---

# kokoro-natural — a natural read from Kokoro

Kokoro is an 82M TTS model with no style input. It ignores SSML, emotion tags, `[pause]` and ALL
CAPS. **Its whole performance comes from the punctuation you write and the voice you pick.** A
script written for the page reads like a list when it is spoken, because every full stop buys a
long break with a full intonation reset. That is the "read, stop, read, stop" fault.

Two levers fix it: **punctuation** in the text, and **a silence pass** on the take.

## 1. Write for the ear

The read is one paragraph, spoken as one thought. Rules, in order:

1. **At most two full stops, and the last one is the point.** One `.`/`?` closes the read; a second
   is allowed only at the single place where the argument genuinely turns (the film below uses it
   after "didn't fit", where the accusation becomes the cover-up). Nine stops is what makes a read
   sound like a list; two is a paragraph. Every other boundary is, in order of strength: `,`
   (short breath) · `;` (half stop, keeps the sentence alive) · `-`/`—` (a brief aside) · `:`
   (introducing the payoff). If the take still has a hole where one of the two stops sits, the
   trim pass closes it to 0.22 s like any other pause — you do not have to give up the stop.
2. **One breath per sentence.** If you cannot say it in one breath, it is two clauses, not two
   sentences.
3. **Carry the chain, not a list.** The punctuation must express the argument: "…hid a Chevrolet,
   they paid for a Rocket 350, and mechanics found a Chevy; the fan belt didn't fit." The
   semicolon is what makes it one discovery instead of three facts.
4. **Write numbers and units the way they are said.** `14,000` → `fourteen thousand` when the
   word count allows, `$550` → `five hundred fifty dollars`. Never leave `$`, `%`, `mph`, `hp` or
   an abbreviation for the model to guess.
5. **Never pad the read to fill time.** A pause is not content; if the film needs length, the
   plates carry it.
6. **Keep the page's word budget** (`tools/score.py` checks it). Expanding a number to words is
   allowed; adding new facts to read longer is not.

Good, one paragraph, no interior stops:

> In 1977, America's best-seller hid a Chevrolet — they paid for a Rocket 350, and the mechanics
> found a Chevy; the fan belt didn't fit. General Motors painted every engine blue, so nobody could
> tell. Four years later, fourteen thousand owners got paid, five hundred fifty dollars each —
> would you have looked at yours?

Bad (what caused the stop-start): `In 1977. America's best-seller hid a Chevrolet. They paid for a
Rocket 350. Mechanics found a Chevy. The fan belt didn't fit. …`

### The punctuation table (what each mark actually buys)

| Mark | Kokoro's pause | Use for |
| --- | --- | --- |
| `,` | ~0.15–0.25 s, sentence keeps flowing | every clause boundary |
| `;` | ~0.25–0.35 s, intonation holds | a turn inside one thought |
| `:` | short, anticipatory | the line before the payoff |
| `-` / `—` | brief, lighter than a comma | an aside |
| `.` | ~0.4–0.6 s **and an intonation reset** | the end of the read only |
| `?` | rising; wh-questions fall naturally | the closing question |
| `…` | 0.5–1 s, falling | almost never — it is longer than a full stop |
| `\n\n` | longer than a full stop | never inside a read |

## 2. Take it, then refine the silence — mandatory

Never ship a Kokoro take straight to the mix. The take goes through the silence pass, every time,
even when the script was written well:

```bash
python3 tools/voice.py <film> --force            # one call, whole paragraph, speed in the request
python3 tools/voice_trim.py <film>               # caps every internal pause at 0.22 s
```

`tools/voice_trim.py` keeps the untouched take as `line-01-raw.wav`, shortens only silence
(half from each side of a pause, 6 ms cosine fades), writes the refined take back to
`line-01-v120.wav`, and re-transcribes it. `--dry-run` prints the pause table and writes nothing.
Aim for: **no internal pause over 0.22 s**, and no more than ~2.3 s of total silence removed — more
than that means the script, not the take, is the problem.

The tool then **re-anchors the word times to the measured speech blocks**. Whisper's timings drift
on a short read — on this film it put "Four years later" before the full stop that precedes it and
placed the word "have" inside a −88 dB pause, up to 0.35 s out. Speech blocks are measured from the
waveform, so they are true; whisper only decides which word belongs where. The aligned table
replaces `transcript.json`, whisper's own output is kept as `transcript-whisper.json` (`--no-realign`
turns this off), and only the aligned table may be copied into `scenes.py`.

## 3. Verify before anything is built on the take

```bash
ffmpeg -hide_banner -nostats -i <film>/audio/paragraph/line-01-v120.wav \
  -af silencedetect=noise=-38dB:d=0.12 -f null - 2>&1 | grep silence_
```

Pass conditions:

- longest internal pause **≤ 0.22 s** (one deliberate beat may reach 0.28 s);
- the read is **one continuous arc** — listen once, all the way through, no restart feel;
- **2.1–2.5 words/s** at `speed 1.2`; if it is slower, the pauses came back;
- the transcript has every word, and its times were measured **after** the trim and re-anchored
  (run `voice_trim.py` again if `transcript-whisper.json` has no matching `transcript.json`);
- no word time sits inside a measured pause — check by comparing `transcript.json` against the
  `silence_start` / `silence_end` pairs from the command above.

## 4. Rebuild what the take moves

The voice is the clock. A new or refined take invalidates every time in the film:

1. re-transcribe (the trim tool does it) and read `transcript.json`;
2. copy the new word times into that film's `scenes.py` (`W`) — absolute = transcript + `LEAD`;
3. re-pick the cuts: each one inside a measured pause, ~65 ms before the next word;
4. recompute `frames` (`round(duration × 60)`; they must sum to `total × 60`), the scene list in
   `meta.json`, and `TOTAL` / `FRAMES` / `ROAR_AT` / `THUMP_AT` in `audio/build_final.py` — and check
   `TAIL`: the mix must outlast the picture by ~0.03 s, because `render-all.sh` muxes with
   `-shortest` and a bed of exactly `total × 60` frames drops the closing frame;
5. `python3 tools/scene_builder.py <film>`, rebuild the mix, render, and run every gate again;
6. rewrite `plan/TIMELINE.md` from the new measurements, and update the queue row if the film was
   already queued.

## 5. Faults and their cause

| What you hear | Cause | Fix |
| --- | --- | --- |
| read, stop, read, stop | full stops inside the read | commas/semicolons, then the trim pass |
| words clipped at the seam of a pause | trim without fade | `voice_trim.py` (6 ms cosine), never raw `silenceremove` |
| a pause that survives the trim | pause shorter than the trigger but longer than 0.22 s | lower `--max-pause` to 0.18 and re-run on `line-01-raw.wav` |
| the whole read sounds rushed | cap too small, or the script has too many clauses | 0.22 s is the floor; shorten the script instead |
| a number read wrong | digits/units left to the model | write it as words |
| the read starts with a click | leading silence trimmed to zero | keep ~40 ms (`LEAD_KEEP`) |
| the render is one frame shorter than the audio and `scan.py` counts `total × 60 − 1` | audio exactly as long as the picture under `-shortest` | raise `TAIL` in `build_final.py` to 0.03 s |
| a reveal lands on the wrong word | times copied from the unaligned whisper sidecar | re-run `voice_trim.py`, use the re-anchored `transcript.json` |
