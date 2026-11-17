# The company database (`/companies`) read as the reader it is for (session 7562, samueloldlaptop, 16 November 2026 Pacific, 17 November UTC)

Energy Research Warehouse (ERW). Asked by Samuel: the reader's read of chain 304's part B for the six tools of the first ten that had none. The tool reached the done line in chain 301 and 303 (`replication/companies/`, faults `docs/reviews/companies-faults-2026-11-11.md`, 31 rows).

**The reader:** a fund analyst sizing a listed power company's US fleet before a meeting: how many MW it operates and owns, its reactors, what it plans and has in the queue, and which of its subsidiaries hold what.
**The five cases:** (1) Constellation Energy; (2) Vistra; (3) NextEra Energy and Florida Power & Light; (4) Talen Energy and Susquehanna; (5) the hyperscalers as companies: Amazon, Microsoft, Meta, Google. On the page's own file, `site/data/companies/index.json` built 2026-11-16 09:04 UTC (12,724 listed of 14,033; 1,309 named only in held tables).
**How it was read:** the index and the 256 shards read by `runs/7562_co_cases.py` and `runs/7562_parents.py` (not in git); the index page drawn to HTML by its own function for `q=amazon` and `q=talen` (`site/scripts/test-companies-read.mjs`, 5 of 5). Not seen: no click, no hover in a browser, no layout at 390 px.

Part A's rows are cited by number and not written again.

## The cases, in one line each

| Case | What the page gives | Where it stops |
|---|---|---|
| 1. Constellation | `q=constellation`: 13 companies. Constellation Nuclear 23,798.1 MW operating (13 plants), 6,228.3 owned; Constellation Energy Generation, LLC, 21 reactors and 0 MW operating; R.E. Ginna Nuclear Power Plant, LLC, 1 reactor; Constellation Power, Inc 7,734.1 MW. "Constellation Energy Corporation", the listed company, reads "other", 0 MW | No figure for the company the analyst means; the two subsidiaries' "Parent: Constellation Energy Corporation" is plain text, though the parent has its own page (row 1); the parent's page names none of its subsidiaries (row 2) |
| 2. Vistra | Vistra Corp: 170.4 MW operating, 743.0 owned, 2 reactors; Vistra Energy Corp. 1,157.8 owned; Luminant Generation Company LLC 11,291.7 operating (a separate row the search for "vistra" does not find); Energy Harbor Corp.'s 4 reactors under Energy Harbor | The tables hold no record that one company owns another beyond 18 parent fields (row 2, row 5) |
| 3. NextEra | Florida Power & Light: 40,818.1 MW operating (140 plants), 4 reactors. "NextEra Energy, Inc.": developer, 0 MW. NextEra Energy Point Beach and Seabrook name it as parent, unlinked | The same as case 1 (rows 1, 2) |
| 4. Talen | TalenEnergy Susquehanna LLC: Operating 2,532, Owned 2,279, Footprint 4,811 MW | The footprint adds the owned share to the operated nameplate of the same plant: the reader takes 4,811 MW for the fleet (row 3, fixed in words) |
| 5. Hyperscalers | Google: lab or hyperscaler, 6 MW of solar and storage in California. `q=amazon`, `q=microsoft`, `q=meta`: "No listed company matches" | Their rows are deals and datacenters, held whole; the empty answer did not say so (row 4, fixed) |

## The rows

Kind: `site` (fixed on this branch, with a test: `site/scripts/test-companies-read.mjs`), `data machine` (a row of `docs/state/data_requests_done_line.md`), `browser`, `ruling`, `license`.

