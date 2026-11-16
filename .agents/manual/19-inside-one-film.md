# Inside one film

> Part of the engine manual. Index, read order and precedence: [AGENTS.md](../../AGENTS.md).

[The working procedure](03-working-procedure.md) steps 2–8 are the whole of it; nothing here
overrides them. Two things only matter once you are inside a single film.

**Naming is the last step before it is shown** — the 5–11 word title in `meta.json` `output` and
on the render, never a working name: [Delivery name](06-pipeline.md#delivery-name).

Projects are independent: two can be in progress at once without touching each other, and
re-rendering the old film never disturbs the new one. Delete `renders/cut/` after a delivery — it
is rebuilt on the next render. Projects nobody has asked about stay archived; unsent drafts are
deleted, not left half-built.
