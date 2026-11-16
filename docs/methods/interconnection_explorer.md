# Method: the interconnection queue explorer

The page `/explore/interconnection` ("Interconnection queues"), in review and not in the menu, as a reader meets it.
Written by session 7509 (chain 304, 16 November 2026). It points to the notes of the tables and does not repeat them:

- `iso_queue_statistics`, the one table the page reads: [`energy_projects.md`](energy_projects.md), "Queue statistics"
  (what counts in each operator's own words, the inputs, the first build's fault and the rebuild of 21 October 2026).
- The six queue tables it is built from: [`caiso_interconnection_queue.md`](caiso_interconnection_queue.md),
  [`ercot_interconnection_queue.md`](ercot_interconnection_queue.md), [`spp_interconnection_queue.md`](spp_interconnection_queue.md),
  [`nyiso_interconnection_queue.md`](nyiso_interconnection_queue.md), [`miso_interconnection_queue.md`](miso_interconnection_queue.md),
  [`isone_interconnection_queue.md`](isone_interconnection_queue.md).
- Berkeley Lab's Queued Up, which the page does not read and the cross-check below does:
  [`lbnl_interconnection_queue.md`](lbnl_interconnection_queue.md) and [`interconnection_queue_summary.md`](interconnection_queue_summary.md)
  (the page `/queues`, another tool).

Tables: `iso_queue_statistics`.

## What the page is

One grid operator's interconnection queue, by the year a position entered it and what became of the position since:
reached operation, withdrawn, still waiting, or status not stated; in positions or in MW. The page does no arithmetic.
Every number on it is one row of `iso_queue_statistics`, or the one count the table's header states for the queue (its
positions with no queue date), and carries that row's check key and its source in its hover.

## The filters

Four, all in the address, each a plain select; a value the table does not hold falls back to the default and the page
says so in one line.

| Filter | Address | Choices | Default |
|---|---|---|---|
| Queue | `queue` | `caiso`, `ercot`, `nyiso`, `miso`, `spp`, `isone` | `caiso` |
| Count | `measure` | `positions`, `mw` | `positions` |
| First entry year | `from` | every entry year the queue has a row for | the first |
| Last entry year | `to` | the same | the newest year that is over |

- The two years are read in order: `from=2020&to=2010` is drawn as 2010 to 2020, and (since session 7509) the two
  selects show 2010 and 2020.
