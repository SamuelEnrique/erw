# The UK's natural gas supply and consumption, a quarter (DESNZ Energy Trends table 4.1)

Energy Research Warehouse (ERW), method note written in session 2233 (chain 099) for a table first written on 24 October 2026 (session 2226).

Tables: `desnz_uk_gas_quarterly`

## Publisher and address

UK Department for Energy Security and Net Zero (DESNZ), Energy Trends section 4 (gas), table ET 4.1 "Natural gas supply and consumption", sheet "Quarter (GWh)". The page `https://www.gov.uk/government/statistics/gas-section-4-energy-trends` links the workbook on assets.publishing.service.gov.uk; the file read is `https://assets.publishing.service.gov.uk/media/6aba6b15fceb6fb3a65012ba/ET_4.1_SEP_26.xlsx`. Source id `desnz:energy_trends_4_1`. Connector: `warehouse/connectors/desnz_gas.py` (session 2226). www.gov.uk's robots file disallows print and search pages only; assets.publishing.service.gov.uk has no robots file (HTTP 404, sessions 2168 and 2226).

## Vintage and revision

The first quarter of 1998 to the second of 2026, from the September 2026 issue, written by run `20261024T022020Z` (24 October 2026), which read the saved page and workbook (its log). The workbook was retrieved at 2026-10-24T02:17:00Z; `vintage` is its Last-Modified, 2026-09-28T13:26:45Z, in every row. The second quarter of 2026 is the one DESNZ marks "[provisional]" (`x_provisional` yes, 21 rows); the other 2,373 rows are `no`. The header's "Retrieved: 20261024T022020Z" is the write's run id; it also states the workbook's retrieval time.

The page is asked for again on every run that is not `--offline`; the workbook it links is reused from `warehouse/raw/desnz_gas/` when that address was saved (a new issue has a new address, ET_4.1_<MON>_<YY>.xlsx). The table is written by `write_csv`, which merges: a row of the new issue replaces the row of the same entity, variable and quarter, and a row the new issue no longer gives is kept from the earlier run. The first write added 2,394 rows and kept none.

## Shape and variables

