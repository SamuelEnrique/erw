# Congestion: the page audited as a hostile expert would

Session 10220, 26 November 2026, chain 710 (part D, in the form of part B), the old laptop. Read as a transmission planner, an FTR trader and a developer pricing basis risk, each wanting to find `/congestion` wrong. In the form of `docs/reviews/trader-model-audit-2026-11-26.md` and `docs/reviews/curtailment-model-audit-2026-11-26.md`.

- Nothing changed on main but this file and its folder of evidence (`docs/reviews/congestion-model-audit-2026-11-26/`). No table written, no lock taken, no default moved, no model called, no request to any service.
- Each finding's test is on its own branch, `wip/audit-congestion-<n>`. The four words branches meet in `site/app/congestion/page.tsx`, so `wip/audit-congestion-words` holds all four merged (two conflicts resolved by hand, every test passing).
- **Not repeated:** the browser read of 26 November (`docs/reviews/browser-read-2026-11-26.md`, B11: rows N1, a thousands comma; N2, a finger on a cell; N3, "contingency Base Case") and the market monitors' cross-check in the method note.

## In short

- **The arithmetic is right.** Every figure the default view draws (SPP, 2026: two ranked lists of 25 constraints, nine places, the held line, the chosen constraint and its tables) comes out of an independent restatement from the page file: 245 of 245 to the digit, and the year figures rebuilt from each constraint's and place's months agree within the months' own rounding. The places' mean day-ahead LMP agrees with the warehouse's own hub price tables, a second source path, in 105 of 106 whole months to the cent (SP15 in October 2026 is 0.03 apart: finding 6).
- **One ranking across two references (finding 1, Major).** Each operator splits its price against its own reference: the energy part is identical at all of an operator's places in every month. The page ranks SPP's and CAISO's places in one table ("the largest addition first": SDG&E 2.24, SPP North 2.22) and called the part "the part of each price that came from congestion". A rank across the two means nothing. Words fixed. Ranking each operator's places separately is Samuel's ruling.
- **One element on two rows under one label (finding 2, Major).** SPP's files name no contingency until November 2021, then list the same element under BASE, and the page drops "BASE". So TEXAS_CO_TXPS_TXCO_PHSHFT_PS stands as rows 1 and 2 of "every year held", 60,293 and 31,835 hours: 92,128 hours for one element. A CAISO element bound under several contingencies is several rows, and all of them count toward "constraints" and "constraint-hours". Words fixed. Joining them is a ruling.
- **The window and its days (finding 3, Moderate).** "2026" ends on 20 November, the day the file was built, and it has not been rebuilt since. CAISO's "2023" starts on 10 August. A constraint's first and last days are UTC days, beside decisions that promise the operator's clock: 187 of SPP's 614 and 127 of CAISO's 480 such dates fall on another day by that clock. Words fixed.
- **SPP's market took in its western area on 1 April 2026, and the page did not say so (finding 4, Moderate).** SPP North's mean congestion part went from -2.07 to +1.84 USD/MWh between April to November 2025 and the same months of 2026. Words fixed, with a data request.
- **A few months and ceiling prices carry the sums (finding 5, Moderate; a data request).** SPP North's 2026 mean of +2.22 is 1.68 without January. July 2026 alone carries 45 percent of the year's sum. Twelve of SPP's detailed constraints peak at exactly 1,500.00 USD/MWh, and CAISO's shadow prices reach 8,529.24. "Cost most" weighs those hours, and this machine cannot count them.
- **What an expert's number would hold that this does not:** real-time congestion (the SP15 less NP15 spread's hourly standard deviation is 17.06 in real time against 10.45 day-ahead in 2025); losses beside congestion (1.02 of SP15's 6.01 USD/MWh spread below NP15 in 2025); flows, FTR or CRR auction prices, and nodes, none of them held.
- **Fixes:** four words branches (findings 1, 2, 3, 4, with the ERCOT wording of finding 7 on branch 4) are for landing, best as `wip/audit-congestion-words`. Three ruling lines (findings 1, 2, 3), each defaulting to "left as it is". Four data requests.

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/congestion/page.tsx` | The page (session 9000, in review, in no menu). Chooser: operator (SPP, CAISO), year (each year held, or every year held), constraint, place, a second place, the places' year. Sections: the constraints that bound most and cost most (two lists of 25), when a constraint binds (an hour-by-month table and hours by month), where congestion adds to the price and where it takes off (every place of both operators in one table), two places side by side (monthly congestion part and share, hour-by-month tables). Opens on SPP, its newest year, the constraint whose shadow price summed highest that year, SPP North hub, no second place |
| `site/app/congestion/Decisions.tsx` | The eight decisions shown on the page |
| `site/lib/congestion.ts` | The file's shape, `yearOf` (a constraint's year or all years), `maxAbs` (the shading), `monthT` |
| `site/data/conditions/congestion.json` | The page file, built 2026-11-20 19:16 UTC by the data machine's daily run and not rebuilt since (no page-file commit since 20 November). SPP constraints 2014-03-01 to 2026-11-20 (307 detailed), CAISO 2015-01-01 to 2026-11-20 (240 detailed). Places: SPP's two hubs from 2022, CAISO's three hubs and four default load areas from 2023-08-10 |
| `warehouse/derived/congestion_page.py` | The builder: from `constraints_binding_hourly` and `price_congestion_hourly`, the two monthly tables and the page file. A constraint is the table's `entity` (name and contingency); year, month and hour of the day by the operator's local clock; ranks by the size of the shadow price; the top 25 by hours and by summed size each year and over all years; a place's means, share (mean over mean) and hours above and below zero |
| `warehouse/connectors/grid_congestion.py` | The connector: SPP's Day-Ahead Binding Constraints and LMP by Settlement Location; CAISO's OASIS PRC_NOMOGRAM and PRC_LMP (DAM). The keys, the signs as printed, whole days only |
| `docs/methods/grid_congestion.md` | The method note: sources, nine decisions, the replication and the cross-check against the market monitors |
| `replication/congestion/replicate.py`, `crosscheck.py` | The replication (12,999 of 12,999 on the build of session 9000) and the cross-check (CAISO's monitor, Table 5.3: 23 of 25 within a point; SPP's monitor's four flowgates, ranks 1, 2, 7, 12) |
| `docs/state/page_files_conditions.md` | The page file's contract (cited by the page) |
| Tables read here (main copy, read only) | `iso_hub_prices_history` (NP15, SP15 from 2023-07-06; SPP North from 2024-09-01; to 2026-10-22) and `iso_dam_hub_prices` (five hubs, 2026-08-26 to 2026-11-13), for the second source path. `constraints_binding_hourly` and `price_congestion_hourly` are not on this machine |

## How every number here was computed

- **The page's own code:** `draw.mjs` draws `/congestion` with the site's components (`node --import ./register.mjs`, the site's loaders with `Brand` as a plain wrapper; the page reads only its file, so no request is answered). Views drawn: the default, CAISO, SPP every year held, two places (SPP North beside SP15), CAISO with the places' year 2023. Every marked figure (`data-fig`) collected in page order (`main_default_fig.json`).
- **The independent restatement:** `s3_restate.py` (standard library), written from the method note, the file's own rules and the page's words, not from `page.tsx`. It rebuilds each constraint's year from its months, ranks the 25 largest by hours and by summed size among the detailed constraints (a constraint in any list is detailed, so these are the 25 largest of all), and rebuilds each place's year means from its months. Then it writes each figure as the page does and compares.
- **The second source path:** `s4_lmp.py` streams `iso_hub_prices_history` and `iso_dam_hub_prices` line by line, keeping monthly sums and one year of hours (2025) for the spread. `s4c_sp15_oct.py` compares SP15's October 2026 hour by hour.
- **One rule at a time and the claims:** `s5_measures.py` and `s6_labels.py`, on the page file.
- Copies of every script and printout: `docs/reviews/congestion-model-audit-2026-11-26/`. The scripts were written to run from `runs/c10220/` of a worktree.

## The arithmetic re-done

| Figures | Compared | Agree | The gaps |
|---|---|---|---|
| The two lists of SPP 2026 (hours, mean size, highest, summed size; 25 rows each) and the nine places of 2026 (mean LMP, mean congestion part, share, hours above zero, hours below) | 245 drawn | 245 to the digit against the file's year figures written as the page writes them | none |
| The same, rebuilt from the months | 245 | 210 exactly; 35 within the months' rounding | summed sizes by 1 to 3 (each month's mean is rounded to the cent), two means by 0.01, SPP North's congestion part 2.21 against 2.22 |
| The lists' order | 50 ranks | 50 | |
| Every detailed SPP constraint's year figures from its months (hours, highest, sum, mean); total hours; the hour-by-month table's sum | 307 constraints | all | |
| The held line ("1,880 constraints bound in 121,437 constraint-hours over 324 days held in 2026") | 3 | 3 | |
| The chosen constraint (TMP128_29363, contingency 333): "Bound 7,052 hours from 2024-04-03 to 2026-11-15"; its table's sum, its line's sum, the darkest cell 62 | 5 | 5 | the dates are UTC days (finding 3) |
| SPP North's hour-by-month table: the darkest cell 30.54; the year mean from the table weighted by days | 2 | 2 | 2.217 against 2.22 |
| The places' mean day-ahead LMP by whole month, against `iso_hub_prices_history` and `iso_dam_hub_prices` (NP15, SP15, ZP26, SPP North, SPP South) | 106 months | 105 to the cent | SP15, October 2026: 46.75 against 46.78 on the same 744 hours. The two tables agree hour by hour from 1 to 21 October, so the difference lies in 22 to 31 October (finding 6) |
| Within an operator, the energy part at every place and month | every month held | identical at all seven CAISO places and both SPP hubs | the fact under finding 1 |
| A place's day-ahead spread as the sum of its parts (SP15 less NP15, SPP South less North, 2023 to 2026) | 8 years | the energy part's difference is 0.00 each time; the LMP spread equals the congestion and loss differences | |

- **Not restated, and why.** The page file's own year figures come from `constraints_binding_hourly` and `price_congestion_hourly`, which are not on this machine. The replication of session 9000 (12,999 of 12,999) was run on the build of that session. The daily run of 20 November that built today's file names `dm_test_replication` among its failed steps (commit `3b1ad41e8`), without saying which replication failed: data request (d).
- **The rules the restatement wrote again and found as the code does them:** the operator's local year, month and hour; ranks, means and highs by the size of the shadow price; summed size as hours times the mean size; a share as the mean congestion part over the mean LMP, blank when the mean LMP is not above zero; the top 25 by hours and by sum, each year and over all years; the default constraint as the newest year's largest sum; the default place as the first SPP place.

## One rule changed at a time

Each line changes one choice and keeps every other. Page file of 20 November 2026 unless a line names a price table.

| Choice the page makes | The other choice | Worth | Said on the page? |
|---|---|---|---|
| Every place of both operators ranked in one table | each operator's places apart | SPP North drawn 2 of 9 becomes 1 of 2; SDG&E stays first of CAISO's 7. SPP South (8 of 9) and ZP26 (9 of 9) stop standing beside each other | no (finding 1) |
| A constraint is a name and contingency key | one row an element (keys of one name joined) | every year held, by hours: TEXAS_CO_TXPS_TXCO_PHSHFT_PS 60,293 becomes 92,128 (the two keys never share an hour: November 2021 holds 211 and 499 of 720 hours), summed size 154,101.0 becomes 396,339.0. SPSNMTIES 1,802 and 8,114; Ozrk_B-xfmr_A 4,097 and 10,338. CAISO 2025 by sum: 39021_SC21ATP 553,893 becomes 605,827 over its contingency rows. CAISO every year held by hours: the first by element is 34112_EXCHEQUR (14,576 summed over its rows, an upper bound) where the first row is 34116_LE GRAND (11,897) | no (finding 2) |
| A constraint's first and last day as UTC days | the operator's own day | 187 of SPP's 614 and 127 of CAISO's 480 dates move back a day; the default constraint's do not | no; the decisions promised the operator's clock (finding 3) |
| SPP North's 2026 mean over every month held | without January 2026 (day-ahead mean 74.07 USD/MWh, the year's dearest month) | +2.22 becomes +1.68; without July, its largest month (45 percent of the year's sum), +1.36 | the hover gives the year's highest and lowest hour only (finding 5) |
| SPP's months set side by side across 1 April 2026 | April to November only, year on year | SPP North -2.07 (2025) against +1.84 (2026); SPP South -2.92 against -1.89 | no (finding 4) |
| The congestion part alone, side by side | with the loss part (the file holds it, the page does not draw it) | SP15 less NP15: 2025 -4.99 becomes -6.01 (loss 17 percent of the two); 2024 -7.15 becomes -7.99; 2026 -3.22 becomes -3.86. SPP South less North 2025: 0.79 becomes 1.24 (loss 36 percent) | no; finding 1's words now say it |
| Day-ahead only | real time (`iso_hub_prices_history`, the hours' mean of four 15-minute prices) | SP15 less NP15 in 2025, 8,760 hours: mean -6.01 day-ahead, -6.07 real time; hourly standard deviation 10.45 against 17.06; the mean absolute hourly gap between the two spreads 6.12; 1,596 hours more than 10 apart; lowest -70.95 day-ahead, -795.95 real time | the page says day-ahead throughout; right |
| Ranked by summed size of the shadow price | by the number of hours at a ceiling price left out | not measurable here: twelve SPP detailed constraints peak at exactly 1,500.00 USD/MWh, and 9 of 2026's 25 by sum peak at 1,400 or more; CAISO's highest held is 8,529.24, with 108 constraint-months at 1,500 or more | no (finding 5; data request a) |
| Hours above zero and below zero | (measured, not changed) | CAISO's places hold a congestion part of exactly zero in up to 29 percent of a year's hours (ZP26 2023: 1,002 of 3,457; 22 place-years at 5 percent or more), so the two counts do not add to the hours | each count says "above zero" or "below zero"; right |
| A share as mean over mean | (measured, not changed) | a month's share runs to -177.9 percent (VEA, April 2024: a low mean LMP) | the share rule is on hover; right |

## Each claim against the code

| Claim, or question | Where | What the code does | Verdict |
|---|---|---|---|
| "the part of each hub's and zone's price that came from congestion" | the lead | the operator's congestion part, measured from its own reference; the energy part is the same at every place of one operator | **Finding 1** |
| "Where congestion adds to the price and where it takes off", one table | the places section | every place of SPP and CAISO in one ranking | **Finding 1** |
| A node's congestion against a hub's | the lead, the hint | hubs and default load areas only, named as such; no node | **Right as stated**; an expert's gap (below) |
| Day-ahead against real time | lead, hovers, chart titles | day-ahead only, said throughout; the note says real time is a later step | **Right** |
| Sign conventions | the hint (source), the sign decision | SPP's shadow prices are negative and CAISO's positive; ranks, means and highs use the size. The parts add to the LMP (the note: within 0.00001 every hour; here the year spreads add up) | **Right** |
| Hours by interval or by hour | the lists, the tables | hourly day-ahead rows; a row is a constraint-hour; the fall-back day's second 01:00 counts in hour 1 | **Right**; an element under two contingencies counts twice (finding 2) |
| "N constraints bound in H constraint-hours" | the held line | N counts name and contingency keys; H counts key-hours | **Finding 2** |
| Constraints named consistently across months and years | the lists, the chooser | the operator's name unchanged; SPP's key changes in November 2021 (name alone, then name and BASE), and the label drops BASE: one element, two rows, one label | **Finding 2** |
| "Cost most: ranked by shadow price summed over the hours bound" | the heading, the cost rule | the size summed over the hours; no flow, no dollars, said | **Right as stated**; a few ceiling-priced hours may carry it (finding 5) |
| Averages hiding a few extreme days | the places' means; the lists' means | year means over every hour held; the highest and lowest hour on hover; one month carries 45 percent of SPP North's 2026 sum | **Finding 5** (a data request) |
| Losses mixed in | the share; the side-by-side | the share divides by the LMP (losses and greenhouse gas within it); the loss part is in the file and not drawn | **Right as a definition**; finding 1's words now say a spread needs the loss part |
| Held grids (ISO-NE, MISO, NYISO, PJM; ERCOT) | "Not drawn" | named with status and reason on hover; no number. The builder holds none of them (the existing test `test_session9000_congestion.py` keeps it so); no held table is downloadable | **Right**; the ERCOT decision left out the API path its own hover names (finding 7) |
| Staleness | "File built 2026-11-20" | the file's build day is printed; no page-file commit since 20 November | **Right as stated**; the newest day held was not said (finding 3) |
| The window covered | the held line, the places' caption, the months | "324 days held in 2026" without its end; CAISO's 2023 under five months; November 2026 a 20-day month drawn as a month | **Finding 3** |
| "Hours of the day and months are each operator's own clock" | the clock decision | right for hours, months and years; the first and last days are UTC | **Finding 3** |
| SPP across 1 April 2026 | every SPP figure | months and years set side by side | **Finding 4** |
| The market monitors' cross-check | the note | SPP's four flowgates rank 1, 2, 7 and 12 by name, and the page's 2025 list by key puts them at the same ranks | **Right** |
| "It gives no advice and makes no estimate of its own" | the hint | counts, sums, means, highs and shares of published figures | **Right** |

## What an expert's own number would hold that this does not

| Item | Why | Size, where measurable |
|---|---|---|
| Real-time congestion and the real-time spread | a developer's plant settles in real time; an FTR pays the day-ahead spread, but a hedge's holder lives the real-time one | SP15 less NP15, 2025: hourly standard deviation 17.06 real time against 10.45 day-ahead; 1,596 hours more than 10 apart; real time down to -795.95 |
| The loss part beside the congestion part | a basis spread is congestion and losses | 11 to 17 percent of SP15 less NP15 (2023 to 2026); 2 to 36 percent of SPP South less North |
| Congestion rent (flow times shadow price) and a dollar total | the monitors rank by it; no flow is published with the day-ahead shadow prices | not sized (said on the page) |
| FTR, CRR and TCR auction prices, the market's own forecast of a path's congestion | auction results are not held | not sized |
| Nodes, not hubs | a developer's node can sit behind a constraint the hub does not see | not held |
| The hours at a constraint's ceiling price, apart | a penalty-priced hour says the limit was relaxed, not what room was worth | data request (a) |
| SPP's and CAISO's real-time binding constraints | the note's decision 8 leaves them for later | not held |
| An element's hours, once each | an element bound under two contingencies in one hour is one congested hour to a planner | data request (a) |

## Findings, largest effect first

| # | Severity | Finding | Effect | Fix | Branch |
|---|---|---|---|---|---|
| 1 | Major | The places table ranks SPP's and CAISO's places in one list, and the lead calls the part "the part of the price that came from congestion", though each operator measures its part from its own reference | SDG&E 2.24 and SPP North 2.22 ranked 1 and 2 against two different references; a spread read from two congestion lines leaves out losses (1.02 of SP15's 6.01 below NP15 in 2025) | words; per-operator ranking: ruling | `wip/audit-congestion-1` |
| 2 | Major | One element stands on several rows: SPP's key changes in November 2021 and the label drops BASE, so one element is two rows under one label; contingency rows count as constraints and constraint-hours | TEXAS_CO_TXPS_TXCO_PHSHFT_PS 60,293 and 31,835 hours (92,128); CAISO's 2025 largest sum 553,893 of 605,827 for the element | words; joining: ruling | `wip/audit-congestion-2` |
| 3 | Moderate | The window and its days: the newest year's end unsaid, CAISO's 2023 under five months, part months drawn as months, first and last days in UTC beside a decision promising the operator's clock | 2026 ends on 20 November; 187 of 614 and 127 of 480 dates on another day by the operator's clock | words; the operator's days: ruling | `wip/audit-congestion-3` |
| 4 | Moderate | SPP's market took in its western area on 1 April 2026; the page sets SPP's years side by side with no word | SPP North April to November: -2.07 (2025), +1.84 (2026) | words; data request (c) | `wip/audit-congestion-4` |
| 5 | Moderate | Year means and summed shadow prices carried by a few months and by ceiling prices | SPP North 2026: +2.22, +1.68 without January; one month carries 21 to 53 percent of SPP's ten largest 2026 sums and 17 to 93 percent of CAISO's; 1,500.00 exactly at twelve SPP constraints | data request (a) | none |
| 6 | Minor | SP15's October 2026 mean LMP is 46.75 on the page and 46.78 in the warehouse's hub table on the same 744 hours | 0.03 USD/MWh, in 22 to 31 October | data request (b) | none |
| 7 | Minor | The ERCOT decision said ERCOT publishes "only on paths its robots file disallows"; the hover and the note add the API whose key has not been made | words | words (on branch 4) | `wip/audit-congestion-4` |

- Two Major, three Moderate, two Minor. Every branch was run with its test, the three congestion test files and `test_session9001_spp_reprice.py` (the files that read the page, its decisions, the note or the builder): 27 passed on each. On `wip/audit-congestion-words`, 45 passed, and the site's `scripts/test-reader-pages-render.mjs` gave 74 ok and no failure (`/congestion`: draws, one h1 and no level skipped, every tip with its target, every table with a caption). Each words test fails on main, two tests each (checked with the change set aside).

## 1. One ranking across two references (Major; words, and a ruling)

- **Where.** `page.tsx`: `ranked` takes every place in `PLACES` (both operators) and sorts by `congestion_mean`; the caption reads "the largest addition first". The lead said "the part of each hub's and zone's price that came from congestion".
- **Why it is wrong.** An operator's LMP is its energy part plus congestion and loss (and greenhouse gas at CAISO). The energy part is the operator's own reference price, the same at every place: the page file holds it identical across CAISO's seven places and SPP's two hubs in every month. A congestion part therefore says how far congestion put a place above or below that operator's reference. It does not say what the price would have been with no congestion, and it cannot be ranked against another operator's part measured from another reference. An FTR trader reads the difference of two places' parts within one operator, and a developer adds the loss part to get the basis.
- **How much.** 2026 as the page opens: 1. SDG&E 2.24, 2. SPP North 2.22, 3. PG&E 1.34, ... 8. SPP South -3.10, 9. ZP26 -3.16. SP15 less NP15, 2025: congestion -4.99 plus loss -1.02 makes the -6.01 spread, with an energy difference of 0.00.
- **The test.** `tests/test_audit_congestion_1.py` on `wip/audit-congestion-1`: the energy part is identical within each operator, the table mixes the two, and the spread is congestion plus loss (passes on main). The words (fails on main).
- **The fix on the branch, words only.** The lead now reads "the part of each hub's and zone's price that the operator puts down to congestion, measured against its own reference price". A line under the places table: "Each operator splits its price against its own reference: the energy part is the same at every place of one operator, so a congestion part says how far congestion put a place above or below that operator's reference price, not what the place's price would have been with no congestion. Places of one operator compare with each other; SPP's and CAISO's places are ranked in one table here, but each is measured against its own operator's reference, so a rank across the two operators means nothing. For two places of one operator, the difference of their congestion parts, with the difference of their loss parts (in the file, not drawn), is their day-ahead price spread." The share decision and the note say the same. Drawn and read: pass (`draw_b1_default.txt`); every figure unchanged (the drawn figures compared byte for byte).
- **For Samuel's ruling.** Default "left as it is". The other choice: the places table holds the chosen operator's places only. SPP North shows 1 of 2 instead of 2 of 9, and the CAISO view loses SPP's two rows.

## 2. One element on several rows (Major; words, and a ruling)

- **Where.** `congestion_page.py` keys a constraint by the table's `entity` (name and contingency). `page.tsx`'s `constraintLabel` wrote the name alone when the contingency was empty or "BASE". SPP's key is the name alone in the files until November 2021 and name with BASE after, so one element became two keys and two rows with the same label. The held line counts keys and key-hours.
- **Why it matters.** A planner asking which element bound most since 2014 reads TEXAS_CO_TXPS_TXCO_PHSHFT_PS at 60,293 hours (the browser read of 26 November took that answer), and then reads the same name again at row 2 with 31,835 hours. The element bound 92,128 hours. The two keys never share an hour: November 2021 holds 211 hours under the name alone and 499 under BASE, of 720. SPSNMTIES and Ozrk_B-xfmr_A are split the same way. In 2021's own list the element stands at rows 1 and 10. CAISO lists one element under several contingencies as several rows, each counted in "constraints bound" and each hour once per row in "constraint-hours". CAISO's largest sum of 2025, 39021_SC21ATP at 553,893, is one of its rows; the element's rows sum to 605,827.
- **The note's date.** "SPP's files before 2022 print no contingency name": the change falls inside November 2021.
- **The test.** `tests/test_audit_congestion_2.py` on `wip/audit-congestion-2`: rows 1 and 2 share one label under the old rule and sum to 92,128, the November 2021 split, and the CAISO rows (passes on main). The words (fails on main).
- **The fix on the branch, words only.** A row with no contingency reads "(no contingency named)". A hint on the held line, "(what a constraint is)", reads: "A constraint here is one element (a line, a transformer, a flowgate, a nomogram) under one contingency, as the operator lists it: an element bound under two contingencies is two constraints and two rows, and an hour it bound under both counts as two constraint-hours. SPP's files until November 2021 name no contingency, so an element SPP listed before and after then stands on two rows of every year held, one marked "no contingency named"." The names decision and the note say the same. Drawn and read: pass ("1. TEXAS_CO_TXPS_TXCO_PHSHFT_PS (no contingency named) 60,293", "2. TEXAS_CO_TXPS_TXCO_PHSHFT_PS 31,835"); every figure unchanged.
- **For Samuel's ruling.** Default "left as it is". The other choice: join an element's keys. Every year held: TEXAS_CO_TXPS_TXCO_PHSHFT_PS becomes one row of 92,128 hours (summed 396,339.0), and the lists move up a row. By element for CAISO: the 2025 largest sum goes from 553,893 to 605,827. Hours counted once for each element need the hourly table (data request a).

## 3. The window and its days (Moderate; words, and a ruling)

- **Where.** `page.tsx`: the held line "over 324 days held in 2026"; the places caption "Hubs and zones by their mean congestion part, 2026"; "Bound N hours from `C.first.slice(0, 10)` to `C.last.slice(0, 10)`", the UTC days of the file's time stamps. The clock decision: "Hours of the day and months are each operator's own clock".
- **Why it matters.** "2026" ends on 20 November (the file was built that day and not since), so a 324-day year stands beside 365-day years with only a count of days to say so. CAISO's places begin on 10 August 2023, so their "2023" holds 3,457 hours. November 2026 holds 20 days and is drawn as a month. An SPP hour from 18:00 Central standard time (19:00 in summer) is the next day in UTC, and 187 of SPP's 614 first and last dates and 127 of CAISO's 480 fall on another day by the operator's clock. The default constraint's two dates do not.
- **The test.** `tests/test_audit_congestion_3.py` on `wip/audit-congestion-3`: the newest year's days, CAISO's start, the dates that move (passes on main). The words (fails on main).
- **The fix on the branch, words only.** The held line adds ", to 2026-11-20, the newest day held; the year is not whole" in the newest year, and "the newest day held 2026-11-20" for every year held. The places caption gives the hours held ("from 2026-01-01 to 2026-11-20"), or, when places differ, "the days held differ by place: each place's on the hover of its mean LMP" (CAISO 2023: 2023-08-10 to 2023-12-31). A line under the side-by-side chart names each place's first and last day. The constraint's line adds "(days in UTC, not the operator's clock)". The clock decision and the note say the same. The local days come from the file's own time stamps through `Intl.DateTimeFormat` in each operator's time zone. Drawn and read: pass (`draw_b3_default.txt`, `draw_b3_py2023.txt`); every figure unchanged.
- **For Samuel's ruling.** Default "left as it is". The other choice: print the operator's own days for a constraint's first and last hour (187 of 614 SPP dates and 127 of 480 CAISO dates move back a day).

## 4. SPP across 1 April 2026 (Moderate; words, and a data request)

- **Where.** Every SPP figure. SPP's files name its western balancing area (SWPW) from 1 April 2026 (`docs/methods/spp_dam_cleared_energy.md`, the codebook's SPP tables, `docs/methods/ba_boundaries.md`: "Southwest Power Pool's western expansion of April 2026").
- **Why it matters.** The constraint set, the reference and the flows of a market that took in a new area may change. The page ranks SPP's 2026 constraints and sets SPP's hubs' years side by side with no mark. SPP North's mean congestion part turned from -3.69 (2025) to +2.22 (2026), and from -2.07 to +1.84 over April to November. The cause is not known here: January 2026 (+7.27) and July 2026 (+10.31) carry much of it (finding 5).
- **The test.** `tests/test_audit_congestion_4.py` on `wip/audit-congestion-4`: the note on file says SPP's files name SWPW from 1 April 2026, and SPP North's part changed sign (passes on main). The words (fails on main).
- **The fix on the branch, words only.** Under SPP's lists: "SPP's market took in its western area on 1 April 2026 (SPP's files name the area SWPW from that day), so SPP's constraints and price parts from April 2026 may be those of a larger market than before. The page sets SPP's months and years side by side across that day with no mark, and whether SPP's hubs' congestion parts moved because of it is not known here." The operators decision and the note say the same. Drawn and read: pass (the line shows on SPP's views, not on CAISO's); every figure unchanged.

## 5. A few months and ceiling prices carry the sums (Moderate; a data request)

- **Where.** The places' year means (every hour held, equally) and "Cost most" (the size of the shadow price summed over the hours bound).
- **How much, from the page file.** SPP North 2026 is +2.22, +1.68 without January (a month whose day-ahead mean was 74.07 USD/MWh) and +1.36 without July, which carries 45 percent of the year's sum. Among the ten largest sums of 2026, one month carries 21 to 53 percent of SPP's and 17 to 93 percent of CAISO's (CAISO's ninth, 24723_CONTROL to TAP189 under the base case: 93 percent in March 2026). SPP's highest shadow price is exactly 1,500.00 at twelve detailed constraints, and 9 of 2026's 25 by sum peak at 1,400 or more. CAISO's highest held is 8,529.24, with 108 constraint-months at 1,500 or more and three constraints peaking at exactly 1,000.00. A shadow price at a round ceiling reads as the price at which the market's software relaxes the limit, not a value the market found. That reading is the auditor's, not checked against either operator's rules on file.
- **Why no branch.** The page says what it computes, and the highest is beside every sum. The hours at a ceiling and their share of each sum need the hourly table: data request (a). Default "left as it is".

## 6. SP15's October 2026 (Minor; a data request)

- The page's mean day-ahead LMP for SP15 in October 2026 is 46.75 over 744 hours. `iso_dam_hub_prices` gives 46.78 over the same 744 hours. `iso_hub_prices_history` agrees with `iso_dam_hub_prices` hour by hour from 1 to 21 October, so the difference (15 to 30 USD/MWh summed over the month's hours, given the two means' rounding) lies in 22 to 31 October. NP15 and ZP26 agree that month. Data request (b).

## 7. The ERCOT decision (Minor; words, on branch 4)

- The decision said ERCOT publishes "only on paths its robots file disallows". The hover beside it and the note add "or through an API whose key has not been made". Branch 4 brings the decision to the hover's words.

## What was checked and found right

- Every figure the default view draws (245), the lists' order, the held line, the chosen constraint and its tables, against an independent restatement.
- The places' mean day-ahead LMP against the warehouse's own hub tables, 105 of 106 whole months to the cent.
- The parts add up: within each operator the energy part is the same everywhere, and a spread is its congestion and loss differences.
- Signs as printed and ranks by size; day-ahead throughout; hours by the operator's clock; the share's blank when the mean LMP is not above zero.
- No held or paused operator's number: the five are named with reasons, and the builder holds none of them.
- The market monitors' SPP flowgates at ranks 1, 2, 7 and 12 on the page's 2025 list, as the note says.

## Not covered, or left open

- The hourly tables are not on this machine. Every check of a figure against the hours is the four data requests.
- The `/conditions` page (the same chain's other page) is not audited here.
- The monthly charts and the hour-by-month tables of a second place were drawn (view "two") but their cells were not restated beyond the default place's table.

## Landing, rulings and data (returned to the chain's main session)

- **For landing (words only):** `wip/audit-congestion-words` (`45e118e40`) holds branches 1, 2, 3 and 4 merged onto origin/main; 45 tests and the reader render pass; drawn and read. It is best landed alone. Each branch alone is also clean on origin/main: `wip/audit-congestion-1` (`9bb3a6d57`), `-2` (`e268ba266`), `-3` (`6a134c972`), `-4` (`e3033c44a`). Any two of them conflict in `site/app/congestion/page.tsx` or the note.
- **For Samuel's ruling, default "left as it is":** finding 1, the places table holds one operator's places (SPP North 2 of 9 becomes 1 of 2); finding 2, an element's keys joined (TEXAS_CO_TXPS_TXCO_PHSHFT_PS 60,293 becomes 92,128 hours; CAISO's 2025 largest sum 553,893 becomes 605,827); finding 3, a constraint's first and last day by the operator's clock (187 of 614 SPP and 127 of 480 CAISO dates move back a day).
- **Data requests:** (a) on `constraints_binding_hourly`, for SPP and CAISO by year: the hours whose shadow price's size is at the year's ceiling values (SPP exactly 1,500.00 or more; CAISO 1,000.00 and above), their share of each top-25 constraint's summed size, and each element's distinct hours (`x_constraint`, unique `ts_utc`) against its key-hours. (b) `price_congestion_hourly` `lmp_dam` at `TH_SP15_GEN-APND`, 22 to 31 October 2026, against `iso_dam_hub_prices` hour by hour (page 46.75, table 46.78 on 744 hours). (c) SPP, March against April 2026: distinct constraints and constraint-hours a day, and both hubs' congestion part by day, to see a break at 1 April 2026. (d) `replication/congestion/replicate.py` run on the page file of 20 November 2026 (the daily run lists `dm_test_replication` as failed).
