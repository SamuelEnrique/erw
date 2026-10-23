# Review pack: the Grid tool

`/grid`, with the grid and the view in the address (for example `/grid?grid=ercot&view=network&shape=gravity`; production `https://erw-flame.vercel.app/grid`, opened after `https://erw-flame.vercel.app/internal/open`). The page is in review, like every page of the site (`site/lib/release.ts`). Written by session 266 from the branch `wip/266-grid-pack`, cut from `main` at `5b515cd0`, on 2026-10-14. It replaces the Grid tool's how-it-works note (session 260, from `main` at `34b468fa`), whose content is folded in here: its numbers, its sources table and its demo (the appendix).

- **What the landing of 13 October changed for an old link:** `/network`, `/mix`, `/emissions`, `/mix/clean`, `/mix/stress`, `/mix/v2`, `/network/v3` and the seven `/grid/<iso>` addresses answer with one permanent redirect into a view of this page, the query carried over (`site/next.config.ts`).
- **What session 266 added:** the age of the exchange's hour in the Now view's sentence, keyed; one line under the network saying the newest hour shown and its two-day lag, keyed; the gravity shape beside "Map" and "Network"; the replication files `site/public/grid/erw_2026_grid_replication.{csv,do,py}`; Ask told of the 14 months of hourly carbon.

## Against roadmap item 2 (session 381)

Roadmap item 2 (`docs/roadmap.md`, "Five tools sellable") is done for a tool when it has a method note signed by Samuel, a replication a reader can run, a cross-check table against published figures and a decisions block. Read on 21 October 2026 by session 381 from `wip/381-five-tools` (cut from `main` at `dc4d5ba6`); every exit code below is of a run that day, its output under `runs/chain_oct21/s381/` on the code machine. The checks that read the built site were not run: the local production build stopped twice on Supabase statement timeouts (the home page's required read), and each cell says so. No method note is signed: none of the five has a signature in any file. No page and no default figure was changed by this session. The parts below this section are the pack as written on 14 October and amended since; where a figure here differs, this section is the newer.

| Roadmap item 2 asks | What the tool has | Where | Today | What it lacks |
|---|---|---|---|---|
| A method note signed by Samuel | `grid_network.md` (the network, the gravity shape, one page with four tabs and Ask since session 299), `grid_network_v3.md` (the replay), `generation_mix_hourly.md` (Mix), `ask_limits.md` (Ask) | `docs/methods/grid_network.md` and the three beside it | not signed: no sign-off block, no signature in any file | Samuel's signature, and a block to sign in |
| A replication a reader can run | The network's figures for the hour shown (ties, net imports, generation, the gravity circles), written from the page's own reads, a do-file and its Python mirror | `site/public/grid/erw_2026_grid_replication.csv` (the hour 2026-10-12 03:00 UTC, written 14 October), `.do`, `.py`; `site/scripts/write-grid-replication.mjs` rewrites the CSV | The mirror on the committed CSV: exit 0. A CSV written today from the page's reads (`write-grid-replication.mjs`, exit 0: the hour 2026-10-19 03:00 UTC, 46 hours behind, 157 of 157 pairs, no generation row held for the hour, so the gravity figures read "not held"; the mirror on it: exit 0) against the page (`check-grid-replication.mjs`): not run on 21 October (no local build). The do-file: not run | A link from the page to the three files (a page change). The committed CSV is of 14 October and the page moves every hour: a reader compares a file with the page of its own snapshot only by writing it, which needs the repository |
| A cross-check table against published figures | New in session 381: a "Cross-checks" section in the decision tools' form, 11 rows (Form EIA-923's annual generation for five balancing authorities, EIA-930's own balance over 360 hours and in the hour shown, CAISO's own generation, EIA's bulk file, two operators' reports of one tie); part 4 below keeps 18 rows | `docs/methods/grid_network.md#cross-checks`; part 4 below | `tests/test_session381.py` holds the form; no page line counts the rows | A "Checked against" line on the page (a page change). Not held: an operator's own tie flows. ISO-NE, MISO and NYISO's EIA-923 totals are not quoted in any note, and `eia_annual_crosscheck_ba` is not in the live set, though question 5's answer says it is |
| A decisions block | "Decisions on this page" (`Decisions()`, `data-decisions="299"`): the owner's rulings of 18 October on questions 1, 2, 3, 4 and 6 | `site/app/grid/page.tsx` | On the page: in the code (`data-decisions="299"`); not read on a build on 21 October | Question 5's answer (session 323, the EIA-923 check) is not in the block: the pack says its words are the code machine's; a page change |
| The Grid tool one page | One page, four tabs (Network, Mix, Clean, Gravity), the grid picked once, Ask as a panel beside every tab; `/network` and `/mix` answer with a permanent redirect into a tab, `/ask` with a 307 to the panel; `/ask/ercot` stays its own page | `site/app/grid/page.tsx`, `site/next.config.ts`, `site/app/ask/page.tsx` | In the code (`next.config.ts` lines 100 to 104, `app/ask/page.tsx`); the redirects not read on a build on 21 October | Nothing that needs no ruling |

**On a built site (session 422, 21 October 2026).** A build at 15:22 UTC of `wip/422-tool-checks`, which is main with chain 019's branches not yet landed (`wip/461-combined`), served on localhost; outputs in `runs/chain_021/s422/` (git ignores `runs/`). `write-grid-replication.mjs` exit 0 (the hour 2026-10-19 03:00 UTC: 70 nodes, 157 ties, 7 demand rows, 0 generation rows), then `check-grid-replication.mjs` on that file exit 0: 60 values compared, 0 different. The mirror on the committed CSV, exit 0.

## 1. What it is for, and for whom

- **The question.** What is a US grid doing: what it used, what generated it, what it exchanged with its neighbours and how much CO2 it carried, in the latest hours held and since 2018.
- **What it gives.** One page with a picker of eight (ERCOT, CAISO, PJM, MISO, NYISO, ISO-NE, SPP and US48, the Lower 48 states) and six views.

| View | The question it answers | For whom |
|---|---|---|
| Now | What did this grid use, generate, exchange and emit in the latest hours held? One sentence leads | Anyone opening the tool |
| Network | Which balancing authorities exchange power, how much, and who supplies whom? The live week, two stories, any day since 2019, as a 3D network, a map or (session 266) the gravity shape | An investor reading a region; an operator checking a neighbour |
| Mix | What generates the power: now, the average day of a month, year after year, the hardest hours | An investor in generation or storage |
| Clean | How much CO2 a MWh carries, now and since 2018, and how clean each hour is | A buyer of clean power; a datacenter siting team |
| Exchange | This grid's ties in the newest complete hour, the week, and twelve months by neighbour | An operator; an analyst of imports |
| Ask | A question in words, answered from the warehouse's tables | A reader who does not know which table holds the answer |

