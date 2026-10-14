# The bill explainer (`/learn/bill`): review of 14 October 2026

Energy Research Warehouse (ERW), session 279. Read and used end to end on a local production build of `wip/279-games` (session 261's fixes merged with `origin/main` at `eb64c7a5`), at 1280 and 390 px: the five default bills, each bill built, a line opened, no use at all, an emptied field, two shares past 100 percent, and Reset. Screens: `bill/before/` (22) and `bill/after/` (22). Session 261's review of 13 October is the base.

## What it is, and for whom

- Five real home bills built line by line from the utilities' own tariffs: PG&E, SCE and SDG&E in California; a home in Oncor's and in CenterPoint's area of Texas. Each line opens to what it is, why it exists and the tariff passage behind its rate. Under the bill: how much of it is the wholesale price of energy.
- For whom: a student first, and anyone with a bill in hand. Not for an operator.
- **What it teaches, in one line:** between a tenth and a quarter of a home's bill is the power itself; the rest is wires, fixed charges and programs. Today: 10.26, 10.28 and 7.43 percent on the three California bills, 24.88 percent on both Texas bills (the same as 13 October: the reference is still September 2026).

## Can a first-time user finish it without help?

- **Reading: yes.** The five default bills are at the top, already worked. The PG&E default totals $262.33.
- **Building a bill: yes, with two places to stumble.** The California fields use the utilities' own words with no help beside them ("Baseline territory", "Income tier"), and SDG&E's allowance defaults to 0, so its default carries no credit unlike the other two.
- **Getting back to the defaults: yes since session 261.** "Reset this bill to its defaults" put SCE's 600, 80, 40 back to 600, 20, 33.3 on both widths (`after/11-after-reset-390.png`).

## Bugs, dead ends, numbers, layout

Numbers: `check-values.mjs`: **the bill's values all match Supabase** (part of 100 of 100 on the Games pages, before and after): each bill's total, its wholesale dollars and share, and the month's price, 44.85 USD/MWh (NP15), 38.52 (SP15), 39.50 (ERCOT) for 2026-09. The tariff rates were read on 30 September and 1 October 2026, as the page says; they were not read again (no pull in this session). `site/scripts/test-bill.mjs`: every bill matches the hand-computed figures.

| # | What | Where | Status |
|---|---|---|---|
| 1 | No Reset | | fixed by 261, holds |
| 2 | Session numbers shown to the reader in the PG&E note | | fixed by 261, holds |
| 3 | "Both tariffs" in the glossary, where there are five | | fixed by 261, holds |
| 4 | **A credit's rate was written "$-0.00857"** (the PG&E Recovery Bond Credit, opened) | `before/09-emptied-field-desktop.png`, the text | **fixed here**: "-$0.00857" (`site/lib/bill.ts`, every rate in a line's detail) |
| 5 | The three California defaults are not the same season: PG&E and SDG&E summer, SCE winter, side by side in October | the default cards | open: a ruling (README question 9) |
| 6 | Two shares past 100 percent are warned about and billed all the same (80 and 40 percent) | `after/10-shares-past-100-desktop.png` | open: a ruling (question 10) |
| 7 | At 0 kWh "Per kWh, all in" is blank; an emptied field is read as 0 without a word | `after/08-zero-kwh-desktop.png` | open: small |
| 8 | The glossary's ten terms cite PG&E and Oncor only | the glossary | open: words |
| 9 | Taxes and local fees are left out, said once in grey | the second paragraph | open: a scope choice |
| 10 | The page is under Economics in the menu, not Games, and does not link to the problem set that uses it | `site/lib/pages.ts` | open: outside this session (question 14) |
| 11 | The site menu's closed dropdown measures 418 px at 390 px; the page does not scroll sideways | every 390 px screen | not the tab's files |

Not broken: no page error, no sideways scroll at 390 px, the six links of the page answer (two by redirect), no "NaN" at 0 kWh or with an emptied field.

## Against the brand (`docs/brand.md`)

The one item already in the brand (`<Brand>`). Holds: white page, serif titles, one dark rule above the total, figures right-aligned in mono, cardinal for the chosen bill and the wholesale bar only. Off, small: the "written, cited" chip is 10 px (the brand's floor is 12); the brand asks for each default in grey beside its field with a reset named for the field, and here the default is inside the label and the reset is one for the whole bill.

## Henry's review

His ten questions are about the battery game; none touches this page. Kelsey's conversation of 5 October: still nothing in the repository.

## Done for real users

| # | What | Effort |
|---|---|---|
| 1 | Samuel's ruling on the California season (question 9), then `site/data/bill_rules.json` and the two problems that read it | S |
| 2 | The tariffs read again and dated, with the next reading's date on the page | M |
| 3 | Help beside each California field, and SDG&E's allowance by climate zone so that a learner without a bill gets a credit | M |
| 4 | Shares past 100 percent refused or clamped (question 10) | S |
| 5 | The brand's small breaks: the 10 px chip, defaults and resets by field | S |
| 6 | The menu, and a link each way with "Prices and your bill" (question 14) | S |
| 7 | One real PG&E and one real Oncor bill tried line by line, the differences written on the page | M |
| 8 | The release line set to `live`, with rule 8's snapshot | S |

## Fixes made on the branch in this session

1. A negative rate in a line's detail reads "-$0.00857", the sign before the dollar (`site/lib/bill.ts`: one helper used by all 15 rate strings). No rate, default or total changed: `test-bill.mjs` passes and the checked values are the same before and after.
