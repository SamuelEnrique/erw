# Session 132 report: the price board and its markets workbench, one page at /board

## To finish

**The freeze is on** (`REVIEW_FREEZE`, 5 to 7 October). This session pushed `wip/132-board` only, deployed nothing, and loaded nothing into the live set. The branch is from main (`e33f4e0`) with `wip/127-board-v4` merged into it, so **it replaces that branch: land this one and delete both**. When `python scripts/freeze.py status` exits 0:

```bash
git checkout wip/132-board && git fetch origin && git merge origin/main
node site/scripts/snapshot-live.mjs take before-132
git push origin wip/132-board && git push origin wip/132-board:task/132-board
python runs/session118/watch_run.py task/132-board 15
node site/scripts/snapshot-live.mjs take after-132 && node site/scripts/snapshot-live.mjs compare before-132 after-132
cd site && node --import ./scripts/alias-loader.mjs scripts/check-board.mjs https://erw-flame.vercel.app && cd ..
git push origin --delete wip/132-board wip/127-board-v4
```

- **What the comparison should show on the three open pages: nothing but the clock.** `/board` stays `review`; the six new tables are under `catalogue_hold` and their sources under `sources_hold`; the menu loses one greyed item ("Markets"), which a visitor sees only as one fewer greyed line in the Prices menu. **That menu line is the one visible difference on a live page's frame, and it is meant.**
- **If the merge conflicts**, it is in the generated metadata the daily run rewrites. Take main's copy and run, under the lock: `python warehouse/metadata/build_coverage.py --only '^(eia_regional_retail_fuel_prices|eia_crude_stream_prices|eia_power_plant_fuel_costs|fred_treasury_yields|imf_commodity_prices|carb_lcfs_credit_prices|eia_all_futures_prices|price_board_stats)$'`, then `python warehouse/archive/archive.py --tables` with the same pattern and `write`.
- **To open the page:** one line of `site/lib/release.ts`, `"/board": "live"`, by the same route.
- **To make it refresh daily:** add `run_other board "$PYTHON" warehouse/health.py run --step "board" -- bash warehouse/refresh_board.sh` to `warehouse/run_daily.sh` after `price_board` and `trader_view`, and let the run's commit step add `site/data/board.json` and `site/public/board/`. Until then the page shows the day it was built (6 October).

## Verdict: ready to open, once three things are ruled

The page is finished and passes its checks. Three rulings are yours, none of them holds the build:

1. **The IMF's terms.** I could not read the IMF's own terms page (it answered HTTP 403); I read its words through a search result's quotation, which permits publishing with attribution. Uranium, lithium, cobalt, nickel and copper are on the board on that reading. **Read the page before the board opens**, or tell me to grey the five rows.
2. **Where the workbench's files live.** They are 16 MB in the repository (740 series files and 74 hourly files) and every one is rewritten by each refresh. Before the refresh is scheduled, decide: stay in git, or move to the public storage bucket the network map uses.
3. **The futures.** EIA still ends them on 5 April 2024 (checked today). The curve beside each spot row is drawn greyed with "licensed source needed" and CME Group named on hover; the 2019 to 2024 history stays internal and unshown, as session 127 left it for you.

**What is left besides those:** nothing in the build. The page shows 6 October's data until the refresh is switched on.

## Read these first

1. **One page now holds the four.** `/board` is the union of the first board, version 3, version 4 and `/markets`, on the dense original as its base, with your rulings applied. 794 rows: 740 with values, 54 placeholders.
2. **Most of the series you approved were already held.** The session pulled six small tables, 39,443 rows written, about 302,000 rows read of the 1,500,000 ceiling counted the widest way (below).
3. **Three things you asked for do not exist in the open, and are greyed with their source named:** NYMEX futures after 5 April 2024 (EIA stopped), coal spot by basin (EIA says S&P Global's history "cannot be released"), and any daily crude grade beyond WTI and Brent (EIA publishes the others monthly, which the board shows as monthly).
4. **I dropped 1,060 zeros from EIA's plant fuel costs.** EIA writes a cost of exactly 0 where a state took no deliveries (California's coal, every month). Shown as prices they read as free coal. They are not written; negative gas costs in New Mexico and Arizona are EIA's and are kept. Flagged as implausible-looking: New Mexico gas at -3.26 USD/Mcf in April 2026.
5. **Three earlier tests were changed**, because they asserted the old addresses: sessions 53 (menu), 104 and 127 (page paths), and 112 (a dated state document naming `/markets`). Each now accepts a retired address that redirects.

## What each earlier page showed, and where it is now

