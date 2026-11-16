# Session 7501 report: `/contracts` taken to the done line (chain 304, part A)

16 November 2026, samueloldlaptop (code role), unattended. Branch `wip/7501-contracts`, worktree `erw-7501`. Not pushed, not landed. Model spend USD 0.

## At the top

- **A click of the page listed nothing.** In the list by quarter signed, the panel's entry "not stated" under "Delivered in" (the first entry for most quarters: 106 of the 227 rows of 2026 Q2) opened a list of no rows with every count at 0. Fixed (faults row 1).
- **One count of the page was labelled wrong.** The limits box said 10,956 of the 18,989 rows held "give their price as words"; 10,907 do, 49 file neither. Fixed: the box now counts the rows that file no number (row 3).
- **One column is not what the page says it is** and is the data machine's: "Place by contracts" in the megawatts view is ranked by contracts then name, not the other view's place; 76 of the 105 cells drawn differ (row 7). Not fixed here.
- **Not meant:** nothing else. One older test file fails on this branch in `/ask` and imports nothing this session changed (under "Tests").
- **Not verified:** which load the live set holds today. Every figure here is for the load of 5 October 2026 (18,989 rows), the last the notes record. The live database was not read.
- No visitor sees any of this: the page is in review and its table is internal. No hold was touched.

## The five parts

- **Method note.** New: `docs/methods/contracts.md`, the page as a reader meets it, in 11 sections: the columns read, the constants, each of the four views with every figure's rule, what a visitor sees and what the internal view sees, the cross-check, the decisions, what the tool does not hold. The three existing notes (`ferc_eqr_contracts.md`, `eqr_buyers.md`, `eqr_terms.md`) each got one section at their end pointing to it, with the counts made exact. Nothing rewritten.
  - A gap found: the existing notes gave the sense of the name rules, the price rule and the megawatts rule, not their patterns. They are written out in sections 5 to 7, from the builders' code (row 6). The replication is therefore a second implementation of rules read once, not a second reading.
- **Replication.** `replication/contracts/`: `copy_rows.py` (what the page is served, from the tables on the machine, into a folder git ignores), `replicate.py` (every figure again from `ferc_eqr_contracts` and `ferc_eqr_contracts_history`, standard library only, none of the six derived tables read), `page_figures.json` and `.csv`, `replicate.do`. The page's side is `site/scripts/contracts-figures.mjs`: it calls the page's own default export for 72 pages (every listed quarter and product, each listed authority of the default page, the three other views by product, an odd address, a server without the token) and reads the figures off the HTML.
  - As printed: `2539 of 2615 inside the tolerance; 76 named; 0 not explained` and `words (quarters, dates, balancing authorities, 255 names of parties in the rankings): 785 of 785 the same`.
  - The 76 named are all row 7. A check beside them: all 105 "Place by contracts" cells equal a rank by contracts then name; 29 equal the other view's place.
  - 1,083 of the figures are one party's own (a cell of a ranking): compared, and written only as agreed or not. No name is written.
- **Cross-check.** Two figures have a published figure; the rest have none, said plainly (table under "For the pack"). Robots and terms read first. `www.ferc.gov` answered HTTP 403 on its terms pages and its EQR page (its robots file answered and disallows no content page): not read, not worked around.
- **Decisions block.** `site/app/contracts/Decisions.tsx`: 19 choices, each with its default and its source in a hover tip, in a fold at the foot of every view, drawn with or without the token. The list is in the tool's own folder; `lib/decisions.ts` and `DecisionsBlock.tsx` are untouched. The method note carries it word for word (a test holds the two together). The tool has no choice a reader can edit: nothing is editable in place.
- **Faults.** `docs/reviews/contracts-faults-2026-11-16.md`, 13 rows: 5 site, fixed with tests (rows 1 to 5); 1 note, completed (row 6); 1 data machine (row 7); 6 rulings (rows 8 to 13).

## Tests

Each file in its own process, `.venv\Scripts\python.exe -m pytest tests\<file> -q -p no:cacheprovider`, `ERW_SPEND_CAP_USD=0`.

| File | Result |
|---|---|
| `site/scripts/test-contracts-render.mjs` (new; `node --import ./scripts/tsx-register.mjs scripts/test-contracts-render.mjs`) | 40 of 40 passed |
| `tests/test_session7501_contracts.py` (new) | 8 passed |
| `tests/test_session83.py` | 13 passed, 3 skipped |
| `tests/test_session90.py` | 25 passed, 1 skipped |
| `tests/test_session99.py` | 8 passed, 2 skipped |
| `tests/test_session125.py` | 23 passed, 4 skipped |
| `tests/test_session241a.py` | 17 passed |
| `tests/test_session282.py`, `test_session304.py`, `test_session333.py` | 5, 9, 5 passed |
| `tests/test_session142.py`, `147`, `158`, `160`, `177`, `215`, `5163` (they sweep the method notes or the page files) | 42, 65, 58, 40, 28, 12, 6 passed |
| `tests/test_session161.py` (sweeps page files) | **1 failed, 10 passed**: `test-ask-161.mjs`, "a read that was not recorded" for this week's EIA-930 demand. It imports `lib/chat` only, no module this session changed. Not run on the base, so not called the base's |

