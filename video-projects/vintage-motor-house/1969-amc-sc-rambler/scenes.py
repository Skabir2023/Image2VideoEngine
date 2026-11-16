#!/usr/bin/env python3
"""The 1969 AMC SC/Rambler reel — data only. `tools/scene_builder.py` writes the scenes.

Voice: Kokoro am_michael, speed 1.2, **one take of the whole paragraph** (55 words, 26.000 s).
Nothing is read in pieces — the rhythm of the read is the read.

Film: 30.000 s = 2.00 s of engine start alone, the 26.00 s read, then the 2.00 s big-block roar
that answers the closing question. LEAD is the engine-start window, so every time below is
absolute film time (word time + 2.00) and PAD is 0.

Cuts (seconds into the film), each in a pause of that take — ~30–65 ms before the next word:

    2.033 | 5.100 | 8.350 | 11.417 | 14.183 | 16.850 | 19.050 | 20.550 | 23.750 | 26.783

The next word after each cut starts at 2.05 (AMC), 5.13 (Racing), 8.41 (so), 11.48 (390),
14.22 ($2,998), 16.89 (It), 19.13 (Then), 20.62 (1,512), 23.83 (stopped), 26.87 (bargain).

Frames are exact and sum to the film:
122+184+195+184+166+160+132+90+192+182+193 = 1800 = 30.000 s at 60 fps.

Eleven plates, eleven scenes, no still used twice: ceil(30 / 3) = 10, and the longest still is
3.25 s.

Build with:  python3 tools/scene_builder.py video-projects/vintage-motor-house/1969-amc-sc-rambler
"""
FILM = "1969 AMC SC/Rambler: 1,512 Cars for a 500-Car Rule"
COMPOSITION_ID = "scrambler-reel"
FPS = 60
LEAD = 2.00
PAD = 0.00

# measured word times, absolute film time (transcript + LEAD)
W = {
    "AMC": 2.05, "never": 2.29, "set": 2.83, "out": 3.07, "to": 3.36, "build": 3.55,
    "a": 4.04, "muscle": 4.14, "car": 4.49,
    "Racing": 5.13, "Rules": 5.61, "said": 6.05, "500": 6.40, "identical": 7.19, "cars": 8.20,
    "so": 8.41, "it": 8.56, "dropped": 8.76, "a2": 9.47, "315": 9.56,
    "390": 11.48, "into": 12.04, "two_door": 12.31, "Rambler": 12.75,
    "It": 13.36, "cost": 13.67, "price": 14.22,
    "It2": 16.89, "hit": 17.01, "60": 17.27, "in": 17.80, "six3": 17.97,
    "Then": 19.13, "AMC2": 19.58, "built": 19.96, "1512": 20.62,
    "That": 22.81, "is": 23.03, "three": 23.16, "times": 23.59, "rule_word": 24.31,
    "demanded": 24.58, "and_word": 25.16, "stopped": 25.83,
    "Would": 26.09, "take": 26.47, "bargain": 26.87, "or": 27.24, "badge": 27.58,
}

