# Session 126 report: the cleanup, and demand growth with the weather taken out

## Decide before 14:00 UTC on 6 October

**Tomorrow's daily run will stop at its first step unless one test on main is changed.** `tests/test_session124.py` on main holds a count as exactly 2,732. The file it reads, `site/public/network/daily_index.json`, is rebuilt by the daily run, and today's run (commit `8716c93`) rebuilt it with 2,734. So main's test now fails against main's own file (`AssertionError: 2734 != 2732`; I ran it on a clean copy of main). The daily workflow runs the tests first and takes the lock only if they pass.

- **If nothing is done:** no daily run on 6 October. No refresh of the daily tables, no digest. The live pages stay as they are but for the 15-minute prices and the hourly network, which under a freeze may be what you want. The first run after the fix pulls the last three days.
- **The fix is ready and is not landed**, because landing is a push that deploys and the freeze is yours to lift. It is one commit on main's head, a test only (`eb86006`, branch `wip/126-daily-run-test`): the count must be above 2,500 and no less than the pair-days confirmed, which holds on any day. On a clean copy of main with this one commit, the workflow's own command (`python -m unittest discover -s tests`) ran 1,268 tests: OK, 174 skipped (that copy holds no tables and no keys). To land it:

  ```bash
  node site/scripts/snapshot-live.mjs take before-126t
  git push origin wip/126-daily-run-test:task/126-daily-run-test
  python runs/session118/watch_run.py task/126-daily-run-test 15
  node site/scripts/snapshot-live.mjs take after-126t && node site/scripts/snapshot-live.mjs compare before-126t after-126t
  git push origin --delete wip/126-daily-run-test
  ```

  It changes no page and no table. It is still a deploy, so I did not make it.

## To finish

**The freeze is on** (`REVIEW_FREEZE`, 5 to 6 October; `python scripts/freeze.py status` exits 1). This session pushed `wip/` branches only, deployed nothing and loaded no table a live page reads. Everything below waits for the freeze to end.

`wip/126-demand-weather` is built on `wip/125-contracts`, so landing it lands session 125's last commits too (its step 4). When `python scripts/freeze.py status` exits 0:

```bash
git checkout wip/126-demand-weather && git fetch origin && git merge origin/main     # the daily runs' commits
node site/scripts/snapshot-live.mjs take before-126
git push origin wip/126-demand-weather && git push origin wip/126-demand-weather:task/126-demand-weather
python runs/session118/watch_run.py task/126-demand-weather 15                        # the checks, then the merge
node site/scripts/snapshot-live.mjs take after-126 && node site/scripts/snapshot-live.mjs compare before-126 after-126
MSYS_NO_PATHCONV=1 node site/scripts/check-review-pages.mjs https://erw-flame.vercel.app /demand/weather "/demand/weather?figure=night&year=2025"
cd site && node --import ./scripts/alias-loader.mjs scripts/check-demand-weather.mjs https://erw-flame.vercel.app && cd ..
git push origin --delete wip/126-demand-weather wip/125-contracts wip/124-network-v3   # once all three are on main
```

- **If the merge conflicts**, it will be in the generated metadata the daily run rewrites (`docs/coverage.md`, `warehouse/metadata/coverage.csv`, `sources.csv`, `archive_manifest.csv`, `redivis_uploads.csv`). Take main's copy of each, then, under the lock, run the last three steps again for this session's four tables and session 125's four (the tables are on this machine):

  ```bash
  T='^(noaa_grid_weather_(stations|hourly|daily)|eia930_demand_weather|ferc_eqr_(contracts_history|contract_terms|party_mw|quarter_changes))$'
  python warehouse/lock.py run --task "session 126: coverage after the merge" --minutes 30 --wait 15 -- bash -c ".venv/Scripts/python.exe warehouse/metadata/build_coverage.py --only '$T' && .venv/Scripts/python.exe warehouse/archive/archive.py --tables '$T' write"
  ```

- **What the comparison should show on the live pages: nothing but the clock.** The page is `review`; its four tables are under `catalogue_hold` and its three sources under `sources_hold` (`warehouse/supabase/live_set.yaml`), so the home page's counts and `/terms` do not move; it is not in the menu (adding it would change the menu on every live page: yours to decide when it opens). The one page that gains a line is `/demand`, in review. The holds are tested (`tests/test_session126.py`, with session 102's); they are not proven on a deployed site, because nothing was deployed.
- **Not done, on purpose:** the weather tables are not in the daily run. Bringing them up to date asks NOAA for about 560,000 rows each time (35 stations from July 2025). That is a standing pull, and needs your approval and a budget.

## Read these first

1. **The daily run changed live pages during the freeze.** Between session 125's last snapshot (15:32 UTC) and 17:04 UTC: **179 differences**, none from this session. `/` 48 (the price board and table ages), `/storage` 66 (a newer day of the daily cycle), and 5 on each of the 13 battery pages (October's row gained a day, with its energy, ancillary and total). The run of 14:00 UTC loaded its tables at 15:23 and its two commits deployed at 16:20 and 16:29. Scheduled jobs do not read the freeze file. Whether a freeze should stop them is yours to rule; the place to do it is the daily workflow and Vercel's ignored-build rule.
2. **One figure on a live page looks wrong.** `/storage` now shows the Lower 48's batteries on 3 October discharging 54,505 MWh against 30,236 MWh charged, a ratio of 1.80. A battery fleet does not return more than it takes. I changed nothing (the freeze); it is `storage_daily_cycle`, from the daily run.
3. **Two live tables are whole, though the run recorded them as failed**, and tomorrow's run will be long again (answer b below).
4. **NOAA's hourly database ended on 27 August 2025.** "2019 to today" needed a second NOAA product for the last thirteen months; the two were checked against each other hour by hour at every station (below). The newest hour NOAA serves is 28 September 2026.
5. **The population weights are stated, not retrieved.** The warehouse holds no population table and the one approved pull was NOAA's, so I did not ask the Census Bureau for one. The rule and the weights are below; the year's energy does not rest on them (at most 1.2 points with equal weights), the peaks do. This is the first thing to settle before the page opens.

