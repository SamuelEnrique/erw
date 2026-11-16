# Session 7509 report: the interconnection queue explorer at the done line (chain 304, part A)

16 November 2026, samueloldlaptop (code role), unattended. Branch `wip/7509-interconnection`, worktree
`C:\Users\lossa\Documents\erw-7509`. Tool: `/explore/interconnection`. Not pushed, nothing landed, no table written,
no request made to any host, model spend USD 0.

## At the top

- **The page opens on a figure that is true of its source and far from the queue.** As it opens: "Entered, positions,
  CAISO, entered 2023" 4, "Reached operation" 0, "Withdrawn, share" 1.00. Berkeley Lab's Queued Up 2026 counts 594
  requests that entered CAISO's queue in 2023; CAISO's public report does not list 590 of them. The page now says so
  in one line above the figures. Which queue and year it opens on is for Samuel's ruling (default: unchanged).
- **ERCOT's "Entered" is not the requests made.** ERCOT's report lists active and completed positions only: 198
  positions for 2000 to 2020 against 1,553 in Queued Up. The page now says so in ERCOT's line.
- **The table is four weeks old.** `iso_queue_statistics` is the build of 21 October (the pulls of 19 October); it is
  not in the daily run, which pulls the queues weekly. The page says "Stale since 21 October 2026". A data request.
- **Part B of the replication is whole for two queues only.** This machine's queue tables are the pull of 30
  September; the table read the pull of 19 October. NYISO and MISO (the same pull) are exact; the other four differ
  and the cause cannot be shown here. A data request.

### Faults in shared explore files

- `site/lib/explore/source.ts`, line 37 (`iso_queue_statistics`, `report`): every figure's hover says the queue is
  "as the ERW last pulled it"; the table is as old as its last build. Smallest change: "as the ERW held it when the
  table was built" (faults row 11).
- `site/components/explore/Explore.tsx`, line 75: "the newest period it holds is 5 November 2026 23:21 UTC" for a
  snapshot table. Smallest change: leave the clause out when `r.interval` is `snapshot` (row 12).
- `site/components/explore/Explore.tsx`, line 80: the freshness `detail` is grey text (`text-xs text-muted`); the page
  standard asks for ink or a tip. Smallest change: drop `text-muted`, or draw it as a `Tip` (row 13).

## The five parts

- **The method note:** `docs/methods/interconnection_explorer.md`, new, for the tool as a reader meets it: the
  filters, every figure's row and place, how a figure is written, the three ways a cell reads "not held", what each
  queue does not hold, the assumptions with defaults and sources, the decisions' keys, licenses, how old the figures
  are, the replication, the cross-check, what the tool does not hold. It points to the tables' notes.
  `docs/methods/energy_projects.md`, "Queue statistics", gained two dated paragraphs (its cross-check was the first
  build's; when an MW row is written). Gaps of the old note found on the way: faults rows 16 and 17.
- **The replication:** `replication/interconnection/` (`fetch_rows.py`, `replicate.py`, `replicate.do`,
  `cross_check.py`, `page_figures.json`, `page_figures.csv`, `rows/.gitignore`). The page is drawn by its own code
  (`site/scripts/interconnection-figures.mjs`: the async page prerendered, its reads answered from the table file).
  As printed:
  `part A: 730 of 730 figures inside the tolerance; 284 of 284 views drawn as the note says; 139 queue-years whose four statuses make up the positions entered; held and not read: ISO-NE, MISO, NYISO`
  - The views: each queue in each count as it opens; for CAISO, ERCOT and SPP every first entry year with the default
    last one and every last entry year with the default first one; the years the other way round; one year alone; an
    address the table does not hold; the three held queues (no figure drawn). Every pair of years is `--grid` on the
    node script (not run: several minutes).
  - Part B (`--queues`), the table's rows from the six queue tables: NYISO 352 of 352, MISO 113 of 113 (held: no
    value printed); CAISO 304 of 309, ISO-NE 245 of 261, SPP 311 of 342, ERCOT 63 of 134 (another pull, above).
  - No row of any table is committed: the statistics table is held by grid. The figure files hold CAISO, ERCOT and
    SPP only (their queue tables are `public` in `site/data/license_status.json`).
  - The do-file was not run: Stata is not on this machine. `replicate.py --headline` printed its expected values.
- **The cross-check:** against Queued Up 2026 as the warehouse holds it (public, CC BY 4.0, with its source line). No
  host was asked. Table under "For the pack". Not read, said in the note: the operators' own published totals, FERC's
  and the EIA's figures (the page adds nothing up, so a national total stands against no figure of it); nothing
  published stands against the median wait by entry year or against "status not stated".
