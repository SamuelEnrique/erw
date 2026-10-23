# The researcher's path: ERCOT's hub prices for 2025, in Stata, with a citation

Energy Research Warehouse (ERW), session 1017 (chain 070), 23 October 2026. A Stanford researcher who works in Stata wants ERCOT's hub prices for 2025 and a line to cite them. The path was walked click by click on a build of `wip/1016-packages` in the internal view, at 1280 and 390 (`runs/walk1017.mjs`; the shots in `docs/brand/review-1017/`, `step<N>_<width>.png`).

| Step | Where | What the page showed | Did it answer? |
|---|---|---|---|
| 1 | `/` | "Data and methods", linked to `/data`, in the header, the menu and the footer | yes |
| 2 | the menu, opened | "Data and methods" beside "Datacenters" and the datacenter tracker | yes |
| 3 | `/data` | the page, its coverage table first | yes |
| 4 | `/data#tools` | the three panels; Stata's has the install line and the six subcommands, each with a Copy control | yes |
| 5 | `/data#ercot_all_hub_prices_history` | the table's row: "Redivis" in its download column (the live set does not hold the history); its three lines opened: `erw fetch ercot_all_hub_prices_history, clear` | in part: no line names the year |
| 6 | `/data/methods/packages` | the specification: "Python keeps three more arguments for the partitioned tables (market, ba, year). Stata and R take them as options of the same names." | the note said so; the packages did not |

## What broke, and what was fixed

- **Stata and R had no `market()`, `ba()` or `year()`** (fixed in this session). The specification said they did, and Python did; without them a Stata reader of `ercot_all_hub_prices_history` would read its whole history (about 3 million rows) to keep one year. Both now take the three options: sent to the live set as the Python package sends them (the address of a partitioned call is the same in the three, checked), and applied after a read from Redivis or local files. The command the researcher needs:

  ```stata
  erw fetch ercot_all_hub_prices_history, market(ercot_dam) year(2025) clear
  erw cite ercot_all_hub_prices_history
  ```

- **The table is on Redivis only, and Redivis's released version holds no ERW table until the owner's click** (not fixed: the release is the owner's). The live set does not keep the ERCOT history (`live_set.yaml`), and `datapages.erw:b9wm` is at v1.0, the starter table alone. So today a researcher outside the project cannot fetch ERCOT's 2025 hub prices with any of the three packages. The last 35 days of the hub prices are in the live set (`iso_dam_hub_prices`), but that table is held for its MISO rows.

## After the click

Once version 1 is released, the two lines above read the record, and the citation names its tag:

> Electric Reliability Council of Texas (ERCOT). ... Via the Energy Research Warehouse (ERW), table `ercot_all_hub_prices_history`, Redivis dataset `datapages.erw`, version <tag>.
