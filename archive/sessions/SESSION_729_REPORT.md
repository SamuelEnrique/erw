# Session 729 report: the tracker's facilities, placed by their utility

22 October 2026, from 15:06 UTC, on portable-laptop, unattended, in the worktree `C:\Users\samen\Documents\erw-729` on `wip/729-allgrids` (cut from `wip/728-allgrids`). Chain `queue/done/062-day-23-october-code-allgrids-2.md`, session 729. Model spend USD 0. No warehouse data written; no request to a publisher. The only requests: the ERW's own archive bucket (three tables rebuilt into `runs/archive_restore/`, outside the repository: `eia861_utility_sales`, `utility_service_territories`, and `datacenter_facilities` for counting only) and the site's own pages on the local build.

## Read these first

- **A tracked facility is now placed by the utility the tracker names, between its county and its state**: where the name is one utility of EIA-861 exactly, after a written normalisation (`UTILITY_NORM_RULES` in `warehouse/derived/siting_page.py`; `normUtility` in `lib/siting.ts` applies the same eight rules, and a test holds the two alike), and that utility's sales rows sit inside one grid of the tab; never by a fuzzy match ("Austin" matches nothing; "Austin Energy" matches ERCOT's). A wires utility with no sales row takes the one grid of the counties it serves where they all agree (Oncor's straddle ERCOT and SPP, so Oncor places nothing, by the rule).
- **The site file gains a part, from public tables only**: `facilities.json` holds 2,072 normalised names in one grid (1,284 names left out: shared across grids, or rows in two grids or outside the tab's); nothing of the held facilities table enters it (719's test, widened by one key, still holds). The builder gains a `--facilities` mode that writes the file alone from the two tables.
- **Count before and after, from the warehouse's copy of the held table (rows only, as 719 counted)**: of 422 tracked facilities, **141 placed before and 141 after**: 14 by county, 0 by utility, 127 by state (ERCOT 44, PJM 62, MISO 17, SPP 10, NYISO 6, ISO-NE 2); 281 not placed. **Only 3 of the 422 name a utility, and none of the 3 is an exact name of EIA-861.** The chain's premise ("the tracker names a utility for many of the rest") does not hold in the table as it is: the way is built, tested and keyed, and places no facility more today. It will as the tracker's rows name utilities as EIA names them.
- **The tracker still shows no facility** (`datacenter_facilities` held whole), so no link shows; the label it will draw reads "(its county)", "(its utility)" or "(its state)". The link and the tab's naming of A are unchanged.
- **No figure moved**: check-values on every cost-of-power and datacenters address of the build, 2,764 of 2,764 (one page's read failed once while two checks ran at once: read again alone, 40 of 40); check-existing-tab, every figure the same.

## What to review

1. After the landing (730), `https://erw-flame.vercel.app/datacenters` after `/internal/open`: no facility while the hold stands. Once rows show, a facility whose utility is EIA's exact name reads "on All grids (its utility)".
2. `docs/brand/review-729/`: the tracker and the link's address (`/cost-of-power?view=allgrids&mw=1400&a=ercot%3ALZ_NORTH`) on the build at 1280 and 390, with the earlier shots as `before_*`.
3. The rules, in `warehouse/derived/siting_page.py` (`UTILITY_NORM_RULES`), and in the file at `site/data/siting/facilities.json` under `utilities.rules`.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | on duty for "session 729" |
| `restore.py --from-bucket` for the three tables | 0, 0, 0 | 433,115, 11,893 and 422 rows into `runs/archive_restore/` |
| `siting_page.py --facilities --in-dir-first --in-dir runs/archive_restore` | 0 | 24 states, 1,504 counties, 2,072 utility names in one grid |
| `tests.test_session729` (7) with 719 (widened), 716, 728 | 0 | after the examples were corrected to what the tables hold (Oncor has no sales row and straddles two grids; Austin Energy is the ERCOT example) |
| the count, a node script over the held copy's state, county and utility columns | 0 | 141 before, 141 after; 3 rows name a utility, 0 match |
| `db_probe.py` | 0 | 2.54 s |
| `npm run build` (lock `s729`, beat) | 0 | |
| `walk-729.mjs` on the build | 0 | 4 of 4; the tracker held, 0 links; the link's address draws the headline |
| check-values, `CHECK_VALUES_PAGES=/cost-of-power,/datacenters` | 1, then 0 | 2,764 of 2,764 values; the one FAIL was "fetch failed" on `/cost-of-power?view=grids` while three readers ran; alone, 40 of 40 |
| `check-existing-tab.mjs`, production against the build | 0 | every figure the same |
| em dashes in the changed files | 0 | none |
| the server stopped, the lock released | 0 | |

## The landing

Not in this session: 730 lands 719 to 730.

## Decisions made without you

1. **A wires utility with no sales row takes its counties' one grid** (the rule written in the list), since EIA-861's delivery-only rows carry no balancing authority: without it CenterPoint and Oncor could never match; with it only a utility whose counties all sit in one grid does.
2. **Every name EIA-861 gives a utility is a key** (its sales rows' names over the years and the territories' name), so a renamed utility ("Westar Energy", "Evergy Kansas South") matches under either name.
3. **The way is landed though it places nothing today**: the chain asks for it, the test proves the three ways, and the tracker's rows will carry EIA's names as they are curated.

## For Samuel's ruling

- Whether the tracker's curation should write utilities as EIA-861 names them (the exact-match rule needs "City of San Antonio - (TX)", not "CPS Energy"), or whether a written alias table (CPS Energy to City of San Antonio) belongs in the builder: an alias is a judgment, not a match, so it is not made here.

## Files

- Changed: `warehouse/derived/siting_page.py` (`UTILITY_NORM_RULES`, `norm_utility`, `utility_grids`, `--facilities`), `site/lib/siting.ts` (`normUtility`, `facilitySite`'s utility way), `site/app/datacenters/Body.tsx`, `site/app/datacenters/DatacentersTable.tsx` (the label), `site/data/siting/facilities.json` (the `utilities` part), `tests/test_session719.py` (the key set), `docs/reviews/siting-open-2026-10-23.md` (line 28).
- New: `tests/test_session729.py`, `docs/brand/review-729/`, this report.
- On this machine, not in git: `runs/archive_restore/datacenter_facilities.csv` (the held copy, counted only), `runs/chain_062/facilities_place_input.json` (its state, county and utility columns, for the count).
