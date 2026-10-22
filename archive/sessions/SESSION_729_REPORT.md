# Session 729 report: the tracker's facilities, placed by their utility

22 October 2026, from 15:31 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-729` on `wip/729-allgrids` (cut from `wip/728-allgrids`). Chain `queue/done/062-day-23-october-code-allgrids-2.md`, session 729. Model spend USD 0. No warehouse data written; no request.

## Read these first

- **None there: no code was written.** The chain file asked to place, by an exact match of the utility it names, the facilities that 719's county and state rule leaves out. On this machine's copy of `datacenter_facilities`, read locally for counts only:
  - **3 of 422 facilities name a utility**, and each is a holding company's name, not an operating utility's as EIA-861 lists it. An exact match places none, and the chain forbids a fuzzy one.
  - **The 281 left out are of two kinds:**
    - **153 have no US state**: operators' sites abroad, from the operators' own lists. No US grid serves them.
    - **128 are in a state no one grid holds at 85 percent**: a state split between grids (California at 79 percent CAISO, Illinois between PJM and MISO), or one outside the tab's grids (the Southeast, the West).
  - **The 3 rows from an ISO's queue** name their ISO, and are already placed by their state.
- **Nothing of the held table is in this report** beyond counts (the table is held whole since 21 October 2026).
- Open item 25 is closed with this reason (`docs/reviews/siting-open-2026-10-23.md`).

## What to review

1. This report, and the open items' line 25.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| counts on `warehouse/output/datacenter_facilities.csv` (local, not committed) | 0 | 422 rows: 141 placed (14 by county, 127 by state), 153 with no US state, 128 in a split or outside state, 3 naming a utility |

## The landing

With 722 to 728 after 16:15 UTC (728's report).

## Decisions made without you

1. **No utility rule was written for three holding-company names.** A rule that places nothing today would add a map of every EIA-861 utility (about 100 KB) to the tab's files for no row.

## For Samuel's ruling

- Whether the tracker's extraction should record a facility's operating utility (EIA-861's name), so the tab could place it by its utility once the table is public.

## Files

- Changed: `docs/reviews/siting-open-2026-10-23.md`.
- New: this report.
