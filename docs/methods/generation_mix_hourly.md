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
- **Storage is batteries, flywheels, compressed air and pumped storage together**, as EIA's technology groups them; hydro is conventional hydro.
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

## "Select grids" on every view (session 168, 9 October 2026)

The owner's instruction of 8 October 2026: the control stands on every view; a view that can use the choice uses it; a
view that cannot shows it greyed, with a hover that says why. What each view does (`site/lib/mixpage.ts`, `gridUse`):

- **The seven views that always had it** (the average day, year after year, records, how clean, how hard, availability
  by source): as before. They compare the grids chosen side by side, four at most, ERCOT alone as they open.
- **Now and by state** and **Wind and solar forecasts**: they open with every grid, as they did, and every chip is on.
  A click on a grid shows that grid alone; then a click adds or takes off a grid, and a click on the only grid left
  shows every grid again. Now and by state draws each grid chosen (its "today so far" and its last seven days, EIA-930),
  and its operator list gives way to the choice until every grid is on again; the state's monthly mix is by state and
  stays as it is. The forecasts draw the forecast of each grid chosen that has one, and list the grids chosen that
  have none.
- **Since 2001**: it cannot use a grid. EIA's record since 2001 is kept by state, and a grid's area does not follow
  state lines, so the control is greyed and its hover reads "This view is by state: EIA's record since 2001 is not kept
  by grid." The states are chosen with "Select states", as before.

