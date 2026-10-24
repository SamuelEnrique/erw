# Rwanda's electricity generation by plant, the regionally shared hydro plants, imports, and electricity sold by customer category, a quarter, July 2021 to June 2024 (Rwanda Utilities Regulatory Authority, Electricity Statistics Reports)

Energy Research Warehouse (ERW), method note written in session 2452 (chain 118) for a table first written on 24 October 2026 (session 2448 of chain 118, its report `archive/sessions/SESSION_2448_REPORT.md`).

Tables: `rura_rwanda_electricity_quarterly`

## Publisher and address

Rwanda Utilities Regulatory Authority (RURA), its quarterly Electricity Statistics Reports, listed on its energy sector statistics page (`https://www.rura.rw/sectors/energy/statistics`, read 814) and that page's first list page (read 815), which names ten reports from "Report_for_Electricity_Statistics_as_of_December_2020" to "the_Second_Quarter_2024". Three are taken, three requests:

- `https://www.rura.rw/fileadmin/user_upload/RURA/Documents/Sectors/Energy/Energy_Statistics/Electricity_Statistics_Report_as_of_September_2022.pdf` (Q3 2021 to Q3 2022)
- `.../Electricity_Statistics_Report_as_of_the_First_Quarter_2023_.pdf` (Q1 2022 to Q1 2023)
- `.../Electricity_Statistics_Report_as_of_the_Second_Quarter_2024.pdf` (Q2 2023 to Q2 2024)

Source id `rura:electricity_statistics_report`. Each report has 10 pages and the same plan: Table 1, "Domestic generation, regional shared and imports (kWh)" (in the September 2022 report "Trends of domestic generation, regional shared and imports (kWh) from Q3-21 to Q3-22"), a row a plant, then "Total domestic generation", "Regional shared HPP", "Imports" and "Total"; Table 2, the generation mix in percent; Figure 1, the system peak demand (MW); a figure of "electricity supplied to the national grid" (kWh); Table 3, "Trends of electricity sold (kWh)", a row a customer category; a figure of exported electricity (kWh); and the end user tariffs (Tables 4 to 7). Every table and figure carries the source line "Source: EUCL-REG". The plant table's first heading reads "Pant name" in the 2022 and 2023 reports and "Plant name" in the 2024 report. Each cover page reads "Disclaimer: Information provided in this report is subject to alteration in case of any revision or update deemed necessary."

What the reports say, and do not say, about the lines taken:

- **"Regional shared HPP" is not defined** in any of the three, nor are the plants or the countries it covers named. The prose calls it "Regional Shared plants" or "Regional shared power plants" and counts it in what Rwanda "produced" (Q2 2024: "Domestic power plants accounted for 81.3% of this electricity generation, while Regional Shared plants contributed 11.6%, and 7.1% was sourced through imports"). RURA's own mix (Table 2) counts it as hydro generation, not as imports: Table 2's six shares reproduce from Table 1 in all 12 quarters, within 0.006 percentage points, only when the regional shared line is added to hydro (this note's grouping, which the reports do not print: methane Kivuwatt and Shema Power; peat Hakan QP and Gishoma PPP; thermal (fuel oil) Jabana 1 TPP, Jabana 2 TPP and the three So Energy plants; solar Nasho solar, Jali Solar and GigaWatt Global; hydro every other plant and the regional shared line), and Table 2's "Imports" share equals Table 1's imports over its total in all 12 quarters. Hydro without the regional line would be 5.4 to 11.9 points lower (the regional line's share of the total) (Q2 2024: 37.84 percent against the printed 49.44). The Q2 2024 prose's "50.70% of the produced electricity came from renewable sources" is hydro (49.44) plus solar (1.26). The regional shared figures are round thousands of kWh from Q3 2021 to Q2 2023 (17,976,000 to 21,268,000) and not from Q3 2023 (20,820,844 onward).
- **"Imports" is not defined** beyond the prose ("sourced through imports", "imported electricity").
- **Electricity sold**: the Q2 2024 report defines it as "the amount of electricity that a utility provider has delivered to customers within a specific timeframe ... This metric represents the actual consumption of electricity by end-users ... The electricity sold includes both the pre-paid and post-paid electricity"; the two earlier reports give only the last sentence, under the heading "ELECTRICITY SOLD DOMESICALLY" (so spelled). Table 3 nevertheless includes "Exports" as a category, and its "Total" adds them. The Q2 2024 prose names the "Nasho Own Use" line "Nasho irrigation" ("Nasho irrigation consumed 0.3%"; 852,997 of 297,107,270 kWh).
- **Electricity supplied to the national grid** is described as "the amount of electricity supplied within the country per quarter, excluding the electricity exported to neighboring countries", and given only in a figure. In all 12 quarters it equals Table 1's Total less the exports (Table 3's, or for Q3 and Q4 2021 the September 2022 report's export figure, 2,699,238 and 2,058,757 kWh), within 1 kWh.
- **Losses**: the word does not appear in any of the three reports. They give no loss line and no own use of plants.

