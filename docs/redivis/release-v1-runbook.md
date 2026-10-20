# Redivis release v1: the click, on one page

Energy Research Warehouse (ERW), session 312 (19 October 2026), for Samuel. The full steps and their reasons are in [`release-v1.md`](release-v1.md); this page is what to open, what to compare and what to press, on or after **21 October 2026**. No session releases: the click is a person's.

## Before you open Redivis (on the data machine, about 5 minutes)

| Do | Expect | If not |
|---|---|---|
| `python warehouse/redivis/release_v1.py` | "138 tables in v1 (with the three metadata tables), 41 public tables held out" (20 October 2026, session 363; the counts move with the license record and with new tables) | read the line it prints; a permission you recorded moves a table into v1 |
| `python warehouse/redivis/release_v1.py --check` | exit 0, "0 difference(s)" | stop: the package and the license record disagree |
| `python warehouse/redivis/upload.py --reconcile` | every row of `runs/redivis_reconcile.csv` matches (the draft's `count(*)` against the CSV) | a table off by rows: run its stores (`python warehouse/table_stores.py <table>`) and reconcile again |

## The draft on 20 October 2026 (session 363)

- `python scripts/sync.py --check` at 11:00 UTC: 209 tables in coverage; 156 current, 49 behind (the runner's uploads are newer than this machine's copies), 2 diverged, **1 "ahead"** (`eia930_generation_latest`: uploaded at 11:03 UTC, then found to be an older snapshot by the archive's comparison, session 362, and the runner's version put back at 11:33 UTC, count(*) 1,906) and **1 not on Redivis** (`node_basis_daily`, the chain's new table of 950,000 rows).
- **The account's free storage of 10 GB is full.** Redivis refused `node_basis_daily` twice (10:25 and 11:03 UTC): "This import would cause your account to exceed its free storage allotment of 10GB." It is listed in v1 by the license record (`tables.csv`) but is not in the draft: before the click, either make room (a paid tier, or tables taken out of the draft) and upload it (`python warehouse/redivis/upload.py node_basis_daily`), or delete its row from v1's list and note it. Step 3 below will show it missing until then.
- New in the draft since session 312: `price_years_by_window`, `node_basis_summary`, `ercot_4cp_intervals` (public) and `ercot_node_prices_hourly` (the internal dataset).

## On redivis.com (about 15 minutes)

1. **Open** the dataset `energy_research_warehouse` (the account `REDIVIS_OWNER`, or Ben Domingue's organization if it was moved), and switch to the draft (version `next`).
2. **Delete the held tables from the draft**: every row of [`release-v1/tables.csv`](release-v1/tables.csv) with `in_v1 = no` (42 today, session 367). Do it right before the click: the daily upload puts a held table back when its data changes.
3. **Compare the table list** with the `in_v1 = yes` rows of `tables.csv`: the same names, and the three metadata tables `erw_coverage`, `erw_sources`, `erw_headers`.
4. **Paste the README**: [`release-v1/README.md`](release-v1/README.md) into the dataset's description.
5. **Spot-check three tables**: each description is the table's provenance header, with its `License:` line in it.
6. **Press Release.** The note: `v1: ERW commit <git rev-parse HEAD>, the daily run of <date>; 137 tables and 3 metadata tables; 42 held for a license (docs/redivis/release-v1/tables.csv)`.

## After the click (2 minutes)

- Write the release date into [`release-v1.md`](release-v1.md) and the README's citation ("version v1, released YYYY-MM-DD"), and on `/data` replace "pending release" with the date (`site/app/data/page.tsx`, the line under "How to cite a table"). Commit and push.

## How a table is cited

> \<the publisher\>. \<the report\>. Via the Energy Research Warehouse (ERW), table `<table>`, Redivis dataset `energy_research_warehouse`, version v1 (released YYYY-MM-DD).

Each table's own line is in `tables.csv`, column `citation`. `/data` shows the form since session 312.
