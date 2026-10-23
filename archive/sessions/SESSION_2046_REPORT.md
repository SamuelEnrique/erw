# Session 2046 report: six held tables described

23 October 2026, from 18:54 UTC, on lab-desktop (the data machine), the fifth session of `queue/done/059-night-24-october-data-storms-reactor-events-lng-climate.md`. Model spend USD 0. Pulls: none.

## Read these first

- **183 of the 389 tables in this branch's `coverage.csv` had no method note** (by `build_coverage.method_notes()`); this chain's four new tables are among them and are left to session 2052. Chain 057's session 2018 was writing EIA crude notes at the same time (two untracked notes in its worktree), so this session took six tables of other publishers, none of them EIA's:
  - `docs/methods/cftc_cot_positions.md` (9,824 rows: 4 contracts, 4 variables, 614 weeks, 6 January 2015 to 6 October 2026)
  - `docs/methods/frb_treasury_yields.md` (5,856 rows: 3 series of 1,952 business days, 2 January 2019 to 21 October 2026)
  - `docs/methods/carb_lcfs_credit_prices.md` (1,124 rows, 7 January 2019 to 14 September 2026)
  - `docs/methods/carb_auction_allowance_prices.md` (336 rows: 56 auctions, November 2012 to August 2026)
  - `docs/methods/imf_commodity_prices.md` (465 rows: 5 series of 93 months, January 2019 to September 2026)
  - `docs/methods/nrc_reactor_status.md` (235,005 rows: 99 reactors, 1 January 2020 to 23 October 2026)
- **Each note's counts were computed from its table read past its header lines, and checked again by this session** (the six row counts, entity counts and date ranges above, and the weekdays of the two weekly tables). Each rule in a note was read in its connector.
- **Five contradictions found, each acted on** (descriptions corrected; no code, rule or figure changed):
  - `cftc_cot.py` said the report date is a Tuesday; 6 of 614 are Mondays (holiday weeks, 2017 to 2025). The docstring and the header's words now say so.
  - `carb_lcfs.py`'s docstring said every week sits on its Monday; CARB dates one week (7 September 2021) by its Tuesday, as the code's own comment says. The docstring now says so.
  - `carbon_auctions.py`'s docstring said "License: internal" for CARB; the table has been public since session 324 (`sources.csv` and its header). Corrected; RGGI's table stays internal.
  - `imf_pcps.py`'s docstring and header said the IMF's terms page answered HTTP 403; it was read on 12 October 2026 (read 13). Both now cite read 13, and quote the page's "The IMF prohibits bulk download of information by automated technology without explicit permission" (below).
  - `nrc_reactor_status.py` said its header names the files refused; a `--recent` run's header names only that run's file, so 2019 (refused in session 133, no row) is not named. The docstring now says so, and that a unit's name becomes one underscore for each run of other characters (`nrc:d_c_cook_1`).
- **The Method cells** of the six are filled in `docs/coverage.md` (`runs/c059/method_cells_locked.sh`, `runs/c045/method_cells.sh` under the data lock).

## Errors

- **The Method-cell run moved three tables' coverage rows to this machine's copies** (as session 2004's did): `imf_commodity_prices`'s last run went back from 23 to 20 October, and `carb_auction_allowance_prices`' and `nrc_reactor_status`'s moved too. `coverage.csv` was put back to the branch's, and `docs/coverage.md` rebuilt from the branch's with only the six Method cells added.

## Decisions made without you

- **Six tables of six publishers, none of them EIA's,** so this session and chain 057's session 2018 do not describe the same tables.
- **The notes were written by a helper agent working only in this chain's worktree, and checked by this session** (each count recomputed, each contradiction read in the code before acting).
- **Descriptions corrected, not code:** each contradiction was a docstring or a header's words; the tables' figures and rules stand.

## For Samuel's ruling

- **The IMF's terms prohibit "bulk download of information by automated technology without explicit permission"** (read 13). `imf_commodity_prices` reads about 500 rows a month through the IMF's API. The verdict (may be public; commercial reuse needs written permission) quotes this sentence; whether this pull is a bulk download is for a person.
- **The IMF lithium series' unit:** the connector labels it USD/t from its own map, and it reads 490,008 in April 2022 and 144,779 in September 2026, six to ten times USGS's battery-grade carbonate (`docs/methods/usgs_mcs_critical_minerals.md`). Its basis should be confirmed against the IMF's series definition by a person (the IMF's pages are not asked for it without permission).

## Files

- New: the six notes above, this report.
- Changed: `warehouse/connectors/cftc_cot.py`, `carb_lcfs.py`, `carbon_auctions.py`, `imf_pcps.py`, `nrc_reactor_status.py` (descriptions), `docs/coverage.md` (the Method cells).
- On the data machine only: `runs/c059/method_cells_locked.sh`, `runs/c059/s2046*`.
