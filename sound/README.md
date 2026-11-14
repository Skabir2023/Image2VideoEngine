# Engine recordings

Both files are from Pixabay, under the **Pixabay Content License**: free for
commercial use, no attribution required, no royalties. The one restriction is that the
audio file may not be redistributed on its own or claimed as your own recording —
using it inside the video, as here, is fine.

| File | Length | Used for | Source |
| --- | --- | --- | --- |
| `big-block-v8-rev_henaway_pixabay-90919.mp3` | 3.76 s | the engine bed (sustained 0.45–1.55 s looped) and the closing rev, in the first two films | Henaway — pixabay.com/sound-effects/city-big-block-v8-rev-90919/ |
| `engine-start-idle-rev_nhumphrey_pixabay-33510.mp3` | 39.31 s | **the current sound law**: start `0.10–1.60 s`, bed `14.00–16.00 s`, closing roar `27.72–29.45 s` at rate `0.86` | NHumphrey — pixabay.com/sound-effects/technology-car-engine-start-idle-and-revving-33510/ |

They are generic engines, not recordings of the actual car — the second file carries a start, an idle
and a rev, which is why the current sound law (start / bed / roar) is built entirely from it.

Both files are quiet: the NHumphrey recording measures about `−47 dBFS` RMS in its idle. Level-match
whatever slice you take to a target RMS in the build script and print the measured result; a fixed
`volume=` multiplier will give you an inaudible bed.
