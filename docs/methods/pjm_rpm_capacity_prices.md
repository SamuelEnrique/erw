# PJM's capacity auction clearing prices by locational deliverability area, a delivery year, 2007/08 to 2028/29 (RPM Base Residual Auction), internal

Energy Research Warehouse (ERW), method note written in session 2222 (chain 098) for a table first written on 25 September 2026 (session 7, run `20260925T235822Z`, `archive/sessions/SESSION_7_REPORT.md`). The same prices, with the other grids' capacity auctions, are in `iso_all_capacity_prices` (`docs/methods/capacity_and_ancillary.md`).

Tables: `pjm_rpm_capacity_prices`

## Publisher and address

PJM Interconnection, "RPM Resource Clearing Prices for all RPM Auctions held to date", a workbook linked from `https://www.pjm.com/markets-and-operations/rpm`: `https://www.pjm.com/-/media/DotCom/markets-ops/rpm/rpm-auction-info/rpm-auctions-resource-clearing-price-summary.xlsx`. Source id `pjm:rpm-clearing-price-summary`. Raw files under `warehouse/raw/capacity_prices/<run_id>/`.

Connector: `warehouse/connectors/capacity_prices.py` (session 7), no arguments. One request (with retries). The layout is checked: one "Capacity Product Type" header row, RTO as the first LDA column, "DY yy/yy" block labels, and every Base Residual Auction (BRA) row's product must be known. One price an LDA and delivery year, the headline product: the single product to 2013/14, "Annual" 2014/15 to 2017/18, "CP" (Capacity Performance) from 2018/19; Extended Summer, Limited and Base products are skipped; a cell "**" (PJM: "LDA was not modeled") is no row. A workbook whose newest delivery year starts before the current year fails the run as stale.

Schedule: the daily run, `warehouse/run_daily.sh` (`pull capacity_prices`, every day, "Session 7 price board"), on the GitHub runner (`.github/workflows/daily-prices.yml`). `run_status.csv` records 27 runs from 20260925T235822Z (local) to 20261023T144516Z (github), all ok; `archive_manifest.csv` holds 234 rows as of run 20261023T152740Z-github. Not named in `warehouse/supabase/live_set.yaml`. Readers: `site/lib/siting.ts` and the chat's table list (`site/lib/chat/spec.json`).

## Vintage and revision

