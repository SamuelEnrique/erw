# Session 2817 report: the package's and the site's records

26 October 2026, about 05:53 UTC, on lab-desktop (the data machine), chain 143, unattended. It ran after session 2818, so that every table of the chain was in. Precheck passed (`runs/c143/pre2817.out`). Model spend USD 0. Pulls: none.

## Read these first

- **The license record** (`scripts/licenses.py tables --headers` with main's output folder, then `write` and `check`): 622 tables, 259 publishers with a verdict, 1,626 requests in the record; 0 problems. Nothing changed: the chain's sessions had written it.
- **`release_v1.py --check`:** passed (0 differences).
- **`package/tools/build_tables.py --check`** found the package's `tables.csv` stale by this chain's seven tables:
  - `eurostat_electrification_rate_annual`
  - `destatis_de_electricity_monthly`
  - `bfe_ch_electricity_wednesdays`
  - `czso_cz_regional_electricity_annual`
  - `eurostat_nuclear_fuel_cycle_annual`
  - `eurostat_ev_recharging_power_annual`
  - `eurostat_industry_electricity_annual`

  It was rebuilt (622 tables: public 460, internal 112, unsettled 50), with the site's two files, and the check then passed.
- **Tests:** 1001, 1008, 1009, 378, 205, 152, 2718 and 444, and the chain's own (2806 to 2809, 2812, 2813, 2818), passed (97 tests, 1 skipped).

## Decisions made without you

- **Run after session 2818,** whose source added a table (industry's electricity).

## For Samuel's ruling

- None.

## Files

- Changed: `package/src/erw/data/tables.csv`, `site/data/table_citations.json`, `site/data/table_verdicts.json`.
- New: this report.
- On the data machine only: `runs/c143/pre2817.out`, `lic2817*.out`, `rel2817.out`, `bt2817*.out`, `t2817.out`.
