# Battery storage: method

Tables: `storage_daily_cycle`, `storage_capacity` (session 2312; as held on 24 October 2026, 14,503 and 1,627 rows)

Built in session 31 for the site's `/storage`. Three tables:

| Table | Tier | What |
|---|---|---|
| `eia930_all_storage` | source | EIA-930's hourly battery net generation per balancing authority |
| `storage_daily_cycle` | derived | The daily cycle computed from it |
| `storage_capacity` | derived | Every battery unit in the ERW's EIA-860M tables |

## eia930_all_storage (source)

- **The series.** EIA API v2, route `electricity/rto/fuel-type-data`, fuel type `BAT` ("Battery storage"), hourly, from `warehouse/connectors/eia930_storage.py`.
- **Values.** Net generation in MW as EIA publishes it: **positive while the batteries discharge, negative while they charge**.
- **Time.** EIA's hourly period is the hour's end in UTC, so `ts_utc` is one hour before it, the hour's start (checked for EIA-930 in session 5).
- **Partition column.** `ba` = `erco`, `isne`, `miso`, `swpp`, `us48`.

**Who reports BAT, checked 2026-09-29:**

| BA | BAT series starts |
|---|---|
| US48 | 2024-07-15 |
| ERCO | 2024-11-06 |
| ISNE | 2024-11-06 |
| MISO | 2025-01-15 |
| SWPP | 2026-02-04 |
| CISO, NYIS, PJM | none (the API returns 0 rows) |

CAISO's own battery output is `caiso_battery_storage` (CAISO's Today's Outlook).

**Why its own table.** `eia930_all_generation` carries the same series as `net_generation_battery_mw`, but only for its rolling 30 days. This table keeps every hour from the series start.

**Completeness.** Per UTC day: a day is written only when all 24 hours have a value; otherwise it is left out and recorded as a gap in `warehouse/metadata/run_status.csv`. Nothing is filled.

**Pull and resume.**

- The history was pulled once in session 31, one BA and one month at a time.
- Every API page is saved raw under `warehouse/raw/eia930_storage/<run_id>/`.
- Each finished past month is kept as a checkpoint, so an interrupted pull resumes where it stopped.
- The daily run pulls the last 3 days and merges them on (entity, variable, ts_utc), as EIA-930 demand does.

## storage_daily_cycle (derived)

**Days.** Per BA and complete local day: 24 hours, or 23 and 25 on the daylight saving days.

**Local time:**

- ERCO and SWPP: America/Chicago.
- MISO: EST, the fixed UTC-5 MISO publishes in.
- ISNE: America/New_York.
- US48: America/New_York, the Eastern time EIA's Grid Monitor shows by default.

| Variable | Formula | Unit |
|---|---|---|
| `mwh_discharged` | sum of the day's positive hourly values x 1 h | MWh |
| `mwh_charged` | sum of the day's negative hourly values x 1 h, written positive | MWh |
| `peak_discharge_hour` | the local hour (0 to 23, the hour's start) of the largest positive value; the earliest on a tie; absent with no discharge | hour |
| `peak_charge_hour` | the local hour of the most negative value; absent with no charge | hour |
| `round_trip_ratio` | `mwh_discharged / mwh_charged`, when both are above zero | ratio |

**`round_trip_ratio` is not a measured efficiency.** It is the day's energy out over energy in as EIA-930 reports them. Charge held across midnight moves it, and so do batteries a BA reports under other fuel types (solar or wind with integrated storage). The unit `hour` is Decision 29 of `docs/datastandard.md`.

<a id="caiso"></a>
### CAISO's rows (session 34)

CAISO reports no battery series to EIA-930, so its rows come from CAISO's own data, not EIA's:

- **Input.** `caiso_battery_storage`, variable `batteries_mw`: CAISO's Today's Outlook "Total batteries", 5-minute, MW, positive discharging, negative charging. It includes the batteries of hybrid plants, which CAISO publishes as part of the total.
- **Hours.** Each hour is the mean of its twelve 5-minute values, so its MW over the hour is its MWh. The five variables above then follow from those hourly values, with the same formulas, so CAISO's day compares with the EIA-930 BAs'.
- **Days.** Pacific (America/Los_Angeles) local days. A day is written only when every 5-minute interval is present (288, or 276 and 300 on the daylight saving days). The autumn day is never whole: CAISO's own file for it prints 288 rows, listing 01:00 to 01:55 once (read for 1 November 2026 in session 7052, done-line request 162), so one of the day's two 01:00 hours is not published; 2 November 2025 and 1 November 2026 are left out for that reason, not for the clock conversion.
- **Marking.** Entity `caiso:ISO`, partition `ba` = `ciso`, and the row's `source` is `erw:storage_daily_cycle_caiso` (the EIA-930 rows' is `erw:storage_daily_cycle`), with this section as its `source_url`. The site labels them as CAISO's data.
- **History.** From 2025-08-24, the start of `caiso_battery_storage`. The daily run computes the table after both inputs are refreshed.

