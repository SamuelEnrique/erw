# Session 1027 report: ERCOT's reserve margins

23 October 2026, from about 07:00 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-1022` on `wip/1027-allgrids` (cut from `wip/1026-allgrids`). Chain `queue/done/071-night-23-october-code-allgrids-packages.md`, session 1027. Model spend USD 0. No warehouse data written; no request to a publisher. The reads: the ERW's own archive bucket (one table rebuilt into `runs/archive_restore/`), the live set with the anon key (one request), a local build of this branch.

## Read these first

- **ERCOT's planning reserve margin is in the All grids tab**, under the Headroom column's capacity line: "reserve margin 11.4%, summer 2027" on every ERCOT row, keyed `allgrids|reservemargin|<row>`. From `ercot_cdr_reserve_margins` (public; ERCOT's Capacity, Demand and Reserves report posted 19 December 2025): the first summer after the tab file's build day, at the report's peak load hour (hour ending 17), total capacity 109,350 MW over firm peak load 98,135 MW. The tip adds the peak net load hour (10.5%) and the report's first season below zero (spring 2028, -4.9%), and says it is a forecast.
- **The other grids read "reserve margin not held"**, with the reason on hover: no report of their own is held.
- **Open items line 20 is closed for ERCOT** (the other grids wait on the data machine's chain 049, session 895, EIA's margins by NERC assessment area; chain 072's session 1047 wires them).
- **The live set does not hold the table yet**: one request for its summer rows returned none (it is in `live_set.yaml`; the loader runs with the data machine's daily run). So the replication reads the figure from the table's CSV (`--tables`) until then, and from the live set after.

## What to review

1. `docs/brand/review-1027/after_reserve_1280.png` and `after_reserve_390.png`: three CAISO rows (not held) and six ERCOT hubs.
2. `/cost-of-power?view=allgrids&mw=1000`, the Headroom column, an ERCOT row's third line and its tip.
3. `docs/methods/siting.md`, decision 29.

## What was done

- **The builder** (`warehouse/derived/siting_page.py`): `reserve_margins(path, today)` writes `headroom.json`'s `reserve` (the table, the build day, the report, its vintage; ERCOT's first summer after the day at the peak load and peak net load hours, with total capacity and firm peak load; the first season below zero at the peak load hour). Optional like the zones: a machine without the table writes no margin.
- **The file**: only `headroom.json`'s new `reserve` key was written here, by the builder's function on the table rebuilt from the archive (`warehouse/archive/restore.py --from-bucket ercot_cdr_reserve_margins`, 1,600 rows, as of the 01:40:50 UTC run); the file's other keys are as built before (the other tables were not rebuilt for this session). Test 706's rebuild comparison sets the new key aside, as it does the zones.
- **The page**: `reserveMargin()` in `lib/siting.ts`, the check key's resolver, the Headroom column's tables and tip (`ercot_cdr_reserve_margins` added, so the download's header names it); the line in `HeadroomTd`; `tokens.css` sets its words in sans and its figure in mono, as the lines above it (the first build showed the whole line in mono; fixed and rebuilt).
- **The replication**: `reserve_figures()` for the hub table's ERCOT row, from the live set and, with `--tables`, from the table's CSV.
- **Test 1027**: the builder on a three-season file (the first summer after the day, the first season below zero); the tab's file (a summer after the build day, ERCOT's definition holds: capacity less firm peak over firm peak); the cell, the key and the column; the replication's choice of summer.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| tests 1027, 1020, 746, 728, 706, 718 | 0 | 18 tests OK (706 failed first on the new key; fixed) |
| `db_probe` before each build | 0 | 0.63 s |
| build of the branch (lock `s1027`), twice | 0 | no "statement timeout" |
| the page at 1280 and 390 | 0 | 48 cells, 14 keyed (the ERCOT rows), raw 11.428383 = the table's; width 390 at 390 |

The full replication was not run (about 32 live set requests, and the live set does not hold the table yet); session 1029's walk or the landing's checks read the key.

## The landing

The landing gate's check-values (07:29 UTC) failed that line: it showed one decimal where every checked figure shows two. It now reads "reserve margin 11.43%, summer 2027", the same figure (11.428383).


Sessions 1020 to 1039 landed in one push: see `SESSION_1039_REPORT.md`, "The landing".

## Decisions made without you

1. **Summer, the first after the build day, at the peak load hour** (decision 29 in the method note).
2. **"Reserve margin not held" on every row of the other grids**, as the chain's file asks; about 30 more short tips on the hub table's page.
3. **Only the new key of `headroom.json` was written**, not a full rebuild of the tab's files on this machine.
4. **The negative figure in the tip is written with a hyphen-minus** (-4.9%), as the tab writes its other negatives.

## For Samuel's ruling

- None new.

## Files

- Changed: `warehouse/derived/siting_page.py`, `warehouse/replication/siting.py`, `site/lib/siting.ts`, `site/app/cost-of-power/AllGridsView.tsx`, `site/app/tokens.css`, `site/data/siting/headroom.json`, `docs/methods/siting.md`, `tests/test_session706.py`.
- New: `tests/test_session1027.py`, `docs/brand/review-1027/` (two shots), this report.
