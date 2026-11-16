# Money and other people's media

> Part of the engine manual. Index, read order and precedence: [AGENTS.md](../../AGENTS.md).

- Free routes only for images (Google Flow's Nano Banana, or Meta AI in a browser) and for voice
  (local Kokoro). Flow's **images** are free; its **videos are not** (Omni 7–12, Veo 10–100
  credits a clip), so a clip is a paid action like any other: name the total, then ask. **Ask
  before anything paid** — image APIs, stock footage, music.
- Stock footage and sound have their own free routes, keyed from `.env`: Pixabay images and
  videos, Pexels photos and videos. Pixabay has **no audio endpoint** — engine sound comes from
  `sound/engines/` and the closing hit from `sound/SFX Sound Effects/`, both already local and
  catalogued in `sound/kit.json`, never from a search. A stock clip is used only when it shows
  this film's car or an indistinguishable analogue; a modern wheel, a wrong colour or any living
  being is a reject.
- The two routes and their keys: Pixabay images `https://pixabay.com/api/` and video
  `…/api/videos/`, both taking `?key=$PIXABAY_API_KEY`; Pexels photos
  `https://api.pexels.com/v1/search` and video `…/videos/search`, both taking
  `Authorization: $PEXELS_API_KEY`. The keys live in `image2videoEngine/.env` and are never
  printed, logged or committed — report a key's length at most.
- **Neither API serves 1080×1920 plates**, and Pixabay rejects `per_page` below 3 with HTTP 400
  (its `q` is loose, so ask for ten and read them). Stock is motion accents and sound, never the
  six angles: a cropped 16:9 still cuts the car in half.
- Anything downloaded lands under that film's `stock/` with a sidecar naming the provider, the
  asset id, the page URL, the author and the licence; rejected candidates stay in `stock/qa/`.
  A clip with no recorded source cannot be published.
- The engine does not generate images. Write the prompts (see the project's `plan/PROMPTS.md` for
  the pattern), generate elsewhere, save as 1080×1920 PNG into that project's `stills/`, and
  record the prompt in the matching `<shot>.images.json`.
- Engine recordings stay under the Pixabay Content License (`sound/README.md`): usable in the
  video, never redistributed as standalone audio files.
- Never edit, re-encode or delete the person's own footage or recordings.
- Voice, if it must be remade (Kokoro running locally). Its new word times must then be copied
  into that project's `scenes.py` and `audio/build_final.py` by hand — the build does not read the
  transcript for you:

```bash
curl -s http://localhost:8880/v1/audio/speech -o audio/paragraph/line-01-v120.wav \
  -H 'Content-Type: application/json' \
  -d '{"model":"kokoro","input":"<the complete measured paragraph>","voice":"am_michael",
       "response_format":"wav","speed":1.2}'
npx hyperframes transcribe audio/paragraph/line-01-v120.wav   # → JSON sidecar beside the WAV
```

---
