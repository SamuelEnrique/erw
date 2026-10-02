# Method: capacity prices and ancillary service prices

Energy Research Warehouse (ERW), session 65. Tables: `iso_all_capacity_prices` (series, internal), `ercot_as_prices` and `caiso_as_prices` (series, hourly, public). Code: `warehouse/connectors/iso_capacity_prices.py`, `ercot_as_prices.py`, `caiso_as_prices.py`. No page reads them yet: a later session wires them into the seller tab and the regional comparison.

**Why.** A hub's energy price is not the whole wholesale price of power. ERCOT pays for capacity through its energy price (scarcity pricing in an energy-only market). PJM, NYISO, ISO-NE and MISO pay for capacity apart, in auctions. Comparing regions on energy alone therefore flatters the markets with a capacity auction. A plant or battery also earns from ancillary services, which the merchant revenue tables leave out. These three tables hold the published prices; nothing in them is converted, estimated or filled.

## Capacity prices: `iso_all_capacity_prices`

One row per market, zone, delivery period and auction. `value` is the clearing price as published, `unit` its published unit, `ts_utc` the first day of the delivery period, `x_period_end` its last day, `x_auction` the auction as the publisher names it, `x_license` the row's own license. The partition column is `market`.

| `market` | Publisher and posting | Entity | Period (`freq`) | Unit | Held |
|---|---|---|---|---|---|
| `pjm_bra` | PJM, "RPM Resource Clearing Prices for all RPM Auctions held to date" (workbook) | `pjm:RTO` and each locational deliverability area PJM modeled | delivery year, June 1 to May 31 (`P1Y`) | USD/MW-day | Base Residual Auction, 2007/2008 to 2028/2029, 234 rows |
| `nyiso_icap_spot` | NYISO ICAP market, "View Spot Auction Summary" | `nyiso:NYCA`, `nyiso:G-J Locality`, `nyiso:NYC`, `nyiso:LI` | calendar month (`P1M`) | USD/kW-month | monthly spot auction, 2018-01 to 2026-10, 424 rows |
| `isone_fca` | ISO-NE, "Results of the Annual Forward Capacity Auctions" (Markets key statistics page) | `isone:System-wide`, or the zone as printed | commitment period, June 1 to May 31 (`P1Y`) | USD/kW-month | FCA 1 to FCA 18, 26 rows |
| `miso_pra` | MISO, Planning Resource Auction "Results Posting" (PDF), page "Results by Zone" | `miso:Z1` to `miso:Z10`, `miso:ERZ` (external zones) | season (`P3M`): summer June to August, fall September to November, winter December to February, spring March to May | USD/MW-day | planning years 2024/25, 2025/26 and 2026/27, 130 rows |

Session 65's run: 814 rows, against a ceiling of 5,000.

**Reading rules, per source.**
- **PJM.** The same workbook and parser as `pjm_rpm_capacity_prices` (session 7). The Base Residual Auction's headline price only. A cell PJM marks `**` (the area was not modeled apart that year) is no row.
- **NYISO.** One page per month. The price is the "Price ($/kW-M)" of each of the four localities, on an unforced capacity (UCAP) basis. The external control areas on the page (HQ, IESO, NE, PJM) are not kept. `vintage` is the page's Posted Date. A locality on the page without a price fails the month; a month whose page shows no auction is a gap.
- **ISO-NE.** The clearing price cell is read as printed. A price printed without a zone is the system-wide price. A zone printed with its own price is its own row, and no system-wide row is made up for that auction (FCA 15 and 16 print Rest of Pool, Northern New England and Southeast New England only). FCA 8 and 9 paid new and existing resources apart: variables `capacity_price_new` and `capacity_price_existing`. `x_note` carries "floor price" where the page says the auction cleared at the floor (FCA 1 to 7). A cell the grammar does not know fails the pull.
- **MISO.** Each price is matched to its zone by its position under the zone's column heading on the page. The external zones' cell is sometimes a range ("405.31 to 424.30"): then there is no ERZ row for that season (Fall 2025 and Summer 2026). The 2026/27 posting is the corrected one of 2026-05-22; MISO replaced the posting of 2026-04-28, whose link now answers HTTP 403. The corrected file was found in MISO's own document list, the one its resource adequacy page reads.

