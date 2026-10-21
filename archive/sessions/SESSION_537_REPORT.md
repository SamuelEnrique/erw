# Session 537 report: a build does not keep a failed read

21 October 2026, about 20:20 to 21:00 UTC, unattended, on samueloldlaptop (the code machine), in the worktree `C:\Users\lossa\Documents\erw-537` on `wip/537-s` (from `origin/main` at `2ecba09d`). Chain 024 (`queue/done/024-night-21-october-code.md`), session 537. Model spend USD 0; no pull from any publisher; no warehouse data written; `site/lib/release.ts` not touched; no page's text or default figure changed.

## Read these first

- **The disk of this machine is full.** At 20:30 UTC `npm ci` in the worktree failed with `ENOSPC: no space left on device` (8 lines in `runs/chain_024/s537/npm-ci.out`); `C:` had 27 MB free. The partial `site/node_modules` this session had written (480 MB) was removed, which brought it to 633 MB; by 20:39 it was down to 426 MB again (the other worktrees hold about 528 MB of `node_modules` and 150 to 500 MB of `.next` each: `erw-531`, `532`, `533`, `535`, `538`, `541`). This session deleted nothing but its own files. **No build was made**, so check-routes and the build proof wait under "To finish". Session 542's landing needs space before its build.
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
| `npm run build`, check-routes, check-values | not run | no disk space (above): under "To finish" |

## Decisions made without you

1. **A minute** (`RETRY` = 60): short enough that a page heals between two visits, long enough that a database that is down is asked at most once a minute a page. It is shorter than both of the site's intervals (900 and 3,600 s).
2. **`unstable_cache` for the mark**: it is the one public call whose interval Next folds into the page's (Next 16.3.8, without `cacheComponents`, which the site does not use). The alternatives were worse: `unstable_noStore()` would make the page dynamic, read on every request; a second `fetch` with a short revalidation would send a request.
3. **The mark is made in the reader, not in `attempt()`**: so every caller that turns a failure into "no data" is covered, including `lib/grid.ts` and `lib/chat/tools.ts`, which catch it themselves. A route handler that meets a failed read writes one small cache entry and is otherwise unchanged (its answers are not cached by the page's interval).
4. **No build on a full disk**: a build writes 150 to 500 MB into `.next`, and with 426 MB free it could have filled the disk under the other sessions' git writes. The proof that needs a build is left with its exact commands.
5. **No other worktree's files were removed** to make room: they are other sessions' (and the orchestrator lands from them).

## For Samuel's ruling

- The code machine's disk (238 GB) is full: about 3.5 GB of it is the chain's worktrees' `node_modules` and `.next`; the worktrees of landed sessions could be removed after session 542's landing (git worktree remove), or `node_modules` shared.

## To finish

Each under the build mutex (`mkdir C:/Users/lossa/Documents/erw/runs/build.lock`, `owner.txt`, `duty.py beat`, `db_probe.py`), from `C:/Users/lossa/Documents/erw-537/site` (or the landing's copy), once the disk has at least 2 GB free. `F=C:/Users/lossa/Documents/erw/runs/chain_024/s537`.

1. `npm ci > $F/npm-ci-2.out 2>&1; echo "exit=$?"`
2. The proof build, one table failed on purpose (`caiso_grid_emergencies`, read by `/grid/caiso/alerts` and `/events/caiso-heat-2022` through `attempt()`):
   - `touch $F/fail.flag`
   - in the background: `node --env-file=.env.local scripts/failing-read-proxy.mjs --port 54537 --fail caiso_grid_emergencies --while $F/fail.flag --log $F/proxy.log`
   - `SUPABASE_URL=http://127.0.0.2:54537 npm run build > $F/build-proof.out 2>&1; echo "exit=$?"`
   - `C:/Users/lossa/Documents/erw/.venv/Scripts/python.exe $F/manifest537.py .next/prerender-manifest.json $F/baseline-prerender-manifest.json > $F/manifest-diff.txt` (the baseline is the main copy's build of 09:37 UTC, copied into `$F`: 43 routes at 3600, one at 900, one at 600, 148 with none, none at 60). Expected: the two pages above at 60, every other route as in the baseline (a route added since 09:37 named).
   - `SUPABASE_URL=http://127.0.0.2:54537 npx next start -p 3537`; `/grid/caiso/alerts` shows its "no data"; `rm $F/fail.flag`; after 65 s two requests: the second shows the notices; the proxy log shows no read for `/events/uri-2021` or `/data` when they are asked after 65 s (pages that read well are not regenerated).
3. Stop that server; the ordinary build: `npm run build > $F/build.out 2>&1; echo "exit=$?"`, `npx next start -p 3537`, `node scripts/check-routes.mjs http://localhost:3537 > $F/check-routes.out 2>&1; echo "exit=$?"`, `node scripts/check-values.mjs http://localhost:3537 > $F/check-values.out 2>&1; echo "exit=$?"` (twice if the first differs: the stale fetch cache; the ten held pages' floors fail as expected). Stop the server on port 3537; let the mutex go.
4. After the landing, the memory note "build-can-cache-a-database-timeout" can say a page now heals within a minute.

## Files

- `site/lib/supabase.ts` (changed), `site/scripts/alias-loader.mjs` (one stand-in added), `site/scripts/test-failed-read.mjs` (new), `site/scripts/failing-read-proxy.mjs` (new), `tests/test_session537.py` (new), this report.
