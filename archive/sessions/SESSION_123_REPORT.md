# Session 123 report: the energy mix, how hard the system works

**Built and deployed as a review page, `/mix/stress`.** One table, `grid_stress_yearly` (2,002 rows: seven grids, 2019 to 2026 to date): the evening ramp, the lowest net load, what each fuel gave in the 100 tightest hours against its installed capacity, and the longest dark, calm stretch against the battery fleet. Every definition is on the page as it is computed. No live page changed (snapshot below). No model call, no request to any publisher.

**Verdict: ready to open, with two limits a reader must be able to see, and can.** Thermal fuels' share of installed capacity exists for 2025 and 2026 only, because the generator inventory on this machine does not list plants retired before 2025. And the records rest on hourly files that hold faulty hours; four kinds are screened out and counted. What is left is at the end.

## Read these first

1. **The evening ramp has more than doubled in Texas.** The largest one-hour rise of net load in an evening, as a share of that year's peak demand: 7.9 percent in 2019, 19.1 in 2025 (15,940 MW in the hour from 16:00 on 19 January 2025, when solar fell from 16.7 GW to 3.7). Over three hours: 17.9 to 32.8 percent. California: 23.7 percent in one hour and 47.1 over three in 2025. MISO: 4.0 to 10.0. PJM, New York and New England: 4 to 9 percent, rising slowly.
2. **In Texas the tightest hours moved off the sun.** Solar's output in the 100 tightest hours as a share of its installed capacity: 71.1 percent in 2019, 48.7 in 2023, 33.1 in 2024, 5.0 in 2025. In 2019 the tightest hours were summer afternoons; by 2025 they are after dark or on winter mornings. The same number in SPP, where solar is still small, went the other way (42 to 67 percent).
3. **What showed up in the tightest hours of 2025.** Nuclear 85.5 to 96.1 percent of its capacity; natural gas 53.5 to 72.8; coal 44.3 to 89.1 in the five grids that still burn it; wind 11.1 to 31.6. Hydro and storage together: Texas 31.7 percent (39.9 in 2026 to date), New York 68.3. The page says this is what the fleet did, not what it could do.
4. **The lowest net load, as a share of peak demand, 2025.** California 3.1 percent, SPP 8.1, Texas 11.5 (9,586 MW at 09:00 on 2 March, with wind and solar at 77.8 percent of demand), New England 18.9, MISO 27.5, New York 32.5, PJM 33.8. Texas's fell to 7.7 in 2026 to date.
5. **Dark and calm.** The longest stretch of 2025 with wind and solar under a tenth of installed capacity: 18 hours in Texas (322,188 MWh short of their average: 37.8 hours of Texas's battery fleet at full power, 26 times its energy), 18 in California, 16 in MISO, 20 in PJM, 15 in SPP, 62 in New England, 101 in New York. The page says no fleet can do either, and that a battery holds a few hours.
6. **Four kinds of hour that would have been records, and are not used.**
   - **EIA's balance does not close** (demand against generation less interchange, a fifth of demand apart). California, 8 March 2025: demand 13,710 MW against net generation 25,095; it would have been the year's lowest net load at minus 5,099 MW.
   - **A stale report**: an hour that repeats the one before to the MW. SPP has 2,568, and loses 2019 and 2026 to them.
   - **A spike**: a one-hour rise the next hour takes back. PJM, 1 December 2019: demand 86,378, then 103,428, then 89,476. It would have been PJM's largest ramp of the year, more than twice the real one. It passes session 118's rule, which allows 25 percent.
   - **Wind or solar blank** in a year that reports it.
7. **Hydro and storage are one line against capacity.** PJM's hydro output in its tightest hours is 157 percent of its hydro capacity, and MISO's 106: their pumped storage is in their "hydro", while the inventory counts it as storage. Each one's output is shown; the share is of the two together.
8. **New York's solar is not in the file.** Zero or blank in every hour of every year. New York's net load is demand less wind only, the page says so in a box, and solar has no line (never a zero).

## The table and how it is computed

`grid_stress_yearly`: one row a grid, year and variable; `x_at` holds the hour a record or a stretch begins. Validator: pass. Archive, Redivis draft, Supabase under `review_hold`. The page reads its own copy (`site/data/stress/`), which a test holds equal to the table.

| Term | As computed |
|---|---|
| Net load | demand less wind less solar, hour by hour |
| Evening ramp | each day's largest rise of net load from one hour to the next between 14:00 and 22:00 local; and over three hours. Between hours that are both used and next to each other |
| Tightest hours | the 100 used hours of the year with the highest net load |
| A fuel in those hours | its mean output over its installed capacity (nameplate, EIA's monthly inventory, in each hour's month) |
| Dark and calm | wind and solar together under 10 percent of their installed capacity of that month |
| A stretch | a run of such hours with no gap; it belongs to the year it begins in |
| Energy missing | the year's average wind and solar output less what they put out, over the stretch |
| Hours of the fleet | that energy over the operating battery fleet's MW; beside it, over its MWh |

A year is written when it holds nine tenths of its hours to date. Not written: California 2019 and 2020 (the hydro gap), SPP 2019 and 2026 (stale reports). The newest year is marked "to date" everywhere.

**What the inventory cannot give.** It lists units operating now and those retired since January 2025. For years before 2025 a fuel that lost plants would show too small a capacity and too large a share. So wind and solar have a share for every year; natural gas, coal, nuclear, and hydro and storage, for 2025 and 2026 only. The page and the table say so on every line it applies to.

## The live pages

One deploy: `task/123-mix-stress`, run 37307252440, merged to main as `83d4559`. One load: `grid_stress_yearly`, under `review_hold` (no page reads it from the database). No freeze was in force (`scripts/freeze.py status`: exit 0).

Snapshots `before-123` (12:06 UTC) and `after-123` (12:14 UTC, production serving the new page): 25 pages, 4,098 checked numbers each, 0 failed reads.

**10 differences, all of them the hourly network refresh of 12:05 UTC. None is this session's.**

| Page | Differences | What | Expected |
|---|---|---|---|
| `/network` | 10 | the live week's newest hour moved from 3 October 03:00 UTC to 4 October 03:00 UTC (EIA's interchange caught up a day); the refresh stamp 11:05 became 12:05; the ISOs' newest demand hour 09:00 became 10:00; the build stamp in the source line | yes: the hourly network job, between the two snapshots |
| the other 24 pages and views, `/`, `/terms` and the four methods pages among them | 0 | | |

