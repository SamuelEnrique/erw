# Session 7518 report: the interconnection queue explorer read as its reader (chain 304, part B)

16 November 2026, samueloldlaptop (code role), unattended. Branch `wip/7509-interconnection`, worktree
`C:\Users\lossa\Documents\erw-7509`, on top of session 7509's done line. Tool: `/explore/interconnection`. Not pushed,
nothing landed, no table written, no host asked for anything, model spend USD 0. The read:
`docs/reviews/interconnection-read-2026-11-16.md` (17 rows).

## At the top

- **ERCOT's "Reached operation" was not plants in operation.** ERCOT's report has no status word. The library the
  queue connector reads it through (gridstatus 0.36.0, `ercot.py`) writes "Completed" when the report's "IA Signed" day
  is filled. The page read "Reached operation, positions, ERCOT, entered 2025: 55" (20,948.69 MW); on this machine's
  copy of ERCOT's queue (the pull of 30 September) all 44 such positions of entry year 2025 have a projected operation
  day still to come and none a day of approval to synchronize. For entry year 2022 the table holds 115, Berkeley Lab
  counts 17 in operation. The page now heads ERCOT's two groups "Agreement signed" and "No agreement yet" and says
  why; the table is unchanged and its fix is a data request (the cause is the connector's, so the map's Queues tab
  and every reader of ERCOT's `status` carry it).
- **No other page was edited.** `/queues` (the lab desktop's), the map's Queues tab (the portable laptop's) and the
  three shared explore files are as they were. Two lines for those machines are below.
- **One older test's assertion was brought to its intent** (`tests/test_session2202.py`: the page now holds two
  `tip={`, the headline map's and the wait chart's).
- **No difference was unexpected.** The replication's counts did not move: 730 of 730, 284 of 284.

## The reader and the five cases

- **Reader:** a renewable or storage developer deciding which grid operator's queue to file in. Chosen over the AI
  lab's energy lead because every figure is a generator's request; what a large load's reader can and cannot take is
  its own section of the read, and the page now says it in one line.
- 1. SPP, entered 2018: 150 entered, 4 reached operation, 99 withdrawn (0.66), 47 waiting; wait 4.40 years over 2.
- 2. CAISO, entered 2021 (the year of its cluster 14 window): 361 entered, 255 withdrawn (0.71), 104 waiting.
- 3. ERCOT, entered 2020: 82 entered, 46 with a signed agreement (read as "Reached operation" until today), 36 with none.
- 4. A storage developer comparing the three queues' wait for the last entry year with ten finished projects: CAISO
  2018, 6.74 years over 10; ERCOT 2022, 3.75 over 13; SPP 2017, 8.01 over 24. No technology on the page.
- 5. The reader who wants PJM, MISO, NYISO or ISO-NE: no PJM table; three held; now each with a link to `/queues`.

## The rows by kind (17)

- **site, fixed with a test: 8** (rows 1, 3, 4, 5, 7, 8, 10, 11).
- **data machine: 2** (rows 2 and 6).
- **browser: 3** (rows 15, 16, 17).
- **license: 1** (row 9). **ruling: 1** (row 14).
- **another machine's tool, not edited: 2** (row 12 the desktop's `/queues`, row 13 the portable laptop's map tab).
- Cited, not written again: part A's rows 1, 3, 9, 10 and 15.

## What was fixed

- ERCOT's statuses headed by what they are, in the three headline numbers, the stacked chart and the table of years
  (`STATUS_WORDS`, `statusWords` in `site/lib/explore/interconnection.ts`); ERCOT's line and two decisions say why;
  ERCOT's row of the six queues carries a tip.
- "The six queues", in positions: three more columns (the withdrawn share, the median wait, the waits counted of the
  one entry year), each a row of the table with its check key.
- The wait chart: a tip that says whose waits a point counts, that a recent year's median is not final, and that
  `/queues` and the All grids tab count a wait by the year online.
- `?queue=pjm`: the fallback line says the ERW holds no PJM table and links `/queues?grid=pjm&tech=all`. A held
  queue's line links the same grid on `/queues`. No figure of a held queue is drawn.
- Two lines above the decisions block: Queued Up is another source whose count for a queue and a year is not this
  page's; a large load's request is in no figure, with links to `/datacenters` and `/cost-of-power?view=allgrids`.
- **The done line kept:** the method note gained "ERCOT's two statuses", "Whose wait", "Where the other queues and the
  load side are", the new columns and three cross-check lines; `energy_projects.md` a dated bullet; `replicate.py`
  holds the new words, columns, tips and links view by view. As printed at the end:
  `part A: 730 of 730 figures inside the tolerance; 284 of 284 views drawn as the note says; 139 queue-years whose four statuses make up the positions entered; held and not read: ISO-NE, MISO, NYISO`
  Part B as session 7509 left it (NYISO 352 of 352, MISO 113 of 113; the four others on another pull).
- `site/scripts/interconnection-figures.mjs --only=<address>;<address>` draws named addresses alone.

## Tests

Each file in its own process, `ERW_SPEND_CAP_USD=0`, `.venv\Scripts\python.exe -m unittest tests.<file>`:

- `test_session7518_interconnection_read`: 12, pass (new).
- `test_session7509_interconnection`: 12, pass. `test_session405`: 12, pass. `test_session2202`: 6, pass after one
  assertion was updated (above). `test_session472`: 4. `test_session2200`: 8. `test_session2203`: 6.
  `test_session2204`: 5. `test_session417`: 4. `test_session1496`: 6. `test_session167`: 10 (1 skipped).
  `test_session114_part2`: 28. `test_session207`: 15. `test_session215`: 12. `test_session239`: 21.
  `test_session248`: 13. `test_session314`: 14. `test_session330`: 4. `test_session368`: 10 (1 skipped).
  `test_session5251_ask`: 41. `test_session5260_ask`: 13. `test_session538`: 14. `test_session89_miso_pause`: 14. All pass.
- `site/scripts/test-map-sources.mjs`: 37 of 37.
- Not run (they need the built site): `check-values.mjs`, `check-routes.mjs`, `check-download.mjs`, `check-holds.mjs`.
  The three new columns draw keys `check-values` already reads on the queues' own views.

## What to review

`https://erw-flame.vercel.app/explore/interconnection` (in review; after the stack lands):

1. `https://erw-flame.vercel.app/explore/interconnection?queue=ercot`: the three numbers read "Entered", "Agreement
   signed", "No agreement yet"; the line above them says why; the table of years has the same two column heads.
2. The same page, "The six queues, entered 2025": nine columns; an "i" beside ERCOT; SPP's share 0.48, its wait "not held", waits counted 0; CAISO "not held" across (no row for 2025).
3. `https://erw-flame.vercel.app/explore/interconnection?queue=spp&from=2018&to=2018`: 150, 4, 0.66; the "i" beside
   "the median wait from entry to operation"; in the six queues' table CAISO 6.74 over 10, ERCOT 5.06 over 20, SPP 4.40 over 2.
4. `https://erw-flame.vercel.app/explore/interconnection?queue=pjm`: CAISO drawn, and a line that links PJM on `/queues`.
5. `https://erw-flame.vercel.app/explore/interconnection?queue=miso`: "license needed", no figure, a link to MISO on `/queues`.
6. Any view, above "Decisions on this page": the line on Queued Up as another source and the line on the load side.

## Data request rows

| Requested (UTC) | Session | Table or file | What, exactly | Source | State |
|---|---|---|---|---|---|
| 2026-11-16 13:10 | 7518 | `ercot_interconnection_queue` (`warehouse/connectors/iso_queues.py`), then `iso_queue_statistics` and the map's file | ERCOT's `status` "completed" is the library's word for a filled "IA Signed" day (gridstatus 0.36.0, `ercot.py`), not a plant in operation: 580 of 1,778 rows on the pull of 30 September, 44 of entry year 2025 with no day of approval to synchronize. Read ERCOT's operating group from the report's own day of approval to synchronize (already `actual_in_service_date`) or its commissioning day; keep the signed agreement as a status or a date column of its own; check what the library's "Completed" stands on for NYISO and ISO-NE; rebuild `iso_queue_statistics`. Then ERCOT comes out of `STATUS_WORDS` in `site/lib/explore/interconnection.ts` (the test `test_a_completed_position_of_ercot_is_not_a_plant_in_operation` fails and says so) | `docs/reviews/interconnection-read-2026-11-16.md`, rows 1 and 2 | requested |
| 2026-11-16 13:10 | 7518 | `iso_queue_statistics` | The same rows by technology group (storage, solar, solar with storage, wind, gas, other) beside the rows for all, from the queue tables' `fuel_technology`, so the explorer can be asked about storage alone | the same file, row 6 | requested |

## Browser read rows

| Asked (UTC) | Session | Branch | Address | What to look at | What should be seen | State |
|---|---|---|---|---|---|---|
| 2026-11-16 13:10 | 7518 | `wip/7509-interconnection` | `https://erw-flame.vercel.app/explore/interconnection?queue=spp&from=2018&to=2018` | The two line charts of a one-year view: the axis of "the share of each entry year's positions withdrawn" and of the wait | One point each. If the share's axis runs past 1 (the drawn HTML's ticks run 0.6 to 1.8), a fault of the shared `LineChart` | wanted |
| 2026-11-16 13:10 | 7518 | `wip/7509-interconnection` | `https://erw-flame.vercel.app/explore/interconnection?queue=ercot` | The headlines, the stacked chart's legend and hover card, and "The six queues" at 1280 and 390 px; hover and tab to the "i" beside ERCOT | "Agreement signed", "No agreement yet"; the legend "Signed", "No agreement"; nine columns that scroll inside the table's own frame, no sideways scroll of the page; the tip readable, not cut by the frame | wanted |
| 2026-11-16 13:10 | 7518 | `wip/7509-interconnection` | `https://erw-flame.vercel.app/explore/interconnection?queue=spp` | The "i" beside "SPP: the median wait from entry to operation", by hover and by keyboard, at 1280 and 390 px | A tip of five sentences that stays inside the screen | wanted |
| 2026-11-16 13:10 | 7518 | `wip/7509-interconnection` | `https://erw-flame.vercel.app/explore/interconnection?queue=miso` and `?queue=pjm` | The link "the interconnection queue page" in the held line and in the line under the filters | It opens `/queues` with MISO, or PJM, chosen | wanted |

## For the desktop's tool (`/queues`)

- For one entry year the page gives its counts only in the hover of a bar of "What became of each year's requests"
  (read row 12). A table of years, as this page has, would let a reader set the two side by side. Its figures and this
  page's are two sources: SPP 2018, 135 requests there and 150 here; CAISO 2021, 220 withdrawn there and 255 here.

## For the portable laptop's tool (the map's Queues tab)

- It draws the same rows with its own copy of the lines (`site/app/map/QueuesView.tsx`, `NOT_HELD`): ERCOT's column is
  headed "Operating" and nothing says it is signed agreements, nor what CAISO's 2023 and ERCOT's "Entered" leave out
  (part A's rows 1 and 3). Smallest change: import `NOT_HELD` and `statusWords` from
  `site/lib/explore/interconnection.ts` in place of its own copy (read row 13).

## Landing request

- Head commit: the last commit of `wip/7509-interconnection` (`git -C C:\Users\lossa\Documents\erw-7509 log -1`).
- Tests: the files under "Tests", all pass; the new file is `tests/test_session7518_interconnection_read.py` (12).
- Changes: `site/app/explore/interconnection/page.tsx` and `Decisions.tsx`, `site/lib/explore/interconnection.ts`,
  `site/scripts/interconnection-figures.mjs`, `replication/interconnection/replicate.py` and its two figure files,
  the two method notes, the read file, `tests/test_session2202.py` (one assertion), the new test file.
- Does not change: the shared explore files, `/queues`, the map, `site/lib/release.ts`, any table.
- A snapshot would differ on: no live page (every page is in review; a visitor sees the in-review page).

## Needs the key

None.

## Decisions made without you

- The reader is the developer, not the lab's energy lead (the page counts generators' requests).
- ERCOT's two groups are renamed on this page only, in words; no figure moved and no variable was renamed.
- A held queue's line links Queued Up's count of the same grid on `/queues`: another source already on the site, so no
  hold is lifted and no held figure is drawn here.
- The three new columns of the six queues' table are drawn in positions only (the MW view holds no share or wait).
- `tests/test_session2202.py`: one assertion updated, with its reason in a comment.
- `docs/methods/energy_projects.md` gained one dated bullet (its table gave "Completed" as ERCOT's own word).
- No web page was read: every figure of another source is from the files on this machine.
- The one-point chart axis (row 15) is left for a browser: the chart is the site's shared component.

## For Samuel's ruling

1. ERCOT's words. Default taken: "Agreement signed" and "No agreement yet" on this page until the table is rebuilt.
   The other choice: keep "Reached operation" with the line above it only.
2. The withdrawn share in the MW view is by count (0.71 for CAISO 2021; by MW it would be 0.67). Default: by count.
3. The table's download stays held whole, so the CAISO, ERCOT and SPP rows the page shows cannot be downloaded.
   Default: held. The other choice: a download of the three public queues' rows.

## Not finished, and why

- Nothing of the task is left open. Not done because it is not this session's: the table's own fix (data request 1),
  the two other machines' pages, and the browser reads.
