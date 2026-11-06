# Session 3308 report (chain 200, session 11 of the plan): the pages at 390 and 1280, screenshots, AccessLint, check-values

lab-desktop, 6 and 7 November 2026, 22:30 to 23:58 UTC. Branch `wip/3300-companies`. A local build of the branch (`runs/c200/local_checks.py`, under the build lock, run detached; `npm ci` in the worktree: Turbopack refuses a `node_modules` junction), served on 3330 with the internal cookie.

## Found on the gate's build of session 3307 and fixed

- **The company pages scrolled to 674 px at 390** (`check-390.mjs`): the grid's columns took their content's width. `min-w-0` on both columns of `/companies`, `/companies/<id>` and `/deals/capital`.
- **The year chart's labels and bar figures collided** at 390 and at 1280 on long histories: spans of five years past 15 years (was 30), labelled "1990" with "to 94" under it, and no figure written over the bars (each group's figures are in its hover card).
- **check-companies.mjs** expected a figure on every company page; a small utility with EIA-861 rows alone has none.

## Checked on the local build of the fixed branch (`2ebd1a4b9` and its fold, below)

- `check-companies.mjs`: **194 of 194**, 1,689 figures read back equal to the files (the index under four queries, twenty company pages: the ten largest and ten drawn with seed 3306), the downloads' row counts, the visitor's in-review page.
- `check-390.mjs` on seven pages (the index twice, four companies, `/deals/capital`): **0 findings**, each 390 of 390.
- `shots-companies.mjs` (new): seven pages at 1280 and 390, full-page screenshots in `runs/c200/local/shots/` (not in git), no page wider than its window, and on Florida Power & Light's and TVA's pages the year chart's hover card answers the pointer ("1990 to 94, Operating 1,224 MW ...") and the arrow keys move it.
- **AccessLint** (`audit_live`) on the index, NextEra's page and `/deals/capital` (the pages as drawn, scripts out, tables cut to four rows, served locally for five minutes): **no violation**. Colour contrast is not judged this way (no stylesheet).
- `check-values.mjs` on the local build: 7,824 of 7,824 values match Supabase; the same three floors as on main (`/deals`, `/learn/problems/know-your-grid`, `/roundup`); the new pages carry `data-n` keys, not `data-check`, and are traced by check-companies.

## Changed after the screenshots

- **The rows fold.** Florida Power & Light's page ran to about 14,900 px with every table's hundred rows open. Each table's rows are now a closed fold under its heading ("Show the newest 50 of its 241 rows"), 50 at most, every row still in the download; the keyed figures stay in the HTML, so the tracer reads them.

## Decisions made without you

- AccessLint was run on trimmed copies served from the machine, not on the live build: its browser has no internal cookie and so sees the in-review page.

## Cost

- No model call. USD 0.00.
