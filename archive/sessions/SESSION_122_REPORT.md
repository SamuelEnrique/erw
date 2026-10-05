# Session 122 report: the energy mix, how clean and when

**Built and deployed as a review page, `/mix/clean`.** Two tables: the carbon-free share of each grid's generation by hour (463,459 held hours, seven grids, from 2019), and by month and year with hourly-against-annual matching and load shifting (27,012 rows). No live page changed (snapshot below). No model call, no request to any publisher.

**Verdict: ready to open for six grids; California needs one sentence from you.** The figures are sound for what the page says they are. California's 2026 figure sits on a different source from its earlier years and jumps 17 points; the page says so in a box, but a reader who skips the box will read the jump as real. Whether California's earlier years should be shown at all is your call. What is left is at the end.

## Read these first

1. **The page says first what the figures are.** Generation inside the grid, not what customers used: imports are not in it. And the average of the hour's generation, not the marginal plant. Both are in the first lines, and the second again where load is moved.
2. **Carbon-free share of generation, 2025.** California 54.7 percent (11 months; EIA's series), Texas 45.8, SPP 45.6, New York 44.3, PJM 39.3, New England 36.9, MISO 34.9. Texas rose from 32.1 in 2019. New York fell from 58.9 in 2019 (Indian Point closed in 2020 and 2021).
3. **A 100 percent annual clean purchase does not cover 100 percent of a flat load.** Delivered as the grid's own carbon-free plants ran, in 2025 it covered, in the hour the power was used: PJM 95.2 percent, New England 94.5, New York 94.0, MISO 89.6, SPP 84.9, Texas 84.6, California 78.5. Delivered as the grid's solar: 41 to 51 percent, and buying 150 percent barely moves it (Texas: 45.0 to 46.8). The more wind and sun in a grid's clean mix, the wider the gap.
4. **Moving load into the cleanest hours cuts cost more than carbon.** Moving 20 percent of each day's energy into the month's four cleanest hours, 2025: carbon down 4.2 percent in Texas and 3.6 in California, around 1 elsewhere; cost at the day-ahead hub price down 11.5 percent in California, 9.8 in SPP, 8.2 in Texas. The carbon moves little because it is an average. The page says the marginal effect is not held and can differ either way.
5. **California is two series.** From 16 December 2025 its hours are CAISO's own; before, EIA's. The warehouse's own note on the break records that EIA's California gas output was 251.7 GWh a day against CAISO's 178.3 in the months both hold. So 2025 on EIA's data is 54.7 percent carbon-free and 2026 to September on CAISO's is 71.6. That step is mostly the source. The page boxes it; the month of the join is not written; 2019 and 2020 are not written (the hydro gap).
6. **A fault in EIA's file that nobody had recorded: New York's nuclear plants under "other".** In stretches from October 2021, 3,147 hours in all, New York's nuclear output is at nothing and "other" is higher by about as much. From 13 March to 1 May 2023 nuclear averages 12 MW against 2,671 in the same weeks of 2022; "other" 3,080 against 899. Four reactors do not stop together for seven weeks. Those hours are left out, and New York loses 2022 and 2023 as whole years. **The other energy mix page reads the same file**: `/mix/v2` (in review) shows New York's nuclear as "other" in those months. I did not change that page or the fault register; both are below under "What is left".
7. **No cost for PJM or MISO.** No hub price of PJM is held. MISO's prices are not used while MISO is paused and its terms are under review. MISO's generation is EIA's file and is shown.

## The tables

| Table | Rows | What | Where |
|---|---|---|---|
| `clean_energy_hourly` | 463,459 | a grid and an hour: carbon-free share, with the two sums and the source side | archive, Redivis draft; not loaded (`catalogue_hold`) |
| `clean_energy_summary` | 27,012 | by month: the share, the average day's 24 hours, the four cleanest hours, the shift's carbon and cost. By year: the same, the hours above 50, 75 and 90 percent, and the matching for three purchases in three shapes | archive, Redivis draft, Supabase under `review_hold` |

Both pass the validator. The page reads its own copy (`site/data/clean/`, one file a grid), which a test holds equal to the table row by row. Nothing was released on Redivis.

## How it is computed

- **The hours** are the energy mix's (`mix_profile.hours_of`): EIA-930 by source from January 2019; California from the join from CAISO's own supply; an hour is held when its sources add up to its total and no main source is blank. That last test is what leaves out California's hydro gap (October 2019 to August 2020).
- **Session 118's rule** screens demand in those hours already. Here it is also put to the hour's net generation: 7 more hours left out (California 6, New England 1).
- **Carbon-free**: nuclear, wind, solar, hydro. **Not**: natural gas, coal, and "other" (oil, geothermal, biomass, unnamed). Geothermal sits in "other" because EIA's file does not always separate it, so California is shown a little dirtier than it is. Storage is not a source.
- **A month** is written when 90 percent of its days hold every hour; **a year** when at most one month is missing. Nothing is filled.
- **Matching**: a flat 1 MW load buys p percent of its year's use (50, 100, 150), delivered in the shape of the grid's own carbon-free mix, solar or wind. Counted: the smaller of delivery and load, each hour. Nothing stored.
- **Shifting**: each day, 10 or 20 percent of the day's energy is taken evenly from every hour and put into that month's four cleanest hours. The day's energy is unchanged. The schedule is the month's own average day, known only afterwards: the page says it is not a forecast.
- **Carbon**: the hour's load times `carbon_intensity_hourly`. California's hours before the join are set back an hour where EIA stamps them late, as session 118's rule reads them.
- **Cost**: the day-ahead hub price. Texas from 2019; California, New England, New York and SPP from September 2024, so their 2024 figure rests on about 120 days and the page shows the days.

## The live pages

One deploy: `task/122-mix-clean`, run 37305996590, merged to main as `4bc489c`. One load: `clean_energy_summary`, under `review_hold` (the page does not read it; no live page does). No freeze was in force (`scripts/freeze.py status`: exit 0).

Snapshots `before-122` (11:54 UTC) and `after-122` (12:02 UTC, production serving the new page): 25 pages, 4,098 checked numbers each, 0 failed reads.

**26 differences, all of them the clock. None is this session's.**

| Page | Differences | What | Expected |
|---|---|---|---|
| `/` | 26 | the price board's newest real-time interval of the hubs, with their lines of text | yes: the 15-minute price job |
| the other 24 pages and views, `/network`, `/terms` and the four methods pages among them | 0 | | |

The home page's counts of rows and public tables did not move, and `/terms` did not move: the two tables and the two new sources are under their holds.

## Decisions made without you

- **"Other" is not carbon-free.** The alternative was to reread the workbooks for geothermal alone. It understates California; the page says so.
- **California before the join is shown**, boxed. The prompt asked for CAISO's own data from the join and the hydro gap left out, which I read as: EIA before, CAISO after, the gap in neither.
- **The misnamed-nuclear test.** Nuclear under a quarter of its usual output while "other" is above its usual level by at least half of nuclear's usual output. It keeps SPP's real double outage of October 2022 and California's of October 2020, where "other" did not move.
- **MISO's cost is not shown.** Its hub prices are in the warehouse; its terms are under review and an earlier session ruled that a new page shows no figure of its prices.
- **The site's copy, not the database.** The page works whatever is loaded, which matters after 15:00 today.
- **Session 123's hold lines went in this push.** The two tables were built in the same hour and the registry row of 123's source came with them; a held source's table must be held. Its page and table are 123's.

## Errors, and what caught them

| What | Caught by | Now |
|---|---|---|
| No price matched any hour: I had read a function's two results as one | the trial's log ("a price for 0 hours") | fixed before any table was written |
| New York hours at 0 percent carbon-free | reading the trial's lowest values | the misnamed-nuclear test; the fault written up |
| The shift's energy counted days the figures did not | rewriting the sum to return its own totals | one function gives the totals and the days |
| A held source whose table was not held | session 102's test | both held |

## Tests

`tests/test_session122.py`, 23 tests: the share; storage and negative output; the impossible-hour rule on net generation; nuclear under another name (flagged, a real outage kept, not asked where nuclear is small); the shift keeps the day's energy on 23, 24 and 25 hour days; matching (a flat supply covers all, a half-time supply covers half whatever is bought); the hydro gap in no figure; a month and a year never share a key; no cost for PJM or MISO; the site's copy equals the table; the page says first what the figures are and holds no number of its own.

CI on the push: the full suite and the site build passed (run 37305996590). Locally: the session's tests with the three older suites it touches, the site build, the route check (16 live, 103 in review, 0 failed), and five views of the page in the internal view.

## What is left

1. **California (yours).** Either accept the boxed break, or show California from the join only. One line in the builder.
2. **New York's nuclear in the fault register and on `/mix/v2`.** The fault is real and written up in `docs/methods/clean_energy.md`. It belongs in `warehouse/faults/faults.yaml`, and `/mix/v2` should leave those hours out as this page does. Both touch session 118's and 94's tables; I left them for a session that owns them.
3. **Geothermal.** Read EIA's geothermal column separately so California's share is not understated. Half an hour of work and a rebuild.
4. **Marginal carbon.** The page says what it does not hold. A marginal figure needs a source the warehouse does not have.
5. **PJM's price** (needs a key the warehouse does not hold) and **MISO's** (your review of its terms).