Session 2448's probe (`runs/c118/s2448/probe.csv`) made 9 requests: the robots file of www.reg.rw (no answer within 60 seconds, 12:22:00Z, read 810), and 8 to www.rura.rw: its robots file (HTTP 200, 12:23:11Z, read 811), the home page (read 812), the statistics page (read 813), the energy sector statistics page and its list page (reads 814 and 815), and the three reports (reads 816 to 818): the Q2 2024 report first, at 12:24:20Z (266,173 bytes, Last-Modified "Wed, 19 Mar 2025 09:24:32 GMT"), then the Q1 2023 report at 12:24:54Z (670,326 bytes, "Fri, 12 Apr 2024 15:20:24 GMT") and the September 2022 report at 12:24:57Z (641,960 bytes, "Fri, 12 Apr 2024 15:19:28 GMT"). All are saved in `runs/license_reads/s2448/`, each with the probe log's SHA-256 (checked in this session). The write read them offline from `warehouse/raw/rura_rwanda/20261024T122200Z_probe/` ("raw file reused", run log).

Connector: `warehouse/connectors/rura_rwanda.py` (session 2448): `[--offline] [--out-dir DIR]`, three requests, 2 seconds apart when asked, oldest report first; a quarter two reports give is taken from the later one. The tables are found by pdfplumber's `extract_tables`, by the first cell "plant name", "pant name" or "customer category"; the plant table's rows are gathered from every page it spans. A row of Table 1 whose label is not one of the four totals is a plant. Checks, each stopping the run: the plants add to the domestic total, and domestic, regional shared and imports add to the total, within 1 MWh; the categories add to the total sold within 1 MWh where a total is printed; each heading reads "Qn YYYY"; each value reads as a number (a dash or blank has no row). **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. The table is internal; it is held from the live set (listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`) and is not in the Redivis release package, which takes public tables only (`warehouse/redivis/release_v1.py`: "an internal table is never in the public dataset").

## Vintage and revision

One write, run `20261024T123517Z` ("This run wrote 690 rows: 690 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs"), from the saved reports; the report records no separate trial. Each row's `source_url`, `retrieved_at` and `vintage` are its report's: 110 rows from the September 2022 report (Q3 and Q4 2021; retrieved 2026-10-24T12:24:57Z, `vintage` 2024-04-12T15:19:28Z), 293 from the Q1 2023 report (Q1 2022 to Q1 2023; 12:24:54Z, 2024-04-12T15:20:24Z) and 287 from the Q2 2024 report (Q2 2023 to Q2 2024; 12:24:20Z, 2025-03-19T09:24:32Z). The `vintage` is the server's Last-Modified, the upload date, not the date of publication: the two older reports were both saved on 12 April 2024.

The reports agree wherever two give the same line and quarter (165 cells for Q1 to Q3 2022, 0 differences, this session's count; the run log's "0 values differ"). The cover's disclaimer allows revision; no figure is marked provisional. The seven reports not taken (December 2020, June 2022, Q4 2022, Q2 2023, Q3 2023, Q4 2023, Q1 2024) were not read, so whether they give other figures for the same quarters is not known. A later run asks the three addresses again and merges by (entity, variable, ts_utc).

## Shape and variables

Series, 690 rows, 45 entities, `unit` MWh throughout (the reports' kWh divided by 1,000), `freq` P3M, `geo` RW, `market` blank, `node` the report's label. 44 plant entities `rura:RW:<plant>` with the one variable `generation` (487 rows), and `rura:RW` with 18 variables (203 rows):

| Variable | Rows | The report's line |
|---|---|---|
| generation (44 plants) | 487 | Table 1, a row a plant; 33 plants in all 12 quarters, 11 in fewer (below) |
| generation_domestic | 12 | Table 1, Total domestic generation |
| generation_regional_shared | 12 | Table 1, Regional shared HPP |
| imports | 12 | Table 1, Imports |
| generation_total | 12 | Table 1, Total |
| sales_residential, _non_residential, _water_pumping_stations, _water_treatment_plants, _broadcasters, _health_facilities, _telecom_towers, _hotels, _commercial_data_centers, _industries | 12 each | Table 3, the ten categories of every report |
| sales_street_lights, sales_exports | 10 each | Table 3, Street lights, Exports: Q1 2022 to Q2 2024 |
| sales_nasho_own_use | 5 | Table 3, Nasho Own Use: Q2 2023 to Q2 2024 (the Q2 2024 report only) |
| sales_total | 10 | Table 3, Total: Q1 2022 to Q2 2024 |

The plants with fewer than 12 quarters: Nyirabuhombohombo 11 (a dash in Q2 2024), Gaseke MHPP 9, Gishoma PPP 10, So Energy Mukungwa 1, Masoro and Birembo 9 each (to Q3 2023), Jabana 1 TPP and Murunda MHPP 8 each (to Q2 2023), and Kavumu Mwange, Shema Power and Ntaruka A HPP 6 each (from Q1 2023; dashes before in the Q1 2023 report, not listed in the September 2022 report). Four zeros are kept as printed ("0.0"): Janja MHPP Q3 2021, Gishoma PPP Q1 2022, Gashashi Q4 2022, Keya MHPP Q1 2023. The table holds no plant's fuel or capacity; the labels carry "HPP", "MHPP", "TPP" or "PPP" for some plants only.

Source values for three quarters, kWh as printed (`runs/c118/s2452/notes/rw07.txt`, `rw08.txt`, `rw09.txt`); the table holds each divided by 1,000:

| Line | Q3 2021 (Sep 2022 report) | Q1 2023 (Q1 2023 report) | Q2 2024 (Q2 2024 report) |
|---|---|---|---|
| Total domestic generation | 231,427,729 | 276,116,106 | 297,381,774 |
| Regional shared HPP | 17,976,000 | 18,452,000 | 42,452,549 |
| Imports | 7,308,458 | 7,353,011 | 26,100,538 |
| Total | 256,712,188 | 301,921,117 | 365,934,860 |
| Table 3, Total sold | (not printed) | 249,372,331 | 297,107,270 |
| Table 3, Exports | (figure only: 2,699,238) | 2,526,787 | 6,566,586 |
| Supplied to the national grid (figure) | 254,012,949 | 299,394,330 | 359,368,274 |

The years both of whose four quarters the table holds, MWh, from the table (`runs/c118/s2452/notes/rw2.out`):

| Year | Total | Domestic | Regional shared | Imports | Sold (total) | of which exports |
|---|---|---|---|---|---|---|
| 2022 | 1,131,313.995 | 1,034,040.178 | 65,400.000 | 31,873.817 | 934,713.644 | 9,128.672 |
| 2023 | 1,274,698.336 | 1,066,682.873 | 98,224.269 | 109,791.194 | 1,057,251.437 | 10,673.618 |

- **Imports rise in 2023:** 2.4 to 3.2 percent of the total from Q3 2021 to Q1 2023, then 4.9 percent in Q2 2023 and 18.8 percent in Q3 2023 (61,000.830 MWh), then 6.5 to 7.8 percent.
- **Methane overtakes the large hydro plants:** Shema Power rises from 248.490 MWh in Q1 2023 to 86,974.800 in Q2 2024, the largest plant that quarter, ahead of Kivuwatt (53,720.408) and Nyabarongo HPP (38,954.100).
- **Sold against supplied:** domestic sales (the total sold less exports) fall short of the electricity supplied to the national grid by 16.2 to 19.2 percent of it in Q1 2022 to Q2 2024 (Q2 2024: 68,827.590 MWh); the reports do not say what the gap holds (point 3).

## Placing values in time, and what is filled

`ts_utc` is the quarter's first day at 00:00:00Z, a label for the calendar quarter, 2021-07-01 (July to September 2021) to 2024-04-01 (April to June 2024). Every value is the quarter's energy. A dash, a blank, or a line a report does not print has no row; nothing is filled. Q3 and Q4 2021 have no total sold, street lights or exports, and Q3 2021 to Q1 2023 no Nasho Own Use, because the reports giving those quarters do not print them in Table 3.

## License

Header: "License: internal. RURA's pages carry a copyright line and state no terms of reuse; internal until a ruling. Cite: Rwanda Utilities Regulatory Authority, Electricity Statistics Report." The saved home page (read 812) carries "© 2026 Rwanda Utilities Regulatory Authority". The robots file (read 811) disallows TYPO3 system paths (among them `/fileadmin/templates/html/*`, not `/fileadmin/user_upload/`) and, after a second `User-agent: *` line, names a long list of crawlers with "Disallow:/", among them CCBot; it names no Anthropic agent. `warehouse/metadata/license_verdicts.csv` holds no row for RURA. `warehouse/metadata/license_reads.csv` records reads 810 to 818 (session 2448). `docs/licenses.md`, the table's row: verdict today "not settled (needs written permission by default)", not read "Rwanda Utilities Regulatory Authority (RURA)", flag internal, "not settled", if the ERW sells anything "may be public", ERW verdict internal; the table is listed under "Not settled: a publisher was not read" (point 6). The report leaves the ruling to Samuel.

## Checks (session 2452)

The figures in this note were computed from the rows of `warehouse/output/rura_rwanda_electricity_quarterly.csv`, read past its 10 header lines (counted), and from the three saved reports, read only with pdfplumber's `extract_tables` and `extract_text` from their bytes (scripts `runs/c118/s2452/notes/rw_dump.py`, `rw.py`, `rw2.py`, `rw3.py` and `rw4.py`, outputs `rw07.txt`, `rw08.txt`, `rw09.txt`, `rw.out`, `rw2.out`, `rw3.out` and `rw4.out` beside them).

- 690 rows, 45 entities, July 2021 to June 2024, as header lines 1, 3 and 10 state; no (entity, variable, ts_utc) twice; no blank value; one `source`.
- **Against the reports:** an independent read of the three reports' Table 1 and Table 3, the latest report winning, gives exactly the table's 690 keys and values (0 missing, 0 extra, 0 differences); 35 dashes and 4 printed zeros among the cells used.
- **The identities:** generation total less exports equals the "supplied to the national grid" figure in all 12 quarters within 1 kWh (Q3 2021: 1 kWh); Table 2 reproduces from Table 1 with the regional shared line as hydro, within 0.006 points (above).
- **The text layer:** in `runs/c118/s2448/q2_2024.txt`, session 2448's text copy of the Q2 2024 report, Shema Power's line carries 443,147, 469,423 and 549,377, Kavumu Mwange's figures, as the report says; pdfplumber's own `extract_text` gives the same figures as its tables.
- Session 2448's cross-check (`runs/c118/s2448/cross.py`, `cross.out`): RURA's total (domestic, regional shared and imports) against `owid_ember_electricity_annual`'s Rwanda demand, 2022 and 2023 only: 1.131 against 1.060 TWh (6.7 percent above) and 1.275 against 1.200 TWh (6.2 percent above); sold 0.935 and 1.057 TWh. The total includes the exports (0.009 and 0.011 TWh), which do not explain the gap.

## The session report against the table

Every figure of `SESSION_2448_REPORT.md` checked against the table, the reports and `cross.out` holds (690 rows, 45 entities, July 2021 to June 2024, three reports of five quarters, reads 810 to 818, the checks within 1 MWh, 0 values differing between reports, the September 2022 sales table's ten categories and no total, Shema Power's 87 GWh in a quarter, peat's 3.03 percent, 233.74 MW in Q2 2024, 6.7 and 6.2 percent, 1.131 against 1.060 and 1.275 against 1.200 TWh, 0.935 and 1.057 TWh about 17 percent below supply (17.4 and 17.1), 9 requests of 15, 8 to www.rura.rw, the reports 0.3 to 0.7 MB, the copyright line), except:

- "So Q3 and Q4 2021 have no `sales_total` and lack those three categories": true, but Nasho's own use is missing from Q1 2022 to Q1 2023 as well (point 1).
- "from a 56 MW methane plant": no saved file gives Shema Power's capacity; not verified (point 7).

## Limits

- **What the regional shared line is** is not stated: hydro by its name and by RURA's mix, but no plant, country or share rule is given.
- **Sales include exports.** `sales_total` is not domestic consumption; less `sales_exports` it is.
- **No losses.** The reports give none; supply less domestic sales holds losses and anything else not billed, in proportions the reports do not give.
- **Plants are not typed.** The table holds no fuel per plant; RURA's mix is in percentages only (Table 2, not taken).
- **Three of ten reports.** Earlier quarters (from December 2020) and the intermediate reports were not read.

## What it does not hold

- The generation mix (Table 2, percentages), the system peak demand (Figure 1, MW: 233.74 in Q2 2024), the electricity supplied to the national grid and the exports figure (figures only), the tariffs (Tables 4 to 7), and quarters before July 2021 or after June 2024.

## Points for the session to act on

1. **Nasho's own use is missing from Q3 2021 to Q1 2023, not only from 2021.** Header line 3 reads "(Q3 and Q4 2021: ten categories, no total, street lights, Nasho's own use or exports)", and the docstring that the September 2022 report prints no "street lights, Nasho's own use or exports, so Q3 and Q4 2021 have no sales_total and those three categories". The Q1 2023 report's Table 3 has no "Nasho Own Use" line either (its lines are 12 categories, Industries to Street lights, and Total), so `sales_nasho_own_use` has 5 rows, Q2 2023 to Q2 2024, and `sales_total` for Q1 2022 to Q1 2023 is a total without that line. The Q2 2024 report's prose calls it "Nasho irrigation". The header could give the quarters each category covers.
2. **What "Regional shared HPP" and "Imports" are, the header does not say, and the reports do not define.** Header line 2 gives `generation_regional_shared` with no definition and the docstring "the regionally shared plants' share". None of the three reports defines the line or names the plants or countries. RURA's own mix counts it as hydro generation, not imports: Table 2 reproduces from Table 1 within 0.006 points in all 12 quarters only so, its "Imports" share is Table 1's imports over the total, and the Q2 2024 report's 50.70 percent renewable is hydro (49.44, the regional line included) plus solar (1.26). The figures are round thousands of kWh to Q2 2023. The header could say that RURA counts the line with hydro generation and defines neither it nor imports.
3. **`sales_total` includes exports, and the reports give no losses.** Header line 2 reads "Sales include exports and Nasho's own use as categories", and the two older reports head the table "ELECTRICITY SOLD DOMESICALLY". Generation total less `sales_exports` is RURA's "electricity supplied to the national grid" (a figure "excluding the electricity exported"), in all 12 quarters within 1 kWh. Domestic sales fall short of it by 16.2 to 19.2 percent in Q1 2022 to Q2 2024; the word "loss" appears in none of the reports. The header could say that the total sold less exports is domestic sales, and that supply less domestic sales is not a published loss figure.
4. **The exports of Q3 and Q4 2021 are printed, in a figure.** Header line 3 says those quarters have no exports; that is true of Table 3, but the September 2022 report's Figure 2 gives 2,699,238 and 2,058,757 kWh, and its supplied figure equals the total less them. Whether to take them is the session's choice (the peak, also a figure, is left out); the header could say they are in the figure.
5. **Header line 1's range reads "2021-07 to 2024-04".** These are the first and last quarters' first months; the last quarter runs to June 2024, as the report's title says. "Q3 2021 to Q2 2024" or "July 2021 to June 2024" would be the range.
6. **The license record says RURA was not read.** `docs/licenses.md` lists the table under "Not settled: a publisher was not read" ("not read: Rwanda Utilities Regulatory Authority (RURA)"), though `license_reads.csv` records reads 811 to 818 of its pages. As for AMM in session 2410, what is missing is a verdict (the pages state no terms), not a read.
7. **One figure of the report has no source in the saved files.** "Shema Power's 87 GWh in a quarter, from a 56 MW methane plant": the 86,974,800 kWh is the Q2 2024 report's; no saved report or page gives the 56 MW. The report could drop it or name its source.

Compared besides, with no contradiction found: the header's and docstring's counts, quarters, units, the factor of 1,000, the three addresses and the quarters each gives, "A quarter two reports give is taken from the later report", "0 values differ", "A dash or blank has no row; nothing is filled", the checks, the source line "EUCL-REG", the peak "in a figure only", node as the report's label, `retrieved_at` and `vintage` against the probe log, the robots file and the copyright line as quoted, and every row against the reports.

Acted on in session 2452: the docstring and header now say that neither "Regional shared HPP" nor "Imports" is defined and that RURA's own mix counts the regional line as hydro; that sales include exports, generation less exports being RURA's supply to the national grid, and that the reports give no losses; and how the categories grow (street lights and exports from Q1 2022, Nasho's own use from Q2 2023; Q3 and Q4 2021's exports given only in a figure, not taken). Header line 1 ends with the last quarter's last month. Session 2448's report is corrected on Shema Power's capacity, which no saved file gives. Point 6: "not read" means no verdict, as for AMM; nothing was changed. The table was written again offline: the same rows.
