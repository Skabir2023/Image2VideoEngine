#!/usr/bin/env python3
"""The engine's scene builder. One builder for every film; a film only holds data.

    python3 tools/scene_builder.py video-projects/<page>/<film>

It reads `<film>/scenes.py` — a table, no logic — and writes that film's
`compositions/*.html` and `index.html`. Nothing is copied between films: change the
template, the CSS or a check here and every film built afterwards has it.

`scenes.py` must define:

    FILM            the film's title, as it appears in the caption and the file name
    COMPOSITION_ID  the master timeline's id (e.g. "gullwing-reel")
    FPS             60
    LEAD            where the voice starts (1.00 s: the engine catches before it)
    PAD             LEAD - 0.30, the shift applied to every time measured at the old lead
    W               the measured word times, absolute film time
    SCENES          one dict per shot — see `## The scene table` below

Optional: `AUDIO` (default `audio/final-audio.wav`).

## The scene table

Each scene dict carries `file` (s01-hero), `still` (a bare filename in `stills/`),
`seed`, `zoom0`, `focus`, `scrim` ("top" | "bottom"), `blur_in` / `blur_out` (the seam
at its head and tail), `shots` (camera moves), and the card: `kick`, `big` (two lines),
`rule`, `lab`, `foot`, each with its own `*_at` absolute film time.

Times are written ABSOLUTE — as measured on the voice — and the builder converts them
to scene time. A time that lands outside its own scene is a hard error here, because a
card pushed past the end of its shot never renders and says nothing about it.

Frames are the source of truth: `frames = round(duration x 60)`, and the six must sum
to the film.
"""
import importlib.util
import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parent.parent

TEMPLATE = """<!doctype html>
<!-- SCENE {n:02d} of {total} — {slug}. {dur} s, frames {frames}. Cut to the voice. -->
<html lang="en">
<head>
<meta charset="utf-8">
<title>{film} — {n:02d} {slug}</title>
<script src="assets/gsap.min.js"></script>
<script src="assets/stage.js"></script>
<script src="assets/kit-config.js"></script>
<script src="assets/broll.js"></script>
<script src="assets/text.js"></script>
<script src="assets/seams.js"></script>
<link rel="stylesheet" href="assets/fonts.css">
<style>
  html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #050506; }}
  #plate {{ position: absolute; inset: 0; z-index: 0; will-change: filter; }}
  #fg {{ position: absolute; inset: 0; z-index: 2; color: #F5EFE6; }}
  .scrim {{ position: absolute; left: 0; right: 0; {scrim_side}: 0; height: 1020px; background: {scrim_grad}; }}
{styles}
  #leak {{ position: absolute; inset: -10%; z-index: 3; pointer-events: none; opacity: 0; mix-blend-mode: screen;
          background: radial-gradient(ellipse 46% 38% at 30% 28%, rgba(255,183,120,0.55) 0%, rgba(232,65,43,0.22) 42%, rgba(232,65,43,0) 72%); }}
</style>
</head>
<body>
<div id="root" data-composition-id="{id}" data-start="0" data-duration="{dur}" data-width="1080" data-height="1920">
  <div id="plate" class="clip" data-start="0" data-duration="{dur}" data-track-index="0"></div>
  <div id="fg" class="clip" data-start="0" data-duration="{dur}" data-track-index="1">
    <div class="scrim"></div>
{markup}
  </div>
  <div id="leak" class="clip" data-start="0" data-duration="{dur}" data-track-index="3"></div>
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
    handheld: 1.05,
    grain: 0.25,
    vignette: 0.52,
    shots: [{shots}],
    shakes: [{shakes}],
  }});

  const tl = S.driver(DUR, () => {{}});
  BROLL.live(tl, cam);

{tweens}

{vfx}
  window.__timelines = window.__timelines || {{}};
  window.__timelines['{id}'] = tl;
}})();
</script>
</body>
</html>
"""

