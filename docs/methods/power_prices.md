# Power prices: the newest price at every hub and zone

The first tab of `/prices` ("Power prices"). Written by session 328 (20 October 2026), the page's method note until then
being its own lead paragraph. The second tab, ERCOT, is the peak premium explorer: `ercot_peak_premium.md`.

## What the page shows

For each grid operator in `site/data/markets.json` (ERCOT, CAISO, NYISO, MISO, SPP and ISO-NE), one row a hub or zone:

| Column | What it is | Where it is read |
|---|---|---|
| Real time, USD/MWh | the newest real-time price the operator has published for that node | `latest_prices`, the live set's own table |
| Interval start (UTC) | the start of that interval, with its variable (ERCOT `spp_rtm`, a 15-minute settlement price; the others `lmp_rtm_5min`, a 5-minute price) | `latest_prices` |
| Day-ahead this hour, USD/MWh | the day-ahead price of the hour that contains the time the page was drawn | the grid's day-ahead table in `markets.json` (`iso_dam_hub_prices`, `nyiso_dam_zone_prices` or `isone_dam_zone_prices`) |
| Hour start (UTC) | the start of that day-ahead hour | the same |

Every price is a checked number: `check-values` reads it again from the same row of the same table.

## The rules

- **Refresh.** `latest_prices` is written every 15 minutes by `warehouse/connectors/latest_prices.py`
  (`.github/workflows/latest-prices.yml`); the page is drawn again at most every 15 minutes (`revalidate = 900`). A
  real-time price can therefore be up to about half an hour old when read.
- **The day-ahead hour.** The page reads the last day of each day-ahead table and shows the row whose hour contains
  the time the page was drawn. Where the table holds no such row, the cell says what the table holds: its newest hour
  for that node, or that it holds no row of the node in the last day (session 319). The owner ruled on 20 October 2026
  that the column stays, with these words (recorded by session 351).
- **PJM** is not shown: its prices are licensed for internal use only.
- **MISO** is paused since 4 October 2026 (`miso_pause.md`): no request goes to MISO, so its rows are those held
  before the pause, or none.
- A hub price is an average over many points of a grid; the price at one site differs by congestion and losses.

## Downloads

Under the tables, each grid's real-time and day-ahead table as the live set's CSV, with a Python and a Stata reader of
that CSV (`/api/download?table=<name>&as=py` or `&as=do`). `latest_prices` is not an ERW table and has no download: the
intervals it shows reach the real-time tables with the daily run.

## The figures on the page and their keys

Each number `/prices` shows carries its key (`site/components/Num.tsx`), which `site/scripts/check-values.mjs` checks against the live set and `site/scripts/check-methods.mjs` against this note (session 409). The keys the sections above do not name:

- `iso_dam_hub_prices`, `nyiso_dam_zone_prices`, `isone_dam_zone_prices`, `lmp_dam`, `spp_dam`: the column "Day-ahead this hour, USD/MWh", each grid's day-ahead table and variable as `site/data/markets.json` names them: `spp_dam` in `iso_dam_hub_prices` for ERCOT; `lmp_dam` in `iso_dam_hub_prices` for CAISO, MISO and SPP, in `nyiso_dam_zone_prices` for NYISO and in `isone_dam_zone_prices` for ISO-NE.

## The replication (session 7011, chain 301)

