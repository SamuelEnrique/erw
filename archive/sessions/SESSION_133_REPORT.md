# Session 133 report: the energy mix, one page at /mix

## Two things to know before anything else

1. **One ceiling was passed, by the strictest count.** The NRC pull's ceiling was 300,000 rows. The table holds 233,295 rows and the run that wrote it read 241,560. But I downloaded the NRC's 365-day file two more times before it (a probe and a trial run) and its 2025 file once in the probe: **345,336 lines crossed the wire in all**, the same rows counted each time. Nothing extra was written. I should have reused the first download; I did not.
2. **A commit of mine briefly held a folder that is not this session's** (`warehouse/output/raw/`, test byproducts, untracked before I started). I caught it before any push, took it out of the commit, and checked that no commit of this branch holds it. It is on disk as it was.

## To finish

**The freeze is on** (`REVIEW_FREEZE`, 5 to 7 October). This session pushed `wip/133-mix` only, deployed nothing and loaded nothing into the live set. The branch is from main (`e33f4e0`) and builds on no other. When `python scripts/freeze.py status` exits 0:

```bash
git checkout wip/133-mix && git fetch origin && git merge origin/main
node site/scripts/snapshot-live.mjs take before-133
git push origin wip/133-mix && git push origin wip/133-mix:task/133-mix
python runs/session118/watch_run.py task/133-mix 15
node site/scripts/snapshot-live.mjs take after-133 && node site/scripts/snapshot-live.mjs compare before-133 after-133
cd site && node --import ./scripts/alias-register.mjs scripts/check-mix.mjs https://erw-flame.vercel.app && cd ..
git push origin --delete wip/133-mix
```

Then, under the data lock, so the database and the Redivis draft hold the tables this branch rebuilt:

```bash
python warehouse/lock.py run --task "session 133: the rebuilt mix tables" -- python warehouse/redivis/upload.py --tables generation_mix_hourly_profile generation_mix_records clean_energy_hourly clean_energy_summary grid_stress_yearly
python warehouse/lock.py run --task "session 133: load" -- python warehouse/supabase/load.py
```

- **What the comparison should show on the three open pages: nothing but the clock.** `/mix` stays `review`. The menu's entries do not change (the three retired addresses were not in it); only the description line of the greyed "Energy mix" item is reworded. The load touches three tables no open page reads (`generation_mix_hourly_profile`, `clean_energy_summary`, `grid_stress_yearly`); take a snapshot around it all the same.
- **If you land session 132 first, this branch conflicts with it in four files** (I tried the merge). Three are generated and one is two lists side by side:
  - `warehouse/supabase/live_set.yaml`: keep both sessions' blocks under `catalogue_hold`.
  - `warehouse/metadata/coverage.csv`, `docs/coverage.md`, `warehouse/metadata/archive_manifest.csv`: take main's copy, then under the lock run `python warehouse/metadata/build_coverage.py --only '^(caiso_fuel_supply_history|eia860m_retired_generators_all|nrc_reactor_status|caiso_wind_solar_forecast|ercot_wind_solar_forecast|generation_mix_hourly_profile|generation_mix_records|clean_energy_hourly|clean_energy_summary|grid_stress_yearly)$'` and `python warehouse/archive/archive.py --tables` with the same pattern and `write`.
- **To open the page:** `"/mix": "live"` in `site/lib/release.ts`.
- **To make the forecasts refresh daily:** the three steps at the top of `warehouse/refresh_mix.sh`. ERCOT keeps one week of postings, so each day the refresh does not run is a day of ERCOT forecasts that cannot be had later.

## Verdict: ready to open, with two things to rule and one that is thin

The page is finished and passes its checks. What is left:

1. **The NRC's terms.** Its notice page answered HTTP 403, so I could not quote it. The data is a U.S. government work and is used for one hover note. Confirm on the page, or tell me to take the note off.
2. **ERCOT's forecast view rests on 146 hours** (six days). It is real and labeled with its dates, but "forecast error by month" cannot be drawn for ERCOT until the refresh has run for some weeks. CAISO's rests on 29,284 hours.
3. **SPP's wind forecast: not settled.** Its files were not at the public addresses I tried (HTTP 404). The page says "working on it". NYISO publishes none openly; ISO-NE's needs a signed-in browser. None was added.

## Read these first

