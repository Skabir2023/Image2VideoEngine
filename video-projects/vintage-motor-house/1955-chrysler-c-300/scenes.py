#!/usr/bin/env python3
"""The 1955 Chrysler C-300 reel — data only. `tools/scene_builder.py` writes the scenes.

Voice: Kokoro am_michael, speed 1.2, **one take of the whole paragraph** (43 words, 17.634 s).
Nothing is read in pieces — the rhythm of the read is the read.

Film: 20.400 s = 1.00 s of engine start alone, the 17.6 s read, then the 2.00 s Hemi roar that
answers the closing question. LEAD is the engine-start window, so every time below is absolute
film time (word time + 1.00) and PAD is 0.

Cuts (seconds into the film), each in a pause of that take:

    3.200 | 5.883 | 8.850 | 10.660 | 13.800 | 15.767 | 17.500

The next word after each cut starts at 3.88 (was), 5.93 (300), 9.77 (At — a 0.96 s sentence pause
opened at 8.81), 10.72 (it — 0.77 s after "Daytona"), 13.84 (Then), 15.83 (horsepower), 17.57
(with). The pause between "hit" and "127" is zero — they run together — so 127 lives in the
interior scene, where it has 1.85 s locked before the cut instead of two frames.

The first cut is the exception to the 30–70 ms rule: "in 1955" finishes at 2.99 and "was" does not
open until 3.88, a 0.89 s pause, and the hero may not outlive 3 s (master §7). So the cut goes at
3.200 — inside the pause, never on a word — and the side view gets 0.68 s of air before the line
lands. The hero still plays the whole engine start alone.

Frames are exact and sum to the film:
192+161+178+109+188+118+104+174 = 1224 = 20.400 s at 60 fps.

Eight plates, eight scenes, no still used twice: ceil(20.4 / 3) = 7 is the floor.

Build with:  python3 tools/scene_builder.py video-projects/vintage-motor-house/1955-chrysler-c-300

Build with:  python3 tools/scene_builder.py video-projects/vintage-motor-house/1955-chrysler-c-300
"""
FILM = "1955 Chrysler C-300: The Luxury Coupe That Won NASCAR"
COMPOSITION_ID = "c300-reel"
FPS = 60
LEAD = 1.00
PAD = 0.00

# measured word times, absolute film time (transcript + LEAD)
W = {
    "America's": 1.05, "most": 1.60, "powerful": 1.87, "car": 2.42, "in": 2.61, "y1955": 2.76,
    "was": 3.88, "a": 4.04, "Chrysler": 4.14, "luxury": 4.64, "coupe": 5.08,
    "300": 5.93, "horsepower": 6.25, "from": 7.35, "a2": 7.51, "ci331": 7.59, "Hemi": 8.81,
    "At": 9.77, "Daytona": 9.95, "it": 10.72, "hit": 10.89, "mph127": 11.15,
    "and": 12.04, "won": 12.35, "the": 12.45, "NASCAR": 12.71, "title": 13.26,
    "Then": 13.84, "Chrysler2": 14.11, "named": 14.48, "the2": 14.76, "car2": 14.85,
    "after": 15.02, "its": 15.39, "own": 15.54, "horsepower2": 15.83,
    "Would": 16.80, "you": 17.07, "take": 17.23, "one": 17.42,
    "with": 17.57, "two": 17.78, "gears": 17.94,
}

