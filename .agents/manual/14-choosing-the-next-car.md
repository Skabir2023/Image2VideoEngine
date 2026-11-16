# Choosing the next car

> Part of the engine manual. Index, read order and precedence: [AGENTS.md](../../AGENTS.md).

The sequence is [the working procedure](03-working-procedure.md); this section is the workbook law
it relies on.

The page's Car List workbook (`<page>/Vintage-Motor-House-Car-List-300.xlsx`, 312 cars) is the
source of truth for what has been filmed. Work in batches of **10**:

```bash
python3 tools/publish.py pick video-projects/<page> --count 10    # read-only
```

It prints the first 10 cars with `Used? = No`, plus any car that is free again after 90 days. Then
the rule, in the workbook itself:

1. Pick 10 cars with `Used? = No` for the batch.
2. The moment a car is filmed, set `Used? = Yes` and fill `Angle Used` + `Date Used` on its row.
3. A car may be filmed again **90 days after** `Date Used`, with a **different angle**, as a **new
   row at the bottom** of the list — never by overwriting the old row.
4. The list holds 312 cars; `pick` counts them so you always know how much runway is left.

`schedule` marks both workbooks when a film is booked ([The
workbooks](15-publishing.md#the-workbooks)), so the only case you mark by hand is a film that is
built but deliberately not scheduled.

Then per car the content contract applies — facts first, and nothing under 80 is built ([Content
rules](11-content-rules.md)). The plan files are listed in [Make the folder and the
plan](03-working-procedure.md#2-make-the-folder-and-the-plan); the caption at the end of
`SCRIPT.md` is what becomes the `queue` row.

---
