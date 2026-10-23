# Managed money positions in four NYMEX energy futures, a week (CFTC's Commitments of Traders)

Energy Research Warehouse (ERW), method note written in session 2046 (chain 059) for a table first written on 6 October 2026 (session 134).

Tables: `cftc_cot_positions`

## Publisher and address

Commodity Futures Trading Commission (CFTC), Commitments of Traders, Disaggregated report, futures only (`https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm`), read from the CFTC's public reporting service `https://publicreporting.cftc.gov/resource/72hh-3qpy.json`: one request a contract, `cftc_contract_market_code=<code>`, `$where=report_date_as_yyyy_mm_dd >= '2015-01-01T00:00:00'`, ordered by date, `$limit=5000`. Source id `cftc:disaggregated_cot_futures`. Connector: `warehouse/connectors/cftc_cot.py` (session 134).

ICE Futures Europe's Brent, the contract most of the market trades, is not here: ICE's terms forbid copying and systematic retrieval of its site (the connector's docstring, read 6 October 2026). The Brent entity is NYMEX's Brent Last Day contract, a far smaller market.

## Vintage and revision

6 January 2015 to 6 October 2026 in the file on the data machine, read by run `20261010T145853Z` (10 October 2026) and restored from the Redivis draft by `scripts/sync.py`, as its header says. Header: "Rows read: 2,456 weeks of four contracts. Weeks with a blank managed money position, not written: 0."

Each run reads every week from 2015, deletes the file and writes the table again, so the CFTC's corrections are taken. A table whose newest report is more than 21 days old is not written.

## Shape and variables

Series, 9,824 rows: 4 contracts, 4 variables, 614 weeks each (16 series of 614 rows). `entity` `cftc:<contract market code>`; `unit` count (contracts); `ts_utc` the report's as-of date at 00:00:00Z; `freq` P1W; `geo` US; `market` nymex; `node` the CFTC's market name as given that week; `vintage` empty.

| Entity | Contract | `node` (the CFTC's names) |
|---|---|---|
| cftc:067651 | WTI crude oil | CRUDE OIL, LIGHT SWEET to 1 February 2022, then WTI-PHYSICAL |
| cftc:06765T | Brent Last Day | BRENT CRUDE OIL LAST DAY, then BRENT LAST DAY |
| cftc:023651 | Henry Hub natural gas | NATURAL GAS, then NAT GAS NYME |
| cftc:111659 | RBOB gasoline | GASOLINE BLENDSTOCK (RBOB), written two ways before 1 February 2022, then GASOLINE RBOB |

Variables: `managed_money_long`, `managed_money_short` and `open_interest` are the CFTC's figures (`m_money_positions_long_all`, `m_money_positions_short_all`, `open_interest_all`); `managed_money_net` is long less short, the one figure computed here. Of the 614 dates, 608 are Tuesdays and 6 are Mondays (3 July 2017, 24 and 31 December 2018, 21 December 2020, 3 July 2023, 10 November 2025), the as-of date the CFTC gives for those weeks. On 6 October 2026 managed money held 178,353 long and 124,755 short in WTI (open interest 1,889,422), and was net short 144,537 in Henry Hub.

## Reading the source

- A row for a contract other than the one asked for stops the run; a table without all four contracts stops it.
- A week with a blank managed money long or short is not written and is counted (none here); a blank open interest leaves that one variable out. A value that is not a number stops the run.
- One request of up to 5,000 rows a contract; the connector does not page (614 weeks here). A request is tried up to four times, with a one-second pause after each answer.
- The docstring names session 134's ceiling of 1,200,000 rows for its pulls in all; the code counts no ceiling of its own.

## License

`license_verdicts.csv` records the CFTC, read 11: "may be public", for public and for commercial use. The sentence: "Government information at the CFTC website is in the public domain. Public domain information may be freely distributed and copied, but it is requested that in any subsequent use the CFTC be given appropriate acknowledgement." `license_tables.csv` lists the table under the CFTC.

## Cross-checks (session 2046)

- The counts above were computed from the rows, read past the header lines: 2,456 contract weeks times 4 variables is the 9,824 rows; no (entity, variable, ts_utc) is given twice.
- `managed_money_net` equals long less short in all 2,456 contract weeks (largest difference 0). Long plus short never exceeds open interest: at most 64.2 percent of it.
- The 614 dates are 7 days apart but for five pairs of 6 and 8 days around the Monday reports: no week is missing.

## What it does not hold

- ICE Brent and ICE's own report; options and the combined futures and options report.
- The report's other trader groups (producers, swap dealers, other reportables) and its spreading and change columns.
- Weeks before 2015, and any contract but the four.
