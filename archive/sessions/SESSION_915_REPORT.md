# Session 915 report: wind and solar PPA prices (Berkeley Lab)

23 October 2026, from 08:28 UTC, on lab-desktop (the data machine), a session of `queue/done/051-day-23-october-data-world-gas-hydro.md`. Model spend USD 0. Pulls: 5 requests of 20 (eta-publications.lbl.gov's robots file, asked alone first and the same as session 253's; the wind and solar publication pages; their two data files).

## Read these first

- **Why this source:** the price a buyer signs for in a power purchase agreement is the other side of the wholesale prices the ERW holds, and no ERW table had it. Berkeley Lab's report data files list every wind and utility-scale solar PPA price LBNL has gathered (from FERC filings and other public records), one row a contract.
- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `lbnl_ppa_prices`, 1,133 PPAs, an events table: 587 wind PPAs executed from 1996 to 2025 (the Land-Based Wind Energy Technology Data Update, 2026 Edition, August 2026) and 546 solar PV PPAs executed from 2006 to 2025 (Utility-Scale Solar, 2025 Data Update, October 2025; PV only, no PV+battery). Each PPA's execution date, contract capacity (MW), term, region and LBNL's consolidated region, and its price levelized over the term in real dollars (wind 2025, solar 2024). LBNL names no project, so each row's id is a hash of its fields.
- **The cross-checks, against each file's own averages:**
  - **Wind:** the PPAs and their megawatts counted by execution year equal LBNL's "Wind PPA Average" sheet in 24 of 24 year groups. The rows' MW-weighted average sits a little above LBNL's generation-weighted one (2015: 38.0 against 37.4 USD/MWh; 2024: 71.6 against 70.0).
  - **Solar:** outside Hawaii, the rows' MW-weighted average is within 5 percent of LBNL's generation-weighted average in 13 of 16 years and within 10 percent in 15 (2015: 50.4 against 49.8; 2024: 53.3 against 48.2, from 24 PPAs).
- **The license:** each file's copyright notice says "This work is openly licensed via CC BY 4.0", which the header carries. Berkeley Lab's verdict in `license_verdicts.csv` (read 14) rests on the same statement in the Queued Up file.

## Decisions made without you

- **The solar prices are in 2024 dollars:** the sheet's own note still names 2023 dollars, but its averages and the file's other price sheets are headed "2024 $/MWh". The header names the difference.
- **The 2025 solar data update** is the newest the publications server links (the same file session 253 saved on 13 October); a 2026 update is not asked for by a guessed address.
- **Events, not series:** one row a contract, `event_type` `ppa`, its price in `price` with `currency` USD and the unit and dollar year in `x_price_unit` and `x_dollar_year`.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/lbnl_ppa_prices.py`, `tests/test_session915.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c051/s915/`, `runs/license_reads/s915/`, `runs/s915*`, `warehouse/raw/lbnl_ppa_prices/`.

## Corrected by session 918

- The solar PPAs run to June 2025 (executed), not 2024: the file is the 2025 data update, with 2024's prices as its last full year. The header, computed from the rows, said 2006 to 2025 from the first write.
