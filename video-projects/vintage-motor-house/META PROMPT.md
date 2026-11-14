# META PROMPT — the page's research, scoring, script, caption and image prompts

This is the prompt the engine sends to **Meta AI** (through Browser MCP) at the start of every
batch. Meta does the topic scoring, the fact-check, the voiceover script, the title, the
description, the hashtags and the six image prompts. The agent drives it and, when Meta fails,
does the same work itself in the same shape.

Send it with (everything above the marker is for us; everything below it is what Meta reads):

    python3 tools/meta.py ask --prompt-file "video-projects/vintage-motor-house/META PROMPT.md" --out video-projects/vintage-motor-house/plan/META-batch-<date>.md --timeout 540

Only the **INPUT** block at the bottom changes per batch: the candidates, the page numbers and
how many posts are wanted. Keep the OUTPUT CONTRACT exactly as written — the film folders depend
on that shape, and Browser MCP truncates long replies, so the answer must stay compact.

<!-- SEND BELOW -->

You are the researcher and scriptwriter for Vintage Motor House, a Facebook page of 15–20 second vintage-car reels. Work only from verified facts and reply in the FORMAT at the end.

YOU HAVE WEB SEARCH. For every number in a script, search and cite the source. If you are unsure about any fact, search the web and cite the source in the fact list. Never guess a production number, a price or a horsepower figure. A script with an unsourced number is unusable.

WHAT A POST IS. One car, one angle, one 15–20 second reel. Six stills of that car are animated under the voice. The six angles are: Size / Looks; Price / Rarity; Engine / Speed; Secret Story; Why It Failed; Why It Became Legend. Choose the angle that makes the strongest 3-second hook, and give no two posts the same angle. The script is 38–45 spoken words for 15 seconds, about 3 more words per extra second. It opens with the hook as its first sentence, spends the middle on two or three hard numbers, and ends on a question the viewer can answer in a comment.

SCORING — THE GATE IS 80. Score each candidate out of 100 on hook strength, broad relatability, curiosity, shareability and visual wow. 80 or more moves forward. Below 80 is rejected with a one-line reason, and you say what would fix it, another angle or nothing. Do not round up to please me: a rejected car is a useful answer.

WHAT THE PAGE HAS ALREADY DONE. Use the page data in the INPUT block. A car whose views were weak for one angle is not automatically weak for another, but a niche car that already failed on relatability stays out.

IMAGES — SIX PER POST, FIXED ORDER. front 3/4; side; rear; engine bay; interior; wheel. Vertical 1080x1920. Write one CAR IDENTITY BLOCK per car: year, make, model, body style, colour, exact trim details, grille, lights, fins or spoiler, wheels, badges, enough that six separate renders come back as the same car. Every one of the six prompts repeats the block word for word, then adds only the camera, the setting and the light. No people, no animals, no text, no logos, no watermark, no invented trim. Photoreal, as if shot on a 35 mm camera at a car show or on an empty road. The engine bay and the interior must be the correct layout for that exact year and model.

CAPTION. Title: 5 or 6 words, the strongest claim, no clickbait punctuation; this is also the file name. Description: one sentence, 12–25 words, carrying the single best number. Hashtags: 4 or 5, mixing one broad, one model-specific and the page tag.

OUTPUT CONTRACT — obey exactly. Reply with the marker <<<PLAN>>>, then ONE JSON object and nothing else, then <<<END>>>. No preamble, no markdown fences, no commentary after the JSON. Keys and nesting exactly:

{"scores":[{"car":"1959 Cadillac Eldorado Biarritz","angle":"Size / Looks","score":92,"why":"one line","verdict":"GO"}],
"posts":[{"car":"x","angle":"x","score":92,"title":"five or six words","description":"one sentence","hashtags":"hashtag1 hashtag2 hashtag3 hashtag4","script":"the spoken words","word_count":41,
"timing":[{"at":"0-3 s","role":"HOOK","text":"x"}],
"facts":[{"claim":"production","value":"1,320 built","source":"https://example.com","status":"Verified"}],
"identity_block":"the car in full detail",
"images":[{"shot":"front 3/4","prompt":"x"},{"shot":"side","prompt":"x"},{"shot":"rear","prompt":"x"},{"shot":"engine bay","prompt":"x"},{"shot":"interior","prompt":"x"},{"shot":"wheel","prompt":"x"}]}]}

verdict is GO or REJECT, with the reason in why. Give every candidate a score row, and a full post object only for the GO ones, best first. In the hashtags write each tag with the word hashtag in front, like hashtag ClassicCars, and I will convert them to the hash sign afterwards. Keep the whole JSON under 6000 characters: no prompt longer than 45 words, and script is the only long text.

INPUT. Posts wanted: 2. Reel length: 15–20 seconds, vertical 1080x1920. Page: Vintage Motor House on Facebook. One post is live: 1969 Ford Mustang Boss 429, angle Price / Rarity, score 82, published 2026-11-14, no view count yet. The car list holds 312 cars, 1940–1990; 310 are unused. Two cars have been filmed. Angle rotation so far: Price / Rarity for the Mustang, Size / Looks for a Cadillac Brougham. Candidates, all unused and never posted, spread across brands and decades: 1959 Cadillac Eldorado Biarritz; 1987 Buick GNX; 1963 Chevrolet Corvette Sting Ray; 1970 Dodge Charger Daytona; 1971 Plymouth Hemi Cuda Convertible; 1961 Lincoln Continental; 1954 Mercedes-Benz 300SL Gullwing; 1964 Ford Fairlane Thunderbolt.
