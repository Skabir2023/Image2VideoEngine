#!/usr/bin/env python3
"""Write the seven full-bleed scenes for the Eldorado Brougham reel — 16:9, 20.000 s.

Same machine as the Boss 429 film: a still plate moved by the BROLL camera, a dark
scrim along the bottom, and a text block that lands on the words being spoken. On top
of that, every scene carries the same thin layer of always-moving furniture — a
progress rail that runs the whole film, a light pass every 2.6 s and drifting motes —
so no frame is ever still, and the right edge stays empty.

Timings are measured, not guessed: the voice is one Kokoro call at speed 1.2
(15.046 s) and `audio/paragraph/transcript.json` holds the word-level stamps.
Speech starts at 2.40 s — the film opens on the engine starting, with nobody
talking — so every word time is +2.40, and each cut lands on the pause just
before the next phrase.

The read is one connected paragraph, not five separate facts: a number with no
context, then what it means, what they put in the car, and the turn on price. The
cuts follow those clauses.

The last 2.65 s is the close: the car head-on with its lamps lit, the lockup, and
the spoken ask — "roof, or glove box, which would you keep?" — over the engine,
answered on screen by the one thing the viewer can do, before black.

Frame-exact: 354 / 95 / 94 / 33 / 170 / 295 / 159 = 1200 frames = 20.000 s at 60 fps.

Run from the engine root: python3 video-projects/1957-cadillac-eldorado-brougham/build_scenes.py

HyperFrames opens the written HTML from the engine root, so every path inside it is
relative to that root: the shared library at assets/, the plates at video-projects/<slug>/stills/.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent          # .../video-projects/<page>/1957-cadillac-eldorado-brougham
ENGINE = next(p for p in HERE.parents if (p / "assets" / "stage.js").exists())
PROJECT = HERE.relative_to(ENGINE).as_posix()   # the same folder, as the render sees it
OUT = HERE / "compositions"
OUT.mkdir(exist_ok=True)

STILLS = f"{PROJECT}/stills"
TOTAL = 20.0

SCENES = [
    # 0.00 – 5.90  the engine catches, then "Seven hundred and four. That's how many Cadillac built"
    dict(
        file="s01-hero", n=1, dur="5.900000", frames=354,
        still=f"{STILLS}/01_hero_front34-01.png", seed=11, focus="50% 56%", zoom0=1.02,
        scrim="bottom", flash_in=False, flash_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.11),
               dict(t=0.30, dur="rest", move="truckR", by=26)],
        kick="1957 · CADILLAC", kick_at=0.55,
        big=[("{NUM}", ""), ("EVER BUILT", "small")], b1_at=2.25, b2_at=4.30,
        count=(0, 704, 2.25, 1.15),
        rule=5.10, lab="ELDORADO BROUGHAM", lab_at=5.16,
    ),
    # 5.90 – 7.48  "and every one was finished by hand"
    dict(
        file="s02-side", n=2, dur="1.583333", frames=95,
        still=f"{STILLS}/02_side_profile-01.png", seed=23, focus="50% 52%", zoom0=1.03,
        scrim="bottom", flash_in=True, flash_out=True,
        shots=[dict(t=0, dur="full", move="truckL", by=42),
               dict(t=0, dur="full", move="push", by=0.05)],
        kick=None, kick_at=None,
        big=[("EVERY ONE", ""), ("BY HAND", "red")], b1_at=0.10, b2_at=0.75,
        rule=None, lab=None, lab_at=None,
    ),
    # 7.48 – 9.05  "a brushed stainless roof"
    dict(
        file="s03-rear", n=3, dur="1.566667", frames=94,
        still=f"{STILLS}/03_rear34-01.png", seed=37, focus="50% 50%", zoom0=1.02,
        scrim="bottom", flash_in=True, flash_out=True,
        shots=[dict(t=0, dur="full", move="orbitR", by=34),
               dict(t=0, dur="full", move="push", by=0.07)],
        kick=None, kick_at=None,
        big=[("STAINLESS", ""), ("STEEL", "red")], b1_at=0.12, b2_at=0.52,
        rule=0.92, lab="BRUSHED, NOT PAINTED", lab_at=0.98,
    ),
    # 9.05 – 9.60  a 0.55 s insert: the bay, no type, the breath between roof and glovebox
    dict(
        file="s04-engine", n=4, dur="0.550000", frames=33,
        still=f"{STILLS}/04_engine_bay-01.png", seed=53, focus="52% 50%", zoom0=1.10,
        scrim="none", flash_in=True, flash_out=True,
        shots=[dict(t=0, dur="full", move="push", by=0.06)],
        kick=None, kick_at=None,
        big=None, b1_at=None, b2_at=None,
        rule=None, lab=None, lab_at=None,
    ),
    # 9.60 – 12.43  "a vanity set with six magnetic cups in the glovebox"
    dict(
        file="s05-interior", n=5, dur="2.833333", frames=170,
        still=f"{STILLS}/05_interior_dash-01.png", seed=67, focus="58% 54%", zoom0=1.04,
        scrim="bottom", flash_in=True, flash_out=True,
        shots=[dict(t=0, dur="full", move="orbitL", by=40),
               dict(t=0, dur="full", move="push", by=0.09)],
        kick=None, kick_at=None,
        big=[("VANITY SET", ""), ("SIX CUPS", "red")], b1_at=0.14, b2_at=0.46,
        rule=1.02, lab="MAGNETIC, SO THEY STAY PUT", lab_at=1.10,
    ),
    # 12.43 – 17.35  "and then they asked $13,074 … more than a Rolls-Royce"
    dict(
        file="s06-wheel", n=6, dur="4.916667", frames=295,
        still=f"{STILLS}/06_wheel_close-01.png", seed=79, focus="56% 56%", zoom0=1.02,
        scrim="bottom", flash_in=True, flash_out=True,
        shots=[dict(t=0, dur="full", move="truckR", by=38),
               dict(t=0, dur="full", move="push", by=0.06)],
        kick=None, kick_at=None,
        big=[("$13,074", ""), ("MORE THAN A ROLLS-ROYCE", "small")], b1_at=0.85, b2_at=3.40,
        rule=3.75, lab="1957 LIST PRICE", lab_at=3.81,
    ),
    # 17.35 – 20.00  no words: the car head-on, lamps lit, engine revving, the lockup,
    # then the question — the one thing the viewer can act on before it goes black
    dict(
        file="s07-close", n=7, dur="2.650000", frames=159,
        still=f"{STILLS}/07_close_front-02.png", seed=91, focus="50% 52%", zoom0=1.14,
        scrim="bottom", flash_in=True, flash_out=False,
        shots=[dict(t=0, dur="full", move="pull", by=0.11)],
        kick="VINTAGE MOTOR HOUSE", kick_at=0.05,
        big=[("ELDORADO", ""), ("BROUGHAM", "red")], b1_at=0.14, b2_at=0.28,
        rule=None, lab=None, lab_at=None,
        ask="THE ROOF, OR THE GLOVEBOX?", ask_at=0.39,
        ask2="TELL US IN THE COMMENTS", ask2_at=1.20,
        fade_at=2.05,
    ),
]

TEMPLATE = """<!doctype html>
<!-- SCENE {n:02d} of 7 — full-bleed car plate, camera moving, text cut to the voice. {dur} s. -->
<html lang="en">
<head>
<meta charset="utf-8">
<title>Eldorado Brougham — {n:02d} {slug}</title>
<script src="assets/gsap.min.js"></script>
<script src="assets/stage.js"></script>
<script src="assets/kit-config.js"></script>
<script src="assets/broll.js"></script>
<script src="assets/text.js"></script>
<link rel="stylesheet" href="assets/fonts.css">
<style>
  html, body {{ margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: #050506; }}
  #plate {{ position: absolute; inset: 0; z-index: 0; }}
  #fg {{ position: absolute; inset: 0; z-index: 2; color: #F5EFE6; }}
  .scrim {{ position: absolute; left: 0; right: 0; {scrim_side}: 0; height: {scrim_h}; background: {scrim_grad}; }}
{styles}
  #flash {{ position: absolute; inset: 0; z-index: 9; background: #F5EFE6; opacity: 0; pointer-events: none; }}
  #fade {{ position: absolute; inset: 0; z-index: 11; background: #000; opacity: 0; pointer-events: none; }}
</style>
</head>
<body>
<div id="root" data-composition-id="{id}" data-start="0" data-duration="{dur}" data-width="1920" data-height="1080">
  <div id="plate" class="clip" data-start="0" data-duration="{dur}" data-track-index="0"></div>
  <div id="fg" class="clip" data-start="0" data-duration="{dur}" data-track-index="1">
{scrim_markup}    <div class="sweep" id="sweep"></div>
    <div class="motes" id="motes"></div>
{markup}    <div class="rail"><div class="railfill" id="rail"></div></div>
  </div>
  <div id="flash" class="clip" data-start="0" data-duration="{dur}" data-track-index="5"></div>
  <div id="fade" class="clip" data-start="0" data-duration="{dur}" data-track-index="6"></div>
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
    handheld: 0.9,
    grain: 0.22,
    vignette: 0.46,
    shots: [{shots}],
    shakes: [{{ at: 0.02, power: 0.16, decay: 0.14 }}],
  }});

  const tl = S.driver(DUR, () => {{}});
  BROLL.live(tl, cam);

