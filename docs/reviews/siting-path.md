# A lab's path through the All grids tab, walked (22 October 2026)

Energy Research Warehouse (ERW), session 717 of chain 050, on samueloldlaptop, on a local production build of `wip/717-allgrids` (sessions 700 to 717) in the internal view, 22 October 2026 at about 11:50 UTC. The walk sets a load of **1 GW** (1,000 MW), the size the research report has the labs committing.

The page: `/cost-of-power?view=allgrids`. Every input is in the address, so each step below is an address and the clicks that make it. Screenshots: `docs/brand/review-717/` (1280 by 900; one at 390 by 844).

## The questions

Each is a question an infrastructure lead at an AI lab asks when siting a gigawatt. They are drawn from the research report Samuel kept on 21 October 2026 (`docs/reviews/research/deep-research-report.md`, cited by its section), and from the chain prompt's own order of what makes the tab worth a lab's time.

1. **What will a gigawatt pay per MWh, grid by grid, and where is it cheapest?** The report: "Projected cost to power 1 MW of new AI compute in [State X]" ("First LinkedIn posts", item 4); "model power cost differences ... across regions" (the second long-form piece).
2. **What does that come to in a year, all-in, against a second site?** The report: the "Power, Costs, and Siting" piece, "showing optimal sites for given compute power".
3. **How long until it connects, and what rule governs a large load there?** The report: "factor in interconnection queue wait times" (the same piece); Anthropic's CEO on misjudging "energy growth/timing" ("Roles", Anthropic).
4. **Is the power there: is demand growing, and is generation coming?** The report: OpenAI's "electron gap" ("Roles", OpenAI); "identifies key gaps/risks for AI load" (the first long-form piece).
5. **How clean is the power where it runs, and over the hours it runs?** The report: "consider carbon intensity" (the second long-form piece).
6. **What does flexibility buy: a load that curtails at the peaks?** The report: OpenAI's Camellia campus "has a 25-year contract to provide 1 GW of flexible demand response" ("Roles", OpenAI); "Flexible AI Loads and the Grid" (the third long-form piece).
7. **Where inside ERCOT exactly: which node, and what is its basis to the hub?** The chain prompt: the ERCOT node set, "firm against curtailing", comes first.
8. **Who is the utility, and what does it charge industry?**
9. **What does the warehouse not know, and where would it come from?**
10. **Can I send the screen to a colleague?** The report: a hub that "others can cite" ("On the data warehouse's role").

## The walk, step by step

