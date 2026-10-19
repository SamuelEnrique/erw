# Redivis release v1: the click, on one page

Energy Research Warehouse (ERW), session 312 (19 October 2026), for Samuel. The full steps and their reasons are in [`release-v1.md`](release-v1.md); this page is what to open, what to compare and what to press, on or after **21 October 2026**. No session releases: the click is a person's.

## Before you open Redivis (on the data machine, about 5 minutes)

| Do | Expect | If not |
|---|---|---|
| `python warehouse/redivis/release_v1.py` | "126 tables in v1 (with the three metadata tables), 41 public tables held out" (the counts move with the license record) | read the line it prints; a permission you recorded moves a table into v1 |
| `python warehouse/redivis/release_v1.py --check` | exit 0, "0 difference(s)" | stop: the package and the license record disagree |
| `python warehouse/redivis/upload.py --reconcile` | every row of `runs/redivis_reconcile.csv` matches (the draft's `count(*)` against the CSV) | a table off by rows: run its stores (`python warehouse/table_stores.py <table>`) and reconcile again |

## On redivis.com (about 15 minutes)

1. **Open** the dataset `energy_research_warehouse` (the account `REDIVIS_OWNER`, or Ben Domingue's organization if it was moved), and switch to the draft (version `next`).
2. **Delete the held tables from the draft**: every row of [`release-v1/tables.csv`](release-v1/tables.csv) with `in_v1 = no` (41 today). Do it right before the click: the daily upload puts a held table back when its data changes.
3. **Compare the table list** with the `in_v1 = yes` rows of `tables.csv`: the same names, and the three metadata tables `erw_coverage`, `erw_sources`, `erw_headers`.
4. **Paste the README**: [`release-v1/README.md`](release-v1/README.md) into the dataset's description.
5. **Spot-check three tables**: each description is the table's provenance header, with its `License:` line in it.
6. **Press Release.** The note: `v1: ERW commit <git rev-parse HEAD>, the daily run of <date>; 126 tables and 3 metadata tables; 41 held for a license (docs/redivis/release-v1/tables.csv)`.

## After the click (2 minutes)

- Write the release date into [`release-v1.md`](release-v1.md) and the README's citation ("version v1, released YYYY-MM-DD"), and on `/data` replace "pending release" with the date (`site/app/data/page.tsx`, the line under "How to cite a table"). Commit and push.

## How a table is cited

> \<the publisher\>. \<the report\>. Via the Energy Research Warehouse (ERW), table `<table>`, Redivis dataset `energy_research_warehouse`, version v1 (released YYYY-MM-DD).

Each table's own line is in `tables.csv`, column `citation`. `/data` shows the form since session 312.
