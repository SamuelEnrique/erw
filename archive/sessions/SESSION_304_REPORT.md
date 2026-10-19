# Session 304 report: the replication packages, the code-side rulings of 14 October, and the review note

19 October 2026, from 13:20 UTC, unattended, on samueloldlaptop (the code machine), the tenth and last session of the chain of 19 October (`CHAIN_OCT19_PROMPT.md`). Branch `wip/304-replication` in the worktree `erw-296`, from session 303's commit (not yet landed when this session began: the no-landing window of 14:00 to 16:15 UTC); lands on main as `task/304-replication` after session 303. Model spend USD 0: no model call. No pull, no warehouse data written.

## Read these first

- **The four replication packages rebuild every number on their pages today.** Each has its CSV, do-file and Python mirror (`site/public/{battery,datacenter,seller,grid}/`); each mirror was run on 19 October and its lines compared with the page's checked numbers on the local build. The battery and the datacenter match line for line. **The generator's NPV did not:** the page applies solar's degradation of 0.7 percent a year since session 298 (NPV -76.66 million for 100 MW), and the mirror and the do-file still summed an undegraded annuity (-74.16). Both now sum each year's flow at the hurdle rate with the revenue falling by 0.7 percent a year, as the site's `flows` and `npv` do, and print -76.66; the breakeven PPA price (58.36) is unchanged, since the contract covers the whole of the energy for the whole life. **The grid's package** is rewritten from the page's reads by `write-grid-replication.mjs`; written today, its check read 15 of 60 different, every one a figure the live set does not hold this week (no net generation for the hour shown) that the mirror writes "not held" and the page writes as an empty attribute: the check now reads an absent figure as absent whichever way it is written, and today's file is 60 of 60. **Expected values are written at the top of each do-file** (the lines the mirror printed on 19 October, equal to the page).
- **The rulings of 18 October on items 2, 4, 5 and 10 of `docs/state/morning_2026-10-14.md`.** 2: `test-board.mjs` allows 10 days (it still fails today: Henry Hub's spot close is 13 days old while the daily run fails on the Redivis cap). 4: the tracker says beside its newest figures that ERCOT paused approvals to energize datacenters of 75 MW or more on 3 August 2026, cited to the Batch Zero deck to TAC of 26 August 2026. 5: `/policy` and `/contracts` write "as filed" beside a date after today (none lies after today on 19 October, so nothing shows yet; the code is tested). 10: every verdict in `site/lib/findingverdicts.ts` carries its day, the twelve of 14 October (blocks 29 to 40, session 286) are in it with their reasons copied from the document, and the review list dates each verdict: the four to drop read "dismissed", the eight others "no verdict yet" with what the verification read them as; nothing publishes.
- **The review note** for your thirty minutes: `docs/state/review_2026-10-19_code.md` (what landed, session by session with its address; every screenshot folder; every decision made without you; every item waiting for you).
- **Then the queue step** (rule 12): `python scripts/chain_queue.py next`, recorded at the end of this report.

## What to review

1. `docs/state/review_2026-10-19_code.md`.
2. `https://erw-flame.vercel.app/internal/findings` (the dated verdicts; the twelve of 14 October), `https://erw-flame.vercel.app/datacenters` (the pause beside the newest figures).
3. The top of each do-file: `site/public/seller/erw_2026_generator_replication.do` and the three others.

## What was done

- `site/public/seller/erw_2026_generator_replication.py` and `.do`: the NPV with degradation; the expected values at the top of the four do-files.
- `site/scripts/check-grid-replication.mjs`: an absent figure is absent whichever way it is written; a share the page does not hold is empty, not zero.
- `site/scripts/test-board.mjs` (10 days); `site/app/datacenters/LargeLoad.tsx` (the pause line, `data-load-pause`); `site/app/policy/PolicyTable.tsx` and `site/app/contracts/page.tsx` ("as filed", `data-as-filed`); `site/lib/findingverdicts.ts` (`day` on every verdict, the twelve of 14 October); `site/app/internal/findings/page.tsx` (each verdict dated; dismissed; no verdict yet).
- `tests/test_session304.py` (8 tests), `tests/test_session267_findings.py` (the forty dated verdicts), `docs/brand/review-304/`, `docs/state/review_2026-10-19_code.md`.

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 304"` | 0 | `runs/chain_oct19/s304_precheck.out` |
| The generator's mirror on its CSV, before and after the degradation | 0, 0 | NPV -74.16 then -76.66; every other line the page's (59.85, 102.24, 130.80, 23.27, 32.17, 72, 7,078,769, 0.67, 2,580, 39.14, 58.36) |
| The datacenter's mirror on its CSV | 0 | 33.73, 29,546,505, 0.0684, 49,310, 32.51, 1.22, 35.33, 37.88, 313.01 and the years: the page's |
| The battery's mirror on its CSV | 0 | 81.40 per kW, coverage 2.63, scenario A NPV -69,779,883, IRR -8.8: the pack's part 8 |
| `write-grid-replication.mjs` (today's file), then `check-grid-replication.mjs` on it | 0; 1 then 0 | 234 rows, hour 2026-10-18T03:00Z; 45 of 60 same (15 figures not held this week), then 60 of 60 after the absent-figure rule |
| `tsc --noEmit`, `eslint` on the files touched, `node --check` on the scripts | 0 | no error |
| `npm run build` (worktree, under the mutex) | 0 | `s304_build.out` |
| `test-board.mjs` | 1 | `eia-henry-hub-spot is stale: 2026-10-06`: 13 days on 19 October, past the 10 allowed, while the daily run fails (the data condition of the day, not the rule) |
| `tests.test_session304`, `test_session267_findings`, `240`, `132`, `161` | 0 | 72 passed |
| Screenshots, 1280 and 390, before and after, four pages | | `docs/brand/review-304/` (the tracker and the contracts; the two long pages' shots left out for their size, said in the README) |
| Suite, clean copy, the commit pushed | 0 | `Ran 4414 tests`, `OK (skipped=250)` at `1f342e48` in `../erw-check` (`runs/chain_oct19/s304_suite3.out`); the commit pushed is this report's commit on `cdefdb59`, the merge of the landed main (`59772e15`) into `1f342e48`, whose tree is byte for byte `1f342e48`'s; the report commit changes three documents only (this report, session 303's report, the review note), so the suite and the build of `1f342e48` are the suite and the build of the commit pushed |

## Landing of session 303 (recorded here: session 303's report is in that landing's own commit)

- Pushed `task/303-one-chart-library` at `e294d37b` at 16:18 UTC (the no-landing window of 14:00 to 16:15 UTC honoured); GitHub's checks passed (run 39284436606, https://github.com/SamuelEnrique/erw/actions/runs/39284436606) and merged it as `59772e15`; production served the new build at 16:40:08 (a new style sheet name) and the after snapshot was taken at 16:40:28.
- Snapshot `s303-before` (16:18:23) against `s303-after` (16:40:28): 25 pages, 0 differences. Expected: none of the 25 snapshot pages draws a time-series chart whose checked numbers changed, and every page is in review (the visitor sees the in-review page). Nothing unexpected.

## Landing

- Pushed `task/304-replication` (this report's commit on `cdefdb59`, the merge of the landed main; `git log` names it) after the before snapshot `s304-before`, taken as its own command; `python scripts/freeze.py status` exit 0 (no freeze) before the push; GitHub's check and merge, production's new build and the after snapshot `s304-after` with its comparison are waited for by `runs/chain_oct19/land_wait.sh s304` and written to `runs/chain_oct19/s304/wait_result.txt` (not in git).
- The comparison's lines and the queue step's result are appended to this report in a commit on `wip/304-replication` after this landing (see "Decisions made without you"): a report cannot hold the comparison of the landing that carries it.

## Decisions made without you

- **The generator's package was changed to match the page**, not the page to match the package: the page's default (session 298, your ruling 7a) is the rule.
- **The grid package is verified on a file written today**, as its README asks, and the committed file (session 266's hour) was left as it is: a page in review keeps its committed file, and the check script reads any file named.
- **The expected-values block at the top of each do-file quotes the mirror's own lines**, so a Stata run is compared line by line.
- **Item 10:** the eight non-drop verdicts of 14 October are shown as "no verdict yet" with the verification's reading in grey, not as strong or usable in bold; a draft raised after 14 October reads "No verdict yet (raised after the verifications of 13 and 14 October 2026)".
- **Item 4:** the pause line stands between the headline figures and the chart; the deck is named by its file name and the method note is linked; the deck's two figures for `large_load_statements` are the data machine's (session 308).
- **The review folder leaves out the two long pages** (1.5 to 4 MB a shot).
- **Session 303's report is completed in this commit** (its suite line and its own landing), since that report was in the landing's own commit; this report's own landing and the queue step's result are appended in a commit on `wip/304-replication` after the landing, pushed to that branch only (a wip push deploys nothing), to be merged by you or by the next chain. Every other session of the chain recorded its landing in the next session's report; this is the last.
- Questions skipped (Impeccable's playbooks ask them); Impeccable `detect` on the three page files: see the checks.

## For Samuel's ruling

- The review note's "Waiting for you" list, in one place: `docs/state/review_2026-10-19_code.md`.

## Files

- Changed: `site/public/seller/erw_2026_generator_replication.{py,do}`, `site/public/{battery,datacenter,grid}/*.do` (the expected values), `site/scripts/check-grid-replication.mjs`, `site/scripts/test-board.mjs`, `site/app/datacenters/LargeLoad.tsx`, `site/app/policy/PolicyTable.tsx`, `site/app/contracts/page.tsx`, `site/lib/findingverdicts.ts`, `site/app/internal/findings/page.tsx`, `tests/test_session267_findings.py`.
- New: `tests/test_session304.py`, `docs/brand/review-304/`, `docs/state/review_2026-10-19_code.md`, this report.
- Not in git: `runs/chain_oct19/s304*`.