| # | Clicks, from the tab | The address | What the page showed | Answered?  Now (session 727, a build of `wip/727-allgrids`) |
|---|---|---|---|---|---|
| 1 | "Your load": Size 1000, Show. "Sort and filter": Sort by the all-in figure, Order smallest first, Show | `?view=allgrids&mw=1000&sort=allin&dir=asc` | 14 rows have every cost part held, all ERCOT. ERCOT HB_WEST is cheapest at USD 40.83 per MWh all-in (33.01 energy, 7.83 four-peak charge, no capacity market) and LZ_CPS dearest at 46.69. Every other grid sorts last: transmission or capacity is not held, or held under a license. Sorted by energy instead, CAISO's SP15 is cheapest (28.94), then ZP26 (29.01) and SPP South (29.27) | **In part.** All-in can be compared only inside ERCOT; energy everywhere | **The same figures**: HB_WEST 40.83 (33.01 energy, 7.83 four-peak), then HB_HUBAVG 42.13, HB_BUSAVG 42.22, HB_NORTH 42.26, LZ_SOUTH 42.27; by energy SP15 28.94, ZP26 29.01, SPP South 29.27. Still in part: all-in inside ERCOT only (gaps 1 and 2 of 713; sessions 730 and 741) |
| 2 | "A and B, side by side": A ERCOT HB_WEST, B ERCOT LZ_NORTH, Show | `...&a=ercot%3AHB_WEST&b=ercot%3ALZ_NORTH` | The headline: "A datacenter load of 1,000 MW at ERCOT HB_WEST pays USD 40.83 per MWh all-in, USD 321,907,123 a year; generators there took a median of 45.80 months to connect." The panel: every column for both, B less A, the year (LZ_NORTH USD 340,205,905; +18,298,782) and the MWh (7,884,000 each) | **Yes**, for two ERCOT sites. A site outside ERCOT has no year all-in | **The same**: USD 40.83, 321,907,123 a year; LZ_NORTH +18,298,782; 7,884,000 MWh each. Since 726 the panel's Utility row says both sides are the state's stand-in (TXU, bundled) |
| 3 | Sort by months to connect, smallest first | `?view=allgrids&mw=1000&sort=connect&dir=asc` | ERCOT 45.8 months, MISO 58.4, PJM 71.3, SPP 84.6, NYISO 87.3, CAISO 100.0; ISO-NE not held. Under each, the grid's newest decided large-load rule, ERCOT's 8,927 MW approved to energize, and NYISO's measured waits ("license needed") | **In part.** A generator's wait is shown; a load's own wait only for NYISO, held | **The same months**: ERCOT 45.80, MISO 58.4, PJM 71.3, SPP 84.6, NYISO 87.3, CAISO 100.0; since 718 from `interconnection_durations`; ERCOT's "8,927 MW approved"; since 726 a "document" link beside each rule |
| 4 | Sort by demand growth | `...&sort=headroom` | ERCOT +5.41 percent, SPP +5.25, PJM +4.12, CAISO +3.64, ISO-NE +2.90, MISO +2.80, NYISO +0.52; MW under construction due within twelve months (ERCOT 24,269); capacity over peak for NYISO (130 percent) and ISO-NE (134) | **Yes**, by grid; not by zone | **Demand growth the same** (ERCOT +5.41, SPP +5.25, PJM +4.12, CAISO +3.64, ISO-NE +2.90, MISO +2.80, NYISO +0.52) and 24,269 MW coming in ERCOT; **capacity above the peak is now drawn for every grid** by 718's `grid_peak_vs_capacity` as percent above the peak (ERCOT 97, CAISO 106, SPP 78, NYISO 34, ISO-NE 37, PJM 31), where 717 saw "percent of the peak" for NYISO (130) and ISO-NE (134) only. Not by zone (728) |
| 5 | Profile: Electrolyzer. Sort by carbon, smallest first | `...&profile=electrolyzer&sort=carbon&dir=asc` | Over the hours it runs (the cheapest 55 percent), CAISO's NP15 92.9 kg CO2 per MWh and ZP26 94.1, against the subregion's annual 194.3. PJM and MISO have no hourly figure (no price, so no hours run) | **Yes** | **The same**: NP15 92.90, ZP26 94.13, SP15 94.93 over the hours it runs, against 194.35 annual; 3,940 hours off |
| 6 | Profile: Flexible compute. Sort by the all-in figure | `...&profile=flexible&sort=allin&dir=asc` | At HB_WEST the four-peak charge falls to 0.00 (off in all four intervals of 2025) and the energy to 30.64. All-in USD 30.64 against 40.83 flat; the year USD 241,206,147 against 321,907,123 | **Yes**, in ERCOT. Elsewhere the peaks that set a transmission charge are not held | **The same**: HB_WEST 30.64 all-in (four-peak 0.00, off 14 hours), USD 241,206,147 against 321,907,123; the firm charge beside it reads 7.84 (over the 8,746 hours it runs) |
| 7 | "ERCOT nodes (873)", click "Energy" twice (smallest first), click the first node | `...&rows=nodes&nsort=energy&ndir=asc`, then `&node=ercot%3ABBREEZE_1_2` | BBREEZE_1_2 (wind): energy 23.83, basis -10.47, all-in 31.66, 335 of 365 days; its panel the basis percentiles and months | **Yes** for price; its zone, utility and county are not held | **The same**: BBREEZE_1_2 23.83, basis -10.47, all-in 31.66, 335 of 365 days, its panel's percentiles -23.83, -6.02, 3.28. **New since 724**: the Basis spread column (27.12 for BBREEZE_1_2) and the panel's "Set as A" and "Set as B"; its zone, utility and county still not held (733) |
| 8 | Sort by the utility's industrial revenue per MWh | `...&sort=utility&dir=asc` | Each row's state's largest seller to industry inside the grid, its revenue per MWh and growth | **No, in part**: the state's largest seller is not the row's utility (the data machine's session 681: wrong in 4 of 7 hub counties). Session 718 reads the territories | **Changed by 718 and 726**: 18 rows whose name is a place take their county's largest seller inside the grid (SP15 Los Angeles County 204.28, N.Y.C. New York County 128.79 delivery only, Houston Harris County 89.39); PJM, placed in Allegheny County, now has a utility (11.34, delivery only) where 717 saw "not held"; the rest are the state's stand-in. Since 726 each figure says its basis under it, and the sort line says what the column compares. Sorted smallest first, PJM's wires charge comes first: a delivery-only figure beside bundled ones, said so |
| 9 | `/internal/siting-gaps` | `/internal/siting-gaps` | 28 rows, each with its source, license and connector | **Yes** | **30 rows** (28 then): 718 filled two rows in part and 724 added real time at the nodes |
| 10 | Copy the address of step 2 into a new tab | the same address | The same screen: the box, the sort, A and B, the headline | **Yes** | **The same** |

