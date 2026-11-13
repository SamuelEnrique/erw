# Landing requests: the desktop's third window (chain 229, the licensing sweep)

Energy Research Warehouse (ERW). Written by chain 229 (`queue/done/229-day-13-november-desktop-window3-licenses.md`), session 4106, on 13 November 2026. This window never builds the site, never runs `scripts/land_check.py` and writes no warehouse data. The landing desk (window B) lands each row through `scripts/land_check.py` with the task and port given, runs the commands it prints each on its own (the snapshot before, the push to `task/`, the snapshot after, the comparison), never between 14:00 and 16:15 UTC, and marks the row landed with the commit.

| # | Branch | Head | Task | Port | Requested (UTC) | Tests on this machine | State |
|---:|---|---|---|---:|---|---|---|
| 1 | `wip/4100-licenses` | `c21ab94fa` (or its one later commit, this file's) | `4100-licenses` | 4100 | 2026-11-13 10:55 | on the head's tree with `origin/main` merged at 10:52: `licenses.py check`, `build_llms.py --check`, `build_tables.py --check`, `release_v1.py --check`, `check_spec.py` exit 0; tests 4101 (new), 205, 207, 275 and 378: 53 passed. Before the merge, on session 4103's tree: the 34 test files that read the license files and the 62 that read the package record, llms.txt, the guide or the site's verdict files, with 275 and 1011: 972 passed, 30 skipped, 1 failed (275's README count, fixed at once; 275, 207, 215 and 248 then 44 passed); on session 4102's tree the 350 files that read the release package or the chat spec: 1,356 passed, 13 skipped, 0 failed. The whole suite not run (three windows on this machine); not built (this window never builds) | requested |

## Row 1: what it holds

Sessions 4100 to 4106, reports `archive/sessions/SESSION_4100_REPORT.md` to `SESSION_4106_REPORT.md`.

- **The confirmation tool.** `scripts/license_confirm.py` checks robots first, finds a verdict's sentence on the current page, cuts sentences by code and records the result. Its record is the new `warehouse/metadata/license_confirmations.csv` (16 publishers confirmed on 13 November).
- **The document.** `scripts/licenses.py` gains the stale count, the section "Confirmed against the current page (chain 229)", and the standing "waits for a ruling". The last one means a flag stricter than the verdict is never loosened by a session.
- **The tests.** `tests/test_session4101_licenses.py` holds the flag-and-verdict agreement.
- **New verdicts:** Catalyst Cooperative (PUDL), may be public; Public Utility Commission of Texas, needs written permission; Louisiana Department of Revenue, needs written permission; Electrek and Energy-Storage.news, needs written permission (no page readable).
- **What a visitor would see change** (every page is `review` today, so no visitor sees it until a page opens):
  - **Four more tables held "license needed"** under the owner's ruling of 12 October: `policy_actions`, `policy_action_tags`, `policy_reads` (the PUCT's news releases) and `impact_tax_rules` (the Louisiana Department of Revenue).
  - `license_status.csv` holds 49 tables; release v1 holds 135, with 49 held out.
  - The state file says `/policy` loses `policy_actions` and `policy_reads`, and `/companies` goes fully dark.
  - `ferc714_forecast_growth` and `ferc714_planning_area_forecasts` become public in the ERW's verdict (flagged public since the owner's ruling of 6 November; PUDL's CC BY 4.0 now read).
- **Files kept in step:** `docs/licenses.md`, `docs/state/licenses_2026-10-21.md`, `site/data/license_status.json`, `site/data/table_verdicts.json`, `site/data/table_citations.json`, `package/src/erw/data/tables.csv`, `package/llms.txt`, `package/README.md`, `docs/guide.md`, `docs/redivis/release-v1*`, `site/lib/chat/spec.json`; tests 207 and 378 edited.
- **Documents:**
  - the four permission letters brought up to date (`docs/reviews/licenses/`, nothing sent);
  - `docs/licenses_costs.md` (new);
  - `docs/state/data_requests_licenses.md` (new: window A's requests, the FRED series' primary sources among them).
- `site/lib/release.ts` not changed.

## Known on this machine

- **A copied dash:** `site/data/table_citations.json` and `docs/redivis/release-v1/tables.csv` carry an en dash inside a news outlet's name, copied from `warehouse/metadata/sources.csv` (written by the daily run). Request 1 of `docs/state/data_requests_licenses.md` asks window A to fold it. No test reads it.
