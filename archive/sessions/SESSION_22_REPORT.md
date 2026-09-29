# Session 22 report

Energy Research Warehouse (ERW), session 22, run 2026-09-27 to 2026-09-28 (UTC). **API spend: USD 9.0665**, under the USD 20 stop: news scoring 3.7041 + 5.2119, datacenter extraction 0.1505.

**The API ran out of credit, so this session did not reach the USD 20 stop.** At 05:54 UTC on 2026-09-28, call 49 of the second scoring run was answered "Your credit balance is too low to access the Anthropic API" (HTTP 400). The 31 calls after it failed the same way and cost nothing.

- **The uncapped datacenter backfill was ingested in full but only partly scored.** All 7,909 stories are stored; 3,563 were scored and 4,345 are not.
- **177 scored datacenter stories (152 clusters) still need extraction.**
- **The daily run's scoring and extraction will fail the same way** until credit is added, if the GitHub key is on the same account.

The commands to finish are under "Open questions".

No key was printed or committed. `origin/main` was merged before the push.

**Three things to know first:**
- **Every chart is now interactive, on one library.** It is ECharts 5.6.0 from cdnjs. Each chart has hover values with units, zoom and pan, and a PNG download. Time series also get legend toggles and a range slider. The map adds zoom and pan, hover cards, a state click that filters the page, and a legend that toggles kinds. Every page was checked at 390 px, and three that scrolled sideways were fixed.
- **The datacenter tracker grew from 11 to 309 facilities in one table,** `datacenter_facilities`:
  - 275 sites from nine operators' own public lists;
  - 31 facilities from the news (11 before);
  - 3 queue positions.

  15 facilities (4.9%) state MW, all from operator pages. Most operator sites and all news facilities state none.
- **Deduplication merged nothing.** No news facility names a county or city: 19 of the 31 have no US state, and the other 12 give only a state. The rule matches operator plus location, and a state alone is never merged.

## What was built

| Task | Result | API cost | Commit |
|---|---|---|---|
| 1 | Every chart on ECharts; the interactive map; 390 px check of every page | 0 | `e1e5463` |
| 2 | Uncapped datacenter backfill; 9 operator connectors; queue rows; `datacenter_facilities` with dedupe; spot check | 9.0665 | `ea4f623`, `2c66785` |
| 3 | Live set, coverage, briefing, tools list, value check 684 of 684, screenshots, this report | 0 | final commit |

## Task 1: interactive charts

**The library is ECharts 5.6.0.** It loads once from `https://cdnjs.cloudflare.com/ajax/libs/echarts/5.6.0/echarts.min.js` (`site/components/echarts.ts`). The first choice was 5.5.1, but cdnjs has no build of it (HTTP 404), which the first screenshots showed. Plotly was not used, so the site has one library. uPlot is removed from `package.json`.

**The shared components:**

| Component | Used by | What it gives |
|---|---|---|
| `TimeChart` | every time series (through `LineChart`, `StackedArea` and `Sparkline`) | Hover values with units; zoom and pan (wheel, drag, pinch); a range slider under every series; legend toggles; PNG download. The home sparklines keep hover and zoom only |
| `ShareBar` | the day's mix on `/grid` (one per balancing authority) and `/mix` | Hover value and share, legend toggles, PNG |
| `BoxChart` | the ERCOT peak-premium explorer | The five numbers on hover, zoom along the price axis, PNG. The number rows stay below |

Every table view and every citation is unchanged.

**The map** (`/map`) draws the states from GeoJSON: the us-atlas Albers file, already projected, with an identity projection. It adds:
- zoom and pan (wheel, drag, pinch) and a reset control;
- a hover card on each point (id, technology, MW, kind, status, placement);
- a click on a state that filters the page to it (the state select follows it, and a second click clears it);
- a legend that toggles kinds, kept in step with the Kind checkboxes;
- PNG download.

