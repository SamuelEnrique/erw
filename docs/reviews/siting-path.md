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

| # | Clicks, from the tab | The address | What the page showed | Answered? |
|---|---|---|---|---|
| 1 | "Your load": Size 1000, Show. "Sort and filter": Sort by the all-in figure, Order smallest first, Show | `?view=allgrids&mw=1000&sort=allin&dir=asc` | 14 rows have every cost part held, all ERCOT. ERCOT HB_WEST is cheapest at USD 40.83 per MWh all-in (33.01 energy, 7.83 four-peak charge, no capacity market) and LZ_CPS dearest at 46.69. Every other grid sorts last: transmission or capacity is not held, or held under a license. Sorted by energy instead, CAISO's SP15 is cheapest (28.94), then ZP26 (29.01) and SPP South (29.27) | **In part.** All-in can be compared only inside ERCOT; energy everywhere |
| 2 | "A and B, side by side": A ERCOT HB_WEST, B ERCOT LZ_NORTH, Show | `...&a=ercot%3AHB_WEST&b=ercot%3ALZ_NORTH` | The headline: "A datacenter load of 1,000 MW at ERCOT HB_WEST pays USD 40.83 per MWh all-in, USD 321,907,123 a year; generators there took a median of 45.80 months to connect." The panel: every column for both, B less A, the year (LZ_NORTH USD 340,205,905; +18,298,782) and the MWh (7,884,000 each) | **Yes**, for two ERCOT sites. A site outside ERCOT has no year all-in |
| 3 | Sort by months to connect, smallest first | `?view=allgrids&mw=1000&sort=connect&dir=asc` | ERCOT 45.8 months, MISO 58.4, PJM 71.3, SPP 84.6, NYISO 87.3, CAISO 100.0; ISO-NE not held. Under each, the grid's newest decided large-load rule, ERCOT's 8,927 MW approved to energize, and NYISO's measured waits ("license needed") | **In part.** A generator's wait is shown; a load's own wait only for NYISO, held |
| 4 | Sort by demand growth | `...&sort=headroom` | ERCOT +5.41 percent, SPP +5.25, PJM +4.12, CAISO +3.64, ISO-NE +2.90, MISO +2.80, NYISO +0.52; MW under construction due within twelve months (ERCOT 24,269); capacity over peak for NYISO (130 percent) and ISO-NE (134) | **Yes**, by grid; not by zone |
| 5 | Profile: Electrolyzer. Sort by carbon, smallest first | `...&profile=electrolyzer&sort=carbon&dir=asc` | Over the hours it runs (the cheapest 55 percent), CAISO's NP15 92.9 kg CO2 per MWh and ZP26 94.1, against the subregion's annual 194.3. PJM and MISO have no hourly figure (no price, so no hours run) | **Yes** |
| 6 | Profile: Flexible compute. Sort by the all-in figure | `...&profile=flexible&sort=allin&dir=asc` | At HB_WEST the four-peak charge falls to 0.00 (off in all four intervals of 2025) and the energy to 30.64. All-in USD 30.64 against 40.83 flat; the year USD 241,206,147 against 321,907,123 | **Yes**, in ERCOT. Elsewhere the peaks that set a transmission charge are not held |
| 7 | "ERCOT nodes (873)", click "Energy" twice (smallest first), click the first node | `...&rows=nodes&nsort=energy&ndir=asc`, then `&node=ercot%3ABBREEZE_1_2` | BBREEZE_1_2 (wind): energy 23.83, basis -10.47, all-in 31.66, 335 of 365 days; its panel the basis percentiles and months | **Yes** for price; its zone, utility and county are not held |
| 8 | Sort by the utility's industrial revenue per MWh | `...&sort=utility&dir=asc` | Each row's state's largest seller to industry inside the grid, its revenue per MWh and growth | **No, in part**: the state's largest seller is not the row's utility (the data machine's session 681: wrong in 4 of 7 hub counties). Session 718 reads the territories |
| 9 | `/internal/siting-gaps` | `/internal/siting-gaps` | 28 rows, each with its source, license and connector | **Yes** |
| 10 | Copy the address of step 2 into a new tab | the same address | The same screen: the box, the sort, A and B, the headline | **Yes** |

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

## Walked again (session 727, chain 062)

The ten steps again on production (`https://erw-flame.vercel.app`, chain 050's sessions 700 to 721 served whole since 14:56 UTC), 22 October 2026 at about 15:20 UTC, the same addresses at 1 GW. Shots: `docs/brand/review-727/` (`qNN_*_1280.png`).

| # | Then (717) | Now (727) | Changed by |
|---|---|---|---|
| 1 | HB_WEST cheapest all-in at 40.83 (14 rows held, all ERCOT), LZ_CPS dearest at 46.69 | The same | |
| 2 | The headline and the panel, HB_WEST against LZ_NORTH | The same headline (USD 40.83, USD 321,907,123 a year, 45.80 months) | |
| 3 | ERCOT 45.8 months, MISO 58.4, PJM 71.3, SPP 84.6, NYISO 87.3, CAISO 100.0; ISO-NE not held | The same months, now read from `interconnection_durations` | 718 |
| 4 | Demand growth by grid; capacity over peak for NYISO and ISO-NE only | Demand growth by grid; **capacity above the peak for every grid** (ERCOT 97 percent, CAISO 106, SPP 78, MISO 62, ISO-NE 37, NYISO 34, PJM 31). Rows inside a grid still tie (session 728) | 718 |
| 5 | CAISO NP15 92.9 kg over the electrolyzer's hours, annual 194.3 | The same | |
| 6 | HB_WEST flexible 30.64 against 40.83 flat | The same (off 14 hours; the four-peak charge 0.00 off at the peaks) | |
| 7 | BBREEZE_1_2 cheapest node, 23.83; its panel | The same. Session 724 adds the spread, the missing days, "Set as A", a filter and a download (on its branch, landing with 722 to 726) | 724 |
| 8 | The state's largest seller stood in for the row's utility, wrong in 4 of 7 hub counties | **A row named for a place takes its county's utilities** (Consolidated Edison for N.Y.C., Southern California Edison for SP15, CenterPoint named for Houston). Sorted smallest first, PJM's FirstEnergy Pennsylvania leads at 11.34, a delivery figure; session 726 names the kind in the cell (on its branch) | 718, 726 |
| 9 | 28 rows of gaps | 29 rows (Texas's wires utilities file no sales row, 718) | 718 |
| 10 | The same screen from the copied address | The same | |

No step that held at 717 fails now. The walk's open items stay those of the open-items file (`docs/reviews/siting-open-2026-10-23.md`, lines 7, 11, 15 and 16).
