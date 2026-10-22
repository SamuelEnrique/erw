# A utility planner's path through the All grids tab, walked (22 October 2026)

Energy Research Warehouse (ERW), session 725 of chain 062, on samueloldlaptop. The walk ran on production (`https://erw-flame.vercel.app`, chain 050 served whole) in the internal view, on 22 October 2026 at about 15:15 UTC. The load is 1 GW unless a step says otherwise. Screenshots are in `docs/brand/review-725/`. The page's text at each step stayed on this machine (`runs/chain_062/walk725/`), since it carries figures waiting on a ruling. Nothing was fixed here; session 726 fixes what lies in the chain's files.

## The questions

A planner at a utility, or at a state commission, asks where large loads are going and what they would ask of the grid:

1. **Who serves each place, and what does industry pay there?**
2. **Is demand growing where the loads go, and is generation coming?**
3. **How long does a connection take, and under what rule?**
4. **Where are the large loads: the tracker's facilities on the tab?**
5. **Two places side by side, as a planner compares service areas.**
6. **A heavy industry load, as a planner's own customers are.**

## The walk, step by step

| # | The address (after `/cost-of-power?view=allgrids&mw=1000`) | What the page showed | Answered? |
|---|---|---|---|
| 1 | `&sort=utility&dir=desc` (u01) | Each row's utility, its industrial revenue per MWh and its sales growth. Highest: PG&E at CAISO's NP15 and ZP26, USD 325.37 per MWh (-8.61 percent); then Southern California Edison at SP15, 204.28; Consolidated Edison at N.Y.C., 128.79 | **In part**: see steps 2 and 3 |
| 2 | The same, PJM's row | **FirstEnergy Pennsylvania Electric Co, USD 11.34 per MWh.** It is a delivery-only figure: the utility bills the wires, and the energy is bought from a retail seller. The tip says so, but the cell does not. The sort sets this wires revenue beside bundled prices (PG&E's 325.37 includes the energy), so the order mixes three kinds of figure: bundled, delivery only and energy only | **No.** The order misleads without the tip |
| 3 | The same, ISO-NE's zones and MISO's ILLINOIS.HUB | **Direct Energy Business**, an energy-only retail seller, stands as "the utility" for .Z.SEMASS, .Z.WCMASS and the other Massachusetts zones and for Illinois. It is the state's largest seller to industry, but a planner asks for the wires utility (Eversource, National Grid, ComEd, Ameren) | **No.** The figure is right for what it says, but it is not the utility a planner means |
| 4 | `&sort=utility&grid=ercot` (u02) | ERCOT's 17 rows: TXU Energy Retail (an energy-only seller) for most; LZ_HOUSTON and HB_HOUSTON list CenterPoint and price San Bernard Electric Coop (session 718) | **In part**: chain 050's ruling item 18 (Texas's wires utilities) |
| 5 | `&sort=headroom&dir=desc` (u03) | ERCOT's 17 rows all +5.41 percent, 24,269 MW coming, capacity 97 percent above peak: the grid's figures, so the rows inside a grid tie | **In part**: a zone's own growth is session 728's |
| 6 | `&sort=connect&dir=asc` (u04) | ERCOT 45.80 months (rule 2026-09, 8,927 MW approved to energize), MISO 58.40, PJM 71.30, SPP 84.60, NYISO 87.30, CAISO 100.00; ISO-NE not held. A grid's figure again | **In part**: a generator's wait, by grid; a load's own wait outside NYISO is not held (gap 8 of the open items) |
| 7 | `/datacenters` (u07) and `?view=grids` (u08) | **No facility shows**: `datacenter_facilities` is held whole since 21 October, so session 719's links are not drawn. The "By grid" view draws ERCOT's zone prices by year, and ERCOT's large-load approvals (8,927 MW approved, 3,900 MW running) | **No** while the hold stands |
| 8 | `&sort=utility&a=ercot%3ALZ_HOUSTON&b=pjm%3Agrid` (u05) | The panel: Houston's utility 89.39 against PJM's 11.34, "B less A -78.05". The difference compares a coop's bundled industrial price with a wires utility's delivery revenue | **No**, for the utility line (as step 2) |
| 9 | `&sort=utility&kind=zone` (u06) | 27 of 48 rows, load zones only | **Yes** |
| 10 | `&mw=300&profile=industry&sort=allin&dir=asc` (u09) | ERCOT HB_WEST 40.83 all-in, as for a datacenter: heavy industry runs every hour, and "interruptible" moves capacity only (chain 050's decision 702) | **Yes**, with the decision in the tip |
| 11 | The utility sort at 390 (u10) | The box folds; the table scrolls inside its frame; no sideways scroll of the page | **Yes** |
| 12 | `/internal/siting-gaps` (u11) | 29 rows: the gaps a planner would fill (large-load tariffs, load queues, settlement points) | **Yes** |

## What session 726 fixes (inside the chain's files)

1. **The utility cell names the figure's kind**: "delivery only" or "energy only" beside the revenue per MWh (bundled says nothing). The sort's line says that the column mixes the three kinds and how to read them (steps 2, 3 and 8).
2. **The A and B panel's utility line** shows each side's kind, and draws no "B less A" when the two kinds differ (step 8).

Left as found, for the owner:

- **Which utility a row names** where the largest seller to industry is an energy-only retailer (step 3). Naming the wires utility instead changes the figure from a retail price to a delivery revenue: a ruling beside chain 050's item 18. Listed in 726's report.
- Headroom and time to connect by zone (steps 5 and 6): session 728 (zone growth) and the gaps file (a load's own wait).
- The tracker's facilities (step 7): the hold.

## After session 726

On a local build of `wip/726-allgrids` (shots: `docs/brand/review-726/`):

| # | Before (725) | After (726) |
|---|---|---|
| 2 | PJM's USD 11.34 sorted beside bundled prices, its kind in the tip only | "11.34 delivery only" in the cell; N.Y.C.'s "128.79 delivery only"; an energy-only seller's figure reads "energy only"; bundled says nothing. The sort's line, when sorted by the utility, says the column mixes three kinds and how to read them |
| 8 | "B less A -78.05" between a coop's bundled price and a wires utility's delivery revenue | Each side names its kind ("11.34 delivery only"), and "B less A" reads "not alike", its tip naming both kinds (`after_u05_ab_not_alike_1280.png`) |

Step 3 (a retailer named as the utility) waits on the owner's ruling (725's report).

## Walked again (session 758, chain 063)

The twelve steps again on production, 22 October 2026 at about 19:25 UTC, with one step for the zone lines (728). Shots: `docs/brand/review-758/`.

| # | Then (725) | Now (758) |
|---|---|---|
| 1, 2 | The Utility column mixed bundled, delivery-only and energy-only figures, unsaid | Each figure names its kind ("11.34 delivery only", "118.36 energy only"); the sort's line says the column mixes three kinds and how to read them |
| 3 | A retailer named as the utility (ISO-NE's Massachusetts zones, MISO's Illinois) | As left: rulings item 13, not ruled |
| 4 | Texas's wires utilities not priced | As left: rulings item 12, not ruled |
| 5 | Rows inside a grid tie on headroom | NYISO's and ISO-NE's zones show their own growth under the grid's ("zone -6.70 % in 2025" at NORTH); ERCOT's and CAISO's rows keep the grid's |
| 6 | Time to connect by grid | As left (a load's own wait is a gap) |
| 7 | The tracker shows no facility | As left: `datacenter_facilities` is held whole |
| 8 | "B less A -78.05" across kinds | "not alike", each side's kind named |
| 9 to 12 | Zones only; heavy industry; 390; the gaps | The same |

No step fails that held before, and no new fault was found.
