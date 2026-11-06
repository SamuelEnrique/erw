# Sri Lanka's power stations, installed capacity and net generation by owner and source, and the day and night maximum demand, 2024 and 2025 (CEB, Statistical Digest 2025, page 3)

Energy Research Warehouse (ERW), method note written in session 2375 (chain 112) for a table first written on 24 October 2026 (session 2371 of chain 112, its report `archive/sessions/SESSION_2371_REPORT.md`).

Tables: `ceb_srilanka_electricity_annual`

## Publisher and address

Ceylon Electricity Board, Sri Lanka (CEB), its Statistical Digest 2025 (Web Edition), listed as a PDF on its other publications page (`https://www.ceb.lk/publication-media/other-publications/en`, read 608, which lists the digests 2005 to 2025), one request:

- `https://www.ceb.lk/front_img/img_reports/1783568926SD-2025-Finalized-(Web-Edition).pdf`

Source id `ceb:statistical_digest`. The digest is 12 pages (PDF title "CEB Statistical Digest Report", created 9 July 2026, 09:18:17 +05:30). Its third PDF page, headed "GENERATION STATISTICS" and printed with the folio 1, holds the three tables taken, each giving 2024 and 2025: number of power stations and installed capacity (MW) by "Owenership & Type of Power Station" (CEB's spelling), both 2024 columns headed "(Restated)"; net generation (GWh) by "Ownership & Source"; and a small table of average daily generation, day and night maximum demand (MW) and the night maximum's date. Rows run under two owners, "CEB :" and "IPP :" (independent power producers), each with a "Total" row, and a grand "Total" (stations and capacity) or "Total Generation" row. The page's notes: "1. NCRE -Non Conventional Renewable Energy"; "2. NCRE (Other)- Dendro, Biomass & Municipal Solid Waste". The percentage and percentage-change columns are not taken.

Session 2371's probe (`runs/c112/s2371/probe.csv`) made 13 requests: 3 to www.pucsl.gov.lk and 4 to gendata.pucsl.gov.lk (PUCSL's dispatch dashboard, left because its figures load only in the browser; reads 599 to 605), and 6 to www.ceb.lk, at least 33 seconds apart (08:42:39Z to 08:46:26Z), against the robots file's crawl delay of 30: the robots file (read 606), the home page (read 607), the publications page (read 608) and three digests (HTTP 200: 2025, 1,040,814 bytes at 2026-10-24T08:44:43Z, Last-Modified "Thu, 09 Jul 2026 03:48:46 GMT"; 2023, 580,335 bytes; 2022, 1,999,717 bytes). All 13 are saved in `runs/license_reads/s2371/`, and the 2025 digest's text, as pdftotext gave it, in `runs/c112/s2371/sd2025.txt`. The 2025 digest was seeded into `warehouse/raw/ceb_srilanka/20261024T084109Z_probe/` (the same SHA-256, d986f5ea...), and the trial and the write read it offline ("raw file reused", run log).