The grids chosen go in the address (`grids=`) and are carried from view to view; nothing chosen writes nothing, so
every opening address is as it was. With every grid on, each of the three views shows exactly what it showed before
(compared as text before and after, 9 October 2026: only the control's row was added).

## The Mix tab's energy mix, keyed, hourly and by month (chain 077, 23 October 2026)

Sessions 1152, 1155, 1158, 1159 and 1160 of chain 077. The block "<grid>: hourly mix, last 7 days" on the Mix tab of
`/grid` opens with a server-drawn panel, `data-grid-panel="grid_mix_<grid>"` (`site/components/grid/MixFigures.tsx`,
the figures computed by `site/lib/mixHourly.ts`, read in `site/components/grid/MixView.tsx`). Every figure in it is a
check key that `site/scripts/check-values.mjs` recomputes, and each has a one-line hover tip naming its table, entity,
variables and window.

**The hourly view (the opening one).**

- **The tables.** `eia930_all_generation` (EIA-930 by balancing authority, `eia930:<BA>`, nine days read from the live
  set's 35-day window) and `eia930_all_demand`. There is no hourly generation by sub-region: EIA-930 publishes
  sub-region (sub-BA) data for demand only (`eia930_subba_demand_hourly`, not in the live set), and generation by
  balancing authority only. "generation_mix_hourly" is the name of this note and of its builder, not of a table.
- **The window of the headline: the 24 hours that end with the newest hour held.** An hour is held when its
  `net_generation_mw` is. The panel says how many of the 24 are held ("24 of 24 hours held"). The table is loaded by
  whole UTC days, so the newest hour is the last hour of the newest complete day; the chart runs on to it when it is
  later than the last complete day.
- **Net generation and each fuel.** The 24 hours' net generation in MWh,
  `series_sum|eia930_all_generation|net_generation_mw|<start>|<end>|eia930:<BA>`; each fuel group's MWh,
  `series_sum|eia930_all_generation|<variables>|<start>|<end>|eia930:<BA>`, where `<variables>` is every EIA variable
  of the group that the window holds, sorted and comma separated (wind is `net_generation_wind_mw` and
  `net_generation_wind_with_battery_mw`; check-values reads a comma list with `in.(...)`; a key without a comma reads
  as it always did); and its share, `calc|pct|<the fuel's key>|<the net generation key>` (each inner `|` written `~`).
  The groups are the Grid tool's (`components/mix/Now.tsx`): natural gas, coal, nuclear, wind, solar, hydro, storage
  and other.
- **The share's two denominators.** The headline's share is of `net_generation_mw` over the same hours, as the task
  asked; the chart's hover card gives each fuel's MW and its share of the sum of the fuels drawn at that hour (this
  note's rule for a share since session 133). The two can differ by the gap between EIA's total and its sources (on
  ERCOT's fixture of 20 October 2026 the eight headline shares add to 99.9997 percent).
- **The peak hour is the demand peak.** The hour of highest `demand_mw` in the same 24 hours,
  `series_max|eia930_all_demand|demand_mw|<start>|<end>|eia930:<BA>` (check-values proves it is the highest of the
  window), named with its MW in the panel and marked on the chart by a dashed accent line ("Peak demand, HH:MM UTC",
  also in the hover card). It is not the peak of net generation, and not the "tightest hours" of `grid_stress.md`
  (the highest net load): see that note's chain 077 section.
- **The newest hour, and its age said against the drawing clock.** The newest hour held is a key,
  `series|eia930_all_generation|eia930:<BA>|net_generation_mw|<hour>`; its age is whole hours from the hour's end to
  the time the page was drawn (`renderTime()`; the page is cached up to an hour, so the age can be up to an hour
  short). The age is not a key: the clock is not a table.
- **The chart's stack.** Since session 1152 each stacked band is drawn from the running sum of its own side of zero
  (`site/components/TimeChart.tsx`): when batteries charge (storage below zero) the band is drawn below the axis and
  the bands above start from zero, where until then the band after storage started from storage's negative value and
  drew a wedge across the axis. A stack whose values are all held and positive draws as before; only the Grid tool's
  stacked charts use `stack`. `tests/test_session1152.py` pins the base.

**The monthly view (`mixp=month`, the chips "Hourly, last 7 days" and "By month").**

- **The table.** `generation_mix_hourly_profile` (this note, above), entity `iso:<grid>`: the grid's last 24 months,
  stacked, each fuel's MWh and share on hover. Under it, the newest month's MWh and stored share,
  `series|generation_mix_hourly_profile|iso:<grid>|<coal, hydro, natural_gas, nuclear, other, solar, storage, wind>_mwh|<month>`
  and `series|generation_mix_hourly_profile|iso:<grid>|<coal, hydro, natural_gas, nuclear, other, solar, storage, wind>_share_pct|<month>`
  (and `net_generation_mwh`, `days_held`, `days_in_month` for the month), and the MWh of the twelve calendar months to
  it, `series_esum|generation_mix_hourly_profile|iso:<grid>|<fuel>_mwh|<from>|<to>`. A month of the twelve that the
  build did not write is named on the face (ERCOT: 2025-12). No twelve-month share is drawn.
- **The Lower 48** has no monthly view by grid (the table holds the seven ISO grids): its panel says "not built for the
  Lower 48", and the state monthly view below it is its monthly mix.
- **`mixp` in the address** is a field of the mix page's choice (`site/lib/mixpage.ts`), written only on "Now and by
  state" and only when it is `month`, so every older address opens as it did.
- **CAISO's alert months** (session 1155): a month of the chart that holds an Energy Emergency Alert or a Flex Alert day
  is marked, with one count of the alert days of the months drawn; the rule and the keys are in
  `california_reliability.md`, "On the Grid tool: the alert state".

**California's hourly mix stays withheld, said as the session 118 ruling.** EIA-930's generation for California is not
the series it was since the join day (`eia930_caiso_break.md`), and the hourly view reads only EIA-930, so for CAISO
the panel draws no hourly figure: it carries the two chips and a line that the monthly mix, CAISO's own data since
January 2026, is under "By month". The Now block says it in the withheld panel's words ("Not shown: ...",
`site/components/CaisoMixWithheld.tsx`); it is not "license needed": no grid of these tables is held for a license.

**The tables at 390 pixels, and the brand (sessions 1158, 1159).** The panel's two tables scroll inside a named frame a
keyboard can reach (`scrollRegion`, `site/lib/cells.ts`, as `ToolTable` draws it); each fuel's name is its row's header
cell; the colour swatch is hidden from a screen reader. Their rows are the shared table's (about 33 px) by one rule in
`site/app/tokens.css` scoped to `[data-grid-panel]`. A fuel with no share leaves its cell blank (a ruling is asked:
"not held").

**The reads made smaller (session 1160), the same rows drawn.** The Now view's mix (the first block of every Mix tab)
reads the newest hour holding the grid's total in its 34-day window (one row), then the grid's rows from that hour on
(`site/lib/gridReads.ts`, `latestHour`), where it read every variable of the 34 days; for CAISO, whose EIA-930
generation the view does not draw, nothing is read. "Generation mix, as a table" (`components/grid/Conditions.tsx`,
`MixTable`) no longer reads each region's station temperatures, which it does not draw (`loadConditions(ba, day,
{ weather: false })`). A grid's Mix tab went from 66 to 90 requests to 54 to 76. The node test
`site/scripts/test-grid-reads.mjs` proves on real rows that the same hour, total and fuels are drawn.

Decisions (chain 077):

- **The peak is demand's, not net generation's**: a trader's peak is the load peak (prices, reserves, the four
  coincident peaks and the evening ramp key off demand), and net generation differs from it by the grid's net imports.
  The owner may ask for the net load peak (demand less wind and solar) instead; it would be a new key, not a change.
- **The headline ends with the newest hour held, not with the clock**, and says how many of its hours are held; no hour
  is filled. The owner may ask for "yesterday, local day" instead.
- **The age is said against the drawing clock, not as a key**, as session 266 did for the network (`data-network-clock-lag`).
- **The monthly view shows the newest month's stored share and the twelve months' MWh, no twelve-month share**: the
  table's shares are of the sum of its eight sources, and a share of two sums would be a third convention.
- **The stacking fault was fixed in `TimeChart`, not around it**: the look on production was a drawing fault, not a
  design.
- **`series_sum` takes a comma list, rather than a new key kind**: no existing key holds a comma, so no existing key
  changes what it computes. `site/scripts/check-methods.mjs` reads such a key as a figure of each variable (session
  1162).

## The Mix tab's last unkeyed figures, and the views drawn from committed files (chain 078, 24 October 2026)

Session 1166 keyed what session 1151 listed as still without a key on `/grid`. No figure's text moved: each figure is
wrapped in its key, with a one-line source in its hover tip (dotted, as the tool's panels write theirs).

**The Mix tab's "Yesterday"** (`components/grid/Conditions.tsx`, the arithmetic moved as it stood into
`lib/gridYesterday.ts`, which `site/scripts/check-values.mjs` imports to recompute the keys):

- The forecast's miss at the peak, MW: `fmt|pm0|calc|diff|<demand>|<forecast>`, the two `series` keys of
  `eia930_all_demand`'s `demand_mw` and `demand_forecast_mw` in the peak hour ("~" for "|"); written "+" at or above
  zero, else a minus sign, then the whole size (`pm0`, `site/scripts/check-format.mjs`).
- Its percent of demand: `fmt|f1|calc|diffpct|<demand>|<forecast>`, a new op of calc, (A less B) over A, times 100,
  written to one decimal (`f1`, `toFixed(1)`).
- The day's mean absolute miss: `fmt|f1|fcerr|mape|eia930:<BA>|<from>|<to>`, and its hours `fcerr|hours|eia930:<BA>|<from>|<to>`
  (a new kind `fcerr|`: the mean over the hours that hold both of the miss's size over demand, in percent; the UTC day
  from `<from>` to `<to>`).
- The degree days: `fmt|f1|degday|cdd|nws:<station>|<day>` and `fmt|f1|degday|hdd|nws:<station>|<day>` (a new kind
  `degday|`: the UTC day's mean of its 24 hourly `weather_obs_hourly` `temperature_f` rows, less 65 F, or 65 F less it; a
  day with another count of hours has none, as the page writes "not computed").

**"Generation mix, as a table"** (`Conditions.tsx`, `MixTable`): each fuel's share of the day,
`fmt|f1|calc|pct|series_sum~eia930_all_generation~<the group's variables, comma separated>~<day>~<next day>~eia930:<BA>|series_sum~...~net_generation_mw~...`:
the group's variables are those the day's rows hold (Other: every variable no other group takes).

**"Hours held"** (`components/grid/YourGrid.tsx`, the 30-day mix table): `series_n|eia930_all_generation|<variable>|<start>|<end>|eia930:<BA>`
(session 1154's kind: the distinct hours of the rows).

**CAISO's notices** (`components/grid/Reliability.tsx`): "The table holds N notices" is `awe|rows|any` and "the latest
on <day>" is `awe|newest|any` (two new forms of the `awe|` kind, `lib/caisoAlerts.ts` `aweValue`: every row of
`caiso_grid_emergencies`, and the newest `event_date` of any).

**The views drawn from committed files** (`components/mix/views.tsx`, the Mix tab's views and the Clean tab's "How clean,
and when"): a new kind `file|<data file>|<path>` (`site/scripts/check-file.mjs`), always behind `fmt|<form>|` (`n0`,
`n1`, `n2`, `sn0`, `sn1`: the page's own functions, `lib/mixpage.ts`, with a sign above zero for the last two). The
recomputation reads the file in the repository (`site/data/`), not the database; where the file is a build of a
live-set table, check-values then compares the file's value with that table's row on a line of its own, "same" or
"DIFF", counted apart and not a failure of the run (`grid_stress.md` gives the decision). The figures keyed:

- "How clean, and when" (`site/data/clean/<grid>.json`, `clean_energy_summary`, the year's row `year_<variable>`, P1Y):
  the table "Carbon-free share and hours" (`year_carbon_free_share_pct`, `year_carbon_free_share_flat_pct`,
  `year_hours_cf_ge<50, 75, 90>_pct`) and "The seven grids" (`year_carbon_free_share_pct`, `year_hours_cf_ge50_pct`,
  `year_match_mix_100_energy_pct`, `year_shift20_carbon_change_pct`, `year_shift20_cost_change_pct`). A grid held for a
  license (ISO-NE, MISO and NYISO, `lib/license.ts`) is not keyed: its blocks say "license needed" as before.
- "The average day" (`site/data/mix/<grid>.json`, `generation_mix_hourly_profile` for a month; a year is the builder's
  sum of its months and is checked against the file alone): the table "Shares of generation by source"
  (`<coal, hydro, natural_gas, nuclear, other, solar, storage, wind>_share_pct` and `_mwh`), and in "Solar and wind at
  their peak hour" the largest source's share, solar's and wind's shares and `days_held`.
- "Records" (`generation_mix_records`, by the record's variable and hour): `<solar_share_max_pct, wind_share_max_pct,
  wind_solar_share_max_pct, cleanest_hour_kgco2_per_mwh, dirtiest_hour_kgco2_per_mwh>`, since the first year and in the
  year chosen (`year_<solar_share_max_pct, wind_share_max_pct, wind_solar_share_max_pct, cleanest_hour_kgco2_per_mwh,
  dirtiest_hour_kgco2_per_mwh>`); and the records of `site/data/mixplus/<grid>.json` (`warehouse/derived/mix_views.py`,
  a file only: `file|` records `<demand_hour_max, gas_share_min, no_coal_run, solar_day_max, solar_hour_max,
  wind_day_max, wind_hour_max>`).
- "Wind and solar forecasts" (`site/data/mix_forecast.json`, a file only): the hours held, and in the table by month
  the hours, the mean actual and forecast, the mean error and the mean absolute error (`file|` `n`, `actual`,
  `forecast`, `bias`, `mae`).
- "How hard the system works" and the tightest hours of "Availability by source": `grid_stress.md`.

Not keyed, and why: figures the page computes from the files' arrays rather than reads (the duck curve's midday low,
evening high and ramp, solar's and wind's peak MW and hour, the availability's daily mean, lowest and highest hour,
the cleanest and dirtiest hour of each month, the history by state's shares and million MWh): each needs the page's
own rule as a key kind (a later session); the clean view's large tables (the annual purchase against the hours, moving
a flat load by year: up to nine columns a year); the error as a share of the mean actual (a ratio the page computes).
On 24 October 2026, for ERCOT and CAISO, 573 keys were drawn by these views on a server render
(`site/scripts/test-grid-file-keys.mjs` recomputes every one from the files); 370 of them are builds of a live-set
row, and all 370 were the same as the table.

Every chart of these views answers a hover with its value, unit and hour or period (`components/svgchart.tsx`: the
category charts name the hour or the year and each series' value and unit; the heat maps "row, column: value unit").

Decisions (chain 078):

- **A form in the key, rather than a looser text rule**: a figure written to one decimal or with a sign is keyed as
  `fmt|<form>|<key>`, and check-values holds its text to the recomputed value in that form, exactly. No existing key
  changes what it computes or how its text is read.
- **The arithmetic moved, not copied**: the page and check-values call the same functions (`lib/gridYesterday.ts`,
  `aweValue`), so the key is the page's rule; the node test holds them to the expressions that stood in the page.
- **The clean view's table of the seven grids keys only the grids not held**: it drew, and still draws, the held grids'
  figures, which the license rule says should read "license needed" (a ruling for the owner; no figure was moved).
- **The headline tables, not every cell**: a view's top numbers and its first tables are keyed; the large tables below
  them wait for a pass of their own.

## The figures on the page and their keys

Each number `/grid` shows carries its key (`site/components/Num.tsx`), which `site/scripts/check-values.mjs` checks against the live set and `site/scripts/check-methods.mjs` against this note (session 409). The keys the sections above do not name:

- `eia930_generation_latest`, `net_generation_mw` (a `series_esum` key): on the Mix tab, the block "today so far": the sum of the hourly net generation of the latest UTC day held, over its complete hours, in MWh.
- `state_generation_mix_monthly`, `net_generation_<natural_gas, coal, nuclear, wind, solar, hydro, other_renewables, oil_and_other, not_itemized>_mwh`: the block "monthly mix since 2001", the table's last column: each fuel group's MWh in the newest month held for the state chosen (the United States, `eia:US`, unless another is chosen).
- `eia930_all_generation`, `net_generation_<coal, geothermal, hydro, natural_gas, nuclear, oil, other, other_storage, pumped_storage, solar, solar_with_battery, unknown, unknown_storage, wind, wind_with_battery, battery>_mw`: the latest hour's blocks that open the Mix tab (`components/grid/NowView.tsx`), "The mix in that hour": each source's net generation in MW, as EIA names it, in the latest hour that holds the total; the largest of them is also named in the tab's first sentence.
- `eia930_all_demand`, `demand_forecast_mw`: the block "yesterday" under them (`components/grid/Conditions.tsx`): EIA's day-ahead demand forecast for the hour of the day's peak demand; the error beside it is the peak demand less that forecast.
- Chain 077 (23 October 2026), the panel `grid_mix_<grid>` above the hourly chart of the Mix tab: `eia930_all_generation`, `net_generation_mw` (a `series_sum` key, the 24 hours' net generation; and a `series` key, the newest hour held); each fuel group's `series_sum` over its variables, comma separated, and its share as `calc|pct|` of the two sums; `eia930_all_demand`, `demand_mw` (a `series_max` key, the peak demand hour). With `mixp=month`: `generation_mix_hourly_profile`, `<coal, hydro, natural_gas, nuclear, other, solar, storage, wind>_mwh` and `<coal, hydro, natural_gas, nuclear, other, solar, storage, wind>_share_pct` (`series` keys, the newest month; `series_esum` keys, the twelve months). The section "The Mix tab's energy mix, keyed, hourly and by month" above gives each rule.
