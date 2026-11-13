# Session 1878: the company database's and the capital view's faults, fixed (chain 217, 12 November 2026)

Energy Research Warehouse (ERW). Chain 217, session 1878, samueloldlaptop, unattended, Opus 5.5. Worked in the worktree `erw-1878` on `wip/1878-companies`, from the unlanded stack head `399962a60`. No freeze checked or needed: nothing deployed, nothing pushed to `main` or a `task/` branch.

## What it did

- Fixed the 15 `open` rows of `docs/reviews/companies-faults-2026-11-11.md` (session 1877's read), copied into the branch from origin/main and marked `fixed (d50b6c30, wip/1878-companies)`:
  - **Row 1:** `/companies`, `/companies/<id>` and `/deals/capital` (each branch: the page, the unread file, the hold) are wrapped in `<Brand>`, so `app/tokens.css` applies (no colored header band, the brand's faces, a chart kept readable on a phone); the dead `bg-accent text-white` is gone from every `thead` row.
  - **Row 2:** each company figure's hover says what is actually summed or counted, by the builder's rules (`basisOf` in `site/lib/companydb.ts`): "the sum of the 6 rows of 13 neither withdrawn nor completed (6 positions)", "a count of 7 reactors it is the licensee or operator of, over 14 rows (licensee, operator or parent)", operating and planned MW with their generators and plants, owned MW, a fuel's MW.
  - **Row 3:** `plural` and `leadRows`: the lead, the fold's summary and heading, the names list, the held line, the headline tips, the index's hold tip, and both CSVs' held lines ("1 row", "1 company ... is not listed").
  - **Row 4:** `RULE_WORDS` ("EIA utility id", "reviewed alias", "name of an EIA company", "same name", "a company word added") in the names list and the Match cell's hover.
  - **Row 5:** a name more than one listed row carries (over all 12,787, not the page) gets its id after it in small mono ("EIA 61757", hover "EIA utility id 61757"; an unanchored company its own id).
  - **Row 6:** the States cell's hover holds every state, the count first; "CN" reads "CN (Canada, as EIA-861 writes it)" in the filter and the hover.
  - **Row 7:** the "Deals by quarter" frame is drawn only for a company held deal rows name (while held), or with quarters (once not).
  - **Row 8:** the MW by year chart, its legend, its card and its `<title>` keep only the series with a group above zero.
  - **Row 9:** the Seen tip names a planned generator's planned month; a last date after the file's build reads "(planned)".
  - **Row 10:** each fuel share has a hover: "mw_solar 430 of plants_mw 9,635 (company_directory)".
  - **Row 11:** `sort` in the query (`footprint`, the default and left out of the address, `operating`, `planned`, `queue`, `policy`, `name`); the column heads link to it with `aria-sort`, the form keeps it, the download and the readers carry it, the index CSV says it on an `# Order:` line, and the caption follows it.
  - **Rows 13 to 16** (`site/lib/capitalview.ts`, testable only on rows written for the test while `energy_deals` is held): `GroupedBars` gains the tone `blue` (`--chart-blue`, the brand's third series color) and the view gives each of the four types its own color, kept when one type is picked; an absent type is `null` (no bar) and the card says "none"; `BarGroup` gains optional `cards`, and each type's card line reads "1.3 USD billion; 2 deals, 1 with no USD"; `bn` writes USD 30 million "0.03" and USD 2 million "0.002"; the Seller cell says "not named"; the total line no longer sums across types (the `capital|total|usd` key goes with it; the other `capital|...` keys stay).
- Every existing key is kept: `company_directory|<id>|<col>`, `company_links|<link>|mw` and `usd` on the company page, `company_directory|company:<id>|<col>` on the index, `capital|n_rows` and the cells' keys. No new visible grey text: the added words are hovers, the id tag is ink.
- Tests: `site/scripts/test-session1878.mjs` (18 node tests, each naming its row) and `tests/test_session1878.py` (the node tests, the older `test-companies.mjs`, every rule of the committed index has its words, the pages' source for rows 1, 5 to 11 and 13 to 16, the keys, no dash). `test-companies.mjs`: two lines follow the change (the query now carries `sort`, the index CSV's plural).

## Checks, each exit read

- `node --import ./scripts/alias-register.mjs scripts/test-session1878.mjs`: exit 0, 18 of 18.
- `node ... scripts/test-companies.mjs`: exit 0, 10 tests passed.
- `pytest tests/test_session1878.py tests/test_session3304_companies.py tests/test_session3306_capital.py` and the eleven older tests that read these files or `GroupedBars` (107, 145, 162, 1855, 2201, 2203, 2204, 235, 329, 404, 584, 239), then 203: exit 0, 152 passed, 1 skipped; 15 passed. Session 2201's test pins the card's default text, so the `cards` override was written around it rather than the test changed.
- `npx tsc --noEmit` under the build lock, twice (before and after the `GroupedBars` card line was rewritten for 2201's test): exit 2 both times, 15 errors, all `PageProps`, `LayoutProps` and `@/content/*.json` of an unbuilt tree, none in these files. The second run waited about 40 minutes for a landing gate's lock (`land-435aeefc`); its first attempt was stopped by the shell's time limit while waiting, before it held the lock.
- Not run: `npm run build`, the whole suite, `check-companies.mjs` and `check-values.mjs` against a served build.

## Decisions made without you

- **Row 1 wraps in `<Brand>`, not `<Brand noUsage>`** as the faults row proposed: the three pages never carried a "sent or stored" promise (so none is lost), `/deals` wraps in plain `<Brand>`, and the index's search is sent to the server as the address, so `noUsage`'s premise ("the page's typed inputs are never sent") does not hold. The usage count of these pages is as before.
- The fourth series color is the brand's blue (`--chart-blue`, docs/brand.md "Chart series"), an existing token: no token was added or changed.
- The new node tests are in their own script rather than appended to `test-companies.mjs`, whose Python wrapper pins "10 tests passed".
- The faults file is added to the branch as on origin/main (line endings aside): merging the branch into main will meet it as an add on both sides, the branch's copy the one with the states.

## For Samuel's ruling

- Row 12 (grey notes, deals row 17) stays yours. Rows 17 to 24 stay the data machine's.
- Row 22's capital buyer count a kind, once the data machine writes it, is a code row to follow.

## To finish

- Read the built pages before landing: `npm run build`, serve, `check-companies.mjs` (its keys are unchanged), and look at `/companies?sort=planned`, a company page with a completed queue position (`nextera-energy-interconnection-holdings`), and one at 390 px (`eia-814`) for the chart's scroll inside its frame.
- Land `wip/1878-companies` through a `task/` branch with the clean-copy suite.
