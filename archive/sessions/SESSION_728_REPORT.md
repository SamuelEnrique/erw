# Session 728 report: a zone's own demand growth

22 October 2026, from 14:29 UTC, on portable-laptop, unattended, in the worktree `C:\Users\samen\Documents\erw-728` on `wip/728-allgrids` (cut from `wip/727-allgrids`). Chain `queue/done/062-day-23-october-code-allgrids-2.md`, session 728. Model spend USD 0. No warehouse data written; no request to a publisher. The only requests: the ERW's own archive bucket (three tables rebuilt into `runs/archive_restore/`, below), the live set with the anon key (the replication) and the site's own pages on the local build. The tab reads no database (716's rule, held).

## Read these first

- **Every load zone of the tab now draws its own demand growth under its grid's** (27 zones: ERCOT's 8, NYISO's 11, ISO-NE's 8), from EIA-930's sub-region demand (`eia930_subba_demand_hourly` and its yearly tables), keyed `allgrids|zdemand|<row>`. The open-items table's line 11 is closed; the gaps row "demand growth of the row's own zone" is filled in part.
- **The window is the calendar year 2025 over 2024, not the grid's twelve months**, and the cell says so ("zone +5.51 % (2025 over 2024)"; the tip gives the sub-regions, the means and why). The sub-region table holds whole years to 2025 and the last 90 days (24 July to 21 October 2026): January to July 2026 are not held, so the grid's window (October 2025 to September 2026 over the twelve before) cannot be filled for a zone. The library (`zoneGrowth`, `lib/siting.ts`) takes the grid's window as soon as every one of its 24 months is held (a 2026 yearly table would do it), else the last two whole calendar years both held, else says why.
- **Each zone's sub-regions are a written table in the builder** (`ZONE_SUBBA` in `warehouse/derived/siting_page.py`, with the reason beside each): NYISO's and ISO-NE's zones are EIA's sub-regions one to one; ERCOT's load zones are not its weather zones, so Houston takes the Coast weather zone, North the North Central, North and East zones together, South the South and South Central together, West the West and Far West together, and Austin Energy's, CPS Energy's, LCRA's and Rayburn's zones take the weather zone that holds them (wider than their own, said in the tip). A hub draws nothing; a zone the table did not name would say the grid's figure stands for it (none today).
- **A month counts at 90 percent of its hours**, "Your load"'s demand file's own rule (`near_cell` 0.9): EIA gives ERCOT's December 2025 short by two days (696 of 744 hours), which a 95 percent rule dropped, leaving 2025 not whole for every ERCOT zone.
- **The headroom file gained a part, no figure moved, 27 were added.** The builder's new `--subba` mode adds the sub-region part to the headroom file in place (this machine holds few of the builder's other tables), so every other figure of the file is as it was; the full builder also writes the part when the tables are there. check-values on every cost-of-power address of the build: 2,732 of 2,732 (2,705 before, the 27 zone keys new); check-existing-tab: every figure the same.
- **The replication follows**: it computes N.Y.C.'s zone growth from the tab's own headroom file (the sub-region months are not in the live set), in the clean venv against the build: 82 figures computed, 70 beside the page, 0 differ.
- **The zones' figures** (2025 over 2024; the grid's twelve-month figure beside): ERCOT LZ_WEST +11.35 (grid +5.41), LZ_SOUTH +6.84, LZ_AEN, LZ_CPS and LZ_LCRA +6.43 (all the South Central weather zone), LZ_HOUSTON +5.51, LZ_NORTH +5.46, LZ_RAYBN +0.81; NYISO HUD VL +2.71, DUNWOD +2.56, MHK VL +1.94, CAPITL +1.92, N.Y.C. +1.08, CENTRL +1.06, LONGIL +1.05, GENESE +0.60, WEST -1.40, MILLWD -2.17, NORTH -6.69 (grid +0.52); ISO-NE WCMASS +2.00, NEWHAMPSHIRE +1.84, CONNECTICUT +1.48, VERMONT +1.39, NEMASSBOST +1.33, RHODEISLAND +0.75, SEMASS +0.34, MAINE -1.10 (grid +2.90).

## What to review

After the landing (session 730), on `https://erw-flame.vercel.app` after `/internal/open`:

1. `/cost-of-power?view=allgrids&mw=1000&sort=headroom&kind=zone`: the load zones with "zone +x.xx % (2025 over 2024)" under each grid's growth; hover one for its sub-regions and means.
2. `/cost-of-power?view=allgrids&mw=1000&sort=headroom&kind=zone&grid=nyiso`: NYISO's eleven zones, NORTH falling, HUD VL rising.
3. Shots: `docs/brand/review-728/` (`before_04-headroom_*` and `before_05-headroom-zones_*` from production; `04-headroom_*`, `05-headroom-zones_*`, `05b-headroom-zones-nyiso_*` from the build).

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | on duty for "session 728" |
| `restore.py --from-bucket` for `eia930_subba_demand_hourly`, `_2024`, `_2025` | 0, 0, 0 | 186,177, 726,716 and 723,617 rows into `runs/archive_restore/` |
| `siting_page.py --subba --in-dir-first --in-dir runs/archive_restore` | 0 | 27 sub-regions, months 2024-01 to 2026-09 |
| `tests.test_session728` (6) with 706, 712, 716, 718, 724, 726 | 0 | 33 tests, 2 skipped (two test-side fixes first: the index's region key, the Num's prop name) |
| `npx tsc --noEmit` | 2 | the errors are Next's generated types (`PageProps`, `@/content/*.json`), none in the edited files; the build's own TypeScript step passes |
| `db_probe.py` | 1, then 0 | closed at 14:51 (3.47 s); open at 14:52 (2.75 s) |
| `npm run build` (lock `s728`, beat), three times (the figures; the zone line's words inside the tip's trigger; then its rule in `tokens.css`, session 715's sans rule for a cell's small labels) | 0, 0, 0 | |
| `walk-728.mjs` on the build, three times | 0 | 6 of 6 steps each; 27 zone lines and 27 keys on the headroom sort, 11 on NYISO's |
| check-values, `CHECK_VALUES_PAGES=/cost-of-power`, `MSYS_NO_PATHCONV=1` | 0 | 2,732 of 2,732 |
| `check-existing-tab.mjs`, production against the build | 0 | every figure the same |
| the replication, clean venv, `--page http://localhost:3728` | 0 | 82 computed, 70 beside the page, 0 differ; `allgrids|zdemand|nyiso:N.Y.C.` 1.079679 both |
| em dashes in the changed files | 0 | none |
| the server stopped, the lock released | 0 | |

## The landing

Not in this session: 730 lands 719 to 730.

## Decisions made without you

1. **The window falls back to two whole calendar years** where the grid's twelve months are not all held, said in the cell and the tip, rather than drawing nothing for every zone until a 2026 yearly table lands. The library prefers the grid's window the moment it is held.
2. **The headroom sort stays on the grid's figure**: the zones' figures are of another window, so sorting the two together would compare unlike things. The zone's figure is drawn, keyed and read, not sorted by.
3. **ERCOT's utility zones take their weather zone's demand** (Austin, CPS, LCRA, Rayburn), said to be wider than their own, rather than drawing nothing: the weather zone is the nearest demand the warehouse holds for them.
4. **The 90 percent rule for a month**, "Your load"'s own, in place of 95.
5. **The builder's `--subba` mode** adds the part in place, since this machine holds few of the builder's other tables and a full run here would recompute other figures from this machine's copies.

## For Samuel's ruling

- Whether the data machine's chain should pull a 2026 yearly table of `eia930_subba_demand_hourly` (or extend the rolling table), so that a zone's growth takes the grid's own twelve-month window.

## Files

- Changed: `warehouse/derived/siting_page.py` (`ZONE_SUBBA`, `subba_paths`, `subba_part`, `--subba`), `site/lib/siting.ts` (`HeadroomFile.subba`, `zoneGrowth`, the key), `site/app/cost-of-power/AllGridsView.tsx` (`ZoneGrowthLine`), `site/app/tokens.css` (the zone line in session 715's sans rule), `warehouse/replication/siting.py` (the zone key), `site/data/siting/headroom.json` (the `subba` part), `docs/reviews/siting-gaps.md` and `site/data/siting/gaps.json` (the row filled in part), `docs/reviews/siting-open-2026-10-23.md` (line 11 closed).
- New: `tests/test_session728.py`, `docs/brand/review-728/` (the script, 6 shots, 4 before shots, two records), this report.
- On this machine, not in git: `runs/archive_restore/eia930_subba_demand_hourly*.csv`, `runs/chain_062/repl728.out`.
