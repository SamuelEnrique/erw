# SESSION 35: Ask your grid, v1

## Read first
CLAUDE.md, PRIORITIES.md, docs/datastandard.md, archive/sessions/SESSION_34_REPORT.md,
the /grid, /storage, /emissions and /board pages and their queries (the pattern), the
/ask route and the chat spec and catalogue, warehouse/metadata/coverage.csv (which
tables carry which BA), the news tables and their tags.

## Budget and rules
- Expected Anthropic API spend: USD 1. Hard cap: USD 3 (ERW_SPEND_CAP_USD=3,
  ERW_SESSION=35). Model calls allowed: the scoped-chat check in Part C only.
- No pulls, no re-pulls, no backfills. The gate is closed; this session adds no source
  and no table. Every number on every page comes from a warehouse table already held.
  No placeholders; where a grid has no data for a block, the block says so plainly.
- No redundant work: one template, seven renders. Read coverage once to learn which
  tables carry which BA; do not scan tables to find out.
- The daily job may land while you work: pull and merge before pushing, never force
  push.

## Who this is for
A student in a first energy course, high school senior to undergraduate. Every page
should let them answer: who runs my grid, where my power comes from right now, what it
costs, how clean it is, what is being built, and what is different about this grid.
Reading level set there; no jargon without a one-line definition.

## Part A: one template, seven pages
Routes /grid/ercot, /grid/caiso, /grid/pjm, /grid/nyiso, /grid/isone, /grid/miso,
/grid/spp, from one component fed by a per-grid config (BA code, ISO name, time zone,
hubs or zones, which tables carry it). Nav: Grid gets a "Your grid" entry listing the
seven. Stanford palette, mobile-safe, tier chips and citations on every block, method
links where a block is derived.

Blocks, each present only when the warehouse holds that BA's data, otherwise a one-line
"not in the warehouse yet, here is where EIA publishes it":
1. Right now: demand, the day's shape so far and the same day last week
   (eia930_all_demand).
2. Where the power comes from: generation by fuel, last 24 hours and the last 30 days'
   mix (eia930_all_generation).
3. Batteries: the daily charge and discharge cycle (storage_daily_cycle; CAISO from its
   own series), fleet MW and MWh in this footprint (storage_capacity).
4. How clean: carbon intensity now, the last 24 hours, monthly since 2018
   (carbon_intensity_*).
5. What it costs: the main hub or zone day-ahead and real-time, the 30-day sparkline,
   peak and off-peak (price_board_* tables). PJM: the block says prices are internal-
   use until PJM permits publication.
6. What is being built: the interconnection queue by fuel and status, projects and
   datacenter facilities mapped to this BA (queue tables, energy_projects, datacenter
   facilities).
7. In the news: the last 14 days of scored stories tagged to this grid (the news
   tables; if no ISO tag exists, match on the ISO's names and say so in the report).

## Part B: the written layer
For each grid, five short sections in docs/grids/<iso>.md rendered on the page:
what this grid is and who runs it; how its market sets prices; what makes it
different (ERCOT's isolation and no capacity market, CAISO's solar and the evening
ramp, PJM's capacity auction, NYISO's downstate constraint, ISO-NE's winter gas, MISO's
north-south seam, SPP's wind); a short history with three dated events; a glossary of
ten terms used on the page. Each section ends with its sources: the ISO's own pages
and EIA, by URL. No market number appears in prose unless it is read from a warehouse
table on the page or carries an inline citation to an ISO or EIA page. Mark the whole
layer with a "written, cited" chip so students know it is text, not data.

## Part C: Ask ERCOT (and the six others)
The existing /ask, scoped: /ask?grid=ercot limits the catalogue to tables and rows
carrying that BA plus docs/grids/ercot.md, and the system prompt says which grid it
speaks for. The page has an "Ask ERCOT" box that opens it. Check: one question per
grid, seven calls total, each answer must cite a table or the written layer and state
no number it did not fetch; put the seven answers and their ledger cost in the report.
Every call goes through the cost ledger.

## Part D: verify and ship, last
check-routes and check-values extended to the seven pages (at least one check key per
block per grid), the chat spec regenerated, llms.txt lists the pages, package tests
untouched, deploy, live checks again.

## Do not
No pulls, no new tables, no model calls beyond Part C, no deletions from Redivis, no
gate changes, no force push, no invented numbers in prose.

## Report: archive/sessions/SESSION_35_REPORT.md
Per grid: which blocks render and which say "not yet", and why. The written layer's
sources. The seven scoped-chat answers with cost. Spend from the ledger against the
cap. Decisions made without a human. Run health and gate state. Open questions.
Skipped. Commit after every working step. Push at the end. Stop.