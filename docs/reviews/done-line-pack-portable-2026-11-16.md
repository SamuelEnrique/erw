# The portable laptop's pack, chain 305 (16 and 17 November 2026)

Energy Research Warehouse (ERW). Session 7607, chain 305's last session, portable-laptop. One sitting for Samuel: the one tool this chain took to the done line (`/map`), what the browser reads found on the old laptop's pages, the four tools read as their readers, and every ruling with the default taken. Model spend of the whole chain: USD 0.

Tools 11 to 16 of the claims file (`/events`, `/grid/caiso/alerts`, `/learn/bill`, `/learn/problems`, `/play/battery`, `/play/ev`) were moved to the old laptop by your instruction of 16 November and are in its pack, `docs/reviews/done-line-pack-oldlaptop-2026-11-16.md`, section "The second run".

## 1. The project map, `/map` (signable)

**What you sign:** that the Projects tab's figures are EIA's own inventory read as the note says (`docs/methods/map.md`), that the replication reproduces them (`replication/map/`), and that the cross-check against EIA's Electric Power Monthly is fair. Landed at `492752123` (portable landing row 37).

**The five choices that move its figures most**

| Choice | Default | Source |
|---|---|---|
| What a unit's megawatts are | Nameplate capacity | EIA, Form EIA-860M, "Nameplate Capacity (MW)"; net summer capacity is 7.5 percent lower over the operating units of 2026-09 |
| Megawatts across kinds | Never added: each kind (operating, planned, queue position, datacenter) has its own count and sum | A queue position is a request, mostly withdrawn before it is built (`energy_projects.md`) |
| Which queue positions are drawn | Not withdrawn (active, suspended, completed, not stated) | Version 1 of the map (session 16) |
| Which queues are drawn | ERCOT, SPP, CAISO, ISO-NE | Each operator's terms: MISO's pulls paused, NYISO's notice confers no license |
| A unit's grid | EIA's balancing authority code; none is "Outside the seven ISOs" | EIA, Form EIA-860M |

**The cross-check, in one table** (EIA, Electric Power Monthly, Table 6.1, end of August 2026, against the map's operating units of the September inventory, net summer)

| What | The map's units | EIA's table | Difference | Why |
|---|---:|---:|---:|---|
| 18 of 27 technologies (nuclear 98,423.3; coal steam 167,235.5; gas combined cycle 295,138.4; hydro 80,046.2 among them) | same | same | 0.0 | the same inventory |
| Solar photovoltaic | 169,644.1 | 166,677.0 | +2,967.1 (1.78%) | one month of new units |
| Batteries | 55,707.8 | 54,097.0 | +1,610.8 (2.98%) | one month of new units |
| Every technology | 1,324,124.6 | 1,318,801.0 | +5,323.6 (0.40%) | one month of change |
| The map's own measure, nameplate | 1,423,491.7 | | | nameplate against net summer: 7.5 percent |

**Stata** (from `replication/map/`, after `python fetch_rows.py --units-only`): `do replicate.do` should print, on EIA's inventory of September 2026: operating units 28,712; their nameplate 1,423,491.7 MW; planned units 2,361; their nameplate 290,264.2 MW; batteries operating and planned 1,640. Not run here (no Stata on this machine); `python replicate.py --headline` prints the same five lines. After a new month, compare with the Python, not with these.

**The rulings, each with its default**

1. The map draws 3,709 queue positions and 278 datacenters from tables its own last line calls "held: license needed" (row 7 of the datacenter faults of 11 November, open, and the same for ISO-NE's 415 positions). Default: nothing changed. The datacenter tracker holds the same facilities whole (this pack, section 3).
2. No A and B on the map (two states or two grids side by side). Default: not built.

## 2. The old laptop's pages, read in a browser (part A)

The old laptop cannot build the site; every change it made that needed a browser was a row of `docs/state/browser_reads_wanted.md`. This chain read all 278 rows (sessions 7600 to 7602): rows 1 to 31 on 16 November, rows 32 to 278 on 17 November, on builds of its branches at 1280 and 390 px.

- **Rows 32 to 278: 119 seen, 4 seen in part, 7 with a fault.** Six fixed with tests on `wip/7602-landed-reads` (landing row 38): a hover box taller than its room is widened (rows 52, 62); a one-point chart's axis ran to 1.8 for a share (63); the event pages' table of each event day pushed a phone sideways (80, 82, on production too); `/supply`'s grid links line had no place to break (179, on production too). One for the data machine: the battery page's awards comparison stops at July while the awards page counts eight months (55, request 261).
- Index and pictures: `docs/reviews/browser-reads-2026-11-16/` and its README's sections (section 6).

## 3. Four tools read as their readers (part C)

On `wip/7603-datacenters-read` (landing row 39), each read with five real cases of a named reader:

| Tool | Reader | Rows | Fixed | Rulings and other |
|---|---|---:|---|---|
| `/datacenters` | a fund analyst sizing datacenter load in one territory | 7 | a grid's public peak, capacity and reserve margin printed as held; the note beside a report's month | 2 license, 2 rulings |
| `/deals` | an AI lab's infrastructure lead | 5 | (every view held, 583 rows) | 1 license |
| `/research` | a fund analyst reading the week's findings | 8 | **two cards drew NYISO's and ISO-NE's held prices** (on main too; found by `check-holds.mjs`; now taken out on the server); the page at 712 px on a phone; the record's figures in the scanner's words; tables held whole offered as public | 2 requests (262, 263), 1 key, 1 ruling |
| `/grid` | a utility market analyst on ERCOT | 5 | none needed; every shared figure agrees | 1 ruling, 1 key |

## 4. Every ruling of this chain, in plain words, with the default taken

1. **A long hover box on a phone** still scrolls inside itself: there is no width to give. Default: left so.
2. **A box opened in a table's frame on a phone** has the frame's scroll indicator across one of its lines for about a second. Default: left so.
3. **"(session 83)" in grey** beside each line of the decisions blocks of `/contracts` and the five tools, against the rule of no grey text. Default: nothing changed.
4. **The hub table's rule lines are 24 px high** (they were 18), as axe's target size asks. Default: 24 px.
5. **The impact page's chart cards** say "2027 build: Property 0 USD (2025)" where its read's row 6 wanted "none" and "not held" told apart. Default: unchanged.
6. **The map against the hold**, and **no A and B on the map** (section 1).
7. **A Texas queue site's load zone** is not placed (ERCOT publishes its zones as a picture). Default: not placed.
8. **ERCOT's own peak record** is not set beside EIA-930's 91,075 MW on `/grid`. Default: unchanged; the option is a line with ERCOT's release.
9. **`/grid`'s second line** lists 24 tables and their licenses before any figure. Default: left.
10. **The weekly note's line on how it was written** ("model ..., literal-number check passed, USD 0.0090"). Default: left.

## 5. What needs the key (no model was called)

| What | Estimate |
|---|---:|
| `/research`, "Ask the warehouse", one request | about USD 0.05 |
| `/grid`, "Ask ERCOT about this view", one question | about USD 0.02 |

Neither was measured; both are estimates from the weekly note's own cost.

## 6. The pictures

- `docs/reviews/browser-reads-2026-11-16/` (part A: 48 pictures on main, 175 more on `wip/7602-landed-reads` until it lands) and `docs/reviews/map-done-line/` (the map's browser read, 18 pictures). Part C asks for no pictures; its reads' screenshots stay in this machine's build folder.
