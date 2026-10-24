# EIA-860M's generators retired in the vintage's year and the year before, one row a generator (vintage 2026-08: retired in 2025 or 2026)

Energy Research Warehouse (ERW), method note written in session 2242 (chain 101) for a table first written on 25 September 2026 (session 8, commit `f433610`, `archive/sessions/SESSION_8_REPORT.md`, "Task 2: EIA-860M generators (entities)"). Every retired generator EIA lists, back to 1972, is `eia860m_retired_generators_all` (`docs/methods/eia860m_retired_generators_all.md`); the operating and planned generators are the notes beside this one.

Tables: `eia860m_retired_generators`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-860M, `https://www.eia.gov/electricity/data/eia860m/`; the workbook `https://www.eia.gov/electricity/data/eia860m/xls/august_generator2026.xlsx`, sheets Retired and Retired_PR ("Inventory of Retired Generators as of August 2026" and "Inventory of Retired Generators as of August 2026 - Puerto Rico"). Source id `eia:860m`. Raw files under `warehouse/raw/eia860/<run_id>/` (none on this machine).

Connector: `warehouse/connectors/eia860.py` (session 8); its reading and checks are those of `docs/methods/eia860m_operating_generators.md`. For this table every row of the two sheets gets EIA status RE, label "Retired", `status` `retired`; then only the rows whose retirement year is the vintage's year or the year before are kept (the log line "retired: N of M retired in Y-1 or Y").

Schedule: the daily run, `warehouse/run_daily.sh` (`pull eia860`), on the GitHub runner (`.github/workflows/daily-prices.yml`, cron `0 14 * * *`); no other schedule runs the connector. `warehouse/scheduled.py` restores and reads the table for the data machine's `merchant_revenue`, `merchant_hubs`, `seller_hybrid` and `generator_hourly_export`. `run_status.csv`: the same 28 runs as the operating table, all ok. `archive_manifest.csv`: 249 rows as of run 20261023T152740Z-github. Loaded whole into the live set: `live_set.yaml`, `full`, `'^eia860m_retired_generators$'` (session 19). Readers: the builders `battery_solar.py`, `generator_hourly_export.py`, `merchant_revenue.py`, `mix_stress.py`, `mix_views.py`, `seller_hybrid.py`, `storage_buildout.py` and `storage_capacity.py`; `site/lib/packages.ts` and the chat's table list.

## Vintage and revision

`vintage` is 2026-08 in every row. The copy here was rebuilt from the ERW's archive by `warehouse/restore_tables.py` "as of run 20261020T063359Z-github" (header line 1), and the connector's header that follows names run `20261020T061209Z`; `retrieved_at` is 2026-09-26T00:04:26Z in every row (disagreement 1). A new vintage replaces every row; when the vintage's year turns to 2027, the generators retired in 2025 leave the table (they stay in `eia860m_retired_generators_all`).

## Shape and variables

Entities, 249 rows, 36 columns: the columns of `eia860m_operating_generators` without `planned_retirement_date`, with `retirement_date` before `operating_year` and `operating_month`. 116 plants, 40 states, 30 balancing authority codes (17 rows blank), 109 operators. Puerto Rico: 3 generators, 0.8 MW.

- Retired in 2025: 209 generators, 5,710.2 MW; in 2026 (January to August): 40, 909.9 MW. Nameplate in all 6,620.1 MW; net summer 5,839.1 MW (248 rows; one blank), net winter 6,353.9 MW.
- Retirement months, rows: 2025-01 21, 02 14, 03 27, 04 6, 05 35, 06 12, 07 9, 08 6, 09 10, 10 24, 11 12, 12 33; 2026-01 4, 02 2, 03 3, 04 none, 05 14, 06 9, 07 3, 08 5.

| technology_group | Rows | Nameplate MW |
|---|---|---|
| coal | 8 | 2,626.0 |
| natural_gas | 61 | 2,033.1 |
| petroleum | 84 | 1,078.6 |
| biomass | 43 | 352.8 |
| storage | 8 | 338.5 |
| other | 6 | 96.8 |
| geothermal | 2 | 30.0 |
| hydro | 8 | 27.4 |
| wind | 20 | 23.4 |
| solar | 9 | 13.5 |

- Largest: Intermountain Power Project unit 2 (`eia860:6481:2`), 820 MW of conventional steam coal. Smallest 0.1 MW. First operated from 1908 to 2024.
- `energy_capacity_mwh` in 8 rows (the 8 storage generators' energy capacities sum to 1,236.1 MWh; the largest 1,200).
- Net summer capacity 0 in 2 rows and net winter 0 in 3.

## Placing values in time, and what is filled

No series. `retirement_date` and `status_date` are the first day of EIA's retirement month, the same in every row; EIA gives months. Nothing is filled.

## License

Header: "License: public (EIA-PD)." `license_verdicts.csv`, EIA (read 1): "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.", verdict "may be public". `docs/licenses.md`, the table's row: EIA, "may be public", flag public, "agrees", ERW verdict public. No row in `license_status.csv`.

## Checks (session 2242)

The figures in this note were computed from the rows of `warehouse/output/eia860m_retired_generators.csv`, read past its 13 header lines (scripts `runs/c101/s2242/check_eia860m.py` and `cross_eia860m.py`).

- 249 rows, as the header states; no `entity_id` twice; `entity_id`, `geo` and `capacity_mw` formed as the header says in every row; every retirement in 2025 or 2026, as the docstring says ("generators retired in the vintage's year or the year before").
- No `entity_id` is also in the operating or planned tables.
- Against `eia860m_retired_generators_all` (7,334 rows, vintage 2026-08): all 249 are there with the same retirement date and the same capacity in value; and every row there retired in 2025 or 2026 is here (249 of 249). 68 capacities are written differently ("50" here, "50.0" there), as that table's note found.

## Where the description and the data disagree

1. **The run in the header is not the run in the rows.** The header names run `20261020T061209Z`; every row's `retrieved_at` is 2026-09-26T00:04:26Z. The copy was rebuilt from the archive, which leaves `retrieved_at` out when it compares rows and keeps a row's `retrieved_at` from the run that first archived its values (`warehouse/archive/archive.py`, `VOLATILE`). The values are those of vintage 2026-08 either way; a reader who needs the retrieval of a row takes the header's run as the last write and `retrieved_at` as the first.
2. **"Earlier vintages are in git history."** As for the operating table: the tables left git in session 9 (commit `b5006bf6`); git holds only session 8's copy of vintage 2026-08.
3. **"Writes only when the newest published vintage differs."** `run_status.csv` records 26 writes of vintage 2026-08 and 2 runs that wrote nothing (see the operating table's note).

Acted on in session 2242: `eia860.py`'s docstring and header now say that earlier vintages are in the raw files and the archive (the tables left git in session 9), and that a run writes only when the vintage differs from the tables on the machine that runs it, so every run on the GitHub runner, which holds no tables, writes. The rows are unchanged; the next write carries the header. The rows without a generator id or a technology, and the first-retrieval times the archive keeps, are EIA's or the archive's, recorded, not changed.

## The session report against the table

`SESSION_8_REPORT.md`: 249 rows; "retired: retirement year 2025 or 2026 (the vintage year and the year before), `retirement_date` and `status_date` at the first of EIA's month": all hold.

## What it does not hold

- Generators retired before 2025 (`eia860m_retired_generators_all`, 1972 on); the reason for a retirement; earlier vintages; the retired units' generation.
