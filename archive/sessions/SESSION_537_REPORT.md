# Session 537 report: a build does not keep a failed read

21 October 2026, about 20:20 to 21:15 UTC, unattended, on samueloldlaptop (the code machine), in the worktree `C:\Users\lossa\Documents\erw-537` on `wip/537-s` (from `origin/main` at `2ecba09d`). Chain 024 (`queue/done/024-night-21-october-code.md`), session 537. Model spend USD 0; no pull from any publisher; no warehouse data written; `site/lib/release.ts` not touched; no page's text or default figure changed.

## Read these first

- **The proof is done, on two builds.** (1) A build through `scripts/failing-read-proxy.mjs`, which failed every read of `caiso_grid_emergencies` (exit 0): the two pages that read that table, `/grid/caiso/alerts` and `/events/caiso-heat-2022`, were built with a revalidation of 1 minute; the 191 other routes of the prerender manifest have exactly the interval of the main copy's build of 09:37 UTC (`runs/chain_024/s537/manifest-diff-2.txt`). On that build's server, after the proxy let the table through and 65 s had passed: `/events/uri-2021` and `/data`, asked twice each, sent no read at all (proxy log: 0 lines) and their text was unchanged; the two pages that had lost the read answered STALE once, read the table again (2 reads passed), and the next request had the notices (`/events/caiso-heat-2022` lost its "could not be read" line: 7,438 to 8,361 characters of text; `/grid/caiso/alerts` 14,870 to 15,679). Their `Cache-Control` was then `s-maxage=3600` again. (2) The ordinary build against the live set (exit 0, no statement timeout, no route at 1 minute, all 193 routes as the baseline): check-routes 226 of 226 pages, both passes, exit 0; check-values 6,445 of 6,456 values match, its 10 failures exactly the ten held pages' floors (session 408's list), exit 1 as expected.
- **The disk was full earlier tonight.** At 20:30 UTC `npm ci` failed with `ENOSPC` (`C:` 27 MB free; 256 MB at 20:46). The orchestrator (session 542) removed 28 landed worktrees (43 GB free); the build work was then done at 20:50 to 21:11 UTC under the build mutex.
- **The change** (`site/lib/supabase.ts`): a read that fails now asks Next, through `unstable_cache`, for a revalidation of `RETRY` = 60 seconds for the page being rendered. Next takes the shortest revalidation of the reads made during a render as the page's own interval (`unstable_cache` lowers the prerender store's `revalidate`: `next/dist/server/web/spec-extension/unstable-cache.js`, lines 117 to 131 in 16.3.8), and a failed fetch is never kept in Next's data cache (only a 200 is: `patch-fetch.js` line 696). So a page that lost a read during the build, or during a regeneration, is regenerated on the first request after a minute (in the background, as every regeneration is: that request is answered with the page as it was, the next with the new page), where it used to keep "no data" for its hour, or until the next deploy for a page with no interval.
- **Pages whose reads succeeded are not changed**: they never reach the mark, so their interval and their reads are exactly as before, and the database is not read more often for them. The mark reads nothing from the database (one small entry in Next's own cache, per page). A table held for a license (`LicenseNeeded`) and a server with no database named (`NotConfigured`) are not failed reads and are not marked. `required()` reads still throw and fail the build; session 90's turns (`BUILD_READS` 2) and waits are unchanged. Outside Next (`NEXT_RUNTIME` unset: the node scripts that import the file) nothing is marked, and `next/cache` is imported only inside Next.
- **Where the mark is made**: in the reader itself (`restPaged`, which `rest` calls, and `restCount`), not in `attempt()`, so a read caught elsewhere is covered too (`lib/grid.ts` `safe()`, the `.catch` in `lib/chat/tools.ts`).

## What to review

- `site/lib/supabase.ts`: the block "Session 537" above `onePage` (`RETRY`, `markFailedRead`, `askAgainOnFailure`), and the two calls in `restPaged` and `restCount` (`restCount`'s body moved unchanged into `countOf`).
- `site/scripts/test-failed-read.mjs`: twelve cases that fail reads on purpose with a stand-in for fetch.
- `site/scripts/failing-read-proxy.mjs`: a pass-through to Supabase that fails one table's reads while a file exists, for the build proof under "To finish".
- `site/scripts/alias-loader.mjs`: a stand-in for `next/cache` that notes each `unstable_cache` call (used by the test only; no script that leaves `NEXT_RUNTIME` unset reaches it).
- `tests/test_session537.py`.
- On GitHub: `https://github.com/SamuelEnrique/erw/tree/wip/537-s`

## Checks

Every gate redirected to a file under `runs/chain_024/s537/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 537"` | 0 | on duty |
| `npm ci` in the worktree's `site/` (under the build mutex) | 1 | `ENOSPC: no space left on device`; the partial folder removed, the mutex let go at 20:30 |
| `scripts/db_probe.py` | 0 | open, 0.55 s |
| `node --import ./scripts/alias-register.mjs scripts/test-failed-read.mjs` | 0 | 12 of 12 cases: a read that succeeds (one page and three pages) makes no mark and sends its own revalidation; the statement timeout past the two retries (3 requests, as before), a plain HTTP 502, a refused request, a failed second page and a failed count each make one mark of 60 seconds keyed `erw-failed-read`; `required()` still throws; a held table is not asked and not marked; no database named, and outside Next, no mark |
| `failing-read-proxy.mjs` tried by hand on 127.0.0.2:54537 | n/a | the failed table answered 500, another read passed through; 127.0.0.2 is not taken for a stand-in by `lib/supabase.ts`, so a `required()` read would still fail a build through it |
| `tests.test_session537` | 0 | 8 tests OK |
| The tests that read `lib/supabase.ts` or the alias loader (90, 148, 153, 154_page, 157_page, 163, 215, 272, 301, 408, 66, 537) | 0 | 213 tests OK, 15 skipped |
| The whole suite (`ERW_LOCK_EXEMPT=1 ... -m unittest discover -s tests`) | 0 | 5,234 tests OK, 291 skipped; none of the known flakes (`test_session156`, `484`, `114`, `188_idle`) failed this time |
| Disk again at 20:46 UTC, 16 minutes after the failure (the second try the brief allows) | n/a | 256 MB free: still too little for `npm ci` (528 MB) and a build |
| `npm ci` again, after session 542 freed 43 GB (under the mutex) | 0 | |
| `duty.py beat` before each of the three builds; `db_probe.py` | 0, 0, 0; 0, 0 | open (1.24 s) |
| Proof build, first: `SUPABASE_URL=http://127.0.0.2:54537 npm run build`, `caiso_grid_emergencies` failing | 0 | the two pages at `1m`, 191 routes as the baseline (`manifest-diff.txt`); its healing check measured "no data", which these two pages do not print (they say "could not be read" or show no notice), so it was made again |
| Proof build, second, the fetch cache removed first | 0 | the same: two pages at 60 s, 191 the same (`manifest-diff-2.txt`) |
| `heal537.mjs http://localhost:3537` on that build | 0 | the pages that read well: no read, text unchanged; the two that lost it: STALE, 2 reads, then healed (`heal.out`) |
| Their `Cache-Control` after healing (`cc537.mjs`) | 0 | `s-maxage=3600` on all four |
| `npm run build` (ordinary, the live set) | 0 | no statement timeout; 193 of 193 routes with the baseline's interval (`manifest-diff-ordinary.txt`) |
| `check-routes.mjs http://localhost:3537` | 0 | pass 1: 226 of 226 against production; pass 2: 225 in review and 1 live asked as a visitor, 0 failed |
| `check-values.mjs http://localhost:3537` | 1 | 6,445 of 6,456 match, 11 latest prices superseded; the 10 failures are the ten license-held floors only (`/deals`, `/map`, `/events`, five event pages, `/learn/bill`, `/research/card/gas_sets_price`): expected, no floor lowered |
| The server on 3537 and the proxy on 54537 stopped; the mutex let go | n/a | 21:11 UTC |

## Decisions made without you

1. **A minute** (`RETRY` = 60): short enough that a page heals between two visits, long enough that a database that is down is asked at most once a minute a page. It is shorter than both of the site's intervals (900 and 3,600 s).
2. **`unstable_cache` for the mark**: it is the one public call whose interval Next folds into the page's (Next 16.3.8, without `cacheComponents`, which the site does not use). The alternatives were worse: `unstable_noStore()` would make the page dynamic, read on every request; a second `fetch` with a short revalidation would send a request.
3. **The mark is made in the reader, not in `attempt()`**: so every caller that turns a failure into "no data" is covered, including `lib/grid.ts` and `lib/chat/tools.ts`, which catch it themselves. A route handler that meets a failed read writes one small cache entry and is otherwise unchanged (its answers are not cached by the page's interval).
4. **No build on a full disk**: with 426 MB free a build could have filled the disk under the other sessions' git writes; it waited until session 542 made room, then ran.
5. **No other worktree's files were removed** to make room: they are other sessions' (and the orchestrator lands from them).
6. **The healing check reads the page's text, not "no data"**: the two pages this table feeds write "could not be read" (`/events/caiso-heat-2022`) or show no notices (`/grid/caiso/alerts`); the check saves each answer's visible text (`runs/chain_024/s537/heal-*.txt`) and compares. The check scripts (`heal537.mjs`, `cc537.mjs`, `manifest537.py`) stay in `runs/chain_024/s537/`, not in the site.

## For Samuel's ruling

- The code machine's disk filled up on 21 October (27 MB free at 20:30 UTC) until session 542 removed 28 landed worktrees: a rule for removing a chain's worktrees once their branches land, or one shared `node_modules`, would keep it from happening again.

## To finish

Nothing for this session: the build proof, check-routes and check-values were run (above). After the landing, the memory note "build-can-cache-a-database-timeout" can say that a page now heals within a minute of a read that failed.

## Files

- `site/lib/supabase.ts` (changed), `site/scripts/alias-loader.mjs` (one stand-in added), `site/scripts/test-failed-read.mjs` (new), `site/scripts/failing-read-proxy.mjs` (new), `tests/test_session537.py` (new), this report.