- **What it is.** Measurement from public hourly reports, mostly EIA's Form EIA-930. Every number names its hour.
- **What it is not.** Not a forecast, not a dispatch model, not real time (part 6, item 1), not a reliability study. It shows flows between balancing authorities, not flows on lines.
- **Where it came from.** Ten pages folded into one in session 237 (the review of 12 October, item 6). Its report lists every block of every old page and where it stands now; nothing was dropped.

## 2. The model, step by step

This tool has no financial model. Its "model" is the path from a publisher's hourly figure to the number on the screen.

1. **The sources.** EIA-930's hourly demand, demand forecast, net generation by source and interchange between pairs of balancing authorities (`warehouse/connectors/eia930.py`, `eia930_interchange.py`); EIA's per-balancing-authority CO2 workbooks from 2018-07-01 (`eia930_emissions.py`); CAISO's own supply by fuel for California from 2025-12-16.
2. **The hour.** EIA stamps an hour by its end, in UTC; the ERW stores the hour's start (`ts_utc`). EIA's megawatthours per hour are read as the hour's mean MW (`hourly()` in `site/app/network/data.ts`).
3. **Completeness.** A generation or emissions day is written only when it holds all 24 hours; an interchange pair-day missing an hour is not written. Nothing is filled; every gap is a row of `warehouse/metadata/run_status.csv` (`warehouse/connectors/eia930_interchange.py`).
4. **Nodes and links.** Each balancing authority that reports interchange in the week is one node, and each pair is counted once: 70 nodes and 157 pairs in the snapshot (`pair_flows()` in `warehouse/derived/network_hourly.py`). EIA's 16 regional and country sums are not nodes (`EIA_REGIONS` in `site/app/network/Network.tsx`).
5. **Which report of a pair.** The flow is read from the balancing authority whose code sorts first, as it reported it; in an hour it did not report, the other side's report, sign flipped; an hour neither reported is blank (`pair_flows()` in `warehouse/derived/network_hourly.py`).
6. **The sign.** Positive interchange means the reporter exports. Checked against net generation minus demand for the seven ISO grids over 360 hours (`docs/methods/grid_network.md`, "The sign, checked against the data").
7. **A grid's net export (Now, Exchange).** The sum of the grid's reporting ties in one hour, signed from its side; a negative sum is written as a net import with its own check key (`tiesAt()` and `netValue()` in `site/lib/network.ts`).
8. **The newest complete hour.** The hourly builder ends the week at the latest hour in which at least 90 percent as many pairs reported as in a fully reported hour (`newest_full_hour()` in `warehouse/derived/network_hourly.py`); the page then shows the newest hour every reporting pair holds, not waiting for a pair silent 48 hours (`completeHour()` in `site/lib/networkV3.ts`).
9. **The refresh.** Every hour a job pulls the 48 hours of interchange ending at EIA's own newest period and 48 clock hours of demand for the seven ISO grids, and writes one object to public storage (`merge()` and `upload()` in `warehouse/derived/network_hourly.py`). Now and Exchange read it on each request (`fetchHourly()` and `pickSnapshot()` in `site/lib/network.ts`); the page draws the committed file when the object is not whole or is older, and says so.
10. **Now's sentence and four numbers.** Demand: the latest hour held in the last nine days and the same hour a week earlier. The mix: the latest hour that holds EIA's total net generation, the largest source named. The exchange: step 7 at step 8's hour, and (session 266) how many hours that hour began before the snapshot's refresh, keyed `net|lag|<hour>|<refresh>`. Carbon: the latest hour EIA has estimated in the last seven days. All in `NowView()` in `site/components/grid/NowView.tsx`; the sentence joins up to four different hours and names each.
11. **The lag under the chart (session 266).** One line under the network: the newest hour shown and the hours from its start to the snapshot's refresh, with why (EIA-930 publishes a local day's interchange on the second morning after it), computed in `NetworkView()` in `site/components/grid/NetworkView.tsx` and checked by `netValue()` in `site/lib/network.ts`.
12. **The 3D drawing (Network).** Positions are a force layout computed once per daily build, 600 steps, seed 42 (`layout()` in `warehouse/derived/grid_network.py`). Sphere size is demand (the seven ISO grids) or the week's interchange volume (the others); color is carbon intensity of generation; link width and particle speed follow the hour's MW (`size` and `colorOf()` in `site/app/network/Network.tsx`).
13. **The map (Map).** Each balancing authority is an area derived from counties (EIA-861), labelled as derived in its frame; ties are lines between the areas (`NetworkMap()` in `site/app/network/NetworkMap.tsx`, `readBoundaries()` in `site/lib/networkMap.ts`).
14. **The gravity shape (Gravity, session 266).** The Lower 48 at the center; each of the seven ISO grids a circle whose area is its net generation in the hour (`eia930_all_generation`, read in `liveExtras()` in `site/app/network/data.ts`), on a fixed bearing, at a distance that falls as its net imports over its generation rise: a net importer nearer the center, a net exporter farther out (`gravityLayout()` and `netImportAt()` in `site/lib/networkGravity.ts`, drawn by `NetworkGravity()` in `site/app/network/NetworkGravity.tsx`). The rule is written in `docs/methods/grid_network.md`, "The gravity shape (session 266)".
15. **The replay.** A day since 2019 from EIA-930's daily interchange: the Eastern day's MWh over that day's hours, so a day draws on the scale of an hour (`watchDay()` in `site/app/network/Network.tsx`; `easternHours()` in `site/lib/networkV3.ts`). The index runs from 2019-01-01 to 2026-10-11 (`site/public/network/daily_index.json`).
16. **Days no tie can carry.** A pair-day further than 10 median absolute deviations from the pair's own median is left blank, a deviation under 500 MWh counting as 500 (`screen()` in `warehouse/derived/ba_supply.py`); the replay keeps such a day when both sides reported it and agree within 5 percent (`AGREE` in `warehouse/derived/network_daily.py`).
17. **Twelve months by neighbour.** `ba_supply_monthly` holds three measures of a grid's net imports: the sum of its ties, EIA's total interchange, demand less net generation; the sum of the ties is the headline (`supplyOf()` and `HEADLINE` in `site/lib/basupply.ts`).
18. **Trace the power.** For the grid selected: the neighbours that supplied it on net over the period, largest first, and for each its own four largest suppliers; nothing traced through Mexico's operator (`trace()` in `site/lib/networkV3.ts`).
19. **The mix over months and years (Mix).** An hour is used when its total is held and positive, its sources add to within 5 percent of the total (PJM 15 percent) and no main source is blank; a month needs 90 percent of its days, a year at most one month missing (`docs/methods/generation_mix_hourly.md`; `MixView()` in `site/components/grid/MixView.tsx`).
20. **Carbon intensity (Clean).** Of generation: CO2 generated times 1,000 over net generation, kg CO2 per MWh; of demand: CO2 consumed over demand (`warehouse/derived/carbon_intensity.py`; `EmissionsParts()` in `site/components/grid/Emissions.tsx`).
21. **California.** From the hour starting 2025-12-16T08:00:00Z California's generation is CAISO's own in Mix and Clean; EIA's CO2 stays the numerator. EIA-930's California generation by fuel is not drawn in Now (`CaisoMixWithheld()` in `site/components/CaisoMixWithheld.tsx`). The gravity shape sizes CAISO by EIA-930's total, as every other grid (part 9, question 1).
22. **Ask.** ERCOT through its own profile; the six other grids through the general chat scoped to the grid; the Lower 48 through the general chat. Every number in an answer must come from a query of a table (`AskView()` in `site/components/grid/AskView.tsx`; the briefing `package/llms.txt`, exported to `site/lib/chat/spec.json` by `export_spec()` in `warehouse/chat/ask.py`). Since session 266 the briefing says the live set holds about 14 months of hourly carbon intensity.
23. **The license gate.** A block that reads a grid operator's own table keeps its gate: PJM's prices never shown, MISO's "paused while terms are reviewed", and from 2026-10-21 "license needed" in place of the numbers (`Num()` in `site/components/Num.tsx`, `site/lib/license.ts`).
24. **The check.** `site/scripts/check-values.mjs` reads the tables and the snapshot itself and recomputes every keyed number on the page; `site/scripts/check-grid-replication.mjs` compares the replication file's figures with the page, value by value.

