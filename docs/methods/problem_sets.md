# The problem sets (`/learn/problems`)

Energy Research Warehouse (ERW). Five sets of five questions for a class, written in session 44 (sets A to C), 46 (D) and 55 (E). The code is `site/lib/problems.ts`; the index is `/learn/problems`, and since session 288 it is the one entry of the Games menu for the sets (Samuel's ruling 14 of 14 October 2026).

## How an answer is made

- Every figure is computed on the server when the page is built, from the live set (Supabase) or a committed file the site reads (`site/data/bill_rules.json`, `site/data/severance_rules.json`, `site/data/merchant_snapshot.json`, the network snapshot). None is typed.
- Each figure carries a check key; `site/scripts/check-values.mjs` recomputes it on its own and compares it with the page. A derived figure is `calc|<op>|<A>|<B>` (ratio, difference, percent) of two keys that are each recomputed.
- The pages are rebuilt at most once an hour, so the numbers move as the tables update.

## Which month, which hubs, which days (session 288, Samuel's rulings of 14 October 2026)

- **The latest complete month (ruling 5a).** A month of `cost_of_power_monthly` is complete for a hub when its `rt_hours` equals its `hours_in_month`: every hour held. Set B question 1, the bill questions B3 and B4, and since session 288 B2, B5 and D3 take the latest such month. B5 and D3 read `cost_of_power_hourly_profile`, which has no hour count of its own: they take the latest profile month that is complete for ERCOT's hub average in `cost_of_power_monthly`. Until session 288 these three took the latest month held, often one that had just begun.
- **All hubs, named and counted (ruling 4).** Set B question 2 names every hub of `cost_of_power_monthly` with its grid (two are CAISO's: NP15 and SP15) and says how many there are. No month is complete at all seven: ISO-NE's internal hub misses hours in most months (720 of 744 hours in August 2026, 576 of 720 in September; whole only in November and December 2024, January and March 2026). So the question takes the latest month in which every hub holds at least 95 percent of its hours, and the worked solution names each hub that is short with its hours, each a checked number. On 14 October 2026 that is August 2026. Until session 288 it read "all six ISO hubs" and listed seven.
- **The storm's days against as many normal days (ruling 6a).** Set E question 5 sets what the solar plant earned over the event window (18 days for Uri) against the mean baseline day of the same event (the same dates of earlier years) times the window's days. The keys are `mrs|<inputs>|<event>|days`, `|base_mean` and `|base_window`, recomputed from `lib/merchant.ts`'s `stress()`. Until session 288 the window was set against one normal week, seven days, which made the ratio about 2.6 times too large.
- **The ratio questions (ruling 7a)** ask in the order a student reads: "ERCOT's peak was how many times CAISO's?" (A1, A3, C1, C5).

## Dated editions, the teacher's copy and the rows (session 293, Samuel's ruling 8a)

The live sets move every day: a class that prepares on one day meets other numbers on the next (set A question 1 read 2.56 on 13 October and 2.92 on 14 October). So each set also comes as a dated edition.

- **What an edition is:** every set as `site/lib/problems.ts` built it on the edition's date, frozen in `site/data/problem_editions/<date>.json` by `site/scripts/build-problem-edition.mjs` (the same code as the live pages, run once from the live set). `index.json` beside it lists the editions held.
- **The students' copy** (`/learn/problems/<set>/<date>`): the questions and their tables, no answers.
- **The teacher's copy** (`/learn/problems/<set>/<date>/teacher`): every answer and worked solution open, why it matters, and a print button.
- **The rows each question needs:** a CSV a question (`/problems/<date>/<set>-<id>.csv`, in `site/public/`), with a header naming the edition, the source and the time read. The rows come from the question's figures' check keys, the same keys `check-values.mjs` recomputes: one series row; the rows of a sum or a maximum over a range; the days of a month's mean; the two rows of a battery cycle. A figure computed from a committed file rather than a table (the bill rules, the severance rules, the merchant snapshot, the network snapshot, the game's battery) is one row marked "computed", its source the file.
- **Its numbers are drawn as frozen,** not checked against today's tables (`check-values.mjs` reads the live sets): their source rows are in the downloads.
- **A new edition** is one command, `node --import ./scripts/alias-register.mjs scripts/build-problem-edition.mjs <date>` in `site/`, and a commit. The first is of 15 October 2026 (UTC), read at 00:17.

## Limits
- The battery questions of set D use the game's assumed battery (`site/lib/battery.ts`): 13.5 kWh, 90 percent round trip.

## For a class to assign (session 3650, 6 November 2026)

- **What a student can do after each set:** one line under the set's title, from `site/lib/problemkit.ts` (`GUIDE`).
- **A worked example first:** each set opens with one question worked in full, its answer open, by the method of one of the five on other figures (set A: question 1 on the day before; B: question 1 on the complete month before; C: question 1's method on Uri's demand; D: question 1's method on one day; E: question 3 on the held month before), so it gives none of the five answers away. Its figures are computed and keyed as the questions' are.
- **The five from the easiest to the hardest:** `GUIDE[set].order`, by the number of moves a question needs (read and compare first; a maximum or a sum over a range next; a complete month, a local day, a rule file or a ranking last). The question ids do not change, so the editions' files keep their names; an edition built before this session keeps its own order.
- **The one-line computation:** each answer, on its click, shows the line that gives it (`line` in `lib/problems.ts`), made of the same keyed figures, so it moves with the data. No number is typed in it (`site/scripts/test-problemkit.mjs`).
- **Every figure's source as its hover:** the table, the entity, the variable and the time read from the check key, the table's citation (`site/data/table_citations.json`) and this note (`sourceOfKey`).
- **The index:** each set's grids, tables and skills, and its figures as CSV, `/learn/problems/<set>/data.csv`: every keyed figure of the live set with its key, table, value, unit and source. A figure of a row held for a license (`components/Num.tsx`, `heldBy`) is left out; in review the address answers the internal view alone, as the page does. For instructors, a hover beside the title holds each set's table keys and this note's path.

## The tool as a reader meets it (session 7534, chain 304, 16 November 2026)

This section completes the note for the done line: every view, every figure's table and rule, every choice with its
default and source, and what the sets do not hold. The tables' own notes are not repeated: `docs/methods/eia930_all_storage.md`
(the battery rows behind `storage_daily_cycle`), `docs/methods/cost_of_power.md` (`cost_of_power_monthly`, the hourly
profile and the seller's model on `site/data/merchant_snapshot.json`), `docs/methods/events.md` (`event_window_daily`),
`docs/methods/bill.md` (the two bills), `docs/methods/severance.md` (the tax rules) and `docs/methods/battery_game.md`
(the game's battery).

### Every view

- **The index, `/learn/problems`:** the five sets, each with its grids, tables, skills, its figures as CSV, and links to
  the newest edition and its teacher's copy; at its foot the decisions block of every set. No figure of its own.
- **A set's page, `/learn/problems/<set>`:** what a student can do after it, the note for teachers with the pages to
  open, the worked example (answer open), the five questions from the easiest to the hardest, each with its tables and
  its day where it has one, and under "Show answer" the answer, the one-line computation, the worked solution and why
  it matters. Every figure carries its check key and its source on hover; a figure of a held table is drawn "license
  needed" (`components/Num.tsx`). At its foot the set's decisions.
- **The edition's students' copy, `/learn/problems/<set>/<date>`:** the questions as built on the date, each with a
  download of the rows it needs; no answer.
- **The edition's teacher's copy, `/learn/problems/<set>/<date>/teacher`:** every answer and worked solution, frozen,
  and a print button.
- **The set's CSV, `/learn/problems/<set>/data.csv`:** every keyed figure of the live set (held ones left out).

### Every figure, set by set

Each figure is a row of the table named, or a sum, maximum or mean of rows, or a ratio, difference or percentage of two
such figures (`calc|<op>|<A>|<B>`). The rule picks the day, month or row; the words of the answer name what was picked.

| Set, question | Table(s) | The rule |
|---|---|---|
| A, example | `eia930_all_demand` | Question 1's method on the UTC day before (when both grids' demand holds 24 hours there; else the same day): the two peaks and their ratio |
| A1 | `eia930_all_demand`, `eia930_all_generation` | The newest UTC day both tables hold in full (24 hours, ERCOT and CAISO, demand and both generation variables): each grid's highest hour, ERCOT's over CAISO's |
| A2 | `eia930_all_generation` | The same day: the 24 hours of natural gas over the 24 hours of all net generation, each grid, in percent |
| A3 | `storage_daily_cycle` | The latest day both ERCOT (`eia930:ERCO`, EIA-930) and CAISO (`caiso:ISO`, CAISO's own) are held: `mwh_discharged`, CAISO's over ERCOT's |
| A4 | `carbon_intensity_daily` | The latest day both are held: `intensity_generation`, ERCOT's less CAISO's |
| A5 | `storage_daily_cycle`, `eia930_all_demand` | The newest ERCOT battery day whose Central-time day of hourly demand is whole: the day's discharge over the day's demand, in percent |
| B, example | `cost_of_power_monthly` | Question 1 on the complete month before |
| B1 | `cost_of_power_monthly` | ERCOT's hub average, the latest complete month (`rt_hours` equal to `hours_in_month`): `rt_load_weighted` less `rt_simple_mean` |
| B2 | `cost_of_power_monthly` | Every hub of the public rows (four since the hold of 21 October: CAISO NP15 and SP15, ERCOT's hub average, SPP North), the latest month each holds at least 95 percent of its hours: the largest and smallest `rt_shape_premium`, any hub short of its hours named with them. September 2026 on 16 November, every hub whole |
| B3, B4 | `cost_of_power_monthly` and `site/data/bill_rules.json` | The default bill of /learn/bill (PG&E, Oncor); its kWh times the latest complete month's `rt_load_weighted` of the bill's hub, over 1,000; that over the bill, in percent |
| B5 | `cost_of_power_hourly_profile` | The latest profile month complete for ERCOT's hub average: the lowest and highest of `rt_mean_h00` to `rt_mean_h23`, and their difference |
| C, example | `event_window_daily` | Uri, `eia930:ERCO`, `demand_max_mw`: the highest 2021 day over the highest baseline day |
| C1 | `event_window_daily` | Uri, `ercot:HB_HUBAVG`, `rt_max`: the highest 2021 day over the highest of the 2019 and 2020 days |
| C2 | `event_window_daily` | CAISO 2020, `demand_max_pct_vs_baseline`: the highest day, less 14 August |
| C3 | `event_window_daily` | Elliott, PJM: the highest `demand_max_mw` from 19 December 2022, and that day's `demand_max_pct_vs_baseline` |
| C4 | `event_window_daily` | ERCOT 2023 from 1 August: the day of the highest `rt_max` and the day of the highest `demand_max_mw`, and whether they are one |
| C5 | `event_window_daily` | Uri's highest `rt_max` over the 2023 heat's |
| D, example | `storage_daily_cycle` | One day, the latest holding both discharge and charge: out over in, in percent |
| D1 | `storage_daily_cycle` | The seven latest days ERCOT holds in the last 45 days (since session 7534; 12 days until then): the sums of discharge and charge, out over in; beside it the game's 90 percent |
| D2 | `storage_daily_cycle` | The latest day holding both peak hours: `peak_discharge_hour` less `peak_charge_hour` |
| D3 | `cost_of_power_hourly_profile` | B5's month: the game's 13.5 kWh battery buys 13.5 / 0.9^0.5 kWh at the cheapest hour and delivers 13.5 x 0.9^0.5 kWh at the dearest; the cash over 1,000; times 10,000 homes |
| D4 | `eia_fuel_spot_prices` and `site/data/severance_rules.json` | The latest complete month of WTI Cushing (the month before the newest held): the mean of its days; 1,000 barrels at that price; each state's base tax (Texas the greater of 4.6 percent and 4.6 cents a barrel, Louisiana 12.5 percent, New Mexico its three percent-of-value taxes); no fee |
| D5 | `eia_fuel_spot_prices` and the rules file | The latest held month at or before D4's with a Comptroller certified price: Henry Hub's mean, per Mcf, times 2,400 Mcf at 7.5 percent; the credit's tier by the certified price; the tax less the credit |
| E1 | the network snapshot (`eia930_all_interchange`) | The newest hour in which ERCOT's ties report a flow: the ties with a flow, and the largest in size, its direction from ERCOT's side |
| E2 | the same | The same hour: each balancing authority's sum of its signed tie flows; the largest |
| E, example and E3 | `merchant_revenue_monthly` (the snapshot) | Solar at ERCOT's hub average, the latest (and the one before) month holding 90 percent of its hours: sales over energy, the flat price, their ratio in percent |
| E4 | the snapshot | The 100 MW / 400 MWh battery's held months (90 percent of the month's days): each month's revenue less fixed O&M over a twelfth of the debt service; the months below 1.0 and the rest |
| E5 | the snapshot (`event_window_daily`'s window) | Uri's window days: the plant's revenue summed; the mean baseline day times the window's days; their ratio |

### The decisions

The same list is drawn at the foot of each set's page (its own choices) and of the index (all of them),
`site/app/learn/problems/Decisions.tsx`; `site/scripts/test-problem-sets-render.mjs` holds the two equal. The sets have
no input, so nothing is editable in place.

| Key | The choice | Default | Source |
|---|---|---|---|
| `live` | Live sets ask of the newest rows; a dated edition keeps its day's | rebuilt at most hourly; the edition of 15 October 2026 | this note; ruling 8a |
| `full-day` | Set A's day | the newest UTC day both tables hold whole | EIA-930; `site/lib/gridday.ts` |
| `battery-day` | A battery question's day | the latest day the daily cycle holds, whatever its hours | `storage_daily_cycle` (no hour count) |
| `local-day` | A5's demand day | Central time, local midnight to local midnight, only whole | ERCOT's local day |
| `complete-month` | A month question's month | `rt_hours` equal to `hours_in_month` | ruling 5a |
| `public-hubs` | B2's hubs and month | the public rows' hubs; 95 percent of hours | ruling 4; `site/lib/license.ts` |
| `bill` | B3 and B4's bills | the default bills of /learn/bill, 600 kWh | `site/data/bill_rules.json` |
| `baseline` | An event's normal days | the event table's baseline | `docs/methods/events.md` |
| `seven-days` | D1's week | the seven latest days held in 45 days | session 7534 |
| `game-battery` | D1 and D3's battery | 13.5 kWh, 90 percent, 10,000 homes | `docs/methods/battery_game.md` |
| `tax` | D4 and D5's tax | the base rate on the month's mean spot price, no fee; New Mexico's newest rates | `site/data/severance_rules.json` |
| `credit` | D5's credit | the Comptroller's certified price and its tier | Tax Code Sec. 201.059 |
| `network-hour` | E1 and E2's hour | the newest hour ERCOT's ties report | `site/lib/network.ts` |
| `seller` | E3 to E5's plants | the seller's model at its defaults | `docs/methods/cost_of_power.md` |
| `storm-days` | E5's normal days | as many days as the storm | ruling 6a |

### What the sets do not hold

- No hour count behind a battery day: a day built from part of its hours reads as a whole one (faults row 5 of
  `docs/reviews/problem-sets-faults-2026-11-16.md`).
- No figure of ISO-NE, MISO or NYISO: their rows are held for a license; set B ranks the public hubs only.
- Seven figures of set C (EIA-930 rows of a table held by grid) and, until `wip/7533-learn-bill` lands, six of set B are
  drawn "license needed" though recomputed (faults rows 7 and 8).
- New Mexico's tax rates after 31 August 2026 (not read; the step says so).
- In a dated edition, the network's hour is not kept, so its two network questions cannot be worked from their
  downloads (faults row 9).

### The replication and the cross-check

- `replication/problem_sets/replicate.py`, from this note and each question's own rule, not from `lib/problems.ts`: on
  the reads the five sets made of the live set (kept by `site/scripts/problem-sets-figures.mjs`, which also draws the
  pages with the site's code), every figure by its check key and every answer in words, 146 of 146 on 16 November 2026
  at 22:51 UTC; the edition of 15 October from its own downloads, 89 of 92, three network figures named.
  `replicate.do` gives five headline figures in Stata.
- The cross-check: `docs/reviews/problem-sets-crosscheck-2026-11-16.md` (13 rows: the event figures against FERC's,
  CAISO's and ERCOT's own accounts, the bills against EIA's average retail prices, the tax rules against their quoted
  statutes, the debt service against Lazard's illustration).
