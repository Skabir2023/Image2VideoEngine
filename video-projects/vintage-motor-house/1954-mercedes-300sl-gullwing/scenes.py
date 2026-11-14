#!/usr/bin/env python3
"""The 300SL Gullwing reel — data only. `tools/scene_builder.py` writes the scenes.

Voice: Kokoro am_michael, speed 1.2 — one chained story, 44 words:

    "Mercedes built a race car, whose frame was too high to climb over, so the doors
     went up. They built only 1,400 of them. That body still hit 161 miles per hour,
     because fuel went straight into the cylinder. Would you dare drive a legend?"

Transcript: audio/paragraph/transcript.json, measured on that WAV. LEAD is the
engine-start window: one full second of the car catching before the first word, and
every time below is absolute film time (word start + 1.00), so PAD is 0.

Cuts land in the measured silences, ~40 ms before the word that opens the next shot —
2.500 | 4.700 | 6.133 | 9.133 | 10.617 | 12.750 | 15.150 | 16.567.

Frames are exact and sum to the film: 1128 frames = 18.800 s at 60 fps.

Build with:  python3 tools/scene_builder.py video-projects/vintage-motor-house/1954-mercedes-300sl-gullwing
"""
FILM = "Doors That Opened To Sky"
COMPOSITION_ID = "gullwing-reel"
FPS = 60
LEAD = 1.00
PAD = 0.00

W = {
    "Mercedes": 1.05, "race": 1.99, "frame": 2.82, "too": 3.32,
    "doors": 4.96, "went": 5.24, "They": 6.17, "only": 6.86, "1400": 7.23,
    "That": 9.17, "still": 9.88, "161": 10.67, "miles": 11.52,
    "because": 12.87, "fuel": 13.13, "straight": 13.59,
    "Would": 15.19, "dare": 15.56,
}

SCENES = [
    dict(
        file="s01-hero", n=1, frames=150,
        still="01_hero_front34.png", seed=11, focus="50% 58%", zoom0=1.05,
        # no focus-in on shot 1: frame 0 is the post thumbnail and must read instantly
        scrim="top", blur_in=False, blur_out=True, leak=True,
        shots=[dict(t=0, dur="full", move="push", by=0.10),
               dict(t=0, dur="full", move="truckR", by=28)],
        kick="1954 · MERCEDES 300SL", kick_at=W["Mercedes"],
        big=[("RACE CAR", ""), ("", "")], b1_at=W["race"], b2_at=9.9, b2_size="",
        rule=2.10, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        file="s02-side", n=2, frames=132,
        still="02_side.png", seed=23, focus="50% 54%", zoom0=1.02,
        scrim="bottom", blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="truckR", by=46),
               dict(t=0, dur="full", move="push", by=0.05)],
        kick=None, kick_at=None, big=[("FRAME", ""), ("TOO HIGH", "red")],
        b1_at=W["frame"], b2_at=W["too"], b2_size="",
        rule=4.30, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        file="s03-rear", n=3, frames=86,
        still="03_rear.png", seed=31, focus="50% 54%", zoom0=1.04,
        scrim="bottom", blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="pull", by=0.08),
               dict(t=0, dur="full", move="truckL", by=22)],
        kick=None, kick_at=None, big=[("DOORS", ""), ("WENT UP", "red")],
        b1_at=W["doors"], b2_at=W["went"], b2_size="",
        rule=5.55, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        file="s04-star", n=4, frames=180,
        still="08_star.png", seed=43, focus="50% 50%", zoom0=1.04,
        scrim="bottom", scrim_gain=1.20, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.13),
               dict(t=0.30, dur="rest", move="craneDown", by=16)],
        # no kicker on this plate: grey mono over gold chrome does not read
        kick=None, kick_at=None,
        big=[("1,400", ""), ("", "")], b1_at=W["1400"], b2_at=9.9, b2_size="",
        roll=dict(dur=0.85, seed=1400),
        rule=None, lab="COUPES BUILT", lab_at=8.10,
        foot=None, foot_at=None,
    ),
    dict(
        file="s05-engine", n=5, frames=89,
        still="04_engine.png", seed=53, focus="50% 46%", zoom0=1.02,
        scrim="bottom", scrim_gain=1.15, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.12)],
        kick="THAT BODY", kick_at=W["That"],
        big=None, b1_at=0, b2_at=0,
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        file="s06-wheel", n=6, frames=128,
        still="06_wheel.png", seed=61, focus="50% 56%", zoom0=1.03,
        scrim="bottom", scrim_gain=1.30, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="orbitR", by=42)],
        kick=None, kick_at=None, big=[("161", ""), ("", "")],
        b1_at=W["161"], b2_at=9.9, b2_size="",
        roll=dict(dur=0.80, seed=161),
        rule=11.40, lab="MILES PER HOUR", lab_at=W["miles"],
        foot=None, foot_at=None,
    ),
    dict(
        file="s07-injection", n=7, frames=144,
        still="09_engine_detail.png", seed=73, focus="50% 50%", zoom0=1.05,
        scrim="bottom", scrim_gain=1.25, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.11),
               dict(t=0.40, dur="rest", move="truckL", by=30)],
        kick="BECAUSE", kick_at=W["because"],
        big=[("FUEL", ""), ("STRAIGHT IN", "red")],
        b1_at=W["fuel"], b2_at=W["straight"], b2_size="mid",
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        file="s08-gauges", n=8, frames=85,
        still="11_gauges.png", seed=83, focus="50% 50%", zoom0=1.05,
        scrim="bottom", scrim_gain=1.55, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.10)],
        kick=None, kick_at=None, big=[("WOULD YOU", ""), ("DARE?", "red")],
        b1_at=W["Would"], b2_at=W["dare"], b2_size="",
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        file="s09-closing", n=9, frames=134,
        still="12_steering.png", seed=97, focus="50% 54%", zoom0=1.06,
        scrim="bottom", blur_in=True, blur_out=False, leak=True,
        shots=[dict(t=0, dur="full", move="pull", by=0.09),
               dict(t=0.50, dur="rest", move="craneUp", by=16)],
        kick=None, kick_at=None, big=[("COMMENT", ""), ("BELOW", "red")],
        b1_at=16.80, b2_at=17.05, b2_size="",
        rule=17.30, lab="1954 MERCEDES 300SL", lab_at=17.35,
        foot=None, foot_at=None,
        extra_shakes=[dict(at=16.82, power=0.55, decay=0.40),
                      dict(at=17.25, power=0.30, decay=0.28)],
    ),
]