**Units and the conversion.** The table keeps two units and converts nothing (Decision 37). To compare them:

    USD/kW-month = USD/MW-day x 365 / 12 / 1000        (a year of 365 days; 30.4167 days per month)
    USD/MW-day   = USD/kW-month x 1000 x 12 / 365

For a stated period use its own days, not the average month: a MISO season's price times the season's days, a PJM delivery year's price times 365 (366 in a leap year). Example: PJM's 2025/2026 RTO price of USD 269.92/MW-day is USD 8.21/kW-month. For a size of capacity over a month: USD/kW-month x kW; USD/MW-day x MW x the days of the month.

**The prices are not on one basis.** PJM clears unforced capacity (UCAP), and from 2025/2026 accredits by marginal ELCC. NYISO's spot price is per kW of UCAP. ISO-NE clears qualified capacity. MISO clears zonal resource credits by season, accredited capacity, and since 2025/26 against a sloped demand curve. A megawatt in one market is not exactly a megawatt in another, and the auction prices are for the capacity cleared in the auction: in MISO and NYISO most capacity is self-supplied or contracted, and the auction prices the residual.

**Markets with no rows, by design.**
- **ERCOT** is an energy-only market: there is no capacity auction and no capacity price. Its scarcity pricing (the operating reserve demand curve) is inside the energy price already in `ercot_all_hub_prices_history`. No row is not a gap.
- **California** has no capacity market. Load-serving entities meet resource adequacy (RA) obligations through bilateral contracts. The CPUC publishes yearly Resource Adequacy Reports with price statistics (system, local and flexible RA; weighted average, percentiles) in PDF tables. They were not pulled: the tables differ from year to year and every value would need checking against the document by a person. To add them, a person would pick the report years, confirm for each table which contracts and months it covers, and check the extracted values against the PDF; the rows would then be yearly statistics of contract prices, not auction clearing prices, and should be a table of their own.
- **SPP** has no capacity market: its resource adequacy requirement is met bilaterally.

**Gaps (in the run's status, never estimated).** MISO planning year 2023/24 and the annual auctions before it: MISO's document list holds no results posting for 2021/22 to 2023/24, the 2019 and 2020 postings are annual auctions with another page layout, and the history table in later postings merges cells and cannot be read reliably. MISO ERZ for Fall 2025 and Summer 2026 (a range). Not pulled at all: PJM's incremental auctions, NYISO's strip and monthly auctions, ISO-NE's annual and monthly reconfiguration auctions.

**License: internal as a whole.** A table is internal if any of its sources is. Per row, `x_license`:

| Source | `x_license` | Terms, quoted |
|---|---|---|
| PJM | internal | PJM's data license bars non-members from republishing its data (`docs/price-sources.md`, section 7). Not guessed: the same ruling as `pjm_rpm_capacity_prices` |
| ISO-NE | internal | `https://www.iso-ne.com/legal-privacy`: "Any duplication of the Content or non-personal use may violate copyright, trademark, and other laws." |
| MISO | internal | `https://www.misoenergy.org/meet-miso/legal-and-privacy/`: "You are not permitted to modify, publish, transmit, participate in the transfer or sale of, reproduce, create derivative works of, distribute, publicly perform, publicly display or in any way exploit any of the materials or content" |
| NYISO | public, with a caution | Public by the ERW's standing rule (every ISO but PJM). But `https://www.nyiso.com/legal-notice` grants no license: "Access to this Web site does not confer any license or ownership interest in either the form or content of the Web site". A person decides whether NYISO's rows may be shown alone; until then they stay inside the internal table |

The ISO-NE and MISO rulings are stricter than the ERW's treatment of those ISOs' hub prices (public). That difference is for a person to settle; this table takes the cautious reading.

## ERCOT ancillary service prices: `ercot_as_prices`

The day-ahead Market Clearing Price for Capacity (MCPC), hourly, from 2018-01-01. Entity `ercot:<service>`, variable `mcpc_dam`, unit USD/MW-hour, `ts_utc` the start of the delivery hour.

| Service | Entity | Held from |
|---|---|---|
| Regulation Up | `ercot:REGUP` | 2018-01-01 |
| Regulation Down | `ercot:REGDN` | 2018-01-01 |
| Responsive Reserve | `ercot:RRS` | 2018-01-01 |
| Non-Spin | `ercot:NSPIN` | 2018-01-01 |
| ERCOT Contingency Reserve Service | `ercot:ECRS` | 2023-06-10, when ERCOT began buying it; no row before |

**Sources.** ERCOT's public reports, the route the ERCOT price history already uses: NP4-181-ER "Historical DAM Clearing Prices for Capacity" (one file per year; the current year's is republished weekly) and, for the days after it ends, NP4-188-CD "DAM Clearing Prices for Capacity" (one file per day-ahead run). ERCOT publishes the hour ending in Central time with a repeated-hour flag for the autumn clock change; the table holds the hour's start in UTC.