SCENES = [
    dict(
        # 0.000 – 2.033  the title over two seconds of engine start, before the first word
        file="s01-hero", n=1, frames=122,
        still="01_hero_front34.png", seed=11, focus="50% 56%", zoom0=1.06,
        scrim="top", blur_in=False, blur_out=True, leak=True,
        shots=[dict(t=0, dur="full", move="push", by=0.12),
               dict(t=0, dur="full", move="truckR", by=22)],
        kick="1969 · AMC SC/RAMBLER", kick_at=0.18,
        big=[("1,512 CARS", "small"), ("FOR A 500-CAR RULE", "red")], b1_at=0.42, b2_at=0.62,
        b2_size="small",
        roll=dict(dur=0.88, seed=3), fly=True,
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 2.033 – 5.100  "AMC never set out to build a muscle car."
        file="s02-side", n=2, frames=184,
        still="02_side.png", seed=23, focus="50% 54%", zoom0=1.04,
        scrim="bottom", blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="truckR", by=50),
               dict(t=0, dur="full", move="push", by=0.07)],
        kick=None, kick_at=None,
        big=None, b1_at=0, b2_at=0,
        rule=None, lab=None, lab_at=None,
        foot="NOT THE PLAN", foot_at=W["muscle"],
    ),
    dict(
        # 5.100 – 8.350  "Racing rules said 500 identical cars."
        file="s03-rear", n=3, frames=195,
        still="03_rear.png", seed=31, focus="50% 52%", zoom0=1.03,
        scrim="bottom", blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="pull", by=0.09),
               dict(t=0.30, dur="rest", move="truckL", by=20)],
        kick="THE RULE", kick_at=W["Racing"],
        big=[("500", ""), ("IDENTICAL CARS", "red")], b1_at=W["500"], b2_at=6.70,
        b2_size="small",
        roll=dict(dur=0.90, seed=5),
        rule=7.55, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 8.350 – 11.417  "so it dropped a 315-horse"
        file="s04-engine", n=4, frames=184,
        still="04_engine.png", seed=43, focus="50% 48%", zoom0=1.06,
        scrim="bottom", scrim_gain=1.20, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.14)],
        kick="THE ENGINE", kick_at=W["dropped"],
        big=[("315", ""), ("HORSEPOWER", "red")], b1_at=W["315"], b2_at=9.80,
        b2_size="small",
        roll=dict(dur=0.85, seed=7),
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 11.417 – 14.183  "390 into a two-door Rambler. It"
        file="s05-scoop", n=5, frames=166,
        still="07_scoop.png", seed=73, focus="50% 50%", zoom0=1.05,
        scrim="bottom", scrim_gain=1.25, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.15),
               dict(t=0.50, dur="rest", move="truckL", by=22)],
        kick=None, kick_at=None,
        big=[("390", ""), ("CUBIC INCHES", "red")], b1_at=W["390"], b2_at=11.75,
        b2_size="small",
        roll=dict(dur=0.85, seed=11),
        rule=None, lab="SC/RAMBLER", lab_at=W["Rambler"], foot=None, foot_at=None,
    ),
    dict(
        # 14.183 – 16.850  "$2,998"
        file="s06-interior", n=6, frames=160,
        still="05_interior.png", seed=53, focus="50% 52%", zoom0=1.05,
        scrim="bottom", scrim_gain=1.25, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.12),
               dict(t=0.40, dur="rest", move="craneDown", by=14)],
        kick=None, kick_at=None,
        big=[("$2,998", ""), ("BASE PRICE", "red")], b1_at=W["price"], b2_at=14.50,
        b2_size="small",
        roll=dict(dur=0.90, seed=13),
        rule=15.90, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 16.850 – 19.050  "It hit 60 in 6.3."
        file="s07-wheel", n=7, frames=132,
        still="06_wheel.png", seed=61, focus="50% 56%", zoom0=1.04,
        scrim="bottom", scrim_gain=1.30, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="orbitR", by=38)],
        kick=None, kick_at=None,
        big=[("6.3", ""), ("SECONDS", "red")], b1_at=W["six3"], b2_at=18.20,
        b2_size="small",
        roll=dict(dur=0.80, seed=17),
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 19.050 – 20.550  "Then AMC built"
        file="s08-tail", n=8, frames=90,
        still="08_tail.png", seed=83, focus="50% 54%", zoom0=1.05,
        scrim="bottom", scrim_gain=1.30, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="pull", by=0.10)],
        kick="AMC BUILT", kick_at=W["built"],
        big=None, b1_at=0, b2_at=0,
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 20.550 – 23.750  "1,512. That is three times what the rule demanded"
        file="s09-tach", n=9, frames=192,
        still="10_tach.png", seed=91, focus="50% 50%", zoom0=1.05,
        scrim="bottom", scrim_gain=1.25, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.13),
               dict(t=0.60, dur="rest", move="craneUp", by=12)],
        kick=None, kick_at=None,
        big=[("1,512", ""), ("THREE TIMES THE RULE", "red")], b1_at=W["1512"], b2_at=W["That"],
        b2_size="small",
        roll=dict(dur=0.90, seed=19),
        rule=23.20, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 23.750 – 26.783  "and stopped. Would you take the"
        file="s10-headlight", n=10, frames=182,
        still="09_headlight.png", seed=103, focus="50% 50%", zoom0=1.05,
        scrim="bottom", scrim_gain=1.20, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.14),
               dict(t=0.40, dur="rest", move="truckR", by=18)],
        kick=None, kick_at=None,
        big=[("AND", ""), ("STOPPED", "red")], b1_at=W["and_word"], b2_at=W["stopped"],
        b2_size="",
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 26.783 – 30.000  "bargain, or the badge?" and the roar answering it
        file="s11-shifter", n=11, frames=193,
        still="11_shifter.png", seed=111, focus="50% 52%", zoom0=1.04,
        scrim="bottom", scrim_gain=1.20, blur_in=True, blur_out=False, leak=True,
        shots=[dict(t=0, dur="full", move="push", by=0.13),
               dict(t=0.55, dur="rest", move="truckL", by=16)],
        kick=None, kick_at=None,
        big=[("OR THE", ""), ("BADGE?", "red")], b1_at=W["or"], b2_at=W["badge"],
        b2_size="",
        rule=28.05, lab="1969 AMC SC/RAMBLER", lab_at=28.25, foot=None, foot_at=None,
        extra_shakes=[dict(at=28.02, power=0.55, decay=0.40)],
    ),
]
