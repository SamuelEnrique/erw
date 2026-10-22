# Session 705 report: time to connect on the All grids tab

22 October 2026, from 09:20 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-705` on `wip/705-allgrids` (cut from `wip/704-allgrids`). Chain `queue/done/050-night-23-october-code-allgrids.md`, session 705. Model spend USD 0. No warehouse data written; no request to a publisher.

## Read these first

- **Each row shows how long a generator took to connect in its grid**: the median months from queue entry to commercial operation of the requests that came online from 2023 to 2025. This is Berkeley Lab's Queued Up, 2026 edition (`lbnl_interconnection_queue`, public), through the new `site/data/siting/connect.json`.
  - ERCOT 45.8 months (227 requests), MISO 58.4 (25), PJM 71.3 (169), SPP 84.6 (30), NYISO 87.3 (5), CAISO 100.0 (41).
  - ISO-NE has no request online in those years with both dates, so it reads "not held". There is no median under five requests (the queues page's own floor).
  - The tip gives the quartiles and says this is a generator's wait, not a load's.
- **Under it, the large-load path**:
  - **"rule YYYY-MM"**: the newest decided large-load rule held for the grid, from "Your load"'s own rules file (`rules.json`, `large_load_rules`). The tip gives the regulator, docket, date, topic, its one-line reading and the document.
    - ERCOT: Texas's order of 18 September 2026 in docket 58481 (financial security of USD 50,000 per MW before a study).
    - CAISO, NYISO and ISO-NE have no decided rule held: "no rule held", with the count of open ones.
    - MISO: paused.
    - No faster path for a controllable load is stated in the rules held, and ERCOT's tip says so.
  - **ERCOT: "8,927 MW approved"**, its large loads approved to energize at its report of 19 June 2026 (`ercot_large_load_status`). The tip says this is approved to connect, not a wait.
  - **NYISO: "wait license needed"**: the waits measured by stage are held (`large_load_waits`, internal), computed in "Your load"'s file, and drawn as "license needed". No other grid has measured waits.
- **Keys**: `allgrids|connect|<row>`, `allgrids|llapproved|<row>`.
- **Sessions 703 to 705 were built once**, on this branch: check-values read every `/cost-of-power` address, 7,502 of 7,502 values, and the existing tab had 0 differences from production.

## What to review

1. After the landing, open `https://erw-flame.vercel.app/cost-of-power?view=allgrids` (internal view) and scroll the table to "Time to connect".
2. ERCOT rows: "45.80 mo", then "load: rule 2026-09, 8,927 MW approved". Hover each.
3. NYISO rows: "87.29 mo", "load: no rule held, wait license needed".
4. ISO-NE rows: "not held"; hover it for why.
5. Screenshots: `docs/brand/review-705/`. Before is 701's build; after is this one at 1280, 390 and 1600 wide.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `tests.test_session705` to `700` | 0 | 43 tests OK, 1 skip (the file recomputed from the table here; the floor of five; the newest decided rule; ERCOT's approvals; the held waits) |
| `test_session215` after its list gained `allgrids` (the landing gate's one failure, on 702's branch) | 0 | |
| `db_probe.py` | 0 | 0.62 s |
| `npm run build` (lock `s705`, beat) | 0 | no statement timeout |
| `check-values.mjs`, `CHECK_VALUES_PAGES=/cost-of-power` | 0 | 7,502 of 7,502 on 26 addresses |
| `check-existing-tab.mjs` production against the build | 0 | 0 differences |

## The landing

Sessions 700 to 705 land in one push from this branch; the landing section follows below once it is done.

## Decisions made without you

1. **The months are days / 30.4375 between `q_date` and `on_date`**, for requests operational with both dates, online in the newest three whole years of the edition (2023 to 2025).
2. **"The rule" is the newest decided row of the grid's rules.** The rules file holds proceedings and orders, not one threshold rule per grid. The 75 MW threshold is ERCOT's, and no table states it as a row.
3. **ERCOT's approved megawatts stand where a wait is not held.** They are labelled as approvals, not waits.
4. **NYISO's load queue (`nyiso_load_queue`) is not drawn**: NYISO's tables are license-held. The waits measured from it are internal.

## For Samuel's ruling

- The gaps file gains: connection timelines by utility, ERCOT's 75 MW rule as a held row, and a controllable load's path (session 713 completes the list).

## Files

- Changed: `site/lib/siting.ts` (`connectCell` and its file types), `site/lib/sitingdata.ts`, `site/app/cost-of-power/AllGridsView.tsx` (`ConnectTd`), `site/scripts/siting-files.mjs`, `warehouse/derived/siting_page.py` (`connect.json`).
- New: `site/data/siting/connect.json`, `tests/test_session705.py`, `docs/brand/review-705/`, this report.
