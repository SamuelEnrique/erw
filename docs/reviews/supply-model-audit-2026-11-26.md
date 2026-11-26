# Supply and trade: its figures audited as a hostile expert would

Session 10222, chain 710 part D, 26 November 2026, the old laptop. `/supply` ("Supply and trade", platform tool listed under Prices), read as a utility resource planner and a fund analyst sizing what is burned to make the power, what the oil and gas markets hold, and what is coming. The Grid audit of tonight (`grid-model-audit-2026-11-26.md`, the Grid tool's mix and carbon) and the demand audit (`demand-model-audit-2026-11-26.md`) are not repeated; nor are the reader's rows of `supply-read-2026-11-16.md` and `supply-regions-read-2026-11-19.md`.

- Nothing changed on main but this file, its evidence folder (`docs/reviews/supply-model-audit-2026-11-26/`) and the session report. No table written, no lock taken, no default moved, no model called, no live service asked, no web read.
- Each finding has its own branch, `wip/audit-supply-<n>` (the table of branches below).

## In short

- **The arithmetic is right.** Every figure the default view prints in its nine tables was re-done from the warehouse's tables and the page file's newest values by a restatement that imports none of the site's or the warehouse's code: 618 of 623 printed cells of 89 rows equal to the digit, the five headline cards and the eight "outside the range" lines equal, and the fuel burned for power re-done from EIA-930's workbooks hour by hour (16 rows: 637 of 637 weekly values the workbook can settle, and every year, five-year and surprise figure equal). The five other cells are percents of three series under 0.4 Bcf/d, which the file's four-decimal copy cannot settle.
- **California's gas burned for power is compared across a change of source (finding 1).** From 16 December 2025 the row is CAISO's own supply; its year before and its five years are EIA's, whose California "natural gas" ran 30.5 percent above CAISO's own in 2024 and 47.3 percent in 2025. The page prints -0.43 Bcf/d (-22.8 percent, "looser") on the year; on CAISO's own figures throughout it is +0.01 (+0.8 percent). The seven grids' total on the year: +3.49 percent printed, +6.46 like for like. Nothing on the page says so. Words for landing; the figure is the owner's.
- **"Normal for the season" is a five-year average, which for a series with a trend or a change of level is not the season (finding 3).** Permian gas +33.4 percent "looser" against normal while +9.1 on the year; New York's oil burned for power -100 percent against a five-year average of 9.51 kb/d, a series whose level fell 94 percent from 2022 to 2024. The note says it of positioning only. Words, for landing.
- **A held grid's row reads "licensed source needed" (finding 2).** NYISO's and ISO-NE's day-ahead cleared rows are held for a license (the hover says so); the face says a licensed source is needed, as PJM's row does, though the ERW holds both and the price board writes "license needed". The words of the read of 16 November (row 1) were lost when the builder began writing the status itself. Words, for landing.
- **The production rows' newest months are EIA's estimates, revised every month (finding 4).** The source line says "history only"; between the Outlook's copies of 9 October and 17 November the same months moved by up to 3.94 percent (Bakken gas, July 2026), more than several printed monthly changes. Words, for landing.
- **Smaller:** the week of the join (ending 19 December 2025) is built on both sources (1.19 Bcf/d against 0.99 on CAISO's own; one point of the California line, finding 1's branch); the storage regions share names with the electricity regions of the section below (finding 5, words).
- **Right as stated:** the three comparisons, the surprise as the change against the five-year average change (never "expectations"), 52-week years, units, the LNG terminals' rule, the net imports' sign, positioning's three-year range, the release calendar, the heat rates as stated assumptions, a blank hour never read as zero, whole weeks only, held grids: no operator's held table reaches a figure; ISO-NE, MISO and NYISO reach the burn rows only through EIA-930 (public domain).
- **What a planner or analyst would add:** measured burn (EIA's monthly power-sector gas by state, or EIA-923, to set the derived burn against: a data request), the capacity that burns it and what is coming (EIA-860M, held, on no page linked from here), weekly gas production and an analysts' consensus (licensed), implied oil demand (not pulled).

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/supply/page.tsx` | The page. The five headline cards (Week, Year, Normal), "Changes outside the five years' range" (eight), "Next releases", the group chips, the seasonal bands (gas storage and four stock series), nine tables (one a group), "The whole country" (`components/supply/Country.tsx`), the decisions block, the downloads. Every figure is the file's; the page only chooses and writes. Server side it holds a held grid's cleared row (`holdRows`), writes units and states in words |
| `site/lib/supply.ts` | The types, `holdRows`, unit and state words, `latestTitle` (a gas month's volume; a net import below zero), `burnWeekWords`, `dateWords`, number formats (`places`, `fmt`, `signed`, `pct`), `reading` (tighter or looser), `surprises` (ordered by the surprise over the width of the five changes), `HEADLINE`, the address, `nextRelease` |
| `site/components/supply/SupplyCharts.tsx` | `Band` (this year, last year, the five years' mean and range) and `Trend` (the last 52 values) |
| `site/components/supply/Country.tsx`, `site/lib/countrytrade.ts` | "The whole country": EIA's thirteen regions, net imports by neighbour, each side's report, who trades with whom, the mix by month (section's own audit: `supply-regions-read-2026-11-19.md`) |
| `site/lib/decisions.ts` `SUPPLY_DECISIONS` | The eleven decisions at the foot, word for word in the note |
| `site/data/supply.json` | The page file: 100 rows, built 2026-11-17 08:45 UTC. Each row's latest, its period before, its year before, its five-year average with lowest and highest, its change and surprise, its last 52 values and its seasonal band |
| `warehouse/derived/supply_page.py` | The builder: `compare` (the three comparisons and the surprise), `season`, the weekly rows (EIA's storage and petroleum reports), the monthly rows (the Outlook's regions, gas trade per day, LNG terminals by the 5,000 MMcf rule, the other points as the total less those named), positions (CFTC managed money), `burn_rows` (EIA-930 hours through `warehouse/derived/mix_profile.py`'s held hour, whole local days, stated heat rates and heat contents, weeks ending Friday), `cleared_rows` (each operator's report, seven whole local days), `calendar` |
| `warehouse/derived/mix_profile.py`, `caiso_join.py` | The hours the burn rows read: EIA's Adjusted columns, a held hour (net generation above zero, the sources within 5 percent of it, PJM 15, no main source blank), California's late hours set back, California from 16 December 2025 from CAISO's own supply |
| `warehouse/connectors/eia_supply.py` | The four EIA tables; the Outlook's months to three before the run |
| Notes | `docs/methods/supply_and_trade.md` (with its replication and cross-checks), `generation_mix_hourly.md`, `eia930_caiso_break.md`; `replication/supply/` |

## The default view re-done, to the digit

The page is drawn with its own default export (`draw_supply.mjs`: no build, no server, every request refused, the font stood in for). It marks 188 figures (`data-n`) and 1,387 in the whole-country section (`data-cn`); its text and hovers are in `main_default.txt`.

- **The restatement** (`restate.py`, standard library, none of the warehouse's or the site's code, written from the note's "The three comparisons", "The surprise", "Notes on the series" and "Day-ahead energy cleared"). The history of each series is the main copy's table, read only (the weekly tables of 12 November, which end three to four weeks before the file's newest week, and the monthly of 9 October, which end with July 2026); the newest values, which those copies do not reach, are the page file's own last 52 values. Where both hold a date the file's value is used and the difference is counted (EIA's revisions, below).
- **The burn rows** (`burn.py`, standard library and the workbook reader, from the note's "Fuel burned for power" and the held hour of `generation_mix_hourly.md`): each grid's EIA-930 workbook of 3 October 2026 (the main copy's raw folder) streamed hour by hour, the held hour, whole local days, the fuel named in every hour, the stated heat rate and heat content, weeks ending Friday. California only before 16 December 2025 (EIA's side, its late hours set back). `burn_cmp.py` sets each week beside the file's.
- **Results** (`restate.out`, `burn_cmp.out`, `diffs.out`):

| What | Page | Restated |
|---|---|---|
| Printed cells of the nine tables (latest, date, period before, year, five-year average, against it, surprise) | 623 in 89 rows | 618 equal to the digit; 5 percents of three series under 0.4 Bcf/d (LNG at Elba Island, every other point of exit, LNG imports) that the file's four-decimal copy cannot settle (the builder takes them at full precision) |
| The file's own figures behind them | 89 rows | 68 equal within 0.00006; the 21 others differ only past the file's fourth decimal (percents formed from four-decimal values; the Outlook's months revised between the two copies, below) |
| Headline cards (Lower 48 storage 3,862 Bcf; commercial crude 414.4, Cushing 27.36, gasoline 210.8, distillate 103.3 million bbl) | 5 | 5 equal; their Week, Year and Normal lines are the same figures as the rows' |
| "Changes outside the five years' range" | 8, in order | the same 8 in the same order |
| Burn rows' weekly values that EIA's workbook settles | 637 | 637 equal (every grid's to 2 October 2026; California's and the total's to the join) |
| Burn rows' year, five-year average and surprise | 16 rows | 16 equal |
| ERCOT's gas burned for power, week ending 13 November 2026 | 4.66 Bcf/d; +2.11 (+83.1 percent) on 2.54 (week ending 14 November 2025); five-year average 3.04 (2.11 to 3.69) | the same; the five weeks 2.54, 3.55, 3.69, 3.28, 2.11 |
| The seven grids together, week ending 30 October 2026 | 20.48 Bcf/d, +0.69 (+3.5 percent) on the year | the same |

- **The whole country** (`regions_replicate.out`): the section was not restated here; its replication, written from the note and the contract and not from the page's code (`replication/supply/replicate_regions.py`), was run on the files now on main (rebuilt 20 November, after the replication of 19 November): **45,313 of 45,313 figures over 27 files**, every region and year drawn by the site's own code (117 drawings).

### EIA's revisions between the two copies

- The Outlook's regions (`revs.out`): of each series' last 51 months held in both, 5 to 31 moved between the copy of 9 October and the file of 17 November, 5 to 7 of them in 2026; the largest, Bakken marketed gas July 2026, 3.4365 to 3.5717 Bcf/d (+3.94 percent); Haynesville crude March 2026 +2.42 percent; Eagle Ford crude June 2026 +1.01 percent.
- Gas trade: LNG exports, all terminals, July 2026, 16.7347 to 16.7293 Bcf/d; Corpus Christi Stage 3 (`yccpl`) July 1.5255 to 1.5201. Weekly storage and petroleum: no revision of a week both copies hold.

### One rule changed at a time

`measures.py` (`measures.out`) on the restated weeks and the page file.

| Rule | The page | Changed to | Measured worth |
|---|---|---|---|
| California's gas before 16 December 2025 | EIA-930's | CAISO's own supply throughout (`caiso_own.py`) | on the year -0.43 Bcf/d (-22.8 percent) becomes +0.01 (+0.8); the five-year average 1.89 becomes 1.73 (against it -23.0 becomes -15.6 percent); the seven grids together on the year +3.49 becomes +6.46 percent |
| The week of the join | built on both sources | CAISO's own alone | week ending 19 December 2025: 1.19 becomes 0.99 Bcf/d (a point of the line, in no default figure) |
| The gas heat rate | 7.6 MMBtu per MWh | 7.0; 7.2; 7.8; 8.0 | the seven grids together 20.48 Bcf/d becomes 18.87; 19.41; 21.02; 21.56; every percent unchanged (the rate scales every value alike) |
| The five-year average | the five values 52 to 260 weeks back | the year before alone | Permian marketed gas: against normal +7.75 Bcf/d (+33.4 percent), against the year before +2.57 (+9.1); New York oil -9.51 kb/d (-100 percent) against a year before of 0.01 |

## Each claim against the code

- **Generation against capacity; nameplate against summer capacity; capacity factors and their hours.** The page holds no capacity: no MW of a fleet, no factor, no addition or retirement. The burn rows are energy (MWh of EIA-930 net generation) times a heat rate, with no capacity anywhere. Nothing claims otherwise. A planner sizing what generates and what is coming finds it on no page linked from here (below).
- **Net against gross generation.** EIA-930 is net generation; the stated heat rates are EIA's operating heat rates, fuel over net generation (Electric Power Annual, Table 8.1, as the note cites). An hour below zero counts as zero. Consistent.
- **Imports' place.** A grid's burn is what its own plants burn: gas burned in Arizona for California's imports is not in California's row. The note says "burn in the seven ISO grids, not the whole country's". Right. The whole-country section's net imports are each side's report, never a share of demand (`SHOWN.importShare` off). Right.
- **A share of what total.** The burn rows carry no share. The whole-country mix is each source's share of the region's net generation, said with why a month need not add to 100. Right.
- **Months and weeks not whole.** A burn week is seven whole local days; a cleared week the same; a mix month 90 percent of its days, said. A grid whose newest week is older says so on hover (`burnWeekWords`). Right.
- **EIA's revisions.** Weekly crude production is called EIA's estimate, revised in its monthly data (the note's cross-check: 0.3 to 2.8 percent below the survey). The Outlook's regional months are called "history only" on the page though the newest are EIA's estimates and move each month: **finding 4.**
- **A change of source.** California's burn rows join EIA's hours to CAISO's own on 16 December 2025 and compare across it: **finding 1.**
- **"Normal for the season".** The five-year average of a series with a trend (production, positioning) or a change of level (New York's and SPP's oil) is not the season: **finding 3.**
- **Region against state against balancing area.** The burn rows are EIA-930 balancing authorities (CISO, ERCO, ISNE, MISO, NYIS, PJM, SWPP), called the seven ISO grids. Storage is EIA's five storage regions; refining is by PADD, said; the whole-country section is EIA's thirteen electricity regions. Two of the storage names (Midwest; Pacific beside Northwest) read as the electricity regions of the section below: **finding 5.**
- **Held grids.** NYISO's and ISO-NE's cleared rows carry no figure in the file or on the page (status and note only, session 7051); MISO's is paused, PJM's licensed. The burn rows of ISO-NE, MISO and NYISO are EIA-930's (public domain, `eia930_*` public in `license_status.json`). No operator's held table reaches a figure. The face of a held row: **finding 2.**
- **The as-of date.** "built 17 Nov 2026" in the header, the build time on hover, each row's own date; the release calendar worked out from the rule each time the page is read. The weekly rows are of 6 November, the burn of 13 November (MISO 6 November, the total 30 October, each said on hover), the monthly of August 2026. Right.
- **Tighter or looser.** Written only where the note gives a reading; a difference written as zero carries none. Restated in every cell. Right. (Coal and oil burn read as a gas desk reads burn: the read of 16 November, row 18, for the owner.)
- **The surprise.** Never "expectations"; the outside mark only when all five changes are held. Right.

## What a planner's or an analyst's own number would hold that this does not

- **Measured burn.** The burn rows are derived at one fleet heat rate per fuel; ERCOT's or PJM's fleet differs, and at 7.0 to 8.0 MMBtu per MWh the seven grids' level moves from 18.87 to 21.56 Bcf/d. EIA publishes power-sector gas consumption by state each month (Natural Gas Monthly) and by plant (EIA-923); this machine holds neither. A data request (row 1).
- **The fleet and what is coming.** EIA-860M's operating, planned and retired generators are in the warehouse (`eia860m_*`) and on no page linked from here; a planner sizing burn asks which plants burn it and which retire.
- **Weekly gas production, a consensus, implied oil demand.** Licensed (S&P Global, the polls) or not pulled (product supplied), as the note says.
- **The other side of a grid's burn.** Imports' fuel (California's from the Southwest) is not held.

## Findings

| # | Severity | Finding | Measured | Branch | Kind |
|---|---|---|---|---|---|
| 1 | Moderate | California's gas burned for power, and the seven grids' total, are compared across the change from EIA's hours to CAISO's own (16 December 2025); EIA's California gas ran far above CAISO's own in the years compared against; the page says nothing | EIA over CAISO's own: +0.1 percent in 2021 and 2022, +0.8 in 2023, +30.5 in 2024, +47.3 in 2025; California on the year -22.8 percent printed, +0.8 like for like; the total +3.49 printed, +6.46 like for like | `wip/audit-supply-1` (words); `wip/audit-supply-2` (the figure) | words, for landing; figure, the owner's |
| 2 | Minor | NYISO's and ISO-NE's cleared rows, held for a license, read "licensed source needed" on the face | 2 rows; the hover says "Held, not shown" | `wip/audit-supply-3` | words, for landing |
| 3 | Moderate | "Normal for the season" is a five-year average; for production and positioning (trend) and New York's and SPP's oil (a change of level) it is not the season | Permian gas +33.4 against normal, +9.1 on the year; New York oil in the same week of 2021 to 2025: 19.0, 27.2, 1.23, 0.07, 0.006 kb/d, the five-year average 9.51 | `wip/audit-supply-4` | words, for landing |
| 4 | Minor | The Outlook's regional months are labelled "history only"; the newest are EIA's estimates and move each month | up to 3.94 percent between two monthly copies (Bakken gas, July 2026); Eagle Ford crude's printed change -11 kb/d against an 8.4 revision of July | `wip/audit-supply-5` | words, for landing |
| 5 | Minor | The storage regions' names read as the electricity regions of the section below | "Midwest" in both, with other states | `wip/audit-supply-6` | words, for landing |

### 1. California's burn across a change of source

- **Where.** `warehouse/derived/supply_page.py` `burn_rows` reads `mix_profile.hours_of("caiso")`, which is EIA-930's hours before `caiso_join.JOIN` (2025-12-16T08:00Z) and CAISO's own supply from it; `compare` sets the latest week against weeks 52 to 260 back with no regard to the join. The seven grids' total sums California's weeks. Page: the CAISO burn rows' "On last year", "Five-year average", "Against the average" and "Change against the five-year average change"; the total's.
- **Why it is wrong.** The note says California is CAISO's own from 16 December 2025 and nothing about the comparisons. `eia930_caiso_break.md` found EIA's California "natural gas" about 73 GWh a day above CAISO's own before the break (geothermal and more). So a fall against 2024 and 2025 is partly a change of source.
- **How much** (`measures.out`, `burn_cmp.out`). Over the weeks both hold, EIA's California gas burn over CAISO's own: 2021 +0.1 percent, 2022 +0.1, 2023 +0.8, 2024 +30.5, 2025 +47.3. Week ending 13 November 2026: the page's year before 1.88 Bcf/d (EIA, 14 November 2025), CAISO's own 1.44: -0.43 (-22.8 percent, "looser") printed, +0.01 (+0.8) like for like; the five-year average 1.89 printed (1.65 to 2.14), 1.73 on CAISO's own (1.29 to 2.14). The total of 30 October 2026: +0.69 Bcf/d (+3.49 percent) printed, +1.24 (+6.46) with CAISO's own in its base. The week of 13 to 19 December 2025 is three days of EIA's and four of CAISO's own: 1.19 against 0.99 on CAISO's own alone (one point of the line). CAISO's own weeks, restated by `caiso_own.py`, equal the file's in 41 of the 44 weeks after the join (the three others: the week of the join and two weeks this machine's copy of CAISO's file holds short).
- **The tests.** `tests/test_audit_supply_1.py` (the words, on `wip/audit-supply-1`; the measure where this evidence is in the checkout); `tests/test_audit_supply_2.py` (the figure, on `wip/audit-supply-2`: -22.8 against +0.8, 1.89 against 1.73, +3.49 against +6.46, the week of the join).
- **The fix on the branch.** Words only: each cell whose comparison crosses the join says on hover "California is EIA-930's hours before 16 December 2025 and CAISO's own supply by fuel from that day, so this comparison crosses a change of source. EIA's California natural gas ran about 30 percent above CAISO's own in 2024 and about 47 percent above it in 2025 (the weeks both hold), so the change against those years is lower than the gas burned alone would make it." (the total: "California's part of this total is ..."); the note gains the paragraph with the figures. Drawn and read (`b1_cmp.out`): the 188 figures, the 1,387 of the section and the visible text unchanged; seven hovers gain the words.
- **For the owner.** California on CAISO's own supply throughout (its history from `caiso_fuel_supply_history`) moves California's gas burn on the year from -22.8 to +0.8 percent, its five-year average from 1.89 to 1.73 Bcf/d, and the seven grids' total on the year from +3.49 to +6.46 percent. Default: left as it is.

### 2. A held row says a source is needed

- **Where.** `site/lib/supply.ts` `holdRows` acts only on a row with status "ok"; since session 7051 `supply_page.py` `cleared_rows` writes NYISO's and ISO-NE's rows itself with status "licensed" and a note ending "Held, not shown" (NYISO) or "held, not shown" (ISO-NE); the page draws status "licensed" as "licensed source needed".
- **Why it is wrong.** The ERW holds both tables and may not show them; "licensed source needed" is PJM's words, for a source it does not hold. The price board writes a held grid "license needed", and the read of 16 November fixed these two rows to it (row 1); the builder's change undid the words. `site/scripts/check-supply.mjs` expects "license needed" for a held grid; read against its code, it would fail on main for that reason (not run: it reads a built site).
- **The fix on the branch.** A cleared row with status "licensed" whose note says it is held is drawn as "held" ("license needed"), its note on hover; PJM's row unchanged. Drawn and read (`b3_cmp.out`): the two rows' words change, nothing else. Test: `tests/test_audit_supply_3.py`.

### 3. Normal for the season

- **Where.** The headline "Tighter or looser than last week, last year and normal for the season"; the column "Five-year average" (no hover) and "Against the average", in every table; the note says "positioning has no season" and no more.
- **Why it is wrong.** A five-year average is the season only for a series with a season and no trend. Production has grown (Permian marketed gas: 23.18 Bcf/d five-year average, 28.36 a year before, 30.93 now: "looser" against normal by +33.4 percent while +9.1 on the year; nine of twelve regional rows "looser"). New York's oil burned for power changed level within the five years (the same week of 2021 to 2025: 19.0, 27.2, 1.23, 0.07, 0.006 kb/d; yearly means 25.4 in 2022, 1.5 in 2024), so 0.00 reads -100 percent against 9.51. SPP's oil the same, smaller (about 1.2 in 2021 to 2023, 0.1 in 2025).
- **The fix on the branch.** The head "Five-year average" of each table says on hover what it is and where it is not the season; the note gains the paragraph. Drawn and read (`b4_same.out`): the page is main's with that one hover on nine heads. Test: `tests/test_audit_supply_4.py`.

### 4. "History only"

- **Where.** The production rows' source line (`supply_page.py`: "EIA, Short-Term Energy Outlook, history only (eia_basin_production_monthly)"), on the hover of each row's name.
- **Why it is wrong.** The connector keeps the Outlook's months to three before its run (`eia_supply.py`, `HISTORY_LAG = 3`) because the newest are EIA's estimates; they move with each Outlook. `revs.out`: between the table of 9 October and the file of 17 November, 5 to 7 months of 2026 moved in every region; Bakken gas July 2026 +3.94 percent, Haynesville crude March 2026 +2.42, Eagle Ford crude June 2026 +1.01; Eagle Ford crude's printed change on the month before, -11 kb/d, against a revision of +8.4 to July itself.
- **The fix on the branch.** The builder's source words: "EIA, Short-Term Energy Outlook, without its forecast months: the newest months are EIA's estimates, revised each month (eia_basin_production_monthly)", which reach the page at the next build of the page file (drawn on a copy of the file with the new words, `b5_cmp.out`: twelve hovers change, the figures and the visible text not; the table to download is still found from the bracketed name). The note gains the revisions. Test: `tests/test_audit_supply_5.py`.

### 5. Two kinds of region on one page

- **Where.** "Natural gas in storage": East, Midwest, Mountain, Pacific, South Central (EIA's storage regions); "The whole country": EIA's thirteen electricity regions, among them a Midwest.
- **The fix on the branch.** The storage table's heading says on hover that its regions are the storage report's groups of states, not the electricity regions below. Drawn and read (`b6_same.out`). Test: `tests/test_audit_supply_6.py`.

## The branches

Each from `origin/main`, pushed. Tests run on each: the branch's own test and every test file that reads a changed file (12 or 13 files; on the merged branch 19), all passing but `tests/test_session8430_supply_regions.py::ThePageDrawn::test_the_whole_country_section`, which fails the same way on a clean `origin/main` (not this audit's). Every words branch that changes the page rewrites the pin of session 8430 (`site/scripts/pins/supply-page-8430.json`, a hash of the drawn page at 103 addresses on the pin's own copy of the input files) from its own code; the pin holds "add, never change" and any words change outside the whole-country section moves it. On each branch no address's count of checked figures moved (`pin_*_diff.out`).

| Branch | Head | Kind | Files | Test | Drawn and read |
|---|---|---|---|---|---|
| `wip/audit-supply-1` | `d29a45b4a` | words, for landing | `site/lib/supply.ts`, `site/app/supply/page.tsx`, `docs/methods/supply_and_trade.md`, the pin | `tests/test_audit_supply_1.py` | pass |
| `wip/audit-supply-2` | `608da1374` | figure, not for landing | test only | `tests/test_audit_supply_2.py` | not drawn (no words) |
| `wip/audit-supply-3` | `17ccae413` | words, for landing | `site/lib/supply.ts`, `docs/methods/supply_and_trade.md`, the pin | `tests/test_audit_supply_3.py` | pass |
| `wip/audit-supply-4` | `ded60b390` | words, for landing | `site/app/supply/page.tsx`, `docs/methods/supply_and_trade.md`, the pin | `tests/test_audit_supply_4.py` | pass |
| `wip/audit-supply-5` | `5ce84b8e9` | words, for landing | `warehouse/derived/supply_page.py`, `docs/methods/supply_and_trade.md` | `tests/test_audit_supply_5.py` | pass (on a copy of the file with the new words) |
| `wip/audit-supply-6` | `b01b29897` | words, for landing | `site/app/supply/page.tsx`, `docs/methods/supply_and_trade.md`, the pin | `tests/test_audit_supply_6.py` | pass |
| `wip/audit-supply-words` | `36f0bfae8` | words, for landing: 1, 3, 4, 5 and 6 merged | the same | the five | pass (`bw_cmp.out`) |

The words branches conflict only in the pin (each rewrites it) and in two neighbouring constants of `site/app/supply/page.tsx` (4 and 6); `wip/audit-supply-words` is the five merged, the pin rewritten once from the merged code (103 of 103 addresses moved, no count of figures). Land that branch, or one branch alone.

## Data requests (rows for the data machine)

1. **Measured burn beside the derived.** From EIA's Natural Gas Monthly (deliveries to electric power consumers, by state) or EIA-923 (fuel consumed by plant, with each plant's balancing authority): for each of the seven balancing authorities, or the states that make them up, each month of 2024 and 2025, the gas burned for power in Bcf a day, beside the burn rows' monthly mean from `site/data/supply.json`'s rule (EIA-930 net generation x 7.6 / 1.037e6). To size the stated heat rate's error by grid.
2. **The Outlook's revisions.** From the archive's vintages of `eia_basin_production_monthly` (`warehouse/archive`): for each region and each month of 2025 and 2026, the value as first written and as held now, to size how far a printed monthly change moves after it is printed.

## What was checked and found right

- The three comparisons and the surprise in every row: 52-week years (exactly 364 days on EIA's Fridays), the nearest within 3 days, all five or none, the outside mark, the change of each of the five years taken a step before each.
- The units: thousand barrels over 1,000; gas trade MMcf over 1,000 and the month's days (August 31); the month's volume on hover.
- The LNG terminals named by the 5,000 MMcf rule: the same ten from the main copy's table; "every other point" as the total less those ten.
- The cleared rows: CAISO, SPP and SPP West weeks of seven whole local days, equal; held, paused and licensed rows with no figure.
- Positioning: managed money's net and its place in 156 weeks, equal.
- The order of the eight surprises: the surprise over the width of the five changes.

## Not covered, or left open

- California's EIA-side weeks were restated with the late hours set back and the month of the join left out, as the note says; the gap months of 2019 and 2020 (CAISO's own) were not, and are in no default figure.
- The weekly petroleum and storage rows' newest weeks (6 November) are the file's: this machine's tables end three weeks earlier. Every comparison's history is the table's.
- The Ask panel was not run (it calls a model).
- The release calendar's dates were not set against EIA's and the CFTC's pages (no web read).
