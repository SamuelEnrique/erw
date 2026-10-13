# How it works: the Grid tool

- **Address:** `/grid`, with the grid and the view in the address, for example `/grid?grid=ercot&view=mix`.
- **Status:** in review (`site/lib/release.ts`). A visitor sees the in-review page; the internal view shows the tool.
- **Written from:** the branch `origin/wip/237-grid` at commit `13dfe385` (session 237), on 2026-10-13. Not from `main`: no commit of session 237 is on `main` (head `de22f049`). Until the branch lands, `/grid` on the site is the older "Grid conditions" page, and `/network`, `/mix` and `/emissions` are still pages of their own.
- **Owed on the branch:** four browser checks (`check-network-v3.mjs`, `check-network-v3-hard.mjs`, `check-mix-v2.mjs`, `check-ask-ercot.mjs`). Section 4 says what each stands at.

## 1. What it is for, and for whom

The Grid tool is one page that shows what a US grid is doing, from public hourly reports. It has a picker of eight (ERCOT, CAISO, PJM, MISO, NYISO, ISO-NE, SPP and US48, the Lower 48 states) and six views.

| View | The question it answers | For whom |
|---|---|---|
| Now | What did this grid use, generate, exchange and emit in the latest hours held? | Anyone opening the tool |
| Network | Which balancing authorities exchange power, how much, and who supplies whom? Live week, two stories, any day since 2019. 3D network or map | An investor reading a region; an operator checking a neighbour |
| Mix | What generates the power: now, the average day of a month, year after year, the hardest hours | An investor in generation or storage |
| Clean | How much CO2 a MWh carries, now and since 2018, and how clean each hour is | A buyer of clean power; a datacenter siting team |
| Exchange | This grid's ties in the newest complete hour, the week, and twelve months by neighbour | An operator; an analyst of imports |
| Ask | A question in words, answered from the warehouse's tables | A reader who does not know which table holds the answer |

What it is not. It is measurement, not a forecast and not a dispatch model. It is not real time (section 5, item 1). It shows flows between balancing authorities, not flows on lines. It is not a reliability study.

The tool was built in session 237 by folding ten pages into one: `/network`, `/mix`, `/emissions` and the seven `/grid/<iso>` pages redirect into its views (`site/next.config.ts`, permanent redirects, the query carried over). `/mix/clean`, `/mix/stress`, `/mix/v2` and `/network/v3` arrive in two steps. The session's report lists every block of every old page and where it stands now.

## 2. The model, in numbered steps

This tool has no financial model. Its "model" is the path from a publisher's hourly figure to the number on the screen.

1. **The sources.** EIA Form EIA-930 (the Hourly Electric Grid Monitor) gives hourly demand, the day-ahead demand forecast, net generation by energy source and interchange between pairs of balancing authorities. EIA's per-balancing-authority workbooks give hourly CO2 estimates from 2018-07-01. CAISO's own supply by fuel is read for California from 2025-12-16.
2. **The hour.** EIA stamps an hour by its end, in UTC. The ERW stores the hour's start (`ts_utc`). EIA's megawatthours per hour are read as the hour's mean MW.
3. **Completeness.** A generation or emissions day is written only when it holds all 24 hours. An interchange pair-day missing an hour is not written. Nothing is filled; every gap is a row of `warehouse/metadata/run_status.csv`.
4. **Nodes.** Each balancing authority that reports interchange in the week is one node: 70 nodes in the branch's snapshot (`site/data/grid_network.json`, built 2026-10-12T14:33:43Z). EIA's 16 regional and country sums (US48, TEX, CAN and the like) are not nodes.
5. **Links.** Each pair is counted once: 157 pairs in that snapshot. The flow is read from the balancing authority whose code sorts first, as it reported it. In an hour it did not report, the other side's report is used with the sign flipped. An hour neither reported is blank.
6. **The sign.** Positive interchange means the reporter exports. The ERW checked this against net generation minus demand for the seven ISO grids over 360 hours (2026-09-13 to 2026-09-28); the sum matches it, not its negative (section 4).
7. **A grid's net export.** In Now and Exchange it is the sum of the grid's reporting ties in one hour, signed from its side. A negative sum is written as a net import with its own check key.
8. **The newest complete hour.** The hourly builder ends the week at the latest hour in which at least 90 percent as many pairs reported as in a fully reported hour. The page then opens on the newest hour every reporting pair holds; a pair silent for the last 48 hours of the week is named and not waited for.
9. **The refresh.** Every hour a job pulls the 48 hours of interchange ending at EIA's own newest period, and 48 clock hours of demand for the seven ISO grids, and writes one JSON object to public storage. The page draws that object when it is whole and not older than the committed file; otherwise the committed file, and says so.
10. **The drawing.** Positions are a 3D force layout computed once per daily build (600 steps, seed 42) and never re-settled. Sphere size is demand (the seven ISO grids) or the week's interchange volume (the others); colour is carbon intensity of generation; link width and particle speed follow the hour's MW.
11. **The replay.** A day since 2019 is drawn from EIA-930's daily interchange. A flow is the Eastern day's MWh over that day's hours (24; 23 or 25 when the clocks change), so a day draws on the scale of an hour.
12. **Days no tie can carry.** A pair-day further than 10 median absolute deviations from the pair's own median is left blank; a deviation under 500 MWh counts as 500. The replay keeps such a day when both sides reported it and agree within 5 percent.
13. **Twelve months by neighbour.** `ba_supply_monthly` holds three measures of a grid's net imports: the sum of its ties, EIA's total interchange, and demand less net generation. The sum of the ties is the headline; where the three spread more than 1 point of demand the panel shows the range.
14. **Trace the power.** For the grid selected: the neighbours that supplied it on net over the period, largest first, and for each of those its own four largest suppliers. Nothing is traced through Mexico's operator.
15. **The mix in an hour (Now).** The latest hour that holds EIA's total net generation, with each energy source as EIA names it, grouped into eight colours. California's is withheld there (step 18).
16. **The mix over months and years (Mix).** An hour is used when its total is held and positive, its sources add up to within 5 percent of the total (PJM: 15 percent), and no main source is blank. A month is written when at least 90 percent of its days are complete; a year when at most one month is missing.
17. **Carbon intensity.** Of generation: EIA's CO2 generated times 1000 over net generation, kg CO2 per MWh. Of demand: EIA's CO2 consumed (generated plus imported minus exported) times 1000 over demand. Daily and monthly figures are energy-weighted over complete UTC days and months.
18. **California.** From the hour starting 2025-12-16T08:00:00Z California's generation is CAISO's own; EIA's CO2 stays the numerator. The two sources are never mixed in one day or month. EIA-930's California generation by fuel is not drawn in Now.
19. **How hard the system works (Mix).** Net load is demand less wind less solar. The evening ramp is the largest one-hour rise of net load between the hours starting 14:00 and 22:00 local. The tightest hours are the 100 with the highest net load in a year. Dark and calm is an hour with wind and solar under 10 percent of their installed capacity.
20. **Yesterday (Now).** The UTC day's peak demand and its hour, EIA's day-ahead forecast for that hour and its error, the day's mean absolute forecast error, seven days of demand with the temperature at one airport, and degree days at base 65 F.
21. **Reliability (CAISO only).** Every Flex Alert and emergency notice CAISO lists since 1998, by day, and for each day since 2018-07-01 the peak, the evening ramp and, since 2025-08-24, the batteries' share of the evening peak.
22. **Known faults.** Filtered or stated, never corrected by guess: California's hours stamped one hour late (2023-11-01 to 2025-12-02); California's 7,869 hours with no hydro; Texas's "other" repeating its batteries (6 to 14 December 2025); SPP's 2,568 stale hours; New York's nuclear filed under "other" (3,147 hours); impossible hours of demand and net generation.
23. **The map.** The Map shape draws the same hour, colours and ties over areas the ERW derived from counties (EIA-861, 2025). It is labelled as derived inside its frame. No published boundary of the balancing authorities is held.
24. **Ask.** ERCOT is asked through its own profile; the six other grids through the general chat scoped to that grid; the Lower 48 through the general chat. Every number in an answer must come from a query of a table. A question in the address is placed in the box and never sent by the page.
25. **The license gate.** A block that reads a grid operator's own table keeps the gate it had: PJM's prices are not shown, MISO's read "paused while terms are reviewed", and from 2026-10-21 a "license needed" table shows those words in place of its numbers.

How fresh each layer is, as the files state it:

| Layer | Refreshed | Behind the clock | Where it is written |
|---|---|---|---|
| Demand of the seven ISO grids | Every hour | One to two hours | `grid_network.md`, "Why the newest hour is not the current hour" |
| Interchange between pairs (Exchange; the Network's live week) | Every hour | 53 hours on 13 October 2026 at 07:57 UTC; about 35 to about 59 | `grid_network.md`, "How far behind the newest hour is" |
| Generation by source (Now; "Now and by state") | Daily | "A day or more after the hour" | `generation_mix.md`, "eia930_generation_latest" |
| Carbon intensity by hour | Daily, the last 3 days merged | "Often more than three days" (a comment in `Emissions.tsx`) | `emissions.md`, "Daily refresh" |
| Sphere and region colour in the live week | Daily | The latest hour of carbon intensity held | `grid_network.md`, "What refreshes hourly, and what daily" |
| The replay | With the daily tables | 2019-01-01 to 2026-10-10 in the branch's index | `site/public/network/daily_index.json` (branch) |
| The two stories | Pulled once | Fixed windows | `grid_network.md`, "The stories" |
| The state mix since 2001 | Monthly | About two months | `generation_mix.md`, "Two sources, two geographies" |

## 3. Every assumption, its default and its source

| Assumption or rule | Default | Where the user changes it | Source |
|---|---|---|---|
| Grid in view | ERCOT at `/grid`; the Lower 48 when an address opens Network, Mix or Clean and names no grid | The picker "Grid" (`grid=`) | ERW's choice (`site/lib/gridtool.ts`): an old link to `/network`, `/mix` or `/emissions` shows what it showed. Awaits the owner's ruling (session 237 report, ruling 1) |
| View | Now | The tabs (`view=`) | ERW's choice |
| Hour stamp | The hour's start, UTC | Fixed | EIA-930 states the hour's end; `docs/methods/grid_network.md` |
| Power unit | MW, the hour's mean | Fixed | EIA-930 publishes MWh per hour |
| Sign of interchange | Positive: the reporter exports | Fixed | EIA-930, checked over 360 hours (`grid_network.md`, "The sign") |
| Pair rule | The code that sorts first; else the other side, sign flipped | Fixed | ERW's choice: each tie once, so two reports are not added |
| Live window | 168 hours | The slider | ERW's choice (`network_hourly.py`, `HOURS`) |
| Hourly pull | 48 hours ending at EIA's own newest period | Fixed | ERW's choice: 48 clock hours would hold only about 14 hours of interchange (`grid_network.md`) |
| Newest complete hour, builder | At least 90 percent as many pairs as a fully reported hour, which is the 90th percentile of the pulled hours' counts | Fixed | `network_hourly.py` (`FULL_SHARE = 0.9`; session 61). The methods note says "the median hour"; the code is newer and is what runs |
| Hour the page opens on | The newest hour every reporting pair holds; a pair silent for 48 hours is not waited for | The slider | ERW's choice (`site/lib/networkV3.ts`, `completeHour`; session 124) |
| Page cache | One hour for Network; read on each request for Now and Exchange | Fixed | `revalidate = 3600`; `fetchHourly(0)` since session 237 |
| Layout | Force layout, 600 steps, seed 42, links weighted by the square root of their mean flow | Drag to rotate, scroll to zoom | ERW's choice (`warehouse/derived/grid_network.py`): the picture does not move between hours |
| Sphere size | 3 plus 22 times the square root of demand over the largest demand (ISO grids); 2 plus 10 times the square root of volume over the largest volume (others) | Fixed | ERW's choice (`site/app/network/Network.tsx`) |
| Sphere and region colour | Carbon intensity of generation, green to cardinal over the range held; grey where not held | Fixed | `carbon_intensity_hourly`, `carbon_intensity_daily` |
| Link width | 0.4 plus 3 times the square root of the flow's share of the period's largest flow | Fixed | ERW's choice: a small tie stays visible |
| Battery ring | Off | The switch "Batteries: off" | `eia930_all_storage` (ERCOT, ISO-NE, MISO, SPP); `caiso_battery_storage` (CAISO) |
| Price ring | Off. Weight: the square root of the price's share of the period's highest price | The switch "Prices: off" | Each ISO's hub price; ERW's choice of the square root, so one scarcity hour does not thin every other ring |
| Shape | Network (3D) | The toggle "Map", "Network" (`shape=map`) | ERW's choice (session 180) |
| A replayed day | EIA's Eastern day, as the day's average MW | The date picker "A day since 2019:"; "Play the year" | `eia930_daily_interchange` |
| Screen for a day of interchange | 10 median absolute deviations, floor 500 MWh | Fixed | ERW's choice (`ba_supply.screen`; `docs/methods/impossible_hours.md`, rule C) |
| A screened day kept | Both sides reported and agree within 5 percent | Fixed | ERW's choice (`network_daily.py`; session 124): two operators, one flow |
| A day's demand used in the replay | Above zero and between half and twice the median of the six days around it | Fixed | `eia930_daily_demand`; ERW's choice (`grid_network_v3.md`, session 109) |
| Held day, twelve months | Every regular neighbour reported and no pair-day screened; a thin month holds under two thirds of its days | Fixed | `ba_supply_monthly`; ERW's choice (sessions 62 and 68) |
| Headline measure of imports | The sum of the reported ties; the range is shown when the three measures spread over 1 point of demand | Fixed | ERW's choice (`site/lib/basupply.ts`, `HEADLINE`, `SPREAD`) |
| Trace the power | Two steps; four largest second-step suppliers; in the replay, the month of the day shown | "Over:" "this day", "its month", "the year" | ERW's choice (`networkV3.ts`, `trace`) |
| Mix: an hour is used | Sources within 5 percent of the total (PJM 15 percent); no main source blank; a main source supplies at least 5 percent of generation | Fixed | ERW's choice (`generation_mix_hourly.md`); PJM's 15 percent is "the one in this method most open to another answer" |
| Mix: a month, a year | 90 percent of days complete; at most one month missing | "Year", "Month" chips | ERW's choice |
| Mix: an added factor | Drawn for a month when every local hour holds 20 days of it; a year, 300 | "Add factors" | ERW's choice |
| Emission factors | EIA's, per fuel and balancing authority, in lbs per kWh; a US factor where history is short | Fixed | EIA's workbooks, sheet "Notes"; EIA FAQ 74 |
| Carbon look-back | The latest hour within 7 days (Now and the ranking) | Fixed | ERW's choice (`Emissions.tsx`): EIA's CO2 often runs more than three days behind |
| California's join | 2025-12-16T08:00:00Z | Fixed | The owner's ruling (`eia930_caiso_break.md`) |
| Carbon-free | Nuclear, wind, solar, hydro; "other" is not | Fixed | ERW's choice (`clean_energy.md`): EIA does not always split geothermal and biomass from oil |
| Tightest hours | The 100 used hours of a year with the highest net load | "Year" chips | ERW's choice (`grid_stress.md`) |
| Evening ramp | Largest one-hour rise, hours starting 14:00 to 22:00 local; a rise the next hour takes back by more than half is not counted | Fixed | ERW's choice (`grid_stress.md`) |
| Dark and calm | Wind and solar under 10 percent of their installed capacity | Fixed | ERW's choice; capacity from EIA-860M |
| Impossible hour | Not used when over 25 percent from the median of the four hours around it, or outside one third to three times the grid's median | Fixed | ERW's choice (`impossible_hours.md`, rule A) |
| Degree days | Base 65 F, one airport per grid (ERCOT: KDFW) | Fixed | US convention; National Weather Service (`Conditions.tsx`) |
| California's evening | Afternoon: hours starting 12:00 to 14:00; evening peak: hours starting 17:00 to 20:00 | Fixed | ERW's choice (`california_reliability.md`) |
| Map areas | Each county to the code with the most customers, a utility's customers split evenly over its counties; simplified at 0.02 degrees | Fixed | EIA-861, 2025; Census county shapes, 2017; the even split is the ERW's one assumption |
| Ask ceilings | 10 questions an hour per address; 15 a day per visitor; USD 3 a day and USD 30 a month for the tools | Fixed for a visitor | ERW's choice (`docs/methods/ask_limits.md`), "for a person to rule on" |
| License day | 2026-10-21 | Fixed | The owner's ruling of 12 October 2026 (`docs/state/licenses_2026-10-21.md`). The branch's own status file still reads 2026-10-20; the working tree's is newer |

## 4. The cross-checks

| What is compared | Ours | Theirs | The gap | The reason | Where it is written |
|---|---|---|---|---|---|
| Sum of a grid's ties against net generation minus demand, 360 hours | Sum of ties | EIA's own balance | Mean absolute gap: ERCOT 1.6 MW, NYISO 0.4, ISO-NE 0.7; CAISO 3,199.1, MISO 1,397.9, PJM 2,042.1, SPP 978.1 | For the last four, reported interchange does not close EIA's balance: "a property of the data" | `grid_network.md`, "The sign" |
| Net imports as percent of demand, September 2025 to August 2026 | Sum of ties: CAISO 16.49, PJM -2.72, MISO 2.54 | Demand less net generation: CAISO 26.87, PJM -3.18, MISO 0.17 | CAISO: the balance "reads about ten points higher" | EIA's net generation for California fell in December 2025; why is not in the data held | `grid_network.md`, "Who supplies a grid" |
| The same, ties against EIA's total interchange | CAISO 16.49, ERCOT 0.07, ISO-NE 4.96, MISO 2.54, NYISO 11.82 | 16.49, 0.07, 4.96, 2.54, 11.81 | The same to the second decimal, but NYISO | Agree on the same days; PJM (-2.72 against -1.25) and SPP (-1.44 against -1.00) do not, with many days left out | Same |
| Newest complete hour, 13 October 2026, 07:57 UTC | The page's file: hour beginning 2026-10-11 03:00 UTC | EIA's API: the same; EIA's bulk file: the same | 0 hours; all three 53 hours behind the clock | The lag is EIA's | `grid_network.md`, "How far behind"; session 247 report, section 3 |
| California's generation, 888 hours from the join | EIA-930 total: 22,618 MW | CAISO's own: 24,358 MW | 1,740 MW; solar 944 MW, wind 473 MW | EIA's solar and wind read below CAISO's own | `eia930_caiso_break.md`, "The join" |
| California's intensity of generation, 6,657 hours | On CAISO's generation: 100.91 kg CO2/MWh | On EIA's generation: 110.80 | 7 to 11 percent lower by month | The denominator | Same |
| EIA's gas CO2 over CAISO's gas MWh | 0.4049 tCO2/MWh | EIA's own factor: 0.4051 | Inside the 2 percent the build allows | Same series from the join; the build stops if the ratio leaves the factor by more than 2 percent | Same |
| Carbon intensity on two denominators, 2026-08-26 to 2026-09-27 | EIA's workbook columns | The warehouse's rolling tables | Mean absolute 0.157 kg CO2/MWh (generation), 0.034 (demand); ERCOT and NYISO up to 22.7 and 38.2 on one day | EIA revised net generation after the rolling pull | `emissions.md`, "The check against session 32's version" |
| Trace, California over 2021 | 56,992,955 MWh from nine suppliers | By hand with pandas: 56,993,006 | Every share agrees to two decimals (BPAT 21.05 percent) | The file holds a day's average MW to one decimal | `grid_network_v3.md`, "Trace the power, checked by hand" |
| Trace, Texas, 12 to 19 February 2021 | SPP 84.6 percent (142,209 MWh), Mexico 15.4 percent (25,957 MWh) | The same sum by hand | A hundredth of a point | | `grid_network_v3.md`, "Days the rule would leave out" |
| Two operators, one tie: MISO to SPP, 15 February 2021 | MISO's report: 95,060 MWh | SPP's report: 95,390 MWh | 0.3 percent | Two reports of one flow | Same |
| Two sides of a tie, California 2021 | BANC as BANC reported it: 3,559,578 MWh | As California reported it: 3,297,404 MWh | The two figures, side by side | The two sides do not always agree; the trace reads the code that sorts first | `grid_network_v3.md` |
| CAISO's notices, days per year and type | The table's distinct days | CAISO's own summary pages | 214 of 232 cells match; 18 differ | CAISO counts declarations, the table counts days | `california_reliability.md`, section 1 |
| State mix groups against EIA's total | Groups plus "not itemized" | EIA's ALL | Largest difference 0.09 MWh | Rounding to three decimals | `generation_mix.md` |
| Every number on the screen against its table or file | 1,178 values on 42 addresses | The same values recomputed | 0 (the first run found 7: 3 were "-0", 4 were PJM's ties off by 1 MW) | EIA revised an hour between the page's read and the checker's | Session 237 report, "Checks" |
| Routes, mix, map, Ask panel | `check-routes` 185 of 185; `check-mix` 36 of 36; `check-network-map` 31 of 31; `check-ask-panel` 13 of 13 | | 0 failed | | Same |
| **Owed:** `check-network-v3.mjs` | 32 of 33, then 31 of 33; its two waits were corrected and not rerun | | 2 assertions that read the address back | The check read the address before the component wrote it in the tool's words | Session 237 report, "To finish" |
| **Owed:** `check-network-v3-hard.mjs`, `check-mix-v2.mjs`, `check-ask-ercot.mjs` | Not run | | Not known | The build lock was held; each may need a pin moved | Same |
| Also not run on the branch | The whole `check-values`, the whole python suite (204 modules), the clean-copy suite, Impeccable, AccessLint | | Not known | They are the landing's | Same |
| The exchange against an operator's own tie flows | no number held | no number held | no number held | No operator's tie-flow connector is built | `grid_network.md`: "Not built" |

## 5. What it cannot see, ranked by how much it moves the answer

The ranking is the ERW's reading for the question "what is this grid doing now". For another question the order changes.

1. **The present.** The exchange and the network are two days old. On 13 October 2026 at 07:57 UTC the newest complete hour was 53 hours behind the clock, in the page's file, EIA's API and EIA's bulk file alike. EIA publishes a local day's interchange on the second morning after it, so the lag runs between about 35 and about 59 hours. Demand is one to two hours behind. Generation by source is a day or more behind. The Now sentence therefore joins four numbers of up to four different hours, and names each hour.
2. **Anything inside a balancing authority.** EIA-930 reports totals between balancing authorities only. Flows by line, transmission limits, congestion, outages and reserves are not in the file. No number held.
3. **A balance that closes.** For CAISO, MISO, PJM and SPP the sum of the ties does not equal net generation minus demand: mean gaps of 3,199.1, 1,397.9, 2,042.1 and 978.1 MW over 360 hours. California's import share is 16.49 percent by its ties and 26.87 percent by the balance.
4. **What a MWh used here emitted at the margin.** Carbon figures are averages of generation inside the grid. Imports enter only the "of demand" figure. What one more MWh of load would emit is not computed. No number held.
5. **California's mix in Now.** It is withheld: EIA-930's California total read 1,740 MW below CAISO's own over 888 hours. The Mix view's other views read CAISO's own supply from the join.
6. **Prices for three grids, and more from 21 October.** PJM's prices are licensed and never shown. MISO's own files are paused since 4 October 2026. From 2026-10-21 the rows of ISO-NE, MISO and NYISO read "license needed" in the tables their operators decide (section 6, question 8).
7. **Minutes.** Every figure is an hourly mean, and the replay a daily mean. Five-minute ramps and flows are not held. CAISO's five-minute battery series is averaged to hours. No number held for what the hour hides.
8. **Revisions.** EIA calls the data preliminary. One revised day moved ERCOT's and NYISO's intensity by up to 22.7 and 38.2 kg CO2/MWh; one revised hour moved four of PJM's ties by 1 MW during a check.
9. **Unscreened hours.** The rule for impossible values is applied by day and in the derived tables, not to an hour of interchange: the live week draws hourly interchange as EIA gives it. EIA's reported columns hold 16 impossible hours of PJM's demand since 2018, among them 1,527,760,000, 2,147,480,000 and 431,044,000 MW on 19 October 2021. The Lower 48's sum can hold a faulty hour and pass.
10. **Solar behind the meter.** It lowers demand and is not a source. EIA reports no solar for NYISO. Small-scale solar is in no fuel group. No number held for its size.
11. **Demand outside the seven ISO grids.** In the live week the other balancing authorities have no demand, so no share of demand. The replay holds daily demand for 54 of the network's balancing authorities.
12. **History by the hour.** Hourly interchange is held from 2026-09-13, plus two story windows (2021-02-07 to 2021-02-24 and 2025-06-20 to 2025-06-28). Before that the replay is daily, and 47 of its days are blank in EIA's file, most of them in late 2025.
13. **True boundaries.** The map's areas are derived: 44 of the 70 grids have an area, 26 have none, and 40 counties of the lower 48 are blank. One year, 2025, stands for every year shown.
14. **Hours lost to source faults.** PJM's mix rests on a 15 percent tolerance (2,689 hours differ by 5 to 15 percent). New York loses 2022 and 2023 in "How clean, and when" to 3,147 hours of misfiled nuclear. SPP loses 2,568 stale hours in the stress figures.

## 6. The ten hardest questions

### 1. Is this live?

No. Demand is one to two hours behind. The exchange and the network were 53 hours behind at 07:57 UTC on 13 October 2026, and run between about 35 and about 59 hours behind by the hour of the day. EIA's API and EIA's bulk file were at the same hour, so the lag is the publisher's. Closing it needs each operator's own real-time tie flows: seven connectors, four of them needing a license or a ruling. Not built.

### 2. Do your flows add up?

For three grids, yes: the sum of the ties is within 2 MW of net generation minus demand for ERCOT (1.6), NYISO (0.4) and ISO-NE (0.7). For four, no: CAISO 3,199.1 MW, PJM 2,042.1, MISO 1,397.9, SPP 978.1, mean absolute gap over 360 hours. The tool shows the ties as reported and does not force a balance.

### 3. How much of California's power is imported?

By its ties, 16.49 percent of demand (September 2025 to August 2026); by EIA's total interchange, 16.49; by demand less net generation, 26.87. The tool's headline is the ties. The balance overstates imports since EIA's California generation fell in December 2025 (January 2026: 348 GWh a day against 457 GWh in January 2025). Why EIA's figure fell, the tool does not know.

### 4. Can it show congestion, a line's limit or an outage?

No. The source holds totals between balancing authorities. A hub price ring is the only price signal, for the grids with a public price; a hub is not a site. Line flows and limits would need each operator's data.

### 5. Is the map the balancing authorities' territory?

No. It is the ERW's derivation from counties, and says so in its frame. Three pulls reached no published boundary. 3,067 of 3,107 counties are drawn; 1,126 counties are served by utilities of several codes and went to the largest, with a smallest winning share of 33 percent. Nothing on the page is computed from the areas.

### 6. Is the carbon number what my load would emit?

No. It is the grid's average: CO2 generated over net generation, or CO2 consumed over demand with imports counted. It is not marginal. The choice of denominator alone moves California's figure from 110.80 to 100.91 kg CO2/MWh. A marginal figure would need the plant that meets the next MWh, which the tool does not hold.

### 7. Does "Trace the power" say where Texas's power came from in the storm?

It says which ties carried it: over 12 to 19 February 2021, SPP 84.6 percent (142,209 MWh) and Mexico 15.4 percent (25,957 MWh) of Texas's net inflow. These are physical flows, not contracts, and not where the power was generated. It does not show load shed or plant outages.

### 8. Where are PJM's and MISO's prices, and what goes dark on 21 October?

PJM's license says "non-members are specifically prohibited from republishing data", so no PJM price is shown. MISO's terms forbid automated access; its pulls are paused since 4 October 2026. The four numbers of Now, the Network and the Exchange read EIA's tables, which are public: the license table lists `/grid`, `/network` and `/emissions` among the pages no license touches. What does go dark is in the folded blocks: `price_board_latest` and `price_board_peak_offpeak` (ISO-NE, MISO, NYISO rows) in "What it costs"; `clean_energy_hourly` and `clean_energy_summary` (the same three) in "How clean, and when"; `energy_projects` (ISO-NE) in "What is being built"; and `datacenter_facilities` and `news_index` whole. That table was written from `main`'s pages; the branch draws the same blocks inside the tool.

### 9. How do you know the screen matches the publisher?

A script recomputed 1,178 values on 42 addresses of the tool and all matched. Its first run found 7 mismatches: 3 were a zero printed as "-0", 4 were PJM's ties differing by 1 MW because EIA revised an hour mid-check. Four browser checks are still owed, and no check compares the exchange with an operator's own figures. The register of known faults holds 28 faults in source data: 11 fixed, 8 held for approval, 9 open.

### 10. Can the Ask panel be wrong?

Yes. For ERCOT, 100 of 100 test questions passed on 8 October 2026, each asked once; the note says "A pass here does not say that every asking passes". A question cost USD 0.0171 on those 100. For the six other grids and the Lower 48, no evaluation figure was found in the files read: no number held. Every number in an answer is checked against a query's result before it is shown.

## 7. A five-minute demo, click by click

This path was written from the code and the check scripts on the branch. It was not clicked through in a browser.

The page is in review. On the machine the demo runs from, open the internal view first: `https://erw-flame.vercel.app/internal/open` (or the older link, `https://erw-flame.vercel.app/internal/unlock?token=<your internal token>`). Then `https://erw-flame.vercel.app/grid`. Before the branch lands that address shows the older page; the tool can then be shown only from a local build of the branch (`cd site && npm run build && npx next start -p 3237`).

**Say this first:** every number here is a public hourly report, mostly EIA's; each one names its hour; nothing is forecast.

### Minute 0 to 1: Now

1. The page opens on **ERCOT**, tab **Now**. The title reads "ERCOT: Electric Reliability Council of Texas".
2. Read the sentence aloud. It names demand in the latest hour EIA has published, the same hour a week earlier, the largest source, the net export or import over ERCOT's reporting ties, and the kg of CO2 per MWh. No fixed number can be given: the screen shows the latest data.
3. Point at the three headline numbers: **Demand**, **Net export** (or **Net import**), **Carbon intensity**. Read the hour under each. Say that the three hours differ, and that the exchange is about two days old because EIA publishes it so.

### Minute 1 to 2: Exchange

1. Click the tab **Exchange**. The address becomes `/grid?grid=ercot&view=exchange`.
2. Read the headline row: **Net export** or **Net import**, **Ties reporting**, **Largest flow**. In the branch's snapshot ERCOT has 2 ties, with Southwest Power Pool (SWPP) and Mexico's operator (CEN).
3. Scroll to **Over the last twelve months**. Read the sentence "Net imports were ... percent of ERCOT's demand". The methods note held 0.07 percent for September 2025 to August 2026 and 0.08 percent for 2025-10 to 2026-09; the screen shows the newest twelve months. Say: Texas is nearly an island.

### Minute 2 to 4: Network

1. Click the tab **Network**. The 3D network is the shape shown; ERCOT's panel is open. The lead names the balancing authorities drawn: 70 in the branch's snapshot.
2. Under "Watch:" click **Texas during Uri**. The line "Showing:" reads "Texas during Uri, 2021-02-07 to 2021-02-24", with "3,898 read from the other side's report" and "191 hours of demand not reported". An hour takes 0.7 seconds and the story holds 432 hours, so click **Pause** after a few seconds.
3. In **A day since 2019:** choose `2021-02-15`. The moment reads "2021-02-15, EIA's Eastern day (the day's average MW)". The panel should read "Net imports this day: 886 MW on average, 1.77 percent of its 50,152 MW demand". The year's file holds 779.2 MW in from SWPP, 107.1 MW in from CEN and a demand of 50,151.8 MW; the panel adds, divides and rounds them. Carbon intensity of generation that day: 445 kg CO2/MWh (444.8 in the file).
4. Click **Prices: off**. It turns on. One ring appears, on ERCOT: in 2021 ERCOT is the only grid with a public price held. The panel reads "Hub price this day 6,704.67 USD/MWh" and "Over the period shown: -9.48 to 9,002.04 USD/MWh, 365 days held." PJM never has a ring.
5. In the panel click **Trace the power**. It opens on "its month". Read the suppliers and their shares aloud. Where Mexico's operator is listed, the panel says nothing is traced through it. The month's own shares are not held in a document; for 12 to 19 February the methods note holds SPP 84.6 percent and Mexico 15.4 percent.
6. Click **Map**. The frame draws 44 areas and carries the label "Derived map: each county is given to one balancing authority from the utilities that serve it (EIA-861). It is not a boundary any balancing authority or agency published."
7. The address now holds the whole view: `/grid?grid=ercot&view=network&net=day&t=2021-02-15&node=ERCO&prices=1&trace=1&shape=map`. Opening it restores the same moment, not playing. Say: any view can be shared as a link.

### Minute 4 to 5: Clean, then Ask

1. Click the tab **Clean**. In **Carbon intensity now, ranked** ERCOT's row is the highlighted one. Read its two figures, "Of generation" and "Of demand", and the hour beside them. Say that the two differ by trade, and that both are averages.
2. Click the tab **Ask**. The box is labelled **Ask ERCOT**; the button reads **Ask**. A question sent here is a model call (USD 0.0171 a question on the test set of 8 October 2026). The answer appears below the box with its source.

**With a sixth minute:** click **Mix**, then **How hard the system works** in the second row. As built on 5 October 2026, Texas's largest one-hour evening ramp ran from 7.9 to 19.1 percent of the year's peak demand over 2019 to 2025 (15,940 MW, starting 16:00 on 19 January 2025). Solar ran at 71.1 percent of its installed capacity in Texas's 100 tightest hours of 2019 and at 5.0 percent in those of 2025. The table may have been rebuilt since: read the screen's own figures.

### If something goes wrong

- **"This tool is in review" in place of the tool:** the internal view is not open in this browser.
- **"This browser cannot draw 3D":** click **Map**, or read the panel through "Show a balancing authority:".
- **A line "(the daily snapshot: the hourly copy was not reachable)":** the page is drawing the committed file; its numbers are the daily build's.
- **A panel price reads "paused while terms are reviewed" or "Not shown: PJM's prices are licensed":** that is the gate, working.

## Where the numbers in this document come from

"Branch" is `origin/wip/237-grid` at `13dfe385`; "main" is the checkout's copy of the methods notes, which the branch does not change (the branch's only changed methods note is `generator_earns_algorithm.md`).

| Number | File (ref) | Section |
|---|---|---|
| Eight grids, six views, the address words, the redirects | `site/lib/gridtool.ts`, `site/next.config.ts` (branch) | `GRID_CHOICES`, `GRID_VIEWS`, `redirects()` |
| 70 nodes, 157 pairs, 168 hours, built 2026-10-12T14:33:43Z; ERCOT's 2 ties | `site/data/grid_network.json` (branch) | counted in the file |
| 16 regional sums not drawn; 48 hours; 0.9; the 90th percentile | `warehouse/derived/network_hourly.py` (main) | `REGIONS`, `PULL_HOURS`, `FULL_SHARE`, `newest_full_hour` |
| 360 hours; 1.6, 0.4, 0.7, 3,199.1, 1,397.9, 2,042.1, 978.1 MW | `docs/methods/grid_network.md` (main) | "The sign, checked against the data" |
| 600 steps, seed 42 | `docs/methods/grid_network.md`; `warehouse/derived/grid_network.py` (main) | "The snapshot and the page"; `layout` |
| Sphere size, link width, ring weights, 0.7 seconds an hour | `site/app/network/Network.tsx`, `site/lib/networkV3.ts` (branch) | `size`, `linkWidth`, `priceWeight`, the play interval |
| 53 hours; about 35 to about 59 hours; seven connectors, four needing a license | `docs/methods/grid_network.md` (main); `archive/sessions/SESSION_247_REPORT.md` | "How far behind the newest hour is"; section 3 |
| 16.49, 26.87, 16.49, 0.07, 4.96, 2.54, 11.82, 11.81, -2.72, -1.25, -3.18, -1.44, -1.00, 0.17; 348 and 457 GWh | `docs/methods/grid_network.md` (main) | "Who supplies a grid (session 68)" |
| 0.08 percent (ERCOT, 2025-10 to 2026-09) | `docs/methods/grid_network.md` (main) | "From the old page", three measures table |
| 10 deviations, 500 MWh; 5 percent; 25 percent; one third to three times; 16 hours of PJM | `docs/methods/impossible_hours.md` (main) | "The rule"; "What it leaves out" |
| 54 balancing authorities with daily demand; half to twice the median; 47 blank days | `docs/methods/grid_network_v3.md`, `grid_network.md` (main); `site/public/network/daily_index.json` (branch) | "The replay's share of demand"; "The replay: what a day is" |
| 56,992,955 and 56,993,006 MWh; 84.6 and 15.4 percent; 95,060 and 95,390 MWh; 3,559,578 and 3,297,404 MWh | `docs/methods/grid_network_v3.md` (main) | "To launch-ready (session 124)" |
| 5 and 15 percent; 2,689 hours; 90 percent of days; 20 and 300 days | `docs/methods/generation_mix_hourly.md` (main) | "Which hours are used"; "The controls" |
| 0.09 MWh | `docs/methods/generation_mix.md` (main) | "state_generation_mix_monthly" |
| The intensity formulas; 0.157 and 0.034; 22.7 and 38.2 | `docs/methods/emissions.md` (main) | "carbon_intensity_hourly, ..."; "The check against session 32's version" |
| 2025-12-16T08:00:00Z; 22,618, 24,358, 1,740, 944, 473 MW; 110.80 and 100.91; 0.4049 and 0.4051; 2023-11-01 to 2025-12-02 | `docs/methods/eia930_caiso_break.md` (main) | "The join"; "The late hours" |
| 7,869 hours without hydro | `docs/methods/known_data_faults.md` (main); `site/data/carbon_left_out.json` (branch) | "Session 118"; `hydro_gap` |
| 3,147 hours of New York's nuclear | `docs/methods/clean_energy.md` (main) | "The hours" |
| 100 hours; 10 percent; 14:00 to 22:00; 2,568 hours; 15,940 MW; 19.1, 71.1 and 5.0 percent | `docs/methods/grid_stress.md` (main) | "The definitions"; "As built on 5 October 2026" |
| 214 of 232; 18; 2018-07-01; 2025-08-24; the evening hours | `docs/methods/california_reliability.md` (main) | sections 1 and 2 |
| 44 of 70; 26; 3,067 of 3,107; 1,126; 33 percent; 40 counties; 0.02 degrees; the label's words | `docs/methods/grid_network.md` (main); `site/public/network/ba_boundaries.json` (branch) | "The derived map: counties"; `provenance` |
| 432 hours; 3,898; 191; the story's window | `site/public/network/story_uri_2021.json` (branch) | `hours`, `missing`, `window` |
| 779.2, 107.1, 50,151.8 MW; 444.8; 6,704.67; -9.48; 9,002.04; 365 days | `site/public/network/daily_2021.json` (branch) | the row of 2021-02-15; `hub_prices.ERCO` |
| 886 MW and 1.77 percent | arithmetic on the three figures above, as `site/scripts/check-network-v3.mjs` (branch) does it | check "a" |
| 1,178 of 1,178 on 42 addresses; 7 mismatches; 185, 36, 31, 13; 32 and 31 of 33; 204 modules | `runs/session249/code_report_237.md` (the branch's `archive/sessions/SESSION_237_REPORT.md`) | "Checks, with exit codes"; "To finish" |
| 28 faults: 11 fixed, 8 held for approval, 9 open | `site/data/data_faults.json` (branch), built 2026-10-05 | `faults`, `by_resolution` |
| 100 of 100; USD 0.0171 | `docs/methods/ask_ercot.md` (main) | "A day's hours as a line, and two slow answers (session 161)" |
| 10 an hour; 15 a day; USD 3 and USD 30 | `docs/methods/ask_limits.md` (main) | "What happens to a question"; "The configuration" |
| 2026-10-21; the pages no license touches; the tables held by grid | `docs/state/licenses_2026-10-21.md` (working tree, session 248) | "Read these first"; "The pages that go dark"; "The pages no license touches" |
| PJM's sentence; MISO's pause of 4 October 2026 | `docs/licenses.md`, `docs/methods/miso_pause.md` (main) | "The publishers"; opening paragraph |
| `https://erw-flame.vercel.app`, the two internal addresses, port 3237 | `runs/session249/code_report_237.md`; `docs/battery_game_demo.md` (main) | "What to review", "To finish"; opening lines |

Three places where files disagree, and which is newer:

- **The count of pair-days the day rule leaves out.** `grid_network_v3.md` (session 124) gives 2,732, of which 1,911 are kept as confirmed by both sides and 815 stay out. `grid_network.md` (the index as built 2026-10-08) gives 2,740 and 1,918, with 704 left out of the files. The branch's `daily_index.json` (built 2026-10-12T15:10:06Z) gives 2,743 and 1,920, with 704 screened over its eight years, and is the newest.
- **The floor of that rule.** `grid_network.md` writes "at least 500 MWh"; `grid_network_v3.md` writes "at least 5,000 MWh". `impossible_hours.md` holds both: "A deviation under 500 MWh counts as 500, so no day is left out for standing less than 5,000 MWh from its pair's median."
- **CAISO's notices.** `california_reliability.md` (session 58) gives 1,900 rows to 2025-04-30. Session 247's report gives 1,906 rows to 8 October 2026, and is the newer.

Read and not used: `docs/methods/demand_weather.md` is the method of `/demand`, not of any view of this tool. The temperature in "yesterday" is the National Weather Service's hourly observation at one airport (`weather_obs_hourly`).
