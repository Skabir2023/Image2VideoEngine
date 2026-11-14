# Eldorado Brougham — plates

All six drawn free through Google Flow (`tools/imagegen/engine.py --engine flow`), 16:9,
1920×1080, one 35 mm-ish studio plate each, same identity block every time so the six read
as one car:

> Photorealistic 1957 Cadillac Eldorado Brougham, ivory-white four-door pillarless hardtop,
> brushed stainless steel roof, quad headlamps, Dagmar front bumper bullets, gold-anodized
> grille, whitewall tires, industrial concrete studio background, soft overcast light,
> 35 mm photograph, no people, no text, no watermark, no modern cars.

| # | File | Shot | Checked |
|---|---|---|---|
| 1 | `01_hero_front34-01.png` | front three-quarter hero, quad lamps and gold grille | yes — ivory hardtop, stainless roof, correct nose |
| 2 | `02_side_profile-01.png` | full side profile, body line and whitewalls | yes — same car, hardtop roofline, wire wheels |
| 3 | `03_rear34-01.png` | rear three-quarter, tail fins and rear bumper | yes — same car, stainless roof reads |
| 4 | `04_engine_bay-01.png` | hood open on the V8, dual quads, chrome air cleaner | yes — bay detail, gold grille and dagmars on the nose |
| 5 | `05_interior_dash-01.png` | camera on the rear seat looking forward: turquoise benches, chrome dash, glovebox | yes — no people, dash and glovebox read, no doors in shot |
| 6 | `06_wheel_close-01.png` | tight front wheel, whitewall, wire wheel, gold crest | yes — crest hubcap, rocker trim |
| 7 | `07_close_front-02.png` | head-on, low angle, quad lamps lit, gold grille, concrete hall | yes — lamps lit, no people, no text |

Raw jpegs from the generator are kept in `stills/_raw/`; each PNG has a `*.images.json`
manifest next to it.

The industrial concrete backdrop was chosen on purpose: the bottom of every plate is dark
enough for the scrim and the ivory type to sit on without a separate grade.

The interior plate was redrawn after the first cut: the open front door was hinged at the
wrong end and carried a floating window-frame bar. The replacement puts the camera inside
the cabin, so no door is in shot at all (`05_interior_dash-OLD.png` keeps the rejected one).

The seventh plate is the close: the same car head-on with its lamps lit, so the film can
end on the engine revving over a fresh image instead of stopping on the price card.
`07_close_front-01.png` is the spare take.