| # | Case | The cell or click | What the reader meets | Kind | State |
|---:|---|---|---|---|---|
| 1 | 1, 3 | The "Parent" fact on `/companies/eia-65506` (Constellation Energy Generation) and on NextEra Energy Point Beach's and Seabrook's pages | Plain text: `parent_id` is empty, though "Constellation Energy Corporation" is listed as `constellation` and "NextEra Energy, Inc." as `nextera`. Of the 10 parents named, 4 have no id (Constellation Energy Corporation, NextEra Energy, Inc., Xcel Energy, AmerenUE), and the first two are listed companies with pages of their own | data machine | requested (row 306): resolve a stated parent to the listed company of the same name (`warehouse/derived/companies.py`), with the same rules as a name |
| 2 | 1 to 3 | A parent's own page (`/companies/constellation`, `/companies/talen-energy`) | 0 MW and no list of the companies that name it as parent. The index file carries no `parent_id`, so the page cannot find them | data machine | requested (row 307): `parent_id` in `index.json`'s columns and a list of the companies that name a company as parent in its shard |
| 3 | 4 | The Footprint MW column's hover | "a sort key" only. 280 listed companies both operate and own plants (114,658 MW counted twice at most); Susquehanna's 2,532 MW reads 4,811. The method says so (`docs/methods/companies.md`, footprint_mw); the page did not | site | fixed: the hover says it is an order for the list, not a fleet, and that a plant both operated and owned is counted twice |
| 4 | 5 | `/companies?q=amazon` | "No listed company matches." The 1,309 companies named only in held tables (deals, datacenters, NYISO's queue, policy actions) were counted only in the notes above the table | site | fixed: the empty answer says how many are named only in held tables and that a company the ERW knows only from a deal or a datacenter is among them |
| 5 | 1 to 3 | Every company's figures | No parent sum: a fleet is the subsidiaries' rows, found by search, and some do not share the parent's name (Luminant for Vistra) | ruling | default: each legal entity keeps its own figures and none is summed into a parent. The other choice: a parent's page sums its listed subsidiaries' operating and owned MW, each subsidiary listed, once row 307 gives the list |
| 6 | 2 | Who owns whom | The ownership a reader knows (Vistra's purchase of Energy Harbor in 2024, as the analyst would bring it) is in no table: the 18 parent fields are the NRC's and the reviewed aliases' | ruling | default: only stated parents (the NRC's field, a reviewed alias with its evidence). The other choice: an ownership source read and cited; SEC filings are out of reach (EDGAR refuses the ruled contact string) |
| 7 | 5 | The hyperscalers' figures | Amazon, Microsoft and Meta have no row and Google 6 MW: their deals and datacenters are held | license | the two held tables' license (part A's deals row 1, datacenter rows 1 and 2) |
| 8 | 1 | Constellation Nuclear's "Seen 1969-12-01 to 1990-01-01" | A company with 23,798 MW operating today reads as last seen in 1990: the dates are its generators' first months | ruling | default: as part A's row 9 left it (the tip says what the dates are). The other choice: "Seen" ends at the newest file the company is in |
| 9 | 4 | `/companies?q=talen`, hover the Footprint cell | The new words | browser | wanted (row 305) |
| 10 | 5 | `/companies?q=amazon` at 390 px | The empty answer in full, no sideways scroll | browser | wanted (row 306) |

**Counts.** Site, fixed: 2 (rows 3, 4). Data machine: 2 (rows 1, 2). Ruling: 3 (rows 5, 6, 8). License: 1 (row 7). Browser: 2 (rows 9, 10).

**Words the reader would not know.** "Footprint" (row 3); "other" as a kind, part A's row 22.

## The figures this page shares with other pages

| Figure | Here | The other page | Agree? |
|---|---|---|---|
| Google's deals | 0 (energy_deals held) | `/deals`: Google and Constellation, 3,600 MW (session 7561), drawn only in the internal view | Both follow the hold: no figure on either for a visitor |
| ERCOT queue MW of NRG's two gas positions | 1,253.0 (Prairie) and 1,174.4 (Wolf Bone) | `/queues` and `/explore/interconnection`, from the same queue table | Not drawn here; one table |

## What this reader still cannot get from the tool, and why

- **A company's fleet in one figure.** No parent sum and few stated parents (rows 2, 5, 6).
- **The hyperscalers.** Their rows are held (row 7).
- **A fleet total from the Footprint column.** It double counts by design (row 3).
