# Residential energy credits claimed by state and tax year (the IRS's Statistics of Income, Historic Table 2)

Energy Research Warehouse (ERW), method note written in session 2094 (chain 068) for a table first written on 23 October 2026 (session 2087).

Tables: `irs_soi_energy_credits_annual`

## Publisher and address

Internal Revenue Service (IRS), Statistics of Income (SOI), SOI Tax Stats, Historic Table 2, individual income and tax data by state and size of adjusted gross income (`https://www.irs.gov/statistics/soi-tax-stats-historic-table-2`, `PAGE`, for 2020 to 2023, and `https://www.irs.gov/statistics/soi-tax-stats-historic-table-2-2015-2019` for 2015 to 2019). One CSV file a tax year under `https://www.irs.gov/pub/irs-soi/` (`BASE_URL`, `FILES`): `15in54cmcsv.csv`, `16in54cmcsv.csv`, `17in54cmcsv.csv`, `18in55cmagi.csv`, `19in55cmcsv.csv`, and `<yy>in55cmcsv.csv` for 2020 to 2023. The file names do not follow one pattern (session 2087 found `15in55cmcsv.csv` answers HTTP 404), so they are listed in the code, not built. One request a year, a pause of 1 second after each, timeout 120 seconds, with the ERW's user agent (`UA`). Each file is read as Latin-1. Source id `irs:soi_historic_table_2`. Connector: `warehouse/connectors/irs_soi_energy.py` (session 2087).

## Vintage and revision

The file on the data machine was written by run `20261023T211606Z` (23 October 2026), offline, from the nine files session 2087 saved in `warehouse/raw/irs_soi_energy/`. `retrieved_at` is one time a year, from 2026-10-23T21:13:17Z (2020) to 2026-10-23T21:13:23Z (2023) and from 2026-10-23T21:14:17Z (2015) to 2026-10-23T21:14:24Z (2019). `vintage`, the file's Last-Modified, is a year's own: 2016 2025-11-07T08:57:12Z, 2017 2019-10-31T02:11:53Z, 2018 2020-09-01T02:12:26Z, 2019 2021-12-08T13:39:13Z, 2020 2022-12-16T23:25:24Z, 2021 2024-02-27T03:11:29Z, 2022 2025-01-16T03:11:43Z, 2023 2026-08-21T14:12:00Z. The 2015 file was served with "Thu, 01 Jan 1970 00:00:00 GMT", so its `vintage` reads 1970-01-01T00:00:00Z; that is not a date of the file.

Each run builds the table whole and replaces the file (`ip.write_snapshot`). The files are asked for without `fresh` (`ip.fetch_raw`), so a year's file already saved in `warehouse/raw/irs_soi_energy/` is reused, and a revision SOI makes to it is not read until that raw file is gone. A new tax year is not read until it is added to `FILES` and `COLUMNS`. No age check is made.

## Shape and variables

Series, 1,074 rows: 54 places, 324 series (a place and a variable), tax years 2015 to 2023. By year: 2015 to 2017 106 rows each (53 places), 2018 to 2022 108 each (54 places), 2023 216 (54 places, four variables).

- `entity` `irs_soi:<SOI's state code>`: the 50 states, DC, Puerto Rico (`PR`, from 2018; the 2015 to 2017 files have no PR row), SOI's national row (`irs_soi:US`) and its other areas (`irs_soi:OA`). `node` the code.
- `geo` `US-<state>` for the states, DC and PR; `US` for the national row; empty for OA (20 rows).
- `ts_utc` the tax year's first day; `freq` P1Y; `market` empty; `x_soi_column` SOI's column.
- Only the row of all incomes (`AGI_STUB` 0) is taken.

| Variable | SOI column | Unit | Years | Rows |
|---|---|---|---|---|
| `residential_energy_credit_returns` | N07260 | count | 2015 to 2022 | 429 |
| `residential_energy_credit_amount` | A07260 | USD | 2015 to 2022 | 429 |
| `residential_clean_energy_credit_returns` | N07262 | count | 2023 | 54 |
| `residential_clean_energy_credit_amount` | A07262 | USD | 2023 | 54 |
| `energy_efficient_home_improvement_credit_returns` | N07265 | count | 2023 | 54 |
| `energy_efficient_home_improvement_credit_amount` | A07265 | USD | 2023 | 54 |

