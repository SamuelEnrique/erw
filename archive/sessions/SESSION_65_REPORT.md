# Session 65 report: the revenue and cost stack (capacity and ancillary service prices)

Energy Research Warehouse (ERW), session 65, on the portable laptop, 2026-10-02 about 14:55 to 19:30 UTC, with one abrupt restart and one pause on the way. **Model spend: USD 0.00** (the cap was USD 0). No paid service. No force push. Nothing merged or pushed to main, no Supabase write, no Redivis upload, the data lock never taken. **The finish step was not run.**

## To finish

**Read this before the commands.** The work is on the local branch `task/065-revenue-stack` and pushed to `origin/wip/065-revenue-stack`, not to `origin/task/065-revenue-stack`. `.github/workflows/code-branch.yml` runs on every push to `task/**` and merges the branch into main by itself when the tests and the site build pass. So the push in step 9 is the merge to main, and it starts a production deploy. Run it only when the demo is over.

The three tables are valid in scratch directories under `runs/session65/` (not in git). The raw downloads are in `warehouse/raw/`, so the connectors below request only what is new since 2026-10-02: a few CAISO days, ERCOT's newest daily files, one NYISO month page.

```bash
# 1. the branch, with main's newest metadata merged in (never a rebase, never a force)
git checkout task/065-revenue-stack
git fetch origin
git merge origin/main          # a conflict in warehouse/metadata/sources.csv: take main's side; step 4 writes the new sources back

# 2. the data lock, held by this session
python warehouse/lock.py acquire --task "session 65 finish" --minutes 120; echo "exit=$?"

# 3. sync the tables with the cloud
python scripts/sync.py; echo "exit=$?"

# 4. the three tables into warehouse/output (saved raw files are reused; one pull at a time)
python warehouse/connectors/iso_capacity_prices.py > runs/session65/finish_capacity.out 2>&1; echo "exit=$?"
python warehouse/connectors/ercot_as_prices.py     > runs/session65/finish_ercot.out 2>&1; echo "exit=$?"
python warehouse/connectors/caiso_as_prices.py     > runs/session65/finish_caiso.out 2>&1; echo "exit=$?"

# 5. the validator, then coverage (gates: never piped, read each exit code before the next line)
python warehouse/validate/erw_validate.py --json warehouse/output/*.csv > runs/validate_reports.json; echo "exit=$?"
python warehouse/metadata/build_coverage.py --reports runs/validate_reports.json > runs/session65/finish_coverage.out 2>&1; echo "exit=$?"

# 6. the append-only archive
python warehouse/archive/archive.py write --tables "^(iso_all_capacity_prices|ercot_as_prices|caiso_as_prices)$"; echo "exit=$?"

# 7. the Redivis draft (a draft only; releasing a version stays a human click)
python warehouse/redivis/upload.py --changed --dry-run; echo "exit=$?"
python warehouse/redivis/upload.py --tables iso_all_capacity_prices ercot_as_prices caiso_as_prices; echo "exit=$?"
python warehouse/redivis/upload.py --check-license; echo "exit=$?"

# 8. commit the metadata the steps above changed
python -m unittest tests.test_session65 > runs/session65/finish_tests.out 2>&1; echo "exit=$?"
git add warehouse/metadata docs/coverage.md
git commit -m "Session 65 finish: iso_all_capacity_prices, ercot_as_prices, caiso_as_prices merged, coverage, sources, the Redivis draft"

# 9. THE MERGE: this push runs the checks and, when they pass, merges the branch into main
git push origin task/065-revenue-stack

# 10. release the lock, and remove the wip branch once main holds the merge
python warehouse/lock.py release
git push origin --delete wip/065-revenue-stack
```

Expected in step 5: `iso_all_capacity_prices` internal, `ercot_as_prices` and `caiso_as_prices` public; I checked that `build_coverage.table_row` describes all three scratch tables that way. In step 7, `iso_all_capacity_prices` must go to the internal dataset only; `--check-license` fails if it is in the public one. **Do not run `warehouse/supabase/load.py` for these tables:** no live-set rule matches them (tested), and they stay out of Supabase until a later session wires them into a page.

