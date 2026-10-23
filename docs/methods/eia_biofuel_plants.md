# Fuel ethanol, biodiesel and renewable diesel plants and their production capacity, as of 1 January 2025 and 2026 (EIA's biofuels capacity reports)

Energy Research Warehouse (ERW), method note written in session 2038 (chain 058) for a table first written on 23 October 2026 (session 2031).

Tables: `eia_biofuel_plants`

## Publisher and address

U.S. Energy Information Administration (EIA), the plant production capacity reports from Form EIA-819, four workbooks:

| Workbook | As of | Address |
|---|---|---|
| U.S. Biofuels Plant Production Capacity (`COMBINED`) | 1 January 2026 | `https://www.eia.gov/biofuels/capacity/biofuelscapacity.xlsx` |
| Fuel ethanol | 1 January 2025 | `https://www.eia.gov/petroleum/ethanolcapacity/ethanolcapacity.xlsx` |
| Biodiesel | 1 January 2025 | `https://www.eia.gov/biofuels/biodiesel/capacity/biodieselcapacity.xlsx` |
| Renewable diesel fuel and other biofuels | 1 January 2025 | `https://www.eia.gov/biofuels/renewable/capacity/renewablescapacity.xlsx` |

The combined workbook has one sheet with the columns Entity, Facility, State, PADD, Capacity (MMgal/yr), Capacity (Mb/d) and Facility type. Each 2025 workbook has the columns State, Respondent, City, MMgal/yr and Mb/d, a state written once above its plants and a PADD row above its states. Four requests a run, a pause of 1 second after each, timeout 120 seconds, with the ERW's user agent (`UA`). Source id `eia:biofuels_capacity`. Connector: `warehouse/connectors/eia_biofuels_capacity.py` (session 2031).

## Vintage and revision

The file on the data machine was written by run `20261023T185742Z` (23 October 2026), as its header says. `retrieved_at` 2026-10-23T18:54:11Z to 18:54:53Z. `vintage`, each workbook's Last-Modified: combined 2026-09-09T21:16:23Z; ethanol 2025-09-19T20:23:45Z; biodiesel 2025-09-19T19:11:44Z; renewable diesel 2025-09-22T16:47:13Z.

The years the workbooks are as of are the connector's arguments, `--combined-year` (default 2026) and `--single-year` (default 2025), read by session 2031 from each page's title; the sheets do not all print them. The workbooks keep their addresses from one issue to the next. Until session 2038 they were asked for without `fresh`, so a later run would have reused the saved files; since session 2038 a run that is not `--offline` asks for them again (`fresh=not args.offline`), and a new issue's year must then be given in the arguments. Each run replaces the table whole (`ip.write_snapshot`). No age check is made.

Earlier issues sit under `www.eia.gov/archive/`, which EIA's robots file disallows, so only these two years are taken.

## Shape and variables

Entities, 511 rows, one a plant and year, no `entity_id` twice: 258 as of 1 January 2025 and 253 as of 1 January 2026.

| `x_fuel` | 2025 | 2026 |
|---|---|---|
| `ethanol` | 191 | 189 |
| `biodiesel` | 48 | 45 |
| `renewable_diesel_and_other` | 19 | 19 |

- `entity_id` `eia_biofuel:<year>:<fuel>:<state>:<n>`, n the plant's place among its year, fuel and state in the workbook's order. EIA publishes no plant number, so the id does not follow a plant from one year to the next.
- `entity_type` plant; `status` active on every row; `status_date` the 1 January the capacity is as of.
- `name`: for 2026 the combined workbook's Facility column, for 2025 the city (the 2025 sheets name no facility). The 2026 names and operators are in capital letters ("MARQUIS ENERGY LLC", "HENNEPIN"); the 2025 ones are not.
- `operator` the Entity (2026) or Respondent (2025) as EIA writes it; `geo` US-<state>: 38 states in 2025, 37 in 2026. `lat`, `lon` and `capacity_mw` empty.
- `x_year`, `x_fuel`; `x_facility_type` the combined workbook's Facility type for 2026, and for 2025 the connector's name of the workbook's fuel ("Ethanol", "Biodiesel", "Renewable Diesel Fuel and Other Biofuels"); `x_padd` as published; `x_city` the 2025 city (empty for 2026).
- `x_capacity_mmgal_per_year` and `x_capacity_kbbl_per_day` as published: what a plant can make in a year (million gallons) or a day (thousand barrels). "(s)", less than 0.5, is kept: 1 cell of MMgal/yr and 16 of Mb/d.
- `x_coprocessing` yes on 4 rows of 2025, the refineries EIA's footnote 1 marks as co-processing renewable feedstock and petroleum (the mark taken off the respondent's name): Kern Oil & Refining (Bakersfield, California), Shell Oil Products U.S. (Norco, Louisiana), BP Products North America (Blaine, Washington), US Oil & Refining Co. (Tacoma, Washington).

