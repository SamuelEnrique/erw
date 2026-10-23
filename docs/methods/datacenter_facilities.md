# Method: datacenter facilities (the datacenter power tracker)

Energy Research Warehouse (ERW), session 22. Table: `datacenter_facilities` (entities shape, derived, public). Code: `warehouse/derived/datacenter_facilities.py`. Pages that read it: `/datacenters` and the datacenter points on `/map` (platform tool 4).

## What it is

One table for every datacenter the ERW knows of. It joins facilities from three kinds of source and removes duplicates between them by operator plus location. It estimates nothing. Each value comes from one input row, which `member_ids` names.

| kind | Input table | What a row is |
|---|---|---|
| news | `datacenter_projects` (`warehouse/datacenters/extract.py`) | A facility named in scored news stories. Every field was checked against the story's own words (session 16 ruling) |
| operator | `datacenter_operator_sites` (`warehouse/datacenters/operators/run.py`) | A region, campus or data center on an operator's own public list |
| queue | the six `<iso>_interconnection_queue` tables | A queue position whose project name or fuel field indicates a datacenter or a large load |

## Operator sources

There is one connector per operator in `warehouse/datacenters/operators/`. Each reads the operator's public page and any per-site pages it links. Every response is stored raw under `warehouse/raw/datacenter_operators/<run_id>/`. The rules are in `common.py`:

- **State.** Kept only where the page names it, by full name or postal code. Azure's "East US" and Oracle's "US East (Ashburn)" therefore have no state.
- **MW.** Kept only with its exact span (`mw_span`), and the span must be in the page text. Vantage states "206MW of critical IT load" and Switch "up to 495 MW of power". Digital Realty's list has a `field_utility_power_capacity` number with no stated unit, so it is not used.
- **Status.** Kept only where stated: Oracle's Live or Coming soon, and Google's `inDevelopment` flag. Everything else is empty.

| Operator | Page | Rows are |
|---|---|---|
| Amazon Web Services | locations.json behind the AWS Regions page | US regions (Local and Wavelength Zones left out) |
| Microsoft | Azure geographies page | US regions from the region sentence, plus cards naming a US state |
| Google | datacenters.google/locations, Compute Engine regions and zones | campuses (with the page's coordinates) and US cloud regions |
| Meta | datacenters.atmeta.com/all-locations | location cards (state, site, investment, groundbreaking year) |
| Oracle | OCI public cloud regions | US regions (city only, Live or Coming soon) |
| Digital Realty | data-centers page (its JSON list) and each facility page | US facilities with the operator's coordinates and address |
| Equinix | US colocation page, metro pages, IBX pages | US IBX data centers with the address in the page description |
| Vantage Data Centers | data-center-locations and each campus page | US campuses, MW from the Campus Overview |
| Switch | colocation page and the five location pages | campuses, MW from "up to N MW of power" |

Skipped, and checked on each run:

- **QTS:** the site redirects to a host that answers HTTP 503.
- **CoreWeave:** the region list is behind a login.
- **Crusoe:** the data center page states fleet totals only, with no list of sites.

## Queue rows

The pattern `data center`, `datacenter`, `large load`, `co-located load`, `digital campus`, `hyperscale`, `crypto` or `bitcoin` is matched against the name and fuel fields only. A queue position asks to connect generation or storage, so its MW (`queue_mw`) is not the datacenter's load. It never fills `mw`. The queue's interconnection customer is the operator, and the county's internal point places the row.

## Deduplication

Two rows are one facility when both of these hold:

- **Operator.** They share an operator, after aliases: Amazon Web Services, Amazon Data Services and AWS count as one operator, and likewise Meta Platforms and Facebook. A news row's operator or developer both count.
- **Location.** They are in the same state and name the same county or city, or they are placed within 25 km of each other.

An operator's separately listed sites are never merged with each other. Vantage Ashburn I, II and III, or Equinix DC1 to DC15, are distinct because the operator says so. A news or queue row that matches exactly one operator site joins it. One that matches several stays on its own, and `geo_note` says so. News rows that match each other are merged. A row with only a state is never merged.

The merged row takes its name, place and coordinates from the operator site, if there is one. MW comes from the operator's span or else the news (`mw_from` names the member). Status comes from the news, which is dated, or else the operator. `member_ids` and `source_urls` list every member.

## Columns

The entities standard columns come first, then: `kind` (the first member's kind), `kinds`, `site_type` (region, campus, facility, announced_site, queue_position or empty for news), `developer`, `state`, `county`, `city`, `mw`, `mw_span`, `mw_from`, `queue_mw`, `project_status` (the source's own word), `geo_precision` (operator, point, county, place or none), `geo_note`, `n_members`, `member_ids` and `source_urls`; since session 166 also `country` (after `city`).

## Country, and what the tracker's totals count (session 166)

No source the ERW reads records a country: the news extractor asks for a US state, and the operators' lists are read for US sites. So `country` is `US` where a row states a US state (the 50 states, the District of Columbia and Puerto Rico, the gazetteer's list) and empty otherwise, and `geo` is `US-<state>` or empty: never `US` on no source's word. A row without a US state may be outside the US (Firmus's two Tasmanian rows, a Stargate Norway row and a Karlsruhe row are among the 119 such rows of 8 October 2026) or a US site whose story or page names no state (Azure's "East US").

The tracker's totals and its two bars (stated MW by state, top operators by MW) count only rows with `country` `US` whose `status` is not `withdrawn` (the extractor's "cancelled"). Every other row stays in the table: a row without a country reads "country not stated", with the reason on hover. The Status column and filter show `status`, the entities vocabulary, never a source's raw word (`project_status` keeps that word in the table).

