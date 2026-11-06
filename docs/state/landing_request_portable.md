# Landing requests: the personal laptop (chain 156, the deal tracker and the datacenter tracker)

Energy Research Warehouse (ERW). Written by chain 156 (`queue/done/156-night-6-november-portable-deals-datacenters.md`), session 2248, on 6 November 2026. The gate of row 1 was stopped by Claude Code for low memory on this machine and is not started again here unasked. The desktop's landing service lands each row through `scripts/land_check.py` with the task and port given, runs the commands it prints each on its own (the snapshot before, the push to `task/`, the snapshot after, the comparison), never between 14:00 and 16:15 UTC, and marks the row landed with the commit.

| # | Branch | Head | Task | Port | Requested (UTC) | Tests on this machine | State |
|---:|---|---|---|---:|---|---|---|
| 1 | `wip/2252-deals` | `9a5d15d11` | `2230-2252-deals` | 3230 | 2026-11-06 | the chain's tests and the older tests they touch: 173 passed, 6 skipped, on `a1ff82330`; the whole suite passed on `wip/2241-deals` (7,884 tests), not run whole on the head | waiting |
| 2 | `wip/3059-policy` | `44bf41ab0` | `3054-3059-policy` | 3260 | 2026-11-06 | the 221 test files that touch policy, dashes, the method notes, coverage or the daily run: 3,167 passed, 131 skipped, 0 failed, on the head's tree; Node `test-policy-reads.mjs` 25 of 25, `test-policy-week.mjs` 90 of 90; the whole suite not run (stopped at 7% under the chain's 20-minute rule); not built (this window never builds) | waiting, or landed with row 3, which holds it |
| 3 | `wip/3063-policy` | `4f8fef90d` | `3054-3063-policy` | 3260 | 2026-11-06 | the 223 test files that touch policy, dashes, the method notes, coverage or the daily run: 3,174 passed, 131 skipped, 0 failed, on the head's tree; Node `test-policy-monitor.mjs` 52 of 52, `test-policy-reads.mjs` 25 of 25, `test-policy-week.mjs` 90 of 90; `scripts/check_policy.py` 287 of 287 ok; the whole suite not run; not built, not type-checked (no `node_modules` on this machine) | waiting (holds row 2) |

## Row 1: what it holds

Sessions 2230 to 2252, stacked: `wip/2230-deals` to `wip/2251-deals` are ancestors of `wip/2252-deals`. Reports: `archive/sessions/SESSION_2230_DEALS_REPORT.md` to `SESSION_2252_DEALS_REPORT.md`.

