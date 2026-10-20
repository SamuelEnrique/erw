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
  for that node, or that it holds no row of the node in the last day (session 319).
- **PJM** is not shown: its prices are licensed for internal use only.
- **MISO** is paused since 4 October 2026 (`miso_pause.md`): no request goes to MISO, so its rows are those held
  before the pause, or none.
- A hub price is an average over many points of a grid; the price at one site differs by congestion and losses.

## Downloads

Under the tables, each grid's real-time and day-ahead table as the live set's CSV, with a Python and a Stata reader of
that CSV (`/api/download?table=<name>&as=py` or `&as=do`). `latest_prices` is not an ERW table and has no download: the
intervals it shows reach the real-time tables with the daily run.
