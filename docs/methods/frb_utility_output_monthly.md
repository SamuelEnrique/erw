# Output and capacity utilization of electric and gas utilities, a month (Federal Reserve G.17)

Energy Research Warehouse (ERW), method note written in session 891 (chain 048) for tables first written on 23 October 2026.

Tables: `frb_utility_output_monthly`

## Publisher and address

Board of Governors of the Federal Reserve System, G.17 release, Industrial Production and Capacity Utilization, page
`https://www.federalreserve.gov/releases/g17/`, its whole-release text files, seasonally adjusted:
`https://www.federalreserve.gov/releases/g17/ipdisk/ip_sa.txt` (industrial production) and
`https://www.federalreserve.gov/releases/g17/ipdisk/utl_sa.txt` (capacity utilization). The host has no robots file
(HTTP 404, session 889). Connector: `warehouse/connectors/frb_utility_output.py` (session 889).

## Vintage and revision

Monthly, to September 2026 when written (run `20261023T051558Z`; both files retrieved 2026-10-23T05:15:17Z). Each
release revises earlier months: the table is a snapshot of the release read, and each run replaces it whole. A run asks
for both files again (ceiling: two requests); `--offline` reads the ones saved in `warehouse/raw/frb_utility_output/`.
Session 889 made 10 requests of its 20: five to the Census Bureau, five to the Federal Reserve.

The series end at different months: the aggregates (`G2211A2`, `G2211`, `G22111`, `G22112`, `G2212`, `G221111A4T8`,
`B50001`, `B50089`) and every utilization series in September 2026, the detailed `N` series in July 2026. They begin
at different months too: all industrial production in January 1919, electric and gas utilities in January 1939, most
utility series in January 1972, fossil fuel and renewables generation in January 2001, every utilization series in
January 1967.

## Shape and variables

Series. `entity` `frb_g17:<G.17 series code>`. `ts_utc` the month's first day, 00:00:00Z; `freq` `P1M`; `geo` `US`;
`node` the series' title as the file gives it (such as "Electric power generation NAICS=22111"). Seasonally adjusted.

| Variable | Unit | What it is |
|---|---|---|
| `production` | `index` | industrial production, an index on the G.17 release's base, 2017 = 100 |
| `utilization` | `pct` | capacity utilization, percent of capacity |

The unit `index` is Decision 53 (session 889), an index number on its source's base period, added to the validator and
the data standard together. An index is never summed.

The series (19), with the variables each holds:

| Code | Title in the file | Variables |
|---|---|---|
| `G2211A2` | Electric and gas utilities NAICS=2211,2 | production, utilization |
| `G2211` | Electric power generation, transmission, and distribution NAICS=2211 | production, utilization |
| `G22111` | Electric power generation NAICS=22111 | production |
| `N221112` | Fossil Fuel electric power generation NAICS=221112 | production |
| `N221113` | Nuclear electric power generation NAICS=221113 | production |
| `N221111` | Hydroelectric power generation NAICS=221111 | production |
| `N221114T8` | Renewables and other electric power generation NAICS=221114-8 | production |
| `G221111A4T8` | Hydroelectric, renewables, and other NAICS=221111,4-8 | production |
| `G22112` | Electric power transmission, control, and distribution NAICS=22112 | production |
| `N22112R` | Residential electricity sales NAICS=22112pt. | production |
| `N22112C` | Commercial and other electricity sales NAICS=22112pt. | production |
| `N22112M` | Industrial electricity sales NAICS=22112pt. | production |
| `G2212` | Natural gas distribution NAICS=2212 | production, utilization |
| `N2212R` | Residential gas sales NAICS=2212pt. | production |
| `N2212C` | Commercial and other gas sales NAICS=2212pt. | production |
| `N2212M` | Industrial gas sales NAICS=2212pt. | production |
| `N2212T` | Gas transmission NAICS=2212pt. | production |
| `B50001` | Total index | production, utilization |
| `B50089` | Energy, total | production |

`B50001` (all industrial production) and `B50089` (energy, total) are taken for comparison. `G221111A4T8` is taken by
the same rule as the utilities' series; the first header's list of codes did not name it, and called `G2212`'s parts its
sales, though `N2212T` is gas transmission. Session 891 corrected the docstring and the header (which now also gives each
series' last month) and wrote the table again, the same rows. The series overlap
(generation holds its fuels, electric power holds generation and transmission and distribution).

When written: 15,365 rows, 19 series: production 12,497 rows, utilization 2,868.

## Reading the files

- Each file holds title lines (`"<code>: <title>"`) and data lines (`"<code>" <year>` and up to twelve values, January
  first). A line in neither form stops the run; so does a year with more than twelve values.
- Only the utilities' series (codes beginning `G221` or `N221`, NAICS 2211 and 2212) and `B50001` and `B50089` are
  taken.
- A month the file leaves empty has no row. Nothing is filled.
- An (entity, variable, ts_utc) given twice, within a file or in both, stops the run.
- The G.17 text files (the whole release) are read rather than the Board's data download, which needs a series package
  built on its pages.

## License

Public: "Unless otherwise indicated, information on Board's website is in the public domain and may be copied and
distributed without permission. Please cite to the Board as the source of the information." (the Board's disclaimer
page, `https://www.federalreserve.gov/disclaimer.htm`, read 41 of `license_reads.csv`, 13 October 2026, session 207, for
`frb_treasury_yields`). Verdict in `license_verdicts.csv`: may be public, and may be public if the ERW sells anything.
The Board's seals and logos are protected, and material marked as a non-Board source's is that source's. Cite the Board
as the source.

## Cross-check (session 889)

Against EIA's retail sales (`eia_retail_sales_monthly`), growth from 2017:

- Residential: 1.102 against 1.099 in 2025, 1.062 against 1.062 in 2020.
- Industrial: 1.066 against 1.059 in 2025.
- Commercial: apart. The Board's "commercial and other sales" grew 21.7 percent from 2017 to 2025, EIA's commercial
  sales 10.4 percent, so the Board's category is wider.
- The generation index (value added) runs below EIA's net generation in 2024 and 2025 (1.038 against 1.097 in 2025).
- Electric power's capacity utilization (`G2211`) was 73.0 percent in September 2026, against 77.5 in 2017.

## What it does not hold

- The G.17 release's other industries: only the utilities' series and the two totals are taken.
- The release's series not seasonally adjusted: only `ip_sa.txt` and `utl_sa.txt` are read.
- Capacity in physical units, or output in MWh: the table holds indexes and percents. EIA's retail sales are in
  `eia_retail_sales_monthly`.
- The Census Bureau's construction spending on power, tried first in session 889 and left: its release workbook holds
  only the latest months, and a table of a few months was not written.
- Earlier releases' figures: each run holds the release read.
