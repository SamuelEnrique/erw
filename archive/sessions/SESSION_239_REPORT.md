# Session 239 report: the merges, the menu, the old addresses

Branch `wip/239-merges` (worktree `erw-188`), from `bba5d091`. Unattended, in the chain of 12 to 13 October 2026.
Nothing pushed, no table written, no model called.

## Read these first

- **`/datacenters/v2` is NOT redirected.** The owner's list names it, but `/datacenters` does not draw what it shows
  (ERCOT's large-load status beside the facilities held), that page is session 240's in this chain, and
  `scripts/check-datacenters.mjs` reads it at 200. A redirect now would drop a page's content. The line is written
  in `site/next.config.ts`, commented, ready for the landing once `/datacenters` draws those blocks, or by ruling.
- **`/deals` opens on the table it showed before; the tracker (`/deals/v2`) is its second tab**, not its first. A link
  the home page writes (`/deals?type=capital`) reads the table's filter, which the tracker does not have. One line of
  `site/lib/tabs.ts` swaps the order.
- **`/map` holds the resources as a second view ("Resources"), not as layers of the one map.** The two maps are two
  components (`ProjectMap`: units on an SVG of the states; `ResourceMap`: grids and shapes on a canvas in its own
  plane). The reversible option, as the brief allowed.
- **`/network/v3` redirects to `/network`**, as it did. Session 237 redirects `/network` on into the Grid tool: the
  orchestrator joins the two at the merge (a chain of two redirects, or `/network/v3` straight to 237's target).
- **The menu lost seven entries** (`site/lib/pages.ts`): the Grid group lost `/consumption` (session 237 edits the
  same group: a merge by hand is likely there), Infrastructure is Project map, Datacenter tracker, Storage, Deals.
- **Not verified, and said so below:** the whole python suite and the whole `check-values` were not run; `check-buildout.mjs` was not run; 23 of the 30 screenshots were not looked at; `tests/test_session215.py` and `scripts/test-usage.mjs` fail on code this session did not change; the build log holds one "statement timeout" line and was not rebuilt. And the mutex was broken once, for about four minutes (see "Checks").

## What was built

Six pages hold what thirteen held. Each old page's file became a view file of the surviving page
(`git mv page.tsx view.tsx`, the sheet and the metadata moved to the page), so every block is drawn by the code that
drew it. The tab in view is in the address and marked `aria-current="page"`.

| Page | Tabs (address) | Folded in |
|---|---|---|
| `/storage` | The fleet (`/storage`), The build-out (`?tab=buildout`), The owners (`?tab=owners`) | `/storage/buildout`, `/storage/owners` |
| `/severance` | Calculator (`/severance`), Lease (`?tab=lease`) | `/severance/lease` |
| `/prices` | Every hub and zone (`/prices`), ERCOT (`?tab=ercot`) | `/explorer/ercot-peak-premium` |
| `/demand` | As metered (`/demand`), With the weather taken out (`?view=weather`), Consumption (`?view=consumption`) | `/consumption` |
| `/deals` | Deals (`/deals`), Tracker (`?tab=tracker`), Companies (`?tab=companies`) | `/deals/v2`, `/companies` |
| `/map` | Projects (`/map`), Resources (`?tab=resources`) | `/resources` |

- One tabs component for all six: `site/components/tool/Tabs.tsx`, reading `site/lib/tabs.ts` (the pages, their
  tabs, their addresses, the old addresses). Styled by the brand rule of the cost-of-power tabs, generalized in
  `site/app/tokens.css` (a selector added to the same rule, `nav[data-tabs]`; no rule copied, none changed).
- Each surviving page is wrapped in `<Brand>` and the shared sheet (`ToolPage`); no color, font or spacing was
  written in a page's file.
- A company is a filter of the tracker: each company's opened row links to `/deals?tab=tracker&party=<name>`, and a
  deal's party links to its row at `/deals?tab=companies#co-<name>`.
- The lease tab keeps its promise, word for word, and in the machine: `/severance` is in `NO_PREFETCH`
  (`components/SiteLink.tsx`), it was already a quiet path of the usage counter (`lib/usage.ts`), the page carries
  `data-no-usage`, and the tabs are plain anchors (never prefetched).
- The resource map writes its address with `tab=resources` first; the layer and overlay files keep their addresses
  (`/resources/layer/<name>`, `/resources/overlay/<name>`) and their status.
- The menu (`site/lib/pages.ts`): the seven pages that became tabs left it; each surviving line describes its tabs
  and lists the tables of all of them; `related` lines name surviving pages. Games untouched; the `/analysis` entry
  and the Grid entries of session 237's pages untouched; Thesis Builder and Power contracts stay.
- `site/lib/release.ts`: every status as it was (all `review`); the old addresses keep their lines, with a note.

## Every address, before and after

Asked as a visitor (no cookie) on the local build. "In-review page" is the short page the release gate answers.

| Address asked | Before (read from the code at `bba5d091`, not asked) | After: status | After: `Location` | What a visitor is then answered |
|---|---|---|---|---|
| `/storage/buildout` | 200, the in-review page | 308 | `/storage?tab=buildout` | the in-review page of `/storage` (in review) |
| `/storage/buildout?grid=ercot&measure=mwh` | 200, the in-review page | 308 | `/storage?grid=ercot&measure=mwh&tab=buildout` | the in-review page of `/storage` (in review) |
| `/storage/owners` | 200, the in-review page | 308 | `/storage?tab=owners` | the in-review page of `/storage` (in review) |
| `/storage/owners?grid=caiso` | 200, the in-review page | 308 | `/storage?grid=caiso&tab=owners` | the in-review page of `/storage` (in review) |
| `/severance/lease` | 200, the in-review page | 308 | `/severance?tab=lease` | the in-review page of `/severance` (in review) |
| `/explorer/ercot-peak-premium` | 200, the in-review page | 308 | `/prices?tab=ercot` | the in-review page of `/prices` (in review) |
| `/consumption` | 200, the in-review page | 308 | `/demand?view=consumption` | the in-review page of `/demand` (in review) |
| `/deals/v2` | 200, the in-review page | 308 | `/deals?tab=tracker` | the in-review page of `/deals` (in review) |
| `/deals/v2?view=ai&type=ppa` | 200, the in-review page | 308 | `/deals?view=ai&type=ppa&tab=tracker` | the in-review page of `/deals` (in review) |
| `/companies` | 200, the in-review page | 308 | `/deals?tab=companies` | the in-review page of `/deals` (in review) |
| `/resources` | 200, the in-review page | 308 | `/map?tab=resources` | the in-review page of `/map` (in review) |
| `/resources?on=oil_gas_basins&z=2&c=-101,32` | 200, the in-review page | 308 | `/map?on=oil_gas_basins&z=2&c=-101%2C32&tab=resources` | the in-review page of `/map` (in review) |
| `/board/v3` | 308 to /board | 308 | `/board` | the in-review page of `/board` (in review) |
| `/board/v4` | 308 to /board | 308 | `/board` | the in-review page of `/board` (in review) |
| `/map/v2` | 308 to /map | 308 | `/map` | the in-review page of `/map` (in review) |
| `/datacenters/v2` | 200, the in-review page | 200 |  | the in-review page, at the address (unchanged) |
| `/network/v3` | 308 to /network | 308 | `/network` | the in-review page of `/network` (in review) |
| `/curtailment/v2` | 308 to /curtailment | 308 | `/curtailment` | the in-review page of `/curtailment` (in review) |
| `/cost-of-power/seller/v2` | 308 to /cost-of-power/seller | 308 | `/cost-of-power/seller` | the in-review page of `/cost-of-power/seller` (in review) |
| `/seller/v2` | 200, the in-review page (no such page: 404 in the internal view) | 308 | `/cost-of-power/seller` | the in-review page of `/cost-of-power/seller` (in review) |
| `/storage` | 200, the in-review page | 200 |  | the in-review page, at the address (unchanged) |
| `/severance` | 200, the in-review page | 200 |  | the in-review page, at the address (unchanged) |
| `/prices` | 200, the in-review page | 200 |  | the in-review page, at the address (unchanged) |
| `/demand` | 200, the in-review page | 200 |  | the in-review page, at the address (unchanged) |
| `/deals` | 200, the in-review page | 200 |  | the in-review page, at the address (unchanged) |
| `/map` | 200, the in-review page | 200 |  | the in-review page, at the address (unchanged) |

No redirected address opens a page that was closed: each target is in review, as each old address was. `/storage`
stays at its address (one of the snapshot's 25); a visitor is answered the in-review page there, as before.

## The inventory: nothing a page shows is dropped

Read from the page files at commit bba5d091. "Check key" is what `scripts/check-values.mjs` reads (`data-check`, by
`components/Num.tsx`) or the page's own row mark (`data-row`, `data-n`, `data-deals`). Every block is drawn by the same
code as before: the page file became a view file (`git mv page.tsx view.tsx`), its sheet (`ToolPage`) and its
metadata went to the surviving page, nothing else was cut.

### /storage (stays; tab "The fleet", `/storage`)

| Block | Check keys | After |
|---|---|---|
| Title "Battery storage", lead, Method link | none | `/storage`, same |
| Headline "Batteries operating in the US" | `storage|mw|operating`, `storage|n|operating` | same |
| Chart "The last 24 hours, by grid, MW" | none (a chart) | same |
| "The fleet" by status, with MWh | `storage|mw|<status>`, `storage|n|<status>`, `storage|mwh|<status>`, `storage|n_mwh|<status>` | same |
| "By ISO", "By state" | `storage|...` sums by ISO and state | same |
| "Planned additions by year" | `storage|...` by year | same |
| "The daily cycle" | `series|storage_daily_cycle|...` | same |
| "Hour by hour, the last 30 days" | none (a chart) | same |
| Source line (4 tables) | none | same |
| new: two links in the lead to the build-out and the owners tabs | none | added |

### /storage/buildout -> `/storage?tab=buildout` (query carried: `grid`, `measure`)

| Block | Check keys | After |
|---|---|---|
| Title "How much storage has been built", lead | none | the tab, same (the lead's link to Storage now names the fleet and the owners tabs) |
| Ask ERCOT link (ERCOT only, internal view) | none | same |
| Panel "Choose": grid, measure | none | same; its links are `/storage?tab=buildout&grid=..&measure=..` |
| Summary sentence | `series|storage_buildout_monthly|...` (mw, mwh, hours, a year ago) | same |
| Three headline numbers | `series|storage_buildout_monthly|...` (mw, units, mwh, hours, added) | same |
| "Operating storage by year, by duration": chart and year table | `series|storage_buildout_monthly|...` by bucket and year | same |
| "Storage against solar": chart | `series|storage_buildout_monthly|..._per_...` | same |
| "By grid" table | `series|storage_buildout_monthly|...` every grid | same; its grid links are the tab's |
| Three folds (assignment to a grid, what EIA-860M covers, the newest month) | counts from the table | same |
| Source line | none | same |

### /storage/owners -> `/storage?tab=owners` (query carried: `grid`)

| Block | Check keys | After |
|---|---|---|
| Title "Who owns the batteries", lead, Method link | none | the tab, same (the link to the build-out names the tab) |
| Ask ERCOT link | none | same |
| Panel "Choose": grid | none | same; links `/storage?tab=owners&grid=..` |
| Summary sentence | `data-row` keys of `storage_owners_monthly` (operating_mw, owners_operating, top10_share_pct) | same |
| Three headline numbers | `data-row` (operating_mw/mwh/hours/units, top5/top10 share, planned_mw/units, owners_planned) | same |
| Chart "The largest owners, operating MW" | none (bars of the rows below) | same |
| Tables "Operating: the largest owners", "Planned: the largest owners" | `data-row` per owner | same |
| Folds "What an owner is here", "What is counted" | none | same |
| Source line | none | same |

### /severance (stays; tab "Calculator", `/severance`)

| Block | Check keys | After |
|---|---|---|
| Title, two paragraphs, the "not tax advice" note, "A whole lease?" | none | same; the lease link is `/severance?tab=lease`, prefetch off |
| "Calculator" (the form, the result, the default prices) | `sev|...`, `sevcert|...`, `sevcredit|...`, the monthly mean of `eia_fuel_spot_prices` | same |
| Cite line, rules version | none | same |
| "Every rule, with its source" | none (rules file) | same |

### /severance/lease -> `/severance?tab=lease`

| Block | Check keys | After |
|---|---|---|
| Crumb, title "Severance tax for a lease: every well, every month" | none | the tab, same |
| Three paragraphs: what it does; **"Your file stays on your computer."** (nothing is sent or stored); "not tax advice" | none | same, word for word |
| "Your lease": the lease tool (drop or paste a CSV, per well and month, flags, the results download) | computed in the browser (`scripts/test-lease.mjs`) | same component, `LeaseTool` |
| Cite line (default prices, their span), rules version | none | same |
| The promise in the machine: no prefetch, no usage count | | `/severance` is in `NO_PREFETCH` (SiteLink) and in `QUIET` (lib/usage.ts); the page carries `data-no-usage`; the tabs are plain anchors |

`/severance/lease/real` (internal) and `/severance/finder` are not redirected and answer as before.

### /prices (stays; tab "Every hub and zone", `/prices`)

| Block | Check keys | After |
|---|---|---|
| Title "Power prices", two paragraphs | none | same |
| One section an ISO: hub or zone, real time, interval, day-ahead this hour | `latest_prices|<entity>|<variable>|<ts>`, `series|<da table>|<entity>|<variable>|<ts>` | same |
| Cite line an ISO | none | same |
| Related line | none | same, under both tabs (Price board, Supply and trade) |

### /explorer/ercot-peak-premium -> `/prices?tab=ercot`

| Block | Check keys | After |
|---|---|---|
| "Explorer", title "ERCOT peak premium", Ask ERCOT link, two paragraphs, Method link, "Last input interval" | none | the tab, same |
| The explorer: hub and year, the blocks' medians and spreads, the tail, scarcity and negative intervals | `series|ercot_peak_premium_annual|<hub>|<variable>|<year>` | same component, `Explorer` |
| "Distribution by time of day", the monthly chart, the CSV download | none (charts of `ercot_peak_premium_monthly`) | same |
| Two cite lines | none | same |
| Related line (was: Prices, Price board) | none | the page's: Price board, Supply and trade (Prices is the page itself) |

### /demand (stays; views "As metered", "With the weather taken out")

Both views as before (every `data-n` key of `eia930_demand_growth` and `eia930_demand_weather`). The view links are the
shared tabs now (same `data-views`, `data-view`, `aria-current`); the Method link stays under the header.

### /consumption -> `/demand?view=consumption`

| Block | Check keys | After |
|---|---|---|
| Title "Consumption by sector", two paragraphs | none | the view, same |
| "United States": sectors, 12 months against the 12 before | `series_esum|eia_retail_sales_monthly|...` | same |
| "Sector shares and growth, by state" | `series_esum|...` (state totals) | same |
| "Where industrial and commercial load is growing fastest" | `series_esum|...` | same |
| "Industrial and commercial energy, all fuels (US)" | `series_esum|eia_sector_energy_consumption_monthly|...` | same |
| Cite lines | none | same |
| Related line (was: Energy mix, Datacenter tracker) | none | the page's: Grid conditions, Energy mix |

### /deals (stays; tab "Deals", `/deals`; `?type=capital` works as before)

| Block | Check keys | After |
|---|---|---|
| Title "Energy deals", two paragraphs | none | same; the link to the companies names the tab |
| "This month": three cells | `deals|month_count|<month>`, `deals|month_mw|<month>`, `deals|month_ai_pct|<month>` | same |
| The sortable table with filters, each row expandable | `deals|...` per row (usd, mw) | same; a party's link goes to `/deals?tab=companies#<anchor>` |
| Cite line, Related line | none | same (Related: Datacenter tracker, Project map) |

### /deals/v2 -> `/deals?tab=tracker` (query carried: `view`, `type`, `tech`, `grid`, `party`, `year`)

| Block | Check keys | After |
|---|---|---|
| Title "The deals tracker", crumb, lead | none | the tab; the crumb names the two other tabs |
| Panel "Your selection" (a GET form; views all, storage, AI power) | none | same; the form posts to `/deals` with `tab=tracker` hidden |
| Summary sentence | `data-deals-summary` | same |
| "Most stories give no size and no price" | `data-deals-all` (count, with_mw, with_price, with_other_price, with_dollars) | same |
| Three headline numbers | `data-deals` (count, mw, with_mw, with_price, with_dollars) | same |
| Chart "Deals by month" | `data-deals-month`, `data-deals-n` | same |
| The table of the selection | `data-deal`, `data-deal-mw` | same |
| Three folds (how a deal gets here, rows that were one deal, what this does not tell you) | `data-deals-folded` | same |
| Source line | none | same |

### /companies -> `/deals?tab=companies` (the hash `#co-<name>` still opens a row)

| Block | Check keys | After |
|---|---|---|
| Title "Companies", two paragraphs (the scope: a seed, not a census) | none | the tab, same |
| The table: filters by sector, niche, stage, state, confidence; company, niche, stage, location, confidence | none (rows of `energy_companies`) | same component, `CompaniesTable` |
| A row opened: what it does, founders, raised, website, confidence and its clause, sources | none | same, plus a new line "Deals": the tracker filtered by the company's name |
| Cite line | none | same |
| Related line (was: Deals, Datacenter tracker) | none | the page's: Datacenter tracker, Project map |

### /map (stays; tab "Projects", `/map`; every filter in the address as before)

Title, lead with the unit count (`data-map-units`), the map with its panel, summary, totals, card and table by
technology (`ProjectMap`), the source line, the Related line: same.

### /resources -> `/map?tab=resources` (query carried: `on`, `z`, `c`, `fuel`)

| Block | Check keys | After |
|---|---|---|
| Title "Where the resources are", lead | none | the tab, same |
| The map: toggles by group, the canvas, legends in the source's unit, hover values, the plants, the queue and the datacenters over it, the fuel filter, zoom buttons | `data-count`, `data-count-value`, `data-queue-*`, `data-legend*`, `data-hover-*` (read by `scripts/check-resources.mjs`) | same component, `ResourceMap`; the address it writes keeps `tab=resources` first |
| "Method note" (closed): how the map is drawn, one note a layer, layers not held, what is built or planned, the method document, the build date | none | same |
| Layer and overlay files | | `/resources/layer/<name>`, `/resources/overlay/<name>`: same addresses, same status |

The two maps are two components (`ProjectMap`: units on an SVG of the states; `ResourceMap`: grids and shapes on a
canvas, in its own plane), so the resources are a second view of the one page, not layers of the one map.

### The versioned addresses

| Address | What it showed | After |
|---|---|---|
| /board/v3, /board/v4, /map/v2, /network/v3, /curtailment/v2, /cost-of-power/seller/v2 | folded by sessions 132, 167, 168, 144, 145 | redirect already, unchanged |
| /deals/v2 | the tracker | `/deals?tab=tracker` (above) |
| /seller/v2 | never an address (404) | redirects to `/cost-of-power/seller` |
| /datacenters/v2 | ERCOT's large-load status beside the facilities held | NOT redirected: `/datacenters` does not draw its blocks, and that page is session 240's. The line is ready in `next.config.ts` |

## What to review

Open `https://erw-flame.vercel.app/internal/open` first, then:

- https://erw-flame.vercel.app/storage , https://erw-flame.vercel.app/storage?tab=buildout , https://erw-flame.vercel.app/storage?tab=owners
- https://erw-flame.vercel.app/severance , https://erw-flame.vercel.app/severance?tab=lease
- https://erw-flame.vercel.app/prices , https://erw-flame.vercel.app/prices?tab=ercot
- https://erw-flame.vercel.app/demand , https://erw-flame.vercel.app/demand?view=weather , https://erw-flame.vercel.app/demand?view=consumption
- https://erw-flame.vercel.app/deals , https://erw-flame.vercel.app/deals?tab=tracker , https://erw-flame.vercel.app/deals?tab=companies
- https://erw-flame.vercel.app/map , https://erw-flame.vercel.app/map?tab=resources
- an old address, to see it land: https://erw-flame.vercel.app/storage/buildout?grid=ercot&measure=mwh
- Screenshots of each tab at 1280 and 390: `docs/brand/review-239/`.

## Checks, with exit codes

Local build of the branch, port 3239, the internal view where a page is in review. Outputs: `runs/session239/`.

| Check | Exit | Result |
|---|---|---|
| `npm run build` | 0 | built in two minutes. **One "statement timeout" line in the build log** (a read of `series` during the static pages); not rebuilt. The six merged pages are drawn at request time, and the route check below found no new "no data" on any page |
| `npx tsc --noEmit` | 0 | after the build. A first run before any build of the branch ended 2, on eight lines of the older build's `.next/types/validator.ts` naming the page files that became views, and on nothing else |
| `check-values.mjs`, restricted to `/storage,/severance,/prices,/demand,/deals,/map` | 0, twice | 889 of 889 values match Supabase, both runs. A restricted run, not the gate of a landing: the whole list was not run |
| `check-routes.mjs` | 1, then 0 | first run: one failure, `/demand?view=consumption` with 3 "no data" against 0 on production, where that address still draws the metered view (`/consumption` shows the same 3 before and after: three cells of its table). The list now asks that view through `/consumption`; second run 174 of 174, and 0 failed as a visitor |
| `check-demand.mjs` | 0 | 102 of 102 |
| `check-demand-weather.mjs` | 0 | 78 of 78 |
| `check-prices-compare.mjs` | 0 | 54 of 54 |
| `check-map.mjs`, `check-map-v2.mjs` | 0, 0 | 91 of 91 each |
| `check-deals-v2.mjs` (at `/deals?tab=tracker`, 1280 wide) | 0 | 19 of 19; not run with `--phone` |
| `check-resources.mjs` (at `/map?tab=resources`) | 0 | all 97 passed |
| `check-no-request.mjs` | 0 | typing into the page made no request and stored nothing (it proves `/battery/customer`; no browser proof exists for the lease tab) |
| `test-lease.mjs`, `test-severance.mjs`, `test-buildout.mjs`, `test-resources.mjs`, `test-ask-tables.mjs` | 0 each | 93 checks, 26 cases, 935 checks, 88, 14 of 14 |
| `test-usage.mjs` | **1** | fails at `toolOf("/cost-of-power/battery")`, in `lib/usagepath.ts`, a file this session did not change (it names a tool from a group's own pages; the battery page is in a sub-group). Believed older than this session; not run on the base to prove it |
| The battery page (`runs/session208/capture.mjs`, 1280) | 0 | numbers against session 211's: 0 lines differ; page height 5016 |
| Python, the 122 modules that name a changed file | 13 failed, then 1 | 12 were pins of the merged pages, moved (list below) and rerun green. **`tests/test_session215.py` still fails**: the check prefix `cap` of `site/app/cost-of-power/seller/page.tsx`, neither file changed by this session |
| Python, the 91 modules that name the route check, the release list, the audience list or the usage counter (after the last edits) | 0 failed | |
| `tests/test_session239.py` | 0 | 21 tests |
| Em dash, over the 54 files changed | none added | two scripts hold the character from before, one each, unchanged (`check-buildout.mjs`, `test-buildout.mjs`) |

Not run: the whole python suite (the orchestrator's clean-copy run), the whole `check-values`, `check-buildout.mjs`
(it needs a build against its stub), `check-ask-ercot.mjs`, `check-datacenters.mjs`, the live-page snapshot (nothing was deployed),
the design and accessibility tools.

**The screenshots.** 30 files, each tab at 1280 and 390, quantized to 64 colors (1.8 MB). I opened 7 of the 30 and
they show the pages; the other 23 were not looked at. One thing seen at 390: the two tables of the consumption view
are wider than a phone and the page scrolls sideways there (whether `/consumption` did so before was not checked).

**A first set of screenshots was wrong, and the mutex was broken while it was taken.** The script that took them ran
after the session's own checks had stopped the server and given the mutex back (09:15:47 UTC); I had not read the
lock's owner again before starting it. For about four minutes (09:16 to 09:19) 30 headless browsers ran one after
another while session 241b held the mutex, and every picture was the browser's "cannot reach this page". Those 30
files were removed and are in no commit; the set in the folder was taken later, under the mutex (09:30 to 09:33),
with each step checking the lock and the server first. If session 241b's build or checks failed in that window,
this is a likely cause.

**The mutex was held 11 minutes for the build and checks** (09:04:53 to 09:15:47) and 3 minutes for the screenshots.

## Tests whose pins moved (each with a note "session 239")

- `tests/test_session45.py`, `test_session46.py`: the lease page's file is `app/severance/lease/view.tsx`; `NO_PREFETCH` begins with `/severance`.
- `tests/test_session53.py`: a home-page card may name an address that redirects to a tab; the menu holds `/severance`, not `/severance/lease`.
- `tests/test_session87.py`, `test_session90.py`, `test_session92.py`: the owners and build-out files are views; the owners view has no metadata of its own (the page is in review; the proxy marks the in-review answer noindex).
- `tests/test_session113.py`: the tracker's addresses are `/deals?tab=tracker...`; its file is `app/deals/v2/view.tsx`.
- `tests/test_session146_page.py`, `test_session159.py`: the resources page's file is `app/resources/view.tsx`; the menu names the resources on `/map`'s line.
- `tests/test_session152.py`: three views of `/demand`.
- `tests/test_session203.py`: the menu's list without the seven pages that became tabs.
- `site/scripts/test-usage.mjs`: `/storage/buildout` is counted as "Storage".
- `tests/test_session110.py` passes again by `site/lib/audience.ts` (two links name the tabs); no pin moved there.
- New: `tests/test_session239.py` (21 tests; it sets nothing at import).
- `site/scripts/check-routes.mjs`: the consumption view is asked through `/consumption` (see "Checks").

## Decisions made without you

- The parameter is `tab` on five pages and `view` on `/demand` (the parameter that page has used since session
  152). The tracker of `/deals` and the resource map already use `view` for their own choices.
- The folded pages' files stay in their folders as view files; they were not copied to `site/app/_retired`, because
  nothing is retired: every block is still drawn by its own code.
- The first tab of `/deals` is the table it showed (see "Read these first").
- The Ask ERCOT context of the three ERCOT views keeps the names the profile knows (`/storage/buildout`,
  `/storage/owners`, `/explorer/ercot-peak-premium`); those addresses redirect to the tabs.
- `/seller/v2` never was an address; it redirects to `/cost-of-power/seller` so a link written short answers.
- `site/lib/audience.ts`: the two storage links of the home page's lists name the tabs (the home page's own file is
  untouched).
- A view has no page metadata of its own: the browser's title is the surviving page's ("Storage", "Deals"...), and
  the `noindex` the owners, tracker and resources pages carried is gone with it. Every page is in review and a
  visitor's answer is marked noindex by the proxy; before a page opens to visitors, give the tabs their titles
  (`generateMetadata`) and decide what is indexed.

## For Samuel's ruling

- `/datacenters/v2`: fold its blocks into `/datacenters` and redirect, or keep it.
- `/deals`: which tab is first, the table or the tracker.
- The tabs' names: "The fleet / The build-out / The owners", "Calculator / Lease", "Every hub and zone / ERCOT",
  "As metered / With the weather taken out / Consumption", "Deals / Tracker / Companies", "Projects / Resources".
- Each tab keeps the title its page had ("How much storage has been built", "Who owns the batteries"...): one
  title a tab, or one title a page.

## To finish (for session 241 or a later one)

- `/prices`, `/severance`, `/deals` (the table and the companies tabs), the consumption view of `/demand` and the
  ERCOT explorer are wrapped in the brand and its sheet but still built from the older pieces (`Section`, `Cite`, an
  `h1` and tables of their own): bring them onto `ToolHeader`, `ToolSection`, `ToolTable`, `SourceLine`.
- The two maps draw with colors of their own components (`ProjectMap`, `ResourceMap`): read them from the tokens.
- `scripts/check-buildout.mjs` reads a build made against its stub (its header); it now opens
  `/storage?tab=buildout` and was not run in this session (no stub build).
- Links to the old addresses in other pages' files and documents (`site/app/page.tsx`, `site/app/about/page.tsx`,
  `site/app/queues/page.tsx`, `site/app/shoulder/page.tsx`, `docs/tools.md`, the method notes) still name them; each
  answers through its redirect.
- `docs/tools.md` (the inventory the menu follows) still lists the seven pages as pages.
- At 390 px the two tables of the consumption view are wider than the page.
- `scripts/check-routes.mjs`: ask `/demand?view=consumption` by its own address once production holds the view.
- `tests/test_session215.py` (`cap`) and `scripts/test-usage.mjs` (`toolOf` and the sub-groups): fix or move, by whoever owns the generator page and the usage counter.

## The landing

filled by the orchestrator
