# The sound library

Two folders, one catalogue, four slots. Every reel on the page is scored from here.

```
sound/
  kit.json                 ← the catalogue: slot → recording, slice, target level, alternates
  engines/                 ← 11 recordings of an engine running (Pixabay)
  SFX Sound Effects/       ← 223 one-shots, a compilation from at least four sources (see Provenance)
```

`sound/kit.json` is the brain, `tools/sound.py` is the hand:

```bash
python3 tools/sound.py list                      # every slot and what it resolves to
python3 tools/sound.py probe hot-rod-idle        # duration, RMS, peak, 0.25 s envelope
python3 tools/sound.py cut bed --out /tmp/bed.wav   # the slot, levelled, ready to listen to
python3 tools/sound.py check                     # files exist, slices fit; exit 1 if the kit rotted
```

Two checks guard the kit. `tools/sound.py check` proves every slot still resolves and every slice
still fits inside its file — run it after touching either folder. `tools/score.py` reads the
film's `audio/build_final.py` and fails the story gate if a recording it names is no longer in
`sound/`, so a renamed file breaks before a render instead of after one.

## The four slots

A reel has **four** sounds and no others. The law is in `.agents/manual/09-sound-law.md`; this is
the menu.

| Slot | When | Default | Level |
| --- | --- | --- | --- |
| `start` | the engine catching, alone, before the first word (1.0–2.6 s) | `engine-start-idle-rev_nhumphrey` 0.10–2.60 | −20 dBFS RMS |
| `bed` | under the whole film, ducked beneath every word | `hot-rod-idle-573183` 0.60–6.60, looped with a 0.30 s crossfade | −29 dBFS RMS |
| `roar` | the closing 2.0 s, after the last word, no voice over it | `car-engine-roaring-376881` 0.20–2.20 | −20 dBFS RMS |
| `hit` | one low hit under the closing card; the only hit in the film | **generated**: 58→40 Hz, 0.26 s | −34 dBFS RMS |

Each slot carries **alternates** chosen by the angle, not by taste:

- `start/no-start` — `Car Engine Failure`: it cranks and never catches. The *Why It Failed* angle.
- `start/modern` — an S63 V8 bark. 1980s and later; too clean for a flathead.
- `bed/quiet-idle` — the Alero's flat idle. A luxury car: present, never busy.
- `bed/diesel` — a clatter. Trucks and vans only.
- `roar/two-revs`, `roar/loud-pass` — throttle response, or a car pulling away.
- `hit/cinematic` — `mixkit-space-impact-774`, a bigger and colder boom for *Size / Looks*.
- `hit/tight-thud`, `hit/universe` — **DO NOT SHIP**; they measure better than anything else in
the folder and belong to the one group whose source could not be established. Kept only because
it is worth hearing what the generated hit has to match.

A build picks one variant per slot and **copies its numbers into the film's
`audio/build_final.py`**, because those four knobs are the film's own (the same car may want a
longer start than the last one). `cut` prints exactly what to paste. Nothing reads `kit.json` at
render time — the kit is the menu, the build is the order.

## Licences — read this before a new file joins a slot

| Source | Licence | What it allows |
| --- | --- | --- |
| `engines/*` (Pixabay) | Pixabay Content License | commercial use, no attribution, inside a video. **Not** redistribution of the audio file on its own, not claimed as your own recording. |
| `SFX Sound Effects/mixkit-*` | Mixkit Free License | commercial use inside a video, no attribution. Same no-standalone-redistribution rule. |
| `hit` (generated) | none needed | drawn by `tools/sound.py` from the numbers in `kit.json`. Nothing was sampled, so there is nothing to clear or credit — and it can be tuned tighter than any recording. |
| `SFX Sound Effects/01 Boom … 13 Metal Slam`, `Evolve_*`, `001–010.wav`, `boom sound effect.mp3` | **unclearable** | no originator, no pack name, no licence text anywhere in the folder, and no public pack matches the filenames. This is not "probably fine": unusable in a published film. Audition only. |

That is why the `hit` default is **generated** and not `11 Low Quick`, which measures better: a
better thud with no source is a liability, and a drawn one costs nothing.

## Provenance — what the files themselves prove

A filename is not a source. `sound/SFX Sound Effects/` is not one pack; it is a compilation, and
the files say so once you open them (`kit.json` → `provenance` keeps the detail):

