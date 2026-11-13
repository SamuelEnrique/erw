# Session 3851 report, with 3852 and 3853: the daily run's week, the package's cite test, the findings, the drafts

Energy Research Warehouse (ERW). Chain 221, data machine (lab-desktop), 13 November 2026 05:54 to 06:20 UTC. Opus 5.5. Model spend USD 0. Requests: GitHub's API 12 (under 30); Redivis's API, two `--tables` runs of one table.

## 3851, the daily run's week (6 to 13 November)

- **GitHub's runs since 6 November:**
  - **daily prices:** 17 runs; 15 succeeded, 1 failed (43276079255, the counterparties coverage stop chain 215 fixed) and 1 was cancelled (43309130077, chain 218's duplicate dispatch);
  - **latest prices:** 725 runs, none failed;
  - **hourly network:** 195 runs, none failed;
  - **energy roundup** and **weekly vacuum:** 2 each, both succeeded;
  - **chain watch:** 725 runs, one failed (42672364199, 9 November).
- **`erw_health`, 4,903 rows in seven days.** Each failed step was opened. All but one are faults chains 212 to 218 fixed:
  - the two coverage stops (`datacenter_tracker_rollups`, `deal_counterparties`);
  - NYISO's late stamps (`nyiso` failed four times on 12 November);
  - test 402's rule;
  - the guard's refusals while main was red (tests 1139, 502 and 183, the health summary's and the vacuum's commits, 7 to 11 November);
  - the board put back (7 and 12 November);
  - `dm_test_replication` (fixed by chain 215);
  - `dm_commit`'s rebase stop (chain 216's fix).
  - Not this repository's code: `portwatch` (the IMF's source 13 days old, 7 November) and `frb_treasury`'s empty answers (passed on retry). The Roundup's `api_cost_ledger` draft refused to shrink by 3 rows (8 November); the upload refuses by design and the next run took it.
- **The one not fixed: the daily run's `package tests`** (12 November 23:40): `test_cite_names_the_iso_the_table_and_the_commit[datacenter_tracker_rollups] - KeyError: 'datacenter'`.
  - The test maps each table's name prefix to its publisher by hand. A table whose prefix is not in the map stops it with a KeyError. On this machine that is 227 tables, `utility_large_load_tariffs` among them.
  - **Fixed** (`package/tests/test_erw.py`): a publisher the map does not name, or names in other words than the table's source row, is read from the table's own source rows in `sources.csv`, the way the citation draws it.
  - Run here over every series table: 424 pass. The 14 that fail are tables on this machine's disk that coverage does not list (a KeyError at the coverage lookup, before the publisher); the runner holds none of them.
  - **Not done instead:** a "Derived from:" line in the rollups' header. It would mark the table derived, but its input `datacenter_projects` is public and it is internal, so `apply_derived` would stop the daily run at coverage.
- **The data machine's own run** of 12 November: every step ok or skipped by its schedule (`runs/data_machine_status.txt`). `dm_carb_lcfs` is skipped because CARB's newest week is 59 days old at the source.
- **The health summary's "Stale on main" line:** read with the run of 13 November (carried).

## 3852, the findings

- **The landing requests:** neither file has changed since 7 November (`landing_request_portable.md` rows 1 to 16, `landing_request_oldlaptop.md` rows 1 to 8), and chains 212 and 215 found every row landed. Nothing to land.
- **The drafts:** `check.py` 185 of 185 (session 3844), `check_cards.py` 185 of 185 cards hold, `check_do.py` 185 of 185 do-files hold. The count by family is unchanged: generation_pipeline 35, prices 33, queues_deals_datacenters 27, oil_products_world 18, tariffs_policy 12, demand 12, gas 11, cross_family 8, coal_uranium_metals 8, other_us 7, markets_operations 7, emissions_climate 7.
- **The Ask weekly run:** not before 19 November. Nothing approved.

## 3853, the drafts and the records

- **`utility_large_load_tariffs` on the warehouse's own draft:** 95 rows, Redivis count 95, and `erw_headers` 2,788 lines (8 for the table). Nothing released.
- **The Stanford draft refused it:** "the ERW verdict of utility_large_load_tariffs is unsettled (docs/licenses.md, Every table), not public". The upload refuses such a table by design; it is a ruling, below.
- **The records:** `redivis_uploads.csv` patched onto the branch from the main checkout, which was put back. `build_tables.py --check`, the tests of sessions 1001, 1008 and 1009 and `build_llms.py` ran with this chain's coverage row at the gate.

## Decisions made without you

- **The cite test reads the registry, not a longer map:** each table the ERW adds would need another entry by hand, and the daily run's package tests failed on the first table without one.
- **The rollups table stays "derived: no",** because its license and its input's differ; that difference is yours to rule on with the datacenter tracker's license, not the test's.

## For Samuel's ruling

- **`utility_large_load_tariffs`' ERW verdict** ("not settled (needs written permission by default)" in `docs/licenses.md`): the rows are filed tariffs, public regulatory records, each read from a commission's copy (the NY schedules from the DPS's own system). Default: unsettled, not on the Stanford draft.
- **`datacenter_tracker_rollups` internal beside a public `datacenter_projects`:** one of the two licenses is not the intended one. Default: as they stand.
