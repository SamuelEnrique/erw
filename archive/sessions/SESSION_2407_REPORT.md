# Session 2407 report: Panama's electricity, 1970 to 2021 (the Secretaria Nacional de Energia's historical workbook, in place of CND)

24 October 2026, from 10:08 UTC, on lab-desktop (the data machine), the second session of `queue/done/114-day-15-november-data-paraguay-panama-guatemala-namibia.md`, unattended. Precheck passed (`runs/c114/pre2407.out`). Model spend USD 0. Pulls: 11 of 15 (below).

## Read these first

- **CND not taken.** The Centro Nacional de Despacho's statistics and reports pages (reads 710 and 713 on this branch's numbering) list nothing in their HTML. A script (read 712) loads the lists and the downloads from `sitioprivado.cnd.com.pa`, its private site, with an access key written in the script. Neither the key nor that host was used, as for the Dominican coordinator's and PUCSL's script-only figures (chain 112). Both CND hosts' robots files are comment lines only (reads 708 and 711).
- **In its place, two tables, internal when written (made public in session 2419: test 378's rule allows no table flagged internal where the verdict read allows it)** from the Secretaria Nacional de Energia's "Generacion Historica Electrica (Serie 1970-2021)" workbook (read 717), listed on its Datos y Estadisticas page. Each is written, validated, archived, in coverage (sector power), and held from the live set:
  - `sne_panama_electricity_annual`, 569 rows:
    - Cuadro GE-8, 1980 to 2021: gross generation for the system total, the interconnected system, the Panama Canal Authority's plants and eleven plant types (hydro, steam on bunker, internal combustion, two gas turbine kinds, other light diesel, wind, solar, natural gas, biogas, isolated systems);
    - Cuadro GE-14, 1970 to 2021: net production, maximum demand (MW) and load factor (pct).
  - `sne_panama_generation_monthly`, 504 rows: Cuadro GE-10, total gross generation a month, January 1980 to December 2021.
  - In MWh (the sheets' GWh times 1,000).
  - The eleven types add to the total in every year, as do the interconnected system, the Canal Authority and the isolated systems, within 0.5 GWh. Each year's months add to the sheet's annual column within 0.5 GWh.
  - That annual column differs from GE-8's total by up to 2.272 GWh in a year. Both are kept as published.
- **The workbook ends at 2021.** The Secretaria's newer files on the page are its energy balances to 2025 (read 718: whole-economy balances, not taken) and an Infogram chart of gross generation to 2025 on a third-party host (not requested). No monthly figure from 2020 on beyond 2021 was found within the ceiling.
- **License: internal when written, with a verdict of "may be public" (read 716), for your ruling; made public in session 2419: test 378's rule allows no table flagged internal where the verdict read allows it.**
  - The Datos y Estadisticas page says the Secretaria makes the information available and that its use must cite the source.
  - Every page's footer reads "© Copyright Secretaría de Energía | Todos los derechos reservados" (read 715).
  - The tables' headers carry the citation. www.energia.gob.pa's robots file disallows only `/wp-admin/` and names no AI agent (read 714).

## The cross-check (`runs/c114/s2407/cross.py`, `cross.out`; tables read past their header lines)

- **The ERW's Ember table holds Panama's demand only,** not its generation (`owid_ember_electricity_annual`: `electricity_demand` and `electricity_emissions`), so the check is net production against Ember's demand, which is not a like-for-like pair:
  - From 2000 to 2018, net production is 0.8 to 2.6 per cent below Ember's demand (2015: 9.939 against 10.180 TWh). (This line first said "2000 to 2015" and "2.4"; corrected in session 2410.)
  - From 2019 it is above: 8.8 per cent in 2019, 15.3 in 2020 and 13.4 in 2021 (13.234 against 11.670 TWh). Gross generation is 14.5 to 21.7 per cent above. The gap opens the year after the natural gas plant (Costa Norte) first appears in GE-8 (2018: 623.4 GWh). Net production already holds the net interchange (GE-13's footnotes: net generation plus purchases, negative from 2019), so exports do not explain the gap, which is not explained here (session 2410's note; this line first said the ERW held no trade figure to tell).
- **GE-14's net production is above GE-8's gross generation in 14 years** (1984, 1987 to 1995, 1997 to 2000; 2000: 4.968 against 4.887 TWh), each a year of positive purchases, which net production includes (session 2410; this line first named 2000 only). The two sheets are kept as published.
- **Load factor against net production over the peak and the year's hours:** the largest gap is 6.66 points (1973).

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.cnd.com.pa | 4 | robots, the home page, the statistics page, the annual reports page |
| sitiopublico.cnd.com.pa | 2 | robots, the statistics script |
| www.energia.gob.pa | 5 | robots, the statistics page (a redirect), the Datos y Estadisticas page, the generation workbook (2.3 MB), the balances workbook (1.4 MB) |
| total | 11 of 15 | |

## Errors

- **The first write stopped at the coverage build** (no sector rule yet). The rules and holds were added, and the second write passed.
- **The cross-check's first run failed** on an index (a fault in the script, not the tables), and was fixed.
- **One test failed** on its own fake sheet's row count, and was fixed.

## Decisions made without you

- **The Secretaria's workbook in place of CND,** since CND's figures load only through its private site's key.
- **Two tables, a year and a month,** since `freq` is not a partition column (Decision 44).
- **The tables internal** until you rule on the Secretaria's terms (made public in session 2419: test 378's rule allows no table flagged internal where the verdict read allows it). The verdict "may be public" records its data page's grant.
- **The energy balances not taken,** since they are the whole economy in barrels of oil equivalent, which the session did not ask for.

## For Samuel's ruling

- **The Secretaria Nacional de Energia's figures: public or internal?** Its data page asks only for a citation; its footer reserves all rights.

## Files

- New:
  - `warehouse/connectors/sne_panama.py`
  - `tests/test_session2407.py`
  - this report
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`
  - `warehouse/metadata/license_reads.csv` (708 to 718), `license_verdicts.csv` (the Secretaria), `license_tables.csv`, `docs/licenses.md`
  - the coverage, sources and archive manifest files
- On the data machine only: `runs/c114/s2407/`, `runs/c114/write_tables.sh`, `runs/license_reads/s2407/`.