## Part one: the cleanup's three answers

### a. Session 125's write steps: done

The lock was free at 16:57 UTC. `runs/session125/finish_writes.sh` ran under it from 16:58: all eight steps exit 0.

| | Now |
|---|---|
| `ferc_eqr_contracts_history` | 571,115 rows, three quarters (190,816 + 190,249 + 190,050) |
| `ferc_eqr_contract_terms`, `ferc_eqr_party_mw`, `ferc_eqr_quarter_changes` | 186,873, 812 and 68 rows (the last was 28 with two quarters) |
| Validator, coverage, archive, Redivis draft (internal dataset) | pass; built; written; 5 of 5 uploads counted equal, nothing released |
| Commit | `6ad43e1` on `wip/125-contracts`, pushed |
| The page's stored summary (step 3) | stored at 17:04:40 UTC, with all four quarters |

- **The four-quarter figures equal session 125's trial exactly**: 67,680, 67,914, 68,981 and 70,277 contracts in force; new 11,863, 12,201, 13,561; gone 11,629, 11,134, 12,265; kept 56,051, 56,780, 56,716. Its report said a difference would be a fault; there is none.
- **The summary load touched no live page**: snapshots at 17:04:04 and 17:04:47 UTC, 25 pages, **0 differences**.
- **Four requests went to FERC**, two for each quarter's list of filings, as the command in session 125's report says (9.1 MB and 8.6 MB of file directory; no filing was fetched, the contract rows came from disk). Your rule was "no pull but NOAA's". I ran the command as you listed it and am telling you it is not silent.
- Step 4, landing the branch, waits for the freeze (above).

### b. The daily run of 14:00 UTC: it finished; nothing was left behind

- **It finished.** Run 37321169760: lock taken 14:03:53, its "daily run" step ended 16:18:51 (8,098 seconds, 135 minutes; 85 minutes on 3 October, 80 on 4 October), lock released by its own step at 16:18:59, job ended 16:27:53. `erw_health` records the step as ok.
- **The lock is free** and was free when I first looked (16:57). No lock was left by a dead run, so I released nothing. It is free now.
- **What ran long: two stretches, not one step.**

  | Stretch | 5 October | 4 October |
  |---|---|---|
  | The pulls, from the first connector to the reserve prices | 14:07:34 to 15:08:35, 61 minutes | 14:06:02 to 14:43:52, 38 minutes |
  | of which EIA's series | 11.0 minutes | 7.3 minutes |
  | of which from the generator inventory to the policy sources | 28.8 minutes | 11.6 minutes |
  | From the last derived table to the end (validator, coverage, archive, loader, digest, Redivis) | 15:15:28 to 16:18:51, 63 minutes | 14:46:22 to 15:23:00, 37 minutes |

  - The 29 minutes hold Monday's work: the queues, the large-load list and the project list ran (they did not on Sunday), and the weekend's news came in at once (437 new stories; 400 scored, and 400 again by the shadow scorer). The log does not time each of them.
  - The loader's rows carry `loaded_at` 15:23:51, so the validator, coverage and archive took about 8 minutes and the loader, digest, status and Redivis about 55. **The loader rewrote every row of two large tables**: `ercot_as_prices` (336,332 rows) and `ercot_hub_prices_daily` (345,306). Every row of both carries today's stamp, and the database grew from 971.0 MB to 1,127.2 MB.
  - Why every row (my reading, not measured): on 4 October the reserve-price connector failed (ERCOT's file was a workbook, not the CSV it expects), so today's run built that table from nothing, with new retrieval stamps on every row.
- **The loader then recorded both tables as FAILED, and they are whole.** After writing, its count of each came back from Supabase as HTTP 500 ("JSON could not be generated"). I counted them: 336,332 and 345,306 rows in the live set, the same as the files. But the catalogue's hash for both is empty, so **tomorrow's run will write both again, whole**, and again each day until the count succeeds. Expect another long run tomorrow. `ercot_as_prices` is read by the live battery page.
- **How I know, and what I do not:** the run's log is of no use for timing (its output arrives in four blocks, at 14:07, 15:08, 15:18 and 16:18). The times above are from each connector's own run-log name, `erw_health`, and the rows' `loaded_at`. I cannot split the last 55 minutes between the loader and Redivis.
- **What else failed inside a run recorded as ok** (from its log): ISO New England's real-time hourly prices (no complete day, 2 and 3 October empty at the source); `grid_network` (`'bool' object has no attribute 'get'`, the same error as on 4 October); the three known gaps (CARB's auction file, NYISO's queue, ERCOT's large-load list); **Monday's digest was not written** (`duplicate items in the brief`, the headline "exemptions from materials licensing"), nor the shadow digest; `STATUS.md` was not rebuilt (`eia930_all_interchange` holds two columns the reader does not expect, `ba` and `x_to_ba`); and one package test (`test_large_table_by_partition[ercot_dam_esr_awards]`).
- **The three things session 125 could not read.** The new alert step ran and sent one line, naming the package test only: the failures above sit inside a step recorded as ok, so the alert does not see them. The network's daily builder with session 124's code: `network_replay` ok in 13 seconds. The digest: not written; `news_email` is in the run's ok list all the same, and I did not establish what it sent.

### c. Vercel: what is visible from outside

