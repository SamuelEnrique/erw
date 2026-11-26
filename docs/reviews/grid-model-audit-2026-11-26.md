# The Grid tool: its figures audited as a hostile expert would

Session 10205, chain 710 part D, 26 November 2026, the old laptop. Read as a grid operator's analyst and a carbon accountant who want to find it wrong. The chain's three questions first: how interchange is netted, how carbon intensity is computed, what "now" means.

- The page: `/grid` (`site/app/grid/page.tsx`), opening on the Lower 48, Mix tab. The figures: `site/components/grid/NowView.tsx`, `ExchangeView.tsx`, `NetworkFigures.tsx`, `Emissions.tsx`, `YourGrid.tsx`; the arithmetic in `site/lib/network.ts` and `site/lib/networkV3.ts`.
- The files they read: `site/data/grid_network.json` (the committed snapshot) or its hourly copy in Storage; the live set's `eia930_all_demand`, `eia930_all_generation`, `carbon_intensity_hourly` and `carbon_intensity_monthly`.
- The builders: `warehouse/derived/grid_network.py` (daily snapshot), `warehouse/derived/network_hourly.py` (hourly), `warehouse/derived/carbon_intensity.py`, `warehouse/connectors/eia930_emissions.py`.
- Nothing changed on main but this file and its evidence folder. No table written, no lock taken, no default moved, no model called, no live service asked.
- Each finding has its own branch, `wip/audit-grid-<n>`. Words-only fixes (1, 2, 4, 5) are for landing; 3 and 6 move figures and wait for the owner.

## In short

