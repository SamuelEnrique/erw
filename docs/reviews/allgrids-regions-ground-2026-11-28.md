# The ground of "Where the next gigawatts can go": the All grids tab as it stands, what is reused, and five cases

Energy Research Warehouse (ERW). Chain 780 (`queue/done/780-night-28-november-portable-allgrids-regions-browser-read.md`, part A, step 1), session 11600, the portable laptop, 28 November 2026. Written before the section was built, from a read of the code with no build; the section is on `wip/c780-allgrids-regions`.

## The tab as it stands (`/cost-of-power?view=allgrids`)

`site/app/cost-of-power/page.tsx` draws `<AllGridsView q={q} />` when the address says `view=allgrids`; `q` is every name of the address that came once. The tab is a grid of two columns: the input box at the left, the results at the right, and one part under both.

| # | Part | Drawn by | Reads |
|---|---|---|---|
| 1 | The box "Your load": the profile, the size, the load factor, the strike; folds "Sort and filter" and "A and B, side by side" | `AllGridsForm.tsx` | the address (`lib/siting.ts`, `sitingInputs`) |
| 2 | The count of rows and the load in a sentence | `AllGridsView.tsx` | `site/data/datacenter/index.json`, `site/data/siting/nodes.json` |
| 3 | The switch "Hubs and zones" and "ERCOT nodes" | `AllGridsView.tsx` | the address |
| 4 | The headline for A | `AllGridsView.tsx` | the page's price files (`site/data/datacenter/<grid>_<year>.json`) |
| 5 | "A and B, side by side": every cost part, B less A | `AllGridsView.tsx` | the same files; `site/data/siting/*.json` |
| 6 | The line that says the sort | `AllGridsView.tsx` | the address |
| 7 | The hub table's CSV | `AllGridsDownload.tsx` | the rows shown |
| 8 | The hub table: a row a hub or zone, eight columns (energy, transmission, capacity, time to connect, demand growth, carbon, utility rate, all-in); or the ERCOT nodes | `AllGridsView.tsx`, `AllGridsNodes.tsx` | `site/data/siting/capacity.json`, `connect.json`, `headroom.json`, `carbon.json`, `utility.json`, `tariffs.json`, `conn_rules.json`, `ercot_4cp.json`, `nodes.json` |
| 9 | The method line | `AllGridsView.tsx` | |
| 10 | "Large-load rules by utility": the counts, a rule opened, the rules' table, the 90 days of changes | `LargeLoadSection.tsx`, `LargeLoadRules.tsx` | `site/data/siting/large_load_rules.json` |

Nothing of the tab reads Supabase. Its figures carry keys `allgrids|...` and `largeload|...`, which `site/scripts/check-values.mjs` works out again from the same files on its two addresses of the tab.

**Names the address already uses** (a new part must take none of them): `profile`, `mw`, `lf`, `strike`, `rows`, `sort`, `dir`, `grid`, `kind`, `lo`, `hi`, `held`, `a`, `b`; `node`, `nq`, `ncls`, `ncounty`, `nzone`, `nsort`, `ndir`; `llrow`, `rstate`, `rgrid`, `rstatus`, `rq`, `rsort`, `rdir`, `ra`, `rb`, `rule`, `rregion`. The section's own begin with `sr`.

