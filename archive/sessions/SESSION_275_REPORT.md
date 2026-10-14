# Session 275 report: Redivis release v1, prepared

14 October 2026, 10:24 to 10:40 UTC, unattended, on lab-desktop (the data machine), the fifth session of the overnight chain of 14 October, built in a worktree (`../erw-275`) while session 273's pull ran. Branch `task/275-redivis-v1`. Model spend USD 0: no model call. Pulls: none. **Nothing was created, changed or released on Redivis.**

## Read these first

- **The package for one click is in `docs/redivis/release-v1/`; the steps are `docs/redivis/release-v1.md`.** Eight steps, about 20 minutes, on or after 21 October 2026: rebuild and check the package, reconcile the draft, remove the 40 held tables from the draft, paste the README, spot-check, click Release, record the date.
- **v1 is 125 tables and the three metadata tables.** Every table coverage flags public that is still public on 21 October. 40 tables of the public draft are held out, each with its reason in `tables.csv` (a publisher's terms ask for permission or a license not recorded).
- **Each table has its description, license line and citation** (`tables.csv`), and every series variable with its unit and every column of the other tables (`variables.csv`, 3,766 rows). The license line is the table's own header line where it has one (95 tables), else the license record's verdict (30 tables, "may be public" by the publisher's own terms).
- **One thing the click cannot fix by itself (ruling 1):** the uploader routes by coverage's flag, so a held table whose data changes goes back into the public draft; step 4 says to remove them right before the click.

## What to review

1. `docs/redivis/release-v1.md`: the steps and the three rulings.
2. `docs/redivis/release-v1/README.md`: what the dataset's page would say.
3. `docs/redivis/release-v1/tables.csv`: filter `in_v1 = no` for the 40, and read a few citations.

## Checks

| What | Exit | Notes |
|---|---|---|
| `python scripts/precheck.py --what "session 275"` | 0 | six of six |
| `python warehouse/redivis/release_v1.py --out-dir <the main checkout's warehouse/output>` | 0 | 128 in v1 with the metadata tables, 40 held out; 3,766 variables and columns |
| `python warehouse/redivis/release_v1.py --check` | 0 | 0 differences |
| `python -m unittest tests.test_session275` | 0 | 4 tests |

## Decisions made without you

1. **The 34 tables held only by grid on the site are held out of v1 whole.** A copy without ISO-NE's, MISO's and NYISO's rows would be a new table; ruling 2.
2. **The package is rebuilt on the day** (step 1), so a permission recorded before then moves a table into v1, and tonight's later sessions need not keep it current.
3. **The dataset's README credits the IRW** as the ERW's own CLAUDE.md does.
4. **Who clicks is left open** between the owner's account and Ben Domingue's organization (`owner_kind: user` today); ruling 3.
5. **No read of Redivis either:** the reconcile in step 2 is the person's.

## For Samuel's ruling

1. Route a held table to the private dataset from its date (one change to `upload.py`), so the public draft stays as v1 left it?
2. The 34 by-grid tables: held out whole, or a public copy without the held grids' rows?
3. Who clicks: the owner's account, or the dataset moved to Ben Domingue's organization first?

## Files

- New: `warehouse/redivis/release_v1.py`, `docs/redivis/release-v1.md`, `docs/redivis/release-v1/` (`tables.csv`, `variables.csv`, `README.md`), `tests/test_session275.py`, this report.

## The landing

- In session 273's report.
