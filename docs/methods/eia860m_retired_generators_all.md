# Every retired generator EIA lists, one row a generator (EIA-860M, sheets Retired and Retired_PR)

Energy Research Warehouse (ERW), method note written in session 2222 (chain 098) for a table first written on 6 October 2026 (session 133, `archive/sessions/SESSION_133_REPORT.md`, one of that session's approved pulls for the energy mix).

Tables: `eia860m_retired_generators_all`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-860M, Monthly Update to the Annual Electric Generator Report (`https://www.eia.gov/electricity/data/eia860m/`): the newest monthly workbook, here `https://www.eia.gov/electricity/data/eia860m/xls/august_generator2026.xlsx`, sheets Retired ("Inventory of Retired Generators as of August 2026") and Retired_PR (the same for Puerto Rico). Source id `eia:860m:retired`. Raw files under `warehouse/raw/eia860m_retired_all/<run_id>/`.

Connector: `warehouse/connectors/eia860m_retired_all.py` (session 133), `[--out-dir DIR]`. It reads the workbook through `eia860.py` (its sheet reader, code tables and labels) and writes every row of the two Retired sheets, where `eia860.py` keeps only the vintage's year and the year before (`eia860m_retired_generators`). A sheet title that does not say the vintage's month, an EIA code `eia860.py` does not know, a plant and generator id given twice, a non-numeric capacity or more than 400,000 rows stops the run. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names the connector or the table (`run_daily.sh` runs `eia860.py` every day, which does not write this table). The table is in `catalogue_hold` of `warehouse/supabase/live_set.yaml`: not loaded into the live set. Readers: `warehouse/derived/mix_stress.py` and `mix_views.py`.

## Vintage and revision

One run, `20261006T095425Z`; `retrieved_at` 2026-10-06T09:55:47Z and `vintage` 2026-08 in every row. A new vintage replaces the rows (a snapshot), but only when someone runs the connector: the operating and two-year tables move with `eia860.py`'s daily run, this one does not. On this machine all three hold vintage 2026-08 today. The header's last line says the copy here was restored from the Redivis draft by `scripts/sync.py`.

## Shape and variables

Entities, 7,334 rows, one a generator. `entity_id` `eia860:<plant id>:<generator id>`, `entity_type` generator, `status` retired, `eia_status` RE ("Retired") in every row; `capacity_mw` is EIA's nameplate capacity (equal to `nameplate_mw` in every row); `status_date` and `retirement_date` are the first day of EIA's retirement month (equal in every row); `geo` `US-<state>`; then EIA's plant, generator and utility ids, state, county, balancing authority, sector, technology (23 values), prime mover and energy source with their labels, the ERW's `technology_group`, net summer and winter capacity, and the operating year and month.

- 52 state codes: the 50 states, DC and PR (10 generators, 129.9 MW).
- Retirement dates 1972-11-01 to 2026-08-01: 16 generators before 2000, none in 2000 or 2001, then 225 in 2002 and 1,962 in the 2000s, 3,441 in the 2010s, 1,915 from 2020.
- Nameplate 306,513 MW in all: coal 145,939, natural gas 103,104, petroleum 27,283, nuclear 17,644, biomass 5,739, wind 2,069, hydro 2,042, other 1,053, geothermal 627, storage 569 (54 generators), solar 444. The largest unit is W H Zimmer (1,425.6 MW, coal, May 2022).

| Retired in | Generators | MW |
|---|---|---|
| 2015 | 407 | 25,714 |
| 2016 | 349 | 18,912 |
| 2017 | 265 | 13,956 |
| 2018 | 352 | 26,181 |
| 2019 | 386 | 21,550 |
| 2020 | 284 | 19,148 |
| 2021 | 275 | 11,104 |
| 2022 | 295 | 18,957 |
| 2023 | 474 | 17,342 |
| 2024 | 338 | 11,482 |
| 2025 | 209 | 5,710 |
| 2026 (to August) | 40 | 910 |

## Placing values in time, and what is filled

A snapshot: the rows are the workbook's as of its month. Dates are EIA's year and month, written as the first of the month. Nothing is filled. 44 generators (all retired from 1972 to 2010) have no coordinates; EIA gives a few a latitude or a longitude but not both, and the connector then leaves both empty and logs the count. The balancing authority is blank for 1,425 generators: 977 of the 1,978 retired before 2010, 80 of the 1,915 retired from 2020. Net summer capacity is blank for 56, net winter for 57; county for 2.

## License

Header: "License: public (EIA-PD)." `license_verdicts.csv`, EIA (read 1): "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.", verdict "may be public", an acknowledgment asked for. `docs/licenses.md`: "may be public", flag public, "agrees", ERW verdict public.

## Checks (session 2222)

The figures in this note were computed from the rows of `warehouse/output/eia860m_retired_generators_all.csv`, read past its 11 header lines (script `runs/c098/s2222/check_retired.py`).

- 7,334 rows, as the header states ("Rows: 7,334 of the 400,000 ceiling; retirements from 1972 to 2026"); no `entity_id` twice; every `entity_id` is `eia860:` plus the plant and generator ids; no capacity blank, zero or negative; no retirement before the unit's operating year.
- Against `eia860m_retired_generators` (249 rows, vintage 2026-08, retired 2025: 209, 2026: 40): all 249 are here, with the same retirement date, technology, state and energy source; capacities agree in value (68 are written "50" there and "50.0" here); this table holds no 2025 or 2026 retirement that the two-year table lacks.
- Against `eia860m_operating_generators` (28,605 rows, vintage 2026-08): no generator is in both.

## Where the description and the data disagree

1. **"The columns of eia860m_retired_generators."** The docstring and header say this table has that table's columns. The two-year table has one more, `energy_capacity_mwh` (session 34, EIA's nameplate energy capacity of a storage unit; its 8 storage generators all carry it). This table has no such column, so its 54 retired storage generators (569 MW) have no MWh.
2. **"Retirements from 1972 to 2026."** The header's range reads as a history from 1972. The sheets list 16 generators retired before 2000 and none in 2000 or 2001; in effect the table holds retirements from 2002, with a few older ones. Capacity in a month before 2002 cannot be built from it.

Acted on in session 2222: the connector's docstring and header text now say the table has the two-year table's columns but energy_capacity_mwh; the header changes at its next run (no schedule runs it), and the rows are unchanged. The history from 1972 is recorded, not changed.

## The session report against the table

The figures of `SESSION_133_REPORT.md` about this table hold: "The 860M pull was one workbook's Retired sheets, 7,334 rows", and the pull table's "400,000 | 7,334 | 22,002 | the workbook read three times" (22,002 is three times 7,334). The report's statement that capacity for gas, coal, nuclear and hydro is now given from 2019 concerns the derived tables, not this one, and was not tested here.

## What it does not hold

- Operating or planned generators (`eia860m_operating_generators`, `eia860m_planned_generators`); storage energy capacity; retirements before 2002 beyond the 16 EIA lists; earlier vintages of the sheets; the reason for a retirement.
