# Session 636 report: one more source: crude oil imports by origin, destination and grade, finished

22 October 2026, from 06:15 UTC, on lab-desktop (the data machine), a session of `queue/done/040-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **New table `eia_crude_imports_detail_monthly`: 154,779 rows, 7,406 series, January 2011 to July 2026.** U.S. crude oil imports by country of origin, destination and grade, from EIA's company level imports (route `crude-oil-imports`, Form EIA-814), in `kbbl`.
  - The destinations are the U.S., port PADDs, port states, ports, refinery PADDs, refinery states and refineries. The grades are light sweet, light sour, medium, heavy sweet and heavy sour.
  - Session 632's connector and 29 saved pages, and this session's 2 requests (the rest of the route).
- **Why this source**: session 632 had stopped short of the end of it. Finishing it under this session's ceiling gave a table the ERW does not hold (imports by refinery and by grade), where a new source would have left 29 saved pages unused.
- **EIA's count is larger than its pages.** EIA counts 160,665 records on every page, but its pages hold 154,779: the last page was short (4,779 records) and ended at the latest month, July 2026. EIA's plant outages route did the same.
  - All 187 months from January 2011 to July 2026 are there, from 591 to 1,174 records a month, and no key repeats.
  - The connector now takes a short read only when every month from the first to the last is there, writes EIA's count and the rows read in the header, and stops when a month is missing.
- **Cross-checks against `eia_crude_imports_by_country`** (EIA's imports by country of origin, in `kbbl/d`; the U.S. destination summed over grades and divided by the month's days):
  - **all countries against the U.S. total** (MCRIMUS2), 187 months: median ratio 1.000, from 0.955 to 1.040, within 1% in 167;
  - **Saudi Arabia** (MCRIMUSSA2), 186 months: median 1.000, from 0.752 to 1.005, within 1% in 170;
  - **Canada** (MCRIMUSCA2), 187 months: median 1.000, from 0.966 to 1.009, within 1% in 182.
- **Written under the data lock** (06:19 UTC) with `--offline` (0 requests). The validator, coverage `--only` and the archive exited 0 (154,779 rows archived). Each table has one row in the metadata files. Release rows added; `licenses.py check` 0 problems (290 tables). **Held** from `/data` and Redivis v1. Sector rule (`oil`). Tests: `tests/test_session636.py`, 4.

## Decisions made without you

- The short read taken when every month is there, as above. It is a rule for this route; a missing month still stops the run.
- 2009 and 2010 (about 22,000 records) are left for an early window in a later session.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 2 of 20 | the pages at offsets 145,000 and 150,000 (the 29 earlier pages reused) |

## Files

- New: `tests/test_session636.py`, this report. Changed: `warehouse/connectors/eia_crude_imports_detail.py` (the ceiling, the short read), the sector rule, both holds, the release package, the license record, coverage, sources and the archive manifest.
