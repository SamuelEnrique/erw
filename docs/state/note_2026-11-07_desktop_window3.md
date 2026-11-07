# Chain 200: the desktop's third window, 6 and 7 November 2026: the company database (tool 10) and capital flows' first view (tool 11)

lab-desktop, sessions 3300 to 3310 (the first free number at or above 3300 on origin main and every branch; the day's other chains held 3247 to 3282 and the fourth window 3400 onward). Prompt: `queue/done/200-day-6-november-desktop-window3-companies.md`; next file: `queue/next/201-day-7-november-desktop-window3-continued.md`. Branch `wip/3300-companies` (worktree `../erw-3300`). Opus 5.5.

## What landed

- **First landing, `7c0690513`** (6 November 2026, 22:41 UTC; gated commit `c67349fbb`, run 42305048694): the three tables' code, the reviewed aliases, the tracers and cross-checks, the method note and Decision 76, `/companies`, `/companies/<id>`, `/deals/capital`, their downloads, and the registrations a new table needs. Snapshots `s3307-before` and `s3307-after`: 50 differences, all the two new menu entries ("Companies in review", "Capital flows in review") on each of the 25 pages.
- **Second landing, `0ee931c1b`** (7 November 2026, 02:09 UTC; gated commit `8a0dff6c6`, run 42326558862): the pages at 390 px (`min-w-0`), the year chart's spans and labels, each table's rows folded (50 shown), `shots-companies.mjs`, the reports to session 3308. Snapshots `s3309-before` and `s3309-after`: 0 differences.
- Both gates: suite pass (8,048 tests), build pass; check_values exit 1 on floors that fail on main in every gate that evening (`/deals` held, `/learn/problems/know-your-grid`, `/roundup` 0 of 0, and from 00:00 UTC `/digest`), every value read matching Supabase (7,824 and 7,816); check-routes, check-cross-checks and check-csp then run on each gate's own build by `runs/c200/rest_checks.py`: all exit 0.

## The three tables

| Table | Rows | One row |
|---|---|---|
| `company_directory` | 13,963 | a company (11,593 with an EIA utility id; 9,229 named in two or more inputs) |
| `company_aliases` | 25,877 | a name a company goes by, by table and role |
| `company_links` | 96,964 | a company named in a row of an input (internal where the input is held for a license) |

Written under the data lock (`runs/c200/write_table.sh`, then `write_table2.sh` for the rewrite with the NRC fix), validated, archived (runs `20261106T193229Z-local` and `20261106T201532Z-local`), in coverage (tier model_extracted: their names come from the deals', datacenters' and policy actions' extraction). The license sweep makes them "license needed" (the most restrictive of their inputs' publishers): held from Redivis v1 and out of the live catalogue until uploaded. Method: `docs/methods/companies.md`. Tracers (`warehouse/derived/check_companies.py`): 0 failures over the 96,964 links and over the page files.

### Match rates by input

| Input | Links | To an EIA company | In 2+ inputs | License |
|---|---|---|---|---|
| energy_deals | 853 | 7.7% | 31.3% | internal (held) |
| datacenter_facilities | 457 | 30.4% | 99.8% | internal (held) |
| datacenter_projects | 191 | 6.3% | 100% | internal (held) |
| eia860m_operating_generators | 28,712 | 100% (by id) | 99.5% | public |
| eia860m_planned_generators | 2,361 | 100% | 97.5% | public |
| eia860_plants_annual | 17,349 | 100% | 98.8% | public |
| eia860_generator_owners | 5,680 | 100% | 35.0% | public |
| eia861_utility_data | 22,716 | 100% | 82.2% | public |
| utility_service_territories | 11,893 | 100% | 99.5% | public |
| ercot_interconnection_queue | 1,758 | 12.5% | 14.5% | public |
| nyiso_interconnection_queue | 1,604 | 13.7% | 18.1% | internal (held) |
| policy_actions | 3,178 | 0.3% | 35.6% | public |
| nrc_power_reactors | 212 | 45.8% | 72.2% | public |

## The pages

- `/companies` (index: search over every name, kind, segment, state, grid, has; the largest footprint first; downloads CSV, Python, Stata) and `/companies/<id>` (facts left, figures right; MW by fuel; MW by year with a hover card and arrow keys; deals by quarter, held; every public row keyed to its table and row with the source as a hover; downloads), and `/deals/capital` (tool 11's first view; held whole while `energy_deals` is). All in review (`release.ts` untouched: `/companies` had its line; `/deals/capital` is under `/deals`'s).
- 12,787 companies listed; 1,176 named only in held tables are not listed (counted); a held table's rows are counted on a company's page, never shown.

## The checks of the pages

- `site/scripts/check-companies.mjs` on each gate's build: 194 of 194 (1,689 figures before the fold, 1,306 after), the index under four queries and twenty company pages (the ten largest, ten drawn with seed 3306), the downloads' row counts, the visitor's in-review page.
- `check-390.mjs` on seven pages: 0 findings after the fix (674 px before). `shots-companies.mjs`: seven pages at 1280 and 390 within their windows; the year chart's hover card answers the pointer and the arrow keys. AccessLint on three pages as drawn: no violation (contrast not judged). Screenshots in `runs/c200/local/shots/` (not in git).

## The SEC EDGAR Form D estimate

One request of ten: `robots.txt` answered 403 to the ERW's named user agent (SEC asks for a contact email in it). From SEC's published pages (through a search): 10 requests a second at most; the Form D Data Sets, one ZIP a quarter, public domain. A pull: about 47 requests (robots, the page, the definitions PDF, 2015 Q1 to 2025 Q4), once the owner names a contact email. `docs/reviews/edgar-formd-probe-2026-11-06.md`.

## The thin places

- **Deals and datacenters are held**: the deal and facility parts of every company page and all of `/deals/capital` show counts only until `energy_deals` and the datacenter tables have a permission or a row license.
- **Corporate families**: EIA names operating companies; a parent only where the NRC, a deal's "X's Y" or the reviewed file says so.
- **Queue developers**: only ERCOT's (public) and NYISO's (held); CAISO, ISO-NE, MISO, SPP and Berkeley Lab name none. No company holds both a live queue position and a deal (the cross-check B is empty).
- **Headquarters**: only for owners of jointly owned generators (EIA-860 schedule 4).
- **No daily rebuild yet**: the tables and the page files are as of 6 November 2026.
- **A leftover folder**: `C:/Users/Shared/Documents/erw-land-c67349fb` (the first gate's kept worktree, unregistered; a file still held by its stopped server): safe to delete.

## Decisions made without you

- New tables beside `energy_companies` (the Thesis Builder's stays, with the deals page's Companies tab); the main table is `company_directory` (the validator's two-part rule); `company_alias` and `company_link` join the entity types (Decision 76).
- The license hold governs the pages over the prompt's "has deals" and "has facilities" filters (disabled while held).
- `/capital` became `/deals/capital` so `release.ts` stays untouched.
- The probe stopped at one request rather than put the owner's email in a user agent.
- The first landing went with check-values' three floor failures (`/deals`, `/learn/problems/know-your-grid`, `/roundup`), main's in two other gates the same evening; the gate's last three checks were run on its build by hand (all passed).
- An en or em dash in a source name is a hyphen in the page files (rule 2); the tables keep names as written.
- 76 kinds in the reviewed file (labs and hyperscalers, OEMs, lenders and investors) are a session's judgement of well-known companies, cited to the rows that name them.

## For Samuel's ruling

1. A permission or a row license for `energy_deals` and the datacenter tables (opens the deal and facility parts of the pages and all of `/deals/capital`).
2. The Form D pull (about 47 requests) and the contact email for its user agent.
3. The 76 judged kinds in `warehouse/companies/reviewed_aliases.csv`: keep, or kinds from rows only.
4. Whether `energy_companies` (the Thesis Builder's) folds into `company_directory` in time.
5. `build_coverage.py` never reads "Derived from:" for an entities table (derived stays "no" for a dozen tables).
6. `/deals`'s check-values floor (10) cannot be met while the deals are held; `/digest`'s fails each night until the day's digest is written.
7. Whether the company tables and page files join the data machine's daily run.

## The cost

- No model call under the owner's key in any session: USD 0.00 of the USD 15 allowed. Three web searches by Claude Code's own tool (session 3305).
