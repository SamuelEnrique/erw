# ERCOT's wind and solar output, hourly, system-wide, from the yearly workbooks (ERCOT's Hourly Aggregated Wind and Solar Output)

Energy Research Warehouse (ERW), method note written in session 2138 (chain 090) for a table first written on 7 October 2026 (session 144).

Tables: `ercot_wind_solar_output_hourly`

What the curtailment page makes of ERCOT's output, and why these years have no estimate below the High Sustained Limit, is in `docs/methods/curtailment.md` (session 144 and later); this note describes the code and the rows as they stand.

## Publisher and address

Electric Reliability Council of Texas (ERCOT), "Hourly Aggregated Wind and Solar Output", data product PG7-126-M (report type 13424), page `https://www.ercot.com/mp/data-products/data-product-details?id=PG7-126-M`: one workbook a year. The connector reads the list, `https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=13424`, and asks for each workbook at `https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=<DocID>`. Source id `ercot:PG7-126-M`. Connector: `warehouse/connectors/ercot_wind_solar_history.py` (session 144), in two steps: `--pull` saves the files under `warehouse/raw/ercot_wind_solar_history/` with a manifest, and `--write` builds the table from the saved files only, under the data lock. The same connector writes `ercot_wind_solar_hsl_hourly` and `ercot_wind_solar_hsl_monthly` from ERCOT's hourly reports by region.

## Vintage and revision

2023, 2024 and 2025 in the file on the data machine, from 2023-01-01T06:00:00Z to 2026-01-01T05:00:00Z, the Central years whole. The file was rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261020T063359Z-github`, carrying the header of run `20261020T061137Z` (20 October 2026): "This run: ERCOT_2023_Hourly_WindSolar_Output 2023-01-01T06Z to 2024-01-01T05Z, 17,520 values; ERCOT_2024_Hourly_WindSolar_Output 2024-01-01T06Z to 2025-01-01T05Z, 17,568 values; ERCOT_2025_Hourly_WindSolar_Output 2025-01-01T06Z to 2026-01-01T05Z, 17,520 values."

| Year | Workbook (doclookupId) | Published by ERCOT | Rows | `retrieved_at` |
|---|---|---|---|---|
| 2023 | 971575038 | 2024-01-08 | 17,520 | 2026-10-07T09:32:46Z |
| 2024 | 1068801799 | 2025-01-13 | 17,568 | 2026-10-07T09:32:54Z |
| 2025 | 1182433954 | 2026-01-14 | 17,520 | 2026-10-07T09:22:54Z |

`vintage` is empty; `retrieved_at` is the workbook's download time from the manifest. ERCOT's list of 7 October 2026 held these three workbooks and no other, as the docstring and the header say. The daily workflow runs `--pull --write` (`warehouse/run_daily.sh`); a workbook already saved is not asked for again, so a year is not revised once held. When two saved workbooks hold the same hour, the later published is kept. Rows are merged into the file held on (entity, variable, ts_utc).

## Shape and variables

Series, 52,608 rows: 1 entity, 2 variables, 26,304 hours each, no hour missing. `entity` ercot:system; `unit` MW; `freq` PT1H; `ts_utc` the hour's start; `geo` US-TX; `market` and `node` empty. Values are the numbers the workbook stores, not rounded.

| Variable | The workbook's column (sheet) |
|---|---|
| `wind_generation_mw` | ERCOT.WIND.GEN (Wind Data) |
| `solar_generation_mw` | ERCOT.PVGR.GEN (Solar Data) |

| Year | Hours | Wind TWh | Wind mean MW | Wind highest MW | Solar TWh | Solar mean MW | Solar highest MW |
|---|---|---|---|---|---|---|---|
| 2023 | 8,760 | 107.989 | 12,327.5 | 26,268.3 | 31.868 | 3,637.9 | 13,741.7 |
| 2024 | 8,784 | 111.711 | 12,717.6 | 27,666.6 | 47.749 | 5,435.9 | 21,588.5 |
| 2025 | 8,760 | 114.939 | 13,120.9 | 28,264.5 | 67.516 | 7,707.3 | 29,503.1 |

Years are Central years. The highest wind hour is 2025-03-04T02:00Z, the highest solar hour 2025-09-09T17:00Z. No value is negative; the lowest wind hour is 37.9 MW.

The workbook's Time (Hour-Ending) is Central clock time. In each saved workbook the hour ending 01:00 is listed twice on the autumn clock change (5 November 2023, 3 November 2024, 2 November 2025) and the hour ending 02:00 is not listed on the spring change (12 March 2023, 10 March 2024, 9 March 2025), as the header says; the first of the two 01:00 rows is read as daylight time.

## Reading the source

- `--pull` asks `iso_prices.paused("ercot")` first and makes no request while ERCOT is paused (the run then reports "paused: no request made", and a `--write` in the same command still builds the table from the saved files).
- `--pull` asks the list afresh, then each listed file with the extension xlsx not yet saved. Each request is tried up to three times (waits of 10, 20 and 30 seconds), timeout 180 seconds, with a pause of 2 seconds after each file saved, lists included. HTTP 401 or 403, or a body that is not a zip or workbook where one should be, is recorded in the manifest and stops the pull: an access control is reported, never worked around. A workbook that cannot be read is recorded as "unread" and stops the pull.
- Ceiling: 2,000,000 rows of these series read to keep, counted in the manifest over every run and probe (`series_rows`). Before each workbook the pull stops if 17,600 more rows would pass it. The header gives 59,088 rows read.
- When `--pull` and `--write` run together, the write runs only when the pull ended without a stop or a failure.
- `--write` reads every saved workbook whose sha256 is the manifest's. A sheet named Wind Data or Solar Data must exist with a column Time (Hour-Ending) and the output column (ERCOT.WIND.GEN, ERCOT.PVGR.GEN, or the older names "Total Wind Output, MW" and "Total Solar Output, MW"). A time that is not a date and hour, or not on the hour, an output that is not a number, an hour listed twice in one workbook other than the autumn repeat, and a time the spring change skips stop the table. A blank output is no row. Each workbook must hold whole Central years, every step one hour (`check_year`). Only the output column is read: ERCOT.LOAD, installed capacity and the ratios are not.
- A failure of this table does not stop the two other tables of the run, nor theirs this one.

## License

Public. `license_verdicts.csv` records ERCOT, read 2 (`https://www.ercot.com/help/terms`, 12 October 2026 in `license_reads.csv`): "may be public", for public and for commercial use. The sentence: "raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices." The header quotes the same sentence, read 6 October 2026, and asks that "ERCOT" be cited. `sources.csv` flags `ercot:PG7-126-M` public; `license_tables.csv` lists the table under ERCOT.

