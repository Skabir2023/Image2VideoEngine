# Publishing a finished film

> Part of the engine manual. Index, read order and precedence: [AGENTS.md](../../AGENTS.md).

The person posts on **BrightBean**, which fronts Facebook (and other channels) through one API.
Each **page** books its own films; the tools live in the engine root. Uploading and scheduling are
public, external actions: **ask for a yes on that film before running `schedule` for real.**

## What a page holds

The queue and the ledger belong to the channel, not to one film, so they sit at the page level and
you name the **film** on the command line:

```
video-projects/<page>/                ← the channel: everything here is shared by its films
  data.csv      the queue: one row per film waiting to go out
  uploaded.csv  the ledger: every booked film and its slot
  schedule.json the page's posting hours — the four slots below
  *.xlsx        the page's workbooks
  <film>/       meta.json, renders/, audio/, compositions/, stills/, plan/, qa/
```

There are no `videos/` or `uploaded/` folders and no copies of renders. A row in `data.csv` **is**
the queue entry, and it points at the finished film where it lies:

| Column | Holds |
| --- | --- |
| `id` | short id binding the row to its post |
| `video` | absolute path of the finished film in its own `renders/` — nothing is copied |
| `video_sha` | fingerprint of that file; what stops a double upload |
| `title`, `description`, `hashtags` | the three caption parts, editable |
| `caption` | the three joined, exactly as Facebook receives them |
| `car`, `angle` | what `schedule` uses to find the workbook rows |
| `status` | `ready` → `uploaded:<post id>` → `scheduled` → `published` |
| `scheduled_at`, `published_at`, `post_id`, `post_url` | written by `schedule` / `sync` |

So `tools/publish.py queue video-projects/<page>/<film>` reads that film's `meta.json` and
`renders/`, and appends one row to the page. Two films from one page share one queue and one
ledger, which is what keeps the page's four daily slots honest across both.

`meta.json` names the channel:

```json
"social": { "platform": "facebook", "account": "Vintage Motor House" }
```

`account` is the BrightBean account handle exactly as `/accounts` reports it — not the Facebook
page URL. Only `facebook | Vintage Motor House` is set up today; other channels use the same
endpoints but need their own project whose `account` names them.

## The credential

`BRIGHTBEAN_API_KEY` is read from the environment, then `image2videoEngine/.env`, then
`~/.env_brightbean`. It never goes in a project folder and is never printed — the tools report its
length at most. `BRIGHTBEAN_BASE` overrides the API host.

## The commands

Run them from the engine root. `status` is read-only; the rest write where the table says. Every
`schedule` row below is run as `python3 tools/scheduler.py <page-or-film> …`; the rest are
`python3 tools/publish.py <command> …`.

| Command | What it does | Writes |
| --- | --- | --- |
| `pick` | lists the next cars to film and the ones free again after 90 days | nothing |
| `queue` | adds a `ready` row pointing at the render, with title, description, hashtags and caption | `data.csv` |
| `schedule --dry-run` | resolves the channel, computes the slots, prints them | nothing |
| `schedule` | uploads each queued film from where it lies, creates the post, books the slot, moves the row, marks both workbooks | `uploaded.csv`, `data.csv`, both `.xlsx` |
| `sync` | reads each post back, records `published` and the post URL, marks the workbooks on publish | `uploaded.csv`, `data.csv`, both `.xlsx` |

A row leaves `data.csv` only after its slot is booked — and only the row moves. The film stays
exactly where it was rendered, `renders/<title>.mp4`, so the link in the queue never goes stale
and there is nothing to clean up afterwards.

## Never upload the same film twice

Three gates, in this order, because a repeated upload is the one mistake that cannot be undone:

1. **`queue` refuses the file.** Every row records `video_sha`. Queueing bytes that are already in
   `data.csv` or `uploaded.csv` — or pointing at a file some row already points at — stops with
   the row and status that already hold it.
2. **`schedule` refuses the fingerprint.** Before a row is uploaded, its `video_sha` is compared
   with every booked row; a match is skipped with a `SKIP` line naming the earlier film, and the
   row stays in `data.csv` with the reason in `error` so a human can look (the usual cause is the
   same cut queued twice under different titles).
