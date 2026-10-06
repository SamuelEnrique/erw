# The energy mix by hour: the average day of each month, and the records

Two derived tables behind the page `/mix/v2` ("The energy mix", version 2, in review), built by
`warehouse/derived/mix_profile.py` for the seven ISO grids (CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP) from
January 2019. No request is made: the builder reads files the warehouse already holds.

| Table | Shape | What a row is |
|---|---|---|
| `generation_mix_hourly_profile` | series, monthly | one figure of a grid's month: a source's average MW in one local hour, a source's MWh or share, the days counted |
| `generation_mix_records` | series, hourly | one record of a grid: the hour that holds it, for the whole history or for one local year |

## Inputs

- **EIA Form EIA-930**, hourly demand, net generation, total interchange and net generation by energy source: the
  per-balancing-authority workbooks the emissions connector saved (`warehouse/raw/eia930_emissions/<run>/<BA>.xlsx`,
  sheet "Published Hourly Data", EIA's Adjusted columns). An hour is dated by its start. Public domain.
- **California from 2025-12-16T08:00:00Z:** CAISO's own supply by fuel (`caiso_fuel_supply`), by the one join of the
  warehouse ([`eia930_caiso_break.md`](eia930_caiso_break.md)). EIA's generation series for California changed on that
  day. Before it, EIA's hours, with the late ones of 2023-11 to 2025-12-02 set back. The local month that holds the
  join, December 2025, is not written: a month is never built on both sources. Demand is EIA's throughout.
- **`carbon_intensity_hourly`** (`intensity_generation`, kg CO2 per MWh), for the cleanest and the dirtiest hour.

## The sources

Eight, as the site groups them: natural gas (EIA's NG), coal (COL), nuclear (NUC), wind (WND, WNB), solar (SUN, SNB),
hydro (WAT), storage (BAT, PS, OES, UES; negative when charging) and other (OIL, GEO, OTH, UNK). From CAISO's own
data: hydro is large and small hydro, storage is batteries, other is biogas, biomass, geothermal and other; imports
are not generation and are left out.

Storage appears as a source only from when EIA itemizes it (Texas and New England from late 2024, MISO from 2025, SPP
from 2026; never for PJM, New York, or California on EIA's side). Before that, EIA holds it inside "other" or not at
all. Nothing is moved between sources.

## Which hours are used

An hour is held when three things are true:

1. its net generation is held and positive;
2. the sum of its sources is within 5 percent of that total (PJM: 15 percent);
3. no main source is blank. A main source is one that supplies at least 5 percent of the grid's generation over its
   history; it is never taken as zero.

An hour that is not held is used for nothing. Within a held hour a smaller source EIA left blank counts as zero
(storage before EIA itemized it; New England's coal when its last plant is off). A share is of the sum of the
sources, not of EIA's total.

Why each test, from what the workbooks hold:

- **The 5 percent.** In Texas from 6 to 14 December 2025 EIA's "other" repeats the batteries' output (other at
  3,281 MW in an hour with storage at 3,172), and the sources stand 5 to 8 percent above the total. Those hours are
  not held, and Texas's December 2025 is not written.
- **PJM's 15 percent.** PJM itemizes no storage. In 2,689 of its hours, most of them at 05:00 and 06:00 from 2020 to
  2024, its sources differ from its total by 5 to 15 percent, above about as often as below, with no source blank.
  At 5 percent, 36 of PJM's 93 months could be written; at 10 percent, 74; at 15 percent, 91 (January 2020 and
  June 2022 stay unwritten). The hours are kept, and the shares are of the sources. This is
  a choice, and the one in this method most open to another answer.
- **The main sources.** EIA's workbook holds no hydro for California from October 2019 to mid August 2020 (blank in
  97 to 100 percent of the hours of those months). EIA's total leaves it out too, so the sources still add up to it;
  what shows the fault is EIA's balance, demand against net generation less interchange, which is off by 9 to 15
  percent of demand in those months against 2 to 4 around them. A month built on those hours would show California
  without hydro. They are not held, and those months are not written.

A day is complete when every hour of the local day is held (23 or 25 on the days the clocks change). A month is
written when at least 90 percent of its days are complete, as the average over those days. Never filled.

## `generation_mix_hourly_profile`

Entity `iso:<grid>`; `ts_utc` the first day of the local month at 00:00:00Z; freq `P1M`.

| Variable | Unit | Meaning |
|---|---|---|
| `avg_<source>_mw_hHH` | MW | the mean, over the month's complete days, of that source in local hour HH (00 to 23) |
| `avg_demand_mw_hHH`, `avg_net_generation_mw_hHH` | MW | the same for EIA's demand and for net generation |
| `<source>_mwh`, `net_generation_mwh` | MWh | over the complete days |
| `<source>_share_pct` | percent | of the sum of the eight sources over those days |
| `days_held`, `days_in_month` | count | the complete days, and the days of the month |

`source` is `erw:generation_mix_hourly`, or `erw:generation_mix_hourly_caiso` for a month built on CAISO's own data.

**A year on the page** is not a row of the table: the builder writes it into the site's copy from the months, each
hour weighted by its month's complete days, the MWh summed and the shares taken of the sum. A year is given only when
at most one of its months is missing.

## `generation_mix_records`

Entity `iso:<grid>`; `ts_utc` the hour of the record (its start, UTC); freq `PT1H`; `x_period` is `all` or a local
year; `x_side` is `eia930` or `caiso`, the source of that hour. Key: `entity, variable, x_period`.

| Variable (and `year_` before each, for a year) | Unit | Meaning |
|---|---|---|
| `solar_share_max_pct`, `wind_share_max_pct`, `wind_solar_share_max_pct` | percent | the highest share of an hour's generation |
| `cleanest_hour_kgco2_per_mwh`, `dirtiest_hour_kgco2_per_mwh` | kg CO2 per MWh | the lowest and the highest carbon intensity of generation |

What a record counts, so that a faulty hour is not a record:

- **A share is of the hour's generation:** the sum of what its sources put out. A source below zero (batteries
  charging, a solar farm's own use at night) adds nothing to it. Against net generation, a grid whose batteries charge
  at midday would show solar above 100 percent.
- **An hour of EIA's is not ranked when EIA's own balance does not close:** its demand differs from its net generation
  less its total interchange by more than 20 percent of demand, or its total interchange is blank. Such an hour is a
  partial report: California has hours in which only its wind was reported. The hour stays in the monthly averages,
  where one hour moves little; a record is one hour. CAISO's own hours are not put to this test: each holds all of
  CAISO's sources, and EIA's demand is not CAISO's sum.
- **An hour is not ranked for carbon intensity** when its intensity is less than half of what its own natural gas
  generation alone implies at EIA's factor for gas: its CO2 and its generation do not agree.
- **A record of zero is not written** (New York's solar: EIA reports none for NYISO, whose solar is behind the meter).

The run log counts the hours each rule leaves out. Nothing is corrected or filled.

## What the tables do not hold

- Generation by plant or by zone; imports by source; anything behind the meter (rooftop solar lowers demand; it is
  not a source here).
- The months named above, and any other month with fewer than 90 percent of its days complete. As built on
  4 October 2026: California 79 of 93 months, Texas 92, New England, MISO and New York 93, PJM 91, SPP 88.
- A weather adjustment. A month's average day is that month's.
- California's December 2025 on either source.

## Rebuilding

```bash
python warehouse/lock.py run --task "the energy mix by hour" --minutes 20 -- <python> warehouse/derived/mix_profile.py --snapshot
python warehouse/derived/mix_profile.py --snapshot-only     # the site's copy alone, from the tables as they are
python warehouse/derived/mix_profile.py --out-dir DIR       # a trial: nothing in warehouse/output
```

Both tables are rebuilt whole each run: a month that no longer passes the tests does not stay from an earlier run.

## Checks

`tests/test_session94.py`: the held-hour tests on hours made for the test (a blank main source, a blank small source,
sources 8 percent off, PJM's allowance); a month with too few complete days is not written; the join month is not
written; a share of an hour's generation never exceeds 100; the site's copy equals the tables, figure for figure; a
year in the copy equals its months weighted by their days; and the page's choices, its stack and its net load, run in
Node. `site/scripts/check-mix-v2.mjs`: every number the page shows, against the site's copy, on the built site.

---

# Session 133: the one energy mix page

From session 133 the energy mix is one page at one address, `/mix`. It holds what `/mix` (session 18, `generation_mix.md`), `/mix/v2` (this note, above), `/mix/clean` (`clean_energy.md`) and `/mix/stress` (`grid_stress.md`) showed, as views of the one page, and the views the session added. `/mix/v2`, `/mix/clean` and `/mix/stress` redirect to the view each became; their page files are kept, unrouted, under `site/app/_retired/`.

The page face carries no method, by the owner's rule: a figure that is missing is a short placeholder with its reason on hover, and everything about method, gaps and sources is in this note and the three beside it. The notes that stood on the earlier pages (how a month is built, what a year needs, the California callouts, New York's misnamed nuclear hours, average against marginal carbon) are in those notes and are not repeated on the page.

## The views

| View | What it shows | Reads |
|---|---|---|
| Now and by state | the original page, as it was: today so far, the hourly mix of the last seven days by grid operator, the monthly mix by state since 2001 | the live tables `eia930_generation_latest`, `eia930_all_generation`, `state_generation_mix_monthly` |
| The average day | generation by fuel by hour, the average day of any month or year since 2019; shares by source; solar and wind at their peak | `site/data/mix/` |
| Year after year | net load by hour (the duck curve) and solar by hour for one calendar month across the years, with month tabs; the table by year | `site/data/mix/` |
| Records | the records of an hour, of a day and of a run, for the whole history and for one year | `site/data/mix/`, `site/data/mixplus/` |
| How clean, and when | carbon-free share by year, an annual purchase against the hours, the cleanest hours, moving a flat load into them, the seven grids | `site/data/clean/` |
| How hard the system works | the evening ramp by year, the lowest net load, the fuels in the 100 tightest hours, dark and calm stretches, the seven grids | `site/data/stress/` |
| Availability by source | each fuel's output as a share of its installed capacity by hour of day and season; the same in each year's 100 tightest hours; installed capacity by month | `site/data/mixplus/`, `site/data/stress/` |
| Wind and solar forecasts | forecast a day ahead against actual, by hour and by month (CAISO, ERCOT) | `site/data/mix_forecast.json` |
| Since 2001 | net generation by state and fuel, by year | `site/data/mix_history.json` |

All seven grids are on every per-grid view. MISO's and PJM's generation is EIA's (Form EIA-930), which is public; only their prices are not shown (below).

## The controls

- **Select grids:** up to four. Lines are laid over each other on one chart; stacked areas sit side by side, each on its own scale.
- **Share of peak:** each grid's MW as a percent of the highest hour of its own average-day demand in the period shown, so a small grid compares with a large one. On "Since 2001" the switch is the share of the state's generation.
- **Add factors** (the average day, and year after year): one factor at a time on a second axis, the average day of the same period.
  - Price: the grid's main hub, day-ahead (dashed) and real time (dotted), from `ercot_all_hub_prices_history` (ERCOT, from 2019), `iso_hub_prices_history` (CAISO, NYISO, SPP, ISO-NE, from September 2024) and the rolling hub tables. A real-time hour is the mean of its intervals when all are held. MISO's prices are paused and PJM's need a license: neither is read, and the page says "paused while terms are reviewed" and "licensed source needed".
  - Demand: EIA's hourly demand, already the line over the stack.
  - Temperature: the mean of the NOAA stations held for the grid (`noaa_isd_hourly`), degrees Fahrenheit; a station-hour is the mean of its observations in the hour. The table holds event windows, not every month, so many months read "not held yet".
  - Carbon intensity: `carbon_intensity_hourly`, intensity of generation, kg CO2 per MWh; California's hydro-gap hours are left out (EIA's figure divides by a total without hydro).
  - Net imports: EIA's total interchange with its sign turned (positive when the grid imports), MW.
  - A factor is drawn for a month when every local hour holds at least 20 days of it, for a year at least 300.

## California's hydro gap, and the join that fills it

EIA's file for California holds no hydro in any of the 7,869 hours from 2019-10-01T21:00Z to 2020-08-24T17:00Z (`impossible_hours.CISO_NO_HYDRO`), and EIA's total leaves it out too. A main source that is blank is never taken as zero, so none of those hours was held and the mix had no California from October 2019 to August 2020.

Session 133 pulled CAISO's own supply by fuel back to June 2018 (`caiso_fuel_supply_history`: the same file, `https://www.caiso.com/outlook/history/YYYYMMDD/fuelsource.csv`, and the same reading as `caiso_fuel_supply`, which begins in June 2025). The join:

- **The Pacific months October 2019 to August 2020 are read from CAISO's own supply, whole.** A month is never built on both sources. Demand stays EIA's, as from the join of 16 December 2025 (`eia930_caiso_break.md`).
- Hydro is CAISO's large and small hydro; storage is its batteries; other is biogas, biomass, geothermal and other; imports are not generation.
- The rows of those months carry the join's source (`erw:generation_mix_hourly_caiso`), and the page names them "from CAISO's own data".
- No cleanest or dirtiest hour is taken from those months: EIA's carbon intensity there still divides by a total without hydro.
- September 2019 and October 2020 are still not held: they fail the mix's own completeness tests on EIA's hours, for other reasons than hydro.
- The rest of the history table (June 2018 to September 2019, September 2020 to May 2025) is held and not used by the mix: EIA's hours stand there.

**The impossible-value screen (session 118), put to CAISO's own hours.** CAISO's file holds hours that did not happen: on 1 October 2019 natural gas reads -4,098 MW and solar 9,969 MW at midnight. An hour of CAISO's own supply is left out when a thermal or hydro source is more than 5 MW below zero; when solar is above 100 MW in a local hour from 22:00 to 03:59; when solar repeats the hour before to the MW while above 1,000 MW; or when its net generation fails `impossible_hours.screen` (a quarter away from the hours around it, or outside the grid's own range). 25 hours of the eleven months are left out. An hour left out makes its day incomplete, and nothing is filled.

Result: California holds 90 months in the mix (79 before), and the years 2019 and 2020.

## Installed capacity, and availability by source

- **Installed capacity** is EIA's monthly generator inventory (EIA-860M): the units operating now (`eia860m_operating_generators`) and every unit EIA lists as retired (`eia860m_retired_generators_all`, 7,334 generators retired from 1972 to 2026, pulled in session 133). Nameplate MW by the balancing authority EIA gives each unit, month by month: a unit counts from its first month of operation to the month before its retirement. Before session 133 only the last two years' retirements were held, so capacity for gas, coal, nuclear and hydro was given from 2025 only; it is now given from 2019.
- **What the inventory still cannot give:** a unit's capacity in an earlier year when it has been uprated or derated since (the inventory holds today's nameplate), and the balancing authority it was in before a change of authority.
- **Availability** of a fuel, for a year and a season: by local hour, the mean over the held hours of the fuel's output (not below zero) over its installed nameplate MW that month, percent. Seasons are by month within the calendar year: winter is January, February and December; spring March to May; summer June to August; autumn September to November. Hydro and storage are set against their capacity together, as on the stress view. A season needs 60 held hours in every hour of the day.
- **The 100 tightest hours** of a year are `grid_stress.md`'s: the held hours with the highest net load. The table now gives every fuel for every year from 2019.
- **Nameplate is not what a plant can give on a day.** Output over nameplate is low for a fuel that is dispatched (gas), for one that depends on weather, and where units are on outage.

