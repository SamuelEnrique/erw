# Session 7009 report: the landing desk's new rows, the large-load data requests 18 to 22 and 28, the live set

Energy Research Warehouse (ERW). Chain 301, data machine (lab-desktop), 16 November 2026. Opus 5.5. Model spend USD 0.

## The landing desk

- **Gate a** (companies, policy, sessions 7000 to 7002) landed at `bce9303d6` (task/7002-landing, run 43843414368; every step of `land_check.py` passed, the suite 9,537 tests OK). The task workflow ran the suite a second time because main moved under it (this chain's progress push); no push to main while a landing is in flight after that. Snapshots `before-1dc85dc4` and `after-1dc85dc4`: 0 differences.
- **Requested since 16 November:** the old laptop's rows 15 (`wip/7200-large-load`, `d192de75c`) and 16 (`wip/7202-key-refusal`, `b793f3c7f`), the portable's row 33 (`wip/7400-trackers`, `7a39daafa`). Stacked in that order on origin/main as `wip/c301-desk-a`: each merges cleanly, and so does this chain's branch. They go through the gate after gate b (the build lock holds one gate at a time).

## The live set

- **Loaded** (snapshots `before-load7004` and `after-load7004`: 0 differences): `iso_dam_hub_prices`, `iso_rtm_hub_prices`, `eia930_all_demand`, `eia930_all_generation`, `eia930_generation_latest`, `policy_actions` and the three attention tables; every table "match". The loader's exit 1 is the stale IEA source row alone (`load.py --prune` is the owner's). The days of 5 to 8 November now stand in the live set for US48 demand, CAISO and SPP.

## The data requests (`docs/state/data_requests_large_load.md`)

- **18** not loaded: the three research tables' verdict is unsettled; the default taken, they stay out of the live set.
- **19** noted: the tables were rewritten today row for row the same; the page file follows `wip/7200-large-load`'s landing.
- **20** done: `warehouse/derived/ercot_zone_wires.py` writes `site/data/siting/ercot_zone_wires.json` from `ercot_node_wires_utilities` (the TDSPs of each CDR zone by county count; NORTH: Oncor 36, TNMP 19; WEST: Oncor 32, AEP Texas North 26; SOUTH: AEP Texas Central 24; HOUSTON: CenterPoint 5). ERCOT's ESI ID extract is under `/misdownload`: not read. The cell is a code row (data_ready 15).
- **21** answered: both FERC-714 filings carry one ERCOT forecast (2030 summer peak 138,944 MW and 138,944.36 MW); the +0.36 MW is right as printed.
- **22** answered: no later LLWG status report exists in any form; the meetings of July to October link none, and the three decks read to check carry none of the status sentences.
- **28** done: the monitor reads the 15 operator and FERC steps of `utility_large_load_rule_changes` as documents by written rules (12 records, 5 of them joining FERC dockets held); `monitor.json` 2,078 documents, 1,533 records; the policy replication reads them too, 23,269 of 23,269 equal.
- **23, 24, 25, 26, 27, 29** follow the desk's landing (23 and 25 change `siting_page.py` and its tests; 29 edits the research files that `wip/7200-large-load`'s page builder reads; 24, 26 and 27 are readings of commission and legislature copies).

## Requests: the done line (`docs/state/data_requests_done_line.md`)

- **1** noted: after goals 1 to 4 and the requests, the tools marked lab-desktop in `docs/state/done_line_claims.md`, in order (`/board`, `/prices`, `/prices/compare`, `/supply`, `/storage`, `/demand`, `/curtailment`, `/queues`).

## Decisions made without you

- **Two landings in one gate** where they stack cleanly (the desk's three rows and this chain's later commits), to keep the build lock's hours short.
- **A rule change's sector** is left empty (not scored), as any unscored record's.

## For Samuel's ruling

- None new.
