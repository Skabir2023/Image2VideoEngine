#!/usr/bin/env python3
"""The 1969 Dodge Charger Daytona reel — data only. `tools/scene_builder.py` writes the scenes.

Voice: Kokoro **am_adam**, speed 1.03 (am_adam reads ~18% faster than the page's am_michael at
the same setting, so 1.03 is what puts 86 words on 30 s of picture), one take:

    "Only 503 of these exist, because NASCAR said build 500 or stay home. So Dodge built
     the minimum, then hung a wing on the trunk. It sat 23 inches up, and no, that was not
     so the trunk would open. It was reaching for clean air. The nose came to a point, the
     rear window went flat, and that shape hit 200 miles per hour. Then the cars sat unsold
     on dealer lots. Would you drive a car built to beat a rule? Tell me below."

Transcript: audio/paragraph/transcript.json, measured on that WAV. LEAD is the engine-start
window — one second of the car catching before the first word — so every time below is
absolute film time (word start + 1.00) and PAD is 0.

Fourteen shots: a fresh image every ~2 s, with the three tight details (wing strut, steering
wheel, fender badge) on the beats that ask for them. Cuts sit in the measured pauses, never on
a word:

0 | 3.233 | 6.283 | 9.100 | 10.383 | 12.183 | 14.283 | 17.150 | 19.233 | 21.033 | 23.833 |
25.883 | 27.500 | 28.600 | 30.000

The 10.383 cut is the one tight pause in the film ("…trunk." ends 10.36, "It" starts 10.41):
it hands the wing to the strut close-up so the 23 can roll on the detail. The last two cuts land
under the roar, in silence.

Frames are exact and sum to the film: 1800 frames = 30.000 s at 60 fps.

Build with:  python3 tools/scene_builder.py video-projects/vintage-motor-house/1969-dodge-charger-daytona
"""
FILM = "The Most Imposing 1969 Dodge Charger Daytona Ever Built"
COMPOSITION_ID = "daytona-reel"
FPS = 60
LEAD = 1.00
PAD = 0.00

# measured word times, absolute film time
W = {
    "Only": 1.05, "503": 1.38, "these": 2.32, "exist": 2.76,
    "because": 3.30, "build": 4.37, "500": 4.71, "stay": 5.50, "home": 5.87,
    "So": 6.89, "Dodge": 6.98, "minimum": 7.96, "hung": 8.80, "wing": 9.15,
    "It": 10.41, "sat1": 10.49, "23": 10.74, "inches": 11.10, "up": 11.51,
    "no": 11.88, "was": 12.39, "not": 12.66, "the": 13.00, "would": 13.49, "open": 13.80,
    "reaching": 14.62, "clean": 15.24, "air": 15.55,
    "nose": 16.12, "point": 16.72,
    "window": 17.50, "went": 17.83, "flat": 18.26,
    "shape": 18.84, "hit": 19.09, "200": 19.30, "miles": 19.93, "per": 20.28, "hour": 20.49,
    "Then": 21.05, "cars": 21.56, "sat2": 21.88, "unsold": 22.12, "lots": 23.30,
    "Would": 23.85, "you": 24.18, "drive": 24.28,
    "Tell": 26.05, "me": 26.38, "below": 26.45,
}

