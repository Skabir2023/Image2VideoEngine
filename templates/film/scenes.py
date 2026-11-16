#!/usr/bin/env python3
"""{{FILM}} — data only. `tools/scene_builder.py` writes the compositions from this file.

This is the skeleton the scaffolder lays down. It carries **no numbers**, because every number in
a finished `scenes.py` is a measurement of that film's own voice and sound, and an estimate here
would build a film that is quietly out of sync. Fill it in this order:

  1. `audio/paragraph/line-01-v120.wav` — one Kokoro take of the whole paragraph, speed 1.2.
  2. `npx hyperframes transcribe` that file → `transcript.json`; copy the word times into `W`,
     each + `LEAD`, because the picture clock starts where the film does, not where the voice does.
  3. `LEAD` is 1.00 s for the usual one-second engine start (2.00 for a film that opens on a
     two-second start, as the 30 s builds do). `PAD` is `LEAD - 0.30`, the shift applied to any
     time measured at the old lead; it is 0.00 when the transcript is measured fresh.
  4. Split the film into scenes on the pauses: a cut lands ~65 ms **before** the next word.
     `frames = round(duration * 60)`, and the frames must sum to `total * 60` exactly.
  5. One plate per 3 s: `plates = ceil(seconds / 3)`, the six fixed angles first.

## The scene dict

    dict(
        file="s01-hero", n=1, frames=122,
        still="01_hero_front34.png",                # a bare filename in stills/
        seed=11, focus="50% 56%", zoom0=1.06,       # the camera; seed keeps grain deterministic
        scrim="top",                                # "top" | "bottom" — keeps the card legible
        blur_in=False, blur_out=True,               # the seam at this scene's head and tail
        shots=[dict(t=0, dur="full", move="push", by=0.12),
               dict(t=0, dur="full", move="truckR", by=22)],
        kick="1969 · AMC SC/RAMBLER", kick_at=0.18,
        big=[("1,512 CARS", "small"), ("FOR A 500-CAR RULE", "red")], b1_at=0.42, b2_at=0.62,
        b2_size="small",                            # only when the second line needs 96 px
        roll=dict(dur=0.88, seed=3), fly=True,      # TX.roll for every number, never flat text
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),

Times are **absolute film time** — the builder converts them to scene time and refuses one that
lands outside its own scene.
"""
FILM = "{{FILM}}"
COMPOSITION_ID = "{{ID}}"
FPS = 60
LEAD = 1.00      # 1.00 s of start alone; 2.00 for a film that opens on a two-second start
PAD = 0.00       # LEAD - 0.30 for the 30 s builds; 0.00 when the transcript is measured fresh

W = {
    # "first": 0.00,  ==  transcript time + LEAD
}

SCENES = [
    # one dict per shot, in the shape documented above
]

if not SCENES or not W:
    raise SystemExit(
        f"{__file__} is a skeleton: it carries no measurements, so building it would put every\n"
        "cut and every card in the wrong place.\n"
        "  Fill LEAD, W and SCENES from this film's own transcript, then build again.\n"
        "  The shape of each scene dict is in the docstring at the top of this file."
    )
