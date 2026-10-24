# Session 2217 report: Denmark's grid an hour (Energinet's settlement data), a second source of the session's own choosing

24 October 2026, from 01:51 UTC, on lab-desktop (the data machine), the eighth session of `queue/done/098-day-2-november-data-price-indexes-reservoirs-rooftops.md`, unattended. Model spend USD 0. Pulls: 1 request of 20 (below).

## Read these first

- **Why this source:** Denmark runs the world's most wind-led national grid, and Energinet, its transmission system operator, publishes every hour's settled production by technology, gross consumption and the flow on each interconnector, openly and under CC BY 4.0 (session 2215's verdict, read 335). The ERW held no European grid an hour, and no queue file plans one.
- **One table written, validated, archived, in coverage (sector power), in the release package, both holds:** `energinet_dk_production_hourly`, 2024-12-31T23:00Z to 2026-10-13T23:00Z (1 January 2025 to 14 October 2026 in Danish time), 607,311 rows.
  - Two price areas (DK1 west of the Great Belt, DK2 east), 15,625 hours each.
  - Twenty-one measures in MWh for the hour: thirteen production columns (central, local, commercial, offshore and onshore wind by size, hydro, solar by size, solar self-consumption, unknown), local self-consumption, gross consumption, and the exchanges with Norway, Sweden, Germany, the Netherlands, Great Britain and across the Great Belt (Energinet's sign: negative an export).
  - **A null has no row.** Local self-consumption is null from 1 September 2026 (Energinet ended it), 2,064 records.
  - The three grid losses and power-to-heat are not taken: both sit inside gross consumption.
- **The cross-check** (`runs/c098/s2217/cross.py`, `cross.out`):
  - **Energinet's own arithmetic:** production plus net imports equals gross consumption to within rounding in every one of the 31,250 records, but only with local self-consumption counted. Without it, DK1 falls short by a median 2.4% (up to 10.3%) and DK2 by 0.9%. This is why the measure is taken: the trial left it out, and the write takes it.
  - **The Great Belt link:** DK1's and DK2's signed flows cancel, to a median 3.2 MWh (the link's losses).
  - **Against Ember:** DK1 plus DK2 gross consumption in 2025 (8,760 Danish hours in each area) is 40.513 TWh, against Ember's 40.670 TWh Danish demand through Our World in Data (`owid_ember_electricity_annual`). The ratio is 0.9961.
  - Wind made 19.090 TWh in 2025, 47.1% of gross consumption.

## The pulls

1. The dataset for 1 January 2025 to 15 October 2026, Danish time, in one answer (`limit=0`, 27 MB of JSON, 31,250 records), saved as `runs/license_reads/s2217/01_*.bin`. The probe copy was seeded into the raw store, and the trial and the write read it offline.

## Errors

- **The trial's header line failed once** (`r.nunique` is pandas' method, not the column). Fixed to `r["nunique"]` and run again; no request was spent.

## Decisions made without you

- **Energinet's settlement data as the session's own choice,** for the reasons above.
- **Local self-consumption taken,** since the hour's balance closes only with it. It ends 1 September 2026, and the rows stop there.
- **The hour in Danish time kept as `x_hour_dk`,** beside the UTC hour, for readers who count Danish days.
- **The span starts at Energinet's 1 January 2025 in Danish time** (23:00 UTC on 31 December 2024). It ends at the latest hour Energinet had settled.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/energinet_production.py`, `tests/test_session2217.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, the coverage, sources, archive manifest and license files, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c098/s2217/`, `runs/license_reads/s2217/`, `runs/s2217_*`, `warehouse/raw/energinet_production/`.
