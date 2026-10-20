# Session 359 report: ERCOT's four coincident peaks

20 October 2026, from 10:11 UTC, unattended, on lab-desktop (the data machine), the third session of the chain of 20 October, night. Model spend USD 0. Pulls: ERCOT 8 of the ceiling of 20 requests.

## Read these first

- **`ercot_4cp_intervals`: 28 rows, the four summer intervals of 2018, 2019, 2020, 2022, 2023, 2024 and 2025**, each with ERCOT's coincident peak load (the Total row of its Four Coincident Peak Load Calculation) and, from 2022, ERCOT's posting date. Validated, in coverage, loaded (live set, `review_hold`), in the Redivis draft.
- **2021 is not held anywhere ERCOT still publishes it**: the NP9-83-M list keeps four workbooks (2022 to 2025), and the page's historical zip ends with 2020. Not filled.
- **The summer of 2026 is not published yet.** ERCOT posts the year's calculation in late November (the protocols: by 1 December). ERCOT's pages hold no separate monthly document of the interval; the prompt's "monthly peak intervals" are these workbooks' four columns.
- **ERCOT prints each interval's time without saying start or end.** The table reads it as the interval's end, as ERCOT's settlement and price reports name intervals, and keeps ERCOT's words in `x_interval_local`: a reversible reading, said in the note.

## What to review

1. `docs/methods/ercot_4cp.md` (the shape landed first, 09:02 UTC; the source and the figures added here).
2. `warehouse/connectors/ercot_4cp.py`; `tests/test_session359.py` (4 tests).

## Pulls against their ceilings

| Pull | Ceiling | Used |
|---|---|---|
| ERCOT | 20 | 8: the 4CP page, the NP9-83-M product page (for its report type, 13037), the list, four workbooks, the 1996-2020 zip, 1.5 seconds apart. The first five files were taken by a script of this session before the connector existed; the connector's manifest records them, and its `--pull` finds them held |

## Checks

| What | Exit | Notes |
|---|---|---|
| `ercot_4cp.py --write` (data lock) | 0 | 28 rows; the first two tries failed on my reading of the Total row (the label sits in the second column) and on the lock (below) |
| `erw_validate.py` | 0 | PASS |
| `build_coverage.py --only '^ercot_4cp_intervals$'` | 0 | 1 row built, 208 carried over |
| `load.py --only '^ercot_4cp_intervals$' --no-vacuum` | 1 | 28 written, match; exit 1 the other machines' sources, as in session 358 |
| `redivis/upload.py` | 0 | count(*) 28 |
| `tests.test_session359` and the lock's tests (149, 170, 181, 185, 188) | 0 | |

**`warehouse/lock.py`'s wait crashed** when the lock was released between its try and its look (`TypeError: 'NoneType' object is not subscriptable`): fixed, a holder that is gone is a reason to try again, within the same deadline.

## Decisions made without you

1. **The printed time is the interval's end** (above).
2. **The Total row is the figure**, not a sum the ERW makes: ERCOT's own note on what it excludes (DC tie exports, block load transfer exports, wholesale storage load) is in the header.
3. **The 2019 workbook is ERCOT's revised one** (PUC Docket 50333), the only 2019 file in the zip.

## For Samuel's ruling

- Whether to ask ERCOT for 2021's workbook (an information request), or leave the year out.

## Files

- New: `warehouse/connectors/ercot_4cp.py`, `tests/test_session359.py`, this report.
- Changed: `docs/methods/ercot_4cp.md`, `warehouse/lock.py`, `warehouse/supabase/live_set.yaml`, coverage, `sources.csv` (`ercot:NP9-83-M`), the release package.
- Outside git: `warehouse/output/ercot_4cp_intervals.csv`; `warehouse/raw/ercot_4cp/`.
