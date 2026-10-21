# Session 428 report: the performance items session 411 left for 401's files

21 October 2026, about 13:50 to 15:30 UTC, unattended, on portable-laptop (code role), in the worktree `C:\Users\samen\Documents\erw-428` on `wip/428-performance` (from `origin/wip/461-combined` at `2289156d`, chain 019's prepared and unlanded combined branch, so that one landing takes both chains). Chain `queue/done/021-day-21-october-code.md`, the part headed "Session 420". **Run as session 428:** the number 420 is taken (`archive/sessions/SESSION_420_REPORT.md` on `origin/wip/findings-oct20`), and the chain says a number found taken is skipped upward; 428 is the next free number above the chain's own 416 to 427. The chain was written for samueloldlaptop and runs here by the owner's instruction to run what the queue prints. Model spend USD 0; no warehouse data written; no request but to localhost and, for one check, the production site.

## Read these first

- **Five changes, no figure moved.** check-values on the five pages touched: 1,526 of 1,526 values equal Supabase. One floor fails (`/research/card/gas_sets_price`, 4 checked numbers against a floor of 6) and fails the same on production: not this branch's.
- **The 3D network waits for its frame.** On `/grid?view=network` the scene's chunk (3d-force-graph with three.js, about 841 KB) is fetched once its frame is on screen or within 200 px of it. At 390 px the frame is below the first screen, so the chunk is no longer fetched while the page loads: blocking time 2,196 to 734 ms, the largest chunk's script 3,455 to 986 ms, performance 64 to 69. At 1280 px the frame is on the first screen and the chunk is fetched at once, as before.
- **The forced reflow was the shared ScrollRegions** (session 412, mounted on every page), not the battery's or the seller's own code: the source location Lighthouse names is `markScrollers`, which read a box's size, wrote its attributes, and read the next. It now reads every box first and writes after, and its first pass waits for the page to settle (its own 150 ms pass) instead of reading inside the effect. Its share of the reflow is gone on the battery and seller pages and smaller on `/cost-of-power` (125 to 85 ms at 390) and `/research` (164 to 76 ms at 390). What Lighthouse still lists is mostly "[unattributed]": layout with no script frame.
- **`/cost-of-power`'s blocking time is not reduced**: it is the layout and hydration of about 2,875 elements (Lighthouse's DOM size), with no view drawn hidden (the page chooses its view on the server). Making it smaller is a change of what the page draws: listed, not made.
- **The machine was loaded** (other sessions' suites ran beside these runs), so the scores moved within the noise session 411 described (up to 7 points between two addresses of one page); the readings above are the audits each change targets, not the score.

## What to review

- The branch: `https://github.com/SamuelEnrique/erw/tree/wip/428-performance`.
- The changes: `site/app/network/Network.tsx` (the observer), `site/components/ScrollRegions.tsx` (reads before writes; no pass inside the effect), `site/app/research/page.tsx` (the chart of the day at its own size), `site/app/cost-of-power/GridsView.tsx` and `LoadAnswers.tsx` (the unused values), `docs/tooling.md` (the line on `lighthouse_audit`).
- The shots: `docs/brand/review-428/` with its README.

## Lighthouse, before and after

Lighthouse 13.4.1 from npm in the session's scratchpad (`LIGHTHOUSE_DIR`), through `site/scripts/lighthouse-pages.mjs`, on localhost only, one run at a time under the build lock. Before: the build of `wip/461-combined` (`2289156d`) on port 3527. After: this branch's build on port 3528. Full reports in `runs/chain_021/s428/lhr_before/` and `lhr_after/` (not in git).

| Page | Width | Perf before, after | TBT ms before, after | 3D chunk fetched at load, before, after | Script ms of the largest chunk, before, after |
|---|---|---|---|---|---|
| `/cost-of-power` | 1280 | 88, 85 | 46, 93 | no, no | 296, 320 |
| `/cost-of-power` | 390 | 62, 57 | 1308, 1500 | no, no | 1141, 1431 |
| `/cost-of-power/battery` | 1280 | 99, 98 | 18, 44 | no, no | 247, 298 |
| `/cost-of-power/battery` | 390 | 69, 70 | 887, 1301 | no, no | 1077, 1377 |
| `/cost-of-power/seller` | 1280 | 97, 98 | 46, 57 | no, no | 279, 284 |
| `/cost-of-power/seller` | 390 | 67, 63 | 940, 1245 | no, no | 1086, 1229 |
| `/research` | 1280 | 97, 92 | 121, 218 | no, no | 572, 639 |
| `/research` | 390 | 61, 54 | 1912, 2222 | no, no | 2276, 2450 |
| `/grid?view=network` | 1280 | 82, 70 | 257, 320 | yes, yes | 899, 1006 |
| `/grid?view=network` | 390 | 64, 69 | 2196, 734 | yes, no | 3455, 986 |

The framework chunk's script time rose 10 to 30 percent on every page between the two sets, including pages this session did not change: the machine, not the branch. Forced reflow attributed to the ScrollRegions chunk (Lighthouse's `forced-reflow-insight`, ms): `/cost-of-power` 46 to 73 at 1280 and 125 to 85 at 390; battery 0 to 0 and 3 to 0; seller 4 to 0 and 4 to 0; `/research` 35 to 0 and 164 to 76; network 0 and 0.

