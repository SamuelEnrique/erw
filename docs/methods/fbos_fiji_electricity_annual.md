# Fiji's electricity production and sales, a year (FBoS table 3.7[A] and Electricity 2024, Appendix III)

Energy Research Warehouse (ERW), method note written in session 2499 (chain 121) for a table first written on 24 October 2026 (session 2492).

Tables: `fbos_fiji_electricity_annual`

## Publisher and address

The Fiji Bureau of Statistics (FBoS), from Energy Fiji Limited's (EFL) figures:

- Key Statistics table 3.7[A], "Production and Sales of Electricity by Energy Fiji Ltd" (September 2025): `https://www.statsfiji.gov.fj/download/138/table-3/827/3-7a_electricity.pdf`;
- the economic survey "Electricity 2024" (February 2026, 31 pages), Appendix III "Sales of Electricity by Type of Consumers": `https://www.statsfiji.gov.fj/download/271/electricity/5954/2024-electricity.pdf`.

Two GETs, no key. Source id `fbos:electricity`. Connector: `warehouse/connectors/fbos_fiji_electricity.py` (session 2492). www.statsfiji.gov.fj's robots file disallows nothing (read 826). Chain 119 (session 2465) found efl.com.fj's own pages a day's demand figure a post and its year pages frames without figures; the Bureau is the way to EFL's yearly figures.

## Vintage and revision

2011 to 2024, written by run `20261024T162915Z` (the write under the lock, offline), which read the files saved at 2026-10-24T15:00:20Z (table 3.7[A]) and 15:00:42Z (the report). Neither answer gives a last-modified time.

## Shape and variables

Series, 83 rows, 5 entities. `unit` MWh; `ts_utc` the year's 1 January; `freq` P1Y; `geo` FJ; `node` and `x_label` FBoS's column label.

- `fbos:fj:efl`, `generation` (units produced) and `sales` (units sold), from table 3.7[A] in kWh, divided by 1,000.
- `fbos:fj:<consumer>` (industrial, commercial, domestic, others), `sales`, from Appendix III, times 1,000. The appendix heads its figures "kwh (000's)", but its totals are table 3.7[A]'s units sold in millions of kWh (2011: 740.9 against 740,873,951 kWh). Each year's total is checked against 3.7[A] within 0.1 GWh and the run stops on a difference, so the figures are read as GWh. "Commercial" includes businesses with heavy machinery; "others" are street lights and institutions.

| GWh | 2011 | 2019 | 2020 | 2024 |
|---|---|---|---|---|
| Produced | 837.2 | 1,061.2 | 976.4 | 1,218.9 |
| Sold | 740.9 | 945.4 | 862.5 | 1,088.4 |
| Sold to domestic consumers | 218.5 | 269.8 | 275.0 | 332.2 |

## Reading the source

- The run stops at once, asking nothing, while `fbos_fiji_electricity` or www.statsfiji.gov.fj is paused.
- Two requests a run (timeout 120 seconds); `--offline` reads the saved files.
- Both files are read as text. A table's rows are the consecutive lines that begin with a year and hold its number of cells (3 in 3.7[A], 5 in the appendix), the years consecutive.
- **Cells without a row:** "n/a" (one: 2011's others), counted in the header.
- The run stops, and no file is written, for: a table not found, a figure of another form, years not consecutive, a year in the appendix not in 3.7[A], an appendix total that differs from 3.7[A]'s units sold, a key given twice.

Nothing is filled. Not taken: the sales' value (Fiji dollars), the appendix's totals (checked), the report's other tables (the industry's gross output and employment), and Appendix V's production index, which includes the Fiji Sugar Corporation's own generation.

## License

Public, with a citation. The report's page ii, "Reproduction of material" (read 831): "Any table or material published in this Report may be reproduced and published without the Fiji Bureau of Statistics' prior approval. However, the source of information should always be identified and acknowledged in all modes of presentation." Verdict (session 2495): may be public, sold or not. The header carries the citation: Fiji Bureau of Statistics, Key Statistics table 3.7[A] and Economic Surveys: Electricity 2024, Appendix III (source: Energy Fiji Ltd). Held from the live set; in the next Stanford draft.

## Cross-checks (session 2492)

- Units produced over `owid_ember_electricity_annual`'s demand for Fiji: 0.87 to 1.06 (2011 to 2024; 1.011 in 2022, 1.06 in 2024). EFL's grids are most of Fiji's supply; the sugar mills' own generation is not in EFL's figures.
- 2014's units sold (794.1 GWh) are within 0.1 percent of its units produced (794.9 GWh), against 7 to 12 percent of units produced not sold in the other years; as printed.

## What it does not hold

- Generation by source (hydro, diesel, biomass, solar): neither file gives it; monthly figures; prices (FJD).
