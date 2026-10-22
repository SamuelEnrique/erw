# Session 563 report: chain 023's landing, STATUS_TITLE

21 to 22 October 2026, 23:31 to END_TIME UTC, on portable-laptop (code role), from queue file `queue/done/032-night-22-october-code-563.md`, taken by name and pushed to main first (`aa5e8411`). The worktree is `C:\Users\samen\Documents\erw-429`, on `wip/563-land-023` (from `wip/562-land-023` at `2694ef9c`, merged with origin/main). The owner gave about 100 minutes. Model spend USD 0; no warehouse data written.

## Read these first

READ_FIRST

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
SNAPSHOT_ROWS

## Decisions made without you

1. **The ten floors are main's, not the branch's.** As the queue file asks, they were compared against main: production is main's deploy, and the same pages fail the same floors with the same counts there. They are named here, and they do not stop the landing. Why main's pages draw fewer numbers than their floors (a read that fails, a floor set when more was drawn, or a held table) is a fault on main for a later session.
2. **`/roundup`'s fetch failure is taken as transient.** Read alone, it gives what production gives.
3. **The suite ran beside check-values.** Session 562's floors needed check-values alone on the machine. The comparison with production settles them, the suite reads no page, and running them one after the other would not fit in 100 minutes.

## For Samuel's ruling

- None new.

## To finish

TO_FINISH

## Files

- `archive/sessions/SESSION_563_REPORT.md` (this report).
- The merge of origin/main into the landing branch.
- Not in git: `runs/s563/` in the worktree.
