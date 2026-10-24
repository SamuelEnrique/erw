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
  Lower 48", and the state monthly view below it is its monthly mix. Since session 1185 (chain 091) the view is drawn
  for the Lower 48 as the sum of the 48 contiguous states and DC in `state_generation_mix_monthly` (EIA-923, not
  EIA-930), keyed `states_sum`: `generation_mix.md`, section "The Lower 48 by month, the sum of the states".
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

Chain 078 in this note (sessions 1164 to 1177): 1166 (this section), 1167 (its last part, with its decisions), 1169
(the next section). On the same tab elsewhere: 1168's stress charts in `grid_stress.md`, 1171's sentence on revisions
in `grid_network.md`, 1174's ERCOT notice state in `ercot_grid_notices.md`, section 6.

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

Session 1167 (the standing rule, `site/lib/license.ts`: no held grid's rows are drawn): the clean view's table of the
seven grids now draws ISO-NE's, MISO's and NYISO's six cells as "license needed", in the view's own placeholder (the
publishers on hover), as every other block of the view already did; the four other grids' figures and keys are as they
were. The hub price beside the mix (the average day and year after year, "Price"; `data/mixplus`, built from
`iso_hub_prices_history` for every grid but ERCOT) reads "license needed" for ISO-NE and NYISO, whose prices the file
holds; MISO keeps "paused while terms are reviewed" (its file holds none). The rule is `site/lib/gridHeld.ts`, its test
`site/scripts/test-grid-held.mjs`.

The same session, "What is being built" (`components/grid/YourGrid.tsx`): `lib/grid.ts` reads `energy_projects` by
`entity_id`, and the shared reader's hold (`site/lib/supabase.ts`) filters a table held by grid by `entity` only, so
ISO-NE's queue rows came through (`isone_queue:137` and `isone_queue:1515` are in the live set, an anon read of 24
October 2026). The read now drops them (`shownQueue`) and the block reads "ISO-NE's interconnection queue: license
needed". A held grid's hub prices in "What it costs" said "Not in the warehouse yet"; the read is refused for a
license, so they now say "license needed".

Decisions (session 1167):

- **Words a visitor sees changed by the rule, not by design**: the clean table's held cells, the Price factor for
  ISO-NE and NYISO, ISO-NE's queue block and the held grids' "What it costs" (every page is in review).
- **One rule file**, `site/lib/gridHeld.ts` over `licenseHeldRow`. The table named for the mix's prices is
  `iso_hub_prices_history`, the builders' source for every grid but ERCOT; it joins the Mix and Clean tabs' lists in
  `site/lib/gridtables.ts`, which `tests/test_session502.py` holds to the code.
- **The queue is held for ISO-NE only**, as the status file holds `energy_projects`; NYISO's and MISO's positions stay
  drawn though their own queue tables are held (put to the owner, `docs/reviews/grid-rulings-2026-10-23.md`).
- **The filter is the Grid tool's own** (`shownQueue`): the shared reader's missing `entity_id` filter is outside this
  chain's files, and is put to the owner.

## California's generation, EIA-930's and CAISO's own side by side: not built (chain 078, 24 October 2026)

Session 1169 was to draw, on the Mix tab for CAISO, EIA-930's hourly total and CAISO's own over the week (the Grid pack's blind spot 4), if a public CAISO own-generation table is in the live set. None is: `caiso_fuel_supply` (CAISO's Today's Outlook, hourly, public) is in the catalogue with `in_live_set` "no" and no rows in Supabase (an anon read on 24 October 2026), and `caiso_fuel_supply_history` is under `catalogue_hold`; so nothing was drawn, and California's hourly mix by fuel stays withheld (session 118).

Decisions (chain 078):

- **Written down and left, as the session's own condition says**: no chart from a committed file or a CSV in its place, since the week must be read where check-values can recompute it (the live set); loading `caiso_fuel_supply` (a `recent` rule in `warehouse/supabase/live_set.yaml`, a data session's) is the step that opens it.
- **This note, not the join's (`eia930_caiso_break.md`)**: the panel was to sit on the Mix tab, whose note this is.

## One read of a grid's generation a page (chain 091, 24 October 2026)

Chain 091 in this note (sessions 1178 to 1189): 1179 (this section) and the energy mix panel's part in 1181 to 1186 (the subsection "The energy mix panel in chain 091" below, written by session 1188 from their reports). Each of those sessions' own sections is in `grid_network.md` (1180 to 1184, 1186, 1187) and `generation_mix.md` (1185).

Session 1179. The Mix tab read the grid in view's `eia930_all_generation`, every variable, four times a render, each for its own window: 45 days (`site/lib/grid.ts` `load`, the grid's own blocks), 34 days (`latestHour`, the Now view's mix: two small requests), 10 days (`components/grid/Conditions.tsx` `loadConditions`: "Yesterday" and the grid's row of "Generation mix, as a table") and 9 days (`components/grid/MixView.tsx`, the hourly panel above). Now the render reads it once, at the widest window, and each reader takes its own days from it (`site/lib/gridReads.ts`): `shareGeneration(entity, since)` starts the read and keeps it for the render with React's `cache` (one Map a request, as `gridNotices()` is kept since session 1160); `generationSince(entity, since)` gives the rows at or after the reader's own start (its `daysAgo(n)`, computed where it was), in the read's order; `latestHour` gives the newest total at or after its start and every row from that hour on. The seven ISO grids share 45 days (`load`, on the Mix and Clean tabs); the Lower 48's Mix tab, which has no `load`, shares 10 days (`app/grid/page.tsx`), its widest whole read. The other regions of the mix table are read as before (10 days each): they are not the grid in view.

On the live set, 24 October 2026, 01:58 and 02:01 UTC (`site/scripts/time-grid-reads.mjs`, one request at a time): the Mix tab of each ISO grid 5 to 8 fewer requests (ERCOT 67 to 61, CAISO 75 to 70, ISO-NE 58 to 50) and about 3,800 to 4,500 fewer rows of the table (27,134 to 23,396 for ERCOT, PJM, MISO, NYISO); `/grid` (the Lower 48) 43 to 39 requests and 28,300 to 24,974 rows; across the eleven Mix addresses and ERCOT's Clean tab, 677 requests to 614 and 444,370 rows to 401,920. The figures: the eleven Mix addresses and ERCOT's Clean tab drawn by the code before and after on the same answers (kept in memory, each request sent once): 2,232 figures, every key, value and text the same.