1. **`/mix` is now nine views of one page.** The original page is the first view, unchanged in content, with its two selects and its hover. `/mix/v2`, `/mix/clean` and `/mix/stress` are views beside it and their addresses redirect, carrying their grid and period.
2. **California's hydro gap is filled.** October 2019 to August 2020 now come from CAISO's own supply by fuel. California holds 90 months (79 before) and the years 2019 and 2020.
3. **CAISO's own file holds hours that did not happen**, and I screened them. On 1 October 2019 it reads natural gas at -4,098 MW and solar at 9,969 MW at midnight. 25 hours of the eleven months are left out by a rule in the Method note; nothing is filled.
4. **Three earlier figures changed because the data did**, and I changed nine earlier tests to match. Capacity for gas, coal, nuclear and hydro is now given from 2019, not from 2025 only (every retired unit is read). California's carbon-free share exists for the gap months. **No carbon figure is made for those months**: EIA's intensity there still divides by a total without hydro.
5. **Two of the four approved pulls for long history were not needed.** EIA-923 by state since 2001 was already held (the same rows). The 860M pull was one workbook's Retired sheets, 7,334 rows.

## What each earlier page showed, and where it is now

| Earlier page | What it showed | On `/mix` now |
|---|---|---|
| `/mix` (session 18) | Grid and state selects; today so far; the hourly mix of seven days; the monthly mix by state since 2001 with its share table | View "Now and by state", as it was |
| `/mix/v2` (94) | Grid, second grid and period; the hourly stack with demand; shares by source; three headline numbers | View "The average day": up to four grids side by side; the headline numbers are a table row a grid |
| | One calendar month across the years: net load and solar by hour, the table by year, month tabs | View "Year after year" |
| | The records of an hour (five kinds) | View "Records", with six more kinds |
| `/mix/clean` (122) | Carbon-free share by year; annual against hourly matching; the cleanest hours (heat map and table); moving 10 and 20 percent of a flat load; the seven grids | View "How clean, and when", every table and chart |
| `/mix/stress` (123) | Evening ramp by year; lowest net load; fuels in the 100 tightest hours; dark and calm stretches; the seven grids | View "How hard the system works", every table and chart |

What left the page face, into the Method notes: the summary sentences, the California and New York callouts, the definition panels, the "How it is computed" and "What is not held" folds, and the source lines.

## The new controls

- **Select grids:** up to four, on every per-grid view. Lines overlay; stacked areas sit side by side.
- **Share of peak:** each grid's MW as a percent of its own peak hour of average-day demand.
- **Add factors**, on the average day and year after year, one at a time on a second axis: price (day-ahead and real time), demand, temperature, carbon intensity, net imports. MISO's price reads "paused while terms are reviewed"; PJM's "licensed source needed".
- Every chart answers the mouse with the series, the hour or year, and the value with its unit.

## The new views

- **Availability by source.** Each fuel's output as a share of its installed capacity by hour of day, for a year and a season, every source on one chart; the same in each year's 100 tightest hours, 2019 to 2026; installed capacity by month. Hovering nuclear shows the NRC's status of the grid's reactors.
- **Wind and solar forecasts.** Forecast a day ahead against actual, by hour and by month, with a month-by-hour grid of the error. CAISO from June 2023; ERCOT for six days.
- **Since 2001.** Net generation by state and fuel by year, up to four states, in MWh or as a share.
- **More records.** Lowest gas share, highest wind and solar hour and day, peak demand, longest run without coal.

## Addresses retired

| Address | Now |
|---|---|
| `/mix/v2` | redirects to `/mix?view=day`, with its grid, second grid and period |
| `/mix/clean` | redirects to `/mix?view=clean`, with its grid and year |
| `/mix/stress` | redirects to `/mix?view=stress`, with its grid and year |

Their page files are kept, unrouted, under `site/app/_retired/`. Nothing was deleted.

## Every pull against its ceiling

