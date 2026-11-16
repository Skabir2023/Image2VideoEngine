# What to post next — the two spreadsheets

> Part of the engine manual. Index, read order and precedence: [AGENTS.md](../../AGENTS.md).

Two workbooks hold the page's production calendar, at the page level
(`video-projects/vintage-motor-house/`). They, not memory, decide what gets made. Read both before
a batch, write both after every film.

## `Vintage-Motor-House-Car-List-300.xlsx` — the 312 cars

Sheet `Car List 300+`, one row per car, 312 rows from 1940 to 1990:

`No. | Year | Brand | Model | Used? | Angle Used | Date Used | Views | Star?`

- Every row starts at `Used? = No`; `Used? = Yes` with `Angle Used` and `Date Used` is the record
  of a film that exists — never mark it for a car whose film is not finished — and `Views` /
  `Star?` follow once it is posted. Which cars to take, the 90-day wait and the new row at the
  bottom for a return are [Choosing the next car](14-choosing-the-next-car.md). (The list repeats
  `Year | Brand | Model` by design.)
- The file's own `How To Use` sheet says the same thing in four lines; keep it true instead of
  inventing a parallel convention.

## `Vintage-Motor-House-Tracker.xlsx` — the posts

Sheet `Tracker`, one row per post:

`Date | Post No. | Car (Year Make Model) | Angle Used | Viral Score % | Script Done? | Images Done? | Posted? | Views (48h) | Views (7 days) | Star? (50K+) | Notes`

- **One row = one car + one angle, and that pair never repeats.**
- `Script Done?` / `Images Done?` move as the film moves; `Posted?` when it is live; views at 48 h
  and 7 days; `Notes` records the hook and the fact used, so a Part 2 does not reuse them.
- `Star?` becomes Yes at 50,000+ views. That car earns a Part 2 after 90 days.
- State at the time of writing: one real row — 2026-11-14, Post No. 1, 1969 Ford Mustang Boss 429
  (Price / Rarity, 82, posted 02:40). The 2026-11-13 sample rows were invented and were deleted;
  the Tracker only ever records films that were actually published.

## The maths that says "don't panic"

312 cars × 3 angles = 936 posts. Two a day is about 15 months, one a day about 2.5 years, before
one angle repeats. There is therefore never a reason to pad the list with a car you cannot verify,
and never a reason to rush a batch.

## The six angles, rotated

`Size / Looks` · `Price / Rarity` · `Engine / Speed` · `Secret Story` · `Why It Failed` ·
`Why It Became Legend`

- Rotate them across a batch. Ten luxury cars in a row is the failure mode, ten reels are not.
- The angle chooses the hook, the script and what the cards say. It does **not** change the six
  stills or their order; it changes which of them carry the big cards and the footnote.
- One car can carry three to five of these, one per post, never two inside 90 days.

## Ten films, ten folders

[The working procedure](03-working-procedure.md) is the sequence; a batch runs it ten times. The
batch changes exactly one thing: the choosing happens once, up front, for all ten (steps 1–2
across the whole list, then steps 3–8 per film). Nothing about a single film changes because nine
others are being made.

Batching in practice: the engine is **one folder** and the page is **one folder**; each film is a
folder inside its page, made with the skeleton in step 2. Never clone the engine (`node_modules`
alone is 700 MB) and never copy the page — the workbooks and the queue would fork. Ten films means
ten small film folders.

A film folder is roughly 30–45 MB and holds nothing but that film. Nothing in `video-projects/` is
an input to another film; the only shared things are `assets/`, `sound/` (the kit and both
folders), `tools/` and `node_modules/`.

A film that will post itself needs only its `social` block in `meta.json` — or none at all, since
the page's `data.csv` and `uploaded.csv` are created on first use in the page folder above it. The
posting hours are page-level too (`schedule.json`): one grid per channel, and a new page gets its
own ([Slots](15-publishing.md#slots)).

Making one film a day on demand is the anti-pattern. A batch of ten is one session of work and ten
days of posts, and it is what keeps the list honest.

## Reading the workbooks without Excel

`openpyxl` is not installed, and should not be added just for this. An `.xlsx` is a zip:

```bash
python3 - <<'PY'
import zipfile, xml.etree.ElementTree as ET
N = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
z = zipfile.ZipFile('Vintage-Motor-House-Car-List-300.xlsx')
for row in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).iter(N + 'row'):
    vals = []
    for c in row.iter(N + 'c'):
        isel, v = c.find(N + 'is'), c.find(N + 'v')
        vals.append(''.join(t.text or '' for t in isel.iter(N + 't')) if isel is not None
                    else (v.text if v is not None else ''))
    print(vals)
PY
```

Text in these two files is stored inline; if a column comes back empty, the same loop needs
`xl/sharedStrings.xml` for shared strings.

**Do not round-trip the workbook through a library** — `openpyxl` and friends rewrite the styles
and can drop the person's formatting. If they ask you to write a cell (they did, for post 1), copy
the file into `backup/` first, then edit only the target cells inside `xl/worksheets/sheetN.xml`
as text, keeping the existing `s=` style number and `t="inlineStr"` shape, and keep `dimension`,
`autoFilter` and `cols` consistent with the new last row. Entering a film they have finished is
fine; inventing a post, a score or a view count is not.

---
