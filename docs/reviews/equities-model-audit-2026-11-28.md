# Energy equities: `/equities` and the price board's equities group, audited as a hostile equity analyst would

Session 11403, 28 November 2026, chain 770 (part B, item 2), the old laptop. Read as an equity analyst who covers energy and utilities, sets two companies side by side with this page, and wants to find it wrong. In the form of `docs/reviews/battery-model-audit-2026-11-20.md` and of chain 710's audits (`docs/reviews/datacenter-model-audit-2026-11-26.md`, `docs/reviews/board-model-audit-2026-11-26.md`).

- Pages: `https://erw-flame.vercel.app/equities` and the group "Energy equities" at `https://erw-flame.vercel.app/board#equities` (both in review: a visitor sees the in-review page).
- Nothing changed on main but this file and its folder of evidence (`docs/reviews/equities-model-audit-2026-11-28/`). No table written, no lock taken, no default moved, no model called, no request to any service (EDGAR included: this machine may not ask it).
- The files read: `site/data/equities/` as origin/main holds it (`index.json` built `2026-11-28T03:47:24Z`: 307 companies, 243 with filed statements; 309 series files; `board.json`, 30 rows; `energy_prices.json`, 12 series). No equities file changed on main between `f35d8245b` and `839f9845f`.
- Each finding's test is on its own branch, `wip/audit-equities-<n>`, cut from origin/main. Branches that change only words are for landing (the rows at the foot); a branch whose fix would move a figure carries the test only and waits for Samuel's ruling.

## In short

