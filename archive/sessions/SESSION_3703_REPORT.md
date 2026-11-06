# Session 3703 report: the Grid tool's replication

Energy Research Warehouse (ERW). Chain 208, session 4 of 20, portable laptop, 6 November 2026, about 22:05 to 22:24 UTC. Branch `wip/3701-sellable`, head `d3eee6ee1`.

- **What the Grid tool prints**: read by an Explore agent and checked against the code. `/grid` opens on the Lower 48 on the Mix tab, and its headline figures are live reads. The Network and Gravity tabs draw from a snapshot. The Clean tab's monthly block reads `carbon_intensity_monthly`. The Ask panel shows stored answers.
- **`replication/grid/`:**
  - `network_figures.mjs` runs the page's own pure functions with node, with no build and no `node_modules`.
  - `figures_of_the_page.py` writes `page_figures.json` and `.csv`: 188 figures.
  - `replicate.py` (standard library and pandas) recomputes them without the page's code.
- **On 6 November** (the snapshot built 2026-11-05T23:09:35Z; the tables of `warehouse/output`, retrieved 26 September to 2 October), **147 of 158 computed figures met**:
  - network and gravity: 85 of 85;
  - carbon months: 14 of 14, rebuilt from the hours and CO2;
  - Ask: 48 of 59, plus 11 a known difference;
  - 22 "license needed";
  - 8 not held: 7 hourly carbon figures after the tables' copy, and 1 table not on the machine.
- **The 11 known differences:** answers asked on 14 and 19 October against the live set, while the copies of their tables here are from late September and early October. CAISO's `cost_of_power_monthly` and `carbon_intensity_monthly` were rebuilt in between; SPP's queue gained a project.
- **Test:** `tests/test_session3703.py`, 11 tests, OK. The table tests ran against the main checkout's tables (`ERW_REPLICATION_TABLES`); in a worktree they skip.

## Decisions made without you

- The Mix tab's latest-hour figures are not in the comparison. They are live reads, and this chain's rule makes the snapshots its only touch of production. `mix_now()` holds the page's rules and is tested on a fixture.
- The "page figures" of the network are the page's own code on the snapshot, not a build. The functions are the ones the page calls; a build needs 3 GB.
- A stored answer that the copy of its table does not reproduce is a known difference when the copy was made on another day than the answer. It is a failure when the dates are the same.
- The panel's grid scope (`scope_rows`) is applied to a grid's own chat and the Grid panel. Without it, CAISO's 2024 wind curtailment summed every ISO.

## For Samuel's ruling

- None new.
