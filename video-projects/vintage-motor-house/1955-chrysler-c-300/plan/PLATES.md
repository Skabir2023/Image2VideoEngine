# Plates — 1955 Chrysler C-300

Eight stills, generated free through **Meta AI** (Browser MCP) in one tab, or **Google Flow** in
Agent mode. Every prompt repeats the identity block verbatim so the plates read as one car.

## Car identity block
1955 Chrysler C-300 two-door hardtop coupe, Tango red body with a white roof, wide chrome egg-crate Imperial grille, single round headlights in heavy chrome bezels, chrome bumpers with bullet tips, small gold C-300 script badge on the front fender, tan leather bench interior, Kelsey-Hayes chrome wire wheels with whitewall tires

## The eight plates

Every prompt opens with `Create one photorealistic photograph, vertical portrait 9:16: ` + the
identity block, then the framing clause and an outdoor location chosen by plate number, and closes
with the showroom look and `no people, no animals, no text, no watermark`.

The six fixed angles come first and in order — front ¾, side, rear, engine bay, interior, wheel —
then two close-ups. The film is 20.4 s and `ceil(20.4 / 3) = 7` is the floor; eight plates carry
eight scenes at 1.7–3.85 s each, so no still outlives 3.2 s and no plate is used twice.

| # | File | Framing clause | Beat it carries |
| --- | --- | --- | --- |
| 1 | `01_hero_front34.png` | Front three-quarter, car facing camera, full car in frame, the very wide full-width chrome egg-crate grille split by a centre bar and running almost bumper to bumper, both round headlights at the outer edges, long flat hood, upright windscreen, low camera | the title card over the engine start |
| 2 | `02_side.png` | Parked on a lawn, photographed square from the side at a little distance, the whole car in one frame with its nose to the left, camera at door-handle height, both wire wheels and the full roofline visible, no other vehicle in the frame | "America's most powerful car in 1955" |
| 3 | `03_rear.png` | Rear three-quarter, chrome rear bumper, twin exhaust tips, the small tail fins and the round taillights visible | "300 horsepower, from a 331 Hemi" |
| 4 | `04_engine.png` | Hood lifted, engine bay filling the frame: 331 Hemi V8 with the bat-wing air cleaner and two four-barrel carburetors on a single intake | "At Daytona it hit 127" |
| 5 | `05_interior.png` | Interior through the open door: tan leather bench seat, wide white two-spoke steering wheel, chrome dash with round gauges, floor-mounted PowerFlite selector lever | "Chrysler named the car after its own horsepower" |
| 6 | `06_wheel.png` | Extreme close-up of one front wire wheel filling the frame, camera low beside the car, chrome Kelsey-Hayes spokes and whitewall tire only, just the wheel arch visible | "Would you take one" |
| 7 | `07_grille.png` | Extreme close-up of the centre of the egg-crate grille and the gold C-300 badge filling the frame, chrome bumper below, no full car | "Would you take one" |
| 8 | `08_taillight.png` | Extreme close-up of one round taillight and the tip of the rear fin filling the frame, chrome bumper edge below, red paint above, no full car | "with two gears?" and the closing roar |

Each `.images.json` beside the plate records the engine, the full prompt, the size and the time.

## Checks
- No people, no animals, no reflections of people, no text overlay, no watermark.
- Same Tango red body, white roof, wire wheels, whitewalls and tan interior in every plate.
- Native 9:16, scaled once to 1080×1920 with lanczos; nothing cropped.
- Engine bay is a 331 Hemi — hemispherical heads, bat-wing cleaner, two four-barrels — not a
  generic small-block.
- Eight distinct frames for eight scenes; a still may not appear twice.
