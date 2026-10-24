# EIA's annual net generation by balancing authority, a year, 2023 to 2025 (EIA, Form EIA-923 annual files, summed by plant)

Energy Research Warehouse (ERW), method note written in session 2256 (chain 102) for a table first written on 19 October 2026 (session 323).

Tables: `eia_annual_generation_ba`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-923 Power Plant Operations Report, one zip a year listed on `https://www.eia.gov/electricity/data/eia923/`. In each, the workbook `EIA923_Schedules_2_3_4_5_M_12_<year>_Final` (2023: `..._Final_Revision`) has a sheet "Page 1 Generation and Fuel Data", a row for each plant, prime mover and fuel with the plant's "Balancing Authority Code" and the year's "Net Generation (Megawatthours)", and a sheet "Page 1 Energy Storage". The three files read:

| Year | Address | Last-Modified (`vintage`) |
|---|---|---|
| 2023 | `https://www.eia.gov/electricity/data/eia923/archive/xls/f923_2023.zip` | Tue, 19 Aug 2025 13:42:05 GMT |
| 2024 | `https://www.eia.gov/electricity/data/eia923/archive/xls/f923_2024.zip` | Mon, 12 Jan 2026 20:59:57 GMT |
| 2025 | `https://www.eia.gov/electricity/data/eia923/xls/f923_2025.zip` | Fri, 11 Sep 2026 13:28:33 GMT |

The Electric Power Annual has no table by balancing authority (its index, `https://www.eia.gov/electricity/annual/`, read on 19 October 2026), so the annual figure is EIA-923's plant rows summed by their code.

Source id `eia:eia923_annual`. Connector: `warehouse/connectors/eia923_annual_ba.py` (session 323), its only table. The connector makes no request: it reads the zips saved in a folder named by `--from-raw` (required) and that folder's `manifest.csv`. Session 323 made the five requests itself (the two index pages and the three zips, 21:08:28 to 21:08:50 UTC on 19 October 2026) and saved them in `warehouse/raw/eia923_annual/s323/` on the data machine (not in git). EIA's robots file disallows any path holding `archive/` (`Disallow: /*archive/`, read 307 of `warehouse/metadata/license_reads.csv`, session 2163); the 2023 and 2024 zips are under `/electricity/data/eia923/archive/xls/`. They were asked on 19 October 2026, four days before the ERW's first read of EIA's robots file (read 144, session 937, 23 October 2026).

Read by `warehouse/derived/eia_annual_crosscheck.py` (`eia_annual_crosscheck_ba`), which adds `net_generation_mwh` and `storage_net_generation_mwh` for each balancing authority and year and sets EIA-930's hourly sums against them. Method: `docs/methods/eia_annual_crosscheck.md`.

The table is not scheduled: no line of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `scripts/` or `.github/workflows/` names the connector, and `warehouse/metadata/run_status.csv` holds no row for it. It was written once, by run `20261019T225937Z` on the data machine (session 323's report: "19 October 2026, from 21:08 UTC (the reading) and 22:59 UTC (the writes)").

## Vintage and revision

Years 2023, 2024 and 2025 (`ts_utc` 2023-01-01 to 2025-01-01). `retrieved_at` is the time each zip was saved (2026-10-19T21:08:49Z for 2023, 21:08:50Z for 2024 and 2025); `vintage` is the zip's Last-Modified. `coverage.csv` gives the same 515 rows, 68 nodes, the same first and last `ts_utc`, and last run 2026-10-19T22:59:37Z; `archive_manifest.csv` holds 515 rows.

Each run deletes the table and writes it whole from the zips in the folder named. EIA revises a year's file after it is final (2023's workbook is "Final_Revision"); a revision reaches the table only when a person saves the new zip and runs the connector again.

## Shape and variables

Series, 515 rows, 68 entities, three variables. `entity` `eia923:<Balancing Authority Code>`; `eia923:none` for plants with no code (blank or "."); `eia923:state_fuel_increment` for EIA's "State-Fuel Level Increment" rows (its estimate for plants outside the monthly sample, plant id 99999 in 2025's file, counted as one plant). `freq` P1Y; `ts_utc` the year's 1 January; `geo` US; `market` and `node` empty; `source_url` the year's zip. Values are EIA's sums, rounded to 0.001 MWh.

| `variable` | `unit` | Rows (2023, 2024, 2025) | What it is |
|---|---|---|---|
| net_generation_mwh | MWh | 201 (67, 67, 67) | the sum of "Net Generation (Megawatthours)" over the plant rows of Page 1 Generation and Fuel Data with the code |
| storage_net_generation_mwh | MWh | 113 (36, 37, 40) | the same sum over Page 1 Energy Storage (see below) |
| plants | count | 201 (67, 67, 67) | the plants with a row on Page 1 Generation and Fuel Data |

| Year | Net generation, all entities | Plants | `none` | `state_fuel_increment` | Storage sheet, all entities |
|---|---|---|---|---|---|
| 2023 | 4,183.270 TWh | 12,308 | 15.400 TWh, 229 plants | 7.450 TWh | +59.767 TWh |
| 2024 | 4,308.634 TWh | 13,210 | 15.336 TWh, 230 plants | 9.407 TWh | +79.264 TWh |
| 2025 | 4,425.029 TWh | 14,045 | 16.133 TWh, 227 plants | 12.479 TWh | +99.682 TWh |

