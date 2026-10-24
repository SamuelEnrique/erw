# The price years: what each economics page's figure is under every window of years held

Tables: `price_years_by_window`

One derived table, `price_years_by_window`, built by `warehouse/derived/price_years.py` (session 357, the chain of
20 October 2026). No request is made. It answers the first weakness each economics pack ranks (section 6, item 1,
"the years ahead"): every page prices its project on the last twelve months, and a reader could not see what the same
project would have earned, or the same load paid, under any other year held, or an average of years, without the page
computing it.

**Its name.** The chain's prompt calls it `price_years`; the validator's rule for a series table needs three parts in
the name (`docs/datastandard.md`, "File naming"), so the table is `price_years_by_window`. Everything else in this
note calls it the price years.

## The table's shape (written before the table, for the code machine)

Shape: `series` (`docs/datastandard.md` v0). One row per tool, grid, price point, configuration and window. Partition
column `market` (the grid id). Key `(entity, variable, ts_utc)`.

| Column | What it holds |
|---|---|
| `entity` | the price point the page reads, `<grid>:<hub or region>` as the page's own table names it: `ercot:HB_HUBAVG`, `caiso:TH_SP15_GEN-APND`, `spp:SPPNORTH_HUB`; for the datacenter every region the page offers (`ercot:LZ_NORTH`, `ercot:HB_WEST`, `caiso:TH_NP15_GEN-APND`, ...) |
| `variable` | `<tool>_<configuration>_<window>`, the three parts below joined by `_` |
| `ts_utc` | the window's first month, the first day of the grid's local month at `00:00:00Z` (the tools' monthly tables' convention, Decision 11) |
| `value` | the figure, in `unit` (below). Never empty: a window the page cannot price has no row |
| `unit` | `USD/kW-year` for the battery and the generator (revenue per kW of rated power or nameplate, a year; the peaker's is its margin over fuel and variable O&M); `USD/MWh` for the datacenter (what the load paid per MWh it consumed) |
| `freq` | `P<n>M`: the calendar months from the window's first month to its last, both included |
| `geo`, `market`, `node` | the grid's state code(s), the grid id (`ercot`, `caiso`, `spp`), the hub or region name as the page writes it |
| `source`, `source_url`, `retrieved_at`, `vintage` | `erw:price_years`, this note's address, when the table was built; `vintage` empty |
| `x_tool` | `battery` (What a battery earns, `/cost-of-power/battery`), `generator` (What a generator earns, `/cost-of-power/seller`), `datacenter` (What a datacenter pays, `/cost-of-power`) |
| `x_grid` | the grid id, as `market` |
| `x_config` | the configuration (below) |
| `x_window` | the window id (below) |
| `x_window_kind` | `year`, `last_12`, `avg_3y`, `avg_7y`, `all`, `all_less` |
| `x_left_out` | the stress events taken out, their ids joined by `+`, or `none` |
| `x_from`, `x_to` | the window's first and last month, `YYYY-MM` |
| `x_months` | the months counted: the months the page's own rule holds inside the window (a battery or generator month held from 90 percent of its days or hours; a datacenter month complete from 95 percent of its hours) |
| `x_complete` | `true` when the window is whole by the page's rule (a calendar year with all twelve months counted; every other window is written only when whole, so `true`); `false` for a calendar year held in part (the year the data begin, and the running year) |

### The tools and their configurations

| Tool | Grids | Configurations (`x_config`) | The page's figure |
|---|---|---|---|
| `battery` | ERCOT (`ercot:HB_HUBAVG`, from 2018), CAISO (`caiso:TH_SP15_GEN-APND`, from August 2023), SPP (`spp:SPPNORTH_HUB`, from September 2024; the page shows it in the internal view) | `<strategy>_<N>h`: `foresight_2h`, `foresight_4h`, `foresight_8h`, `dayahead_2h`, `dayahead_4h`, `dayahead_8h` | total revenue, energy and ancillary services, per kW a year (`lib/batterystack.ts`) |
| `generator` | ERCOT, CAISO, SPP at the page's main hubs | `solar`, `wind`, `battery` (energy only, 4 hours, as the page), `peaker` | revenue per kW of nameplate a year; the peaker's margin over fuel and variable O&M (`lib/merchant.ts`, `lib/seller2.ts`) |
| `datacenter` | ERCOT (fourteen regions: eight load zones, six hubs), CAISO (three), SPP (two) | `<run>_<market>`: `flat_rt`, `hours_rt`, `share_rt`, `shift_rt`, `flat_da`, `hours_da`, `share_da`, `shift_da` at the page's defaults (off in 100 hours a year; off in 5 percent of hours; 20 percent of each day's energy shifted) | what the load paid per MWh it consumed; a flexible load under the page's rule, decided from day-ahead prices (`lib/datacenter.ts`, `monthsRuled(..., "forecast")`), which is the page's own figure |

NYISO, ISO-NE and MISO are not in the table: from 21 October 2026 their rows read "license needed"
(`warehouse/metadata/license_status.csv`), and MISO's pulls are paused. PJM's prices are licensed and are never here.
A grid joins the table when its license allows it.

### The windows

| `x_window` | `x_window_kind` | What it is |
|---|---|---|
| `year_<YYYY>` | `year` | one calendar year, every year with a month counted; `x_complete` says whether all twelve are |
| `last_12` | `last_12` | the page's own last twelve months (each page's `lastTwelve`): the page's default and the figure its headline shows today |
| `avg_3y` | `avg_3y` | the last three full calendar years held, averaged a year (written only when all three are full) |
| `avg_7y` | `avg_7y` | the last seven full calendar years held, averaged a year (written only when all seven are full: on 20 October 2026, ERCOT for all three tools, and the datacenter's day-ahead load at SPP's South hub, held from 2019) |
| `all` | `all` | the whole span held, by the page's own rule: the battery's reader window at its default (every held month, the twelve-calendar-month mean); the generator's "every full year held"; the datacenter's every complete month |
| `all_less_<event>` | `all_less` | `all` with one stress event's days taken out of the months they fall in (`x_left_out` names it) |
| `all_less_events` | `all_less` | `all` with every stress event of the grid taken out |

