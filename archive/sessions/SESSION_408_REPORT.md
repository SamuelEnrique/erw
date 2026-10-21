# Session 408 report: every page's floor, every number's key

21 October 2026, about 06:00 to 08:00 UTC, unattended, on samueloldlaptop (the code machine), in the worktree `C:\Users\lossa\Documents\erw-408` on `wip/408-s` (from `wip/381-382-land` at `df638a38`). Chain `queue/done/015-day-20-october-code-pm.md`, session 408. Model spend USD 0; no pull from any publisher; no warehouse data written.

## Read these first

- **The rule is in a test**: `tests/test_session408.py` finds every route under `site/app/` whose page shows a warehouse figure, by code, and fails when one is neither read by `site/scripts/check-values.mjs` nor in its `EXEMPT` table with a reason. The rule: the page's code is its `page.tsx` and every site file it imports, followed through imports; it shows a figure when that code holds a `<Num ... check=` (followed through every file), or when it reaches `lib/supabase.ts` through `app/` and `lib/` files. A shared component's own read (the citation's dates in `components/Cite.tsx`, the download buttons in `components/tool/TableDownloads.tsx`) does not count as the page's: followed through components, every page of the site would count.
- **The list is the script's own**: `node scripts/check-values.mjs --list` prints the addresses it reads (`PAGES` and `INTERNAL`, JSON) and stops before any variable is read or request made, so a page added by a later session, in the literal list or by `PAGES.push` (as session 402 adds the dated Digests), is seen as the script reads it. Needs node, not the site's packages: it runs on GitHub's runner before `npm ci`.
- **Two routes were not read and are now**: `/contracts` and `/cost-of-power/battery/awards`. Both read Supabase and neither draws a figure through `Num`, so each carries no checked number; their floors are 0 (see "For Samuel's ruling").
- **Eleven routes are exempt, each with its reason in the test**: the six `/internal/` views, `/thesis`, `/severance/lease/real`, the problem sets' index and the two dated-edition routes (their numbers are the day's, from files).
- **The explorer pages and the Digest are not added here** (sessions 403, 404, 405 and 402 add them on their own branches). A trial merge of `wip/403-s`, `wip/404-s`, `wip/405-s` and `wip/402-s` onto this branch, with the test run on it, found every `/explore/` and `/digest` route read. `wip/408-s` merges with each of the four without a conflict; **`wip/402-s` and `wip/403-s` conflict with each other** on the end of `PAGES` (403 lengthens its last line, 402 pushes after it): the fix is to keep both, 403's lines then 402's `PAGES.push`.
- **Session 403's restricted floor write is taken as written**: its two hunks of `check-values.mjs` from commit `9a869e2b` (the comment and the `CHECK_VALUES_WRITE_FLOOR` branch), without its page list hunk, so the two branches merge cleanly (identical lines on both).
- **A page read with no floor gets a `note` line** in the run's output (not a failure).

- **Not mine, but it stops every full run of check-values today**: `/reports/draft/shape-premium` (internal) answers HTTP 500 on this build. Its `latest` (line 128 of `site/app/reports/draft/shape-premium/page.tsx`) is the newest day on which all six hubs have a `da_shape_premium` row. ISO-NE, MISO and NYISO have been license-held since 21 October, so no such day exists, `latest` is undefined and `.slice` throws. check-values stops at the first page that does not answer 200 ("check-values FAILED: /reports/draft/shape-premium: HTTP 500"), so no landing's full run can pass until it is fixed. Not fixed here: what the draft shows for a held hub needs a ruling (below).
- **Ten pages carry fewer checked numbers than their floors, every one because of a license hold** (the numbers carry `data-license-held` in their place; no failed read and no "could not be read" line on any of them). The list is under "For Samuel's ruling". No floor was lowered.

## What to review

- `tests/test_session408.py` on `wip/408-s`: `https://github.com/SamuelEnrique/erw/blob/wip/408-s/tests/test_session408.py` (the rule, and `EXEMPT` with the eleven reasons).
- `site/scripts/check-values.mjs`: the `PAGES.push`, the `--list` mode and the `note` line (search "session 408"); session 403's two hunks (search "Session 403").
- `site/scripts/check-values-floor.json`: two lines added, `"/contracts": 0` and `"/cost-of-power/battery/awards": 0`.
- Nothing a visitor sees changed: no file under `site/app/`, `site/components/` or `site/lib/` was touched, so no screenshots.

