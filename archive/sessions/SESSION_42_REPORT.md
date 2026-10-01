# Session 42 report: stopped at Part 0, the gate is not open

Energy Research Warehouse (ERW), session 42, 2026-09-30 from 19:31 to about 19:35 UTC. **Wall time about 4 minutes.**

**API spend: USD 0.00, confirmed.** No model call.

- **No pull:** the approved EIA-930 interchange pull (Part A) was not made.
- **Nothing else built,** and no Supabase change.
- **Nothing to merge:** the daily job had not landed on origin (`git fetch` at 19:31 UTC showed nothing new).

## Part 0: the gate

**Daily-prices run 12** (workflow_dispatch, commit 9fb7d93, created 2026-09-30 18:52:43 UTC), read through the GitHub API at 19:31 UTC:

| Step | State |
|---|---|
| 1 to 5 (set up, secrets, checkout, Python, install) | completed, success |
| 6 Merge tests | completed, **success** (18:53:53 to 18:53:58), the step session 41 fixed |
| 7 Pull, validate, rebuild coverage | **in progress** since 18:53:58 (about 37 minutes), no conclusion |
| 8 to 12 | pending |

**The run is still running, so the gate is not open.** As the prompt directs, nothing was pulled and the session stops here. For scale, the last run to complete this step, run 9 on 2026-09-29, spent 53 minutes in it before failing at coverage.

## Not done (waiting for the gate)

- Part A, the interchange connector and pull.
- Part B, the network tables, snapshot and `/network`.
- Part C, verify and ship.

`SESSION_42_PROMPT.md` stays at the repository root, unchanged, for the rerun.

## Open question

1. **Rerun Session 42 once run 12 completes?** If step 7 fails, its failure issue will name the cause, and a fix comes before the interchange pull.

---

## The rerun, 2026-10-01 (session 49 Part A): EIA-930 interchange and the 3D grid network

Energy Research Warehouse (ERW). Session 42's plan was carried out as **Part A of session 49**, run 2026-10-01 from about 03:30 to 03:57 UTC (the connector and network commit, 6dd3dae), with the verification and uploads later in the same session. Work was interleaved with session 49's other parts, so the wall time is about 45 minutes all told.

**API spend: USD 0.00, confirmed.** No model call; the chat spec was regenerated with `ask.py --export-spec`, which makes no API call. No force push.

### Part 0: the gate

Session 49's instruction: "The gate is open; no routing." Daily run 14 had passed (2026-10-01 00:20 UTC, session 48), so the approved pull ran.

### Part A: interchange

#### A1. The connector and the table

- **Connector:** `warehouse/connectors/eia930_interchange.py`. It reads EIA API v2 `electricity/rto/interchange-data`, hourly, every pair EIA reports (no facet).
- **Field names were checked against the API first:**
  - The fields are `period`, `fromba`, `fromba-name`, `toba`, `toba-name`, `value` and `value-units`.
  - The route has no `respondent` column. The shared pager (`fetch_route`) sorts by respondent and got HTTP 400 ("Invalid sort respondent"), so the connector has its own pager, sorted by period, fromba and toba.
- **The table:** `eia930_all_interchange` (source tier, public).
  - One entity per reporting BA and neighbor, `eia930:<FROM>-<TO>`.
  - `ba` is the reporter, lowercase; `x_to_ba` is the neighbor.
  - Variable `interchange_mw`.
  - `ts_utc` is the hour's start, since EIA's period is the hour's end.
- **Raw pages:** saved under `warehouse/raw/eia930_interchange/<run>/`.
- **Day checkpoints:** saved to make the pull resumable. The last 4 days are never checkpointed, since EIA revises them.
- **Completeness per pair and UTC day:** a pair-day missing any hour is not written. One `run_status` row counts the incomplete pair-days and names the first 20.

#### Rows against the ceiling