The stress events are the battery page's leave-out boxes, read from `battery_stack_stress_daily`: ERCOT `uri_2021`,
`elliott_2022`, `ercot_heat_2023`; CAISO's events made by rule from its own system-wide notices
(`caiso_notices_<YYYYMMDD>`). SPP has none. A variable then reads, for example,
`battery_foresight_4h_last_12`, `generator_solar_year_2021`, `datacenter_flat_rt_all_less_uri_2021`.

How a page reads it: the row whose `entity`, `x_tool`, `x_config` and `x_window` match; the figure is `value`, the
months counted `x_months`, the span `x_from` to `x_to`. A window without a row is not held for that configuration: the
page says so and shows no number.

## How it is computed (session 357)

`warehouse/derived/price_years.py` reads the battery's rows as the battery page reads them
(`app/cost-of-power/battery/read.ts`): ERCOT's and CAISO's rows of `battery_stack_monthly` and
`battery_stack_stress_daily` from the live set, with the anon key; SPP, a grid in review, from the committed
`site/data/battery_stack_review.json`. The live set is read, not this machine's copy of the two tables, because the
daily run loads the live set and it can be newer: on 20 October 2026 it held CAISO's 2 November 2025 (the autumn
clock change), which this machine's copy left out, and CAISO's 2-hour battery read USD 61.29 per kW over the last
twelve months on the page against 61.11 from this machine's copy.

It hands them to `site/scripts/price-years.mjs`, which imports the pages' own modules and runs them:

- **battery**: `monthsOf`, `lastTwelve`, `sumOf`, `yearStream`, `years`, `windowAverage` with `eventMonths` and
  `stress` (`lib/batterystack.ts`). A calendar year is `yearStream` (the held months' sum); the averages and the whole
  span are `windowAverage` over the years named, the page's own reader window; a left-out event takes its days out of
  the months they fall in (`windowMonths`), exactly as the page's leave-out boxes do.
- **generator**: `monthsOf`, `years`, `spanOf`, `spans`, `fullYears` (`lib/seller2.ts`) over `months`
  (`lib/merchant.ts`) on `site/data/merchant_snapshot.json`, the page's own snapshot. A left-out event takes the
  snapshot's own daily figures of the event's window days (as `stress()` in `lib/merchant.ts` reads them: the asset's
  day, the peaker's day through `peakerOver`) out of the full years' sum; the years averaged over stay the page's full
  years. The snapshot holds daily figures for ERCOT's three events only, so CAISO and SPP have no left-out rows. A
  window day without its figure stops the window (no row): it is never taken out by guess.
- **datacenter**: `monthsRuled(files, region, buy, x, "forecast")`, `years`, `lastTwelve`, `span`
  (`lib/datacenter.ts`) over `site/data/datacenter/<grid>_<year>.json`, the page's own figure for a flexible load (the
  rule decided from day-ahead prices) and the flat load's. A left-out event takes the event days' hours out of the
  complete months' sums: each hour's price times the load's weight in it, and the weight, as the page's own run set
  them (`Ruled.prices`, `Ruled.weights`); the run is not redone without the days, so a flexible load's yearly budget of
  hours off is as the page spent it. The event days are the battery page's (`battery_stack_stress_daily`), by the
  grid's local date; the datacenter counts hours in standard time.

The page's last twelve months is the default window, and the run fails unless every one of them equals the page's
own figure to half a cent: the battery's against its check-key stat (`stat(..., "l12_kw:total")`), the generator's
against `spans().twelve`, the datacenter's (the main region, flat, real time) against `span(lastTwelve())`; with
`--live`, the battery's twelve configurations again against a second read of the live set
(`site/scripts/price-years-live.mjs`). The proofs are written into the table's header.

## The first build (20 October 2026)

2,754 rows: battery 234, generator 108, datacenter 2,412. 45 proofs, all equal. Figures the packs quote, read from
the table: the battery's default (ERCOT, 4 hours, perfect foresight) USD 81.40 per kW over the last twelve months,
255.08 a year over 2023 to 2025, 614.58 over every year held, 269.52 without Uri's days (the pack's 269.68 left out
the whole of February 2021, the page's rule of before session 296), 739.80 over the seven full years 2019 to 2025;
the generator's ERCOT solar 59.85, 102.24 (three years), 130.80 (seven), from 59.46 (2024) to 217.53 (2021); the
datacenter's flat load at `LZ_NORTH` 33.73, from 21.68 (2016) to 150.61 (2021), 43.00 over every complete month held
and 33.16 without Uri's days.

    python warehouse/lock.py run --task price-years -- <python> warehouse/derived/price_years.py --live

## Checks against the table (session 2466)

Counted from `warehouse/output` by `runs/c119/s2466/check_tables.py`: `price_years_by_window` 2,754 rows, 23 columns (`x_tool`, `x_grid`, `x_config`, `x_window`, `x_window_kind`, `x_left_out`, `x_from` and the rest among them), 19 entities, 470 variables, 13 freq values, each a window's length (P4M to P141M), 2015 to 2026, units USD/MWh and USD/kW-year, the markets `caiso`, `ercot` and `spp`, no key given twice, every value a number. The Tables line was added so that the finder of held tables with no note sees it.
