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
