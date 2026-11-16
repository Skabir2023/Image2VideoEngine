#!/usr/bin/env python3
"""The 1977 Oldsmobile Cutlass Supreme reel — data only. `tools/scene_builder.py` writes the scenes.

Voice: Kokoro am_michael, speed 1.2, **one take of the whole paragraph** (53 words), then refined
by `tools/voice_trim.py`: every internal pause capped at 0.22 s. The read is written with two full
stops and the rest commas, semicolons and dashes, because Kokoro takes its pacing from punctuation
alone — the first take had nine stops and read as "read, stop, read, stop". Refined take: 18.601 s,
longest pause 0.210 s.

Film: 21.533 s = 1.00 s of engine start alone, the 18.6 s read, then the 2.00 s roar that answers
the closing question. LEAD is the engine-start window, so every time below is absolute film time
(word time + 1.00) and PAD is 0.

Cuts (seconds into the film), each inside a measured pause of that take, ~65 ms before the next
word:

    2.400 | 4.533 | 6.917 | 8.467 | 9.800 | 12.233 | 13.467 | 16.383 | 19.250

The next word after each cut starts at 2.470 (America's), 4.590 (They), 6.980 (and), 8.530 (The),
9.870 (General), 12.290 (so), 13.520 (Four), 16.450 ($550), 19.320 (yours).

The pauses at 14.28 (after "later,") and 17.95 (after "would") are deliberately not cut: the first
would leave a 1 s scene, the second would put the money and the question in one shot.

The engine bay keeps "the mechanics found a Chevy." and the fan belt gets its own plate, because
the belt is the proof of the engine and deserves the beat. The 350 is spoken 0.8 s before its scene
ends — the card carries the words and the two rolls in the film are 14,000 and $550, both with more
than 1.5 s to lock.

Frames are exact and sum to the film:
144+128+143+93+80+146+74+175+172+137 = 1292 = 21.533 s at 60 fps.
Longest still 2.92 s (s08), inside the 3.25 s ceiling.

Ten plates, ten scenes, no still used twice: ceil(21.533 / 3) = 8 is the floor.

Build with:  python3 tools/scene_builder.py video-projects/vintage-motor-house/1977-oldsmobile-cutlass-supreme
"""
FILM = "1977 Oldsmobile Cutlass Supreme - The Best-Seller That Hid A Chevrolet"
COMPOSITION_ID = "cutlass-supreme-reel"
FPS = 60
LEAD = 1.00
PAD = 0.00

# measured word times on the refined take, absolute film time (transcript + LEAD)
W = {
    "In": 1.000, "y1977": 1.118,
    "America's": 2.470, "best": 2.901, "seller": 3.150, "hid": 3.489, "a": 3.691, "Chevrolet": 3.755,
    "They": 4.590, "paid": 4.916, "for": 5.253, "a2": 5.518, "Rocket": 5.720, "v350": 6.103,
    "Mechanics": 7.199, "found": 7.563, "a3": 7.818, "Chevy": 7.982,
    "The": 8.530, "fan": 8.669, "belt": 8.873, "didn't": 9.240, "fit": 9.560,
    "General": 9.870, "Motors": 10.243, "painted": 10.597, "every": 11.175, "engine": 11.315,
    "blue": 11.688,
    "so": 12.290, "Nobody": 12.353, "could": 12.665, "tell": 12.934,
    "Four": 13.520, "years": 13.680, "later": 13.934, "n14000": 14.500, "owners": 15.413,
    "got": 15.682, "paid2": 15.839,
    "p550": 16.450, "each": 17.138,
    "Would": 17.580, "you": 18.170, "have": 18.360, "looked": 18.622, "at": 19.011,
    "yours": 19.320,
}