- **GitHub's records do not show that Vercel built none of the merges after 12:50 UTC.** They show one merge with no deployment at all, and four built after it:

  | Commit on main | Merged, UTC | GitHub's record of Vercel |
  |---|---|---|
  | `83d4559` task/123 | 12:12:16 | Production, success, 12:14:21 |
  | **`e511e2e` task/124-network-v3** | **12:49:56** | **none: no status, no deployment** |
  | `b2f09c5` task/125-contracts | 13:44:26 | Production, success, 13:46:10 |
  | `c0bab7d` the freeze file | 15:05:42 | Production, success, 15:07:10 |
  | `8716c93` the daily run | 16:18:55 | Production, success, 16:20:41 |
  | `bbc2fea` the health summary | 16:27:49 | Production, success, 16:29:26 |

  Every commit on a `wip/` or `task/` branch reads "Canceled by Ignored Build Step", which is the rule working.
- **Production serves `8716c93` or later.** The site ships one static file that the daily commit changed: `/network/daily_index.json`, fetched from production at 17:03 UTC, is byte for byte the file of `8716c93` and of `bbc2fea` (SHA-256 `91defd47...`), and not the file of `c0bab7d`, `b2f09c5` or `e511e2e` (`37401f2b...`). `bbc2fea` changed nothing the site serves, so from outside the two cannot be told apart; GitHub's record says `bbc2fea`. `/network/v3` (session 124's page) answers 200 on production.
- **The site has no build stamp that names a commit.** The build writes a time into its content file and no page shows it. A commit hash in the footer or at one address would have answered this question in one request.
- **Three things to look at in Vercel's Deployments tab:**
  1. **12:49 to 13:46 UTC: is there any row for `e511e2e`?** Missing, canceled, or queued and then replaced by the next build. It is the only merge of the day with no record. Its code went live with `b2f09c5`.
  2. **Which deployment is marked Current for Production.** It should be `bbc2fea`, 16:29 UTC. If an older one is pinned (a rollback or a manual promotion), later builds succeed and are not served; what I fetched says that is not so now.
  3. **The two deployments of 16:20 and 16:29, inside the freeze.** They are the daily run's commits. If a freeze should hold production still, the ignored-build rule is where to say it.

  I changed nothing on Vercel and did not open its dashboard.

## Part two: demand growth with the weather taken out

**Built:** a NOAA connector and three weather tables; one derived table; the review page `/demand/weather` in the shared components; a method written from the build's own numbers; 37 tests on saved real samples. All four tables pass the validator, are in coverage, archived and in the Redivis draft (row counts equal). No model call. No pull but NOAA's.

**Verdict: not ready to open.** The numbers for the year's energy and the overnight minimum are solid enough to read. The weights need a real population table, the peaks rest on those weights, and California's fit is too weak to say much. What is left is at the end.

### The pull

| | |
|---|---|
| Rows read from NOAA | **2,770,528** of the 3,000,000 ceiling, USD 0 |
| Stations | 35, five a grid, United States only |
| Hours | 1 January 2019 to 28 September 2026 13:00 UTC, 67,862 a station |
| To 31 July 2025 | ISD-Lite, NOAA's hourly cut of the Integrated Surface Database (one row an hour) |
| From 1 August 2025 | Local Climatological Data, version 2, through NOAA's data service (every report; times moved from local standard time to UTC; the same rule for an hour) |

- **Why two products.** NOAA's database stops on 27 August 2025: its station list gives that day as every station's last, its 2025 files were last written on 29 August 2025, and it has no file for 2026. I did not find that out until the station list was on the screen.
- **The seam is checked, not assumed.** Both products were read from 1 July 2025 to the end of the first, and compared hour by hour at every station before anything was written. Outside the eight synoptic hours of the day, every station agrees to a tenth of a degree Celsius in at least 99.89 percent of hours. At the synoptic hours 34 of 35 agree in more than 99 percent; Austin agrees in 28.6 percent, because the first product takes a synoptic report there that the second does not carry (0.1 C on average over all hours). A station under 90 percent stops the build.
- **Counted against the ceiling and not used:** my trial reads to choose the product (29,558 rows), one cut-off answer and the probes that explained it (5,393 rows). All are in the 2,770,528.
- **NOAA's terms, quoted** (the full text is in the method). NOAA's record for the database names no license. It says: "Cite as: NOAA National Centers for Environmental Information (2001): Global Surface Hourly [indicate subset used]", and two statements of liability ("NOAA and NCEI cannot provide any warranty as to the accuracy, reliability, or completeness of furnished data"). Its readme holds the one restriction: "The non-U.S. data in ISD are subject to WMO Resolution 40 restrictions, and cannot be redistributed to other users or customers." All 35 stations are in the United States. The second product's record has the same liability words and its own citation (Kantor and others, 2023, doi 10.25921/96dw-mb77). **The words "public domain" are the National Weather Service's about its own pages, not these two records'.** I registered both sources as `public`, as the warehouse has held NOAA's database since session 49, and the tables carry both citations. Public domain was expected, and nothing contradicts it; nothing on these two records says it in those words either. A person should confirm.

### The stations

**The rule.** For each grid, the five most populous metropolitan areas whose principal city the grid operator serves; for each, the principal airport's station; the weight is the area's share of the five areas' population, to the nearest twentieth.

**The weights are stated, not retrieved.** They are set from the 2020 Census counts of metropolitan areas as generally known, the way session 60 stated California's three, and rounded to twentieths so that a count wrong by a few percent gives the same weight. No population figure is written to any table. Station identifiers, names and positions are NOAA's own.

