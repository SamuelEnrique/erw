# The Western market's transfers between balancing areas, five minutes

Chain 601, part F (session 9000, 20 November 2026). Connector: `warehouse/connectors/caiso_tie_flows.py`. Table: `caiso_tie_flows_5min`, rolling: the last 35 days.

## What it holds

For each pair of balancing areas in the Western Energy Imbalance Market (WEIM) that had any transfer that was not zero that day, the net transfer every five minutes in CAISO's real-time dispatch, in MW: the pair's tie transfers from the first area (alphabetical) to the second, less those the other way. Twenty-five areas and 63 active pairs on 18 November 2026.

## Source

CAISO OASIS, `ENE_EIM_TRANSFER_TIE` version 4, `baa_grp_id=ALL`, `market_run_id=RTD`, one request a day, five seconds apart: `https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=ENE_EIM_TRANSFER_TIE&version=4&baa_grp_id=ALL&market_run_id=RTD&startdatetime=...&enddatetime=...`. OASIS has no robots file (read 20 November 2026, 10:32 UTC).

## Decisions

1. **Transfers, not metered flows.** These are the market's transfers on each tie as OASIS prints them. A page calls them transfers.
2. **Each side reports.** Each area reports its own ties (E an export, I an import). On 18 November 2026 both sides' reports agreed in every interval of every pair, so the pair's figure is the first area's report, and the second's (negated) only where the first is missing.
3. **Active pairs only.** A pair with no transfer that was not zero all day has no row that day; the header says so.
4. **Whole days.** A pair's day is written only when all its intervals are there (288, or 276 and 300 at the clock changes). OASIS lacked three intervals of 19 November 2026 at 11:02 UTC the next day; that day was left out and is asked again by the next runs (a day within four days is always asked again).
5. **Rolling.** Rows older than 35 days are dropped at each write; the header counts them.
6. **Other operators.** SPP's file browser shows no five-minute tie flow folder; ERCOT's are on paths its robots file disallows; PJM, NYISO and ISO-NE are held; MISO is paused. EIA-930's hourly interchange (held since July 2018) covers every authority by the hour.
