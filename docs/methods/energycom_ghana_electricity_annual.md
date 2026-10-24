# Ghana's electricity generation by source, imports and exports, and peak load, a year, 2000 to 2025 (Energy Commission, National Energy Statistical Bulletin 2026)

Energy Research Warehouse (ERW), method note written in session 2375 (chain 112) for a table first written on 24 October 2026 (session 2373 of chain 112, its report `archive/sessions/SESSION_2373_REPORT.md`).

Tables: `energycom_ghana_electricity_annual`

## Publisher and address

Energy Commission, Ghana, its 2026 National Energy Statistical Bulletin ("Energy Statistics and Balances", May 2026), one of the PDF files on its Energy Statistics page (`https://www.energycom.gov.gh/index.php/planning/energy-statistics`, read 609), one request:

- `https://www.energycom.gov.gh/index.php/planning/energy-statistics?download=855:2026-energy-statistics`

Source id `energycom:national_energy_statistics`. The page offers 12 downloads: the bulletins 2017 to 2026 (one a year) and "key energy statistics" for 2018 and 2021; only 2026 is read. The bulletin is 67 PDF pages (created 31 May 2026, 12:47:08Z, in Microsoft Word); its foreword says it covers "Ghana's energy supply and utilisation from 2000 to 2025". Three tables of section 3, "Electricity", are taken, each a row a year from 2000 to 2025:

- Table 3.7, "Annual Electricity Generation" (PDF page 23, printed 12): generation in GWh by Hydro, Thermal and Other Renewables, the Total, and the three shares (not taken). Source line "GRIDCo and ECG".
- Table 3.8, "Electricity Import and Export (GWh)" (PDF page 25, printed 14): Import, Export, Net Export. Source line "GRIDCo".
- Table 3.9, "Ghana and System Peak Load (MW)" (PDF page 27, printed 16): Ghana Peak Load, System Peak Load. Source line "VRA & GRIDCo".

The numbers are the body's captions. The list of tables (PDF page 6) and the section's own text call the same three tables 3.4, 3.5 and 3.6, and give 3.7 to 3.9 to transmission, distribution and consumption; the body's own Table 3.4 is "Grid Installed and Dependable Capacity (MW)" (point 2).

The footnotes that bear on the variables: 8, on the text of section 3.2 (printed page 11), attached to "Total electricity generation": "Electricity generation includes embedded generation and import"; 9, on Import: "Imports include both planned and unplanned imports"; 10, on Ghana Peak Load: "Ghana Peak denotes the maximum electricity demand within Ghana, encompassing loads served by the Electricity Company of Ghana (ECG), Northern Electricity Distribution Company (NEDCo), direct customers of the Volta River Authority (VRA), as well as the mining sector and Volta Aluminium Company (VALCO)"; 11, on System Peak Load: "System Peak denotes the total system demand, defined as the sum of Ghana Peak and export load". Section 3.4's text describes the system peak as "comprising Ghana Load at Peak, and export load" (point 3).

Session 2373's probe (`runs/c112/s2373/probe.csv`) made 5 requests, 14 to 18 seconds apart (08:53:32Z to 08:54:35Z), against the robots file's crawl delay of 3: the robots file (read 606), the home page, a flyer that refreshes to `index.php` (read 607), the index page (read 608), the Energy Statistics page (read 609) and the bulletin (HTTP 200, 2,205,076 bytes, at 2026-10-24T08:54:35Z, no Last-Modified). All five are saved in `runs/license_reads/s2373/`, and the bulletin's text, as pdftotext gave it, in `runs/c112/s2373/es2026.txt`. The bulletin was seeded into `warehouse/raw/energycom_ghana/20261024T085332Z_probe/` (the same SHA-256, 3999b628...), and the trial and the write read it offline ("raw file reused", run log).

