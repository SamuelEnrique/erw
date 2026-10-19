# Session 315 report: the Research tool, its form

19 October 2026, from 21:40 UTC, unattended, on samueloldlaptop (the code machine), the second session of the chain of 19 October, daytime (`CHAIN_OCT19B_PROMPT.md`). Branch `wip/315-research` in the worktree `erw-296`, from session 314's commit (its landing recorded below); lands on main as `task/315-research`. Model spend USD 0: no model call. No pull, no warehouse data written (the public tables' names were read from the live catalogue for the form).

## Read these first

- **The page is in the ruled order, with a reader's own form first.** `/research` opens on "Ask for an analysis": the question in the reader's words (10 to 500 characters), the tables it should read (chosen by name from the public tables of the live set, ten at most, optional) and an email for the answer; then "Or choose a finding and its inputs", session 182's flow as it was; then today's chart, this week's chart, the findings library and the archive. The form writes one row of `analysis_requests` through the server route (`POST /api/analysis`, finding `reader_question`, the three fields as its params, each bounded by the route; the database function of migration 027 bounds the whole and counts the day's requests, 24). The data machine's worker never takes such a row (`worker.py` reads `finding neq reader_question`): a person answers by email, and the row is listed with the other requests ("A reader's question"). The email is stored with the request, used for the answer alone, shown to no visitor (the list answers the internal view only), and the form says so.
- **Every figure on a card is a Num with its card.** Each callout figure and each cell of a card's table of estimates carries a check key naming the card and the figure's place in the card's own JSON (`finding|<card>|callout|<i>|before or after|<grid>`, `finding|<card>|effect|<row>|<column>|<grid>`), read by `check-values` from `site/data/findings/<card>.json`; the week's card on the page carries the same keys; today's chart carries its record's own figures (`digest_chart|<date>|<table>|<key>`). `check-values` reads 140 keys on `/research` and the two card pages added to its list (121 of the cards, 10 of today's record, and the page's older ones), 140 of 140 matching the files. No word on any card changed.
- **The section 9 rulings.** 1b: nothing changes at `/internal/findings`. 3a: the 25 percent guard stays (`RECORD_JUMP`). 5b: six of the seven plain-name drafts follow the methods notes that name their tables (status `note`, each change listed below); the seventh (`eia_retail_sales_monthly`, `retail_sales`) is named by no note and stays a draft. 6a: a card figure whose own words name NYISO or ISO-NE reads "license needed" from 21 October 2026 by the tools' rule (`lib/license.ts`, the day in `license_status.json`), the card staying; on 19 October the figures show. The cards' charts (their NYISO and ISO-NE series) are session 318's, which redraws every card chart through the shared components. 2a and 4b are session 316's.
- **"Automated Analysis" survives as the method's name only** (`docs/methods/automated_analysis*.md`); the menu, the page and its sections read Research (as session 238 left them; a test now holds it).

## What to review

In the internal view: open https://erw-flame.vercel.app/internal/open first.

1. https://erw-flame.vercel.app/research : the form. Type a question and an email, pick a table or two, press "Ask the warehouse": the request is listed under "Requests" as "A reader's question", with the question, the tables and the email; the worker leaves it. (A press is a real request, counted in the day's 24.)
2. The same page: "Today's chart", the line "The record's figures"; "This week's chart", its callouts; the library's first card, its callouts and (under "Method, the table of estimates") the table: every figure carries `data-check`.
3. `docs/brand/review-315/` (the README says what each shot shows).
4. `warehouse/analysis/plain_names.json`: the six entries with status `note` (the list of changes below); `docs/reviews/packs/research.md` ("Session 315"); `docs/methods/automated_analysis_findings.md` ("The Research tool, its form and its figures").

## The six plain names rewritten from the methods notes (ruling 5b)

