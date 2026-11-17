# The All grids tab read as the reader it is for (chain 302, goal 4, session 7203, 16 November 2026)

Energy Research Warehouse (ERW). Five real cases, each read on the tab (`/cost-of-power?view=allgrids`) as the energy lead of an AI lab would read it, then on the page's default view ("Your load", `/cost-of-power`). For each: can the reader get the cost of power, the time to connect, the headroom, the carbon, the utility and its rule, without leaving the tab and without a figure that contradicts another page?

**How it was read.** This machine had no memory for a site build on the day (2.0 GB free; a build needs 2.5 GB). The tab was drawn to HTML with the site's own components and files (`site/scripts/tsx-loader.mjs`) and read cell by cell with every hover; "Your load" was read through its own model (`site/app/cost-of-power/model.ts`) on the same files. No click was made and no chart was seen. A fault that only a browser shows (a hover cut by a frame, a layout at 390 px) is not in this list.

## The cases, in one line each

| Case | On the tab | The rule |
|---|---|---|
| 1 GW in ERCOT West | two rows (the West load zone, the West hub): every column but the zone's own headroom | the state's rule from both cells; Oncor's and AEP Texas's through "11 in TX" |
| 500 MW in Dominion's Virginia | no row of its own: PJM is one row with no price | one click from the PJM row: 8 rules in Virginia, 3 of them Dominion's |
| 300 MW in Arizona (APS) | no row: Arizona is in no ISO | in the table only: APS's revision is proposed and prints none of the eight fields |
| 1 GW in Ohio (AEP) | no row of its own: the PJM row | one click from the PJM row: 4 rules in Ohio, AEP Ohio's approved, its queue figure held |
| 500 MW in Georgia (Georgia Power) | no row | in the table only: in effect, five of the eight fields printed |

## The rows

Kind: `site` (fixed here, with a test), `data machine` (a row of `docs/state/data_requests_large_load.md`), `license` or `ruling` (written with the default taken).

