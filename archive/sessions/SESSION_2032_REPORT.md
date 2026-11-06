# Session 2032 report: six held tables described (the carbon and macro tables)

23 October 2026, from 19:01 UTC, on lab-desktop (the data machine), the fifth session of `queue/done/058-day-24-october-data-outages-fuels-mines-vehicles.md`, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **183 of the 389 tables in this branch's `docs/coverage.md` have no method note** (its Method column empty). Session 2004 wrote six EIA notes; chain 057's session 2018 runs beside this chain unlanded, and EIA's tables come first in its list, so this session took six source tables of another kind, the carbon and macro tables, and said so:
  - `docs/methods/rggi_auction_allowance_prices.md` (304 rows, 7 series on 2 entities, 85 auctions, 25 September 2008 to 9 September 2026)
  - `docs/methods/carb_auction_allowance_prices.md` (336 rows, 6 series on 2 entities, 56 auctions, November 2012 to August 2026)
  - `docs/methods/carb_lcfs_credit_prices.md` (1,124 rows, 3 series, 402 weeks, 7 January 2019 to 14 September 2026)
  - `docs/methods/frb_treasury_yields.md` (5,856 rows, 3 series, 1,952 days each, 2 January 2019 to 21 October 2026)
  - `docs/methods/imf_commodity_prices.md` (465 rows, 5 series, 93 months each, January 2019 to September 2026)
  - `docs/methods/portwatch_chokepoint_transits.md` (119,616 rows, 42 series on 3 entities, 2,848 days each, 1 January 2019 to 18 October 2026)
- **Each count recomputed by this session** from the tables read past their header lines (rows, series, entities, first and last day, no key given twice), and two of the notes' findings checked again: the 2-year yield above the 10-year on 544 days, 27 August 2019 to 5 September 2024; LCFS's one week dated on a Tuesday, 7 September 2021.
- **Six contradictions between a connector's words and its code or the license record, each corrected in the words** (no rule of the code changed; the 165 tests of the nine test files that import these connectors pass):
  - `carbon_auctions.py` said both tables are internal; CARB's has been public since session 324 (the code and `sources.csv`).
  - `imf_pcps.py` said the IMF's terms page answered 403 and was read only through a search quotation; it was read on 12 October 2026 (read 13, HTTP 200). The docstring and the header line now cite read 13 and the permission a commercial reuse needs.
  - `portwatch.py` said the same of the terms page; the docstring and header line now cite read 13 and keep the table internal by the session 8 ruling.
  - `portwatch.py`'s header said "every run replaces all of it"; the code merges by key (`ip.write_csv`), so a day the service stops serving keeps its row.
  - `carb_lcfs.py` said every week sits on its Monday; the code keeps CARB's date, and one week is dated Tuesday 7 September 2021.
  - `carb_lcfs.py` and `imf_pcps.py` named session 132's 1,500,000-row ceiling; no code counts it.
  The tables' headers take the corrected lines at their next run.
- **Two faults of the code found and not changed here,** for a code session with its tests:
  - None of the five connectors asks `iso_prices.paused()` before requesting its publisher, which CLAUDE.md asks of every connector. No effect today: none of these publishers is paused.
  - `carbon_auctions.py` and `portwatch.py` word their age check without "(limit", so a stale source fails the run instead of being skipped as `iso_prices.gap_skip` intends; `frb_treasury.py` and `imf_pcps.py` use the wording but never call `gap_skip`.
- **The Method cells** of the six are filled by `runs/c058/coverage_rows.sh` once the data lock is free (chain 057's session 2024 held it from 19:09 UTC); its result is in the next commit.

## Decisions made without you

- **The six notes were drafted by a helper agent working only in the chain's worktree, and checked by this session** (each count recomputed, each contradiction read in the code before acting), as session 2004 did.
- **Not EIA tables,** so as not to write the notes chain 057's session 2018 is likely writing at the same time.
- **The descriptions corrected, not the code,** for the two faults above.

## For Samuel's ruling

- Seen again, not new: the IMF's terms (read 13) say "The IMF prohibits bulk download of information by automated technology without explicit permission". `imf_pcps.py` and `portwatch.py` read the IMF's services by script every day. Whether to pause the IMF, as MISO was paused, or to ask the IMF, is yours; this session changed nothing.

## Files

- New: the six notes above, this report.
- Changed: `warehouse/connectors/carbon_auctions.py`, `imf_pcps.py`, `portwatch.py`, `carb_lcfs.py` (descriptions and header lines); `docs/coverage.md` and `coverage.csv` (the Method cells, next commit).
- On the data machine only: `runs/c058/s2032/`.
