# The value of construction put in place in the United States by type and owner, data centers and power among it, a month, January 1993 to August 2026 (U.S. Census Bureau, Construction Spending, C30)

Energy Research Warehouse (ERW), method note written in session 2261 (chain 102) for a table first written on 24 October 2026 (session 2258).

Tables: `census_c30_construction_monthly`

## Publisher and address

U.S. Census Bureau, Construction Spending (C30), its monthly time series by type of construction (`https://www.census.gov/construction/c30/historical_data.html`), four workbooks:

- `https://www.census.gov/construction/c30/xlsx/privsatime.xlsx`: private, seasonally adjusted annual rate
- `https://www.census.gov/construction/c30/xlsx/privtime.xlsx`: private, not seasonally adjusted
- `https://www.census.gov/construction/c30/xlsx/pubsatime.xlsx`: public, seasonally adjusted annual rate
- `https://www.census.gov/construction/c30/xlsx/pubtime.xlsx`: public, not seasonally adjusted

The User-Agent is "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)". Source id `census:c30_construction_spending`. Connector: `warehouse/connectors/census_c30.py` (session 2258), its only table. www.census.gov has no robots file (HTTP 404, read 460); the C30 data page (read 461) links the current release. The private power detail workbook (`privatepower.xlsx`) answered HTTP 500 to session 2258's probe and is not asked.

The table is not scheduled: no line of `warehouse/run_daily.sh`, the other `warehouse/*.sh` scripts, `scripts/` or `.github/workflows/` names the connector (searched in session 2261), and `run_status.csv` holds no row for it. It was written once, by run `20261024T041904Z` on the data machine, offline from the session's probe copies.

## Vintage and revision

January 1993 to August 2026 (`ts_utc`), 404 months. The workbooks were retrieved by session 2258's probe from 2026-10-24T04:17:06Z (privsatime) to 04:17:38Z (pubtime), and each row's `retrieved_at` is its workbook's time as the probe's manifest records it. Their Last-Modified times are the rows' `vintage`: 2026-10-01T14:00:31Z to 15:28:41Z, the release of 1 October 2026 (the workbooks' source line names it). `coverage.csv` gives the same 88,376 rows, 110 nodes and the same first and last `ts_utc`.

The Census Bureau revises recent months at each release, at the same addresses. Each run writes the whole table again (`ip.write_snapshot`), and the four workbooks are asked again unless `--offline`. The release's marks are kept in `x_status`: p (preliminary) on August 2026 (220 rows), r (revised) on June and July 2026 (440 rows), blank on the rest.

## Shape and variables

Series, 82,760 rows since session 2261 (88,376 as first written, the 5,616 placeholder zeros since left out), 110 entities, 2 variables, 220 series.

