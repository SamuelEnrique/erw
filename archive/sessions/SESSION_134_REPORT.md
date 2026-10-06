# Session 134 report: Supply and trade, a new page at /supply

## Three things to know before anything else

1. **One test fails on this branch until session 132 lands, so land 132 first.** `tests/test_session53.py::Nav::test_no_menu_over_eight`: the Prices menu holds nine entries here (the eight on main, and Supply and trade). Session 132 retires `/markets`, which brings it back to eight. I tried the merge of this branch with `wip/132-board`: `site/lib/pages.ts` merges cleanly and the menu then holds eight. Pushed to a `task/` branch before 132 is on main, this branch's checks will fail on that one test.
2. **Part of the brief is not on the page.** Day-ahead energy cleared per grid was not pulled: I did not reach it. Its seven rows are on the page with their placeholders and no value. Weekly natural gas production and ICE Brent positioning are not open data, so they are placeholder rows too. Fuel burned for power is shown by week (the mean of seven whole days), not as a daily chart. Details under "Verdict".
3. **Six tests of earlier sessions fail on this machine, and I believe only on this machine.** They compare the mix tables in `warehouse/output` with the site's copies. The tables here are the ones session 133 rebuilt last night; this branch, cut from main, has main's copies and main's tests. All six are in the three test files session 133 changed, and the same suite passed on `wip/133-mix`. I did not prove it by running them on a clean machine. Nothing in this session touches those tables, files or tests.

## To finish

**The freeze is on** (`REVIEW_FREEZE`, 5 to 7 October; `python scripts/freeze.py status` exited 1 today). This session pushed `wip/134-supply` only, deployed nothing and loaded nothing into the live set. The branch is from main (`e33f4e0`) and builds on no other. When `python scripts/freeze.py status` exits 0, and after sessions 132 and 133 are on main:

```bash
git checkout wip/134-supply && git fetch origin && git merge origin/main
node site/scripts/snapshot-live.mjs take before-134
git push origin wip/134-supply && git push origin wip/134-supply:task/134-supply
python runs/session118/watch_run.py task/134-supply 15
node site/scripts/snapshot-live.mjs take after-134 && node site/scripts/snapshot-live.mjs compare before-134 after-134
cd site && node --import ./scripts/alias-register.mjs scripts/check-supply.mjs https://erw-flame.vercel.app && cd ..
git push origin --delete wip/134-supply
```

- **What the comparison should show on the three open pages: nothing but the clock.** `/supply` is `review`. No open page reads anything this session wrote. The menu gains one greyed item under Prices. There is no load and no Redivis step left: the five tables are held out of the live set (`catalogue_hold`) and are already in the Redivis drafts, unreleased.
- **The merge with main will conflict once 132 and 133 are there** (I tried both with `git merge-tree`). With 132, seven files; with 133, four of the same:
  - `warehouse/supabase/live_set.yaml`, `warehouse/metadata/build_coverage.py`, `warehouse/metadata/sources.csv`, `warehouse/metadata/redivis_uploads.csv`: two lists side by side. Keep both sessions' lines.
  - `warehouse/metadata/coverage.csv`, `docs/coverage.md`, `warehouse/metadata/archive_manifest.csv`: generated. Take main's copy, then under the lock run `python warehouse/metadata/build_coverage.py --only '^(eia_gas_storage_weekly|eia_petroleum_supply_weekly|eia_gas_trade_monthly|eia_basin_production_monthly|cftc_cot_positions)$'` and `python warehouse/archive/archive.py --tables` with the same pattern and `write`. Read each exit code before the next step.
- **To open the page:** `"/supply": "live"` in `site/lib/release.ts`.
- **To make it refresh:** the line at the top of `warehouse/refresh_supply.sh`, added to `warehouse/run_daily.sh`. Nothing calls it today. The data on the page is as of 6 October until someone runs it: `python warehouse/lock.py run --task "supply refresh" -- bash warehouse/refresh_supply.sh`, then commit `site/data/supply.json` and `warehouse/metadata/release_schedule.json`.

## Verdict: not ready to open yet. Three things are left, one of them one line

