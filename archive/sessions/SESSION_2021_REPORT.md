# Session 2021 report: a source of its own choosing: EIA's U.S. liquefaction capacity (LNG export projects)

23 October 2026, from 18:56 UTC, on lab-desktop (the data machine), the second of `queue/done/057-night-23-october-data-wholesale-solar-industry-buildings.md`'s two sessions of a source of its own choosing. Model spend USD 0. Pulls: 3 requests of 20 (www.eia.gov's robots file, asked in a call of its own, unchanged; EIA's natural gas data page, which lists each quarter's file; the 2026 Q3 workbook, through the connector's trial). The write reused the saved workbook (`--offline`).

## Read these first

- **Why this source:** the ERW holds LNG exports by terminal a month (`eia_lng_exports_monthly`) but not the plants behind them: how many trains each terminal has, at what capacity, which are being built and when they start, and which approvals they hold. EIA publishes that every quarter, for the whole country, in one workbook. Chain 058's list (OE-417, EAGLE-I, RINs, biofuels plants, MSHA, FHWA, the AFDC) was left to chain 058.
- **One table written, validated, archived, in coverage (sector gas, public), in the release package, both holds:** `eia_lng_liquefaction_projects`, 48 entities (type `project`), from `U.S.liquefactioncapacity_2026_Q3.xlsx` (released 1 October 2026):
  - 39 trains or groups of trains (sheet "Existing & Under Construction"): 20 in commercial operation, 4 commissioning (Plaquemines Phases 1 and 2, Corpus Christi Stage III, Golden Pass Train 1), 15 under construction (to 2031);
  - 9 large approved projects not yet under construction (sheet "Approved"), status planned;
  - each with its baseload and peak nameplate capacity (bcf/d and Mtpa), the DOE FTA and non-FTA and the FERC authorized export quantities with their dockets, the in-service date as EIA writes it (a day, a year or a half year), the start of commercial operation, the project type and the operator.
- **Status:** the standard's statuses: operating, under_construction, planned; EIA's "Commissioning" has none, so those four rows' `status` is empty and `x_status` says Commissioning. EIA's words are in `x_status` for every row.
- **EIA's footnote marks** beside a figure ("0.66B", "6.20^", "1.20+", "Note A", "n/a") are split from the number and kept in `x_marks`; names and train labels stay as EIA prints them, its letters included ("Train 1B", "Gulf LNGE").

## The cross-check

Each terminal's highest monthly exports of 2026 (`eia_lng_exports_monthly`, MMcf over the month's days; terminal codes as `eia_gas_trade_monthly` names them) against the peak nameplate capacity of its trains in operation or commissioning, `runs/c057/s2021/cross.py`:

| Terminal | Highest 2026 month, bcf/d | Peak capacity | Ratio |
|---|---|---|---|
| Sabine Pass | 4.51 | 4.56 | 0.99 |
| Plaquemines (Phases 1 and 2) | 3.82 | 3.85 | 0.99 |
| Corpus Christi (with Stage III) | 3.13 | 4.54 | 0.69 |
| Freeport | 2.30 | 2.37 | 0.97 |
| Cameron | 2.10 | 1.98 | 1.06 |
| Calcasieu Pass | 1.58 | 1.76 | 0.90 |
| Cove Point | 0.86 | 0.76 | 1.13 |
| Elba Island | 0.43 | 0.44 | 0.98 |
| Golden Pass (Train 1) | 0.22 | 0.80 | 0.27 |

All terminals exported 16.5 bcf/d in July 2026 against 21.1 bcf/d of peak and 16.1 of baseload capacity in operation and commissioning. The plants run near their peak nameplate; the two still ramping (Corpus Christi Stage III, Golden Pass) below it; Cameron and Cove Point a little above it, which a nameplate rating allows in cold months and a monthly volume's heat content may account for (not checked).

## Errors

- **"n/a" stopped the first trial** (Lake Charles's FERC quantity): it is no figure, like "Note A", and is kept in `x_marks`.
- **The first cross-check paired two terminal codes wrongly** (my guess of YCRP and YCCPL); read from `eia_gas_trade_monthly`'s names and run again.
- **The write's metadata patch conflicted in the branch** (its context lines were the main checkout's): the four added rows (coverage, `docs/coverage.md`, the archive manifest, sources) were put in their sorted places by hand (`runs/c057/s2021/insert_rows.py`), the conflicted files restored from the branch first; no row twice.
- **A collision with chain 059's agent in the main checkout:** `runs/c045/write_table.sh` releases the data lock before it puts main's metadata files back, so its `git checkout` at 19:03:04 ran outside the lock, and chain 059's locked Method-cell run began at 19:03:07. Both other agents (chains 058 and 059) were told; both answered that their worktrees kept nothing from it (chain 059 rebuilt its coverage from its own HEAD). From here this chain uses `runs/c057/write_table.sh` (chain 058's script: the lock waited for, and released only after main's files are put back) and `runs/c057/method_cells_locked.sh` (chain 059's).

## Decisions made without you

- **This source, of the session's own choosing,** said above.
- **Commissioning left without a standard status;** a new status waits for a ruling on the vocabulary.
- **Capacity in x_ columns, `capacity_mw` empty:** a gas plant's capacity is not MW.
- **One quarter's file:** each quarter is a new file name (`--file`); earlier quarters are not taken.

## For Samuel's ruling

- Whether "commissioning" should join the standard's statuses (four LNG rows, and others like them).

## Files

- New: `warehouse/connectors/eia_lng_liquefaction.py`, `tests/test_session2021.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c057/s2021/`, `runs/license_reads/s2021/`, `runs/s2021*`, `warehouse/raw/eia_lng_liquefaction/`, `runs/c057/write_table.sh`, `runs/c057/method_cells_locked.sh`.