| Key | Was (session 267's draft) | Now (the note) |
|---|---|---|
| `variable:eia_state_generation_monthly|net_generation` | Net generation, by state and fuel | Net generation, all sectors, by state and energy source (EIA-923): `generation_mix.md` |
| `variable:eia_retail_electricity_prices|retail_price` | Retail electricity price, by state and sector | Retail electricity price, by state and sector (EIA-861M): `price_board.md` |
| `series:cftc_cot_positions|cftc:023651|managed_money_long` | Managed-money long positions, NYMEX natural gas (CFTC Commitments of Traders) | Managed money long positions, NYMEX natural gas futures (CFTC Commitments of Traders, disaggregated, futures only): `supply_and_trade.md` |
| `variable:cftc_cot_positions|managed_money_long` | the same | Managed money long positions, futures only (CFTC Commitments of Traders, disaggregated): `supply_and_trade.md` |
| `series:storage_buildout_monthly|iso:pjm|battery_operating_mw_net_added_12m` | PJM: operating battery storage, net MW added over the last 12 months | PJM: operating battery storage added over the last twelve months, net of retirements (EIA-860M): `storage_buildout.md` |
| `variable:storage_buildout_monthly|battery_operating_mw_net_added_12m` | Operating battery storage, net MW added over the last 12 months | Operating battery storage added over the last twelve months, net of retirements (EIA-860M): `storage_buildout.md` |

Left as a draft: `variable:eia_retail_sales_monthly|retail_sales` ("Retail electricity sales, by state and sector", MWh): no methods note names the table (the scanner's note mentions its `customers` variable only).

## What was done

- `site/components/analysis/AskForm.tsx` (new); `site/app/research/page.tsx` (the form first, the tables from the live catalogue, the week's callouts and today's record's figures as Nums); `site/app/api/analysis/route.ts` (`READER_QUESTION`, the bounded fields); `warehouse/analysis/findings/worker.py` (never taken); `site/components/analysis/RequestForm.tsx` (the row's words).
- `site/components/analysis/FindingCard.tsx` (`gridOfWords`, `calloutKey`, the callouts and the table of estimates as Nums); `site/components/Num.tsx` (`finding|` keys held by grid, `digest_chart|` by table); `site/scripts/check-values.mjs` (the two families; a text figure compared as text); `site/scripts/build-content.mjs` and `site/lib/markdown.ts` (the record's `numbers`).
- `warehouse/analysis/plain_names.json` (six entries, status `note`); `tests/test_session267.py` (the status allowed, marked).
- `docs/methods/automated_analysis_findings.md` (the session's section), `docs/reviews/packs/research.md` ("Session 315", the order line), `docs/brand/review-315/`, `tests/test_session315.py` (11 tests).

## Checks

| Check | Exit | Result |
|---|---|---|
| `tsc --noEmit` (worktree), twice | 2, 0 | the first a name clash (`catalogue`), fixed |
| `eslint` on the files changed | 0 | 0 errors, 3 warnings that stood before (`check-values.mjs`) |
| Impeccable `detect` on the four page and component files | 0 | no finding |
| `tests.test_session315`, `267`, `238`, `181`, `181_worker`, `170`, `260` | 0 | OK |
| `npm run build` (worktree, under the mutex, `duty.py beat` sent) | 0 | 0 statement timeouts |
| `check-values.mjs`, `/research` (`CHECK_VALUES_PAGES=/research`, `MSYS_NO_PATHCONV=1`), four runs | 127, 127, 1, 1, 0 | the first two found no page (the page was not in the checker's list; added with two card pages), the third the text rule (a figure shown as its own raw text), the fourth the p values' format; then 140 of 140 |
| `check-analysis.mjs`, `check-routes.mjs` | 0, 0 | 279 of 279; 211 pages, 0 failed as a visitor |
| Captures at 1280 and 390, four sections, before (production) and after | | `docs/brand/review-315/` |
| Suite, clean copy, the commit pushed | 0 | the whole suite in `erw-check` at `252da1c4` (the merge with main): 4454 tests, 2 failures, both older pins on this session's files (`test_session215`'s list of the check prefixes, `test_session262`'s pack headings), fixed in `0d113977`, which changes those two files alone; at `0d113977` every test that reads either file (13 modules, 160 tests) passes in the clean copy. A second whole run at `0d113977` was stopped by the machine (low memory) with its node subprocesses, and is not restarted unattended: the chain's decision below |
| `scripts/freeze.py status` | 0 | no freeze: no `REVIEW_FREEZE` file |

## Landing of session 314 (recorded here: session 314's report is in that landing's own commit)

- Pushed `task/314-battery-chart` at `42163551` at 22:06 UTC (after the before snapshot `s314-before`, 22:06:13, taken as its own command; `freeze.py status` exit 0). GitHub's first check (run 39332561651) failed in its build step on a Google Fonts download in the runner ("Module not found: Can't resolve '@vercel/turbopack-next/internal/font/google/font'", nothing of the session's files); the failed job was rerun through the API and passed; merged as `93917764` at 22:27. Production served the new build at 22:36:05 (a new style sheet name); the after snapshot `s314-after` was taken at 22:36:26.
- Snapshot `s314-before` against `s314-after`: 25 pages, 0 differences. Expected: every page is in review. Nothing unexpected.
- `origin/wip/304-replication` was deleted after the merge (its one commit is in this landing); GitHub deleted the task branch itself.

## Landing

Recorded in session 316's report (the comparison comes after this commit).

## Decisions made without you

- **The reader's question rides the existing queue** as a request with finding `reader_question` and its fields as params: no new table, no new kind (the database function admits `run` and `roundup` alone), so no migration; the worker reads it out of its queue by name. Reversible.
- **The email is a required field** (the ruling names "an email for the answer"); the tables are optional (a reader may name them in the question). The form says what is done with the email; the terms page does not yet name it (below).
- **The figures' grid is read from their own words** (the callout's label and period, the row's measure), as the library reads a card's grids; a figure naming no grid carries "-" and is never held.
- **The cards' charts are left to session 318** for the license rule (their series are drawn by the option code the ruling moves off the canvas there); the figures on the cards and the page are held now.
- **A plain name taken from a note has its own status, `note`**, beside `label` (the code's own words) and `draft`, so session 267's test that a `label` series entry is what the code writes keeps holding.
- **Today's record's figures** are drawn under the fact as a line of checked numbers, the record's own keys in words; the fact's sentence is untouched.
- Questions skipped (Impeccable's playbooks ask them).

## For Samuel's ruling

- Whether `/terms` should name the email a reader leaves with a question (stored with the request, used for the answer alone): one sentence, yours.
- Who answers a reader's question, and in what time: the form promises an answer by email and names no delay.
- Whether the week's and today's figures should read "license needed" by the same rule when their words name a held grid (they do now, by the shared Num), or stay as the Roundup printed them.

## Files

- New: `site/components/analysis/AskForm.tsx`, `tests/test_session315.py`, `docs/brand/review-315/`, this report.
- Changed: `site/app/research/page.tsx`, `site/app/api/analysis/route.ts`, `site/components/analysis/{FindingCard,RequestForm}.tsx`, `site/components/Num.tsx`, `site/scripts/{check-values,build-content}.mjs`, `site/lib/markdown.ts`, `warehouse/analysis/findings/worker.py`, `warehouse/analysis/plain_names.json`, `docs/methods/automated_analysis_findings.md`, `docs/reviews/packs/research.md`, `tests/test_session267.py`.
- Not in git: `runs/chain_oct19/s315*`.
