#!/usr/bin/env python3
"""The 1978 BMW M1 reel — data only. `tools/scene_builder.py` writes the scenes.

Voice: Kokoro **am_adam**, speed 1.30, one take (see plan/SCRIPT.md for why 1.30 and not 1.20):

    "BMW built this car to go racing. The rules changed before the first one was done. They
     needed 400 road cars to qualify. So they hired Lamborghini. Lamborghini ran out of cash.
     Seven prototypes in. So every car crossed the Alps. Italian body. Italian frame. Finished
     in Stuttgart. It still made 277 horsepower. 160 miles an hour. They built 453. Then made a
     series where it could only race itself. The car wasn't the failure. The plan was."

Transcript: audio/paragraph/transcript.json, measured on that WAV (25.39 s, 78 words). LEAD is the
engine-start window — one second of the car catching before the first word — so every time below
is absolute film time (word start + 1.00) and PAD is 0.

**Sixteen shots, a fresh image about every 1.9 s, all of them close:** the six fixed angles first,
then the roundel on the nose, the roundel on the tail, headlight, steering wheel, exhaust, engine
louvres, wing mirror, air intake, a lit night hero for the closing card, and the tail lamp to end
on. Every cut sits inside a measured silence in the take (`ffmpeg silencedetect`, −32 dB / 0.12 s),
never on a word:

0 | 2.967 | 5.133 | 7.333 | 8.883 | 10.433 | 11.733 | 13.217 | 14.217 | 15.200 | 16.233 |
18.700 | 20.750 | 24.150 | 25.417 | 28.400 | 30.000

The 24.15 cut is the long one: it carries "They built 453. Then made a series…" so the 453 can
roll and lock with its label still on screen. The last two cuts are under the roar, in silence.

Frames are exact and sum to the film: 1800 frames = 30.000 s at 60 fps.

Build with:  python3 tools/scene_builder.py video-projects/vintage-motor-house/1978-bmw-m1
"""
FILM = "The 1978 BMW M1 That Missed Its Own Race"
COMPOSITION_ID = "m1-reel"
FPS = 60
LEAD = 1.00
PAD = 0.00

# measured word times, absolute film time (transcript + LEAD)
W = {
    "BMW": 1.05, "built": 1.24, "this": 1.63, "car": 1.94, "to": 2.22, "go": 2.34, "racing": 2.50,
    "The1": 3.04, "rules": 3.17, "changed": 3.42, "before": 3.79, "the1": 3.96, "first": 4.11,
    "one": 4.30, "was1": 4.36, "done": 4.58,
    "They1": 5.18, "needed": 5.29, "400": 5.62, "road": 6.21, "cars": 6.46, "to2": 6.69,
    "qualify": 6.81,
    "so": 7.37, "they": 7.49, "hired": 7.74, "Lambo1": 8.05,
    "Lambo2": 9.02, "ran": 9.54, "out": 9.68, "of": 9.82, "cash": 9.96,
    "seven": 10.65, "prototypes": 10.93, "in": 11.61,
    "So": 11.95, "every": 12.21, "crossed": 12.62, "the2": 12.71, "Alps": 12.86,
    "Italian1": 13.24, "body": 13.75,
    "Italian2": 14.26, "frame": 14.78,
    "Finished": 15.20, "in2": 15.53, "Stuttgart": 15.62,
    "It": 16.49, "still": 16.63, "made": 16.98, "277": 17.50, "horsepower": 17.94,
    "160": 18.89, "miles": 19.66, "an": 19.91, "hour": 20.05,
    "They2": 20.56, "built2": 20.85, "453": 21.24,
    "Then": 22.16, "made2": 22.24, "a": 22.34, "series": 22.39, "where": 22.69, "it": 22.94,
    "could": 23.10, "only": 23.31, "race": 23.49, "itself": 23.69,
    "The2": 24.01, "car2": 24.36, "wasnt": 24.44, "the3": 24.76, "failure": 24.89,
    "The3": 25.45, "plan": 25.54, "was3": 25.74,
}