The page is built, passes its own checks in a real browser, and answers its question for gas storage, crude and product stocks, production, refining, trade, gas trade, fuel burn and positioning: 86 rows with values. What is left before it should open:

1. **Schedule the refresh** (one line, above). A weekly page with no refresh is stale within a day: the next petroleum report is out on Wednesday 7 October at 10:30 Eastern. Each row shows its own date and the page shows when its file was built, so a stale page does not mislead, but it does not do its job.
2. **Day-ahead energy cleared per grid: not pulled.** Five grids read "not held yet", MISO "paused while terms are reviewed", PJM "licensed source needed". This was in the brief and is the one approved item I did not attempt. It needs a connector per operator.
3. **Land 132 first** (the menu test, above).

Not blocking, and yours to rule:

- **MISO and PJM show values in the fuel burn group.** Those figures come from EIA's hourly file (EIA-930), which is public, not from either operator's site. Session 133 did the same on `/mix`. If rule 4 means every MISO and PJM row is blank whatever its source, it is a change in `burn_rows` in `warehouse/derived/supply_page.py`; MISO's and PJM's own-data rows (day-ahead cleared) are already blank.
- **The Brent row is the NYMEX Brent Last Day contract**, labeled as such, because that is the Brent contract the CFTC reports. Its open interest is about an eighth of WTI's. The ICE Brent row is beside it, blank, "licensed source needed".
- **The tables are wider than the page's column at desktop width in some groups**, so the last column (the 52-point trend) needs a sideways scroll inside the table. The page itself does not scroll sideways, at desktop or phone width.

## Addresses retired

None. The page is new, at one address, `/supply`, with no version number. Its state is in the address: `?g=` for the groups shown, `?s=` for the series whose chart is open.

## What trader desks and public dashboards show each morning

Read by web search on 6 October 2026, before building. The sources are linked in the Method note.

1. **The weekly petroleum report is the most watched weekly dataset in oil, and prices react to the surprise, not the level.** Cushing stocks and implied demand matter as much as the headline crude number; refinery utilization is read beside them.
2. **Gas storage is read three ways:** the weekly change against the five-year average change for that week, the level against a year earlier, and the level against the five-year average, as a surplus or deficit in Bcf.
3. **A gas desk's daily balance** sets production against power burn, LNG feedgas, exports to Mexico and other demand, in Bcf a day.
4. **Positioning** is read as managed money's net position in WTI, Brent, Henry Hub and RBOB, its weekly change, and where it sits in its recent range.

What the page took: the three comparisons on every row, the surprise as the change against the five-year average change, seasonal bands, Cushing beside the headline, the gas rows in Bcf a day, positioning with its three-year range, the calendar. What it could not take: analysts' consensus, daily pipeline flows and ICE's Brent positioning are licensed; implied demand was not among the approved pulls.

## What the page shows

- **Five headline figures**, each tighter or looser against last week, last year and the five-year average: gas in storage (Lower 48), commercial crude, Cushing, gasoline and distillate stocks.
- **The surprises of the newest reports**: the rows whose latest change is outside the range of the same change in the five years before, farthest first. 15 rows today.
- **Next releases**, worked out on Eastern time each time the page is read, from each report's standing day and the holiday dates EIA lists. It does not go stale between refreshes.
- **"Select" chips** for the nine groups, held in the address.
- **Ten seasonal band charts** by default (gas storage for the Lower 48 and five regions; crude, Cushing, gasoline, distillate): this year bold, last year thin, the five-year average dashed, the five-year range as a band. **Any row with a value opens its own band chart.**
- **Nine tables, 99 rows.** Each row: latest, its date, change on the period before, on last year, the five-year average, the difference from it, the change against the five-year average change, and a 52-point trend. Positioning adds long, short and the place in its three-year range.
- **Hover everywhere**: band charts give the date and each series with its unit; trend lines give the value and date; every figure gives what it is measured against; every placeholder gives its reason.
- **No method on the face.** It is in `docs/methods/supply_and_trade.md`, linked from the page.

Of the 86 rows with values, 83 have the period before, 85 last year, 77 the five-year average and 75 the surprise. Where one is missing the cell is a placeholder, never a figure.

