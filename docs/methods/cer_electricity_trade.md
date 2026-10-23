# Canada's electricity trade with the U.S. (Canada Energy Regulator)

Energy Research Warehouse (ERW), method note written in session 891 (chain 048) for tables first written on 23 October 2026.

Tables: `cer_electricity_trade`

## Publisher and address

Canada Energy Regulator (CER), Electricity Trade Summary workbook, compiled from the CER's monthly Commodity Statistics
reports, linked from the page
`https://www.cer-rec.gc.ca/en/data-analysis/energy-commodities/electricity/statistics/electricity-trade-summary/`.
Workbook when written:
`https://www.cer-rec.gc.ca/en/data-analysis/energy-commodities/electricity/statistics/electricity-trade-summary/electricity-trades-summary-resume-echanges-commerciaux-electricite.xlsx`.
Connector: `warehouse/connectors/cer_electricity_trade.py` (session 887).

## Vintage and revision

Monthly rows January 2010 to July 2026, province rows 2010 to 2025, when written (run `20261023T050405Z`; the workbook
retrieved 2026-10-23T05:02:35Z, updated by the CER 25 September 2026). A snapshot: each run replaces the table whole. A
run asks for the page and the workbook again (ceiling: two requests); `--offline` reads the ones saved in
`warehouse/raw/cer_electricity_trade/`. Session 887 made 10 requests of its 20: the CER's robots file, the trade page, a
terms address that answered with a page saying "not found", the terms page, open.canada.ca's robots file, one search of
its catalogue, a second search that timed out and was not asked again, the workbook, then the connector's page and
workbook. The CER notes that the latest figures, with revisions, are in its Commodity Tracking System; this table holds
the workbook as published.

## Shape and variables

Series. `entity` `cer_trade:CA` (Canada with the U.S., a month) or `cer_trade:<province>:<destination>` (a province's
exports to a U.S. state, a year). The province is its ISO 3166-2 code without `CA-` (`QC`), the state its postal code.
Where the CER names a market or two states, as the exporter reports them, the destination is kept as named: `MN_ND`
(Minnesota and North Dakota), `ISONE` (ISO New England) or `PJM`. `ts_utc` the month's or the year's first day,
00:00:00Z; `freq` `P1M` or `P1Y`; `geo` `CA` or `CA-<province>`; `node` in words ("Canada, electricity exports with the
U.S.", or "<province> to <destination>" as the CER names them, such as "Manitoba to Minn / N. Dakota").

| Variable | Unit | What it is |
|---|---|---|
| `exports` | `MWh` | Canada's exports to the U.S. in the month (`cer_trade:CA`), or a province's exports to a destination in the year; the CER's MW.h |
| `imports` | `MWh` | Canada's imports from the U.S. in the month (`cer_trade:CA` only); the CER's MW.h |

When written: 1,136 rows, 93 series. Monthly: 199 months of exports and of imports, 398 rows. Province rows: 738, 92
province and destination pairs, from 10 provinces and territories (AB, BC, MB, NB, NL, NS, NU, ON, QC, SK) to 40
destinations (37 states, `MN_ND`, `ISONE` and `PJM`). 34 province rows are zero, as the CER gives them. One row is
Nunavut to Michigan, 2,100 MWh in 2025, as the CER gives it.

Exports: 68.26 TWh in 2015, 35.64 in 2024, 31.64 in 2025. The largest flows of 2025: Ontario to New York (7.77 TWh),
Manitoba to Minnesota and North Dakota (3.46), Ontario to Michigan (3.30), British Columbia to Washington (3.11) and
Quebec to Vermont (3.03).

## Reading the workbook

- The page must link exactly one trade workbook (`.xlsx`), or the run stops. A file that is not a workbook stops it too.
- Sheet "Fig. 1(m), Fig. 3(m)", the months: the columns are found by their headings ("Date", and the exports and imports
  headings ending "(MW.h)"), not by position. Headings not as read stop the run.
- Sheet "Fig. 2", the provinces: the columns "Date", "Volume (MW.h)", "Province (Eng. / Ang.)" and "Destination (Eng. /
  Ang.)" are found by heading.
- Province rows hold complete years only. The last complete year is the last month's year if that month is December, the
  year before otherwise. The workbook's 2026 province rows, January to July, are left out and named in the header; the
  monthly rows hold 2026.
- A province or destination not in the map stops the run; so does an (entity, variable, ts_utc) given twice.
- A cell the CER leaves empty has no row. Nothing is filled.
- The workbook's export and import values and its weighted average prices are in Canadian dollars, a unit the data
  standard does not have, and are not taken. No exchange rate is applied.

## License

The CER's Terms and conditions, Ownership and Usage of Content (read 96 of `license_reads.csv`,
`https://www.cer-rec.gc.ca/en/terms-conditions.html`, 2026-10-23T04:58:15Z): "Unless otherwise specified you may
reproduce the materials in whole or in part for non-commercial purposes, and in any format, without charge or further
permission, provided you do the following: [...] Unless otherwise specified, you may not reproduce materials on this site,
in whole or in part, for the purposes of commercial redistribution without prior written permission from the Canada
Energy Regulator's copyright administrator." Non-commercial reproduction asks for the title, the author and a statement
that the copy is not produced in affiliation with or with the endorsement of the CER, which the table's header carries.
Verdict in `license_verdicts.csv`: may be public; needs written permission if the ERW sells anything (contact: Canada
Energy Regulator Library, info@cer-rec.gc.ca, 403-299-3561). The table is flagged public, like SPP's tables with the same
kind of terms. The CER's robots file (read 95) disallows `/fracfocus` and `/bin` for every agent; the trade page and
workbook are allowed. The same agency's datasets on open.canada.ca carry the Open Government Licence - Canada; this
workbook was not found there (one search read, a second timed out and was not asked again).

## Cross-check (session 887)

- The months summed equal the workbook's own annual sheet in 17 of 17 years, for both exports and imports.
- The provinces summed equal the annual exports in 16 of 16 complete years.
- EIA's international exports for Canada (`eia_international_electricity_annual`) equal the CER's to the hundredth of a
  TWh in every year compared except 2020 (EIA 67.42, CER 67.76). EIA takes Canada's figures from the CER.

## What it does not hold

- The workbook's values and weighted average prices in Canadian dollars (a `CAD` unit is left for Samuel's ruling).
- The 2026 province rows, January to July (a part of a year); the monthly rows hold 2026.
- Imports by province: the province rows hold exports only, as the CER's figure gives them.
- Months before January 2010.
- The CER's later revisions in its Commodity Tracking System: the table holds the workbook as published.
