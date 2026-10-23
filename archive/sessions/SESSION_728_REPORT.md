# Session 728 report: a zone's own demand growth

22 October 2026, from 15:21 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-728` on `wip/728-allgrids` (cut from `wip/727-allgrids`). Chain `queue/done/062-day-23-october-code-allgrids-2.md`, session 728. Model spend USD 0. No warehouse data written. The only requests went to the ERW's own archive bucket (two tables rebuilt into `runs/archive_restore/`); no request to a publisher.

## Read these first

- **19 rows now show their zone's own demand growth** under their grid's: NYISO's eleven zones and ISO-NE's eight load zones, where EIA-930 names the same area as a sub-region (`eia930_subba_demand_hourly`). The match is by name: ZONJ New York City is N.Y.C.; 4006 Southeast Mass. is .Z.SEMASS.
  - **The figure**: the sub-region's mean hourly demand in 2025 against 2024, over the hours each year holds (EIA gives a few hours blank; nothing is filled).
  - **The range**: NYISO's NORTH -6.70 percent, MILLWD -2.18, WEST -1.41; HUD VL +2.71, DUNWOD +2.55; N.Y.C. +1.08. ISO-NE's WCMASS +2.00, NEWHAMPSHIRE +1.84; MAINE -1.10.
  - **The key**: `allgrids|zonegrowth|<row>`. 19 keys; check-values 2,696 of 2,696.
- **A calendar year, not the grid's window**:
  - The live sub-region table holds 90 days, and the yearly tables end with 2025, so January to July 2026 is held by no sub-region table. The tip says so.
  - The sort by headroom stays the grid's figure, since the two windows differ.
- **ERCOT's and CAISO's rows keep the grid's figure.** ERCOT's sub-regions are its weather zones (Coast, Far West and so on), not its load zones, and CAISO's are utilities (PG&E, SCE), not trading hubs. A map between them would be invented.
- **Tables rebuilt**: `eia930_subba_demand_hourly_2024` and `_2025`, from the ERW's archive into `runs/archive_restore/` (`restore.py --from-bucket`).
- **Brand**: the zone line's words are sans and its figure mono, as session 715's rule has every other small label. 726's "delivery only" and "energy only" were added to the same rule; they had been drawn in the figures' mono.
- Open items 9 and 23 are closed (`docs/reviews/siting-open-2026-10-23.md`).

## What to review

1. After the landing, `https://erw-flame.vercel.app/cost-of-power?view=allgrids&mw=1000&sort=headroom&grid=nyiso,isone` (internal view): under each zone's "+0.52 %" (NYISO's) or "+2.90 %" (ISO-NE's), "zone +1.91 % in 2025". Hover it for the sub-region, its two means and its hours.
2. Shots: `docs/brand/review-728/before_headroom_nyiso_1280.png` (production) against `after_headroom_nyiso_1280.png`, and at 390.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `restore.py eia930_subba_demand_hourly_2024` and `_2025 --from-bucket` | 0 | rebuilt 1 of 1, each |
| `warehouse/derived/siting_page.py --in-dir-first ...` | 0 | headroom.json: 19 zones, 2025 over 2024; every other file kept (the same content) |
| `tests.test_session728`, `706`, `718`, `716`, `712`, `237` | 0 | OK; 706's comparison of the file leaves out the zones, as it does 718's peak capacity |
| `db_probe.py` | 0 | |
| `npm ci`, `npm run build` twice (lock `s728`, beat) | 0 | |
| check-values, `CHECK_VALUES_PAGES=/cost-of-power` | 0 | 2,696 of 2,696 |
| `check-existing-tab.mjs`, production against the build | 0 | every figure the same |

## The landing

Sessions 722 to 730 landed in one push at 16:15 UTC: see `SESSION_730_REPORT.md`, "The landing".

## Decisions made without you

1. **Only the 19 rows whose names EIA-930 gives as sub-regions.** No weather zone stands for a load zone, and no utility for a hub.
2. **The newest whole calendar year over the one before**, since no sub-region table holds 2026's first seven months.
3. **The sort stays the grid's**: a calendar-year zone figure and a twelve-month grid figure are not one measure.

## For Samuel's ruling

- Whether the data machine should keep a 2026 yearly sub-region table (its first seven months are in no table), so a zone's growth can use the grid's twelve months.

## Files

- Changed: `warehouse/derived/siting_page.py` (`SUBBA_ROW`, `zone_growth`), `site/data/siting/headroom.json`, `site/lib/siting.ts` (`HeadroomFile.zones`, `zoneGrowth`, the key), `site/app/cost-of-power/AllGridsView.tsx` (the cell), `site/app/tokens.css` (two labels), `tests/test_session706.py`, `docs/methods/siting.md` (decision 21), `docs/reviews/siting-open-2026-10-23.md`.
- New: `tests/test_session728.py`, `docs/brand/review-728/`, this report.
