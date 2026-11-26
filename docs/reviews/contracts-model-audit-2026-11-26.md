# The contracts page: the model audited as a hostile expert would

Session 10226, 26 November 2026, chain 710 (part D, in the form of part B), the old laptop. Read as a power and gas trader, or a utility's risk manager, who would use `/contracts` ("Where power contracts are being struck") to set a filed price, term and counterparty against the market and wants to find it wrong. In the form of `docs/reviews/battery-model-audit-2026-11-20.md` and `docs/reviews/trader-model-audit-2026-11-26.md`.

- Nothing changed on main but this file and its folder of evidence (`docs/reviews/contracts-model-audit-2026-11-26/`). No table written, no lock taken, no default moved, no model called, no request to any service.
- **What the page is, and is not.** `/contracts` reads FERC's Electric Quarterly Reports, the contract files of one quarter's filings (`ferc_eqr_contracts`, internal). It holds no futures, no forwards, no forward curve, no CFTC positions, no capacity auction and no ancillary market price: none of those is on the page, in its notes or in its tables (grep of `site/app/contracts/`, `site/lib/contracts.ts` and the four method notes it links). The brief's questions on settlement against last trade, rolls, a curve's dates and positions' report dates have nothing to bite on here; the questions that do apply (units, dates, which contracts are counted, staleness, held data) are answered below.
- **Not repeated:** the faults of 16 November (`docs/reviews/contracts-faults-2026-11-16.md`, rows 1 to 13: the "not stated" filter, capitals, the limits box's count, the dates after today, the tolling counts, the notes' patterns, "Place by contracts", "MW filed" without a ceiling, agreements against contracts, fourteen authorities, grey notes, the license, the cross-check) and the reader's read (`docs/reviews/contracts-read-2026-11-16.md`, rows 1 to 22: among them the zero in the headline (11, 19), the price period not served (12), three capacity units (18), the end date 2099 (20), the market operator as buyer (21)).
- Each finding's test is on its own branch, `wip/audit-contracts-<n>`. Branches that change only words are for landing (the rows at the foot); a choice that would move a figure is a ruling line, with its measured effect, and is not made.

## In short