## The news extractor's merge rule (session 166)

The news extractor (`warehouse/datacenters/extract.py`) lets the model mark a facility as one already held (`same_as`). Since session 166 that mark is accepted only when the two name the same operator or developer (either side's), the same site name, or the same county or city in the same state; a state alone joins nothing, and the run log names each refusal. Before the rule, the 2025 story of a USD 2B Utah datacenter (no operator, no county) was joined to the 2026 Valar Atomics 9.4 GW story on the word "Utah" alone, and took its 9,400 MW (`datacenter:868a5b4c04ff1f44`). The rule does not split a row already joined: that row stays as it is until `--reextract` (a model run) rebuilds the news table.

## Limits

- **Not a census.** The news covers stories since 2025-01-01. Nine operators publish lists, and most of those give no MW. The queues hold very few load rows, because ISO queues are for generation.
- **Region names are not places.** A cloud region's name is not a street address. A region is placed only where its operator names a city and state.

## Grid pages: which grid a facility belongs to (session 36A)

The grid pages (`/grid/<slug>`, session 35) count the facilities of their grid. The table places a facility by state, not by grid, so the pages apply one rule, kept in `docs/grids/grids.json` and applied the same way by `site/lib/grid.ts` and `site/scripts/check-values.mjs`:

1. **Queue:** a facility with a member from an ISO's interconnection queue (a member id `<iso>_queue:...`) belongs to that ISO.
2. **Utility:** otherwise, a facility whose `utility` is one a grid lists under `utilities` belongs to that grid. The list holds the utilities the table names today: OGE Energy (SPP) and WEC Energy (MISO).
3. **State:** otherwise, a facility counts for every grid whose `states` include its state: the states wholly or mostly inside the grid (TX; CA; NY; the six New England states; for PJM DE, DC, MD, NJ, OH, PA, VA, WV; for MISO MN, WI, IA; for SPP KS, NE, OK). A state shared by several grids is on none of their lists, so its facilities are not counted by state.

In session 36A, 5 of the 340 facilities were placed by rules 1 and 2 (two ERCOT queue rows, one NYISO queue row, one utility each for MISO and SPP), all in states their grid already counts, so no grid's count changed.

## The tracker as it stands (session 329, 20 October 2026)

What the page `/datacenters` draws today, after the sessions since 166:

- **A top block** (session 240): the facilities held, the megawatts stated with what the sum counts, and what changed
  in the seven days to the day the page was drawn; then the list grouped by operator. Each figure is computed from
  `datacenter_facilities` and read again by `check-values`.
- **ERCOT's large loads** (session 241, from what `/datacenters/v2` showed): `ercot_large_load_status` beside the Texas
  sites, with ERCOT's pause of new large loads (session 304). The table's newest row is June 2026: ERCOT's reports since
  then state no figure (session 310); its method is `ercot_large_load_status.md`. The table is held for review in the
  live set, so it is not offered as a download.
- **The chart** (the large loads by report) is drawn in SVG (session 303).
- **The filters** (country, state, status, operator, source kind, a floor of megawatts) start at "All" (the floor of megawatts at none) and have a Reset.
- **Downloads** (session 329): `datacenter_facilities` and `datacenter_projects` as the live set's CSV with a Python and
  a Stata reader of that CSV (session 328's shared line); `datacenter_operator_sites` is not in the live set and is
  named with its place on Redivis.
- Read on 20 October 2026 from the public catalogue: `datacenter_facilities` and `datacenter_projects` were rebuilt that
  day; `datacenter_operator_sites` last on 12 October.

## The figures on the page and their keys

Each number `/datacenters` shows carries its key (`site/components/Num.tsx`), which `site/scripts/check-values.mjs` checks against the live set and `site/scripts/check-methods.mjs` against this note (session 409). The keys the sections above do not name, each counted by the page from `datacenter_facilities`:

- `datacenters|count`: "Facilities held", every row of the table, in the page's first line; the same count opens the paragraph beside ERCOT's large loads.
- `datacenters|counted`, `datacenters|no_us_state`, `datacenters|cancelled`: under it, the rows in a named US state and not cancelled (the rows the sums count), and the two kinds left out of the sums: the rows with no US state stated and the US rows cancelled (status `withdrawn` or `cancelled`). The paragraph beside ERCOT's large loads shows `no_us_state` too.
- `datacenters|mw_total`: "Megawatts stated", the sum of the stated MW of every row counted.
- `datacenters|n_with_mw`, `datacenters|status_mw|<status>`: under it, how many rows counted state a MW, and the stated MW summed by status as the table has it (a blank status reads "status not stated").
- `datacenters|first_week|<day>`: "First reported this week", the facilities whose first story is dated in the seven UTC days that end on the day the page was drawn (the key holds the first of those days).
- `datacenters|n_first_story`: in "What changed this week", how many facilities carry a first story's date (those found in the news).
- `datacenters|state_mw|<state>`, `datacenters|operator_mw|<operator>`: the bars "Stated MW by state" and "Top operators by MW" (the five largest), the stated MW of the rows counted summed by state and by operator. The list grouped by operator shows `operator_mw` again on each operator's line, unfiltered, with `datacenters|operator_count|<operator>`, the operator's number of facilities.
- `datacenters|sites_us`, `datacenters|sites_texas`: in "Beside it: the facilities the ERW holds", the sites in a named US state and, of those, the sites in Texas (state `TX`).
- `datacenters|sites_n_with_mw`, `datacenters|sites_mw`: the sites that state a size in MW and the sum of those sizes, every site held counted, the cancelled and those with no US state among them, so more than "Megawatts stated" at the top.
- `datacenters|texas_n_with_mw`, `datacenters|texas_mw`: the Texas sites that state a size in MW, and the sum of those sizes.
- `datacenters|kind_count|<kind>`: the sites by where each came from, an operator's own list, news stories or an interconnection queue.

## The figures on the grid page and their keys

Each number `/grid` shows carries its key (`site/components/Num.tsx`), which `site/scripts/check-values.mjs` checks against the live set and `site/scripts/check-methods.mjs` against this note (session 409). The keys the sections above do not name:

- `griddc|<grid>|n`, `griddc|<grid>|mw`: a grid's block "What is being built" (`components/grid/YourGrid.tsx`): the count of the `datacenter_facilities` rows mapped to the grid by the rule of "Grid pages: which grid a facility belongs to" above, and the sum of their MW (`capacity_mw`) where a source states it.
- `gridnews|<grid>|<since>|n`: the block "In the news" under it: the count of the scored stories of `news_index` dated on or after the day shown (fourteen days back) whose headline names the grid or whose region is one of its states (`site/lib/grid.ts`, `newsMatch`). The block links no note of its own; this note's link stands nearest it.

## The power side (session 467)

Since 21 October 2026 `datacenter_facilities` is held whole ("license needed", `warehouse/metadata/license_status.csv`): most of its rows rest on news stories or on operators' own pages, whose publishers ask for permission. The rows that rest only on a public source are interconnection-queue positions (the third machine's session 441, `docs/reviews/sources-by-row-2026-10-21.md` on `wip/441-450-third`: 2 of 420 facilities on 21 October, both from ERCOT's queue). The section "On the power side" of `/datacenters` (`site/app/datacenters/PowerSide.tsx`) shows those sites without reading the held table:

- **Which sites.** The positions of each ISO's own queue table in the live set whose name or fuel field matches the builder's `QUEUE_PATTERN` (`warehouse/derived/datacenter_facilities.py`; the page reads it with PostgreSQL's case-blind match, `site/lib/data.ts`, `queueSites`). A queue table that is held itself (ISO-NE's, MISO's and NYISO's since 21 October) is not read, and the section names its grid. A facility the builder merged with a news story or an operator's site is still a queue position here: the queue's fields are public whatever else names the site.
- **Its grid, county and connection.** As the queue states them: the county and state, the queue id and the ISO's own status, the first line of the point of interconnection, the queue date and the proposed or actual in-service date. The megawatts are the generation or storage the position asks to connect, not the site's load; the key is `entity|<grid>_interconnection_queue|<id>|capacity_mw` (`ercot_interconnection_queue`, `caiso_interconnection_queue`, `spp_interconnection_queue` today).
- **Its load zone.** Only where the queue names one that the cost-of-power calculator holds. ERCOT's queue states a county, not a load zone, and ERCOT publishes its load zones as a picture of a map with no list of counties (`site/data/curtailment/zone_shapes.json`, session 149), so no ERCOT site is placed in a zone: the section shows every zone of the grid instead.
- **What a flat load paid.** For each grid with a site, each of its load zones (ERCOT's regions marked `zone`; every region of a grid whose regions carry no kind) under the calculator's defaults: a load the same in every hour, bought in real time where twelve complete months of real-time prices are held, else day-ahead, over the region's last twelve complete months. The figure is the one `/cost-of-power?grid=<grid>&region=<region>` shows as its headline (`site/lib/datacenter.ts`, `regionCosts`), in USD per MWh, energy only. Its key is `dcpow|<grid>|<region>|per` (the per MWh figure), which `site/scripts/check-values.mjs` recomputes with the calculator's own steps (`site/scripts/datacenter-ways.mjs`, `pageOf`). A grid whose prices are held shows none.
- **What it does not compute.** The size, compute and cost of the frontier AI facilities themselves: the section links Epoch AI's data on AI data centers (`https://epoch.ai/data/data-centers`, as `docs/paper/related_projects_notes.md` records it) and names those figures as theirs.

## The tracker by grid (session 468)

`/datacenters?view=grids` (`site/app/datacenters/GridsView.tsx`, in review as the page is) counts the same sites, the queue positions that name a datacenter or a large load, by grid and by the zone their queue states (`site/lib/datacenter/bygrid.ts`, `groups`):

- **The groups.** One row a grid and zone that holds a site. A site whose queue names no zone (every ERCOT position today: ERCOT's queue has no zone column the ERW reads) is in the grid's row marked "not stated by the queue", and that row is set beside the grid's whole queue; a site whose queue names a zone is set beside that zone's positions.
- **The figures and their keys**, each `dcq|<grid>|<zone>|<stat>` with `-` for no zone, recomputed by `site/scripts/check-values.mjs` from the queue tables with the same reads and the same function: `sites` (the positions counted), `sites_with_mw` (those that state the MW they ask for, the count behind the sum), `mw_asked` (the MW those positions ask to connect: generation or storage, never the site's load), `active_positions` and `active_mw` (the grid's or the zone's positions whose harmonized status is active, and their MW where stated: requests, not plants).
- **The price.** In the table, the cheapest and the dearest load zone of the grid (or the zone named) for a flat load over the calculator's last twelve months (`dcpow|<grid>|<region>|per`, above). The chart sets each complete calendar year beside them, at most the last eight held, for the cheapest load zone of that year, the calculator's default zone and the dearest load zone of that year, in the market each zone's last twelve months are bought in (real time where held, else day-ahead); the fold under it holds the chart's figures, each `dcpow|<grid>|<region>|year|<YYYY>` (a complete calendar year), which check-values recomputes from the calculator's months for that region (`site/lib/datacenter.ts`, `years`).
- **What it leaves out.** The facilities that rest on news stories or on operators' own pages (held), a load zone for a Texas county (no list of counties is published), and any delivery, capacity or tax charge.
- **Downloads.** The queue tables of the grids shown and the price tables the calculator's regions read, as the shared downloads line offers them (a table not in the site's catalogue is left out, and the line says so when none is).

## Held by row: how a row is shown (sessions 499 and 500)

The site can now hold `datacenter_facilities` row by row instead of whole, by each row's own license (session 441's
method, [`docs/reviews/sources-by-row-2026-10-21.md`](../reviews/sources-by-row-2026-10-21.md)). Nothing changes until the
data machine writes a column `row_license` (one of `public`, `license needed`, `unsettled`, the strictest of the row's
members: its operator site, its stories and its queue position), kept in the row's `extra` by the loader, and marks the
table `hold = row` in `warehouse/metadata/license_status.csv`. Today no table carries the mark, so `/datacenters` shows
the hold as before.

Once both are there, the site reads the facilities whose own license is public (`extra->>row_license=eq.public`, checked
again row by row), shows them as it shows every facility, each with its sources linked, and says above them how many
rows are held (check key `held|entities|datacenter_facilities|rows`, a count of the rows whose license is missing or not
public). The top block's counts and megawatts are then of the public rows only. Session 441 counted 2 such rows on 20
October, both from ERCOT's queue. The power side and the view by grid (sessions 467 and 468) read the grids' own queues
and are unchanged.

## The rows by who stands behind them, keyed (session 827)

The deal tracker's sort (`docs/methods/energy_deals.md`, "The public rows, keyed"; `warehouse/deals/public_rows.py
--datacenters`) run on `datacenter_projects` and `datacenter_projects_evidence`: a facility at least one of whose
evidence rows comes from a publisher whose terms the ERW reads as public is shown, with its power-side fields only;
one every evidence row of which asks for permission is held; one resting on a publisher not read is unsettled. The
counts are `site/data/datacenters_public.json` and the line above the held table on `/datacenters` draws them:
`dcpub|counts|shown`, `dcpub|counts|held`, `dcpub|counts|unsettled` (`check-values` reads the live set's row count of
`datacenter_projects` against the file). On 23 October 2026 every one of the 168 evidence rows rests on a news outlet
that asks for permission, so 0 are shown and 150 held (`docs/reviews/datacenters-public-rows-2026-10-23.md`). The
sites a public source names are the interconnection-queue positions, which "On the power side" draws from the queue
tables themselves (session 467). Session 828 writes "What is shown and what is held" in full.