BIG_CSS = """  .kick { position: absolute; left: 72px; top: 150px; font: 700 31px/1 'JetBrains Mono', monospace; letter-spacing: 0.30em; color: #EFE8DC; text-shadow: 0 2px 20px rgba(0,0,0,0.92); }
  .b1, .b2 { position: absolute; left: 62px; font: 400 208px/0.90 'Anton', sans-serif; letter-spacing: -0.005em; transform-origin: 0 50%; }
  .b2.small { font-size: 96px; }
  .b2.mid { font-size: 148px; }
  .red { color: #E8412B; }
  .rule { position: absolute; left: 68px; width: 190px; height: 3px; background: #E8412B; transform-origin: 0 50%; }
  .lab { position: absolute; left: 68px; font: 700 40px/1 'JetBrains Mono', monospace; letter-spacing: 0.28em; text-shadow: 0 2px 22px rgba(0,0,0,0.95); }
  .foot { position: absolute; left: 68px; font: 500 31px/1.4 'Inter', sans-serif; color: rgba(245,239,230,0.72); text-shadow: 0 2px 18px rgba(0,0,0,0.9); }"""

# A card that lands this close to its scene's end is on screen for a blink; say so.
BLINK = 0.30


def load(film: Path):
    table = film / "scenes.py"
    if not table.exists():
        sys.exit(f"no scene table: {table}\n"
                 f"A film is data now — write {table.name} with FILM, COMPOSITION_ID, "
                 f"FPS, LEAD, PAD, W and SCENES.")
    spec = importlib.util.spec_from_file_location(f"scenes_{film.name.replace('-', '_')}", table)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check(t):
    """Refuse a table that would render nothing where it says it renders something."""
    problems, warnings = [], []
    seen = set()
    starts, acc = [], 0
    for s in t.SCENES:
        starts.append(acc / t.FPS)
        acc += s["frames"]

    for s, start in zip(t.SCENES, starts):
        dur = s["frames"] / t.FPS
        end = start + dur
        if s["file"] in seen:
            problems.append(f"{s['file']}: duplicate scene name")
        seen.add(s["file"])
        for k in ("blur_in", "blur_out"):
            if k not in s:
                problems.append(f"{s['file']}: missing {k}")

        cards = []
        if s.get("kick"):
            cards.append(("kick", s["kick_at"]))
        if s.get("big"):
            cards.append(("b1", s["b1_at"]))
            if s["big"][1][0]:
                cards.append(("b2", s["b2_at"]))
        if s.get("rule"):
            cards.append(("rule", s["rule"]))
        if s.get("lab"):
            cards.append(("lab", s["lab_at"]))
        if s.get("foot"):
            cards.append(("foot", s["foot_at"]))

        for name, when in cards:
            at = when + t.PAD
            if not (start - 1e-6 <= at <= end + 1e-6):
                problems.append(f"{s['file']}: {name} at {at:.3f} s is outside the scene "
                                f"({start:.3f}–{end:.3f}) — it would never render")
            elif end - at < BLINK:
                warnings.append(f"{s['file']}: {name} at {at:.3f} s has only {end - at:.2f} s "
                                f"on screen before the cut")
    return problems, warnings, starts