Connector: `warehouse/connectors/energycom_ghana.py` (session 2373): `[--offline] [--out-dir DIR]`, one request, the tables read with pdfplumber's table extraction on the page whose text holds "Table 3.N: <title>" and a table with at least ten rows of years (the list of tables names the titles too, and is skipped for having none). pdfplumber gives the rows with cells shifted on alternate lines, so each row's non-empty cells are read in order: the year, then the values, the shares left out. Hydro, thermal and other renewables must add to the total, and exports less imports to net exports, within 1.5 GWh; a year twice, a value that is not a number or a dash, or a failed check stops the run. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. The table is internal; it is held from the live set (listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`) and is not in the Redivis release package, which takes public tables only (`warehouse/redivis/release_v1.py`: "an internal table is never in the public dataset").

## Vintage and revision

One write, run `20261024T085642Z` ("This run wrote 221 rows: 221 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs"), from the saved bulletin. `retrieved_at` is the bulletin's download time, 2026-10-24T08:54:35Z, in every row; `vintage` is blank in every row, the server having sent no Last-Modified (the bulletin itself is dated May 2026). Every row's `source_url` is the bulletin.

The three tables mark no figure as provisional or revised (the bulletin marks its 2024 energy balance "* Revised" and some other tables "* Subject to revision" or "*Provisional", not these). All 26 years come from the 2026 edition: whatever the Commission revised since earlier editions is in it, and a figure revised in a later edition replaces this one only when a later run reads that edition. A later run merges by (entity, variable, ts_utc).

## Shape and variables

Series, 221 rows, one entity `energycom:GH`, `node` Ghana, `geo` GH, `freq` P1Y, `market` blank; `unit` MWh for generation and trade (the bulletin's GWh times 1,000) and MW for the peaks. 9 variables, 26 rows each (2000 to 2025) except `generation_other_renewables`, 13 (2013 to 2025):

| Variable | The bulletin's column |
|---|---|
| generation_hydro | Table 3.7, Hydro |
| generation_thermal | Table 3.7, Thermal |
| generation_other_renewables | Table 3.7, Other Renewables |
| generation_total | Table 3.7, Total |
| imports | Table 3.8, Import |
| exports | Table 3.8, Export |
| net_exports | Table 3.8, Net Export |
| peak_ghana | Table 3.9, Ghana Peak Load |
| peak_system | Table 3.9, System Peak Load |

| Year | Hydro | Thermal | Other renewables | Total | Imports | Exports | Net exports | Ghana peak | System peak |
|---|---|---|---|---|---|---|---|---|---|
| 2000 | 6,610 | 614 | | 7,224 | 864 | 392 | -472 | 1,115 | 1,161 |
| 2001 | 6,609 | 1,250 | | 7,859 | 462 | 302 | -160 | 1,213 | 1,190 |
| 2002 | 5,036 | 2,237 | | 7,273 | 1,146 | 612 | -534 | 1,191 | 1,227 |
| 2003 | 3,885 | 1,996 | | 5,881 | 940 | 535 | -405 | 1,012 | 1,135 |
| 2004 | 5,280 | 758 | | 6,038 | 878 | 667 | -211 | 992 | 1,137 |
| 2005 | 5,629 | 1,159 | | 6,788 | 815 | 639 | -176 | 1,204 | 1,325 |
| 2006 | 5,619 | 2,811 | | 8,430 | 629 | 755 | 126 | 1,263 | 1,462 |
| 2007 | 3,727 | 3,251 | | 6,978 | 435 | 249 | -186 | 1,276 | 1,274 |
| 2008 | 6,196 | 2,129 | | 8,325 | 275 | 538 | 263 | 1,283 | 1,367 |
| 2009 | 6,877 | 2,081 | | 8,958 | 198 | 752 | 554 | 1,331 | 1,423 |
| 2010 | 6,995 | 3,171 | | 10,166 | 106 | 1,036 | 930 | 1,394 | 1,506 |
| 2011 | 7,561 | 3,638 | | 11,199 | 81 | 802 | 721 | 1,601 | 1,665 |
| 2012 | 8,071 | 3,953 | | 12,024 | 128 | 716 | 589 | 1,716 | 1,729 |
| 2013 | 8,233 | 4,635 | 3 | 12,870 | 27 | 654 | 627 | 1,864 | 1,943 |
| 2014 | 8,387 | 4,571 | 4 | 12,962 | 51 | 630 | 579 | 1,925 | 1,970 |
| 2015 | 5,844 | 5,643 | 3 | 11,490 | 223 | 581 | 358 | 1,836 | 1,933 |
| 2016 | 5,561 | 7,435 | 27 | 13,023 | 574 | 473 | -100 | 2,072 | 2,087 |
| 2017 | 5,616 | 8,425 | 28 | 14,069 | 247 | 377 | 130 | 2,152 | 2,158 |
| 2018 | 6,017 | 10,195 | 33 | 16,246 | 140 | 739 | 600 | 2,489 | 2,525 |
| 2019 | 7,252 | 10,894 | 52 | 18,197 | 127 | 1,430 | 1,303 | 2,700 | 2,804 |
| 2020 | 7,293 | 12,815 | 57 | 20,165 | 58 | 1,855 | 1,797 | 2,951 | 3,090 |
| 2021 | 7,521 | 14,417 | 122 | 22,060 | 44 | 1,734 | 1,690 | 2,992 | 3,246 |
| 2022 | 8,192 | 14,818 | 162 | 23,172 | 37 | 2,215 | 2,177 | 3,251 | 3,469 |
| 2023 | 9,187 | 14,930 | 148 | 24,264 | 79 | 2,528 | 2,449 | 3,273 | 3,618 |
| 2024 | 9,893 | 15,506 | 181 | 25,580 | 57 | 2,113 | 2,056 | 3,664 | 3,952 |
| 2025 | 8,752 | 18,996 | 197 | 27,945 | 11 | 2,451 | 2,441 | 3,908 | 4,283 |

GWh and MW as the bulletin prints them, from the table (`runs/c112/s2375/notes/gh.out`); the table holds the GWh times 1,000 in MWh. A blank cell is the bulletin's dash, which has no row.

- **Net exports are negative in eight years** (2000 to 2005, 2007 and 2016), Ghana a net importer; the smallest value is -534 GWh (2002). These are the table's only negative values; no value is zero.
- **Ghana's peak is above the system peak in 2001 and 2007** (1,213 against 1,190 MW, and 1,276 against 1,274), against footnote 11's definition; the rows are as published and header line 3 names the two years. Both are years of net imports (point 3).
- **Hydro's share** falls from 91.5 percent of the total in 2000 to 31.3 in 2025; other renewables are 0.705 percent in 2025 (the bulletin: "92%", "31%", "0.71%").

## Placing values in time, and what is filled

`ts_utc` is the year's 1 January at 00:00:00Z, a label for the calendar year, 2000-01-01 to 2025-01-01. Generation and trade are the year's totals; the peaks are the year's maxima. A dash (other renewables before 2013) has no row; nothing is filled. Every other cell of the three tables has a figure.

## License

Header: "License: internal. The bulletin states no terms of reuse; internal until a ruling. Cite: Energy Commission, Ghana, National Energy Statistical Bulletin 2026." `warehouse/metadata/license_verdicts.csv` holds no row for the Commission. `warehouse/metadata/license_reads.csv` records reads 606 to 609 (session 2373): the robots file ("allows every path; a crawl delay of 3 seconds; names no AI agent"; the file is `User-agent: *`, `Allow: /`, `Crawl-delay:3` and a sitemap line), the flyer home page, the index page ("its Terms & Condition link leads to the home page"; the saved page's link is `<a href="/" class="">Terms &amp; Condition`) and the Energy Statistics page ("states no terms of reuse"). The index page's footer reads "© 2026 Energy Commission"; the bulletin's text holds no copyright or reuse notice (its foreword: the bulletin "is intended to serve as a key reference for policymakers, planners, regulators, researchers, and other stakeholders"). `docs/licenses.md`, the table's row: verdict today "not settled (needs written permission by default)", not read "Energy Commission, Ghana", flag internal, "not settled", if the ERW sells anything "may be public", ERW verdict internal. The report leaves the ruling to Samuel ("public or internal? It states no terms").

## Checks (session 2375)

The figures in this note were computed from the rows of `warehouse/output/energycom_ghana_electricity_annual.csv`, read past its 10 header lines (counted), from session 2373's text of the bulletin, and from the saved PDF, read only (scripts `runs/c112/s2375/notes/gh.py` and `ghpdf.py`, outputs `gh.out` and `ghpdf.out` beside them).

- 221 rows, 9 variables, 2000 to 2025, as header lines 1, 3 and 10 state; one entity; no (entity, variable, ts_utc) twice; no blank value; every MWh value a whole multiple of 1,000.
- **Against the bulletin's text:** an independent parse of pdftotext's lines of the three tables (`es2026.txt`) gives 26 years of each, and all 26 years of all nine columns equal the table's (0 differences), the dashes of other renewables included.
- **The table's sums:** hydro, thermal and other renewables against the total within 1 GWh (+1 in 2013, 2019 and 2023, -1 in 2018); exports less imports against net exports within 1 GWh (-1 in 2012, 2016, 2018 and 2025, +1 in 2022). Header line 3's 1.5 GWh holds.
- **The trial against the table:** `runs/c112/s2373/trial/energycom_ghana_electricity_annual.csv` has the same 221 keys with 0 differences in value or `retrieved_at`.
- Session 2373's cross-check (`runs/c112/s2373/cross.py`, `cross.out`, run on the trial): generation less exports plus imports against `owid_ember_electricity_annual`'s Ghana demand, which ends in 2024: 16.89 against 16.00 TWh in 2019 (5.59 percent above), 18.37 against 17.99 (2.1), 20.37 against 20.39 (-0.1), 20.99 against 21.05 (-0.27), 21.82 against 21.85 (-0.16) and 23.52 against 21.83 (7.76, 2024).
- **Session 2375's own, on footnote 8:** the bulletin's Table 3.10, "Electricity Transmitted and Transmission Losses (GWh)" (source GRIDCo), against the table. Transmitted less generation is 843, 434, 1,129, 919, 853, 777 and 583 GWh in 2000 to 2006, while imports were 864, 462, 1,146, 940, 878, 815 and 629: transmitted less generation less imports is -21, -28, -17, -21, -25, -38 and -46 GWh, and -25 and -5 in 2009 and 2010. From 2018 generation exceeds the energy transmitted, by 286 GWh (2018) rising to 992 GWh (2025). And the 2025 energy balance (Table 6.24, PDF page 57, "1 GWh = 86 TOE" on the conversion page) books the electricity plants' output as 2,403 ktoe (the table's 27,945 GWh times 0.086 is 2,403.3) and imports as a separate 0.9 ktoe (11 GWh is 0.95); 2024's (Table 6.25) 2,199 and 4.9 ktoe (25,580 GWh is 2,199.9 ktoe, 57 GWh 4.9). Both read the generation total as excluding imports (point 1).

## The session report against the table

Every figure of `SESSION_2373_REPORT.md` checked against the table, the bulletin and `cross.out` holds (221 rows, 2000 to 2025, the three tables and their variables, GWh times 1,000, the checks within 1.5 GWh in every year, footnote 8's words, Ghana's peak above the system peak in 2001 at 1,213 against 1,190 MW and in 2007, reads 606 to 609, the Terms & Condition link, the robots file and its 3 seconds, the tables' source lines naming GRIDCo and ECG, Ember within 0.3 percent in 2021 to 2023, 20.99 against 21.05 TWh in 2022, 2.1 percent above in 2020, 5.6 in 2019 and 7.8 in 2024, 23.52 against 21.83 TWh, imports under 0.15 TWh a year from 2019, 7.22 TWh in 2000, the system peak from 1,161 to 4,283 MW, 5 requests of 15, 2.2 MB, the first trial stopped at the list of tables), except:

- "the body's table 3.9, listed as 3.6 in the contents": tables 3.7 and 3.8 are listed as 3.4 and 3.5 as well (point 2).
- "Adding imports to a generation figure that already includes them counts them twice": the bulletin's transmission table and energy balance read the generation total as excluding imports (point 1).
- "Generation rose ... to 27.94 TWh (2025)": the bulletin's 27,945 GWh is 27.945 TWh (point 4).

## Limits

- **Generation is not grid generation alone.** By footnote 8 it includes embedded generation (plants connected to the distribution networks; section 3.1 gives the installed capacity "excluding embedded generation"); from 2018 it exceeds the energy GRIDCo transmitted (286 to 992 GWh), which fits. Generation less exports plus imports is therefore the country's supply, comparable with Ember's demand as the cross-check uses it.
- **The system peak's make-up.** The bulletin defines the system peak in two ways (footnote 11 and section 3.4's text), so `peak_system` less `peak_ghana` is not a measure of export load (negative in 2001 and 2007).
- **One edition.** The table holds the 2026 edition's series only; no earlier edition was read, so how far the Commission revised its earlier figures, or changed its definitions, is not known from these files. Its table numbers differ between the list of tables and the body, and may differ in other editions.
- **Imports** include "planned and unplanned imports" (footnote 9); the bulletin does not split them.

## What it does not hold

- Installed and dependable capacity (body Tables 3.4 to 3.6), electricity transmitted and transmission losses, the distribution utilities' purchases, sales and losses, consumption by sector, customer numbers, dam elevations, reliability indices, the generation shares, the energy balances, and the oil, gas and biomass sections; generation by plant or month; the bulletins of 2017 to 2025 and the key energy statistics of 2018 and 2021; years before 2000.

## Points for the session to act on

1. **The bulletin's own tables read footnote 8's "and import" as not true of Table 3.7's total.** Header line 2 says "The bulletin's generation includes embedded generation and import (its footnote 8)", and the report adds that "Adding imports to a generation figure that already includes them counts them twice". The footnote is printed beneath the text of section 3.2, on "Total electricity generation"; Table 3.7's total is hydro plus thermal plus other renewables (within 1 GWh every year), with no import column. The bulletin's Table 3.10 puts the energy transmitted at the generation total plus imports, within 46 GWh, in every year 2000 to 2006 (2002: generation 7,273, imports 1,146, transmitted 8,402 GWh), which could not be if the total already held the imports; and the 2025 and 2024 energy balances book the plants' output at the table's total (2,403 and 2,199 ktoe) with imports in a row of their own (0.9 and 4.9 ktoe). Imports should not be read as part of `generation_total`, and generation less exports plus imports counts them once. The header could keep footnote 8's words and add that the bulletin's transmission table and energy balance treat the total as excluding imports.
2. **The table numbers are the body's; the list of tables and the text number them otherwise.** Header line 7 and the docstring name "tables 3.7, 3.8 and 3.9", the body's captions. The bulletin's list of tables (PDF page 6) names them "Table 3.4: Annual Electricity Generation", "Table 3.5: Electricity Import and Export (GWh)" and "Table 3.6: System and Domestic Peak Load (MW)", and lists 3.7 to 3.9 as "Electricity Transmitted and Transmission Losses", "Distribution Utilities' Purchases, Sales and Losses" and "Electricity Consumption by Sectors"; the section's text cites the generation table as "(Table 3.4)", the trade table as "Table 3.5" and the peak table as "Table 3.6"; and the body's own Table 3.4 is "Grid Installed and Dependable Capacity (MW)". The report names the difference for the peak table only. Adding the titles and the printed pages (12, 14 and 16) to header line 7 would let a reader find the tables either way.
3. **The bulletin defines the system peak in two ways, and the header gives one.** Header line 2 and the docstring say "the system peak is Ghana's peak plus export load" (footnote 11). Section 3.4's text describes it as "comprising Ghana Load at Peak, and export load", which is Ghana's load at the system's peak hour, not necessarily Ghana's own peak. The two years in which Ghana's peak is above the system peak, 2001 (1,213 against 1,190 MW) and 2007 (1,276 against 1,274), are both years of net imports (net exports -160 and -186 GWh); under the text's reading such a year is possible, under the footnote's it is not. The header could name both definitions, so that `peak_system` less `peak_ghana` is not read as export load.
4. **Two small slips.** The report's "27.94 TWh (2025)" is the bulletin's 27,945 GWh, 27.945 TWh (the bulletin's text: "27,945 GWh in 2025"). The docstring of `runs/c112/s2373/cross.py` reads "Session 2371: energycom_ghana_electricity_annual against Ember's Sri Lanka"; the script reads Ghana (`owid_energy:GHA`) and was written in session 2373.
5. **The license record says the Commission was not read.** `docs/licenses.md` lists the table under "Not settled: a publisher was not read" ("not read: Energy Commission, Ghana") and lists the Commission among the "Publishers no read of this sweep covers", though `license_reads.csv` records reads 606 to 609 of its pages from session 2373. What is missing is a verdict row in `license_verdicts.csv` (the bulletin and the pages state no terms), not a read.

Compared besides, with no contradiction found: the header's and docstring's counts, years, variables, units, the factor of 1,000, "A dash has no row; nothing is filled", footnote 8's words as quoted, the years named in header line 3, `retrieved_at` and the blank `vintage` against the probe log, the robots file, the source lines, and every row against the bulletin's text. Of the bulletin's footnotes, 9 (planned and unplanned imports) and 10 (whose loads make up Ghana's peak) agree with the variables as the docstring describes them; 8 and 11 are points 1 and 3.

Acted on in session 2375: the docstring and header line 2 now say that table 3.7's total holds no imports, footnote 8 notwithstanding, and give both of the bulletin's definitions of the system peak, so that `peak_system` less `peak_ghana` is not read as export load. The source line names the tables by title and printed page, with the list of tables' other numbering. Session 2373's report is corrected on imports (counted once) and the 2025 total (27.945 TWh), and its cross-check's docstring names Ghana. Point 5: as for CEB, "not read" means no verdict; nothing was changed. The table was written again offline: the same rows.
