# EIA-860M's operating generators, one row a generator, a snapshot of EIA's newest monthly inventory (vintage 2026-08)

Energy Research Warehouse (ERW), method note written in session 2242 (chain 101) for a table first written on 25 September 2026 (session 8, commit `f433610`, `archive/sessions/SESSION_8_REPORT.md`, "Task 2: EIA-860M generators (entities)"). Its two siblings from the same workbook and connector are `eia860m_planned_generators` and `eia860m_retired_generators` (notes beside this one); every retired generator EIA lists is `eia860m_retired_generators_all` (`docs/methods/eia860m_retired_generators_all.md`).

Tables: `eia860m_operating_generators`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-860M, "Monthly Update to the Annual Electric Generator Report". The page `https://www.eia.gov/electricity/data/eia860m/` links one workbook a month; the table's is `https://www.eia.gov/electricity/data/eia860m/xls/august_generator2026.xlsx`, sheets Operating and Operating_PR (their titles, as the header quotes them: "Inventory of Operating Generators as of August 2026" and "Inventory of Operating Generators as of August 2026 - Puerto Rico"). Labels for codes come from the EIA-860 instructions, `https://www.eia.gov/survey/form/eia_860/instructions.pdf`. Source id `eia:860m` (`warehouse/metadata/sources.csv`, license public). Raw files under `warehouse/raw/eia860/<run_id>/` (none on this machine).

Connector: `warehouse/connectors/eia860.py` (session 8), `[--force] [--from-raw RUN_ID] [--out-dir DIR]`. It reads EIA's page, skips a linked month later than today's, and takes the newest link that answers with a workbook (the bytes begin `PK`; session 8 found EIA linking September to December 2026 with HTML pages behind them). Each sheet's title must say "as of <Month Year>" of the vintage; a prime mover, energy source or technology text not in the connector's tables, a plant and generator given twice, or a megawatt cell that is not a number stops the run. It writes the three tables only when EIA's newest vintage differs from the one the tables hold, or with `--force` or `--from-raw`.

Schedule: the daily run, `warehouse/run_daily.sh` (`pull eia860 "$PYTHON" warehouse/connectors/eia860.py`, "Session 8 entities"), on the GitHub runner (`.github/workflows/daily-prices.yml`, cron `0 14 * * *`). No step of `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh` or `warehouse/refresh_supply.sh` runs it; `warehouse/scheduled.py` names the table only as an input its builders restore and read (`project_map`, monthly; `merchant_revenue`, `merchant_hubs`, `seller_hybrid`, `generator_hourly_export` on the data machine). `run_status.csv` records 28 runs from 20260926T000505Z (local) to 20261023T144817Z (github), all ok: 2 "vintage 2026-08 unchanged" and 26 "vintage 2026-08" (25 of them on the runner). `archive_manifest.csv`: 28,605 rows as of run 20261023T152740Z-github. Not loaded into the live set: `warehouse/supabase/live_set.yaml` has no rule for it ("the operating and planned generators reach Supabase through energy_projects", session 19). Readers: the builders `energy_projects.py`, `project_map.py`, `storage_buildout.py`, `storage_capacity.py`, `storage_owners.py`, `merchant_revenue.py`, `seller_hybrid.py`, `generator_hourly_export.py`, `grid_peak_vs_capacity.py`, `mix_stress.py`, `mix_views.py`, `battery_solar.py` and `eqr_terms.py`; `site/lib/pages.ts` and the chat's table list (`site/lib/chat/spec.json`).

## Vintage and revision

`vintage` is 2026-08 in every row: EIA's inventory as of August 2026. The copy here was restored from the Redivis draft by `scripts/sync.py` (its last header line); its header names run `20261010T144729Z`, and `retrieved_at` is 2026-10-10T14:48:42Z in every row. `coverage.csv` names a later write of the same vintage, 2026-10-23T14:48:17Z (github), with the same 28,605 rows. On 23 October the runner still found August 2026 as EIA's newest published vintage.

The table is a snapshot: a new vintage replaces every row, so a generator that leaves EIA's operating inventory leaves the table. EIA revises a generator's figures from one monthly vintage to the next; the ERW holds only the newest.

## Shape and variables

