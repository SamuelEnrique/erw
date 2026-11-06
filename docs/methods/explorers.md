# The signature explorers: the question, the tables, the computation, the tolerance, the limits

Energy Research Warehouse (ERW), session 1496 (chain 158, 6 November 2026). Platform tool 5 is three signature explorers under `/explore/` (sessions 403 to 405 and 2200 to 2202), each one page. This note gathers what each one is, for a reader and for the owner's review. The tables' own method notes hold the detail and are linked from each section. Every explorer is in review (not open to visitors) and draws its figures on the server from the live set (Supabase, the anon key), so its state is its address.

What the three share (`site/components/explore/Explore.tsx`):

- **Live, not a frozen file.** Each figure is one row of a table read on request, never a copy kept in the site. The line under the title says when each table was last computed and the newest period it holds, from the site's catalogue (`Freshness`). A table not computed for more than three days is said to be stale, with its date, in that line's first words.
- **Keyed and traced.** Every figure carries its row's check key (`series|<table>|<entity>|<variable>|<period>`). `site/scripts/check-values.mjs` reads every key again from the live set on every landing; its floors (`site/scripts/check-values-floor.json`) hold each explorer's default view and three others to at least ten checked figures. Every figure's hover names its table, its entity, its variable, its period and its source report (`site/lib/explore/source.ts`). `site/scripts/check-explorers.mjs` proves in a browser that every figure has its source, every chart answers a hover, and the page fits 390 pixels.
- **Nothing computed on the page.** The page draws rows; the tables are computed by the warehouse (`warehouse/derived/`) and their method notes say how.
- **The downloads.** Each table whole, and since session 1496 the rows the page draws as a download of their own (`/api/download` with its filters; the section of each explorer says which).

## ERCOT peak premium

`/explore/ercot-peak-premium`

- **The question.** How much higher and how much wider ERCOT's real-time price runs from 16:00 to 21:00 than at midday, and how that changed between two years: the thesis chart made live, for any hub, the whole year or one calendar month.
- **The tables.** `ercot_peak_premium_annual` and `ercot_peak_premium_monthly` (`warehouse/derived/ercot_peak_premium.py`; method `docs/methods/ercot_peak_premium.md`), from ERCOT's real-time settlement point prices (NP6-785-ER, NP6-905-CD), every 15-minute interval with no cap or exclusion.
- **The computation.** None on the page: each block's five numbers (minimum, quartiles, median, maximum), the peak median less the midday median, the peak interquartile range, the 99.9th percentile and the midday minimum are rows of the tables, computed by the warehouse per hub, per year (or month) and per local hour block (America/Chicago).
- **The tolerance.** A figure is the table's row to the digits shown (two decimals; the tables hold six). The thesis's own figures, HB_HUBAVG 2015 against 2025 (all-hours median 20.49 and 25.68, 99.9th percentile 583.96 and 311.80, peak interquartile range 7.64 and 34.12, midday minimum -3.98 and -18.25), are the explorer's default view. On 6 November 2026, on a build of main, every one of the eight matched to the cent (session 1494).
- **The limits.** The newest year and month are partial and marked so. A month view reads the monthly table; there is no day view. The hubs are ERCOT's six (HB_HUBAVG, HB_BUSAVG, HB_NORTH, HB_SOUTH, HB_WEST, HB_HOUSTON).
- **The download.** The hub's rows of the table drawn, from the first year drawn to the last, as CSV with the table's header. With a month chosen, the download holds every month of those years: the route filters by entity and time, not by month.

## Demand growth

`/explore/demand-growth`

- **The question.** How much more power a grid used than in 2019: the change in its average hour, or its highest hour, of metered demand, for the seven grid operators and the Lower 48, over the whole year, the year so far, one calendar month or one local hour of the day.
- **The tables.** `eia930_demand_growth` (method `docs/methods/demand_growth.md` and `docs/methods/eia930_demand_growth.md`), from EIA Form EIA-930 (Hourly Electric Grid Monitor): a balancing authority's adjusted demand, and the Lower 48's demand.
- **The computation.** None on the page: each figure is the table's growth since 2019, or its level, for a grid, a window and a year. The table leaves out EIA's faulty hours by the rules its method note gives (a faulty high hour would be a year's peak).
- **The tolerance.** The table's row to the digits shown. The ERW's documents name no thesis chart for demand growth (the method note, 21 October 2026), so the first chart is the table's own headline figure for every grid in the window chosen.
- **The limits.** The Lower 48 has no peak (its demand is EIA's sum over every balancing authority, faulty hours included). California's series breaks in December 2025 (the method note's section). The newest year is partial and the page says to which month.
- **The download.** The window's rows of the table, every grid and every year (the variables of the window drawn), as CSV with the table's header.

## Interconnection

`/explore/interconnection`

- **The question.** What became of the positions that entered each ISO's interconnection queue in a year (reached operation, withdrawn, still waiting, status not stated), in positions or in MW, for the six queues.
- **The tables.** `iso_queue_statistics` (method `docs/methods/energy_projects.md`, "Queue statistics"), from each ISO's own interconnection queue as the ERW last pulled it (`<iso>_interconnection_queue`).
- **The computation.** None on the page: each figure is the table's count, or one count its header states, for a queue, an entry year and a status.
- **The tolerance.** The table's row, exactly (counts and MW).
- **The limits.** A queue whose publisher asks for permission (NYISO, MISO, ISO-NE since 21 October 2026, `site/lib/license.ts`) is held: not read, its figures not shown, the page says so. While the table's header says it was built before the fix of 20 October 2026, the page says in one line that its counts are the first build's and shows them as the table holds them, never a corrected guess.
- **The download.** The table whole (its downloads line). The rows drawn are the queue's entities by prefix (`<iso>:queue_*`), which the download route's filter does not read, so no download of the rows drawn is offered.
