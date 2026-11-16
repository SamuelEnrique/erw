# Session 7507 report: the ERCOT peak premium explorer at the done line

Chain 304, part A, tool 7 of 9. samueloldlaptop (code role), unattended, 16 November 2026. Branch `wip/7507-peak-premium`, not pushed. The work is commit `5815691f4`; this report is the commit after it. Model spend: USD 0.

## At the top

- **No figure the page shows is wrong.** Every row of both tables equals the value recomputed from ERCOT's 15-minute prices (25,704 of 25,704).
- **Not meant, and seen:** on the site today the page says "Stale since 21 October 2026" for both tables (26 days). The tables are computed only on the data machine; the cloud's daily run skips them. A data request row is below.
- **The figures committed here are of this machine's copy of the tables** (built 29 September 2026). The warehouse's copy is newer, so the year 2026 and the months from September 2026 differ on the site. Every complete year and month is the same. A data request row is below.
- **No site build and no type check was run** (this machine cannot). The page change touches three lines of types; a build of the merged commit is needed before landing.
- **Not read:** the 2025 average price in the market monitor's 2025 report (its Table 1 is drawn in a font this machine's PDF reader does not decode). No figure was guessed.

## Shared explore files changed

None. `site/components/explore/`, `site/lib/explore.ts` (it is `site/lib/explore/index.ts`) and `site/lib/explore/source.ts` are as they were. Changed: the page, its own library `site/lib/explore/peakpremium.ts`, and a new `Decisions.tsx` in the page's folder.

## The five parts

- **The method note.** `docs/methods/ercot_peak_premium.md` completed with "The tool as a reader meets it", eight parts: what the page shows; every figure's table and rule; where the input is now and rules stated in full; what the tool does not hold; the decisions; the cross-check; the replication; five rulings. Nothing above it is rewritten. Gaps it closes: the input tables were renamed in session 29; how a tie is rounded; which years a month's view opens on; the partial-month rule (amended).
- **The replication.** `replication/ercot_peak_premium/`: `replicate.py` (from the note and the two tables), `from_hourly.py` (both tables from the 15-minute prices), `replicate.do`, `page_figures.json`, `page_figures.csv`. The page's own figures come from `site/scripts/peak-premium-figures.mjs`, which draws the page with the site's code on the table files. As printed:
  - `550 of 550 views open as the note says (the hub, the period, the two years, the years marked, the rows' download, the freshness line)`
  - `24786 of 24786 figures inside the tolerance, with the same text; 0 drawn by the page and not expected; 0 drawn two ways`
  - `25704 of 25704 rows of the two tables recomputed from the 15-minute prices` (2,469,864 hub-intervals, all six hubs, every year and month, the partial ones included)
  - No named difference. Not replicated: the charts' points as a browser draws them, and the count of days since the tables were computed.
- **The cross-check.** Eight rows in the note's section 6, against Potomac Economics' 2024 and 2025 State of the Market reports. Robots files read first (`potomaceconomics.com`, `eia.gov`); `ercot.com` not asked. The table is under "For the pack".
- **The decisions block.** "Decisions on this page", 11 choices, each with its default and source on hover, no grey text. None is editable: the page computes nothing.
- **The faults file.** `docs/reviews/ercot-peak-premium-faults-2026-11-16.md`, 14 rows: 5 fixed (3 on the page, the block, the note), 2 data machine, 4 rulings, 3 not a fault.

## Tests

One file a process: `ERW_SPEND_CAP_USD=0 .venv\Scripts\python.exe -m pytest tests/<file> -q -p no:cacheprovider`.

