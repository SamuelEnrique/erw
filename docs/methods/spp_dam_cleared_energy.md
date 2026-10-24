# SPP demand cleared in the day-ahead market, by hour and balancing authority area (DA-MC files)

Energy Research Warehouse (ERW), method note written in session 2214 (chain 098) for a table first written in session 136 (approved pull).

Tables: `spp_dam_cleared_energy`

## Publisher and address

Southwest Power Pool (SPP), Marketplace portal, Market Clearing (`https://portal.spp.org/pages/market-clearing`): one day-ahead file a day, `https://portal.spp.org/file-browser-api/download/market-clearing?path=/<YYYY>/<MM>/DA-MC-<YYYYMMDD>0100.csv`. Source id `spp:DA-MC:cleared`. A day whose file `spp_as_quantities.py` (or this connector) already saved is read from the machine; raw files under `warehouse/raw/spp_dam_cleared/`.

Connector: `warehouse/connectors/spp_dam_cleared.py` (session 136), with the shared frame `warehouse/connectors/dam_cleared.py`: by default the last 14 days and tomorrow, two seconds between requests, a ceiling of 5,000 rows read a run, and a run fails if the newest hour is more than 5 days old.

Schedule: weekly, on Saturdays (UTC), in the supply step of `warehouse/run_daily.sh` (`bash warehouse/refresh_supply.sh`, `SUPPLY=1` on any other day), under the 15-minute pull budget and `warehouse/health.py`, on the GitHub runner (`.github/workflows/daily-prices.yml`).

## Vintage and revision

The header's last run is `20261010T150020Z`: "Rows read from the operator in this run: 720 ... Hours written by this run: 720, 2026-09-26T05:00:00Z to 2026-10-11T04:00:00Z", "144 new, 576 replacing ..., 13632 rows are kept from earlier runs"; then "Restored from the Redivis draft". `retrieved_at` runs from 2026-10-04T11:40:59Z to 2026-10-10T15:01:12Z; `vintage` empty; 405 source files. The table merges and keeps days SPP's window no longer covers.

## Shape and variables

Series, 14,352 rows: `variable` dam_cleared_energy, value SPP's column "Total Demand", `unit` MW (over the hour), `freq` PT1H, `market` spp_dam, `node` "Total Demand", `geo` "US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY".

| `entity` | Rows | First to last | Lowest, MW | Highest, MW | Mean, MW |
|---|---|---|---|---|---|
| spp:SPP | 9,720 | 2025-09-01T05:00:00Z to 2026-10-11T04:00:00Z | 26,722.7 | 61,332.1 | 38,252.34 |
| spp:SWPW | 4,632 | 2026-04-01T05:00:00Z to 2026-10-11T04:00:00Z | 1,934.3 | 5,071.9 | 3,143.75 |

A file from before 1 April 2026 names no area; its rows are spp:SPP. From that day the file names SPP and SWPW (the western area). spp:SPP's mean was 34,864.6 MW in March 2026 and 34,094.4 in April 2026.

## Placing values in time, and what is filled

`ts_utc` is the file's `GMTIntervalEnd` less one hour (the hour's start, UTC); the file's own Interval is Central hour ending. An empty cell gives no row; a day SPP has not posted (HTTP 404) is not written; nothing is filled.

## License

Header: "License: public, with citation. SPP's terms: "Permission is implicitly granted to copy and distribute ... in whole or in part (with appropriate citation) EXCEPT when such materials will be used, in whole or in part, within a commercial publication" (https://www.spp.org/terms-conditions/, read 6 October 2026)." `docs/licenses.md`: "may be public", flag public, "needs written permission" if the ERW sells anything, ERW verdict public.

## Checks (session 2214)

The figures in this note were computed from the rows of `warehouse/output/spp_dam_cleared_energy.csv`, read past its 12 header lines (scripts in `runs/c098/s2214/`).

- 14,352 rows, `ts_utc` from 2025-09-01T05:00:00Z to 2026-10-11T04:00:00Z, as the header states; no (entity, variable, ts_utc) twice; both entities hold every hour of their spans (405 Central days for spp:SPP: 24 hours each but 2025-11-02 with 25 and 2026-03-08 with 23; 193 days for spp:SWPW).
- Against EIA-930 (`eia930_daily_demand`, SWPP): spp:SPP's day sum is a median 1.0795 of SWPP's daily demand over 405 days, from 0.9317 to 1.2240 (SPP's cleared demand and EIA's balancing authority demand are different measures).

## Where the description and the data disagree

None found: the docstring, the header and the rows agree on the areas, their start, the unit, the hour's placing and the span.

## What it does not hold

- SPP's other cleared quantities (generation, virtual bids, offers), real-time quantities, and reserve quantities (`spp_as_quantities`).
