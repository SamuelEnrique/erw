# Session 381 report: the five sellable tools against roadmap item 2

21 October 2026, about 01:50 to 02:35 UTC, unattended, on samueloldlaptop (the code machine), the second part of session 381 in the chain of 20 to 21 October (`queue/done/014-night-20-october-code.md`). Worktree `C:\Users\lossa\Documents\erw-381`, branch `wip/381-five-tools`, cut from `main` at `dc4d5ba6`. Model spend USD 0; no pull from any publisher; no warehouse data written; no page and no default figure changed.

## Read these first

- **Each of the five packs now opens with "## Against roadmap item 2 (session 381)"**: one table a tool, a row for each part of item 2's "done" (a method note signed by Samuel, a replication a reader can run, a cross-check table against published figures, a decisions block), and for Research and the Grid tool a row for their own words ("Automated Analysis in its final form", "the Grid tool one page"). Each row says what the tool has, where, what was run today with its exit code, and what it lacks.
- **No method note is signed.** None of the five has a signature in any file; only the datacenter note has a block to sign in (`datacenter_pays_algorithm.md`, "Sign-off", blank).
- **Research's replication did not run for a reader, and now one does.** The `.py` each card downloads is its generator: run from `site/public/findings/` it fails, 11 of 11, `ModuleNotFoundError: findings_common` (and it would read the warehouse's tables). New: `site/public/findings/erw_2026_research_replication.py`, standard library and numpy, reruns the nine library cards' figures from their CSVs alone: exit 0, and with `--json site/data/findings` 304 of 304 figures equal to the cards' JSON (relative tolerance 1e-7, p-values included). It is not linked from `/research` (a page change, for your ruling).
- **The Grid tool and Research now have a "Cross-checks" section in the decision tools' form** (our figure, the published figure, source and date, gap, reason): `docs/methods/grid_network.md#cross-checks` (11 rows, all figures the ERW already holds with their source: Form EIA-923, EIA-930's own balance and bulk file, CAISO's own supply, two operators' reports of one tie) and `docs/methods/automated_analysis_findings.md#cross-checks` (4 rows; three of them against your thesis, not a publisher). Nothing was fetched.
- **The checks that read the built site were not run.** The local production build stopped twice on Supabase statement timeouts (`Supabase entities: HTTP 500 ... canceling statement due to statement timeout`, on the home page's required read, 10 and 16 timeout lines); not a fault of the branch, which changes no page code. A third attempt after the suite stopped the same way.

## The landing of 367 to 371 (first part)

Written by the orchestrator.

## What to review

- The five tables, on the branch: `https://github.com/SamuelEnrique/erw/blob/wip/381-five-tools/docs/reviews/packs/battery.md` (and `generator.md`, `datacenter.md`, `research.md`, `grid.md`), each above part 1.
- The new replication: `https://github.com/SamuelEnrique/erw/blob/wip/381-five-tools/site/public/findings/erw_2026_research_replication.py`; run `cd site/public/findings && python erw_2026_research_replication.py --json ../../data/findings`.
- The two new cross-check tables: `docs/methods/grid_network.md` and `docs/methods/automated_analysis_findings.md`, section "Cross-checks", on the branch.
- The packs index, `docs/reviews/packs/README.md`: the plain block names the new mirror, and the sentence that called each card's `.py` its mirror is corrected.

## Checks

Outputs under `C:/Users/lossa/Documents/erw/runs/chain_oct21/s381/` on the code machine.

| Check | Exit | Result |
|---|---|---|
| Battery mirror, `python erw_2026_battery_replication.py` in `site/public/battery` | 0 | USD 81.40 per kW over October 2025 to September 2026; USD 8,140,219 for 100 MW; NPV USD -69,779,883; a bad month USD 475,477 (2024-12) |
| Datacenter mirror, in `site/public/datacenter` | 0 | USD 33.73 per MWh, a flat load at `LZ_NORTH`; USD 29,546,505 for 100 MW |
| Generator mirror on `erw_2026_generator_hourly.csv`, in `site/public/seller` | 0 | USD 59.85 per kW; price received USD 23.27 per MWh; coverage 0.67 times |
| Grid mirror on the committed CSV (the hour 2026-10-12 03:00 UTC) | 0 | as part 8 of the Grid pack |
| `write-grid-replication.mjs` into `runs/.../grid_rep_today.csv` | 0 | the hour 2026-10-19 03:00 UTC, 46 hours behind, 70 nodes, 157 of 157 pairs, 7 demand rows, 0 generation rows (EIA-930's generation for that hour not held in the live set when read) |
| Grid mirror on today's CSV | 0 | lag 46; the gravity figures not held |
| Each card's own `.py` download, run from `site/public/findings` (11) | 1 each | `ModuleNotFoundError: No module named 'findings_common'` |
| `erw_2026_research_replication.py` (no argument) | 0 | the nine cards' figures printed |
| `erw_2026_research_replication.py --json ../../data/findings` | 0 | 304 figures compared, 0 different |
| The pack and replication tests: `test_session381`, `262`, `269`, `263` to `266`, `267_findings`, `315`, `323`, `352` | 0 | 122 tests, OK |
| `npm ci` in the worktree's `site/` (under the mutex) | 0 | |
| `npm run build`, first | 1 | the home page's prerender: `Supabase entities: HTTP 500 ... statement timeout` (10 timeout lines in the log) |
| `npm run build`, run once more | 1 | the same, 16 timeout lines |
| The whole suite, `ERW_LOCK_EXEMPT=1 python -m unittest discover -s tests` | 1 | 4,716 tests, 2 failures, 248 skipped (487 s). Neither touches this branch's files (its only site change is the new file in `public/findings/`): `test_session166`'s board builder counts 3 skipped ancillary tables against 4 (the NYISO table is "held, license needed" on this machine), and fails the same way on the base `dc4d5ba6` in a clean worktree; `test_session156`'s node tests, 17 of 20 of `site/scripts/test-ask-ready.mjs` (cases 10 and 18 read the site's ask fixtures, the Texas curtailment share among them), the same alone on the branch. Not fixed: neither is this session's |
| `npm run build`, a third attempt after the suite | 1 | the same home-page prerender, `Supabase entities: HTTP 500 ... statement timeout` (4 lines) |
| `check-cross-checks.mjs`, `check-decisions-face.mjs`, `check-analysis.mjs`, `check-grid-replication.mjs`, the mirrors' headline figures against the pages | not run | no build to serve; nothing listened on port 3381 at the end |

## Decisions made without you

1. **The table goes above part 1 of each pack** and `tests/test_session262.py` admits one optional heading, "## Against roadmap item 2 (session 381)", before the nine parts; every other rule of the pack form is unchanged and passes.
2. **"Signed" means a signature in a file.** The battery and generator notes say "written for sign-off" and have no block; the datacenter note's block is blank. All five rows say "not signed". No sign-off block was written into the four notes that lack one: its words (what signing accepts) are yours.
3. **Research's replication is one mirror of the do-files, not a fix of the cards' `.py` downloads.** The downloads are the generators, which need the warehouse; the mirror needs only the CSVs a reader downloads. It covers the nine cards of the library at their defaults (the two superseded cards are left out). It compares with the cards' JSON only when given the folder, since the JSON is not a download.
4. **No page was changed**, so no snapshot was taken and nothing was deployed (the branch is `wip/`): a "Checked against" line on `/grid` and `/research`, a link to the Grid and Research replications, a decisions block on `/research` and question 5's answer in the Grid's block are each listed as lacking, not built.
5. **Cross-check rows only from figures already held with their source.** ERCOT's 2023 peak record (85,508 MW) is listed, not tabled, because the note that quotes it names no address. ISO-NE, MISO and NYISO against EIA-923 are listed with their percent gaps only: no note gives their totals, and `eia_annual_crosscheck_ba` is not in the live set (a read on 21 October answered PGRST205, "Could not find the table"), though the Grid pack's question 5 says both tables are.
6. **The build was tried a third time after the suite**, beyond the prompt's "run once more", because the checks of the five tools need it and the database had answered the replication writer in between. It stopped on the same timeout; the site's checks are left for the next session with a build (commands below).

## For Samuel's ruling

1. **The five signatures**, and a sign-off block for the four notes that have none (the datacenter note's block is the model).
2. **Research's `.py` downloads do not run for a reader**: (a) ship `findings_common.py` beside them and say they need the warehouse's tables; (b) replace the download with the new mirror; (c) keep them as the record of how the card was made and say on the card that the do-file and the mirror are the replication.
3. **A link from `/research` to `erw_2026_research_replication.py`**, and from `/grid` to its three replication files (both are page changes).
4. **A decisions block on `/research`** saying the rulings of 19 October (1b, 2a, 3a, 4b, 5b, 6a), as the Grid's says those of 18 October.
5. **"Checked against" lines on `/grid` and `/research`**, counting the new tables as the three decision pages count theirs.
6. **Whether a row against your thesis counts as "against published figures"** for Research (three of its four rows).
7. **Question 5's answer on the Grid page**, and `eia_annual_crosscheck_ba` into the live set (the data machine), which the pack says is done and the live set does not hold.
8. **Whether "Automated Analysis in its final form" is met** by session 315's form.

## To finish (the site's checks, when a build completes)

From `C:/Users/lossa/Documents/erw-381/site`, under the build mutex, after `npm run build` and `npx next start -p 3381`, each redirected to a file and its exit code read:

```
node scripts/check-cross-checks.mjs http://localhost:3381
node scripts/check-decisions-face.mjs http://localhost:3381 <out-dir>
node scripts/check-analysis.mjs http://localhost:3381
node scripts/write-grid-replication.mjs <out-dir>/grid_rep.csv
PYTHON=C:/Users/lossa/Documents/erw/.venv/Scripts/python.exe node scripts/check-grid-replication.mjs http://localhost:3381 <out-dir>/grid_rep.csv
```

Then write each exit code into the "Today" cell of the five packs' tables (the cells that say "not run on 21 October").

## Files

- `site/public/findings/erw_2026_research_replication.py` (new)
- `tests/test_session381.py` (new); `tests/test_session262.py` (the optional heading)
- `docs/reviews/packs/battery.md`, `generator.md`, `datacenter.md`, `research.md`, `grid.md` (the new section); `docs/reviews/packs/README.md` (the plain block)
- `docs/methods/grid_network.md`, `docs/methods/automated_analysis_findings.md` (the "Cross-checks" sections)
- `archive/sessions/SESSION_381_REPORT.md`
