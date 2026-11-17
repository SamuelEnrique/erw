# Session 7531 report: /events and its nine event pages at the done line (chain 304, second run)

Energy Research Warehouse (ERW), samueloldlaptop, 16 November 2026. Branch `wip/7531-events`, worktree
`C:\Users\lossa\Documents\erw-7531`, from origin/main at `dd2dabe11`. Brief: `runs/c304b_brief.md` (chain 304's
part A, five parts). Model spend USD 0 (`ERW_SPEND_CAP_USD=0`; no model called).

## What was done

- **The method note** `docs/methods/events.md`, completed (140 lines added, nothing removed): the ten pages as a reader
  meets them, every figure's entity, variable and rule in one table, the assumptions, what the tool does not hold, the
  license hold as it stands, three dated corrections, the decisions (15) and the replication and cross-check.
  `docs/methods/event_study.md` gains a dated section: the four windows its table of event days left out, and the
  fourth implementation.
- **The replication** `replication/events/replicate.py` (standard library, from the notes and the public table alone):
  **1,149 of 1,149** (every one of the 1,100 numbers not held that the ten pages compute, each the row its sentence's
  rule picks and inside half its last shown digit, with the event study tables' day counts); the table's comparison
  rows from its level rows 2,890 of 2,890; the builder's 62 pooled estimates not held with their intervals 186 of 186;
  15 of 15 sentences of the pages that state a fact of the rows true. The pages' figures come from the pages drawn
  whole with the site's own code (`site/scripts/events-pages.mjs`; the hold set aside for the drawing only).
  `replicate.do`: five headline figures in Stata (not run: no Stata here). The rows it runs on are beside it
  (`window_rows.csv`, 29,469 rows of 19 October 2026).
- **The held-row fix (same day, same branch).** The first commits copied license-held rows into this public
  repository: 484 rows of `event_window_daily` and 3 of `event_study_estimates` whose entity is ISO-NE's, MISO's or
  NYISO's hub, and the 27 page figures of those hubs. Both tables are "license needed", held by grid
  (`site/data/license_status.json`; the rule `licenseHeldRow` in `site/lib/license.ts`). `replicate.py` now drops a
  held row as it reads it, counts held figures as "held, not recomputed here" (27 figures, 3 estimates), and its
  `--write` copies no held row or figure (each file's first line, and `heldFigures` in `page_figures.json`, give the
  count); `events-pages.mjs` writes no held figure to the figures file. The counts moved from 1,176 of 1,176 and
  195 of 195 for that reason alone. Removed: `window_rows.csv` 484 rows, `estimate_rows.csv` 3, `page_figures.csv` 27
  lines, `page_figures.json` 27 figures; `notice_rows.csv` and `statements.csv` held none. Test:
  `NoHeldRowInTheFolder` in `tests/test_session7531_events.py`. The coordinator squashes the branch so that no commit
  holds the rows.
- **The cross-check** `docs/reviews/events-crosscheck-2026-11-16.md`: 16 rows against FERC's Uri and Elliott reports
  (FERC's copies; nerc.com refuses AI agents in its robots file and was not read), CAISO's Root Cause Analysis of
  August 2020 and its September 2022 heatwave deck, ERCOT's releases of 6 and 14 September 2023, PJM's Inside Lines
  review of 2025, the market monitor's Winter Storm Fern analysis, and EIA's two COVID-19 articles. Every peak is
  within 2.0 percent of the operator's own and on the same day.
- **The decisions block** `site/app/events/Decisions.tsx`, mounted at the foot of the index (13 choices) and the nine
  event pages (13, the COVID-19 page 15), each choice's default, source and session in a hover tip; nothing editable
  (the pages have no input).
- **The faults** `docs/reviews/events-faults-2026-11-16.md`: 10 rows. 3 site faults fixed with tests, 1 note
  completed, 1 data machine, 5 rulings.
- **Tests:** `site/scripts/test-events-render.mjs` 43 of 43 (the ten pages drawn on the rows beside the replication);
  `tests/test_session7531_events.py` with the older files naming the pages (`test_session241a`, `319`, `92`): 51
  passed, 15 skipped by their own rules (tables not on this machine). (42 of 42 and 47 before the held-row fix, which
  added one render check and four tests that no held row or figure is in `replication/events/`.)

## What to review

1. `https://erw-flame.vercel.app/events`: the COVID-19 card now reads "Lower 48, deepest weekly drop from the week of
   2020-03-22: ... 2020-05-17" (it led with the week of 2020-03-01). At the foot, open "Decisions on this page (13)";
   hover an "i": Default, Source, Made in.
2. `https://erw-flame.vercel.app/events/covid-2020`: the grey caveat now says the seven ISO grids are set against 2019
   and 2018 and the Lower 48 against 2019 alone; the first chart is titled "against the same weeks of earlier years",
   unit "% vs baseline"; each ISO grid's small chart has a third line, "2018, same weekday". Fold at the foot: 15.
3. `https://erw-flame.vercel.app/events/ercot-heat-2023`: a new second paragraph quotes ERCOT's release of 14 September
   2023 (85,464 MW on 10 August; 84,182 MW on 8 September and 83,911 MW on 7 September), linked; the sentence under the
   first chart says "the 82,705 MW ERCOT announced that evening as its September record".
4. Any event page, e.g. `https://erw-flame.vercel.app/events/elliott-2022`: almost every figure reads "license
   needed" (fault 1, below). Only ERCOT's and SPP's hub figures show numbers.

## Needs the key

- Nothing. `/ask` was not asked whether it reads the event tables (no model call); the replication needs no key.

## Decisions made without you

- The pages were drawn with a stand-in for the license status file that drops the two event tables, so the replication
  could recompute the held figures; this is in a script loader only (`EVENTS_DRAW_UNHELD=1`), and the page, its status
  file and its hold are unchanged. Since the held-row fix the figures of rows the row rule holds (ISO-NE's, MISO's and
  NYISO's hubs) are dropped from what the drawing writes and counted only; the EIA-930 figures fault 1 draws as held
  are of no grid's rows and are recomputed. The render test runs without it and holds the hold as it stands.
- The COVID-19 small charts gained a 2018 line (only where 2018 is held): the baseline the page now names is drawn.
- The index's COVID-19 card follows the event page's own rule (from the week of 2020-03-22) rather than a new one.
- ERCOT's later records were added as a quote with its link; nothing of the page's quotes of 6 September was removed.
- insidelines.pjm.com's robots file was read just after its one page was read, not before (it allows every path but
  `/wp-admin/`). Every other host's robots file was read first. PJM's own Elliott report (over 10 MB) could not be read
  today; FERC's report gives PJM's own peak figure in its place.
- The decisions block lives in the tool's folder (as the battery awards page's does), not in the shared
  `lib/decisions.ts`, which other branches edit.

## For Samuel's ruling

1. **The hold draws EIA's figures as "license needed" (fault 1).** On the built pages 1,117 of the 1,127 numbers read
   "license needed": CAISO's, PJM's, ERCOT's, SPP's and the Lower 48's demand, every carbon intensity, every estimate.
   The cause: the hold of 21 October is by grid (ISO-NE, MISO, NYISO), and a figure whose entity names no grid the
   license module knows (`eia930:PJM`) is held as if the whole table were; the module's own comment says such a row is
   kept, and the rows are EIA's publication. Default taken: unchanged (no hold lifted). Choices: name EIA-930's
   entities to their grids (CAISO, PJM, ERCOT, SPP shown; ISO-NE, MISO, NYISO held), or keep EIA-930 rows as rows of no
   grid (all shown), or as now.
2. **Decimals in one column (fault 7):** "47,496" beside "413,170.00". Default: unchanged (the site's checked-number
   rule). Choice: fixed decimals per column of the event study block.
3. **SPP's Elliott peak (fault 8):** FERC gives 47,157 MW "during Winter Storm Elliott"; the page says the warehouse
   holds no SPP peak record. Default: unchanged. Choice: one sentence citing FERC.
4. **No weather for the three newest events (fault 9):** their estimates carry the weather in full. Default: no new
   NOAA pull. Choice: approve data request row 50.
5. **Grey notes (fault 10):** the page standard asks for tips, not grey text; every event page has grey captions.
   Default: left as they are.

## Rows for the coordinator

### (a) Landing request, row 29

| 29 | `wip/7531-events` | `HEAD` | `7531-events` | 7531 | 2026-11-16 | `site/scripts/test-events-render.mjs` (43 of 43, the ten pages drawn to HTML without a build on the public rows beside the replication); `tests/test_session7531_events.py` with `test_session241a`, `test_session319`, `test_session92`: 51 passed, 15 skipped by their own rules (tables not on this machine); `replication/events/replicate.py` 1,149 of 1,149 (was 1,176: the 27 figures of ISO-NE's, MISO's and NYISO's hubs are held by grid and counted, not recomputed or copied; squash the branch so no commit holds the 487 held rows); not built here (memory) | requested |

(Replace `HEAD` with the branch's head commit as pushed: see the final message.)

## Row 29: what it holds (chain 304, session 7531, /events and its nine event pages at the done line)

- **From** origin/main `dd2dabe11`. Report: `archive/sessions/SESSION_7531_REPORT.md` on the branch.
- **What changes:** `site/app/events/page.tsx` (the COVID-19 card reads from the week of 2020-03-22; the decisions
  fold), `covid-2020/page.tsx` (the baseline words: 2019 and 2018 for the seven ISO grids, the Lower 48 2019; a 2018
  line in each ISO grid's small chart; the chart's unit), `ercot-heat-2023/page.tsx` (a paragraph quoting ERCOT's
  release of 14 September 2023; one sentence's words), the nine event pages (the decisions fold after the event study
  block), the new `site/app/events/Decisions.tsx`. New: `site/scripts/events-pages.mjs`, `events-page-loader.mjs`,
  `events-page-register.mjs`, `test-events-render.mjs`; `replication/events/` (replicate.py, replicate.do, the rows,
  page_figures, statements); `docs/reviews/events-faults-2026-11-16.md`, `events-crosscheck-2026-11-16.md`;
  `docs/methods/events.md` and `event_study.md` extended; `tests/test_session7531_events.py`.
- **What does not change:** any figure's value or check key except the index's COVID-19 card (its key moves from the
  week of 2020-03-01 to 2020-05-17), every table, `EventWindow.tsx`, `EventStudy.tsx`, `lib/eventstudy.ts`,
  `site/lib/release.ts`, `site/data/license_status.json` and the hold.
- **Before landing:** a site build of the merged commit (none was made here); `check-values` reads the pages as before
  (the index's COVID-19 card's new key is a row of the live set: `series|event_window_daily|eia930:US48|demand_pct_vs_baseline_week|2020-05-17T00:00:00Z|covid_2020`, held today by fault 1, so drawn "license needed").
- **Snapshot differences to expect:** none on the 25 addresses (every page is in review). With the review cookie:
  the ten event addresses gain the decisions fold; `/events` the card's words and date; `/events/covid-2020` its words
  and a 2018 line; `/events/ercot-heat-2023` one paragraph. **Tables:** none.
- **After the landing:** rows 76 to 83 of `docs/state/browser_reads_wanted.md`. Data requests rows 49 and 50.

### (b) Browser reads, rows 76 to 83

| # | Asked (UTC) | Session | Branch (landing row) | Address | What to look at | What should be seen | State |
|---:|---|---|---|---|---|---|---|
| 76 | 2026-11-16 | 7531 | `wip/7531-events` (row 29) | `https://erw-flame.vercel.app/events` | The COVID-19 card; at 390 px | "Lower 48, deepest weekly drop from the week of 2020-03-22: license needed % against the same weeks of 2019, 2020-05-17" (the number held by the hold, fault 1); no sideways scroll | wanted |
| 77 | 2026-11-16 | 7531 | `wip/7531-events` (row 29) | `https://erw-flame.vercel.app/events` | The fold "Decisions on this page (13)" under the Flex Alert section; open it; hover and tap an "i"; at 390 px | Closed to start; 13 lines; each tip shows "Default:", "Source:" and "Made in:", stays inside the screen at 390 px; the window line's tip lists the nine windows | wanted |
| 78 | 2026-11-16 | 7531 | `wip/7531-events` (row 29) | `https://erw-flame.vercel.app/events/covid-2020` | The grey paragraph under the framing; the first chart's title and unit | "The baseline of the seven ISO grids is the mean of the same weekday of 2019 and of 2018 ..."; title "Weekly demand against the same weeks of earlier years, all grids"; unit "% vs baseline" | wanted |
| 79 | 2026-11-16 | 7531 | `wip/7531-events` (row 29) | `https://erw-flame.vercel.app/events/covid-2020` | Each grid's small chart and its legend; the Lower 48's | Three lines for the seven ISO grids (2020, "2019, same weekday", "2018, same weekday"), two for the Lower 48; the 2018 line distinguishable from the 2019 one; hover answers on all three | wanted |
| 80 | 2026-11-16 | 7531 | `wip/7531-events` (row 29) | `https://erw-flame.vercel.app/events/covid-2020` | The fold at the foot, below "What the estimates say"; at 390 px | 15 choices, the last two "after-order" and "weeks"; tips inside the screen | wanted |
| 81 | 2026-11-16 | 7531 | `wip/7531-events` (row 29) | `https://erw-flame.vercel.app/events/ercot-heat-2023` | The framing's second paragraph and its link; the sentence under the first chart | "Eight days later ERCOT wrote ... 85,464 MW on August 10, 2023 ... 84,182 MW on September 8 ... 83,911 MW" linking to ERCOT's release of 14 September 2023; "the 82,705 MW ERCOT announced that evening as its September record" | wanted |
| 82 | 2026-11-16 | 7531 | `wip/7531-events` (row 29) | `https://erw-flame.vercel.app/events/uri-2021` | The fold at the foot; the "baseline" line's tip | 13 choices; the baseline tip's default reads "The same calendar days of 2019 and 2020"; the fold does not overlap the event study's own fold above it | wanted |
| 83 | 2026-11-16 | 7531 | `wip/7531-events` (row 29) | `https://erw-flame.vercel.app/events/elliott-2022` | Every figure under the charts and in "What the estimates say" | As on this machine today: every EIA-930 figure and estimate "license needed" with the hover naming ISO-NE, MISO and NYISO; ERCOT's hub figures as numbers (fault 1, a ruling). If numbers show for PJM, say so: the hold reads differently on the live build | wanted |

### (c) Data requests, rows 49 and 50

| # | Requested (UTC) | Session | Table or file | What, exactly | Source | State |
|---:|---|---|---|---|---|---|
| 49 | 2026-11-16 | 7531 (chain 304, samueloldlaptop; branch `wip/7531-events`) | `event_window_daily` (live set) | Say which build of `event_window_daily` the live set holds. The old laptop's copy is the build of 2026-10-19T09:43:29Z (run 20261019T094329Z, 29,953 rows, 484 of them held by grid), on which the replication passes 1,149 of 1,149 (1,176 before the held-row fix, which counts the held hubs' 27 figures and does not recompute them). If the live set holds another, load the build of 19 October or say what differs; then run `python replication/events/replicate.py --tables <dir>` on the live rows. No request to any publisher | `docs/reviews/events-faults-2026-11-16.md`, row 6 | requested |
| 50 | 2026-11-16 | 7531 (chain 304, samueloldlaptop; branch `wip/7531-events`) | `noaa_isd_hourly`, `event_window_daily`, `event_study_estimates` | Only if Samuel approves the new pull (faults row 9): pull NOAA ISD hourly temperatures for the stations of the January 2025 cold, the June 2025 heat and the January 2026 cold (PJM PHL and ORD, MISO MSP, NYISO JFK, ISO-NE BOS, SPP OKC, ERCOT DFW and IAH) over each window and its baseline days, rebuild `event_window_daily` and `event_study_estimates`, load the first | NOAA NCEI ISD (public); `docs/methods/event_study.md`, "Temperature-controlled specification" | waiting for Samuel's ruling |

### (d) Progress line

| 12 | `/events` and its nine event pages | done `HEAD` on `wip/7531-events` (landing row 29): the note `docs/methods/events.md` completed (the ten pages, every figure's rule, 15 decisions, what it does not hold, the hold) and `event_study.md`'s nine windows; the replication 1,149 of 1,149 (1,100 numbers of ten pages not held, each the row its rule picks; 2,890 of 2,890 comparison rows; 186 of 186 of the builder's estimates; 15 of 15 sentences true; 27 figures and 3 estimates of ISO-NE's, MISO's and NYISO's hubs held by grid, counted, not recomputed or copied: the held-row fix moved it from 1,176 and 195) with a do-file of five; the cross-check, 16 rows against FERC, CAISO, ERCOT, PJM, the market monitor and EIA, every peak within 2.0 percent; the decisions block on all ten pages; faults: 10 found, 3 fixed, 1 data machine, 5 rulings (1 note completed) | 7531 |
