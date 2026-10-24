# Kenya's generation capacity by technology and electricity consumption by customer category, fiscal years 2023/24 to 2025/26 (EPRA, Energy and Petroleum Statistics Reports, tables 2.1 and 2.2)

Energy Research Warehouse (ERW), method note written in session 2326 (chain 108) for a table first written on 24 October 2026 (session 2325 of chain 108, its report `archive/sessions/SESSION_2325_REPORT.md`).

Tables: `epra_kenya_electricity_annual`

## Publisher and address

Energy and Petroleum Regulatory Authority, Kenya (EPRA), its Energy and Petroleum Statistics Reports, listed as PDF files on its statistics page (`https://www.epra.go.ke/index.php/statistics-0`, read 527). Three fiscal-year reports (July to June) are read, one request each:

- `https://www.epra.go.ke/sites/default/files/2024-10/EPRA%20Energy%20and%20Petroleum%20Statistics%20Report%20FY%202023-2024_2.pdf` ("Energy & Petroleum Statistics Report for the Financial Year Ended 30th June 2024", read 530)
- `https://www.epra.go.ke/sites/default/files/2025-09/Statistics-Report-June-2025-Web.pdf` (the year ended 30 June 2025, read 529)
- `https://www.epra.go.ke/sites/default/files/2026-09/Energy%20%26%20Petroleum%20Statistics%20Report%202026.pdf` (the year ended 30 June 2026, read 528)

Source id `epra:energy_petroleum_statistics_report`. From each report two tables of chapter 2 are taken: Table 2.1, "Installed, Effective and Captive Power Capacity as at 30th June <year>" (the 2024 report in lower case), with columns for interconnected installed and effective capacity, captive capacity, offgrid capacity, total installed capacity and the percentage of the total, a row a technology (Geothermal, Hydro, Thermal, Solar, Wind, Bioenergy, Imports, WHR or WHRC, Total); and Table 2.2, "A summary of energy consumption by each customer category during the financial year 2023/2024" (2024/2025; the 2026 report "during the year 2025/2026"), consumption in GWh and its percentage for Industrial, Domestic, Small commercial (SMEs), Street lighting, E-Mobility (Electric Mobility in 2024) and Total. The percentage columns are not taken.

Session 2325's probe (`runs/c108/s2325/probe.csv`) made 6 requests, at least 3 seconds apart: the robots file (read 525), the home page (read 526), the statistics page (read 527) and the three reports (HTTP 200: 4,410,843 bytes for 2026 at 2026-10-24T07:11:19Z, Last-Modified "Mon, 28 Sep 2026 10:44:25 GMT"; 1,861,039 bytes for 2025 at 07:12:01Z, "Mon, 29 Sep 2025 18:41:35 GMT"; 2,513,940 bytes for 2024 at 07:12:08Z, "Thu, 17 Oct 2024 13:42:23 GMT"). All six are saved in `runs/license_reads/s2325/`, and the reports' text, as pdftotext gave it, in `runs/c108/s2325/r04.txt` (2026), `r05.txt` (2025), `r06.txt` (2024) and `r2026.txt` (2026, laid out). The reports were seeded into `warehouse/raw/epra_kenya_electricity/20261024T071044Z_probe/`, and the trial and the write read them offline.

Connector: `warehouse/connectors/epra_kenya_electricity.py` (session 2325): `[--offline] [--out-dir DIR]`, at most three requests, the tables read with pdfplumber's table extraction (blank cells kept in place). Each part's technologies must add to its total row, and each technology's interconnected installed, captive and offgrid capacity to its total installed capacity, within 0.15 MW; the customer categories must add to their total within 0.15 GWh. A report without both tables, a title without its year, table 2.1 and 2.2 of different years, a row or category not in its map, a value that is not a number, a check that fails or a fiscal year given by two reports stops the run. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. The table is public, and it is held from the live set (listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`) and from the Redivis release (`STORAGE_HELD` in `warehouse/redivis/release_v1.py`).

## Vintage and revision