SOI's "Residential energy tax credit" is one column to 2022; for 2023, when the credit was split, SOI gives the "Residential clean energy credit" and the "Energy efficient home improvement credit", and the table keeps them as two credits, not added into the earlier one (`COLUMNS`). Returns are SOI's count of returns claiming the credit; amounts are SOI's thousands of dollars times 1,000, so every amount is a whole multiple of 1,000 USD. Values are written as whole numbers. No value is 0 or negative.

The national row (`irs_soi:US`): 2,605,570 returns and USD 2,169,448,000 in 2015; 726,440 returns in 2018, the fewest; 3,220,260 returns and USD 7,983,695,000 in 2022. In 2023, 1,518,210 returns claimed USD 7,791,024,000 of the clean energy credit and 2,612,610 returns USD 2,324,249,000 of the home improvement credit. A return can claim both 2023 credits, so their returns are not added.

## Reading the source

- A file without `STATE`, `AGI_STUB` or the year's columns of `COLUMNS` stops the run (`read_year`); the column names are stripped of spaces and read in capitals.
- A state given twice among the rows of all incomes, or a state code not of two capital letters, stops the run.
- A figure that is not a number once its commas are removed stops the run (`number`); nothing is filled.
- A year with no row of all incomes stops the run; a place, variable and year given twice stops it.
- The request is tried up to 4 times (`iso_prices.with_retries`), waiting 5 seconds times the attempt number after each failure; HTTP 404 is a `SourceGap`, not retried; any answer but HTTP 200 is a failure.
- Ceiling: nine requests, one file a year. No row ceiling is set in the code.
- Any failure is recorded as a failure, and no file is written.
- The connector does not call `iso_prices.paused()`; the IRS is not in `warehouse/metadata/paused_sources.csv`.

## License

Public. `sources.csv` has `public` for `irs:soi_historic_table_2`; the header: "License: public (a work of the U.S. government; cite "Internal Revenue Service, Statistics of Income")." `license_verdicts.csv`, Internal Revenue Service (IRS), Statistics of Income, from the licenses round of session 2089: "Government work is something created by a U.S. government officer or employee as part of their official duties." Verdict: may be public, and may be public for commercial use. The sentence is from USA.gov's Copyrighted government works page, read in session 2089; the IRS's own privacy policy, read in the same session, says nothing on the reuse of the site's content. Cite "Internal Revenue Service, Statistics of Income".

Robots: the robots read of session 2087 found that `www.irs.gov`'s file disallows its statistics index search and site paths, not `/pub/irs-soi` or `/statistics`.

## Cross-checks (session 2094)

- The counts above were computed from the rows, read past the header lines; they equal the header's (1,074 rows, 54 places). No (entity, variable, ts_utc) appears twice.
- Session 2087 checked the places against SOI's national row. Recomputed here: the places other than `irs_soi:US` (the states, DC, PR and OA) sum to the national amount exactly in every year and for every credit. Their returns differ from the national count by 0 (2015), 40 (2016), 30 (2017), 50 (2018), 30 (2019), 50 (2020), 70 (2021) and minus 10 (2022), and in 2023 by 10 (clean energy) and 50 (home improvement): SOI rounds its counts. The session's report gives "within 50"; 2021's 70 is the largest difference. Without PR the amounts no longer match from 2018, so PR is inside SOI's national row.
- Session 2087 also found the national rows of 2022 and 2023 equal to the figures SOI's labelled workbooks (`22in55cm.xlsx`, `23in55cm.xlsx`) print beside the same labels. The workbooks were not read again here.

## What it does not hold

- The income classes (`AGI_STUB` 1 and above); only the row of all incomes.
- Tax years before 2015, and years SOI has not yet published.
- Any other column of SOI's files, other credits included.
- Any figure below the state.
