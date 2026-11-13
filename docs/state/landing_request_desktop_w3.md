# Landing requests: the desktop's third window (chain 229, the licensing sweep)

Energy Research Warehouse (ERW). Written by chain 229 (`queue/done/229-day-13-november-desktop-window3-licenses.md`), session 4106, on 13 November 2026. This window never builds the site, never runs `scripts/land_check.py` and writes no warehouse data. The landing desk (window B) lands each row through `scripts/land_check.py` with the task and port given, runs the commands it prints each on its own (the snapshot before, the push to `task/`, the snapshot after, the comparison), never between 14:00 and 16:15 UTC, and marks the row landed with the commit.

| # | Branch | Head | Task | Port | Requested (UTC) | Tests on this machine | State |
|---:|---|---|---|---:|---|---|---|
| 1 | `wip/4100-licenses` | `3ab353fcc` (or its one later commit, this file's) | `4100-licenses` | 4100 | 2026-11-13 10:55, updated 11:20 (sessions 4100 to 4109) | on `3ab353fcc`'s tree (`origin/main` merged at 10:52): the 462 test files that read the license files, the package record, llms.txt, the guide, the site's verdict files, the release package or the live set, with this chain's tests 4101 and 4109: 2,999 passed, 94 skipped, 0 failed (6 min 51 s, 11:10 UTC); `licenses.py check`, `build_llms.py --check`, `build_tables.py --check`, `release_v1.py --check`, `check_spec.py` exit 0. The whole suite not run (three windows on this machine); not built (this window never builds). The branch takes no further commit: chain 229 goes on on `wip/4110-licenses` | superseded by row 4 (main's `package/llms.txt` moved at 11:57; row 4 has `origin/main` merged with the conflict resolved) |
| 2 | `wip/4110-licenses` | `f2c354f14` (or its one later commit, this file's) | `4100-licenses` | 4100 | 2026-11-13 11:50 | holds row 1 (`wip/4100-licenses` is its ancestor): landing row 2 alone lands both. On `f2c354f14`'s tree (`origin/main` merged at 11:40, with session 5101's curtain fix): the 479 test files that read the license files, the package record, llms.txt, the guide, the site's verdict files, the release package, the live set, `/data/licenses` or the method notes changed, with tests 4101, 4109 and 5101: 3,113 passed, 101 skipped, 0 failed (7 min 49 s, 11:41 UTC); `licenses.py check`, `build_llms.py --check`, `build_tables.py --check`, `release_v1.py --check`, `check_spec.py` exit 0. The whole suite not run; not built (this window never builds). The branch takes no further commit: chain 229 goes on on `wip/4115-licenses` | superseded by row 4 (main's `package/llms.txt` moved at 11:57; row 4 has `origin/main` merged with the conflict resolved) |
| 3 | `wip/4115-licenses` | `cc3bdbd17` (or its later commits of session 4149: its report and this file) | `4100-licenses` | 4100 | 2026-11-13 11:54 | holds rows 1 and 2: landing row 3 alone lands all three. Sessions 4115, 4148 and 4149 add the record's header lines (`scripts/licenses.py`), the note `docs/state/note_2026-11-13_desktop_window3.md` and reports, nothing else. On the tree of session 4115 (`origin/main` merged at 11:40): the 34 license test files with tests 4101 and 4109, 508 passed, 12 skipped, 0 failed; row 2's 479 files passed on its head. The whole suite not run; not built. The branch takes no further commit: chain 231 goes on on `wip/4150-licenses` | requested |## Row 1: what it holds
| 4 | `wip/4150-licenses` | `0362df771` (or its one later commit, this file's) | `4100-licenses` | 4100 | 2026-11-13 12:07 | holds rows 1 to 3 (chain 229, sessions 4100 to 4149) with `origin/main` merged at 11:57: one conflict, `package/llms.txt`, resolved as main's text with the held count 49 and the catalogue written again by `build_llms.py`; the chat spec exported again. On the head's tree: the 479 test files of row 2 with tests 4101, 4109 and 5101: 3,113 passed, 101 skipped, 0 failed (7 min 34 s, 11:58 UTC); `licenses.py check`, `build_llms.py --check`, `build_tables.py --check`, `release_v1.py --check`, `check_spec.py` exit 0. The whole suite not run; not built. The branch takes no further commit: chain 231 goes on on `wip/4151-licenses` | requested |
Sessions 4100 to 4109, reports `archive/sessions/SESSION_4100_REPORT.md` to `SESSION_4109_REPORT.md`.

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
- **Sessions 4107 to 4109.**
  - Berkeley Lab's verdict is now cut from a page (CC BY 4.0, the Queued Up 2026 page), and 20 more verdicts are confirmed on their current pages.
  - New verdicts: Svenska kraftnat, Latvia's CSB and E-Control (their three internal tables wait for a ruling).
  - Hosts whose robots files refuse Anthropic's agents are not asked, and window A is asked to stop three such fetches (requests 13 to 15).
  - `large_load_public` is ruled public in `licenses.py` (the owner's ruling of 14 October).
  - `warehouse/redivis/release_v1.py` holds out a table whose ERW verdict is unsettled (133 in v1, 51 held out).
  - `tests/test_session4109_public_site.py` checks that no table reaches the public site while its verdict is not public. It names three findings cards built from internal tables (`gas_sets_price`, `siting_flexible`, `siting_gigawatt`), waiting for the owner's ruling, and stops `/` and `/research` from opening while they wait.
- `site/lib/release.ts` not changed.

## Row 2: what it adds to row 1

Sessions 4110 to 4114, reports `archive/sessions/SESSION_4110_REPORT.md` to `SESSION_4114_REPORT.md`.

- **The page:** `/data/licenses` (`site/app/data/licenses/page.tsx`) has two lines brought in step with the record (the letters' update and the costs file; the publishers whose tables stay internal).
- **The method notes:** 13 notes' license lines extended with dated paragraphs, nothing deleted.
- **The test:** `tests/test_session4109_public_site.py` gains `HeldGridFiles`. 138 files of NYISO's and ISO-NE's prices under `site/public/` are grandfathered in `tests/fixtures/chain229_held_grid_public_files.txt` (they wait for the owner's ruling), and a new one fails.
- **The verdicts:** 13 more (the Georgia PSC, the Virginia SCC, CME, MakStat, Grenada's CSO, ERU, HOPS, CEB, Ghana's Energy Commission, Mongolia's ERC, REN, ELES), and CENCE's and VMME's existing verdicts found by two `CANON` rules. All their tables are internal, so no page changes.
- **The tool:** `scripts/license_confirm.py verdict --start/--end`.
- **The rulings file:** `docs/state/unsettled_licenses_2026-11-13.md` (the 26 tables still not settled, a default each).
- **No change a visitor would see** beyond row 1's.

## Known on this machine

- **A copied dash:** `site/data/table_citations.json` and `docs/redivis/release-v1/tables.csv` carry an en dash inside a news outlet's name, copied from `warehouse/metadata/sources.csv` (written by the daily run). Request 1 of `docs/state/data_requests_licenses.md` asks window A to fold it. No test reads it.
