# Where and when power is spare (`/curtailment/where-when`)

Session 8014, chain 581 (part C), 20 November 2026. Builder: `warehouse/derived/where_when.py`, a step of the data machine's daily run (`dm_where_when`, held by `dm_test_where_when`). Contract: `docs/state/page_files_curtailment.md`. View: `site/app/curtailment/where-when/page.tsx`, reading `site/lib/wherewhen.ts`. License: public. The page `/curtailment` as it is does not change.

## What exists, read first (session 8014)

- Curtailment the warehouse holds, and to what place: CAISO, the whole system, by five minutes since 2019 with CAISO's reason (local or system) (`caiso_curtailment_intervals`, rolled up by month and hour of the day in `caiso_curtailment_profile`), and by day since 2014 (`caiso_curtailment_daily`); SPP, the whole system, by day since March 2014 with SPP's reasons (economic, manual, redispatch) (`spp_curtailment_daily`); both by month in `iso_curtailment_monthly`. All public. ERCOT publishes no curtailment figure; the curtailment page shows the ERW's arithmetic of ERCOT's limits against output, labelled as the ERW's (`ercot_estimate_page.py`). No curtailment figure of MISO (paused), PJM, NYISO or ISO-NE is held. No operator publishes curtailment by node or zone in a table the warehouse holds.
- Hours priced below zero: `free_energy.py` writes, for every hub and zone of a grid whose prices a page may show, the hours below zero and under USD 5 over the last month and the last twelve months, with a month by hour heatmap of the twelve months (`site/data/curtailment/free_energy.json`, the curtailment page's "Where free energy is").
- The curtailment page already draws CAISO by day, month, hour of the day and reason; SPP and ERCOT by day and month; the share of available output; free energy; and what the curtailed energy was worth.

What is new here, and nothing else: the hour by month grid over every year held (not the last twelve months only), for curtailment and prices in one view; each place's trend by year; the places ranked; two places side by side.

## Inputs and rules

| Part | Source | Rule |
|---|---|---|
| CAISO curtailment | `caiso_curtailment_profile` (via `site/data/curtailment_profile.json`, the same figures) | MWh by month and hour of the day (Pacific clock time), solar and wind; a year's total only when 90 percent of its days and all twelve months are held |
| SPP curtailment | `spp_curtailment_daily` | MWh summed by month, by SPP's variables; SPP publishes by day, so no hour of the day; a year's total only when 90 percent of its days are held |
| Hours below zero | the public hub and zone price tables `free_energy.py` reads, with its reader (`price_compare.read_prices`, `datacenter_page.hourly_side`) | for each year: real time where the place holds 95 percent of the year's hours in real time, otherwise day-ahead; an hour of real time is the mean of its four 15-minute prices; each hour counted once; months and hours in the grid's standard time. A year's share below zero only when 95 percent of its hours are held |
| Held prices | `warehouse/metadata/license_status.py`, `paused_sources.csv` | NYISO and ISO-NE (license needed), MISO (paused), PJM (no price held): named with their places, no number |

A cell's share below zero is the hours below zero over the hours held, for that month and hour of the day. With "every year held", the counts of every year are summed before the share is taken. Nothing is estimated or filled.

## Run

`python warehouse/derived/where_when.py` (about 35 seconds); `--out-dir DIR` writes elsewhere for a trial.

## Checks (20 November 2026)

- CAISO's yearly totals equal the sum of `caiso_curtailment_profile`'s months for the same year (the test holds 2025).
- Each price place's month by hour counts of a year sum to its yearly count of hours below zero, and no cell holds more hours below zero than hours held (the test holds every place and year).
- No grid whose prices the license holds is drawn; ERCOT's estimate is not drawn (the test).

### Decisions (session 8014)

| Key | Decision | Default |
|---|---|---|
| `as-published` | The operators' curtailment and the public prices as published; counts, sums and shares only; no advice | as published |
| `who-publishes` | CAISO by hour; SPP by month; ERCOT none drawn | CAISO, SPP |
| `held-prices` | NYISO, ISO-NE, MISO and PJM named with no number | named, not drawn |
| `hour-rule` | Real time where 95 percent held, else day-ahead; whole years only | free_energy.py's rule |
| `first-place` | Opens on CAISO, solar, newest whole year, no second place | CAISO |
| `shading` | Each grid shaded on its own scale | own scale |
| `clock` | CAISO in Pacific clock time; prices in standard time | as each source |
| `ranking` | Largest share below zero first; averages not ranked | largest first |
