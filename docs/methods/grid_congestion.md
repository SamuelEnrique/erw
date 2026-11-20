# Congestion as the operators publish it: binding constraints and the congestion part of price

Chain 601, part C (session 9000, 20 November 2026). Connector: `warehouse/connectors/grid_congestion.py`. Tables: `constraints_binding_hourly`, `price_congestion_hourly`. The ground for the choice of operators: `docs/reviews/grid-conditions-sources-2026-11-20.md`.

## What a reader gets

- **Which constraints bound, when, and at what shadow price**, in the day-ahead market of SPP (from 2025, deepening a year at a time toward 2014) and CAISO (from 2025, deepening toward 2015). A constraint is a transmission element (a line, a transformer, a flowgate, a nomogram) that the market's dispatch held at its limit; its shadow price is what one more megawatt of room on it would have been worth in that hour, in USD per MWh, as the operator prints it.
- **The parts of the day-ahead price** at the hubs and zones each operator splits: energy, congestion, loss (and greenhouse gas at CAISO). The congestion part says how much of a place's price came from the wires being full.

## Sources

| Table | Operator | Report | Address |
|---|---|---|---|
| `constraints_binding_hourly` | SPP | Day-Ahead Binding Constraints (`spp:DA-BC`) | `https://portal.spp.org/file-browser-api/download/da-binding-constraints?path=/YYYY/MM/By_Day/DA-BC-YYYYMMDD0100.csv`; archived years `/<year>/<year>.zip` |
| `constraints_binding_hourly` | CAISO | OASIS Nomogram/Branch Shadow Prices, DAM (`caiso:PRC_NOMOGRAM`) | `https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=PRC_NOMOGRAM&version=1&market_run_id=DAM&startdatetime=...&enddatetime=...` |
| `price_congestion_hourly` | SPP | Day-Ahead LMP by Settlement Location (`spp:DA-LMP-SL`) | `https://portal.spp.org/file-browser-api/download/da-lmp-by-settlement-location?path=/YYYY/MM/By_Day/DA-LMP-SL-YYYYMMDD0100.csv` |
| `price_congestion_hourly` | CAISO | OASIS Locational Marginal Prices, DAM (`caiso:PRC_LMP`) | `https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=PRC_LMP&version=12&market_run_id=DAM&node=...` |

Every row carries the exact document it was read from (`source_url`) and when (`retrieved_at`). Raw files are kept under `warehouse/raw/grid_congestion/`.

## Decisions

1. **Operators.** SPP and CAISO only. ERCOT publishes its shadow prices only on the paths its robots file disallows (`/misapp`, `/misdownload`) or through an API whose key the owner has not made, and the owner's ruling 2 of 6 November 2026 forbids new requests there. PJM (paid license), NYISO and ISO-NE (written permission) are held, and MISO is paused. A page draws each of them blank with the reason on hover.
2. **The key.** `entity` is the operator's own constraint name, unchanged. CAISO lists one branch under more than one contingency in the same hour (found on 2019-01-15: the Lugo to Victorville 500 kV branch under two contingencies), so a CAISO entity is `caiso:<NOMOGRAM_ID_XML>|<CONSTRAINT_CAUSE>`. SPP's file holds each constraint name once an hour (checked on the trial day, 617 rows).
3. **Signs as printed.** SPP prints shadow prices as negative numbers, CAISO as positive. Neither is changed in the table. A roll-up that ranks constraints by cost uses the absolute value and says so.
4. **Absence is not zero.** A constraint has a row only in an hour it bound. A month with no row for it is a month it did not bind in the day-ahead market (or a day the operator's file was missing, which the header's gap list names).
5. **Places.** SPP: its two hubs (SPPNORTH_HUB, SPPSOUTH_HUB). CAISO: the three trading hubs and the four default load aggregation points (PG&E, SCE, SDG&E, VEA). Both are the places the warehouse's own price tables hold, so the LMP of this table can be checked against them: on the trial (10 to 19 November 2026) the LMP matched `iso_hub_prices_history`, `iso_zone_prices_history` and `iso_dam_hub_prices` in every matched hour (difference 0.0), and `lmp_dam` equals the sum of its parts within 0.00001 in every hour.
6. **Depth.** CAISO's OASIS keeps PRC_LMP for a rolling window (about 39 months: 2022-06-15 and 2019-01-15 answered "No data found"), so CAISO's price parts start in 2023. SPP's price files for archived years come as one zip of every settlement location a year; they are not read until a later session chooses to, and the header says so.
7. **Never filled.** A price (place, part, day) is written only when every hour of the operating day is there exactly once.
8. **Real time.** The real-time constraint files (SPP five-minute, CAISO five-minute) are larger and are not in this first table; a later session may add them as their own variables.

## Replication

`runs/c601/check_parts.py <path to price_congestion_hourly.csv>` recomputes the parts' sum and the cross-check against the held price tables.
