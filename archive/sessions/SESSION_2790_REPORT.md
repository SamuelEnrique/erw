# Session 2790 report: European energy import dependency by product a year (Eurostat's nrg_ind_id), the third own choice

26 October 2026, about 02:03 to 02:08 UTC, on lab-desktop (the data machine), chain 141, unattended. Run before session 2787, so that its table is described and uploaded with the chain's others. Precheck passed (`runs/c141/pre2790.out`). Model spend USD 0. Pulls: 3 requests of 20 (1 by the probe, 2 by the fetch).

## Read these first

- **Why this source:** a measure the ERW did not hold, under a verdict on record. Each country's net imports as a share of its gross available energy, the headline of Europe's supply security, for gas, oil, coal and in total. Asked with a wildcard key, as the memory says.
- **`eurostat_import_dependency_annual`, public, held from the live set and in the Stanford holds** (`warehouse/connectors/eurostat_import_dependency.py`, 16,627 rows, 39 areas, 13 products, 1990 to 2024):
  - From nrg_ind_id, the whole dataset (1.2 MB), with the SIEC codelist for the products' names. Eurostat's last update: 16/07/26 23:00.
  - `import_dependency` in pct, negative for a net exporter. The products are the total, solid fossil fuels and five coals, natural gas, oil and its crude and NGL parts, peat, and oil shale.
  - The EU27's total: 50.02 per cent in 1990, 55.74 in 2010, 57.29 in 2024.
  - **251 values outside -100 to 200** (from -31,930 to 3,601) where a product's gross available energy is near zero. They are kept as Eurostat publishes them and counted in the header. 6,959 zeros are kept. The United Kingdom and Kosovo are left out, as in the production table.
- **Cross-check** of natural gas (G3000) against `eurostat_gas_balance_monthly`'s net imports over its observed inland consumption, twelve months summed, per cent:
  - Germany: 99.6 against 100.1 (2019), 93.8 against 93.7 (2023).
  - Italy: 95.0 against 95.1, 95.8 against 96.3.
  - Spain: 101.9 against 101.5, 98.8 against 98.5.
  - France: 104.4 against 104.5, 97.8 against 99.5.

  Close, the monthly balance's observed consumption standing for the annual gross available energy.
- **Terms:** ec.europa.eu's robots file asked again in its own request (read 1587), byte for byte as before. Eurostat's verdict (read 280) stands; the license record shows the table as agreed, public.
- **Written under the data lock:** validated, archived (16,627 rows), in coverage. The patch applied cleanly with no marker. Coverage has 611 tables and `sources.csv` 701 sources, none twice. `finish_table.sh`: the release and license checks pass (611 tables, 0 problems).

## Requests (3 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | ec.europa.eu's robots file (its own request) | 200, as before |
| 2 | nrg_ind_id, every key (the fetch) | 200, 1,217,578 bytes |
| 3 | the SIEC codelist | 200 |

Read recorded: 1587.

## Decisions made without you

- **Extreme ratios kept,** as Eurostat publishes them, counted rather than dropped.
- **Heating and cooling degree days not taken:** Eurostat gives them in Celsius degree days on bases the validator does not hold.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eurostat_import_dependency.py`, `tests/test_session2790.py`, this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `coverage.csv`, `docs/coverage.md`, `sources.csv`, `archive_manifest.csv`, the license record (read 1587), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c141/s2790/`, `runs/license_reads/s2790/`, `warehouse/raw/eurostat_import_dependency/`.