## Checks

Every gate redirected to a file under `runs/chain_oct21/s408/`, never piped; the exit code read before the next step. Port 3408.

| Check | Exit | Result |
|---|---|---|
| `tests.test_session408` before the floors were written | 1 | 6 of 7 pass; the floor test waits for the run, as it should |
| The 33 test modules that read `check-values.mjs`, with `test_session408` | 1 | 436 tests, the one failure the same floor test (12 skipped) |
| Trial merge of `wip/403-s`, `wip/404-s`, `wip/405-s` onto `wip/408-s` | 0, 0, 0 | no conflict; `tests.test_session408` there: only the floor test failed (every `/explore/` route read) |
| Trial merge of `wip/402-s` onto that | 1 | the 402 and 403 conflict above (not 408's); resolved in the trial by keeping both: every `/digest` route read |
| Mutation: `/contracts` taken out of the list, the route test run | 1 | `['/contracts'] != []`, as it should |
| `npm ci` | 0 | |
| `duty.py beat` before each build | 0, 0 | |
| `npm run build`, 06:25 UTC | 1 | the home page's required read: "Supabase series: HTTP 521" (the database's front answered "web server is down"); mutex let go, 15 minutes |
| `npm run build`, 07:06 UTC | 0 | no timeout in the log |
| `check-values.mjs`, `CHECK_VALUES_PAGES=/contracts,/cost-of-power/battery/awards,/learn/bill` | 1 | Git Bash turned `/contracts` into `C:/Program Files/Git/contracts` (MSYS path conversion), and `/learn/bill` is below its floor (held): run again |
| the same with `MSYS_NO_PATHCONV=1` and `/impact` in place of `/learn/bill` | 0 | 340 of 340 values match; a `note` line for each of the two new pages |
| the same with `CHECK_VALUES_WRITE_FLOOR=1` | 0 | 340 of 340; "the floor file was updated for 6 pages of a restricted run"; the diff is the two new lines only |
| `check-values.mjs` full run (120 s a request, 30 minutes) | 1 | "check-values FAILED: /reports/draft/shape-premium: HTTP 500" (above) |
| `check-values.mjs` restricted to every first segment but `/reports` (the home page cannot be named alone: `/` is a prefix of every address) | 1 | 5,731 of 5,731 values match Supabase; 10 FAILED, every one a floor (the list below) |
| `check-values.mjs`, `CHECK_VALUES_PAGES=/reports/draft/ai-gigawatts` | 0 | 94 of 94 |
| The home page's keys counted (`held.mjs`, scratchpad, reading the page with the internal cookie) | 0 | 11 checked numbers (floor 10), 3 held (`latest_prices`); its values were not compared this session |
| `tests.test_session408` after the floors | 0 | 7 tests OK |
| Whole suite, `ERW_LOCK_EXEMPT=1 ... -m unittest discover -s tests` | 1 | 4,789 tests, 252 skipped, 1 failure: `test_session156` (the ask fixtures), the one the chain's rules say may fail tonight without a session's cause |

## Decisions made without you