- **The audit** `docs/reviews/deals-audit-2026-11-06.md` (106 deals and 60 facilities read, the fault classes, the second read's counts before and after, every row's state) and its folder.
- **The deal extraction**: `warehouse/deals/fields.py` (kind, stage, grid, USD, price, AI basis, flags, status history), `dedupe.py` (one record a deal), `counterparties.py` with `aliases.yaml` (the table `deal_counterparties`), `crosscheck.py`, `calls.py`, the prompt and schema in `extract.py`; the fixtures in `warehouse/deals/eval/` and `tests/fixtures/deals/`; `scripts/deals_backfill.py` (`--dry-run` only on this machine).
- **The datacenter extraction**: `warehouse/datacenters/facility_fields.py` (MW basis, power kind, grid, utility), `extract.py`; `warehouse/derived/datacenter_tracker_rollups.py` (a new series table), `datacenter_facilities.py` (grid and the new fields).
- **The daily run**: `warehouse/run_daily.sh` gains `deal_counterparties` and `datacenter_tracker_rollups`. The new columns of `energy_deals`, `datacenter_projects` and `datacenter_facilities` are written by the first daily run after the landing; the old rows are upgraded in place (`upgrade_file`).
- **The pages** (all `review`; `site/lib/release.ts` not changed): `/deals` (the table with filters and downloads, comparables, the AI-power view, the charts), `/datacenters` (the rollups, the facilities against each grid, the timeline, the charts); `site/lib/dealsview.ts`, `deals2.ts`, `dealsai.ts`, `dcrollups.ts`; `site/components/Num.tsx` holds `dcchart|`, `dcgrid|`, `dctime|` by `datacenter_facilities`.
- **The tracers**: `scripts/check_deals.py` (71 of 71) and `scripts/check_datacenters.py` (28 of 28); `site/scripts/check-values.mjs` gains their key families.
- **The method notes**: `docs/methods/energy_deals.md` and `datacenter_facilities.md` (v2 sections), `datacenter_projects.md`, and two new notes, `deal_counterparties.md` and `datacenter_tracker_rollups.md`.
- **Tests**: `tests/test_session2232_deals.py` to `test_session2252_deals.py`; older tests edited: 103, 114, 149 (checks), 166 (the builder reads a member's field with `.get`), 215 (the three prefixes), 282, 301, 531.

## Known on this machine

- **The gate's tries on 6 November**: on `wip/2241-deals`, the suite passed and `check_values` failed once on `/roundup` "fetch failed" (old laptop's chain 154's page; read as a one-off); on `wip/2252-deals`, the probe closed it once and main moved twice before Claude Code stopped it.
- **`/deals` is a held floor page** (`HELD_FLOOR_PAGES`): its figures read "license needed", as on main.
- **Not built at the head**: the site was last built by the gate on `wip/2241-deals` (the deals pages, sessions 2238 to 2241: the build passed); **the datacenter pages of sessions 2243 to 2246 have not been built anywhere**, for memory. `npx tsc --noEmit` in `site/` on the head (session 2252) leaves only the 15 errors of a build's generated files, as on main. The gate's build is the first.
- **After the landing, for the data machine**: the license rows of `deal_counterparties` and `datacenter_tracker_rollups` at their first build (held as their parents are, this chain assumes: `license_status.csv` and test 207's count), and the backfill only after the owner approves it (`docs/state/note_2026-11-07_portable.md`).

## Row 2: what it holds (chain 166, the personal laptop's second window: the policy monitor)

Written by session 3059 of `queue/done/166-night-6-november-portable-window2-policy-monitor.md` (its sessions 2260 to 2271 run as 3054 to 3065: every number to 3053 was taken). Sessions 3054 to 3059, stacked: `wip/3054-policy` to `wip/3058-policy` are ancestors of `wip/3059-policy`, which has `origin/main` merged (cda8db883). Reports: `archive/sessions/SESSION_3054_REPORT.md` to `SESSION_3059_REPORT.md`. This window never builds the site and never lands: the desktop lands it through `scripts/land_check.py --ref wip/3059-policy --task 3054-3059-policy --port 3260`.

- **The audit** `docs/reviews/policy-audit-2026-11-06.md` (80 actions read against their documents, ten fault classes, each row's state) with `policy-audit-2026-11-06-sample.csv`.
- **The fields** `warehouse/policy/fields.py` (body, instrument, action_status, dates with evidence, next step, figure with unit and evidence, docket ids; written rules, no model), wired into `warehouse/connectors/policy_sources.py` as new columns beside the old (no column the Digest or the page reads changes); the listing asks the Register for `effective_on` and `comments_close_on`; `widen_held` widens any earlier shape. **After the landing, for the data machine:** the next run of `policy_sources.py` on the desktop (its store `warehouse/raw/policy_sources/fr_text/` holds the printed texts) derives the fields of every Register row from its text; on the runner a row read before keeps them empty until then. No new request to the Register is made for rows already read.
- **The records** `warehouse/policy/records.py` (one record a proceeding, every source, a status history); not a warehouse table and not a daily step (the owner's ruling is asked).
- **The impact read** `warehouse/policy/impact.py` (the model's clause, kept only when its words stand in the text; the table it bears on by written rules) and its 60 reads, `docs/reviews/policy-impact-2026-11-06.csv` (USD 0.45, session 3058's ledger rows). Not a daily step.
- **The scorer** `warehouse/policy/score.py`: one sentence added to the policy note on the sector; it applies to actions scored after the landing.
- **Tests**: `tests/test_policy_fields.py`, `test_policy_records.py`, `test_policy_impact.py` and `tests/fixtures/policy/`. Method note: `docs/methods/policy_monitor.md` sections 14 and 15.
- **No page changes in this row**: `/policy` is as on main. The monitor view (`/policy?view=monitor`) is the next row's.

## Row 3: what it adds to row 2 (chain 166, sessions 3060 to 3063)

`wip/3063-policy` holds row 2 (`wip/3059-policy` is its ancestor) and `origin/main` merged (49bf6a05c). Land it with `scripts/land_check.py --ref wip/3063-policy --task 3054-3063-policy --port 3260`; row 2 is then landed too. Reports: `archive/sessions/SESSION_3060_REPORT.md` to `SESSION_3063_REPORT.md`.

- **The monitor view** `/policy?view=monitor` (a third view of `/policy`, in review with the page; `site/lib/release.ts` not changed): `site/app/policy/MonitorView.tsx`, `MonitorCalendar.tsx`, `MonitorCharts.tsx`, `site/lib/policymonitor.ts`; `site/lib/policyweek.ts`'s `VIEWS` gains `monitor`; `page.tsx` draws it from `site/data/policy/monitor.json` alone.
- **Its data file and daily step**: `warehouse/policy/monitor_site.py` writes `site/data/policy/monitor.json` (1.24 MB, 1,495 records on the archive's copy; committed); `warehouse/run_daily.sh` gains `soft_step policy_monitor_records` after `policy_monitor_site` (the workflow's commit step already adds `site/data/policy`). `warehouse/policy/impact_reads.csv` (session 3058's reads) is read by it.
- **The tracer**: `scripts/check_policy.py` with `site/scripts/policy-figures.mjs` (the keys `policycal|`, `policyfig|`, `policysum|`, shown as `data-check`, not `<Num check>`): **for the landing**, the gate's `check-values.mjs` does not know these families and need not; if it asks every `data-check` of a page to be a known family, add the three, traced by `check_policy.py`.
- **Older tests edited** for the third view: `tests/test_session157_page.py` (the views), `test_session332.py` (three views offer the downloads), `test_session241a.py` (`/policy` opens the wrapper four times; `MonitorView.tsx` among its files), `site/scripts/test-policy-week.mjs`.
- **The build is the gate's first**: `MonitorCharts.tsx` calls `components/svgchart.tsx`'s `CategoryChart` as its other callers do; nothing here was compiled. A type error there is this row's to fix, in the next chain (`queue/next/169-night-7-november-portable-window2-continued.md`).