- **The arithmetic is right.** Every figure the default view prints follows from its files as the code says: the Lower 48's Now blocks and the Gravity tab's table of the seven grids came out to the digit in an independent restatement, and again with the page's own library. The carbon formula restates to four decimals on every hour of six grids where EIA did not revise the CO2 (3,083 hours of generation, 2,089 of demand).
- **"The Lower 48 is the sum of its grids, so its exchange is theirs" is false.** The seven grids carry 65.2 percent of the Lower 48's demand, and the Lower 48's own exchange is with Canada and Mexico: a mean net import of 2,996 MW against the seven grids' summed 5,641 (finding 1, words, for landing).
- **A grid's net export is not its own.** Each tie is read from the authority whose code comes first in the alphabet. PJM's six of seven ties come from its neighbours; the page's PJM figure is 990 MW off PJM's own reports in the median hour and the other way round in 32 percent of hours. The page says "signed from its side" and nothing else (finding 2, words, for landing; the rule itself is the owner's).
- **The same ties, two rules.** A region's Gravity tab takes the mean of both sides; the grid's tabs take one side. MISO's net differs by 451 MW in the median hour between them (finding 3, the owner's ruling).
- **The carbon figure is an average, each fuel at one factor, imports at EIA's own valuation, and the page says none of it.** A simple marginal estimate is 0.47 of the average in ERCOT and 1.41 in SPP; EIA's gas factor holds within 1 percent hour after hour; imports carry a quarter of NYISO's "of demand" CO2, at 318 kg/MWh against its own 253 (finding 4, words, for landing).
- **"Now" is four different hours.** Demand is an hour or two old, the exchange about two and a half days, carbon about three; the sentence and the "now, ranked" table did not say carbon is the oldest or that each grid sits at its own hour (finding 5, words, for landing).
- **No screen on the snapshot's reports.** Two reports above 20,000 MW in seven weeks, both SPP's of its MISO tie; the pair rule happened to read MISO's (finding 6, the owner's ruling; effect in the window: none).
- **Held grids reach no figure.** ISO-NE, MISO and NYISO appear only through EIA-930, which is public domain; no operator's held table feeds the four Now figures, the exchange or the carbon blocks. No eGRID figure is read by `/grid`.

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/grid/page.tsx` | The page: picker of eight (seven grids and the Lower 48), four tabs; with no grid in the address it opens on the Lower 48, Mix tab (`lib/gridtool.ts` `DEFAULT_GRID`, `DEFAULT_VIEW`). The decisions block of 18 October. |
| `site/app/grid/RegionTool.tsx`, `components/grid/RegionViews.tsx`, `lib/gridregions.ts`, `lib/regionsdata.ts` | EIA's thirteen regions, drawn from `site/data/regions/` files the data machine builds; their trade tab reads `interchange_pairs.py`'s files. |
| `components/grid/NowView.tsx` | The Mix tab's top: demand (latest hour and a week earlier), the mix's latest hour, the net exchange over the snapshot's complete hour and its lag, carbon intensity of generation and of demand. |
| `components/grid/ExchangeView.tsx` | Under the Gravity shape: for the Lower 48, the seven grids' net export in the complete hour and the largest exporter of all 70 nodes; for a grid, its ties, the week, the twelve months (`ba_supply_monthly`). |
| `components/grid/NetworkFigures.tsx`, `lib/gridKeys.ts` | The Network and Gravity tabs' figures drawn on the server, with check keys. |
| `components/grid/Emissions.tsx` | The Clean tab: carbon intensity per ISO "ranked", the last 24 hours, monthly since 2018. |
| `components/grid/YourGrid.tsx`, `Conditions.tsx`, `MixView.tsx`, `lib/mixpage.ts` | A grid's own page blocks (licence gates through `lib/license.ts`), yesterday's block, the mix views. Not re-done here beyond the carbon words. |
| `lib/network.ts` | `pickSnapshot` (Storage when whole and newer, else committed), `tiesAt`, `netExports`, `topExporter`. |
| `lib/networkV3.ts` | `completeHour`: the newest hour every pair that reported in the last 48 hours holds. |
| `site/data/grid_network.json` | The snapshot: 70 nodes, 159 pairs, 168 hours; each pair once by the pair rule. Committed copy built 2026-11-25 14:48 UTC. |
| `warehouse/derived/grid_network.py`, `network_hourly.py` | The snapshot's builders: the pair rule (a pair's flow is the report of the authority whose code sorts first, else the other's with the sign turned), EIA's regions and country totals left out, no plausibility screen. |
| `warehouse/derived/interchange_pairs.py` | The region trade files: each side's sum, their gap, and the mean of the two where both reported. |
| `warehouse/derived/carbon_intensity.py`, `connectors/eia930_emissions.py` | `intensity_generation` = EIA's generated CO2 x 1000 / the workbook's net generation; `intensity_demand` = EIA's consumed CO2 x 1000 / the workbook's demand. Hour, complete UTC day, complete UTC month. |
| Notes | `docs/methods/grid_network.md`, `interchange_pairs.md`, `emissions.md`, `eia930_all_interchange.md`, `grid_conditions.md`. `price_board_carbon.md`, `egrid_*.md`: not read by `/grid`. |

## The default view re-done, to the digit

The live set holds newer hours than this machine. Every figure below is the page's figure on the tables as this machine holds them (the main copy's `warehouse/output`, read only, built 5 to 13 November) and on the committed snapshot. Scripts and outputs: `docs/reviews/grid-model-audit-2026-11-26/`.

- **Restatement.** `c710_grid_audit.py` reads the tables and the snapshot with none of the site's code. `c710_grid_page.mts` computes the Gravity figures with the page's own `lib/network.ts` and `lib/networkV3.ts`. `c710_grid_draw.mjs` draws the Now, Exchange and Clean blocks to HTML with the site's components, every read answered from those rows and every other request refused (`b1_draw_*.txt`). All three agree.

| Figure (Lower 48, Mix tab and Gravity tab) | Restated | Page's code / drawn page |
|---|---|---|
| Demand, hour starting 2026-11-12 23:00 UTC | 491,749 MW | 491,749 |
| A week earlier (2026-11-05 23:00) | not in the table, so not printed | not printed |
| Largest source, hour starting 2026-11-04 23:00 | natural gas 212,169 MW of 488,990 | 212,169 of 488,990 |
| Carbon intensity of generation, 2026-11-02 23:00 | 305.3429 kg/MWh | 305.34 |
| Of demand, imports counted, same hour | 304.4106 | 304.41 |
| Snapshot's complete hour | 2026-11-22 23:00 UTC (159 of 159 pairs; the newest hour, 23 November 23:00, has 156) | the same |
| Hours before the refresh | 64 | 64 |
| Net export: CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP | -3,474; -128; -416; -1,280; -1,627; +1,033; -370 MW (11, 2, 3, 10, 4, 7, 11 ties) | the same |
| Largest net exporter of the 70 | SRP, 5,558 MW | the same |

- **The carbon builder, restated.** On the 4 October workbook extract against the table built from the 5 November one, the formula gives the table's value to 0.0000 kg/MWh on every hour whose CO2 EIA did not revise: ERCOT, PJM, MISO, SPP, ISO-NE and NYISO, 3,083 hours of generation and 2,089 of demand (`grid_audit_h.json`). The Lower 48's denominators moved between the two workbooks in 411 of 514 such hours (at most 0.11 kg/MWh): EIA revises its regional sums.

### One rule changed at a time

| Rule | The page | Changed to | Measured worth |
|---|---|---|---|
| Netting | each tie from the code first in the alphabet | each tie from the grid's own report first | PJM: mean net export +1,786 MW becomes +632; 990 MW apart in the median hour, 9,954 at most, opposite signs in 370 of 1,152 hours. CAISO: 506 median, 11 hours of sign. NYISO 8, MISO 5, ERCOT and ISO-NE 0 (13 September to 3 November 2026, `grid_audit_j_screened.json`) |
| Netting | one side | mean of the two sides (the region tab's rule) | median hour apart: MISO 451 MW, PJM 503, CAISO 258, NYISO 215, ERCOT 188, ISO-NE 4 |
| The hour | the newest hour every reporting pair holds | the newest hour of the snapshot | one hour newer (23 November 23:00), 3 of 159 pairs missing; the note's rule avoids a third of lines missing |
| Carbon denominator | the workbook's net generation | EIA-930 API net generation (session 32's) | the default hour: 305.34 becomes 306.34; over 336 hours a mean of 0.75 kg/MWh, at most 4.34 |
| Carbon kind | average | hour-to-hour marginal (least squares, Oct 2025 to Sep 2026) | ERCOT 143 against 305 (0.47); SPP 581 against 413 (1.41); PJM 395 against 336 (1.17); MISO 428 against 433; Lower 48 338 against 336 |
| Imports' carbon | EIA's valuation | none at all (a bound) | NYISO "of demand" falls at most 66.5 of 266.6 kg/MWh (25.0 percent); ISO-NE 21.5 of 237.9; PJM 7.4; Lower 48 2.2 |

## Each claim against the code

- **Netting, both sides reported.** EIA files each tie twice, once by each authority. The snapshot keeps one report a pair-hour: the first code's, else the other's turned. In the table's hours 156,216 of 186,480 pair-hours carry both reports; they differ by more than 10 MW in 21.1 percent and in sign in 2.89 percent. The page says "the sum of a grid's reporting ties, signed from its side": true of the sign, silent on whose report. The note says it for the map (`grid_network.md`, "What the cross-check shows a reader should know") and the map's decisions block says it; the Now, Exchange and Network figures did not. **Finding 2.**
- **Sign conventions.** Positive is export from the grid's side in the hour blocks, as stated. The twelve months' block turns it (positive is import) and says so. Right.
- **Double counting.** Each pair once; over all 70 nodes the net exports sum to zero at the complete hour (checked). EIA's regions and country totals are left out, so nothing is counted twice. Right. The Lower 48's exchange is not the seven grids' sum: **finding 1**.
- **Average against marginal.** The page and note never say average. **Finding 4.**
- **Hour against year factors.** EIA multiplies each fuel's hourly generation by one factor per fuel and authority: the gas ratio sits within 417.1 to 420.3 kg/MWh in ERCOT over 336 hours, 410.3 to 412.0 in the Lower 48. The hourly figure is the hour's mix, not its plants. The note says "an emission factor per fuel and BA"; the page says only "EIA's estimate". **Finding 4.**
- **eGRID year.** `/grid` reads no eGRID table. Not applicable.
- **Imports' carbon.** "Imports counted" rests on EIA's imported CO2, whose method the warehouse does not hold. Measured: NYISO's imports at 318 kg/MWh against its own 253, ISO-NE's at 310 against 209, the Lower 48's from Canada and Mexico at 484 against 357. **Finding 4.**
- **What "now" is and how stale.** Demand: an hour or two (the note's own measure). The exchange: the snapshot's complete hour, said with its lag (64 hours on the committed file; the note's 35 to 59 is for the Storage copy). Carbon: the table's newest hour is 72 hours before its build, and the sentence called it "the latest EIA has estimated" with no age. The ranked table put PJM (30 October), SPP (31 October) and the others (2 November) in one ranking titled "now". **Finding 5.**
- **Held grids.** ISO-NE, MISO and NYISO reach the Lower 48's figures and the seven-grid table only through EIA-930 (public domain). The blocks that read an operator's own tables pass `lib/license.ts` (YourGrid's queue and news cells say "license needed"). No held row reaches a figure audited here.
- **The window.** Each figure names its hour; the exchange's week is the snapshot's 168 hours; the Clean tab's months are complete UTC months. Right as stated.

## What an expert's own number would hold that this does not

- **The grid's own total interchange,** or both sides with their gap: PJM's figure moves 990 MW in the median hour (finding 2). A grid operator's analyst reads his own grid's filings first.
- **A marginal emission factor** for a load's effect: half to one and a half times the average shown (finding 4). A carbon accountant doing location-based Scope 2 uses an average, but one for avoided or added emissions uses a marginal one.
- **Imports traced or valued by the exporter's own grid:** at most 66.5 kg/MWh off NYISO's "of demand" figure (finding 4).
- **Plant-level emissions** (EPA's hourly unit data) in place of fuel factors: not measurable here; this machine holds no such table.
- **Losses:** intensity per MWh generated, not per MWh delivered at the meter; not measured (no losses table on this machine).
- **A plausibility screen** on interchange reports, as the twelve months' block has (finding 6).

## Findings

| # | Severity | Finding | Measured | Branch | Kind |
|---|---|---|---|---|---|
| 1 | Major | "The Lower 48 is the sum of its grids, so its exchange is theirs" (Gravity) and "is the sum of its grids" (Now card) are false | seven grids 65.2 percent of Lower 48 demand (60.9 to 68.4, 1,392 hours); Lower 48's own exchange mean -2,996 MW against the seven's -5,641; 3,312 MW apart on mean, opposite signs in 74 of 1,200 hours | `wip/audit-grid-1` | words, for landing |
| 2 | Major | A grid's net export reads each tie from the code first in the alphabet; the page says only "signed from its side" | PJM 990 MW median off its own reports, opposite sign 32 percent of hours; CAISO 506 | `wip/audit-grid-2` | words, for landing; the rule is the owner's |
| 3 | Moderate | Two rules for the same ties in one tool (grid tabs: one side; region trade tab: mean of both) | MISO 451 MW, PJM 503, CAISO 258 apart in the median hour | `wip/audit-grid-3` | figure, the owner's ruling |
| 4 | Moderate | The carbon figure's words: an average (not marginal), one factor per fuel, imports at EIA's valuation, none said on the page | marginal 0.47 to 1.41 of average; gas factor within 1 percent; imports 25 percent of NYISO's consumed CO2 | `wip/audit-grid-4` | words, for landing |
| 5 | Minor | "Now": the carbon hour is days older than demand's and the sentence did not say so; "now, ranked" ranks grids at different hours | carbon 72 hours behind its build; PJM 3 days behind the others in the ranking | `wip/audit-grid-5` | words, for landing |
| 6 | Minor | No plausibility screen on the snapshot's interchange reports | 2 reports above 20,000 MW in seven weeks (SPP of its MISO tie, 4 and 6 October), none read by the pair rule | `wip/audit-grid-6` | figure, the owner's ruling |

### 1. The Lower 48 is not the sum of its grids

- **Where.** `site/components/grid/ExchangeView.tsx` line 42; `site/components/grid/NowView.tsx` line 103.
- **Why it is wrong.** The Lower 48 holds the seven ISO grids and every other balancing authority of the lower 48 states (the Southeast, the West outside California, Florida, the Carolinas, Tennessee). Their trade with one another cancels inside it, so its own exchange is with Canada and Mexico alone (EIA's `US48` rows run to `CAN` and `MEX` only).
- **How much.** 27 August to 29 October 2026: the seven grids' demand 65.2 percent of the Lower 48's (60.9 to 68.4). 13 September to 3 November: the Lower 48's own net export -2,996 MW on mean, the seven grids' summed -5,641; 3,312 MW apart on mean, opposite signs in 74 of 1,200 hours.
- **The test.** `tests/test_audit_grid_1.py`: in the committed snapshot the 70 nodes' nets sum to zero and the seven's do not, and ties run abroad (passes on main); the seven are under 75 percent of the Lower 48's demand in every hour held (passes on main where the table is); the words (fail on main, pass on the branch).
- **The fix on the branch.** Words only: "The Lower 48 holds these seven grids and the other balancing authorities of the lower 48 states; what they trade with one another cancels inside it, so its own exchange is with Canada and Mexico alone." The Now card: "Trade between its grids cancels inside the Lower 48; its own exchange is with Canada and Mexico." Drawn to HTML and read (`b1_draw_us48_exchange.txt`, `b1_draw_us48_now.txt`).

### 2. A grid's net export is one side's reports

- **Where.** `warehouse/derived/grid_network.py` `RULE` and lines 131 to 138; `network_hourly.py` (the same rule); `site/lib/network.ts` `tiesAt`, `netExports`. The words: `ExchangeView.tsx` lines 45, 86 and 92, `NetworkFigures.tsx` line 37, `NowView.tsx` lines 90 to 91.
- **Why it is wrong.** "The sum of a grid's reporting ties, signed from its side" reads as the grid's own account. For PJM six of its seven ties are read from CPLE, CPLW, DUK, LGEE, MISO and NYIS; for CAISO four of eleven (AZPS, BANC, BPAT, CEN); for SPP ten of eleven. Where the two sides disagree the page shows the neighbour's account as PJM's.
- **How much.** Each grid's sum over every tie, hour by hour, 13 September to 3 November 2026, the page's rule against its own report first (a neighbour's where it filed none), reports above 20,000 MW set aside:
  - PJM: mean +1,786 MW against +632; median hour 990 MW apart, at most 9,954; opposite signs in 370 of 1,152 hours (32 percent).
  - CAISO: -4,198 against -4,619; median 506, at most 1,361; 11 hours of sign.
  - NYISO 8 MW median, MISO 5, ERCOT and ISO-NE 0 (the only neighbour they read first, CEN and HQT, files nothing back).
  - SPP: only 120 hours hold a report on all eleven of its ties (SPA reports a third of the time); in those, 574 MW median.
- **The largest disagreements, tie by tie** (`grid_audit_i.json`): MISO and PJM report their tie 1,213 MW apart on mean, opposite in sign in 295 of 1,104 hours; NYISO and PJM 624 MW; ERCOT and SPP 536 MW, opposite in 325 of 1,104 hours; AZPS and CAISO 472 MW.
- **The test.** `tests/test_audit_grid_2.py`: in the snapshot most of PJM's ties are read from the neighbour (passes on main); on the table PJM's two sums are more than 500 MW apart in the median hour and opposite in more than a tenth of hours (passes on main where the table is); the words (fail on main).
- **The fix on the branch.** Words only, one phrase in `lib/network.ts` (`TIE_SIDE_WORDS`): "each tie as the balancing authority first in the alphabet reported it (the other where it filed nothing), so the sum can differ from the grid's own reports to EIA", added to the four notes and the Now sentence. Drawn and read (`b2_draw_pjm_exchange.txt`, `b2_draw_pjm_now.txt`).
- **For the owner.** Reading each grid's own reports first would move PJM's figure 990 MW in the median hour and turn its sign in a third of hours. Default: left as it is.

### 3. Two rules for the same ties

- **Where.** `grid_network.py` (one side) against `interchange_pairs.py` lines 102 to 110 (the mean where both reported), which feeds the region tab's trade files.
- **How much.** The page's rule against the mean of both sides, median hour: MISO 451 MW, PJM 503, CAISO 258, NYISO 215, ERCOT 188, ISO-NE 4.
- **The test.** `tests/test_audit_grid_3.py` (passes on main): the two rules in the code; MISO's two sums more than 200 MW apart in the median hour.
- **For the owner.** One rule for the whole tool moves every exchange figure on one side or the other. Default: left as it is.

### 4. The carbon figure says less than it is

- **Where.** `NowView.tsx` line 93 ("Each MWh it generated carried X kg of CO2") and line 106 ("imports counted"); `Emissions.tsx` lines 161 to 163; `YourGrid.tsx` lines 236 and 237; `docs/methods/emissions.md`.
- **Why it is wrong.** Three things a carbon accountant needs and the page does not say. (a) It is an average over all the power of the hour; the CO2 an added MWh causes is another number. (b) EIA's CO2 is each fuel's generation times one factor per fuel: which plant ran does not enter. (c) Imports carry EIA's own valuation, not a trace of the neighbour's grid.
- **How much.** (a) Hour-to-hour least squares, October 2025 to September 2026: ERCOT 142.7 kg/MWh against an average of 305.2 (standard error 6.5, independent hours assumed, so a floor); SPP 581.0 against 413.1; PJM 394.7 against 336.0; MISO 427.6 against 432.7; the Lower 48 337.6 against 335.5. (b) Natural gas CO2 over natural gas generation, 336 hours: ERCOT 417.1 to 420.3 kg/MWh (5th to 95th percentile), the Lower 48 410.3 to 412.0; coal in ERCOT 1,113.8 to 1,127.3. (c) Imported CO2 over gross imports, 13 September to 2 October 2026: NYISO 318.0 kg/MWh against its own 253.1; ISO-NE 310.3 against 208.7; the Lower 48 (Canada and Mexico) 483.8 against 356.6. Imports are 25.0 percent of NYISO's consumed CO2 over the year.
- **The test.** `tests/test_audit_grid_4.py`: ERCOT's gas factor within 1.5 percent of its median; ERCOT's marginal under two thirds of its average (both pass on main where the tables are); the words (fail on main).
- **The fix on the branch.** Words only: the card says "an average over all the power made, not what an added MWh would emit" and "imports counted at EIA's estimate"; the ranked table's note names the one factor per fuel, EIA's import estimate and the average; the note gains "What the hourly intensity is and is not" with the figures above. Drawn and read (`b4_draw_us48_now.txt`, `b4_draw_us48_clean.txt`).

### 5. What "now" is

- **Where.** `NowView.tsx` line 93; `Emissions.tsx` line 131.
- **Why it is wrong.** The sentence names four hours. Carbon's comes from EIA's workbooks, days after the hour, and it was called "the latest EIA has estimated" with no age, beside a demand hour an hour or two old. The Clean tab's "Carbon intensity now, ranked" ranks each ISO at its own latest hour: on this machine PJM's is 30 October, SPP's 31 October, the others' 2 November.
- **How much.** `carbon_intensity_hourly`'s newest hour is 72 hours before the table's build (2 November 23:00 against 5 November 23:08 UTC). The committed snapshot's complete hour is 64 hours before its build.
- **The test.** `tests/test_audit_grid_5.py`: the table's newest hour more than a day before its build, the ISOs' newest hours not all one (pass on main where the table is); the words (fail on main).
- **The fix on the branch.** Words only: "its CO2 estimates come days after the hour, so this hour is older than the hour of demand named first"; the title "Carbon intensity, each ISO's latest hour, ranked". Drawn and read (`b5_draw_us48_now.txt`, `b5_draw_us48_clean.txt`).

### 6. No screen on the snapshot's interchange

- **Where.** `grid_network.py` and `network_hourly.py` take each report as filed; `ba_supply.py` `screen` sets aside a pair-day further than `impossible_hours.MADS` median absolute deviations from its pair's median.
- **How much.** In the table's seven weeks two reports above 20,000 MW, both SPP's of its MISO tie (daily means of 89,864 and 89,814 MW on 4 and 6 October, `miso_swpp_by_day.csv`). MISO sorts first, so the rule read MISO's report; neither reached a figure. Had SPP's been read, SPP's net export would have read about 90 GW for the day.
- **The test.** `tests/test_audit_grid_6.py` (passes on main).
- **For the owner.** A screen moves a figure only in an hour such a report is read; in this window, none. Default: left as it is.

## What was checked and found right

- `completeHour`: the newest hour every pair that reported in the last 48 holds; 159 of 159 at 2026-11-22 23:00 on the committed file.
- `tiesAt` and `netExports`: each pair signed from the grid's side; the nodes' nets sum to zero.
- `pickSnapshot`: Storage only when whole and at least as new as the committed file.
- The lag: `(built - hour)` in hours, rounded, as the decisions block says.
- The carbon formula and its rounding (4 decimals), the hour start convention (EIA's hour end minus one hour), complete days and months only.
- Demand and the mix: the newest hour held, the fuels largest first, the total EIA's own (the fuels sum to 489,106 MW against its 488,990).
- CAISO's mix withheld (`CaisoMixWithheld`) and its carbon hours read an hour earlier through `caiso_join.true_hours`, as the code says.

## Not covered, or left open

- The Mix views (`MixView.tsx`, `lib/mixpage.ts`, `mix2.ts`), the stress block, the records and the region tabs' figures were not re-done; their replication (`replication/grid/`) met 1,349 of 1,349 on 19 November.
- CAISO and the Lower 48's carbon on the extract (the restatement covered six grids; the Lower 48's denominators were revised).
- The Storage copy of the snapshot (a live service) was not read; every exchange figure here is the committed file's.
- The Ask panel was not run (it calls a model).
- Two node-run tests fail on clean main on this machine (`tests/test_session1898.py` check-holds, `tests/test_session137.py` with the libuv assertion); not touched.