- **A year not over.** An entry year at or after the year the queue was pulled for the build (the header's "Inputs
  read" line; 2026 for ERCOT and SPP on the table of 21 October 2026) is marked "(partial)" in the selects and in the
  table, hatched in the chart, and is never the default last year.
- PJM is not offered: the ERW holds no PJM queue table.

## What it draws

For the queue and the count chosen, with `lo` and `hi` the earlier and later of the two years:

1. **Three headline numbers, for entry year `hi`,** each with entry year `lo`'s figure under it when the two differ:
   `positions_entered` (or `mw_entered`), `positions_operating` (or `mw_operating`), and `withdrawal_rate`. A queue
   with no `withdrawal_rate` row at all (ERCOT) shows `positions_waiting` (or `mw_waiting`) third. The share is by
   count in both counts. The second number is labelled "Reached operation" and, for ERCOT, "Agreement signed"; ERCOT's
   third is labelled "No agreement yet" ("ERCOT's two statuses", below; session 7518).
2. **The stacked bars:** one bar an entry year from `lo` to `hi`, its four parts the rows `<count>_operating`,
   `<count>_withdrawn`, `<count>_waiting` and `<count>_status_not_stated`. A part with no row has no part.
3. **Two lines, where the queue holds them:** `withdrawal_rate` by entry year, and `wait_years_median` by entry year.
4. **The table "Every entry year":** one row a year from `lo` to `hi`: entered, the four statuses, and in positions
   also `withdrawal_rate`, `wait_years_median` and `wait_positions` ("Waits counted"). Under it, the header's count of
   the queue's positions with no queue date.
5. **The table "The six queues":** entry year `hi` for each queue, entered and the four statuses; and, in positions
   (since session 7518), the same year's `withdrawal_rate`, `wait_years_median` and `wait_positions`, so that the three
   queues shown stand side by side on the share and the wait of one entry year. Its columns keep the common words
   ("Reached operation", "Still waiting"); ERCOT's name in it carries a tip that says what the two are for ERCOT.
6. **One line on what the queue does not hold** (below), the freshness lines, the decisions block, the method link,
   the downloads and the source line.
7. **Since session 7518:** a tip beside the wait chart's title ("Whose wait", below); two lines above the decisions
   block, one on Berkeley Lab's Queued Up as another source and one on the load side ("Where the other queues and the
   load side are", below); and, on a held queue's line and at an address that asks for `queue=pjm`, a link to the
   same grid on `/queues`.

`wait_years_mean` is in the table and not on the page.

## How a figure is written

A count of positions (`positions_*`, `wait_positions`, the header's count) is written whole with thousands separators.
MW, the withdrawn share and the wait in years are written with two decimals, a whole value included (550.00, 1.00); a
value exactly halfway is rounded away from zero (a share of 0.625 is 0.63). The table holds six decimals. The share is
a fraction of 1, not a percent. Until session 7509 a value that happened to be whole lost its decimals ("550" above
"162.10" in one column).

## When a cell reads "not held"

The page writes "not held" where the table has no row. That happens in three ways, and the page does not tell them
apart in the cell:

- **The operator does not give it.** ERCOT's report lists no withdrawn position: no `positions_withdrawn`,
  `mw_withdrawn` or `withdrawal_rate` row for ERCOT. MISO's and ISO-NE's tables hold no in-service date: no wait.
- **No position to compute it from.** `wait_years_median` has a row only when at least one operating position of the
  year holds both dates in order (`wait_positions` is then above 0).
- **An MW row is written only when at least one position of the status states a capacity** (the builder,
  `warehouse/derived/queue_statistics.py`: the sum is written when any capacity is present). So a status with no
  position in a year has `positions_<status>` 0 and no `mw_<status>` row: the same cell reads 0 in positions and "not
  held" in MW. On the table of 21 October 2026 that is every "not held" MW cell of the three queues shown: 35 for
  CAISO, 16 for ERCOT, 42 for SPP; none is a year with positions whose MW is missing. This note did not say so before
  session 7509 (fault 6 of the faults file; a row for the data machine).
- A queue with no row at all for entry year `hi` (CAISO after 2023) reads "not held" across its row of the six-queue
  table.

## What a queue does not hold

One line above the figures, for the queue chosen (`NOT_HELD` in `site/lib/explore/interconnection.ts`):

- **CAISO:** its public queue report lists only a few of the requests that entered in 2023 and none later. The table
  holds 4 positions for 2023 (all withdrawn); Berkeley Lab counts 594 requests that entered CAISO's queue in 2023, and
  590 queue ids CAISO's report does not list ([`caiso_interconnection_queue.md`](caiso_interconnection_queue.md)).
  The page opens on CAISO and on 2023, so its opening headline reads 4 entered, 0 reached operation, share 1.00: true
  of the report, and far from the requests made (fault 1; the line was added by session 7509).
- **ERCOT:** its report lists active and completed positions only. No withdrawn count and no share; and "Entered" is
  the positions of an entry year still in the report, not every request made that year (198 for 2000 to 2020 against
  1,553 in Queued Up, which counts 795 withdrawn; fault 2).
- **SPP:** its wait reads its Commercial Operation Date, which its queue also fills for positions not yet built.
- **MISO, ISO-NE:** no in-service date, so no wait (both are held, below).

### ERCOT's two statuses (session 7518)

ERCOT's report has no status word. The queue connector reads it through the library gridstatus (0.36.0, `ercot.py`),
which writes "Completed" for a position whose "IA Signed" day is filled and "Active" for one whose day is empty, takes
the queue date from "Screening Study Started", the proposed in-service date from "Projected COD" and the actual one
from "Approved for Synchronization". So for ERCOT:

- `positions_operating` and `mw_operating` are the positions **whose interconnection agreement is signed**, built or
  not. On this machine's copy of ERCOT's queue (the pull of 30 September 2026, 1,778 rows, 580 of them "Completed"),
  the 44 such positions of entry year 2025 all have a projected operation day still to come and none a day of approval
  to synchronize; of the 116 of entry year 2022, 107 have a projected day still to come and 15 a day of approval.
  Berkeley Lab's Queued Up counts 17 requests of entry year 2022 in operation at the end of 2025, where the table holds
  115 "operating".
- `positions_waiting` and `mw_waiting` are the positions with no signed agreement.
- `wait_positions` is the positions with a signed agreement and a day of approval to synchronize, and the wait runs
  from the day the screening study started to that day.

The page therefore heads the two "Agreement signed" and "No agreement yet" for ERCOT (`STATUS_WORDS` in
`site/lib/explore/interconnection.ts`), in the headline numbers, the stacked chart and the table of years, and says so
in ERCOT's line; the variables keep their names. The table itself is not changed here: a row for the data machine asks
that ERCOT's operating group be read from the report's own day of approval to synchronize
(`docs/reviews/interconnection-read-2026-11-16.md`, row 1). Until session 7518 the page, this note and the table's
note called the group "Reached operation" and gave "Completed" as ERCOT's own word.

### Whose wait (session 7518)

A year's median counts only its positions that have already reached operation with both dates. A position still
waiting is in no wait, and if it is built its wait will be longer than the time since it entered: a recent entry
year's median stands on its fastest positions and is not final (CAISO, entry year 2020: 1.27 years over 5 positions,
with 36 of the year's 153 still waiting). The tip beside the wait chart's title says so, and names the two other pages
that count a wait another way, both from Berkeley Lab's Queued Up and both by the year a plant came online: `/queues`
(the median over all years, and by operation year) and the "Time to connect" column of `/cost-of-power?view=allgrids`
(the plants that came online in the last three whole years). For one queue the three do not give one number, and are
not meant to: SPP, entry year 2018, 4.40 years over 2 positions here; 4.06 years over 272 requests of every year on
`/queues`; 84.6 months (7.05 years) over the 30 that came online from 2023 to 2025 on the All grids tab.

### Where the other queues and the load side are (session 7518)

- PJM, and the three held queues: Berkeley Lab's Queued Up counts them on `/queues` (`?grid=pjm`, `miso`, `nyiso`,
  `isone`), under its own license (CC BY 4.0). A held queue's line and an address that asks for PJM link there. No
  figure of a held queue is drawn here and no hold is lifted: the link is to another source on another page.
- Queued Up's count for a queue and an entry year is not this page's (two sources, pulled ten months apart): SPP,
  entered 2018, 150 positions here and 135 requests there; CAISO, entered 2021, 361 on both, 255 withdrawn here and 220
  there. The line above the decisions block says the two are different sources.
- A large load's request is in no figure of this page. The line under it points to ERCOT's large-load status on
  `/datacenters` and to the "Time to connect" column of the All grids tab.

## Assumptions, each with its default and its source

The list the page carries as its decisions block; the table's note has the rule behind each.

| Assumption | Default | Source |
|---|---|---|
| A queue is one pull of the operator's report, not a history | the pull the table was last built from (19 October 2026 for CAISO, ERCOT, SPP and ISO-NE; 26 September 2026 for NYISO and MISO) | the header's "Inputs read" line |
| Status groups | operating: completed; withdrawn: withdrawn (SPP also TERMINATED); waiting: active and suspended; else status not stated. For ERCOT "completed" is a signed interconnection agreement, and the page heads it so ("ERCOT's two statuses", above) | `energy_projects.md`, "What counts"; gridstatus 0.36.0, `ercot.py` |
| Entry year | the year of the queue date; no date, no year (the header counts them) | the same |
| Withdrawn share | withdrawn over entered, by count | the same |
| Wait | days from `queue_date` to `actual_in_service_date` over 365.25, operating positions with both dates in order; the median | the same |
| MW | `capacity_mw` as the queue states it, summed; a position with none adds none | the same |
| Stale | a table last computed more than eight days ago (the queues are pulled weekly, on Mondays UTC) | `warehouse/run_daily.sh`; session 7509 (three days until then) |
| Held | NYISO, MISO, ISO-NE: not read, "license needed" | `docs/licenses.md`, `site/data/license_status.json` |

## The decisions on the page

`site/app/explore/interconnection/Decisions.tsx`, drawn at the foot of the page and under a held queue's line: one line
a choice, its default and its source on hover. No choice is editable in place, because the page computes nothing: the
filters are the choices a reader can make. The keys, in the page's order:

1. `snapshot`: one pull of the operator's report, not a history.
2. `statuses`: the four statuses and the operators' words behind each.
3. `entry-year`: the year of the queue date; undated positions in no year.
4. `ercot-withdrawn`: ERCOT holds no withdrawn positions; its third headline is still waiting.
5. `share`: withdrawn over entered, by count, a fraction of 1.
6. `wait`: the median of queue date to in-service date, with its count; SPP's date.
7. `mw`: the stated capacity, summed; when an MW cell reads "not held".
8. `no-sum`: every number one row; nothing added up.
9. `years`: every year to the newest complete one; a year not over is partial.
10. `queues`: CAISO first; six queues, no PJM; three held.
11. `rounding`: positions whole, the rest two decimals.
12. `freshness`: the catalogue and the header; stale after eight days.

## Licenses

`iso_queue_statistics` is held by grid from 21 October 2026: NYISO's, MISO's and ISO-NE's rows are not read and the
page shows "license needed" for them, in the queue's own view and in the six-queue table. CAISO's, ERCOT's and SPP's
queue tables are public. MISO is paused (`warehouse/metadata/paused_sources.csv`): nothing is requested of it; its
rows stay as they are, held.

## How old the figures are

The table is not rebuilt in the daily run. `warehouse/run_daily.sh` pulls the queues weekly; `iso_queue_statistics` is
rebuilt only when the data machine runs `warehouse/derived/queue_statistics.py`. On 16 November 2026 the table is the
build of 21 October 2026, from the pulls of 19 October (and 26 September for NYISO and MISO), while the queue tables
were last pulled on 5 November. The page says both in its freshness lines. Its source line said the queues were "as
the ERW last pulled them"; session 7509 changed it to the pull the table was built from. The figures' hover words
(`site/lib/explore/source.ts`, a file the three explorers share) still say "as the ERW last pulled it": fault 7.

## The replication

`replication/interconnection/`:

- `fetch_rows.py --from <warehouse/output>` copies the tables into `rows/` (not in git: the statistics and three queue
  tables are held).
- `replicate.py` (part A) reads `iso_queue_statistics` as this note says the page reads it and sets every figure and
  every view beside what the page's own code draws on the same file (`site/scripts/interconnection-figures.mjs`): each
  queue in each count as it opens, every first entry year with the default last one, every last entry year with the
  default first one, the years the other way round, one year alone, an address the table does not hold, and each held
  queue. On the table of 21 October 2026: **730 of 730 figures inside the tolerance; 284 of 284 views drawn as the note
  says; 139 queue-years whose four statuses make up the positions entered.** `--grid` on the node script adds every
  pair of years.
- `replicate.py --queues` (part B) computes every row of the table again from the six queue tables by the table's
  note. On the old laptop's copies on 16 November 2026: NYISO 352 of 352 and MISO 113 of 113 rows equal at six
  decimals (the same pull the table read; held, so no value is printed). CAISO 304 of 309, ISO-NE 245 of 261, SPP 311
  of 342, ERCOT 63 of 134: this machine's copies of those four are the pull of 30 September, the table read the pull
  of 19 October (ERCOT 1,778 rows here, 1,758 read; SPP 3,076 and 3,078; CAISO 2,278 both, one position of 2019
  withdrawn between the pulls). Whether the four agree on the pull the table read cannot be shown on this machine: a
  row for the data machine (fault 8).
- Since session 7518 part A also holds, view by view: ERCOT's own words in its headlines and its table of years; the
  six queues' columns (three more in positions) and the tip on ERCOT's row; the wait chart's tip; the line on the load
  side with its two links; the link to `/queues` on a held queue's line and at an address that asks for PJM. The
  counts did not move (730 figures: the three new columns draw rows the queues' own views already drew; 284 views).
  `site/scripts/interconnection-figures.mjs --only=<address>;<address>` draws the named addresses alone.
- `replicate.do`: the five headline figures in Stata, expected values at its top.
- `cross_check.py`: the arithmetic of the next section.
- `page_figures.json`, `page_figures.csv`: the figures of the three queues shown, the page's text beside the table's
  value.

## The cross-check

Against Lawrence Berkeley National Laboratory and GridTracker, *Queued Up: 2026 Edition* (data file through the end of
2025, published May 2026, CC BY 4.0), as the warehouse holds it (`lbnl_interconnection_queue`, retrieved 2 October
2026, summarized in `interconnection_queue_summary`). No host was asked for anything by session 7509. The explorer's
side is each operator's own report as pulled on 19 October 2026. No figure is adjusted.

| Queue | Figure | The explorer's table | Queued Up 2026 | Difference | Why |
|---|---|---|---|---|---|
| CAISO | entered 2000 to 2020, requests | 1,910 | 1,910 | 0 | the same requests |
| CAISO | the same: reached operation | 249 | 232 | +17 | the pulls are ten months apart: of Berkeley Lab's active rows, 19 are completed and 47 withdrawn in CAISO's report (`caiso_interconnection_queue.md`) |
| CAISO | the same: withdrawn | 1,504 | 1,492 | +12 | the same |
| CAISO | the same: withdrawn share | 0.787 | 0.781 | +0.006 | |
| CAISO | the same: still waiting | 157 | 186 | -29 | the same |
| CAISO | entered 2021, requests | 361 | 361 | 0 | |
| CAISO | entered 2021, MW | 105,537 | 150,347 | -44,810 | Berkeley Lab adds every part of a hybrid (`mw_1 + mw_2 + mw_3`); CAISO's report states one capacity |
| CAISO | entered 2023, requests | 4 | 594 | -590 | CAISO's public report does not list them (fault 1) |
| CAISO | still waiting, every entry year, MW | 73,848 | 190,717 | -116,869 | the same 2023 requests; the sum is the cross-check's, never the page's |
| ERCOT | entered 2000 to 2020, requests | 198 | 1,553 | -1,355 | ERCOT's report lists no withdrawn position (795 in Queued Up) and 136 of the 459 that reached operation (fault 2) |
| ERCOT | entered 2022: `positions_operating` against requests in operation | 115 | 17 | +98 | the table's group is a signed agreement, not operation ("ERCOT's two statuses"; session 7518) |
| ERCOT | entered 2020: the same | 46 | 60 | -14 | the same, and ERCOT's report no longer lists most plants that operate |
| ERCOT | entered 2025, requests | 354 | 387 | -33 | the same, less so for a recent year |
| ERCOT | entered 2025, MW | 104,175 | 106,525 | -2,350 | |
| ERCOT | still waiting, every entry year, MW | 298,304 | 408,108 | -109,803 | not established here: the pulls are ten months apart |
| SPP | entered 2000 to 2020, requests | 1,722 | 1,682 | +40 | not established here: SPP's summary holds 40 more requests of those years than Berkeley Lab's file |
| SPP | the same: withdrawn share | 0.722 | 0.721 | +0.001 | |
| SPP | entered 2025, requests | 421 | 367 | +54 | not established here; 16 of the 421 have no status stated |
| SPP | still waiting, every entry year, MW | 138,850 | 151,152 | -12,302 | not established here: the pulls are ten months apart |

The whole table (each of the five last complete years, positions and MW) is what `cross_check.py` prints.

Where nothing published stands against a figure:

- **The median wait by entry year.** Berkeley Lab publishes durations by the year a plant came online, not by the
  year it entered (CAISO 6.02 years over 225 requests, ERCOT 3.70 over 470, SPP 4.06 over 272, over all years:
  `interconnection_queue_summary`). The table's note sets CAISO's waits by online year beside Berkeley Lab's
  (92.35 against 91.39 months, on the first build). By entry year there is no published figure.
- **The operators' own published totals, FERC's and the EIA's figures on queue size** were not read by session 7509:
  no request was made to any host. The page shows no total a national figure could stand against (it adds nothing
  up). ERCOT's documents are not read (its robots file disallows the paths) and MISO is paused.
- **Status not stated** (SPP's requests listed with no status): no published count.

The cross-check in `energy_projects.md` ("The cross-check against LBNL's Queued Up") was made on the first, faulty
build (CAISO 1,762 requests of 2000 to 2020); on the rebuilt table the count is 1,910, Berkeley Lab's own.

## What the tool does not hold

- PJM, and any utility outside the six operators.
- A history of any queue: positions an operator's report no longer lists are in no figure.
- The technology, the developer, the county or the point of interconnection of a position (the map's tabs and
  `/queues` draw those from other tables).
- Cost, network upgrades, study stage, or why a position was withdrawn.
- A total over years, statuses or queues, and any forecast of which waiting position is built.
- NYISO's, MISO's and ISO-NE's figures while their license is needed.

## Checks

`tests/test_session7509_interconnection.py` (the figure text, the filters, the lines, the decisions' keys against this
note, the committed figures, and the replication on the page as drawn where the tables are on the machine);
`tests/test_session405.py`, `tests/test_session2202.py` (the page's form); `site/scripts/check-values.mjs` (every
figure's row read again on the built site).
