# Session 2958 report: the wiring

6 November 2026, about 08:42 to 08:50 UTC, on lab-desktop (the data machine), chain 157 (the owner's), unattended. Model spend USD 0. Pulls: none.

## Read these first

- **The All grids tab's Headroom column draws the active interconnection queue** (commit `960f8c36b`):
  - "<MW> MW in queue", keyed `allgrids|queue|<row>`, written whole, replicated (`warehouse/replication/siting.py`, `queue_figures`).
  - ERCOT 298,606 MW (19 October 2026), SPP 134,797 (26 October), CAISO 73,848 (19 October).
  - ISO-NE's, MISO's and NYISO's rows read "license needed", since their queue tables are held whole. PJM's reads "not held".
  - Through `sitingStat`: SP15 73,847.7, HB_HUBAVG 298,606, SPP North 134,796.7; the held rows give no figure.
  - `siting_page.py` gains `queue_by_grid`. For this commit only the `queue` key was added to the committed `headroom.json`; nothing the tab drew before moved.
  - `docs/methods/siting.md` is now version 10 (decision 35). Test `tests/test_session2958.py`; with the 37 tab test files, 148 passed. No type error in the changed files.
- **The other slots the chain names, not wired, and why:**
  - **Forecast growth:** FERC-714's forecasts are not held (sessions 2949 and 2950).
  - **"Pipeline MW with an agreement":** EIA-860M records no interconnection agreement. The tab's signed line (Berkeley Lab's) already stands for it.
  - **"Time to connect", the ISOs' durations:** a recent request year's median counts only the requests already in service (the method note), so it would read faster than the measured median the cell draws now. How to show both is a design question.
  - **The datacenter tracker's by-grid view and the price board's gas group:** each needs a design choice of which figure and where, beyond a line in an existing cell. The keys are listed in session 2957's report.
- **The 390 and 1280 read and the landing** go with this chain's landing in session 2969, on its gate's local build, so the branch passes one gate.

## Decisions made without you

- **One line wired, the rest carried** with their reasons.
- **The landing joined to session 2969's.**

## For Samuel's ruling

- **Where the gas balance should show on the price board** (its gas group: the storage position against five years, or the monthly LNG share), and **whether the tab's Time to connect should draw the ISOs' own durations** beside Berkeley Lab's median.
