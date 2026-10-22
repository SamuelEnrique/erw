# Session 700 report: the All grids tab of /cost-of-power, its rows, profiles and columns

22 October 2026, from 08:46 UTC, on samueloldlaptop (the code machine), unattended, in the worktree `C:\Users\lossa\Documents\erw-700` on `wip/700-allgrids` (from origin/main at `9a4ab077`). Chain `queue/done/050-night-23-october-code-allgrids.md`, session 700. Model spend USD 0. No warehouse data written; no request to a publisher.

## Read these first

- **"What a datacenter pays" has a third view, All grids** (`/cost-of-power?view=allgrids`), between "Your load" and "Grid by grid". Its rows are "Your load"'s own index, so the two views hold the same regions:
  - **48 hub and zone rows**: ERCOT 14, CAISO 3, NYISO 11, ISO-NE 9, SPP 2, MISO's 8 hubs ("paused while terms are reviewed"), and PJM as one row (no PJM hub or zone price is held).
  - **873 ERCOT nodes behind a toggle**: every point of `node_basis_daily` that is neither a hub nor a load zone (888 points, 7 hubs, 8 zones).
  - The default order is alphabetical by grid, then by name, and the line above the table says so.
- **The left box holds every input**: the profile (Datacenter selected), the size (default 100 MW) and the load factor. Each shows its default in grey with its source on hover, and each has a Reset named for its field.
- **The four profiles set three inputs each** (load factor, curtailment rule, interruptible) in `site/lib/siting.ts`:
  - datacenter: 0.90, never curtails;
  - flexible compute: 0.90, off at the four ERCOT peaks and at or above USD 1,000;
  - electrolyzer: 0.55 within 0.40 to 0.70, runs below a strike;
  - heavy industry: 0.80, interruptible.
- **The eight column heads carry their source and method on hover.** No number is shown yet but the row counts, which are check keys (`allgrids|rows|hubs` 48, `allgrids|rows|nodes` 873).
- **`docs/methods/siting.md` v0**: each column's table, filter, vintage, license, the function that computes it today and its words where it cannot be filled; the profiles and their sources; five decisions.
- **Four tables the tab needs are not in the live set and were not on this machine**: `node_basis_daily`, `egrid_power_plants`, `eia861_utility_sales` and `eia_state_capacity_annual` (`epa_ghgrp_power_co2` and `eia861m_utility_sales_monthly` too). Each was rebuilt from the ERW's own archive bucket into `runs/archive_restore/` (`warehouse/archive/restore.py --from-bucket`; not `warehouse/output`, so no data lock). The tab reads them only through its own files under `site/data/siting/`, written by the new `warehouse/derived/siting_page.py`.

## What to review

1. Open `https://erw-flame.vercel.app/internal/open` and enter the token, then go to `https://erw-flame.vercel.app/cost-of-power?view=allgrids` once this session has landed.
2. Click "All grids" in the row of views under the title. You should see the box "Your load" on the left, and on the right the line with "48 rows", the toggle and the table.
3. Hover each column head (Energy to All-in): each gives its source and method in one line.
4. Click "ERCOT nodes (873)": the table lists the nodes, and the line reads "873 nodes, from 2025-10-01 to 2026-10-20".
5. Change the profile to Electrolyzer. The load factor should become 0.55, editable from 0.40 to 0.70. Type 0.6 and press Show: "Reset load factor" appears.
6. Screenshots: `docs/brand/review-700/`. `before_allgrids_*` is production before (the address then showed "Your load"); `after_allgrids_*` and `after_nodes_*` are this build, at 1280 and 390.

## Checks

Every gate redirected to a file under `runs/chain_050/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 700"` | 0 | on duty |
| `tests.test_session700`, `tests.test_session138` | 0 | 9 and 24 tests OK; with the restored node table in place, 9 of 9 and no skip (the node file equals the table's nodes) |
| `scripts/db_probe.py` | 0 | 0.68 s |
| `npm run build` (build lock `s700`, duty beat) | 0 | no statement timeout in the log |
| `check-values.mjs`, `CHECK_VALUES_PAGES=/cost-of-power`, on the build | 0 | 1,408 of 1,408 values; both new pages read, 1 key each, no floor yet |
| `check-existing-tab.mjs` (new), production against the build | 0 | `/cost-of-power` 234 keys, `?run=hours` 236, `?grid=caiso` 78, `?view=grids` 40: 0 differences. No default figure of the existing tab moved |
| screenshots `shot.mjs` at 1280 by 900 and 390 by 844 | 0 | 6 files |

## The landing

Landed with sessions 700 to 705 in one push at 10:09 UTC (`b25a5c66`); the gate, the snapshots (0 differences) and the deletion of the merged branches are in `SESSION_705_REPORT.md`, "The landing".

## Decisions made without you

1. **All grids is a third view** between "Your load" and "Grid by grid". "Grid by grid" (session 37's tab) stays as it is.
2. **The profile dropdown is in the All grids tab's own box**, not in "Your load"'s: there it would change nothing, and no default of "Your load" may move.
3. **PJM is one row of its own ("the grid")**, because no PJM hub or zone price is held. MISO's 8 hubs are rows, with the existing tab's words.
4. **The defaults the prompt does not give**:
   - the flexible profile's strike is USD 1,000 per MWh, the page's scarcity level;
   - the electrolyzer's load factor is 0.55, the middle of 0.40 to 0.70;
   - the electrolyzer's strike is each row's own price at that share of hours.
5. **A node's price is its hub's twelve-month mean plus its mean daily day-ahead basis** (`node_basis_daily` holds days, not hours).
6. **Check keys are written `allgrids|<column>|<row>`**, the site's form of the prompt's `allgrids_<column>_<row>`.
7. **The held tables were rebuilt from the ERW's own archive** into `runs/archive_restore/`, outside `warehouse/output`. This is a read of our own storage bucket, not a publisher's site.
8. **`site/scripts/check-existing-tab.mjs` is new.** It is how each session of the chain proves that the existing tab's figures do not move.

## For Samuel's ruling

- Whether "Grid by grid" (session 37's view) should be retired now that All grids exists.
- The profiles' defaults the prompt left open (decision 4): the strike of flexible compute, and the electrolyzer's 0.55 and its strike.

## Files

- New: `site/lib/siting.ts`, `site/lib/sitingdata.ts`, `site/app/cost-of-power/AllGridsView.tsx`, `AllGridsForm.tsx`, `site/scripts/siting-files.mjs`, `site/scripts/check-existing-tab.mjs`, `site/data/siting/nodes.json`, `warehouse/derived/siting_page.py`, `docs/methods/siting.md`, `tests/test_session700.py`, `docs/brand/review-700/`, this report.
- Changed: `site/app/cost-of-power/page.tsx` (the view), `site/lib/datacenter.ts` (the view's name in the address), `site/scripts/check-values.mjs` (two pages, the `allgrids` keys).