If step 4 is run with `--offline` instead (no request at all), the CAISO line needs `--until 2026-10-03`, and the capacity line works only until the end of November 2026 (after that NYISO's next month page is not in the raw files).

## In plain words

**What capacity is paid is now in the warehouse, for the four markets that pay it apart from energy.** One new table, `iso_all_capacity_prices`, holds the auction clearing prices of PJM, NYISO, ISO-NE and MISO exactly as each publishes them, each in its own unit. ERCOT has no rows by design (energy-only), and California has none (no capacity market).

**What ancillary services pay is in the warehouse for ERCOT and CAISO.** Two new hourly tables of day-ahead clearing prices: ERCOT from 2018, CAISO from 2024-09-01.

**All three tables are complete, valid, and waiting in scratch directories.** Nothing is in `warehouse/output`, Supabase or Redivis yet. That is the finish step, above, and it is yours to start.

**Three things a person should know.**
- **Pushing the task branch is the merge.** The repository merges any passing `task/**` branch into main by itself. I pushed to `wip/065-revenue-stack` instead, so the demo was never at risk. See "To finish".
- **A flat 1 GW in New York City costs about a quarter more once capacity is counted, and ISO-NE about 5 percent more.** That narrows, but does not close, the gap session 62's draft shows between the Northeast and ERCOT. The table is under "Part E".
- **The real-time averages of September 2025 to August 2026 are probably a little low for NYISO and ISO-NE.** A few of the real-time days the hub history leaves out were stress days. The year session 64 added is not affected. See "D3".

**The checks you asked for.**
- **D1:** the no-pipes rule is in CLAUDE.md, and the loader now refuses to run on a coverage file that no longer describes the tables.
- **D2:** before this session the lock was per machine, not per session. Two sessions on the laptop could both pass the lock check. It is now per session.
- **D4:** the seller tab's two stale sentences now read their dates from the data.

## The pulls: rows against each ceiling

| Table | Rows | Ceiling | Window | Validator | Where |
|---|---|---|---|---|---|
| `iso_all_capacity_prices` | 814 | 5,000 | delivery periods 2007-06 to 2029-05 | pass, exit 0 | `runs/session65/iso_all_capacity_prices/` |
| `ercot_as_prices` | 335,972 | 500,000 | 2018-01-01 to 2026-10-02 (Central days) | pass, exit 0 | `runs/session65/ercot_as_prices/` |
| `caiso_as_prices` | 145,728 | 500,000 | 2024-09-01 to 2026-10-02 (Pacific days) | pass, exit 0 | `runs/session65/caiso_as_prices/` |

No pull came near its ceiling, and none was narrowed.

**The table name.** The prompt calls the capacity table `capacity_prices`. The naming rule needs three parts with the publisher first (Decision 19, the same finding as session 7), so it is `iso_all_capacity_prices`, with the market in the `market` column.

### Capacity prices, by market

| `market` | Rows | Entities | Period held | Unit, as published |
|---|---|---|---|---|
| `pjm_bra` (Base Residual Auction) | 234 | RTO and 17 delivery areas | delivery years 2007/2008 to 2028/2029 | USD/MW-day |
| `nyiso_icap_spot` (monthly spot auction) | 424 | NYCA, G-J Locality, NYC, LI | 2018-01 to 2026-10, every month | USD/kW-month |
| `isone_fca` (Forward Capacity Auction) | 26 | system-wide, or the zones as printed | FCA 1 to FCA 18 (commitment periods 2010/11 to 2027/28) | USD/kW-month |
| `miso_pra` (Planning Resource Auction) | 130 | zones 1 to 10 and the external zones | planning years 2024/25, 2025/26, 2026/27, by season | USD/MW-day |

Nothing is converted in the table. The conversion is in `docs/methods/capacity_and_ancillary.md`: USD/kW-month = USD/MW-day x 365 / 12 / 1000.

### ERCOT ancillary service prices

Day-ahead Market Clearing Price for Capacity, hourly, USD/MW-hour, from ERCOT's public reports (NP4-181-ER yearly files and NP4-188-CD daily files), the route the ERCOT price history already uses.

| Service | Hours held | From |
|---|---|---|
| Regulation Up, Regulation Down, Responsive Reserve, Non-Spin | 76,727 each | 2018-01-01 |
| ECRS | 29,064 | 2023-06-10, when ERCOT began buying it |

No day was left out. The prompt expected about 340,000 rows; there are 335,972.

### CAISO ancillary service prices

Day-ahead clearing prices from OASIS (report PRC_AS), hourly, USD/MW-hour, the two system regions only. 18,216 hours for each of the eight (region, service) series: 759 complete days.

- **Three days are not held:** 2025-04-06, 04-07 and 04-08. OASIS answers "no data returned" for them. They are gap rows in the run's status.
- **Where the price is:** in the expanded region (`caiso:AS_CAISO_EXP`). In the unexpanded system region, spinning and non-spinning reserve cleared at 0.00 in every hour held, and regulation almost always. A page should read the expanded region.
- **The pull:** one request per day, six seconds apart, in one process. OASIS did not throttle.

## Licenses, with the quoted terms

| Table | License | Terms |
|---|---|---|
| `ercot_as_prices` | public | ERCOT terms, item 5: "raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses" |
| `caiso_as_prices` | public | CAISO terms of use: materials "may be used by you provided that you keep intact all copyright, trademark and other proprietary notices and that you credit the California ISO" |
| `iso_all_capacity_prices` | **internal as a whole** | a table is internal if any of its sources is; each row carries its own license in `x_license` |

Per source in the capacity table:

| Source | Row license | Terms |
|---|---|---|
| PJM | internal | PJM's data license bars non-members from republishing (`docs/price-sources.md`, section 7). Its terms do not clearly allow redistribution, so the rows are internal, as the prompt ruled. Not guessed |
| ISO-NE | internal | "Any duplication of the Content or non-personal use may violate copyright, trademark, and other laws." |
| MISO | internal | "You are not permitted to modify, publish, transmit, participate in the transfer or sale of, reproduce, create derivative works of, distribute, publicly perform, publicly display or in any way exploit any of the materials or content" |
| NYISO | public, with a caution | public by the ERW's standing rule, but NYISO's legal notice grants no license: "Access to this Web site does not confer any license or ownership interest in either the form or content of the Web site" |

## What could not be pulled, and why

- **California's resource adequacy prices.** Not pulled. The CPUC publishes them as statistics in yearly PDF reports whose tables differ from year to year; each value would need checking against the document by a person. The methods doc says what a person would need to do. They would be yearly statistics of contract prices, not auction prices, and should be a table of their own.
- **MISO before planning year 2024/25.** MISO's own document list holds no results posting for 2021/22 to 2023/24. The 2019 and 2020 postings are there but are annual auctions with another page layout, and were not read. The history table inside the later postings merges cells and cannot be read reliably. One gap row.
- **MISO's external zones for Fall 2025 and Summer 2026.** The posting prints a range, not one price. Two gap rows, no estimate.
- **CAISO, three days in April 2025.** No data at the source.
- **Not attempted, by the prompt's scope:** PJM's incremental auctions, NYISO's strip and monthly auctions, ISO-NE's reconfiguration auctions, real-time ancillary prices, the other ISOs' ancillary markets.

**MISO's HTTP 403.** The link first used for the 2026/27 results answered 403. It was not worked around. MISO's own document list (the one its resource adequacy page reads) shows that the posting of 2026-04-28 was replaced by a corrected one on 2026-05-22, at another address; the old address is dead. The connector reads the corrected posting. Its page layout differs slightly (dollar signs on the prices, a footnote mark on the external-zone heading), and the parser now reads both layouts; the 2024 and 2025 postings parse to the same values as before.

## D1: gates are never piped

- **The rule** is CLAUDE.md non-negotiable 7.
- **The loader** (`warehouse/supabase/load.py`) now refuses to run when `coverage.csv` no longer describes the tables it would load: a table missing from coverage, a row count that differs, or a coverage row from another run than the file's own. It compares contents, not file times, so a table restored from Redivis still matches. The refusal comes before any write.
- **Tested** (`tests/test_session65.py`, class `Gates`), including a check that no gate in `run_daily.sh` or the workflows is piped.

## D2: was the data lock per session or per machine?

**Per machine.** Before this session the lock's token sat in one file per machine, `.erw/lock.json`, which every process on the machine read. While one session held the lock, any other session on the same laptop passed the lock check with the first session's token, and a release in either gave the lock up for both. The status named only the machine, so neither session could tell. That is how sessions 62, 63 and 64 each reported holding the lock while overlapping.

**Now per session.** The holder is `<machine>/<session>`, and each session keeps its token in its own file, `.erw/lock.<session>.json`. A second session on the same machine finds the lock held by the first, by name, and its writers refuse. A worker still passes its token to the task it starts through `ERW_LOCK_TOKEN`.

**Tested** (class `LockHolder`): two sessions on one machine; the second cannot pass the check, cannot take the lock, and cannot release the first one's.

## D3: are the dropped days stress days?

The real-time price of a left-out day is by definition not held, so the test uses the day-ahead price, which is held for all of them in NYISO and ISO-NE: each left-out day's day-ahead mean against the day-ahead mean of the kept days of the same month. Output: `warehouse/output/analysis_internal/dropped_rt_days.csv` and `dropped_rt_days_summary.csv` (internal, not a table).

| ISO | Year | Real-time days left out | Their day-ahead mean less the kept days' | Median | Share above the month's mean | Year's day-ahead mean, kept days less all days |
|---|---|---|---|---|---|---|
| ISO-NE | 2024-09 to 2025-08 (session 64) | 28 | -6.65 USD/MWh | -3.01 | 32% | +0.46 |
| NYISO | 2024-09 to 2025-08 (session 64) | 21 | -5.36 | -6.56 | 33% | +0.05 |
| ISO-NE | 2025-09 to 2026-08 (session 49) | 25 | +10.98 | +1.27 | 56% | -0.09 |
| NYISO | 2025-09 to 2026-08 (session 49) | 11 | +22.72 | +2.97 | 55% | -0.60 |
| CAISO | either year | 1 each | not testable: the day-ahead day is missing too (the autumn clock change) | | | 0 |

**The answer.**
- **The year session 64 added: no.** The 28 ISO-NE and 21 NYISO days it left out were cheaper than their months, not dearer. That year's real-time averages are not biased low; if anything they are a touch high, by under 0.5 USD/MWh.
- **The later year (September 2025 to August 2026): partly yes.** Most left-out days were ordinary, but a few were stress days: ISO-NE on 2026-02-03 (day-ahead 257.70 against 121.21 for the month) and 2025-12-09; NYISO on 2026-07-03 (252.94 against 72.20) and 2026-02-07. On the day-ahead evidence the real-time averages are likely low by about 0.1 USD/MWh for ISO-NE and 0.6 USD/MWh for NYISO over the year, and by 5 to 6 USD/MWh in the worst month (ISO-NE December 2025, NYISO July 2026).
- **This matters for session 62's draft,** whose year is the later one: NYISO's and ISO-NE's flat real-time costs there are, if anything, slightly understated. Real-time prices move more than day-ahead prices on stress days, so the true bias could be larger than these figures.

**A rule for partly complete days: recommended, not applied.**
1. Fill a hole in the 5-minute feed from the same ISO's own hourly real-time price where it publishes one (ISO-NE's final hourly real-time LMP, NYISO's time-weighted hourly LBMP). That is the publisher's number for the hour, not an estimate, and it would recover most of these days. Mark those hours in a column.
2. Keep a day that is still short when at least 23 of its 24 hours are complete, and write the missing hour as a gap row. A day with less stays out, as now.
3. Have every monthly average state the days it rests on, and flag a month in which a left-out day's day-ahead mean is more than 1.5 times the month's.

## D4: the seller tab's stale sentences

`site/app/cost-of-power/seller/page.tsx`: the first month and the count of months of the hubs outside ERCOT are computed from the snapshot's own months, so the two sentences cannot go stale again. Branch only; it ships with the finish step. The site builds on the branch, `tsc` passes, and the page lints clean.

## Part E: a flat 1 GW, energy next to capacity (internal, for review)

`warehouse/output/analysis_internal/energy_plus_capacity_1gw.csv`, built by `warehouse/derived/energy_plus_capacity_1gw.py`. September 2025 to August 2026. Nothing in session 62's draft was changed.

| Region | Capacity zone | Energy, USD | Capacity, USD | Sum, USD | Capacity share of the sum | Capacity per flat MWh |
|---|---|---|---|---|---|---|
| CAISO | none | 249,062,342 | not held | not held | | |
| ERCOT | none | 276,135,276 | not held | not held | | |
| ISO-NE | Rest of Pool, then system-wide | 616,431,496 | 31,089,000 | 647,520,496 | 4.8% | 3.55 |
| MISO | Zone 6 (Indiana) | 413,371,403 | 56,788,160 | 470,159,563 | 12.1% | 6.48 |
| NYISO | New York City | 601,033,917 | 159,030,000 | 760,063,917 | 20.9% | 18.15 |
| NYISO | NYCA (statewide) | 601,033,917 | 53,590,000 | 654,623,917 | 8.2% | 6.12 |
| PJM | RTO | not held | 103,971,800 | not held | | 11.87 |
| SPP | none | 268,289,073 | not held | not held | | |

**The conversions.**
- **Energy:** `flat_1gw_cost_usd` from `ai_power_regions`: the real-time flat hub price x 8,760 hours x 1,000 MW.
- **Capacity in USD/kW-month** (NYISO, ISO-NE): price x 1,000,000 kW, per month.
- **Capacity in USD/MW-day** (MISO, PJM): price x 1,000 MW x the days of the month.
- **The price that applied:** for each of the twelve months, the clearing price whose delivery period holds the month. ISO-NE: FCA 16 (Rest of Pool, 2.591) to May 2026, FCA 17 (system-wide, 2.590) from June. MISO Zone 6: 91.60 in fall, 33.20 in winter, 69.88 in spring, 424.30 in summer 2026. NYISO: the twelve monthly spot prices. PJM RTO: 269.92 to May 2026, 329.17 from June.
- **Capacity per flat MWh** is the year's capacity cost divided by 8,760,000 MWh.

**Why "not held".**
- **ERCOT:** energy-only by design; there is no capacity price.
- **CAISO:** no capacity market, and the CPUC's resource adequacy statistics were not pulled.
- **SPP:** no capacity market; resource adequacy is met bilaterally.
- **PJM energy:** PJM's hub prices are not in the warehouse, so there is no sum.

**What the table is and is not.** It is 1 GW of capacity bought at the auction price, a size. It is not a load's bill: that depends on the load's share of the peak and on the reserve requirement, and most capacity is self-supplied or contracted outside the auctions. The four markets also do not measure a megawatt of capacity the same way.

**What it says about session 62's first finding.** On energy alone, a flat 1 GW in New York City costs 2.18 times ERCOT's. With capacity it is 2.75 times ERCOT's energy figure, which already carries ERCOT's capacity cost. ISO-NE moves from 2.23 to 2.34 times, MISO from 1.50 to 1.70. The ranking does not change; the Northeast's distance from ERCOT grows.

## Tests and checks

- **`tests/test_session65.py`: 39 tests, pass.** Each connector's parsing on a saved real sample, the ceilings, the never-fill rule, the raw-file cache, D1 and D2.
- **Samples.** Real CAISO and ERCOT documents are in `tests/fixtures/session65/` (public sources). PJM's, ISO-NE's, MISO's and NYISO's documents are not copied into the public repository: their parsers are tested on the files in `warehouse/raw/` where a machine holds them, and skipped elsewhere (so those four tests are skipped on the GitHub runner). Their parsing rules are also tested on made-up markup.
- **All of `tests/`:** 297 tests, pass, exit 0 (`python -m unittest discover -s tests`, run after the last change).
- **The package tests:** 385 passed, exit 0 (the full file, run after the last change).
- **The site:** `npm run build` exit 0 and `npx tsc --noEmit` exit 0 on the branch. `npx eslint` over the whole site exits 1: 8 errors in source files this branch does not touch (for example `app/companies/CompaniesTable.tsx`) and the rest outside the source folders. The changed page lints clean (exit 0).
- **The validator:** each of the three tables passes, exit 0, in its scratch directory.
- **Docs and registrations on the branch:** `docs/methods/capacity_and_ancillary.md`; Decision 37 in `docs/datastandard.md` (the units USD/kW-month and USD/MW-hour); the three tables in `warehouse/metadata/sources.csv`, `build_coverage.py` and `package/llms.txt`; the chat spec re-exported to match.

## Errors, decisions and what moved

- **The raw-file cache missed every CAISO day (my error to find, fixed).** OASIS answers each PRC_AS request at a redirected address, and the cache was keyed on the address OASIS answered at, not the one asked for. So the first resumed run asked again for days already saved: about 29 of them before I saw it and stopped the run. Nothing was written twice. Fixed in two places: `iso_prices.fetch_raw` now lists a redirected answer under both addresses, and the CAISO connector also looks under the address OASIS answers at. After the fix, 99 saved days were reused at once. Tested.
- **A suspect file after the restart.** MISO's 2026 "PDF" in the raw folder was 111 bytes: the 403 error body. It was never treated as data (the cache only reuses HTTP 200 answers). Every other raw file of the session was checked against its manifest checksum after the restart, and the CAISO files again after the pause: none was bad.
- **The push target.** Decided without a person: `wip/065-revenue-stack`, because a push to `task/**` merges to main. Samuel then confirmed it.
- **Two package tests were failing before this session** (since sessions 62 and 64): one read "CC" from `lbnl_interconnection_queue`'s license line, one expected `event_window_daily` to hold the New York City zone. Both now follow the rules `build_coverage.py` itself applies. This changed tests only, no table.
- **The chat spec** (`site/lib/chat/spec.json`) is generated from `llms.txt`; it was re-exported after the briefing changed. No model call.
- **ISO-NE and MISO read as internal.** Their terms, quoted above, do not allow republishing, although the ERW treats their hub prices as public. I took the cautious reading for the new table and left the old ruling alone.
- **A cached "no data" answer is not asked for again.** CAISO's three empty days stay gaps on later runs unless their raw files are removed. If CAISO publishes those days later, delete the three files and rerun.
- **Not wired into the daily run.** The three connectors are not in `run_daily.sh` or the workflow. The prompt did not ask for it, and it would have changed what runs on main.
- **CHANGELOG.md was not updated:** it has not been kept since session 31.

## Not done

- The finish step (Part F), by instruction.
- California's resource adequacy prices and MISO before 2024/25, as above.
- The rule for partly complete real-time days: recommended only.
- Wiring the tables into the seller tab or the regional comparison: a later session, after the reviewer's feedback.

## For Samuel

1. **When to run "To finish".** Step 9 merges to main and deploys.
2. **ISO-NE and MISO: internal or public?** The capacity table reads their terms as internal; their hub prices are public in the ERW. One ruling should cover both.
3. **May NYISO's capacity rows be shown on their own?** Its legal notice grants no license in writing.
4. **Should the three tables refresh daily?** They are not in the daily run.
5. **D3's recommendation:** whether to recover the left-out real-time days from the ISOs' hourly real-time prices. It would change `iso_hub_prices_history` and everything built on it.
6. **Session 62's draft:** whether its first finding should say that the comparison is energy only, and cite the table above.

## Finish

Run on 2026-10-02, about 19:45 to 20:30 UTC, on Samuel's instruction, in the order of "To finish", one command at a time, each exit code read before the next. Every step exited 0; nothing was improvised. `warehouse/supabase/load.py` was not run. No model call, no force push.

| Step | Command | Exit | Result |
|---|---|---|---|
| 1 | `git checkout`, `git fetch origin`, `git merge origin/main` | 0, 0, 0 | already on the branch; main had nothing new ("Already up to date"), so no conflict |
| 2 | `lock.py acquire --task "session 65 finish" --minutes 120` | 0 | taken by `portable-laptop/45dfa531` (the session, as D2 now names the holder) |
| 3 | `scripts/sync.py` | 0 | 99 tables in coverage, 99 here and matching, 0 missing |
| 4 | `iso_capacity_prices.py` | 0 | `iso_all_capacity_prices` 814 rows |
| 4 | `ercot_as_prices.py` | 0 | `ercot_as_prices` 336,092 rows, to 2026-10-03 (one more delivery day than the scratch table: 120 rows) |
| 4 | `caiso_as_prices.py` | 0 | `caiso_as_prices` 145,728 rows, the same as the scratch table |
| 5 | `erw_validate.py --json warehouse/output/*.csv` | 0 | no table blocked |
| 5 | `build_coverage.py --reports ...` | 0 | 102 tables; the three new ones pass; `iso_all_capacity_prices` internal, the other two public; all tier source |
| 6 | `archive.py write --tables ...` | 0 | 3 tables archived, 482,634 rows, 0 failed (bucket `erw-archive`) |
| 7 | `upload.py --changed --dry-run` | 0 | nothing uploaded. It listed 74 changed tables and said it would refuse two rolling-window tables that are not this session's (`eia930_all_interchange`, `news_scores_shadow`: fewer rows here than last uploaded). I did not touch them |
| 7 | `upload.py --tables` (the three) | 0 | `iso_all_capacity_prices` 814 rows to `energy_research_warehouse_internal` only; `ercot_as_prices` 336,092 and `caiso_as_prices` 145,728 to the public dataset; Redivis counts equal the CSVs. Drafts only, nothing released |
| 7 | `upload.py --check-license` | 0 | 14 internal tables, 0 in the public dataset |
| 8 | `unittest tests.test_session65`; `git add`; `git commit` | 0, 0, 0 | 39 tests pass; commit `a6e3835` (coverage, sources, the archive manifest, the upload record) |
| 9 | `git push origin task/065-revenue-stack` | 0 | the workflow's checks passed (run 37060178167) and it merged the branch: main is at `e4debe2`, "Merge task/065-revenue-stack: checks passed", and holds `a6e3835` |
| 10 | `lock.py release` | 0 | "the data lock is free" |
| 10 | `git push origin --delete wip/065-revenue-stack` | 0 | removed, after checking that main holds every commit on it. The workflow had already deleted the remote task branch |

**The production deploy and the live page.** I could not read the deploy's status from Vercel or GitHub directly (no `gh` or `vercel` command on this machine, and GitHub's public API answered "rate limit exceeded"). The evidence that the deploy succeeded is the live page itself: `https://erw-flame.vercel.app/cost-of-power/seller?iso=miso` answers 200 and now reads "the warehouse holds MISO's hub prices from September 2024 only" and "The other hubs' prices start in September 2024: 25 months is a short sample of weather and gas, not a distribution." Neither "September 2025 only" nor "twelve or thirteen months" is on the page any more. The new wording exists only in this branch, so the page is served by the merged code.

**Left for a person.**
- Releasing the Redivis versions: both datasets hold the new tables in their drafts only.
- The two tables the dry run would refuse (`eia930_all_interchange`, `news_scores_shadow`): this machine holds fewer rows than the last upload. The daily run will meet the same refusal if it runs here; it is worth a look before the next upload from this laptop.
- This "Finish" section is committed on the local branch `task/065-revenue-stack` only. It is not pushed: a push to a `task/` branch would run the merge and a production deploy again. It reaches main with the next session's merge, or with a push when you choose.

