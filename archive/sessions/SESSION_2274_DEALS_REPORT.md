# Session 2274 (chain 174, deals and datacenters) report: facilities' MW basis

6 November 2026, about 13:41 to 13:43 UTC, portable-laptop (code role), unattended. Worktree `erw-2254` on `wip/2274-deals`, cut from `wip/2273-deals`. Model spend **USD 0**. Nothing deployed; no warehouse data written.

- **The class**: MW basis wrong, 1 of 60 on the second read (F049, "2.5 GW data centre park" stored as `total`).
- **Read against the vocabulary**: `facility_fields.MW_BASES` (session 2236) defines `total` as "the facility's total power, grid or utility capacity, its power demand, a campus of N GW"; a park of 2.5 GW is that form, so the stored basis follows the vocabulary and the second read's grade does not. Kept, no code; the audit file's section says so.

## Decisions made without you

1. **The vocabulary over the later grade**, since the vocabulary is the written rule the model is asked to follow.

## For Samuel's ruling

- Whether a park's or campus's stated GW is its total (the vocabulary now) or unstated.
