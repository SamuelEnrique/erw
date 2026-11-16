# The datacenter power tracker, as a reader meets it (`/datacenters`)

Energy Research Warehouse (ERW), platform tool 4. Written by session 7401 (chain 303, 16 November 2026) as the one note for the tool: every view of the page, every figure's table and rule, and what the tracker does not hold. It points to the tables' own notes and does not repeat them:

- [`datacenter_facilities`](datacenter_facilities.md): the one table the facility views read, how its three kinds of source are joined, and every check key of the page.
- [`datacenter_projects`](datacenter_projects.md): the facilities the scored news names, and the checks each field passes.
- [`datacenter_operator_sites`](datacenter_operator_sites.md): nine operators' own site lists.
- [`datacenter_tracker_rollups`](datacenter_tracker_rollups.md): the rollups as a table of the warehouse.
- [`ercot_large_load_status`](ercot_large_load_status.md): what ERCOT's monthly report states in words.
- [`grid_peak_vs_capacity`](grid_peak_vs_capacity.md) and the queues' notes (`ercot_interconnection_queue` and the others).

Where this note and a table's note differ on a table's columns, the table's note governs; on what the page shows and how a figure is computed from the rows, this note governs.

The figures quoted here are of the live set's rows as read on 16 November 2026 at 09:18 UTC (458 rows, vintage 15 November), the day's `replication/datacenter_tracker/page_figures.json`. They move with the table every day.

## 1. The two views

| Address | What it draws | Read from |
|---|---|---|
| `/datacenters` | The top block (facilities held, megawatts stated, first reported this week), what changed this week, two bars (by state, by operator), ERCOT's large loads, the facilities beside ERCOT's figures, the list grouped by operator, the rollups by grid and by operator, the timeline, three charts, the power side (the queue sites and what a flat load paid), the downloads | `datacenter_facilities`; the site's copy of `ercot_large_load_status`; the queue tables; the cost-of-power calculator's price files |
| `/datacenters?view=grids` | The queue sites by grid and zone beside each grid's own queue, what a flat load paid by year, and the facilities against each grid's peak hour, capacity and reserve margin | the queue tables; the calculator's price files; `datacenter_facilities`; the site's copy of `grid_peak_vs_capacity` and of ERCOT's reserve margin |

The map's datacenter layer (`/map?layer=datacenters`) draws the placed facilities of the same table and is the map's, not this note's.

**The hold.** `datacenter_facilities` is held whole ("license needed") since 21 October 2026: most rows rest on news stories or on operators' own pages, whose terms ask for permission. Under the hold the page draws the hold's sentence where the facility figures would be, and draws ERCOT's section and the power side, which rest on public sources. Every rule below is what the page computes when the hold allows; the replication runs the page's own functions on the rows to say what that is.

## 2. What a facility is

- **One row is one facility**: a named site, or a named operator or developer at a stated place, from one of three kinds of source: scored news stories since 1 January 2025 (191 rows on 16 November), an operator's own public list (264), or an interconnection-queue position whose name or fuel field names a datacenter or a large load (3). `datacenter_facilities.md` gives the nine operators and the queue pattern.
- **Two rows are one facility** when they share an operator (after aliases) and a place: the same state and the same county or city, or within 25 km. An operator's separately listed sites are never merged with each other. A row with only a state is never merged.
- **A facility needs a stated place** (a site, a city, a county, a state or a country). Market commentary, a company-wide plan without a site and a description that is not a name are not facilities (`datacenter_projects.md`).
- **Not a census.** The news covers the stories the ERW scores; nine operators publish a list the ERW can read (QTS, CoreWeave and Crusoe do not); the queues hold few load rows, because they are queues of generation.

## 3. What a sum counts

