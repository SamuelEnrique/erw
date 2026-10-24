# EIA-860M's planned generators, one row a generator, planned or under construction, a snapshot of EIA's newest monthly inventory (vintage 2026-08)

Energy Research Warehouse (ERW), method note written in session 2242 (chain 101) for a table first written on 25 September 2026 (session 8, commit `f433610`, `archive/sessions/SESSION_8_REPORT.md`, "Task 2: EIA-860M generators (entities)"). The same connector writes `eia860m_operating_generators` and `eia860m_retired_generators` (notes beside this one).

Tables: `eia860m_planned_generators`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-860M, "Monthly Update to the Annual Electric Generator Report", `https://www.eia.gov/electricity/data/eia860m/`; the table's workbook is `https://www.eia.gov/electricity/data/eia860m/xls/august_generator2026.xlsx`, sheets Planned and Planned_PR ("Inventory of Planned Generators as of August 2026" and "Inventory of Planned Generators as of August 2026 - Puerto Rico"). Labels from the EIA-860 instructions, `https://www.eia.gov/survey/form/eia_860/instructions.pdf`. Source id `eia:860m`. Raw files under `warehouse/raw/eia860/<run_id>/` (none on this machine).

Connector: `warehouse/connectors/eia860.py` (session 8), `[--force] [--from-raw RUN_ID] [--out-dir DIR]`; its reading of the page, its checks and its rule for writing are those of `docs/methods/eia860m_operating_generators.md`. For this table: EIA codes U, V and TS are `under_construction`, P, L, T and OT `planned`; a code outside the seven stops the run.

Schedule: the daily run, `warehouse/run_daily.sh` (`pull eia860`), on the GitHub runner (`.github/workflows/daily-prices.yml`, cron `0 14 * * *`); no other schedule runs the connector (`run_data_machine.sh`, `run_data_machine_tables.sh`, `run_monthly.sh` and `refresh_supply.sh` do not name it). `warehouse/scheduled.py` restores and reads the table for `project_map` (monthly). `run_status.csv`: the same 28 runs as the operating table, 20260926T000505Z (local) to 20261023T144817Z (github), all ok, 26 of them writes of vintage 2026-08. `archive_manifest.csv`: 2,316 rows as of run 20261023T152740Z-github. Not loaded into the live set (no rule in `live_set.yaml`; it reaches Supabase through `energy_projects`). Readers: the builders `energy_projects.py`, `project_map.py`, `ercot_node_planned_generation.py`, `siting_page.py`, `storage_buildout.py`, `storage_capacity.py` and `storage_owners.py`; `site/lib/siting.ts`, `site/app/cost-of-power/AllGridsView.tsx`, `site/lib/pages.ts` and the chat's table list.

## Vintage and revision

`vintage` is 2026-08 in every row. The copy here was restored from the Redivis draft by `scripts/sync.py`; its header names run `20261010T144729Z`, and `retrieved_at` is 2026-10-10T14:48:42Z in every row. A new vintage replaces every row: a generator that begins operating moves to `eia860m_operating_generators` under the same `entity_id`, and one EIA drops from its plans leaves the table. EIA revises planned months and capacities from one vintage to the next; the ERW holds only the newest.

## Shape and variables

Entities, 2,316 rows, 34 columns: the columns of `eia860m_operating_generators`, with `planned_operation_date` in place of `operating_year`, `operating_month` and `planned_retirement_date`. 1,584 plants, 52 states (the 50, DC and Puerto Rico), 47 balancing authority codes, 976 operators. Puerto Rico: 5 generators, 177.2 MW.

| status | EIA status | Label | Rows | Nameplate MW |
|---|---|---|---|---|
| planned | P | Planned for installation, but regulatory approvals not initiated | 684 | 100,029.3 |
| planned | L | Regulatory approvals pending. Not under construction | 393 | 62,758.2 |
| planned | T | Regulatory approvals received. Not under construction | 224 | 27,180.3 |
| under_construction | U | Under construction, less than or equal to 50 percent complete | 486 | 54,706.6 |
| under_construction | V | Under construction, more than 50 percent complete | 373 | 25,209.7 |
| under_construction | TS | Construction complete, but not yet in commercial operation | 156 | 18,837.0 |