One write, run `20261024T071447Z` ("This run wrote 129 rows: 129 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs"), from the three saved reports. `retrieved_at` is each report's download time and `vintage` its Last-Modified: 2026-10-24T07:12:08Z and 2024-10-17T13:42:23Z for 2023/24, 07:12:01Z and 2025-09-29T18:41:35Z for 2024/25, 07:11:19Z and 2026-09-28T10:44:25Z for 2025/26. Each fiscal year's 43 rows carry its report as `source_url`.

The reports mark no figure as provisional. Each year is read from its own report only, so a figure EPRA revises in a later report is not taken. A later run merges by (entity, variable, ts_utc).

## Shape and variables

Series, 129 rows, one entity `epra:KE`, `node` Kenya, `geo` KE, `freq` P1Y, `market` blank; `unit` MW for capacity and MWh for consumption (EPRA's GWh times 1,000). 43 variables, each with a row in all three years: `capacity_<part>_<technology>` for the parts `interconnected_installed` (8: bioenergy, geothermal, hydro, imports, solar, thermal, wind, total), `interconnected_effective` (the same 8), `captive` (7: bioenergy, geothermal, hydro, solar, thermal, waste_heat_recovery, total), `offgrid` (5: hydro, solar, thermal, wind, total) and `total_installed` (9: all eight technologies and total), and `consumption_<category>` (6).

| Variable | June 2024 | June 2025 | June 2026 |
|---|---|---|---|
| capacity_interconnected_installed_total | 3,199.9 | 3,192.0 | 3,263.02 |
| capacity_interconnected_effective_total | 3,051.7 | 3,082.0 | 3,082.00 |
| capacity_captive_total | 532.6 | 603.8 | 676.60 |
| capacity_offgrid_total | 46.0 | 45.0 | 47.58 |
| capacity_total_installed_total | 3,778.5 | 3,840.8 | 3,987.20 |
| capacity_total_installed_geothermal | 943.7 | 943.7 | 1,013.68 |
| capacity_total_installed_hydro | 872.4 | 872.5 | 872.57 |
| capacity_total_installed_thermal | 636.1 | 627.1 | 630.15 |
| capacity_total_installed_solar | 442.9 | 514.1 | 587.45 |
| capacity_total_installed_wind | 436.1 | 436.1 | 436.05 |
| capacity_total_installed_bioenergy | 163.8 | 163.8 | 163.80 |
| capacity_total_installed_imports | 200.0 | 200.0 | 200.00 |
| capacity_total_installed_waste_heat_recovery | 83.5 | 83.5 | 83.50 |

MW as at 30 June, from the table (`runs/c108/s2326/notes/ke.out`); the column is the fiscal year's end, the row's `ts_utc` its 1 July a year earlier.

| Variable | 2023/24 | 2024/25 | 2025/26 |
|---|---|---|---|
| consumption_industrial | 5,431.74 | 5,620.71 | 5,920.06 |
| consumption_domestic | 3,220.78 | 3,640.32 | 4,327.07 |
| consumption_small_commercial | 1,715.54 | 1,913.26 | 2,012.17 |
| consumption_street_lighting | 103.60 | 150.43 | 173.17 |
| consumption_e_mobility | 1.26 | 5.04 | 12.25 |
| consumption_total | 10,472.92 | 11,329.75 | 12,444.71 |

GWh as EPRA prints them; the table holds each times 1,000 in MWh.

- **Imports are a capacity row.** EPRA's table 2.1 counts 200 MW of imports as interconnected installed and effective capacity, and in the total installed capacity of every year.
- **Captive capacity is mostly solar and bioenergy.** Captive solar grows 229.2, 300.5 and 373.30 MW; captive capacity is 14.10, 15.72 and 16.97 percent of the total installed (the 2024 report's text says 14.88 percent for June 2024, which its own table does not give: 532.6 / 3,778.5 is 14.10).
- **Effective capacity in June 2026.** The 2026 report prints effective capacity unchanged from June 2025 in total (3,082.00 MW) and for geothermal (876.10), although installed geothermal rose by 70 MW (the report: the 35 MW Kaishan and the 35 MW Globeleq plants at Menengai); its solar effective capacity, 210.30 MW, is above its installed, 210.25. The table keeps both as printed (`r04.txt`, table 2.1).
- **Consumption is sales.** The 2024 report's Table 2.4 gives KPLC's monthly energy purchased (13,684.84 GWh for the year) and sales; the sales total, 10,472.92 GWh, is table 2.2's total. EPRA puts system losses at 23.47 percent of energy purchased in 2023/24 (`r06.txt`), 23.36 in 2024/25 (`r05.txt`) and 21.38 in 2025/26 (`r04.txt`).
- **No zero, no negative value.** The smallest is offgrid hydro, 0.1 MW in every year.

## Placing values in time, and what is filled

`ts_utc` is the fiscal year's first day, 1 July at 00:00:00Z: 2023-07-01 for 2023/24, 2024-07-01 and 2025-07-01. Capacity is as at the fiscal year's last day, 30 June, so June 2026's capacity has the label 2025-07-01; consumption is the fiscal year's total. A cell EPRA leaves blank or marks "-" has no row; nothing is filled. Blank or "-" in all three years, so without a variable: captive wind and imports; offgrid geothermal, bioenergy, imports and waste heat recovery; interconnected waste heat recovery. Calendar-year and half-year reports are not read.

## License

Header: "License: public. Each report: material "may be freely used, shared, copied, reproduced, printed and/or stored, provided that appropriate acknowledgment is given of EPRA as the source and copyright holder". Cite: EPRA." `warehouse/metadata/license_verdicts.csv`: "Energy and Petroleum Regulatory Authority, Kenya (EPRA)", read 528, the notice on page 2 of the 2026 report, "Unless otherwise stated, material in this publication may be freely used, shared, copied, reproduced, printed and/or stored, provided that appropriate acknowledgment is given of EPRA as the source and copyright holder.", the same in the 2025 and 2024 reports (reads 529 and 530), verdict "may be public", if the ERW sells anything "may be public"; tables 2.1 and 2.2 name no third party. EPRA's robots file disallows Drupal's admin, search and user paths and names no AI agent (read 525). `docs/licenses.md`, the table's row: verdict today "may be public", flag public, "agrees", ERW verdict public.

## Checks (session 2326)

The figures in this note were computed from the rows of `warehouse/output/epra_kenya_electricity_annual.csv`, read past its 10 header lines (counted), and from session 2325's text of the reports, read only (scripts `runs/c108/s2326/notes/ke.py` and `ke2.py`, outputs `ke.out` and `ke2.out` beside them).

- 129 rows, 43 variables, 43 a year, fiscal years ending June 2024 to 2026, as header lines 1, 3 and 10 state; one entity; no (entity, variable, ts_utc) twice; no blank, zero or negative value; MW on every capacity row and MWh on every consumption row.
- **The table's sums:** each part's technologies against its total within 0.1 MW (captive -0.1 and offgrid 0.1 in 2024; interconnected installed 0.1 and offgrid 0.1 in 2025; 0 in 2026); each technology's interconnected installed, captive and offgrid capacity against its total installed within 0.1 MW (hydro and solar in 2025); the categories against their total within 10 MWh (2025 and 2026). Header line 3's 0.15 MW and 0.15 GWh hold.
- **Against the reports' text:** the totals of table 2.1 (3,199.9, 3,051.7, 532.6, 46.0, 3,778.5 for June 2024; 3,192.0, 3,082.0, 603.8, 45.0, 3,840.8 for June 2025; 3,263.02, 3,082.00, 676.60, 47.58, 3,987.20 for June 2026) and every figure of table 2.2 in `r06.txt`, `r05.txt` and `r04.txt` are the table's.
- **The trial against the table:** `runs/c108/s2325/trial/epra_kenya_electricity_annual.csv` has the same 129 keys with 0 differences in value or `retrieved_at`.
- Session 2325's cross-check (`runs/c108/s2325/cross.py`, `cross.out`, run on the trial): the capacity and consumption printed above; `irena_capacity_annual`'s Kenya at each December of 2023, 2024 and 2025: geothermal 984.7, 939.7 and 925.4 MW, renewable hydropower 892.8, 892.0 and 892.7, onshore wind 436.1 in each, solar photovoltaic 474.9, 551.1 and 551.1; `owid_ember_electricity_annual`'s Kenya demand 13.26, 13.69, 14.75 and 15.58 TWh for 2022 to 2025.
- Session 2326's own: EPRA's consumption against Ember's demand, below by 23.5 percent (2023/24 against 2023), 29.0 (2023/24 against 2024), 23.2 (2024/25 against 2024), 27.3 (2024/25 against 2025) and 20.1 (2025/26 against 2025).

## The session report against the table

Every figure of `SESSION_2325_REPORT.md` checked against the table, the reports' text and `cross.out` holds (fiscal years 2023/24 to 2025/26, 129 rows, 43 variables, the parts and categories, GWh times 1,000, the 0.15 MW and 0.15 GWh checks, the license notice from reads 528 to 530, the robots file, wind 436.1 MW in both, geothermal 943.7 against IRENA's 939.7, hydro 872.4 to 872.6 against 892.0 to 892.7 and about 2.3 percent below, solar 514.1 against 551.1, consumption 11.33 TWh in 2024/25, losses about 20 percent and more, 6 requests of 15, capacity dated by the fiscal year's 1 July), except:

- "about 23 per cent below Ember's calendar 2024 and 2025 demand (14.75 and 15.58 TWh)": 23.2 percent below 2024's, 27.3 below 2025's (point 1).
- "except monthly generation and peak demand, which the reports give only as charts": the 2024 report tabulates monthly energy purchased (point 2).

## What it does not hold

- Generation by technology or month, energy purchased, system losses, peak demand, customer numbers, tariffs and pass-through costs, regional consumption, the petroleum and renewable chapters, fiscal years before 2023/24 (the statistics page lists reports from 2020; the 2020 to 2023 ones are calendar-year reports) and the half-year reports.

## Points for the session to act on

1. **The report's comparison with Ember holds for one year only.** The report says EPRA's 2024/25 consumption, 11.33 TWh, is "about 23 per cent below Ember's calendar 2024 and 2025 demand (14.75 and 15.58 TWh)". Against 2024 it is 23.2 percent below, against 2025 27.3 percent (`ke2.out`).
2. **Monthly figures are in one report's tables.** The report says EPRA's reports carry the figures the plan asked for "except monthly generation and peak demand, which the reports give only as charts". The 2024 report's Table 2.4, "A summary of system losses during the financial year 2023/2024", gives for each month from July 2023 to June 2024 the total energy purchased (1,158.855 GWh in July 2023; 13,684.84 GWh for the year) and sold, and system losses (`r06.txt`, lines 514 to 525); the 2025 and 2026 reports chart system losses (Figures 2.16 to 2.18). The reason for not asking Kenya Power holds for 2024/25 and 2025/26, not for 2023/24.
3. **The header does not say June 2026's effective capacity repeats June 2025's.** EPRA's 2026 table prints interconnected effective capacity of 3,082.00 MW in total and 876.10 MW for geothermal, the June 2025 figures, though installed geothermal rose from 940.0 to 1,009.98 MW, and solar effective capacity (210.30 MW) above installed (210.25). The rows are EPRA's as printed; a clause in header line 3, or a check that effective does not exceed installed, would keep a reader from taking the 2026 effective column as measured.

Compared besides, with no contradiction found: the header's and docstring's counts, parts, technologies (WHR and WHRC both waste heat recovery), categories, units, the factor of 1,000, "A cell EPRA leaves blank or marks '-' has no row; nothing is filled", the dating by 1 July and each row's report against the rows and the reports' text. Consumption in table 2.2 is KPLC's sales, as the report says.

Acted on in session 2326: session 2325's report now gives EPRA's 2024/25 consumption as 23.2 per cent below Ember's 2024 demand and 27.3 per cent below 2025's, and names the 2024 report's monthly table 2.4 (energy purchased, sold and lost, 2023/24), which is not taken. Header line 3 now names, as the connector computes them, the effective capacity above installed (solar, June 2026) and the effective figures unchanged from June 2025 while installed changed (geothermal, solar, thermal and the total, June 2026). The table was written again offline: the same rows.