| | Rows |
|---|---|
| Ceiling | 150,000 |
| The approved window, the last 30 days (counted with a zero-length request before pulling) | 236,808, over the ceiling: not pulled |
| Pulled: the latest 18 complete UTC days, 2026-09-13 to 2026-09-30 (the API's count) | 131,008 |
| Written | 127,560 |
| Incomplete pair-days, not written | 465 |

- **Directed pairs:** 341. Data runs through 2026-09-28 at the time of the pull.
- **Decision (recorded in the method page):** the window was cut from 30 to 18 days to stay under the ceiling. 18 days was the most whole days the count allowed.

#### EIA's sign convention, checked against the data

- **Method:** for each of the seven ISO BAs, its interchange summed over neighbors, compared hour by hour (360 hours) with its net generation minus its demand.
- **Positive means exports from the reporting BA.**

| BA | Mean of \|interchange - (net gen - demand)\|, MW | With the opposite sign, MW |
|---|---|---|
| ERCO | 1.6 | 511.9 |
| NYIS | 0.4 | 5,201.7 |
| ISNE | 0.7 | 1,569.4 |
| CISO | 3,199.1 | 14,419.1 |
| MISO | 1,397.9 | 4,611.0 |
| PJM | 2,042.1 | 6,098.4 |
| SWPP | 978.1 | 2,626.8 |

The opposite sign is far worse everywhere. The table is in `docs/methods/grid_network.md`.

#### A2. The daily run

- `warehouse/run_daily.sh` runs the connector after `carbon_intensity` with the same `--days` as the other EIA-930 steps (3 days, merged into the history), then rebuilds the network.
- `warehouse/redivis/config.yaml` restores `eia930_all_interchange` before each run, so the history survives.
- The workflow commits `site/data/grid_network.json`.

### Part B: the network

#### B1. The derived tables (`warehouse/derived/grid_network.py`)

- **`grid_network_nodes`:**
  - 69 BAs, 83 rows.
  - Each carries `x_name` (EIA's name) and `x_iso`.
  - Demand and carbon intensity are held for the seven ISO BAs only (CISO, ERCO, ISNE, MISO, NYIS, PJM, SWPP). The other BAs' demand is not pulled.
  - Each node has an interchange volume over the 168 hours.
  - EIA's regions and country totals are not nodes, since they would double-count: CAL, CAR, CENT, FLA, MIDA, MIDW, NE, NY, NW, SE, SW, TEN, TEX, US48, CAN, MEX.
- **`grid_network_links`:** 156 pairs, 168 hours (2026-09-22 to 2026-09-29), 26,160 pair-hours, variable `flow_mw`.
- **The pair rule:**
  - Each pair is counted once: its flow is read from the BA whose code sorts first, as that BA reported it (positive means that BA exported).
  - In an hour that BA did not report, the flow comes from the other BA's report with the sign flipped.
  - `tests/test_session49.py` checks a sample of 300 link-hours against the source table under this rule.

#### B2. The snapshot

- **The file:** `site/data/grid_network.json` (about 179 KB) holds the nodes, their fixed positions and 168 hourly flows per pair. The page reads only this file.
- **Supabase: nothing loaded.** The nodes table could have gone into Supabase under session 42's 345 MB rule. Session 49's rule is 395 MB, and the live set stood at 393.5 MB after Part C's event table, with room needed for the cost-of-power rebuild. So the nodes stay in the JSON only.
  - Supabase before and after Part A: 382.1 MB, unchanged by this part.
- **Node figures from the live set:** they are read from Supabase (`--nodes-from-supabase`), so the page agrees with what check-values reads. EIA revises recent hours, and the first local build showed older values.

#### B3. Positions

- **Layout:** a 3D Fruchterman-Reingold layout, 600 steps, seed 42, links weighted by the square root of their mean flow.
- **Fixed:** computed once per build and stored as x, y, z per node. The page never re-settles it (`fx`, `fy`, `fz` fixed, `cooldownTicks(0)`).

#### B4. The page `/network`

- **Navigation:** first under Grid. Each `/grid/<iso>` page links to it.
- **The graph:**
  - Built with 3d-force-graph (`site/package.json` ^1.80.1), loaded only in the browser.
  - Drag to rotate, scroll to zoom. It turns slowly until touched.
  - Sphere size: demand for the seven ISO BAs, interchange volume for the others (the legend says so).
  - Color: carbon intensity, green (#175E54) to cardinal (#8C1515); grey where not held.
  - Link width follows MW. Particles run in the direction of flow, at a speed scaled to MW.
- **Time:** a slider over the 168 hours with play and pause, the hour shown in UTC and Eastern.
- **The node card:** name, demand and intensity (each with a check key), the top three flows that hour, and the grid page for the seven ISOs.
- **Explainer:** quotes EIA's Today in Energy (id=27152, read and verified) on the three interconnections and ERCOT being its own BA, interconnection and RTO.
- **Without WebGL:** a fallback message points to the grid pages.

**Gaps:**
- the demand of the 62 BAs outside the seven ISOs is not held;
- interchange before 2026-09-13 is not held;
- EIA-930 reports BA-to-BA totals, not flows by line.

### Part C: verify and ship

| Check | Result |
|---|---|
| Validator | PASS for `eia930_all_interchange`, `grid_network_nodes` and `grid_network_links` |
| Coverage | rules in `SECTOR_RULES` and `iso_of`; rebuilt |
| Archive | 127,560 + 83 + 26,160 rows (run 20261001T042639Z-local) |
| Redivis | uploaded to the public draft with `upload.py --tables`: 127,560, 83 and 26,160 rows, `count(*)` equal; nothing released |
| llms.txt and the chat catalogue | an Interchange section and routing row; `warehouse/chat/tools.py` and `site/lib/chat/tools.ts` list `eia930_all_interchange` among the BA tables; `spec.json` regenerated without an API call |
| check-routes | covers `/network` |
| check-values | covers the node card defaults: `/network` in its page list, demand and intensity keys |
| Local build | check-values 2,431 of 2,431 values, every page; check-routes passes `/network` |
| Tests | `tests/test_session49.py`: the snapshot against the rules, the pair rule against the table, the layout seed, the ceiling |
| Deploy and live check | with session 49's push; results in `SESSION_49_REPORT.md` |

### Open questions

1. **A longer window.** The 30-day window needs about 237,000 rows, so a 150,000 ceiling allows 18 days. Raise the ceiling, or keep the 18 days and let the daily merge grow the history?
2. **Demand for the other 62 BAs** would let every sphere be sized by demand: one more EIA-930 route, about 1,500 rows a day.
3. **The nodes table in Supabase:** not loaded, since the live set is near its 395 MB line. It is small (83 rows) if a page ever needs it live.