SCENES = [
    dict(
        # 0.000 – 2.400  the title over the engine start, before the first word
        file="s01-hero", n=1, frames=144,
        still="01_hero_front34.png", seed=11, focus="50% 56%", zoom0=1.06,
        scrim="top", blur_in=False, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.12),
               dict(t=0, dur="full", move="truckR", by=22)],
        kick="1977 · OLDSMOBILE CUTLASS", kick_at=0.32,
        big=[("AMERICA'S", ""), ("BEST-SELLER", "red")], b1_at=0.80, b2_at=1.10,
        b2_size="mid",
        roll=None, fly=True,
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 2.400 – 4.533  "America's best-seller hid a Chevrolet."
        file="s02-side", n=2, frames=128,
        still="02_side.png", seed=23, focus="50% 54%", zoom0=1.04,
        scrim="bottom", blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="truckR", by=50),
               dict(t=0, dur="full", move="push", by=0.07)],
        kick=None, kick_at=None,
        big=[("HID A", ""), ("CHEVY", "red")], b1_at=W["hid"], b2_at=W["Chevrolet"],
        b2_size="",
        roll=None, fly=True,
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 4.533 – 6.917  "They paid for a Rocket 350."
        file="s03-rear", n=3, frames=143,
        still="03_rear.png", seed=31, focus="50% 52%", zoom0=1.03,
        scrim="bottom", blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="pull", by=0.09),
               dict(t=0.30, dur="rest", move="truckL", by=20)],
        kick="THE ORDER SHEET", kick_at=W["They"],
        big=[("PAID FOR", ""), ("A ROCKET", "red")], b1_at=W["paid"], b2_at=W["Rocket"],
        b2_size="mid",
        roll=None, fly=True,
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 6.917 – 8.467  "and the mechanics found a Chevy."
        file="s04-engine", n=4, frames=93,
        still="04_engine.png", seed=43, focus="50% 48%", zoom0=1.06,
        scrim="bottom", scrim_gain=1.18, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.14)],
        kick=None, kick_at=None,
        big=[("FOUND A", ""), ("CHEVY", "red")], b1_at=W["found"], b2_at=W["Chevy"],
        b2_size="",
        roll=None, fly=False,
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 8.467 – 9.800  "The fan belt didn't fit." — the proof you can hold
        file="s05-belt", n=5, frames=80,
        still="06_wheel.png", seed=61, focus="50% 56%", zoom0=1.04,
        scrim="bottom", scrim_gain=1.30, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="orbitR", by=38)],
        kick=None, kick_at=None,
        big=[("FAN BELT", ""), ("DIDN'T FIT", "red")], b1_at=W["fan"], b2_at=W["didn't"],
        b2_size="small",
        roll=None, fly=True,
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 9.800 – 12.233  "General Motors painted every engine blue."
        file="s06-valvecover", n=6, frames=146,
        still="07_blue_valvecover.png", seed=71, focus="50% 50%", zoom0=1.05,
        scrim="bottom", scrim_gain=1.22, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.13),
               dict(t=0.55, dur="rest", move="truckL", by=16)],
        kick=None, kick_at=None,
        big=[("EVERY", ""), ("ENGINE BLUE", "red")], b1_at=W["painted"], b2_at=W["engine"],
        b2_size="mid",
        roll=None, fly=False,
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 12.233 – 13.467  "so nobody could tell." — the anonymous cabin
        file="s07-interior", n=7, frames=74,
        still="05_interior.png", seed=53, focus="50% 52%", zoom0=1.05,
        scrim="bottom", scrim_gain=1.25, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="craneDown", by=14)],
        kick=None, kick_at=None,
        big=[("NOBODY", ""), ("COULD TELL", "red")], b1_at=W["Nobody"], b2_at=W["could"],
        b2_size="small",
        roll=None, fly=True,
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 13.467 – 16.383  "Four years later, 14,000 owners got paid."
        file="s08-gauge", n=8, frames=175,
        still="08_gauges.png", seed=79, focus="50% 50%", zoom0=1.04,
        scrim="bottom", scrim_gain=1.22, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="truckL", by=30),
               dict(t=0.40, dur="rest", move="push", by=0.08)],
        kick="THE VERDICT", kick_at=W["Four"],
        big=[("14,000", ""), ("OWNERS", "red")], b1_at=W["n14000"], b2_at=W["owners"],
        b2_size="mid",
        roll=dict(dur=0.90, seed=7), fly=False,
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 16.383 – 19.250  "550 dollars each" — the price of a lie
        file="s09-grille", n=9, frames=172,
        still="09_grille.png", seed=89, focus="50% 50%", zoom0=1.05,
        scrim="bottom", scrim_gain=1.25, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.15),
               dict(t=0.40, dur="rest", move="truckL", by=20)],
        kick=None, kick_at=None,
        big=[("$550", ""), ("EACH", "red")], b1_at=W["p550"], b2_at=W["each"],
        b2_size="mid",
        roll=dict(dur=0.70, seed=11), fly=False,
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 19.250 – 21.533  the tail, the question, and the roar answering it
        file="s10-tail", n=10, frames=137,
        still="10_taillight.png", seed=97, focus="50% 54%", zoom0=1.05,
        scrim="bottom", scrim_gain=1.20, blur_in=True, blur_out=False,
        shots=[dict(t=0, dur="full", move="push", by=0.13),
               dict(t=0.55, dur="rest", move="truckL", by=16)],
        kick=None, kick_at=None,
        big=[("WOULD YOU", ""), ("HAVE LOOKED?", "red")], b1_at=19.58, b2_at=19.86,
        b2_size="small",
        roll=None, fly=False,
        rule=20.02, lab="1977 OLDSMOBILE CUTLASS SUPREME", lab_at=20.14,
        foot=None, foot_at=None,
        extra_shakes=[dict(at=19.42, power=0.55, decay=0.40)],
    ),
]
