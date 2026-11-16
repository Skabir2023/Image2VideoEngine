# Timing law — the voice is the clock

> Part of the engine manual. Index, read order and precedence: [AGENTS.md](../../AGENTS.md).

The voice is the clock. Nothing is placed by eye or by silence detection.

- One paragraph, one take, `speed: 1.2` **in the TTS request** (never `atempo` afterwards).
- **Every take is trimmed before it is measured.** `tools/voice_trim.py` caps each internal pause
  at `0.22 s` and re-anchors the word times to the speech blocks it measured;
  `transcript-whisper.json` keeps the raw model output. A take whose longest pause is over
  `0.22 s` is not the clock yet.
- `audio/paragraph/transcript.json` is a list of `{text, start, end}` in seconds, measured on that
  WAV. Reference build: 41 words, 17.138 s. It is the JSON sidecar that `hyperframes transcribe`
  writes beside the WAV, renamed in place.
- **Nothing parses that file at build time.** The measured times are copied into the `*_at` values
  in that film's `scenes.py` and the constants in its `audio/build_final.py`. A new voice take
  therefore means re-transcribing *and* rewriting those numbers.
- The voice is placed at `LEAD`, so **every word time in the transcript is +`LEAD`** before it is
  used for picture. `LEAD` is not a free number: it is where the start hands over, so it equals
  that start's length — `1.00 s` on the default film, `2.00 s` when the start holds full level for
  two seconds (the 30 s AMC), `0.30 s` when the picture wants the narrator sooner. It is not empty
  air: the engine start plays alone there (see [Sound law](09-sound-law.md)), so the car speaks
  before the narrator does.
- **A cut lands ~65 ms before the first word of the next line** — the picture changes in the
  pause, never on top of a word. A pause is not automatically a cut: if taking it would leave a
  scene under ~1.2 s, the beat belongs to the neighbouring scene instead (the Cutlass passes on
  two cuts for exactly that reason, and says so in its `scenes.py`).
- **Every text reveal sits on the word it belongs to.** A big card that changes mid-word is the
  classic fault of this engine; it happened once at 12.24 s and must not recur.
- Frame counts are exact: `frames = round(duration × 60)`, and the six must sum to
  `total_duration × 60` (reference: 256+311+218+95+98+138 = 1116 = 18.600 s).
- The closing card holds alone long enough for the engine to answer the final question — `1.42 s`
  on the reference build, a full `2.0 s` with the closing roar. The **last** scene is what grows;
  the others keep their frames.
