# Script — 1954 Mercedes-Benz 300SL Gullwing

**Doors That Opened To Sky** · Why It Became Legend · 45 words · 18.8 s

## The read, as one paragraph

Mercedes built a race car, whose frame was too high to climb over, so the doors went up. They built only 1,400 of them. That body still hit 161 miles per hour, because fuel went straight into the cylinder. Would you dare drive a legend?

One chain, not four facts in a row. Every line is caused by the one before it:

- the **frame** was too high, **so** the **doors** went up;
- **they built only 1,400** — the consequence of being hand-built around that frame;
- **that body still hit 161** — the payoff, and **because fuel went straight into the
  cylinder**, the reason it could;
- **would you dare** — the question the whole chain has earned.

Word count: 45 (the 15 s band is 38–45). No number is invented: 1,400 coupes, 161 mph,
direct injection into the cylinder, and the high sill that made the doors go up are all in
`FACTCHECK.md`. Horsepower is left out on purpose — the film does not need a fourth figure.

## Beats

- **HOOK** (1.05–2.50, 1.45 s) — "Mercedes built a race car," / the car that had to be
  climbed into.
- **TURN** (2.50–4.70, 2.20 s) — "whose frame was too high to climb over,"
- **PAYOFF OF THE TURN** (4.70–6.13, 1.43 s) — "so the doors went up."
- **SCARCITY** (6.13–9.13, 3.00 s) — "They built only 1,400 of them."
- **SPEED** (9.13–12.75, 3.62 s) — "That body still hit 161 miles per hour,"
- **REASON** (12.75–15.15, 2.40 s) — "because fuel went straight into the cylinder."
- **QUESTION** (15.15–16.57, 1.42 s) — "Would you dare drive a legend?"
- **ANSWER** (16.57–18.80, 2.23 s) — no words. The engine roars.

## Caption

**The Fastest 1954 Mercedes 300SL Gullwing Ever Built**

You have probably never climbed into a car through the roof. In 1954 you had to: the 300SL's
frame sat so high that Mercedes hinged the doors upward instead. They built only 1,400 of them.
And that same body ran 161 miles per hour, because fuel went straight into the cylinder, no
carburetor in the way. Would you drive it, or would you just open both doors and watch people
stare?

 #Mercedes #ClassicCars #300SL #Gullwing #VintageMotorHouse

Caption score **88**/100 (gate 80): hook shock 22/25, relatability 18/20, curiosity gap 18/20,
shareability 13/15, visual wow 17/20. The first caption — "Doors That Opened To Sky" over one
line of fact — scored 64 and was replaced: atmospheric, but no second person, no numbers and
no question to answer. It also failed the grounding test — any car with doors could carry it.

`python3 tools/caption.py check` on this caption: **passes** (8-word title with the year, the
model and `Fastest`; 5 sentences, 71 words, second person, ends on a question; 5 tags; 88 ≥ 80).

Title = 8 words, year + make + model + the power word **Fastest**, no full stop.
"Fastest production car of its day" is Mercedes' own wording (`FACTCHECK.md`), so the word is
sourced, not a comparison invented for the caption.

Description = 5 sentences, 71 words, second person throughout, using only the film's own
verified numbers (1,400 built, 161 mph, direct injection), and ending on the question the
voiceover already asks.

Hashtags = 5, one line, brand + classic-car + model.

The render keeps the name it was built and booked under (`Doors That Opened To Sky.mp4`) —
it was already queued and uploaded, and a render is never renamed after queueing. The caption
on the post is what changes. Films built from here on carry the viral title as their file name.

## Voice

Kokoro `am_michael`, speed 1.2 in the request, one take, 15.830 s of audio.
`audio/paragraph/transcript.json` is measured on that WAV; every cut and every card time in
`scenes.py` is copied from it by hand (+1.00 s for the lead). The build never reads the JSON.
