# Session 3304 report (chain 200, session 5 of 13): the company pages, their files and their tracers

lab-desktop, 6 November 2026, 19:39 to 20:15 UTC. Branch `wip/3300-companies`.

## What was done

- **`warehouse/derived/companies_page.py`**: the pages' files, `site/data/companies/`: `index.json` (12,788 listed companies, 1.6 MB) and 256 shards `c/<xx>.json` (22.8 MB): each company's figures, MW by fuel, MW by year, names, public rows and held counts. No lock (nothing under `warehouse/output` is written).
- **The hold applied.** `energy_deals`, `datacenter_projects`, `datacenter_facilities` and `nyiso_interconnection_queue` are "license needed" (whole tables, no row license); the site shows nothing of a held row (the deals page's rule, `site/app/deals/Held.tsx`). So their rows, names and figures are not in the files; a company's held rows are counted by table; the 1,176 companies named only in held tables are not listed (counted in the index); the "has deals" and "has facilities" filters are shown disabled with a hover. When a permission is recorded, the next build of the files includes them and the filters turn on (`index.columns`).
- **The pages** (in review: `/companies` is `review` in `release.ts`, untouched, and `/companies/<id>` inherits it):
  - `/companies`: a GET form on the left (name search over every name, kind, segment, state, grid, has), the companies on the right, the largest footprint first, 50 a page; downloads of the filtered set (CSV, Python, Stata).
  - `/companies/<id>`: the company's facts on the left (kind, segment, parent, EIA id, HQ state, grids, seen, weakest match, its rows by table, the held counts); on the right the headline figures, MW by fuel, MW by year (operating, planned, ERCOT queue; five-year bars past 30 years; hover cards), deals by quarter (a held frame while `energy_deals` is held), every public row by table (the newest 100 shown, all in the download), its names. Downloads of its public rows (CSV, Python, Stata).
  - Every figure carries `data-n` (`company_directory|<id>|<column>`, `company_links|<link>|mw`) and its source as the hover; explanations only as hover tips.
- **Wiring:** `/companies` in the Infrastructure menu (five of eight); its old redirect to `/deals?tab=companies` removed (`next.config.ts`, `lib/tabs.ts`); the deals page's Companies tab stays. File tracing for the routes in `next.config.ts`. Tests 203 and 239 updated where they pinned the old redirect and menu.
- **Tracers:** `check_companies.py --pages` (each listed company's figures recomputed from the public links by the checker's own code: 0 failures); `site/scripts/check-companies.mjs` (a served build's figures against the files on the index and twenty company pages, the downloads, the visitor's view); `site/scripts/test-companies.mjs` (10 tests of the pure rules, pass); `tests/test_session3304_companies.py` (9 tests, pass).
- **Faults found and fixed:** the NRC writes several licensees in one field joined by `<br>`, each with "en dash Owner" or "en dash Operator": the field is now split and the words dropped (a test); an en dash in a source name (the NRC's "Northern States Power Company, en dash, Minnesota") is written as a hyphen in the page files (rule 2), the tables keep it as written. The three tables are rewritten with the fix by `runs/c200/write_table2.sh` (waiting on the data lock at the session's end).

## Not done in this session

- **The build and the browser checks**: the build lock was held by another window's landing gate (from 19:40 UTC) and my type check waits for it; the data lock by the fourth window's session 3402.

## Decisions made without you

- The license hold governs the company pages over the prompt's "has deals" and "has facilities" filters (disabled while held).
- The page files are committed (23 MB); no daily rebuild is scheduled yet (queue/next/201's sessions).
- A waiting write of mine could not be stopped (the tool refused to stop its processes), so a placeholder file in main made it stop by its own guard; `write_table2.sh` waits for that, removes the placeholder, and under the lock waits while main's metadata files hold another writer's uncommitted change.

## For Samuel's ruling

- A permission or a row license for `energy_deals` and the datacenter tables would open the deal and facility parts of the company pages and all of `/capital`.

## Cost

- No model call. USD 0.00.
