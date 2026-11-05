# Liechtenstein's electricity a year since 1985: production, imports, exports and consumption (the Amt fuer Statistik's Energie 2025, Tabelle 5)

Energy Research Warehouse (ERW), method note written in session 2625 (chain 130) for a table first written on 25 October 2026 (session 2622).

Tables: `asli_liechtenstein_electricity_annual`

## Publisher and address

The Amt fuer Statistik Liechtenstein, Energie 2025 (published 1 July 2026, report year 2025), its tables workbook, sheet "Tabelle 5", "Stromproduktion und -verbrauch seit 1985": `https://www.statistikportal.li/statistikportal/publications/551-energie/2025/01/1/551.2025.01.1_02_energie-2025-tabellen.xlsx`, linked from the portal's Energie page. One GET, no key. Source id `asli_li:energie_2025_tabelle5`. Connector: `warehouse/connectors/asli_liechtenstein_electricity.py` (session 2622), whose raw store is `warehouse/raw/asli_li/`. www.statistikportal.li's robots file names `*` with no rule (read 1255).

## Vintage and revision

Written by run `20261025T065201Z` (the write under the lock, offline), which read the workbook saved at 2026-10-25T06:49:03Z. `vintage` is empty: the server sends no last-modified time. Each year's edition has its own address and gives the whole series again.

## Shape and variables

Series, 164 rows, 4 entities, each year from 1985 to 2025. `entity` `asli:li:<item>`:
- `production` (`variable` `generation`), "Produktion im Inland";
- `imports` (`imports`), "Import";
- `exports` (`exports`), "Export";
- `consumption` (`consumption`), "Verbrauch im Inland".

`unit` MWh; `ts_utc` the year's first day; `freq` P1Y; `geo` LI; `node` the table's column. `x_pv_method` is old (to 2021) or new (from 2022), and `x_old_method_value` holds, on 2022's rows only, the figure by the old method.

In 1985: production 48,878 MWh, imports 124,453, exports 349, consumption 172,982. In 2025: production 136,358.7, imports 271,226, exports 0, consumption 407,584.7.

**2022 is printed twice.** The Office changed how it counts photovoltaic production in 2023 and gives 2022 by both methods ("nach der alten und neuen Methode"), on two unlabelled rows. The first is read as the old method and the second as the new, the note's order. The new is written, as 2023 on are counted by it, and the old kept beside it: production 100,496.2 against 103,291.9 MWh, consumption 409,321.2 against 412,116.9.

## Reading the source

- The run stops at once, asking nothing, while `asli_li` or www.statistikportal.li is paused.
- One request a run; `--offline` reads the saved workbook.
- **The sheet** "Tabelle 5" is read by its title cell and its two header rows (the four columns, then "Jahr" and four "MWh"). Every later row with a year in the first column is a year, up to the first row without one.
- **The years** must run from 1985 without a gap; only 2022 may be given twice.
- **The key:** a cell "-" is the workbook's zero; "." (not available) is not written; any other text stops the run.
- **Check:** each year's production plus imports less exports equals consumption within 1 MWh, both 2022 rows included.

Nothing is filled. Not taken: Tables 6 to 19 (production by source, heat, photovoltaics, combined heat and power, district heat, self-sufficiency), the overview tables and the eTab tables on etab.llv.li.

## License

Public. The workbook's Metadaten sheet (read 1258) states "Nutzungsbedingungen: CC BY 4.0". Verdict: may be public, cited as the Office's. In the release package; held from the live set.

## Cross-check

EIA's world table holds no Liechtenstein. Within the workbook, Table 5's note gives domestic production as the sum of photovoltaics, combined heat and power and hydro (Tables 6, 8 and 9). The run's check is the table's own balance.
