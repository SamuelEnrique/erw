# The bill explainer (`/learn/bill`): review of 13 October 2026

Energy Research Warehouse (ERW), session 261. Read and used end to end on a local production build of `origin/main` (`811328fe`), at 1280 and 390 px: the five default bills, each bill built, a line opened, no use at all, an emptied field, and two shares past 100 percent. Screens: `bill/before/` (20) and `bill/after/` (22: the same list and the bill after Reset).

## What it is, and for whom

- Five real home bills built line by line from the utilities' own tariffs: PG&E, SCE and SDG&E in California; a home in Oncor's and in CenterPoint's area of Texas. Each line opens to what it is, why it exists and the tariff passage behind its rate. Under the bill, a bar: how much of it is the wholesale price of energy.
- For whom: a student first, and anyone with a bill in hand. An investor learning gets the one fact that matters to them here: retail is not wholesale. Not for an operator.
- **What it teaches, in one line:** between a tenth and a quarter of a home's bill is the power itself; the rest is wires, fixed charges and programs. (Today: 10.26, 10.28 and 7.43 percent on the three California bills, 24.88 percent on both Texas bills.)

## Can a first-time user finish it without help?

- **Yes, for the reading**: the five default bills are at the top, already worked.
- **Yes, for building a bill**, with three places to stumble:
  1. The California inputs are a utility's own words with no help beside the field: "Baseline territory (default T, San Francisco)", "Income tier (default 3: no CARE or FERA discount)". The glossary that explains "baseline allowance" is at the foot of the page, after the bill.
  2. SDG&E asks for "Your baseline allowance for this bill, kWh (on your SDG&E bill)". A learner without a bill leaves it at 0 and gets no credit: the SDG&E total (310.97) is then not like the other two California totals, which carry their credit. The page says so, in the small print of the default card.
  3. Until this session there was no way back to the defaults but reloading the page.
- No dead end, no crash on any input tried.

## Bugs, dead ends, numbers, layout

Numbers: `check-values.mjs` on `/learn/bill`: **18 of 18 match** (each bill's total, its wholesale dollars and share, and the month's wholesale price). The wholesale reference is September 2026, the latest complete month: 44.85 USD/MWh (NP15), 38.52 (SP15), 39.50 (ERCOT). No wrong number found against the tables. The tariff rates themselves were read on 30 September and 1 October 2026, as the page says; they were not read again today (no pull in this session).

| # | What | Where | Fixed here |
|---|---|---|---|
| 1 | **No Reset.** Five bills, up to six inputs each, and no control to put them back | `before/01-default-desktop.png` | yes |
| 2 | **Session numbers shown to the reader**: the PG&E bill's note said "since session 49 the wholesale reference is the NP15 zone ... Until session 48 it was CAISO's main hub, SP15" | `before/02-bill-1-desktop.png` | yes |
| 3 | The glossary's first term said "Both tariffs charge by it": there have been five since session 52 | `before/01-default-desktop.png` | yes |
| 4 | **The three California defaults are not the same season.** PG&E and SDG&E are summer bills; SCE is a winter bill ("the season on 2026-10-01"). The cards stand side by side as if comparable, and on 13 October PG&E's summer (June to September) is over | the default cards | no: the defaults are the answers of two problems |
| 5 | Two shares that add to more than 100 percent (SCE, SDG&E) are warned about and billed all the same, with a negative off-peak quantity: 80 and 40 percent gave a total of $272.15 | `before/10-shares-past-100-desktop.png` | no: clamp or refuse is a choice |
| 6 | A credit's rate is written "$-0.00857" when its line is opened (the Recovery Bond Credit of the PG&E bill) | the PG&E bill, opened | no: small |
| 7 | At 0 kWh, "Per kWh, all in" is blank; an emptied field is read as 0 without a word | `before/08-zero-kwh-desktop.png`, `09-emptied-field` | no: small |
| 8 | The glossary's ten terms cite PG&E and Oncor only, though three more utilities are on the page | `before/01-default-desktop.png` | no: words |
| 9 | Taxes and local fees are left out. The page says so once, in grey, in the second paragraph | the same | no: a scope choice |
| 10 | In the menu the page is under Economics, not Games, and nothing on it links to the problem set that uses it | `site/lib/pages.ts` | no: outside this session's files |

Not broken: no page error, no sideways scroll at 390 px, the five bills fit a phone, all five of the site's own links answer (two by redirect), no "NaN" at 0 kWh or with an emptied field.

## Against the brand (`docs/brand.md`)

The one item of the four that already wore the brand before this session (`<Brand>`).

- Holds: white page, serif titles, one dark rule above the total, figures right-aligned in mono, links underlined, cardinal for the chosen bill and the wholesale bar only.
- Off, small (measured on the built page):
  - the "written, cited" chip is 10 px, three times on the page; the brand's smallest text is 12 px. (Its capitals and letter-spacing are already put right by the brand's stylesheet.)
  - section 7 of the brand asks for each default in grey with its source beside the field, and a reset named for the field. Here the default is inside the label, and the reset added today is one for the whole bill.

## Henry's review and Kelsey's conversation

- **Henry:** his ten questions are about the battery game. None touches this page.
- **Kelsey's conversation of 5 October:** nothing of it is in the repository. Needs Samuel: what it asked of the bill explainer, if anything.

## Done for real users

| # | What | Effort |
|---|---|---|
| 1 | Samuel's ruling on the season of the California defaults (README, question 9), then one change to `site/data/bill_rules.json` and the two problems that read it | S |
| 2 | The tariffs read again and dated, with a line on the page saying when they are next read; a rate change is the one way this page goes stale without anyone seeing | M |
| 3 | Help beside each California field: a line under "Baseline territory" and "Income tier", and SDG&E's allowance by climate zone so that a learner without a bill gets a credit | M |
| 4 | Shares past 100 percent refused or clamped (README, question 10) | S |
| 5 | The brand's small breaks: the 10 px chip, the defaults and resets by field | S |
| 6 | The menu: under Games beside the problem sets, and a link each way between this page and "Prices and your bill" | S |
| 7 | A real bill tried against it: one PG&E and one Oncor bill, line by line, and the differences written on the page (taxes, fees, the retailer's own charges) | M |
| 8 | The release line in `site/lib/release.ts` set to `live`, with rule 8's snapshot | S |

## Fixes made on the branch

1. "Reset this bill to its defaults" under the inputs: it puts the chosen bill back and leaves the other four as typed (`BillCalc.tsx`).
2. The PG&E note no longer names sessions 48 and 49 (`site/data/bill_rules.json`: a note's words, no rate).
3. The glossary says "All five tariffs charge by it".

No rate, no default and no total is changed: the 18 checked values are the same before and after.
