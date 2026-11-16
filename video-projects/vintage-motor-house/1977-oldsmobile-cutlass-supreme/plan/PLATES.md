# Plates — 1977 Oldsmobile Cutlass Supreme

Ten stills, generated free through **Google Flow** (Agent mode, 0 credits) or **Meta AI** in one
tab. Every prompt repeats the identity block verbatim so the plates read as one car.

## Car identity block
1977 Oldsmobile Cutlass Supreme Brougham two-door Colonnade coupe, deep metallic navy-blue body with a padded dark blue Landau vinyl roof, wide chrome split grille with vertical bars, quad rectangular headlamps in chrome bezels, chrome bumpers with black rub strips, blue velour bench interior with a woodgrain dash and round gauges, Rally wheels with chrome trim rings and whitewall tyres, and a small-block V8 painted GM corporate blue under the hood

## The ten plates

Every prompt opens with `Create one photorealistic photograph, vertical portrait 9:16: ` + the
identity block, then the framing clause and an outdoor location chosen by plate number, and closes
with the showroom look and `no people, no animals, no text, no watermark`.

The six fixed angles come first and in order — front ¾, side, rear, engine bay, interior, wheel —
then four close-ups. The film is 23.6 s and `ceil(23.6 / 3) = 8` is the floor; ten plates carry ten
scenes at 1.35–3.09 s each, so no still outlives 3.1 s and no plate is used twice.

| # | File | Framing clause | Beat it carries |
| --- | --- | --- | --- |
| 1 | `01_hero_front34.png` | Front three-quarter, car facing camera, full car in frame, the wide chrome split grille and all four rectangular headlamps visible, long flat hood, upright Colonnade roofline, low camera near the front bumper | the title over the engine start |
| 2 | `02_side.png` | Parked square to the camera at a little distance, the whole car in one frame with its nose to the left, camera at door-handle height, both Rally wheels and the full Landau roof visible, no other vehicle in the frame | "America's best-seller hid a Chevrolet" |
| 3 | `03_rear.png` | Rear three-quarter, wide chrome rear bumper with rub strip, vertical taillights in the rear panel, small OLDSMOBILE lettering across the decklid, twin exhaust tips below | "They paid for a Rocket 350" |
| 4 | `04_engine.png` | Hood lifted, engine bay filling the frame: a small-block V8 with blue-painted rocker covers and a blue-painted block, a single air cleaner, the fan and the accessory belt clearly visible at the front of the engine, firewall and inner fenders behind | "Mechanics found a Chevy. The fan belt didn't fit." |
| 5 | `05_interior.png` | Shot from inside the cabin looking forward across the dashboard: blue velour bench seat visible under the camera, two-spoke steering wheel with column shifter, woodgrain instrument panel with round gauges in a row, chrome door handle on the near door, hood closed, no exterior sheet metal in frame | "GM painted every engine blue" |
| 6 | `06_wheel.png` | Extreme close-up of one front Rally wheel filling the frame, camera low beside the car, chrome trim ring and whitewall tyre only, just the wheel arch visible | "Nobody could tell" |
| 7 | `07_blue_valvecover.png` | Tight close-up of the blue-painted rocker cover on the V8, the paint the same shade as the body, an oily rag and a socket wrench resting on the inner fender, no full engine | "14,000 owners got paid" |
| 8 | `08_gauges.png` | Tight close-up of the round instrument cluster seen through the steering wheel, speedometer and odometer only, woodgrain panel around them, no full cabin | "$550 each" |
| 9 | `09_grille.png` | Extreme close-up of the centre of the split grille and the OLDSMOBILE badge filling the frame, chrome and black grille bars, the chrome bumper edge below, no full car | "Would you have looked at yours?" |
| 10 | `10_taillight.png` | Extreme close-up of one vertical taillight and the decklid edge filling the frame, chrome surround and navy paint above, no full car | the closing card and the roar |

Each `.images.json` beside the plate records the engine, the full prompt, the size and the time.

## Checks
- No people, no animals, no reflections of people, no text overlay, no watermark.
- Same navy body, blue Landau roof, Rally wheels, whitewalls and blue interior in every plate.
- Native 9:16, scaled once to 1080×1920 with lanczos; nothing cropped.
- The engine is a blue-painted small-block; the plate for the belt shows the belt, and the plate for
  the paint shows the paint, because those are the two facts the film rests on.
- Ten distinct frames for ten scenes; a still may not appear twice.
