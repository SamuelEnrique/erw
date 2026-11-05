# Session 563 report: chain 023's landing, merged on main through the full gate (`87c343cc`); Vercel has not deployed it yet

21 to 22 October 2026, 23:31 to 00:45 UTC, on portable-laptop (code role), from queue file `queue/done/032-night-22-october-code-563.md`, taken by name and pushed to main first (`aa5e8411`). The worktree is `C:\Users\samen\Documents\erw-429`, on `wip/563-land-023` (from `wip/562-land-023` at `2694ef9c`, merged with origin/main). The owner gave about 100 minutes. Model spend USD 0; no warehouse data written.

## Read these first

- **Landed on main.** `task/563-land-023` passed `code-branch.yml` (run 39697392914, success) and was merged as `87c343cc` at 00:12 UTC. The merge carries chain 023's ten branches (429, 430, 497 to 505), sessions 555 and 562's fixes and merges, and this session's report so far.
- **Not deployed yet.** In the 20 minutes the session waited, Vercel made no production deployment of `87c343cc` or of the commit after it (`16a76297`). The last is `ccc085a8` (23:29 UTC). Production still serves the earlier build: with the internal cookie, `/board` has no license line (502) and `/cost-of-power/battery` does not read "25 published figures" (501). Sessions 483 and 488 saw the same thing: Vercel was rate limited. The next deployment of main carries the landing. Checking it is queue file 036 (session 607).
- **Rule 8:** `s563-before` (00:03 UTC) against `s563-after` (00:35 UTC): 0 differences on 25 pages, expected. No deployment happened in between, and every page is in review, so a visitor sees the in-review page either way. A visitor still sees no difference once Vercel deploys, because no page is live (`site/lib/release.ts`). The snapshot after the deployment is in queue file 036.
- **The gate:** the suite (one error, the laptop's own `test_session185`), the build, the type-check and check-values in full. The ten floors that failed in session 562's run fail the same way on production, which is main's deploy, so they are main's and are named below. `/roundup`'s fetch failure did not recur when the page was read alone.

## Checks

Every output is in `runs/s563/` in the worktree (not in git). Commands are never piped, and each exit code was read.

| Check | Exit | Result |
|---|---|---|
| `scripts/chain_queue.py next --file 032-night-22-october-code-563.md`, pushed | 0 | `aa5e8411` on main |
| `scripts/precheck.py --what "session 563"` | 0 | passed; the duty mark is held by another checkout's token, so it was not set again |
| merge of origin/main (`424d8d8b`) | 0 | clean, `5f7c4cd7` (34 files from main) |
| `scripts/buildlock.py acquire s563` | 0 | |
| `scripts/freeze.py status` | 0 | no freeze |
| `scripts/db_probe.py` | 1, 1, 0 | open at 2.85 s (23:32 UTC) |
| `node scripts/build-content.mjs` | 0 | |
| `npm run build` | 0 | done 23:34 UTC |
| `npx tsc --noEmit` | 0 | |
| the whole suite | 1 | 5,585 tests in 20 minutes, 286 skipped, 1 error: `test_session185`'s dry run, a `PermissionError` deleting a copied `python.exe` from a temporary `.venv`. Sessions 429 and 503 recorded it on main on this laptop: the machine's, not the branch's. `test_session153`, which failed in session 562's run, passes |
| `check-values.mjs` in full on the build | 1 | 152 of 152 pages in 27.4 minutes (23:34 to 00:02 UTC), 6,456 of 6,456 values match Supabase, 11 FAILED: the known `/deals` floor under its hold; the nine other floors of session 562's run, with the same counts as on production (below); and `/roundup`'s "fetch failed". `/roundup` read again alone: no FAIL, 0 of 0 values, the same as production, and the page answers 200 in 14 ms. That run's exit is 127: its run-wide floor of ten values, then node's exit crash on Windows (`UV_HANDLE_CLOSING`), not a page fault |
| the ten floors on production (main's deploy, `CHECK_VALUES_PAGES=/map,/events,/learn/bill,/research/card/gas_sets_price,/roundup,/deals`) | 1 | 22 pages, 1,107 of 1,107 values match, 10 FAILED: the same ten floors with the same counts as on the branch's earlier run (`/deals` 1, `/map` 0, `/events` 2, `/events/uri-2021` 9, `/events/covid-2020` 7, `/events/caiso-heat-2020` 0, `/events/caiso-heat-2022` 0, `/events/east-heat-2025` 0, `/learn/bill` 5, `/research/card/gas_sets_price` 4). `/roundup` reads with no FAIL there |
| the six test modules main brought before the push (`test_session555` to `560`, the data machine's) | 0 | 26 tests |
| merge of origin/main before the push (`defab2f0`) | 0 | clean, `fbb2758f`; 34 files, none under `site/` |
| `snapshot-live.mjs take s563-before` | 0 | 25 pages, 0 failed (00:03 UTC) |
| `git push origin HEAD:refs/heads/task/563-land-023` | 0 | `fbb2758f` |
| `code-branch.yml` | success | run 39697392914, merged as `87c343cc` at 00:12 UTC |
| the Vercel deployment of `87c343cc` | none in 20 minutes | GitHub's deployments list (public API) ends at `ccc085a8`, 23:29 UTC; production read with the internal cookie still lacks 502's and 501's lines |
| `snapshot-live.mjs take s563-after` | 0 | 25 pages, 0 failed (00:35 UTC) |
| `snapshot-live.mjs compare s563-before s563-after` | 0 | 0 differences on 25 pages: expected (no deployment between them; every page in review) |

## Decisions made without you

1. **The ten floors are main's, not the branch's.** As the queue file asks, they were compared against main: production is main's deploy, and the same pages fail the same floors with the same counts there. They are named here, and they do not stop the landing. Why main's pages draw fewer numbers than their floors (a read that fails, a floor set when more was drawn, or a held table) is a fault on main for a later session.
2. **`/roundup`'s fetch failure is taken as transient.** Read alone, it gives what production gives.
3. **The suite ran beside check-values.** Session 562's floors needed check-values alone on the machine. The comparison with production settles them, the suite reads no page, and running them one after the other would not fit in 100 minutes.

## For Samuel's ruling

- None new.

## To finish

Queue file `queue/next/036-night-22-october-code-607.md` (session 607, machine: code) holds these:

```bash
# 1. Once Vercel has deployed main at or after 87c343cc (GitHub's deployments list for the Production environment, or the internal view):
#    with the internal cookie, /board shows "Tables read, with their licenses" and /cost-of-power/battery "25 published figures"
node site/scripts/snapshot-live.mjs take s607-after
node site/scripts/snapshot-live.mjs compare s563-after s607-after    # every line into the report; 0 expected (no page is live)
# 2. Delete the merged wip branches: wip/429-combined, wip/430-check-values, wip/497-faults, wip/498-digest-numbers,
#    wip/499-500-row-license, wip/501-battery-rows, wip/502-license-lines, wip/503-fresh-suite, wip/504-buildlock,
#    wip/505-check-holds, wip/555-land-023, wip/562-land-023, wip/563-land-023, and those named in session 429's "To finish"
#    (each only if `git merge-base --is-ancestor origin/<branch> origin/main` says it is merged)
```

Left from the branches' own "To finish", none of them part of the landing:

- **The ten floors on main** (`/deals` under its hold aside): `/map`, `/events`, `/events/uri-2021`, `/events/covid-2020`, `/events/caiso-heat-2020`, `/events/caiso-heat-2022`, `/events/east-heat-2025`, `/learn/bill`, `/research/card/gas_sets_price`. They draw fewer checked numbers than `scripts/check-values-floor.json` asks, on production too. Find why: a read that fails, a floor set when more was drawn, or a hold.
- **497**: the tall render frame's panels in two columns, and the README of `docs/brand/review-497/`.
- **503**: the suite in a fresh worktree, before and after `npm ci`.
- **499**: the data machine's columns (`publishers`, `row_license`) and `hold = row`.
- **498**: the daily run calling `check_digest.py` and `check_roundup.py` (a workflow change).
- **504**: chain files name `scripts/buildlock.py` in place of chain 019's helper.

## Files

- `archive/sessions/SESSION_563_REPORT.md` (this report).
- The merge of origin/main into the landing branch.
- Not in git: `runs/s563/` in the worktree.
