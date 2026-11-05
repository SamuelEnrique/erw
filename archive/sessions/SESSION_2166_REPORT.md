# Session 2166 report: six held tables described

24 October 2026, from 00:32 UTC, on lab-desktop (the data machine), the fifth session of `queue/done/094-day-31-october-data-britain-imports-gas-use-waterways.md`. Model spend USD 0. Pulls: none. (The notes were drafted by a helper agent beside sessions 2167 to 2169 and checked by this session at 00:51 UTC.)

## Read these first

- **The choice:** the grid operators' public source tables that no note names, leaving out those chains 090 and 092 described on their branches (ERCOT's ancillary services, cleared energy, storage and wind and solar tables, NYISO and SPP's reserve quantities). Only NYISO's interconnection queue had a note of the queue connector's family.
- **Six notes written,** each with its checks computed on the table and a section on where the description and the data disagree:
  - `docs/methods/caiso_interconnection_queue.md` (2,278 requests, snapshot of 19 October 2026)
  - `docs/methods/ercot_interconnection_queue.md` (1,758 requests)
  - `docs/methods/miso_interconnection_queue.md` (3,881 requests; MISO paused since 4 October 2026, the table left as it is)
  - `docs/methods/spp_interconnection_queue.md` (3,078 requests)
  - `docs/methods/caiso_fuel_supply.md` (157,248 rows, 504 Pacific days of 1 June 2025 to 22 October 2026)
  - `docs/methods/nyiso_dam_zone_prices.md` (15,840 rows, 60 days, 11 zones)
- **Against Berkeley Lab's queue** (`lbnl_interconnection_queue`, through 2025): all 2,837 of SPP's Berkeley Lab ids are in its table, capacity within 0.5 MW on 2,815; CAISO's report no longer lists 590 ids Berkeley Lab holds; 566 ERCOT requests Berkeley Lab calls active are completed in ERCOT's table; MISO's capacity agrees on 3,560 of 3,616 matches. NYISO's zone prices equal `iso_zone_prices_history` to the cent on all 11,880 shared zone-hours.
- **The helper's claims checked by this session:** CAISO's queue has 18 rows with `geo` US-MX; `caiso_fuel_supply` lacks five Pacific days (2025-11-02 and 2026-03-08, the clock-change days, and 2026-08-21, 2026-09-22, 2026-10-15), every day written holding 312 rows (a first count of this session shifted every hour by eight hours and was redone in Pacific time). Both hold.
- **Every disagreement acted on:**
  - **A description corrected** (code unchanged): `caiso_fuel_supply.py`'s docstring now says no clock-change day is written, names the three other days absent and says the ceiling counts a run's own rows; its header's window line says "the complete days", not "every day".
  - **Recorded in the notes, not changed:** CAISO's US-MX rows (the queue connector's two-letter test takes Mexico's code for a state's); the queues' retrieval times older than their headers' runs (the tables were rebuilt from the archive on 19 October, as their headers' first lines say); ERCOT's header naming statuses its map never uses, and four negative requested capacities (repowers); MISO's header from another run than its rows, a full timestamp in `vintage`, and a "public" header against the record's ruling; SPP's actual in-service date equal to the proposed one on every row; NYISO's zone prices without a license line, the record's ruling of 21 October governing.
- **The Method cells** of the six are filled in `docs/coverage.md`.

## Errors

- **This session's first count of the fuel table's days used a fixed eight-hour shift** and found one day absent; counted in Pacific time it is five, as the helper found.

## Decisions made without you

- **The queue connector's two-letter geo test left as it is** (a fix would change four tables' `geo` and belongs with a run of the queues, not a note).
- **MISO's header and table left as the restore wrote them,** the pause forbidding a new pull.

## For Samuel's ruling

- None new.

## Files

- New: the six notes, this report.
- Changed: `warehouse/connectors/caiso_fuel_supply.py` (its description and header wording), `docs/coverage.md` (the six Method cells).
- On the data machine only: `runs/c094/s2166/` (the helper's scripts).