No row carries EIA's code OT. Nameplate in all: 288,721.1 MW (planned 1,301 rows, 189,967.8 MW; under construction 1,015 rows, 98,753.3 MW); net summer 281,147.8 MW, net winter 283,503.3 MW, both given in every row.

| technology_group | Rows | Nameplate MW |
|---|---|---|
| solar | 1,079 | 122,381.4 |
| natural_gas | 475 | 69,448.1 |
| storage | 493 | 67,058.1 |
| wind | 81 | 23,753.9 |
| nuclear | 5 | 4,968.0 |
| hydro | 117 | 431.0 |
| biomass | 29 | 211.0 |
| petroleum | 23 | 173.8 |
| geothermal | 9 | 157.3 |
| other | 5 | 138.5 |

- `planned_operation_date` from 2026-08-01 to 2039-12-01: 603 rows in 2026, 815 in 2027, 420 in 2028, 208 in 2029, 221 in 2030, 39 in 2031, then 10 from 2032 to 2039. None is before the vintage month.
- Nameplate from 0.1 MW to 2,640.0 MW (Coastal Virginia Offshore Wind (CVOW) Commercial Project, `eia860:64550:CVOWC`).
- Blanks: `status_date` in every row and `energy_capacity_mwh` in every row (as the docstring and header say); `county` 5; `balancing_authority` 12; `generator_id` 1 (`eia860:64835:`, Silver Queen Wind Farm, 252 MW). No row lacks a latitude or longitude.

## Placing values in time, and what is filled

No series. `status_date` is empty: a planned generator has no operating month yet. `planned_operation_date` is the first day of EIA's planned month (EIA gives months). The 493 planned storage generators carry no energy capacity: EIA's Planned sheet has no such column, and nothing is estimated from their megawatts.

## License

Header: "License: public (EIA-PD)." `license_verdicts.csv`, EIA (read 1): "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.", verdict "may be public". `docs/licenses.md`, the table's row: EIA, "may be public", flag public, "agrees", ERW verdict public. No row in `license_status.csv`.

## Checks (session 2242)

The figures in this note were computed from the rows of `warehouse/output/eia860m_planned_generators.csv`, read past its 13 header lines (scripts `runs/c101/s2242/check_eia860m.py` and `cross_eia860m.py`).

- 2,316 rows, as the header states; no `entity_id` twice; `entity_id` is `eia860:` plus `plant_id` and `generator_id`, and `geo` is `US-` plus `state`, in every row; `capacity_mw` equals `nameplate_mw` as text in every row; one `vintage`, `source_url` and `retrieved_at`.
- No `entity_id` is also in the operating or retired tables, nor in `eia860m_retired_generators_all`.
- Against `energy_projects` (its rows from this table, vintage 2026-08): 2,316 in both, the same ids, capacity and status in every row.

## Where the description and the data disagree

1. **"Earlier vintages are in git history."** As for the operating table: the tables left git in session 9 (commit `b5006bf6`), and git holds only session 8's copy of vintage 2026-08.
2. **"Writes only when the newest published vintage differs."** `run_status.csv` records 26 writes of vintage 2026-08 and 2 runs that wrote nothing; the runner wrote on each of its 25 runs (see the operating table's note).
3. **The generator id.** The docstring gives `entity_id` as `eia860:<plant id>:<generator id>`; one row has no generator id, so its `entity_id` is `eia860:64835:`.

## The session report against the table

`SESSION_8_REPORT.md`: 2,316 rows, and "`status` `planned` (P, L, T, OT) or `under_construction` (U, V, TS), EIA's code kept": both hold.

## What it does not hold

- Planned storage's energy capacity; generators already operating or retired; interconnection queue positions that EIA does not list (`energy_projects` joins the grids' queues); earlier vintages, so no record of how a generator's planned month moved.