## Every pull against its ceiling

One ceiling for the session: 1,200,000 rows in all. Cost USD 0.

| Pull | Rows written | Rows returned, every request counted | Note |
|---|---|---|---|
| EIA weekly gas storage, 8 series from 2010 | 6,992 | 13,984 | two runs: a trial into a separate folder, then the run that wrote |
| EIA weekly petroleum (stocks, production, refinery runs and utilization, imports and exports), 30 series from 2010 | 26,088 | 52,176 | two runs |
| EIA monthly gas trade by point of entry and exit, from 2015 | 1,979 | 73,326 | two runs. The route answers every country and terminal; the connector keeps the totals and each terminal's total |
| EIA Short-Term Energy Outlook, production by region, from 2015 | 1,668 | 3,744 | two runs. Forecast months are not written |
| EIA, probes while writing the connector | 0 | about 6,000 | counted as 6,000 in the connector's own budget |
| CFTC Commitments of Traders, 4 contracts from 2015 | 9,808 | 4,904 weekly reports, plus a few probe requests of a handful of rows that I did not count exactly | two runs |
| **Total** | **46,535** | **about 154,000 of 1,200,000 (13 percent)** | |

Also read: EIA's two release schedule pages (two web pages, each read two or three times), and the header line of one ICE file, of which nothing was kept. **No MISO request was made. No model call was made.** All five tables passed the validator and are in coverage, the archive and the Redivis drafts. Nothing was released.

## Terms of each new source, quoted

- **EIA** (four tables), Copyrights and Reuse: "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website". Public.
- **CFTC** (positioning), Web Policy, read 6 October 2026: "Government information at the CFTC website is in the public domain. Public domain information may be freely distributed and copied, but it is requested that in any subsequent use the CFTC be given appropriate acknowledgement." Public, with the CFTC named as the source on every positioning row.
- **ICE** (ICE Brent positioning), Terms of Use, read 6 October 2026: content may be downloaded "only for your own personal, non-commercial use", and a user will not "sell, license, rent, modify, print, collect, copy, reproduce, download, upload, transmit, disclose, distribute, disseminate, publicly display, publicly perform, publish, edit, adapt, electronically extract or scrub, compile or create derivative works from any content or materials". **These terms forbid republishing, so the series was not pulled at all**, neither public nor internal.

No series is held internal: everything pulled is public domain.

## What is not held, and why

| Asked for | On the page | Why |
|---|---|---|
| Day-ahead energy cleared per grid | 7 rows, no value | not pulled this session |
| Weekly natural gas production | 1 row, "licensed source needed" | EIA publishes none of its own; the weekly figures in its gas update are S&P Global's |
| Brent positioning on ICE | 1 row, "licensed source needed" | ICE's terms, above |
| Oil burned for power in California, MISO and New England; coal in New England | 4 rows, "not held yet" | EIA's hourly file leaves the fuel blank in recent weeks. A blank hour is not a zero |
| Fuel burned, the seven grids together: week before and five-year average | placeholders in those two cells | California's week ending 25 September is short of whole days; one week of the five years is missing for PJM |
| Fuel burned by day | by week | the builder works by day, then gives the week's mean. No daily chart was built |
| The week's figure against analysts' consensus | against the five-year average change | consensus polls are licensed |

Oil in ERCOT and coal in New York have no row: EIA's file never names the first and reports the second as zero in every hour.

## What looks implausible, flagged and not changed

- **Gas burned for power, about 23 Bcf a day in the seven grids**, will read low to anyone who knows the national power burn figure. It covers the seven ISO grids only, at one stated heat rate of 7.6 MMBtu per MWh. The Method note says both. It is an estimate of direction, not a balance figure. I did not check it against a published national figure.
- **LNG exports, "every other point of exit together": up 2,337 percent on the year.** True and meaningless: 0.11 Bcf a day against almost nothing. The percent is shown as computed.
- **WTI managed money net long: up 466 percent on the year.** From 14,053 contracts to 79,592. True; a percent of a net position reads large when the base is small.
- **Crude production in the Haynesville region, 32 thousand barrels a day**, is small because it is a gas basin. As EIA gives it.