- **The decisions block:** `site/app/explore/interconnection/Decisions.tsx`, the page's own file: twelve choices,
  each with its default and source on hover, at the foot of the page and under a held queue's line. Not editable in
  place: the page computes nothing.
- **The faults:** `docs/reviews/interconnection-faults-2026-11-16.md`, 18 rows: 7 site (fixed, with tests), 3 data
  machine, 3 shared explore file, 3 rulings, 2 note (completed).

## Tests

Each file in its own process: `.venv\Scripts\python.exe -m unittest tests.<file>`, `ERW_SPEND_CAP_USD=0`.

- `tests/test_session7509_interconnection.py`: 12, pass (the replication on the drawn page runs because `rows/` is
  filled on this machine; on a machine without it that one test skips).
- `tests/test_session405.py`: 12, pass (one assertion brought to `figureText`, with its reason).
- `tests/test_session2202.py`: 6, pass. `tests/test_session472.py`: 4, pass. `tests/test_session2200.py`: 8, pass.
- Not run (they need the built site): `site/scripts/check-values.mjs`, `check-routes.mjs`, `check-methods.mjs`. The
  new text of a whole value ("550.00") still begins with what `check-values.mjs` expects ("550"): held by a test.

## What to review

`https://erw-flame.vercel.app/explore/interconnection` (in review; after the stack lands):

1. Open it. A line above the three numbers says CAISO's report lists only a few of the 2023 requests. The third
   number reads 1.00, not 1.
2. Count: MW. The column reads "550.00" for 1999; cells of a status with no position read "not held".
3. Queue: ERCOT. The line says "Entered" is the positions still in the report. The third number is "Still waiting".
4. Address `?queue=caiso&from=2020&to=2010`: the selects read 2010 and 2020.
5. Queue: NYISO. "license needed", no figure, and the decisions block under it.
6. Foot of the page: "Decisions on this page", twelve lines; hover the "i" of any for its default and source.
7. The source line: "as the ERW held them when this table was built: CAISO's as pulled on 19 October 2026".

## For the pack

- **What Samuel signs:** every number on the page is one row of `iso_queue_statistics` (730 of 730); the table's
  rule holds on its own rows (139 of 139); what CAISO's and ERCOT's "Entered" leave out is said on the page.