Series, 2,394 rows: 21 lines, 114 quarters each. `entity` desnz_et41:uk; `variable` the line in snake case, its notes dropped; `node` the line as DESNZ writes it, notes included (for example "Stock change [note 4] [note 5]"); `unit` MWh (DESNZ's GWh times 1,000); `ts_utc` the quarter's first day; `freq` P3M; `geo` GB; `market` blank; extra column `x_provisional`. Totals are DESNZ's lines, never sums made here.

Lines: indigenous_production, imports, imports_of_liquefied_natural_gas, exports, stock_change, transfers, total_supply, statistical_difference, total_demand, transformation, electricity_generation, heat_generation, energy_industry_use, losses, final_consumption, iron_steel, other_industries, transport, domestic, other_final_users, non_energy_use.

TWh a year (the four quarters summed here for this note, not in the table):

| Year | Indigenous production | Imports | of which LNG | Exports | Total supply | Total demand | Electricity generation | Domestic |
|---|---|---|---|---|---|---|---|---|
| 1998 | 1,048.4 | 10.6 | 0.0 | 31.6 | 1,024.7 | 1,021.7 | 267.7 | 355.9 |
| 2010 | 642.5 | 606.3 | 206.8 | 168.2 | 1,095.6 | 1,089.6 | 376.5 | 383.1 |
| 2022 | 423.2 | 618.3 | 277.8 | 260.2 | 781.8 | 795.0 | 257.9 | 273.6 |
| 2024 | 343.7 | 453.3 | 111.2 | 118.4 | 686.3 | 687.3 | 179.6 | 252.3 |
| 2025 | 332.1 | 463.7 | 137.4 | 133.1 | 676.6 | 680.4 | 192.2 | 250.4 |

The second quarter of 2026 (provisional): total demand 121.38 TWh, indigenous production 77.68, imports 73.68 (LNG 12.30), exports 40.22. Exports are positive in every quarter and subtracted in the balance. Negative values: transfers (66 quarters), stock change (61; DESNZ's note: a positive stock change is a draw) and the statistical difference (56). Zeros: LNG imports (30 quarters), non-energy use (15), heat generation (4).

DESNZ's eight notes are carried in the header: the percentage change; from 2000 imports and exports on a physical flow basis only (a break); from 2016 LNG imports include cargoes (a break); a positive stock change is a draw; from 2016 stock data from National Grid (a break); transfers of biomethane may be estimated; heat generation in the latest year estimated from the previous year's; from 2013 losses revised (a break).

## Reading the source

- The run stops at once, asking nothing, while `desnz_gas` or either host (www.gov.uk, assets.publishing.service.gov.uk) is paused.
- Two requests a run: the page (fresh unless `--offline`; timeout 60 seconds) and the one workbook it links (timeout 120 seconds), each followed by 1 second's pause. HTTP 404 stops the run; any other failure is tried up to `RETRIES` (4) times, 5, 10 and 15 seconds apart. `--offline` reads the saved files only.
- The page must link exactly one workbook matching `LINK` (`https://assets.publishing.service.gov.uk/media/<id>/ET_4.1_<MON>_<YY>.xlsx`); none or several stops the run.
- In the workbook: no sheet "Quarter (GWh)", other than one header row beginning "Column1", a column header not "<year> <n>th quarter" (with " [provisional]" allowed), a cell that is not a number, no line at all, or a line and quarter given twice stops the run; no file is written. A blank cell has no row; nothing is filled.
- The million cubic metre sheets and the annual sheets are not read. DESNZ's notes come from the sheet "Notes", rows "Note <n>".
- The code counts no row ceiling.

## License

Public. `license_verdicts.csv` records DESNZ, read 315: "may be public", for public and for commercial use. The sentence: "All content is available under the Open Government Licence v3.0 , except where otherwise stated" (GOV.UK; the Energy Trends tables state no other terms). The header carries the attribution: "Contains public sector information licensed under the Open Government Licence v3.0." `sources.csv` flags `desnz:energy_trends_4_1` public; `license_tables.csv` lists the table under DESNZ.

## Cross-checks (session 2233)

- The written table and session 2226's trial copy hold the same 2,394 keys with every column equal, so the session's results (`runs/c099/s2226/cross.out`) hold for the written rows:
  - total supply less total demand less the statistical difference: at most 10.0 MWh in any quarter;
  - against `desnz_uk_electricity_quarterly` (ET 5.1b, all generating companies, gas), electricity generated over the gas used for electricity generation in the 114 shared quarters: a median 0.468, 0.429 to 0.496; by year 0.440 (1998) to 0.491 (2026's two quarters), 0.478 in 2017 and 0.481 to 0.488 in the other years from 2016. Session 2226's report (line 12) says "0.48 and above from 2016"; 2017's 0.478 is below it;
  - LNG's share of imports, 2016 to 2025: 13.7 percent (2017) to 44.9 (2022).
- Computed from the rows here: total supply equals indigenous production plus imports less exports plus stock change plus transfers within 10 MWh in every quarter; total demand equals transformation, energy industry use, losses and final consumption within 10 MWh; final consumption equals its six sectors within 20 MWh; transformation equals electricity and heat generation within 1,000 MWh (DESNZ's rounding of a GWh).
- Not made: the chain file's check of LNG against EIA's U.S. exports to the UK, since `eia_lng_exports_monthly` is by U.S. terminal, not by destination.

## What it does not hold

- The monthly tables ET 4.2 (supply and consumption, Official Statistics in Development), 4.3 and 4.4 (imports and exports by route); the routes of imports are only the quarterly imports and their LNG part.
- The million cubic metre sheets and the annual sheets of ET 4.1.
- Quarters before 1998.