SCENES = [
    dict(
        # 0.000 – 2.967  "BMW built this car to go racing."
        file="s01-hero", n=1, frames=178,
        still="01_hero_front34.png", seed=11, focus="50% 56%", zoom0=1.05,
        # no focus-in on shot 1: frame 0 is the post thumbnail and must read instantly
        scrim="top", blur_in=False, blur_out=True, leak=True,
        shots=[dict(t=0, dur="full", move="push", by=0.16),
               dict(t=0, dur="full", move="truckR", by=24)],
        kick="1978 · BMW M1", kick_at=W["BMW"],
        big=[("BUILT TO", ""), ("GO RACING", "red")], b1_at=W["built"], b2_at=W["go"], b2_size="mid",
        rule=2.62, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 2.967 – 5.133  "The rules changed before the first one was done."
        file="s02-side", n=2, frames=130,
        still="02_side.png", seed=23, focus="50% 54%", zoom0=1.04,
        scrim="bottom", blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="truckR", by=54),
               dict(t=0, dur="full", move="push", by=0.10)],
        kick=None, kick_at=None,
        big=[("THE RULES", ""), ("CHANGED", "red")], b1_at=W["rules"], b2_at=W["changed"],
        b2_size="mid",
        rule=4.75, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 5.133 – 7.333  "They needed 400 road cars to qualify."
        file="s03-rear", n=3, frames=132,
        still="03_rear34.png", seed=31, focus="50% 52%", zoom0=1.03,
        scrim="bottom", blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="pull", by=0.10),
               dict(t=0.30, dur="rest", move="craneDown", by=20)],
        kick=None, kick_at=None,
        big=[("400", ""), ("", "")], b1_at=W["400"], b2_at=9.9, b2_size="",
        roll=dict(dur=0.85, seed=400),
        rule=6.95, lab="ROAD CARS TO QUALIFY", lab_at=W["road"], foot=None, foot_at=None,
    ),
    dict(
        # 7.333 – 8.883  "So they hired Lamborghini."
        file="s04-engine", n=4, frames=93,
        still="04_engine.png", seed=43, focus="50% 48%", zoom0=1.06,
        scrim="bottom", scrim_gain=1.25, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.17)],
        kick="HIRED: LAMBORGHINI", kick_at=W["hired"],
        big=None, b1_at=0, b2_at=0,
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 8.883 – 10.433  "Lamborghini ran out of cash."
        file="s05-interior", n=5, frames=93,
        still="05_interior.png", seed=47, focus="50% 50%", zoom0=1.05,
        scrim="bottom", scrim_gain=1.30, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.15),
               dict(t=0.25, dur="rest", move="truckL", by=18)],
        kick=None, kick_at=None,
        big=[("OUT OF", ""), ("CASH", "red")], b1_at=W["out"], b2_at=W["cash"], b2_size="",
        rule=10.05, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 10.433 – 11.733  "Seven prototypes in."
        file="s06-wheel", n=6, frames=78,
        still="06_wheel.png", seed=53, focus="50% 54%", zoom0=1.06,
        scrim="bottom", scrim_gain=1.35, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="orbitR", by=40)],
        kick="SEVEN PROTOTYPES", kick_at=W["seven"],
        big=[("7", ""), ("", "")], b1_at=W["seven"], b2_at=9.9, b2_size="",
        roll=dict(dur=0.78, seed=7),
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 11.733 – 13.217  "So every car crossed the Alps."
        file="s07-roundel-front", n=7, frames=89,
        still="07_roundel_front.png", seed=61, focus="50% 46%", zoom0=1.06,
        scrim="bottom", scrim_gain=1.25, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.16),
               dict(t=0.40, dur="rest", move="truckR", by=16)],
        kick="CROSSED THE ALPS", kick_at=W["crossed"],
        big=None, b1_at=0, b2_at=0,
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 13.217 – 14.217  "Italian body."
        file="s08-roundel-rear", n=8, frames=60,
        still="08_roundel_rear.png", seed=67, focus="50% 50%", zoom0=1.05,
        scrim="bottom", scrim_gain=1.30, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.14)],
        kick=None, kick_at=None, big=None, b1_at=0, b2_at=0,
        rule=None, lab=None, lab_at=None,
        foot="ITALIAN BODY", foot_at=W["Italian1"],
    ),
    dict(
        # 14.217 – 15.200  "Italian frame."
        file="s09-headlight", n=9, frames=59,
        still="09_headlight.png", seed=71, focus="50% 48%", zoom0=1.06,
        scrim="bottom", scrim_gain=1.30, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.18)],
        kick=None, kick_at=None, big=None, b1_at=0, b2_at=0,
        rule=None, lab=None, lab_at=None,
        foot="ITALIAN FRAME", foot_at=W["Italian2"],
    ),
    dict(
        # 15.200 – 16.233  "Finished in Stuttgart."
        file="s10-steering", n=10, frames=62,
        still="10_steering.png", seed=73, focus="50% 52%", zoom0=1.05,
        scrim="bottom", scrim_gain=1.30, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="truckL", by=22)],
        kick=None, kick_at=None, big=None, b1_at=0, b2_at=0,
        rule=None, lab=None, lab_at=None,
        foot="FINISHED IN STUTTGART", foot_at=W["Stuttgart"],
    ),
    dict(
        # 16.233 – 18.700  "It still made 277 horsepower."
        file="s11-exhaust", n=11, frames=148,
        still="11_exhaust.png", seed=79, focus="50% 54%", zoom0=1.05,
        scrim="bottom", scrim_gain=1.35, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.16),
               dict(t=0.55, dur="rest", move="craneUp", by=18)],
        kick=None, kick_at=None,
        big=[("277", ""), ("", "")], b1_at=W["277"], b2_at=9.9, b2_size="",
        roll=dict(dur=0.85, seed=277),
        rule=18.10, lab="HORSEPOWER", lab_at=W["horsepower"], foot=None, foot_at=None,
    ),
    dict(
        # 18.700 – 20.750  "160 miles an hour."
        file="s12-louvres", n=12, frames=123,
        still="12_louvres.png", seed=83, focus="50% 48%", zoom0=1.05,
        scrim="bottom", scrim_gain=1.35, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="truckR", by=30),
               dict(t=0, dur="full", move="push", by=0.10)],
        kick=None, kick_at=None,
        big=[("160", ""), ("", "")], b1_at=W["160"], b2_at=9.9, b2_size="",
        roll=dict(dur=0.85, seed=160),
        rule=20.05, lab="MILES PER HOUR", lab_at=W["miles"], foot=None, foot_at=None,
    ),
    dict(
        # 20.750 – 24.150  "They built 453. Then made a series where it could only race itself."
        file="s13-mirror", n=13, frames=203,
        still="13_mirror.png", seed=89, focus="50% 50%", zoom0=1.05,
        scrim="bottom", scrim_gain=1.30, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.15),
               dict(t=0.60, dur="rest", move="truckL", by=22)],
        kick="PROCAR · 1979", kick_at=W["where"],
        big=[("453", ""), ("", "")], b1_at=W["453"], b2_at=9.9, b2_size="",
        roll=dict(dur=0.85, seed=453),
        rule=23.30, lab="BUILT", lab_at=W["built2"] + 0.95, foot=None, foot_at=None,
    ),
    dict(
        # 24.150 – 25.417  "The car wasn't the failure."
        file="s14-intake", n=14, frames=77,
        still="14_intake.png", seed=97, focus="50% 52%", zoom0=1.06,
        scrim="bottom", scrim_gain=1.35, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.17)],
        kick=None, kick_at=None,
        big=[("NOT THE", ""), ("FAILURE", "red")], b1_at=W["wasnt"], b2_at=W["failure"],
        b2_size="mid",
        rule=25.00, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
    dict(
        # 25.417 – 28.400  "The plan was." — the closing card, and the roar lands on it
        file="s15-night", n=15, frames=179,
        still="16_night_hero.png", seed=101, focus="50% 52%", zoom0=1.05,
        scrim="bottom", scrim_gain=1.25, blur_in=True, blur_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.14),
               dict(t=0.70, dur="rest", move="truckR", by=18)],
        kick=None, kick_at=None,
        big=[("THE PLAN", ""), ("WAS", "red")], b1_at=W["plan"], b2_at=W["was3"], b2_size="",
        rule=27.10, lab=None, lab_at=None, foot=None, foot_at=None,
        extra_shakes=[dict(at=26.48, power=0.55, decay=0.42)],
    ),
    dict(
        # 28.400 – 30.000  the tail lamp as the roar dies: the car leaving
        file="s16-tail", n=16, frames=96,
        still="15_taillight.png", seed=107, focus="50% 50%", zoom0=1.05,
        scrim="bottom", scrim_gain=1.20, blur_in=True, blur_out=False,
        shots=[dict(t=0, dur="full", move="pull", by=0.10)],
        kick=None, kick_at=None, big=None, b1_at=0, b2_at=0,
        rule=None, lab=None, lab_at=None, foot=None, foot_at=None,
    ),
]
