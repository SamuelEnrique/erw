# Session 7511 report: the severance tool read as the reader it is for (chain 304, part B)

16 November 2026, samueloldlaptop (code role), unattended. Worktree `erw-7502`, branch `wip/7502-severance`, stacked on session 7502's work, not pushed. Model spend: USD 0. The read: `docs/reviews/severance-read-2026-11-16.md`.

## At the top

- **A disagreement between two pages was found and not fixed (row 13).** `/learn/problems` (set D, questions 4 and 5) sends a student to `/severance` and gives an answer 17 to 86 cents from what the calculator shows for the same case: for 1,000 bbl of Texas oil in October 2026, USD 4,695.05 in the key and USD 4,695.22 on the calculator. The key taxes the month's mean before it is rounded; the calculator rounds the mean to the cent first. The cause is site code, in the problem sets: `lib/problems.ts`, the landing's value checker (`scripts/check-values.mjs`, which this machine cannot run without a build) and a frozen edition file a builder writes. A change to one of the three without the others would fail a landing, so it is written as a ruling with the patch, and no file of that tool was touched. The key's figures were computed here from the table by that file's rule; the page itself was not drawn.
- **No file outside the severance tool was edited.**
- **Eight site faults fixed on the page, each held by a test.** None changes a tax: 612 of 612 figures of part A's replication still agree after the changes.
- **Two disagreements with `/impact` (rows 14 and 15)** are for the owner's ruling, as that page is under his review: it prices an Mcf at 1,034 Btu a cubic foot where `/severance` prices it as one MMBtu (3.4 percent more tax on the same gas), and it counts Texas's regulatory fee inside "Severance" where `/severance` draws it apart.
- **Not run:** no site build. The four changed site files passed a narrow type check (`tsc --noEmit` on them and what they import, the site's settings less Next's plugin, exit 0, no message: `runs/7511/tsc.out`). That is not a build.
- **How a case was set:** the calculator reads no input from the address, so each case was drawn by giving the component's inputs their values as it is drawn (the test's header says how). It is what a reader's choices would leave on the screen, with no click made.

## The reader and the five cases

- **The reader:** a small operator of low-producing wells, or whoever files and checks its production tax reports. Every input of the page is an operator's and the Lease tab speaks of "your wells"; no input is an owner's share. The mineral owner's question is case 5.
- 1. A Gray County, Texas gas well at 60 Mcf a day: the low-producing gas well credit in August and September 2026.
- 2. A three-well oil lease in Wichita County, Texas at 8 barrels a well a day: the low-producing oil lease credit, August to October 2026.
- 3. A well near Jal, Lea County, New Mexico (district 19, suffix 2541), 3,000 bbl and 9,000 Mcf, a one-eighth federal royalty: the four taxes in August and October 2026.
- 4. Louisiana, October 2026: a Caddo Parish stripper well at 5 barrels a day; a De Soto Parish horizontal gas well completed 15 March 2026, 300,000 Mcf.
- 5. A Reeves County, Texas well at 600 barrels and 1,500 Mcf a day in October 2026: the tax on the well's month and on a one-eighth royalty's share.
- The places, rules, months and prices are real; the sizes are stated sizes and belong to no named well, lease, operator or owner.

## The rows by kind (17)

- **Site, fixed: 8.** Rows 1 (a certified price drawn as "$1.2"), 2 (a flag that said the Comptroller had published no price, when the rules file holds none), 3 (August's report period beside October's price, unsaid), 4 ("the well did not produce" for a file that begins late), 5 (New Mexico's ad valorem line cited the wrong document), 6 (a tax left out drawn as "0%" and "$0.00"), 8 ("Regulatory fees $0.00" for a Louisiana or New Mexico file), 9 (no word that a share of the volume gives the tax on that share).
- **Data machine: 2.** Rows 10 (who bears the tax, and Louisiana's fee, are not in the rules file) and 12 (the states' first purchase prices of crude are not in the warehouse).
- **License: 1.** Row 11 (Waha, the Permian's gas price, needs a license; Henry Hub stays).
- **Ruling: 5.** Rows 7, 13, 14, 15 and 16.
- **Browser: 1.** Row 17 (four ready rows below).
- **Cited from part A, not written again:** its row 2 (September 2026's certified prices are published and not held: cases 1 and 2 meet it, September's gas credit of 100 percent is not computed) and its row 5 (New Mexico's rates end on 31 August 2026: case 3's October meets it).

## What was fixed

- `site/app/severance/Calculator.tsx`: the report period list is named and carries a hover (the latest month held, the month the price box opened on, that the list does not change the price); certified prices to the cent; "Monthly volume" carries a hover on shares, placed outside the label; New Mexico's ad valorem line cites TRD's rate table and reads "left out" with the districts' range when no district is chosen.
- `site/app/severance/lease/LeaseTool.tsx`: the fees card reads "not held", with a hover, for a file with no Texas well.
- `site/lib/lease.ts`: the two flags' words (rows 2 and 4); certified prices to the cent.
- `site/lib/severance.ts`, `site/app/severance/page.tsx`: certified prices to the cent.
- Nothing the page had was dropped. No new input, no new page, no grey note added.

## Tests

One file at a time, output under `runs/7511/tests/`, each exit code read.

| File | Count | Result |
|---|---|---|
| `site/scripts/test-severance-read.mjs` (new) | 30 | pass |
| `site/scripts/test-severance-page.mjs` | 21 | pass |
| `site/scripts/test-lease.mjs` | 93 | pass |
| `site/scripts/test-severance.mjs` | 26 cases | pass |
| `site/scripts/test-forecast.test.mjs` | 52 | pass |
| `tests/test_session40.py`, `45`, `239`, `282`, `334` | 3, 6, 21, 5, 4 | pass |
| `tests/test_session57.py` | 7 | pass, 3 skipped by their own rule |
| `tests/test_session7502_severance.py` | 14 | pass |
| `replication/severance/replicate.py` on the page's figures drawn again | 612 figures, 37 word keys | 612 of 612, 37 of 37 |

- Not run: `site/scripts/test-finder.mjs` (its three files are not on this machine: part A, row 4) and `scripts/check-values.mjs` (it needs a built site).

## What to review

- `https://erw-flame.vercel.app/severance` (in review: open it with the review cookie).
  1. Product: gas. Tick "Low-producing gas well credit". Above the list: "Report period (the production month)" with an "i". Hover it: the latest month held (2026-08), the month the price box opened on, and that the list does not change the price. In the list, October 2025 reads "certified $1.20".
  2. Hover the "i" beside "Monthly volume": a share of the volume gives the tax on that share; who bears the tax is not a rule the page has read.
  3. State: New Mexico. With no district: the fourth line reads "no district chosen: left out of the total (0.7105% to 1.7249% by district)" and "left out" in the figures column. Choose "LEA JAL, district 19, suffix 2541": 1.4863%, and the line's link is TRD's rate table.
- `https://erw-flame.vercel.app/severance?tab=lease`
  1. Paste a file with one Louisiana well and no Texas well: the fourth card reads "not held" with an "i"; hover it.
  2. "Try the sample (fictional wells)": the card keeps its figure, USD 73.80, and the totals are part A's.
  3. Paste a Texas gas well with a September 2026 row at 60 Mcf a day: its flag reads "no certified price for 2026-09 is held in the rules file (its latest is 2026-08): no credit computed".

## Data request rows

| Requested (UTC) | Session | Table or file | What, exactly | Source | State |
|---|---|---|---|---|---|
| 2026-11-16 | 7511 | `site/data/severance_rules.json` | With session 7502's re-reading of the rules: add, as cited passages, who bears each state's production tax (the operator, the first purchaser, each interest owner in proportion) for Texas, Louisiana and New Mexico, and Louisiana's oilfield site restoration fee with its rates as a fee of Louisiana oil and gas. The page then says whose a share's tax is, and the Lease tab's fees card holds a Louisiana figure | Texas Tax Code chapters 201 and 202 (the files session 41 read); Louisiana's severance tax statutes (La. R.S. Title 47, with 47:633 already read) and La. R.S. 30:87, legis.la.gov; New Mexico TRD, Oil and Gas Production Taxes | requested |
| 2026-11-16 | 7511 | `eia_crude_first_purchase_prices` | Add EIA's monthly domestic crude oil first purchase price for Texas, Louisiana and New Mexico (the table holds Mars blend and North Dakota only), and put the table in the live set, so `/severance` can offer the state's price at the lease beside WTI Cushing | EIA, Domestic Crude Oil First Purchase Prices by area: the API route `petroleum/pri/dfp1` that the table's connector (`warehouse/connectors/eia_series.py`) already reads for North Dakota | requested |

## Browser read rows

| Asked (UTC) | Session | Branch | Address | What to look at | What should be seen | State |
|---|---|---|---|---|---|---|
| 2026-11-16 | 7511 | wip/7502-severance | /severance | Product gas; tick "Low-producing gas well credit"; hover and tap the "i" beside "Report period (the production month)", at 1280 and at 390 px | The hover opens, names 2026-08 and the month of the price box, stays inside the screen, no sideways scroll; the list under it is as wide as the other boxes | wanted |
| 2026-11-16 | 7511 | wip/7502-severance | /severance | The "i" beside "Monthly volume", at 390 px; then click the words "Monthly volume" | The hover stays inside the screen; a click on the words puts the cursor in the volume box | wanted |
| 2026-11-16 | 7511 | wip/7502-severance | /severance | New Mexico, no district, then "LEA JAL, district 19, suffix 2541", at 390 px | First "left out" in the figures column and the long line wraps without a sideways scroll; then 1.4863% and a link to TRD's rate table | wanted |
| 2026-11-16 | 7511 | wip/7502-severance | /severance?tab=lease | Paste a file with one Louisiana well; the fourth card and its "i"; the network panel | "not held" in the card's figure size with the mark beside it; the hover inside the screen at 390 px; no request after the paste | wanted |

## Landing request

- **Head:** the commit that holds this report on `wip/7502-severance` (its hash is in the reply to the orchestrator), on top of session 7502's stack.
- **Tests:** the table above.
- **What changes:** on `/severance`, two hovers, the certified prices' cents and New Mexico's ad valorem line; on the Lease tab, two flags' words and the fees card of a file with no Texas well. One new test file, one review file.
- **What does not:** the rules file, the arithmetic of every tax, `release.ts`, every table, every page outside the tool.
- **Snapshot:** no difference expected on the 25 addresses read as a visitor (every page is in review). With the review cookie, `/severance` differs only once a credit or New Mexico is chosen; "Every rule, with its source" is the same text today (USD 53.55 and USD 1.36 already have their cents).
- **Before landing:** a build on the landing machine: `Calculator.tsx` and `LeaseTool.tsx` now import `Tip` from `components/tool/ToolPage.tsx`, as other client components of the site do.

## Needs the key

- Nothing. No step of this read needs a model.

## Decisions made without you

- The reader is the small operator, not the mineral owner the chain file names first: the page's inputs are an operator's. The owner's question is case 5 and rows 9 to 11.
- Row 13 (the problem sets) was not fixed, for the reason at the top.
- The cases' sizes are stated, not taken from a named well: `rrc_lease_production_monthly` is internal, and the brief forbids a lease id, name or operator in a committed file.
- The internal pages were not drawn for a case; part A's four real leases stand for them.
- The method note was not edited: no rule or default changed, only words on the page.
- A scratch script (`site/scripts/_severance-read.mjs`) and its drawings stay out of git.

## For Samuel's ruling

1. **The problem sets against the calculator (row 13).** Should a month's tax be computed on the mean rounded to the cent (the calculator, and the key's own printed line) or on the mean as it comes (the key's figure)? Default taken: nothing changed; the patch is three lines and a rebuilt edition.
2. **One Mcf as one MMBtu, or 1,034 Btu a cubic foot (row 14)?** `/severance` and `/impact` differ by 3.4 percent on the same gas. Default taken: each keeps its rule.
3. **Texas's regulatory fee inside "Severance" on `/impact` (row 15)?** `/severance` says the fee is not in the tax. Default taken: left.
4. **Should the calculator's price follow the report period chosen (row 7)?** Default taken: no; the hover says the two are separate.
5. **One file, one lease (row 16)?** A file of two Texas oil leases is averaged as one. Default taken: as now.
6. **Waha (row 11).** A license would give Permian gas its own price. Default taken: Henry Hub, and the reader types the statement's price.
