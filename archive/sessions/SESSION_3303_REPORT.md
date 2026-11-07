# Session 3303 report (chain 200, session 4 of 13): the method note, the tracers, the cross-checks

lab-desktop, 6 November 2026, 19:35 to 19:40 UTC. Branch `wip/3300-companies`.

## What was done

- **`docs/methods/companies.md`**: what the three tables are, the inputs and their roles, the seven rules, every column of `company_directory`, the licenses, the tracers, the cross-checks, what the tables cannot say, the history.
- **`warehouse/derived/check_companies.py`**: five tracers (each link's row exists in its input; its name is in that row's column for the role; the directory and the links name the same companies; the directory's 23 counts and MW recomputed from the links alone, by code written apart from the builder's, agree to 0.1 MW; every alias is a name of the links). On the written tables: **0 failures over 96,964 links, 13,964 companies, 25,877 aliases** (exit 0).
- **The cross-checks**, written as checks, not corrections: `docs/reviews/companies-crosscheck-2026-11-06.md`.
  - A utility's EIA-861 retail sales (2025, the newest year with at least 80% of the median year's utilities; 2019 holds twice the usual count) against its EIA-860M operated capacity: 295 companies have both; implied use (sales over capacity times 8,760 hours) above 1 for 110 (they buy power), 0.2 to 1 for 166, under 0.2 for 19; median 0.60. Tennessee Valley Authority 0.07; Florida Power & Light 0.36; Public Service Electric & Gas 35.59 (79 MW of its own, 24.7 TWh sold).
  - A developer's queue MW against its deals' MW: no company holds both a live ERCOT or NYISO position and a deal (the deals name brands, the queues project companies).
- **Tests:** `tests/test_session3303_companies.py`, 4 tests (a clean fixture passes; a changed figure, a name not in its row and a row not in its table are each caught); with session 3301's, 24 tests, exit 0.

## Decisions made without you

- The sales year is chosen by rule (the newest near the median year's count), not the newest: EIA-861's 2019 rows hold about twice the utilities of other years, and a plain "newest" would hide that choice.
- The second cross-check is written though empty: its emptiness is itself what it shows.

## For Samuel's ruling

- None new.

## Cost

- No model call. USD 0.00.
