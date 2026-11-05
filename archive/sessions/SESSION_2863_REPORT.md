# Session 2863 report: the daily run's merge tests

5 November 2026, 20:47 to @@END@@ UTC, on lab-desktop (the data machine), chain 147, unattended. Model spend USD 0. Pulls: GitHub's API 9 requests (runs, jobs, two job logs, the deployment status); www.ercot.com 2 requests by `iso_prices.py ercot` (both failed at name resolution; see below).

## Read these first

- **The run did not fail at a dependency.** "Merge tests" failed on tests that held page files to dated figures or fixed counts. The data machine writes those files again every day, and its own run tests only some of them. Two groups:
  - From 31 October (run 41208065020): `test_session701`, `test_session709`, `test_session720`. The All grids tab's node figures need `node_basis_daily` to hold 90 percent of the days in the hub's twelve months. The hub's twelve became November 2025 to October 2026. The table's day-ahead days stop at 20 October: ERCOT's 31-day DAM list was last saved on 19 October, and Aug and Sep hold 20 and 11 days. So the nodes held 323 of 365 days (88.5 percent) and none was drawn. Test 709 then crashed on the first drawn node, and the siting cards no longer matched the tab.
  - From 2 November, also: `test_session422` (the datacenter mirror printed 34.07 against the pack's 33.73 once the twelve months rolled), `test_session190_replication` (HB_NORTH held 671 of October's 744 real-time hours because the runner stopped on 30 October, so the page drew no hub figure), and `test_session144_page` (CAISO's October held 27 of 31 days; the test wanted exactly 149 months and nothing missing).
- **The NumPy warning is not the fault.** It is the last line of the output, which `health.py` recorded as the reason. Session 2864 fixes that.
- **Reproduced here:** the same 5 failures and 2 errors in a clean detached worktree of origin/main with no keys (`runs/s2863/local_six.out`).
- **The fix, `wip/2863-daily-run`** (`4601b60f`, merged with main as `d288264b`):
  - `test_session422`: each mirror runs on its CSV as of the packs' build (the months to September 2026, `in_last_twelve` set on October 2025 to September 2026). All nine quoted figures come out exactly: 81.40, 475,477, 2.63, 59.85, 23.27, 0.67, 33.73, 37.88, 0.0684.
  - `test_session144_page`: every CAISO month from May 2014 to the newest share must have one. Only the month after the newest may lack one. A hole inside the span still fails.
  - `test_session190_replication`: the mirror and the page must agree on the hub. With twelve whole months the figure is compared. Without them, the mirror must count fewer than twelve.
  - `test_session701`: the nodes drawn are exactly the ones the 90 percent rule allows, counted from `nodes.json`.
  - `test_session709`: with no node drawn, every row says why. The sorts put nodes with no figure last.
  - `site/scripts/siting-card.mjs` was run again: the two cards now carry the tab's current figures.
  - `daily-prices.yml`: a `days` input, default 3. A manual run can pull the missed week while ERCOT's real-time list still holds it (seven days).
  - `tests/test_session2863.py` (4 tests). It also checks that no repaired test gained a skip or an expected failure.
- **Suite in the clean worktree, pass 1:** 7,322 tests in two halves.
  - Half 0: 441 modules, 3,737 tests, 0 failed.
  - Half 1: 440 modules, 3,585 tests, 2 failed. One was my own new test's skip count, fixed and passing. The other was `test_session705`: it fails from an `erw-NNN` worktree and passes in the main checkout (OK here); this is memory's known artifact, not this change.
- **Landing:** @@LANDING@@

## What it found

- **Run state on GitHub:** every daily run since 31 October shows "success" with the later steps skipped. The job stays green because `health.py run` records the failure and passes `status` to the next steps' `if:`. That is why the breakage was invisible on GitHub.
- **No local ERCOT hub fill:** `iso_prices.py ercot --days 9` asks `www.ercot.com/misapp/...`, a path ERCOT's robots file disallows (docs/licenses.md row 170, session 2002). Its two requests failed at name resolution and nothing was written. `consolidate.py check` shows both hub families unchanged. This chain's rules keep robots, so I made no second try. The runner's own run, with `days=7`, refills the hubs.
- **The node figures need ERCOT's DAM list.** `ercot_rt_spp.py --pull-dam` also uses `/misapp`. The data machine's daily run already asks `/misapp` every day for the real-time list (`dm_ercot_node_prices`). This is for Samuel's ruling below.
- **Already held, relevant to 148:** `ercot_node_wires_utilities`, `ercot_node_places` (county and zone of 569 nodes) and `ercot_node_transmission` (TPIT by county) are on this machine. `nodes.json` already carries county, zone and TPIT projects. 148's sessions 2889 to 2891 must read these first.

## Decisions made without you

- **Tests that compared a page file with a dated figure or a fixed count now check the rule the figure follows.** No assertion was dropped: each check now holds in both states of the data. The packs' figures are still tested exactly, on the data of their build.
- **No `/misapp` request,** neither for the hub fill nor for the DAM list, under this chain's robots rule.
- **A `days` input on the workflow** rather than a one-off run of the connectors here.

## For Samuel's ruling

- **ERCOT's DAM Settlement Point Prices list (NP4-190-CD)** is reached only at `/misapp`, which ERCOT's robots file disallows. Without it, no ERCOT node has a twelve-month figure on the All grids tab until a ruling. The options are a daily `--pull-dam` on the data machine (it already asks `/misapp` daily for real time) or ERCOT's public API with a key.
- **The data machine's daily run asks robots-disallowed ERCOT paths every day** (`dm_ercot_node_prices`, `ercot_rt_spp.py`), and so does the runner (`iso_prices.py ercot`, through gridstatus). Both have been known since session 2002. They are left as they are.

## Files

- On `wip/2863-daily-run`: `tests/test_session144_page.py`, `test_session190_replication.py`, `test_session422.py`, `test_session701.py`, `test_session709.py`, `tests/test_session2863.py` (new), `.github/workflows/daily-prices.yml`, `site/data/findings/siting_{gigawatt,flexible,battery_swing}.json`, `site/public/findings/siting_{gigawatt,flexible}.csv`.
- On the data machine only: `runs/s2863/` (the two runs' job lists and logs, the local reproduction, the suite halves, the hub fill's log), `runs/c147/gh.py`, `ghlog.py`, `suite_half.py`.