def build(t, film: Path, project: str, out: Path, s, start: int):
    slug = s["file"].split("-", 1)[1]
    dur = s["frames"] / t.FPS
    top = s["scrim"] == "top"
    scrim_side = "top" if top else "bottom"
    # a macro plate is bright right where the type sits, so those shots get a deeper scrim
    g = s.get("scrim_gain", 1.0)
    a = lambda v: min(1.0, v * g)
    scrim_grad = (f"linear-gradient(180deg, rgba(5,5,6,{a(0.97):.2f}) 0%, rgba(5,5,6,{a(0.90):.2f}) 42%, "
                  f"rgba(5,5,6,{a(0.62):.2f}) 74%, rgba(5,5,6,0) 100%)") if top else \
                 (f"linear-gradient(0deg, rgba(5,5,6,{a(0.96):.2f}) 0%, rgba(5,5,6,{a(0.84):.2f}) 40%, "
                  f"rgba(5,5,6,{a(0.52):.2f}) 76%, rgba(5,5,6,0) 100%)")

    if top:
        y1, y2 = 300, 500
        rule_y, lab_y, foot_y = 760, 794, 880
    else:
        y1, y2 = 1120, 1330
        rule_y, lab_y, foot_y = 1560, 1594, 1690
    if s.get("big") and s["big"][1][1] == "small":
        y2 = y1 + 220
    if s.get("b2_size") == "mid":
        y2 = y1 + 290

    # absolute film time (measured before the lead) -> scene time
    rel = lambda x: max(0.0, round(x + t.PAD - start, 3))

    markup, tweens = [], []
    if s.get("kick"):
        markup.append(f'    <div class="kick" id="kick">{s["kick"]}</div>')
        tweens.append(f"  TX.words(tl, $('kick'), {rel(s['kick_at']):.3f}, 0.04);")

    if s.get("big"):
        b1, _b1cls = s["big"][0]
        b2, b2tag = s["big"][1]
        markup.append(f'    <div class="b1" id="b1" style="top:{y1}px">{b1}</div>')
        if b2:
            cls = "b2" + (" red" if b2tag == "red" else "") + (" small" if b2tag == "small" else "") \
                + (" mid" if s.get("b2_size") == "mid" else "")
            markup.append(f'    <div class="{cls}" id="b2" style="top:{y2}px">{b2}</div>')
        markup.append(f'    <div class="rule" id="rule" style="top:{rule_y}px"></div>')

        tweens.append(f"  TX.slam(tl, $('b1'), {rel(s['b1_at']):.3f});")
        if s.get("roll"):
            tweens.append(f"  TX.roll(tl, $('b1'), {rel(s['b1_at']):.3f}, "
                          f"{s['roll']['dur']:.2f}, {s['roll']['seed']});")
        if b2:
            tweens.append(f"  TX.slam(tl, $('b2'), {rel(s['b2_at']):.3f});")
        if s.get("rule"):
            tweens.append(f"  tl.fromTo($('rule'), {{ scaleX: 0 }}, "
                          f"{{ scaleX: 1, duration: 0.34, ease: 'power3.out' }}, {rel(s['rule']):.3f});")
        if s.get("lab"):
            markup.append(f'    <div class="lab" id="lab" style="top:{lab_y}px">{s["lab"]}</div>')
            tweens.append(f"  TX.words(tl, $('lab'), {rel(s['lab_at']):.3f}, 0.04);")
    if s.get("foot"):
        markup.append(f'    <div class="foot" id="foot" style="top:{foot_y}px">{s["foot"]}</div>')
        tweens.append(f"  tl.fromTo($('foot'), {{ opacity: 0, y: 16 }}, "
                      f"{{ opacity: 1, y: 0, duration: 0.40, ease: 'power3.out' }}, {rel(s['foot_at']):.3f});")

    shots = ", ".join(
        "{{ t: {t}, dur: {dur}, move: '{move}', by: {by}, ease: 'inOutSine' }}".format(
            t=sh["t"], dur=("DUR" if sh["dur"] == "full" else f"DUR - {sh['t']}"),
            move=sh["move"], by=sh["by"])
        for sh in s["shots"])

    shakes = ["{ at: 0.03, power: 0.20, decay: 0.12 }"]
    for sk in s.get("extra_shakes", []):
        shakes.append("{{ at: {at:.2f}, power: {power:.2f}, decay: {decay:.2f} }}".format(**sk))

    # --- seams and VFX -------------------------------------------------------
    # The blur cut lives in the engine (assets/seams.js): one call per composition, and a
    # scene only says whether it focuses in at its head and defocuses at its tail. Frame 0
    # of the film and the last frame pass 0, so both stay sharp.
    vfx = [f"  SEAM.blur(tl, DUR, {{ in: {0.18 if s['blur_in'] else 0}, "
           f"out: {0.20 if s['blur_out'] else 0} }});"]

    if s.get("leak"):
        vfx.append("  tl.fromTo($('leak'), { opacity: 0, x: -120, y: 60 }, "
                   "{ opacity: 0.85, x: 90, y: -40, duration: DUR, ease: 'none' }, 0);")
        vfx.append("  tl.fromTo($('leak'), { opacity: 0 }, { opacity: 0.55, duration: 0.55, "
                   "ease: 'power2.out' }, 0);")
        vfx.append(f"  tl.to($('leak'), {{ opacity: 0, duration: 0.45, ease: 'power2.in' }}, DUR - 0.45);")

    html = TEMPLATE.format(
        film=t.FILM, total=len(t.SCENES), n=s["n"], slug=slug, id=s["file"],
        dur=f"{dur:.6f}", frames=s["frames"], still=f"{project}/stills/{s['still']}",
        seed=s["seed"], zoom0=s["zoom0"], focus=s["focus"],
        scrim_side=scrim_side, scrim_grad=scrim_grad,
        styles=BIG_CSS, markup="\n".join(markup), tweens="\n".join(tweens),
        shots=shots, vfx="\n".join(vfx), shakes=", ".join(shakes),
    )
    (out / f"{s['file']}.html").write_text(html)
    return dur