Decisions (chain 091):

- **The reader keeps its own start.** Each reader still computes `daysAgo(n)` where it did and takes the rows at or after it, so its rows are the ones its own read gave; a reader whose start is before the shared one, or whose entity is not the one shared, reads as before.
- **A failed shared read fails every reader of the render with its error**, where before each read could fail alone; each reader still says so in its own words (`attempt`, `NoData`, `Missing`).
- **The Lower 48 shares 10 days, not 45**: it has no 45-day read, and 34 days whole would read more than the two small requests of `latestHour`, which stay.
- **The pinned calls stay as they were** (`latestHour(GEN, entity, "net_generation_mw", daysAgo(34))`, `loadConditions(ba, conditionsDay())`, `<MixTable />`): the share is found inside the readers, so no caller changed.
- **The timing script walks each page as one render**: `site/scripts/tsx-loader.mjs` now gives the site's modules React with a `cache` kept in `globalThis.__erwRequestCache` (a new Map a page), since React's own `cache` outside Next calls the function every time; with no Map set it does so as before. The node test is `site/scripts/test-grid-generation.mjs`.

### The energy mix panel in chain 091 (sessions 1181 to 1186)

What the chain's other sessions changed in the panel `grid_mix_<grid>` (the section "The Mix tab's energy mix, keyed, hourly and by month" above); each rule in full is in the section named.

