# Session 7602 report: the old laptop's rows 32 to 278 read in a browser

Energy Research Warehouse (ERW). Chain 305 (`queue/done/305-night-16-november-portable-done-line-and-browser-reads.md`), resumed from `queue/done/350-resume-chain-305.md`, portable-laptop (code role), 17 November 2026, about 05:15 to 07:00 UTC. Model spend: USD 0 (`ERW_SPEND_CAP_USD=0`; no script that calls a model was run).

## First

- **Part B has nothing left for this machine.** Samuel moved tools 11 to 16 of `docs/state/done_line_claims.md` to samueloldlaptop on 16 November at about 22:00 UTC; the old laptop took all six to the done line and read each as its reader (`docs/state/note_2026-11-17_oldlaptop_c304.md`, "The second run"). Skipped and said so in the progress file. Part C's seven of this machine are read too (by the old laptop). Part C's four others (the datacenter tracker, the deal tracker, Automated Analysis, Grid) have no read on any branch: claimed as rows 25 to 28 of the claims file, and next.
- **Two slips of the chain's rules, both checked after:** the first two pushes to main went out with no before snapshot (the after snapshot against session 7600's: 0 differences), and the second build started at 1,175 MB free, under 2 GB (it finished). Both are in the progress file's "Not as the chain file expected".

## Part A: rows 32 to 278 of `docs/state/browser_reads_wanted.md`

- **The build:** the old laptop's 27 branches the rows name, merged here with `wip/7600-large-load-read`, no conflict; built in the foreground and served. Read with the machine's own Chrome, headless, through a new reader (`site/scripts/read-rows-c305.mjs`, its row lists in `docs/reviews/browser-reads-2026-11-16/s7602/`), at 1280 and 390 px, in the internal view.
- **130 rows: 119 seen, 4 seen in part, 7 with a fault.** Each row's state and what was seen is written in the table on main; none is left `wanted`.
- **Six faults fixed with tests,** on `wip/7602-landed-reads` (from main; landing row 38), and read again on a second build:
  - rows 52 and 62: a hover box taller than its room was capped and scrolled inside itself; the shared placer now widens it up to 576 px (whole at 1280 px; a phone still scrolls it);
  - row 63: a one-point chart drew a withdrawn share on an axis to 1.8; the shared chart now pads a value alone by a tenth of itself (0.55 to 0.75);
  - rows 80 and 82: the event pages' fold of each event day's estimate pushed the page to 469 px at 390, on production too; it scrolls in its own frame;
  - row 179: `/supply`'s grid links line had no place to break and ran to 899 px at 390, on production too; it breaks between grids.
- **One data fault:** row 55, the awards page and the battery page give the same comparison as USD 0.37 against 2.10 (5.60 times) and USD 0.40 against 2.24 (5.64 times): the battery page reads a snapshot written on 10 October and never again. Request row 261.
- Index and 175 pictures: `docs/reviews/browser-reads-2026-11-16/README.md`, section "Rows 32 to 278".

## Tests

- Four new test files and the 19 older ones that name a changed file, on the landing branch: 194 passed, 1 skipped. Three pinned counts moved with a dated note (`test_session241a.py`, `test_session7531_events.py`, `test_session7505_battery_awards.py`).
- `tests/test_session161.py` fails on origin/main as well (its Node test meets a fixture request that is not recorded): not this session's.

## What to review (the pages are in review; after the landing)

1. `https://erw-flame.vercel.app/events/covid-2020` on a phone (390 px): open "Each event day's estimate, the Lower 48, demand served (MWh)": the table scrolls inside its frame and the page does not move sideways.
2. `https://erw-flame.vercel.app/supply` on a phone: the line "ERCOT mix, neighbours; CAISO mix, neighbours; ..." wraps inside the page.
3. `https://erw-flame.vercel.app/explore/demand-growth?grid=caiso` at full width: open "Decisions on this page" and hover the mark of "Demand at the grid is not sales to customers": the box is wide and whole, ending "it does not close 2026's gap to sales."

## Needs the key

- Nothing in this session.

## Decisions made without you

- The six fixes and the write-up are on one branch from main, not on the old laptop's branches: every page they touch has landed.
- A row's figures that moved with the live set since it was written (rows 69, 156, 157, 268) are marked seen with the newer figures named.
- Rows 117, 118 and 267 were read by playing the game to its end with no move; row 267's "plus the fleet bonus" appears only when a play earns a bonus, so it was not seen.
- All 175 pictures are committed (20 MB), as rows 1 to 31's were.

## For Samuel's ruling

- **A long hover box on a phone** still scrolls inside itself (there is no width to give). Default: left so.
- **Row 50:** the impact page's chart cards now say "2027 build: Property 0 USD (2025), Income 0 USD (2025)", not the row's "property not held, sales none". Default: unchanged (the read's row 6 stays a ruling).

## Commits

- `wip/7602-landed-reads`: `5c2e5b889`, `e577460b6`, `3b636ad76`, `af1e118af`, the merges of `wip/7600-large-load-read` (`5f4741557`, `50664da62`), `wip/7602-interconnection-read` (`7210933ec`, `6697df2bb`) and `wip/7602-awards-read` (`e3e07e793`), and `eef5b5861`.
- main: `445300cc4` (the resume file 351), `f6f9e2d23` (progress and claims), `fe6b6a861` (the rows marked, request 261, landing row 38), and this report.
- Snapshots: `c305-7602-a` against `c305-after-7600`, 0 differences; `c305-7602-b` and `c305-7602-c` around `fe6b6a861`, 0 differences.