The capacities stay in `x_` columns: an entity's `capacity_mw` is power, and a plant's gallons a year are not.

Plants by PADD:

| `x_fuel` | Year | PADD 1 | PADD 2 | PADD 3 | PADD 4 | PADD 5 |
|---|---|---|---|---|---|---|
| ethanol | 2025 | 2 | 177 | 4 | 4 | 4 |
| ethanol | 2026 | 2 | 175 | 4 | 4 | 4 |
| biodiesel | 2025 | 9 | 28 | 6 | 0 | 5 |
| biodiesel | 2026 | 7 | 27 | 6 | 0 | 5 |
| renewable diesel and other | 2025 | 0 | 3 | 6 | 3 | 7 |
| renewable diesel and other | 2026 | 0 | 3 | 6 | 3 | 7 |

## Reading the source

- The combined workbook without its seven columns stops the run; a facility type other than Ethanol, Biodiesel or Renewable Diesel Fuel and Other Biofuels stops it; a state that is not a two-letter code stops it. Rows empty in every column are passed over.
- A 2025 workbook without the header row State, Respondent, City, MMgal/yr, Mb/d among its first 10 rows stops the run. A first cell that begins "PADD" sets the PADD; "U.S. Total" ends the sheet; a first cell that is neither a state name the connector knows (`STATES`) nor a PADD stops the run; a plant before any state stops it; a sheet with no plant stops it.
- A capacity neither a number (commas allowed) nor "(s)" stops the run.
- An `entity_id` given twice stops the run. Nothing is filled.
- Each request is tried up to 4 times (`iso_prices.with_retries`), waiting 5 seconds times the attempt number after each failure; HTTP 404 is a `SourceGap`, not retried; any answer but HTTP 200 is a failure.
- Ceiling: four requests (the four workbooks). No row ceiling is set in the code.
- Any failure is recorded as a failure, and no file is written.
- The connector does not call `iso_prices.paused()`; EIA is not in `warehouse/metadata/paused_sources.csv`.

## License

Public. `sources.csv` has `public` for `eia:biofuels_capacity`; the header: "License: public (EIA: "U.S. government publications are in the public domain"; cite "U.S. Energy Information Administration")." `license_verdicts.csv`, EIA, read 1 (EIA's copyrights and reuse page, `https://www.eia.gov/about/copyrights_reuse.php`, read 12 October 2026): "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service." Verdict: may be public, and may be public for commercial use.

Robots: read 202 (session 2031), `www.eia.gov`'s file, which disallows `/archive/` and site machinery; the capacity pages and workbooks are allowed.

## Cross-checks (session 2038)

- The counts above were computed from the rows, read past the header lines; the counts by year and fuel equal the header's.
- Capacity summed: 2026 ethanol 18,439 MMgal/yr (1,205 Mb/d as published), biodiesel 1,970 (127), renewable diesel and other 4,970 (325); 2025 ethanol 18,477.7 (1,206.7), biodiesel 1,988 (128), renewable diesel and other 4,720 (308). The largest plant of each fuel is the same in both years: Marquis Energy, Hennepin, Illinois, ethanol 400; RBF Port Neches, Houston, Texas, biodiesel 144; Diamond Green Diesel, Norco, Louisiana, renewable diesel 982.
- Session 2031 compared the plants with the tables EIA's pages print: for 2025, every state of the ethanol and biodiesel pages in plants and MMgal/yr; for 2026, every PADD's plant counts, and Mb/d computed once from the plants' MMgal/yr within 1 of the page (PADD 2 ethanol 1,137 against 1,136; the U.S. 1,203 against 1,202 for ethanol and 129 against 128 for biodiesel). Recomputed here at 42 gallons a barrel and 365 days: 1,136.7, 1,202.8 and 128.5, the session's figures to rounding. EIA's pages were not read again.

## What it does not hold

- Issues before 1 January 2025 (under the disallowed `/archive/`).
- A plant matched across years: the ids are places in a workbook.
- Production: EIA's ethanol plant production is `eia_oxygenate_production_monthly`; the fuel that generated RINs is `epa_rfs_rins_monthly` and `epa_rfs_fuel_annual`.
- Coordinates: EIA's workbooks give none.