A click on a point still opens its card. A scripted browser check passed each of these at 1280 px and at 390 px: the hover card, clicking Nevada (365 points, 34,229 MW), clicking it again to clear, the legend toggle and wheel zoom.

**390 px check.** A script loaded all 22 pages at 390 px and measured the scroll width. Three pages scrolled sideways, and none of them because of a chart:
- **`/digest/[date]`:** a wide table.
- **`/data`:** the Access block, a grid item with a long code name.
- **`/curtailment`:** a long table name in a citation.

The fixes: wide prose tables now scroll inside themselves, `code` may break, and the Access grid items get `min-w-0`. After the fixes, all 22 pages are exactly 390 px wide and every chart loads (6 on the home page, 16 on `/grid`).

## Task 2: datacenter tracker expansion

### (a) The uncapped news backfill

`ingest.py --backfill --sectors datacenter_power --from 2025-01-01 --to 2026-09-27 --max-stories 1000000`:
- **Queries:** 378 Google News queries over 18 feeds, 21 months, none failed.
- **Items:** 9,101 dated items. 666 were already stored or had the same URL, 320 had a near-identical title, and 206 fell outside the dates.
- **New stories:** 7,909, and none was left out by a cap. `news_stories.csv` now holds 12,469.
- **Links:** none of the Google News links resolved to the outlet. 7,904 were served Google's own page and 5 timed out.

| Step | Stories | Cost (USD) |
|---|---|---|
| Score, run 1 (`--days 640 --limit 1500`): 35 calls | 1,500 (2025-01-01 to 2025-05-01) | 3.7041 |
| Extract (`datacenters/extract.py`): 11 calls | 124 datacenter stories, 107 clusters: 11 to 31 facilities; 9 fields not kept (status spans) | 0.1505 |
| Score, run 2 (`--days 270`): 48 calls, 31 failed on credit | 2,064 (2026-01-01 to 2026-06-11) | 5.2119 |
| **Total** | **3,563 scored; 124 extracted** | **9.0665** |

About USD 0.0025 per story scored and 0.0012 per story extracted.

**The split was planned to stay under the stop.** All 7,909 stories would have cost about USD 20.4 with extraction. So after run 1 the plan was to score 2025-06-01 onward (6,055 stories) and leave May 2025 unscored. The credit ran out partway through that plan.

**Not scored:**
- 2025-05 to 2025-12: 3,017 stories;
- 2026-06-11 to 2026-09-27: 1,328 stories.

**Where the stories went.** Among the 3,563 scored backfill stories, the scorer put 1,402 in sector "other" and only 301 in datacenter_power. The site filters and search terms find many stories outside the rubric's named sectors, as session 18 also found.

### (b) Operator sources

One connector per operator is in `warehouse/datacenters/operators/`, and `run.py` writes `datacenter_operator_sites` (entities, public).
- **Raw pages:** every page read is stored under `warehouse/raw/datacenter_operators/<run_id>/` with a manifest.
- **Location rules** (`common.py`): nothing is inferred. A state is kept only where the page names it. A status is kept only where stated: Oracle's Live or Coming soon, and Google's `inDevelopment` flag.
- **MW rule:** MW is kept only with its exact span, and the span must be in the page text.