**Never filled.** A (service, Central day) is written only when every hour of the day is there: 24, or 23 and 25 at the clock changes. An empty cell is no row. Session 65's run left out no day: 335,972 rows, against a ceiling of 500,000.

**License: public.** ERCOT's terms (`https://www.ercot.com/help/terms`, item 5): "raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses".

## CAISO ancillary service prices: `caiso_as_prices`

Day-ahead ancillary service clearing prices, hourly, from 2024-09-01 (the window of `iso_hub_prices_history`). Entity `caiso:AS_CAISO` (the CAISO system) and `caiso:AS_CAISO_EXP` (the system with the interties, "expanded"). Variables `as_price_dam_ru` (Regulation Up), `as_price_dam_rd` (Regulation Down), `as_price_dam_sr` (Spinning Reserve), `as_price_dam_nr` (Non-Spinning Reserve). Unit USD/MW-hour.

**Source.** CAISO OASIS report PRC_AS (AS Clearing Prices), market run DAM, one request per Pacific operating day, six seconds apart, in one process. Each day's answer is kept in `warehouse/raw/caiso_as_prices/`, so an interrupted pull resumes where it stopped and no day is asked for twice.

**Kept and left out.** The two system regions only, by the session 65 ruling; the sub-regions (AS_NP26, AS_SP26 and their expanded forms) are not. If the two regions would pass the ceiling of 500,000 rows, only the expanded region is kept. The regulation mileage prices (RMU, RMD) are per MW of movement, not of capacity, and are left out. The hour-ahead and real-time runs are not pulled.

**Never filled.** `gridstatus` reads this report and fills missing cells with zero, so it is not used. A (region, service, Pacific day) is written only when every hour of the day is there. A day OASIS answers with "no data" is a gap in the run's status.

**License: public.** CAISO's terms of use (`https://www.caiso.com/privacy-terms-of-use`): materials and information on the website "may be used by you provided that you keep intact all copyright, trademark and other proprietary notices and that you credit the California ISO".

## USD/MW-hour is not USD/MWh

An ancillary service price pays a resource for holding a megawatt ready for an hour, whether or not it is called. It is not a price of energy and is never added to a hub price per MWh. What a resource earns from a service is its awarded MW times the price, hour by hour; the awards are not in these tables.

## What the tables do not cover

- **Bilateral contracts.** Most capacity and resource adequacy is bought outside the auctions; those prices are private. California's and SPP's are entirely so.
- **Real-time ancillary prices.** ERCOT's real-time ancillary prices (since real-time co-optimization began in December 2025) and CAISO's hour-ahead and real-time runs are not held.
- **The other ISOs' ancillary markets.** PJM, NYISO, ISO-NE, MISO and SPP all buy regulation and reserves; none of those prices is held.
- **Awards and quantities.** The tables hold prices only: no cleared MW, no offer data, no accreditation.
- **Capacity outside the headline auction.** Incremental, reconfiguration, strip and monthly auctions, and MISO before 2024/25.
- **A load's capacity bill.** That depends on its peak contribution and the reserve requirement, not on the auction price alone.

## Checks

`tests/test_session65.py`: each parser on a saved document (CAISO and ERCOT in `tests/fixtures/session65/`; the capacity sources' documents are not copied into the repository and are read from `warehouse/raw/` where the machine holds them), the ceilings, the never-fill rule, the raw-file cache. The validator passes each table.
