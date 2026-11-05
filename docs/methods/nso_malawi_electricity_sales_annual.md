# Malawi's electricity sales by type of user, a year (NSO's Statistical Year Book 2023, table 10.1)

Energy Research Warehouse (ERW), method note written in session 2499 (chain 121) for a table first written on 24 October 2026 (session 2493).

Tables: `nso_malawi_electricity_sales_annual`

## Publisher and address

The National Statistical Office of Malawi (NSO), its Statistical Year Book 2023, table "10.1 Number of Electricity Consumers and Units Sold by Type of User, 1992-2019" (source: ESCOM, the Electricity Supply Corporation of Malawi): `https://cms.nsomalawi.mw/api/download/230/Statistical_Year_Book_2023.pdf`. One GET, no key. Source id `nso_malawi:statistical_yearbook`. Connector: `warehouse/connectors/nso_malawi_electricity.py` (session 2493). cms.nsomalawi.mw and www.nsomalawi.mw answer HTTP 404 for a robots file (reads 833, 835).

EGENCO's www.egenco.mw failed certificate verification at its robots file (read 832), and the regulator MERA's site search found no statistics (reads 836, 837). The year book is the public source of ESCOM's figures that the session found.

## Vintage and revision

1992 to 2019, written by run `20261024T162927Z` (the write under the lock, offline), which read the year book saved at 2026-10-24T15:04:17Z. `vintage` is its last-modified time, 2024-08-06T09:07:07Z. The 2023 edition's table ends in 2019.

## Shape and variables

Series, 140 rows, 5 entities: `nso:mw:<class>` (total, power, general, domestic, exports), `variable` `sales`, `unit` MWh (the table's millions of kWh times 1,000), `ts_utc` the year's 1 January, `freq` P1Y, `geo` MW, `node` and `x_label` the column as NSO labels it.

| GWh | 1992 | 2000 | 2010 | 2017 | 2019 |
|---|---|---|---|---|---|
| Total | 675.8 | 942.7 | 1,420.9 | 1,455.6 | 1,633.0 |
| Domestic | 134.9 | 315.0 | 581.5 | 744.2 | 572.3 |

## Reading the source

- The run stops at once, asking nothing, while `nso_malawi_yearbook` or cms.nsomalawi.mw is paused.
- One request a run (timeout 180 seconds); `--offline` reads the saved year book.
- **Finding the table:** the one page that names table 10.1 and holds the "Kwh" headings.
- **Reading the figures:** by their position. Each quantity column is the span of its "Kwh" heading widened by 10 points a side; a figure's digit groups (thousands written with spaces, as "1 598.4") are joined within that span. The value columns between them (Malawi kwacha, millions) fall outside the spans and are not read.
- **Cells without a row:** "..." (none in the quantity columns); a figure out of form (none).
- **Written as printed, and listed in the header:** the years whose four classes do not sum to the total within 1 GWh: 2003, 2009, 2010 and 2018. In 2010 the power column repeats the total (1,420.9).
- The run stops, and no file is written, for: the table not found once, no row of the five "Kwh" headings, years not 1992 to 2019 in order, a key given twice.

Nothing is filled. Not taken: the consumers' numbers, the values (MWK).

## License

Internal. NSO's home page (read 838): "Copyright © 2026 National Statistical Office of Malawi. All Rights Reserved"; the year book states no terms of reuse. Verdict (session 2495): needs written permission. Held from the Redivis storage and the live set.

## Cross-checks (session 2493)

- Total sales over `owid_ember_electricity_annual`'s demand for Malawi: 0.70 to 0.79 in 2000 to 2011 and 2013, 2016 to 2018; 0.92 in 2019.
- **Years that do not fit their neighbours, as printed:** 1998's total (1,598.4 GWh) is about twice 1997's and 1999's; 2014 and 2015 (722.0 and 768.0 GWh, 0.34 and 0.36 of Ember's demand) are about half 2013's and 2016's, as if half a year; 2012 is 0.59. The table gives no note on any of them. A user should not read a trend from those years.

## What it does not hold

- Years after 2019; generation (the table is sales); monthly figures; prices (MWK).
