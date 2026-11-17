# Session 7603 report: the datacenter tracker read as its reader

Energy Research Warehouse (ERW). Chain 305, part C, portable-laptop, 17 November 2026, about 07:00 to 07:40 UTC. Model spend: USD 0.

- **Checked first:** no `datacenters-read-2026-11-16.md` on any branch; claimed as row 25 of `docs/state/done_line_claims.md` in session 7602.
- **The reader:** a fund analyst sizing datacenter load in one utility's or grid's territory. Five cases: ERCOT's large load approved and running; the Stargate campus at Abilene; Dominion's territory (Loudoun County, PJM); a flat 300 MW load at ERCOT's West zone; the Giga Texas queue position.
- **Read on a build of origin/main** (with session 7602's fixes), at 1280 and 390 px. `docs/reviews/datacenters-read-2026-11-16.md`: 7 rows.
- **Two site faults fixed with a test** (`tests/test_session7603_datacenters_read.py`, 6 passed) and read again on a second build:
  - "The facilities against each grid" printed "license needed" in the grid's own public cells too: `Num.tsx`'s `heldBy` read every `dcgrid` key as the held facilities table. The peak and capacity (`grid_peak_vs_capacity`) and ERCOT's reserve margin (`ercot_cdr_reserve_margins`) are now asked of their own public tables, in `Num.tsx` and its mirror `check-holds.mjs`: ERCOT 83,597 MW peak, 164,685 MW capacity, 11.4 percent margin; the facilities' columns still held.
  - The note beside ERCOT's report of 24 April 2026 read "March 2026 (as written; the report is of 2026)"; it now says "the report is of April 2026".
- **Shared figures agree:** ERCOT's 8,927 MW approved (the All grids tab); a flat load at West, USD 35.35 per MWh and 2025's USD 42.18 (`/cost-of-power`). **One disagreement stands:** the map draws 278 of the facilities this page holds (row 7 of the datacenter faults of 11 November, open).
- Needs the key: nothing. For Samuel's ruling: the map against the hold (default unchanged); placing a Travis County site in a load zone (default not placed).
- Commit: `150369357` on `wip/7603-datacenters-read`.
