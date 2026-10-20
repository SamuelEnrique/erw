# Redivis release v1: the steps

Energy Research Warehouse (ERW), session 275 (14 October 2026). Everything for one click, by a person signed in to Redivis with edit access to the dataset `energy_research_warehouse` (its owner, the account named `REDIVIS_OWNER`, or a member of Ben Domingue's organization given that access). **Nothing was created, changed or released on Redivis in preparing this.** No script in the repository releases a version (`warehouse/redivis/README.md`, "The rule").

## What v1 is

- **135 tables and the three metadata tables** (`erw_coverage`, `erw_sources`, `erw_headers`), listed with `in_v1 = yes` in [`release-v1/tables.csv`](release-v1/tables.csv): every table coverage flags public that is still public on the public day, **21 October 2026**.
- **42 tables of the public draft are held out** (`in_v1 = no`, each with its reason): a publisher's terms ask for permission or a license that is not recorded (`warehouse/metadata/license_status.csv`). Internal tables are never in this dataset; they are in `energy_research_warehouse_internal`, which stays private.
- **2 tables are held for Redivis's storage** (`in_v1 = held`, sessions 375 and 385): `node_basis_daily` is in v1 by its license, but the account's free 10 GB is full and Redivis refused it (session 363); `ercot_all_hub_prices_history` was in the draft until 20 October, when the daily's upload was refused for storage and the uploader, which deletes a table before it uploads its new copy, left it out. Each is uploaded once the storage is settled (`python warehouse/redivis/upload.py <table>`), or its row is taken out of v1 and noted; no session uploads them.
- For each table, `tables.csv` gives its description (the first line of its provenance header, which the uploader already set as the table's description), its license line (the header's own `License:` line, or the license record's verdict where the header has none), its citation and its publishers. [`release-v1/variables.csv`](release-v1/variables.csv) gives every series variable with its unit and every column of the entity and event tables (4,496 rows on 20 October 2026, session 366). [`release-v1/README.md`](release-v1/README.md) is the dataset's README.

## The steps (about 20 minutes, on or after 21 October 2026)

1. **Bring the package up to date and check it.** In a checkout of `main` on the data machine:
   ```bash
   python warehouse/redivis/release_v1.py          # rewrites docs/redivis/release-v1/ from today's records
   python warehouse/redivis/release_v1.py --check  # exit 0: tables.csv agrees with coverage and the license record
   ```
   A permission recorded before the day (a filled `permission` column in `license_status.csv`) moves that table into v1 here. On the data machine after a restore from the archive (session 373), a restored table's first header line is the restore's own note ("Rebuilt from the ERW archive by warehouse/restore_tables.py ..."), not the table's title, so a whole rewrite would give 63 of the package's tables that note as their description (counted by session 375) until their connectors next write them: splice the rows that change instead (session 375 did, for four tables), and read `git diff docs/redivis/release-v1/` before committing.
2. **Check the draft against the tables on disk:** `python warehouse/redivis/upload.py --reconcile` (read only: `count(*)` of every draft table against its CSV, written to `runs/redivis_reconcile.csv`). Every row should match.
3. **Open the dataset** on redivis.com, switch to the draft (version `next`).
4. **Remove the 42 held tables from the draft**, each named in `tables.csv` with `in_v1 = no`: the table's menu, Delete (the draft only; a released version keeps what it held). Do this right before the click: the daily upload puts a held table back into the public draft whenever its data changes, because the uploader routes by coverage's flag (ruling 1 below).
5. **The dataset's README:** paste `docs/redivis/release-v1/README.md` into the dataset's description.
6. **Spot-check three tables:** each table's description is its provenance header (cut at Redivis's 2,000 characters), and its license line is in it.
7. **Click Release.** The version's note: `v1: ERW commit <git rev-parse HEAD>, the daily run of <date>; 135 tables and 3 metadata tables; 42 held for a license, node_basis_daily and ercot_all_hub_prices_history for storage (docs/redivis/release-v1/tables.csv)`.
8. **Record it:** the date of the release in this file and in `docs/redivis/release-v1/README.md`'s citation ("version v1, released YYYY-MM-DD"), committed.

## How to cite v1

> \<the publisher\>. \<the report\>. Via the Energy Research Warehouse (ERW), table `<table>`, Redivis dataset `energy_research_warehouse`, version v1 (released YYYY-MM-DD).

Each table's own line is in `tables.csv`, column `citation`.

## For a ruling before the day

1. **The uploader and the held tables.** `upload.py` routes a table by coverage's flag, so from 21 October a held table whose data changes goes back into the public draft, and step 4 must be repeated before each release. One change would route a held table to the private dataset from its date. Make it?
2. **The by-grid tables.** 36 of the 42 are held only for ISO-NE's, MISO's and NYISO's rows on the site; v1 holds them out whole. A copy without those rows could be in v1 instead.
3. **Who clicks:** the owner's account (`owner_kind: user` in `warehouse/redivis/config.yaml`), or the dataset moved to Ben Domingue's organization first.
