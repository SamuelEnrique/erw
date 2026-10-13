# Session 213 report: "What a datacenter pays" on the battery page's three questions, and where the three pages still differ

13 October 2026, from 01:56 UTC, unattended, on the old laptop (`samueloldlaptop`, a code machine). Branch `wip/213-datacenter-layout`, from `wip/212-generator-layout` (decision 1), pushed, **not landed** (the chain prompt: "Do NOT land"). Model spend USD 0. Pulls: none. No data lock, no warehouse table written. No em dash in anything written.

## Read these first

- **The page asks the battery page's three questions, in its order, with its components.** "What will it pay?": the summary sentence, the three headline numbers, the cost chart by year, the cost table "What will it cost" (its rows as they were, Texas's delivery rows among them), one sentence of what the model cannot see, a line of links to the grid's own pages, and the two CSV lines. "Which option is better?": scenarios A and B on the shared block, ten assumptions now (the contract's share of the energy and its price last, 0 by default), the results table with its eight rows and "B against A" as before. "What matters most": the sensitivity chart with one line on how to read it, the contract rows drawn only when the scenario holds a contract. Screenshots before and after, 1280 and 390 px: `docs/brand/review-213/`.
- **Every number is unchanged.** The defaults stay (hurdle rate 9.6). The results table's sixteen cells and the chart's eight bars are identical in every raw value before and after; the page's visible numbers that stay are the same; `check-values` 345 of 345 across the three cost-of-power pages; the browser check 96 of 96; the Python mirror of the library (214 tests of ten modules) OK. One wording changed in a results note (the fixed-price row says "the last twelve months' market price").
- **What left the page is in two CSV downloads, computed by the page's own code.** `months.csv` (every year and every month: the flat price, this load's, the foreseen price, the hours off, the cost for the size, the hours held) and `tables.csv` (long form, a row a cell: "Will the power be there", "How clean", "How soon" with the waits of a large load by stage and the rules in motion, every region of the grid, the Commission's transmission charge matrix, and New York's load in line where NYISO's terms allow it). What the page computes moved out of `page.tsx` into `model.ts`, unchanged line for line; the words the two blocks wrote (the waits, the rules) are written by the same library functions. In review a visitor is answered 404.
- **Gone outright, for your ruling:** the three grid questions as sections ("Will the power be there", "How clean", "How soon"), with the waits and the rules blocks (`LoadWaits.tsx` and `RulesInMotion.tsx` stay on disk, undrawn, as do the three cells in `grid-cells.tsx`); the standalone contract panel and "With your contract" (`LoadContract.tsx` on disk, undrawn). The links those sections carried to the demand, mix, queue and datacenter pages stand in one line under the cost table.
- **The three pages now share one layout.** The table below lists every place they still differ. The datacenter and generator pages are in the site's own style; the brand sheet is the battery's until Samuel approves it.

## What to review

1. The screenshots: https://github.com/SamuelEnrique/erw/tree/wip/213-datacenter-layout/docs/brand/review-213 (`datacenter_before_1280.png` against `datacenter_after_1280.png`, then the two at 390 px; `README.md` says what to look at).
2. The table of differences below.
3. To see it live on the old laptop: `git switch wip/213-datacenter-layout`, `cd site`, `npm run build`, `npx next start -p 3213`, open http://localhost:3213/internal/open, then http://localhost:3213/cost-of-power . The downloads: `/cost-of-power/months.csv` and `/cost-of-power/tables.csv`.

## Where the three pages still differ (battery, generator, datacenter)

The three on `wip/213-datacenter-layout`: `/cost-of-power/battery` (sessions 203, 208, 211), `/cost-of-power/seller` (session 212), `/cost-of-power` (this session).

| Place | Battery | Generator | Datacenter | Why, and what would close it |
|---|---|---|---|---|
| The first question's title | "What did it earn?" | "What did it earn?" | "What will it pay?" | the chain prompt's words: a buyer pays |
| The second question's title | "Is it worth building?" | "Is it worth building?" | "Which option is better?" | the chain prompt's words |
| The third question | "What matters most" | the same | the same | none |
| The style | the brand, version 0 (`brand.css`, Source Serif 4, IBM Plex, no header bands, the headline row on a subgrid, square bar ends, balanced titles) | the site's tokens (Georgia, cardinal header bands) | the site's tokens | `docs/brand.md`: no page but the battery's takes the brand until Samuel approves it; the sheet is scoped to `.brand-a` and would be one class on each page |
| The view switch above the page | none | none | "Your load" and "Grid by grid" (`ViewNav`) | the datacenter page keeps its older tab-wide view; a ruling |
| The panel's name and fields | "Your battery": grid, duration, strategy, size | "Your plant": grid, hub, asset, size (a battery's energy, a peaker's heat rate and variable O&M), a battery beside it | "Your load": grid, region, size, how it runs, how it buys | each tool's own inputs |
| The summary sentence | one sentence, keyed | one sentence (the model's words) plus the capture price | one sentence with the GPU-hour | each tool's own |
| The three headline numbers | last twelve months per kW; a bad month; debt coverage | revenue per kW; the price received (or while selling or running); debt coverage | market energy per MWh; a bad month; power per GPU-hour | each tool's own measures; the row of three is the same component |
| The chart | the year chart in SVG, stacked by stream, drawn by the page (direct labels, no legend box) | revenue by year, ECharts, a legend | cost by year, ECharts, a legend | the brand asks for direct labels; the two ECharts charts wait for the brand |
| The income or cost table | "Income by stream" (streams by span) | "The last twelve months beside the long-run averages" (five measures by span) | "What will it cost" (rows of the cost, with Texas's delivery rows) | each tool's own; the heading is an `h3` on all three |
| Under the table | one sentence of what the model cannot see; "Every month, CSV" (and the stress days for ERCOT) | one sentence; "Every month, CSV" and "The other tables, CSV"; "Your plant's own year" (the pasted profile) | one sentence; a line of links to the grid's own pages; "Every month, CSV" and "The other tables, CSV" | the battery has no second download (it has no other tables); the generator keeps its one reader's tool; the datacenter keeps the links its grid sections carried |
| The assumptions | twelve (ten of the finance and the model's two steps, then the contract's two) | ten (eight, then the contract's two) | ten (eight, then the contract's two) | each tool's own |
| The contract's form | a share of the battery's power at USD per kW-month | solar and wind a share of the energy at USD per MWh; a battery and a peaker a toll on a share of the capacity | a share of the energy at USD per MWh | each tool's own; the defaults are 0 on all three |
| The results table | seven rows | eight rows | eight rows and "B against A" | each tool's own; the last row "What differs" is the block's on all three |
| The sentence under the table | NPV | NPV | the present value and the all-in GPU-hour | each tool's own |
| The chart's measure | NPV | NPV | all-in power per GPU-hour | each tool's own |
| The how-to-read line | "holds the other eleven" | "holds the other nine" | "holds the other nine" | the count of assumptions |
| Check keys on the face | 51 (`bs|...`) | 2 (`mr|...`: the headline's coverage and debt payments) | none (`data-stat` marks; the browser check holds the figures) | the datacenter page never carried check keys (its tables are its own files); `check-values` reads the other two |
| The downloads | `months.csv` (and the public stress table) | `months.csv`, `tables.csv` | `months.csv`, `tables.csv` | |
| The usage counter | `data-no-usage` on the page (session 208) | the pasted profile's promise silences it | `data-no-usage` on the page (this session) | the same rule three ways; one mark on all three would be cleaner |
| The methods note's anchor | `battery_earns_algorithm#cannot-see` | `generator_earns_algorithm#cannot-see` | `datacenter_pays_algorithm#cannot-see` | the same |

## What was done

1. **The contract as two scenario assumptions** (`lib/datacenter/finance.ts`): `cshare` (letter `n`, percent of the energy, 0 to 100, step 10 points) and `cprice` (letter `c`, USD per MWh, 0 to 1,000, step USD 1); `contractShare`, `merchantShare`, `contractYear`, `marketYear`; `price`, `bill` and `costInYear` read them (the market's cost and the other charges change by the yearly rate as before, the contract's cost is fixed); `levelPrice` does not (the market's breakeven for the whole of the energy); `sensitivity` draws the contract rows only when the scenario holds a contract; `FINANCE_KEYS` the eight of session 194. At a share of 0 every expression is the old one in the old order, to the bit (the Python mirror of session 194 holds every number to one in a million on its cases, and did not until the order was kept: decision 4).
2. **The block, the chart and the headline** (`LoadScenarios.tsx`, `LoadHeadline.tsx`): the block is handed `chart: null`; `LoadSensitivity` draws the shared `Sensitivity` in the third section; `useBlock` holds what both read; the first headline number reads A's contract (the price of the energy with it, named in its note) and is the market's at a share of 0.
3. **The page** (`page.tsx`): three `ToolSection`s inside `data-question` wrappers; `model.ts` holds what `LoadView` computed before (every line moved, none changed); `months.csv/route.ts` and `tables.csv/route.ts` the downloads (the seller's `csv.ts` shared), each gated on the page's status; `grid-cells.tsx` the three cells the grid questions drew, undrawn; `data-no-usage` on the page (the contract panel's promise had silenced the counter, as on the battery in session 208); the form's line about the contract panel now points to the second question.
4. **The checks.** `test-datacenter-finance.mjs`: the session 213 block (thirteen assertions on the contract's arithmetic, the address, the chart's rows and the row in words). `check-datacenter-scenarios.mjs`: the chart read from the document, the three questions' order, the how-to-read line, the two downloads fetched by the browser and parsed (their tables, and the months' newest twelve complete months giving the page's flat price to the dollar a month), section 9 rewritten as the contract as assumptions, a visitor's 404. Eight test modules' pins moved (decision 5).
5. **The note** (`docs/methods/datacenter_pays_algorithm.md`): a session 213 lead to section 4, the "What the model cannot see" list with its anchor, 4.10 marked gone, 4.14's ten assumptions with the contract's formulas.

## Checks, with exit codes

None piped; outputs under `runs/session213/`.

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py` (session 211's, 01:15 UTC; the same duty holds) | 0 | on duty until 13 October 17:15 UTC |
| `npx tsc --noEmit`, twice | 0, 0 | |
| `node scripts/test-datacenter-finance.mjs`, three times | 1, 1, 0 | the first: four pins of eight assumptions; the second (after the pins): the arithmetic's order with other charges and growth, fixed (decision 4); the third all passed |
| `python -m unittest` on the ten modules that read the datacenter page, before the pins moved (`tests1.out`) | 1 | 214 tests, 20 failures and 2 errors: eighteen pins of a section or a line that moved; two of the Python mirror, the arithmetic's order (decision 4) |
| the same ten after (`tests2.out`) | 0 | 214 tests OK |
| `npm run build`, five times (the restructure; the arithmetic's order; a visible note; the form's line; the usage mark) | 0 ×5 | no "statement timeout" line |
| `runs/session208/capture.mjs` before and after, 1280 and 390, and on the final build | 0 ×6 | the one checked key identical; the visible text's numbers: 1,437 before, 258 after, the only new ones the two contract fields' "Default 0." |
| `runs/session212/cells.mjs` before, after and on the final build | 0 ×3 | 16 cells and 8 bars, every raw value identical |
| `node scripts/check-datacenter-scenarios.mjs http://localhost:3213`, twice | 1, 0 | the first: eight "no request" assertions, the usage counter (fixed, `data-no-usage`); the second 96 of 96 |
| `CHECK_VALUES_PAGES=/cost-of-power node scripts/check-values.mjs` (`MSYS_NO_PATHCONV=1`; the three cost-of-power pages) | 0 | 345 of 345 values match Supabase |
| `node scripts/test-battery-finance.mjs`, `test-seller-finance.mjs`, `test-decisions-195.mjs` | 0, 0, 0 | |
| `curl` of `months.csv` as a visitor | | 404 "in review" |
| `scripts/freeze.py status` | not run | nothing deployed |
| Whole suite in a clean copy | not run | not landed; the chain prompt says not to. Run it before the landing |

## Decisions made without you

1. **The branch comes from `wip/212-generator-layout`** (which comes from `wip/203-brand-battery`): the exported `Sensitivity`, the shared `csv.ts` and the battery's `read.ts` (the internal view's test the downloads use) live there. The landing order is the battery, the generator, then this. Reversible: a rebase.
2. **The three grid questions left the page.** The ruling names three questions and the battery's components; "Will the power be there", "How clean" and "How soon" are none of them, and their rows are tables, which the ruling sends to the download. Their links stand in one line under the cost table, so nothing the page pointed to is unreachable. Restoring any of them is one `ToolSection` each (`grid-cells.tsx`, `LoadWaits.tsx` and `RulesInMotion.tsx` are on disk).
3. **The contract's price letter is `c`**, the share's `n`; the page's own parameters take none of the block's letters. The datacenter finance test had listed `ac` as a name that is not a scenario's; it now lists `ak`.
4. **The order of the arithmetic was kept to the bit.** The first draft wrote the cost of a year as the market's cost times the growth plus the other charges flat, which moved the present value when other charges and growth were both set (the Python mirror caught it, 2 of 300 cases). The other charges change by the rate as before; only the contract's cost is fixed.
5. **Eight test modules' pins moved**, each with a session 213 note: 138 (the three titles, the downloads' tables, the placeholders in `note`, the one "cannot see" sentence allowed on the face, the two download folders), 140 and 149 (New York's rows behind the switch, in the download), 153 and 195 (a page line now in `model.ts`), 154 and 163 ("How soon", the waits and the rules as the download holds them), 194 (ten assumptions; the block in the second question, the chart in the third; the letters).
6. **No brand sheet on this page** (as session 212 on the generator): `docs/brand.md` gates it on Samuel's approval of the battery.
7. **The headline's first number reads A's contract** (the price of the energy with it, named in its note), as the battery's coverage does; the bad month and the GPU-hour's note do not name it (the GPU-hour's value does read it).

## For Samuel's ruling

1. The page, from the screenshots; the three grid questions off the page (decision 2) against keeping any of them as a fourth section.
2. The brand sheet for the generator and datacenter pages (one class each), when the battery's is approved.
3. The two titles the chain prompt gave the datacenter ("What will it pay?", "Which option is better?") against the battery's ("What did it earn?", "Is it worth building?"): keep the buyer's words, or one pair for all three.
4. The datacenter's "Grid by grid" view switch, which the other two pages have nothing like.
5. The landing order: the battery (`wip/203-brand-battery`), the generator (`wip/212-generator-layout`), then this.
6. The ECharts charts of the generator and datacenter pages against the battery's SVG with direct labels, when the brand lands.
7. Sessions 208, 211 and 212's open items stand.

## To finish

- The landing, after the generator's: `git switch -c task/213-datacenter-layout wip/213-datacenter-layout`, `git merge origin/main`, the whole suite in a clean worktree, `npm run build`, the before snapshot as its own command, `git push`, the after snapshot and the comparison (the page is in review: 0 differences expected on the 25 pages).

## The prompt

Chain of 12 October, evening, sessions 210 to 213, code machine, unattended. Session 213: "'What a datacenter pays' (site/app/cost-of-power), the mirror layout. Branch wip/213-datacenter-layout. Do NOT land. 1. Three questions, same components and order: 'What will it pay?' (headline, three numbers, cost chart, cost table), 'Which option is better?' (Scenarios A and B with its existing assumptions and contract inputs), 'What matters most' (sensitivity chart if the page has one; if not, build it with the battery's component on the page's own cost model). 2. Defaults stay as they are (hurdle 9.6). Same removals as session 212. Every number unchanged; check-values passes. Screenshots at 1280 and 390 to docs/brand/review-213/. 3. Report: one table across battery, generator and datacenter, listing any place the three pages still differ in layout, labels or components."
