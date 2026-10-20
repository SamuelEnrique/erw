# Redivis release v1: the click, on one page

Energy Research Warehouse (ERW), session 312 (19 October 2026), for Samuel. The full steps and their reasons are in [`release-v1.md`](release-v1.md); this page is what to open, what to compare and what to press, on or after **21 October 2026**. No session releases: the click is a person's.

## Before you open Redivis (on the data machine, about 5 minutes)

| Do | Expect | If not |
|---|---|---|
| `python warehouse/redivis/release_v1.py` | "138 tables in v1 (with the three metadata tables), 43 public tables held out" (41 for a license, `node_basis_daily` and `ercot_all_hub_prices_history` for storage; 20 October 2026, session 385; the counts move with the license record and with new tables) | read the line it prints; a permission you recorded moves a table into v1. After a restore from the archive, read `git diff docs/redivis/release-v1/` first: a restored table's first header line is the restore's note, and a whole rewrite makes it the description of 63 tables (`release-v1.md`, step 1) |
| `python warehouse/redivis/release_v1.py --check` | exit 0, "0 difference(s)" | stop: the package and the license record disagree |
| `python warehouse/redivis/upload.py --reconcile` | every row of `runs/redivis_reconcile.csv` matches (the draft's `count(*)` against the CSV) | a table off by rows: run its stores (`python warehouse/table_stores.py <table>`) and reconcile again |

## The draft on 20 October 2026 (sessions 363 and 375)

- `python scripts/sync.py --check` at 20:19 UTC, after session 373 restored 71 tables from the archive: 209 tables in coverage; **201 current**, 1 behind (`api_cost_ledger`: the same 3,710 rows, Redivis's newest entry 38 minutes later), 2 diverged (`grid_network_links`, `price_board_latest`), 2 "ahead" (`eia930_all_storage`, `eia930_generation_latest`: this machine's runs, not uploaded) and 3 not on Redivis (`ercot_all_hub_prices_history`, `node_basis_daily`, `nyiso_load_queue`). At 11:00 UTC (session 363) it read 156 current and 49 behind.
- **The account's free storage of 10 GB is full.** Redivis refused `node_basis_daily` twice (10:25 and 11:03 UTC, session 363): "This import would cause your account to exceed its free storage allotment of 10GB." Since session 375 `tables.csv` marks it `in_v1 = held` ("held: Redivis storage"), not dropped: before the click, either make room (a paid tier, or tables taken out of the draft) and upload it (`python warehouse/redivis/upload.py node_basis_daily`), or delete its row from v1's list and note it. Step 3 below shows it missing until then. **Session 385 found a second one**: `ercot_all_hub_prices_history` (0.72 GB here) was in the draft until the daily's upload of 20 October, 17:32 UTC, was refused for storage; the uploader deletes a table before it uploads the new copy (Redivis uploads append, so that is its only true replace) and removes the empty new one when the upload fails, so the refusal left the table out (Redivis answers 404 for it). It is held in v1 the same way. While the storage stands, any growing table whose upload is refused leaves the draft in the same way (`docs/redivis/organization-move.md`, "The storage"). The daily step `dm_node_rt` (session 376) builds it without the Redivis step, and an upload refused for storage is a skip since session 377, not a failure.
- New in the draft since session 312: `price_years_by_window`, `node_basis_summary`, `ercot_4cp_intervals` (public) and `ercot_node_prices_hourly` (the internal dataset). `nlr_jedi_multipliers` and `impact_tax_rules` are in v1 since session 366; `iso_queue_statistics` comes with the code machine's `wip/348-map` and is not in the package until that branch is on main.
- The package was spliced, not rewritten (session 375): four rows changed (`node_basis_daily` held, and the publishers of `node_basis_summary`, `ercot_4cp_intervals` and `price_years_by_window`, from session 378's license record); `release_v1.py --check` reads 0 differences. No request was made to Redivis.

## On redivis.com (about 15 minutes)

1. **Open** the dataset `energy_research_warehouse` (the account `REDIVIS_OWNER`, or Ben Domingue's organization if it was moved), and switch to the draft (version `next`).
2. **Delete the held tables from the draft**: every row of [`release-v1/tables.csv`](release-v1/tables.csv) with `in_v1 = no` (41 today; the two `in_v1 = held`, `node_basis_daily` and `ercot_all_hub_prices_history`, are not in the draft at all). Do it right before the click: the daily upload puts a held table back when its data changes.
3. **Compare the table list** with the `in_v1 = yes` rows of `tables.csv`: the same names, and the three metadata tables `erw_coverage`, `erw_sources`, `erw_headers`.
4. **Paste the README**: [`release-v1/README.md`](release-v1/README.md) into the dataset's description.
5. **Spot-check three tables**: each description is the table's provenance header, with its `License:` line in it.
6. **Press Release.** The note: `v1: ERW commit <git rev-parse HEAD>, the daily run of <date>; 135 tables and 3 metadata tables; 41 held for a license, node_basis_daily and ercot_all_hub_prices_history for storage (docs/redivis/release-v1/tables.csv)`.

## After the click (2 minutes)

- Write the release date into [`release-v1.md`](release-v1.md) and the README's citation ("version v1, released YYYY-MM-DD"), and on `/data` replace "pending release" with the date (`site/app/data/page.tsx`, the line under "How to cite a table"). Commit and push.

## How a table is cited

> \<the publisher\>. \<the report\>. Via the Energy Research Warehouse (ERW), table `<table>`, Redivis dataset `energy_research_warehouse`, version v1 (released YYYY-MM-DD).

Each table's own line is in `tables.csv`, column `citation`. `/data` shows the form since session 312.
