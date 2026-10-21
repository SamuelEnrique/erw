# Session 422 report: the five tools' checks on a built site

21 October 2026, about 14:11 to 15:35 UTC, unattended, on portable-laptop (the code machine; chain 021 was written for samueloldlaptop and runs here by the owner's instruction to run what the queue prints), in the worktree `C:\Users\samen\Documents\erw-422` on `wip/422-tool-checks` (from `origin/wip/461-combined` at `2289156d`). The chain `queue/done/021-day-21-october-code.md`, session 422. Model spend USD 0; no warehouse data written; no web request; no page, check or mirror changed.

## Read these first

- **Every check session 381 could not run now has an exit code, on a build of main with chain 019's branches not yet landed** (`wip/461-combined`: the build is of what would land, not of production). The build ran at 15:22 UTC under the build lock, with the database gate open (2.86 s).
- **The economics pages and their mirrors agree.** `check-cross-checks.mjs` exit 0, 18 of 18; `check-decisions-face.mjs` exit 0, 144 of 144; the nine default headline figures of the battery, generator and datacenter pages (from the face check's `face.json`) equal the mirrors' to the digit shown.
- **The Grid's replication agrees**: `write-grid-replication.mjs` exit 0, `check-grid-replication.mjs` exit 0, 60 values, 0 different. **Research's mirror agrees**: 304 figures, 0 different.
- **`check-analysis.mjs` exits 1, 269 of 279**, as main holds it: its 10 failures are callouts naming NYISO or ISO-NE, which the cards draw as "license needed" since the holds of 21 October. Session 474 fixed the check on `wip/474-checks` (279 of 279 on production); that version is not in this build, so it was not fixed again here.
- **A runner of mine ran once without the build lock.** The first run of `runs/chain_021/s422/run_checks.sh` gave the lock helper a path Git Bash did not convert (`MSYS_NO_PATHCONV=1` exported over `/c/...` paths), so its `acquire` failed; I stopped the task, but its script went on, and it built and ran the checks from about 14:43 to 15:00 UTC without the lock, while session 419 held it. The second run, with the paths fixed, held the lock; every result in this report is the second run's. The first run's results agreed but for `check-grid-replication.mjs`, exit 1 then (its output was overwritten; the file and the page must be read from the same snapshot, and the two runs read the live set minutes apart).

## What to review

- The five packs, each a new paragraph "On a built site (session 422, 21 October 2026)" at the end of its section "Against roadmap item 2": `docs/reviews/packs/battery.md`, `generator.md`, `datacenter.md`, `grid.md`, `research.md`.
- The test: `tests/test_session422.py`.

## Checks

Every gate redirected to a file under `runs/chain_021/s422/` in the worktree (git ignores `runs/`), never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 422"` | 0 | passed; the machine was already on duty from the main checkout |
| Battery mirror, `erw_2026_battery_replication.py` in `site/public/battery` | 0 | USD 81.40 per kW; a bad month USD 475,477 (2024-12); debt coverage 2.63 |
| Datacenter mirror, in `site/public/datacenter` | 0 | USD 33.73 per MWh at `LZ_NORTH`; a bad month USD 37.88 per MWh (2026-08); USD 0.0684 per GPU-hour |
| Generator mirror, in `site/public/seller` | 0 | USD 59.85 per kW; price received USD 23.27 per MWh; coverage 0.67 |
| Grid mirror on the committed CSV | 0 | the hour 2026-10-12 03:00 UTC |
| `erw_2026_research_replication.py --json ../../data/findings` | 0 | 304 figures compared, 0 different |
| `db_probe.py`, both runs, 14:13 to 15:23 UTC | 1 then 0 | closed at 3.39 to 5.28 s; open at 2.76 s (14:43, the first run's build) and 2.86 s (15:22, the valid build) |
| `npm run build` | 0 | at 15:22 UTC |
| `check-cross-checks.mjs` | 0 | 18 of 18: battery 17 published figures, seller 34, datacenter 8, each table holding the rows its page counts |
| `check-decisions-face.mjs` | 0 | 144 of 144; the defaults' headlines equal the mirrors' figures above |
| `check-analysis.mjs` (main's version) | 1 | 269 of 279; the 10 failures are NYISO and ISO-NE callouts drawn as held (above) |
| `write-grid-replication.mjs` | 0 | the hour 2026-10-19 03:00 UTC: 70 nodes, 157 ties, 7 demand rows, 0 generation rows |
| `check-grid-replication.mjs` on that file | 0 | 60 values compared, 0 different |
| `tests.test_session422` | 0 | 6 tests, 1 skipped before this report existed; reruns the mirrors and compares their headlines with the packs |
| `tests.test_session422` with the battery pack's 81.40 changed to 81.41 | 1 | fails, as it should |
| The 13 earlier tests that read the packs (249, 257, 260, 262, 264, 265, 266, 267_findings, 269, 296, 298, 315, 381) with 422's | 0 | 162 tests, 2 skipped |

## Decisions made without you

1. **The build is of `wip/461-combined`, not of main**: chain 021 stacks on chain 019's unlanded branches (the parent's decision), so the checks read the pages as they would land, which is what a landing gate reads.
2. **The mirrors were compared with the pages through the face check's own record** (`face.json`, the numbers it read at the defaults), not through a second reading of the pages.
3. **`check-analysis.mjs` was not fixed here**: session 474's fix is on its own branch; fixing it twice would make two versions to merge. The 10 failures are named and checked by this session's test as held grids.
4. **The packs' tables were not rewritten**: a paragraph under each table records the results, so the cells session 381 wrote stay as its record.
5. **Nothing of 019's method notes or decisions blocks was touched**; the checks that read them passed.

## For Samuel's ruling

- None new. The research cards' held grids (session 474's finding, in chain 019's note) are the related open item.

## To finish

- Land `wip/422-tool-checks` with chain 021's other branches on top of `wip/461-combined` (documents and a test; no build needed beyond the landing's own). After `wip/474-checks` lands, rerun `node scripts/check-analysis.mjs <base>` on the landing's build: expected 279 of 279.

## Files

- `docs/reviews/packs/battery.md`, `generator.md`, `datacenter.md`, `grid.md`, `research.md` (one paragraph each).
- `tests/test_session422.py` (new).
- This report.
- Not in git: `runs/chain_021/s422/` (the runner, the mirrors' outputs, the build's and each check's outputs, `face.json` and the face check's shots).
