# Boss 429 — 15s old-car B-roll reel (full workflow test)

Subject: 1969 Ford Mustang Boss 429.
Format: 15 seconds, 9:16 vertical, 6 plates x ~2.5s, 16:9 source images.
Final path: Sumi HTML composition + render path, then merge Kokoro voiceover.

## Shot ladder (fixed, same for every car in this reel style)

1. 01_hero_front34 — front three-quarter hero, hook image
2. 02_side_profile — full side profile
3. 03_rear34 — rear three-quarter / exhaust
4. 04_engine_bay — open engine bay, top-down detail
5. 05_interior_dash — steering wheel + dashboard, driver side
6. 06_wheel_close — wheel close-up, payoff image

## Timing

- 15s total, 6 shots.
- Each shot ≈ 2.5s.
- Transitions between shots are keyframe camera moves / motion-graphics cuts in the composition, not separate offline clips.

## Camera-move grammar per shot (to express in the composition)

- Shot 1 hero: slow push-in / slight rise to seat the grille + one headlight in the 9:16 crop.
- Shot 2 side: lateral reveal along the long body line.
- Shot 3 rear: settle on tail-lights + stance, slight re-center.
- Shot 4 engine: controlled top-down settle into the bay.
- Shot 5 interior: slow settle into the dash/wheel, driver-side angle.
- Shot 6 wheel: hold on the wheel/tire detail, the closing payoff.

## Visual identity to lock across all 6 plates

- 1969 Ford Mustang Boss 429.
- Same exterior color, same body style, same wheel/tire look in every image.
- Documentary low-overcast daylight, empty lot/showground, no people, no animals, no text/watermark.
- 16:9 generation; final composition crops/positions for 9:16.

## Pipeline order

1. Subject locked.
2. Viral-score table + fact-check.
3. 15s voiceover script + caption.
4. 6 Flow image prompts (identical CAR IDENTITY BLOCK).
5. Generate 6 stills.
6. Fact-check image<->script match + no-living-beings check.
7. Build 6 scene compositions.
8. Render, scan, join.
9. Kokoro voiceover + merge.
10. Show the timeline.
