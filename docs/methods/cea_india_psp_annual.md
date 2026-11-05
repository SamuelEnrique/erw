# India's power supply position a fiscal year, by state, region and All India, from the Central Electricity Authority's March reports, 2020-21 to 2025-26

Energy Research Warehouse (ERW), method note written in session 2353 (chain 105's 2303) for a table first written on 24 October 2026 (session 2295, `archive/sessions/SESSION_2295_REPORT.md`, "India's power supply position (the Central Electricity Authority, in place of Grid-India)", commit `dc2688cb`, on the branch `wip/2294-2307-data`). No other method note covers it. India's demand a calendar year, from Ember, is `owid_ember_electricity_annual` (entity `owid_energy:IND`).

Tables: `cea_india_psp_annual`

## Publisher and address

Central Electricity Authority (CEA), Government of India, "Power Supply Position - Energy", its monthly Energy Power Supply Position Reports, listed on the dashboard page `https://cea.nic.in/reports/dashboardView?headingId=107&subHeadingId=1003&subSubHeadingId=10010&title=Power%20Supply%20Position%20-%20Energy&lang=en`, each report a PDF at `https://cea.nic.in/api/dashboardReports/download-pdf/en/<id>`. The table reads the March report of each fiscal year, whose second block is the year to date (April to March); the six ids are in `REPORTS` in the connector (2020-21 `84cabd50-...` to 2025-26 `895565cb-...`). Each report is one page, "Figures in MU net". Source id `cea:power_supply_position_energy` (`sources.csv`: publisher "Central Electricity Authority (India)", report "Power Supply Position - Energy, monthly reports", license internal, first and last seen 2026-10-24). cea.nic.in's robots file allows every path (read 506); grid-india.in and www.grid-india.in reset the connection at their robots files, so Grid-India gave nothing (session 2295).

Raw files on this machine: the six PDFs under `warehouse/raw/cea_india_psp/20261024T053219Z_probe/` (3,981,746 bytes), fetched by session 2295's probe (`runs/c105/s2295/probe.py`, rows 7 to 12 of its `probe.csv`) from 2026-10-24T05:33:42Z to 05:34:19Z, every response 200 with no `Last-Modified`. Three folders of that morning's trials (`20261024T053511Z`, `...053534Z`, `...053558Z`) hold empty manifests; the write's folder, `20261024T053656Z`, holds only the data lock's check.

Connector: `warehouse/connectors/cea_india_psp.py` (session 2295), `--offline` and `--out-dir`. It requires each report to print "April,YYYY to March,YYYY", takes each line ending in eight figures (the month's requirement, supply, shortfall and percent, then the year's), keeps the year's three energies, joins a name printed on the next line, and closes the places above each region line into that region. The regions must sum to All India within 5 MU a region, or the run stops. Ceiling: six requests, one a fiscal year.

Schedule: none. No line of `warehouse/run_daily.sh`, the data machine's scripts, `warehouse/scheduled.py` or a workflow names the connector; it was run once by hand. `run_status.csv`: no row (the run wrote `runs/status/cea_india_psp.json`, "777 rows", run `20261024T053656Z`, which nothing appended; disagreement 10). `archive_manifest.csv` (this worktree): 777 rows, run `20261024T053702Z-local`, data hash `67c90848...`, which the table's rows give again. Not in `redivis_uploads.csv` and not in `warehouse/redivis/config.yaml`. Live set: `catalogue_hold` in `warehouse/supabase/live_set.yaml`, no rule. Sector `power` (`build_coverage.py`). Readers: none; `tests/test_session2295.py` (3 tests) builds lines in CEA's form.

## Vintage and revision

One snapshot: header line 10, "File holds 777 rows, one snapshot; the previous file held 0 rows". The run `20261024T053656Z` read the six PDFs from the probe's folder (its log: "raw file reused" six times) and asked for nothing (disagreement 8). `retrieved_at` is the probe's time for each report, one value a fiscal year (2025-26 05:33:42Z to 2020-21 05:34:19Z); `vintage` is blank in every row, and nothing records a publication time, since CEA sent none.

All six English titles read "(Revised)"; the 2020-21 report is titled "Energy Supply Position Report (Revised)", the others "Energy Power Supply Position Report (Revised)"; 2023-24's Hindi title reads provisional where its English reads revised (disagreement 7). A later run asks for all six again and replaces the file whole, so a revision by CEA would overwrite the figures here and leave no earlier copy.

## Shape and variables

Series, 777 rows, 16 columns: the series columns and `x_kind`, `x_region`, `x_fiscal_year`; 10 header lines. Three variables, 259 rows each: `energy_requirement`, `energy_supplied`, `energy_not_supplied`. Unit MWh (CEA's MU, million units of net energy, times 1,000; every value is a whole MU). `freq` P1Y, `geo` IN, `market` and `vintage` blank. Entity `cea_psp:<slug of CEA's name>`, 49 entities; `node` CEA's English name, 51 spellings (disagreement 3).

| Fiscal year | Rows | Places | States | Islands (outside their region) | Regions | All India | `retrieved_at` |
|---|---|---|---|---|---|---|---|
| 2020-21 | 129 | 43 | 35 | 2 | 5 | 1 | 05:34:19Z |
| 2021-22 | 129 | 43 | 35 | 2 | 5 | 1 | 05:34:15Z |
| 2022-23 | 126 | 42 | 34 | 2 | 5 | 1 | 05:34:10Z |
| 2023-24 | 126 | 42 | 34 | 2 | 5 | 1 | 05:34:05Z |
| 2024-25 | 126 | 42 | 34 | 2 | 5 | 1 | 05:34:01Z |
| 2025-26 | 141 | 47 | 39 | 2 | 5 | 1 | 05:33:42Z |

- **`x_kind`**: `state` 633 rows, `state_outside_region_total` 36 (Lakshadweep, `x_region` Southern Region, and Andaman-Nicobar, `x_region` Eastern Region, every year), `region` 90, `country` 18. CEA's own footnote: "Lakshadweep and Andaman & Nicobar Islands are stand- alone systems, power supply position of these, does not form part of regional requirement and energy supplied."
- **Places that change.** Dadra & Nagar Haveli and Daman & Diu are two entities in 2020-21 and 2021-22 (`dadra_nagar_haveli`, `daman_diu`) and one from 2022-23 (`dadra_nagar_haveli_and_daman_diu`). The five `others_<region>` entities hold only 2025-26 (CEA's "Others" lines, which only that report prints). DVC (the Damodar Valley Corporation) is one of the Eastern Region's lines, as CEA prints it.
- **All India**, TWh: requirement 1,275.534 (2020-21), 1,379.812, 1,513.497, 1,626.132, 1,693.959, 1,707.493 (2025-26); supplied 1,270.663 to 1,706.985; not supplied 4.871, 5.787, 7.583, 4.112, 1.590, 0.508, a shortfall of 0.382, 0.419, 0.501, 0.253, 0.094 and 0.030 percent.
- **The largest places in 2025-26**, requirement in MU: Maharashtra 202,867, Uttar Pradesh 163,501, Gujarat 156,588, Tamil Nadu 132,328, Rajasthan 110,657.
- **The largest shortfalls**: UT of J&K and Ladakh 2,551 MU in 2020-21 (12.9 percent of its requirement), 1,524 in 2021-22 (7.64), 19 in 2025-26 (0.09); Jharkhand 990 MU in 2022-23 (7.46 percent); Andaman-Nicobar 4.73 percent in 2025-26 (20 MU).
- **Not supplied is printed, not computed.** Requirement less supplied differs from not supplied by exactly 1 MU in 47 of the 259 place-years, each figure rounded on its own ("The MU figures has been rounded off to nearest unit place", note 1). Supplied never exceeds requirement; from 2022-23 CEA says so by construction ("Energy Supplied has been matched with Energy Requirement where Energy Requirement is less than Energy Supplied", note 3).

## Placing values in time, and what is filled

`ts_utc` is the fiscal year's first day, 1 April, at 00:00:00Z (2020-04-01 to 2025-04-01); `x_fiscal_year` is CEA's label (2020-21). A row covers India's fiscal year, 1 April to 31 March, as the report's "April,YYYY to March,YYYY" block; the month's figures in the same lines are not taken. India's day starts at 18:30Z the day before; the stamp is the date, not the instant.

Nothing is filled. A place has a row only in the years its report prints it. One figure is CEA's own substitute: Andaman-Nicobar 2025-26 is marked (**), "As data of March-2026 not received hence data of February-2026 has been considered" (note 4), and its node keeps the mark. Tripura is marked (*), "Excludes energy exported to Bangladesh".

The regions sum to All India within 2 MU in every year and variable (largest: 2021-22 requirement, regions 1,379,810 against 1,379,812; 2022-23 supplied, 1,505,916 against 1,505,914). All India therefore excludes the two islands too (496 MU of requirement in 2025-26). A region's line less its states (islands left out), requirement in MU:

| Region | 2020-21 | 2021-22 | 2022-23 | 2023-24 | 2024-25 | 2025-26 |
|---|---|---|---|---|---|---|
| Northern | -2 | 0 | +1,197 | +1,344 | +1,457 | 0 |
| Western | 0 | -1 | +6,225 | +10,332 | +11,314 | 0 |
| Southern | 0 | 0 | +49 | +49 | +47 | 0 |
| Eastern | 0 | -1 | +63 | +53 | +57 | 0 |
| North-Eastern | +1 | -1 | +9 | +8 | +9 | +1 |

From 2022-23 every region is marked (##): "The Regional figures include data of other miscellaneous entities drawing power directly from ISTS" (the interstate transmission system; note 2). From 2022-23 to 2024-25 that consumption is in the region's line and in no place's; in 2025-26 CEA prints it as each region's "Others" line, and the gaps close. A sum of states is therefore not its region in those three years.

## License

Header line 9: "License: internal until the licenses' round reads CEA's terms. Source: Central Electricity Authority." `coverage.csv` and `sources.csv`: internal. `warehouse/metadata/license_verdicts.csv`, Central Electricity Authority (India) (read 517, CEA's Copyright Policy, `https://cea.nic.in/api/websitepolicy/pdf/view/en/2`, read 2026-10-24T06:23:58Z): "The content available on this Website/(www.cea.nic.in) is provided for public use and may be reproduced free of charge, subject to the following conditions: [...] Users must obtain prior permission by sending an email request to the designated CEA contact.", verdict "needs written permission", the same if the ERW sells anything; contact "the designated CEA contact (the policy names no address)"; note: "free of charge, after prior permission by email, unmodified, with CEA acknowledged as the source, not misleading; third-party material excepted. cea_india_psp_annual stays internal until the permission is asked for and given." `docs/licenses.md`, the table's row: Central Electricity Authority (India), "needs written permission", flag internal, "agrees", ERW verdict internal; it is listed under "Permission needed". `license_tables.csv`: "the source registry". No row in `license_status.csv`. `SESSION_2299_REPORT.md` leaves "Ask CEA for permission?" for Samuel's ruling; no letter was sent.

## Checks (session 2353)

The figures in this note were computed by `runs/c105/s2353/check_cea_india_psp_annual.py` (output `check_cea_india_psp_annual.out` beside it) from the rows of `warehouse/output/cea_india_psp_annual.csv` in the main checkout, read past its 10 header lines (counted), and from the six saved PDFs, parsed there with pdfplumber by its own reading of the lines (not the connector's). `look_cea_pdf.py` printed each report's text (`look_cea_pdf_*.out`). No request was made.

- 777 rows, no (entity, variable, ts_utc) twice, no blank value; one unit, one source; each fiscal year's rows cite the one report of that year by `source_url`; the data hash equals the archive manifest's.
- **Against the reports:** every one of the 777 rows equals the report's year-to-date figure, and every place the six reports print is in the table (43, 43, 42, 42, 42 and 47 lines). As printed, All India 2025-26 reads "1,48,147 1,48,093 54 0.0 17,07,493 17,06,985 508 0.0" (the table: 1,707,493,000, 1,706,985,000 and 508,000 MWh); 2020-21, "12,75,534 12,70,663 4,871 0.4" for the year. Maharashtra 2025-26: "2,02,867 2,02,854 13" for the year; 2020-21: "1,50,679 1,50,663 16". UT of J&K and Ladakh 2025-26, whose name is printed on the line after its figures, "20,185 20,166 19", is in the table under its name.
- **Against Ember's India demand** (`owid_ember_electricity_annual`, `owid_energy:IND`, `electricity_demand`, calendar years): All India's energy supplied a fiscal year over Ember's demand of the calendar year it starts in is 0.8128 (2020-21: 1,270.7 against 1,563.3 TWh), 0.8185, 0.8353, 0.8465 (2023-24), 0.8319 and 0.8196 (2025-26: 1,707.0 against 2,082.8 TWh): 81 to 85 percent, as session 2295 found (`runs/c105/s2295/cross.py`, on its trial file, whose figures the table repeats). Against the calendar year it ends in, 0.7569 to 0.8125 (2020-21 to 2024-25). CEA counts the energy the grid supplied, net; Ember's demand is larger (captive generation among the difference), and the gap is a definition, not an error to correct.

## Where the description and the data disagree

1. **"Lakshadweep" alone outside its region.** The docstring ("state_outside_region_total for a place CEA marks # and leaves out of its region's total, Lakshadweep") and `SESSION_2295_REPORT.md` ("Places CEA marks "#" (Lakshadweep)"). Andaman-Nicobar is marked # in all six reports, is `state_outside_region_total` in all six years, and is left out of the Eastern Region's sum.
2. **`x_kind` in the header.** Header line 2: "x_kind state, region or country". 36 rows carry `state_outside_region_total`.
3. **"node the name as CEA prints it".** The docstring. The connector strips CEA's # marks and keeps (*) and (**): Tripura is "Tripura *" in 2020-21 and 2021-22 and "Tripura (*)" after, and Andaman-Nicobar is "Andaman- Nicobar  (**)" (two spaces) in 2025-26. 49 entities carry 51 node spellings, and `coverage.csv` gives the table 51 nodes, which `docs/coverage.md` lists as if they were 51 places.
4. **The header's list of region gaps.** Header line 3 names twelve gaps of regions CEA marks ##; the North-Eastern Region, marked ## in the same years, holds +9, +8 and +9 MU more than its states in 2022-23 to 2024-25 and is not named (the connector names a gap only above 5 MU a place).
5. **"Until 2024-25".** `SESSION_2295_REPORT.md`: "Until 2024-25 the consumption it does not show by state is folded into the region". Only from 2022-23: the 2020-21 and 2021-22 reports carry no ## and their regions equal their states within 2 MU.
6. **"Others" as states.** The five `others_<region>` entities of 2025-26 have `x_kind` state; CEA's note 2 says they are "other miscellaneous entities drawing power directly from ISTS", not states, and the docstring's "consumption it does not show by state" is the connector's word for them, not CEA's.
7. **"The 2026 one is marked revised".** The docstring ("CEA revises reports; the 2026 one is marked revised"). All six English titles read "(Revised)"; 2023-24's Hindi title reads provisional.
8. **"Retrieved: 20261024T053656Z" and "each asked again unless --offline".** Header line 4 names the run that wrote the file, and the docstring says each report is asked again on a run. That run was offline and asked for nothing (its raw folder holds only the lock check); the six PDFs were fetched by session 2295's probe at 05:33:42Z to 05:34:19Z, as the second half of line 4 and `retrieved_at` say.
9. **"Internal until the licenses' round reads CEA's terms."** Header line 9 and the docstring. Session 2299 read them (read 517): "needs written permission".
10. **No record of the run.** `CLAUDE.md` describes `run_status.csv` as "every run and every gap"; it holds no row of `cea_india_psp`; the run by hand wrote only `runs/status/cea_india_psp.json`.

Not acted on: this note changes no file but itself.

## The session report against the table

`SESSION_2295_REPORT.md`: "777 figures, fiscal years 2020-21 to 2025-26, for 49 states, regions and All India": holds (49 entities). "Names printed over two lines are joined, and 'Others' carry their region": holds. "The regions sum to All India in every year, to CEA's rounding": holds, within 2 MU. "The gaps are named in the header, up to 11,314 MU (the Western Region, 2024-25)": holds, but for the North-Eastern Region's (disagreement 4). "All India's energy supplied grew from 1,271 TWh (2020-21) to 1,707 TWh (2025-26)" and "The shortfall fell from 0.38 percent to 0.03 percent": hold, though not every year (0.50 percent in 2022-23). "81 to 85 percent of Ember's India demand": holds (81.3 to 84.6). "Places CEA marks '#' (Lakshadweep)" and "Until 2024-25": disagreements 1 and 5.

## What it does not hold

- The month's figures and CEA's percents (the percents follow from the energies); the other eleven reports of each year; years before 2020-21.
- Peak demand and peak met, which these energy reports do not carry; generation by source; consumption by sector; captive generation.
- The two island systems in All India or in their regions (they are rows of their own); the "miscellaneous entities drawing power directly from ISTS" by place before 2025-26 (only in their region's line).
- Grid-India's daily and monthly reports (its hosts refused the reader); any earlier copy of a report CEA has revised.
