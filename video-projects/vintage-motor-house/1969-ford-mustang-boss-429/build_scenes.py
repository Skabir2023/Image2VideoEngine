#!/usr/bin/env python3
"""Write the six full-bleed car scenes for the continuous-cut Boss 429 reel.

Every scene is the same machine: a still plate moved by the BROLL camera, a dark
scrim, and a text block that lands on the words being spoken.

All the timings here are measured, not guessed: the voice is one Kokoro call at
speed 1.2 (17.138 s) and `audio/paragraph/transcript.json` holds the word-level
timestamps. Speech starts at 0.30 s, so every word time is +0.30, and each cut
lands ~65 ms before the first word of the next line — so the picture changes on
the pause, and the text arrives with the word, never before it.

Frame-exact: 256 / 311 / 218 / 95 / 98 / 138 = 1116 frames = 18.600 s at 60 fps.

Run from the engine root: python3 video-projects/vintage-motor-house/build_scenes.py

The written HTML is opened by HyperFrames from the engine root, so every path inside it is
relative to that root: the shared library at assets/, the plates at video-projects/<slug>/stills/.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent          # .../video-projects/<page>/1969-ford-mustang-boss-429
ENGINE = next(p for p in HERE.parents if (p / "assets" / "stage.js").exists())
PROJECT = HERE.relative_to(ENGINE).as_posix()   # the same folder, as the render sees it
OUT = HERE / "compositions"
OUT.mkdir(exist_ok=True)

STILLS = f"{PROJECT}/stills"

SCENES = [
    dict(
        file="s01-hero", n=1, dur="4.266667", frames=256,
        still=f"{STILLS}/01_hero_front34-01.png", seed=11, focus="50% 58%", zoom0=1.04,
        scrim="top", flash_in=False, flash_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.10),
               dict(t=0, dur="full", move="truckR", by=34)],
        kick="1969 · FORD MUSTANG", kick_at=0.35,
        big=[("BOSS", ""), ("429", "red")], b1_at=0.52, b2_at=0.68,
        rule=2.58, lab="NASCAR HOMOLOGATION", lab_at=2.63,
        foot=None, foot_at=None,
    ),
    dict(
        file="s02-engine", n=2, dur="5.183333", frames=311,
        still=f"{STILLS}/04_engine_bay-01.png", seed=23, focus="50% 46%", zoom0=1.0,
        scrim="bottom", flash_in=True, flash_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.14),
               dict(t=0.35, dur="rest", move="craneDown", by=24)],
        kick=None, kick_at=None,
        big=[("429", ""), ("CUBIC INCHES", "small")], b1_at=0.92, b2_at=1.08,
        rule=2.58, lab="7.0 LITRE · HAND-BUILT V8", lab_at=2.70,
        foot="Solid-lifter big block · one year only", foot_at=3.95,
    ),
    dict(
        file="s03-side", n=3, dur="3.633333", frames=218,
        still=f"{STILLS}/02_side_profile-01.png", seed=37, focus="48% 54%", zoom0=1.03,
        scrim="bottom", flash_in=True, flash_out=True,
        shots=[dict(t=0, dur="full", move="truckR", by=60),
               dict(t=0, dur="full", move="push", by=0.06)],
        kick=None, kick_at=None,
        big=[("1,359", "red"), ("EVER BUILT", "small")], b1_at=0.50, b2_at=1.12,
        rule=2.28, lab="1969 ONLY", lab_at=2.42,
        foot=None, foot_at=None,
    ),
    dict(
        file="s04-interior", n=4, dur="1.583333", frames=95,
        still=f"{STILLS}/05_interior_dash-01.png", seed=53, focus="44% 54%", zoom0=1.03,
        scrim="bottom", flash_in=True, flash_out=True,
        shots=[dict(t=0, dur="full", move="orbitL", by=44)],
        kick=None, kick_at=None,
        big=[("DETUNED", ""), ("TO SELL", "red")], b1_at=0.36, b2_at=0.52,
        rule=1.06, lab="STREET LEGAL", lab_at=1.14,
        foot=None, foot_at=None,
    ),
    dict(
        file="s05-wheel", n=5, dur="1.633333", frames=98,
        still=f"{STILLS}/06_wheel_close-01.png", seed=67, focus="50% 56%", zoom0=1.02,
        scrim="bottom", flash_in=True, flash_out=True,
        shots=[dict(t=0, dur="full", move="orbitR", by=48)],
        kick=None, kick_at=None,
        big=[("ONE YEAR", ""), ("ONLY", "red")], b1_at=0.36, b2_at=0.52,
        rule=1.04, lab="1969 · THEN GONE", lab_at=0.92,
        foot=None, foot_at=None,
    ),
    dict(
        file="s06-rear", n=6, dur="2.300000", frames=138,
        still=f"{STILLS}/03_rear34-01.png", seed=79, focus="48% 56%", zoom0=1.02,
        scrim="bottom", flash_in=True, flash_out=False,
        shots=[dict(t=0, dur="full", move="push", by=0.07)],
        kick=None, kick_at=None,
        big=[("WOULD YOU", ""), ("DRIVE IT?", "red")], b1_at=0.38, b2_at=0.54,
        rule=1.24, lab="BOSS 429", lab_at=1.36,
        foot=None, foot_at=None,
    ),
]

TEMPLATE = """<!doctype html>
<!-- SCENE {n:02d} of 6 — full-bleed car plate, camera moving, text cut to the voice. {dur} s. -->
<html lang="en">
<head>
<meta charset="utf-8">
<title>Boss 429 — {n:02d} {slug}</title>
<script src="assets/gsap.min.js"></script>
<script src="assets/stage.js"></script>
<script src="assets/kit-config.js"></script>
<script src="assets/broll.js"></script>
<script src="assets/text.js"></script>
<link rel="stylesheet" href="assets/fonts.css">
<style>
  html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #050506; }}
  #plate {{ position: absolute; inset: 0; z-index: 0; }}
  #fg {{ position: absolute; inset: 0; z-index: 2; color: #F5EFE6; }}
  .scrim {{ position: absolute; left: 0; right: 0; {scrim_side}: 0; height: 1020px; background: {scrim_grad}; }}
{styles}
  #flash {{ position: absolute; inset: 0; z-index: 9; background: #F5EFE6; opacity: 0; pointer-events: none; }}