**Tests a new part could trip:** `tests/test_session714.py` (the tab's file holds one titled box), `test_session717.py` (two `cols.map(`), `test_session774.py` (every `allgrids|` key has its branch in the check), `test_session716.py` (no Supabase read), `test_session715.py` (no colour written by hand), `test_session700.py` and `test_session7201_large_load_on_site.py` (lines of `page.tsx` and of the tab that stand). So the section is a file of its own, mounted by one line.

**What chain 750 left on this tab** (`docs/reviews/browser-read-2026-11-26.md`): row CP2, the box "Your load" does not follow the back button (filed for the desk and the old laptop); the line for Samuel's ruling that the tab has more than 500 keyboard stops before its foot. Neither is this section's; the section adds stops of its own and counts them in its build read.

## What the site already has, and what it has not

| Needed | Reused | Where |
|---|---|---|
| A hover a keyboard reaches | `Tip` | `site/components/largeload/parts.tsx` |
| A count held for a license: blank, "license needed" on hover | `Blank` | the same file |
| A hover placed against the window (so none is cut at 390 px) | `TipPlace`, for anything under `[data-llr]` | `site/components/largeload/TipPlace.tsx`, mounted once in the layout |
| A figure with its key | `Num` | `site/components/Num.tsx` |
| A key into a page file, and the reader of one | `pfKey`, `readPageFile` | `site/lib/pagefile.ts` (the check works a `pf|` key out with no rule of its own) |
| Whether the site holds a table for a license | `licenseHeldRow`, `licenseByGrid`, `licenseByRow` | `site/lib/license.ts` |
| A small trend | `InlineSpark` | `site/components/InlineSpark.tsx` (the tab's own twelve months use it) |
| A download made in the browser | `Download` | `site/components/largeload/Download.tsx` |
| A link that keeps the release gate | `SiteLink` | `site/components/SiteLink.tsx` |
| A section's frame under both columns | the large-load section's own classes | `LargeLoadSection.tsx` |

**Not on the site, so not reused:** a shared table that sorts (the hub table sorts on the server from the address, the nodes and the rules each in the browser, each in its own file); a control that chooses columns (the battery tool's "Picks" is private to its file); a map of the thirteen regions (the Grid tool's map draws authorities and is loaded only in the browser). The section sorts on the server from the address, as the hub table does, so a link carries a choice and the back button undoes it. It draws no map: none exists to reuse, and the contract carries no shape of a place. **The carbon scale the Grid tool draws is not exported** (`app/network/Network.tsx`), so the section draws no colour at all.

## What the contract gives, and what it does not (`docs/state/page_files_siting_regions.md`)

- `index.json`: the places (13 regions, 7 market operators, each large balancing authority), the ten sections and their counts. `table.json`: one value a place for 25 columns. `<id>.json`: a place's own counts and lists (hubs, top constraints, the queue by fuel, the large-load rules, the mix, three partners, the datacenters).
- A count is a cell: the figure, its unit, its period, its source key and, when not shown, its reason beginning with one of six kinds.
- **Asked of the desktop** (`docs/state/data_requests_done_line.md`): row 584, the contract calls `datacenter_facilities` and `datacenter_projects` public and the site holds both for a license; row 585, a count's small trend (the contract gives one series only, carbon by hour of day) and the address of a figure's source.

## Five cases, written before the section was built

1. **An AI lab's siting analyst choosing three regions to study for a gigawatt campus.** Opens the tab and goes to the section. Sorts by peak demand to see which places could take a gigawatt at all, then by the planning reserve margin, then by active megawatts in the queue; keeps price, reserve margin, queue, the smallest load a rule applies to and carbon as the columns; opens three places and reads each one's top constraints and its utilities' rules. Should leave with three names and, for each, what its operator printed, with nothing on the page telling which to pick.
2. **A developer weighing two regions for a 300 MW load.** Sets the two as A and B. Reads every count A beside B: price mean and its 95th percentile, hours above USD 100, the share of the price that was congestion, the median years from request to operation, the smallest load a rule covers. Opens each for its rules' contract terms and collateral, each rule opening its document. Should not need a second page for any of it.
3. **An investor reading where congestion and queues are worst.** Sorts by the share of the price that was congestion, largest first, then by active megawatts in the queue, then by the share withdrawn. A place whose operator prints no such figure is last and says "not published" or is blank with "license needed"; it is never a zero. Downloads the rows shown as a CSV.
4. **A utility planner comparing its region with its neighbours.** Lists the balancing authorities alone, finds its own, opens it for its three partners and its net imports at the 100 highest hours, then sets it beside a neighbour as A and B. Reads how well each one's demand is forecast (the operator's error beside the ERW forecast's).
5. **A student.** Reads the sentence under the title to learn what a place is and where a count comes from; puts the mouse on a column's unit for its period and source; opens Texas and reads what its power is made of and the hour of the day its carbon is lowest. Should meet no word the page does not explain on hover.

Each case is taken start to finish in a build at 1280 and 390 px once the desktop's real files are on main; until then on the tests' fixture (`tests/fixtures/siting_regions/`, made-up values, never deployed).