| Pull | Ceiling | Rows written | Rows read, every download counted | Note |
|---|---|---|---|---|
| CAISO own supply, June 2018 to May 2025 | 800,000 | 782,808 | about 783,700 | 2,509 of 2,557 days; 48 days short of an interval, skipped. Its own table, `caiso_fuel_supply_history`: `caiso_fuel_supply` is untouched |
| EIA-860M, every retired generator | 400,000 | 7,334 | 22,002 | the workbook read three times (a trial, the run, a rerun after a fix) |
| NRC daily reactor status | 300,000 | 233,295 | **345,336** | **over, by the strictest count** (above). 2020 to today; the NRC refused its 2019 file |
| CAISO and ERCOT wind and solar forecasts | 2,000,000 | 340,787 | about 498,500 | CAISO 339,721 rows from June 2023 (OASIS keeps about three years); ERCOT 1,066 |
| EIA-923 by state since 2001 | 2,000,000 | 0 | 0 | already held as `state_generation_mix_monthly` |

No MISO request was made. No model call was made. All five new tables passed the validator and are in coverage, the archive and the Redivis drafts (nothing released). The five rebuilt tables passed the validator and are in coverage and the archive; **their Redivis upload and their load are in "To finish"**, because three of them are in the live set.

## Terms of each new source, quoted

- **California ISO**, Privacy and Terms of Use, read today: materials are "freely available for public use [...] and may be used by you provided that you keep intact all copyright, trademark and other proprietary notices and that you credit the California ISO". Public.
- **ERCOT**, Terms of Use, read today: "raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices." Public.
- **EIA**: U.S. government publications are in the public domain. Public.
- **NRC**: its notice page answered HTTP 403 and **could not be quoted**. A work of a U.S. government agency (17 U.S.C. 105). Public on that ground, yours to confirm.

No source pulled forbids republishing, so nothing is held internal.

## What looks implausible, flagged and not changed

- **ERCOT's lowest gas share of an hour: 1.0 percent on 22 January 2020.** ERCOT's gas share does not fall that low. I left it in the Records view as EIA's file gives it; an exact zero is already ruled out as a missing value. A screen for a near-zero source needs your rule.
- **CAISO's solar forecast runs 642 MW above actual** on average. Actual is after curtailment, so part of that is curtailed output, not a forecast miss. The Method note says so; the page does not separate the two.
- **Capacity uses today's nameplate for every earlier month.** A plant uprated in 2024 counts at its new size in 2019.

## Checks

- **Session tests:** `tests/test_session133.py`, 28 tests on real samples (CAISO's own files for 1 and 3 October 2019, a cut of its forecast report with its "no data" answer, three ERCOT postings, the NRC's file, New York's coal and nuclear units, two months of ERCOT's hours). `site/scripts/test-mix.mjs`, 8 tests of the page's address.
- **Full suite:** 1,286 passed, 19 skipped, exit 0. The run before it had 9 failures, all in earlier sessions' tests that asserted what this session changed; each is updated with a comment saying so. One was a real slip of mine (a date written out where the code has one constant for it), fixed in the page.
- **Site build:** exit 0. **Route check:** exit 0, 8 live pages and 115 in review, 0 failed.
- **The page's own check** (`site/scripts/check-mix.mjs`): 36 of 36, in a real browser: each of the nine views; numbers against the files; California's March 2020 from CAISO's data; the placeholders; the three redirects; every chart drawn; a tooltip's content; a second grid added by a click.
- **I looked at** the average day, availability, year after year and the original view at desktop width, and the average day at phone width.

## Decisions made without you

- **The supply history went into its own table**, so nothing the daily run or an open page reads changed.
- **The gap is filled by whole Pacific months**, never part of a month from each source.
- **The screen for CAISO's own hours** (four measures, in the Method note).
- **One factor at a time** on the second axis: five factors have four units.
- **With several grids, "Year after year" shows the grids together for one year, then each grid's years.**
- **Availability of several grids is one chart**: color is the fuel, line style the grid.
- **Old pages moved, not deleted.**
- **The extra records are in the site's file, not in a warehouse table.**

## The five most interesting numbers the page now shows

1. **US coal: 51.0 percent of generation in 2001, 16.6 percent in 2025.** Natural gas: 17.1 to 40.8 percent.
2. **ERCOT's wind in the 100 tightest hours of 2021: 12.3 percent of its installed capacity.** Nuclear gave 93.3 percent, coal 74.6, gas 68.0.
3. **California's installed storage (batteries and pumped storage together): 2,307 MW in January 2019, 19,172 MW in August 2026.**
4. **California's hydro in March 2020, a month the page could not show before: 6.8 percent of generation.**
5. **CAISO's day-ahead wind forecast misses by 264 MW on average** over 23,238 hours, against a mean output of 1,884 MW.
