# Session 7502 report: the severance tool at the done line (chain 304, part A)

16 November 2026, samueloldlaptop (code role), unattended. Worktree `erw-7502`, branch `wip/7502-severance`, not pushed. Model spend: USD 0.

## At the top

- **No figure of the arithmetic is wrong.** 612 of 612 figures of the calculator, the Lease tab and the internal real-lease page are inside half the page's last shown digit.
- **Two site faults found and fixed, each with a test:**
  - the calculator's default price could be a part-month's mean named as the month's, when the price table runs more than about two weeks behind (not the case today);
  - the New Mexico district list showed another district's name after a reader chose the second of three pairs that share a rate (the tax was right).
- **One thing the page shows that is out of date:** it calls August 2026 the latest certified Texas price. The Comptroller has published September 2026 (oil USD 48.59, no credit; gas USD 1.23, 100 percent credit). Not fixed here: the rules file is the data machine's to re-read (faults row 2).
- **Not finished:** the refund finder (`/severance/finder`) is not replicated. Its three files are not on this machine (faults row 4).
- **Not run:** no site build (this machine cannot). The changes to `page.tsx`, `Calculator.tsx`, `Decisions.tsx` and `lib/leaseprices.ts` are held by node drawing the components, by the tests, and by a narrow type check: `tsc --noEmit` on those four files and what they import, with the site's own settings less Next's plugin, exit 0, no message (`runs/7502/tsc.out`). That is not a build: the landing machine's build is the first whole one.
- **Said plainly:** the replication was written by a session that had also read the page's code. It is in Python, in its own words, from the note and the rules file, and the note was completed first where it did not say enough.

## The five parts