How fresh each layer is, as the files state it:

| Layer | Refreshed | Behind the clock | Where it is written |
|---|---|---|---|
| Demand of the seven ISO grids | Every hour | One to two hours | `docs/methods/grid_network.md`, "How far behind the newest hour is, and why" |
| Interchange (Exchange, Now's net export, the Network) | Every hour | 53 hours at the refresh of 2026-10-14 08:05 UTC; between about 35 and about 59 | the same; the line under the chart |
| Generation by source | Daily | "A day or more after the hour" | `docs/methods/generation_mix.md` |
| Carbon intensity by hour | Daily, the last 3 days merged | Often more than three days; the live set holds 2025-08-09T16:00 to 2026-10-10T23:00 UTC | `docs/methods/emissions.md`, "Daily refresh"; the catalogue row of `carbon_intensity_hourly` |
| The replay | With the daily tables | To 2026-10-11 | `site/public/network/daily_index.json` |
| The two stories | Pulled once | Fixed windows | `docs/methods/grid_network.md` |

## 3. Every assumption

"Fixed" means the reader cannot change it on the page.

| Assumption | Default | Source | Ruling of 12 October |
|---|---|---|---|
| Grid in view | ERCOT at `/grid`; the Lower 48 when an address opens Network, Mix or Clean and names no grid; the picker "Grid" (`grid=`) | ERW's choice: `DEFAULT_GRID` and `WHOLE_VIEWS`, `site/lib/gridtool.ts`. Awaits the owner (session 237 report, ruling 1) | none |
| View | Now; the tabs (`view=`) | ERW's choice: `gridPick()`, `site/lib/gridtool.ts` | none |
| Hour stamp | The hour's start; Now prints the grid's local time, Exchange UTC; fixed | EIA-930 states the hour's end; `docs/methods/grid_network.md` | none |
| Sign of interchange | Positive: the reporter exports; fixed | EIA-930, checked over 360 hours (`docs/methods/grid_network.md`) | none |
| Pair rule | The code that sorts first; else the other side, sign flipped; fixed | ERW's choice: each tie once (`pair_flows()`, `warehouse/derived/network_hourly.py`) | none |
| Live window, hourly pull, full share | 168 hours; 48 hours; 0.9; the slider moves inside the window | `HOURS, PULL_HOURS, FULL_SHARE`, `warehouse/derived/network_hourly.py` line 68 | none |
| A fully reported hour | The 90th percentile of the pulled hours' pair counts; fixed | `newest_full_hour()` in the same file (session 61); the methods note still says "the median hour", the code is what runs | none |
| Hour the page shows | The newest hour every reporting pair holds; a pair silent 48 hours is not waited for; the slider | `completeHour()`, `site/lib/networkV3.ts` (`quiet = 48`) | none |
| The lag's reference (session 266) | Hours from the hour's start to the snapshot's latest hourly refresh, rounded; fixed | ERW's choice, so the number is checkable: `net|lag` in `netValue()`, `site/lib/network.ts` | none |
| Page cache | One hour for the page; the snapshot read on each request in Now and Exchange | `revalidate = 3600`, `site/app/grid/page.tsx`; `FRESH = 0`, `site/components/grid/NowView.tsx` | none |
| Look-back of Now | Demand 9 days, generation 34 days, carbon 7 days; fixed | `NowView()`, `site/components/grid/NowView.tsx` | none |
| Layout | Force layout, 600 steps, seed 42; drag to rotate, scroll to zoom | `layout()`, `warehouse/derived/grid_network.py` line 94 | none |
| Sphere size | 3 plus 22 times the square root of demand over the largest (ISO grids); 2 plus 10 times the square root of volume over the largest (others) | ERW's choice: `size`, `site/app/network/Network.tsx` | none |
| Link width | 0.4 plus 3 times the square root of the flow's share of the period's largest flow | ERW's choice: `site/app/network/Network.tsx`; `flowWidth()`, `site/lib/networkMap.ts` | none |
| Sphere and circle color | Carbon intensity of generation; grey where not held; the brand's tokens | `carbon_intensity_hourly`, `carbon_intensity_daily`; `TOKENS`, `site/app/network/Network.tsx` (session 241) | The brand rule of 12 October: colors from `site/app/tokens.css` only |
| Shape | Network (3D); the toggle "Map", "Network", "Gravity" (`shape=map`, `shape=gravity`) | ERW's choice (session 180; gravity: the owner's task of 14 October 2026); `parseShape()`, `site/lib/networkMap.ts` | none |
| Gravity: circle size (session 266) | Area proportional to net generation in the hour; the Lower 48's radius 80 of a 640 frame; at least 6 | `GRAVITY`, `gravityLayout()`, `site/lib/networkGravity.ts`; `docs/methods/grid_network.md` | none |
| Gravity: the pull (session 266) | Middle ring 205; a full pull 90; full at net imports of 25 percent of generation; importer in, exporter out | the same | none |
| Gravity: bearings (session 266) | CAISO 262, SPP 318, MISO 8, ISO-NE 40, NYISO 66, PJM 104, ERCOT 196 degrees from north | `GRAVITY_GRIDS`, `site/lib/networkGravity.ts`: follows the map; carries no data | none |
| Gravity: CAISO's generation (session 266) | EIA-930's total, as for every grid | `eia930_all_generation`; `docs/methods/eia930_caiso_break.md` on the break | none (part 9, question 1) |
| Battery ring; price ring | Off; off; "Batteries", "Prices" | `eia930_all_storage`, `caiso_battery_storage`; each ISO's hub price; PJM never has a ring | none |
| Playing speed | 0.7 seconds an hour; 0.18 seconds a day in the replay | `site/app/network/Network.tsx` | none |
| A replayed day | EIA's Eastern day, as the day's average MW; "A day since 2019:", "Play the year" | `eia930_daily_interchange` | none |
| Screen for a day of interchange | 10 median absolute deviations, floor 500 MWh | `screen()`, `warehouse/derived/ba_supply.py` line 77; `docs/methods/impossible_hours.md`, rule C | none |
| A screened day kept | Both sides reported and agree within 5 percent | `AGREE = 0.05`, `warehouse/derived/network_daily.py` line 128 | none |
| Headline measure of imports | The sum of the reported ties; the range shown when the three measures spread over 1 point of demand | `HEADLINE` and `SPREAD`, `site/lib/basupply.ts` | none |
| Trace the power | Two steps; four largest second-step suppliers; "Over:" this day, its month, the year | `trace()`, `site/lib/networkV3.ts` (`top = 4`) | none |
| Mix: an hour is used | Sources within 5 percent of the total (PJM 15 percent); no main source blank | `docs/methods/generation_mix_hourly.md` | none |
| Carbon look-back in the ranking | The latest hour within 7 days | `LOOK_BACK_DAYS = 7`, `site/components/grid/Emissions.tsx` | none |
| California's join | 2025-12-16T08:00:00Z | The owner's ruling (`docs/methods/eia930_caiso_break.md`) | none |
| Carbon-free | Nuclear, wind, solar, hydro; "other" is not | ERW's choice (`docs/methods/clean_energy.md`) | none |
| Tightest hours; evening ramp | The 100 hours of highest net load in a year; hours starting 14:00 to 22:00 local; "Year" chips | ERW's choice (`docs/methods/grid_stress.md`) | none |
| Impossible hour | Over 25 percent from the median of the four hours around it, or outside one third to three times the grid's median | `docs/methods/impossible_hours.md`, rule A | none |
| Map areas | Each county to the code with the most customers | EIA-861, 2025; `site/public/network/ba_boundaries.json`, labelled derived | none |
| Ask ceilings | 10 questions an hour per address; 15 a day per visitor; USD 3 a day and USD 30 a month | `docs/methods/ask_limits.md` | none |
| License day | 2026-10-21 | `site/data/license_status.json`, `docs/state/licenses_2026-10-21.md` | The owner's ruling of 12 October 2026: launch on 21 October |