def main(argv):
    if len(argv) != 2:
        sys.exit(__doc__.split("## The scene table")[0].rstrip())
    film = Path(argv[1]).resolve()
    if not film.is_dir():
        sys.exit(f"no such film folder: {argv[1]}")
    project = film.relative_to(ENGINE).as_posix()
    out = film / "compositions"
    out.mkdir(exist_ok=True)

    t = load(film)
    problems, warnings, starts = check(t)
    for w in warnings:
        print(f"warning: {w}")
    if problems:
        print("\n".join(f"error: {p}" for p in problems))
        sys.exit(f"\n{len(problems)} problem(s) — nothing written.")

    total = sum(s["frames"] for s in t.SCENES)
    rows = []
    for s, start in zip(t.SCENES, starts):
        rows.append((s["file"], start, build(t, film, project, out, s, start), s["frames"]))

    print(f"\n{t.FILM}: {len(t.SCENES)} scenes, {total} frames = {total / t.FPS:.3f}s at {t.FPS} fps")
    print(f"\n{'scene':<16}{'start':>9}{'dur':>9}{'frames':>8}")
    for f, st, d, fr in rows:
        print(f"{f:<16}{st:>9.3f}{d:>9.3f}{fr:>8}")

    audio = getattr(t, "AUDIO", "audio/final-audio.wav")
    layers = "\n".join(
        f'  <div id="layer-{i+1:02d}" class="comp-layer" data-composition-id="{f}"\n'
        f'       data-composition-src="compositions/{f}.html"\n'
        f'       data-start="{st:.6f}" data-duration="{d:.6f}" data-track-index="{i+1}"></div>'
        for i, (f, st, d, fr) in enumerate(rows))

    (film / "index.html").write_text(f"""<!doctype html>
<!-- {t.FILM} — master timeline. {len(rows)} scenes, {total} frames = {total / t.FPS:.3f} s at {t.FPS} fps.
     Written by tools/scene_builder.py from scenes.py, so the layers can never drift from the scenes. -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{t.FILM}</title>
<script src="assets/gsap.min.js"></script>
<style>
  html, body {{ margin: 0; padding: 0; width: 1080px; height: 1920px; overflow: hidden; background: #050506; }}
  #master {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; }}
  .comp-layer {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }}
</style>
</head>
<body>
<div id="master" data-composition-id="{t.COMPOSITION_ID}" data-start="0" data-duration="{total / t.FPS:.6f}"
     data-width="1080" data-height="1920">

  <audio id="master-mix" src="{audio}" data-start="0" data-duration="{total / t.FPS:.6f}"
         data-track-index="20" data-volume="1"></audio>

{layers}
</div>

<script>
  window.__timelines = window.__timelines || {{}};
  const tl = gsap.timeline({{ paused: true }});
  window.__timelines['{t.COMPOSITION_ID}'] = tl;
</script>
</body></html>
""")
    print(f"\nwrote {len(rows)} compositions + index.html")


if __name__ == "__main__":
    main(sys.argv)
