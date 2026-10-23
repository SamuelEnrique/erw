# Session 2048 report: transport's energy (Oak Ridge's Transportation Energy Data Book)

23 October 2026, from 18:59 UTC, on lab-desktop (the data machine), the seventh session of `queue/done/059-night-24-october-data-storms-reactor-events-lng-climate.md`. Model spend USD 0. Pulls: 5 requests of 20 (tedb.ornl.gov's robots file, asked in a call of its own and read first; the book's home page; its data page; its citation page; the zip of Edition 41's 267 spreadsheets). The trial and the write reused the saved data page and zip (`--offline`).

## Read these first

- **One table written, validated, archived, in coverage (sectors oil, products and power), held from the live set and from Redivis, flagged internal:** `ornl_tedb_transportation_annual`, 674 rows from five tables of Edition 41 (data to 2024, released December 2025):
  - Table 2.2, the four end-use sectors' and the nation's energy consumption, 1950 to 2024 (175 rows; TEDB's quadrillion Btu written as TBtu, x 1,000);
  - Table 2.4, transportation's energy use and each source's share (petroleum, natural gas, coal, renewables, electricity), 1950 to 2024 (234 rows; a share in percent, TEDB's fraction x 100);
  - Table 2.7, transportation's energy use by mode and fuel in 2023, 28 modes from cars to commuter rail (103 rows, TBtu);
  - Table 2.8, the same modes' totals, 2022 and 2023 (58 rows);
  - Table 6.2, light-duty sales of hybrids, plug-in hybrids and battery electric vehicles, and all light-duty sales, 1999 to 2024 (104 rows; TEDB's thousands written as a count).
- **Each mode is a path** (`ornl_tedb:t2_7:highway.light_duty.cars`, `t2_8:nonhighway.rail.passenger.transit`), read from the row's capitals and indentation against a closed map of labels; a footnote letter in a label ("Light-duty trucksb") is dropped, and a label not in the map stops the run.
- **Flagged internal until a ruling:** the book's pages state no terms of reuse (its citation page, read 189), and Table 6.2 is compiled by Argonne's Transportation Research Center from sales it does not name; other tables of the book draw on licensed sources. The table's verdict is "not settled".
- **2024 sales:** 1,609,000 hybrids, 321,800 plug-in hybrids and 1,247,700 battery electric vehicles of 15,436,000 light-duty vehicles.

## The cross-checks

- **Table 2.7 against Table 2.8:** the 28 modes' 2023 totals agree to the tenth of a TBtu.
- **Table 2.2 against EIA** (`runs/c059/s2048/cross.py`): the chain file asked for the transportation sector of `eia_sector_energy_consumption_monthly`, but that table holds the commercial and industrial sectors only, and no ERW table holds EIA's transportation total. The check was made on the sectors the ERW holds, EIA's monthly figures summed to the year:

| Sector | 2015 | 2020 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|
| Total, TEDB less EIA (`TETCBUS`), TBtu | +21.9 | +23.3 | -164.1 | -146.2 | -382.3 |
| Commercial (`TECCBUS`) | +13.5 | -7.5 | +41.5 | +28.3 | +34.4 |
| Industrial (`TEICBUS`) | -4.8 | -2.2 | -68.8 | -44.6 | -195.0 |

  TEDB rounds to a tenth of a quad (50 TBtu either way); to 2020 every year is within it. From 2022 EIA's figures stand above TEDB's, as EIA's later revisions would make them; this session did not trace the revisions.
- **Table 2.2's transportation against Table 2.4's total:** 35 years, within 49.1 TBtu (the rounding again).
- **Plug-in sales against chain 058's registrations:** not made; chain 058's registration table was not written when this session ran (its session 2036 comes later).

## Errors

- **The first trial found no header:** TEDB's sheets begin in column B; the reader now drops an empty first column.

## Decisions made without you

- **Five tables of the book's 267,** those the chain file named and the sectors' table that lets them be checked; the per-cent change rows and the shares that are ratios of rows held are not taken.
- **Flagged internal** (reversible by a ruling).
- **Quads and thousands converted by a stated rule** (x 1,000) to the vocabulary's TBtu and count, rather than new units.

## For Samuel's ruling

- **The Transportation Energy Data Book's terms:** publish (a Department of Energy laboratory's book, freely posted), ask ORNL (the book's feedback address), or keep internal.

## Files

- New: `warehouse/connectors/ornl_tedb.py`, `tests/test_session2048.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_reads.csv` (188, 189), `license_tables.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c059/s2048/`, `runs/license_reads/s2048/`, `runs/s2048*`, `warehouse/raw/ornl_tedb/`.
