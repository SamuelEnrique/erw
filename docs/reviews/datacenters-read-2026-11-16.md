# The datacenter tracker (`/datacenters`) read as the reader it is for (session 7560, samueloldlaptop, 16 November 2026 Pacific, 17 November UTC)

Energy Research Warehouse (ERW). Asked by Samuel: the reader's read of chain 304's part B (`queue/done/304-day-16-november-oldlaptop-done-line-economics.md`) for the six tools of the first ten that had none. The tool reached the done line in chain 303 (`docs/reviews/trackers-signature-pack-2026-11-16.md`, section 1; faults `docs/reviews/datacenter-faults-2026-11-11.md`). The file carries the name of the other reads (16 November, Pacific time); the session ran after midnight UTC, on 17 November.

**The reader:** an AI lab's energy lead sizing a 300 MW training site, who wants to know what is already announced or running near each candidate site, how big, on which grid, and how far ERCOT's approvals have got.
**The five cases:** (1) Abilene, Texas (32.4487, -99.7331; Taylor County, ERCOT), 300 MW; (2) New Albany, Ohio (40.0812, -82.8088; AEP Ohio, PJM), 300 MW; (3) Ashburn, Virginia (39.0438, -77.4874; Loudoun County, Dominion, PJM), 300 MW; (4) Phoenix, Arizona (33.4484, -112.0740) and Atlanta, Georgia (33.7490, -84.3880), outside the ISOs; (5) ERCOT's own queue and large-load figures for a Texas site. Each "near" is within 30 miles, on the table as the live set served it at 05:30 UTC on 17 November 2026 (vintage 2026-11-16, 458 facilities, 274 counted).
**How it was read:** this machine cannot build the site. The rows were fetched with the replication's own reader (`replication/datacenter_tracker/fetch_rows.py`, the anon key, nothing committed: the table is held); distances by the haversine in `runs/7560_dc_cases.py` (not in git); the facilities table drawn to HTML by its own component (`site/scripts/test-datacenters-read.mjs`, 8 of 8). Not seen: no click, no hover in a browser, no layout at 390 px.

Part A's rows (`docs/reviews/datacenter-faults-2026-11-11.md`) and the pack's cross-check are cited and not written again.

## The cases, in one line each

| Case | What the page gives | Where it stops |
|---|---|---|
| 1. Abilene | Texas: 46 facilities counted, 457 MW stated by 4 of them; no facility in the table stands within 30 miles of Abilene. The one row named "Stargate" is marked withdrawn and states no place | The OpenAI, Oracle and Crusoe campus at Abilene, reported since January 2025, is not a row (row 4); the page has no "near a point" (row 1) |
| 2. New Albany | Ohio: 13 facilities, 10,418 MW stated by 2. Within 30 miles: Google New Albany (operating), Meta New Albany, Google Cloud us-east5 and Google Columbus, Microsoft in Licking County (a story of 26 October 2026), Google Lancaster; none states MW. Each links its state's row on the All grids tab | 10,400 of Ohio's 10,418 MW is one row: SB Energy, basis "total", planned, from Utility Dive's story on AEP's earnings (row 5) |
| 3. Ashburn | Virginia: 33 facilities, none states MW; 30 of them within 30 miles of Ashburn (Equinix DC1 to DC21, Google Cloud us-east4, a George Washington University campus marked planned) | The largest market in the world has no megawatt on the page; Dominion's 4,800 MW datacenter billing peak of August 2026 is in the cross-check file only (row 7) |
| 4. Phoenix and Atlanta | Phoenix: 4 within 30 miles (Digital Realty PHX10 and PHX15, Meta Mesa, Google Mesa), no MW. Atlanta: 6, of which Switch Keep Campus states 150 MW and Carrier Connect 4 MW. Grid: blank on every Arizona and Georgia row | The blank read as missing data (row 3, fixed); the county's utility (APS or SRP, Georgia Power) is in no row (row 8) |
| 5. ERCOT's queue and approvals | 8,927 MW approved to energize and 3,900 MW observed running, ERCOT's report of 19 June 2026, with the line on ERCOT's pause of 3 August 2026; two queue positions named for datacenters, "Giga Texas Data Center" (completed) and "Alpha Digital Campus Combined-cycle and Co-located Load" (active) | "completed" and "active" read as running facilities (row 2, fixed; part A's row 16) |

## The rows

Kind: `site` (fixed on this branch, with a test: `site/scripts/test-datacenters-read.mjs`), `data machine` (a row of `docs/state/data_requests_done_line.md`), `browser` (a row of `docs/state/browser_reads_wanted.md`), `ruling` (written with the default taken).

