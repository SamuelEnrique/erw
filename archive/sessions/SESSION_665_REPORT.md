# Session 665 report: the erw package against the Stanford draft

22 October 2026, from about 09:58 UTC, on lab-desktop (the data machine), a session of `queue/done/043-night-23-october-data-redivis-gaps.md`. Model spend USD 0.

## Read these first

- **The package's Redivis backend now opens the Stanford dataset**: `erw.RedivisBackend(owner="datapages", dataset="erw:b9wm", owner_kind="organization")`, or `ERW_REDIVIS_DATASET=datapages.erw:b9wm`. It listed the draft's 187 tables (the 186 public tables and the starter; the metadata tables are left out of the list) and read its version (`datapages.erw:b9wm:next`, unreleased, "not citable").
- **A stream of rows is refused; an export is not.** Redivis refuses every streamed read (`to_pandas_dataframe`): "Cannot stream more than 100GB to external environments within a 30 day period. Please use the export API instead." The cap is the token's user's, reached on 15 October (session 305). The backend now falls back to the table's CSV export when the stream is refused (as the uploader's `read_frame` reads), keeping numbers as exported and retyping only dates.
- **Two of the five tables are proven against the local files through the export:** `ercot_peak_premium_annual` (derived series) and `eia860m_retired_generators` (entities): `fetch` equal row for row, with the same provenance header from `erw_headers`. The other three (`ercot_grid_notices`, `eia_fuel_spot_prices`, `eia_drilling_monthly`) and `cite`, `coverage` and `filter` were not run: the session's ceiling of 100 requests was reached (an export read costs about 8).
- **The exact test for the rest:** `ERW_REMOTE_TESTS=1 python -m pytest package/tests/test_backends_stanford.py -v -m remote` (11 tests; about 80 requests).
- **`llms.txt`** names the Stanford dataset as a backend and gives its citation line with its DOI, `10.57761/4f55-6d55`.
- The chain asked for the package against a released version where only that is possible: the backend reads the draft (`version="next"`) as well as a released tag, so nothing waits on the click except the citation itself.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| Redivis API | 100 of 100 | the trial (9: the dataset, the table list, one refused stream), the remote tests refused (6), the export read's first run (53: one table passed, one failed on how a float prints), its rerun of that table (32, passed) |

## Decisions made without you

- The Stanford test is a module of its own rather than a third parameter of `test_backends.py`: that file's events table, `news_index`, is unsettled by its ERW verdict and not in the Stanford dataset; `ercot_grid_notices` stands in.
- The package's default backend is unchanged (the owner's account), as the uploader's is.
- When a stream is refused for the cap, the backend reads the table's export instead of failing: same rows, a slower read. A refusal for any other reason still fails.

## For Samuel's ruling

- Redivis's 30-day streaming cap on the token's user: exports still work, but they count against the separate 100 GB export allowance the daily restore also uses (2 GB a day by `config.yaml`). Whether to ask Redivis or Datapages for an organization's allowance.

## Files

- Changed: `package/src/erw/remote.py`, `package/llms.txt`. New: `package/tests/test_backends_stanford.py`, this report. On the data machine only: `runs/s665/`.