## The note on nuclear's row

Hovering nuclear's row shows the NRC's daily Power Reactor Status for the reactors in the grid: how many, their mean power as a percent of licensed power, and the reactors with the most days below half power, for the year or season shown. `nrc_reactor_status` holds each reactor's power on the morning of each report from January 2020 (the NRC's server refused its 2019 file on 6 October 2026). It is used for this note and nothing else. A reactor is placed in a grid when its NRC name matches exactly one nuclear plant of EIA's operating inventory: 60 of the 99 units the NRC lists are in the seven grids; 4 match no plant operating now (Duane Arnold, Indian Point 2 and 3, Three Mile Island 1) and are in no grid's note, so the note for New York before 2021 does not count Indian Point.

## More records

Beside the five records of `generation_mix_records` (above), the Records view shows, from the same held hours (`warehouse/derived/mix_views.py`, written to the site's file, not to a table): the hour with the lowest share of natural gas (among hours in which gas is above zero: a zero in the file is a missing value, as New York's hour of 9 October 2024 with every source at zero shows); the highest hour and the highest day of wind and of solar; the peak hour of demand; and the longest run of hours without coal. A day is ranked only when every hour of it is held. A run is of held hours next to each other in which coal's output is not above zero, and is given only for a grid whose file reports coal at all.

