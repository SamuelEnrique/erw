# Session 312: the Redivis release prepared, and the Python advisories

19 October 2026, 12:25 to about 12:55 UTC, unattended, on lab-desktop (the data machine), the eighth session of the chain of 19 October. Model spend USD 0. Pulls: none from any publisher (PyPI only, for the dependency).

## Read these first

- **Roadmap item 9 is ready up to the click.** The package (session 275's, rebuilt today): 126 tables and the three metadata tables in v1, and 41 held out for a license. `grid_stress_days` joins the held list (session 311). Each table's description, license line and citation are in `docs/redivis/release-v1/`. **New: a one-page runbook, `docs/redivis/release-v1-runbook.md`**, which says what to run, open, compare and press. **New: the citation line and the version on `/data`** (`site/app/data/page.tsx`, under the Redivis paragraph: "How to cite a table ... version v1 ... pending release"). Nothing was released, and nothing was deleted from the draft.
- **M7: this machine now runs cryptography 50.0.2** (from 46.0.7, with its four advisories), with lxml 6.1.3 and setuptools 84.0.0 already past theirs. **The runner cannot move:** gridstatus 0.36.0, the newest on PyPI today, pins `lxml~=5.3`, `cryptography<47` and `setuptools<79`. This is written in `requirements.txt` and is for your ruling.
- **On the new version the validator passes on all 201 tables (exit 0).** The package tests here are not green: 49 failures, of which 47 are row counts or partitions against `docs/coverage.md`, because this machine's copies of the runner's tables are at other days than the coverage rows. The other 2 were real faults in session 306's two tables (no parseable `Source:` line; `grid_stress_days` not marked derived) and are fixed: 8 of 8 pass.
- `docs/coverage.md` agrees with `coverage.csv` (201 tables each; every table this chain rebuilt went through `build_coverage.py --only`). The full rebuild is left to the daily run on the runner, because a full build here reads this machine's older copies of the runner's tables (session 271's trap).

## What to review

1. `docs/redivis/release-v1-runbook.md`.
2. The `/data` paragraph (`site/app/data/page.tsx`): its words are the code machine's to adjust.
3. `requirements.txt`'s note on the three pinned packages, and `requirements-py314.txt`'s cryptography line.

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py --what "session 312"` | 0 | |
| `pip install --no-deps cryptography==50.0.2`, then importing cryptography, gridstatus, pdfplumber, supabase and redivis | 0, 0 | |
| `pip check` | 1 | only gridstatus's four known pins (certifi, cryptography, lxml, setuptools) |
| `erw_validate.py warehouse/output/*.csv` | 0 | 201 PASS |
| `pytest package/tests` | 1 | 49 failed, 649 passed: 47 against coverage on this machine; 2 real, fixed |
| `pytest package/tests -k "battery_sourced_ranges or grid_stress_days"` after the fix | 0 | 8 passed |
| `sourced_ranges.py`, `stress_days.py`, `table_stores.py` for both, `load.py --only` both, under the lock | 0 | sources 318 (`erw:grid_stress_days` registered) |
| `release_v1.py`, `--check` | 0, 0 | 126 in v1, 41 held |
| `npx tsc --noEmit` | 2 | 20 errors, none in `app/data/` (a stale `.next` type file and `app/research/[week]`, before this session) |
| tests 207, 215, 282 (the `/data` page) | 0 | 32 tests |

## The landing

- freeze 0; before `s312-before` 12:46:42 UTC; merged origin/main; pushed 12:46:49 (`1252a4fe`); deployment 7174161557 success 12:48:08 (the `/data` change built); after `s312-after` 12:48:20; compare: **0 differences on 25 pages** (expected: `/data` is in review, so a visitor sees the in-review page).

## Decisions made without you

1. **The runbook is a page of its own beside session 275's steps**, which keep the reasons. The steps' counts now read 41 held, of which 35 are held only for ISO-NE's, MISO's and NYISO's rows.
2. **The runner's dependencies are left as they are**, held by gridstatus's pins; moving them needs a gridstatus release, or `--no-deps` on the runner, which is a change to the daily run.
3. **The coverage builder is not run in full here** (above).

## For Samuel's ruling

- M7 on the runner: wait for a gridstatus release that relaxes `lxml`, `cryptography` and `setuptools`, or install the runner's environment with `--no-deps` from an exact list (as on this machine).
- The click itself (`docs/redivis/release-v1-runbook.md`), on or after 21 October.

## Files

- New: `docs/redivis/release-v1-runbook.md`, this report.
- Changed: `site/app/data/page.tsx`, `docs/redivis/release-v1.md`, `docs/redivis/release-v1/`, `requirements.txt`, `requirements-py314.txt`, `warehouse/connectors/sourced_ranges.py`, `warehouse/derived/stress_days.py`, `package/tests/test_erw.py`, `warehouse/metadata/sources.csv`, `coverage.csv`, `docs/coverage.md`, `archive_manifest.csv`, `redivis_uploads.csv`; session 311's report (its landing).