Connector: `warehouse/connectors/ceb_srilanka.py` (session 2371): `[--offline] [--out-dir DIR]`, one request, the tables read with pdfplumber's table extraction from the first of the first eight pages that holds both "Total Generation" and "Installed Capacity (MW)". The capacity table's header must be CEB's, the three tables' years must agree, each owner's sources must add to its total, and CEB's and the IPPs' totals to the Total row, within 1.5 (in CEB's printed unit: a station, a MW or a GWh); an owner or source not in the map, a value that is not a number or a failed check stops the run. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. The table is internal; it is held from the live set (listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`) and is not in the Redivis release package, which takes public tables only (`warehouse/redivis/release_v1.py`: "an internal table is never in the public dataset").

## Vintage and revision

One write, run `20261024T084813Z` ("This run wrote 80 rows: 80 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs"), from the saved digest. `retrieved_at` is the digest's download time, 2026-10-24T08:44:43Z, and `vintage` its Last-Modified, 2026-07-09T03:48:46Z, in every row; every row's `source_url` is the digest.

The 2024 stations and capacity are CEB's restated figures: page 3 heads both 2024 columns "(Restated)", and the digest's summary page marks 2024's 377 stations and 4,651 MW with "* Restated". The generation and demand figures carry no mark; on the summary page only the rooftop solar connections and capacity of 2025 and some financial lines are marked "(a) : Provisional". Each year is read from the 2025 digest only, so 2024 is the figure as CEB printed it a year later. A later run merges by (entity, variable, ts_utc).

## Shape and variables

Series, 80 rows, one entity `ceb:LK`, `node` Sri Lanka, `geo` LK, `freq` P1Y, `market` blank. 40 variables, each with a row in both years: 12 `stations_<owner>_<source>` (`unit` count), 12 `capacity_<owner>_<source>` (MW), 14 `generation_<owner>_<source>` (MWh, CEB's GWh times 1,000) and `max_demand_day`, `max_demand_night` (MW). Owner `ceb`, `ipp`, or `all` for the grand Total row, which has only `total`.

| Owner and source | CEB's row | Stations 2024 | Stations 2025 | MW 2024 | MW 2025 |
|---|---|---|---|---|---|
| ceb_total | CEB : Total | 29 | 28 | 3,338 | 3,261 |
| ceb_major_hydro | Major Hydro | 19 | 19 | 1,533 | 1,530 |
| ceb_thermal_oil | Thermal (Oil) | 8 | 7 | 801 | 727 |
| ceb_thermal_coal | Thermal (Coal) | 1 | 1 | 900 | 900 |
| ceb_ncre_wind | NCRE (Wind) | 1 | 1 | 104 | 104 |
| ipp_total | IPP : Total | 348 | 389 | 1,313 | 1,554 |
| ipp_thermal_oil | Thermal (Oil) | 2 | 2 | 482 | 582 |
| ipp_ncre_mini_hydro | NCRE (Mini Hydro) | 217 | 221 | 432 | 437 |
| ipp_ncre_wind | NCRE (Wind) | 19 | 19 | 163 | 163 |
| ipp_ncre_other | NCRE (Other) | 15 | 16 | 63 | 64 |
| ipp_ncre_grid_solar | NCRE (Grid Connected Solar) | 95 | 131 | 173 | 307 |
| all_total | Total | 377 | 417 | 4,651 | 4,814 |

| Variable | CEB's row | 2024 | 2025 |
|---|---|---|---|
| generation_ceb_total | CEB : Total | 12,861 | 12,968 |
| generation_ceb_major_hydro | Major Hydro | 5,426 | 6,306 |
| generation_ceb_thermal_oil | Thermal (Oil) | 1,568 | 1,415 |
| generation_ceb_thermal_coal | Thermal (Coal) | 5,482 | 4,870 |
| generation_ceb_ncre_wind | NCRE (Wind) | 383 | 373 |
| generation_ceb_small_islands | Small Islands | 2.8 | 3.0 |
| generation_ipp_total | IPP : Total | 3,940 | 4,845 |
| generation_ipp_thermal_oil | Thermal (Oil) | 768 | 798 |
| generation_ipp_ncre_mini_hydro | NCRE (Mini Hydro) | 1,473 | 1,425 |
| generation_ipp_ncre_wind | NCRE (Wind) | 409 | 401 |
| generation_ipp_ncre_other | NCRE (Other) | 167 | 203 |
| generation_ipp_ncre_grid_solar | NCRE (Grid Connected Solar) | 257 | 343 |
| generation_ipp_ncre_rooftop_solar | NCRE(Rooftop Solar) | 867 | 1,674 |
| generation_all_total | Total Generation | 16,802 | 17,812 |
| max_demand_day | Day Maximum Demand (MW) | 2,459.7 | 2,826.1 |
| max_demand_night | Night Maximum Demand (MW) | 2,673.0 | 2,895.9 |

GWh and MW as CEB prints them on page 3, the same as the table's rows (generation times 1,000 in MWh), from `runs/c112/s2375/notes/lk.out`.

- **Rooftop solar and small islands are generation rows only.** The station and capacity tables have no rooftop solar and no small islands row, so `capacity_all_total` (4,651 and 4,814 MW) leaves out rooftop solar, which the summary page gives as 1,141 MW (2024) and 1,935 MW (2025, provisional), while `generation_all_total` includes the rooftop row.
- **The rooftop row is energy exported to CEB's network.** The next page, "ROOFTOP SOLAR PV DETAILS OF THE CEB NET WORK", gives "Energy exported in GWh" by scheme (Net Metering 87 and 115, Net Accounting 419 and 702, Net Plus 260 and 233, Net Plus Plus 101 and 624; Total 867 and 1,674), from 73,050 and 108,979 consumer accounts: the same totals as `generation_ipp_ncre_rooftop_solar`. CEB prints the row under "IPP :", and the table keeps it there; it is not independent producers' output, nor the panels' whole output (what consumers use themselves is not exported).
- **The night maximum is the year's maximum.** The summary page's "Maximum Demand" is 2,673 and 2,896 MW, the night figures; the day maximum is lower in both years.
- **No zero, no negative value.** The smallest are `stations_ceb_ncre_wind` and `stations_ceb_thermal_coal`, 1 in both years; the only figures CEB prints with a decimal are small islands' generation and the two maximum demands.

## Placing values in time, and what is filled

`ts_utc` is the year's 1 January at 00:00:00Z, a label for the calendar year: 2024-01-01 and 2025-01-01. Stations and capacity are as CEB states them for the year (the page gives no date within it); generation is the year's total; the maximum demands are the year's maxima, the night one recorded on 2024-09-26 and 2025-10-30 (not taken). No cell of the three tables is blank, and nothing is filled.

## License

Header: "License: internal. Neither the digest nor CEB's pages read state terms of reuse; internal until a ruling. Cite: Ceylon Electricity Board, Statistical Digest 2025." `warehouse/metadata/license_verdicts.csv` holds no row for CEB. `warehouse/metadata/license_reads.csv` records reads 606 to 608 (session 2371): the robots file ("allows every path; a crawl delay of 30 seconds; names no AI agent"; the file is `User-agent: *` and `Crawl-delay: 30`, nothing else), the home page ("links the publications pages") and the other publications page ("states no terms of reuse"). The two pages carry the line "Copyright @ 2026 Ceylon Electricity Board" and no terms; the digest's text holds no copyright or reuse notice. `docs/licenses.md`, the table's row: verdict today "not settled (needs written permission by default)", not read "Ceylon Electricity Board, Sri Lanka (CEB)", flag internal, "not settled", if the ERW sells anything "may be public", ERW verdict internal. The report leaves the ruling to Samuel ("public or internal? It states no terms").

## Checks (session 2375)

The figures in this note were computed from the rows of `warehouse/output/ceb_srilanka_electricity_annual.csv`, read past its 10 header lines (counted), and from the saved digests, read only (scripts `runs/c112/s2375/notes/lk.py`, `lk2.py`, `lk3.py`, `lkpdf.py` and `lkold.py`, outputs `lk.out`, `lk2.out`, `lk3.out`, `lkpdf.out` and `lkold.out` beside them).

- 80 rows, 40 variables, 2024 and 2025, as header lines 1, 3 and 10 state; one entity; no (entity, variable, ts_utc) twice; no blank, zero or negative value; 24 rows in count, 28 in MW, 28 in MWh.
- **Against the PDF:** pdfplumber's extraction of the third page, made again (`lkpdf.out`), gives row by row the figures of the two tables above, which are the table's; every one of the table's 80 values, in CEB's units, is among the page's printed numbers (`lk3.py`, `lk3.out`).
- **The table's sums, in CEB's units:** CEB's sources against its total: stations and capacity 0 in both years, generation +0.8 GWh (2024, the 2.8 GWh of small islands) and -1 GWh (2025); the IPPs': stations 0, capacity 0 and -1 MW (2025), generation +1 and -1 GWh; CEB's and the IPPs' totals against the Total row: stations 0, capacity 0 and +1 MW (2025), generation -1 GWh (2024) and +1 GWh (2025). Header line 3's 1.5 holds.
- **Against the digest's own summary:** renewable generation (major hydro and the NCRE rows) 8,982 and 10,725 GWh, 53.46 and 60.21 percent of the total; the summary page prints 8,982 and 10,726 GWh, 53.5 and 60.2 percent. Net generation over the night maximum times the year's hours is 71.56 and 70.21 percent; the summary's "System Load Factor (Calculated on Net Generation)" is 71.6 and 70.2. Net generation over the year's days is 45.91 and 48.80 GWh a day, as page 3 prints.
- **The trial against the table:** `runs/c112/s2371/trial/ceb_srilanka_electricity_annual.csv` has the same 80 keys with 0 differences in value, unit, `retrieved_at`, `vintage` or `source_url`.
- Session 2371's cross-check (`runs/c112/s2371/cross.py`, `cross.out`, run on the trial): CEB's net generation 16.802 and 17.812 TWh against `owid_ember_electricity_annual`'s Sri Lanka demand, 17.07 and 17.25 TWh: 1.57 percent below in 2024 and 3.26 percent above in 2025.
- Session 2375's own: without the rooftop row, CEB's net generation is 15,935 and 16,138 GWh, 6.65 and 6.45 percent below Ember's demand; the rooftop row is 5.16 and 9.40 percent of the total, and 2025's is 1.931 times 2024's.
- **The earlier digests:** in the 2023 digest's second page, 1,366 of 10,953 extracted characters belong to "(cid:" codes and no label reads; in the 2022 digest's generation table pdfplumber puts CEB's five source rows of 2021 into one cell (Major Hydro to Small Islands), while its capacity table reads cleanly (4,186 and 4,084 MW in total for 2021 and 2022). Both as the report and the docstring say.

## The session report against the table

Every figure of `SESSION_2371_REPORT.md` checked against the table, the PDF, the probe log and `cross.out` holds (80 rows, 2024 and 2025, page 3 of the Statistical Digest 2025, the owners, net generation 16.802 and 17.812 TWh, Ember's 17.07 and 17.25 TWh, 1.57 percent below and 3.26 above, rooftop solar 1,674 GWh nearly double 2024's 867, installed capacity 4,651 MW restated and 4,814 MW, night maximum 2,673.0 and 2,895.9 MW, the checks within 1.5, reads 599 to 608, 13 requests of 15 and the hosts' counts, CEB's requests 30 seconds or more apart, the 2023 and 2022 digests not used), except:

- "power stations and installed capacity, by owner ... and source (major hydro, oil, coal, wind, mini hydro, other NCRE, grid and rooftop solar, small islands)": rooftop solar and small islands are generation rows only (point 2).
- "the 2025 rooftop solar (1,674 GWh, nearly double 2024's) is part of the difference": the row is energy exported to CEB's network (point 1). Without it CEB is 6.65 and 6.45 percent below Ember in both years, so the swing from below to above Ember matches the rooftop row's growth; the cross-check does not test what Ember counts.
- "Its figures load only in the browser, through a dozen script chunks": the generation profile page names 21 script files (point 5).

## Limits

- **Capacity and generation do not cover the same plants.** Capacity and station counts leave out rooftop solar (1,141 and 1,935 MW on the summary page) and small islands; generation includes rooftop exports and small islands. A capacity factor computed from `capacity_all_total` and `generation_all_total` mixes the two.
- **Rooftop exports are CEB's network's.** The rooftop page is titled for "THE CEB NET WORK"; the Lanka Electricity Company (LECO), supplied by CEB in bulk ("Bulk Supply to LECO" in the sales tables), runs its own distribution network. Whether exports from rooftop systems on LECO's network are in the row, the digest does not say.
- **Small islands** are CEB's generation for the small islands (2.8 and 3.0 GWh); the digest gives no capacity or station count for them and does not say whether they are grid-connected.
- **Two years only.** Each year is the 2025 digest's figure; a figure CEB restates in the 2026 digest replaces it only when a later run reads that digest.

## What it does not hold

- The summary page (rooftop connections and capacity, reservoir capacity and storage, energy sold, losses, prices and revenue, consumer accounts, load factor), rooftop exports by scheme, fuel cost, fuel rate and thermal efficiency by plant, sales by distribution division and tariff, LECO's sales, the percentage columns, average daily generation and the night maximum's date; generation by plant or month; years before 2024 (the publications page lists digests from 2005; the 2023 and 2022 digests were fetched and not used); PUCSL's dispatch data.

## Points for the session to act on

1. **The rooftop row is energy exported, and rooftop capacity is missing.** Header line 2 calls the generation rows "CEB's net GWh" by owner and source, and the docstring lists `ncre_rooftop_solar` as a source of net generation. The digest's next page, "ROOFTOP SOLAR PV DETAILS OF THE CEB NET WORK", gives the same 867 and 1,674 GWh as "Energy exported in GWh" from 73,050 and 108,979 consumer accounts under four net metering schemes; the chart on page 3 is titled "Energy Exported from Rooftop Solar (CEB)". The row is therefore exports to CEB's network, not producers' output, and it sits under "IPP" only because CEB prints it there. The capacity rows leave rooftop solar out (the summary page: 1,141 MW in 2024, 1,935 MW in 2025, provisional). A clause in header line 2 would keep a reader from reading `generation_ipp_ncre_rooftop_solar` as independent producers' generation, or `capacity_all_total` as all capacity.
2. **The report lists rooftop solar and small islands among the station and capacity sources.** Its bullet reads "power stations and installed capacity, by owner (CEB, the independent producers, all) and source (major hydro, oil, coal, wind, mini hydro, other NCRE, grid and rooftop solar, small islands); net generation, likewise". The station and capacity tables have neither row (24 station and capacity variables, 12 each, none for rooftop or small islands); both are in generation only.
3. **"CEB prints whole numbers" does not hold, and the 1.5 has no unit.** The docstring gives the tolerance of 1.5 "(CEB prints whole numbers)". CEB prints small islands' generation as 2.8 and 3.0 GWh and the maximum demands to 0.1 MW; the 2.8 GWh is why CEB's 2024 sources add to 0.8 GWh more than its total. The check runs on CEB's printed values, so in the table's generation rows the 1.5 is 1,500 MWh; header line 3 says "within 1.5" without a unit.
4. **"Page 3" is the PDF's third page, printed as page 1.** Header line 7 and the docstring say "page 3"; the page's own folio is 1, and the summary page cites these figures as "Page Ref. 1". The digest's printed page 3 is the sales page. Naming both ("the third PDF page, printed page 1, GENERATION STATISTICS") would let a reader find it.
5. **The dashboard's scripts are 21, not a dozen.** The report says PUCSL's figures load "through a dozen script chunks". The saved generation profile page (`runs/license_reads/s2371/06_...generation_profile.bin`) names 21 distinct script files under `/_next/static/chunks/`, the home page 19. The conclusion (no data address in the page's own script, read 605) stands.
6. **The license record says CEB was not read.** `docs/licenses.md` lists the table under "Not settled: a publisher was not read" ("not read: Ceylon Electricity Board, Sri Lanka (CEB)") and lists CEB among the "Publishers no read of this sweep covers", though `license_reads.csv` records reads 606 to 608 of CEB's pages from session 2371. What is missing is a verdict row in `license_verdicts.csv` (the pages state no terms), not a read.

Compared besides, with no contradiction found: the header's and docstring's counts, years, owners, sources and their names, the units, the factor of 1,000, "2024's stations and capacity are CEB's restated figures", "Nothing is filled", `retrieved_at` and `vintage` against the probe log, the robots file's 30 seconds and the spacing of the requests, the reasons the 2023 and 2022 digests are not read, and every row against the PDF.

Acted on in session 2375: the docstring and header line 2 now say that `generation_ipp_ncre_rooftop_solar` is rooftop solar's energy exported to the network, not IPP output, and that rooftop solar has no capacity row (1,141 MW in 2024 and 1,935 MW in 2025 on the summary page), so `capacity_all_total` leaves it out. Header line 3 gives the 1.5 tolerance in CEB's printed units; the docstring no longer says CEB prints whole numbers; the source line names the PDF's third page as printed page 1. Session 2371's report now lists small islands and rooftop solar as generation rows only and counts the dashboard's 21 scripts. Point 6: "not read" in `docs/licenses.md` means no verdict, which an internal table under unstated terms does not have (as REN's since chain 104); nothing was changed. The table was written again offline: the same rows.