The largest in 2025: PJM 879.12 TWh, MISO 695.05, ERCO 524.99, SWPP 292.24, SOCO 262.21. Codes outside the Lower 48 are in the table: HECO (Hawaii, 15 to 22 plants), CEA (one Alaska plant, a battery substation, 2025 only, -2,500 MWh), and NBSO (plants in Maine coded to New Brunswick's operator). HGMA holds 2023 and 2024 only. Net generation is below zero at HST in every year (-3,965, -3,259 and -4,346 MWh) and at CEA in 2025.

`storage_net_generation_mwh` is not the storage plants' net. In the saved workbooks Page 1 Energy Storage holds every generator row of each plant that has storage (2025: 1,571 rows of 997 plants, prime movers BA 951 rows, PV 448, PS 39, GT 28, HY 19, WT 19 and others), and every one of those plants is also on Page 1 Generation and Fuel Data, where their rows sum, in all, to the same figure (59.767, 79.264 and 99.682 TWh). Grand Coulee's hydro row (16,153,784 MWh in 2025) is on both sheets, under BPAT. So 92 of the 113 storage values are above zero, 20 below and 1 zero, and the variable is already inside `net_generation_mwh`. The battery and pumped storage rows alone (prime movers BA and PS) sum to -7.271, -8.251 and -9.638 TWh on Page 1 Generation and Fuel Data.

The counts in this note were computed in session 2256 with pandas from the rows of `warehouse/output/eia_annual_generation_ba.csv`, read past its 10 header lines, and from the three saved zips in `warehouse/raw/eia923_annual/s323/` (read on the data machine, no request); no (entity, variable, ts_utc) is given twice, and the yearly sums of `net_generation_mwh` equal the sums of the workbooks' Page 1 Generation and Fuel Data.

## Checks the connector makes

- No request, so no pause check; EIA is not in `warehouse/metadata/paused_sources.csv`.
- Each sheet's header row is the first of its first 20 rows that holds "Plant Id", or the run stops. A year with no Page 1 Energy Storage sheet has no storage rows.
- A value of "Net Generation (Megawatthours)" that is not a number becomes empty and drops out of the sum without a word (`errors="coerce"`); in the three files read there is none.
- The file's year is read from the workbook's name; `source_url`, `retrieved_at` and `vintage` from the folder's `manifest.csv`.
- The write needs the data lock (`ip.write_csv`); a failure writes nothing and records the failure in the run status file.

## License

The header: "License: public. EIA's data are in the public domain (https://www.eia.gov/about/copyrights_reuse.php). Credit: U.S. Energy Information Administration." `license_verdicts.csv` gives EIA "may be public" (read 1; the same if the ERW sells anything), asking for the acknowledgment "Source: U.S. Energy Information Administration". `license_tables.csv` names EIA as the one publisher, from the source registry; `docs/licenses.md` gives the ERW verdict public; `coverage.csv`: public. `warehouse/supabase/live_set.yaml` loads the table whole (session 323, the Grid tool's decisions block) under `review_hold`.

## Found while writing this note

- The docstring, the method `docs/methods/eia_annual_crosscheck.md` and session 323's report ("Storage counts in EIA-923's figure (Page 1 Energy Storage, negative)") call `storage_net_generation_mwh` negative, storage taking more than it returns. 92 of its 113 values are positive: Page 1 Energy Storage repeats every generator row of the plants that have storage, all of them already on Page 1 Generation and Fuel Data.
- `eia_annual_crosscheck.py` adds the two variables ("storage included"), so EIA-923's side of `eia_annual_crosscheck_ba` counts those plants twice. Against `net_generation_mwh` alone, EIA-930 less EIA-923 as a percent of EIA-923 is, for 2023, 2024 and 2025: CISO -1.96, +2.38, +3.85 (the table: -9.18, -8.35, -8.72); ERCO -6.10, -5.61, -7.59 (-7.53, -7.62, -10.45); ISNE -5.18, -4.33, -3.83; MISO -5.44, -4.57, -5.49; NYIS -4.72, -3.30, -3.36; PJM -0.02, -0.93, -0.60; SWPP +3.06, +2.64, +3.38; US48 -2.91, -2.62, -2.62 (-4.27, -4.38, -4.76). The reasons the cross-check gives by rule would change with them: CISO's would be within 2 percent in 2023.
- The 2023 and 2024 zips are under `/electricity/data/eia923/archive/`, which EIA's robots file disallows (`/*archive/`, read 307). They were asked before the ERW first read that file; a rebuild with newer files from those paths needs the owner's word.
- A value that is not a number is dropped from a sum without a log line or a count (`pd.to_numeric(..., errors="coerce")`), where the ERW's rule is to fail loudly.
- The cross-check's Lower 48 is every code but `none`, `HECO` and `state_fuel_increment`, so CEA (an Alaska plant, -2,500 MWh in 2025) is counted in it; the amount is too small to move a figure.

## What it does not hold

- Years before 2023: earlier zips are on EIA's page; session 323's ceiling was five requests.
- Months, plants, fuels or prime movers: the sums are by code and year only.
- Battery and pumped storage net generation on its own: the storage variable is the whole generation of plants that have storage.
- EIA's estimate placed in a balancing authority: the "State-Fuel Level Increment" rows are an entity of their own.
