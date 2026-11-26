# What power costs across the map (`site/data/regions/prices_map.json`)

Energy Research Warehouse (ERW). Session 8013, chain 505, part E (the master plan's eighth tool). Builder: `warehouse/derived/prices_map.py`, a step of the data machine's daily run. Contract: section 13 of `docs/state/page_files_regions.md`. Test: `tests/test_session8013_prices_map.py`.

## What already existed (read first, so nothing is built twice)

- `/prices/compare` ("Where power is cheap", `site/data/price_compare.json`, table `hub_price_comparison`): twelve months and the last whole month, day-ahead and real-time, average, share of hours below zero and above USD 200, and the four dearest less four cheapest hours, for CAISO, ERCOT and SPP; NYISO, ISO-NE and MISO held by name, PJM not held.
- `/board` (`site/data/board.json`): daily means, moves, 7- and 30-day means, twelve months, on-peak and off-peak at the main hubs.
- `/prices`: the newest real-time and day-ahead price of every hub, from the live set.
- The All grids tab of `/cost-of-power`: what a load pays over twelve months.
- The Grid tool's network has a price ring at each grid's main hub; its map of balancing authorities had no price.

So this file adds what none of them gives in one place, keyed to the map: each shown hub's newest whole day beside its thirty days and twelve months, with the authority and region it sits in. It reuses `price_compare.py`'s reader, hourly rule, coverage rule and license and pause handling, and `price_board.py`'s on-peak rule and main hubs, unchanged.

## The measures

Day-ahead prices only, in each grid's local time. The day is the newest local day before the build's own day that holds every hour. That day gives the mean, the on-peak and off-peak means (hours beginning 06:00 to 21:00, Monday to Friday, to Saturday for CAISO, NERC holidays off), and the four dearest hours' mean less the four cheapest. The thirty and 365 local days ending on that day give the mean and the share of hours below zero. A window is written only when at least 95 percent of its hours are held; otherwise it is blank with the count. An authority's area takes its grid's main hub (the board's and `markets.json`'s choice).

## Held and paused grids

A grid whose prices `docs/licenses.md` holds for a license (today ISO-NE and NYISO, as `warehouse/metadata/license_status.py` reads it) carries its key with no figure and the words "license needed". MISO is paused, and PJM holds no price in the warehouse; each is listed with its reason. No hold is worked around.

## Limits

The day is the newest held when the file was built, which can be a few days old if the price tables have not been refreshed on the machine; the file names the day. Since session 10218 (the prices audit, `docs/reviews/prices-model-audit-2026-11-26.md`, finding 5) the legend names it too, with the day the file was built, and says when the areas' days differ: on 26 November 2026 the file built on 19 November colored the map by 16 November, while the site's own hourly price files held whole days to 20 November for ERCOT and 25 November for CAISO and SPP. A hub's thirty days can be blank while its twelve months are not, when the newest weeks hold a gap (ERCOT's hubs held 673 of 721 hours on 19 November 2026).
