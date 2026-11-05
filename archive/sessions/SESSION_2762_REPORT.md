# Session 2762 report: European renewable energy shares a year (Eurostat's nrg_ind_ren), the third own choice

25 October 2026, about 22:31 to 22:36 UTC, on lab-desktop (the data machine), chain 139, unattended. Run before session 2759, so that its table is described and uploaded with the chain's others. Precheck passed (`runs/c139/pre2762.out`). Model spend USD 0. Pulls: 3 requests of 20 (1 by the probe, 2 by the fetch).

## Read these first

- **Why this source:** the renewable shares the Renewable Energy Directive counts (SHARES) were not held, nor named in the queue or the unlanded chains' records. The table sits beside this chain's consumption table and session 2413's production table. Session 2757's lesson was applied: the dataset was asked with a wildcard key, in one request.
- **`eurostat_renewable_shares_annual`, public, held from the live set and in the Stanford holds** (`warehouse/connectors/eurostat_renewable_shares.py`, 3,095 rows, 37 areas, 2004 to 2025):
  - From nrg_ind_ren, the whole dataset (228 KB) and the NRG_BAL codelist for the shares' names. Eurostat's last update: 15/09/26 23:00.
  - Six shares in pct: overall (REN), electricity (REN_ELC), heating and cooling (REN_HEAT_CL), transport (REN_TRA), and two newer items, district heating and cooling with waste heat (REN_WHC_DHEAT_DCL, 32 rows) and waste heat in heating and cooling (REN_HEAT_CL_WHC, 28 rows).
  - The EU27's overall share: 9.61 per cent in 2004, 17.42 in 2014, 25.24 in 2024.
  - 25 values above 100 are kept and counted (Norway's electricity in 18 years, Iceland's in 4, Albania's in 3): the directive's normalised renewable output exceeds consumption there. 63 values are provisional (flag p); 37 zeros are kept; there are no blanks. Kosovo is left out, as in the production table.
- **Cross-check** of the electricity share against `eurostat_electricity_production_annual`'s renewables (RA000) over its total. The two methods differ: the directive divides normalised output by consumption, and production is not normalised. They agree closely where trade is small: EU27 28.6 against 29.3 per cent in 2014 and 47.5 against 47.1 in 2024; Poland 12.4 against 12.5 and 30.4 against 30.5. They part where a country exports or imports much: Norway 115.1 against 97.9 (2024), Sweden 88.1 against 69.4, Denmark 79.7 against 88.9. Stated as the methods' difference, not a fault.
- **Terms:** ec.europa.eu's robots file was asked again in its own request (read 1508), byte for byte as session 2757's. Eurostat's verdict on record (read 280) stands.
- **Written under the data lock:** validated, archived (3,095 rows), in coverage. The patch applied cleanly with no marker. Coverage has 603 tables and `sources.csv` 693 sources, none twice. `finish_table.sh`: the release and license checks pass (603 tables, 0 problems).

## Requests (3 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | ec.europa.eu's robots file (its own request) | 200, as in session 2757 |
| 2 | nrg_ind_ren, every key (the fetch) | 200, 228,474 bytes |
| 3 | the NRG_BAL codelist | 200 |

Read recorded: 1508.

## Decisions made without you

- **Shares above 100 kept,** as Eurostat publishes them.
- **Run before session 2759,** so that the notes and the Stanford upload take its table.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eurostat_renewable_shares.py`, `tests/test_session2762.py`, this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `coverage.csv`, `docs/coverage.md`, `sources.csv`, `archive_manifest.csv`, the license record (read 1508), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c139/s2762/`, `runs/license_reads/s2762/`, `warehouse/raw/eurostat_renewable_shares/`.