| # | Case | The cell or click | What the reader meets | Kind | State |
|---:|---|---|---|---|---|
| 1 | 1 | "A and B, side by side", Energy, B less A | 37.21 and 33.21 are drawn and B less A reads -3.99: a cent from the difference of the two figures | site | fixed: the note under the panel says each figure is rounded after the difference is taken. The arithmetic is unchanged (the page's rule elsewhere) |
| 2 | 1 | All-in, at 1,000 MW | USD 45.03 per MWh and USD 355 million a year are the market's prices as they were. A load of a gigawatt would move the West zone's prices; nothing said so | site | fixed: the all-in hover says the load's own effect on prices is not modelled, with the load's size |
| 3 | 1 | Energy, the main figure | The figure names no market in place (day-ahead, on hover only). "Your load" opens on real time: the same zone reads 37.21 on the tab and 35.35 there | site | fixed: the cell reads "da 37.21 rt 35.35". Market by market the two pages agree to the last digit (four figures, held by the test) |
| 4 | 1 | Utility, the West zone and the West hub | TXU Energy Retail, the state's largest seller: a retailer, not the wires utility a load in West Texas meets (Oncor, AEP Texas, Texas-New Mexico Power). No table gives a zone's wires utilities | data machine | requested (row 20). Until then the cell opens the state's rule and counts the 11 rules read in Texas; fixed (`8aa576aa5`, large-load request 20: done (session 7009, chain 301)) (marked by session 7052, chain 370) |
| 5 | 1 | Headroom, "2030 peak forecast +0.4 MW since the 2024 filing" | A revision of 0.4 MW (0.0 percent) to ERCOT's 2030 summer peak between two yearly filings, in the same cell as a firm peak of 98,135 MW for summer 2027 from ERCOT's own report. Either the two filings carry one forecast or a row is wrong | data machine | requested (row 21); answered (`8aa576aa5`, large-load request 21: answered (session 7009)) (marked by session 7052, chain 370) |
| 6 | 1 | Time to connect, "8,927 MW approved" | ERCOT's large-load report of 19 June 2026: five months old on the day of the read. The hover gives the date; whether a later report exists is not known here | data machine | requested (row 22); answered (`8aa576aa5`, large-load request 22: answered (session 7009)) (marked by session 7052, chain 370) |
| 7 | 1 | Transmission and 4CP, against "Your load"'s delivery table | The tab draws USD 7.83 per MWh (the Commission's rate for every wires utility together, 2025). "Your load" draws Oncor's own transmission lines for the same load: USD 8.58. Two readings of one charge, neither naming the other | site | fixed: the hover names each utility's own lines (Oncor 8.58, CenterPoint 6.92, AEP Texas 8.16, Texas-New Mexico Power 7.06) and says which the figure is. Which one the all-in should count is row 16 |
| 8 | 1 | Headroom | Every figure is ERCOT's: the West zone's own demand growth, its reserve and the limits on power into West Texas are not held | data machine | known (`docs/reviews/siting-gaps.md`, "Headroom"); not asked again |
| 9 | 2, 4 | The PJM row: Energy, Transmission, Capacity, All-in | "license needed" and "not held": no PJM price may be republished by a non-member | license | default: stays as drawn. A license from PJM would open its hubs and zones (Dominion's and AEP's among them) |
| 10 | 2, 4 | The PJM row, Utility | The cell named Allegheny County's utilities with the hover "a county this row's name places it in". The row's name is the grid. Its rule line read "no large-load rule found, 1 in PA" to a reader looking for Virginia or Ohio | site | fixed: the hover says the county is the ERW's choice for the grid's one row; both cells open "22 large-load rules in PJM", and the panel counts them by state, each a link to the table filtered (Virginia 8, Ohio 4) |
| 11 | 2, 4 | The PJM row, Utility, the figure | FirstEnergy Pennsylvania's delivery revenue (USD 11.34 per MWh, delivery only) stands as PJM's utility figure and sorts the row | data machine | requested (row 23): drop the county for the grid's row, or draw PJM's zones as rows without a price, each with its utility; fixed (`fb4dc8ccc`, large-load request 23: done (session 7009, chain 301)) (marked by session 7052, chain 370) |
| 12 | 2, 4 | Carbon, the hover | "The the plants eGRID places in PJM" | site | fixed |
| 13 | 2, 4, 5 | A rule in full | Dominion's GS-5, AEP Ohio's Schedule DCT and Georgia Power's rules print terms (minimums, years, collateral), not rates: no USD per kW is a field, and the registry of filed schedules holds no rate for the three | data machine | requested (row 24); answered in part (`74e701fc8`, large-load request 24: in part (session 7009, chain 301)) (marked by session 7052, chain 370) |
| 14 | 3 | No row for Arizona | The tab's rows are the seven grids' hubs and zones. For APS: no cost, no time to connect, no headroom, no carbon | data machine | requested (row 25): rows for balancing authorities outside the seven grids, from tables the warehouse holds; fixed (`39963e3e9`, large-load request 25: done for the data side (session 7009, chain 301)) (marked by session 7052, chain 370) |
| 15 | 5 | No row for Georgia | The same, for Georgia Power (Southern Company's balancing authority) | data machine | row 25; fixed (`39963e3e9`, large-load request 25: done for the data side (session 7009, chain 301)) (marked by session 7052, chain 370) |
| 16 | 1 | All-in, the transmission part | Whether the all-in figure of a Texas row should count the Commission's rate (as now) or the row's wires utility's own lines where the utility is known | ruling | default: the Commission's rate, as "Your load"'s four-peak block does |
| 17 | all | The SPP North hub, Utility | "no large-load rule read, 3 in KS": the hub's county utility is Evergy Kansas South, and Evergy's Kansas rule names Evergy Kansas Central and Evergy Metro | ruling | default: not matched (no guess); one line in the builder joins them |

## The same five cases on "Your load"

- **ERCOT West.** "Your load" for `grid=ercot&region=LZ_WEST` and for `HB_WEST`, bought day-ahead and in real time: the flat load's price over the same twelve months equals the tab's cell in each of the four (37.21 and 35.35; 33.21 and 31.04), held by `site/scripts/test-allgrids-read.mjs`. The one trap was row 3. Its delivery table is row 7.
- **PJM (Virginia, Ohio).** "Your load" holds no PJM: an address that names it shows ERCOT and says so ('Grid: "pjm" is not held here, so ERCOT is shown.'). The same gap as row 9, said in the same way on both views. Its "Rules in motion" does open PJM's proceedings.
- **Arizona, Georgia.** Not held by "Your load" either: rows 14 and 15.
- **Not compared here.** "Your load"'s four-peak block and its three answers read the live set, which this worktree does not reach. The value checker holds each to its own source after a build.

## What a lab's reader still cannot get from the tab, and why

- **A price anywhere in PJM,** where Virginia and Ohio are: PJM's terms close its prices to a non-member. A license, not work, closes it.
- **A row outside the seven grids** (Arizona, Georgia, the Carolinas, Tennessee, the Northwest): the tab was built on the hubs the page prices. The demand, carbon, utility and queue tables for those balancing authorities are in the warehouse; the rows are not built (row 25).
- **A utility's own rate for a large load.** The rules print what a customer must sign, not what a megawatt-hour costs; the registry of filed schedules holds rates for 6 utilities, none of the five cases' (row 24).
- **A load's own wait.** "Time to connect" is the median of generators that came online; the rules' timed steps are the documents' words, not measured waits; the measured large-load waits are held under a license, and most utilities publish none.
- **Headroom at the site.** Every headroom figure is the grid's. A zone's or a substation's room for a gigawatt is in no public table the ERW holds.