| Operator | Page read | Sites | With state | Placed | With MW |
|---|---|---|---|---|---|
| Amazon Web Services | locations.json behind the Regions page; US regions only | 7 | 4 | 0 | 0 |
| Microsoft Azure | geographies page: region sentence and cards | 19 | 5 | 0 | 0 |
| Google | datacenters.google/locations (campuses, with the page's coordinates) and the Compute Engine zones table | 52 | 52 | 51 | 0 |
| Meta | datacenters.atmeta.com/all-locations cards | 28 | 28 | 25 | 0 |
| Oracle | public cloud regions table | 4 | 0 | 0 | 0 |
| Digital Realty | data-centers JSON list (coordinates) and each facility page (address) | 74 | 71 | 74 | 0 |
| Equinix | US page, 14 metro pages, 73 IBX pages | 73 | 44 | 42 | 0 |
| Vantage Data Centers | locations list and each campus page | 13 | 13 | 13 | 12 |
| Switch | colocation page and 5 location pages | 5 | 5 | 4 | 3 |
| **Total** | | **275** | **222** | **209** | **15** |

**Placement.** A site is placed at the operator's own coordinates where the page gives them, or else at the Census internal point of its stated county or city.

**Region names are not places.** AWS's "US East (N. Virginia)" gives only a state. Azure's "East US" and Oracle's "US East (Ashburn)" give no state. These sites are not placed.

**Digital Realty's unitless figure is not used.** Its list has `field_utility_power_capacity` (120000 for IAD39) with no unit on the page or in the data, so it is not an MW.

**Skipped, with the reason** (each page is read and stored raw on every run):
- **QTS:** qtsdatacenters.com redirects to q.com, which answers HTTP 503.
- **CoreWeave:** the region list is behind a login. The public page names only example region codes.
- **Crusoe:** crusoe.ai/data-centers states fleet totals only (6.1 gigawatts, 16.8M sq ft, 3,500 acres), with no list of sites.

**Found and fixed while building:**
- **Vantage:** the entry text picked up the menu words before "Ashburn I". Entries are now read from their own HTML elements.
- **Equinix:** a research note in the user agent drew HTTP 403. The user agent is now a plain browser one. Most IBX descriptions stop at the city, so the state now comes from the Address block where it repeats that city with a state and ZIP.
- **Digital Realty:** addresses have no comma between street and city. The state is now read from "ST 12345", and the city only where a comma sets it off. This took states from 45 to 71 of 74.

### (c) Interconnection queues

The pattern `data center | datacenter | large load | co-located load | digital campus | hyperscale | crypto | bitcoin` is matched on the name and fuel fields only. It finds 3 rows in six queues holding 14,567 rows. MISO's "High Voltage DC" and NYISO's "DC Transmission" rows are not matched.

| Row | Name | County | Queue MW | ISO status |
|---|---|---|---|---|
| `ercot_queue:25INR0688` | Giga Texas Data Center (Other - Battery Energy Storage) | Travis, TX | 133 | Completed |
| `ercot_queue:28INR0499` | Alpha Digital Campus Combined-cycle and Co-located Load (Gas - Combined-Cycle) | Reeves, TX | 58.26 | Active |
| `nyiso_queue:1630` | Suffern Quarry Data Center | Rockland, NY | 0 | Withdrawn |

**Their MW is not the load.** It is the generation or storage the position asks to connect, so it is kept as `queue_mw` and never as `mw`. The ISO generator queues hold very few loads, and ERCOT publishes no request-level large-load list.

**The rows persist between queue pulls.** They are kept in `datacenter_queue_positions`. The queues are pulled on Mondays only in CI, so on other days an absent queue keeps its rows from the last file.

### (d) Deduplication and the result

`warehouse/derived/datacenter_facilities.py` (method `docs/methods/datacenter_facilities.md`) treats two rows as one facility when both of these hold:
- **Operator:** they share an operator, after aliases (Amazon, AWS and Amazon Data Services count as one, likewise Meta and Facebook). A news row's developer also counts.
- **Location:** they are in the same state and name the same county or city, or they are placed within 25 km of each other.

An operator's separately listed sites (Vantage Ashburn I, II and III; Equinix DC1 to DC15) are never merged with each other. **No rows merged this run,** because no news facility names a county or city.

**Facilities before and after, by state:**

| | Before (session start, `datacenter_projects`) | After (`datacenter_facilities`) |
|---|---|---|
| Facilities | 11 | 309 (275 operator, 31 news, 3 queue) |
| With a stated MW | 0 (0%) | 15 (4.9%), 4,799 MW, all operator spans: Vantage 12, Switch 3 |
| Placed on the map | 1 | 213 |
| By state | AL 1, AR 1, ID 1, NM 1, OH 1, VA 2, none 4 | VA 37, CA 35, TX 35, IL 12, GA 10, NJ 9, OH 9, AZ 7, NV 6, OR 6, IN 5, NY 5, OK 5, SC 5, AL 4, FL 4, IA 4, NE 4, WA 4, MN 3, MO 3, NC 3, TN 3, UT 3, WI 3, AR 2, ID 2, MI 2, NM 2, PA 2, LA 1, MA 1, WY 1, none 72 |

**By status:**

| | Before | After |
|---|---|---|
| Not stated | 6 | 247 |
| Planned | 4 | 31 |
| Operating | 0 | 27 |
| Withdrawn | 1 | 2 |
| Completed (queue) | 0 | 1 |
| Active (queue) | 0 | 1 |

After the backfill extraction, the news table alone went from 11 to 31 facilities: 19 with no US state, plus one each in GA, PA, TN, UT and WI. **None states MW.**

### Spot check: 15 rows across the three sources

The rows were drawn at random from the final tables. The news extractor was not changed afterward.

| # | Source | Row | Checked against | Verdict |
|---|---|---|---|---|
| 1 | news | Amazon, GA | "Amazon's AWS to invest $11 bln in Georgia..." | Correct fields. A state-level investment, which the extractor's rule allows as a named operator at a stated place |
| 2 | news | Super Micro | "Super Micro to Build Third California Campus" | **Wrong:** a server-maker's campus, not a datacenter. California was also not kept |
| 3 | news | OpenAI, Stargate | "OpenAI's First Stargate Site to Hold Up to 400,000 Nvidia Chips" | Correct. No place in the title, so blank |
| 4 | news | Start Campus (Portugal), announced | "Start Campus plans to invest $9.35 billion in Portugal data hub" | Correct (no US state) |
| 5 | news | Applied Digital | "Macquarie to invest up to $5 bln in Applied Digital data centers" | **Wrong:** a financing with no site. It belongs in deals |
| 6 | operator | Vantage Ashburn II: VA, Ashburn, 96 MW | campus page "96MW of critical IT load" | Correct |
| 7 | operator | Switch Keep Campus: Atlanta, GA, 150 MW | "The Keep Campus located in Atlanta, Georgia, will have up to 150 MW of power" | Correct |
| 8 | operator | Digital Realty SJC34: CA, operator coordinates | "SJC34 2820 Northwestern Parkway Santa Clara, CA 95051" | Correct. The city is blank by the no-comma rule |
| 9 | operator | Equinix MI6 | "located at 1525 NW 98th Court Doral, FL." | **Wrong:** city "FL", no state |
| 10 | operator | Google Cloud us-west4: Las Vegas, NV | zones table "Las Vegas, Nevada, North America" | Correct |
| 11 | operator | Meta, Mesa, AZ | card "ARIZONA / Mesa" | Correct |
| 12 | operator | Azure East US: no state | region sentence | Correct: no place is stated |
| 13 | queue | Giga Texas Data Center | `ercot_queue:25INR0688` | Correct. queue_mw 133 kept apart from mw |
| 14 | queue | Alpha Digital Campus Co-located Load | `ercot_queue:28INR0499` | Correct |
| 15 | queue | Suffern Quarry Data Center | `nyiso_queue:1630` | Correct |

**12 of 15 are correct:** news 3 of 5, operators 6 of 7, queues 3 of 3.

**The two news errors are facility-or-not judgments** (a manufacturing campus, a financing). The extractor's field checks cannot catch them, and they are reported here, not fixed.

**The Equinix MI6 error came from a connector bug, not the extractor.** The description has no comma between street and city, so the fallback read "FL" as the city. It was fixed after the check: the state is now read from ", FL." and the city left blank. The rerun gives MI6 state FL, and no Equinix row has a state code as its city. The 12 of 15 above was measured before this fix.

## Task 3

- **Live set:**
  - `datacenter_facilities` was added to `live_set.yaml` and loaded: 309 rows.
  - `datacenter_projects` was reloaded (31 rows) and `news_index` (8,123 rows, 3,564 written).
  - `pg_database_size` is 329.8 MB of the 400 MB limit.
  - The first load stopped because the new table was not yet in `coverage.csv`. Coverage was rebuilt and the load run again.
- **Site:**
  - `/datacenters` reads `datacenter_facilities`. It gains a Source filter and column, the operator's MW span under MW, queue MW labelled as generation, and new scope text.
  - `/map` draws all 309 as the datacenter kind.
  - The click card reads `datacenter_facilities` (`/api/entity`), and the page list names the new table.
- **Coverage:** 106 tables. The three new tables are under power and datacenters.
- **Daily run and CI:**
  - The operator connectors run weekly with the queues (Mondays); `datacenter_facilities` is rebuilt daily after the extractor.
  - `datacenter_operator_sites`, `datacenter_queue_positions` and `datacenter_facilities` are tracked in git (`.gitignore` allowlist) and in the workflow's commit list, so the runner has them every day.
- **Briefing:** `package/llms.txt` describes `datacenter_facilities`, its kinds, `mw_span` and `queue_mw`. The question table points "Datacenter facilities" to it.
- **Tools list:** tool 4 in `docs/platform-tools.md` has the session 22 state.
- **Value check:** 684 of 684 match Supabase (`/weekly`: 20 of 20). The /datacenters and /map datacenter checks now read `datacenter_facilities`; the first run failed 20 of them until this was changed.
- **Screenshots:** every page at 1280 and 390 px, plus `map-interaction-desktop.png` and `map-interaction-mobile.png`. `/datacenters` is now long (309 rows), and its desktop capture is cut at 12,000 px.

## Decisions made without a human

1. **ECharts, not Plotly.** It is lighter, has built-in inside zoom, sliders and PNG export, and supports a map with custom GeoJSON. The version is 5.6.0 because cdnjs has no 5.5.1.
2. **"Kind queue"** is read as the tracker's source kind. The facilities table's `kind` column is news, operator or queue, and `kinds` lists every member's kind. On the map every facility stays the datacenter kind, and hover shows the source.
3. **Region-only rows are kept but not placed.** A cloud region named only by a direction or a city is kept with an empty state, rather than being given one from outside knowledge.
4. **Local and Wavelength Zones are left out of AWS.** They are edge sites inside other operators' buildings.
5. **Scoring order.** Oldest first for the first 1,500, then the newest months, so the gap would fall in 2025 rather than in the recent period.
6. **The Equinix connector was fixed after the spot check,** because it put a false city in a public table. The extractor was not touched.

## Open questions for a human

1. **API credit.** Add credit to the Anthropic account and check whether the GitHub `ANTHROPIC_API_KEY` is the same account. If it is, today's scheduled scoring, extraction, digest and weekly brief will fail on credit.
2. **Finish the backfill** once credit is back, for about USD 11.5 at this session's rates:
   ```
   python warehouse/news/score.py --days 640 --max-calls 120
   python warehouse/datacenters/extract.py --max-calls 100
   python warehouse/derived/datacenter_facilities.py
   ```
3. **Stories scored "other".** Of the 3,563 scored backfill stories, 1,402 went to "other" and only 301 to datacenter_power. Should the rubric's sector list, or the backfill's search terms, change?
4. **Facility-or-not errors in the news.** Super Micro's manufacturing campus and Applied Digital's financing are not datacenter sites. A rule, such as "a financing or a non-datacenter campus is not a facility", would need a change to the extractor, which this session did not make.
5. **QTS.** Its site answers HTTP 503 to a plain request. Is there another public list, and is scraping it acceptable?