`replication/prices/replicate.py` reads the live set as the pages do (the public anon key; `latest_prices` and each market's day-ahead and real-time rows of the last 30 days, as `site/data/markets.json` names them) and compares every row with the warehouse's own table: on 16 November 2026 at 11:25 UTC, 74,258 of 74,258 prices equal, the "day-ahead this hour" rule included; 6 live rows were newer than the warehouse's copy and not compared; MISO, NYISO and ISO-NE show no row to the anon key. `replicate.do` reads five of those prices from the tables in Stata, its expected values at its top.

## The cross-checks (session 7018, chain 301)

The page's prices are the operators' own, read from their market data; the warehouse holds no second public publisher of the same hub and zone prices. EIA's wholesale daily prices are ICE's indices, held internal pending a ruling (`docs/methods/price_board.md`, "What waits for the owner"), and no figure of them is printed here. What was checked, on 16 November 2026:

| Check | Result |
|---|---|
| Every price the page reads from the live set against the warehouse's own table of the same interval (the replication) | 74,258 of 74,258 equal |
| The 15-minute loop's newest intervals against the daily tables' rows of the same intervals | equal where both hold them (the loop's newest six intervals were not yet in the daily tables) |

Not yet read: the operators' own monthly market reports (CAISO's and ERCOT's monthly averages of day-ahead hub prices), which would set a published monthly average beside the page's days.

## The decisions on the page (session 7018, chain 301)

The first tab draws these at its foot (`site/lib/decisions.ts`, `PRICES_DECISIONS`), each choice's default and source on hover; the ERCOT tab carries the peak premium explorer's own:

1. The real-time column is the newest interval each operator has published for the node, read every 15 minutes, so a price can be up to about half an hour old when the page is read. **Default:** The newest published interval, refreshed every 15 minutes. **Source:** The operators' real-time market data, read by the 15-minute loop (warehouse/connectors/latest_prices.py). (session 10)
2. ERCOT's real-time figure is its 15-minute settlement point price; the other grids' are 5-minute locational prices, as each operator publishes them, never averaged to a common interval. **Default:** Each operator's own interval: 15 minutes for ERCOT, 5 for the others. **Source:** ERCOT's settlement point prices; CAISO's, NYISO's, MISO's, SPP's and ISO-NE's real-time LMPs. (session 10)
3. The day-ahead column is the hour that contains the time the page was drawn; where the table holds no such row, the cell says what it holds instead, its newest hour for the node or that it holds none of the last day. **Default:** The day-ahead hour containing the moment the page is drawn. **Source:** The operators' day-ahead market results; the owner's ruling of 20 October 2026 kept the column with these words. (sessions 319 and 351; the owner's ruling of 20 October 2026)
4. The page is drawn again at most every 15 minutes, so the day-ahead hour and the newest real-time interval are as of the last drawing, not of the moment a reader opens it. **Default:** Drawn again at most every 15 minutes. **Source:** The site's own rule (revalidate of 900 seconds), matching the 15-minute loop. (session 11)
5. PJM's prices are not shown: PJM licenses its market data for internal use only, so its grid is named and left without a figure. **Default:** PJM named, no figure. **Source:** PJM's terms for its market data, licensed for internal use only; docs/methods/power_prices.md, "The rules". (session 11)
6. A grid whose price tables need a license from 20 October 2026 shows no price; the license line under the title names it, and its rows wait for the publisher's permission. **Default:** NYISO's and ISO-NE's prices held; the license line says why. **Source:** warehouse/metadata/license_status.csv and the publishers' own terms of use, read for each table. (session 215)
7. MISO is paused since 4 October 2026: its terms forbid automated access, so no request goes to MISO and its rows are those held before the pause, or none. **Default:** No request to MISO; what is held stays. **Source:** MISO's terms of use; docs/methods/miso_pause.md. (session 89)
8. A hub's or zone's price stands for an average over many points of a grid; the price at one site differs from it by congestion and losses, and no figure of the page is priced at a node. **Default:** Hubs and zones only, never a node. **Source:** The operators' hub and zone definitions; docs/methods/power_prices.md, "The rules". (session 328)

## What waits for the owner (session 7018)

- PJM's prices (a license), NYISO's and ISO-NE's (the publishers' permission), MISO's (its review): each grid stands as it is until then.
- Whether ICE's indices, as EIA republishes them, may be printed beside the operators' prices.

## Sign-off

- Signed off by:
- Date:
- Items of the section above ruled, and how:
