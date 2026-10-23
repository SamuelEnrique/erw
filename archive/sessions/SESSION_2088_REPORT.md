# Session 2088 report: six held tables described (the operators' load, CAISO's emergencies, ERCOT's 4CP, SPP's curtailment)

23 October 2026, from 21:19 UTC (its first precheck failed on a transient push check and passed on the second), on lab-desktop (the data machine), the fifth session of `queue/done/068-day-26-october-data-mexico-renewables-loans-credits-pipelines.md`, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **Six method notes,** for ISO tables that chains 066 and 067's unlanded branches do not describe (their notes were read on origin, so none is written twice):
  - `docs/methods/ercot_zone_load_hourly.md` (926,838 rows, 9 series, 2015 to October 2026; one hour missing, 7 November 2016, blank in ERCOT's own workbook; the eight weather zones sum to ERCOT's total within 1 MW in every hour but 48 on 17 and 18 May 2021)
  - `docs/methods/nyiso_zone_load_hourly.md` (749,595 rows, 11 zones, 2019 to October 2026; the zones' sum equals EIA-930's NYISO demand within 0.005 percent in all 1,022 shared hours)
  - `docs/methods/isone_zone_load_hourly.md` (131,319 rows, 9 series, 2025 to September 2026; the eight zones sum to ISO-NE's own total; EIA-930's ISO-NE demand differs by up to 14 percent in most shared hours, said and not explained)
  - `docs/methods/caiso_grid_emergencies.md` (1,906 notices on 815 days, 1998 to October 2026, by type and by the reader each came from)
  - `docs/methods/ercot_4cp_intervals.md` (28 intervals, seven summers, 2021 not held; each 0.07 to 0.56 percent above ERCOT's native load in its hour)
  - `docs/methods/spp_curtailment_daily.md` (38,432 rows, 16 series, March 2014 to October 2026; every solar value before 27 October 2022 is a 0 the code writes for a missing column, said so)
  Each count was recomputed by this session from the tables read past their header lines. Their Method cells are filled; the rows' other cells are kept as the branch had them (a rebuild would have moved their last-run dates to this machine's older copies).
- **Contradictions found, the descriptions corrected** (no rule of the code changed; the 15 test files that import these connectors pass):
  - `caiso_emergencies.py` said which reader takes which years (records 2016 on, matrix 2005 to 2015, stages 1998 to 2004, day lists 1998 to 2001); in the rows, records 2011 on, stages 1998 to 2010 (its test comes first and also takes the 2005 to 2010 matrix tables, which carry stage columns) and day lists 1998 to 2004, and no row from the matrix reader. The docstring now says so and the header's `x_layout` line names the readers without years.
  - Its header listed `power_watch` among the event types; the code files Power Watch under `flex_alert`, as Decision 35 says. Corrected.
  - It said "one row per notice type, region and day"; its repeat rule also keys on the time frame (43 type, region and day combinations hold 141 rows). Corrected in the docstring and header; Decision 35's wording in `docs/datastandard.md` is left for a code session, since decisions are a record.
  - `nyiso_zone_load.py` called the table public; the license record has held NYISO's tables "license needed" since 21 October 2026 (NYISO, read 5). The docstring now says so; the flag itself is not changed (default-neutral).
  - `docs/methods/ercot_4cp.md` said `x_published` is the date "as the document states it"; the code takes the report list's PublishDate. Corrected.
- **Not changed, for a code session:** `caiso_emergencies.py` and `curtailment.py` (`run_spp`) do not ask `iso_prices.paused()` before reaching their publishers, which CLAUDE.md asks of every connector (no effect today: neither publisher is paused).

## Decisions made without you

- **The notes drafted by a helper agent in the chain's worktree, and checked by this session,** as sessions 2004, 2032 and 2038 did.
- **ISO tables, not EIA's,** since chains 066 and 067 took EIA's and CAISO's other tables.

## For Samuel's ruling

- None new.

## Files

- New: the six notes above, this report.
- Changed: `warehouse/connectors/caiso_emergencies.py`, `nyiso_zone_load.py` (descriptions and header lines), `docs/methods/ercot_4cp.md`, `docs/coverage.md` (the Method cells).
- On the data machine only: `runs/c068/s2088/`.
