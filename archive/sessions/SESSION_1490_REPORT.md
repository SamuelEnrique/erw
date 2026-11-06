# Session 1490 report: the generator's replication, in Stata, and the method note

Energy Research Warehouse (ERW), session 1490, chain 158, samueloldlaptop, 6 November 2026, 08:56 to 09:02 UTC (while session 1486's gate ran). Model: Claude Opus 5.5 (this window's). Model spend USD 0. No warehouse data written; nothing sent or posted; no web request. Branch `wip/1487-replication`.

## What it did, with commits

- `e58b0ee70`:
  - `replication/generator/replicate.do`: the page's public do-file, generated from it as the battery's was (`runs/s1490/make_do.py`, one script for the three tools). The public hourly file is read by its repository path; the ten defaults come from `assumptions.csv`, where `s_deg` is the degradation; the file ends with the headline figures beside the page's and the difference.
  - `assumptions.csv` and `page_figures.csv`, for Stata.
  - `docs/methods/generator_earns_algorithm.md` section 8.1, "Run it", pointing to the note's "Cross-checks" table and its decisions block (section 13).
- Tests: `tests/test_session1490.py` (the house rules; only the public file and the assumptions read; no default typed as a scalar; the public do-file's steps present; the CSVs equal the JSON): 6 passed.

## Found

- **The do-file has not been run**: Stata is not on this machine (the owner's step). `replicate.py` runs the same steps (13 of 13).

## Decisions made without you

- None.

## For Samuel's ruling

- Your Stata run of `replication/generator/replicate.do`.