## Cross-checks (session 2138)

- The counts above were computed from the rows, read past the header lines. No (entity, variable, ts_utc) is given twice, and the sheets of the three saved workbooks hold 8,760, 8,784 and 8,760 rows each, which are the rows of the table.
- `eia930_all_generation` begins on 26 August 2026 and shares no hour with this table. Against `generation_mix_hourly_profile` (iso:ercot, `wind_mwh` and `solar_mwh`, built from EIA-930's per-BA workbook over each month's complete days): the 35 months January 2023 to November 2025 are all complete there (`days_held` equals `days_in_month`); December 2025 is not in that table. In each of the 35 months EIA's monthly MWh and this table's sum of the Central month's hours differ by at most 0.0009 percent for wind (69.9 MWh) and 0.0054 percent for solar (104.2 MWh). Over the 35 months: wind 324,346,407 MWh in EIA-930 and 324,346,619 here; solar 143,077,268 and 143,078,114. The two agree; the profile's MWh are whole numbers, and the small differences may be EIA's own rounding of the hours.
- The header's count of the pull, "24 requests, 10,177,213 bytes", is of the run that wrote it, not of the manifest on the data machine, which records 35 requests (18 postings, 8 probes, 6 lists, 3 workbooks) and 11,850,911 bytes. Both give 59,088 series rows and 56,496 file rows.

## What it does not hold

- Years before 2023: ERCOT's list keeps three workbooks.
- 2026: ERCOT has posted each year's workbook in the January after it (8 January 2024, 13 January 2025, 14 January 2026).
- The High Sustained Limit and the regions: the workbook holds neither, so there is no output below the limit for these years. `ercot_wind_solar_hsl_hourly` holds them from 28 September 2026.
- ERCOT's load, installed capacity and ratios, which the workbook holds and the code does not read.