- **The numbered cinematic set** (`01 Boom`, `02 Deep`, `03/04 Grand Hit`, `05 Impact`, `06 Drum
  Roll`, `07/08 Subsonic`, `09 Struck Down`, `10 Dark Drop`, `11 Low Quick`, `11/12 Universe Boom`,
  `13 Metal Slam`, `01 Beating … 29 Swing A`) is 96 kHz / 24-bit stereo with a **Logic Pro X BWF
  header**: a `JUNK` chunk, `time_reference`, `umid`, and an **empty originator and coding history**.
  Embedded dates run 2019-04-15 to 2019-05-07 in two vintages. A real library delivers UCS-named
  files with Soundminer metadata and a filled originator; these are bare re-exports from somebody's
  Logic session over three weeks in 2019, with no pack name and no licence. Searches for the
  filenames found no shipped pack. **Source unidentifiable → licence unclearable.**
- **`01 Evolve_Brassy Swell`, `03 Evolve_Boom Brass D`, `04 Evolve_Boom Feedback E`, `05
  Evolve_Boom Shot`, `06 Evolve_Boom Hint of Metal`, `10 Evolve_Riser Robo Drums`, `02
  Evolve_Brassy Drop.2`** are patch names from **Heavyocity EVOLVE**, a paid Kontakt library that
  does not license its sounds for published video. Banned — and their presence is the proof that
  the folder is a compilation rather than a delivery.
- **`001.wav … 010.wav`** are a third vintage and a third tool: 48 kHz / 24-bit, encoder "Adobe
  Audition 22.0 (Windows)", one date (2021-12-10), numbered only, no licence.
- **`boom sound effect.mp3`** was remuxed by ffmpeg (Lavf57.56.101) with title and album both "boom
  sound effect" — the fingerprint of a download from a video, not a library file.

Only two groups are traceable: the `mixkit-*` files (Mixkit Free License) and the files carrying a
Pixabay numeric id. Everything else in that folder is unclearable, which is why `kit.json` points
at so few of its 223 files and why the rest sit under `banned` or `rest` with a reason each.

## Measure, never guess

Two rules, both learned the hard way on this page.

1. **Decode the file and read the samples.** These recordings are not what their names or their
   waveforms look like. `engine-start-idle-rev_nhumphrey` looks like a 39 s engine and measures
   **−33 dBFS RMS, peak −20 dBFS** — a fixed `volume=0.3` on it produces silence. The recording
   used for the closing roar peaks at **+0.3 dBFS**, and **113 of the pack's 223 files peak above
   0 dBFS**, from **+0.1 to +5.2 dBFS**. Normalise each slice to its slot's target RMS and guard
   the peak; never trust a peak reading to mean it is healthy.
2. **`ffprobe` duration is fine; a frame-count envelope is not.** Container duration matched the
   decoded length on every file here, but the first attempt at drawing a level graph from frame
   counts put every transient in the wrong place. `tools/sound.py probe` decodes to 48 kHz mono
   and blocks it, and that is the only reading the kit records.

A 0.25 s envelope tells you what a file actually is. `11 Low Quick` peaks 1.00 s in and is gone by
2.5 s — a hit. `01 Boom` opens at −3 dB and is 40 dB down by six seconds — a long decaying boom,
not the quarter-second hit its name promises.

The generated hit is the one sound with nothing to measure: `sound.py cut hit` draws it from
`kit.json` and prints the same numbers every time (0.26 s, −34 dBFS RMS, peak −22.3 dBFS).

## What is never in a reel

`kit.json` keeps the list, with a reason each. The short version:

- no music, no risers, no whooshes on the cuts (the seam is a blur cut and needs no sound);
- nothing with a living being in it (applause, kids, dogs) — the plates carry no people, the sound
  must not invent one;
- no platform, game, phone or computer sounds (Discord, Mario, iPhone, Windows XP error): they
  date the reel and read as a mistake;
- no comedy (farts, cartoon splats);
- no trailer booms longer than the closing card;
- no sustained sub drones under an engine bed.

The ~165 remaining files are UI clicks, shutters, typing, ticks, paper and voices. They stay in
the folder — deleting the person's files is not the engine's call — but no slot points at them.

## Adding a file

1. Drop it in `engines/` (an engine) or `SFX Sound Effects/` (a one-shot).
2. `python3 tools/sound.py probe <fragment of the name>`; read the envelope and write down where
   the sound actually starts and ends.
3. Pick the slot it belongs to. If it belongs to none, it does not get added — the four slots are
   the law, not a starting point.
4. Add it to `kit.json` with `file`, `licence`, `slice`, `target_rms_db`, `measured` and a `why`
   that says which angle it serves. If you cannot name where the file came from, the licence is
   `unclearable` and it does not go in a slot — that is the rule the `hit` default was changed to
   satisfy.
5. `python3 tools/sound.py check` must print `kit check: N slots resolve`.