- **The arithmetic is right.** Every figure the page prints as it opens, and every company's newest filed period in the table of every company (307 of 307: period, form, day, address, three sums with their months, debt, shares), comes out to the digit from the page's own files by an independent restatement; so do the eight energy prices' latest values and their 40 moves. The page drawn by its own code prints the same 14 marked numbers.
- **Three utilities print their parent's figures as their own (finding 1, High).** Consumers Energy, Southern California Edison and Pacific Gas and Electric carry, for 30 September 2026, CMS Energy's, Edison International's and PG&E Corp's revenue, net income, capital spending, long-term debt and share count, to the dollar and the share, from the parent's joint 10-Q. The table of every company says Consumers' quarter's revenue was USD 2,183 million: CMS Energy's.
- **Capital spending is sometimes not the filing's capital spending (finding 4, Medium).** Six companies' newest figure is 0 (VAALCO: 102,996,000 for 2024 under the same concept, 0 in every 2026 period); 52 companies have a year to date that falls within a year at least once; debt mixes three definitions and net income two across companies.
- **The segments follow their SIC rule exactly, and no company is placed by judgment (307 of 307).** But the rule gives eight lists for nine names: Integrated oil and gas and Refining are the same 18 companies, and 63 of Independent power's 64 are the electric utilities (AES alone by its own code) (finding 3). Two businesses are listed twice in one segment, a holding company and the partnership it consolidates (finding 2: 4.4 to 10.4 percent of a segment's quarterly revenue is a second count).
- **The two weightings are named and not computed (finding 6).** The board's thirty rows and the page's two lines ("every company counts the same", "larger companies count more") have no value: no share price may be kept. The page said their rule was in the method note; it was only in the contract. Their rule leaves open price or total return, which share count, and preferred-only listings: the market-value line would hold 136 of 307 companies (finding 7). Nothing could be re-done to the digit, because nothing is computed.
- **No held price leaks.** No share price, index level, market value or held grid's price is in any equities file, in any version of the list, board or price file in the repository's history, or in a download.
- **The sample matches where a filing is held.** Seed 11403 drew 12 of the 243 companies; every year to date less the one before equals the quarter filed (24 of 24); SLB, the one the earlier read of the filings covers, matches its filing's revenue and share count. The other filings are not on this machine: a data request lists each figure to find.
- **Four branches fix words and move no figure (5, 6, 8, 9); five carry a test for Samuel's ruling (1, 2, 3, 4, 7); one is a data request (10).**

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/equities/page.tsx` | The page's frame: the brand, `EquitiesView`, the table downloads of `tablesOf()`; robots noindex; in review |
| `site/app/equities/view.tsx` | Everything the page draws: the choices (A, B, the energy price, the window, the filed figure and its periods), the line of a company, index or segment (a blank while its price is held), the filed figures (a line over the periods filed, the newest period's columns, every period behind a fold), the energy prices' table, the table of every company (newest period filed and its revenue), the segments and indices, the downloads |
| `site/app/equities/reader.ts`, `rows/`, `filed/`, `list/` routes | The downloads: a series' days, a company's filed periods, the list of every company, each as CSV, Python and Stata |
| `site/lib/equities.ts` | The pure rules the page, the board and the routes share: `boardRow` and `withEquities` (the board's group), `picksOf`, `linesOf` (the two weightings' names and words), `filingsOf`, `figureLine`, `newestOf`, `companiesOf` (filter and sort), `queryOf`, `seriesCsv`, `filedCsv`, `listCsv` |
| `site/lib/equitiesfiles.ts` | Reads the page files (or a test's folder) |
| `site/app/board/page.tsx`, `rows/route.ts`; `site/components/board/BoardView.tsx`; `site/lib/board.ts` | The price board, with the equities group appended by `withEquities` (a lean group: latest, moves, trend; a row with a file opens `/equities`) |
| `site/data/equities/index.json` | The list: 15 segments (rule, reason, count), 307 companies (SEC number, ticker, exchange, SIC and its label, segments, statuses, newest filed period), no index, no segment line |
| `site/data/equities/series/<ticker>.json` | One a company: prices null with the license reason, the filed periods (`quarterly`, each filing's own period, newest first), the concept of each line |
| `site/data/equities/board.json` | The board's group: two rows a segment (equal weight, weighted by market value), all held |
| `site/data/equities/energy_prices.json` | WTI, Brent, Henry Hub, ERCOT and CAISO day-ahead daily means, uranium, California carbon: their days and moves; PJM, NYISO, ISO-NE held and MISO paused, no rows |
| `warehouse/derived/equity_page_files.py` | The builder of the four files from `equity_universe` and `equity_fundamentals_quarterly` (the data machine's daily step) |
| `warehouse/connectors/sec_edgar.py` | The universe (exchange-listed companies whose SIC is in `SIC_SEGMENTS`) and the statements (the first concept of each line's list a filing holds; joint filings from a co-registrant's file) |
| `docs/methods/equities.md` | The method note: the universe's written rule, the statements, joint filings, the notes, the newest period, the cover's share count |
| `docs/state/page_files_equities.md` | The contract: every file's fields, and the two weightings' rule |
| `docs/reviews/equities-sources-2026-11-26.md` | The sources' robots files and terms: no source of share prices or index levels may be kept |
| `docs/reviews/answers-c701-2026-11-26/equities_crosscheck.txt` | Chain 701's read of five companies' filings: ten figures found in the filings' own text |
| `replication/equities/replicate.py` | Chain 701's replication of the tables (needs the warehouse tables; not run here) |
| `docs/state/note_2026-11-26_data_c701.md`, `note_2026-11-26_portable_c720.md`, `progress_c701.md`, `progress_c720.md` | How the tables (chain 701) and the pages (chain 720) were built and read |
| `warehouse/metadata/paused_sources.csv`, `site/lib/license.ts` | The held and paused publishers |

## How every number here was computed

- **The independent restatement** (`restate.py`): written from the method note's words ("each statement line's figure for the shortest period to that end ... debt and shares outstanding at that end, the later filing's figure where a period was filed twice") and the page's stated rules, not from the builder or `site/lib/equities.ts`. Every company's newest period; the page's default company (ACDC, the list's first) over 3-month periods and its newest columns; the energy prices' moves from their days (`d` the day before held, `w` on or before 7 days back, `m` a calendar month back, `ytd` the last day of the year before, `y` a year back).
- **The page as it opens, drawn by its own code** (`draw_default.mjs`, the site's own loader, no build): every marked number and the prices' table.
- **The segment rule** (`seg_check.py`, `list_codes.py`): every company's SIC against `SIC_SEGMENTS` and `TWO_NOTE`, its exchange against the listed set, the counts.
- **The sample** (`sample.py`): `random.Random(11403).sample` of the 243 tickers with filed figures, sorted; 12 drawn.
- **The held prices** (`held_scan.py`, `held_history.py`): every equities file now, and every version of the list, board and price files in the history.
- **The lines across companies** (`concepts.py`, `pairs.py`, `shared.py`, `jumps.py`, `ties.py`, `zero_capex.py`, `choices.py`).
- Copies of every script and its printout: `docs/reviews/equities-model-audit-2026-11-28/` (written to run from `runs/c770/s11403/` of a worktree).

## The arithmetic re-done

| Figures | Compared | Agree | The gaps |
|---|---|---|---|
| Every company's newest filed period (`newest_filed`): period end, form, day, address; revenue, net income, capital spending with their months; debt and shares | 307 companies (243 with a period), 10 fields each | all | none |
| A company's file against the list: one file each, statuses | 307 | all | two old example files of the contract also sit in `series/` (`index-example.json`, `segment-integrated_oil_gas.json`), every value null; the list names neither, so the page never reads them |
| The default page: ACDC's revenue over 3-month periods (16 points, 2022-03-31 to 2026-09-30, last 511 million), its newest columns (3 and 9 months to 30 September: revenue 511 and 1,459; net income -81 and -244; capital spending not filed and 112; debt 905; shares not filed) | 14 marked numbers, as the page's code draws them | all | none |
| The energy prices: latest value and its date, five moves (base date, base value, change, percent) | 8 series, 40 moves | all | none; the four held series carry no value |
| The table of every company: count and order | 307 of 307 | all | |
| One period filed twice on one day under two accessions (where the list's builder and the page could break the tie differently) | every period of 243 companies | none occur | |

## The sample (seed 11403)

- Drawn: AVA, DEC, DINO, DK, EE, PR, PROP, PSX, RRC, SLB, WMB, XEL (12 of 243). For each, the newest period's five figures as the page prints them, their accession and concept (`sample.txt`).
- **The filing's own arithmetic:** the 9 months less the 6 months filed for 30 June equals the 3 months filed, for revenue and net income, in all 12 (24 of 24).
- **Against a filing held on this machine:** SLB's revenue (9,449 million) and share count (1,476 million) are the figures its 10-Q prints (chain 701's read). With the other four companies chain 701 read (CVX, DUK, KMI, NEE), the files still hold all 9 figures found in those filings.
- **Sign and size:** no negative capital spending, debt or share count. PROP's capital spending is 0 (finding 4).
- **Not filed at the newest period:** debt for AVA and PROP; capital spending for EE and PSX; the balance-sheet share count for 7 of 12 (finding 7).
- **Not checked here:** the other 11 companies' figures against their filings, which this machine does not hold and may not fetch: data request 3.

## Held prices

- Every company's and segment's daily rows are empty; no list entry carries a close, a move or a market value; every board row is `not_held` with no value, trend or file; the four held grids in the energy prices carry no row. No equities file under `site/public/`.
- Every version of `index.json`, `board.json` and `energy_prices.json` on main (7 each): no held value (the first is the contract's example, every value null).
- The downloads write a held column empty, with its reason in the header; a series not shown has its header and no row.
- The energy prices shown are EIA's public spot prices (`eia_fuel_spot_prices`, public in `docs/licenses.md`), ERCOT's and CAISO's, the IMF's and CARB's.

## One choice changed at a time

Each line changes one choice and keeps every other, measured on the page's own files.

| Choice | The other choice | Worth | Said on the page? |
|---|---|---|---|
| SIC 4911 in both regulated utilities and independent power | 4911 in regulated utilities only | Independent power 64 companies to 1 (AES) | the rule on hover ("also in regulated utilities"), not the count (finding 3) |
| SIC 2911 in both integrated and refining | one segment for 2911 | two segments of 18 to one | the rule on hover (finding 3) |
| Every listed company of a code | one listing a business | a second count of 10.4 percent of midstream's 3-month revenue to 30 September 2026, 4.4 of integrated and refining's, 8.4 of regulated utilities', 6.3 of independent power's | no (finding 2) |
| A subsidiary of a joint filing gets the facts the SEC keeps for it | a subsidiary's row left blank where the facts are its parent's | three companies' newest period (Consumers Energy 2,183 million of revenue, which is CMS Energy's) | no (finding 1) |
| Capital spending: the first concept of the list a filing holds | the filing's cash flow line | six newest figures of 0; 52 companies with a falling year to date | the concept on hover (finding 4) |
| Market value from the balance-sheet share count | from the cover's count as well | the value line's companies 136 of 307 to most of 243 (the note: 224 of 243 have a count with the cover's) | not on the page; the note says the page leaves the cover's count out (finding 7) |
| Only us-gaap 10-Q and 10-K facts | foreign filers' 20-F and 40-F | 64 of 307 companies with no figures: 22 percent of integrated, 24 percent of regulated, 34 percent of independent power | yes, each company's blank says why |
| Exchange-listed only | over the counter as well | not measured: the SEC's tickers file is not on this machine | yes, the note |

## Each claim against the code

| Claim | Where | What the code does | Verdict |
|---|---|---|---|
| "no company is placed or moved by judgment" | the note, "The universe" | every company's segments are its SIC's in `SIC_SEGMENTS`, its note `TWO_NOTE`'s, its exchange listed | **Right**: 307 of 307 |
| A segment's count | the segments table | the companies whose segments hold it | **Right**: 15 of 15 |
| "a company's figures from its own filings with the SEC" | the hover "What it is", the filed figures | the facts the SEC keeps in a company's file, the first concept of each list | **Right** but for three subsidiaries (finding 1) and capital spending's concept (finding 4) |
| "Two companies' revenues compare only where the months are the same" | the list's revenue hover | the revenue of the shortest period to the newest end, with its months | **Right** |
| "Debt" | the filed figures, the newest table, the figure's choice | long-term debt by one of three concepts | **Finding 5** (fixed in words) |
| "Every company counts the same" and "Larger companies count more"; the board's "(equal weight)" and "(weighted by market value)" | `linesOf`, the board's rows | nothing computes them | **Finding 6** (fixed in words); the rule's gaps, finding 7 |
| "A segment's line is built by the ERW ... by the written rule of the method note" | the hover "What it is" | no line is built; the rule was the contract's | **Finding 6** (fixed in words) |
| "written by warehouse/derived/equity_pages.py" | every download's provenance | the builder is `equity_page_files.py` | **Finding 8** (fixed in words) |
| "What the files hold today": "no company or index" | the method note | 307 companies, 243 with statements | **Finding 9** (fixed in words) |
| Source line: `equity_prices_daily`, `equity_index_daily` | the page's foot | two tables no machine has written | **Finding 9**: a data request (the builder's list) |
| Industry: "Silver Ores" | the table of every company | the SEC submissions' label of SIC 1220 | **Finding 10**: a data request |
| "A parent's file, which holds the parent's consolidated figures, is never read for a subsidiary" | the note, "Joint filings" | three subsidiaries hold their parent's consolidated figures | **Finding 1**: the effect is as if it were |
| A held price is a blank with its reason, everywhere | the page, the board, the downloads | as said | **Right** (above) |
| The board's filter "Segments and indices", "Indices" | the group's filter | no index row exists: "Indices" shows none | right in what it shows; noted, not a finding |

## Findings, largest effect first

| # | Finding | Severity | Effect | Fix | Branch, head |
|---|---|---|---|---|---|
| 1 | Three utilities listed by a preferred share carry their parent's figures | High | the newest period of Consumers Energy, Southern California Edison, Pacific Gas and Electric: all five lines are the parent's | figures: Samuel's ruling; data request 1 | `wip/audit-equities-1`, `c3a497089` |
| 4 | Capital spending read from a concept that is not the filing's capital spending; debt and net income mix definitions | Medium | six newest figures of 0; 52 companies with a falling year to date; debt 130, 67 and 26 companies on three definitions | figures: Samuel's ruling; data request 2 | `wip/audit-equities-4`, `62a5cd092` |
| 2 | One business listed twice in a segment | Medium | 4.4 to 10.4 percent of a segment's quarterly revenue a second count; an equal-weight line would count two companies | a rule: Samuel's ruling | `wip/audit-equities-2`, `bb7b879b1` |
| 3 | The SIC rule gives eight lists for nine names | Medium | Integrated = Refining (18); Independent power = 63 electric utilities and AES | a rule: Samuel's ruling | `wip/audit-equities-3`, `6e9183fcb` |
| 7 | The weightings' rule leaves open price or total return, which share count, preferred listings | Medium | the value line would hold 136 of 307 companies (3 of 18 in integrated) | a rule: Samuel's ruling | `wip/audit-equities-7`, `82c073f49` |
| 6 | The two weightings are named and not built; the page said their rule was in the method note | Medium | words | words, fixed | `wip/audit-equities-6`, `b8310ca60` |
| 5 | "Debt" is long-term debt | Low | words | words, fixed | `wip/audit-equities-5`, `49f546757` |
| 8 | The downloads name a builder that does not exist | Low | words | words, fixed | `wip/audit-equities-8`, `1f226e40d` |
| 9 | The method note's first section says no company is listed; the source line names two tables never written | Low | words | words, fixed (note); data request 4 (tables) | `wip/audit-equities-9`, `45e671ece` |
| 10 | "Silver Ores" for four coal miners | Low | words, in the data machine's file | data request 5 | `wip/audit-equities-10`, `e6b58484f` |

## 1. Three utilities print their parent's figures as their own

- **Where.** `site/data/equities/series/CMS-PB.json`, `SCE-PG.json`, `PCG-PE.json`, their `newest_filed` in `index.json`; the connector's joint filings (`warehouse/connectors/sec_edgar.py` `coregistrants`, `facts_of`) and the note's "Joint filings".
- **What the files hold.** Each subsidiary files one 10-Q with its parent. For the quarter to 30 September 2026, from the parent's accession (`0000811156-26-000032`, `0000827052-26-000073`, `0001004980-26-000055`), each subsidiary's file holds exactly the parent's revenue, net income, capital spending, debt and share count. Consumers Energy: revenue 2,183,000,000, net income 123,000,000, shares 313,600,000, all CMS Energy's; Southern California Edison: 4,886,000,000, 724,000,000, 384,787,221 shares, all Edison International's; Pacific Gas and Electric: 6,188,000,000, 776,000,000, 2,202,416,553 shares, all PG&E Corp's.
- **Why it is wrong.** A subsidiary whose common stock its parent holds cannot have the parent's public share count. Southern California Edison's own filings gave 434,888,104 shares through 2012; its 2026 rows (and June 2014's 325,811,206) are Edison International's. The non-dimensional facts of a joint filing are the parent's consolidated statements; the subsidiary's own statements sit beside them under the legal-entity axis, which the company facts files do not carry.
- **What a reader sees.** The table of every company: "2026-09-30, 10-Q, Revenue 2,183, 3 months" for Consumers Energy; the newest columns and the lines of all three.
- **The test.** `tests/test_audit_equities_1.py`: one filing, the same figures, in both files of each pair; the list prints the parent's revenue and share count for the subsidiary; SCE's own count before. Passes on main.
- **Not fixed.** Leaving these rows out (or reading the subsidiary's own figures) moves figures: Samuel's ruling. Data request 1.

## 2. One business listed twice in a segment

- **Where.** `index.json`: Plains GP Holdings (PAGP) and Plains All American Pipeline (PAA), both midstream; SunocoCorp (SUNC) and Sunoco LP (SUN), both integrated and refining; and finding 1's three subsidiaries beside their parents in regulated utilities (two of them also in independent power).
- **What the files hold.** Each holding company consolidates its partnership: the same revenue in every period both filed (87 of 87; 6 of 6), from two filings, with different net incomes (the holding company's share).
- **How much.** Of the 3-month revenue to 30 September 2026 summed by segment, the second count is 15.2 billion of 146.1 in midstream (10.4 percent), 18.0 of 413.8 in integrated and in refining (4.4), 13.3 of 158.0 in regulated utilities (8.4), 4.9 of 77.9 in independent power (6.3).
- **What a reader sees.** No segment sum and no line today. A reader summing the list's download, or an equal-weight line built by the contract's rule, counts each pair twice.
- **The test.** `tests/test_audit_equities_2.py`. Passes on main. **Not fixed:** which listing to keep is a rule for Samuel.

## 3. The SIC rule gives eight lists for nine names

- **Where.** `SIC_SEGMENTS` (2911 in integrated and refining; 4911 in regulated utilities and independent power), `index.json`'s segments.
- **What it gives.** Integrated oil and gas and Refining are the same 18 companies. Independent power producers are 64: 63 of them also regulated utilities (SIC 4911), and one by its own code, AES (4991): Vistra, NRG, Constellation and Talen are there as 4911, beside Southern Company and NextEra Energy (Duke, 4931, is in regulated utilities only). A company's code is its own filing choice, sometimes old: ConocoPhillips, with no refinery since 2012, is in Refining; HF Sinclair, a refiner, is in Midstream by 4610.
- **Right by the rule.** Every count is the rule's, and the rule says "in both" on the hover. The note leaves a named list to Samuel ("A named list for the six would be judgment").
- **The test.** `tests/test_audit_equities_3.py`. Passes on main. **Not fixed:** a named list, or a split of 2911 and 4911, is judgment: Samuel's ruling.

## 4. Capital spending is sometimes not the filing's capital spending

- **Where.** `warehouse/connectors/sec_edgar.py` `CONCEPTS["capex_usd"]`: the first of PaymentsToAcquirePropertyPlantAndEquipment, PaymentsToAcquireProductiveAssets, PaymentsToAcquireOilAndGasPropertyAndEquipment, PaymentsToAcquireOilAndGasProperty that a filing holds, read filing by filing.
- **What the files hold.** Six companies' newest capital spending is exactly 0: Big Sky Industrial, VAALCO, EON Resources, Prairie Operating, Hadron Energy, Spruce Power. VAALCO's concept, PaymentsToAcquireOilAndGasProperty, gave 102,996,000 for 2024, 58,527,000 for the first 3 months of 2025, then 3,034,000 for 6 and for 9 months of 2025, and 0 in every 2026 period: a concept that changed between filings, or an acquisitions line read as capital spending.
- **A year to date that falls.** Payments add up: a year to date is never less than the one a quarter before with the same start. 52 companies break that by more than 1 percent at least once (VAALCO, Prairie, EQT, Diamondback, Xcel, NRG and others; the list is in the test's printout).
- **Two more lines mix definitions.** Debt: LongTermDebt (with the current portion) for 130 companies, LongTermDebtNoncurrent (without it) for 67, with capital or finance leases for 26. Net income: the parent's share (NetIncomeLoss) for 212, with noncontrolling interests (ProfitLoss) for 27; for a holding company of a partnership the two differ several times over (PAGP 68 million against PAA's 363 million in the quarter to 30 September).
- **The test.** `tests/test_audit_equities_4.py`. Passes on main. **Not fixed:** reading the cash flow statement's capital spending line, or leaving out a 0, moves figures: Samuel's ruling. Data request 2.

## 5. "Debt" is long-term debt (words)

- **Where.** `site/lib/equities.ts` `STATEMENT` (the newest table's row, the figure's choice, its headline and chart), the list download's header.
- **Why.** Every company's concept is a long-term debt concept; short-term borrowings and commercial paper are never read. "Debt" alone, beside a utility, reads as all of it.
- **The fix on the branch.** The line is "Long-term debt"; the list's header says "long-term debt in USD"; `site/scripts/test-equities-filed.mjs` follows (103 checks pass). No figure moves. `tests/test_audit_equities_5.py` fails on main, passes on the branch; the four equities suites and the three equities scripts pass.

## 6. The two weightings are named and not built (words)

- **Where.** `site/lib/equities.ts` `linesOf`, the board's thirty rows (`board.json`), the hover "What it is" in `site/app/equities/view.tsx`, the contract's `daily[]` row.
- **Why.** No code computes either line (no segment file; every board row held). The hover said "A segment's line is built by the ERW from its companies' prices by the written rule of the method note"; the method note held no such rule (the contract did), and no line is built. Re-doing the weightings "to the digit" is not possible: there is nothing to re-do.
- **The fix on the branch.** The hover says share prices and index levels are held, so no segment line is built, and names the two lines; the method note gains "The segments' two lines (named, not built)": the contract's rule and what it leaves open (finding 7). No figure moves. `tests/test_audit_equities_6.py` fails on main, passes on the branch; the equities suites and scripts pass. It touches the note in another place than finding 9's branch, and merges with it cleanly.

## 7. The weightings' rule leaves open what an analyst asks first

- **Where.** `docs/state/page_files_equities.md`, the series file's `daily[]`.
- **What is open.** "The mean of its companies' daily returns": the close's or the adjusted close's (with dividends) is not said; for utilities and partnerships the dividend is much of the return. "Close times the latest shares outstanding filed": the balance-sheet count only, which 107 of the 243 companies with filed figures lack at their newest period; with the 64 that file nothing, the market-value line would hold 136 of 307 companies (17 percent of integrated oil and gas, 41 percent of midstream, 54 percent of regulated utilities). Five companies are listed by a preferred share (CMS-PB, ETI-P, PCG-PE, PHXE-P, SCE-PG): their close would be a preferred share's price, and four are subsidiaries of a listed parent. 104 of 307 companies sit in two segments.
- **The test.** `tests/test_audit_equities_7.py`. Passes on main. **Not fixed:** each is a rule to settle before any line is built: Samuel's ruling.

## 8. The downloads name a builder that does not exist (words)

- **Where.** `site/lib/equities.ts` `seriesCsv` and `listCsv`: "written by warehouse/derived/equity_pages.py"; the comments of `lib/equitiesfiles.ts` and `app/equities/page.tsx`.
- **Why.** The builder is `warehouse/derived/equity_page_files.py`; no `equity_pages.py` exists. A reader following the provenance (the ERW's rule 5) finds nothing.
- **The fix on the branch.** Each names `equity_page_files.py`. `tests/test_audit_equities_8.py` fails on main, passes on the branch. Merges cleanly with finding 5's branch (the same file, other lines).

## 9. The method note's first section, and the source line (words; a data request)

- **Where.** `docs/methods/equities.md`, "What the files hold today": "`index.json` lists the fifteen segments ... and no company or index; ... no company, index or segment file is written". The page's source line: `equity_universe, equity_prices_daily, equity_fundamentals_quarterly, equity_index_daily`, from the builder's `tables`.
- **Why.** Since 27 November the files hold 307 companies, 243 with statements. No machine has written `equity_prices_daily` or `equity_index_daily`.
- **The fix on the branch.** The section says what changed on 27 November and keeps the first build's words, marked. The tables' list is the builder's: data request 4. `tests/test_audit_equities_9.py` fails on main, passes on the branch.

## 10. "Silver Ores" for four coal miners (a data request)

- **Where.** `index.json` `sic_label` of SIC 1220, printed in the table of every company's "Industry" column.
- **What.** American Resources, Core Natural Resources, Warrior Met Coal and Ramaco Resources are in the Coal segment by SIC 1220, and the page calls their industry "Silver Ores", the SEC submissions' description as the connector keeps it.
- **The test.** `tests/test_audit_equities_10.py`. Passes on main. The label is the data machine's file: data request 5.

## Rows for the main session

**Landing rows (words only, no figure moves):**

- `wip/audit-equities-5` (`49f546757`): "Debt" named "Long-term debt" on `/equities` and in the list download.
- `wip/audit-equities-6` (`b8310ca60`): the hover "What it is" says no segment line is built; the method note carries the two lines' rule.
- `wip/audit-equities-8` (`1f226e40d`): the downloads' provenance names `equity_page_files.py`.
- `wip/audit-equities-9` (`45e671ece`): the method note's first section says what changed on 27 November.
- The four merge with each other cleanly (5 with 8 and 6; 6 with 9 checked by `git merge-tree`). Each needs the site build and the snapshot of rule 8 at landing; this machine runs neither.

**Data requests (for the data machine):**

1. Finding 1: for Consumers Energy (CIK 201533), Southern California Edison (92103) and Pacific Gas and Electric (75488), say which company-facts file gave the rows of 30 September 2026 (and SCE's of 30 June 2026 and its share count of 30 June 2014), and read each subsidiary's own revenue, net income and long-term debt in its filing (accessions `0000811156-26-000032`, `0000827052-26-000073`, `0001004980-26-000055`); write whether the joint-filing rule or the subsidiary's own facts carried the parent's figures.
2. Finding 4: the capital spending line of the cash flow statement in the 10-Q for 30 September 2026 of BSIN (`0001437749-26-036207`), EGY (`0000894627-26-000061`), EONR (`0001437749-26-038029`), PROP (`0001162896-26-000011`), HDRN (`0001193125-26-453519`) and SPRU (`0001628280-26-073907`), and of VAALCO's 10-Qs for 30 June and 30 September 2025 (`0000894627-25-000041`, `0000894627-25-000057`); the concept each tags it under, and whether it is one of the four read.
3. The sample (seed 11403): for AVA `0001193125-26-445765`, DEC `0001922446-26-000108`, DINO `0001915657-26-000074`, DK `0001628280-26-071515`, EE `0001193125-26-450137`, PR `0001658566-26-000124`, PROP `0001162896-26-000011`, PSX `0001534701-26-000037`, RRC `0001193125-26-434351`, WMB `0000107263-26-000036`, XEL `0000072903-26-000181`, find in the filing's own statements each figure `docs/reviews/equities-model-audit-2026-11-28/sample.txt` prints (revenue and net income for 3 months, capital spending for 9, debt and shares at 30 September 2026), as chain 701's `equities_crosscheck.py` did; SLB is already checked.
4. Finding 9: the builder's `tables` (`equity_page_files.py` `build`) names `equity_prices_daily` and `equity_index_daily`, which no machine has written; name only the tables written, or mark the two held.
5. Finding 10: read the SEC's own list of SIC codes for 1220; if its name there is coal mining, write that name as the label of the four companies (or the list's name for every code).

**For Samuel's ruling (default: left as it is):**

- Finding 1: leave out the three subsidiaries' rows that are their parent's (or read their own figures): Consumers Energy, Southern California Edison and Pacific Gas and Electric lose their 2026 rows until then; the table of every company shows their newest own period.
- Finding 2: keep one listing of a business in a segment (the partnership or its holding company; a parent or its subsidiary): up to 10.4 percent of a segment's revenue is counted twice today, and an equal-weight line would count each pair as two.
- Finding 3: a written list for independent power (and one segment for 2911): Independent power falls from 64 companies to 1 by code alone; Integrated and Refining become one segment of 18.
- Finding 4: capital spending from the cash flow statement's line, and a 0 left blank: six companies' newest figure moves from 0, and 52 companies' histories change where a year to date falls.
- Finding 7: settle the weightings' rule before any line is built (total return or price; the cover's share count where the balance sheet has none; preferred-only listings out): the market-value line would hold most of 243 companies instead of 136 of 307.
