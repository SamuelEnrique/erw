# Session 2340 report: six held tables linked to the notes that describe them (the price board, the node basis, ERCOT's peak premium by year)

24 October 2026, from 07:45 UTC to 07:49 UTC, on lab-desktop (the data machine), chain 109, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **How the tables were chosen:** 70 tables have an empty Method cell on this branch, on main and on chains 105's and 108's branches (`runs/c109/empty.py`). The agents beside this chain were told which six this session takes.
- **Six `Tables:` lines,** in notes that already describe each table, each checked against the table read past its header lines:
  - `price_board_latest`, `price_board_peak_offpeak` and `price_board_spreads` in `docs/methods/price_board.md`: 3,237, 3,894 and 2,488 rows. The note names their variables by pattern (`{da,rt}_daily_mean`, `_avg_7d`, `_year_peak_mean`, ...), and every variable held fits one.
  - `node_basis_daily` and `node_basis_summary` in `docs/methods/node_basis.md`: 965,943 rows over 888 points, and 1,260 rows of 168 variables. The note's pattern `<market>_<class>_<statistic>` covers the summary's variables.
  - `ercot_peak_premium_annual` in `docs/methods/ercot_peak_premium.md`, whose line named only the monthly table: 2,016 rows, six hubs, 28 variables, 2015 to 2026, all named in the note.
- **The six Method cells set** by `build_coverage.py`'s own `method_cell`.

## Contradictions found

- None.

## Checks

- `tests.test_session674`, `1000` and `1001`: OK.

## Decisions made without you

- None beyond `Tables:` lines rather than new notes, as sessions 2228, 2270 and 2312 did.

## For Samuel's ruling

- None new.

## Files

- Changed: `docs/methods/price_board.md`, `node_basis.md`, `ercot_peak_premium.md`, `docs/coverage.md` (six Method cells). New: this report.