SCENES = [
    dict(
        # 0.000 – 3.850  the title over the engine start, before the first word
        file="s01-hero", n=1, frames=192,
        still="01_hero_front34.png", seed=11, focus="50% 56%", zoom0=1.06,
        scrim="top", blur_in=False, blur_out=True, leak=True,
        shots=[dict(t=0, dur="full", move="push", by=0.12),
               dict(t=0, dur="full", move="truckR", by=22)],
        kick="1955 · CHRYSLER C-300", kick_at=0.18,
        big=[("MOST", ""), ("POWERFUL", "red")], b1_at=0.42, b2_at=0.66,
        b2_size="",
        roll=None, fly=True,
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 3.200 – 5.880  "was a Chrysler luxury coupe."
        file="s02-side", n=2, frames=161,
        still="02_side.png", seed=23, focus="50% 54%", zoom0=1.04,
        scrim="bottom", blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="truckR", by=50),
               dict(t=0, dur="full", move="push", by=0.07)],
        kick=None, kick_at=None,
        big=[("A CHRYSLER", ""), ("LUXURY COUPE", "red")], b1_at=W["Chrysler"], b2_at=W["coupe"],
        b2_size="small",
        roll=None, fly=True,
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 5.880 – 8.850  "300 horsepower, from a 331 Hemi."
        file="s03-rear", n=3, frames=178,
        still="03_rear.png", seed=31, focus="50% 52%", zoom0=1.03,
        scrim="bottom", blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="pull", by=0.09),
               dict(t=0.30, dur="rest", move="truckL", by=20)],
        kick="THE HEMI", kick_at=W["from"],
        big=[("300", ""), ("HORSEPOWER", "red")], b1_at=W["300"], b2_at=6.90,
        b2_size="small",
        roll=dict(dur=0.88, seed=5), fly=False,
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 8.850 – 10.660  "At Daytona" — the kicker, and the engine that did it
        file="s04-engine", n=4, frames=109,
        still="04_engine.png", seed=43, focus="50% 48%", zoom0=1.06,
        scrim="bottom", scrim_gain=1.20, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.14)],
        kick="DAYTONA, 1955", kick_at=W["Daytona"],
        big=None, b1_at=None, b2_at=None, b2_size="",
        roll=None, fly=False,
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 10.660 – 13.800  "it hit 127 and won the NASCAR title."
        file="s05-interior", n=5, frames=188,
        still="05_interior.png", seed=53, focus="50% 52%", zoom0=1.05,
        scrim="bottom", scrim_gain=1.25, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.12),
               dict(t=1.20, dur="rest", move="craneDown", by=14)],
        kick=None, kick_at=None,
        big=[("127", ""), ("MILES AN HOUR", "red")], b1_at=W["mph127"], b2_at=12.00,
        b2_size="small",
        roll=dict(dur=0.80, seed=7), fly=False,
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 13.800 – 15.770  "Then Chrysler named the car after its own"
        file="s06-wheel", n=6, frames=118,
        still="06_wheel.png", seed=61, focus="50% 56%", zoom0=1.04,
        scrim="bottom", scrim_gain=1.30, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="orbitR", by=38)],
        kick="THE NAME", kick_at=W["Then"],
        big=[("300", ""), ("IS THE NAME", "red")], b1_at=W["named"], b2_at=15.40,
        b2_size="small",
        roll=dict(dur=0.80, seed=11), fly=False,
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 15.770 – 17.500  "horsepower. Would you take one"
        file="s07-grille", n=7, frames=104,
        still="07_grille.png", seed=73, focus="50% 50%", zoom0=1.05,
        scrim="bottom", scrim_gain=1.25, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.15),
               dict(t=0.50, dur="rest", move="truckL", by=22)],
        kick=None, kick_at=None,
        big=[("WOULD YOU", ""), ("TAKE ONE?", "red")], b1_at=W["Would"], b2_at=16.98,
        b2_size="",
        roll=None, fly=True,
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 17.500 – 20.400  "with two gears?" and the Hemi answering it
        file="s08-tail", n=8, frames=174,
        still="08_taillight.png", seed=83, focus="50% 54%", zoom0=1.05,
        scrim="bottom", scrim_gain=1.20, blur_in=True, blur_out=False, leak=True,
        shots=[dict(t=0, dur="full", move="push", by=0.13),
               dict(t=0.55, dur="rest", move="truckL", by=16)],
        kick=None, kick_at=None,
        big=[("TWO", ""), ("GEARS?", "red")], b1_at=W["two"], b2_at=W["gears"],
        b2_size="",
        roll=None, fly=False,
        rule=18.55, lab="1955 CHRYSLER C-300", lab_at=18.85, foot=None, foot_at=None,
        extra_shakes=[dict(at=18.42, power=0.55, decay=0.40)],
        # The taillight comes up on the roar, painted on the lens itself: 32.6% 52.4% is the
        # lens centre measured on the still, so the light sits on the bulb in every frame —
        # it lives inside BROLL's layer and the camera's push and the roar's shake carry it.
        glow=dict(
            at=18.42, rise=0.14, peak=1.0, hold=0.94, settle=0.34,
            bg="radial-gradient(ellipse 9% 5% at 32.6% 52.4%, rgba(255,252,246,1.00) 0%, "
               "rgba(255,214,170,0.95) 30%, rgba(255,132,74,0.60) 66%, rgba(255,90,50,0) 100%), "
               "radial-gradient(ellipse 23% 13% at 32.6% 52.4%, rgba(255,148,86,0.62) 0%, "
               "rgba(244,92,50,0.42) 58%, rgba(232,65,43,0) 100%), "
               "radial-gradient(ellipse 42% 25% at 32.8% 53.4%, rgba(232,65,43,0.26) 0%, "
               "rgba(214,48,26,0.10) 62%, rgba(200,40,20,0) 92%)",
        ),
    ),
]