| # | Case | The cell or click | What the reader meets | Kind | State |
|---:|---|---|---|---|---|
| 1 | 1 to 4 | The filters: state, status, operator, source, country, MW, grid, power | No way to ask "within 30 miles of my site": a state is the smallest place a filter chooses. The reader counts Ohio's 13 or Virginia's 33 rows by hand and has no distance. The project map's "Near a point" with the datacenter kind does it (`/map`, on `wip/7537-map-read`, landing row 35) | ruling | default: the tracker stays a list by state and operator, and distance lives on `/map` once that branch lands. The other choice: the same "Near a point" filter here on the same rows |
| 2 | 5 | The Status column of ERCOT's two queue rows | "completed" (Giga Texas Data Center) and "active" (Alpha Digital Campus), outside the four statuses the page explains. For ERCOT, Completed is a signed interconnection agreement, built or not (the map read's row 5); Active is a position still in study. Both read as a running datacenter | site | fixed: "queue position: completed" and "queue position: active" (the words part A proposed), each with a tip saying what it is and that it does not say the datacenter runs; the Status filter uses the same words. Part A's row 16 found it and left the page as it was until the builder changes; the page side is made here, since no machine waits (row 10 is the builder's side) |
| 3 | 4 | The Place cell of the 20 Arizona and Georgia rows | No grid line at all, where an ERCOT or PJM row names its grid: the reader takes it for missing data | site | fixed: "no ISO set", with a tip (the tracker names an ISO only; none where the state's utilities run their own balancing areas, or a split state no story names) |
| 4 | 1 | Texas, near Abilene | No row within 30 miles. Texas's 46 counted rows have no Abilene campus; the one "Stargate" row is withdrawn with no state. A reader who knows the campus stops trusting the list | data machine | requested (row 301): find why the news extraction holds no Abilene row, and whether the withdrawn "Stargate" row is the national announcement or the campus |
| 5 | 2 | Ohio's bar, 10,418 MW | 10,400 MW is one row (SB Energy, basis total, planned), read from Utility Dive's story on AEP's transmission and earnings. Utah's 9,400 MW is one row too (Valar Atomics, nuclear, a Google News link). The two are 19,800 of the 28,254 MW headline, 70.1 percent | data machine | requested (row 302): check each against its story's words, that the MW is one facility's and not a utility's or a developer's total. Utah's row is part A's row 21 (a 2025 story joined to a 2026 one on the word "Utah"; its second reading needs the key); the Ohio row is named in part A's row 17 (an operator not stated, its developer SB Energy) and its MW was not questioned there |
| 6 | 2 | The headline "Megawatts stated", 28,254 MW | Read as a measure of the country's datacenters, it is two announcements and nineteen others. The note says the tracker is a list of named sites, not a measure of megawatts; the headline does not | ruling | default: the headline stands as it is, with its "stated by 21 of the facilities counted". The other choice: a line under it naming the share of the two largest rows |
| 7 | 3 | Virginia's rows | 33 facilities, 0 MW. Dominion's figures (about 54,000 MW under contract, a datacenter billing peak of 4,800 MW in August 2026) are in `docs/methods/crosschecks/datacenter_tracker.md`, not on the page | ruling | default: the cross-check stays in the note. The other choice: each published figure of the cross-check beside its state on the page, with its document and date |
| 8 | 4 | The Power column of a Maricopa or Fulton County row | Empty. The column can name the county's one EIA-861 utility, or say how many serve the county (session 2243), but no row of the live set carries the fields (`utility_eia861`, `utilities_in_county`): none of the 458 has them. Outside the ISOs the utility is the reader's first question | data machine | requested (row 303): the facility fields of `warehouse/datacenters/facility_fields.py` (session 2236) loaded with the table, or the reason they are not |
| 9 | 1 to 5 | "model confidence 0.7" under a news row's sources | A word the reader would not know: what is scored, and is 0.7 a chance it gets built? | site | fixed: a tip from the extraction's own definition (one real facility, fields right; not a chance of being built) |
| 10 | 5 | The table's status vocabulary | Session 166 cleaned status to four words; the builder lets ERCOT's queue statuses through as "completed" and "active" | data machine | part A's row 16, restated; requested (row 304, its row on this list): map a queue position's status to the vocabulary in `warehouse/derived/datacenter_facilities.py`, or record the two as queue statuses (row 2 is the page's side) |
| 11 | 5 | `/datacenters`, the Status filter set to "queue position: completed" | The hover and the filter's words | browser | wanted (row 301) |
| 12 | 4 | `/datacenters`, the State filter set to AZ, at 390 px | "no ISO set" under each place, its tip inside the screen | browser | wanted (row 302) |

**Counts.** Site, fixed: 3 (rows 2, 3, 9). Data machine: 4 (rows 4, 5, 8, 10). Browser: 2 (rows 11, 12). Ruling: 3 (rows 1, 6, 7). License: 0 new (the table is held whole since 21 October 2026, the known hold). Key: 0.

**Words the reader would not know.** "model confidence" (row 9, fixed); "queue position: completed" for ERCOT (row 2, fixed); "operator list" (the source kind) is plain enough with its tip.

## The figures this page shares with other pages

| Figure | Here | The other page | Agree? |
|---|---|---|---|
| ERCOT's large loads approved to energize, newest report | 8,927 MW, ERCOT's report of 19 June 2026 (`site/data/large_load_status.json`) | `/cost-of-power?view=allgrids`, the ERCOT row's "MW approved", and `/cost-of-power`'s load answers, from the same file | Yes, by construction: one file, and the live set's `ercot_large_load_status` holds the same 8,927 for 2026-06-19 (read 17 November) |
| Project Matador, Amarillo | 222 MW stated, ERCOT | `/map`'s datacenter card (the map read's case 2) | Yes: one table |
| A facility's All grids row | "on All grids (its state)" for Ohio's and Virginia's rows | `/cost-of-power?view=allgrids` | Not drawn here; the link's address is the page's own function |

Not compared: the deal tracker's power purchases for the same campuses (read in session 7561).

## What this reader still cannot get from the tool, and why

- **What is near a site.** No distance on this page (row 1); `/map` does it once landed.
- **Megawatts in Virginia, Arizona and most of Texas.** The operators' lists state no size and the news states few (21 of 274 counted rows); the cross-check's published figures sit in the note (row 7).
- **The utility outside the ISOs.** The fields exist in the builder and not in the live set (row 8).
- **A change over time.** The table keeps one row a facility as it stands now (the page says so).