| Earlier page | What it showed | On `/board` now |
|---|---|---|
| `/board` (session 30) | Power at six main hubs, day-ahead and real time: daily mean, day change, 7-day and 30-day average, 30-day low to high, DA minus RT, 30-day trend | "Power, by hub and zone", every column kept; "Day-ahead minus real time" |
| | Peak and off-peak by grid and market | "Power, on-peak and off-peak" (three rows a hub and market) |
| | Henry Hub and Brent minus WTI tiles; spark spread and implied heat rate | "Natural gas", "Crude oil", "Spark and dark spreads" |
| | Carbon (a sentence: held internal) | "Carbon and credits": two rows reading "not held yet", plus California's fuel credit price |
| | ERCOT since 2015 (two bar strips and a table) | **Off the board**, as ruled: a link to `/explorer/ercot-peak-premium` in the header |
| | Every hub and zone (39), folded | The "Every hub and zone" switch on four groups |
| `/board/v3` (104) | Market switch; lowest and highest grid and Henry Hub as headlines; power, gas, oil with day and week moves | The headline strip and its market switch; the same rows |
| | "What is on this board" note | **Struck**, as ruled |
| `/board/v4` (127) | 33 lines with moves over a day, week, month and year and the one-year range; three spreads with formulas; seven greyed prices | Every row carries those figures; formulas on hover; greyed rows with the source on hover |
| | "How to read the columns" | In the Method note, not on the page |
| `/markets` (19) | By grid: week means and change, on-peak and off-peak, RT minus DA, heat rate, largest RT premium, hours RT over DA + 50, 30-day volatility; top real-time intervals | "The week, by hub", and each hub's workbench |

## What the page shows

Seventeen groups and the week's table. Filters on every group that has more than a handful of rows; every choice is kept in the address.

| Group | Rows | Step | Newest |
|---|---|---|---|
| Power, by hub and zone (31 hubs and zones, two markets; MISO 8 and PJM 5 hubs blank) | 88 | daily | 4 or 5 October (real time 3 October) |
| Power, on-peak and off-peak | 30 | daily | 2 October |
| Spark and dark spreads, implied heat rate | 17 | daily, dark monthly | 3 October; July |
| Day-ahead minus real time | 31 | daily | 3 October |
| Battery spread | 62 | daily | 4 October |
| Ancillary services (ERCOT, CAISO, NYISO, SPP) | 46 | daily | 5 October |
| Natural gas | 8 (1 with values) | daily | 29 September |
| Crude oil: WTI, Brent, the gap, and 41 monthly streams | 45 | daily, monthly | 29 September; July |
| Refined products, spot | 11 (9) | daily | 29 September |
| Oil spreads: two 3-2-1 cracks, Brent minus WTI | 2 and the gap | daily | 29 September |
| Retail gasoline and diesel, by region, state and city | 40 | weekly | 28 September |
| Retail electricity by state and sector | 248 | monthly | July |
| Coal and gas delivered to power plants | 148 (143) | monthly | July |
| Uranium and battery metals | 7 (5) | monthly | August |
| US Treasury yields | 3 | daily | 2 October |
| Carbon and credits | 6 (2) | weekly | 14 September |
| Capacity and equities | 2 (0) | | |

- **Every price row:** latest value and its date; the move over a day, a week, a month and a year; 7-day and 30-day averages; 30-day low to high; a trend line of the last 30 points; a bar placing the latest in its one-year range.
- **Nothing static.** A trend line answers the mouse with the value, the date and the series. Every workbench chart does the same, by the hour where the series is hourly.
- **No method on the page face.** A missing number is "not held yet", "licensed source needed" or "paused while terms are reviewed", with the reason on hover. A check holds this.
- **Hub and zone names in words, codes on hover.**
- **Monthly and weekly series are labeled so**, and their daily (or weekly) move cells say "monthly" or "weekly" instead of a number.

## The markets workbench

Click any row. It opens beside the tables; Expand makes it full width; the address holds the whole view.

- **Window:** week, month, 3 and 6 months, 1, 2 and 5 years, all, or two dates.
- **Overlay:** any second series on the board, chosen from a list grouped as the board is.
- **Spread or ratio** between the two, as its own line with its average and range.
- **Prior years:** this year against the same dates in the five before, with their range as a band.
- **Distribution:** histogram, values above a threshold you set, values below zero, on-peak and off-peak means, median, 30-day volatility, the ten highest with timestamps.
- **CSV** of the rows shown, and a copy-link button.
- **A power hub opens** on seven days by the hour, real time against day-ahead, with on-peak and off-peak means, the ten highest hours, the hub's week and its highest 15-minute intervals: everything `/markets` showed.

Two choices of mine inside it, both in the Method note:

- **Two series of different steps are compared by the month**, the finer one as its monthly mean, named so. Nothing is carried across days.
- **The five-year band of a daily series is by the week**, not the single day. A fuel has no weekend, so a band by the day narrowed wherever a year's date fell on one.

## Addresses retired

| Address | Now |
|---|---|
| `/markets` | redirects to `/board` (308) |
| `/board/v3` | redirects to `/board` |
| `/board/v4` | redirects to `/board` |
| `/data/methods/price_board_v4` | redirects to `/data/methods/price_board` |

Their page files are kept, unrouted, under `site/app/_retired/`. Nothing was deleted. "Markets" is out of the menu.

## Every pull against its ceiling

Ceiling: 1,500,000 rows for the session. Rows written: 39,443 in six tables. Rows read, counting every probe, trial and rerun:

