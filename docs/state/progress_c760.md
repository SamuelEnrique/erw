# Progress of chain 760 (data machine, the one desktop window, weekend of 28 November 2026)

One line a landing, request, table, file or view: its state and session, pushed after each. The chain file is `queue/done/760-weekend-28-november-desktop-desk-regions-forecast.md`.

## The start (session 11200)

- start 1, precheck and main: done, session 11200 (10:33 UTC). Precheck exit 0, on duty until 2026-11-29 02:33 UTC. Main pulled to origin/main (fast-forward, nothing local ahead, so no `wip/c760-local-2026-11-28`). Session numbers 11200 to 11399: none used on origin/main or any branch. Untracked files left where they are: `site/data/findings/queue_divorce__first_year-2010.json`, `site/public/findings/erw_2026_queue_outcomes_technology__first_year-2010.csv`, `site/public/findings/queue_divorce__first_year-2010.do` and `.py`, `warehouse/output/retired/` (and the ignored `runs/`, `warehouse/output/`, untouched). Drive C 13 GB free at 10:33 UTC, memory 7.2 GB free. Under 20 GB: the 26 worktrees whose branch is already in origin/main were removed (`runs/c760/merged_worktrees.out` lists each with its ignored files; each one's ignored `runs/` folder moved first to `runs/wt_saved/<worktree>/`; `runs/c760/remove_merged.out`). Drive C then 46 GB free. The gate worktrees `erw-land-*` and every worktree on an unlanded branch left as they are.
- start 2, the chain file taken: done, session 11200 (`chain_queue.py next --file`, commit `32f9e8808`, pushed 10:34 UTC).
- start 3, chains 701, 730 and 740 closed: see "Taken over" below; their notes end with a line saying chain 760 took them over; their resume files 702, 731 and 741 removed from `queue/next/` in one commit.
- start 4, resume file `queue/next/761-resume-chain-760.md`: see below.
- start 5, this file: done, session 11200.

## Taken over

From chain 701 (data machine, first window; stopped 10:30 UTC 28 November on Samuel's word):

- `wip/c701-g38` (spp_mtlf_hourly, SPP's mid-term load forecast, predict data request 19): pushed, not gated; its one failing test is test_codebook (the x_ columns need units in the codebook entry). To gate, land with snapshots, mark row 19.
- `wip/c701-q-docs` (chain 701's last progress lines and the predict rows 14, 18, 20 states): docs only, to merge to main with a snapshot pair.
- Five tools data request 48 (PJM's highest-hours windows): in part.
- Predict data request 20 (24 ledger rows of ba-spa without a figure): open.
- Predict data request 21 (SPP South Hub and CAISO ZP26 price history, ERCOT's Panhandle hub): open.
- Predict data request 3 (the backtests as tables): the shape chosen by chain 730's row 12; the table writes wait on row 12 landing.
- The daily run's `dm_predict_ahead` took 4 h 34 min against about 25 minutes planned: chain 730's and Samuel's choice (now this chain's, part D).
- The old laptop's landing row 132 (`wip/audit-home-words-2`): returned by chain 701 (its own test stale on main); still marked requested in the file.
- For Samuel's ruling, carried with their defaults (chain 701's note): the large-load changes after 13 November not loaded; the signature pack's moving figures; pge.com's terms; news dated after retrieval; held grids' prices in git history; MISO's files under its pause; FERC EQR 2026 Q3 not pulled; hourly network 3 to 4 hours stale while the daily run runs.

From chain 730 (desktop second window, the ERW forecast; stopped 10:31 UTC 28 November on Samuel's word):

- Landing rows 12 (`a2365371d`), 13 (`76931398f`) and 14 (`11d9eb9eb`) of `docs/state/landing_request_window2.md`: requested, not landed. Row 14 carries 12 and 13.
- `wip/c730-predict-v9` at `a7530e4dc` (work in progress): `long_ahead.py` and `replicate_long_ahead.py` (Texas 125 of 125); wind and solar at AVRN, GRID, GWA (trial 1,688 of 1,688); `shown_for` on every hub (chain 720's request 15). Not done: the whole-file replications of the rebuilt `wind_solar.json`, `price_hubs.json` and `rt_price.json`; the longer backtest further ahead (rerun `runs/c730/la_part{0,1,2}.ps1`, then `long_ahead.py --merge`); `predict.md` section 30; the contract's line; the suite; landing row 15.
- ba-sceg's demand two days behind the other places in the place files of 28 November (chain 730 to rule; now part D).
- The codebook: 38 second looks on 30 tables open.

From chain 740 (desktop third window, datacenters in the Economic impact tool):

- Every row it requested is on main and read on production (its last line, 10:19 UTC 28 November). Open: decision 27 (Meta's construction default and further Meta posts) for Samuel's ruling; several states held by their hosts (refused or not readable). No branch left unlanded.

## Part A: the desk

- desk, session 11200 start (10:36 UTC, `runs/c760/desk.py`): requested and open: window2 rows 12, 13, 14 (chain 730's, taken over); the old laptop's row 132 (returned, see above); predict data requests 19 (on `wip/c701-g38`), 20, 21; five tools 38 (nothing for this machine) and 48 (in part); predict 14 (landed in gate 37) and 15 (on `wip/c730-predict-v9`). `landing_request_portable.md` and `landing_request_portable_w2.md`: nothing requested.

## Part B: where the next gigawatts can go

- B1, the contract `docs/state/page_files_siting_regions.md` and three example files under `site/data/siting/regions/` (index.json with one place of each kind, op-ercot.json, table.json; every value null, `"example": true`), written by `warehouse/derived/siting_regions.py --example` (the builder's skeleton, on `wip/c760-regions`): pushed to main, session 11200 (within the chain's first hour).
- Gate 1 (`wip/c760-g1`: chain 701's `wip/c701-g38`, spp_mtlf_hourly, with its codebook units fixed; window2 row 14, `wip/c730-predict-v8` at `11d9eb9eb`, which carries rows 12 and 13): started 10:48 UTC on `a72e4d6c8`. A merge slip of mine first took main's whole `tests/test_predict.py` (dropping row 14's own test of a held forecast); redone hunk by hunk before the gate (49 related tests pass).