1. **The rule follows components for `Num` and not for Supabase.** Followed through `components/`, every page reaches `lib/supabase.ts` (the citation reads the catalogue's dates, the download buttons the table list), and the rule would name `/terms`. Followed nowhere, it would miss the pages whose figures are drawn by a shared component. A layout is not the page's code (the root layout would otherwise count for every page).
2. **The list is read from the script (`--list`), not parsed from its text**, so `PAGES.push` (402's dated Digests, these two pages) is seen. The mode stops before `env()` is called, so it needs no `.env.local` and no request.
3. **`/contracts` and `/cost-of-power/battery/awards` are read with a floor of 0** rather than exempt: both show figures read from Supabase, so their address answering (not 500, not the in-review page) is worth a request each. No `Num` was added to either: "every value unchanged", and a key is a change of the page for a later session (below).
4. **Eleven exemptions, each with its reason in the test**, which fails when an exemption no longer holds (the route is gone, no longer shows a figure, or is read).
5. **Session 403's change taken as its own two hunks** (the prompt allowed a cherry-pick of its commit; the commit also carries the explorer page, which the prompt says not to add). The lines are byte for byte 403's, so the merge takes them once.
6. **A page with no floor is a `note` line, not a failure**: 403 and 404 add pages without floors (their branches' floor files have no `/explore/ercot-peak-premium` or `/explore/demand-growth` lines), and 402's dated Digests change every day; failing on them would stop each landing. The test holds the floors of the two pages added here only.
7. **The floors were written by a restricted run with `/impact`** beside the two pages, because a run of fewer than ten values does not pass (the two pages carry none). `/impact`'s four floors stayed 10.
8. **The shape-premium draft was not fixed**: it is another page's code, and the fix chooses what the draft says about a held hub.

## For Samuel's ruling

- **The shape-premium draft and the held hubs** (it blocks every full check-values run): (a) the draft's "latest day" taken over the hubs that are not held, the held ones written "license needed"; (b) the draft taken out of check-values' `INTERNAL` list while ISO-NE, MISO and NYISO are held; (c) check-values reports a page that answers 500 as a failed line and goes on, instead of stopping.
- **Floor below, held: `/deals`**: 0 checked numbers, floor 10; `energy_deals` held (one held block in place of the page's figures).
- **Floor below, held: `/map`**: 0, floor 1; `energy_projects` held (session 405 found the same).
- **Floor below, held: `/events`**: 2, floor 9; 7 figures of `event_window_daily` held.
- **Floor below, held: `/events/uri-2021`**: 9, floor 10; 75 held (`event_window_daily`).
- **Floor below, held: `/events/covid-2020`**: 7, floor 10; 343 held (`event_window_daily`).
- **Floor below, held: `/events/caiso-heat-2020`**: 0, floor 10; 65 held (`event_window_daily`).
- **Floor below, held: `/events/caiso-heat-2022`**: 0, floor 10; 53 held (`event_window_daily`).
- **Floor below, held: `/events/east-heat-2025`**: 0, floor 10; 67 held (`event_window_daily`).
- **Floor below, held: `/learn/bill`**: 5, floor 10; 15 held (`cost_of_power_monthly`).
- **Floor below, held: `/research/card/gas_sets_price`**: 4, floor 6; 2 held (the card's figures of a held grid).
- **What to do with floors under the holds**: (a) the floor counts held numbers too (`data-license-held` beside `data-check`), so a hold does not fail it and a lost key still does; (b) floors written again from a run under the holds, and again when a hold is lifted; (c) leave them failing until the holds end.
- **Pages that show Supabase figures with no key**: `/contracts` (the quarter's contract rows, priced rows, affiliates; the buyers and sellers) and `/cost-of-power/battery/awards` (the fleet's award share and the model gap) are read with floor 0. Pages already in the list at floor 0: `/board`, `/deals?tab=tracker`, `/map?tab=resources`, `/roundup` (checked by its weekly brief instead), `/severance`, `/severance?tab=lease`, `/storage?tab=owners`. Should a session give their figures `Num` keys?
- **`/internal/findings`**: exempt as drafts waiting for review. Should check-values read the draft cards' figures before they are published?

## To finish

- Merge `wip/402-s` with `wip/403-s` by keeping both sides of the end of `PAGES` (403's four `/explore/ercot-peak-premium` lines, then 402's `PAGES.push("/digest", ...)`).
- After 403, 404 and 405 land: their pages without floors get them from a restricted run that passes, under the build mutex, for example `MSYS_NO_PATHCONV=1 CHECK_VALUES_WRITE_FLOOR=1 CHECK_VALUES_PAGES=/explore/ercot-peak-premium,/explore/demand-growth node scripts/check-values.mjs http://localhost:<port> > runs/<dir>/cv_floor.out 2>&1; echo "exit=$?"`.
- The home page's values were not compared this session (a restricted run cannot name `/` alone); the full run compares them once the draft answers 200.

## Files

- `tests/test_session408.py` (new); `site/scripts/check-values.mjs`, `site/scripts/check-values-floor.json`; this report.
- Run outputs: `runs/chain_oct21/s408/` (`cv_*.out`, `held.out`, `held_home.out`, `build1.out`, `build2.out`, `suite.out`).
