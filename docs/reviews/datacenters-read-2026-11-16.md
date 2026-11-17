# The datacenter power tracker (`/datacenters`) read as its reader, 16 November 2026

Energy Research Warehouse (ERW). Session 7603, chain 305 (part C), the portable laptop, 17 November 2026. The page as built from origin/main of that morning (with the session 7602 fixes, none of which touch it), served here and read in a browser at 1280 and 390 px in the internal view; every figure below is as the page drew it. The tool's note is `docs/methods/datacenter_tracker.md`; its signature pack `docs/reviews/trackers-signature-pack-2026-11-16.md`.

## The reader and the five cases

The reader: **a fund analyst sizing datacenter load in one utility's or one grid's territory**, before an investment committee, who wants each figure's source and will set it beside the utility's own statements.

1. **ERCOT, the load approved and running:** how much large load ERCOT has approved to energize and how much it has seen running, at the newest report.
2. **Abilene, Texas:** the Stargate campus (Crusoe and Oracle for OpenAI), said in the press to be about 1.2 GW: is it on the tracker, with what MW and which grid?
3. **Dominion Energy Virginia's territory (Loudoun County, PJM):** the facilities and the MW they state, against PJM's peak hour and capacity.
4. **A flat 300 MW load in ERCOT's West load zone:** what it paid for energy over the last twelve months and in 2025, and whether the cost-of-power page says the same.
5. **Giga Texas (Travis County):** the queue position 25INR0688 that names it: what it asks to connect, where, in which load zone.

## What the reader got

| Case | Answer on the page | Without leaving it? | Agrees with the other pages? |
|---:|---|---|---|
| 1 | "By ERCOT's report of 19 June 2026, 8,927 MW of large load had its approval to energize, and ERCOT had observed 3,900 MW of it running (44 percent)"; 3,675 MW at one moment; the twelve reports from 28 May 2025; why there is none since (ERCOT's pause of 3 August 2026, its words to TAC of 26 August) | yes | yes: the All grids tab's large-load cells read "8,927 MW approved" |
| 2 | Nothing: "All 458 rows of datacenter_facilities are held from 2026-10-21" (license needed). Abilene is not among the two public queue sites | no (row 3) | **no**: the project map draws the same table's facilities, "278 datacenters, 28,254 MW stated at 21 of them" (row 4) |
| 3 | The facilities: held. PJM's row of "The facilities against each grid" printed "license needed" in every cell, PJM's own peak hour and capacity among them (row 1, fixed: now drawn from `grid_peak_vs_capacity`); its reserve margin "not held" (NERC's terms not read) | in part | the peak and capacity are the same table the All grids tab reads |
| 4 | "West load zone, real time, Nov 2025 to Oct 2026, 34.07 ... 35.35" in the table of load zones; 2025's dearest zone USD 42.18 in the chart by year | yes | yes: `/cost-of-power?grid=ercot&region=LZ_WEST&mw=300` reads "USD 35.35 per MWh over the last twelve months, USD 92.9 million in all" and "2025: 42.18" |
| 5 | "Giga Texas Data Center, Giga Texas Energy, LLC, ERCOT, Travis, TX, 25INR0688: Completed, 133 MW asked to connect, HORNSBY Substation, load zone not stated by the queue, 2024-08-27; proposed 2027-08-13"; the line that a position's MW is the generation or storage it asks to connect, not the site's load | yes, but not its load zone (row 5) | the map's card reads the same position |

## The rows

| # | Case | The cell or click | What the reader meets | Kind | State |
|---:|---|---|---|---|---|
| 1 | 3 | `?view=grids`, "The facilities against each grid": the columns "Peak hour MW", "Capacity MW" and "Reserve margin" | Every cell "license needed", the grid's own figures too, though the component's rule (`FacilitiesVsGrid.tsx`) is that a grid's public figures stay. `heldBy` (`site/components/Num.tsx`) read the key's first word `dcgrid` as `datacenter_facilities`, held whole; the peak and capacity are `grid_peak_vs_capacity`'s and the margin `ercot_cdr_reserve_margins`', both public | site | fixed (`Num.tsx` and its mirror `site/scripts/check-holds.mjs` ask the two tables; `tests/test_session7603_datacenters_read.py`); read again: ERCOT and PJM's peak and capacity drawn, the facilities' columns still held |
| 2 | 1 | ERCOT's table of reports, the column "The month as ERCOT wrote it" | Beside the report of 24 April 2026: "March 2026 (as written; the report is of 2026)", where the year agrees and the month does not: the note said nothing of what differs | site | fixed (`site/lib/largeload.ts`, `reportMonth`; `LargeLoad.tsx`): "(as written; the report is of April 2026)" |
| 3 | 2, 3 | The facilities: list, rollups, timeline, charts, the facilities' columns by grid | Held whole since 21 October 2026: the rows rest on news stories and operators' own pages, whose terms ask for permission | license | only a license or a recorded permission closes it; the method note counts which rows rest on a public source |
| 4 | 2 | `/map?kind=datacenter` beside this page | The map draws 278 placed facilities of the same table ("28,254 MW stated at 21 of them") while this page holds every row: two pages disagree on what may be shown | ruling | row 7 of `docs/reviews/datacenter-faults-2026-11-11.md`, open; default: unchanged (session 7601 raised it again for the map) |
| 5 | 5 | The queue sites' "Load zone" | "not stated by the queue": a fund analyst would place Travis County in Austin Energy's load zone. ERCOT publishes its load zones only as a picture of a map, with no list of counties, and the page says so | ruling | default: not placed. An option: a county list of ERCOT's zones from a public source, if one is found |
| 6 | 3 | "Reserve margin" for PJM, MISO, SPP, CAISO, NYISO, ISO-NE | "not held": NERC's assessments are not read while NERC's terms are not | license | as row 3: unchanged |
| 7 | all | At 390 px | The page 390 px wide with every fold open; 24 marks, each box inside the screen | none | seen |

## Two pages that share a figure

- ERCOT's 8,927 MW approved: this page and the All grids tab, the same.
- A flat load at ERCOT's West zone, USD 35.35 per MWh (Nov 2025 to Oct 2026) and 2025's USD 42.18: this page and `/cost-of-power`, the same.
- The datacenters: this page holds them, the map draws them (row 4).

## Needs the key

- Nothing.