</style>
</head>
<body>
<div id="root" data-composition-id="{id}" data-start="0" data-duration="{dur}" data-width="1080" data-height="1920">
  <div id="plate" class="clip" data-start="0" data-duration="{dur}" data-track-index="0"></div>
  <div id="fg" class="clip" data-start="0" data-duration="{dur}" data-track-index="1">
    <div class="scrim"></div>
{markup}
  </div>
  <div id="flash" class="clip" data-start="0" data-duration="{dur}" data-track-index="5"></div>
</div>
<script>
(() => {{
  const S = STAGE, DUR = {dur}, $ = (id) => document.getElementById(id);

  const cam = BROLL.make($('plate'), {{
    src: '{still}',
    duration: DUR,
    seed: {seed},
    zoom0: {zoom0},
    focus: '{focus}',
    handheld: 1.0,
    grain: 0.25,
    vignette: 0.52,
    shots: [{shots}],
    shakes: [{{ at: 0.03, power: 0.20, decay: 0.12 }}],
  }});

  const tl = S.driver(DUR, () => {{}});
  BROLL.live(tl, cam);

{tweens}

{flash}
  window.__timelines = window.__timelines || {{}};
  window.__timelines['{id}'] = tl;
}})();
</script>
</body>
</html>
"""

BIG_CSS = """  .kick { position: absolute; left: 72px; top: 150px; font: 700 31px/1 'JetBrains Mono', monospace; letter-spacing: 0.30em; color: #CFC6BA; }
  .b1, .b2 { position: absolute; left: 62px; font: 400 208px/0.90 'Anton', sans-serif; letter-spacing: -0.005em; }
  .b2.small { font-size: 96px; top: auto; }
  .red { color: #E8412B; }
  .rule { position: absolute; left: 68px; width: 190px; height: 3px; background: #E8412B; transform-origin: 0 50%; }
  .lab { position: absolute; left: 68px; font: 700 40px/1 'JetBrains Mono', monospace; letter-spacing: 0.28em; }
  .foot { position: absolute; left: 68px; font: 500 31px/1.4 'Inter', sans-serif; color: rgba(245,239,230,0.60); }"""


def build(s):
    slug = s["file"].split("-", 1)[1]
    top = s["scrim"] == "top"
    scrim_side = "top" if top else "bottom"
    scrim_grad = ("linear-gradient(180deg, rgba(5,5,6,0.94) 0%, rgba(5,5,6,0.82) 32%, "
                  "rgba(5,5,6,0.40) 72%, rgba(5,5,6,0) 100%)") if top else \
                 ("linear-gradient(0deg, rgba(5,5,6,0.92) 0%, rgba(5,5,6,0.72) 34%, "
                  "rgba(5,5,6,0.30) 72%, rgba(5,5,6,0) 100%)")

    if top:
        y1, y2 = 300, 500
        rule_y, lab_y, foot_y = 760, 794, 880
    else:
        y1, y2 = 1120, 1330
        rule_y, lab_y, foot_y = 1560, 1594, 1690
    if s["big"][1][1] == "small":
        y2 = y1 + 220

    markup, tweens = [], []
    if s["kick"]:
        markup.append(f'    <div class="kick" id="kick">{s["kick"]}</div>')
        tweens.append(f"  TX.words(tl, $('kick'), {s['kick_at']:.2f}, 0.04);")

    b1, b1cls = s["big"][0]
    b2, b2tag = s["big"][1]
    markup.append(f'    <div class="b1" id="b1" style="top:{y1}px">{b1}</div>')
    cls = "b2" + (" red" if b2tag == "red" else "") + (" small" if b2tag == "small" else "")
    markup.append(f'    <div class="{cls}" id="b2" style="top:{y2}px">{b2}</div>')
    markup.append(f'    <div class="rule" id="rule" style="top:{rule_y}px"></div>')
    markup.append(f'    <div class="lab" id="lab" style="top:{lab_y}px">{s["lab"]}</div>')
    if s["foot"]:
        markup.append(f'    <div class="foot" id="foot" style="top:{foot_y}px">{s["foot"]}</div>')

    tweens.append(f"  TX.slam(tl, $('b1'), {s['b1_at']:.2f});")
    tweens.append(f"  TX.slam(tl, $('b2'), {s['b2_at']:.2f});")
    tweens.append(f"  tl.fromTo($('rule'), {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.34, ease: 'power3.out' }}, {s['rule']:.2f});")
    tweens.append(f"  TX.words(tl, $('lab'), {s['lab_at']:.2f}, 0.04);")
    if s["foot"]:
        tweens.append(f"  tl.fromTo($('foot'), {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.40, ease: 'power3.out' }}, {s['foot_at']:.2f});")

    shots = ", ".join(
        "{{ t: {t}, dur: {dur}, move: '{move}', by: {by}, ease: 'inOutSine' }}".format(
            t=sh["t"], dur=("DUR" if sh["dur"] == "full" else f"DUR - {sh['t']}"),
            move=sh["move"], by=sh["by"])
        for sh in s["shots"])

    flash = []
    if s["flash_in"]:
        flash.append("  tl.fromTo($('flash'), { opacity: 1 }, { opacity: 0, duration: 0.16, ease: 'power2.out' }, 0);")
    if s["flash_out"]:
        flash.append("  tl.fromTo($('flash'), { opacity: 0 }, { opacity: 1, duration: 0.20, ease: 'power2.in' }, DUR - 0.20);")

    html = TEMPLATE.format(
        n=s["n"], slug=slug, id=s["file"], dur=s["dur"], still=s["still"], seed=s["seed"],
        zoom0=s["zoom0"], focus=s["focus"], scrim_side=scrim_side, scrim_grad=scrim_grad,
        styles=BIG_CSS, markup="\n".join(markup), tweens="\n".join(tweens),
        shots=shots, flash="\n".join(flash),
    )
    (OUT / f"{s['file']}.html").write_text(html)
    return s["file"], s["frames"]


total = 0
for s in SCENES:
    name, fr = build(s)
    total += fr
    print(f"{name}.html  {s['dur']:>9}s  {fr:>3} frames")
print(f"total {total} frames = {total / 60:.3f}s at 60 fps")