- **Counted** (`datacenters|counted`): a facility in a named US state whose status is not withdrawn (the extractor's "cancelled"). A named US state is one of the 50 states, the District of Columbia or Puerto Rico. 274 of the 458 on 16 November.
- **Left out of every sum, kept in the list**: a facility with no US state stated (180: sites outside the US, and US sites whose story or page names no state, a cloud region's name among them) and a US facility that is cancelled (4).
- Every sum on the page is of counted facilities, except the sentence beside ERCOT's section, which says so: it counts every site held (`datacenters|sites_mw`), the cancelled and those with no state among them.

## 4. Megawatts

- **Only what a source states.** A news facility's MW is kept only where the exact words it was read from are in the story and parse to the same number (GW and MW applied); an operator's MW only with its span on the operator's page. A facility that states none is counted beside the sum and never added as zero: 21 of the 274 counted facilities state MW (28,254 MW); 253 state none.
- **What the MW measures** (`mw_basis`) is IT load, the facility's total, one tenant's share, a phase, or unstated. A sum adds MW of every basis, and the page says so beside it. Of the 58 rows that state MW on 16 November, 54 are unstated, 2 a tenant's share and 2 a total.
- **A range or a ceiling.** The table keeps one number and no range. Where the words give a ceiling ("up to 495 MW of power") the number kept is the ceiling; where they give two numbers the number kept is the one the extraction read, and the check asks only that it is one of the numbers in the quoted words. No midpoint is taken and no rule prefers the lower or the upper end. By a word search of the evidence sentences of the 55 news facilities that state MW (13 November's table, no model): 36 put no qualifying word before the figure, 8 put "to" before it (an expansion's target or a range's upper end), and for 11 the figure is in another sentence of the story than the one kept as evidence.
- **A queue position's MW** is the generation or storage it asks to connect, not the datacenter's load. It is shown on the power side under its own name and is never in a facility sum.
- **Who the megawatts belong to.** The views by operator read the operator a source names. On 16 November 26,124 of the 28,254 MW stated are of 13 facilities whose sources name no operator; for 9 of them (20,704 MW) the table states a developer, which the list shows in the facility's row and the views by operator do not read. Whether they should is open (section 13).
- **A few rows carry most of the megawatts.** Five facilities state 25,000 of the 28,254 MW: one of 10,400 MW (a utility's statement of a contracted load), one of 9,400 (the wrong join below), one of 3,000 (a proposal a state is weighing), one of 1,200 and one of 1,000. The megawatts stated are a sum of what the news stated, not a measure of what is being built.
- **One known wrong join** stays in the sums until the news table is rebuilt: a 2025 story of a Utah datacenter joined to a 2026 story of 9.4 GW on the word "Utah" alone (`datacenter_facilities.md`, "The news extractor's merge rule"). It is 9,400 MW of Utah's bar and of the megawatts stated.

## 5. Status, and what "operating" and "planned" mean

- **The vocabulary** is the entities standard's: `planned` (announced, applied or permitted), `under_construction`, `operating`, `withdrawn` (cancelled); a queue position carries its queue's own harmonized status (`active`, `completed`, `withdrawn`).
- **A status is kept only where a source states it**, with its words: a story's ("broke ground", "came online"), Oracle's "Live" or "Coming soon", Google's development flag. Every other operator's listed site carries none. So 301 of the 458 rows have no status, and "operating" (33 rows) is not a count of the datacenters running: most operators' listed sites are running and say nothing of it.
- **Megawatts by status** (`datacenters|status_mw|<status>`) are of the counted facilities that state MW, as the table has their status: planned 21,305 MW, no status 6,766, under construction 108, operating 75.
- **No history.** The table is rebuilt whole each day and keeps one row a facility as it stands: no earlier value, no date of a change.

## 6. The grid of a facility

- **The rule** (`grid`, with `grid_basis`): the grid operator a story names (`named`), else the ISO of the facility's queue position (`queue`), else the grid that serves most of its state (`state`). On 16 November: 175 by state, 3 by queue, none named.
- **The states read to a grid**: Texas to ERCOT; California to CAISO; New York to NYISO; the six New England states to ISO-NE; Pennsylvania, New Jersey, Maryland, Delaware, Virginia, West Virginia, Ohio and the District of Columbia to PJM; Minnesota, Iowa, Wisconsin, Michigan and Louisiana to MISO; Oklahoma, Kansas and Nebraska to SPP. A state split between grids, or outside every ISO, is given none: its facilities are in the group "no grid stated or read" (100 counted facilities, 14,842 MW).
- **A reading, not a fact of the story.** A Texas facility outside ERCOT's footprint is read as ERCOT's; the basis says `state`.
- The grid pages (`/grid/<slug>`) count the facilities of a grid by their own rule (`datacenter_facilities.md`, "Grid pages"), which reads a utility before a state.

## 7. Every figure, in the order the page shows it

Each figure carries a check key. `site/scripts/check-values.mjs` reads it on the built page; `replication/datacenter_tracker/replicate.py` recomputes it from the rows.

### 7.1 The top block (`site/lib/dctop.ts`)

| Figure | Key | Rule |
|---|---|---|
| Facilities held | `datacenters|count` | every row of the table |
| Counted, no US state stated, cancelled | `datacenters|counted`, `no_us_state`, `cancelled` | section 3; the three add up to the rows held |
| Megawatts stated | `datacenters|mw_total`, `n_with_mw` | the stated MW of the counted facilities, and how many state it |
| By status | `datacenters|status_mw|<status>` | section 5 |
| First reported this week | `datacenters|first_week|<day>` | every facility held whose first story is dated in the seven UTC days that end on the day the page is drawn (the key holds the first of them); a facility from an operator's list or a queue carries no date |
| Facilities with a first story | `datacenters|n_first_story` | 193 of 458 |
| Stated MW by state | `datacenters|state_mw|<state>` | counted facilities that state MW, by state |
| Top operators by MW | `datacenters|operator_mw|<operator>` | the same, by operator, the five largest; a tie by name |

### 7.2 ERCOT's large loads (`site/lib/largeload.ts`, section 8 below)

Each of the three figures of each report, by its series key `series|ercot_large_load_status|ercot:large_load|<variable>|<day>`; the share observed running (the newest report's observed non-simultaneous peak over its approved megawatts, to a whole percent: 44); the count and megawatts of new submissions where a report states them.

### 7.3 Beside ERCOT: the facilities the ERW holds

`datacenters|sites_us` (a named US state: 278), `sites_texas` (47), `sites_n_with_mw` and `sites_mw` (every site held that states MW: 58 and 41,922 MW, more than the megawatts stated at the top because the cancelled and the stateless are in it), `texas_n_with_mw` and `texas_mw` (4 and 457), `kind_count|<kind>` (by where each row came from).

### 7.4 The list

One row a facility, grouped by operator, the largest first by the megawatts the sums count. Each group's line shows `datacenters|operator_count|<operator>` (every row of the operator) and, where one of them states MW, `datacenters|operator_mw|<operator>`. The filters change what is listed and the downloaded rows, never a keyed figure.

### 7.5 The rollups by grid and by operator (`site/lib/dcrollups.ts`, `rollups`)

For each grid (section 6) and each operator with a counted facility: the counted facilities `datacenters|rollup_facilities|<grid|operator>|<value>`, the MW they state `rollup_mw` (no key where none states MW: the cell says "none stated"), how many state it `rollup_with_mw` and how many state none `rollup_without`. The group with no grid is keyed `-`.

### 7.6 The timeline (`timeline`, `timelineCells`)

Every facility held that states both the date of its first story and the year it is to be energized (`energized_year`, else the older `planned_year`): 9 on 16 November. The wait is the second year less the first story's year, in whole years. By grid and by the year first reported: `dctime|count|<grid|year>|<value>` and, from three facilities, the median `dctime|median`. A facility with one of the two dates is not on it.

### 7.7 The three charts (`dcFigures`)

1. `dcchart|planned|<quarter>|<grid>`: the MW of counted facilities that are planned or under construction, by the quarter of the first story and the grid (the four grids with the most such MW, the rest as `other`); `|without` counts the quarter's facilities that state none.
2. `dcchart|operator|<name>|mw`: the ten named operators with the most MW stated.
3. `dcchart|power|<kind>|facilities` and `|pct`: the counted facilities by the kind of power their sources state (`power_kind`; `none` where no source states it: 260 of 274), and each kind's share to a tenth of a percent.

### 7.8 The power side and the view by grid

- **The queue sites**: the positions of the queues that are not held whose name or fuel field matches the pattern (2, both ERCOT's, on 16 November; the queues of NYISO, MISO and ISO-NE are held and not read). Each shows the MW it asks to connect, `entity|<grid>_interconnection_queue|<id>|capacity_mw`.
- **By grid and zone** (`site/lib/datacenter/bygrid.ts`): `dcq|<grid>|<zone>|sites`, `sites_with_mw`, `mw_asked` (the MW those positions ask to connect: 191.26), `active_positions` and `active_mw` (the grid's whole queue whose status is active, where the queue names no zone: 1,159 positions and 308,488 MW in ERCOT's).
- **What a flat load paid** (`dcpow|<grid>|<region>|per` and `|year|<YYYY>`): at each load zone of a grid with a site, the mean of the hourly prices held over the last twelve consecutive complete months (a month is complete when 95 percent of its hours hold a price; months are counted in the grid's standard time), in real time where twelve such months are held, else day-ahead; and the same for each complete calendar year, at most the last eight. Energy only. These are the cost-of-power calculator's figures for a flat load (`datacenter_pays_algorithm.md`).
- **The facilities against each grid** (`gridLoads`, `shareOfPeak`): for each of the seven grids, the counted facilities read to it `dcgrid|facilities|<grid>`, those stating MW `with_mw`, their MW that is `planned`, `under_construction` and `operating`; beside the grid's peak hour `peak_mw` and its operating generators' net summer capacity `capacity_mw` (the site's copy of `grid_peak_vs_capacity`: EIA-930 and EIA-860M); the planned and under-construction MW as a share of the peak hour to a tenth of a percent `share_of_peak`; and ERCOT's planning reserve margin `reserve_margin` (its Capacity, Demand and Reserves report). The share is what the facilities state, not what they will draw.

## 8. How ERCOT's section is built

ERCOT's Large Load Integration team reports the queue of large loads to its committees each month as slides. The ERW reads only the three figures every report states in words (the megawatts approved to energize, and the observed peak of those loads, each load's own and all together), dates each by the day on the report's first page, and reads nothing off a chart, so the load requested by status is not here. The reports cover every large load of 75 MW or more that asks to connect, not only datacenters. The newest report held is of 19 June 2026 (8,927 MW approved, 3,900 observed, 3,675 at one moment): on 3 August 2026 ERCOT paused approvals to energize datacenters and crypto facilities of 75 MW or more, and no status update since states the figures. ERCOT's megawatts and the tracker's facilities are two sources and are never added. Rules, the two reports that contradict themselves, and the license: `ercot_large_load_status.md`.

## 9. What the tracker does not hold

- A facility no source the ERW reads names; a facility's load beyond the MW a source states (most state none); whether a stated MW is IT load or the facility's total, where the words do not say.
- An earlier value of any field, or the date a status or a size changed.
- A facility's point of interconnection, its utility where its county is served by several, or a load zone for a Texas county.
- Load requested from any grid operator but ERCOT, and ERCOT's own split of its queue by status or by type.
- A country, except "US" where a US state is stated.
- A count of the datacenters running in the United States, or of their demand: see the cross-checks for what published counts and demand figures are against these.

## 10. The replication

`replication/datacenter_tracker/` (session 7400):

- `fetch_rows.py` reads the rows from the live set into `rows/`, which git ignores: no row of the held table is committed with the replication.
- `replicate.py` computes every keyed figure of both views from the rows by the rules of this note, in its own Python, and sets each beside what the page's own functions give on the same rows (`site/scripts/datacenter-tracker-figures.mjs`). On 16 November 2026: **454 of 454 inside the tolerance** (half the last digit the page shows). `page_figures.json` and `page_figures.csv` hold both sides.
- `replicate.do` reproduces the tool's five headline figures in Stata from the CSV `fetch_rows.py` writes; the expected values are at its top.
- Not replicated: the words of the list (each facility's own row), which are the table's rows themselves.

## 11. The cross-checks

`docs/methods/crosschecks/datacenter_tracker.md`: the tracker's totals beside Lawrence Berkeley National Laboratory's report on datacenter energy use, the EIA's figures, ERCOT's own large-load totals, the grid operators' load forecasts and the largest utilities' stated megawatts, each with its publisher, document and date, and why the two differ. No figure of the tracker is adjusted to match one.

## 12. The decisions on the page

The page lists, at its foot, the choices that move its figures, each with its default and its source on hover (`site/lib/decisions.ts`, `DATACENTER_TRACKER_DECISIONS`, drawn by `site/components/tool/DecisionsBlock.tsx`). The list below is the same list, word for word; `tests/test_session7402_trackers.py` holds the two equal.

1. A sum counts a facility in a named US state whose status is not withdrawn; every other facility stays in the list and is in no sum. **Default:** The 50 states, the District of Columbia and Puerto Rico; a facility with no US state stated is left out, whether it is abroad or a US site whose source names no state. **Source:** No source the ERW reads records a country, so the state is the only test (docs/methods/datacenter_facilities.md, "Country, and what the tracker's totals count"). (session 166)
2. Megawatts are only what a source states in words; a facility that states none is counted beside the sum, never added as zero and never estimated. **Default:** No estimate: most facilities state no MW, and the count that state it is printed beside every sum. **Source:** Session 16's ruling: nothing inferred beyond the stated words; each number is kept only where its quoted words are in the story or on the operator's page. (sessions 16 and 22)
3. A sum adds megawatts of every basis: IT load, a facility's total, one tenant's share, a phase, or a figure whose basis the words do not say. **Default:** One sum, with each row's basis shown in the list; most stated MW have no basis stated. **Source:** The basis is read from the story's own words (mw_basis, docs/methods/datacenter_projects.md); no public source gives a rule to convert one basis to another. (session 2236)
4. Where the words give a range or a ceiling, the table keeps one number, the one read from the quoted words ("up to 495 MW" is 495); no midpoint is taken and no range is kept. **Default:** The number as read; no rule prefers the lower or the upper end. **Source:** The check of every number: it must be one of the numbers in the quoted words (warehouse/deals/extract.py, verified). (sessions 15 and 22)
5. An interconnection-queue position's megawatts are the generation or storage it asks to connect, not a datacenter's load: they are shown on the power side and are in no facility sum. **Default:** Never summed with the facilities. **Source:** The grid operators' queues are queues of generation (docs/methods/datacenter_facilities.md, "Queue rows"). (session 22)
6. A status is kept only where a source states it: planned is announced, applied or permitted; operating only where a story or the operator's page says so. Most operators' listed sites carry none, so the megawatts by status are not a measure of what is running. **Default:** No status is given to a facility whose sources state none. **Source:** Session 17's ruling: a status without its words is left empty; the entities vocabulary of docs/datastandard.md. (sessions 16, 17 and 166)
7. A facility's grid is the grid operator a story names, else its queue position's, else the grid that serves most of its state; a state split between grids is given none. **Default:** Texas to ERCOT, California to CAISO, New York to NYISO, New England to ISO-NE, eight jurisdictions to PJM, five states to MISO, three to SPP; every other state to no grid. **Source:** A reading of the state, not a fact of the story; the basis is shown a row (grid_basis: named, queue or state). (sessions 2236 and 2243)
8. Two rows are one facility when they share an operator and a place: the same state and the same county or city, or within 25 km. An operator's separately listed sites are never merged. **Default:** 25 km; a row with only a state is never merged. **Source:** docs/methods/datacenter_facilities.md, "Deduplication". (session 22)
9. The views by operator read the operator a source names; a facility whose sources name only a developer is in "operator not stated", which holds most of the megawatts stated. **Default:** The operator alone; the developer is shown in the facility's own row. **Source:** The warehouse's own rollup table reads the operator, else the developer (docs/methods/datacenter_tracker_rollups.md); whether the page should is the owner's to rule. (session 240)
10. ERCOT's large loads are the figures its monthly report states in words, dated by the report's first page; nothing is read off a chart, and ERCOT's megawatts are never added to the facilities'. **Default:** Three figures a report: approved to energize, observed (each load's own peak), observed together. **Source:** ERCOT, Large Load Interconnection Status Update, 28 May 2025 to 19 June 2026 (docs/methods/ercot_large_load_status.md). (session 106)
11. The wait from first reported to energized is the difference of two stated years, only where a facility states both; a median needs three such facilities. **Default:** Whole years; no wait is estimated from one date. **Source:** The first story's date and the year a story says the facility is to be energized or come online (energized_year, else the older planned_year). (sessions 2245 and 1855)
12. From 21 October 2026 the facilities are held whole for a license; the page draws the hold's sentence where they would be, and the queue sites, ERCOT's section and the prices, which rest on public sources. **Default:** Held whole; no row is shown. **Source:** warehouse/metadata/license_status.csv: the news outlets' and the operators' terms ask for permission. (sessions 215 and 467; the owner's ruling of 12 October 2026)

## 13. What waits for the owner

Four rows of the faults read of 11 November (`docs/reviews/datacenter-faults-2026-11-11.md`) are the owner's. In plain words, each with the default the page stands on:

1. **Whether the facilities stay held whole** (row 1). Today no reader sees any of the 458 facilities. The other choice: show the rows whose every source is public, with a license shown a row. Default: held whole.
2. **Whether each grid's peak hour and capacity show while the facilities are held** (row 4). They come from EIA's public data and are hidden only because their keys sit with the held table's. Default: hidden, with the hold's footnote.
3. **Whether the map may draw the facilities the tracker holds** (row 7). The map serves the placed rows of the same table to every reader's browser. Default: the map is unchanged; one of the two is wrong until this is ruled.
4. **Whether every figure of the site shows its source on hover** (row 11). Today a figure carries its key, and its source is a line under the table. Default: unchanged, since the change reaches every page.

One more was found by the work of 16 November (row 17 of the same file):

5. **Whether the views by operator read the developer where no operator is named.** The warehouse's own rollup table does; the page reads the operator alone, so "operator not stated" holds most of the megawatts stated. Default: the operator alone, said in the decisions.

## Sign-off

Signing this note accepts, as the tool's rules:

- what a facility is and when two rows are one (section 2);
- what a sum counts: a named US state, not cancelled (section 3);
- megawatts only as stated, never estimated, a sum of every basis, one number where the words give a range (section 4);
- a status only where a source states it, so "operating" is not a count of the datacenters running (section 5);
- the grid of a facility: named, else its queue's, else the grid that serves most of its state (section 6);
- ERCOT's large loads as its reports state them in words, never added to the facilities (section 8);
- the decisions of section 12, the list the page shows at its foot.

It leaves open the five items of section 13.

- Signed off by:
- Date:
- Items of section 13 ruled, and how:
