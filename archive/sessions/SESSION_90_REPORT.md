# Session 90 report: the fixes, and the one deploy

**Done, and live.** One push at 06:22 UTC landed all six items on main; production deployed at 06:29 UTC. **No number on a live page differs.** The home page's battery tile stayed where it was (USD 81.40 per kW): the first deploy in three that did not blank it. The MISO pause is live: the 15-minute run of 06:30 UTC read the five other grids and did not ask MISO.

**Read these four first:**

1. **Two live pages outside the snapshot's twenty gained text, both the MISO pause's own record.** `/terms` lists the source registry: its six MISO data sources now end with "[PAUSED 2026-10-04: MISO's terms forbid automated access; pulls paused pending a review of MISO's terms by a person (docs/methods/miso_pause.md)]". `/data/methods/cost_of_power` gained session 89's paragraph "MISO is paused (4 October 2026). ...". Both are what your ruling asked for (the pause recorded in the registry and the method notes) and neither is a number, but the snapshot script does not read those pages, so I compared them by hand before and after. The other three live methods pages did not change by a character. The script now reads all five (on this branch, not on main: "To finish", 1).
2. **The home tile was a symptom. The cause was the build asking the database for forty pages' rows at once.** With the first fix alone (a failed read is never cached) the site's build on this machine failed: the home page's read was cancelled six times in a row. So the build's reads now take turns, two at a time per build worker. Before: three or more statements cancelled in every build. After, with the build's own cache emptied so that every read really reached the database: none, and the pages were generated in 27 seconds. Vercel's build of the same commit passed twice (the preview, then production).
3. **A failed read on the home page now fails the build.** That is the meaning of "never": at a regeneration the last good page stays; at a build there is no last good page, so the deploy does not go live and the previous one stays up. You will see it as a failed check on the task branch or a failed Vercel build, with the read named in the log. It did not happen tonight after the second fix.
4. **`/contracts` answers in about a second on production**, with the numbers session 83 reported (227 rows, 174 agreements, 78 sellers, 95 buyers, 112 priced). Its summary took 4.8 seconds to count on every request, against the public key's limit of 3.

Energy Research Warehouse (ERW), session 90, first of the night's chain, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from 05:52 to 06:50 UTC, unattended. **Model spend: USD 0.00.** No pull, no model call, no force push. The other session's report was already on `origin/wip/089-findings` and the data lock was free at 05:52 UTC, so the chain started without waiting. The data lock was held for about a minute at 05:58 UTC, for the load that stored the contracts summary, and released.

## To finish

```bash
# Nothing is left half done on main. Two things are on this branch (wip/090-fixes) and not on main, because this
# session had one push and it was spent:

# 1. The snapshot script reads 25 pages: the 20, then /terms and the four live methods pages. With this report.
#    It lands with the next push to a task branch (it changes no page):
git fetch origin && git checkout wip/090-fixes && git merge origin/main
python -m unittest tests.test_session90            # read its exit code
cd site && node scripts/snapshot-live.mjs take before-090b && cd ..
git push origin wip/090-fixes:task/090-snapshot
# when the workflow has merged and Vercel has deployed:
cd site && node scripts/snapshot-live.mjs take after-090b && node scripts/snapshot-live.mjs compare before-090b after-090b

# 2. The home page's MISO card. From about 11 October it will read "no data ... fewer than two rows" where its
#    seven-day line is, because no MISO price of the last seven days will be held. Nothing is wrong; it follows from
#    the pause. If you want the card to say "paused" instead, say so: it is a few lines of the home page.
```

## What was asked, and what was done

