# Hub prices from July 2018 to July 2023: `iso_hub_prices_history_2018`

Energy Research Warehouse (ERW). Session 7803, chain 401 part C, table 8. A new table, read by no page, not in the live set (internal tier); its rows public as SPP's are in `iso_hub_prices_history`.

## What it holds

Day-ahead hourly and real-time prices at the main hubs `iso_hub_prices_history` holds, from 2018-07-01 to 2023-07-05, the day before that table begins, from each operator's own archive, by `warehouse/connectors/hub_history.py`'s backfill (its markets, columns and rules unchanged: a day is written only when every interval of every hub is there; real time is the 15-minute mean of exactly three 5-minute prices). `warehouse/connectors/hub_history_2018.py` names the table and registers its sources.

## Which operators

| Operator | In it | Why |
|---|---|---|
| SPP | yes: SPPNORTH_HUB, `spp_dam` and `spp_rtm` | its portal's file browser keeps the daily files back past 2018 |
| CAISO | no | OASIS keeps about 39 months: asked for 1 July 2018 it answers "No data found" (session 7803's trial), the reason `iso_hub_prices_history` starts on 6 July 2023 |
| NYISO | not pulled | license needed under the hold of 21 October 2026 (`docs/licenses.md`) |
| ISO-NE | not pulled | license needed under the same hold |
| MISO | not pulled | paused since 4 October 2026 (`warehouse/metadata/paused_sources.csv`) |
| PJM | not pulled | the chain |

The four left out are under "For Samuel's ruling" in session 7801's report, default not pulled.

## Build

    python warehouse/connectors/hub_history.py backfill --iso spp --start 2018-07-01 --until 2023-07-06 --out-dir runs/c401/hub2018
    python warehouse/lock.py run --task <task> -- <python> warehouse/connectors/hub_history_2018.py --from runs/c401/hub2018

The backfill writes to its own folder (its raw files under it), never to `warehouse/output`; the second step writes the table under the data lock. Not in the daily run: the span is closed.
