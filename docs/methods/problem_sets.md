# The problem sets (`/learn/problems`)

Energy Research Warehouse (ERW). Five sets of five questions for a class, written in session 44 (sets A to C), 46 (D) and 55 (E). The code is `site/lib/problems.ts`; the index is `/learn/problems`, and since session 288 it is the one entry of the Games menu for the sets (Samuel's ruling 14 of 14 October 2026).

## How an answer is made

- Every figure is computed on the server when the page is built, from the live set (Supabase) or a committed file the site reads (`site/data/bill_rules.json`, `site/data/severance_rules.json`, `site/data/merchant_snapshot.json`, the network snapshot). None is typed.
- Each figure carries a check key; `site/scripts/check-values.mjs` recomputes it on its own and compares it with the page. A derived figure is `calc|<op>|<A>|<B>` (ratio, difference, percent) of two keys that are each recomputed.
- The pages are rebuilt at most once an hour, so the numbers move as the tables update. The sets of the whole country read committed page files instead, and move when the data machine rebuilds a file; each set's page says which (session 10229).
- **Rounding (session 10229, the problems audit's finding 4).** Every answer is computed from the unrounded figures and printed as a whole number or to two decimals, and each set's page says so. A student who divides the printed figures can differ in the last digit (on 26 November 2026, 3 of the 40 derived figures of the sets of the whole country: the sun's legend 4.37 against 4.36, the capacity factor 1.74 against 1.75, the industrial losses 473.69 against 473.70); one who reads the resource map's legend, which prints one decimal, more often (the sun's ratio 4.31, the wind's gap 0.60 against 0.62). The two questions that send the student to the legend say so in their first step.

## Which month, which hubs, which days (session 288, Samuel's rulings of 14 October 2026)

- **The latest complete month (ruling 5a).** A month of `cost_of_power_monthly` is complete for a hub when its `rt_hours` equals its `hours_in_month`: every hour held. Set B question 1, the bill questions B3 and B4, and since session 288 B2, B5 and D3 take the latest such month. B5 and D3 read `cost_of_power_hourly_profile`, which has no hour count of its own: they take the latest profile month that is complete for ERCOT's hub average in `cost_of_power_monthly`. Until session 288 these three took the latest month held, often one that had just begun.
- **All hubs, named and counted (ruling 4).** Set B question 2 names every hub of `cost_of_power_monthly` with its grid (two are CAISO's: NP15 and SP15) and says how many there are. No month is complete at all seven: ISO-NE's internal hub misses hours in most months (720 of 744 hours in August 2026, 576 of 720 in September; whole only in November and December 2024, January and March 2026). So the question takes the latest month in which every hub holds at least 95 percent of its hours, and the worked solution names each hub that is short with its hours, each a checked number. On 14 October 2026 that is August 2026. Until session 288 it read "all six ISO hubs" and listed seven.
- **The storm's days against as many normal days (ruling 6a).** Set E question 5 sets what the solar plant earned over the event window (18 days for Uri) against the mean baseline day of the same event (the same dates of earlier years) times the window's days. The keys are `mrs|<inputs>|<event>|days`, `|base_mean` and `|base_window`, recomputed from `lib/merchant.ts`'s `stress()`. Until session 288 the window was set against one normal week, seven days, which made the ratio about 2.6 times too large.
- **What the bill questions value (session 10229, the problems audit's finding 1).** B3 and B4 name the price their key uses: the kWh on the meter, with no losses added, at the load-weighted real-time price of the bill's hub (the CAISO NP15 for PG&E, the ERCOT hub average for Oncor) in the latest complete month, against the bill as /learn/bill builds it, without taxes and local fees. Until then the question asked "how many dollars are wholesale energy" alone; at the month's simple mean, or with the losses counted, the answer differs in its units digit.
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
| `page-file` | The sets of the whole country (four, and the fifth since session 8905) read committed page files | every figure a `pf\|` key; it moves when the data machine rebuilds the file | `site/lib/pagefile.ts`; session 8901 |
| `trade-month` | Who trades with whom: the month and the years | the newest month ended when the file was built; years both sides reported in all twelve months | `site/data/regions/trade/ten.json`, `trade_matrix.json` |
| `storm-hour` | A storm across the country: the hour | each region's highest hour of demand in the window, the first if two are equal | `site/data/regions/events/*.json` |
| `layer-by-id` | Under the ground and in the wind: the layer | found by its id; the legend's range as the map draws it, from the lowest low to the highest high over the layer's parts (the contiguous states, and Alaska and Hawaii where the list gives them; session 9601), and the totals as the list of layers gives them | `site/data/resources/manifest.json` |
| `industry-pick` | Where energy goes: the month, the industries, the year | the newest month with a total and the same month a year before; the first two ranked industries; the newest year both states hold | `site/data/industry.json` |
| `authority-pick` | Your own balancing authority: the authority, the plant, the rows and the partner | the Tennessee Valley Authority; the first of its ten plants; the retirement and the addition with the most MW; the partner with the largest gross exchange; ERCOT and CAISO for carbon | `site/data/regions/authority/*.json`; session 8905 |

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

## The whole country (chain 507, session 8901)

Four sets after the five, each in a module of its own (`site/lib/problemsets/<slug>.ts`, exporting `META`, `GUIDE_ENTRY`
and `build()`), registered by `site/lib/problems.ts` in `SETS`, in `problemSet` and, through `addGuide`, in the guide of
`site/lib/problemkit.ts`. Every figure is read from a committed page file the site already draws, never from the live set:

| Set | Address | Page files | What it asks |
|---|---|---|---|
| Who trades with whom | `/learn/problems/who-trades-with-whom` | `site/data/regions/trade/ten.json`, `site/data/regions/trade_matrix.json` | Tennessee's net imports by neighbour in a month; two sides' reports of one flow, their ratio and the gap over the hours both reported; a year the Mid-Atlantic and Tennessee disagreed on the direction; a flow's growth by either side's report; the border with Mexico, reported from one side; a month reported over part of its hours |
| A storm across the country | `/learn/problems/storm-across-the-country` | `site/data/regions/events/elliott_2022.json`, `uri_2021.json` | The highest hour of demand of Tennessee and the Carolinas in Elliott and of Texas in Uri against the baseline; what ran in that hour; what flowed into Tennessee; the two regions' imports; two reports of one flow in an hour |
| What is under the ground and in the wind | `/learn/problems/under-the-ground-and-in-the-wind` | `site/data/resources/manifest.json` | Legends and units of the resource map's layers; a map cell as a mean of the source's cells; a modelled capacity factor; geothermal sites; MWh per MW as hours; biomass in tonnes |
| Where energy goes | `/learn/problems/where-energy-goes` | `site/data/industry.json` | The industrial sector's total, end use and losses in the newest month, and a year before; the two largest manufacturing industries of 2022, a fuel's share, on-site generation and a region's share; Texas against Louisiana |

The fifth set, a reader's own balancing authority, was added by chain 590 (session 8905) once its files
(`site/data/regions/authority/`, chain 505) were on main:

| Set | Address | Page files | What it asks |
|---|---|---|---|
| Your own balancing authority | `/learn/problems/your-own-balancing-authority` | `site/data/regions/authority/tva.json`, `erco.json`, `ciso.json` | The Tennessee Valley Authority's capacity and nuclear's share; its largest plant; nuclear's and gas's shares of capacity against their shares of generation; the largest planned retirement and addition against the fleet of that fuel; the partner it exchanged most with, net against gross, and its net imports as a share of demand; ERCOT's carbon per MWh against CAISO's, and why the TVA file has none; its peak, its growth since 2019 against ERCOT's, and the public large-load rows of each |

The questions name the fields of the file, which are the figures of the block "Its own facts" the Grid tool's panel
draws, so a student can ask the same of the authority they live in from its own file (`authority-pick`).

### The pf| key

`pf|<path under site/data>|<path into the JSON>` (`site/lib/pagefile.ts`). The JSON path is segments joined by `/`: an
object key, an array index, or a selector `@field=value`, the one element of an array whose `field` equals `value` as
text; a selector may name several fields joined by `+` (`region_pairs/@a=MIDA+b=TEN+year=2019/gap_mwh`) and matches only
when exactly one element has them all. The characters `% / | ~ + = @ &` inside a segment are written as `%XX`. A path that
does not lead to a finite number gives no figure, and the set throws, so the page says it could not be computed rather
than print a number. `site/scripts/check-values.mjs` reads the file again with `fs` and resolves the path with the same
pure resolver; a `calc|` of two `pf|` keys recomputes through its `calc|` case. In the hover and the CSV a `pf|` figure
names its file and its path, and the source tables the file names in its own header (`tables`); the list of layers names
none, so its figures name no table.

### The decisions taken

- Each set reads committed page files only, so its figures move when the data machine rebuilds a file, not each hour;
  the pages still say the set is computed when the page is built (`page-file`).
- The month, the years, the hour, the layer and the industries are chosen by rules from the files themselves, never
  typed: the newest month of the trade file that had ended at the file's `built` stamp; a pair's years those both sides
  reported in all twelve months, and of those the year of the largest gap for the Mid-Atlantic and Tennessee; a region's
  highest hour of demand in an event's window, the first of equal hours, as the event page's table finds it; a layer by
  its id; the newest month with an industrial total and the same month a year before; the first two industries of the
  file's ranking; the newest year both states hold (`trade-month`, `storm-hour`, `layer-by-id`, `industry-pick`).
- The words of an answer that compare two figures (both sides agree on the direction, the flow grew by about the same
  factor, within 5 percent of each other) are written from the figures by a rule, so a rebuilt file cannot leave words
  that its numbers contradict.
- The five sets' figures, questions and order do not move: the four come after them in `SETS`, and the guide of
  `site/lib/problemkit.ts` keeps the five as they were (the file still imports nothing; the four are added to it when
  `site/lib/problems.ts` loads).
- No dated edition holds the four: the edition of 15 October 2026 was built before them, and a new edition is built from
  the live set by the data machine (`site/scripts/build-problem-edition.mjs`, which now writes a `pf|` figure as a row of
  its own with the page file as its source). Until then the index and each set's page link no edition for them, and the
  edition and teacher pages list no address for them; the live page carries every worked solution and why it matters.
  Since the editions of 20 and 21 November 2026 (`site/data/problem_editions/2026-11-20.json` and `2026-11-21.json`,
  built by the data machine) the sets of the whole country are in the dated editions too, and each set's page links the
  newest (the problems audit of 26 November 2026, finding 5).
- The industry page (`/industry`) is another branch's work and not on main; the set names the file's fields and links the
  method note only.

### Their replication

`replication/problem_sets/replicate_country.py` reads the page files with Python's `json` alone and recomputes every
figure of every answer by the rules above, writing `country_inputs.csv` (every figure read, with its file and path) and
`country_answers.csv` (every figure, read, derived or a series' highest). With `--compare` it checks them against the
figures the site's code builds (`site/scripts/problem-sets-country-figures.mjs`): every answer's figure recomputed, every
recomputed figure shown, each to a relative 1e-9. `replicate_country.do` reads the two CSVs (Stata reads no JSON) and
recomputes each derived figure and each highest hour. Tests: `tests/test_session8901_problem_sets_country.py`,
`site/scripts/test-problem-sets-country.mjs` and `site/scripts/test-pagefile.mjs`.

## A waiting set (chain 720, session 10404, 26 November 2026)

A waiting set is a problem set written and tested that the owner has not approved yet. It has its page at
`/learn/problems/<slug>` and is built exactly as a listed set is. It is not in `SETS` (`site/lib/problems.ts`), so:

- the index (`/learn/problems`) does not list it, and the instructors' note does not name it;
- it has no `data.csv`;
- no dated edition can hold it: `site/scripts/build-problem-edition.mjs` freezes `SETS` alone.

The waiting sets are the list `WAITING_MODULES` of `site/lib/problems.ts`. Approving one is moving its module from that
list to the modules of `SETS`, its choices into `site/app/learn/problems/Decisions.tsx` and this note's list of
decisions, and its figures into the replication. Until then its choices are drawn on its own page only.

### The ERW forecast's report card (`/learn/problems/a-forecasts-report-card`)

- **What it reads:** `site/data/predict/scores.json`, the file `/forecast` draws its scores from (written by
  `warehouse/predict/backtest.py`; contract `docs/state/page_files_predict.md`; method `docs/methods/predict.md`). A
  worked example and six questions on Texas's demand, the last on California beside it.
- **How a figure is found:** the file's rows are arrays in the order of its `rows_columns`. A question names a row by
  its place, series, method, cut and key; the module finds the row's position by those five and writes the figure's
  `pf|` key from the position and the column. No position is typed, so a rebuilt file moves the keys with the rows.
- **What is asked:** the mean absolute percent error of the ERW forecast and of the operator's own over every hour
  scored; the two in megawatts over the last two years; the two rules that need no model; the count of hours behind a
  score; the hour of the day with the largest and the smallest error; the ten highest-demand days; and the same
  difference for California.
- **It takes no side.** The set states each score as the file holds it. For Texas the operator's forecast has the
  smaller error in every question that sets the two side by side, and the set says so in figures. Its test refuses a
  word that ranks or advises.
- **The choices** (drawn on the set's page, each with its default and source): the place is Texas, the place
  `/forecast` opens on, and the second is California, the first region in the file's order, neither chosen by its score;
  the hours of the day are the largest and the smallest of the file's 24 rows, the first on a tie; two methods of a row
  are scored on the same hours, as the file is built.
- **Tests:** `site/scripts/test-problem-set-forecast.mjs` (every figure recomputed from the file by its key, and found
  again by the row its question names; the page drawn) and `tests/test_session10404_problem_set_forecast.py`.
- **Not done:** no replication in Python and Stata yet (the listed sets have one). It is written when the set is
  approved.
