# Session 7510 report: `/contracts` read as the reader it is for (chain 304, part B)

16 November 2026, samueloldlaptop (code role), unattended. Branch `wip/7501-contracts`, worktree `erw-7501`, on top of session 7501's work. Not pushed, not landed. Model spend USD 0. No web request was made.

## At the top

- **Not meant:** nothing. No file outside the tool's own was changed (`site/lib/gridtool.ts` is read by the page now, not edited).
- **Part A's figures did not move.** The 2,615 figures and 787 words read off the 73 drawn pages are the same before and after this session's changes. The replication now compares three more figures a page: `2728 of 2804 inside the tolerance; 76 named; 0 not explained` (the 76 are part A's row 7), `785 of 785` words the same.
- **A count that overstated:** "Rows with a price as a number" counts a rate filed as 0. Of the 1,315 numbers in the listed rows of energy, capacity and tolling, 302 are 0. The page now says how many (row 11); whether a 0 counts at all is yours to rule (row 19).
- **A click that lost the reader's place:** a click on another quarter dropped the balancing authority chosen, and in one quarter of case 1 the authority could not be chosen again from the panel. Fixed (row 1).
- **One older test still fails**, as session 7501 reported: `tests/test_session161.py` in `/ask` (`test-ask-161.mjs`, a recorded read missing for EIA-930 demand). It imports nothing this session changed.
- **Not verified:** which load the live set holds today (every figure is for the load of 5 October 2026); anything a browser shows; the types (the page was drawn in transpile mode).

## The reader and the five cases

- **The reader:** a credit analyst at a fund that lends against contracted power plants, checking one offtake contract's price, term and counterparty. Why: the page was built for a credit investor's question (session 83) and its columns are an underwriter's.
- 1. A unit power energy contract of 15 years delivered in SPP, signed in 2025 Q3: its price against SPP's long-term energy contracts of 2025.
- 2. A resource adequacy capacity contract delivered in CAISO, signed 2025 Q3 to 2026 Q2: its price in USD per kW-month.
- 3. What a buyer in the Southeast pays for capacity under contracts signed since January 2024.
- 4. A tolling agreement for a battery in California, signed in 2024 or 2025: the toll.
- 5. The buyer of case 1's contract: its energy contracts in force and the megawatts they state.

## The rows by kind

`docs/reviews/contracts-read-2026-11-16.md`, 22 rows:

- **site, fixed with a test: 11** (rows 1 to 11).
- **data machine: 4** (rows 12 to 15).
- **browser: 2** (rows 16, 17).
- **ruling: 5** (rows 18 to 22).
- license, key: none new. Part A's rows 7 to 12 are cited where a case meets them, not written again.

## What was fixed

All in `site/app/contracts/page.tsx` and `site/lib/contracts.ts`; nothing the page had was dropped.

- Row 1: a quarter's link and a product's link keep the balancing authority chosen.
- Row 2: the rows beside each quarter say on hover that they are every product's, delivered anywhere.
- Row 3: the authority chosen stays in the panel when it has no row in the quarter (or is past the fourteenth), with its count.
- Row 4: an address that names a quarter not listed (a year) says so and says which quarter is shown.
- Row 5: "1 row ... was signed: 1 agreement between 1 seller and 1 buyer"; "The other 1 gives words".
- Row 6: a term under one year also gives its days ("0.1 years: 30 days"), first and last day counted. The years stay.
- Row 7: a number filed with no unit is followed by "(no unit filed)".
- Row 8: four lines in the fold "What a row is": the quantity's units; the price's units and that one price in two units is not converted; rows that differ only in their price; a market operator as the buyer.
- Row 9: CISO, SWPP, ISNE, NYIS and ERCO say the grid's name on hover (from `site/lib/gridtool.ts`).
- Row 10: the megawatts view's line of advice is a statement.
- Row 11: the note under "Rows with a price as a number" says how many of them are the number 0.
- Also: `docs/methods/contracts.md` gained section 12 (what the list also draws); `replication/contracts/replicate.py` and `site/scripts/contracts-figures.mjs` compare the days, the no-unit marks and the zeros on every drawn page; `page_figures.json` and `.csv` were written again by the replication's own `--write` (2,804 figures).

## Tests

Each file in its own process, one at a time; python as `.venv\Scripts\python.exe -m pytest tests\<file> -q -p no:cacheprovider` with `ERW_SPEND_CAP_USD=0`; node as `node --import ./scripts/tsx-register.mjs scripts/<file>` in `site`.

| File | Result |
|---|---|
| `site/scripts/test-contracts-read.mjs` (new) | 46 of 46 passed |
| `site/scripts/test-contracts-render.mjs` (session 7501's) | 40 of 40 passed |
| `replication/contracts/replicate.py` (run whole, then with `--write`) | exit 0: 2,728 of 2,804 inside, 76 named, 0 not explained; 785 of 785 words |
| `tests/test_session7501_contracts.py` | 8 passed |
| `tests/test_session83.py` | 13 passed, 3 skipped |
| `tests/test_session90.py` | 25 passed, 1 skipped |
| `tests/test_session99.py` | 8 passed, 2 skipped |
| `tests/test_session125.py` | 23 passed, 4 skipped |
| `tests/test_session241a.py`, `282`, `304`, `333` | 17, 5, 9, 5 passed |
| `tests/test_session142.py`, `147`, `158`, `160`, `177`, `215`, `5163` (they sweep the notes and the page files) | 42, 65, 58, 40, 28, 12, 6 passed |
| `tests/test_session161.py` | **1 failed, 10 passed**: the `/ask` failure session 7501 reported, unchanged |

- `tests/test_session83.py` failed once on the way: it holds `counts()` to its exact keys. The count of zeros was moved to its own function (`zeroPriced`) and the file passes unchanged.
- Not run: the site build, the full suite, the landing gate, `check-contracts-largest.mjs` (it needs a built site).

## What to review

Internal view, after landing.

1. `https://erw-flame.vercel.app/contracts?q=2025-Q3&product=energy&ba=SWPP`. The sentence: "8 rows of energy delivered in SWPP were signed in 2025 Q3". In the panel, hover the (i) beside "Quarter signed": "The rows beside each quarter are every product's, delivered anywhere". Hover the (i) beside SWPP: "SWPP is the balancing authority code of Southwest Power Pool (SPP)".
2. Same page, click "2025 Q2" in the panel: the address keeps `ba=SWPP`; the sentence reads "1 row of energy delivered in SWPP was signed in 2025 Q2: 1 agreement between 1 seller and 1 buyer"; the panel ends with "SWPP 1" marked as the choice (it is not among the fourteen listed).
3. Click "2026 Q2": "0 rows of energy delivered in SWPP were signed in 2026 Q2"; the panel ends with "SWPP 0".
4. `https://erw-flame.vercel.app/contracts?q=2025&product=energy&ba=SWPP`: a box reads 'Quarter signed: "2025" is not listed here, so 2026 Q2 is shown.'
5. `https://erw-flame.vercel.app/contracts?q=2025-Q3&product=capacity&ba=CISO`: 27 rows. In "Term": "(0.0 years: 14 days)" twice, "(0.1 years: 30 days)" four times, "(1.0 years)" with no days. Under "Rows with a price as a number": "The other 2 give words".
6. `https://erw-flame.vercel.app/contracts?q=2025-Q2&product=capacity&ba=CPLE`: 2 rows; one price is a number followed by "(no unit filed)".
7. Any list, the fold "What a row is": the lines "Quantity", "Rows that differ only in their price" and "A market operator as the buyer"; the price line ends "A number filed with no unit says so."
8. `https://erw-flame.vercel.app/contracts?q=2026-Q1&product=capacity&ba=CISO`: under "Rows with a price as a number": "The other 3 give words: a market-based rate, a formula, or nothing. 3 of the 9 file the number 0." On the 2026 Q2 page of the same choice no such sentence stands: no row there files 0.
9. `https://erw-flame.vercel.app/contracts?view=mw`, the fold: "The contract itself, not its row here, is the record of its size."

## Data request rows

| Requested (UTC) | Session | Table or file | What, exactly | Source | State |
|---|---|---|---|---|---|
| 2026-11-16 12:35 | 7510 | The database function `internal_eqr_contracts` (`warehouse/supabase/migrations/020_eqr_contracts.sql`: a new migration) | Answer six more columns of each row: `x_begin_date`, `x_end_date`, `x_increment_name`, `x_increment_peaking_name`, `x_rate_minimum`, `x_rate_maximum`. Of the 3,785 listed rows of energy, capacity and tolling, 564 are drawn the same as another row of their agreement but for the price; these columns tell 326 of them apart. The page then draws the row's period beside its price (site work, one cell) | `docs/reviews/contracts-read-2026-11-16.md` row 12; `ferc_eqr_contracts` columns 24, 25, 31, 32, 39, 40 | requested |
| 2026-11-16 12:35 | 7510 | `warehouse/supabase/load.py`, `eqr_summary` (the stored summary of `ferc_eqr_contracts`) | Add the rows, and the rows that file a number, by quarter of execution, product group (energy, capacity, tolling, other) and delivery balancing authority (the code trimmed and in capitals, "not stated" for none). The panel's count beside each quarter then follows the product and authority chosen, and a year reads as its four quarters. Today the count is every product's | review row 13 | requested |
| 2026-11-16 12:35 | 7510 | A new small table or page file: balancing authority codes and names | The codes FERC's filers use for the delivery balancing authority (65 in the rows held, 44 of them on rows of energy, capacity and tolling: CPLE, DUK, SOCO, WACM, BPAT and others) with each one's name, from a publisher whose terms allow it (EIA publishes its list of balancing authorities with their codes; `www.ferc.gov` refuses this project). The page names only the seven grids' codes today | review row 14 | requested |
| 2026-11-16 12:35 | 7510 | `ferc_eqr_party_totals` and `ferc_eqr_party_mw` in the live set, or a function that answers one party's line | A buyer or seller outside the first 25 cannot be found: 25 of 4,517 buyers of energy are stored (`EQR_TOP`). Serve one party's line by its merged name, with the internal token, so the page can take a name | review row 15 | requested |

## Browser read rows

| Asked (UTC) | Session | Branch | Address | What to look at | What should be seen | State |
|---|---|---|---|---|---|---|
| 2026-11-16 12:35 | 7510 | `wip/7501-contracts` | `https://erw-flame.vercel.app/contracts?q=2025-Q3&product=capacity&ba=CISO` (internal view), at 1280 and 390 px | The list's "Term" cells and the page's width | "(0.1 years: 30 days)" inside its cell; the table scrolls inside its own frame; no sideways scroll of the page at 390 px | wanted |
| 2026-11-16 12:35 | 7510 | `wip/7501-contracts` | `https://erw-flame.vercel.app/contracts?q=2025-Q3&product=energy&ba=SWPP` (internal view), at 1280 and 390 px | The (i) beside "Quarter signed", and the (i) beside CISO, SWPP, ISNE, NYIS in "Delivered in" | Each tip opens on hover and on tap, reads in sentence case (the heading is in capitals), and stays inside the screen: the panel is 240 px wide, a tip 288 px | wanted |
| 2026-11-16 12:35 | 7510 | `wip/7501-contracts` | The same address, then a click on "2025 Q2" and on "2026 Q2" | The address and the panel | `ba=SWPP` kept; "SWPP 1" then "SWPP 0" at the foot of "Delivered in", marked as the choice | wanted |

## Landing request

- **Head:** `wip/7501-contracts`, the commit that adds this report (the one before it: `f2962a5b5`; this session's four commits begin at `a59cb8046`). Stacked on session 7501's `118e668fa`.
- **Tests:** the table above: 1 new file (46), session 7501's render test (40), the replication (exit 0), 16 older python files passing, 1 with the `/ask` failure that was there before.
- **Changes:** `site/app/contracts/page.tsx`, `site/lib/contracts.ts`; `site/scripts/contracts-figures.mjs`, `site/scripts/test-contracts-read.mjs` (new); `replication/contracts/replicate.py`, `page_figures.json`, `page_figures.csv`; `docs/methods/contracts.md` (section 12); `docs/reviews/contracts-read-2026-11-16.md` (new); this report.
- **Does not change:** `release.ts`, any table, builder, connector, workflow, migration, shared component or list.
- **Snapshot:** `/contracts` is in review and is not one of the 25 pages read: no difference is expected on any of them. `/data/methods/contracts` gains a section.
- **Before landing:** a site build. The page gained one import (`@/lib/gridtool`) and five functions of `lib/contracts.ts`; it was drawn here in transpile mode, which checks no types.

## Needs the key

- None.

## Decisions made without you

- **The reader** is a credit analyst at a fund, not the chain file's "fund analyst" in general: the page's first line of code says who asked for it.
- **Days of a short term** count both the first and the last day, and the years stay beside them: the page standard drops nothing.
- **The count of zeros** has its own function; `counts()` is left as session 83's test holds it.
- **Balancing authority names** are given only for the seven grids the site already names. No name was written from memory for the others (row 14).
- **The fold's example of two units** is the unit identity (1 $/KW-MO and 1,000 $/MW-MO), not a row's price.
- **The replication was extended** by three figures a page and its two figure files written again by its own `--write`; part A's 2,615 figures are among the 2,804, unchanged.
- **No party's name, row or own figure** is in any committed file: the review states counts and the page's own words; the test's rows are made up. The scratch files that hold names are under `runs/` (ignored) and `site/scripts/_7510_draw.mjs` (excluded, not committed).
- **The deals table was compared by the words of names** (1,905 pairs of seller and buyer): no agreement is on both pages, so no figure could disagree.

## For Samuel's ruling

1. **One unit for capacity prices** (row 18). The list shows $/MW-MO, $/KW-MO and $/KW-DAY side by side. Default: as filed, with one line in the fold on the thousandfold. The other choice: a second figure in USD per kW-month where the filed unit allows it.
2. **Is a rate of 0 a price?** (row 19). 302 of 1,315 numbers are 0. Default: counted as a number, and the page says how many. The other choice: its own count.
3. **Terms that end on 2099-12-31** (row 20): 27 rows, drawn as terms of 70 years and more. Default: as filed. The other choice: the words "as filed" after such a date.
4. **Rows whose buyer is a market operator** (row 21): counted among the contracts signed (356 of 3,785 by the words of the name), and the site's catalog calls the page "bilateral power contracts". Default: counted, with one line in the fold; the catalog's word left to you. The other choice: a filter, which needs a list of operators as a decision.
5. **Rows whose seller is named for storage** (row 22): counted (715) and not listable. Default: no filter added. The other choice: one more entry under "Product".