## Wind and solar: forecast against actual

- **CAISO** (`caiso_wind_solar_forecast`): OASIS report SLD_REN_FCST, the day-ahead forecast (market run DAM) and actual generation (ACTUAL), hourly, for the trading hubs NP15, SP15 and ZP26, added up; an hour needs all three hubs. OASIS keeps the report for about three years: the table begins 1 June 2023 (wind's actual from February 2024). **Actual solar is after curtailment**, so the solar forecast runs above it (a mean of 642 MW above over 29,284 hours): part of that "error" is output that was curtailed, not misforecast.
- **ERCOT** (`ercot_wind_solar_forecast`): reports NP4-732-CD (wind) and NP4-745-CD (solar), system-wide. The forecast is ERCOT's short-term forecast (STWPF, STPPF) for the hour from the newest posting published at least 24 hours before the hour began. **ERCOT's public list keeps about a week of postings**, so the table holds 146 hours with both a forecast and an actual (30 September to 6 October 2026). It grows by a day for each day the refresh runs; until then ERCOT's figures rest on six days and its by-month chart is not drawn.
- **Error** is forecast less actual on the hours that hold both. By local hour and by month: the mean actual, the mean forecast, the mean error and the mean absolute error, MW.
- **The other grids, checked on 6 October 2026:** NYISO's public server lists no wind or solar forecast file. ISO-NE's seven-day wind forecast files answered HTTP 403 to a request that was not a signed-in browser. SPP's resource forecast was not found at the public file addresses tried (HTTP 404); its list needs a second look. None was added. MISO is paused; PJM needs a license.

## Since 2001

`state_generation_mix_monthly` (EIA-923, already held) added up by calendar year, state and fuel group; a year is drawn when it holds twelve months. No new pull was needed: the approved one would have read the same rows.

## Terms of the sources session 133 added, quoted

**California ISO** (supply history; wind and solar forecast), Privacy and Terms of Use (caiso.com/privacy-terms-of-use, read 6 October 2026): materials and information on the website are

> freely available for public use consistent with the general policies of the Public Records Act [...] and may be used by you provided that you keep intact all copyright, trademark and other proprietary notices and that you credit the California ISO when using such materials and/or information.

License: public, credited to the California ISO.

**ERCOT** (wind and solar forecast), Terms of Use (ercot.com/help/terms, read 6 October 2026):

> raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices.

License: public.

**EIA** (the retired generators): U.S. government publications are in the public domain (EIA, Copyrights and Reuse). License: public.

**U.S. Nuclear Regulatory Commission** (reactor status): the NRC's own notice page (nrc.gov/site-help/copyright.html) answered HTTP 403 on 6 October 2026 and could not be quoted. The reports are a work of a U.S. government agency, which U.S. law places outside copyright (17 U.S.C. 105). License: public on that ground, **for a person to confirm on the NRC's page**. The data is used only for the note on nuclear's row.

## The refresh

`warehouse/refresh_mix.sh`: the daily pulls (CAISO's last days of forecast and actual, ERCOT's week of postings, the NRC's last 365 days), the validator and the builders, each under `warehouse/health.py`. Written, not scheduled. The two histories (CAISO's supply to May 2025, the retired generators) are not pulled again: one is closed, the other changes monthly with EIA's inventory and is read with it.
