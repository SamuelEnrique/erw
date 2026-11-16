# Session 7000 report: the ground of chain 301

Energy Research Warehouse (ERW). Chain 301 (`queue/done/301-day-16-november-desktop-open-faults.md`), data machine (lab-desktop), 16 November 2026 from 08:51 UTC. Opus 5.5. Model spend USD 0 (`ERW_SPEND_CAP_USD=0`).

- **The queue step:** `chain_queue.py next --file 301-...` took the file (`d00bb5644`), pushed after `git pull` (exit 0).
- **Precheck** passed (on duty until 2026-11-17 00:52 UTC). **Freeze:** none. Session numbers 7000 to 7003 free on main and every branch.
- **Memory** 6.9 GB free of 16; disk 236 GB free. Chain 285's session was not running (its last commit a "waiting" at 08:46 UTC); the data lock free.
- **The live site answers 200 again** (`erw-flame.vercel.app`; it answered 402 from 24 October), so a push to main deploys: every push of this chain to main has its snapshots.
- **Worktrees:** `erw-c278q` (detached, merged into main) removed after listing its one ignored folder (`scripts/__pycache__/`). The other worktrees hold commits not on main and stay.
- **Parked:** `queue/next/286-day-26-november-data-continued.md` to `queue/parked/` (`57cc612a9`'s neighbour commit); 284 and 300 were already parked by session 7200 (chain 302). No data machine resume file was in `queue/next/`.
- **Resume pointer** `queue/next/310-resume-chain-301.md`, the block of the chain file word for word, committed alone and pushed (`e9854ce9f`).
- **Progress file** `docs/state/progress_c301.md` on main.
- **Landing desk:** no row requested in the four `landing_request_*.md` files; no row of `data_requests_*.md` dated 16 November or later.
- **Snapshots** for the queue pushes: `after-q286` against `after-q301`, 0 differences (every page is in review); `before-p301a` before the progress file's push.

## Goal 1, the rows read in this session (nothing to fix: each checked on the live set)

- **Deals 9** not a fault now: both rows (Anthropic and Google's cloud and chips, Anthropic and Nscale) have `kind` `compute_capacity` in the live set, which `supplyOf` reads as compute, not grid supply.
- **Deals 12** not a fault now: the live set's 590 `energy_deals` rows carry `kind` on 590, `buyer_name` on 420, `usd` on 300, `stage` on the 56 that state one, `flags` on 14 (loaded 13 November).
- **Deals 10, 11, 13** need the key: the re-extraction with the v2 prompt (899 stories behind the 583 rows, Sonnet 5.5, about USD 3). The rows are held whole under the license hold (row 1) meanwhile.
- **Datacenter 8** not a fault now: the live set's 458 facilities carry `grid` on 178, `power_kind` on 24; the grid loads read PJM planned 10,400 MW and MISO 700 MW beside ERCOT's 235, the timeline 9 rows.

## Needs the key

- Deals rows 10, 11, 13: the v2 re-extraction, about USD 3.

## Decisions made without you

- The progress file lives on main (pushed with snapshots), so a restarted session finds it where the resume block says; the code and tables go on `wip/c301-data`.
- Chain 285's two unlanded reports (sessions 3993 and 3994, on `wip/c285-data` between its "waiting" commits) are cherry-picked into this chain's branch so they land; the waiting commits are left.

## For Samuel's ruling

- None new.