Entities, 28,605 rows, 36 columns: the entities columns (`entity_id` `eia860:<plant id>:<generator id>`, `entity_type` generator, `name` EIA's plant name, `geo` US-<state>, `lat`, `lon`, `capacity_mw` EIA's nameplate MW, `status`, `status_date`, `operator` EIA's "Entity Name", `source`), then `source_url`, `retrieved_at`, `vintage`, EIA's ids and places (`plant_id`, `generator_id`, `utility_id`, `state`, `county`, `balancing_authority`, `sector`), EIA's codes with the ERW's labels (`technology`, `technology_group`, `prime_mover`, `prime_mover_label`, `energy_source`, `energy_source_label`), `nameplate_mw`, `net_summer_mw`, `net_winter_mw`, `eia_status`, `eia_status_label`, `operating_year`, `operating_month`, `planned_retirement_date` and `energy_capacity_mwh`.

14,767 plants, 52 states (the 50, DC and Puerto Rico), 65 balancing authority codes, 6,055 operators. Puerto Rico: 228 generators, 6,474.3 MW.

`status` is `operating` in every row, whatever EIA's code:

| EIA status | Label | Rows | Nameplate MW |
|---|---|---|---|
| OP | Operating | 26,269 | 1,391,371.9 |
| SB | Standby/Backup: available for service but not normally used | 1,577 | 8,897.5 |
| OA | Out of service but expected to return to service in next calendar year | 219 | 7,103.4 |
| OS | Out of service and NOT expected to return to service in next calendar year | 540 | 10,573.7 |

Nameplate in all: 1,417,946.5 MW; net summer 1,324,722.1 MW (28,539 rows), net winter 1,367,044.5 MW (28,531 rows). A reader who wants capacity in service takes `eia_status` OP; the 540 OS generators are in this table though EIA does not expect them back next year.

| technology_group | Rows | Nameplate MW |
|---|---|---|
| natural_gas | 6,832 | 582,786.9 |
| coal | 448 | 182,158.0 |
| solar | 8,313 | 169,136.8 |
| wind | 1,580 | 166,845.0 |
| nuclear | 96 | 103,698.4 |
| hydro | 4,003 | 80,163.4 |
| storage | 1,293 | 76,870.0 |
| petroleum | 3,974 | 36,064.7 |
| biomass | 1,754 | 12,517.5 |
| geothermal | 163 | 4,049.2 |
| other | 148 | 3,596.1 |
| blank | 1 | 60.5 |

- Batteries (prime mover BA): 1,137 generators, 54,488.9 MW, each with `energy_capacity_mwh`, 150,437.6 MWh in all. Six more rows carry an energy capacity (five flywheels, FW, and one compressed air unit, CE): 1,143 rows with `energy_capacity_mwh`, 150,584.6 MWh.
- Nameplate from 0.1 MW to 2,561.2 MW (SunZia Wind South, `eia860:66923:SZW-S`); no zero or negative nameplate. Net summer capacity is 0 in 7 rows and net winter in 16.
- Operating months from 1891-01 to 2026-08. `planned_retirement_date` is given in 525 rows, from 2026-08-01 to 2072-08-01 (66 in 2027, 66 in 2028, 42 in 2026).
- Blanks: `county` 78, `balancing_authority` 963, `net_summer_mw` 66, `net_winter_mw` 74, `energy_capacity_mwh` 27,462, `planned_retirement_date` 28,080; `generator_id` 1 (`eia860:62844:`, Cranberry Point Energy Storage, 150 MW); `technology`, `technology_group`, `energy_source` and `energy_source_label` 1 (`eia860:55699:1`, Bayswater Peaking Facility, a 60.5 MW gas turbine). No row lacks a latitude or longitude.

## Placing values in time, and what is filled

The table holds no series. `status_date` is the first day of EIA's operating month (EIA gives months, not days), and equals `operating_year` and `operating_month` in every row; no operating month is after the vintage month. `planned_retirement_date` is the first day of EIA's planned month. A blank cell stays blank: nothing is filled from another vintage or table.

## License

Header: "License: public (EIA-PD)." `warehouse/metadata/license_verdicts.csv`, EIA (read 1): "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.", verdict "may be public", if the ERW sells anything "may be public"; EIA asks for the acknowledgment "Source: U.S. Energy Information Administration" with the date. `docs/licenses.md`, the table's row: EIA, "may be public", flag public, "agrees", ERW verdict public. `license_status.csv` has no row for it.

## Checks (session 2242)

The figures in this note were computed from the rows of `warehouse/output/eia860m_operating_generators.csv`, read past its 13 header lines (scripts `runs/c101/s2242/check_eia860m.py` and `cross_eia860m.py`, outputs beside them).

- 28,605 rows, as the header states; no `entity_id` twice; `entity_id` is `eia860:` plus `plant_id` and `generator_id` in every row; `geo` is `US-` plus `state` in every row; `capacity_mw` equals `nameplate_mw`, as text, in every row; one `vintage`, one `source_url` and one `retrieved_at`.
- No `entity_id` of this table is in `eia860m_planned_generators` or `eia860m_retired_generators`, nor in `eia860m_retired_generators_all`.
- Against `energy_projects` (its rows from this table, vintage 2026-08, built by run 20261019T203519Z): 28,605 rows in both, the same ids, the same capacity and status in every row.
- Against `eia860_plants_annual` (EIA-860, 2025): 14,699 of the 14,767 plants are there (99.5 percent), as `docs/methods/eia860_plants_annual.md` says.

## Where the description and the data disagree

1. **"Earlier vintages are in git history."** The header says so, and the docstring ("earlier vintages remain in git history and in the raw files"). The tables left git in session 9 (commit `b5006bf6`); git holds this file only as session 8 wrote it, vintage 2026-08. A vintage replaced from now on is in no commit. The ERW's archive keeps a table's new and changed rows (`ARCHITECTURE.md`, section 1a), and the raw workbooks are not on this machine.
2. **"Writes only when the newest published vintage differs from the one in the tables."** The docstring says so of the daily run. `run_status.csv` records 26 writes of the same vintage, 2026-08, and only 2 runs that wrote nothing; every one of the runner's 25 runs wrote. `stored_vintage()` returns no vintage when any of the three tables is missing from the machine, so the rule holds only where all three are on hand.
3. **A blank code passes the label check.** The docstring: "A code or technology not in these tables fails the run". A blank one does not: `eia860:55699:1` has no technology and no energy source, so its `technology_group` is blank, the one row of the 28,605 with none. And `eia860:62844:` has no generator id, so its `entity_id` ends in a colon.

## The session report against the table

Every figure of `SESSION_8_REPORT.md` about this table holds: 28,605 rows; vintage 2026-08 (`august_generator2026.xlsx`); status `operating` for EIA codes OP, SB, OA and OS with EIA's code in `eia_status`; the Puerto Rico sheet included. "Last modified 2026-09-23" is not in the table (no column holds the workbook's Last-Modified), so it is not checked here.

## What it does not hold

- Planned and retired generators (`eia860m_planned_generators`, `eia860m_retired_generators`, `eia860m_retired_generators_all`); earlier vintages; EIA-860's annual detail of plants, owners and storage (`eia860_plants_annual`, `eia860_schedules`); generation; the workbook's publication time.
