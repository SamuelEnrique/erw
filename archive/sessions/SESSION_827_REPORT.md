# Session 827 report: the datacenter tracker's power side, the same way

23 October 2026, 08:52 to about 09:20 UTC, unattended, on portable-laptop (the code machine), in the worktree `C:\Users\samen\Documents\erw-827` on `wip/827-deals` (cut from `wip/826-deals`). Chain `queue/done/080-night-23-october-portable-landing-deals-.md`, session 827. Model Fable 5.1. Model spend USD 0. No warehouse data written; no request.

## Read these first

- **No row of `datacenter_projects` can be shown: 0 shown, 150 held, 0 unsettled** (`docs/reviews/datacenters-public-rows-2026-10-23.md`). Every one of its 168 evidence rows is a news outlet's that asks for permission (Data Center Dynamics 81, Reuters 41, Bloomberg 17, WSJ 10, the rest fewer). The sites a public source names are the interconnection-queue positions, which the power side has drawn from the queue tables themselves since session 467; nothing of them changed.
- **The page counts the three sorts in place**: `site/app/datacenters/PublicLine.tsx` under the held table's words, each count a key (`dcpub|counts|shown`, `|held`, `|unsettled`; `check-values` reads the live set's row count of `datacenter_projects` against `site/data/datacenters_public.json`).
- **One sort, two trackers**: `public_rows.py` takes the table's id columns (`entity_id`, `facility_id`) and writes the datacenter file with `--datacenters`; the test proves the sort on an entities table.
- **Session 825's name rule was sharpened here** after its hand check (its report): one direction only (the story's name must be whole words of the filed name), ENERGY kept as a word. The join runs again under it for session 825's review.

## What to review

- `/datacenters` (internal view): the line under the hold's words, its three counts.

## Checks

| Check | Exit | Result |
|---|---|---|
| `public_rows.py --datacenters` | 0 | 0 shown, 150 held, 0 unsettled; 168 evidence rows, every publisher asks |
| `tests.test_session827` (4) with 822 to 826's (30) | 0 | OK |
| `npx tsc --noEmit` | | 0 errors in the deals and datacenters files |

## The landing

`wip/827-deals` holds sessions 822 to 827 over origin/main; its gate runs at this report's time (session 828's report has the outcome). The periodicals' gate (session 820's "To finish") ran through the suite and the build at 08:15 to 09:06 UTC and failed `check_values` on two failures outside the ten license-hold floors: `/roundup` "fetch failed" (a read of the page), and `/digest/2026-10-21`'s WTI figure for 14 October (the issue prints 101.91; the live set and the warehouse's archive hold 96.34 now). `scripts/check_digest.py --supabase --then-csv`: 138 ok, 2 FAILED (the same figure in the issues of 20 and 21 October), so the figure changed in the warehouse after both issues were written. That is a data fact for the owner, not the branch's; it blocks every gate that reads those two pages until it is ruled on.

## Decisions made without you

1. The datacenter sort reuses the deals' reader with id columns rather than a second reader.
2. With no shown row, the page's change is the counting line; the power side's public rows are session 467's and were not redrawn.
3. `datacenter_facilities` is not re-sorted row by row here (its count by kind restates session 441's).

## For Samuel's ruling

- Whether an operator's own site list is a public source (275 rows of `datacenter_facilities`).
- The WTI figure of 14 October in the issues of 20 and 21 October (101.91 printed; 96.34 in the warehouse now): a revision by EIA or a correction in the warehouse, and whether a past issue's figure that the warehouse revised fails the gate (it does today, for every landing).

## Files

- New: `site/app/datacenters/PublicLine.tsx`, `site/data/datacenters_public.json`, `tests/test_session827.py`, `docs/reviews/datacenters-public-rows-2026-10-23.md`, this report.
- Changed: `site/app/datacenters/page.tsx`, `site/scripts/check-values.mjs`, `warehouse/deals/public_rows.py`, `warehouse/deals/eqr_join.py`, `tests/test_session825.py`, `docs/methods/datacenter_facilities.md`.
