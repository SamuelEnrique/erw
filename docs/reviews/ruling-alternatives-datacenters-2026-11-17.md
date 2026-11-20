# Ruling alternatives: /datacenters, the datacenter tracker (17 November 2026)

Session 7628 (portable-laptop, code role). The seven lines of `docs/reviews/ruling-impact-datacenters-2026-11-17.md`. Two are built, each on its own branch from origin/main with a test that pins it, in order of size of change; five are not, each said below. **No branch asks to land; no default on main changed; no hold lifted.** Model spend USD 0.

`datacenter_facilities` is held whole ("license needed", since 21 October): the tracker draws the hold and no facility, in the internal view too. Only counts and sums are written here, never a facility's name, operator or own figure.

- **Build:** the worktree `erw-alt` (2,852 and 3,057 MB free before the two builds), served on port 3320 with the repository's `.env` and no model key, read with the internal cookie at 1280 px. The counting script, counts only: `runs/c7628_dc_counts.mjs`.

| # | Line | Branch | Figure before (origin/main) | Figure after (the other choice) | Files touched | Test | Screenshot |
|---|---|---|---|---|---|---|---|
| 4 | May the project map's datacenter layer keep sending the placed facilities' names, operators and MW while the tracker shows none | `wip/alt-datacenters-1` (`6047bef9a`) | `/map?kind=datacenter`: 278 datacenters with names, operators and MW, 28,254.0 MW stated in every sum and tip | **"The map holds 278 datacenters, no MW stated"**: each point keeps its place, state, grid and status, and loses its name, operator, MW (-28,254.0, -100 percent) and the card's city, developer, power, utility and sources. The 35,035 points and every other kind's figure stay | `site/lib/projectmap.ts`, `site/app/map/page.tsx`, `site/app/map/card/route.ts`, `tests/test_session7628_alt_map_datacenters_held.py` | On `map.json` (built 16 November 2026): 35,035 points, 278 datacenters, 28,254.0 MW to 0, no name, operator or detail left, places and other kinds unchanged; both readers of the file use it | `docs/reviews/ruling-alternatives/datacenters-1-map-layer-held-1280.png` |
| 2 | The views by operator count a facility under its developer where no operator is named ("operator or developer") | `wip/alt-datacenters-2` (`0f4b6f18e`) | "Operator not stated": 13 facilities stating MW, 26,124 MW (92.5 percent of the MW stated) | **4 facilities stating MW, 5,420 MW (-20,704, -79.3 percent)**; the facilities counted (274) and the MW of all lines (28,254) do not move; the developers' lines enter the rollup (not named here: held). Behind the hold: the page draws none of these views | `site/lib/dcrollups.ts`, `tests/test_session7628_alt_dc_operator_or_developer.py` | Through the page's rollup on the repository's copy (458 rows): 274 counted, 28,254 MW, operator not stated 4, 5,420 and 11 counted | `docs/reviews/ruling-alternatives/datacenters-2-operator-or-developer-held-1280.png` (the hold) |

- `wip/alt-datacenters-2` leaves `tests/test_session2246_deals.py` (`test_the_stored_facilities_trace`) failing: it holds the operator-alone rollup as origin/main computes it (it passes there), a pin the ruling would move.

## Lines not built

- **Line 3, each grid's peak hour and capacity on the by-grid view while the facilities are held: already so on origin/main.** `/datacenters?view=grids`, "The facilities against each grid", draws all 14 cells (ERCOT 83,597 and 164,685 MW; PJM 160,560 and 210,667; MISO 120,343 and 195,473; SPP 54,411 and 96,914; CAISO 43,860 and 90,303; NYISO 31,857 and 42,787; ISO-NE 25,898 and 35,400) beside the hold's cells, read on this session's build. The rulings line describes an older page.
- **Line 1, the public rows shown:** the hold stands (the owner's rules of 16 November 2026, rule 5).
- **Line 5, Dominion's 4,800 MW beside Virginia, and line 6, a line under the headline naming the two largest rows' share:** each would add one figure to a view the hold does not draw (the by-state view and the headline), so no reader would see it; and line 6's share (70.1 percent) is a figure of the held rows. Not built while the hold stands.
- **Line 7, PJM's two figures in the cross-check note:** a note, not a page cell; no figure on a page moves.

## Decisions made without you

- **Line 4 as bare points, not as no layer:** the form that keeps the map's count of points and every place a reader can see, and holds what the tracker holds (names, operators, MW). The other form (no layer: 31,073 points) is one line in `heldDatacenters`. The /map tool's own ruling line, which holds the queue layer as well, is that tool's item.
