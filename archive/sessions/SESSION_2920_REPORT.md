# Session 2920 report: the TPIT refresh

6 November 2026, about 05:22 to 05:26 UTC, on lab-desktop (the data machine), chain 153, unattended. Model spend USD 0. Pulls: www.ercot.com, 3 requests of the 10 allowed. The planning page came through the probe (`runs/s2920/probe.csv`), then the connector's own page and workbook. Robots was read by session 2919 ten minutes before: `/gridinfo/` and `/files/` are allowed.

## Read these first

- **ERCOT's planning page now links the October TPIT:** `https://www.ercot.com/files/docs/2022/03/02/ERCOT-October-TPIT-No-Cost-100126.xlsx`, "OCTOBER BASE ... FUTURE PROJECTS AS OF 10/1/2026". The table's base was July's ("AS OF 7/13/2026").
- **`ercot_transmission_projects` written again** (`runs/c147/write_table.sh`, under the data lock): **2,203 project phases** (future 1,508, completed 319, planned 277, cancelled 99; 55 owners), against July's 2,122. Validator pass, coverage row, archive run `20261106T052319Z-local`. Commit `56f69d464`.
- **`ercot_node_transmission` rebuilt** on it: 569 nodes, 148 counties, 11 with no phase. Archive run `20261106T052348Z-local`. Commit `9e414ede7`.
- **`site/data/siting/nodes.json` rebuilt** (`warehouse/derived/siting_page.py`, the main checkout's tables read first). Two parts changed:
  - its `projects` block names the October workbook;
  - its `planned` block moves from EIA-860M's August vintage to September (October 2026 to September 2027).
  - Tests that read `nodes.json`: 42 passed, 2 skipped. Commit `4db733e23`.
- **The tab's other files were not taken.** `carbon.json` and `headroom.json` also differed, with newer hours and a newer EIA-860M month. This step names only `nodes.json`; those files are the daily builders'.

## Decisions made without you

- **Only `nodes.json` committed** of the nine files `siting_page.py` wrote.
- **`nodes.json`'s newer planned generation kept with the TPIT.** The builder writes both blocks together, and the newer month is the warehouse's own table.

## For Samuel's ruling

- None.