- Not run: the site build, the full suite, the landing gate, `check-contracts-largest.mjs` (needs a built site and a fixture this machine does not hold).
- The do-file was not run: no Stata on this machine. `replicate.py --headline` follows it step for step.

## What to review

`https://erw-flame.vercel.app/contracts` (internal view; after landing):

1. Open the page. Limits box, second line: "Of the 18,989 rows held here (i), 10,956 file no number." Hover the (i): which rows "held here" is.
2. Panel "Choose", its note: "... executed from 2024-01-09 to 2223-01-01 as filed."
3. Panel, "Quarter signed", last line "2024 Q1 1,404 rows (i)": hover says held from 2024-01-09.
4. Panel, "Delivered in", click "not stated": 106 rows listed, "106 rows of energy, capacity and tolling delivered in not stated". Before: 0.
5. Same list: PSCO appears once in any quarter that holds it.
6. `https://erw-flame.vercel.app/contracts?view=terms`, "Tolling and storage": "382 rows of 217 contracts ... (i)"; hover: 216 in force.
7. Foot of any view: "Decisions on this page (each with its default and its source on hover)", 19 lines, each with an (i).
8. Source line: a new first link, "this page, view by view", to `https://erw-flame.vercel.app/data/methods/contracts`.

## For the pack

**What Samuel signs for `/contracts`:** that every count on its four views is what FERC's filers filed for 2026 Q2, counted by the rules of `docs/methods/contracts.md`; that the page estimates nothing and fills in no price; that one column ("Place by contracts") is known wrong until the data machine rebuilds it; and that the tables stay internal.

**The five choices that matter most:**

| Choice | Default | Source |
|---|---|---|
| Which rows the list holds | The 1,000 days of execution before the last load | `warehouse/supabase/live_set.yaml`; no published rule |
| When two buyer spellings are one buyer | Six rules; a doubtful pair is never merged (1,281 listed) | `docs/methods/eqr_buyers.md`; FERC publishes no buyer identifier |
| What a megawatt stated is | Units MW or kW only; per contract the largest row | FERC's contract file, quantity and units |
| The most one contract can state | 6,809 MW, the largest station operating in the United States | EIA-860M, Inventory of Operating Generators |
| When a price is read from words | One dollar amount, its unit at once, no condition: 23 rows of 104,952 | `docs/methods/eqr_terms.md` |

**The cross-check:**

| Figure | Ours | Theirs | Publisher, document, date | Difference | Why |
|---|---|---|---|---|---|
| Companies filing the report | 3,704 (2025 Q3); 4,010 (2026 Q2) | 3,672, "the total number of EQR filers as of Q2 2025" | FERC, Order No. 917, 91 FR 14306, footnote 354, 24 March 2026 | +32 (0.9 percent); +338 (9.2 percent) | One and four quarters later; the quarter FERC counted is not held |
| Largest station | 6,809.0 MW | 6,809.0 MW | EIA, EIA-860M, inventory as of September 2026 | 0 | Computed from the publisher's own inventory |
| Contracts by product, megawatts stated, prices in words, largest buyers and sellers | the page's | none | | | Nothing published was found to stand against them |

**The Stata commands** (`replication/contracts/`, after `python copy_rows.py`): `do replicate.do` should print

1. contract rows filed for the quarter: 186,873
2. rows that file their rate as a number: 81,718
3. rows that file words and no number: 104,952
4. energy contracts in force: 22,808
5. energy contracts in force that state megawatts, and the megawatts: 356, 31,402.3
6. rows of energy, capacity and tolling executed in 2026 Q2: 227
7. tolling rows, and their contracts: 382, 217

**The rulings, in plain words** (each with the default taken): under "For Samuel's ruling".

## Data request rows

| Requested (UTC) | Session | Table or file | What, exactly | Source | State |
|---|---|---|---|---|---|
| 2026-11-16 11:05 | 7501 | `ferc_eqr_party_mw` (`warehouse/derived/eqr_terms.py`, `party_mw`), then the load of `ferc_eqr_contracts` that stores the summary | `x_rank_contracts` ranks a party by contracts then name; the page calls it the place in the largest view, which `ferc_eqr_party_totals.x_rank` ranks by contracts, then rows, then name. Rank it the same way (or read `x_rank`), rebuild, load. 76 of the 105 cells drawn differ today | `docs/reviews/contracts-faults-2026-11-16.md` row 7; `replication/contracts/replicate.py` | requested |

## Browser read rows

| Asked (UTC) | Session | Branch | Address | What to look at | What should be seen | State |
|---|---|---|---|---|---|---|
| 2026-11-16 11:05 | 7501 | `wip/7501-contracts` | `https://erw-flame.vercel.app/contracts` (internal view) | The panel's note, and the limits box | "executed from <first day> to 2223-01-01 as filed"; the first day says which load the live set holds (2024-01-09 is the load of 5 October). The box reads "file no number", and its (i) opens on hover and on tap | wanted |
| 2026-11-16 11:05 | 7501 | `wip/7501-contracts` | `https://erw-flame.vercel.app/contracts?q=2026-Q2&product=power&ba=not%20stated` (internal view) | The list | 106 rows, not 0 | wanted |
| 2026-11-16 11:05 | 7501 | `wip/7501-contracts` | `https://erw-flame.vercel.app/contracts?view=terms` (internal view), at 1280 and 390 px | The decisions fold opened, three (i) hovered; the tolling (i) | 19 lines; each tip shows "Default:" and "Source:" and stays inside the screen at 390 px; no sideways scroll | wanted |
| 2026-11-16 11:05 | 7501 | `wip/7501-contracts` | `https://erw-flame.vercel.app/contracts` as a visitor | The page | The in-review page: no figure, no row | wanted |

## Landing request

- **Head:** `wip/7501-contracts`, the commit that adds this report (the one before it: `352af102a`). Stacked on `wip/7500-done-line` (`31757a20c`).
- **Tests:** the table above: 2 new files (40 and 8), 16 older files passing, 1 older file with a failure in `/ask` that imports nothing changed here.
- **Changes:** `site/app/contracts/page.tsx`, `site/app/contracts/Decisions.tsx` (new), `site/lib/contracts.ts`; two scripts and one test; one new method note and three extended; `replication/contracts/`; the faults file.
- **Does not change:** `release.ts`, any table, any builder, any connector, any workflow, any shared component or list.
- **Snapshot:** `/contracts` is not one of the 25 pages read and is in review, so no difference is expected on any of them. A new method page appears at `/data/methods/contracts`, and `/data/methods/ferc_eqr_contracts`, `eqr_buyers` and `eqr_terms` each gain a section.
- **Before landing:** a site build (the page gained an import and five expressions; it was drawn here with the TypeScript compiler in transpile mode, which checks no types).

## Needs the key

- None. Whether `/ask` answers from `ferc_eqr_contracts` was not asked (it would need the model).

## Decisions made without you

- The figures are for the load of 5 October 2026 (`copy_rows.py --load-day` takes another day).
- A party's own figure and every party's name are compared and never written, in `page_figures.json` as elsewhere: the tables' notes forbid it. Chain 303's deals files do write names; this tool's rule is stricter.
- The decisions list is drawn by the tool's own component, with the shared block's marks, not by `DecisionsBlock.tsx` (the hover form of that file is on chain 303's branch and not on this one).
- The page's stand-in for `next/font/google` is inside the two new scripts; the shared loaders are untouched.
- The name rules, price rule and megawatts rule were read from the builders' code to complete the note.
- One request each to `www.ferc.gov` for its disclaimers page, privacy policy and EQR page, after its robots file allowed them; all three answered 403 and no more was asked.

## For Samuel's ruling

1. **"MW filed" in the largest view** adds every row with no ceiling; the megawatts view leaves out rows above 6,809 MW. Two cells of the energy lists hold such a row. Default: left as filed, said on hover.
2. **Agreements and contracts** are counted two ways on one page (seller name with agreement identifier in the list; filer with contract identifier elsewhere). Default: left, both stated in the decisions.
3. **Fourteen of a quarter's balancing authorities are listed** (25 in 2026 Q2); 43 rows of the others are reachable only inside the first 400. Default: left.
4. **The page's explanations are grey notes**, where the page standard asks for hover tips. Default: the old notes stay; what was added is on hover.
5. **The license.** `ferc.gov` still refuses this machine on its terms pages. Default: the hold stands; a person reads them in a browser.
6. **No published tally** stands against most of the tool's figures. Default: said so; a source you know of is one more row.

## One line for another tool

- `tests/test_session161.py` fails on this branch in `test-ask-161.mjs` (a recorded read missing for this week's EIA-930 demand): `/ask`, not this tool.