- **The arithmetic is right.** An independent restatement, written from `docs/methods/contracts.md` and the page's words with the standard library on the raw table (not from `site/lib/contracts.ts` or `load.py`), gives every figure the default view prints (2026 Q2 signed; energy, capacity and tolling; every balancing authority) to the digit, against the page drawn by its own code: 40 of 40 figures, 8 of 8 words (dates, quarters, authorities), 1,135 of 1,135 cells of the 227 rows drawn (date, "as filed", years, days, "no unit filed"), for the load of 5 October 2026 and for a load on 26 November 2026 alike.
- **The quarters listed are survivors, not signings (finding 1, High).** Every quarter is read from the newest quarter's file (2026 Q2), which holds only the contracts in effect in 2026 Q2. Of the energy, capacity and tolling rows that 2025 Q3's own file holds as signed in 2025 Q3 (2,129), the page lists 273 (12.8 percent), and 36 of the 1,946 terms under a year. Quarter beside quarter reads as a trend and as comparable prices; it is neither. And the newest quarter lacks late filers: 28.6 percent more of 2026 Q1's contracts were first filed a quarter late. Words fixed; reading each quarter from its own file is Samuel's ruling.
- **A number filed beside words that qualify it is drawn alone (finding 2, Medium).** The price cell shows `x_rate` and its unit and never the description when a number is filed: 178 of the 1,317 numbers of energy, capacity and tolling in the window (156 of them not 0) stand beside words naming an index, LMP, an adder, a formula, an escalation or a percent. A trader reads "5 $/MWH" as the price. Words fixed; drawing the words beside it is Samuel's ruling.
- **Nothing on the page says how old its file is (finding 3, Low).** The newest file is 2026 Q2's, retrieved 4 October 2026; the connector is on no schedule, and FERC's filings for 2026 Q3 are not on this machine. Words fixed in the note; a data request.
- **"One row per product of an agreement" is not so (finding 4, Low).** 47 of the default's 227 rows sit in 18 agreement and product pairs with 2 to 4 rows each (a row for each price period), as the page's own fold says. Words fixed.
- **About half the numbers filed are 0 (finding 5, Low).** The limits box tells of words and numbers; of the window's 8,033 numbers, 4,119 are 0, so 3,914 of 18,989 rows (20.6 percent) file a number other than 0. Words fixed.
- **Smaller, words:** 11 rows whose execution date reads (2526, 2706, 2915) are left out by the connector, where the fold says only a date that "cannot be read" is (finding 6).
- **Six words branches, no figure moved; two ruling lines (findings 1 and 2).** Checked and right: the ERCOT line (241 of 244 rows are transmission service, 93.9 percent one filer), the decisions' numbers, the 5,000-row limit, the held table reaching no public file.

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/contracts/page.tsx` | The page: four views (by quarter signed, the default; the largest buyers and sellers; ranked by megawatts stated; what the filings state), the limits box, the panel, the sentence, three headline cells, the list of at most 400 rows, two folds, the source line |
| `site/app/contracts/read.ts` | The page's two reads, `internal_eqr_summary` and `internal_eqr_contracts` (at most 5,000 rows of a quarter), with the internal token held on the server; nothing without it |
| `site/app/contracts/Decisions.tsx` | The nineteen decisions, each with its default and source on hover; the same list as `docs/methods/contracts.md` section 9 |
| `site/lib/contracts.ts` | The page's arithmetic: quarters from the summary's months, the quarter filed for, the quarters listed and the later rows, the product groups, `baOf`, `filter`, `counts` (rows, agreements, sellers, buyers, priced, affiliate), `zeroPriced`, `byBa`, `termYears`, `termDays`, `rateText`, `heldFrom` |
| `warehouse/connectors/ferc_eqr_contracts.py` | The pull: one quarter's file of all filings, the newest filing of each company, one row per contract row, `event_date` the execution date; rows with no readable date or a date outside 1677 to 2262 left out and counted; `--history` writes the earlier quarters |
| `warehouse/supabase/live_set.yaml`, `warehouse/supabase/load.py` (`eqr_summary`) | The live set's rows (`event_days: 1000`, counted back from the day of each load) and the stored summary the page reads: rows, priced (`x_rate` not empty), first and last day, quarters filed for, rows by month, product and authority |
| `warehouse/supabase/migrations/020_eqr_contracts.sql`, `021_eqr_summary.sql` | The two database functions: a quarter's rows ordered by execution date, seller and row identifier, at most 5,000; the stored summary |
| `warehouse/derived/eqr_buyers.py`, `warehouse/derived/eqr_terms.py` | The other three views' tables (names by rule, megawatts, prices from words, tags, changes by quarter); not the default view |
| `docs/methods/contracts.md` (the page, view by view), `ferc_eqr_contracts.md`, `eqr_buyers.md`, `eqr_terms.md` | The four notes the source line links |
| `replication/contracts/` (`copy_rows.py`, `replicate.py`) | What the page is served, made from the tables on a machine; the replication of 16 November |
| `warehouse/output/ferc_eqr_contracts.csv`, `ferc_eqr_contracts_history.csv` (main checkout, read only) | 2026 Q2's file (186,873 rows, retrieved 4 October 2026); 2025 Q3, 2025 Q4 and 2026 Q1's (571,115 rows) |

## How every number here was computed

- **What the page is served:** `served.py` runs the replication's own `copy_rows.py` (the loader's `eqr_summary` on the live set's rows; the database function's order and limit) for a load on 5 October 2026 (the last the notes record: 18,989 rows from 9 January 2024) and on 26 November 2026 (17,968 rows from 1 March 2024: the live set moves with each load).
- **The page:** `draw_contracts.mjs` draws `app/contracts/page.tsx`, the default export, with the site's own code (`node --import ./scripts/tsx-register.mjs`, no build), the two reads answered from those files by a stand-in for fetch.
- **The independent restatement:** `restate_contracts.py`, standard library, from the raw table and the note: the window, the quarters, the later rows, the default quarter, product group and authorities, the sentence, the headline cells, ERCOT's count, and each drawn row's date, years and days (a day past its month's end run into the next month, as the page's engine reads it). Printouts `restate_1005.out`, `restate_1126.out`.
- **One rule at a time and the claims:** `measures_contracts.py` (both tables, every quarter's own file against the newest, late filers, the window, zeros, rows per agreement and product, units, ERCOT) and `measures2_contracts.py` (a number beside words; ERCOT's product types). Printouts `measures.out`, `measures2.out`.
- **The drawings of the words branches:** `draw_contracts.mjs` on each branch, then `read_words.py` (the visible text around each new line, and the page's em dashes).
- Counts only: no party's name, no party's figure and no row is in any printout or in this file. Copies of every script and printout: `docs/reviews/contracts-model-audit-2026-11-26/` (written to run from `runs/c10226/` of a worktree).

## The arithmetic re-done

| Figures | Compared | Same | Gaps |
|---|---|---|---|
| The limits box: rows held, rows that file no number; the hover's first day | 3 | 3 (18,989; 10,956; 2024-01-09 for 5 October. 17,968; 10,385; 2024-03-01 for 26 November) | |
| The panel: quarters listed and the rows beside each (10), the later rows (54) and the newest of them (2223 Q1), the oldest quarter's "held from", the note's "Filed for" and first and last day ("as filed" after 2223-01-01) | 16 | 16 | |
| The panel: the 13 balancing authorities of the default, their order (4 ties) and rows | 14 | 14 | |
| The sentence: rows 227, agreements 174, sellers 78, buyers 95, priced 112 | 5 | 5 | |
| The headline cells: rows, priced, "the other 115", 17 of them 0, affiliates 7; no "more than 5,000" | 5 | 5 | |
| "What this cannot see": ERCOT's rows held (14) | 1 | 1 | |
| The list: 227 rows drawn, each date, "as filed", years, days, "no unit filed" | 1,135 cells | 1,135 | |

- The same 40 figures, 8 words and 1,135 cells agree for both load days. The default view's sentence and list do not move between the two (2026 Q2 is held whole by both); the limits box, the oldest quarter (1,404 rows from 9 January against 383 from 1 March) and the hover's first day do.
- **Not restated:** the order of rows within one day in the live database, which follows the database's collation of the seller's name; `copy_rows.py` and this restatement sort by code point. The set of rows drawn is not touched (227, under 400).

## One rule changed at a time

Each line changes one choice and keeps every other. The window of the load of 5 October 2026 unless a line says otherwise.

| Choice the page makes | The other choice | Worth | Said on the page? |
|---|---|---|---|
| Every quarter of execution read from the newest quarter's file (2026 Q2) | each quarter from the file filed for it (2025 Q3, 2025 Q4 and 2026 Q1 are held) | energy, capacity and tolling rows: 2025 Q3 273 to 2,129; 2025 Q4 311 to 2,209; 2026 Q1 396 to 701. Every product (the counts beside the quarters): 1,393 to 2,976; 1,817 to 3,290; 1,912 to 1,954. The default (2026 Q2) does not move | no (finding 1) |
| The newest quarter as first filed | with the contracts its filers report a quarter late | contracts signed in a quarter and first filed for the next: 2025 Q3 +3.2 percent, 2025 Q4 +5.9 percent, 2026 Q1 +28.6 percent (159 on 556); 2026 Q2's own share is not known until 2026 Q3's file is read | no (finding 1) |
| A rate filed as a number is drawn alone | the number with the filer's words beside it | 178 of 1,317 numbers of energy, capacity and tolling (156 not 0) beside words of an index, LMP, adder, formula, escalation or percent; in the default view 1 of 112 (106 of the 112 file words as well) | no (finding 2) |
| A price as a number: `x_rate` not empty | not empty and not 0 | the window: 8,033 to 3,914 rows; the default view: 112 to 95 | the headline cell says how many are 0 (session 7510); the limits box does not (finding 5) |
| Rows | agreement and product pairs | the default: 227 rows, 198 pairs; 18 pairs hold 47 rows | the fold yes, the headline note says the other (finding 4) |
| The window: 1,000 days before the load | the whole file | 2024 Q1: 1,404 (5 October) or 383 (26 November) against 1,546; rows held 18,989 or 17,968 against 186,873 | yes, on hover (session 7501) |
| Agreements: seller's name and agreement identifier | filer's company identifier and contract identifier | the default: 174 against 175 | yes (decision "agreement-and-contract"; fault 9) |
| Buyers: names as filed | names trimmed and in capitals | the default: 95 against 93 | fault 9, cited |
| Energy, capacity and tolling | every product | the default: 227 against 1,391 rows | yes (decision "product-default": 35.7 percent of the file's rows; 16.3 percent of those signed in 2026 Q2) |

## Each claim against the code

| Claim, or question | Where | What the code does | Verdict |
|---|---|---|---|
| "This lists the contracts by the quarter they were signed" | the lead; the panel "Quarter signed" | lists the rows of 2026 Q2's file by the quarter of their execution date; a contract signed earlier and ended before 2026 Q2 is not in that file | **Finding 1** |
| "A contract here is new because its execution date is recent, not because it appears in this filing" | the limits box | right, and the other half is unsaid: an older contract here is one still in effect in the newest quarter | **Finding 1** |
| Settlement against last trade; contract months and rolls; a forward curve's dates; positions' report date | the brief | the page holds none of these: a filed bilateral contract, its execution date, its term's two dates | **Not applicable** |
| Units: USD per MWh against per kW-month, MW against MWh, MW-month | the fold "Quantity", "Price, as filed" | every unit as filed, none converted, said; the default's numbers come in $/MWH (50), $/MW-MO (38), $/MW-DAY (15), $/KW-MO (2), $/KWH (1), "$/MW" with no period (1), and none (5) | **Right as stated**; three capacity units are the read's row 18 |
| "Price, as filed: the rate and its units when the filer gave a number" | the fold; the price cell | the number and unit only; the description filed beside it is not drawn | **Right as worded; finding 2** on what it hides |
| Capacity prices by delivery year | the list | by execution quarter, with the term's two dates; no delivery year is claimed | **Right**; an expert's own number (below) |
| An implied spread from two contracts of different dates | the list | the page computes no spread and no average: it counts and lists | **Right** |
| Term: years, and days under a year, "a strip of one month is 0.1 years and 30 days" | the fold "Term" | (end less start) over 365.25 to one decimal; days both counted. The default's 27 strips of a calendar month all end on the month's last day: 30 or 31 days by the month | **Right**; 1,135 of 1,135 cells |
| "Contract rows signed that quarter ... one row per product of an agreement" | the headline note | one row per product, and per price period where the filer files one | **Finding 4** |
| "About half the rows give their price as words, not a number" | the limits box | 10,907 of 18,989 give words (57 percent); of the 8,033 numbers, 4,119 are 0 | **Right; finding 5** on the zeros |
| "A row whose execution date cannot be read is left out, not guessed" | the fold "Signed" | also left out: 11 rows whose date reads but lies after 2262 (2526, 2706, 2915); counted in the table's header | **Finding 6** |
| ERCOT: "almost all one utility's transmission agreements" | "What this cannot see" | of the file's 244 ERCO rows, 241 are of product type T (transmission: OTHER 197, interconnection 32, point-to-point 12), the other 3 tolling energy; one filer files 229 (93.9 percent) | **Right** |
| Staleness and the as-of date | nowhere on the page | the panel says "Filed for 2026 Q2"; no retrieval date; the connector is on no schedule | **Finding 3** |
| Held or licensed data reaching a public figure | the source line; decision "internal" | the table is internal, `/contracts` is `review` (`site/lib/release.ts`); no EQR figure is in `site/public` or `site/data` (grep: two mentions in `site/data/codebook_methods.json` and `data_faults.json`, words only) | **Right** |
| "No quarter held passes 5,000 rows" | decision "shown" | the largest quarter in the window: 2,486 rows | **Right** |
| "4,077 filings of 4,010 companies, 67 earlier filings left out"; "178,842 rows in force, 8,031 terminated"; "35 percent of the rows of 2026 Q2" | decisions | the table's header and rows: the same; 35.7 percent | **Right** |

## What a trader's own number would hold that this does not

| Item | Why | Size, where measurable |
|---|---|---|
| Each quarter's signings as first filed, and the late filers of the next | the page reads one file | finding 1: 2025 Q3 273 of 2,129 power rows; +28.6 percent late for 2026 Q1 |
| The price a contract settles at: index plus adder, or a formula | the filer's words are not parsed when a number is filed, nor read when no number is | finding 2: up to 178 numbers; 104,929 rows of words unread (eqr_terms) |
| Prices by delivery period, in one unit per product (USD/MWh for energy, USD per kW-month for capacity) | units as filed, period not served (the read's rows 12 and 18) | the default: 56 capacity numbers in four units and one with none |
| Volume: MWh delivered and the price paid | the transactions of the reports are not parsed (decision "contracts-only") | not sized: about 115 million rows a quarter |
| Hub forwards, futures settlements, capacity auction clearing prices to set the filed price against | none held; exchange data are licensed (CME Group, ICE) | not sized |
| Texas | outside FERC's jurisdiction | said |

## Findings, largest effect first

| # | Severity | Finding | Effect | Fix | Branch |
|---|---|---|---|---|---|
| 1 | High | The quarters listed are read from the newest quarter's file: an earlier quarter holds only the contracts still in effect in 2026 Q2, and the newest lacks its late filers; unsaid | 2025 Q3's power rows 273 of 2,129 (12.8 percent); 36 of 1,946 short terms; 2026 Q1's contracts +28.6 percent filed late | words; each quarter from its own file: ruling | `wip/audit-contracts-1` |
| 2 | Medium | A rate filed as a number is drawn alone; the filer's words beside it can make it an adder or a formula's term | up to 178 of 1,317 power numbers in the window (156 not 0); 1 in the default view | words; drawing the words: ruling | `wip/audit-contracts-2` |
| 3 | Low | No as-of date: the newest file is 2026 Q2's, retrieved 4 October 2026, pulled by hand | the page's newest quarter ended five months ago; 2026 Q3's file not held here | words (the note); a data request | `wip/audit-contracts-3` |
| 4 | Low | "One row per product of an agreement" | 47 of 227 default rows in 18 pairs with more than one row | words | `wip/audit-contracts-4` |
| 5 | Low | The limits box is silent on zeros | 4,119 of 8,033 numbers are 0; 3,914 of 18,989 rows file a number other than 0 | words | `wip/audit-contracts-5` |
| 6 | Low | The fold names one reason a row is left out; the connector has two | 11 rows of 2026 Q2's file | words | `wip/audit-contracts-6` |

- Ranked by severity, then by size. One High, one Medium, four Low.
- Each branch alone ran its own test with every test file that reads the page or the note (`tests/test_session83.py`, `test_session7501_contracts.py`, `test_session241a.py`, `test_session304.py`, `test_session333.py`, `test_session90.py`): 79 to 80 passed, 4 skipped (tables this machine does not hold), on each. `site/scripts/test-contracts-read.mjs` (46 of 46) and `test-contracts-render.mjs` (40 of 40) ran on branches 2, 4 (read) and 5 (render) and on the six merged. The six merged onto origin/main: 90 passed, 4 skipped; both node tests pass; drawn, the page carries every new line and no em dash (`draw_trial.txt`), and the restatement still agrees in 40 of 40 figures and 1,135 of 1,135 cells (`restate_trial.out`): no figure moved.
- Each words branch was drawn with the page's own code and its new words read once more: pass on all five branches that change the page (`draw_b1.txt`, `draw_b2.txt`, `draw_b4.txt`, `draw_b5.txt`, `draw_b6.txt`); branch 3 changes only the note.

## 1. The quarters listed are survivors, not signings (High; words, and a ruling)

- **Where.** `warehouse/supabase/live_set.yaml` (`ferc_eqr_contracts: {event_days: 1000}`) on a table that holds one quarter's file (`ferc_eqr_contracts`, filed for 2026 Q2); `site/lib/contracts.ts`, `quarters` and `listed`; the lead ("This lists the contracts by the quarter they were signed"), the panel "Quarter signed", the limits box's third limit.
- **Why it is wrong.** EQR files each quarter the contracts in effect in it; a contract that ended is filed in the quarter it ends and not after. So the page's 2025 Q3 is "signed in 2025 Q3 and still in effect in 2026 Q2". In 2025 Q3's own file, 2,052 contracts of energy, capacity and tolling are signed in 2025 Q3; 46 of them are in 2026 Q2's file, and 122 more first filed later. Of the 2,006 gone, 1,921 file a termination date before 1 April 2026 and 1,955 an actual termination date. Most power contracts are strips: 1,946 of 2,129 rows have a term under a year, and 36 of them survive to the page. So the panel's quarters read as a falling trend (power: 2,129, 2,209, 701 as first filed; 273, 311, 396 on the page) and their prices as comparable, where an older quarter holds the long contracts only. The other way: 2026 Q1's own file holds 556 contracts signed in it and 2026 Q2's file 159 more (+28.6 percent), so the newest quarter, the default view, will gain contracts when 2026 Q3's file is read, and lose its strips.
- **How much.** The table above. The default view (2026 Q2) does not move; the counts beside 2025 Q3, 2025 Q4 and 2026 Q1, and every page of those quarters, would.
- **The test.** `tests/test_audit_contracts_1.py` on `wip/audit-contracts-1`: from the two tables (skipped where they are not on the machine), 2025 Q3's own file against 2026 Q2's, and the late filers of 2026 Q1 (passes on main); the page's and the note's words (fails on main).
- **The fix on the branch, words only.** The limits box's third limit: "So an earlier quarter lists only the contracts still in effect in the newest quarter filed for: a contract signed then that has since ended, as most short strips have, is not here, and the newest quarter lacks the contracts its filers report a quarter late. The counts beside the quarters are not a series of signings." The note's section 3 says the same with the counts. No figure moves.
- **For Samuel's ruling.** Default "left as it is". The other choice: each quarter of execution read from the file filed for it, the history table holding 2025 Q3 to 2026 Q1 (power rows 273 to 2,129 for 2025 Q3; every product 1,393 to 2,976), the quarters before 2025 Q3 needing files not held.

## 2. A number filed beside words that qualify it is drawn alone (Medium; words, and a ruling)

- **Where.** `site/lib/contracts.ts`, `rateText`: a rate that is not empty returns the number and its unit; `x_rate_description` is drawn only when no number is filed. The fold: "Price, as filed: the rate and its units when the filer gave a number; otherwise the filer's own description".
- **Why it matters.** A filer can file a number and words that say what it is: an adder to an index or LMP, a term of a formula, an escalation, a percent. A trader reads the number in the cell as the price. Of the 1,317 numbers of energy, capacity and tolling signed in the window, 1,110 stand beside words, and 178 of those words name an index, LMP, an adder, plus, a formula, an escalation, a heat rate or a percent (156 of the 178 numbers are not 0). The pattern is broad (a "plus" can be benign), so 178 is an upper bound of the numbers that are not the price. In the default view: 106 of the 112 numbers stand beside words, 1 beside such words.
- **The test.** `tests/test_audit_contracts_2.py` on `wip/audit-contracts-2`: `rateText` drops the words when a number is filed, and the count from the table (skipped without it) (passes on main); the fold's words (fails on main).
- **The fix on the branch, words only.** The fold's line adds: "When a number is filed, the filer's description is not drawn beside it, and it can say that the number is an adder to an index or one term of a formula: the number is what was filed in the rate column, not always the price paid." No figure moves.
- **For Samuel's ruling.** Default "left as it is". The other choice: the description drawn in grey after a number (no figure moves; up to 178 cells in the window carry words that change how the number reads).

## 3. Nothing on the page says how old its file is (Low; words in the note, and a data request)

- **Where.** The panel note ("Filed for 2026 Q2"), the source line (no date); `ferc_eqr_contracts.csv`'s header (retrieved 20261004T035009Z, FERC's file Last-Modified 3 October 2026); `warehouse/run_daily.sh` and `.github/workflows/` name no EQR pull.
- **Why it matters.** The title says contracts "are being struck"; its newest quarter ended on 30 June. FERC's filings for 2026 Q3 fall due a month after the quarter (this auditor's reading of the reporting calendar, not checked against a file here); whether the data machine has pulled them is not known on this machine. The live set's window moves with each load, so the oldest quarter shrinks by itself, while the newest stays until a person runs the connector.
- **The test.** `tests/test_audit_contracts_3.py` on `wip/audit-contracts-3`: no schedule names the connector, the page draws no retrieval date (passes on main); the note's words (fails on main).
- **The fix on the branch, words only.** The note's section 10 says the table is pulled by hand, one quarter at a time, and the page gives the quarter filed for and no retrieval date. A date on the page needs the stored summary to carry the file's retrieval time (the data machine): a data request, not a figure.

## 4. "One row per product of an agreement" (Low; words)

- **Where.** `page.tsx`, the headline note under "Contract rows signed that quarter".
- **Why it is wrong.** The page's own fold says one agreement can file a row for each year, month or peak period of its price. In the default view 18 of the 198 agreement and product pairs hold 2 to 4 rows each, 47 of the 227 rows.
- **The test.** `tests/test_audit_contracts_4.py` on `wip/audit-contracts-4`: the count from the table (skipped without it) (passes on main); the note's words (fails on main).
- **The fix on the branch, words only.** "one row per product of an agreement, and per price period where the filer files one."

## 5. About half the numbers filed are 0 (Low; words)

- **Where.** The limits box's second limit (on every view).
- **Why it matters.** It tells a reader that about half the rows give words and so, by implication, about half give a price as a number. Of the window's 8,033 numbers, 4,119 are 0 (51.3 percent; 3,817 of them outside energy, capacity and tolling), so 20.6 percent of the rows file a number other than 0. The headline cell of a quarter says how many of its numbers are 0 (session 7510); the box did not.
- **The test.** `tests/test_audit_contracts_5.py` on `wip/audit-contracts-5`: the count from the table (skipped without it) (passes on main); the box's words (fails on main).
- **The fix on the branch, words only.** "Of the numbers filed, about half are 0, most outside energy, capacity and tolling." The share is words, not a figure drawn from the summary; a count would need the summary to hold it (not asked: the read's row 19 is the ruling on whether a 0 counts).

## 6. The fold names one reason a row is left out (Low; words)

- **Where.** The fold "What a row is", "Signed": "A row whose execution date cannot be read is left out, not guessed." `ferc_eqr_contracts.py` also leaves out a row whose date reads and lies outside 1677-09-22 to 2262-04-11: 11 rows of 2026 Q2's file (2526-01-01, 2706-01-01, 2915-01-01), 0 for a date that cannot be read (the table's header).
- **The test.** `tests/test_audit_contracts_6.py` on `wip/audit-contracts-6`: the connector's two rules (passes on main); the fold's words (fails on main).
- **The fix on the branch, words only.** "A row whose execution date cannot be read, or reads as a year after 2262 (a typing error no table can hold as a date), is left out and counted, not guessed."

## What was checked and found right

- **Every figure of the default view**, for two load days: 40 figures, 8 words, 1,135 cells.
- **The calendar of a term**: years over 365.25, days both counted, a day past its month's end run into the next month.
- **The ERCOT line, the decisions' counts, the 5,000-row limit, the product groups compared in capitals, the authority by `baOf`**.
- **No held figure in a public file**: the page is `review`, the table internal, the token never sent to a browser (`read.ts`), no EQR figure in `site/public` or `site/data`.

## Not covered, or left open

- **Which load the live database holds today**, and whether 2026 Q3's file is pulled: not read from this machine (a data request).
- **Quarters before 2025 Q3 as first filed**: their files are not held; not sized.
- **The other three views** (largest, megawatts, what the filings state): their figures were replicated on 16 November and are not the default view; finding 1's survivorship also touches "Contracts new and gone" (a renumbered contract and an ended one both count as gone), already said there as ceilings.
- **The order of rows within a day** in the live database (its collation), not restated.

## Landing, rulings and data (returned to the chain's main session)

- **For landing (words only):** `wip/audit-contracts-1` (`d95b16176`), `wip/audit-contracts-2` (`4a5e262b1`), `wip/audit-contracts-3` (`e92b4e8ba`), `wip/audit-contracts-4` (`4328d943f`), `wip/audit-contracts-5` (`d587ca08c`), `wip/audit-contracts-6` (`862168ba2`). They merge together onto origin/main of 26 November with no conflict (no merged words branch was needed). Branches 1, 2, 4, 5 and 6 touch `site/app/contracts/page.tsx`; 4 also `site/scripts/test-contracts-read.mjs` (its check of the headline note's words); 3 only the note.
- **For Samuel's ruling, default "left as it is":** finding 1, read each quarter of execution from the file filed for it (2025 Q3's power rows 273 to 2,129; every product 1,393 to 2,976; the default view unchanged); finding 2, draw the filer's description beside a number (up to 178 numbers in the window; no figure moves).
- **Data requests:** (a) the data machine reads, counts only, the load day and first execution date of the live set's `ferc_eqr_contracts` and whether FERC's 2026 Q3 file has been pulled; (b) the stored summary to carry the file's retrieval time, so the page can give its as-of date (finding 3).