## Checks

Every gate redirected into `runs/chain_021/s428/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 428"` | 0 | passed; the machine's duty mark is held by the parent's checkout, so not marked again |
| `tests.test_session428` with `test_session412`, `411`, `401` | 0 | 45 tests OK; 428's own: 7 tests |
| ESLint on the cost-of-power files | 1 | the four unused-value warnings are gone; the one error left (`LoadAnswers.tsx` line 199, "Cannot create components during render") is older and not in this part |
| `scripts/db_probe.py` | 0, 1, then 0 | open at 13:55 (2.87 s), closed at 14:28 (5.25 s, the daily run loading), open at 15:04 (2.86 s); the build waited for it |
| `npm run build` | 0 | no read failed |
| check-values, restricted to the five pages (`CHECK_VALUES_PAGES`) | 1 | 1,526 of 1,526 values equal; the floor of `/research/card/gas_sets_price` (4 against 6) fails the same against production (`values_prod_gas.out`) |
| `test-network.mjs`, `check-network-map.mjs`, `check-network-v3-hard.mjs` on this build | 1, 1, 1 | the same failures on the build before the change (`*_before.out`): five in test-network (it finds no canvas on its address), the replay's colours in check-network-map, 25 elements past 390 px in v3-hard; check-network-map and v3-hard find the scene (`__erwGraph`) on both builds |
| Lighthouse before and after | 0, 0 | 10 runs each, none curtained or failed |
| Impeccable | not run | not installed on this laptop |

## Decisions made without you

1. **Session 420's part ran as session 428**, the number skipped upward as the chain says.
2. **"Loaded only when its view is shown" read as: when the scene's frame is on screen or near it.** The scene already loaded nothing while the map or the gravity shape was shown (session 180); what was left was the network shape fetching it under a phone's first screen. A browser without IntersectionObserver loads at once.
3. **The forced reflow was fixed where Lighthouse found it, in the shared ScrollRegions**, not in the battery or seller pages: their own code reads no size while the page loads. The change keeps every mark session 412's test pins; the first marking now comes 150 ms after the page mounts instead of at once.
4. **`/cost-of-power`'s blocking time is measured and named, not cut**: its cause is the page's size, and a smaller page is a change of what it draws.
5. **Before is the combined branch's existing build** (worktree `erw-461`), so the two sets differ by this branch's commits only; its `site/.env.local` was copied there from the main checkout, as here, to serve it.
6. **The research page reads the chart's size from the content bundle, falling back to 1600 by 900**, as the home page does since session 411.

## For Samuel's ruling

- `/cost-of-power` at 390 px: a smaller first view (folds closed by default, or the calculator's tables drawn on demand) to cut its blocking time; a change of what the page draws.
- The 3D scene at 390 px now appears as the reader scrolls to it, after a short wait for its chunk: keep, or load it at once as before.

## To finish

The landing, with chain 019's and 021's other branches (no agent lands tonight), in a combined branch holding `wip/428-performance`:

```bash
.venv/Scripts/python.exe scripts/freeze.py status; echo "exit=$?"
.venv/Scripts/python.exe scripts/db_probe.py; echo "exit=$?"
git fetch origin && git merge origin/main
.venv/Scripts/python.exe -m unittest tests.test_session428 tests.test_session412 tests.test_session411 > runs/s428.out 2>&1; echo "exit=$?"
cd site && npm run build > ../runs/s428_build.out 2>&1; echo "exit=$?"
npx next start -p 3428 &
MSYS_NO_PATHCONV=1 node scripts/check-values.mjs http://localhost:3428 > ../runs/s428_values.out 2>&1; echo "exit=$?"
node scripts/check-network-map.mjs http://localhost:3428 > ../runs/s428_netmap.out 2>&1; echo "exit=$?"   # expected: only the replay's colours, as before
node site/scripts/snapshot-live.mjs take s428-before   # then the task/ push, the deploy, take s428-after, compare
```

## Files

- `site/app/network/Network.tsx`, `site/components/ScrollRegions.tsx`, `site/app/research/page.tsx`, `site/app/cost-of-power/GridsView.tsx`, `site/app/cost-of-power/LoadAnswers.tsx`.
- `docs/tooling.md` (one line).
- `tests/test_session428.py`.
- `docs/brand/review-428/` (8 shots and a README).
- This report.
- Not in git: `runs/chain_021/s428/` (the Lighthouse sets and reports, the probes, the build, the checks).