| Grid | Airport | NOAA station | Stands for | Weight | Measured | Interpolated | Missing | Longest gap, h |
|---|---|---|---|---|---|---|---|---|
| ERCOT | DFW | 722590-03927 | Dallas-Fort Worth-Arlington | 0.35 | 67,680 | 80 | 102 | 91 |
| ERCOT | IAH | 722430-12960 | Houston-The Woodlands-Sugar Land | 0.35 | 67,720 | 45 | 97 | 90 |
| ERCOT | SAT | 722530-12921 | San Antonio-New Braunfels | 0.15 | 67,699 | 40 | 123 | 90 |
| ERCOT | AUS | 722540-13904 | Austin-Round Rock-Georgetown | 0.10 | 67,637 | 117 | 108 | 91 |
| ERCOT | MFE | 722506-12959 | McAllen-Edinburg-Mission | 0.05 | 67,573 | 109 | 180 | 91 |
| CAISO | LAX | 722950-23174 | Los Angeles-Long Beach-Anaheim | 0.50 | 67,695 | 60 | 107 | 90 |
| CAISO | SFO | 724940-23234 | San Francisco-Oakland-Berkeley | 0.15 | 67,670 | 60 | 132 | 90 |
| CAISO | ONT | 747040-03102 | Riverside-San Bernardino-Ontario | 0.15 | 67,673 | 69 | 120 | 91 |
| CAISO | SAN | 722900-23188 | San Diego-Chula Vista-Carlsbad | 0.10 | 67,678 | 58 | 126 | 90 |
| CAISO | SJC | 724945-23293 | San Jose-Sunnyvale-Santa Clara | 0.10 | 67,610 | 87 | 165 | 90 |
| NYISO | LGA | 725030-14732 | New York-Newark-Jersey City (the part in New York State) | 0.80 | 67,700 | 61 | 101 | 90 |
| NYISO | BUF | 725280-14733 | Buffalo-Cheektowaga | 0.05 | 64,280 | 3,485 | 97 | 90 |
| NYISO | ROC | 725290-14768 | Rochester | 0.05 | 64,319 | 3,425 | 118 | 90 |
| NYISO | ALB | 725180-14735 | Albany-Schenectady-Troy | 0.05 | 67,690 | 71 | 101 | 90 |
| NYISO | SYR | 725190-14771 | Syracuse | 0.05 | 67,680 | 61 | 121 | 90 |
| ISO-NE | BOS | 725090-14739 | Boston-Cambridge-Newton | 0.50 | 67,611 | 154 | 97 | 90 |
| ISO-NE | PVD | 725070-14765 | Providence-Warwick | 0.15 | 67,579 | 128 | 155 | 90 |
| ISO-NE | BDL | 725080-14740 | Hartford-East Hartford-Middletown | 0.15 | 67,697 | 64 | 101 | 90 |
| ISO-NE | ORH | 725100-94746 | Worcester | 0.10 | 67,571 | 102 | 189 | 90 |
| ISO-NE | BDR | 725040-94702 | Bridgeport-Stamford-Norwalk | 0.10 | 67,388 | 147 | 327 | 90 |
| PJM | ORD | 725300-94846 | Chicago-Naperville-Elgin | 0.35 | 67,687 | 62 | 113 | 90 |
| PJM | DCA | 724050-13743 | Washington-Arlington-Alexandria | 0.25 | 67,687 | 72 | 103 | 90 |
| PJM | PHL | 724080-13739 | Philadelphia-Camden-Wilmington | 0.20 | 67,684 | 58 | 120 | 90 |
| PJM | BWI | 724060-93721 | Baltimore-Columbia-Towson | 0.10 | 67,718 | 47 | 97 | 90 |
| PJM | PIT | 725200-94823 | Pittsburgh | 0.10 | 67,710 | 45 | 107 | 90 |
| MISO | DTW | 725370-94847 | Detroit-Warren-Dearborn | 0.30 | 63,829 | 3,918 | 115 | 91 |
| MISO | MSP | 726580-14922 | Minneapolis-St. Paul-Bloomington | 0.25 | 67,600 | 129 | 133 | 90 |
| MISO | STL | 724340-13994 | St. Louis | 0.20 | 67,627 | 113 | 122 | 90 |
| MISO | IND | 724380-93819 | Indianapolis-Carmel-Anderson | 0.15 | 67,715 | 50 | 97 | 90 |
| MISO | MKE | 726400-14839 | Milwaukee-Waukesha | 0.10 | 67,688 | 61 | 113 | 90 |
| SPP | MCI | 724460-03947 | Kansas City | 0.35 | 67,701 | 53 | 108 | 91 |
| SPP | OKC | 723530-13967 | Oklahoma City | 0.25 | 67,686 | 53 | 123 | 90 |
| SPP | TUL | 723560-13968 | Tulsa | 0.15 | 67,670 | 70 | 122 | 90 |
| SPP | OMA | 725500-14942 | Omaha-Council Bluffs | 0.15 | 67,557 | 183 | 122 | 90 |
| SPP | ICT | 724500-03928 | Wichita | 0.10 | 67,655 | 79 | 128 | 90 |