## Decisions made without you

- **The evening is 14:00 to 22:00 local**, and the ramp is one hour, with three hours beside it. The prompt asked for MW per hour and a share of peak.
- **"Peak" is the same year's peak hourly demand.**
- **A stretch ends at an hour that is not used.** A longer stretch may hide behind a faulty hour; the figure is a floor.
- **The energy missing is against the year's average wind and solar output**, as the prompt's words ("against their average") read.
- **The battery fleet is the month the stretch begins in.** Early years show huge figures because the fleets were tiny; the page says to read them as the size of the gap other plants filled.
- **A blank interchange is not a failed balance.** California has 2,208 hours of 2024 with interchange blank; dropping them all would have cost the year. They are kept when demand stands to generation as in the grid's balanced hours (the middle 99 percent of that ratio).
- **California from the join uses CAISO's wind and solar with EIA's demand**, boxed on the page as two series.

## Errors, and what caught them

| What | Caught by | Now |
|---|---|---|
| A blank solar hour taken as zero made a false ramp | reading the first trial's records | blank hours of a reported source are not used |
| MISO's largest ramp of 2026 was a stale hour followed by a jump (18,014 MW) | looking at the hours behind each extreme record | the stale-report rule; the figure is 11,176 |
| PJM's 2019 record was a one-hour demand spike (16,629 MW) | the same | the spike rule; the figure is 7,405 |
| California's 2025 lowest net load was an unbalanced hour (minus 5,099 MW) | the same | the balance test; the figure is 1,379 |
| Two unit names not in the data standard ("MW/h", "hours") | the validator (blocked) | "MW" and "hour"; rebuilt |
| Hydro above 100 percent of its capacity in PJM and MISO | my own test on the built table | hydro and storage together |
| My made-up test hours were constant, so the stale rule dropped them all | the tests | a half-MW flicker in the test data |

Every extreme record of the first trials was looked at hour by hour before it was believed. Three of the six were faults.

## Tests

`tests/test_session123.py`, 22 tests: stretches and gaps; the ramp's window, the spike rule, a step across a missing hour; net load; a fuel against capacity, no share before 2025 for thermal fuels, hydro and storage together; dark and calm against a made fleet; hours that do not describe the grid; a year with too few hours; the inventory by month with a retirement; the built table's identities; New York's solar; every record says when; the site's copy equals the table; the definitions are on the page; no figure written into it.

CI on the push: the full suite and the site build passed (run 37307252440). Locally: the session's tests with 122's and 102's, the site build, the route check (16 live, 107 in review, 0 failed), five views of the page in the internal view.

## What is left

1. **The inventory before 2025.** With EIA's annual retired-generator list (one file, public), thermal fuels' share could go back to 2019. A pull for your approval; not made.
2. **The faults belong in the register.** SPP's stale hours, PJM's spike, California's unbalanced hours and blank interchange are written in `docs/methods/grid_stress.md`. They should also be entries of `warehouse/faults/faults.yaml`; I left session 118's table alone tonight.
3. **Session 118's rule lets a 20 percent one-hour spike through.** The spike rule here is for ramps only. Whether rule A's 25 percent should tighten is a question for the pages that use it, and would move numbers on live pages: held, not done.
4. **Pumped storage.** A cleaner split needs the pumped-storage column of EIA's file read on its own, for both the hours and the inventory.
5. **New York's solar** is not in EIA's hourly file at all. NYISO publishes its own; that is a new source.