- **The five choices that matter most:**
  1. One pull of each operator's report, not a history (default: the pull the table was built from; source: the
     header's "Inputs read").
  2. The four statuses from the operators' own words (default: suspended counts as waiting; source:
     `energy_projects.md`, "What counts").
  3. Entry year is the year of the queue date (default: no date, no year; source: the same).
  4. Withdrawn share by count, a fraction of 1 (default: by count in the MW view too).
  5. The wait is the median of queue date to in-service date over operating positions with both dates (default:
     SPP's date may be the one requested).
- **The cross-check:**

| Ours | Theirs | Publisher, document, date | Difference | Why |
|---|---|---|---|---|
| CAISO, entered 2000 to 2020: 1,910 | 1,910 | Berkeley Lab and GridTracker, Queued Up 2026 data file, May 2026 | 0 | the same requests |
| CAISO, withdrawn share of them: 0.787 | 0.781 | the same | +0.006 | pulls ten months apart |
| CAISO, entered 2023: 4 | 594 | the same | -590 | CAISO's public report does not list them |
| ERCOT, entered 2000 to 2020: 198 | 1,553 | the same | -1,355 | ERCOT's report lists no withdrawn position |
| ERCOT, MW entered 2025: 104,175 | 106,525 | the same | -2,350 | the same, less for a recent year |
| SPP, entered 2000 to 2020: 1,722 | 1,682 | the same | +40 | not established here |
| SPP, withdrawn share of them: 0.722 | 0.721 | the same | +0.001 | |

- **Stata** (`replication/interconnection/replicate.do`, from its folder, after `fetch_rows.py`): three `list`
  commands should print CAISO 2023: 4, 0, 1.00; ERCOT 2025: 104,174.94 and 83,226.25; SPP 2025: 421 and 0.48; then
  three `assert` blocks pass and it displays "the five figures are listed above; the three rules hold".
- **Rulings, in plain words:**
  1. Which queue and year the page opens on. Default: CAISO and its newest complete year (2023), with the new line.
  2. An MW cell of a status with no position reads "not held" where positions reads 0. Default: left; the data
     machine is asked to write 0.
  3. Five explanations under charts and tables are grey text, not hover tips. Default: left, so the page keeps one
     manner; `ToolSection` (shared by every tool) has no tip.
  4. The withdrawn share is a fraction (0.80), not a percent. Default: the fraction.

## Data request rows

| Requested (UTC) | Session | Table or file | What, exactly | Source | State |
|---|---|---|---|---|---|
| 2026-11-16 12:10 | 7509 | `iso_queue_statistics` | Rebuild from the six queue tables as they stand (`warehouse/derived/queue_statistics.py`), load it to the live set, and run the builder after each weekly pull of the queues: the table is the build of 21 October (pulls of 19 October) while the queues were pulled on 5 November | `docs/reviews/interconnection-faults-2026-11-16.md`, row 9 | requested |
| 2026-11-16 12:10 | 7509 | `iso_queue_statistics` | Where `positions_<status>` is 0, write `mw_<status>` 0 (today no MW row is written, and 93 cells of CAISO, ERCOT and SPP read "not held" where the count is 0) | the same file, row 8 | requested |
| 2026-11-16 12:10 | 7509 | `replication/interconnection/` | After the rebuild: `python replication/interconnection/fetch_rows.py --from warehouse/output`, then `python replication/interconnection/replicate.py --queues`; every queue must print all rows equal (here CAISO 304 of 309, ISO-NE 245 of 261, SPP 311 of 342, ERCOT 63 of 134, on the pull of 30 September) | the same file, row 10 | requested |

## Browser read rows

| Asked (UTC) | Session | Branch | Address | What to look at | What should be seen | State |
|---|---|---|---|---|---|---|
| 2026-11-16 12:10 | 7509 | `wip/7509-interconnection` | `https://erw-flame.vercel.app/explore/interconnection` | The foot of the page: open "Decisions on this page", hover and tab to the "i" of three lines, at 1280 and 390 px | Twelve lines; each tip shows "Default:" and "Source:", stays inside the screen at 390 px, no sideways scroll | wanted |
| 2026-11-16 12:10 | 7509 | `wip/7509-interconnection` | `https://erw-flame.vercel.app/explore/interconnection?queue=caiso&measure=mw` | The table "Every entry year" and the stacked chart's hover card | MW with two decimals in every cell that holds one ("550.00"), right-aligned; "not held" where a status has no position; the card's figures as the table's | wanted |
| 2026-11-16 12:10 | 7509 | `wip/7509-interconnection` | `https://erw-flame.vercel.app/explore/interconnection?queue=caiso&from=2020&to=2010` | The two year selects and the titles | First entry year 2010, Last entry year 2020; titles "2010 to 2020" | wanted |
| 2026-11-16 12:10 | 7509 | `wip/7509-interconnection` | `https://erw-flame.vercel.app/explore/interconnection?queue=ercot` | The line above the three numbers, at 390 px | ERCOT's line with "not every request made that year", wrapped, no sideways scroll; the freshness line of `ercot_interconnection_queue` not marked stale within eight days of a pull | wanted |

## Landing request

- Head commit: the last commit of `wip/7509-interconnection` (this report's commit; the orchestrator reads it with
  `git -C C:\Users\lossa\Documents\erw-7509 log -1`).
- Tests: `test_session7509_interconnection` 12, `test_session405` 12, `test_session2202` 6, `test_session472` 4,
  `test_session2200` 8, all pass.
- Changes: `site/app/explore/interconnection/page.tsx` and `Decisions.tsx`, `site/lib/explore/interconnection.ts`,
  `site/scripts/interconnection-figures.mjs`, the notes, the replication, the faults file, two test files.
- Does not change: the shared explore files, `site/lib/release.ts`, any table, any other page.
- A snapshot would differ on: no live page (the page is in review; a visitor sees the in-review page).
- `check-values` on the built site reads the page's figures as before; their text gains two decimals where whole.

## Needs the key

None.

## Decisions made without you

- The page's own `Freshness` call passes eight days as stale, not the frame's three (the queues are weekly).
- The CAISO and ERCOT lines are words only, with no typed count; the counts are in the note and the faults file.
- The replication draws each filter over all its choices from the defaults (284 views), not every pair of years.
- No row of `iso_queue_statistics` is committed, though its CAISO, ERCOT and SPP rows are shown: the table is held.
- The cross-check uses Queued Up as the warehouse holds it; no host was read this session.
- `tests/test_session405.py`: one assertion updated to the new text rule, with its reason.

## For Samuel's ruling

The four rulings under "For the pack", each with its default taken.

## Not finished, and why

- The operators' own published totals, FERC's and the EIA's figures were not read (time; and no figure of the page
  is a total). Said plainly in the note.
- Part B for four queues (the pull the table read is not on this machine).
- Seen on other tools, not touched: the map's Queues tab draws the same CAISO 2023 and ERCOT "entered" figures
  without the two new lines. `/queues` shows Queued Up's 594 CAISO requests of 2023 where this page shows 4.
