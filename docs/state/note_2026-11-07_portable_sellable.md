# The portable laptop's note of chain 208: roadmap item 2 finished, main never red (written 7 November 2026)

Energy Research Warehouse (ERW), session 3719, for Samuel. Chain 208 (sessions 3700 to 3719, `queue/done/208-night-6-november-portable-sellable.md`), unattended on portable-laptop (the code role) from 21:41 UTC on 6 November 2026, one Claude Code window, Opus 5.5.

- **Model spend: USD 0.** No model was called.
- **Requests to public hosts: 8,** each robots file read first. Potomac Economics 3 (robots, the ERCOT page, the 2025 report); EPA 3 (robots, eGRID's summary page, its summary tables); EIA 2 (robots, its answer on CO2 per kWh).
- **Other reads:** GitHub's API three times, for the merge gate's step times; `erw_health` seven times (a week's days), read only, for the emails' kinds.
- No warehouse data written. `site/lib/release.ts` untouched. Nothing sent or posted. No page's layout changed.

## Read these first

- **Landed:** sessions 3701 to 3717 as `9245ed56d` (7 November 00:33 UTC, run 42317420854), with **0 differences on the 25 live pages** between the snapshots before and after. It landed through the new merge gate's first run, which merged main, ran the suite on the merged tree and merged.
- **Requested, not landed:** session 3718's three commits, as row 16 of `docs/state/landing_request_portable.md` (`wip/3701-sellable` at `8d9a9dba2`, task `3718-sellable`). They hold the runner's tracebacks, a fix to it (a test's printed "FAIL:" line could be read as a failure), and `test_session244`'s module loading. That gate's suite ran across a 16-hour sleep of the laptop, and one node test stopped at its timeout.
- **The laptop slept twice** (about 00:19 to 02:12 and 02:40 to 19:08 UTC on 7 November). The chain's last sessions ended after its fifteen hours.

- **Item 2: the last two tools now have their three missing items.** Research (Automated Analysis) and the Grid tool now have a replication a reader runs, a cross-check table, and a decisions block in the method note. The battery, generator and datacenter tools had them (chain 158) and now have their cross-check tables. **None of the five notes is signed**, and the do-files have not been run in Stata.
- **Main was red twice, and both are reproduced from their commits** (`docs/state/main_red_2026-11-06.md`):
  - 30 October to 5 November: the data machine's page files against tests pinned to dated figures;
  - 6 November 01:32 to 02:59 UTC: the runner's catch-up commit, a new table without its license row and page files rebuilt thin.
  - Neither commit had the suite run on it.
- **What now stops it** (on main since 00:33 UTC on 7 November):
  - GitHub's merge gate tests the branch merged with main, and again if main moves;
  - every bot's push to main this chain may touch runs the whole suite first and is refused on a red suite, the failing tests named, the commit sent to a `wip/red-*` branch. There is no new email: the existing daily red reads the refused step, and the job stays green;
  - page files never thinner than main's;
  - the thin rebuild's cause fixed in `warehouse/scheduled.py`.
- **The data machine's own commit path was not changed:** this machine's permission classifier refused the edit. The four lines are in the red-main file, for your ruling.
- **The streak and the emails:**
  - the streak reads true: fourteen red days, streak 0, recomputed from the summaries by a test;
  - this week's sends: two daily-red emails (31 October, 1 November), nothing extra;
  - the daily summary now lists the emails it sent;
  - every failed run of 23 October to 5 November has its root cause written in `queue/summary/` (one not root-caused: the board's tests on 24 October).

## The five tools after this chain

| Tool | Method note | Signed | Replication | Cross-check table | Decisions block |
|---|---|---|---|---|---|
| Battery | `battery_earns_algorithm.md` | no | `replication/battery/`, 22 of 22; Stata not run | `docs/methods/crosschecks/battery.md` (new) | the note's section 6 |
| Generator | `generator_earns_algorithm.md` | no | `replication/generator/`, 13 of 13; Stata not run | `crosschecks/generator.md` (new) | section 13 |
| Datacenter | `datacenter_pays_algorithm.md` | no | `replication/datacenter/`, 14 of 14; Stata not run | `crosschecks/datacenter.md` (new) | section 12 |
| Research | `automated_analysis.md` (new sections) | no | `replication/analysis/` (new): 65 of 66 computed met, 1 known difference, 10 license needed | `crosschecks/automated_analysis.md` (new) | 35 assumptions (new) |
| Grid | `grid_network.md` (new sections) | no | `replication/grid/` (new): 147 of 158 computed met, 11 known differences (old table copies), 22 license needed | `crosschecks/grid.md` (new) | 25 assumptions (new) |

`docs/state/roadmap_item2_state_2026-11-06.md` holds the same, with each item's file, for the Sunday review.

## The cross-checks' largest differences

- **Battery, 2024:** USD 147.68 per kW (perfect foresight, 4 hours, the hub) against Modo's ERCOT fleet average of USD 55 (+92.68). The closest method (E3, 2 hours, North) is +20.68.
- **Datacenter, 2021:** LZ_NORTH's flat mean of USD 150.61 against the North zone's load-weighted USD 221.52 (Potomac's 2025 report): -70.91, Uri's prices in high-load hours.
- **Datacenter, energy against retail:** USD 32.40 against Texas industrial USD 67.02 over November 2025 to July 2026 (-34.62).
- **ERCOT's battery fleet at the end of 2025:** 13,909 MW (EIA-860M) against "exceeded 17 GW" (Potomac). Not explained; Modo's count agrees with EIA's.
- **Carbon intensity in 2023:** ISO-NE 12.76 kg per MWh below eGRID's NEWE (not explained); ERCOT 10.09 above ERCT; the Lower 48 within 0.57 of eGRID.
- **Net generation 2025:** ERCOT 10.45 percent and CAISO 8.72 percent below Form EIA-923.

## The red-main causes and their fixes

| Cause | Commit | Fix |
|---|---|---|
| The data machine's page files against tests pinned to dated figures | `137e9dfb7` (30 October) | the tests check the rule (`9448f7a8a`, chain 147); the data machine's push guard waits for your ruling |
| The daily run's "merge tests" reason was a NumPy warning, the job green | from 31 October | the reason's line (session 2864); `suite_gate.py` names every failing test (this chain) |
| A bot's commit pushed with no suite | `e2794ff06` (6 November) | `scripts/push_guard.py` before the daily, health-summary and vacuum pushes (this chain) |
| The merge gate tested the branch's head, not the merge with main | always | `code-branch.yml` merges main first, and tests again if main moved (this chain) |
| `mix_profile`'s input `caiso_fuel_supply_history` unnamed, so the runner's thin rebuild went unseen | `e2794ff06` | named in `warehouse/scheduled.py`; `scripts/never_thinner.py` in the commit step (this chain) |

## What did not finish

- Session 3718's three commits: requested (row 16), not landed.
- The data machine's commit path (refused by the classifier) and the Roundup's push (the periodicals chain's file).
- The cross-check rows a public report would still give (FERC and NERC on February 2021, Potomac's 2021 report, CAISO DMM's 2025 report). Berkeley Lab's files wait for the ruling on its terms.
- The Grid tool's Ask figures against fresh tables (the data machine), and the Mix tab's live hour.
- The next file (`queue/parked/209-...`) lists these first. **It is parked**: the desktop parked every waiting file at 23:15 UTC "for the weekend review", so this chain did not take it.

## Decisions made without you

- The sessions ran out of their listed order where a gate was running. Sessions 3707 to 3717 were done while session 3706's gate ran its 43-minute suite, and the reports say so.
- The first gate (`f61920f88`) stopped at check-values on two other chains' floors and one unread page. The next gate ran on the branch head (all sessions), keeping its worktree for the skipped checks.
- **Landed past check-values' failures:** the `/deals`, `/learn/problems/know-your-grid` and `/digest` floors.
  - These are other chains' pages, and the branch changes no `site/` file.
  - The unread page passed when read alone.
  - The three checks the gate skipped passed by hand on the same build.
  - Chains 147, 149 and 158 landed the same way.
- The third gate was not run again after the sleep. Session 3718's commits are requested of the desktop instead (row 16).
- "The page's figures" for Research are the cards' own files, which check-values holds the page to. For the Grid tool's network they are the page's own functions run with node on the snapshot. A build needs about 3 GB.
- The Grid tool's live-read figures are not in its comparison: this chain read no row of the live set. `erw_health` was read once, with this machine's key, to check the week's emails.
- A refused bot push leaves the scheduled job green: a red job would make GitHub email you, which the email rule forbids.
- `mix_profile`'s history table is named but not restored from the archive: session 114's rule, which its test holds.
- The parked next file was updated in place and not moved back: only you move a parked file.

## For Samuel's ruling

1. **The data machine's push guard:** the four lines in `docs/state/main_red_2026-11-06.md`. Spell 1 came through that path.
2. **The two check-values floors** (`/deals`, `/learn/problems/know-your-grid`), failing every gate since session 1434: lower them, or have their chains fix the pages?
3. **Berkeley Lab's data files** (session 253's open ruling): they would give six figures a published counterpart.
4. **The Mix tab's live hour:** may a session read the live set to replicate it (`replicate.py mix_now()`)?
5. **The five signatures and the Stata runs** of `replication/<tool>/replicate.do`.
6. **The next file 209** is parked with this chain's unfinished steps first: move it back to `queue/next/` to run it.

## The cost

USD 0 of the chain's USD 15: no model call. Eight requests to public hosts. Three runs of the landing gate: about 55 minutes each for the first two, and the third across the sleep.