3. **BrightBean refuses the caption.** If a post with this exact caption already exists on the
   channel, a retried run adopts that post and books its slot instead of creating a second one, so
   an interrupted `schedule` finishes rather than duplicating.

A genuinely new cut has a new fingerprint and is allowed; re-posting the same car later means a
new film, not the old file. Never re-run `queue` "to be sure", and never edit `video_sha` by hand.

## The caption

`queue` stores the title, description and hashtags as separate columns *and* as one `caption`, so
the text can be corrected before scheduling without re-parsing it. Facebook receives:

```
<title>

<description>

<hashtags>
```

which is the three-line format `MASTER PROMPT.md` requires. The same caption twice in one project
is refused as a mistake. `--caption-file` takes the same three blocks from a file, `--video`
queues something other than the project's finished render, and `--car` / `--angle` are what let
`schedule` find the workbook rows.

## Slots

**The page posts four times a day, and the hours are the page's own wall clock.** They live in
`video-projects/<page>/schedule.json`:

```json
{"times": ["07:00", "13:00", "19:00", "01:00"], "tz": "Asia/Dhaka", "lead_min": 15}
```

`01:00` belongs to the night that started at `19:00`, so the day runs `01:00`, `07:00`, `13:00`,
`19:00` and the four slots are chronological. Vague ask — "schedule the next one" — means:
`python3 tools/scheduler.py video-projects/<page>`, which books the **next free slot on that
grid** and skips any slot already in `uploaded.csv`. Nothing is booked inside `lead_min` (15
minutes) of now, because the upload itself takes a moment.

Override for one run when a time is asked for: `--daily "09:30,21:30"` (same local clock),
`--tz Asia/Tokyo` for another zone, `--lead 5`, `--start-at <ISO>` for an exact instant,
`--interval N` for a fixed gap that ignores the grid, `--limit N` for only the first N films. A
page with no `schedule.json` keeps the old random cadence (60–120 minutes out, then 4–5 hours,
never under 4) so the same minute never repeats every day.

The last slot comes from that page's `uploaded.csv`; the API is asked only when the ledger is
empty, so one page's schedule never depends on another's.

## The workbooks

`schedule` and `sync` edit the project's two `.xlsx` files through `tools/excel.py` — no
`openpyxl`, and the existing styles and inline-string cells survive.

- **Tracker** — for the row whose `Car (Year Make Model)` equals the row's `car`: `Date` if it is
  empty, `Script done = Yes`, `Images done = Yes`, `Posted = Scheduled` when booked and
  `Posted = Yes` once `sync` sees it published. No match prints a note; it never invents a row.
- **Car List 300+** — that car's row: `Used? = Yes`, `Angle Used`, `Date Used`. The model matches
  exactly first (`Mustang Boss 429` must not land on the `Boss 302` a few rows above), and among
  repeats of one car the newest unused row wins, which is the row a repeat after 90 days should
  take.

`--no-excel` leaves both alone. The workbooks are the page's calendar: a missing row is added by
hand, never by the tool.

Both tools edit the `.xlsx` files **found in the film folder you name, or in the page folder above
it** — the page keeps one set, not one per film, and that set is the one they find. On a silent
run of `schedule` with no marks, the workbooks are missing from both folders; put them back at the
page level and re-run `sync`.

## Re-running, failures, API vs MCP

- `schedule` resumes. A row already `scheduled` / `published` is skipped; a film already uploaded
  resumes at its post; a post with the same caption on the same account is adopted instead of
  duplicated. Uploads are streamed in parts and retried once through an idempotency key.
- A failure marks that row `failed`, stores the reason in `error`, prints it, and the batch
  continues. `failed` rows are still pending, so the next `schedule` retries them — fix the cause
  first (the file, the account, the caption).
- Use the **REST API** for scheduled work: it runs unattended and reports each channel's `url`,
  `publishedAt` and `error`. The **MCP** server fronts the same backend and suits a one-off check
  in chat; never book the same film through both, since neither sees the other's slots.
- Uploads are video only (`mediaType: "video"`, `.mp4`) — no thumbnail, no caption on the asset;
  the caption belongs to the post.

---
