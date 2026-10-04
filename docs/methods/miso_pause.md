# MISO pulls are paused (4 October 2026)

Energy Research Warehouse (ERW). Samuel's ruling of 4 October 2026, at the close of session 89: **every pull of MISO's own servers is paused, pending a review of MISO's terms by a person.** Every MISO table and every page stays exactly as it is. Nothing is deleted.

## Why

MISO's terms of use (`https://www.misoenergy.org/meet-miso/legal-and-privacy/`, read on 2026-10-04 in session 85) say:

> "You agree not use any automated means, including, without limitation, agents, robots, scripts, or spiders, to access, monitor, or copy any part of this Website or the App."

The ERW had read MISO's market report files by script every day since session 5. Session 85 found the sentence while recording the license of MISO's reserve prices, quoted it, and left the ruling to a person. This is the ruling.

The same page forbids republishing ("You are not permitted to modify, publish, transmit, participate in the transfer or sale of, reproduce, create derivative works of, distribute, publicly perform, publicly display or in any way exploit any of the materials or content on this Website or the App in whole or in part"). That is the license question, recorded per table in the source registry; it is a separate matter from the pause and is also for the review.

## What is paused

One list holds the pause: `warehouse/metadata/paused_sources.csv`, one row per publisher, with the date, the reason, the terms quoted, who ruled, and what it waits for. Every connector that requests MISO asks `iso_prices.paused("miso")` first and makes no request while the row is there.

| Pull | Where it ran | What it wrote | Now |
|---|---|---|---|
| Hub prices, day-ahead and real-time | the daily run (`iso_prices.py miso`) | MISO's rows of `iso_dam_hub_prices` and `iso_rtm_hub_prices` | out of the daily run's list; the connector refuses |
| The latest real-time price | the 15-minute run (`latest_prices.py`) | MISO's row of `latest_prices` | skipped; the other five grids are read as before |
| The interconnection queue | the daily run on Mondays (`iso_queues.py`) | `miso_interconnection_queue` | skipped |
| Planning Resource Auction results | the daily run on the first of the month (`iso_capacity_prices.py`) | MISO's rows of `iso_all_capacity_prices` | skipped; its rows are kept by the merge writer |
| Day-ahead reserve prices | by hand (`miso_as_prices.py`, session 85) | `miso_as_prices` | refuses to run |
| Hub price history | by hand (`hub_history.py`) | MISO's rows of `iso_hub_prices_history` | refuses MISO |
| The MISO newsroom feed | the daily news ingest (`feeds.yaml`) | stories in `news_stories` and `news_index` | moved out of the list the ingest reads (kept in the file under `paused_feeds`); a story of a MISO outlet found through another search is not opened on MISO's site |

**Not paused:** the figures for the MISO balancing authority that come from the US Energy Information Administration (EIA-930 demand, generation, interchange and emissions; EIA-860M), from NOAA's weather stations, and from Berkeley Lab's queue data. They are those publishers' files, on their servers.

## What a reader will see once the pause is live

Nothing is removed, so the first thing a reader sees is that MISO's figures stop moving.

- **The home page's MISO card** keeps its last real-time price and the time of that interval, which will age. Its seven-day line shortens by a day each day and, about a week after the last pull, is replaced by the card's "no data" line, because no MISO price of the last seven days is held.
- **Pages in review** that show MISO's hub prices (the price board, markets, prices, cost of power, the seller tab's MISO hub, the trader view) stop at the last day pulled. Tables derived from the hub prices (`price_board_*`, `cost_of_power_monthly`, `merchant_revenue_monthly`, the trader view's tables) gain no new MISO days.
- **The queue map and the project table** keep MISO's queue as of its last weekly pull.
- **The digest** no longer carries stories from MISO's newsroom feed; stories about MISO from other outlets arrive as before.

## The source registry

Every row of `warehouse/metadata/sources.csv` that belongs to MISO (the `miso:` reports and the MISO news outlets) carries the pause in its `report` column: "[PAUSED 2026-10-04: MISO's terms forbid automated access; pulls paused pending a review of MISO's terms by a person (docs/methods/miso_pause.md)]". The registry's writer adds the note to any such row whoever writes the registry, so a later run cannot drop it while the pause stands.

## To lift the pause

A person, after the review: delete MISO's row from `warehouse/metadata/paused_sources.csv`; put `miso` back in the `ISOS` list of `warehouse/run_daily.sh`; move the MISO newsroom entry of `warehouse/news/feeds.yaml` from `paused_feeds` up into `feeds`; remove the note from the registry's MISO rows. The days missed can be pulled then: the connectors merge, and MISO keeps its market report files.

## Checks

`tests/test_session89_miso_pause.py`: with every way of making a request replaced by a failure, the daily price run for MISO, the 15-minute run's MISO read, the queue, the capacity and the reserve connectors make no request and report the pause; the other grids are read as before; the daily run's list holds no MISO; no feed the ingest reads searches MISO's site; the registry's MISO rows carry the note and no other row does; the MISO tables on the machine are untouched by a paused run.
