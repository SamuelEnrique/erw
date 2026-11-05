# Session 719 report: the tracker joins the All grids tab

22 October 2026, from 11:55 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-719` on `wip/719-allgrids` (cut from `wip/718-allgrids`, recut at 12:55 over 718's landed tip `e40ff864`, below). Chain `queue/done/050-night-23-october-code-allgrids.md`, session 719. Model spend USD 0. No warehouse data written; no request to a publisher. The database was read only by the site's own pages on a local build.

## Read these first

- **Each facility the tracker (`/datacenters`) shows now links to its row on the All grids tab**, with the facility's MW set as the load and its row set as A: `/cost-of-power?view=allgrids&mw=<its MW>&a=<its row>`. The link reads "on All grids", under the facility's place, with "(its county)" or "(its state)" beside it, and its label says the reason.
- **How a facility is placed**:
  - **By its county**, where every utility serving the county (EIA-861's service territories, `utility_service_territories`) bills inside one grid only, by the balancing authority on its sales rows. The row is the county's own where the tab places one (session 718's counties: Harris is LZ_HOUSTON, for example), else the grid's main region.
  - **Else by its state**, where 85 percent or more of its retail sales are inside one grid (`eia861_utility_sales`, 2024, Bundled and Energy rows). 24 states pass; Texas is 88 percent ERCOT, California 79 percent CAISO and so not placed.
  - **Else not at all**: no link. The tracker names no node, so a facility is never placed at an ERCOT node (the prompt's "by the node the tracker names where it names one" finds none).
- **`datacenter_facilities` is held whole** (license needed since 21 October 2026, `site/data/license_status.json`), which this session found at its checks, not at its start:
  - **The tracker shows no facility while the hold stands, so no link shows on the site today.** The link is drawn for every row the tracker shows once rows show again.
  - **The first version broke the hold, and it was never pushed.** It wrote into the site file the counties where tracked facilities sit and, at the gate's request, each facility's name, operator and MW. Both commits were dropped by recutting the branch over 718's tip, so neither is in any pushed history.
  - The site file `site/data/siting/facilities.json` (66 KB) is now built from the two public tables only: every county in one grid (1,504) and every state. It holds nothing of the tracker's rows, and the tracker places the rows it shows when it draws them.
- **The tab names no facility.** The first version took the facility's name from the live set (one read), which broke session 716's rule that the tab reads no database. A second version took it from the site file, which broke the hold. The tab now shows the row and the MW, and the facility is named only on the tracker beside its link, never in the address.
- **Counts, from the warehouse's copy of the held table on this machine** (row counts only, as `coverage.csv` gives every table's): of 422 tracked facilities, the first version placed 141 (14 by county, 127 by state: PJM 62, ERCOT 44, MISO 17, SPP 10, NYISO 6, ISO-NE 2). The rest are in states split across grids, or outside the tab's grids (the Southeast, the West).
- **Keys unchanged**: the link adds no figure; the address `/cost-of-power?view=allgrids&mw=1400&a=ercot%3ALZ_NORTH` (the link's form) is read by check-values with a floor of 10.

## What to review

1. After the landing, open `https://erw-flame.vercel.app/internal/open`, then `https://erw-flame.vercel.app/cost-of-power?view=allgrids&mw=1400&a=ercot%3ALZ_NORTH`: the tab at 1,400 MW, with ERCOT LZ_NORTH as A in the headline and the A and B panel. This is the address a tracked facility's link opens.
2. `https://erw-flame.vercel.app/datacenters`: no facility shows while `datacenter_facilities` is held, so no link. Once rows show, each placed row has "on All grids (its county)" or "(its state)" under its place.
3. Screenshots: `docs/brand/review-719/` (before: the tracker at 1280 and 390, and the tab at that address; after: the tab at that address at 1280 and 390). The tracker has no after shot, since it draws no row while the hold stands.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `warehouse/derived/siting_page.py --in-dir-first ...` | 0 | facilities.json: 24 states, 1,504 counties in one grid; every other file kept (the same content) |
| `tests.test_session719`, `710`, `713`, `716`, `718` | 0 | OK. 719 checks that the file holds nothing of the held table and the builder never reads it |
| the chain's tests 700 to 720 with 215, 237, 238, 258, 408 (on 720's branch) | 0 | 185 OK, 1 skip |
| `db_probe.py` | 0 | |
| `npm run build` (lock `s720`, beat), on 720's branch | 0 | |
| check-values, `CHECK_VALUES_PAGES=/cost-of-power,/datacenters,/research` | 1 | 2,723 of 2,723 values equal; the one floor failing is `/research/card/gas_sets_price`, one of the ten held pages (production the same) |
| `check-existing-tab.mjs`, production against the build | 0 | every figure the same |

## The landing

With sessions 719 to 721 in one push (see 721's report).

## Decisions made without you

1. **County first, then state at 85 percent, then nothing.** A county whose utilities bill in two grids (Harris: ERCOT and MISO's Entergy Texas) falls to its state. The 85 percent bar keeps California (79 percent CAISO) and the split states unplaced, rather than guessed.
2. **The tab names no facility** (the hold, and 716's rule); the link carries no facility id.
3. **Session 716's rule stands** (no database read in the tab's files). 719's first version broke it and `tests/test_session716.py` caught it.

## For Samuel's ruling

- Whether the tab may name a facility set as A from the tracker once `datacenter_facilities` is public again, by one read of the live set (a narrow exception to session 716's rule) or by a site file built from the public rows.

## Files

- Changed: `warehouse/derived/siting_page.py` (`facilities_file`), `site/lib/siting.ts` (`facilitySite`, `facilityHref`), `site/lib/sitingdata.ts` (`FACILITY_GRID`), `site/app/datacenters/Body.tsx` and `DatacentersTable.tsx` (the link), `site/scripts/check-values.mjs` (one address), `docs/methods/siting.md` (decision 18).
- New: `site/data/siting/facilities.json`, `tests/test_session719.py`, `docs/brand/review-719/`, this report.
