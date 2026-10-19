# ERCOT's grid notices: method

Energy Research Warehouse (ERW), session 322 (the owner's default of 19 October 2026 for the morning note's item 9). The table is `ercot_grid_notices` (events); the code is `warehouse/connectors/ercot_grid_notices.py`. Tier: source. License: public (ERCOT's terms, read 2 of `warehouse/metadata/license_reads.csv`). Credit: Electric Reliability Council of Texas (ERCOT).

## 1. Question

On which days did ERCOT call on supply or demand across its grid: an Energy Emergency Alert, rotating outages, a conservation appeal, a watch? `grid_stress_days` counts a CAISO day by its notices as well as its price (session 297's rule). Until this table, ERCOT was judged by price alone, so 24 December 2022 (Winter Storm Elliott) was not a stress day (session 306).

## 2. Where ERCOT keeps its notices

ERCOT publishes no single history of its notices. Three of its pages were read on 19 October 2026, after its robots file (which disallows none of them):

| Page | What it holds | Read |
|---|---|---|
| News releases, `https://www.ercot.com/news/releases?year=YYYY` | every release from 2010; the grid-condition ones announce EEAs, rotating outages, conservation appeals, Power Watches (2011), Weather Watches and Voluntary Conservation Notices (TXANS, from May 2023), and some Operating Condition Notices | every year's listing, and each release whose title names a grid condition or the weather |
| Operations messages, `https://www.ercot.com/services/comm/mkt_notices/opsmessages?m=MM&y=YYYY` | the control room's messages: Advisory, Watch, OCN, Emergency Notice, EEA, and routine operational lines | the six months ERCOT serves (May to October 2026). December 2022 answered with an empty list: no earlier month is served |
| Market notice archive, `https://www.ercot.com/services/comm/mkt_notices/archives` | market, settlement and outage notices, from 19 October 2023 only | read once; not used: it holds no operating conditions |

## 3. Rows

- **One row per notice and Central day it covers.** A release that names its days covers those ("Requests Conservation Monday, January 15"; "Winter Weather Watch Through Sun., Feb. 6"; "a Weather Watch from January 20-23"; an OCN "between Thursday, December 22 through Monday, December 26"), read from the title, else the first two paragraphs; the dateline ("Austin, TX, Sept. 4, 2019") is not a covered day. A release that names none covers the day it was issued. A control-room message covers the day it was issued, or the days an OCN or Watch names (at most 14 days ahead).
- **`event_type`** from the notice's own words, in this order: `update` (a release or message that ends or cancels a notice), `rotating_outages` and `eea3`, `power_watch` (2011's Power Watch and Power Warning), `eea2`, `eea1` (named in the title, or the first paragraph saying ERCOT issued, declared, entered or is in an EEA), `voluntary_conservation`, `weather_watch`, `conservation_appeal` (the title, or the text asking for conservation and not saying it is not asking), `ocn_weather` and `ocn` (an Operating Condition Notice, for extreme weather or not), and `statement` (a release on the grid that announces no notice). Control-room messages keep their own type (`advisory`, `watch`, `ocn`, `emergency_notice`, `emergency_test`); the routine "Operational Information" and DC tie lines are not kept.
- **`x_counts`**: `yes` for a system-wide call on supply or demand, the kinds `grid_stress_days` counts as it counts CAISO's notices: an EEA level, rotating outages, a conservation appeal or Voluntary Conservation Notice, a Power or Weather Watch, an OCN for extreme weather, and a release ending an emergency (the emergency was in effect that day). `no` for a notice for the Rio Grande Valley only, an Advisory or Watch on the control room's own tools (a geomagnetic disturbance, a study that did not solve), a test, a statement and other updates.
- **`x_text`**: the release's title and first two paragraphs, or the message, as ERCOT wrote them (its terms ask that the contents not be modified). Some of ERCOT's pages carry a replacement character for an apostrophe or a dash; it is kept as served.

## 4. What it holds (19 October 2026)

178 rows, 2 February 2011 to 15 October 2026; 120 of them count, on 100 days. By type, counted: conservation appeals 39, Weather Watches 44, Power Watches 10, OCNs for extreme weather 11 (5 from the release of 16 December 2022, 6 from the control room's OCN of 19 August 2026), Voluntary Conservation Notices 4, rotating outages 2, EEA 1 and EEA 2 one each, and 8 updates ending an emergency.

**Elliott.** ERCOT's release of 16 December 2022 says: "Earlier today, ERCOT issued an Operating Condition Notice (OCN) ... that temperatures will meet ERCOT's criteria of 25 degrees or lower in the Austin/San Antonio and the Dallas Fort-Worth areas between Thursday, December 22 through Monday, December 26." Those five days are notice days; ERCOT issued no conservation appeal or EEA for Elliott in its releases.

## 5. Limits

- Before May 2026 the control room's own messages are not served; an Advisory, Watch or OCN of an earlier day is in the table only where a release announced it. A day may have had a notice the table does not hold.
- The classification reads words, not a code ERCOT assigns. Each counted row can be checked against its `x_text` and its `source_url`.
- The daily window of the operations messages is six months, so each run keeps the rows it read before (the table only grows).