- **The method note** (`docs/methods/severance.md`): completed, 111 lines added under "The tool as a reader meets it", no line removed. The views; how to read the rules file; the eight steps of a figure; the default prices; the lease file; the real-lease page; the 14 choices with default, source and where each is changed; the cross-check.
- **The replication** (`replication/severance/`):
  - `replicate.py`, standard library only; `cases.json` (46 named cases: the default, every state and product at the base rate, every rule at its defaults, 14 specials); `sample_lease.csv` (the page's own sample download); `page_figures.json` and `.csv`; `rows/.gitignore`.
  - The page's side: `site/scripts/severance-figures.mjs` runs the page's own functions (`compute`, `parseLease`, `analyzeLease`, `bestTicks`, `parseRrc`, `leaseCsv`, `latestMonthMean`, `monthMeans`) on the same rows.
  - As printed: `612 of 612 figures inside half the page's last shown digit; 0 named; 0 differ; 37 of 37 word keys the same (rules 2026-09-30.2, drawn at 2026-11-16T12:00:00.000Z)`.
  - What the 612 are: 2 default prices with their day counts; 46 calculator cases (gross, taxable, each tax line, base, with, savings, fees, the stated rate); the rule list's counts and certified prices; the sample lease (9 wells, 31 lines, 9 "may qualify" rows, before and after "Tick the best"); the county's counts and four real leases (totals only).
  - Real leases are named by the rule that picks them (A to D), never by id, name or operator. `rrc_lease_production_monthly` is internal: no row of it is in git.
  - `replicate.do`: six lines for the five headline figures, expected values at its top. Not run (no Stata here); its Python mirror (`--headline`) printed the same values.
- **The cross-check** (`replication/severance/crosscheck.py`, `crosscheck.json`; robots and terms of each host read first): the table is under "For the pack".
- **The decisions block** (`site/app/severance/Decisions.tsx`, mounted under both tabs): 14 choices, each with its default and source on hover, closed to start, no grey note. Every choice the calculator makes was already changed in place (the price box, the completion list, the deduction boxes, the district list, the report period, the ratio), so no new input was needed; the block says where.
- **The faults** (`docs/reviews/severance-faults-2026-11-16.md`): 8 rows. Site fixed 2; data machine 3; rulings 3.

## Tests

Command, one file at a time: `.venv\Scripts\python.exe -m unittest tests.<file>` with `ERW_SPEND_CAP_USD=0`, output to `runs/7502/tests/`.

| File | Tests | Result |
|---|---|---|
| `test_session7502_severance` (new) | 14 | pass |
| `test_session40` (the calculator's 26 hand-computed cases) | 3 | pass |
| `test_session45` (the lease tool) | 6 | pass |
| `test_session239` (the tabs, the promise) | 21 | pass |
| `test_session282` | 5 | pass |
| `test_session334` | 4 | pass (it failed once, on my first placing of the fold after the downloads: it holds the downloads as the last thing of the sheet, so the fold went above them) |
| `test_session46` | 5 | pass, 2 skipped by their own rule |
| `test_session49` | 23 | pass, 7 skipped |
| `test_session57` | 7 | pass, 3 skipped |
| `test_session371` | 10 | pass |
| `test_session203`, `242`, `248`, `408`, `53`, `5160`, `5162`, `5171` | 15, 12, 13, 7, 6, 8, 9, 9 | pass |

- `node --import ./scripts/tsx-register.mjs scripts/test-severance-page.mjs`: 21 of 21 passed.

## What to review

- `https://erw-flame.vercel.app/severance` (in review: open it with the review cookie).
  1. The price box shows the latest complete month's WTI mean; the line under it names the month and its days. Tax at the base rate for 1,000 bbl is 4.6 percent of volume times that price.
  2. Scroll down to just above the downloads: "Decisions on this page (each with its default and its source on hover)". Open it: 14 lines. Hover or tap an "i": Default and Source.
  3. State: New Mexico. In the district list choose "RIO ARRIBA, district 53, suffix 3920". The box keeps that name (before: it showed suffix 3910). The ad valorem line shows 1.2395%.
  4. "Reset to the defaults": Texas, oil, 1,000, no district.
- `https://erw-flame.vercel.app/severance?tab=lease`: "Try the sample (fictional wells)": base tax USD 114,457.19, potential savings USD 18,942.53, fees USD 73.80 (the sample's months are June to August 2026, so these hold while those months' prices do). The same fold is above the downloads.
- `https://erw-flame.vercel.app/data/methods/severance`: the new section at the end.

## For the pack

- **What Samuel signs:** the calculator and the lease tool compute what the cited rules say, to the cent, for Texas, Louisiana and New Mexico; the rates equal the publishers' pages as read on 16 November 2026; the tool is an estimate for education and planning, not tax advice, and not a forecast of a state's collections.
- **The five choices that matter most:**
  1. The price is a hub price, not the value at the well. Default: the latest complete month's mean, WTI Cushing or Henry Hub. Source: EIA daily spot prices.
  2. One Mcf is priced as one MMBtu. Default: 1 to 1. Source: a choice of session 40.
  3. A Texas low-producing credit follows the Comptroller's certified price (2005 dollars), never the price typed. Default: the latest period held, August 2026. Source: the Comptroller's pages; Tax Code Secs. 201.059(b), 202.058(c).
  4. One reduced rate a well and month; only Texas's oil lease credit stacks. Default: none ticked. Source: the Comptroller's pages.
  5. Deductions only where the rule states them. Default: 0. Source: La. R.S. 47:633; New Mexico TRD.
- **The cross-check:**

| What | Ours | Theirs | Publisher, document, date | Difference | Why |
|---|---|---|---|---|---|
| Texas rates and fees (6 figures) | 4.6, 7.5, 4.6, 2.3 percent; USD 0.00625, 0.000667 | the same | Texas Comptroller, Crude Oil and Natural Gas Production Tax pages, read 16 Nov 2026 | 0 | |
| Texas certified prices, Jan 2025 to Aug 2026 | 20 periods, oil and gas | the same 20 | Texas Comptroller, low-producing pages, read 16 Nov 2026 | 0 | |
| Latest certified period | August 2026 | September 2026 | the same | one period behind | the file was read on 30 Sep 2026 |
| Louisiana rates and thresholds | the rules file | the statute's words | La. R.S. 47:633, legis.la.gov, read 16 Nov 2026 | none | |
| Texas oil tax, fiscal 2025 | USD 6,621,844,278 | USD 5,383,668,225 | Texas Comptroller, Historical All Funds Revenue; EIA production and first purchase price (released 30 Oct and 2 Nov 2026) | +23 percent | condensate, enhanced recovery, exempt royalty, cash timing: not measured |
| Texas oil tax, fiscal 2026 | USD 7,175,971,817 | USD 5,876,551,070 | the same | +22 percent | the same |
| Texas gas tax, fiscal 2025 and 2026 | USD 2,749,852,795; 3,531,268,715 | USD 2,479,282,624; 2,434,406,070 | the same workbook; EIA marketed production | +11, +45 percent | Henry Hub is not a Texas well's price; reduced rates and credits; not measured |
| New Mexico rates | TRD's table | none to stand against | | | TRD's page states no rate in words |

- **The Stata commands** (from `replication/severance/`, after `python replicate.py --tables DIR --headline` has written `rows/spot_slim.csv`): `do replicate.do`. It should print:
  - `default oil price, WTI Cushing, mean of 2026-10 (USD per bbl): 102.07`
  - `default gas price, Henry Hub, mean of 2026-10 (USD per MMBtu): 2.99`
  - `Texas oil, 1,000 bbl, tax at the base rate (USD): 4695.22`
  - `Texas gas, 10,000 Mcf, tax at the base rate (USD): 2242.50`
  - `Louisiana oil, 1,000 bbl, well completed before July 1, 2025 (USD): 12758.75`
  - `New Mexico oil, 1,000 bbl, no district chosen (USD): 7287.80`
- **The rulings, in plain words** (each with the default taken): under "For Samuel's ruling".

## Data request rows

| Requested (UTC) | Session | Table or file | What, exactly | Source | State |
|---|---|---|---|---|---|
| 2026-11-16 | 7502 | `site/data/severance_rules.json` | Re-read the rules. Add the Texas certified prices published since 30 September 2026: September 2026, oil USD 48.59 per barrel (not eligible), gas USD 1.23 per Mcf (100 percent credit), and any later period out of an HTML comment. Read whether TRD has published a New Mexico rate table from 1 September 2026 and, if so, take its rates. New version; rerun `warehouse/derived/severance_screen.py` and the `/impact` tax rules on it; then `python replication/severance/replicate.py --tables warehouse/output --write` | comptroller.texas.gov/taxes/crude-oil/low-producing-leases.php and /taxes/natural-gas/low-producing-wells.php; tax.newmexico.gov | requested |
| 2026-11-16 | 7502 | `severance_screen_summary.json`, `severance_screen_flags.csv.gz`, `rrc_lease_production_statewide` | The refund finder's replication, on the machine that holds the three files: the summary's totals (statewide, by rule, by county, by operator, the largest leases) recomputed from the flags file, N of N, and `node site/scripts/test-finder.mjs` run | warehouse/derived/severance_screen.py | requested |

## Browser read rows

| Asked (UTC) | Session | Branch | Address | What to look at | What should be seen | State |
|---|---|---|---|---|---|---|
| 2026-11-16 | 7502 | wip/7502-severance | /severance | The fold "Decisions on this page" above the downloads; hover and tap an "i"; at 390 px | Closed to start; 14 lines; each tip shows Default and Source, stays inside the screen at 390 px, no sideways scroll | wanted |
| 2026-11-16 | 7502 | wip/7502-severance | /severance | New Mexico; choose "RIO ARRIBA, district 53, suffix 3920", then "SAN JUAN, district 06, suffix 4530" | The box keeps the name chosen each time; the ad valorem line shows 1.2395% then 1.3603%; Reset puts "Not chosen" back | wanted |
| 2026-11-16 | 7502 | wip/7502-severance | /severance?tab=lease | "Try the sample"; the network panel; the fold at the foot | No request after the sample loads; the four totals (USD 114,457.19; 114,457.19; 18,942.53; 73.80); the fold under the tool | wanted |
| 2026-11-16 | 7502 | wip/7502-severance | /severance | The price box and the line under it as the page opens | The latest complete month's mean of WTI Cushing, with its month and its count of days | wanted |

## Landing request

- **Head:** the commit that holds this report on `wip/7502-severance` (its hash is in the reply to the orchestrator). Stacked on `wip/7500-done-line`.
- **Tests:** the table above, and `site/scripts/test-severance-page.mjs` (21 of 21).
- **What changes:** `/severance` and its Lease tab gain the decisions fold; the New Mexico district list is keyed by district; the default price is read from a month's first day; the method note gains a section. New files under `replication/severance/`, `site/scripts/`, `tests/`, `docs/reviews/`.
- **What does not:** the rules file, the arithmetic (`lib/severance.ts`, `lib/lease.ts`), the internal pages, `release.ts`, every table.
- **Snapshot:** no difference expected on the 25 addresses read as a visitor (every page is in review). With the review cookie: `/severance` and `/severance?tab=lease` differ by the fold; `/data/methods/severance` by the new section.
- **Before landing:** a build on the landing machine (the first whole build of the four site files this session wrote or edited).

## Needs the key

- Nothing. No step of this tool needs a model.

## Decisions made without you

- The rules file was not edited, though September's certified prices are published: it feeds the finder's builder and `/impact`, and a new version is a re-reading of every passage. A data request row instead.
- The page's `monthMean` moved to `site/lib/leaseprices.ts` (`latestMonthMean`) so a script and a test can run it; its read now begins on a month's first day.
- The decisions block is the tool's own small component, not the shared `DecisionsBlock`: chain 303 changed the shared one on another branch, and a second edit here would conflict.
- Real leases are named by the rule that picks them; only their totals are committed. A lease id, a name or an operator is in no file.
- The publishers' files fetched for the cross-check stay in `runs/` (ignored); `crosscheck.py --fetch` gets them again.
- Louisiana's and New Mexico's collections were not set against production: no time left in the session, said in the note.
- The page's 30 older grey notes were left (faults row 6).

## For Samuel's ruling

1. **Refresh the rules now or on a clock?** The certified Texas prices come out monthly; the file is one period behind after six weeks. Default taken: one data request now; no clock.
2. **Say on the page that the base rule is a ceiling on what a state collects?** For Texas oil it runs 22 to 25 percent above collections. Default taken: said in the method note only.
3. **Move the pages' grey notes into hover tips** (30 of them), as the page standard asks? Default taken: left, counted.
4. **A lease of many wells read as one** on the internal real-lease page: keep, or divide by the RRC's well count as the finder does? Default taken: keep, as the page says.

## Seen in another tool (one line each)

- None read closely. `site/lib/decisions.ts` and `site/components/tool/DecisionsBlock.tsx` differ between this base and `origin/wip/7400-trackers` (the `def` and `source` fields): whoever lands both stacks should expect the tracker branch's version to be the one kept.