SCENES = [
    dict(
        # 0.000 – 3.233  "Only 503 of these exist,"
        file="s01-hero", n=1, frames=194,
        still="01_hero_front34.png", seed=11, focus="50% 56%", zoom0=1.06,
        # no focus-in on shot 1: frame 0 is the post thumbnail and must read instantly
        scrim="top", blur_in=False, blur_out=True, leak=True,
        shots=[dict(t=0, dur="full", move="push", by=0.14),
               dict(t=0, dur="full", move="truckR", by=26)],
        kick="1969 · DODGE DAYTONA", kick_at=W["Only"],
        big=[("503", ""), ("", "")], b1_at=W["503"], b2_at=9.9, b2_size="",
        roll=dict(dur=0.85, seed=503),
        rule=2.45, lab="BUILT", lab_at=W["these"], foot=None, foot_at=None,
    ),
    dict(
        # 3.233 – 6.283  "because NASCAR said build 500 or stay home."
        file="s02-side", n=2, frames=183,
        still="02_side.png", seed=23, focus="50% 54%", zoom0=1.04,
        scrim="bottom", blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="truckR", by=52),
               dict(t=0, dur="full", move="push", by=0.08)],
        kick=None, kick_at=None,
        big=[("500", ""), ("", "")], b1_at=W["500"], b2_at=9.9, b2_size="",
        roll=dict(dur=0.80, seed=500),
        rule=5.75, lab="CARS NASCAR WANTED", lab_at=W["stay"], foot=None, foot_at=None,
    ),
    dict(
        # 6.283 – 9.100  "So Dodge built the minimum, then hung a wing on the trunk."
        file="s03-rear", n=3, frames=169,
        still="03_rear34.png", seed=31, focus="50% 52%", zoom0=1.03,
        scrim="bottom", blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="pull", by=0.09),
               dict(t=0.30, dur="rest", move="craneDown", by=22)],
        kick=None, kick_at=None,
        big=[("THE", ""), ("MINIMUM", "red")], b1_at=W["Dodge"], b2_at=W["minimum"], b2_size="mid",
        rule=8.30, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 9.100 – 10.383  "on the trunk." — the whole wing, one crane up, no card
        file="s04-wing", n=4, frames=77,
        still="04_wing.png", seed=43, focus="50% 46%", zoom0=1.05,
        scrim="bottom", scrim_gain=1.15, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="craneUp", by=34),
               dict(t=0, dur="full", move="push", by=0.12)],
        kick=None, kick_at=None, big=None, b1_at=0, b2_at=0,
        rule=None, lab=None, lab_at=None,
        foot="ON THE TRUNK", foot_at=9.52,
    ),
    dict(
        # 10.383 – 12.183  "It sat 23 inches up, and no,"
        file="s05-strut", n=5, frames=108,
        still="14_wingstrut.png", seed=47, focus="50% 44%", zoom0=1.05,
        scrim="bottom", scrim_gain=1.25, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.17),
               dict(t=0.30, dur="rest", move="truckL", by=20)],
        kick=None, kick_at=None,
        big=[("23", ""), ("", "")], b1_at=W["23"], b2_at=9.9, b2_size="",
        roll=dict(dur=0.78, seed=23),
        rule=11.70, lab="INCHES UP", lab_at=W["no"], foot=None, foot_at=None,
    ),
    dict(
        # 12.183 – 14.283  "that was not so the trunk would open."
        file="s06-tail", n=6, frames=126,
        still="10_tail.png", seed=53, focus="50% 50%", zoom0=1.05,
        scrim="bottom", scrim_gain=1.25, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.14)],
        kick=None, kick_at=None,
        big=[("NOT", ""), ("FOR THE TRUNK", "red")], b1_at=W["was"], b2_at=W["the"], b2_size="mid",
        rule=13.95, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 14.283 – 17.150  "It was reaching for clean air. The nose came to a point,"
        file="s07-nose", n=7, frames=172,
        still="05_nose.png", seed=61, focus="50% 50%", zoom0=1.04,
        scrim="bottom", scrim_gain=1.20, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.16),
               dict(t=0.50, dur="rest", move="truckL", by=26)],
        kick=None, kick_at=None,
        big=[("POINT", ""), ("", "")], b1_at=W["point"], b2_at=9.9, b2_size="",
        rule=None, lab=None, lab_at=None,
        foot="REACHING FOR CLEAN AIR", foot_at=W["clean"],
    ),
    dict(
        # 17.150 – 19.233  "the rear window went flat,"
        file="s08-window", n=8, frames=125,
        still="09_rearwindow.png", seed=73, focus="50% 54%", zoom0=1.03,
        scrim="bottom", blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="truckR", by=38),
               dict(t=0, dur="full", move="push", by=0.08)],
        kick="REAR WINDOW WENT FLAT", kick_at=W["window"],
        big=None, b1_at=0, b2_at=0,
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 19.233 – 21.033  "and that shape hit 200 miles per hour."
        file="s09-engine", n=9, frames=108,
        still="06_engine.png", seed=83, focus="50% 48%", zoom0=1.06,
        scrim="bottom", scrim_gain=1.30, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.15)],
        kick=None, kick_at=None,
        big=[("200", ""), ("", "")], b1_at=W["200"], b2_at=9.9, b2_size="",
        roll=dict(dur=0.85, seed=200),
        rule=20.45, lab="MILES PER HOUR", lab_at=W["per"], foot=None, foot_at=None,
    ),
    dict(
        # 21.033 – 23.833  "Then the cars sat unsold on dealer lots."
        file="s10-steering", n=10, frames=168,
        still="12_steering.png", seed=91, focus="50% 52%", zoom0=1.05,
        scrim="bottom", scrim_gain=1.25, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="pull", by=0.12),
               dict(t=0.40, dur="rest", move="craneDown", by=16)],
        kick=None, kick_at=None,
        big=[("UNSOLD", ""), ("ON LOTS", "red")], b1_at=W["unsold"], b2_at=W["lots"], b2_size="mid",
        rule=23.45, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 23.833 – 25.883  "Would you drive a car built to beat a rule?"
        file="s11-wheel", n=11, frames=123,
        still="08_wheel.png", seed=101, focus="50% 56%", zoom0=1.04,
        scrim="bottom", scrim_gain=1.35, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="orbitR", by=42)],
        kick=None, kick_at=None,
        big=[("WOULD YOU", ""), ("DRIVE IT?", "red")], b1_at=W["Would"], b2_at=W["drive"], b2_size="mid",
        rule=24.55, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 25.883 – 27.500  "Tell me below." — the closing card, and the roar lands on it
        file="s12-close", n=12, frames=97,
        still="11_closing.png", seed=113, focus="50% 50%", zoom0=1.06,
        scrim="bottom", scrim_gain=1.20, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.13),
               dict(t=0.55, dur="rest", move="truckL", by=20)],
        kick=None, kick_at=None,
        big=[("TELL ME", ""), ("BELOW", "red")], b1_at=W["Tell"], b2_at=W["below"], b2_size="",
        rule=26.80, lab=None, lab_at=None, foot=None, foot_at=None,
        extra_shakes=[dict(at=26.90, power=0.55, decay=0.40)],
    ),
    dict(
        # 27.500 – 28.600  the badge, under the roar: this is the car they named
        file="s13-badge", n=13, frames=66,
        still="13_badge.png", seed=119, focus="50% 50%", zoom0=1.06,
        scrim="bottom", scrim_gain=1.20, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.15)],
        kick=None, kick_at=None, big=None, b1_at=0, b2_at=0,
        rule=None, lab=None, lab_at=None,
        foot="1969 · CHARGER DAYTONA", foot_at=27.62,
    ),
    dict(
        # 28.600 – 30.000  the bookend: the hero plate returns under the dying roar
        file="s14-bookend", n=14, frames=84,
        still="01_hero_front34.png", seed=127, focus="50% 58%", zoom0=1.03,
        scrim="top", blur_in=True, blur_out=False, leak=True,
        shots=[dict(t=0, dur="full", move="pull", by=0.08)],
        kick=None, kick_at=None, big=None, b1_at=0, b2_at=0,
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
]