The copy here is of run `20261010T144332Z` (github), restored from the internal Redivis draft by `scripts/sync.py` (its last header line); `retrieved_at` 2026-10-10T14:43:33Z in every row. `vintage` is blank in every row (the same workbook's rows in `iso_all_capacity_prices` carry its Last-Modified, 2026-07-29T18:30:13Z). Each run writes the whole table again from the workbook as it stands ("234 new, 0 replacing"); a later auction adds a delivery year.

## Shape and variables

Series, 234 rows: 18 LDAs over 22 delivery years. `entity` `pjm:<LDA as PJM names it>`, `node` the LDA, `variable` `capacity_price_usd_per_mw_day`, `unit` USD/MW-day, `freq` P1Y, `geo` US, `market` bra.

- LDAs and their rows: RTO 22, SWMAAC 20, EMAAC 19, DPL SOUTH 18, MAAC 17, PS NORTH 17, PEPCO 16, PS 16, ATSI 14, ATSI-CLEVELAND 13, BGE 12, COMED 12, PL 12, DAYTON 9, DEOK 9, DOM 4, JCPL 3, MAAC + APS 1 (2009/10 only).
- Rows a delivery year: 3 (2007/08 to 2009/10), 2 (2010/11), 1 (2011/12, RTO only), then 6 to 17, and 17 in each of 2026/27 to 2028/29.

RTO, USD/MW-day:

| Delivery year | RTO | Delivery year | RTO |
|---|---|---|---|
| 2007/08 | 40.80 | 2018/19 | 164.77 |
| 2008/09 | 111.92 | 2019/20 | 100.00 |
| 2009/10 | 102.04 | 2020/21 | 76.53 |
| 2010/11 | 174.29 | 2021/22 | 140.00 |
| 2011/12 | 110.00 | 2022/23 | 50.00 |
| 2012/13 | 16.46 | 2023/24 | 34.13 |
| 2013/14 | 27.73 | 2024/25 | 28.92 |
| 2014/15 | 125.99 | 2025/26 | 269.92 |
| 2015/16 | 136.00 | 2026/27 | 329.17 |
| 2016/17 | 59.37 | 2027/28 | 333.44 |
| 2017/18 | 120.00 | 2028/29 | 325.00 |

Lowest 16.46 (RTO, 2012/13), highest 466.35 (BGE, 2025/26); no zero or negative price; every value to two decimals. In 2026/27 to 2028/29 every LDA listed clears at the RTO price; in 2024/25 the highest LDA is 397.25 above it.

## Placing values in time, and what is filled

`ts_utc` is the delivery year's first day, 1 June at 00:00:00Z. One BRA price a delivery year: incremental auctions are not included. An LDA PJM did not model in a year has no row, and nothing is filled from its parent LDA; an LDA the workbook does not list in a year has no row either. Which product a row prices (single, Annual or CP) follows from its year; no column says it.

## License

Header: "License: internal. PJM data terms bar non-members from republishing." `license_verdicts.csv`, PJM (read 15): "Permitted Use. Subject to Section 2 below, you may use the Data and the Tools for your internal business use or commercial purposes, including publishing and making derivatives of the Data, Members may republish data, however non-members are specifically prohibited from republishing data.", verdict "needs a paid license". `docs/licenses.md`: "needs a paid license", decided by PJM, flag internal, "agrees", ERW verdict internal; the price "not stated on the page (membership of PJM ...)".

## Checks (session 2222)

The figures in this note were computed from the rows of `warehouse/output/pjm_rpm_capacity_prices.csv`, read past its 9 header lines (script `runs/c098/s2222/check_pjm.py`).

- 234 rows, `ts_utc` 2007-06-01T00:00:00Z to 2028-06-01T00:00:00Z, as the header states; every `ts_utc` a 1 June; no (entity, variable, ts_utc) twice; `entity` is `pjm:` plus `node` in every row.
- Against `iso_all_capacity_prices` (market `pjm_bra`, 234 rows, retrieved 2026-10-02T19:48:35Z): every (entity, delivery year) is in both, and all 234 prices agree to the cent.

## Where the description and the data disagree

1. **"ISO-NE FCA and MISO PRA prices ... are not collected."** The docstring says so (session 7); since session 65 the ERW holds them in `iso_all_capacity_prices` (isone_fca 26 rows, miso_pra 130), beside NYISO's ICAP spot prices (424).
2. **"Other ISOs would get their own tables with the same variable."** They did not: the other grids, and PJM's same 234 prices again, are in one table, `iso_all_capacity_prices`, whose variable is `capacity_price` (market `pjm_bra`), not this table's `capacity_price_usd_per_mw_day` (market `bra`). A join of the two tables by variable or market finds nothing.

Acted on in session 2222: the connector's docstring (`capacity_prices.py`) now says that `iso_all_capacity_prices` holds ISO-NE's and MISO's prices since, and PJM's 234 under its own variable and market names, so a join of the two tables on either finds nothing. The rows are unchanged.

## The session report against the table

Every figure of `SESSION_7_REPORT.md` about this table holds: "BRA clearing price, 18 LDAs, delivery years 2007/08 to 2028/29 | P1Y | 2007-06-01 to 2028-06-01 | USD/MW-day | internal", and "PJM RTO: 2007/08 $40.80 and 2028/29 $325.00".

## What it does not hold

- Incremental auctions; the Extended Summer, Limited and Base products; cleared MW, offers or the auction's other results; LDAs PJM did not model in a year; the product name of a row.
