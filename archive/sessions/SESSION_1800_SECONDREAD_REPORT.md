# Session 1800 report: the findings hunt's twenty, read a second time

6 November 2026, about 20:45 to REPORT_END UTC, on samueloldlaptop (the third window, a code machine), Fable 5.1 high effort, unattended. Model spend USD 0. Pulls: none. No build, no gate, no data lock, nothing sent.

## Read these first

- **The file:** `docs/reviews/findings-second-read-2026-11-06.md`, one row a draft for the twenty that `findings-ranked-2026-11-06.md` put first, the failing lines with the lines instead, the ten for the owner, and the fixes for the desktop's second window. No draft, script or ranking was changed.
- **There is no public download to reproduce from.** `/api/download` answers 403 ("internal view only, until the owner rules") for all eleven tables the twenty rest on; Redivis `v1.0` holds one starter table; five of the eleven are not in the live set. Every draft's Reproduce sentence promises one. The reproduction ran against the tables rebuilt from the archive bucket instead (a read of the bucket and a write to a scratch folder: no lock).
- **Reproduction:** REPRO_SUMMARY
- **Two figures are wrong or cut short:** draft 17 (Alaska's crude share) sums two series under area code SAK, Alaska and the North Slope, so its share is about twice Alaska's (32.7 percent in 2001 where EIA's Alaska was about 17); draft 12 stops at 2024 while its table holds 2025, and says its first year is 2005 where the table holds 1995.
- **The tolerance is tighter than EIA's revisions:** against the 2 October copies, five of ten 2025 figures missed 0.5 percent of the change (US solar 6.675 against 6.786, Nevada solar 30.283 against 30.786, residential price 173.32 against 172.63, Texas commercial 173.81 against 174.68, wind 10.484 against 10.431); every 2001 figure matched.
- **Stata:** all twenty pass the owner's three rules and mirror their Python; the differing steps are draft 1 (a zero year prints no Stata row), draft 12 (three dates parsed and never used in both) and draft 17 (the Stata's month count would be 12 where the Python's row count is 24, the tell of the double count). No do-file was run: no Stata here.
- **Verdicts:** 13 ready for the owner, 6 fix first (1, 3, 12, 15, 16, 17), 1 drop as a lead (2, Vermont's nuclear share, one plant's closing).

## What it did

- `scripts/precheck.py` passed; `git fetch origin`; a detached worktree of origin's main at `6094b647a` in `../erw-1800` (removed at the end).
- Static checks over the twenty (a scratch script): Expected lines equal between `.py` and `.do`, CSV keys and values, PNGs present, the three Stata rules, dashes.
- `restore.py --from-bucket --out <scratch>` for the eleven tables, run from the main copy so `.env` is read (the first attempt from the worktree found no `SUPABASE_URL`).
- Each `reproduce.py` run alone with `python -I` against its copy, the printed first and last years against the Expected line within its tolerance; the same against the main copy's 2 October tables for the ten it holds.
- The sentence, limits and keys read by hand against `docs/voice.md`, `docs/brand.md`, the table headers and the connectors.

## Decisions made without you

- Session 1800: the first free number at or above 1800 on origin's main and every remote branch (none in the 1800s anywhere; main stands at 1728 and 2000 and above).
- The archive's copies stood in for the public download that does not exist; the file says so in its first finding.
- The verdict column uses three words as the prompt asked: ready for the owner, fix first, drop.

## For Samuel's ruling

- Whether `/api/download` opens for the eleven public tables the drafts rest on, or the Reproduce sentence changes to name the ERW's own file.
- Whether a draft's Expected line should pin the table's vintage, given EIA's revisions of a preliminary year exceed the 0.5 percent tolerance.

## Errors

- The first restore attempt, run from the worktree, failed on every table with "SUPABASE_URL is not set": the worktree has no `.env`. Rerun from the main copy.
- RESTORE_ERRORS

## To finish

- Nothing: the review file and this report are on main. The desktop's second window reads the review at its next chain.