## What broke, and what was mended (no ruling needed)

1. **The sorted column was off the screen.** On a laptop, sorting by all-in, carbon or utility ordered the rows by a figure drawn to the right of the table's frame. Now the sorted column is drawn first, beside the rows' names, and the others keep their order. Shots: `q1_allin_cheapest.png` before, `q1_allin_cheapest_after.png` after.
2. **The line of shared figures above the node list fell apart.** It drew the table's own cells, each a block. It is now one sentence, each figure with its key and tip (`q7_nodes_cheapest.png`, `..._after.png`).
3. **The node list's header kept a cardinal band**, which the brand forbids (section 5). It is now captions grey with a dark rule under it, and the node list's figures are mono (`app/tokens.css`).

Each fix was checked: check-values 2,487 of 2,487 on every `/cost-of-power` address of the build, and the existing tab 0 differences from production.

## What is left, listed

- **All-in outside ERCOT** (steps 1, 2, 6): it waits for the large-load tariffs and the capacity prices' permissions. These are the first two of session 713's five gaps.
- **A load's own wait** (step 3): only NYISO's is measured, and it is held.
- **Demand by zone** (step 4): `eia930_subba_demand_hourly` is held but not in the tab's files.
- **The node's place and utility** (step 7): ERCOT's settlement point mapping and resource registration.
- **The row's own utility** (step 8): session 718 wires in the territories the data machine now holds.
- **The page's weight** (every step): the hub table's page is 1.73 MB (session 716).

## Walked again, 22 October 2026 (session 727 of chain 062)

Session 727 walked the ten steps again, and two more, on a local production build of `wip/727-allgrids` (chain 050's 718 to 721 and chain 062's 722 to 726 in place; production still served `e39de81a`, sessions 700 to 718, because the landing of 719 onward waits for the no-landing window to pass) served on port 3727, in the internal view, at 1280 and 390: `docs/brand/review-727/walk-727.mjs` (28 of 28 made, no page error, no page wider than 390). Its shots and records are in `docs/brand/review-727/`. The "Now" column of the table above sets each step's result beside 717's.

- **No step fails.** Every figure of steps 1 to 7 and 10 is as on 22 October at 11:50 UTC; the changes are chain 050's and this chain's own: 718's capacity above the peak for every grid and the 18 rows' county utilities (steps 4 and 8), 724's spread column and panel links (step 7), 726's basis words and document links (steps 3 and 8), two more gaps rows (step 9).
- **Step 11, 719's tracker link** (`/datacenters`): the facilities are held whole (`datacenter_facilities`, license needed since 21 October), so the page shows "license needed" and no link; 0 `data-facility-siting`. The link draws once rows show (719's report; the open-items table, lines 27 and 28).
- **Step 12, 720's card** (`/research/card/siting_gigawatt`): "WHERE A GIGAWATT PAYS LEAST": ERCOT HB_WEST 40.83 and LZ_CPS 46.69 per MWh (USD 321,907,123 and 368,100,514 a year), months to connect ERCOT 45.80 and CAISO 100.00: the tab's figures of step 1, as 720 wrote them.
- **What is left** is unchanged: all-in outside ERCOT (730, 741), a load's own wait, demand by zone (728), the node's place (733), the page's weight (737).