- `entity` `census_c30:<owner>:<type>`: owner `private` (67 types, from privsatime and privtime), `public` (15), `state_local` (15) or `federal` (13), from the column's own words; type the column's name as a slug, its footnote figure dropped. The private total is `census_c30:private:total_private_construction`; the public, state and local, and federal totals are `census_c30:<owner>:total`.
- `variable` `value_put_in_place` (not seasonally adjusted, the month's spending) or `value_put_in_place_saar` (seasonally adjusted, at an annual rate). Each of the 110 columns is given both ways.
- `unit` USD, the Census Bureau's millions of dollars times 1,000,000 (every value a whole number of millions); `freq` P1M; `ts_utc` the month's first day at 00:00 UTC; `geo` US; `market` empty; `node` and `x_column` the column as the Census Bureau names it ("Data center", "Power (inc. Gas and Oil)", "Federal Power").

Rows by owner: private 53,632, public 12,120, state and local 12,120, federal 10,504. Every series holds 404 months except data centers (`census_c30:private:data_center`, from January 2014: 152 months a variable). The energy and data center lines are `private:data_center`, `private:power_inc_gas_and_oil`, `private:electric`, `public:power`, `state_local:power` and `federal:power`.

No value is negative; no series is all zero or constant. 5,625 values are zero:

- 5,616 are the Census Bureau's 0 for a breakdown it does not have: every month from January 1993 to December 2001 (108 months), both variables, in the 14 public types and the 12 federal types. The public workbooks' notes say "Detailed types of construction not available prior to 2002." In those months the public and federal totals hold figures, and so do the 14 state and local types.
- 9 are mini-storage's (`private:mini_storage`): seven unadjusted months (March to June 1993, January to March 1994) and two adjusted ones, as the workbook prints them.

No (entity, variable, ts_utc) is given twice. The counts were computed in session 2261 from the rows, read past the 10 header lines with pandas (every column as text).

## Checks the connector makes

- Before any request, the connector and www.census.gov are checked against `warehouse/metadata/paused_sources.csv`; a paused publisher stops the run with no request. It is not paused.
- Each workbook must open on its title and state "Millions of dollars", and carry a Date column. A public column whose owner is not in the map, a column name given twice, a month given twice, a figure that does not read, a workbook with no figure, or a key (entity, variable, month) given twice stops the run.
- A month is a row whose date reads as Mon-YY with an optional p or r. The first row under the header that is not a month and is not empty ends the sheet: that is how the notes under the months are left out. A blank cell has no row and is counted (privsatime 252, privtime 252: the data center column before 2014). Nothing is filled.
- Ceiling: four requests, a pause of 1 second after each, timeout 120 seconds; each asked again unless `--offline`.

## The cross-check

Session 2258 set each whole year's unadjusted months, summed, beside the mean of its seasonally adjusted annual rates in `runs/c102/s2258/cross.py` (on the data machine, not in git), reading the trial copy of the table (the same rows as the table):

| Series | Years | Lowest ratio | Highest ratio |
|---|---|---|---|
| private:total_private_construction | 33 | 0.9965 | 1.0031 |
| private:data_center | 12 | 0.9993 | 1.0068 |
| private:power_inc_gas_and_oil | 33 | 0.9875 | 1.0294 |
| private:electric | 33 | 0.9844 | 1.0336 |
| public:power | 24 | 0.9937 | 1.0086 |

public:power compares 24 years, not 33, because its months before 2002 are the zeros above. Private residential plus nonresidential equals the private total within 1.0 million USD in every unadjusted month.

The years, unadjusted, in billions of USD:

| Year | Private total | Data center | Power (inc. gas and oil) | Electric | Public power |
|---|---|---|---|---|---|
| 2014 | 739.2 | 1.8 | 98.2 | 70.0 | 11.9 |
| 2015 | 838.3 | 2.7 | 91.5 | 67.1 | 11.9 |
| 2016 | 916.2 | 4.1 | 91.7 | 71.4 | 9.8 |
| 2017 | 983.3 | 4.7 | 89.8 | 65.1 | 6.2 |
| 2018 | 1,023.0 | 6.9 | 94.4 | 70.4 | 5.2 |
| 2019 | 1,046.7 | 8.5 | 110.4 | 78.7 | 7.5 |
| 2020 | 1,130.4 | 9.2 | 110.6 | 88.5 | 7.6 |
| 2021 | 1,295.8 | 9.9 | 110.5 | 89.1 | 8.6 |
| 2022 | 1,519.2 | 12.6 | 111.1 | 91.0 | 10.5 |
| 2023 | 1,620.2 | 20.0 | 134.2 | 109.8 | 16.9 |
| 2024 | 1,730.8 | 34.8 | 146.7 | 123.0 | 21.0 |
| 2025 | 1,707.2 | 49.7 | 152.0 | 128.0 | 20.2 |

## License

The header: "License: public (a work of the U.S. government; see license_verdicts.csv). Source: U.S. Census Bureau, Construction Spending." `license_verdicts.csv` gives the Census Bureau "may be public", the same if the ERW sells anything (read 17, the terms of the Bureau's API): "You may not use the Census Bureau name, or the like to imply endorsement of any product, service, or entity". The verdict's note says the files the ERW reads are plain downloads, which no page read restricts. `docs/licenses.md` and `coverage.csv`: public.

## Found while writing this note

- The docstring says "A blank cell has no row", and the header counts only blank cells. The 5,616 zeros of the public and federal types from 1993 to 2001 are not spending of nothing: the Census Bureau has no breakdown before 2002 and prints 0. They are kept as rows of value 0, so a sum or mean of these series over the 1990s reads as no construction. Read those types from January 2002.
- Session 2258's report says the unadjusted years agree with the adjusted rates "within 1 to 3 percent for power and electric". Its cross-check gives electric up to 1.0336, 3.4 percent.
- The docstring says each workbook must carry "the months as Mon-YY". The code does not stop on a row that is not: any such row ends the sheet, wherever it stands. The months run newest first, so a month written in another form would end the table there, and every older month would be left out without a word. This run holds all 404 months from January 1993 in every series but data centers, so no month was cut.
- The private total's entity keeps the column's words (`total_private_construction`), while the three public totals are `total`; the same kind of line has two forms of name.

Acted on in session 2261: the public detailed types' placeholder zeros before 2002 (5,616 rows) have no row and are counted in the header; a row among the months that is not a month stops the run; the docstring names the totals' entities; session 2258's report is corrected (3.4 percent). The table was written again (82,760 rows); the append-only archive keeps the earlier rows.

## What it does not hold

- The private power detail (`privatepower.xlsx`), which answered HTTP 500.
- The state and regional tables (annual), and the Census Bureau's other construction series (starts, permits, prices).
- Months before January 1993, data centers before January 2014, and the public and federal types' breakdown before 2002 (zero in the table, as above).
