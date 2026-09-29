# Battery storage: method

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
- **Days.** Pacific (America/Los_Angeles) local days. A day is written only when every 5-minute interval is present (288, or 276 and 300 on the daylight saving days).
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