- "Interpolated" is a run of one, two or three missing hours between two measured ones, filled on a straight line and counted. A longer run stays missing. In all: 13,416 station-hours interpolated and 4,390 left missing, of 2,375,170.
- **Every station lacks about 90 hours from 30 August to 2 September 2025**: the second product holds no report for any of them over those four days, the first after NOAA's database ended. No grid has weather then.
- Buffalo, Rochester and Detroit lack an hour or a few on most days in the first product, at the same hours of the clock; those are the interpolated thousands.
- **Minneapolis is the one exception to the two-product rule.** From April 2020 to November 2022 the first product keeps little more than one hour in six for it in the warm months (8,276 hours missing), while the second holds its hourly report for every one of those hours. That stretch is read from the second product for that station (125,199 rows): 23,365 hours held against 12,464, agreeing in 99.82 percent of the 12,456 hours both hold. Without it MISO would have lost the summers of the fit.
- A grid's hour is used only when all five stations hold it. Each grid holds between 99.34 percent (New England) and 99.81 percent of its hours.
- **Left out by the rule:** the New Jersey half of the New York area (PJM's); Sacramento; MISO's southern states (New Orleans would be sixth); west Texas, where much of ERCOT's new load is.

### The fit's error by grid

On 2019 to 2021, for each grid: 48 lines (24 hours of the day, weekday or weekend), demand against heating and cooling degrees, their squares, and their averages over the day before. Heating and cooling have their own terms. Only hours that pass session 118's rule are used. Texas's hours of 15 to 19 February 2021 are left out of the fit (120 hours): the grid was shedding load.

"Left out" means: each of 2019, 2020 and 2021 predicted by a fit made on the other two. Mean absolute error, percent.

| Grid | Hours in the fit | Error on an hour left out, percent | On a day left out | On the hours fitted | 2019, 2020, 2021 left out |
|---|---|---|---|---|---|
| ERCOT | 26,119 | 4.2 | 3.8 | 3.5 | 3.7, 3.7, 5.2 |
| CAISO | 26,236 | 7.1 | 6.2 | 6.6 | 7.5, 7.2, 6.5 |
| PJM | 26,285 | 3.8 | 3.3 | 3.5 | 3.2, 4.5, 3.6 |
| MISO | 26,286 | 3.8 | 3.4 | 3.5 | 3.7, 4.6, 3.3 |
| SPP | 26,287 | 3.7 | 3.2 | 3.6 | 3.7, 4.3, 3.2 |
| NYISO | 26,290 | 4.2 | 3.8 | 3.9 | 4.1, 4.8, 3.7 |
| ISO-NE | 26,192 | 5.5 | 4.6 | 5.2 | 5.1, 6.2, 5.1 |

- California's fit is much the weakest. Its metered demand depends on sunshine on rooftops, which temperature at five airports does not carry, and three of its five airports are on the coast.
- The error left out is close to the error fitted, so the fit is limited by what it leaves out (humidity, sunshine, the calendar), not by overfitting.

**The check where the answer is known.** Growth not explained by temperature in a year the fit had not seen, the year's energy, percent:

| Grid | 2019 left out | 2020 left out | 2021 left out |
|---|---|---|---|
| ERCOT | -2.5 | -1.4 | +4.1 |
| CAISO | -2.0 | -0.6 | +3.0 |
| PJM | +0.9 | -2.6 | +1.6 |
| MISO | +2.3 | -2.6 | +0.2 |
| SPP | +0.6 | -1.5 | +0.8 |
| NYISO | +2.8 | -2.7 | -0.2 |
| ISO-NE | +1.1 | -0.9 | -0.4 |

- **New England, whose demand was flat, comes back within 1.1 points in each of the three years; SPP within 1.5.**
- **2020 comes back below zero in all seven grids** (from -0.6 to -2.7): the year of the lockdowns. The method finds it without being told.
- Texas's 2021 comes back at +4.1, which reads as growth already under way inside the fit's own years. The base of 2019 to 2021 is not a still one.
- **The uncertainty of a figure is the largest of its three misses**, so it holds the lockdowns too. That makes it wide on purpose. It is also rough: three numbers, and the largest of them. A peak is one hour, so its uncertainty is never taken as less than the fit's error on one hour.

### Growth explained and not explained, by grid and year

Percent of the mean of 2019 to 2021. Each cell reads: growth = the part temperature explains, and the part it does not. **Bold** is a finding: larger than its uncertainty ("give or take"). 2026 is 1 January to 27 September, against the same days of 2019 to 2021. "(beyond)": the peak hour was hotter or colder than any hour of 2019 to 2021, the fit is reaching, and the figure is not called a finding.

**The year's energy** (the mean of the year's hours)

| Grid | Give or take | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|
| ERCOT | 4.1; 3.8 for 2026 | +11.7 = +4.4 and **+7.4** | +16.0 = +3.0 and **+13.0** | +20.0 = +2.1 and **+17.9** | +26.5 = +2.7 and **+23.8** | +32.8 = +4.0 and **+28.8** |
| CAISO | 3.0; 3.5 for 2026 | +3.1 = +0.6 and +2.4 | +0.5 = -2.1 and +2.6 | +3.0 = -1.8 and **+4.8** | +2.9 = -1.9 and **+4.8** | +8.6 = +2.6 and **+6.0** |
| PJM | 2.6; 3.1 for 2026 | +2.8 = +1.0 and +1.8 | -0.4 = -2.6 and +2.2 | +3.1 = -0.6 and **+3.7** | +7.2 = +0.4 and **+6.8** | +10.1 = +1.1 and **+8.9** |
| MISO | 2.6; 2.7 for 2026 | +2.4 = +1.2 and +1.2 | +0.4 = -1.1 and +1.5 | +1.0 = -0.8 and +1.9 | +4.1 = +0.5 and **+3.6** | +6.8 = +0.9 and **+5.9** |
| SPP | 1.5; 1.3 for 2026 | +6.1 = +2.9 and **+3.2** | +5.4 = -0.1 and **+5.5** | +8.7 = +0.1 and **+8.6** | +12.7 = +0.2 and **+12.5** | +17.5 = +3.3 and **+14.1** |
| NYISO | 2.8; 3.3 for 2026 | +0.1 = +0.3 and -0.2 | -3.6 = -2.4 and -1.2 | -1.3 = -1.1 and -0.2 | -0.5 = -0.3 and -0.1 | -1.2 = +0.9 and -2.1 |
| ISO-NE | 1.1; 1.2 for 2026 | +0.0 = +0.4 and -0.4 | -4.2 = -2.3 and **-1.9** | -2.4 = -0.9 and **-1.5** | -1.3 = -0.2 and -1.1 | +0.5 = +1.4 and -0.9 |