| | Asked | Done |
|---|---|---|
| a | The MISO pause onto main, so the daily and 15-minute runs stop pulling MISO before 14:00 UTC | On main at 06:28 UTC. The 15-minute run of 06:30 UTC ran from the merged main: five grids retrieved at 06:30 to 06:31, MISO's row unchanged since 06:16 (its last interval, 06:10). The daily run's list has no MISO |
| b | The home page never caches a render in which a read failed; the workflow warms the live pages before the check | Both, and the cause removed (below) |
| c | `/contracts`: precompute the summary when the table is built; the page reads that | The loader computes it from the rows it loads and stores one row; the page's function reads it. 0.1 to 0.3 seconds where it took 4.8 |
| d | `/shoulder` opens on the latest month that holds every figure | Opens on August 2026 for Texas and for California's own data (September lacks the fleet), November 2025 for California by EIA-930 |
| e | `/storage/buildout` shows MW and MWh without decimals | 183 MW and MWh numbers per page, none with a decimal; the two ratios keep two |
| f | Session 89's findings brief onto main | On main: `docs/briefs/findings_2026-10-04.md`, with its test and the reports of sessions 87, 88 and 89 |

### b. The home page, and why its tile went blank

The home page is generated once and served from a cache for 15 minutes. Every read on it went through `attempt`, which turns a failed read into a reason ("no data", "not held") so that the page still renders. Right for a page rendered per request; wrong for a cached one, where one cancelled statement becomes what every visitor sees for a quarter of an hour.

**The rule.** `required` in `site/lib/supabase.ts` is `attempt` that throws. All fourteen reads of the home page use it. A render that throws is not cached: when the page is regenerated in the background the framework keeps the last page it generated successfully and tries again at the next request (its own documented behaviour, `node_modules/next/dist/docs/01-app/02-guides/incremental-static-regeneration.md`, "Handling uncaught exceptions"); when the site is built, the build fails. "no data" and "not held" remain for what the tables do not hold (a grid with no row in `latest_prices`, fewer than two prices in seven days), which is not a failed read.

**The cause.** The first build with the rule failed, as it should: the home page's read was cancelled on every try. The build renders up to eight pages per worker at once, and each page asks for its rows; the public key's statements are cancelled after 3 seconds, and under that load they ran out of time. The log of that build shows the same cancellation on other pages too, which cached "no data" for an hour where a table holds data: the home tile was the one case on a live page. Two changes, both only while the site is built:

- **The reads take turns:** at most two in flight per build worker. Measured on this machine with the build's fetch cache deleted first: 0 cancelled statements, 101 pages in 27 seconds.
- **A cancelled read is tried for longer:** after 1, 3, 5, 8 and 12 seconds, where a request tries after 1 and 3. A page is given 300 seconds to be built, not 60, because a page waiting for its turn is not a page that hangs.

**The workflow.** `site/scripts/warm-live.mjs` asks for every live page once, as a visitor (the pages the snapshot reads), and exits 1 if one never answers 200. The workflow runs it against the build it has just started, before the route check. Run 37182622668 passed with it.

**Two exceptions, both written into the code:** a server with no database named (a build without keys) says so on the page, as before; and a database at `localhost` is a fixture (the build-out and shoulder checks build against a stand-in that answers one table), so the rule does not apply to it. A real database is never at `localhost`; a test checks that nothing else is taken for one.

### c. `/contracts`

`internal_eqr_summary` counted the 19,009 live rows five ways on each request. I ran the same statement over a direct connection, read only: 4.8 seconds. The public key is cancelled at 3.

Now the loader computes the summary from the rows it has just loaded and reconciled (`eqr_summary` in `warehouse/supabase/load.py`) and stores it through `eqr_summary_store`, which only the service key may call (migration 021). The page's function has the same name, arguments and answer, and reads one row; it still answers only with the internal token. If the summary cannot be stored the table is not marked loaded, so the next run tries again.

Checked: the loader's summary and the old statement's answer are equal in every field (rows 19,009, priced 8,039, first 2024-01-08, last 2223-01-01, 37 months, 30 products, 68 balancing authorities, in the same order). With the public key: the summary in 0.10 to 0.29 seconds; "not authorized" with a wrong token; "permission denied" for the store. A quarter's rows take 0.3 to 0.5 seconds, so nothing else on the page is near the limit. On production, in the internal view: 200 in 0.7 to 1.8 seconds, and the three views of session 83's report give the same numbers.

