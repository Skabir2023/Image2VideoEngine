# Plates — 1969 AMC SC/Rambler

Eleven stills, generated free through **Meta AI** (Browser MCP) or **Google Flow** (0 credits in
Agent mode). Every prompt repeats the identity block verbatim so the plates read as one car in one
studio.

## Car identity block
1969 AMC Hurst SC/Rambler two-door hardtop, white body with red and blue racing stripes over the hood and roof, black grille, large ram-air hood scoop, chrome bumpers, blue painted Magnum 500 wheels with chrome trim rings, blackwall tires, gray vinyl bucket seats, Hurst T-handle shifter

## The eleven plates

Every prompt opens with `Create one photorealistic photograph, vertical portrait 9:16: ` + the
identity block, and closes with `empty concrete studio, golden hour light, 35mm, no people, no
animals, no text, no watermark`.

The six fixed angles come first and in order — front ¾, side, rear, engine bay, interior, wheel —
then five close-ups, each on a beat of its own. **No plate is used twice**: the film is 30.0 s and
`ceil(30 / 3) = 10` is the floor; eleven plates carry eleven scenes at 2.2–3.25 s each, which is
one plate more than the floor and never a still longer than ~3 s.

| # | File | Framing clause | Beat it carries |
| --- | --- | --- | --- |
| 1 | `01_hero_front34.png` | Front three-quarter, car facing camera, full car in frame, hood scoop visible | the title card over the engine start |
| 2 | `02_side.png` | Strict side view, camera exactly 90 degrees to the car, complete profile from front bumper to rear bumper, both blue wheels visible, no front or rear fascia | "AMC never planned a muscle car" |
| 3 | `03_rear.png` | Rear three-quarter, black tail panel, chrome bumper, twin exhaust tips, blue wheels visible | "It needed 500 cars to go racing" |
| 4 | `04_engine.png` | Hood lifted, engine bay filling the frame: 390 V8, four-barrel carburetor, ram-air cleaner | "a 315-horse 390" |
| 5 | `05_interior.png` | Interior through the open door: gray vinyl buckets, Sun tachometer on the steering column, Hurst T-handle shifter | "priced it at $2,998" |
| 6 | `06_wheel.png` | Extreme close-up of one front wheel filling the frame, camera low beside the car, blue Magnum 500 wheel with chrome trim ring and blackwall tyre only, just the wheel arch visible | "It hit 60 in 6.3" |
| 7 | `07_scoop.png` | Extreme close-up of the ram-air hood scoop filling the upper half of the frame, black grille below, no full car | "390 into a two-door Rambler" |
| 8 | `08_tail.png` | Extreme close-up of the rear lower panel, chrome bumper and twin exhaust tips filling the frame, black tail panel, no full car | "Then AMC built" |
| 9 | `09_headlight.png` | Extreme close-up of one round headlight and its chrome bezel filling the frame, red and blue stripe running above it, no full car | "and stopped" |
| 10 | `10_tach.png` | Close-up through the windscreen of the steering column tachometer and the top of the steering wheel, gray dash, no people | "1,512 — three times what the rule demanded" |
| 11 | `11_shifter.png` | Extreme close-up of the Hurst T-handle shifter and the black four-speed boot filling the frame, gray vinyl seat edge, no people | "or the badge?" and the closing roar |

Each `.images.json` next to the plate records engine, full prompt, size and time.

## Checks
- No people, no animals, no text overlay, no watermark.
- Same white body, red/blue stripe, Magnum 500 wheels, blackwall tires and gray interior in every plate.
- Native 9:16, scaled once to 1080×1920 with lanczos.
- Engine bay is an AMC 390 V8, not a generic small-block with a different distributor layout.
- The scoop is the upthrust SC/Rambler piece, not a flat Mustang-style scoop.
- Eleven distinct frames for eleven scenes — a still may not appear twice, and none outlives 3 s.