{fx}

{tweens}

{flash}
  window.__timelines = window.__timelines || {{}};
  window.__timelines['{id}'] = tl;
}})();
</script>
</body>
</html>
"""

BIG_CSS = """  .kick { position: absolute; left: 100px; top: 82px; padding: 13px 22px 12px 19px; border-left: 3px solid #C8321E; background: rgba(8,8,9,0.66); font: 700 26px/1 'JetBrains Mono', monospace; letter-spacing: 0.30em; color: #F4EDE3; }
  .b1, .b2 { position: absolute; left: 104px; font: 400 154px/0.92 'Anton', sans-serif; letter-spacing: -0.005em; }
  .b2.small { font-size: 70px; letter-spacing: 0.01em; }
  .red { color: #E8412B; }
  .rule { position: absolute; left: 110px; width: 176px; height: 3px; background: #E8412B; transform-origin: 0 50%; }
  .lab { position: absolute; left: 110px; font: 700 30px/1 'JetBrains Mono', monospace; letter-spacing: 0.28em; }
  .ask { position: absolute; left: 108px; top: 962px; font: 400 54px/1 'Anton', sans-serif; letter-spacing: 0.015em; color: #F5EFE6; }
  .ask2 { position: absolute; left: 112px; top: 1030px; font: 700 23px/1 'JetBrains Mono', monospace; letter-spacing: 0.26em; color: #F4623F; }"""

FX_CSS = """  .rail { position: absolute; left: 0; right: 0; bottom: 0; height: 3px; background: rgba(245,239,230,0.09); }
  .railfill { position: absolute; left: 0; top: 0; bottom: 0; width: 100%; transform: scaleX(0); transform-origin: 0 50%; background: #E8412B; }
  .sweep { position: absolute; top: -30%; left: 0; width: 46%; height: 170%; transform: rotate(15deg); background: linear-gradient(90deg, rgba(245,239,230,0) 0%, rgba(245,239,230,0.11) 50%, rgba(245,239,230,0) 100%); }
  .mote { position: absolute; border-radius: 50%; background: rgba(245,239,230,0.75); }
  .escape { position: absolute; left: 0; right: 0; bottom: 0; height: 660px; }"""

# The always-on furniture. Kept out of .format so the JS braces stay readable.
FX_JS = """  // furniture that never stops: film-long rail, a light pass, motes
  tl.fromTo($('rail'), { scaleX: GS / TOTAL }, { scaleX: Math.min(1, (GS + DUR) / TOTAL), duration: DUR, ease: 'none' }, 0);

  const rnd = S.mulberry32(SEED * 31 + 7);
  const box = $('motes');
  for (let i = 0; i < 16; i++) {
    const m = document.createElement('div');
    m.className = 'mote';
    const sz = 2 + (rnd() > 0.55 ? 1 : 0);
    m.style.width = sz + 'px';
    m.style.height = sz + 'px';
    m.style.left = Math.round(rnd() * 1890) + 'px';
    m.style.top = Math.round(rnd() * 1050) + 'px';
    box.appendChild(m);
    const rise = 70 + rnd() * 150, dx = (rnd() - 0.5) * 70, t0 = rnd() * 0.6;
    tl.fromTo(m, { opacity: 0 }, { opacity: 0.42, duration: 0.55, ease: 'power1.out' }, t0);
    tl.fromTo(m, { y: 0, x: 0 }, { y: -rise, x: dx, duration: DUR - t0, ease: 'none' }, t0);
    tl.to(m, { opacity: 0, duration: 0.6, ease: 'power1.in' }, Math.max(DUR - 0.6, t0 + 0.6));
  }
SWEEPS"""


def fx_script(seed: int, gs: float, dur: float) -> str:
    """Scene-local slice of the always-on layers, phase-locked to the film clock."""
    sweeps = []
    period, travel = 2.6, 1.15
    k = 0
    while k * period - gs < dur:
        at = k * period - gs
        if at > -travel:
            sweeps.append(
                f"  tl.fromTo($('sweep'), {{ x: -1500 }}, {{ x: 2100, duration: {travel}, ease: 'none' }}, {max(at, -travel + 0.01):.3f});")
        k += 1
    sw = ("  // a light pass every 2.6 s, aligned across cuts\n" + "\n".join(sweeps)) if sweeps \
        else "  tl.set($('sweep'), { x: -1500 }, 0);"
    return (FX_JS.replace("SWEEPS", sw)
                 .replace("SEED", str(seed))
                 .replace("GS / TOTAL", f"{gs:.4f} / {TOTAL}")
                 .replace("(GS + DUR) / TOTAL", f"{gs + dur:.4f} / {TOTAL}"))


def build(s: dict, gs: float) -> tuple:
    dur = float(s["dur"])
    side = s["scrim"]
    if side == "full":
        scrim_h, scrim_side = "1080px", "top"
        scrim_grad = ("linear-gradient(180deg, rgba(5,5,6,0.55) 0%, rgba(5,5,6,0.62) 45%, "
                      "rgba(5,5,6,0.84) 100%)")
        scrim_markup = '    <div class="scrim"></div>\n'
    elif side == "none":
        scrim_h, scrim_side, scrim_grad, scrim_markup = "660px", "bottom", "none", ""
    else:
        scrim_h, scrim_side = "660px", "bottom"
        scrim_grad = ("linear-gradient(0deg, rgba(5,5,6,0.90) 0%, rgba(5,5,6,0.70) 36%, "
                      "rgba(5,5,6,0.26) 74%, rgba(5,5,6,0) 100%)")
        scrim_markup = '    <div class="scrim"></div>\n'

    y1, y2, rule_y, lab_y = 640, 792, 956, 984

    markup, tweens = [], []
    if s["kick"]:
        markup.append(f'    <div class="kick" id="kick">{s["kick"]}</div>')
        tweens.append(f"  TX.words(tl, $('kick'), {s['kick_at']:.2f}, 0.05);")

    if s["big"]:
        b1, b1cls = s["big"][0]
        b2, b2tag = s["big"][1]
        if "{NUM}" in b1:
            b1 = b1.replace("{NUM}", '<span id="num">0</span>')
        markup.append(f'    <div class="b1" id="b1" style="top:{y1}px">{b1}</div>')
        cls = "b2" + (" red" if b2tag == "red" else "") + (" small" if b2tag == "small" else "")
        markup.append(f'    <div class="{cls}" id="b2" style="top:{y2}px">{b2}</div>')
        tweens.append(f"  TX.slam(tl, $('b1'), {s['b1_at']:.2f});")
        tweens.append(f"  TX.slam(tl, $('b2'), {s['b2_at']:.2f});")

    if s.get("count"):
        lo, hi, at, span = s["count"]
        tweens.append(
            f"  const ctr = {{ v: {lo} }};\n"
            f"  tl.to(ctr, {{ v: {hi}, duration: {span}, ease: 'power2.out',\n"
            f"      onUpdate: () => {{ $('num').textContent = Math.round(ctr.v); }} }}, {at:.2f});")

    if s["rule"] is not None:
        markup.append(f'    <div class="rule" id="rule" style="top:{rule_y}px"></div>')
        tweens.append(f"  tl.fromTo($('rule'), {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.34, ease: 'power3.out' }}, {s['rule']:.2f});")
    if s["lab"]:
        markup.append(f'    <div class="lab" id="lab" style="top:{lab_y}px">{s["lab"]}</div>')
        tweens.append(f"  TX.words(tl, $('lab'), {s['lab_at']:.2f}, 0.05);")

    # the end card's ask: a question, then the one action that answers it
    if s.get("ask"):
        markup.append(f'    <div class="ask" id="ask">{s["ask"]}</div>')
        tweens.append(f"  TX.words(tl, $('ask'), {s['ask_at']:.2f}, 0.045);")
    if s.get("ask2"):
        markup.append(f'    <div class="ask2" id="ask2">{s["ask2"]}</div>')
        tweens.append(f"  TX.words(tl, $('ask2'), {s['ask2_at']:.2f}, 0.03);")

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
    if s.get("fade_at"):
        fade_at = s["fade_at"]
        flash.append(f"  tl.fromTo($('fade'), {{ opacity: 0 }}, {{ opacity: 1, duration: {dur - fade_at:.2f}, ease: 'power1.inOut' }}, {fade_at:.2f});")

    html = TEMPLATE.format(
        n=s["n"], slug=s["file"].split("-", 1)[1], id=s["file"], dur=s["dur"], still=s["still"],
        seed=s["seed"], zoom0=s["zoom0"], focus=s["focus"],
        scrim_side=scrim_side, scrim_h=scrim_h, scrim_grad=scrim_grad,
        scrim_markup=scrim_markup,
        styles=BIG_CSS + "\n" + FX_CSS,
        markup="\n".join(markup) + ("\n" if markup else ""),
        fx=fx_script(s["seed"], gs, dur),
        tweens="\n".join(tweens), shots=shots, flash="\n".join(flash),
    )
    (OUT / f"{s['file']}.html").write_text(html)
    return s["file"], s["frames"]


total, clock = 0, 0.0
for s in SCENES:
    name, fr = build(s, clock)
    clock += float(s["dur"])
    total += fr
    print(f"{name}.html  {s['dur']:>9}s  {fr:>3} frames")
print(f"total {total} frames = {total / 60:.3f}s at 60 fps")
