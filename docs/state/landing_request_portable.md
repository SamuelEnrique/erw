# Landing requests: the personal laptop (chain 156, the deal tracker and the datacenter tracker)

Energy Research Warehouse (ERW). Written by chain 156 (`queue/done/156-night-6-november-portable-deals-datacenters.md`), session 2248, on 6 November 2026. The gate of row 1 was stopped by Claude Code for low memory on this machine and is not started again here unasked. The desktop's landing service lands each row through `scripts/land_check.py` with the task and port given, runs the commands it prints each on its own (the snapshot before, the push to `task/`, the snapshot after, the comparison), never between 14:00 and 16:15 UTC, and marks the row landed with the commit.

| # | Branch | Head | Task | Port | Requested (UTC) | Tests on this machine | State |
|---:|---|---|---|---:|---|---|---|
| 1 | `wip/2252-deals` | `9a5d15d11` | `2230-2252-deals` | 3230 | 2026-11-06 | the chain's tests and the older tests they touch: 173 passed, 6 skipped, on `a1ff82330`; the whole suite passed on `wip/2241-deals` (7,884 tests), not run whole on the head | waiting |

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
