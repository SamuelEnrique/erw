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

## storage_capacity (derived, no pull)

**Rows.** Every generator with prime mover `BA` (EIA's "Batteries", energy source `MWH`) in `eia860m_operating_generators`, `eia860m_planned_generators` and `eia860m_retired_generators`, one row per generator, a snapshot rebuilt each run.

**Columns:**

- `capacity_mw` is EIA's nameplate MW.
- `status` is the ERW's status vocabulary: operating, planned, under_construction, retired.
- `eia_status` is EIA's own code.
- `planned_year` is the year of EIA's planned operation date (planned units).
- `operating_year` is EIA's (operating and retired units).
- `iso` is the ISO of the unit's balancing authority when it is one of the seven: CISO CAISO, ERCO ERCOT, ISNE ISO-NE, MISO, NYIS NYISO, PJM, SWPP SPP. Otherwise it is empty and the BA code stays in `balancing_authority`.

**Energy capacity (MWh)** is not in the ERW's EIA-860M tables, so this table has none. It is never estimated from MW.

**On `/storage`,** the fleet by status, by ISO, by state and by planned year are sums of this table's rows. The page sums nothing else, and `site/scripts/check-values.mjs` recomputes each sum from Supabase.