## Checks

- **Session tests:** `tests/test_session134.py`, 26 tests on real samples saved under `tests/fixtures/session134/` (rows of EIA's and the CFTC's own answers, EIA's two schedule pages, gas storage by week and exports to Mexico by month as held). `site/scripts/test-supply.mjs`, 9 tests of the page's helpers, its address and its calendar.
- **The page's own check** (`site/scripts/check-supply.mjs`): **26 of 26** on the built site, in a real browser. Every row's latest value and five-year average equal the file; the storage row's four comparisons; the 15 surprises are exactly the file's; all 13 blank rows read their placeholder with a reason and no number; the next releases are none in the past; `?g=` and `?s=` work; a visitor gets the in-review page; ten band charts drawn; a band chart and a trend line answer the mouse; a row opens its chart; a chip filters; no script error; no sideways scroll at 390 pixels.
- **Site build:** exit 0. **Type check:** exit 0. **Route check:** exit 0, 8 live pages and 118 in review, 0 failed; `/supply` and its Method note are in its list.
- **Full suite:** **1,277 passed, 7 failed, 19 skipped, exit 1.** The seven: the menu test (item 1 at the top) and the six tests of sessions 94, 122 and 123 that read this machine's mix tables (item 3 at the top). No test of this session fails, and no earlier test was changed.
- **I looked at** the page at desktop width (the top, an open chart, the production, refining, gas trade, fuel burn and positioning tables) and at phone width.
- **What the checks caught:** the surprises list pushed the page sideways on a phone (fixed); my first build of fuel burn read a blank hour as zero, which showed 0.0 for oil in California and MISO and coal in New England (fixed before any commit: those rows are now "not held yet", and a test holds the rule); a release calendar baked into the file would have named a past date as "next" from Wednesday (now worked out when the page is read).

## Decisions made without you

- **A year is 52 weeks**, so a weekly figure is always compared with the same weekday. EIA's own five-year average is by report week, the same idea.
- **The surprise is the change less the five-year average change**, and the page says exactly that, never "against expectations".
- **A comparison is made only from values held.** The five-year average needs all five years.
- **The Outlook's regional production stops three months before the run**, to keep EIA's forecast out. The table ends with July 2026.
- **Gas trade is in Bcf a day** (EIA's monthly MMcf over the days of the month), so months compare.
- **Heat rates are stated assumptions**: gas 7.6, coal 10.6, oil 11.0 MMBtu per MWh.
- **Tighter or looser is written only where the direction has a reading.** More stocks, production or imports is looser; more exports or burn is tighter. Refinery runs, utilization and positioning carry none. A difference that rounds to zero carries none.
- **The page reads its own file**, not the live set, so nothing was loaded during the freeze. The five tables are in `catalogue_hold`.
- **The page shows short units** (Bcf, kb/d); the file keeps the long ones.
- **`/supply` was added to `docs/tools.md` and to the route check**, which a test and the workflow expect of a page in the menu.

## The five most interesting numbers the page now shows

1. **Gas in storage, Lower 48: 3,415 Bcf on 25 September, up 64 on the week against a five-year average build of 88.** A build 24 Bcf smaller than normal for the week. The level is 27 Bcf above the five-year average and 136 below last year.
2. **Distillate stocks: 105.2 million barrels, 15.7 million (13.0 percent) below the five-year average and below the lowest of the five years.** Gasoline is 15.9 million (7.2 percent) below, also under the range. Commercial crude is 7.8 million above its average: tight products, comfortable crude.
3. **LNG exports: 16.73 Bcf a day in July 2026, 5.70 above the five-year average (up 51.6 percent) and 2.64 above July 2025.**
4. **Henry Hub managed money: net short 132,799 contracts on 29 September, 67,252 more short in one week.** The five years' changes for that week ran from -6,523 to +32,010. The position is a tenth of the way up its three-year range. WTI's net long fell 22,236 in the same week, also outside its five years.
5. **US crude production: 13,955 thousand barrels a day, 1,354 (10.7 percent) above the five-year average and above the highest of the five years.** The Permian alone gave 6,753 in July.