**The overnight minimum** (the mean over the year's days of the lowest hour from midnight to 6 am, local)

| Grid | Give or take | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|
| ERCOT | 4.8; 4.3 for 2026 | +13.5 = +3.8 and **+9.7** | +18.3 = +1.8 and **+16.4** | +23.2 = +1.1 and **+22.1** | +30.9 = +1.5 and **+29.4** | +38.4 = +3.2 and **+35.2** |
| CAISO | 4.3; 4.7 for 2026 | +5.1 = +1.0 and +4.1 | +4.9 = -0.6 and **+5.6** | +4.2 = -1.0 and **+5.2** | +3.5 = -0.9 and **+4.4** | +6.7 = +1.8 and **+4.9** |
| PJM | 2.3; 2.8 for 2026 | +4.3 = +1.1 and **+3.2** | +1.1 = -3.0 and **+4.1** | +4.5 = -1.4 and **+5.9** | +10.0 = +0.6 and **+9.4** | +13.7 = +1.1 and **+12.5** |
| MISO | 2.3; 2.5 for 2026 | +3.6 = +1.2 and **+2.4** | +1.2 = -1.6 and **+2.9** | +2.2 = -1.6 and **+3.8** | +5.3 = +0.5 and **+4.8** | +8.5 = +0.6 and **+7.9** |
| SPP | 2.3; 1.9 for 2026 | +6.6 = +2.5 and **+4.1** | +5.6 = -0.9 and **+6.5** | +9.6 = -0.9 and **+10.5** | +15.5 = -0.2 and **+15.7** | +20.4 = +1.9 and **+18.5** |
| NYISO | 1.9; 2.4 for 2026 | +1.8 = +0.4 and +1.4 | -1.6 = -2.4 and +0.9 | +1.6 = -1.4 and **+2.9** | +3.8 = -0.4 and **+4.1** | +4.1 = +1.1 and **+3.0** |
| ISO-NE | 1.2 | +2.0 = +0.1 and **+2.0** | -1.4 = -2.3 and +0.9 | +2.3 = -1.1 and **+3.3** | not held | not held |

**The summer peak** (the highest hour of June to September)

| Grid | Give or take | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|
| ERCOT | 6.6 | +7.8 = +7.0 and +0.8 (beyond) | +15.4 = +11.6 and +3.8 (beyond) | +15.5 = +4.3 and +11.3 (beyond) | +12.9 = +0.2 and **+12.7** | +23.0 = +7.3 and +15.7 (beyond) |
| CAISO | 9.9 | +14.3 = +14.3 and -0.0 | -1.6 = -6.4 and +4.9 | +6.4 = +2.0 and +4.5 | -1.9 = -5.6 and +3.8 | +11.8 = +14.8 and -3.0 |
| PJM | 4.4 | -0.4 = -1.0 and +0.6 | -1.0 = +3.3 and -4.3 | +2.7 = +2.0 and +0.6 | +7.7 = +10.1 and -2.4 (beyond) | +9.1 = +10.8 and -1.8 (beyond) |
| MISO | 3.8 | +1.6 = +0.6 and +0.9 (beyond) | +5.4 = -0.9 and **+6.3** | +3.5 = -0.2 and +3.8 (beyond) | +5.0 = +4.8 and +0.2 | +6.0 = +2.9 and +3.2 (beyond) |
| SPP | 3.7 | +6.0 = +3.9 and +2.1 (beyond) | +12.0 = +6.5 and +5.5 (beyond) | +8.5 = +1.9 and **+6.5** | +8.8 = +0.0 and **+8.8** | +15.9 = +8.1 and +7.7 (beyond) |
| NYISO | 4.2 | -0.5 = -0.8 and +0.3 | -1.5 = -5.1 and +3.6 | -5.4 = -5.7 and +0.2 | +3.9 = +1.4 and +2.5 (beyond) | +1.4 = +6.8 and **-5.4** |
| ISO-NE | 5.5 | -1.5 = -2.9 and +1.5 | -4.5 = -11.4 and **+6.9** | -1.4 = -5.6 and +4.3 | not held | +2.8 = +9.2 and -6.3 (beyond) |

**The winter peak** (the highest hour of December of the year before to February)

| Grid | Give or take | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|
| ERCOT | 36.7 | +9.8 = -8.4 and +18.2 | +18.0 = +5.9 and +12.1 | +24.7 = +5.9 and +18.8 | +27.9 = -1.7 and +29.6 | +20.6 = -1.2 and +21.8 |
| CAISO | 7.1 | +4.2 = +2.0 and +2.3 | +0.3 = -8.5 and **+8.8** | -3.5 = -16.5 and **+13.1** | +0.0 = -4.4 and +4.4 | +2.8 = +1.4 and +1.4 |
| PJM | 7.6 | +8.5 = +2.2 and +6.3 | +13.0 = +11.4 and +1.6 | +11.9 = +8.1 and +3.8 | +20.6 = +13.3 and +7.4 | +16.5 = +9.4 and +7.1 |
| MISO | 5.5 | +0.1 = +0.4 and -0.3 | +6.2 = +4.6 and +1.6 | +7.4 = +5.7 and +1.7 | +9.3 = +3.5 and **+5.7** | +5.7 = +6.8 and -1.1 |
| SPP | 8.7 | -0.3 = -6.3 and +6.0 | +14.0 = +2.5 and **+11.5** | +23.7 = +4.6 and **+19.1** | +16.2 = +1.6 and **+14.6** | +21.0 = -1.5 and **+22.5** |
| NYISO | 4.2 | +1.5 = +3.7 and -2.3 | +2.1 = +6.4 and **-4.3** | -0.8 = -0.4 and -0.4 | +2.7 = +4.8 and -2.1 | +6.2 = +7.1 and -0.9 |
| ISO-NE | 5.5 | +4.2 = +7.2 and -3.0 | +3.6 = +11.2 and **-7.6** | -2.8 = -2.5 and -0.4 | +4.1 = +1.0 and +3.1 | not held |

- **Not held: four of New England's figures** (2025's summer peak and overnight minimum; 2026's winter peak and overnight minimum). Bridgeport's station lacks hours in 2025 and 2026, a grid's hour needs all five stations, and New England falls between 92 and 95 percent on these. I did not lower the 95 percent bar to admit them.
- 64 of the 136 figures held are findings.

### The five strongest findings

1. **Texas: +23.8 percent in 2025 that temperature does not explain, give or take 4.1.** Demand averaged 55,666 MW against 43,998 MW in 2019 to 2021, growth of 26.5 percent, of which temperature explains 2.7. It has risen every year: +7.4, +13.0, +17.9, +23.8, and +28.8 (give or take 3.8) for 2026 to 27 September.
2. **SPP: +12.5 percent in 2025, give or take 1.5.** Relative to its uncertainty this is the firmest figure in the table (8 times). Temperature explains 0.2 of 12.7. In 2026 so far, +14.1, give or take 1.3.
3. **PJM turned in 2024.** The part temperature does not explain was +1.8 and +2.2 in 2022 and 2023, neither a finding at 2.6. Then +3.7 in 2024, **+6.8 in 2025** and +8.9 in 2026 so far (give or take 3.1). 2023 is the case the page was built for: metered demand fell 0.4 percent, and a mild year explains a fall of 2.6.
4. **The overnight minimum rose more than the year's energy in every grid that grew.** In 2025: Texas +29.4 (give or take 4.8) against +23.8; SPP +15.7 (2.3) against +12.5; PJM +9.4 (2.3) against +6.8; MISO +4.8 (2.3) against +3.6. **New York: +4.1 at night, give or take 1.9, while its year's energy is flat** (-0.1, give or take 2.8). Load that does not switch off would read this way. So would rooftop solar holding daytime demand down while nights grow. The table cannot tell which.
5. **Temperature explains little of the year's energy and much of a summer peak.** The most it explains of any year's energy in any grid is 4.4 points (Texas, 2022). Of Texas's summer peak in 2023 it explains 11.6 of 15.4 points, and that peak is beyond the fit's weather. The summer peaks that are findings are few: Texas 2025 (+12.7, give or take 6.6), SPP 2024 and 2025 (+6.5 and +8.8, give or take 3.7), MISO 2023 (+6.3, give or take 3.8), New England 2023 (+6.9, give or take 5.5), and New York 2026, which fell short of what its hot summer explains (-5.4, give or take 4.2).

**What the remainder is not.** It is growth temperature does not explain. Population, electrification, industry and datacenters are in it together, and so are rooftop solar, efficiency, prices and humidity. The warehouse cannot split them. The page says so above the tool, and no figure above is a count of datacenters.

**Not findings, and worth saying:** New York's and New England's energy in 2025 (-0.1 and -1.1, inside their uncertainty); every Texas winter peak (the uncertainty is 36.7 points: the winter left out that holds February 2021 misses by that much, because the grid was shedding load at its coldest hours); every California summer peak (give or take 9.9).

### California across December 2025

- **Comparable across the change: every figure here.** They rest on demand, which is a different series from generation and which the demand method's own check found does not step; and on hours dated right, because California's late hours are set back before anything is computed.
- **Not comparable, and not used:** California's generation by source in EIA's series either side of 16 December 2025.
- **A check the weather allows.** If demand sat on the wrong hour, the fit would match it clearly better moved by an hour. Over the eight weeks before EIA dated the hours right (to 2 December 2025) and the eight weeks from the change in its generation series, in 2025 and on the same dates a year earlier: the error is smallest as read in three windows of four. In the fourth (October and November 2025) it is 0.12 points smaller with demand an hour late (6.98 against 7.10 percent), against 1.34 points worse an hour early. That is too little to read as a misdated hour and too coarse to rule one out. Metered demand stood 2.9 percent above the fit before and 6.3 after; a year earlier, 4.6 and 6.2. So nothing as large as an hour's shift shows, and the check cannot see a step of a point or two in the level.

### The page

`/demand/weather`, in review, in the demand page's layout and shared components: one summary sentence that names the grids with a finding and their uncertainties; "what the remainder is not" above the tool; one chart of explained against unexplained growth by grid, with the uncertainty drawn on each bar; the table by grid and year; and, folded, the check on years not seen, the stations and their weights, the method, California, and what is not there. A figure and a year can be chosen. `/demand` links to it.

- Site build exit 0. Route check exit 0: 16 live pages and 111 in review, 0 failed. The page's own check (`site/scripts/check-demand-weather.mjs`): 65 of 65, every marked number equal to the site's copy, for all four figures and all five years, and the visitor's view holding no number.
- I looked at it in a browser at desktop width and fixed two things the look showed (the table's last column was cut off; labels of bars pointing left sat on the grid names). **Not looked at on a phone**: the headless browser here does not go narrower than 500 pixels.

## What would make this ready to open

1. **Real population weights.** One file from the Census Bureau (its table of metropolitan areas) and a rerun. It is a pull, and yours to approve. The year's energy will barely move (1.2 points at most under equal weights); the peaks may (New York's 2024 summer peak moves 7.2 points under equal weights, which are a deliberately poor choice there).
2. **A person confirms the license** from NOAA's two records, quoted above and in the method.
3. **A ruling on New England's four missing figures**: keep the rule, allow four stations of five with the weights restated, or replace Bridgeport.
4. **A ruling on the base.** 2019 to 2021 holds the lockdowns, and in Texas growth already under way. It is what you asked for and I kept it. The uncertainty would be tighter and the base stiller with more years before 2019; EIA's hourly demand begins in mid 2018, so that is not available.
5. **Humidity and sunshine.** Dew point is in the weather tables and not in the fit. California needs sunshine or behind-the-meter solar before its figures mean much.
6. **Keeping it current.** A standing pull and its budget (above). Until then the tables end on 28 September 2026.
7. **The station hours are not a warehouse table.** The grid tables are built from NOAA's files on this machine (66 MB). The 14-day pruning of raw files would have removed them; I put a second copy in a folder the pruning leaves alone (`warehouse/raw/noaa_grid_weather/pull_2026-10-05/`). A station-hour table (about 4.7 million rows) would make the weights changeable without the laptop.
8. **The phone**, and your read of the page's words.

## Decisions made without you

- **No request to the Census Bureau**, though the task asked for population weights. "No pull but NOAA's" was a rule, and a rule outranks a convenience. The cost is point 1 above.
- **ISD-Lite and the Local Climatological Data, not NOAA's newer hourly archive.** The newer archive's 2026 files hold about 60,000 rows a station (most with no temperature), which would have cut the stations to 20 under the ceiling.
- **Five stations a grid**, not more for the larger grids: 35 stations was what the ceiling allowed with room to spare.
- **Minneapolis's exception**, and the test that stops a build when the two products disagree being put on the sixteen non-synoptic hours.
- **The uncertainty is the largest of three misses, and a peak's is never under one hour's error.** You asked for an uncertainty from the fit's out-of-sample error; this is the widest honest reading of it. A peak beyond the fit's weather is not called a finding even when it clears its uncertainty.
- **Texas's load-shed days left out of the fit** (15 to 19 February 2021). The dates are stated in the code, not retrieved.
- **The four FERC list requests** in session 125's command (answer a).
- **Not in the menu, and held out of the catalogue and of `/terms`.**
- **Session 124's test changed** (two lines that pinned 2,732). It is another session's test; it was failing on main and would have blocked every landing.
- **The fix for the daily run is prepared and not landed.** A deploy inside a freeze is yours.
- **The overnight minimum is the mean of each day's lowest hour**, not the year's single lowest hour: one hour in a mild spring night says little.

## Errors, and what caught them

| What | Caught by | Now |
|---|---|---|
| I planned the whole pull on a NOAA product that ended thirteen months ago | NOAA's station list, read before any file | two products, the seam checked |
| The seam check stopped the first run at Austin (76 percent) | the check itself | the synoptic hours are judged apart and reported; the clock is right |
| NOAA's service answered 200 with nothing (Omaha) and with a file cut off at 1 January 2026 (Ontario): California's 2026 would have been lost, silently | the newest hour of each station in the log | every answer is tested for wholeness, counted, and asked again |
| Minneapolis missing 8,276 hours, MISO at 88 percent of its hours | the per-station counts | read from the second product for that stretch |
| Local days of 23 and 25 hours were left out of the daily table (16 a grid) | the test written for it | fixed, the chain run again, 630 rows more |
| The coverage builder had no sector for the new tables | the builder (exit 1, the chain stopped) | a rule added |
| My header's "Derived from" line named something that is not a table | reading the builder before the second run | the line names tables only |
| A peak's uncertainty of 1.2 points from three lucky misses | reading the table: smaller than the fit's error on one hour | never under one hour's error |
| The new tables and sources would have moved the home page's counts and `/terms` on landing | reading how earlier review pages were held | under the two hold lists, tested |
| The page's table cut off at the right; chart labels on the grid names | looking at the page | fixed |
| My builder read a table with `comment="#"`, against the house rule of session 103 | the full suite | reads with the header count; the table it builds is identical, row for row |
| Main's own test fails against the file today's daily run wrote (not this session's fault; found by running the full suite) | the full suite | fixed on this branch and on a one-commit branch from main; at the top of this report |
| Three edit scripts written through the shell lost their backslashes (one left the connector unparseable for a minute) | the syntax check after each edit | edit scripts are written as files |

## Tests

`tests/test_session126.py`, 37 tests, on real samples saved under `tests/fixtures/session126/` as NOAA and EIA served them (Austin, 1 to 3 July 2025, in both products; Minneapolis, 14 and 15 July 2020, in both; New England's hourly demand and weather, 2019 to 2022). They hold: the two products agree only with the right clock; a marked or blank value is not a number; an empty or cut-off answer is not whole; three missing hours are interpolated and counted, four are not, and never at an end; a grid's hour needs every station; degrees are taken at each station and then weighted; only whole local days are written, a 23-hour day among them; the ceiling stops a pull; growth is weather plus the rest; **a year left out comes back within 2 points for New England, and a year made of the fit's own demand comes back at zero**; 5 percent more demand is 5 percent more unexplained; an impossible hour is used for nothing; a figure short of its hours is not written; a peak is never more certain than one hour; the load-shed days are out of the fit only; the page is in review and says what the remainder is not; the method quotes NOAA; the tables as built; nothing of it reaches a live page. Where a test blanks or scales a real value, it says so.

Full suite: 1,296 passed, 19 skipped, exit 0 (382 seconds), on `wip/126-demand-weather` as pushed. The first full run failed two tests and both are in the table above: my builder's reader, and session 124's pinned count. Site build exit 0; route check exit 0; the page's check 65 of 65.

## The live pages

| Snapshots | Pages | Differences |
|---|---|---|
| `at-1532` (session 125) to `before-126load` 17:04:04 | 25 | **179**, the daily run and the price jobs, inside the freeze (point 1 at the top). None from this session |
| `before-126load` to `after-126load` 17:04:47, around the contracts summary | 25 | **0** |
| `after-126load` to `end-126` 18:01:34 | 25 | 32, all the clock: 26 on `/` (five hubs' newest real-time price and its interval) and 6 on `/network` (refreshed 13:05 to 17:05 UTC, demand's newest hour 11:00 to 14:00 UTC) |

- This session deployed nothing, pushed `wip/` branches only, and loaded one thing: the contracts page's stored summary, internal.
- Seen on `/network` and not mine to touch: its newest hour of flows reads 4 October 03:00 UTC, in both snapshots.