## 4. The cross-checks

EIA's hourly report is EIA-930 itself: the tables are its figures, so the checks are of our sums and our reading of the hour against EIA's own published balance, EIA's API and bulk file, and the operators' own figures the repository holds. EIA's annual figures (Electric Power Annual) and an operator's own tie flows are not held (the last two rows).

| What is compared | Ours | Theirs | Gap | Reason |
|---|---|---|---|---|
| Sum of a grid's ties against EIA-930's net generation minus demand, 360 hours (`docs/methods/grid_network.md`) | Sum of ties | EIA's own balance | Mean absolute gap: ERCOT 1.6 MW, NYISO 0.4, ISO-NE 0.7; CAISO 3,199.1, PJM 2,042.1, MISO 1,397.9, SPP 978.1 | For the last four, reported interchange does not close EIA's balance: a property of the data |
| The same, the hour shown on 2026-10-14 (2026-10-12 03:00 UTC), from the replication file | Net imports by ties: ERCOT 128, ISO-NE 156, NYISO 2,120 MW | Demand less EIA-930 net generation: 128, 156, 2,111 MW | 0, 0, 9 MW | The three grids whose ties close the balance |
| The same hour, the four others | CAISO 6,591, MISO 1,561, PJM -1,544, SPP -437 MW | 7,058, 103, -1,462, -964 MW | 467, 1,458, 82, 527 MW | As over 360 hours; CAISO's gap also carries EIA-930's lower California generation |
| Net imports as percent of demand, September 2025 to August 2026 | Sum of ties: CAISO 16.49, PJM -2.72, MISO 2.54 | Demand less net generation: CAISO 26.87, PJM -3.18, MISO 0.17 | CAISO about ten points | EIA's net generation for California fell in December 2025 |
| The same, ties against EIA's total interchange | CAISO 16.49, ERCOT 0.07, ISO-NE 4.96, MISO 2.54, NYISO 11.82 | 16.49, 0.07, 4.96, 2.54, 11.81 | Equal to the second decimal but NYISO | PJM (-2.72 against -1.25) and SPP (-1.44 against -1.00) disagree, many days left out |
| Newest complete hour on 13 October 2026, 07:57 UTC (EIA's hourly report) | The page's file: hour beginning 2026-10-11 03:00 UTC | EIA's API route and EIA's bulk file `EIA930_INTERCHANGE_2026_Jul_Dec.csv`: the same hour | 0 hours; all 53 hours behind | The lag is EIA's publication |
| California's generation, 888 hours from the join | EIA-930 total: 22,618 MW | CAISO's own: 24,358 MW | 1,740 MW | EIA's solar and wind read below CAISO's own |
| California's intensity of generation | On CAISO's generation: 100.91 kg CO2/MWh | On EIA's: 110.80 | 7 to 11 percent lower by month | The denominator |
| ERCOT's peak demand, 2023 (Mix's demand) | Highest hour: 85,432 MW | ERCOT's own record: 85,508 MW | 76 MW | An hour's mean against a record over minutes (`docs/methods/demand_growth.md`) |
| Trace, California over 2021 | 56,992,955 MWh from nine suppliers | By hand: 56,993,006 | Every share equal to two decimals | The file holds a day's mean MW to one decimal |
| Trace, Texas, 12 to 19 February 2021 | SPP 84.6 percent (142,209 MWh), Mexico 15.4 percent (25,957 MWh) | The same sum by hand | A hundredth of a point | Rounding |
| Two operators, one tie: MISO to SPP, 15 February 2021 | MISO's report: 95,060 MWh | SPP's report: 95,390 MWh | 0.3 percent | Two reports of one flow |
| The replication file against the page (session 266, local build, snapshot of 2026-10-14 09:05 UTC) | `erw_2026_grid_replication.py`: 60 values (the lag, the counts, each grid's ties, net imports, generation, share, radius and distance) | The page's keyed numbers in Now and Network and the gravity shape's circles | 0 of 60 different | `check-grid-replication.mjs`, exit 0 (a first run read one count wrong: React's comment markers in the HTML, fixed in the check) |
| Every keyed number of `/grid` against its table (session 266, local build) | `check-values` restricted to `/grid`: 1,171 values, the new `net|lag` key among them (53) | The same values recomputed from Supabase and the snapshot | 0, twice | Exit 0 both runs |
| Every keyed number at the tool's landing (session 237) | 4,590 values on every page | Recomputed | 0 | `check-values`, exit 0 |
| EIA's annual net generation against the sum of EIA-930's hours (session 323; the Electric Power Annual has no table by balancing authority, so Form EIA-923's plant rows summed by their code; `eia_annual_crosscheck_ba`, `docs/methods/eia_annual_crosscheck.md`) | EIA-930, 2025: ERCO 485.2, CISO 185.4, PJM 873.8, SWPP 302.1, US48 4,280.5 TWh | EIA-923, 2025: 541.8, 203.1, 878.1, 293.2, 4,494.7 TWh | -10.45, -8.72, -0.48, +3.05, -4.76 percent (2023 and 2024 alike; ISNE, MISO and NYIS -3 to -7) | Likely, not EIA's statement: EIA-930 is what the balancing authority meters, EIA-923 each plant's own net generation (self-generation used on site among it); SPP meters plants EIA-923 codes elsewhere. Missing hours explain none |
| The exchange against an operator's own tie flows | not held | not held | not held | No operator's tie-flow connector is built |

## 5. The edge cases tested

Tested on a local build of the branch (port 3266) on 2026-10-14, in the internal view, unless the row says otherwise.

| Case | What was typed (the address) | What the page does |
|---|---|---|
| A grid with no interchange row for the newest hour | No grid lacked one in the live week of 14 October (all seven hold ties in every one of the 168 hours, checked on the snapshot); the rule was run on a typed case (`tests/test_session266.py`) | Now: the sentence leaves out the exchange and the headline reads "not reported" with "No tie of <grid> reported in the hour starting ..." (session 266 guard; before it the Lower 48's words "by grid" stood there). Gravity: the circle sits on the dashed middle ring, its net imports blank |
| A grid with zero generation | No hour of the live week holds zero or less (`eia930_all_generation`, checked through the public key); the rule run on a typed case (`tests/test_session266.py`) | Gravity: a dashed outline of the smallest radius, at the full pull toward the center when it imports and outward when it exports; no share is shown |
| The phone width | `/grid?grid=ercot&view=network&shape=gravity` at 390 px | The square frame fits the width with no sideways scroll; labels stay readable (`docs/brand/review-266/gravity_390.png`) |
| The gravity view with one grid selected | `/grid?grid=caiso&view=network&node=CISO&shape=gravity` at 1280 and 390 px | CAISO is outlined in ink, the panel opens beside it (below it on a phone) with the same figures as the other shapes; the grids that are not CAISO's neighbours are dimmed |
| The hover card | Pointer over NYISO's circle | The card names the grid, as on the map and the 3D network |
| Gravity in a replayed day | `/grid?grid=ercot&view=network&net=day&t=2021-02-15&shape=gravity` | Says the gravity shape is drawn for the live week only and draws nothing from a stand-in |
| The Lower 48 in Now | `/grid?grid=us48` | The exchange headline reads "by grid", pointing at the exchange of each |

## 6. What the model cannot see, ranked

Ranked for the question "what is this grid doing now"; for another question the order changes.

1. **The present.** The exchange, the network and the gravity shape are about two days old: 53 hours behind at the refresh of 2026-10-14 08:05 UTC, now said under the chart; between about 35 and about 59 hours as EIA publishes. Demand is one to two hours behind; generation by source a day or more.
2. **Anything inside a balancing authority.** Flows by line, limits, congestion, outages and reserves are not in EIA-930. No number held.
3. **A balance that closes.** For CAISO, PJM, MISO and SPP the sum of the ties does not equal net generation minus demand: mean gaps of 3,199.1, 2,042.1, 1,397.9 and 978.1 MW over 360 hours; 467, 82, 1,458 and 527 MW in the hour shown on 14 October. Session 360 (`docs/methods/eia930_balance.md`): EIA's adjusted series do not close it (adjusted is the reported value unless EIA imputed an anomaly, and in 840 hours from 13 September to 17 October it imputed none for these four). Split in two: CAISO's and MISO's ties sum to their total interchange within 1 MW, and the gap is their total interchange against net generation minus demand (3,002.8 MW, 9.6 percent of demand, and 1,430.1, 1.9 percent); SPP's total closes (26.0 MW) and its ties do not sum to it (1,023.2 MW without two hours whose SPP to MISO tie reads minus 2,148,411 MW); PJM has both. Since session 1165 (chain 078) the Network tab states it for the grid in view, each of the seven: the gap in the hour shown and its mean size over the week's hours that hold every tie, keyed (`docs/methods/grid_network.md`, "The balance, said where the figures are").
4. **California's generation.** EIA-930's California total read 1,740 MW below CAISO's own over 888 hours; in the hour shown on 14 October it was 18,499 MW against a demand of 25,557. Now withholds the mix; the gravity shape draws CAISO from EIA-930's total, so CAISO sits nearer the center than CAISO's own figures would put it.
5. **What a MWh used here emitted at the margin.** Carbon figures are averages. No number held.
6. **Prices for three grids, and more from 21 October.** PJM's prices are licensed and never shown; MISO's own files are paused since 4 October 2026; from 2026-10-21 the rows of ISO-NE, MISO and NYISO read "license needed".
7. **The other 63 balancing authorities' generation.** Not in the live set, so the gravity shape draws the seven ISO grids and the Lower 48 only.
8. **Minutes.** Every figure is an hourly mean, the replay a daily mean (ERCOT's 2023 record over minutes is 76 MW above the hour).
9. **Revisions.** EIA calls the data preliminary; one revised hour moved two of MISO's figures between a page's read and a checker's on 13 October 2026.
10. **Unscreened hours.** The rule for impossible values is applied by day and in the derived tables, not to an hour of interchange.
11. **Demand outside the seven ISO grids.** In the live week the others have no demand, so no share of demand; the replay holds daily demand for 54.
12. **History by the hour.** Hourly interchange from 2026-09-13 plus two story windows; before that the replay is daily.
13. **True boundaries.** The map's areas are derived: 44 of the 70 grids have an area, 26 none; 3,067 of 3,107 counties drawn, 1,126 served by several codes.
14. **Hours lost to source faults.** PJM's mix rests on a 15 percent tolerance (2,689 hours differ by 5 to 15 percent); New York loses 2022 and 2023 in "How clean, and when" to 3,147 hours of misfiled nuclear; SPP loses 2,568 stale hours in the stress figures.

## 7. The ten hardest questions

### 1. Is this live?

No. Demand is one to two hours behind. The exchange, the network and the gravity shape were 53 hours behind at the refresh of 2026-10-14 08:05 UTC; the line under the chart now says so, computed from the snapshot. EIA's API and bulk file were at the same hour on 13 October, so the lag is the publisher's. Closing it needs each operator's own real-time tie flows: seven connectors, four needing a license or a ruling. Not built.

### 2. Do your flows add up?

For three grids, yes: within 2 MW of net generation minus demand on average over 360 hours for ERCOT (1.6), NYISO (0.4) and ISO-NE (0.7), and 0, 9 and 0 MW in the hour shown on 14 October. For four, no: CAISO 3,199.1, PJM 2,042.1, MISO 1,397.9, SPP 978.1 MW. The tool shows the ties as reported and does not force a balance.

### 3. How much of California's power is imported?

By its ties, 16.49 percent of demand (September 2025 to August 2026); by EIA's total interchange 16.49; by demand less net generation 26.87. The headline is the ties. In the hour shown on 14 October, 6,591 MW came in by ties, 25.79 percent of a demand of 25,557 MW. Why EIA's California generation fell in December 2025, the tool does not know.

### 4. Can it show congestion, a line's limit or an outage?

No. The source holds totals between balancing authorities. A hub price ring is the only price signal, for the grids with a public price.

### 5. What does the gravity shape say, and how could it mislead?

Each of the seven ISO grids is a circle as large as its generation in the hour, nearer the Lower 48 as it imports more of what it generates. In the hour shown on 14 October CAISO sat closest (imports 35.6 percent of EIA-930's generation, a full pull) and NYISO next (18.0 percent); PJM and SPP sat just outside the ring as small net exporters. It misleads where the generation is wrong (CAISO, part 6 item 4) and in that only the bearing is fixed: two grids close on the page are not neighbours by that alone. The 63 others are not drawn.

### 6. Is the carbon number what my load would emit?

No. It is the grid's average: CO2 generated over net generation, or CO2 consumed over demand with imports counted. The choice of denominator alone moves California's figure from 110.80 to 100.91 kg CO2/MWh. Not marginal.

### 7. Does "Trace the power" say where Texas's power came from in the storm?

It says which ties carried it: over 12 to 19 February 2021, SPP 84.6 percent (142,209 MWh) and Mexico 15.4 percent (25,957 MWh) of Texas's net inflow. Physical flows, not contracts, not where the power was generated. On 15 February 2021 the replay shows net imports of 886 MW on average, 1.77 percent of demand.

### 8. Where are PJM's and MISO's prices, and what goes dark on 21 October?

PJM's license says "non-members are specifically prohibited from republishing data", so no PJM price is shown. MISO's terms forbid automated access; its pulls are paused since 4 October 2026. Now, the Network and the Exchange read EIA's public tables. What goes dark: the hub prices of ISO-NE, MISO and NYISO, the clean-hours figures of the same three, ISO-NE's rows of `energy_projects`, and `datacenter_facilities` and `news_index` whole.

### 9. How do you know the screen matches the publisher?

A script recomputes every keyed number from its table (4,590 of 4,590 on the whole site at the landing). Since session 266 the replication file exports the network's figures from the same reads, and a Python mirror of a Stata do-file rebuilds each one; a check compared 60 of them with the page on 14 October, 0 different. What no check does: compare the exchange with an operator's own figures.

### 10. Can the Ask panel be wrong?

Yes. For ERCOT, 100 of 100 test questions passed on 8 October 2026, each asked once ("A pass here does not say that every asking passes"), at USD 0.0171 a question. For the six other grids and the Lower 48 no evaluation figure is held. Every number in an answer is checked against a query's result before it is shown. Since session 266 the briefing says the live set holds hourly carbon intensity from 2025-08-09T16:00 to 2026-10-10T23:00 UTC, so Ask no longer believes it holds 30 days.

## 8. What Samuel's Stata run must reproduce

The figures of the hour shown when the file was written: 2026-10-12 03:00 UTC, from the snapshot refreshed at 2026-10-14T08:05:18Z (the file is rewritten by `node site/scripts/write-grid-replication.mjs`; the page moves every hour, so compare a file with the page of the same snapshot).

| Name | Value the page shows | The do-file's display line |
|---|---|---|
| The lag, hours (Network line; Now sentence) | 53 | `lag_hours = 53` |
| Balancing authorities drawn | 70 | `nodes = 70` |
| Pairs reporting in the hour | 157 of 157 | `pairs_reporting = 157` |
| Lower 48 net generation, MW (Gravity, center) | 449,872 | `generation_US48 = 449872` |
| CAISO ties; net import, MW; share of demand, percent | 11; 6,591; 25.79 | `ties_CISO = 11`, `net_import_CISO = 6591`, `net_share_of_demand_pct_CISO = 25.79` |
| ERCOT ties; net import, MW; share of demand | 2; 128; 0.21 | `ties_ERCO = 2`, `net_import_ERCO = 128`, `net_share_of_demand_pct_ERCO = 0.21` |
| ISO-NE ties; net import; share | 3; 156; 1.43 | `ties_ISNE = 3`, `net_import_ISNE = 156`, `net_share_of_demand_pct_ISNE = 1.43` |
| MISO ties; net import; share | 10; 1,561; 2.18 | `ties_MISO = 10`, `net_import_MISO = 1561`, `net_share_of_demand_pct_MISO = 2.18` |
| NYISO ties; net import; share | 4; 2,120; 15.23 | `ties_NYIS = 4`, `net_import_NYIS = 2120`, `net_share_of_demand_pct_NYIS = 15.23` |
| PJM ties; net export, MW; share | 7; 1,544; 1.92 | `ties_PJM = 7`, `net_import_PJM = -1544`, `net_share_of_demand_pct_PJM = 1.92` |
| SPP ties; net export; share | 10; 437; 1.26 | `ties_SWPP = 10`, `net_import_SWPP = -437`, `net_share_of_demand_pct_SWPP = 1.26` |
| Gravity: CAISO share of generation; radius; distance | 0.356290; 16.2; 115.0 | `gravity_share_CISO = 0.356290`, `gravity_r_CISO = 16.2`, `gravity_d_CISO = 115.0` |
| Gravity: ERCOT | 0.002112; 29.4; 204.2 | `gravity_share_ERCO`, `gravity_r_ERCO`, `gravity_d_ERCO` |
| Gravity: ISO-NE | 0.014462; 12.4; 199.8 | `gravity_share_ISNE`, `gravity_r_ISNE`, `gravity_d_ISNE` |
| Gravity: MISO | 0.021793; 31.9; 197.2 | `gravity_share_MISO`, `gravity_r_MISO`, `gravity_d_MISO` |
| Gravity: NYISO | 0.179524; 13.0; 140.4 | `gravity_share_NYIS`, `gravity_r_NYIS`, `gravity_d_NYIS` |
| Gravity: PJM | -0.018825; 34.2; 211.8 | `gravity_share_PJM`, `gravity_r_PJM`, `gravity_d_PJM` |
| Gravity: SPP | -0.012235; 22.5; 209.4 | `gravity_share_SWPP`, `gravity_r_SWPP`, `gravity_d_SWPP` |

The do-file has not been run: Stata is not on the machine that wrote it. The Python mirror prints the same lines and was run (the session 266 report).

```
cd "<the repository>/site/public/grid"
do erw_2026_grid_replication.do
* the Python mirror, for a machine without Stata:
* python erw_2026_grid_replication.py erw_2026_grid_replication.csv
```

## 9. Questions only Samuel can answer

1. **CAISO's circle in the gravity shape.** (a) Keep EIA-930's net generation for every grid (one source; CAISO reads smaller and more pulled in since December 2025); (b) use CAISO's own generation from 2025-12-16, as Mix and Clean do (two sources in one drawing); (c) draw CAISO as an outline with a line saying its generation is under review. (a) is built.
2. **The pull's scale.** (a) Keep it linear with a full pull at 25 percent of generation (most grids sit near the ring; CAISO and NYISO stand out); (b) a full pull at 10 percent (small importers such as MISO move visibly, CAISO and NYISO both at the full pull); (c) a square-root scale (both). Each changes only `S_FULL` or one line of `gravityLayout()`.
3. **How old "now" is.** (a) Keep the age of the exchange's hour against the snapshot's refresh (built: checkable); (b) against the clock when the page is drawn (truer to "now", not checkable by `check-values`); (c) both.
4. **The grid at `/grid`.** (a) ERCOT (built); (b) the Lower 48; (c) the visitor's last choice. Session 237's ruling 1, still open.
5. **EIA's annual figures.** (a) Add EIA's Electric Power Annual generation by balancing authority to the repository so the hourly sums can be checked against a published annual figure; (b) leave the cross-checks on EIA-930's own balance and the operators' figures held.
6. **The other 63 balancing authorities in the gravity shape.** (a) Leave them out (built, said in a line); (b) put their hourly generation into the live set (a data change on the main machine); (c) draw them sized by the week's interchange volume, as the 3D network does.

Ruled on 18 October 2026 (the owner's merge and the chain prompt of 19 October), built in session 299: 1 (a), one source,
the break named in the shape's note; 2 (c), a square-root scale with the full pull still at 25 percent; 3 (c), both ages,
the refresh's as the check key and the clock's beside it; 4 (b), the Lower 48; 6 (a), left out and counted in the note.
Question 5 stands. The page says these in its decisions block; `docs/methods/grid_network.md`, "One page, four tabs, and
the Ask panel (session 299)", carries the method.

Question 5, answered in session 323 (the chain prompt of 19 October 2026, daytime): (a), with Form EIA-923 in place of the
Electric Power Annual, whose index has no table by balancing authority. `eia_annual_generation_ba` sums EIA-923's plant
rows by their balancing authority code (2023 to 2025, final files); `eia_annual_crosscheck_ba` sets the sum of EIA-930's
hours against it for CISO, ERCO, ISNE, MISO, NYIS, PJM, SWPP and the Lower 48. EIA-930 is lower by 3 to 10 percent on six
of them and by about 4.5 percent on the Lower 48, within 1 percent on PJM, and about 3 percent higher on SPP; missing hours
explain none of it (section 4's row; `docs/methods/eia_annual_crosscheck.md`). Both tables are in the live set for the
decisions block; the page's words are the code machine's.

## Appendix: the five-minute demo

On the machine you will show it from, open the internal view first: `https://erw-flame.vercel.app/internal/open`, paste the token and press **Open the internal view**. Then `https://erw-flame.vercel.app/grid`. Written from the page's code, its data files and its check scripts; session 266 clicked the gravity shape on a local build, not this path.

**Say this first:** every number here is a public hourly report, mostly EIA's; each one names its hour; nothing is forecast.

### Minute 0 to 1: Now

1. The page opens on **ERCOT**, tab **Now**. The title reads "ERCOT: Electric Reliability Council of Texas".
2. Read the sentence aloud: demand "in the hour starting ..., the latest EIA has published", the same hour a week earlier, the largest source, the net export or import over ERCOT's reporting ties and how many hours that hour began before the latest hourly refresh, and the kg of CO2 each MWh carried.
3. Point at the three headline numbers: **Demand**, **Net export** (or **Net import**), **Carbon intensity**. Read the hour under each.
4. Under them, **The mix in that hour**: the bar and the table of sources as EIA names them.

### Minute 1 to 2: Exchange

1. Click **Exchange** (`/grid?grid=ercot&view=exchange`). Read **Net export** or **Net import**, **Ties reporting**, **Largest flow**. ERCOT has 2 ties: SPP (SWPP) and Mexico's operator (CEN).
2. Scroll to **Over the last twelve months**: "Net imports were ... percent of ERCOT's demand" (0.07 percent for September 2025 to August 2026). Texas is nearly an island.

### Minute 2 to 4: Network

1. Click **Network**. Read the line under the chart: the newest hour shown and how far behind it is.
2. Under "Watch:" click **Texas during Uri** (2021-02-07 to 2021-02-24, 432 hours at 0.7 seconds an hour); click **Pause** after a few seconds.
3. In **A day since 2019:** choose `2021-02-15`. The panel reads net imports of 886 MW on average, 1.77 percent of a demand of 50,152 MW (779.2 MW in from SWPP, 107.1 MW from CEN, demand 50,151.8 MW).
4. Click **Prices: off**. One ring appears, on ERCOT: the hub price that day reads 6,704.67 USD/MWh.
5. In the panel click **Trace the power** and read the suppliers.
6. Click **Map**: the frame says the areas are derived from EIA-861.
7. Click **Live now**, then **Gravity**: the Lower 48 at the center, the seven ISO grids around it, importers nearer the center. Click CAISO: the same panel opens.

### Minute 4 to 5: Clean, then Ask

1. Click **Clean**. In **Carbon intensity now, ranked** ERCOT's row is highlighted: "Of generation" and "Of demand", and the hour.
2. Click **Ask**. The box is labelled **Ask ERCOT**. A question sent here is a model call (USD 0.0171 a question on the test set of 8 October 2026).

**If something goes wrong:** "This tool is in review" in place of the tool: open `/internal/open` again. "This browser cannot draw 3D": click **Map** or **Gravity**. A line "(the daily snapshot: the hourly copy was not reachable)": the page is drawing the committed file. A price reading "paused while terms are reviewed" or "Not shown: PJM's prices are licensed": the gate, working. California's mix in Now reads withheld: by ruling (session 118).

## Where every number comes from

| Number | File | Section |
|---|---|---|
| Eight grids, six views, the address words, the redirects | `site/lib/gridtool.ts`, `site/next.config.ts` | `GRID_CHOICES`, `GRID_VIEWS`, `redirects()` |
| 70 nodes, 157 pairs, the hour 2026-10-12 03:00 UTC, the refresh 2026-10-14T08:05:18Z, 53 hours, every figure of part 8 | `site/public/grid/erw_2026_grid_replication.csv` and the `.py` run on it | the header lines; the printed lines |
| The demand and EIA-930 generation of the hour, and the gaps of part 4 rows 2 and 3 | the same file | kinds `demand`, `generation`, `tie` |
| The gravity constants and bearings | `site/lib/networkGravity.ts` | `GRAVITY`, `GRAVITY_GRIDS` |
| 2025-08-09T16:00 to 2026-10-10T23:00 UTC of hourly carbon | Supabase `catalogue` and `series` read with the public key on 2026-10-14 | `carbon_intensity_hourly` |
| 16 regional sums not drawn; 168 and 48 hours; 0.9; the 90th percentile | `warehouse/derived/network_hourly.py`, `site/app/network/Network.tsx` | `HOURS`, line 68, `newest_full_hour`; `EIA_REGIONS` |
| 360 hours; 1.6, 0.4, 0.7, 3,199.1, 1,397.9, 2,042.1, 978.1 MW | `docs/methods/grid_network.md` | "The sign, checked against the data" |
| 600 steps, seed 42 | `warehouse/derived/grid_network.py` | `layout`, line 94 |
| Sphere size, link width, 0.7 and 0.18 seconds | `site/app/network/Network.tsx` | `size`, `linkWidth`, the play interval |
| 53 hours on 13 October; about 35 to about 59 hours; the second morning; seven connectors, four needing a license | `docs/methods/grid_network.md` | "How far behind the newest hour is, and why (session 247)" |
| 16.49, 26.87, 0.07, 4.96, 2.54, 11.82, 11.81, -2.72, -1.25, -3.18, -1.44, -1.00, 0.17 | `docs/methods/grid_network.md` | "Who supplies a grid (session 68)" |
| 10 deviations, 500 MWh; 5 percent; 25 percent; one third to three times | `docs/methods/impossible_hours.md`; `warehouse/derived/network_daily.py` | "The rule"; `AGREE` |
| The replay's first and last day; 54 with daily demand | `site/public/network/daily_index.json` | `first`, `last`, `with_demand` |
| 56,992,955 and 56,993,006 MWh; 84.6 and 15.4 percent; 142,209 and 25,957 MWh; 95,060 and 95,390 MWh | `docs/methods/grid_network_v3.md` | "To launch-ready (session 124)" |
| 85,508 and 85,432 MW | `docs/methods/demand_growth.md` | "An hour's demand is the average over the hour" |
| 5 and 15 percent; 2,689 hours | `docs/methods/generation_mix_hourly.md` | "Which hours are used" |
| The intensity formulas | `docs/methods/emissions.md` | "carbon_intensity_hourly, carbon_intensity_daily and carbon_intensity_monthly (derived)" |
| 2025-12-16T08:00:00Z; 22,618, 24,358, 1,740 MW; 110.80 and 100.91 | `docs/methods/eia930_caiso_break.md` | "The join" |
| 3,147 hours of New York's nuclear | `docs/methods/clean_energy.md` | "The hours" |
| 100 hours; 14:00 to 22:00; 2,568 hours | `docs/methods/grid_stress.md` | "The definitions" |
| 44 of 70; 26; 3,067 of 3,107; 1,126 | `docs/methods/grid_network.md`; `site/public/network/ba_boundaries.json` | "The derived map: counties"; `provenance` |
| 432 hours; the story's window | `site/public/network/story_uri_2021.json` | `hours`, `window` |
| 779.2, 107.1, 50,151.8 MW; 6,704.67; 886 MW and 1.77 percent | `site/public/network/daily_2021.json`; `site/scripts/check-network-v3.mjs` | the row of 2021-02-15; `hub_prices`; check "a" |
| 4,590 of 4,590 | `archive/sessions/SESSION_237_REPORT.md` | "The landing" |
| 100 of 100; USD 0.0171 | `docs/methods/ask_ercot.md` | "What the 100 questions said (8 October 2026)" |
| 10 an hour; 15 a day; USD 3 and USD 30 | `docs/methods/ask_limits.md` | "What happens to a question"; "The configuration" |
| 2026-10-21; the tables held by grid | `docs/state/licenses_2026-10-21.md`; `site/data/license_status.json` | "Read these first" |
| PJM's sentence; MISO's pause of 4 October 2026 | `docs/licenses.md`; `docs/methods/miso_pause.md` | "The publishers"; opening paragraph |
