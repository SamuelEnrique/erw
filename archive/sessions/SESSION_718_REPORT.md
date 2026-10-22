# Session 718 report: the data machine's tables, wired in

22 October 2026, from 11:50 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-718` on `wip/718-allgrids` (cut from `wip/717-allgrids`). Chain `queue/done/050-night-23-october-code-allgrids.md`, session 718. Model spend USD 0. No warehouse data written. The only requests: `scripts/sync.py` (main pulled; Redivis's counts read), the ERW's own archive bucket (four tables rebuilt into `runs/archive_restore/`), and the live set with the anon key (the replication).

## Read these first

- **`python scripts/sync.py`** pulled main (41 commits, the data machine's chain 043 among them). Coverage now lists four public tables added since 23 October for this tab's gaps: `utility_service_territories`, `interconnection_durations`, `interconnection_durations_summary` and `grid_peak_vs_capacity`. They are not on Redivis, so each was rebuilt from the archive into `runs/archive_restore/`.
- **Each is wired into its column**, by the method note's rule:
  - **Time to connect** reads `interconnection_durations`: the same requests as before, its months to one decimal. ERCOT 45.8, CAISO 100.0, PJM 71.3, MISO 58.4, SPP 84.6, NYISO 87.3; ISO-NE none (Berkeley Lab's file gives it no operation date).
  - **Headroom**: capacity above the peak now covers **every grid** from `grid_peak_vs_capacity` (by each generator's balancing authority, no state mapped): CAISO 106 percent above its 2025 peak, ERCOT 97, SPP 78, MISO 62, ISO-NE 37, NYISO 34, PJM 31.
    - The figure now reads "percent above the peak", where session 706's (NYISO and ISO-NE only) read "percent of the peak".
    - The tip names solar, wind and storage at their ratings, and says it is not a reserve margin.
  - **Utility**: a row whose name is a place (18 rows) now reads its county's utilities from `utility_service_territories`. The counties are the data machine's hub counties of session 681 (Harris, Los Angeles, New York, Suffolk, Allegheny, Marion, Sedgwick), and for a zone, its city's county.
    - The cell names the county's utilities and prices the largest seller to industry among those inside the row's grid.
    - New York City is now Consolidated Edison (delivery only, USD 128.79 per MWh). SP15 is Southern California Edison (USD 204.28). Session 681 had found PG&E there, which serves 50 counties but not Los Angeles.
    - **Harris County lists CenterPoint Energy**, Entergy Texas and San Bernard Electric Coop. Entergy Texas is MISO's and is never priced for an ERCOT row. CenterPoint, the wires utility, files no sales row, so it is named, not priced, and the figure is San Bernard's, with the tip saying all of this.
    - Long Island (Suffolk) has no sales row inside NYISO: named, "no sales row".
    - The other 30 rows keep the state's largest seller, now said to be a stand-in with session 681's finding.
- **"None there" does not apply**: the tables are there, so the energy column's three-year window was not added.
- **Checks on a build of this branch**:
  - check-values 2,515 of 2,515; the existing tab 0 differences from production.
  - The replication, run again in its clean environment against this build: 81 figures, 69 beside the page, 0 differ. Its months to connect now read `interconnection_durations` from the live set, and its utility the county's.
- **The gaps file and the method note follow**: two rows of the gaps are filled in part, one is added (Texas's wires utilities file no sales row), and decision 17 is in the note.

## What to review

1. After the landing, `https://erw-flame.vercel.app/cost-of-power?view=allgrids&sort=utility` (internal view): each row's utility, with "and N more" where its county has several. Hover "Consolidated Edison Co-NY Inc" for the county's list.
2. Sort by demand growth (`&sort=headroom`): each row's line ends "capacity N% above peak", for every grid.
3. Screenshots: `docs/brand/review-718/` (before: 717's walk shots of the utility and headroom sorts; after: this build at 1280 and 390).

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `scripts/sync.py --tables ...` | 0 | main pulled; 4 tables not on Redivis |
| `warehouse/archive/restore.py <table> --from-bucket`, four tables | 0 | 4 rebuilt (one at the second try) |
| `tests.test_session718`, and `705`, `706`, `708`, `712`, `713`, `700`, `710`, `716`, `717` | 0 | OK. 705's, 706's, 708's and 713's pins follow the new tables |
| `db_probe.py` | 0 | 0.77 s |
| `npm run build` (lock `s718`, beat), twice | 0 | |
| check-values, `CHECK_VALUES_PAGES=/cost-of-power` | 0 | 2,515 of 2,515 |
| `check-existing-tab.mjs`, production against the build | 0 | 0 differences |
| the replication, clean environment, against the build | 0 | 81, 69, 0 differ |

## The landing

Sessions 713 to 718 landed in one push (`task/713-718-allgrids`, commit `e40ff864`), merged into main at 13:01 UTC (`e39de81a`, run 39781404444).

- **The first gate** (on `b0b571c0`) failed the suite on two tests: `test_session704` pinned the capacity cell's markup from before 714's tips, and `test_session408` found `/internal/siting-gaps` (713) neither read by check-values nor exempt. 704's pin now follows the tip cell, and the page is exempt in 408 with its reason (words only; it reaches the database only through `internalOk`, as `/internal/holds` does). Commit `1d80200e`, then main merged (`e40ff864`).
- **The second gate** (on `e40ff864`): freeze 0; main in the commit; no `task/` branch in flight; suite 5,928 tests OK (304 skipped); npm ci 0; build 0; check-values 7,553 of 7,553 values equal, with the eleven floors as at the earlier landings (the ten held pages, and `/digest` before the day's Digest; production fails the same).
- **The steps after check-values**, on a build of the same commit in this worktree (lock `s718b`): check-routes 0 (226 pages, 0 failed), check-cross-checks 0 (92 of 92), check-csp 0 (97 pages, 0 violations).
- **Before the push**: freeze status 0; two `task/` branches on GitHub, both already on main (`task/638-644-sources`, the data machine's, and this chain's `task/706-712-allgrids`, already deleted).
- **Snapshots**: `s718-before` at 12:48 UTC; the push at 12:48; Vercel's status on `e39de81a` "Deployment has completed" at 13:04:18 UTC; production showed 718's "above peak" on the headroom sort at 13:04:51; `s718-after` at 13:04 UTC. `compare s718-before s718-after`: **0 differences** on 25 pages, expected (every page is in review).
- The merged `wip/718-allgrids` was deleted on GitHub; 713 to 717 were never pushed.

## Decisions made without you

1. **A zone's county is its city's** (Harris for Houston, Travis for Austin, Bexar for San Antonio, Erie for Buffalo and so on); a hub's is the data machine's choice of session 681. The 30 other rows keep the state stand-in.
2. **A county's utility must bill inside the row's grid** (by the balancing authority its sales rows name). A utility with no sales row is named and not priced.
3. **Capacity above the peak is the table's own figure** (`capacity_over_peak_pct`), not recomputed.

## For Samuel's ruling

- Whether Texas's wires utilities (CenterPoint, Oncor, AEP Texas, TNMP) should be priced from their tariffs (`texas_delivery_charges` holds four) in the Utility column for ERCOT rows, in place of a retail seller.

## Files

- Changed:
  - `warehouse/derived/siting_page.py` (`connect_from_durations`, `peak_capacity`, `county_utilities`, `ROW_COUNTY`) and `site/data/siting/connect.json`, `headroom.json`, `utility.json`, `gaps.json`;
  - `site/lib/siting.ts` (`capacityOverPeak`, `utilityCell`, the column tips) and `site/app/cost-of-power/AllGridsView.tsx` (`CountyUtilityTd`, the headroom words);
  - `site/app/tokens.css` (a utility's name);
  - `warehouse/replication/siting.py`;
  - `docs/methods/siting.md`, `docs/reviews/siting-gaps.md`;
  - `tests/test_session705.py`, `706`, `708`, `713`.
- New: `tests/test_session718.py`, `docs/brand/review-718/`, this report.
