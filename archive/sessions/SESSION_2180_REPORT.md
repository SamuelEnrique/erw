# Session 2180 report: six held tables described

24 October 2026, from 01:44 UTC, on lab-desktop (the data machine), a session of `queue/done/097-day-1-november-data-canada-offshore-inspections-supply.md`, run beside sessions 2181 to 2183. Model spend USD 0. Pulls: none (Supabase for the lock).

## Read these first

- **Six method notes for tables that had none of their own.** They were chosen among the 121 tables that no note names on its `Tables:` line or in its file name, on this branch, on main or on chain 098's branch (`runs/c097/s2180/gap2.out`). The chosen six are public source tables, three EIA and three from the SPP and NYISO day-ahead markets. The Method cells are filled (`runs/c057/method_cells_locked.sh`).

| Note | Rows | Entities, variables | First and last (UTC) | First written |
|---|---|---|---|---|
| `docs/methods/eia_petroleum_supply_weekly.md` | 26,118 | 30, 5 | 1 January 2010 to 2 October 2026 | session 134 |
| `docs/methods/eia_regional_retail_fuel_prices.md` | 16,279 | 40, 1 | 7 January 2019 to 19 October 2026 | session 132 |
| `docs/methods/eia_retail_electricity_prices.md` | 114,574 | 372, 1 | January 2001 to August 2026 | session 8 |
| `docs/methods/spp_dam_cleared_energy.md` | 14,352 | 2, 1 | 1 September 2025 to 11 October 2026 | session 136 |
| `docs/methods/spp_as_quantities.md` | 159,768 | 2, 7 | 1 September 2024 to 5 October 2026 | session 100 |
| `docs/methods/nyiso_dam_cleared_energy.md` | 9,744 | 1, 1 | 1 September 2025 to 12 October 2026 | session 136 |

- **Written by a helper agent in the chain's worktree, checked here:**
  - every row, entity and variable count and every first and last time recomputed from the tables (all as written);
  - each note's `Tables:` line;
  - no em or en dash, and no other non-ASCII character;
  - three findings read again in the code (below).

  Two tables were already described in part by shared notes (`supply_and_trade.md`, `reserve_quantities_nyiso_spp.md`), and the new notes link to them.
- **Found while writing the notes, recorded in them and left in the code** (for a code chain, as session 2152 left ERCOT's):
  1. **`eia_supply.py`, `eia_board.py` and `eia_series.py` never ask `iso_prices.paused()`,** which CLAUDE.md requires (checked: none names it).
  2. **`eia_supply.py` and `eia_board.py` delete the held table before writing, and the data lock is checked only in the write** (checked: `eia_supply.py` line 238, `os.remove` before `ip.write_csv`). A run without the lock would remove the table and write nothing, and no status row is written either.
  3. **`eia_retail_electricity_prices` holds 26,055 prices of exactly 0 USD/MWh,** 26,037 of them where EIA's sales are zero. `eia_board.py` drops exact zeros as "not a price", and `eia_series.py` keeps them.
  4. **`spp_as_quantities` has no schedule** and was last written on 4 October. Its usage line says "to yesterday" while the code reads to today, and its header's method note says that note's tables hold prices only.
  5. **SPP's and NYISO's cleared-energy parsers keep the last value when an hour is given twice,** and drop non-number cells without a count.
  6. **Several docstrings state a ceiling "in all"** where the code limits one run. The petroleum supply header carries two lines meant for the connector's other tables.
  7. **The weekly supply refresh has no run on Saturday 17 October** for any of its connectors.
- **The NYISO license (for your ruling, below):** `nyiso_dam_cleared_energy` is marked public in its header and in `coverage.csv`, and keeps its weekly step. NYISO's verdict is "needs written permission", the same under which `nyiso_as_prices` was given no scheduled step (session 308).

## Errors

- **The Method-cell run moved one coverage row backwards.** It rebuilt `eia_regional_retail_fuel_prices`' row from this machine's copy, a day older than GitHub's run, and set its last run to 22 October. `coverage.csv` was restored from the branch (it holds no Method column), and the row's last run in `docs/coverage.md` was put back to 23 October. Only the six Method links are changed.

## Decisions made without you

- **These six,** public source tables with no note of their own, chosen among the 121.
- **No code changed** in the six connectors. The faults are recorded in the notes for a code chain.

## For Samuel's ruling

- **`nyiso_dam_cleared_energy` under NYISO's "needs written permission" verdict:** should it keep its weekly step and its public mark, as it does now, or follow `nyiso_as_prices` (no scheduled step until NYISO answers)? Nothing is changed here.

## Files

- New: the six notes above, this report.
- Changed: `docs/coverage.md` (the six Method cells).
- On the data machine only: `runs/c097/s2180/`.