| File | Result |
|---|---|
| `tests/test_session7507_peak_premium.py` (new) | 14 passed |
| `tests/test_session403.py` | 12 passed, 1 skipped (it failed once on a `./` import in the page; the import now uses the site's alias, and the test is unchanged) |
| `tests/test_session170.py` | 27 passed, 2 skipped |
| `tests/test_session538.py` | 14 passed |
| `tests/test_session328.py` | 11 passed |
| `tests/test_session416.py` | 9 passed |
| `tests/test_session2200.py` | 8 passed |
| `tests/test_session1496.py`, `test_session2203.py` | 6 passed each |
| `tests/test_session2204.py` | 5 passed |
| `tests/test_session417.py`, `test_session472.py` | 4 passed each |

Not run: `site/scripts/check-values.mjs`, `check-explorers.mjs`, `check-routes.mjs` (they need the built site), the full suite, a build.

## What to review

`https://erw-flame.vercel.app/explore/ercot-peak-premium` (in review, as before).

1. Open it. It opens on HB_HUBAVG, 2015 against the newest complete year. Headlines for 2025: 34.12, 14.52, 25.68 USD/MWh.
2. Scroll to the foot. A fold, "Decisions on this page (each with its default and its source on hover)". Open it: 11 lines, each with a small "i". Point at one: "Default:" and "Source:" in a card.
3. `?hub=ercot:HB_BUSAVG&from=2021&to=2022`. In "The thesis's figures", the median of all intervals of 2021 reads 25.00 (it read 25). In the first table the peak minimum of 2022 reads -251.00.
4. `?month=12&from=2015&to=2026`. The three headline numbers read "not held", with no "USD/MWh" after them.
5. Nothing else on the page changes: same charts, tables, filters, downloads.

## For the pack

**What Samuel signs:** every figure on the page is a row of two public tables; every row of those tables is recomputed from ERCOT's 15-minute settlement prices by a rule written in the note; the page's choices are listed on it; and no published source gives the page's own measures, so the cross-check is of the yearly level and the direction only.

**The five choices that matter most:**

| Choice | Default | Source |
|---|---|---|
| The peak block | 16:00 to 21:00 local, every day; midday 12:00 to 16:00 | The thesis; the note's "Time-of-day blocks" |
| Medians and quartiles, never a mean | The premium is the peak median less the midday median, and the peak block's IQR | The note's "Metrics" |
| Every interval, no cap | February 2021 is in 2021 (645 intervals at or above 1,000 USD/MWh) | The note's "Notation" |
| Real time, time-weighted, at a hub | HB_HUBAVG; not day-ahead, not load-weighted, not a load zone | ERCOT NP6-785-ER, NP6-905-CD |
| Which years a view opens on | The first year held against the newest complete one | Session 403 |

**The cross-check** (HB_HUBAVG; "plain mean" is from `from_hourly.py --means`, not a figure of the page):

| What | Ours | Theirs | Publisher, document, date | Difference | Why |
|---|---|---|---|---|---|
| Real-time price 2024, USD/MWh | mean 26.83 (page's median 19.60) | 31.91 | Potomac Economics, 2024 State of the Market Report for the ERCOT Electricity Markets, May 2025, Table 1, page 5 | 5.08 lower, 16 percent | Theirs is load-weighted, by load zone |
| 2023 | 48.36 (21.37) | 65.13 | the same | 16.77 lower, 26 percent | the same |
| 2022 | 62.30 (44.02) | 74.92 | the same | 12.62 lower, 17 percent | the same |
| 2021 | 148.19 (24.60) | 167.88 | the same | 19.69 lower, 12 percent | the same |
| 2020 | 21.18 (16.56) | 25.73 | the same | 4.55 lower, 18 percent | the same; the years rank the same in both |
| When the price peaks | peak less midday median: -0.16 in 2015, 14.52 in 2025 | tightest hours moved from 4 to 5 p.m. to 7 to 9 p.m. | Potomac Economics, 2025 report, May 2026, page 5 | none in direction | both hours are in the peak block |
| At or below zero, 2025 | 959 intervals, 239.75 hours | "hundreds of hours" | the same, page 4 | none | theirs gives no count |
| Highest price, 2022 to 2024 | 5,101.55, 5,075.46, 4,981.33 | offer cap 5,000 | 2024 report, page 83 | within 2.1 percent | why a hub price passes the cap is not established |

Nothing published stands against the peak-block IQR, the spread of the medians, the block quartiles, the 99.9th percentile, the worst-interval multiple or any monthly figure. The EIA's article on 2025 prices (Today in Energy, 2 February 2026) names no ERCOT price; ICE's on-peak index that the EIA republishes is day-ahead and a 16-hour weekday block, and was not set beside a figure.

**The Stata commands** (`replication/ercot_peak_premium/replicate.do`, not run: no Stata here; `python replicate.py --headline` printed the same lines):

- `list year peak_iqr peak_minus_midday_median all_median`: 2015: 7.64, -0.16, 20.49. 2025: 34.12, 14.52, 25.68.
- `list year all_p999 worst_interval_multiple n_scarcity n_negative n_intervals`: 2015: 583.96, 28.50, 5, 297, 35,040. 2025: 311.80, 12.14, 9, 959, 35,040.
- Four `assert` lines hold the table to its own definitions; they print nothing.
- Part B (from the 15-minute prices, 2025): displays 34.12, 14.52, 25.68, 311.80 and 12.14; `count` gives 35,040, then 9, then 959.

**The rulings:** under "For Samuel's ruling" below.

## Data request rows

| Requested (UTC) | Session | Table or file | What, exactly | Source | State |
|---|---|---|---|---|---|
| 2026-11-16 11:48 | 7507 | `ercot_peak_premium_annual`, `ercot_peak_premium_monthly` | Both were last computed on 21 October 2026 and the page calls them stale (26 days). Run `warehouse/derived/ercot_peak_premium.py` on the data machine and load both, so the year 2026 and the months of October and November 2026 are current. Nothing is wrong in a row: 25,704 of 25,704 recomputed | ERCOT NP6-785-ER and NP6-905-CD, through `ercot_all_hub_prices_history` and `iso_rtm_hub_prices` | requested |
| 2026-11-16 11:48 | 7507 | `replication/ercot_peak_premium/page_figures.json`, `page_figures.csv` | They are of the tables built on 29 September 2026. After the row above, on `wip/7507-peak-premium` or after it lands: `python replication/ercot_peak_premium/from_hourly.py` (expect every row equal), `python replication/ercot_peak_premium/replicate.py --write` (expect N of N), then commit the two files. The do-file's expected values do not move (2015 and 2025 are complete) | The two tables as the data machine holds them | requested |

## Browser read rows

| Asked (UTC) | Session | Branch | Address | What to look at | What should be seen | State |
|---|---|---|---|---|---|---|
| 2026-11-16 11:48 | 7507 | `wip/7507-peak-premium` | `/explore/ercot-peak-premium` | The fold "Decisions on this page" at the foot: open it, point at and tab to an "i" | 11 lines; each tip opens with "Default:" and "Source:", stays inside the page at 390 px, and no line of the block is grey | wanted |
| 2026-11-16 11:48 | 7507 | `wip/7507-peak-premium` | `/explore/ercot-peak-premium?hub=ercot:HB_BUSAVG&from=2021&to=2022` | "The thesis's figures", the median of all intervals, 2021; the first table, peak minimum, 2022 | 25.00 and -251.00; the thesis chart's median labels still read by the chart's own rule | wanted |
| 2026-11-16 11:48 | 7507 | `wip/7507-peak-premium` | `/explore/ercot-peak-premium?month=12&from=2015&to=2026` | The three headline numbers and the two tables | "not held" with no unit after it in the headlines; the 2026 cells of both tables read "not held"; the chart draws 2015's four boxes only | wanted |
| 2026-11-16 11:48 | 7507 | `wip/7507-peak-premium` | `/explore/ercot-peak-premium` | The three charts' hover cards and their "Table" views | Each chart point is a value the page's tables show for the same hub and period (the replication reads the tables, not the charts) | wanted |

## Landing request

- **Head:** the commit that holds this report, on `wip/7507-peak-premium`; the work is `5815691f4`. On the base the branch was given (`31757a20c`, the merge of origin/main into `wip/7500-done-line`).
- **Tests:** the 12 files above, 120 passed, 3 skipped, each in its own process.
- **What changes:** `/explore/ercot-peak-premium` only: whole-dollar prices gain two decimals; "not held" loses its unit; a decisions fold at the foot; the partial-month rule (no month of today's tables changes its mark). New files under `replication/ercot_peak_premium/`, `tests/`, `docs/reviews/`, `site/scripts/peak-premium-figures.mjs`; the note is longer.
- **What does not:** no table, no builder, no shared explore file, no other page, `site/lib/release.ts`.
- **A snapshot would differ on:** none of the 25 pages it reads (the page is in review; a visitor sees the in-review page).
- **Before landing:** a site build of the merged commit (none was run here), and `check-values` (a whole-dollar price now reads "25.00"; the checker accepts a text that starts with "25").

## Needs the key

Nothing.

## Decisions made without you

- The replication recomputes all rows of both tables, not a sample: it runs in about 11 seconds.
- A plain mean is printed by `from_hourly.py --means` for the cross-check only. It is in no table and not on the page.
- The fixture of the test holds real rows only: two hubs of the tables, and HB_HUBAVG's 15-minute prices of March and November 2025.
- The partial-month rule was tightened in the page's own library, and the note amended in its new section rather than in the old lines.
- The page imports its decisions by the site's alias, because an older test forbids a `./` import on this page.
- The 2025 report's Table 1 was left unread rather than decoded by guess.

## For Samuel's ruling

1. The line under the title says the price runs "wider" in the peak "than at midday", but the page shows the peak block's own spread, not a comparison. Default: the sentence stays.
2. The notes under charts and sections are grey text, where the page standard asks for hover tips. They come from the frame every tool shares. Default: not changed.
3. The thesis chart writes 19.1 and 3,553 where the table under it writes 19.10 and 3,553.10. It is the chart set every page uses. Default: not changed.
4. Add a mean, or the industry's on-peak block (06:00 to 22:00, weekdays), so a published price could be set beside the page. Default: not built.
5. Compute the two tables on a schedule. They are 26 days old today. Default: a request to the data machine only.

## Seen in another tool

- The ERCOT tab of `/prices` (`site/app/explorer/ercot-peak-premium/view.tsx`) draws the same tables and may write a whole-dollar price without decimals. Not read here.