- **A failed read (session 1181)**: "Demand is not held for these hours" on a failed `eia930_all_demand` read, and an empty panel on a failed `eia930_all_generation` read, are now "Peak demand: could not be read" and "The hourly mix: working on it" (the view's own words for a failed read), inside the panel. `grid_network.md`, "When a read fails".
- **Its files (session 1182)**: `erw_grid_mix_<grid>_hourly.csv` (each fuel's MWh and share; the 24 hours' total, the peak demand and the newest hour in the header) and `erw_grid_mix_<grid>_monthly.csv` (the month's days and its alert or notice days in the header); the Lower 48's monthly view writes `grid_mix_us48_monthly` (session 1185). `grid_network.md`, "Each panel's table, to download".
- **Its anchor (session 1183)**: `#mix-panel`, and `#mix-panel-<grid>` for a grid after the first on one page; the two chips ("Hourly, last 7 days", "By month") now link the panel's own anchor, where both linked `#hourly`, the first grid's section, on every grid. `grid_network.md`, "Every panel in the address".
- **Its method (session 1184)**: the line "Method: the Mix tab's energy mix, keyed, hourly and by month" at the panel's foot links this note's section of that name (`METHOD_MIX` in `site/lib/gridAnchors.ts`); the Lower 48's monthly view adds a second line to `generation_mix.md` (`METHOD_MIX_US48`). `grid_network.md`, "The method from each panel".
- **The Lower 48 by month (session 1185)**: drawn in place of "not built for the Lower 48" (the bullet above and `generation_mix.md`).
- **Under check-values (session 1186)**: each fuel's share (`calc|pct|`) no longer reads the day's total again for each fuel (each key's value kept for the run), and the panel's `series_sum` and `series_max` keys of one window are read together; every verdict the same. `grid_network.md`, "The Grid pages under check-values, lighter".

Decisions (chain 091, for this panel, written by session 1188):

- **The heading "The Mix tab's energy mix, keyed, hourly and by month (chain 077, 23 October 2026)" is a link target**: its id is held to `METHOD_MIX` by `site/scripts/test-grid-methods.mjs`, so a rename fails that test by name and is made with the constant (session 1184).
- **The anchor is on an element that holds the panel alone**, not on the panel's own element, because sessions 1152 and 1159 pin that element word for word (session 1183).
- **No figure of the panel moved** in any of these sessions: each proved it with `site/scripts/same-figures.mjs` on the same live answers (sessions 1181 to 1185) or with the old and new check-values on the same pages (session 1186).

## The hub's price beside the hourly mix (chain 100, 24 October 2026)

Chain 100 in this note (sessions 1400 to 1409): session 1402, the hub's real-time price for the same hours as the energy mix panel's hourly chart (the section "The Mix tab's energy mix, keyed, hourly and by month" above), as the panel `grid_hubprice_<grid>` under that chart on the Mix tab ("Now and by state", the hourly view; none with `mixp=month`). Code: `site/lib/hubPriceHourly.ts` (pure), `site/components/grid/HubPricePanel.tsx`, the `strip` series of `site/components/TimeChart.tsx`; test `site/scripts/test-hub-price.mjs` on `site/scripts/fixtures/hub_price.json` (real rows, read with the anon key on 24 October 2026). The note's other chain 100 section is session 1403's, "The cleanest hours, live", below; sessions 1404, 1405 and 1406 are in `grid_network.md` (every panel drawn with a render case, the Ask column by tab, the Lower 48 on the Network tab); sessions 1400, 1401 and 1407 changed no note (each blocked without a build); session 1408 wrote this line and the two Decisions blocks marked as its own.

- **Which grids.** The grids whose hub prices are public on the day (`site/lib/license.ts`, `site/data/license_status.json`): ERCOT, CAISO and SPP. `iso_rtm_hub_prices` is held by grid for MISO only, and SPP is public in every status file (`warehouse/metadata/license_status.csv` names no SPP price table as held). The hub is the one the site names for each grid (`docs/grids/grids.json` `hub`): ERCOT Hub Average (`ercot:HB_HUBAVG`, variable `spp_rtm`), SP15 (`caiso:TH_SP15_GEN-APND`, `lmp_rtm_15m_mean`) and SPP North Hub (`spp:SPPNORTH_HUB`, `lmp_rtm_15m_mean`), the scarcity strip's two (session 1154) and SPP's. The other grids say in one line, in the tool's one look, why there is none: PJM "license needed" (no PJM price is held), MISO "paused" (since 4 October 2026, `miso_pause.md`, and the table is held for MISO), NYISO and ISO-NE "license needed" (their prices need a license from 2026-10-21), the Lower 48 "no hub of its own". A grid of the three whose hub becomes held on a later day says "license needed" the same way, and its rows are not read.
- **An hour's price** is the mean of its four 15-minute prices, used only when all four are held: the rule of `cost_of_power.md` ("An hour's price is the mean of its intervals ... It is used only when every interval of the hour is present"), the hour floored in UTC. An interval written twice is held once. Nothing is filled: an hour with a missing interval has no price and is a gap in the strip.
- **The hours** are the hourly chart's own: the last 7 UTC days of the 9 read whose 24 hours hold `net_generation_mw`, to the newest hour held when that is later (`chartWindow`, the rule of `components/mix/Now.tsx` `Hourly`; the test holds the two equal on real rows). The read is the hub's rows of the last 9 days (`daysAgo(9)`), about 860 rows a grid. Where no mix chart is drawn (CAISO, whose hourly mix is withheld by the session 118 ruling; or a grid whose `eia930_all_generation` could not be read), the price is drawn alone, as a line, over the 7 UTC days that end with its newest day whose 24 hours are all held (`priceWindow`).
- **The strip.** Under the stacked chart, on its time axis and its own scale (the lowest and highest hour, and zero when between), the hour's price as a line, a gap where an hour is not held; on hover the hour's price under each fuel's MW and share, and in the chart's table a column of its own. A `TimeSeries` with `strip: true` (and its `unit`) is drawn so; without one every chart is drawn as before.
- **The figures written under it**, each keyed, over the chart's hours: the hours held whole, `series_hn|iso_rtm_hub_prices|<variable>|<start>|<end>|<entity>`; their mean, `series_hmean|iso_rtm_hub_prices|<variable>|<start>|<end>|<entity>`; the highest hour, `series_hmax|iso_rtm_hub_prices|<variable>|<start>|<end>|<entity>`, with its hour in words; the last hour held, `series_hmean|...` over that one hour. `site/scripts/check-values.mjs` reads the table's rows of the key's entity, variable and range and recomputes each with the page's own function (`hubHourStat`); `site/scripts/check-methods.mjs` reads the three kinds as table figures (`TABLE_KEY`). The hours' prices drawn in the strip and named on hover are not written figures.
- **A failed read** of `iso_rtm_hub_prices` says "could not be read" with the reason on hover, draws no figure, and the mix chart above is drawn without its strip (session 1181's rule). A window with no hour held whole says so in words ("no hour from ... holds its four 15-minute prices").
- **Its file, anchor and method**, as every panel of the tool: `erw_grid_hubprice_<grid>.csv` (the four figures, the window and the rule in its header; session 1182's `PanelFile`), the anchor `#hub-price` (`#hub-price-<grid>` for a grid after the first on one page; `HUB_PRICE_ANCHOR` in `site/lib/gridAnchors.ts`), and the line "Method: the hub's price beside the hourly mix", which opens this section (`METHOD_HUB_PRICE`).

On the fixture's rows: ERCOT over 20 to 22 October 2026 holds all 72 hours; SPP North Hub holds 29 of the 72 hours from 19 to 21 October (SPP's rows of 2026-10-19 05:00 to 2026-10-20 05:00 UTC are not in the table, and its newest row on 24 October is 2026-10-21 04:45 UTC, so on the page SPP's strip stops before the mix does); CAISO's 7 days to 22 October hold the 48 hours the fixture carries.

Decisions (chain 100, session 1402):

- **A strip under the chart, not a second axis.** The chart is a stacked area in MW from zero; a price line on a second axis over it would cross the bands, and its scale (negative at night in SPP, a few hundred at a peak) shares nothing with the stack's. The strip keeps the same time axis (the hover's hour is one line through both) and gives the price its own scale.
- **The strip is a series of the chart, not a second chart**, so one hover names the hour's price beside each fuel's MW (`TimeChart`'s card, a row under a rule). `TimeChart`'s signature line, which session 303's test pins, is unchanged: the strip is a field of the series (`strip`), off by default, and the stack, its bounds, its shares and its direct labels are computed from the other series alone.
- **The panel is its own, `grid_hubprice_<grid>`, under the chart**, not inside `grid_mix_<grid>`: the mix panel's element and its two files are pinned (sessions 1152, 1158, 1159, 1182), and its anchor and method are among the 17 that sessions 1183 and 1184 count. Its anchor and method stand beside them (`HUB_PRICE_ANCHOR`, `METHOD_HUB_PRICE`), as session 1185's `METHOD_MIX_US48` does.
- **CAISO's price is drawn alone**, over its own 7 days: its hourly mix is withheld, and the price is public; the window is the price's, not EIA-930's days for California, so nothing of the withheld series decides what is drawn.
- **The last hour held is the last of the chart's hours that holds its four prices**, not the newest row of the table: the figures are of the hours drawn. EIA-930's hours lag the prices by a day or more, so ERCOT's and CAISO's newest prices are past the chart's end; SPP's lag the mix.
- **Three new key kinds** (`series_hn`, `series_hmean`, `series_hmax`) rather than `series_sum` and a `calc`: no existing kind reads an hour as the mean of four rows held whole, and a sum of the rows over four would count an hour missing an interval.

Decisions (chain 100, session 1402, the rest of its report, written by session 1408):

- **The Clean tab's license line names `iso_rtm_hub_prices`**, which that tab does not draw: `MixView.tsx`, whose `MixClean` the tab draws, now reads it, and `scripts/page_tables.py` reads every import of a file for each of its exports, so the Clean tab's list in `site/lib/gridtables.ts` names it, as session 1174 did for ERCOT's notices (`tests/test_session502.py` holds the list to the reader). Put to the owner, recommended kept.
- **The license file decides which grids are drawn, not `docs/grids/grids.json`**: that file still says `prices_public: true` for NYISO, ISO-NE and MISO, while `site/lib/license.ts` holds their prices; the panel goes by the license file. Put to the owner, with a refresh of the file by the data machine recommended.
- **The words under the chart and the strip's name** (`Under the chart, <hub>'s real-time price by hour, the same hours: ...` and `<hub> real-time`) are put to the owner, recommended kept.
- **This section's heading is a link target** (`METHOD_HUB_PRICE` in `site/lib/gridAnchors.ts`), its id held by `site/scripts/test-hub-price.mjs` and `test-grid-files.mjs`: a rename is made with the constant.
- **No figure that stood moved**: `site/scripts/same-figures.mjs` on 14 addresses (2,198 figures), the 8 Mix pages that differ differing by the new figures and panel names only.

## The cleanest hours, live (chain 100, 24 October 2026)

Chain 100 in this note: session 1403, the newest 7 days of `carbon_intensity_hourly` beside the Clean tab's "the cleanest hours of the average day" ("How clean, and when", drawn from the committed build `site/data/clean/<grid>.json` of `clean_energy_summary`, `clean_energy.md`), as the panel `grid_cleanweek_<grid>`, one a grid in view, under that grid's block of the cleanest hours. Code: `site/lib/cleanWeek.ts` (pure), `site/components/grid/CleanWeekPanel.tsx`, the read in `site/components/grid/MixView.tsx` `MixClean`; test `site/scripts/test-clean-week.mjs` on `site/scripts/fixtures/clean_week.json` (real rows, read with the anon key on 24 October 2026).

- **Which variable.** `intensity_generation`, the CO2 EIA estimates for the power made in the grid over its net generation, kg per MWh (`emissions.md`). The committed view is a share of the grid's own generation ("Generation inside the grid, not imports", `clean_energy.md`), so the live week is the intensity of the same generation. `intensity_demand` counts imports and takes exports out, and is not used here. Lower is cleaner in the week; higher is cleaner in the committed view.
- **Which hours.** Local clock time in the grid's time zone, as the committed view's are: the zone each committed file carries (`tz`, from `warehouse/derived/mix_profile.py` `GRIDS`), so a day has 23 or 25 hours on the days the clocks change. For six grids that zone is the one `docs/grids/grids.json` names; for MISO the committed file says `America/Chicago` and `grids.json` says `Etc/GMT+5` (MISO's market time, which does not change with the clocks). The panel follows the committed file, so the two drawings share one clock.
- **Which days.** The 7 local days that end with the newest local day whose hours are all held (23, 24 or 25), read from the grid's rows of the last 12 days (`READ_DAYS`; EIA's CO2 estimates run three days or more behind the clock). An hour not held is a hatched cell, never filled. On the day the clocks go back the repeated hour's second value is named on the cell's hover, and the cell draws the first; on the day they go forward the missing hour is a blank cell that says so.
- **The drawing.** The shared `HeatChart` (`components/svgchart.tsx`), the shape of the committed view: the hour of day across, the day down; darker where dirtier. Hover a cell for its day, its hour in local time with the zone and in UTC, and its kg per MWh. The week's cleanest hour is marked. Its legend says "cleaner" and "dirtier" rather than writing two unkeyed numbers.
- **The figures written under it**, each keyed, over the window `[start, end)` in UTC: the hours held, `series_n|carbon_intensity_hourly|intensity_generation|<start>|<end>|<entity>` (session 1154's kind); the week's cleanest hour, `series_min|...`; its dirtiest, `series_max|...`; the mean of the hours held, `series_mean|...`. The hour of each extreme is said in words (the first on a tie). `site/scripts/check-values.mjs` reads the table's rows of the key's entity, variable and range and recomputes `series_min` and `series_mean` with the page's own function (`weekStat`, each hour once); `series_max` is recomputed as before. `site/scripts/check-methods.mjs` reads the two new kinds as table figures.
- **The line against the committed average day.** The month is the week's local month (of its last day), in the year the committed view shows when that year holds it, else in the newest year that does. In words, from both: whether the week's cleanest hour is one of that month's four cleanest hours of the average day (`cleanest_hour_1` to `_4`), and whether the week's dirtiest hour is that month's dirtiest hour of the average day (the lowest carbon-free share). No figure of either is written in the line, only hours. For California, when that month is before the join (`caisoJoinDay()`, 16 December 2025) and the week after it, the line adds that the two rest on two series.
- **Held grids.** `carbon_intensity_hourly` is public in every status file (`site/data/license_status.json`), so every grid is drawn; `site/lib/gridHeld.ts` `heldCarbon` asks `lib/license.ts` on the day, and a grid that becomes held reads "license needed" with no read. The committed view's `clean_energy_summary` is held for ISO-NE, MISO and NYISO from 20 October 2026, so for those three the week is drawn and its line against the average day reads "license needed": no hour of a held file is named.
- **A failed read** says "could not be read" with the reason on hover and draws no figure; the committed view beside it is drawn as before (session 1181's rule). A read with no whole local day says so in words.
- **Its file, anchor and method**, as every panel of the tool: `erw_grid_cleanweek_<grid>.csv` (the four figures, the window and the rule in its header; `PanelFile`), the anchor `#clean-week` (`#clean-week-<grid>` for a grid after the first; `CLEAN_WEEK_ANCHOR` in `site/lib/gridAnchors.ts`), and the line "Method: the cleanest hours, live", which opens this section (`METHOD_CLEAN_WEEK`).

On the fixture's rows (read 24 October 2026, the table's newest hour 2026-10-20 23:00 UTC for all seven): ERCOT holds 168 of 168 hours from Tuesday 13 to Monday 19 October (Central time), its cleanest hour 131.2 kg per MWh on Friday 16 October at 16:00 CDT, its dirtiest 446.3 on Saturday 17 October at 23:00 CDT, a mean of 288.7. California holds 144 of 168 (no hour of Thursday 15 October Pacific time is in the table), its cleanest 61.0 on Tuesday 13 October at 10:00 PDT. MISO holds 168 of 168.

Decisions (chain 100, session 1403):

- **`intensity_generation`, not `intensity_demand`**, because the committed view is of the grid's own generation (above) and the Clean tab's "The last 24 hours" draws the same variable.
- **The committed file's time zone, not `grids.json`'s, for MISO**: the week is set against the committed view's hours, and the two must share a clock. The difference is listed for a ruling.
- **Whole local days**: the window ends with the newest local day whose hours are all held, so each hour of the day stands once a day in the week's mean, and the newest day is not a row of blanks. The table's newest hours (the partial day after it) are in "The last 24 hours" above.
- **Hours only in the comparison line.** The committed view ranks hours by carbon-free share and the week by kg per MWh: two measures of the same generation, so the hours compare and the figures do not. The week's single cleanest and dirtiest hours are the figures keyed; the line names whether their hours fall among the average day's.
- **Two new key kinds** (`series_min`, `series_mean`) beside `series_max` and `series_n`: no existing kind gives the lowest of a range, and a mean as `series_sum` over `series_n` would count an hour written twice twice in the sum and once in the count.
- **The panel is its own**, `grid_cleanweek_<grid>`, given to the committed view by its caller (`CleanView`'s `live`, passed by the Grid tool's `MixClean` only), so the committed view is drawn exactly as before wherever no caller passes it. Its anchor and method stand outside `GRID_ANCHOR` and `GRID_METHOD`, as session 1402's do.

Decisions (chain 100, session 1403, the rest of its report, written by session 1408):

- **The panel's file header names this note, not `eia930_all_emissions`**: `scripts/page_tables.py` reads the strings of every file `MixView.tsx` imports, so a table named in the header joined the Mix tab's tables; with the note named, the Mix tab's and the Clean tab's license lines stand as they were (`tests/test_session502.py`).
- **The week's single cleanest and dirtiest hours in the comparison, not the week's own average day**: they are the figures the panel keys; the mean of each local hour over the 7 days would be keyed figures of a new kind. Put to the owner, recommended kept, with the block's title and the comparison line's words.
- **MISO's clock** (above) is put to the owner: which of `America/Chicago` and `Etc/GMT+5` is MISO's for the Grid tool; the panel follows the committed file until then.
- **This section's heading is a link target** (`METHOD_CLEAN_WEEK`), its id held by `site/scripts/test-clean-week.mjs` and `test-grid-files.mjs`: a rename is made with the constant.
- **No figure that stood moved**: `same-figures.mjs` on 16 addresses (1,913 figures), the 10 Clean pages differing by the new figures and panel names only.

## The computed views, keyed (chain 107, 24 October 2026)

Chain 107 in this note (sessions 1410 to 1418): session 1413, the computed views keyed (this section's opening, with a new key kind, `filecalc|`); session 1414, the Clean tab's large tables keyed whole (the subsection "The Clean tab's tables, keyed whole"); session 1415, one function of that kind for the Clean tab's carbon chart (a short subsection; its block and Decisions are in `emissions.md`, "On the Grid tool's Clean tab, keyed"); session 1416, "Yesterday" and the mix table (the last subsection). Session 1411 is in `grid_network.md` ("The older blocks when a read fails") and 1412 in `flex_alert_scorecard.md` (section 12); session 1410 changed no note (the next file, and the landing blocked); session 1417 wrote this line and the Decisions blocks marked as its own.

Session 1413. Session 1166 keyed the views' figures that are values of the committed files (`file|`, the section of chain 078 above) and left without a key the figures the views compute from the files' arrays: the duck curve year after year, the peak hours of the average day, the history by state and the availability means. Each now has a key of a new kind, `filecalc|<function>|<data file>|<args>`, always behind `fmt|<form>|` (`site/scripts/check-format.mjs`), whose recomputation applies the page's own function to the committed file in the repository, as `ercotn|` applies `lib/ercotNotices.ts` to the notices (`ercot_grid_notices.md`, section 6). No figure's text or value moved: each figure is wrapped in its key, with a one-line tip that names what it is, its rule and its file.

**The functions.** The duck view and the average day already called pure functions of `site/lib/mix2.ts` (no import: `acrossYears`, `periodOf`, `highest`); the key applies them as they are. The history's and availability's arithmetic stood inline in `site/components/mix/views.tsx`; it moved, as it stood, into `site/lib/mixViewCalc.ts` (no import: `historyTotal`, `historyCell`, `availOf`, `availMean`, `availMin`, `availMax`), which the views now call. `site/scripts/check-filecalc.mjs` parses a key (`filecalcParts`: the function, the file and the shape of each argument, else no key) and applies the function to the file (`filecalcValue`), which `site/scripts/check-values.mjs` reads as a `file|` key reads it. The functions, each `filecalc|<function>|...`:

- `duck_solar_peak`, `duck_low`, `duck_evening`, `duck_ramp` on `mix/<grid>.json` with `<cal>|<year>` (`mix=duck`, "<grid>: <month> by year"): solar at its peak hour of the month's average day; net load's midday low (09:00 to 16:00); its evening high (from 16:00); the ramp between them when the low comes first; MW, written whole (`n0`). The table's "Days held" is the file's own value, `file|mix/<grid>.json|months.<YYYY-MM>.days_held` (session 1166's kind, a build of `generation_mix_hourly_profile`'s `days_held`).
- `day_peak` on `mix/<grid>.json` with `<period>|<solar|wind>` (`mix=day`, "Solar and wind at their peak hour of the average day"): the source's highest hour of the month's or the year's average day, MW (`n0`).
- `hist_share` and `hist_mwh` on `mix_history.json` with `<state>|<year>|<fuel>` (`mix=history`, "<state>: shares of net generation"): the fuel's share of the sum of the state's fuel groups in the year, percent (`n1`), and its net generation in millions of MWh (`n1`); none for a year without twelve months.
- `avail_mean`, `avail_min` and `avail_max` on `mixplus/<grid>.json` with `<year>|<season>|<fuel>` (`mix=supply`, "Mean availability"): the mean, the lowest and the highest of the 24 local hours of a source's output over its installed capacity, percent (`n1`).

**Checked against the file alone.** A computed figure is not a column of a live-set table, so check-values compares it with the file's own arithmetic and writes "the committed file" on its line; no "same" or "DIFF" line follows (those are for `file|` keys whose file is a build of a row). `site/scripts/check-methods.mjs` reads the kind as a family of the page's arithmetic whose measure is its function (`MEASURE_AT.filecalc = 1`), named here by `filecalc|` and the function's name.

**Which figures are keyed, and how many.** On the committed files, one grid at a time (the views' default month, period, year and season): the duck view's table by year, every figure but the hours: 40 keys for CAISO, ERCOT, ISO-NE, MISO and PJM (eight Aprils, four computed figures and the days held each), 35 for SPP and 32 for NYISO (a figure the file does not give is its placeholder, unkeyed); the average day's two peaks, 2 a grid (NYISO 1: its file reports no solar); availability's table, 18 a grid (six sources, three figures each; NYISO 12); the history's table, every share and every million MWh drawn: 66 for the United States (the view's default), 134 for Texas and California together. The hours (when a peak or a low falls) stay words, as session 1166 left the hours of the records; the charts' points are not keyed (they answer a hover with their values).

**Each table's file, anchor and method.** Every keyed table of these views offers its rows as a file (`components/grid/PanelFile.tsx`): `erw_grid_mixday_all_shares.csv` and `erw_grid_mixday_all_peak.csv` (the average day), `erw_grid_duck_<grid>.csv`, `erw_grid_history_<state>.csv`, `erw_grid_supply_all_mean.csv` and `erw_grid_supply_<grid>_tight.csv` (the tightest hours, keyed by session 1166, filed now since it stands in the same view). Each carries an anchor (`MIX_VIEW_ANCHOR` in `site/lib/gridAnchors.ts`: `#day-shares`, `#day-peak`, `#duck-by-year`, `#history-shares`, `#supply-mean`, `#supply-tight`; a second grid or state takes `-<grid>` or `-<state>` in lower case) and the line "Method: the computed views, keyed", which opens this section (`METHOD_MIX_VIEWS`). No read can fail on these views: the files are built into the page (`lib/mixdata.ts` imports them), so a missing file fails the build, not the page; each figure the file does not hold is drawn, as before, as its placeholder with its reason on hover, and has no key.

**Held grids.** These views draw every grid, as before: their files are of public tables (EIA-930, EIA-860M, EIA-923, `site/data/license_status.json`); `lib/gridHeld.ts` holds none of their figures. A key is written only where the page writes a number.

Decisions (chain 107, session 1413):

- **One kind for every computed view, named by its function**, not a kind a view: the recomputation is always "read the committed file, apply the page's function"; the function's name is the figure's measure, so the note names each.
- **The functions already in `lib/mix2.ts` stay there**; only the arithmetic that stood inline in the views moved, as it stood (`site/scripts/test-mix-view-calc.mjs` holds each moved function to the old expression on every state, year, fuel, grid and season of the files).
- **The figure is drawn by a new component, `components/mix/CalcKey.tsx`**, beside session 1166's `K`, so the views' one `K` line (pinned by `tests/test_session1166.py`) stands as it was.
- **The days held of the duck view are a `file|` key**, not a function: the value is the file's own.
- **The hours are not keyed**: they are times written as words, as session 1166 decided for the records and the stress view.
- **The tightest hours table of the availability view gains a file, an anchor and a method line** though its keys are session 1166's: the view's file test holds every figure of a block to its files.

Decisions (chain 107, session 1413, the rest of its report, written by session 1417):

- **The availability files' header names `generation_mix_hourly_profile` first**, the table whose hours availability is computed over, since the file test needs each panel file to open with a table.
- **No table new to the Mix or Clean tab is named in the views' code**, so the tabs' license lines (`site/lib/gridtables.ts`, read by `scripts/page_tables.py` and held by `tests/test_session502.py`) stand as they were.
- **The views' addresses are not yet in check-values' list** (`mix=duck`, `mix=day`, `mix=supply`, `mix=history`; session 1166 left them out): at the landing the `filecalc|` keys are recomputed by the node tests on the committed files; adding the ERCOT address of each view to the list, with its floors, is put to the owner, recommended.

### The Clean tab's tables, keyed whole (session 1414)

Session 1166 keyed the Clean tab's two headline tables ("Carbon-free share and hours", "The seven grids") and left its three large tables without a key; session 1168 keyed the stress view's large tables whole. The Clean tab's large tables are now keyed the same way, every figure of each, in `site/components/mix/views.tsx` `CleanView`, for each grid not held:

- **"<grid>: an annual clean purchase against the hours, <year>"**: for each purchase (50, 100 and 150 percent of the flat load's year) and each shape (the grid's own carbon-free mix, its solar, its wind), the energy met in its own hour and the hours met in full, `fmt|n1|file|clean/<grid>.json|years.<YYYY>.match_<shape>_<p>_<energy, hours>_pct`. Their rows in the live set are `clean_energy_summary`'s `year_match_mix_<p>_energy_pct`, `year_match_mix_<p>_hours_pct`, `year_match_solar_<p>_energy_pct`, `year_match_solar_<p>_hours_pct`, `year_match_wind_<p>_energy_pct` and `year_match_wind_<p>_hours_pct` (P1Y), as `clean_energy.md` defines them.
- **"<grid>: the cleanest hours of the average day, <year>"**, its table by month: the share in the cleanest hour and in the dirtiest hour of the month's average day, computed by the page from the month's 24 hours, `fmt|n1|filecalc|clean_day_max|clean/<grid>.json|<YYYY-MM>` and `fmt|n1|filecalc|clean_day_min|clean/<grid>.json|<YYYY-MM>` (session 1413's kind: the expression that stood in the view, `Math.max` and `Math.min` of `lib/clean.ts dayOf` without its unheld hours, moved as it stood into `site/lib/mixViewCalc.ts` `cleanDayHeld`, `cleanDayMax` and `cleanDayMin`); and the month's share, `fmt|n1|file|clean/<grid>.json|months.<YYYY-MM>.carbon_free_share_pct` (`clean_energy_summary`'s `carbon_free_share_pct`, P1M). "The four cleanest hours" stay words (times), as sessions 1166, 1168 and 1413 left the hours.
- **"<grid>: moving a flat load into the cleanest hours"**, every year held: the flat load's carbon in kg CO2 per MWh (`n1`), each shift's change in carbon (`sn1`, a plus sign above zero), the days counted, the flat load's cost in USD per MWh (`n2`), each shift's change in cost (`sn1`) and the days priced (`n0`): `clean_energy_summary`'s `year_flat_kgco2_per_mwh`, `year_shift<s>_carbon_change_pct`, `year_shift_days`, `year_flat_cost_usd_per_mwh`, `year_shift<s>_cost_change_pct` and `year_cost_days` (P1Y), keyed `file|clean/<grid>.json|years.<YYYY>.<variable without year_>`. A year without a hub price keeps its words ("not held yet", "licensed source needed", "paused while terms are reviewed"), unkeyed.

**The count of keys added, and the checkers' time.** On the committed files, one grid at a time in its default year: 118 keys added for ERCOT (18 in the purchase table, 36 by month, 64 by year), 102 for CAISO (no hub price before September 2024), 86 for PJM (no hub price held) and 86 for SPP (six years); ISO-NE, MISO and NYISO none (held). Over the seven grids drawn one at a time the clean view writes 543 keys, 392 more than the 151 it wrote. `site/scripts/test-grid-file-keys.mjs`, which draws every view for every grid and recomputes every key from its file, ran in 3.23 to 3.28 s on the tree before (three runs) and 3.83 to 3.96 s after (four runs), about 0.6 s more for the keys added. check-values reads the eight Clean pages of its list (`/grid?grid=<grid>&view=clean`): 685 keys there in place of 175, and, for its comparison of a file's value with its table's row (session 1166, ruling 4), 78 row sets of `clean_energy_summary` in place of 12, one light read each (a grid's year or month; the `filecalc|` figures read no row).

**Each table's file, anchor and method.** The Clean tab's five tables each offer their rows as a file (`components/grid/PanelFile.tsx`): `erw_grid_clean_all_shares_<year>.csv`, `erw_grid_clean_<grid>_purchase_<year>.csv`, `erw_grid_clean_<grid>_months_<year>.csv`, `erw_grid_clean_<grid>_shift.csv` and `erw_grid_clean_all_grids_<year>.csv`; a held grid's cells are written "license needed", as the table draws them, and the file's header names the grids held. Each carries an anchor (`CLEAN_TABLE_ANCHOR` in `site/lib/gridAnchors.ts`: `#clean`, the id the first block already had, `#clean-purchase`, `#clean-months`, `#clean-shift`, `#clean-grids`; a second grid takes `-<grid>`) and the line "Method: the Clean tab's tables, keyed", which opens this section (`METHOD_CLEAN_TABLES`). No read can fail on the view: the files are built into the page (`lib/mixdata.ts`).

**Held grids.** `clean_energy_summary` is held by grid (`site/data/license_status.json`; ISO-NE, MISO and NYISO since 21 October 2026): their blocks and cells read "license needed" (session 1167's `lib/gridHeld.ts` rule), and no key of theirs is written; the node test asserts it for every grid.

Decisions (chain 107, session 1414):

- **The cleanest and the dirtiest hour are `filecalc|`**, not a `file|` key at the hour the page picked: the figure is the page's arithmetic on the day (the highest and lowest of its hours), so the key names that rule, and the expression moved as it stood (`site/scripts/test-mix-view-calc.mjs` holds it to the old one on every month of the seven files).
- **The headline tables gained files, anchors and method lines too**: the view's file test holds every figure of a block to its files, and the five tables are one block (`data-mix="clean"`).
- **"Months held" ("11 of 12") stays words**, as session 1166 left it: two figures in one cell would be written to the file as two numbers without their "of".
- **A method line of its own** ("Method: the Clean tab's tables, keyed", `METHOD_CLEAN_TABLES`), beside session 1413's: the computed views' line is counted by `tests/test_session1413.py`, and the Clean tab's tables are mostly values of the file, not computed figures.
- **The node tests were extended in place** (the held clean test of `test-grid-file-keys.mjs`, two tests of `test-mix-view-calc.mjs`): `tests/test_session1168.py` and `tests/test_session1413.py` count their tests.

### One function more, for the Clean tab's carbon chart (session 1415)

- `carbon_left_out_n` on `carbon_left_out.json` with `<variable>` (`intensity_generation` or `intensity_demand`): the months of `carbon_intensity_monthly` that the Clean tab's "Monthly since 2018" leaves out of its chart (session 118's rule, `warehouse/derived/carbon_left_out.py`), a count written whole (`n0`): `site/lib/mixViewCalc.ts` `leftOutCount`, the length of `lib/carbonLeftOut.ts` `carbonLeftOutMonths`, the list the chart's note writes after it. Checked against the committed file alone. The block, its keys and their Decisions are in `emissions.md`, section "On the Grid tool's Clean tab, keyed (chain 107, session 1415)"; the function is named here because every function of this kind is named in this note (`site/scripts/test-mix-view-calc.mjs`).

### "Yesterday" and the mix table, at 390 pixels and on hover (session 1416)

Two blocks of the Mix tab older than chain 077, both in `site/components/grid/Conditions.tsx`: "<grid>: yesterday" (`GridYesterday`, in the tab's opening blocks, `components/grid/NowView.tsx`) and "Generation mix, as a table" (`MixTable`, at the foot of the tab). Session 1166 keyed their figures (the chain 078 section above); this session brings the two blocks to the standard chains 077 to 100 set for the new panels. No figure's key, value or text moved.

- **Named panels.** "Yesterday" is `grid_yesterday_<grid>` (the Grid tool's grid: `ercot`, `caiso`, `pjm`, `miso`, `spp`, `nyiso`, `isone`, `us48`), the mix table `grid_mixtable_all` (it draws the eight regions whatever the grid in view, so its name takes no grid). Each takes, as every panel does, the shared table's row height and full rule (`site/app/tokens.css`, session 1159's rule scoped to `[data-grid-panel]`): the mix table's rows are about 33 px tall where they were about 29 (4 px above and below a cell).
- **Anchors**: the ids the two sections always had, `#yesterday-<EIA-930 code>` (`#yesterday-erco`, `#yesterday-ciso`, ... `#yesterday-us48`) and `#mix-table` (`CONDITIONS_ANCHOR` and `yesterdayAnchor` in `site/lib/gridAnchors.ts`).
- **Files** (`components/grid/PanelFile.tsx`): `erw_grid_yesterday_<grid>.csv`, one figure a row (the peak, the forecast for that hour, its miss in MW and as a share of demand, the day's mean absolute miss and its hours, each degree day, the day's net generation), each with the key and the value the page draws; a degree day the page cannot compute is written in its words ("not computed (N of 24 hours in weather_obs_hourly)", or "could not be read" when the station's read failed, session 1411). `erw_grid_mixtable_all.csv`: the table's rows, each share with its key and value, a region without a complete day "no data for this day", a fuel the region does not report blank, as the table draws it.
- **Method**: the line "Method: "Yesterday" and the mix table, keyed" under each block, to this section (`METHOD_CONDITIONS`).
- **At 390 pixels.** The mix table (ten columns, wider than a phone's 358 px column) scrolls inside a frame a keyboard reaches and scrolls with the arrow keys, named by the table's caption ("Each region's share of its UTC day's net generation by fuel, in percent (EIA-930)"; `site/lib/cells.ts` `scrollRegion`, as session 1158 did for the energy mix panel); its column heads are header cells (`scope="col"`), each region's name its row's header cell (`scope="row"`). "Yesterday" holds no table of its own and no fixed width: its two columns stack under 1024 px (`lg:`), its chart and bar are drawn for the width they have, the chart's table (Chart | Table) is the shared one (320 px at the least, in its own frame). The fuel colours' row is named as a group (`role="group"`: a name on an element without a role is not read).
- **On hover.** The two small charts of "Yesterday" already answered a hover through the shared charts: the seven days' chart (`components/LineChart.tsx` over `components/TimeChart.tsx`) gives the hour start in UTC and each line's value, demand and the day-ahead forecast in MW, the station's temperature in degrees F, with a dashed guide at the hour; the day's mix (`components/ShareBar.tsx`, `ShareSegments` of `components/svgchart.tsx`) gives the fuel, its MWh and its share. A tap on a phone fires the same mouse events, so it opens the same card. Their drawing is unchanged (no line, point, colour or size moved: the components and their props are as they were), so no test compares an old drawing with a new one, as session 1412 needed for the scorecard's own charts. One sentence under the block's opening says so. The mix table holds no chart.
- **Held grids.** EIA-930 and the National Weather Service's observations are public: `lib/gridHeld.ts` holds none of these figures. California's mix of the day stays withheld in "Yesterday" (session 118); the mix table still draws California's shares (session 1166's ruling 2, not changed here).

Decisions (chain 107, session 1416):

- **No chart was redrawn.** Both small charts were the shared charts already, each answering a hover with the hour or the fuel and its MW or MWh; the review of 23 October 2026 lists them as "two small charts with tips". Adding a guide or a card of their own would have moved their look on every page that draws them.
- **The anchors are the ids the blocks had**, not new ones: links to `#yesterday-erco` and `#mix-table` keep working; they stand outside `GRID_ANCHOR` (pinned by sessions 1183 and 1184), as sessions 1413 to 1415's anchors do.
- **The mix table is one panel, `grid_mixtable_all`**, not one a grid: the table is the same on every grid's Mix tab, and `<MixTable />` is written without a prop in `app/grid/page.tsx` (three python tests read that line).
- **"Yesterday" takes its grid from its code** (`GRID_OF`, the inverse of `NowView.tsx`'s `CONDITIONS_CODE`), since `<GridYesterday code={CONDITIONS_CODE[grid.slug]} />` is read word for word by `tests/test_session237.py`.
- **The files repeat no template by hand where a function exists**: the mix table's shares take `shareKey`, the day's net generation `genTotal` (FuelBar's rule); the other keys are written in the file's rows as in the page's figures, and `site/scripts/test-grid-files.mjs` holds every figure of each block to its file and back.
- **The render cases of the two blocks are their own**: the figures they held in `view_now` and `view_mix` (the tab's blocks around them) are now counted in `grid_yesterday_<grid>` and `grid_mixtable_all`; the older cases keep every key they checked.

Decisions (chain 107, session 1416, the rest of its report, written by session 1417):

- **The sentence on hover is written for each grid**: it names the temperature only where the block has a station (none for the Lower 48) and the bar only where the day's mix is drawn (none for CAISO, whose mix stays withheld).
- **The mix table's taller rows are the one visible change without a number**: they follow from naming the table a panel (session 1159's rule); the row height is put to the owner, recommended kept, one row height across the tool.

## The figures on the page and their keys

Each number `/grid` shows carries its key (`site/components/Num.tsx`), which `site/scripts/check-values.mjs` checks against the live set and `site/scripts/check-methods.mjs` against this note (session 409). The keys the sections above do not name:

- `eia930_generation_latest`, `net_generation_mw` (a `series_esum` key): on the Mix tab, the block "today so far": the sum of the hourly net generation of the latest UTC day held, over its complete hours, in MWh.
- `state_generation_mix_monthly`, `net_generation_<natural_gas, coal, nuclear, wind, solar, hydro, other_renewables, oil_and_other, not_itemized>_mwh`: the block "monthly mix since 2001", the table's last column: each fuel group's MWh in the newest month held for the state chosen (the United States, `eia:US`, unless another is chosen).
- `eia930_all_generation`, `net_generation_<coal, geothermal, hydro, natural_gas, nuclear, oil, other, other_storage, pumped_storage, solar, solar_with_battery, unknown, unknown_storage, wind, wind_with_battery, battery>_mw`: the latest hour's blocks that open the Mix tab (`components/grid/NowView.tsx`), "The mix in that hour": each source's net generation in MW, as EIA names it, in the latest hour that holds the total; the largest of them is also named in the tab's first sentence.
- `eia930_all_demand`, `demand_forecast_mw`: the block "yesterday" under them (`components/grid/Conditions.tsx`): EIA's day-ahead demand forecast for the hour of the day's peak demand; the error beside it is the peak demand less that forecast.
- Chain 077 (23 October 2026), the panel `grid_mix_<grid>` above the hourly chart of the Mix tab: `eia930_all_generation`, `net_generation_mw` (a `series_sum` key, the 24 hours' net generation; and a `series` key, the newest hour held); each fuel group's `series_sum` over its variables, comma separated, and its share as `calc|pct|` of the two sums; `eia930_all_demand`, `demand_mw` (a `series_max` key, the peak demand hour). With `mixp=month`: `generation_mix_hourly_profile`, `<coal, hydro, natural_gas, nuclear, other, solar, storage, wind>_mwh` and `<coal, hydro, natural_gas, nuclear, other, solar, storage, wind>_share_pct` (`series` keys, the newest month; `series_esum` keys, the twelve months). The section "The Mix tab's energy mix, keyed, hourly and by month" above gives each rule.
- Chain 100 (session 1402), the panel `grid_hubprice_<grid>` under the hourly chart of the Mix tab (ERCOT, CAISO, SPP): `iso_rtm_hub_prices`, `spp_rtm` (ERCOT) and `lmp_rtm_15m_mean` (CAISO, SPP), as `series_hn`, `series_hmean` and `series_hmax` keys over the chart's hours (the hours held whole, their mean, the highest hour) and a `series_hmean` key over one hour (the last hour held). The section "The hub's price beside the hourly mix" above gives each rule.
- Chain 100 (session 1403), the panel `grid_cleanweek_<grid>` on the Clean tab, beside the cleanest hours of the average day: `carbon_intensity_hourly`, `intensity_generation`, as `series_n`, `series_min`, `series_max` and `series_mean` keys over the newest 7 whole local days (the hours held, the week's cleanest hour, its dirtiest, the mean of the hours held). The section "The cleanest hours, live" above gives each rule.
