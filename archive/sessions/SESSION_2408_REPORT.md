# Session 2408 report: Guatemala's generation by fuel, trade and demand, a month, 2017 to 2025 (AMM)

24 October 2026, from 10:24 UTC, on lab-desktop (the data machine), the third session of `queue/done/114-day-15-november-data-paraguay-panama-guatemala-namibia.md`, unattended. Precheck passed (`runs/c114/pre2408.out`). Model spend USD 0. Pulls: 14 of 15 (below).

## Read these first

- **One internal table:** `amm_guatemala_generation_monthly`, 1,739 rows, January 2017 to December 2025. It is written, validated, archived, in coverage (sector power), and held from the live set. It comes from the Administrador del Mercado Mayorista's yearly workbooks "Generacion Mensual por Planta (XLS)", one a year (reads 657 to 665 on this branch's numbering):
  - generation by fuel: geothermal, wind, solar, hydro, biogas, biomass, syngas (from 2021), natural gas (from 2019), coal, petroleum coke (from 2018), bunker and diesel;
  - the total, imports, exports, international transactions (`net_exports`, TRANSACCIONES INTERNACIONALES (NETO), exports less imports; this line first said "regional"), and the national interconnected system's demand (`demand_sni`, generation plus imports less exports, its losses included);
  - generation is the system's executed dispatch, distributed renewable generation included (session 2410's note);
  - in MWh (the workbooks' GWh times 1,000).
- **Every check holds in every month:**
  - the fuels add to the fuel block's TOTAL, and that total equals GENERACION TOTAL;
  - exports less imports equal TRANSACCIONES, and generation less TRANSACCIONES equals the demand;
  - each row's months add to its own total column;
  - all within 0.01 GWh.
  - A fuel a year's workbook does not list has no row, and neither does a blank month (petroleum coke's first months of 2018, natural gas's of 2019). Zeros are written as published.
- **How the files were found:** AMM's annual reports frame chooses a report by script. Its script `js/informes.js` (read 656) builds the address `pdfs2/pub_gen_mensual_x_planta/GM<year>0101.xls` (`.xlsx` from 2021), with no key or login. The same address is what the page's own button opens.
- **Not taken:**
  - the peak demand (MW), which is not in these workbooks;
  - AMM's two statistics tools (Knowage and Reportes Dinamicos), which are interactive BI applications;
  - years before 2017 and 2026, which the ceiling did not allow.
- **License: internal.** AMM's pages state no terms of reuse (read 653), so no verdict is recorded. `www.amm.org.gt` has no robots file (HTTP 404, read 652).

## The cross-check (`runs/c114/s2408/cross.py`, `cross.out`; tables read past their header lines)

- **AMM's demand against `owid_ember_electricity_annual`'s Guatemala demand.** AMM's is lower every year, by 4.2 per cent in 2019 and by 22.9 per cent in 2021 (11.952 against 15.500 TWh). Ember's series moves unevenly (15.50 TWh in 2021, 13.86 TWh in 2022), and AMM's rises from 10.50 to 13.93 TWh between 2017 and 2024, falling only in 2020 (11.155 to 11.028 TWh; this line first said "steadily", corrected in session 2410). AMM's demand is generation plus imports less exports, its losses included.
- AMM's figure is the interconnected system's (the wholesale market's) demand. This report does not say what Ember's adds to it, and the gap is not explained here.
- **Guatemala turns from net exporter to net importer:** generation is above the system's demand to 2020, about equal to it in 2021 (11.943 against 11.952 TWh), and below it from 2022 (2024: 13.117 against 13.932 TWh).

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.amm.org.gt | 14 of 15 | robots (404), the home page, the operation results page, the monthly reports frame, the reports script, nine workbooks (2017 to 2025): 2025's at 10:26:26Z, 20 seconds before 2017's, the other eight 0 to 2 seconds apart (no robots file, so no crawl delay is asked; corrected in session 2410); the connector waits 2 s between them |

## Errors

- **The first parse stopped at 2018's petroleum coke,** whose first months are blank. A blank fuel month now has no row; a blank month in a system row still stops the run.

## Decisions made without you

- **The table written without a separate trial run,** since the reader had parsed all nine workbooks read-only first. The write itself validated.
- **2017 to 2025,** the most years the ceiling allowed after the five pages needed to find the files.
- **The table internal** while AMM's terms are unstated.

## For Samuel's ruling

- **AMM's figures:** public or internal? AMM states no terms.

## Files

- New:
  - `warehouse/connectors/amm_guatemala.py`
  - `tests/test_session2408.py`
  - this report
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`
  - `warehouse/metadata/license_reads.csv` (652 to 665), `license_tables.csv`, `docs/licenses.md`
  - the coverage, sources and archive manifest files
- On the data machine only: `runs/c114/s2408/`, `runs/license_reads/s2408/`.
