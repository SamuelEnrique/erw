# Oman's electricity by governorate and by source, a year (NCSI's Energy Statistics 2026, tables 11 and 12)

Energy Research Warehouse (ERW), method note written in session 2513 (chain 122) for a table first written on 24 October 2026 (session 2504).

Tables: `ncsi_oman_electricity_annual`

## Publisher and address

The National Centre for Statistics and Information of the Sultanate of Oman (NCSI), its "Energy Statistics 2026, Fifth Edition - data 2025" (53 pages), tables 11 and 12, from the Public Services Regulatory Authority's figures: `https://api.ncsi.gov.om/uploads/pdfs/energy_statistics_bulletin_2026_1783504139.pdf`. One GET, no key. Source id `ncsi:energy_statistics`. Connector: `warehouse/connectors/ncsi_oman_electricity.py` (session 2504). api.ncsi.gov.om and www.ncsi.gov.om have no robots file (reads 871, 872).

The session was planned for Kuwait: its ministry's server fails the TLS handshake (read 867), and its statistics bureau's publications sit behind Arabic form postbacks (reads 868 to 870).

## Vintage and revision

2023 to 2025, written by run `20261024T181930Z` (the write under the lock, offline), which read the bulletin saved at 2026-10-24T17:36:17Z (`retrieved_at`). `vintage` is its last-modified time, 2026-07-08T09:48:59Z. Each year's edition has its own address.

## Shape and variables

Series, 126 rows. `entity` `ncsi:om:<item>`; `ts_utc` the year's 1 January; `freq` P1Y; `geo` OM; `node` and `x_label` NCSI's row and column; `x_table` the bulletin's table.

| Table | `variable` | Items | Unit |
|---|---|---|---|
| 11, by governorate | `production`, `distribution` | the eleven governorates, `others` (production only), `total` | MWh (NCSI's GWh times 1,000) |
| 11 | `connections` | the same | count (NCSI's thousands times 1,000) |
| 12, by source | `production_by_source` | diesel, gas, solar, wind, other, total | MWh (NCSI's TWh, one decimal, times 1,000,000) |

| | 2023 | 2024 | 2025 |
|---|---|---|---|
| Production, TWh | 44.97 | 49.13 | 50.97 |
| Distribution, TWh | 39.30 | 42.16 | 45.03 |
| Connections, thousands | 1,449.4 | 1,497.7 | 1,544.0 |
| Solar, TWh (table 12) | 2.1 | 2.3 | 4.4 |

## Reading the source

- The run stops at once, asking nothing, while `ncsi_oman_energy`, api.ncsi.gov.om or www.ncsi.gov.om is paused.
- One request a run (timeout 300 seconds; the 8 MB file took over two minutes in session 2504); `--offline` reads the saved bulletin.
- **Table 11:** the page that names its title and holds its rows. A row is a line with a governorate's English name (the name may fall on the line of figures after an Arabic line, as Ash Sharqiyah's) and nine figures, the three years' connections, distribution and production, 2025 first. The bulletin prints the table twice (pages 46 and 47); the second print must equal the first.
- **Table 12:** the lines after its title that begin with a source and three figures; the title line itself, which begins "Total", is not a row (session 2504's first parse took it for one).
- **Checks that stop the run:** each year's table 11 production total against table 12's within 0.1 TWh (this also proves the columns' order); a table not found, a row of another width, a governorate or source given twice.
- **Cells without a row:** "-" (Al Buraimi's production, none).
- The governorates' production less the total: -0.1, 0.0 and 0.0 GWh (2025, 2024, 2023), in the header.

Nothing is filled. Not taken: table 13 (renewable stations, TWh to one decimal), the water, waste water and oil and gas tables.

## License

Public. NCSI's home page (read 873): "The contents of this website are licensed under the Open Government Licence" of the Sultanate of Oman. The licence (read 874, in Arabic) allows use, reuse and redistribution for commercial and non-commercial purposes with the source named, and states its compatibility with CC BY 4.0. Verdict (session 2504): may be public. The header carries the citation. Held from the live set; in the next Stanford draft.

## Cross-checks (session 2504)

- Production over `owid_ember_electricity_annual`'s demand for Oman: 1.00 (2023), 1.00 (2024), 0.965 (2025).
- **As printed:** Al Batinah North's and South's distribution in 2023 (9,343.8 and 4,491.6 GWh) look swapped against 2024 (4,837.3 and 10,291.5) and 2025 (4,985.7 and 11,428.0). Ad Dakhliyah's production rises from 6.7 GWh (2023) to 200.0 (2024) and 2,865.4 (2025), with the new solar plants.

## What it does not hold

- Years before 2023 (earlier editions); monthly figures; the stations' production (table 13 gives the renewable ones to one decimal of a TWh); prices (OMR).