### d. `/shoulder`

The page opened on September 2026, whose sentence read "its batteries could run not held hours at full power, covering not held of them". September's fleet is not published yet. It now opens on the latest month that holds every figure its summary sentence and headline numbers state (twenty variables, listed in `site/lib/shoulder.ts`; a test checks the list against the page). September is still in the panel, and when the page opens by itself a line under the months says: "Opened on August 2026, the latest month that holds every figure. September 2026 is held, but not every figure of it yet (EIA publishes the battery fleet a month or two behind)." A month named in the address is shown as asked.

**Decision: "every figure" is every figure of the month.** The year's figure for the ten worst days is not in the list. For California's own data it is not held for 2026 at all (five of the ten worst days fall in September and October, after the fleet's last month), and requiring it would open that grid on December 2025. The sentence already says so in words.

### e. `/storage/buildout`

MW and MWh are written whole, a half rounding up, as the rest of the site rounds: "ERCOT has 18,205 MW of batteries holding 30,020 MWh, an average of 1.65 hours, up from 11,046 MW a year ago." The hover titles of the bars too. The two ratios (hours, and MWh per MW of solar) keep two decimals; unit counts were whole already. The value read from the table is unchanged in each number's `data-raw`, and the value check compares the whole number with the table's value rounded the same way.

## The deploy, and its snapshots

One push, `wip/090-fixes` to `task/090-fixes`, at 06:22:35 UTC. Workflow run 37182622668: tests, the build, the warm step, the route check and the browser proof passed; merged to main at 06:28 (`82c534e`). Vercel: production at 06:29:33 UTC.

**Before** (`before-090`, 06:22:22 UTC): 20 pages, 4,098 checked numbers. **After** (`after-090`, 06:30:11 UTC, 38 seconds after the deploy): 20 pages, 4,098 checked numbers. **36 differences, every one the site's own refresh:**

| Where | Differences | What | Meant |
|---|---|---|---|
| `/` | 30 | The six latest real-time prices and their lines: 12 number keys (each price's key carries its interval, so a new interval is one key gone and one new) and 18 lines of text | yes: the 15-minute refresh |
| `/network` | 6 | "refreshed 05:05 UTC" became "06:05", the newest hour of demand moved on by one, and the source line's "Built" time | yes: the hourly refresh |
| The other 18 pages | 0 | | |

The battery tile is not among them: it read 81.40 in both.

**The confirming snapshot, after the home page's cache turned** (`after-090-cache-turned`, 06:47:06 UTC, seventeen and a half minutes after the deploy): 20 pages, 4,098 checked numbers, and **the same 36 kinds of difference and no other**: the six latest prices on `/` (12 number keys, 18 lines of text) and the network's hourly refresh (6 lines). No number other than a latest price differs. The battery tile reads 81.40. MISO's latest price is among the six because the 15-minute run of 06:15 UTC, before the merge, still read it (its interval of 06:10); it has not moved since.

**Live pages the snapshot does not read**, compared by hand (the page as served at 06:22 and at 06:31 UTC, visible text line by line):

| Page | Differences | What | Meant |
|---|---|---|---|
| `/terms` | 6 lines | The six MISO data sources each gained the registry's pause note | yes: session 89's record of your ruling; the page prints the registry |
| `/data/methods/cost_of_power` | 1 line | Session 89's paragraph "MISO is paused (4 October 2026). ..." | yes: the same |
| `/data/methods/battery_stack`, `grid_network`, `storage` | 0 | | |

## Tests and checks

| Check | Result |
|---|---|
| `tests/test_session90.py` | 26 tests pass (25 when the branch was pushed; one more with the snapshot's 25 pages: every live page of the release list is read, and the first twenty keep their order). The home page's rule is run, not read: `required` throws on a failed answer, on a cancellation that outlasts its tries and on a database that cannot be reached; returns a good read as before; gives a reason, not a throw, with no database named and for a stand-in at localhost and for nothing else; the build sends two reads at a time and a request sends all twelve; the build's waits are 1, 3, 5, 8, 12 seconds; every read of the home page is inside `required`; no error file stands between the page and the cache. The workflow's warm step comes before the route check and fails when no page answers. The summary on known rows, its shape against the page's type, who may store it. The opening month on made rows and on the table as built. Whole MW and MWh, and that the whole-number variables are exactly the table's MW and MWh variables, in the page and in the value check |
| The whole suite, here | 590 tests, exit 1: one failure, old and known since session 82 (`test_session49`: `eia930_all_interchange` holds 151,632 rows against a ceiling of 150,000 on data machines; it skips on the runner) |
| The whole suite, on the runner | pass (run 37182622668) |
| Site: types | exit 0 |
| Site: build | First build, with the rule and without the turns: **exit 1**, the home page's read cancelled, as designed. With the turns: exit 0. With the fetch cache deleted first: exit 0, no statement cancelled |
| `warm-live.mjs` on the local build | exit 0: 20 of 20 pages, 5 seconds |
| `check-routes.mjs` on the local build | exit 0: 0 failed |
| `check-values.mjs` on the local build | exit 0: **7,533 of 7,533 values match Supabase** |
| `check-shoulder.mjs` on the local build | exit 0: 3,482 checks, 1,690 numbers against the table's rows |
| `test-buildout.mjs` | exit 0: 935 checks |
| `check-buildout.mjs`, on a build against the fixture stand-in | exit 0: 10,241 checks, 3,530 numbers (16 pages) |
| Migration 021, alone | applied, exit 0 |
| Load, `--only` the contracts table, under the lock | exit 0: 19,009 rows, counted equal, unchanged; the summary stored |
| Vercel's build | passed for the preview of the same commit (06:21 UTC) and for production (06:29 UTC) |

Not run: the validator and the coverage builder (no table was built or changed), the Redivis uploader.

## Errors and decisions

- **Error, mine: the first load command did nothing.** `lock.py run` could not start `.venv/Scripts/python.exe` given as a relative path, and then started the machine's own Python, which has no pandas. Both times the lock was taken and released and nothing was loaded. The third command named the environment's interpreter by its full path. For the later sessions: `lock.py run -- "$(cygpath -w "$PWD/.venv/Scripts/python.exe")" ...`.
- **The load of the contracts table also wrote the source registry**, as every load does: the twelve MISO rows gained their pause note in Supabase at 05:58 UTC, half an hour before the deploy. No live page reads that table from Supabase (`/terms` prints the registry file the site was built with), and the daily run would have written the same rows at 14:00 UTC.
- **Decision: the build's reads take turns.** You asked for the rule and the warm step. The rule alone would have turned a blank tile into a failed deploy most nights. I measured the cause and removed it; the rule is now the guard, not the fix.
- **Decision: a failed build, not a page marked as never cached.** The other way to obey "never cache" is to let the page render per request after a failed read. Then a slow database would show visitors "not held" on every request until someone noticed, which is the fault moved, not removed.
- **Decision: the same function name for the contracts summary.** The page needed no change; an older build of the site still works against the new function.
- **Decision: session 90's report is on its wip branch only.** Putting it on main is a second push to main, and this session had one.
- **The route check's baseline is the live site.** It passed, so no page in review shows more "no data" than production did before the deploy.

## For Samuel

1. **The snapshot's list** ("To finish", 1). Tonight's deploy changed two live pages the script never looked at. Nothing went wrong, because I looked by hand; the next session might not.
2. **The MISO card** ("To finish", 2), before about 11 October.
3. **The other pages that cached "no data" from the build.** They were never reported because they are in review. With the turns the build cancels nothing, so this should be over; if a page in review shows "no data" for a table that holds data after a deploy, the build's log will have a line beginning `[erw] Supabase`.
4. **The Vercel token is still not on this machine** (`VERCEL_TOKEN`). I watched the deploy through GitHub's record of Vercel's deployments, which was enough. Previews of wip branches are built (each push to a `wip/` branch gets one) but they sit behind Vercel's login, so I could not read them.