## storage_capacity (derived, no pull)

**Rows.** Every generator with prime mover `BA` (EIA's "Batteries", energy source `MWH`) in `eia860m_operating_generators`, `eia860m_planned_generators` and `eia860m_retired_generators`, one row per generator, a snapshot rebuilt each run.

**Columns:**

- `capacity_mw` is EIA's nameplate MW.
- `status` is the ERW's status vocabulary: operating, planned, under_construction, retired.
- `eia_status` is EIA's own code.
- `planned_year` is the year of EIA's planned operation date (planned units).
- `operating_year` is EIA's (operating and retired units).
- `iso` is the ISO of the unit's balancing authority when it is one of the seven: CISO CAISO, ERCO ERCOT, ISNE ISO-NE, MISO, NYIS NYISO, PJM, SWPP SPP. Otherwise it is empty and the BA code stays in `balancing_authority`.

**Energy capacity (MWh), since session 34.** `energy_capacity_mwh` is EIA's "Nameplate Energy Capacity (MWh)", carried by the EIA-860M tables since session 34 (checked in the saved August 2026 workbook: the Operating and Retired sheets have the column, the Planned sheet does not).

- Operating and retired units: every battery unit has a value (1,137 operating units, 150,437.6 MWh; 8 retired, 1,236.1 MWh, vintage 2026-08).
- Planned and under-construction units: none, because EIA publishes none in EIA-860M.
- It is never estimated from MW.
- The three EIA-860M tables were rebuilt from the saved workbook (`eia860.py --from-raw 20260926T000340Z`, no pull); every other column is unchanged.

**On `/storage`,** the fleet by status (MW, and MWh where EIA gives it), by ISO, by state and by planned year are sums of this table's rows. The page sums nothing else, and `site/scripts/check-values.mjs` recomputes each sum from Supabase.

## The page `/storage` as it stands (session 330, 20 October 2026)

- **Three tabs** since session 239: the fleet (this note's three tables and `caiso_battery_storage`), the build-out
  (`storage_buildout.md`) and the owners (`storage_owners.md`); `/storage/buildout` and `/storage/owners` redirect to
  their tabs.
- **The charts** are drawn in SVG (session 303); no value moved.
- **Every number** is a row of its table, carried with its check key and read again by `check-values`.
- **Downloads** (session 330): under each tab, its tables as the live set's CSV with a Python and a Stata reader of
  that CSV (session 328's shared line). `storage_owners_monthly` is held for review in the live set, so the owners tab
  offers none and points to Data and methods.
- **Read on 20 October 2026** from the public catalogue: `storage_capacity`, `storage_daily_cycle` (to 18 October),
  `eia930_all_storage` (to 18 October) and `caiso_battery_storage` (to 19 October) ran that day; the build-out and the
  owners hold EIA-860M's August 2026 inventory, the newest the warehouse holds.

## The figures on the page and their keys

Each number `/storage` and `/grid` show carries its key (`site/components/Num.tsx`), which `site/scripts/check-values.mjs` checks against the live set and `site/scripts/check-methods.mjs` against this note (session 409). The keys the sections above do not name:

- `storage|mw|<status>`, `storage|n|<status>`, `storage|mwh|<status>`, `storage|n_mwh|<status>`: on `/storage`, the fleet tab's four cells (Operating, Under construction, Planned, Retired): the sum of `capacity_mw` of the `storage_capacity` units of that status, the count of those units, the sum of their MWh where EIA gives it, and the count of the units that have it. `storage|n|operating` is also the count of units under the page's headline number.
- `storage|iso_mw|<ISO>|<status>`: on `/storage`, the table by ISO: the operating, under-construction and planned MW of the units whose balancing authority is that ISO, and a last row of the units outside the seven ISOs (`none`).
- `storage|iso_mw|<ISO>|<status>`, `storage|iso_mwh|<ISO>|operating`: on `/grid`, a grid's block "Batteries": the same sums for the grid's ISO (operating, under construction and planned MW), and the MWh of its operating units where EIA gives it.
- `storage|state_mw|<state>|operating`, `storage|state_mw|<state>|build`: on `/storage`, the table of the 15 states with the most operating MW: each state's operating MW, and its under-construction and planned MW together.
- `storage|year_mw|<year>`: on `/storage`, under the bars of planned additions, the MW of the under-construction and planned units whose planned year is that year.
- `storage_buildout_monthly` (its method is `storage_buildout.md`), on the build-out tab of `/storage`, each figure one row of the table for the grid chosen, in the newest month held: `battery_operating_mw` and `battery_operating_units` (operating power, and the units under it), `battery_operating_mwh` and `battery_operating_mwh_per_mw` (operating energy, and the average duration in hours), `battery_operating_mw_net_added_12m` and `battery_operating_mwh_net_added_12m` (added over the last twelve months, net of retirements, in MW and MWh).
- `storage_buildout_monthly`, `battery_operating_mw_<lt2h, 2to4h, 4to6h, ge6h>`, `battery_operating_mwh_<lt2h, 2to4h, 4to6h, ge6h>`, `battery_operating_mw_energy_not_reported`: the bars by duration at each year's end, in MW or in MWh as the measure chosen (`measure=mwh`), and the MW of the units with no energy value, which cannot be drawn in MWh; the folded table "The numbers behind both charts, year by year" gives each, with the year's total and average hours.
- `storage_buildout_monthly`, `solar_operating_mw`, `battery_mwh_per_solar_mw`: the chart "Storage against solar" and the same folded table: the grid's operating solar MW and the MWh of batteries per MW of solar at each year's end.
- `storage_buildout_monthly`, `battery_planned_mw`, `battery_planned_mw_online_<year>`: the table "By grid": each grid's planned MW, all years together and by the year expected online, beside its operating MW, MWh, average hours and twelve months' additions.

## The replication (session 7014, chain 301)

`replication/storage/replicate.py` reads the live set as the page does (the anon key: the fleet, the daily cycle, EIA-930's and CAISO's battery output, the buildout and the owners) and compares every row with the warehouse's tables, and recomputes the fleet's sums from the warehouse: 63,075 of 63,075 equal on 16 November 2026 after one fix (`docs/reviews/storage-faults-2026-11-16.md`: CAISO's revised battery values had reached the live set and not the tables of record). `replicate.do` rebuilds five sums of the fleet in Stata, its expected values at its top.

## The cross-checks (session 7018, chain 301)

The fleet's nameplate (EIA-860M, operating units, vintage 2026-09) beside the highest hour of output each grid's own reporting shows (CAISO's 5-minute data from 24 August 2025; EIA-930's battery series from November 2024, which CAISO does not report), as held on 16 November 2026. Output cannot pass nameplate, and a fleet never discharges whole at once:

| Grid | Operating nameplate, MW | Highest output held, MW | When (UTC) | Share |
|---|---|---|---|---|
| CAISO | 17,265.5 | 13,441 (5-minute) | 2026-08-19 03:10 | 78 percent |
| ERCOT | 19,194.6 | 11,928 (hourly) | 2026-09-03 00:00 | 62 percent |
| MISO | 1,175.9 | 931 (hourly) | 2026-10-13 22:00 | 79 percent |
| ISO-NE | 1,021.7 | 516 (hourly) | 2026-03-02 23:00 | 51 percent |
| SPP | 490.5 | 447 (hourly) | 2026-09-29 22:00 | 91 percent |

Every grid's highest output stands below its nameplate. An hourly mean is lower than a 5-minute peak, and units added after the hour shown raise the nameplate and not the hour. The replication compares every figure the page reads with the tables (63,075 of 63,075).

## The decisions on the page (session 7018, chain 301)

The page draws these at its foot, under each of its tabs (`site/lib/decisions.ts`, `STORAGE_DECISIONS`), each choice's default and source on hover:

1. Battery output is net generation as published: positive while the batteries discharge to the grid, negative while they charge, so a day's charging is the part below zero taken as a positive amount. **Default:** Positive discharging, negative charging. **Source:** EIA-930's battery series (fuel type BAT) and CAISO's Today's Outlook, both signed this way. (session 31)
2. EIA's hourly period is the hour's end in UTC, so each hour is dated by its start, one hour before EIA's stamp; CAISO's hour is the mean of its twelve 5-minute values. **Default:** Every hour dated by its start. **Source:** EIA API v2, electricity/rto/fuel-type-data; CAISO's 5-minute battery history. (session 31)
3. A day is the balancing authority's local day and counts only when every hour of it is held (23 or 25 on the clock-change days; for CAISO every 5-minute interval); a day short of one is left out, never filled. **Default:** Whole local days only. **Source:** docs/methods/storage.md, "Days" and "Completeness". (session 31)
4. Each authority's day is in its own time: Central for ERCOT and SPP, Pacific for CAISO, Eastern for ISO-NE and for the Lower 48 (as EIA's Grid Monitor shows it), and fixed EST for MISO, as MISO publishes. **Default:** Each grid's own local time; MISO on fixed EST. **Source:** The operators' market time zones; EIA's Grid Monitor default. (session 31)
5. The day's energy out over energy in is not a measured efficiency: charge held across midnight moves it, and so do batteries reported under other fuels (solar or wind with integrated storage). **Default:** Shown as out over in, labelled not an efficiency. **Source:** docs/methods/storage.md, the daily cycle's notes. (session 31)
6. California is drawn from CAISO's own 5-minute battery data, not EIA-930's, which CAISO does not report as BAT; it includes the batteries of hybrid plants, which CAISO publishes inside its total. **Default:** CAISO's own data for California, labelled as CAISO's. **Source:** CAISO, Today's Outlook, battery storage history ("Total batteries"). (session 34)
7. The fleet is every generator with EIA's prime mover "Batteries" in EIA-860M, at its nameplate MW and, where EIA gives it, its nameplate energy; the page's sums by status, grid, state and planned year are sums of those rows and nothing else. **Default:** EIA-860M battery units at nameplate; sums of the rows only. **Source:** EIA-860M, Monthly Update to the Annual Electric Generator Report. (session 31)
8. Energy capacity in MWh is EIA's own figure, carried for operating and retired units; planned units have none in EIA-860M, and a unit's MWh is never estimated from its MW. **Default:** MWh only where EIA states it. **Source:** EIA-860M, "Nameplate Energy Capacity (MWh)". (session 34)
9. A unit's grid is the ISO of its balancing authority when that is one of the seven; any other unit stands outside the ISOs with its own authority's code, never assigned by its state. **Default:** The ISO of the unit's balancing authority, else outside the ISOs. **Source:** EIA-860M's balancing authority code for each generator. (session 31)

## What waits for the owner (session 7018)

- PJM's and NYISO's battery output (neither reports BAT to EIA-930 by the check of 29 September 2026; their units are in the fleet's sums).

## Sign-off

- Signed off by:
- Date:
- Items of the section above ruled, and how:
