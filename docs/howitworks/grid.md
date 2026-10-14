# How it works: the Grid tool

- **Address:** `/grid`, with the grid and the view in the address, for example `/grid?grid=ercot&view=mix` (production: `https://erw-flame.vercel.app/grid`).
- **Status:** in review, like every page of the site (`site/lib/release.ts`). A visitor sees the in-review page; a demo needs the internal view (section 7).
- **Written from:** `main` at commit `34b468fa`, on 2026-10-13 (session 260). The tool landed that morning as `01161064` (session 237, in one push with sessions 238 to 240; checks passed 10:57 UTC, production served it from 10:58 UTC). Session 241 then moved the network's colors to the brand's tokens (`be166fdf`). This note replaces the one session 249 wrote from the branch before the landing.
- **What the landing changed for an old link:** `/network`, `/mix`, `/emissions`, `/mix/clean`, `/mix/stress`, `/mix/v2`, `/network/v3` and the seven `/grid/<iso>` addresses answer with one permanent redirect into a view of this page, the query carried over (`site/next.config.ts`).

## 1. What it is for, and for whom

- **The question.** What is a US grid doing: what it used, what generated it, what it exchanged with its neighbours and how much CO2 it carried, in the latest hours held and since 2018.
- **What it gives.** One page with a picker of eight (ERCOT, CAISO, PJM, MISO, NYISO, ISO-NE, SPP and US48, the Lower 48 states) and six views.

| View | The question it answers | For whom |
|---|---|---|
| Now | What did this grid use, generate, exchange and emit in the latest hours held? | Anyone opening the tool |
| Network | Which balancing authorities exchange power, how much, and who supplies whom? The live week, two stories, any day since 2019, as a 3D network or a map | An investor reading a region; an operator checking a neighbour |
| Mix | What generates the power: now, the average day of a month, year after year, the hardest hours | An investor in generation or storage |
| Clean | How much CO2 a MWh carries, now and since 2018, and how clean each hour is | A buyer of clean power; a datacenter siting team |
| Exchange | This grid's ties in the newest complete hour, the week, and twelve months by neighbour | An operator; an analyst of imports |
| Ask | A question in words, answered from the warehouse's tables | A reader who does not know which table holds the answer |

- **What it is.** Measurement from public hourly reports, mostly EIA's Form EIA-930. Every number names its hour.
- **What it is not.** Not a forecast, not a dispatch model, not real time (section 5, item 1), not a reliability study. It shows flows between balancing authorities, not flows on lines.
- **Where it came from.** Ten pages folded into one in session 237. Its report lists every block of every old page and where it stands now; nothing was dropped.

## 2. The model, in numbered steps

This tool has no financial model. Its "model" is the path from a publisher's hourly figure to the number on the screen.

1. **The sources.** EIA-930 gives hourly demand, the day-ahead demand forecast, net generation by energy source and interchange between pairs of balancing authorities. EIA's per-balancing-authority workbooks give hourly CO2 estimates from 2018-07-01. CAISO's own supply by fuel is read for California from 2025-12-16.
2. **The hour.** EIA stamps an hour by its end, in UTC. The ERW stores the hour's start (`ts_utc`). EIA's megawatthours per hour are read as the hour's mean MW.
3. **Completeness.** A generation or emissions day is written only when it holds all 24 hours. An interchange pair-day missing an hour is not written. Nothing is filled; every gap is a row of `warehouse/metadata/run_status.csv`.
4. **Nodes and links.** Each balancing authority that reports interchange in the week is one node, and each pair is counted once: 70 nodes and 157 pairs in the snapshot on `main` (`site/data/grid_network.json`, built 2026-10-13T14:31:46Z). EIA's 16 regional and country sums are not nodes.
5. **Which report of a pair.** The flow is read from the balancing authority whose code sorts first, as it reported it. In an hour it did not report, the other side's report is used with the sign flipped. An hour neither reported is blank.
6. **The sign.** Positive interchange means the reporter exports. Checked against net generation minus demand for the seven ISO grids over 360 hours (section 4).
7. **A grid's net export (Now, Exchange).** The sum of the grid's reporting ties in one hour, signed from its side. A negative sum is written as a net import, with its own check key.
8. **The newest complete hour.** The hourly builder ends the week at the latest hour in which at least 90 percent as many pairs reported as in a fully reported hour. The page then shows the newest hour every reporting pair holds; a pair silent for the last 48 hours of the week is not waited for.
9. **The refresh.** Every hour a job pulls the 48 hours of interchange ending at EIA's own newest period, and 48 clock hours of demand for the seven ISO grids, and writes one object to public storage. Now and Exchange read that object on each request; the page draws the committed file when the object is not whole or is older, and says so.
10. **The four numbers of Now.** Demand: the latest hour held in the last nine days, and the same hour a week earlier. The mix: the latest hour that holds EIA's total net generation, each source as EIA names it. The exchange: step 7 at step 8's hour. Carbon: the latest hour EIA has estimated in the last seven days. So the sentence joins up to four different hours and names each.
11. **The drawing (Network).** Positions are a 3D force layout computed once per daily build (600 steps, seed 42). Sphere size is demand (the seven ISO grids) or the week's interchange volume (the others); color is carbon intensity of generation; link width and particle speed follow the hour's MW.
12. **The replay.** A day since 2019 is drawn from EIA-930's daily interchange: the Eastern day's MWh over that day's hours, so a day draws on the scale of an hour. The index on `main` runs from 2019-01-01 to 2026-10-11.
13. **Days no tie can carry.** A pair-day further than 10 median absolute deviations from the pair's own median is left blank; a deviation under 500 MWh counts as 500. The replay keeps such a day when both sides reported it and agree within 5 percent.
14. **Twelve months by neighbour.** `ba_supply_monthly` holds three measures of a grid's net imports: the sum of its ties, EIA's total interchange, and demand less net generation. The sum of the ties is the headline.
15. **Trace the power.** For the grid selected: the neighbours that supplied it on net over the period, largest first, and for each of those its own four largest suppliers. Nothing is traced through Mexico's operator.
16. **The mix over months and years (Mix).** An hour is used when its total is held and positive, its sources add up to within 5 percent of the total (PJM: 15 percent), and no main source is blank. A month is written when at least 90 percent of its days are complete; a year when at most one month is missing.
17. **Carbon intensity (Clean).** Of generation: EIA's CO2 generated times 1,000 over net generation, kg CO2 per MWh. Of demand: EIA's CO2 consumed (generated plus imported minus exported) times 1,000 over demand.
18. **California.** From the hour starting 2025-12-16T08:00:00Z California's generation is CAISO's own; EIA's CO2 stays the numerator. EIA-930's California generation by fuel is not drawn in Now: the block says it is withheld.
19. **How hard the system works (Mix).** Net load is demand less wind less solar. The evening ramp is the largest one-hour rise of net load between the hours starting 14:00 and 22:00 local. The tightest hours are the 100 with the highest net load in a year.
20. **Ask.** ERCOT is asked through its own profile; the six other grids through the general chat scoped to that grid; the Lower 48 through the general chat. Every number in an answer must come from a query of a table. A question in the address is placed in the box and never sent by the page.
21. **The license gate.** A block that reads a grid operator's own table keeps the gate it had: PJM's prices are not shown, MISO's read "paused while terms are reviewed", and from 2026-10-21 a "license needed" table shows those words in place of its numbers.
22. **The check.** `site/scripts/check-values.mjs` reads the tables and the snapshot itself and recomputes every keyed number on the page (section 4).

How fresh each layer is, as the files state it:

| Layer | Refreshed | Behind the clock | Where it is written |
|---|---|---|---|
| Demand of the seven ISO grids | Every hour | One to two hours | `docs/methods/grid_network.md`, "How far behind the newest hour is, and why" |
| Interchange (Exchange, Now's net export, the Network's live week) | Every hour | 53 hours on 13 October 2026 at 07:57 UTC; between about 35 and about 59 | the same |
| Generation by source | Daily | "A day or more after the hour" | `docs/methods/generation_mix.md` |
| Carbon intensity by hour | Daily, the last 3 days merged | Often more than three days | `docs/methods/emissions.md`, "Daily refresh" |
| The replay | With the daily tables | To 2026-10-11 on `main` | `site/public/network/daily_index.json` |
| The two stories | Pulled once | Fixed windows | `docs/methods/grid_network.md` |

## 3. Every assumption, its default and its source

"Fixed" means the reader cannot change it on the page. A line number is the line on `main` at `34b468fa`.

| Assumption or rule | Default | Where the user changes it | Source |
|---|---|---|---|
| Grid in view | ERCOT at `/grid`; the Lower 48 when an address opens Network, Mix or Clean and names no grid | The picker "Grid" (`grid=`) | ERW's choice: `DEFAULT_GRID` and `WHOLE_VIEWS`, `site/lib/gridtool.ts` lines 35 and 37. Awaits the owner's ruling (session 237 report, ruling 1) |
| View | Now | The tabs (`view=`) | ERW's choice: `gridPick`, `site/lib/gridtool.ts` line 62 |
| Hour stamp | The hour's start; Now prints it in the grid's local time, Exchange in UTC | Fixed | EIA-930 states the hour's end; `docs/methods/grid_network.md` |
| Sign of interchange | Positive: the reporter exports | Fixed | EIA-930, checked over 360 hours (`docs/methods/grid_network.md`, "The sign, checked against the data") |
| Pair rule | The code that sorts first; else the other side, sign flipped | Fixed | ERW's choice: each tie once, so two reports are not added |
| Live window, hourly pull, full share | 168 hours; 48 hours; 0.9 | The slider moves inside the window | `warehouse/derived/network_hourly.py` line 68 (`HOURS, PULL_HOURS, FULL_SHARE`) |
| A fully reported hour | The 90th percentile of the pulled hours' pair counts | Fixed | `newest_full_hour` in the same file (session 61). The methods note says "the median hour"; the code is newer and is what runs |
| Hour the page shows | The newest hour every reporting pair holds; a pair silent for 48 hours is not waited for | The slider (Network) | `completeHour`, `site/lib/networkV3.ts` line 70 (`quiet = 48`) |
| Page cache | One hour for the page; the snapshot is read on each request in Now and Exchange | Fixed | `revalidate = 3600`, `site/app/grid/page.tsx` line 29; `FRESH = 0`, `site/components/grid/NowView.tsx` line 30 |
| Look-back of Now | Demand 9 days, generation 34 days, carbon 7 days | Fixed | `site/components/grid/NowView.tsx` lines 46 to 48 |
| Layout | Force layout, 600 steps, seed 42 | Drag to rotate, scroll to zoom | `layout`, `warehouse/derived/grid_network.py` line 94 |
| Sphere size | 3 plus 22 times the square root of demand over the largest demand (ISO grids); 2 plus 10 times the square root of volume over the largest volume (others) | Fixed | ERW's choice: `site/app/network/Network.tsx` line 176 |
| Link width | 0.4 plus 3 times the square root of the flow's share of the period's largest flow | Fixed | ERW's choice: the same file, line 251 |
| Sphere color | Carbon intensity of generation; grey where not held | Fixed | `carbon_intensity_hourly`, `carbon_intensity_daily`; the colors are the brand's tokens (session 241) |
| Battery ring; price ring | Off; off | "Batteries: off"; "Prices: off" | `eia930_all_storage`, `caiso_battery_storage`; each ISO's hub price. PJM never has a ring |
| Shape | Network (3D) | The toggle "Map", "Network" (`shape=map`) | ERW's choice (session 180) |
| Playing speed | 0.7 seconds an hour; 0.18 seconds a day in the replay | "Play", "Pause" | `site/app/network/Network.tsx` line 296 |
| A replayed day | EIA's Eastern day, as the day's average MW | "A day since 2019:"; "Play the year" | `eia930_daily_interchange` |
| Screen for a day of interchange | 10 median absolute deviations, floor 500 MWh | Fixed | `screen`, `warehouse/derived/ba_supply.py` line 77; `docs/methods/impossible_hours.md`, rule C |
| A screened day kept | Both sides reported and agree within 5 percent | Fixed | `AGREE = 0.05`, `warehouse/derived/network_daily.py` line 128 |
| Headline measure of imports | The sum of the reported ties; the range is shown when the three measures spread over 1 point of demand | Fixed | `HEADLINE` and `SPREAD`, `site/lib/basupply.ts` lines 16 and 18 |
| Trace the power | Two steps; four largest second-step suppliers | "Over:" "this day", "its month", "the year" | `trace`, `site/lib/networkV3.ts` line 169 (`top = 4`) |
| Mix: an hour is used | Sources within 5 percent of the total (PJM 15 percent); no main source blank | Fixed | `docs/methods/generation_mix_hourly.md`; PJM's 15 percent is "the one in this method most open to another answer" |
| Carbon look-back in the ranking | The latest hour within 7 days | Fixed | `LOOK_BACK_DAYS = 7`, `site/components/grid/Emissions.tsx` line 27 |
| California's join | 2025-12-16T08:00:00Z | Fixed | The owner's ruling (`docs/methods/eia930_caiso_break.md`) |
| Carbon-free | Nuclear, wind, solar, hydro; "other" is not | Fixed | ERW's choice (`docs/methods/clean_energy.md`) |
| Tightest hours; evening ramp | The 100 hours of highest net load in a year; hours starting 14:00 to 22:00 local | "Year" chips | ERW's choice (`docs/methods/grid_stress.md`) |
| Impossible hour | Not used when over 25 percent from the median of the four hours around it, or outside one third to three times the grid's median | Fixed | `docs/methods/impossible_hours.md`, rule A |
| Map areas | Each county to the code with the most customers | Fixed | EIA-861, 2025; `site/public/network/ba_boundaries.json`. A derivation, labelled so in its frame |
| Ask ceilings | 10 questions an hour per address; 15 a day per visitor; USD 3 a day and USD 30 a month for the tools | Fixed for a visitor | `docs/methods/ask_limits.md`, "for a person to rule on" |
| License day | 2026-10-21 | Fixed | The owner's ruling of 12 October 2026: `site/data/license_status.json`, `docs/state/licenses_2026-10-21.md` |

## 4. The cross-checks

| What is compared | Ours | Theirs | The gap | The reason | Where it is written |
|---|---|---|---|---|---|
| Sum of a grid's ties against net generation minus demand, 360 hours | Sum of ties | EIA's own balance | Mean absolute gap: ERCOT 1.6 MW, NYISO 0.4, ISO-NE 0.7; CAISO 3,199.1, PJM 2,042.1, MISO 1,397.9, SPP 978.1 | For the last four, reported interchange does not close EIA's balance: "a property of the data" | `docs/methods/grid_network.md`, "The sign, checked against the data" |
| Net imports as percent of demand, September 2025 to August 2026 | Sum of ties: CAISO 16.49, PJM -2.72, MISO 2.54 | Demand less net generation: CAISO 26.87, PJM -3.18, MISO 0.17 | CAISO: about ten points | EIA's net generation for California fell in December 2025; why is not in the data held | the same, "Who supplies a grid" |
| The same, ties against EIA's total interchange | CAISO 16.49, ERCOT 0.07, ISO-NE 4.96, MISO 2.54, NYISO 11.82 | 16.49, 0.07, 4.96, 2.54, 11.81 | The same to the second decimal, but NYISO | PJM (-2.72 against -1.25) and SPP (-1.44 against -1.00) do not agree, with many days left out | the same |
| Newest complete hour, 13 October 2026, 07:57 UTC | The page's file: hour beginning 2026-10-11 03:00 UTC | EIA's API and EIA's bulk file: the same hour | 0 hours; all three 53 hours behind the clock | The lag is EIA's | the same, "How far behind the newest hour is, and why" |
| California's generation, 888 hours from the join | EIA-930 total: 22,618 MW | CAISO's own: 24,358 MW | 1,740 MW | EIA's solar and wind read below CAISO's own | `docs/methods/eia930_caiso_break.md`, "The join" |
| California's intensity of generation | On CAISO's generation: 100.91 kg CO2/MWh | On EIA's generation: 110.80 | 7 to 11 percent lower by month | The denominator | the same |
| Trace, California over 2021 | 56,992,955 MWh from nine suppliers | By hand: 56,993,006 | Every share agrees to two decimals | The file holds a day's average MW to one decimal | `docs/methods/grid_network_v3.md` |
| Trace, Texas, 12 to 19 February 2021 | SPP 84.6 percent (142,209 MWh), Mexico 15.4 percent (25,957 MWh) | The same sum by hand | A hundredth of a point | Rounding | the same |
| Two operators, one tie: MISO to SPP, 15 February 2021 | MISO's report: 95,060 MWh | SPP's report: 95,390 MWh | 0.3 percent | Two reports of one flow | the same |
| Every keyed number on the screen against its table or file, at the landing | 4,590 values on every page of the site | The same values recomputed | 0 | `check-values`, exit 0 | `archive/sessions/SESSION_237_REPORT.md`, "The landing" |
| The same on the site's last build of the morning | 4,637 values | Recomputed | 0 on the second run; 2 on the first | Two of MISO's interchange figures in Exchange: the run crossed 12:00 UTC and met a revised snapshot | `archive/sessions/SESSION_242_REPORT.md`, "Checks" |
| The Network view in a browser | `check-network-v3.mjs` | | 33 of 33 at the landing | It was 32 and 31 of 33 on the branch: the check read the address too early | `archive/sessions/SESSION_237_REPORT.md` |
| The mix through its redirects; the old mix check rewritten | `check-mix.mjs` 36 of 36; `check-mix-v2.mjs` 46 of 46 | | 0 failed | | the same; `archive/sessions/SESSION_241C_REPORT.md` |
| ERCOT's Ask panel, recorded replies, no model call | `check-ask-ercot.mjs` | | exit 0 | | `archive/sessions/SESSION_241B_REPORT.md` |
| Not run since the landing, by any report read | `check-network-v3-hard.mjs`; `check-network-map.mjs` (31 of 31 on the branch); `check-ask-panel.mjs` (13 of 13 on the branch) | | not known | Not in the landing's list | `archive/sessions/SESSION_237_REPORT.md`, "To finish" |
| The exchange against an operator's own tie flows | no number held | no number held | no number held | No operator's tie-flow connector is built | `docs/methods/grid_network.md` |

- **Not written.** The tool has no method note of its own, no replication file and no cross-check against a published figure of flows (session 237's report, "Not done"). Its methods are the notes of the pages it folded in.

## 5. What it cannot see, ranked by how much it moves the answer

The ranking is the ERW's reading for the question "what is this grid doing now". For another question the order changes.

1. **The present.** The exchange and the network are about two days old: 53 hours behind on 13 October 2026 at 07:57 UTC, in the page's file, EIA's API and EIA's bulk file alike. EIA publishes a local day's interchange on the second morning after it, so the lag runs between about 35 and about 59 hours. Demand is one to two hours behind. Generation by source is a day or more behind.
2. **Anything inside a balancing authority.** Flows by line, transmission limits, congestion, outages and reserves are not in EIA-930. No number held.
3. **A balance that closes.** For CAISO, PJM, MISO and SPP the sum of the ties does not equal net generation minus demand: mean gaps of 3,199.1, 2,042.1, 1,397.9 and 978.1 MW over 360 hours. California's import share is 16.49 percent by its ties and 26.87 percent by the balance.
4. **What a MWh used here emitted at the margin.** Carbon figures are averages. What one more MWh of load would emit is not computed. No number held.
5. **California's mix in Now.** It is withheld: EIA-930's California total read 1,740 MW below CAISO's own over 888 hours. The Mix view reads CAISO's own supply from the join.
6. **Prices for three grids, and more from 21 October.** PJM's prices are licensed and never shown. MISO's own files are paused since 4 October 2026. From 2026-10-21 the rows of ISO-NE, MISO and NYISO read "license needed" in the tables their operators decide (question 8).
7. **Minutes.** Every figure is an hourly mean, and the replay a daily mean. No number held for what the hour hides.
8. **Revisions.** EIA calls the data preliminary. One revised hour moved two of MISO's figures between a page's read and a checker's on 13 October 2026.
9. **Unscreened hours.** The rule for impossible values is applied by day and in the derived tables, not to an hour of interchange: the live week draws hourly interchange as EIA gives it.
10. **Demand outside the seven ISO grids.** In the live week the other balancing authorities have no demand, so no share of demand. The replay holds daily demand for 54 of the network's balancing authorities.
11. **History by the hour.** Hourly interchange is held from 2026-09-13, plus two story windows (2021-02-07 to 2021-02-24 and 2025-06-20 to 2025-06-28). Before that the replay is daily.
12. **True boundaries.** The map's areas are derived: 44 of the 70 grids have an area and 26 have none.
13. **Hours lost to source faults.** PJM's mix rests on a 15 percent tolerance (2,689 hours differ by 5 to 15 percent). New York loses 2022 and 2023 in "How clean, and when" to 3,147 hours of misfiled nuclear. SPP loses 2,568 stale hours in the stress figures.

## 6. The ten hardest questions

### 1. Is this live?

No. Demand is one to two hours behind. The exchange and the network were 53 hours behind at 07:57 UTC on 13 October 2026, and run between about 35 and about 59 hours behind by the hour of the day. EIA's API and EIA's bulk file were at the same hour, so the lag is the publisher's. Closing it needs each operator's own real-time tie flows: seven connectors, four of them needing a license or a ruling. Not built.

### 2. Do your flows add up?

For three grids, yes: the sum of the ties is within 2 MW of net generation minus demand for ERCOT (1.6), NYISO (0.4) and ISO-NE (0.7). For four, no: CAISO 3,199.1 MW, PJM 2,042.1, MISO 1,397.9, SPP 978.1, mean absolute gap over 360 hours. The tool shows the ties as reported and does not force a balance.

### 3. How much of California's power is imported?

By its ties, 16.49 percent of demand (September 2025 to August 2026); by EIA's total interchange, 16.49; by demand less net generation, 26.87. The tool's headline is the ties. The balance overstates imports since EIA's California generation fell in December 2025. Why EIA's figure fell, the tool does not know.

### 4. Can it show congestion, a line's limit or an outage?

No. The source holds totals between balancing authorities. A hub price ring is the only price signal, for the grids with a public price; a hub is not a site. Line flows and limits would need each operator's data.

### 5. Is the map the balancing authorities' territory?

No. It is the ERW's derivation from counties, and says so in its frame: "It is not a boundary any balancing authority or agency published." 3,067 of 3,107 counties are drawn; 1,126 counties are served by utilities of several codes and went to the largest. Nothing on the page is computed from the areas.

### 6. Is the carbon number what my load would emit?

No. It is the grid's average: CO2 generated over net generation, or CO2 consumed over demand with imports counted. It is not marginal. The choice of denominator alone moves California's figure from 110.80 to 100.91 kg CO2/MWh. A marginal figure would need the plant that meets the next MWh, which the tool does not hold.

### 7. Does "Trace the power" say where Texas's power came from in the storm?

It says which ties carried it: over 12 to 19 February 2021, SPP 84.6 percent (142,209 MWh) and Mexico 15.4 percent (25,957 MWh) of Texas's net inflow. These are physical flows, not contracts, and not where the power was generated. It does not show load shed or plant outages. On 15 February 2021 the replay shows Texas's net imports at 886 MW on average, 1.77 percent of its demand that day.

### 8. Where are PJM's and MISO's prices, and what goes dark on 21 October?

PJM's license says "non-members are specifically prohibited from republishing data", so no PJM price is shown. MISO's terms forbid automated access; its pulls are paused since 4 October 2026. The four numbers of Now, the Network and the Exchange read EIA's tables, which are public. What goes dark is in the blocks folded in from the grid pages: the hub prices of ISO-NE, MISO and NYISO (`price_board_latest`, `price_board_peak_offpeak`), the clean-hours figures of the same three (`clean_energy_hourly`, `clean_energy_summary`), ISO-NE's rows of `energy_projects`, and `datacenter_facilities` and `news_index` whole. The license table was written before the landing and lists those blocks under the old addresses `/grid/<iso>`; the tool draws the same blocks.

### 9. How do you know the screen matches the publisher?

A script recomputes every keyed number from its table: 4,590 of 4,590 on the whole site at the landing, and 4,637 of 4,637 later that morning, after a first run that met one revised hour (two of MISO's figures). The Network view's browser check passed 33 of 33. What no check does: compare the exchange with an operator's own figures. The register of known faults in source data holds 28: 11 fixed, 8 held for approval, 9 open.

### 10. Can the Ask panel be wrong?

Yes. For ERCOT, 100 of 100 test questions passed on 8 October 2026, each asked once; the note says "A pass here does not say that every asking passes". A question cost USD 0.0171 on those 100. For the six other grids and the Lower 48, no evaluation figure was found in the files read: no number held. Every number in an answer is checked against a query's result before it is shown.

## 7. A five-minute demo, click by click

The page is in review. On the machine you will show it from, open the internal view first: `https://erw-flame.vercel.app/internal/open`, paste the token and press **Open the internal view** (or `https://erw-flame.vercel.app/internal/unlock?token=<your internal token>`). Then `https://erw-flame.vercel.app/grid`.

This path was written from the page's code, its data files and its check scripts on `main` on 2026-10-13. It was not clicked through in a browser.

**Say this first:** every number here is a public hourly report, mostly EIA's; each one names its hour; nothing is forecast.

### Minute 0 to 1: Now

1. The page opens on **ERCOT**, tab **Now**. The title reads "ERCOT: Electric Reliability Council of Texas".
2. Read the sentence aloud. It names demand "in the hour starting ..., the latest EIA has published", the same hour a week earlier, the largest source, the net export or import over ERCOT's reporting ties, and the kg of CO2 each MWh carried. No fixed number is given here: the screen shows the latest data.
3. Point at the three headline numbers: **Demand**, **Net export** (or **Net import**), **Carbon intensity**. Read the hour under each. Say that the hours differ, and that the exchange is about two days old because EIA publishes it so.
4. Under them, **The mix in that hour**: the bar and the table of sources as EIA names them.

### Minute 1 to 2: Exchange

1. Click the tab **Exchange**. The address becomes `/grid?grid=ercot&view=exchange`.
2. Read the headline row: **Net export** or **Net import**, **Ties reporting**, **Largest flow**. ERCOT has 2 ties in the snapshot: Southwest Power Pool (SWPP) and Mexico's operator (CEN).
3. Scroll to **Over the last twelve months**. Read the sentence "Net imports were ... percent of ERCOT's demand". The methods note held 0.07 percent for September 2025 to August 2026; the screen shows the newest twelve months. Say: Texas is nearly an island.

### Minute 2 to 4: Network

1. Click the tab **Network**. The 3D network is the shape shown; ERCOT's panel is open.
2. Under "Watch:" click **Texas during Uri**. The story runs 2021-02-07 to 2021-02-24, 432 hours at 0.7 seconds an hour, so click **Pause** after a few seconds.
3. In **A day since 2019:** choose `2021-02-15`. The panel reads net imports of 886 MW on average, 1.77 percent of a demand of 50,152 MW. The year's file holds 779.2 MW in from SWPP, 107.1 MW in from CEN and a demand of 50,151.8 MW; the panel adds, divides and rounds them.
4. Click **Prices: off**. It turns on. One ring appears, on ERCOT: in 2021 ERCOT is the only grid with a public price held. The hub price that day reads 6,704.67 USD/MWh. PJM never has a ring.
5. In the panel click **Trace the power**. Read the suppliers and their shares aloud. For 12 to 19 February the methods note holds SPP 84.6 percent and Mexico 15.4 percent; the panel opens on the day's month, so read the screen.
6. Click **Map**. The frame carries the label "Derived map: each county is given to one balancing authority from the utilities that serve it (EIA-861). It is not a boundary any balancing authority or agency published."
7. The address now holds the whole view: `/grid?grid=ercot&view=network&net=day&t=2021-02-15&node=ERCO&prices=1&trace=1&shape=map`. Say: any view can be shared as a link.

### Minute 4 to 5: Clean, then Ask

1. Click the tab **Clean**. In **Carbon intensity now, ranked** ERCOT's row is the highlighted one. Read its two figures, "Of generation" and "Of demand", and the hour beside them. Say that the two differ by trade, and that both are averages.
2. Click the tab **Ask**. The box is labelled **Ask ERCOT**; the button reads **Ask**. A question sent here is a model call (USD 0.0171 a question on the test set of 8 October 2026). The answer appears below the box with its source. A box at the foot of every other view opens this view with the question placed in it, not sent.

**With a sixth minute:** click **Mix**, then **How hard the system works** in the second row. As built on 5 October 2026, Texas's largest one-hour evening ramp ran from 7.9 to 19.1 percent of the year's peak demand over 2019 to 2025 (15,940 MW, starting 16:00 on 19 January 2025). Solar ran at 71.1 percent of its installed capacity in Texas's 100 tightest hours of 2019 and at 5.0 percent in those of 2025. The table may have been rebuilt since: read the screen's own figures.

### If something goes wrong

- **"This tool is in review" in place of the tool:** the internal view is not open in this browser. Open `/internal/open` again.
- **"This browser cannot draw 3D":** click **Map**, or read the panel through "Show a balancing authority:".
- **A line "(the daily snapshot: the hourly copy was not reachable)":** the page is drawing the committed file; its numbers are the daily build's.
- **A panel price reads "paused while terms are reviewed" or "Not shown: PJM's prices are licensed":** that is the gate, working.
- **California's mix in Now reads withheld:** by ruling (session 118). Choose **Mix** for California's mix from CAISO's own supply.

## Where the numbers in this document come from

Every file is as it stands on `main` at `34b468fa`.

| Number | File | Section |
|---|---|---|
| Eight grids, six views, the address words, the redirects | `site/lib/gridtool.ts`, `site/next.config.ts` | `GRID_CHOICES`, `GRID_VIEWS`, `redirects()` |
| 70 nodes, 157 pairs, built 2026-10-13T14:31:46Z; ERCOT's 2 ties | `site/data/grid_network.json` | counted in the file |
| 16 regional sums not drawn; 168 and 48 hours; 0.9; the 90th percentile | `warehouse/derived/network_hourly.py` | `REGIONS`, line 68, `newest_full_hour` |
| 360 hours; 1.6, 0.4, 0.7, 3,199.1, 1,397.9, 2,042.1, 978.1 MW | `docs/methods/grid_network.md` | "The sign, checked against the data" |
| 600 steps, seed 42 | `warehouse/derived/grid_network.py` | `layout`, line 94 |
| Sphere size, link width, 0.7 and 0.18 seconds | `site/app/network/Network.tsx` | lines 176, 251 and 296 |
| 53 hours; about 35 to about 59 hours; seven connectors, four needing a license | `docs/methods/grid_network.md` | "How far behind the newest hour is, and why (session 247)" |
| 16.49, 26.87, 0.07, 4.96, 2.54, 11.82, 11.81, -2.72, -1.25, -3.18, -1.44, -1.00, 0.17 | `docs/methods/grid_network.md` | "Who supplies a grid (session 68)" |
| 10 deviations, 500 MWh; 5 percent; 25 percent; one third to three times | `docs/methods/impossible_hours.md`; `warehouse/derived/network_daily.py` | "The rule"; `AGREE` |
| The replay's first and last day; 54 balancing authorities with daily demand | `site/public/network/daily_index.json` | `first`, `last`, `with_demand` |
| 56,992,955 and 56,993,006 MWh; 84.6 and 15.4 percent; 142,209 and 25,957 MWh; 95,060 and 95,390 MWh | `docs/methods/grid_network_v3.md` | "To launch-ready (session 124)" |
| 5 and 15 percent; 2,689 hours; 90 percent of days | `docs/methods/generation_mix_hourly.md` | "Which hours are used" |
| The intensity formulas | `docs/methods/emissions.md` | "carbon_intensity_hourly, carbon_intensity_daily and carbon_intensity_monthly (derived)" |
| 2025-12-16T08:00:00Z; 22,618, 24,358, 1,740 MW; 110.80 and 100.91 | `docs/methods/eia930_caiso_break.md` | "The join" |
| 3,147 hours of New York's nuclear | `docs/methods/clean_energy.md` | "The hours" |
| 100 hours; 14:00 to 22:00; 2,568 hours; 15,940 MW; 19.1, 71.1 and 5.0 percent | `docs/methods/grid_stress.md` | "The definitions"; "As built on 5 October 2026" |
| 44 of 70; 26; 3,067 of 3,107; 1,126; the label's words | `docs/methods/grid_network.md`; `site/public/network/ba_boundaries.json` | "The derived map: counties"; `provenance` |
| 432 hours; the story's window | `site/public/network/story_uri_2021.json` | `hours`, `window` |
| 779.2, 107.1, 50,151.8 MW; 6,704.67 | `site/public/network/daily_2021.json` | the row of 2021-02-15; `hub_prices` |
| 886 MW and 1.77 percent | arithmetic on the three figures above, as `site/scripts/check-network-v3.mjs` does it | check "a" |
| 4,590 of 4,590; 33 of 33; 36 of 36; 31 of 31 and 13 of 13 on the branch | `archive/sessions/SESSION_237_REPORT.md` | "The landing"; "Checks, with exit codes" |
| 4,637 of 4,637; the two MISO figures | `archive/sessions/SESSION_242_REPORT.md` | "Checks" |
| 46 of 46; `check-ask-ercot.mjs` exit 0 | `archive/sessions/SESSION_241C_REPORT.md`; `archive/sessions/SESSION_241B_REPORT.md` | "Read these first"; the table of checks |
| 28 faults: 11 fixed, 8 held for approval, 9 open | `site/data/data_faults.json`, built 2026-10-05 | `by_resolution` |
| 100 of 100; USD 0.0171 | `docs/methods/ask_ercot.md` | "What the 100 questions said (8 October 2026)" |
| 10 an hour; 15 a day; USD 3 and USD 30 | `docs/methods/ask_limits.md` | "What happens to a question"; "The configuration" |
| 2026-10-21; the tables held by grid | `docs/state/licenses_2026-10-21.md`; `site/data/license_status.json` | "Read these first"; "Every \"license needed\" table" |
| PJM's sentence; MISO's pause of 4 October 2026 | `docs/licenses.md`; `docs/methods/miso_pause.md` | "The publishers"; opening paragraph |
| The labels and addresses of section 7 | `site/app/grid/page.tsx`, `site/components/grid/NowView.tsx`, `ExchangeView.tsx`, `AskView.tsx`, `Emissions.tsx`, `site/app/network/Network.tsx`, `site/lib/mixpage.ts` | the labels as written in the code |

- **Two files disagree, and which is newer.** `docs/methods/grid_network.md` says the builder compares an hour with "the median hour"; `warehouse/derived/network_hourly.py` uses the 90th percentile since session 61. The code is what runs.
- **A count that moves daily.** The pair-days the day rule leaves out: 2,745, of which 1,921 are kept as confirmed by both sides, in the index built 2026-10-13T15:09:42Z. The methods notes give older counts (2,732 and 2,740).
