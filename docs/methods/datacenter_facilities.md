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