| Source | Table | Rows written | Rows read | Note |
|---|---|---|---|---|
| EIA API | `eia_regional_retail_fuel_prices` | 16,159 | | weekly, 40 series |
| EIA API | `eia_crude_stream_prices` | 2,982 | | monthly, 42 series |
| EIA API | `eia_power_plant_fuel_costs` | 12,898 | | monthly, 61 locations, 2 fuels |
| EIA API, all three | | | about 104,000 | one trial, two full runs (the second after a unit fix), one rerun of plant fuel, probes |
| FRED | `fred_treasury_yields` | 5,820 | about 61,600 | includes a probe that read three whole histories |
| IMF | `imf_commodity_prices` | 460 | about 2,200 | |
| CARB | `carb_lcfs_credit_prices` | 1,124 | about 134,400 | the workbook was downloaded five times; its 26,336-row transaction log comes with it and is not read |
| **Total** | | **39,443** | **about 302,000 of 1,500,000** | |

Not pulled, because already held: refined product spot prices, retail electricity by state, Henry Hub, WTI, Brent. Not pulled, because not open: futures, coal spot. **No MISO request was made.** No model call was made. All six tables passed the validator and are in coverage, the archive and the Redivis drafts (nothing released).

## Terms of each new source, quoted

- **EIA** (three tables), Copyrights and Reuse: "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website". Public.
- **EIA on coal spot by basin:** "Data source: With permission, S&P Global" and "Because the historical spot price data are proprietary, they cannot be released by EIA". **Forbids republishing: not pulled, greyed.**
- **EIA on futures:** "NYMEX Futures Prices (Futures prices after April 5, 2024, are not available)". Greyed.
- **Federal Reserve, through FRED:** H.15 is a U.S. government work; FRED marks the series "Public Domain: Citation Requested". Public. FRED's series page reset the connection today, so that notice is as the site's older FRED connector recorded it.
- **IMF**, Copyright and Usage, through a search result's quotation: "You may download, extract, copy, create derivative works, publish, distribute, and use Data obtained from IMF Sites", with attribution and no alteration. Public by this reading; **yours to confirm** (above).
- **California** (CARB's credit price), Conditions of Use: "In general, information presented on this website, unless otherwise indicated, is considered in the public domain. It may be distributed or copied as permitted by law." Public. The same words would cover CARB's allowance auctions, which have been internal since session 7: yours to rule; I changed nothing.

No series is held internal by this session, because no source it pulled forbids republishing. The one that does was not pulled.

## The Brent minus WTI gap, verified

EIA's API today (`petroleum/pri/spt`): Brent 113.96 and WTI 96.16 USD a barrel on 29 September 2026. Gap 17.80. The board's row reads 17.80 for the same day.

## Checks

- **Session tests:** `tests/test_session132.py`, 30 tests on real samples (EIA's own rows for the three routes, FRED's file across Christmas, the IMF's answer, CARB's sheet with its one Tuesday, four operating days of ERCOT's prices). `site/scripts/test-board.mjs`, 10 tests of the page's arithmetic on the site's own files.
- **Full suite:** 1,307 passed, 19 skipped, 1 failed (the menu test of session 53, which listed `/markets`). I changed that test and it passes; **I did not run the 8-minute suite a second time.**
- **Site build:** exit 0. **Route check:** exit 0, 8 live pages and 116 in review, 0 failed.
- **The page's own check** (`site/scripts/check-board.mjs`): 29 of 29, in a real browser: every marked number equals the file; MISO and PJM blank; the three redirects; the workbench opens, docks, expands and reopens from an address; a trend line answers the mouse.
- **I looked at the page** at desktop and phone width. On a phone the workbench sits above the tables and the tables scroll sideways.

## Decisions made without you

- **Old pages moved, not deleted**, to `site/app/_retired/`.
- **The page reads files, not the live set**, because a load is a change under the freeze.
- **Dark spread uses the US average coal cost** and 10.5 MMBtu/MWh for every grid, monthly, labeled indicative.
- **A second crack spread** (New York Harbor products against Brent) beside the Gulf Coast one.
- **Treasury yields are filed under the `equities` sector**: the vocabulary has none for interest rates.
- **Source ids `:regional` and `:streams`** on two EIA routes, so the registry rows of older tables on the same routes did not change.
- **Zeros dropped from plant fuel costs** (above).

## The five most interesting numbers the page now shows

1. **Brent minus WTI: 17.80 USD a barrel** on 29 September, 13.07 wider than a year ago, in a one-year range of -2.45 to 30.78.
2. **Gulf Coast 3-2-1 crack spread: 73.63 USD a barrel**, 49.37 above a year ago.
3. **US 10-year Treasury yield: 5.28 percent** on 2 October, 99 percent of the way up its one-year range (3.97 to 5.29).
4. **Lithium: 148,620 USD a ton** (IMF, August), up 67,066 on the year.
5. **New York City real time: 1,372.09 USD/MWh** in one 15-minute interval on the evening of 3 October, the week's highest across the five grids shown.
