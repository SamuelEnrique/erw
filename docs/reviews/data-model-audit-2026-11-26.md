# The data and methodology pages: audited as a hostile expert would

Session 10233, 26 November 2026, chain 710 (part D), the old laptop. Read as a data librarian deciding whether to catalogue the ERW, and as a researcher deciding whether to cite a table from it: someone who opens `/data` to find what the warehouse holds, under what license, where the full table is and how to cite it, and who reads the standard and the faults register to judge whether the numbers can be trusted. In the form of `docs/reviews/companies-model-audit-2026-11-26.md`.

- Nothing changed on main but this file and its folder of evidence (`docs/reviews/data-model-audit-2026-11-26/`). No table written, no lock taken, no default moved, no model called, no request to any service.
- Each finding's test is on its own branch, `wip/audit-data-<n>`. Branches that change only words are for landing (the rows at the foot); a branch whose fix would move a figure, a table's listed license or its status carries the test only and is not for landing.
- **What is audited.** Platform tool 15: `/data` (the coverage table, the pages, access, the packages, the data dictionary, the methods list), `/data/faults`, `/data/licenses`, `/data/standard` and `/data/methods/<slug>`; their lib files; the files they read (`warehouse/metadata/coverage.csv`, `sources.csv`, `license_status.csv` and its site copy, `license_verdicts.csv`, `site/data/table_verdicts.json`, `site/data/data_faults.json` and its register, `docs/datastandard.md`, `docs/coverage.md`, `docs/methods/`), and the validator the standard names. Not repeated: the companies audit's finding 3 (held counts are links), which sizes a different page.

## In short

- **The counts are right.** Every figure the five pages print was restated from the files they read, apart from the site's code: 1,332 cells of `/data`'s 111 rows (each table's sector, interval, first and last day, last run, rows, source report, license, tier, download and tools cell), "111 public tables", the 49 held tables and each publisher's count, the 119 and 10 permissive publishers, the 30 faults, 29 tables, the counts by status (16, 10, 3, 1) and by work (11, 8, 11), the 23 with a note open. Each agrees to the digit. The method list holds 611 notes in this morning's content bundle (615 with the 4 written since), every link of every note resolves (196 checked), and every derived table `/data` lists is named by a note.
- **"Every public table in the ERW" is 111 of 591 (finding 1).** 443 public tables are under the live set's `catalogue_hold` and 37 under `review_hold`, so `/data` lists 19 percent of the warehouse's public tables and says it lists all. Its "retrieval time of every row" is the header's for 7 of the 107 listed tables this machine holds (no `retrieved_at` column). Fixed in words.
- **Redivis does not hold what the page says it holds (finding 2).** "Every ERW table, full history, versioned", and "the full history of every table, and the tables not in the live set, are on Redivis"; the release list says 137 of its 594 rows are in version 1 and 402 are "not yet in the dataset: the account's storage is full". 7 of the 33 rows whose download cell is "Redivis" link a dataset whose draft does not hold the table, among them ERCOT's yearly history, which the page says is "on Redivis only". Fixed in words.
- **One page, two datasets to cite (finding 3).** The citation line says `energy_research_warehouse`; the packages' citation printed beneath it says `datapages.erw` (the Stanford organization's copy, 190 tables). Fixed in words; which one is for Samuel's ruling.
- **A row's cells contradict each other (finding 4).** 4 tables print License "public" and, in the next cell, "Not public (unsettled)": the license record has not read their publishers' terms, the packages refuse them, and v1 leaves them out. The 32 held rows print "license needed" and "unsettled" for the same table. 3 tables print Tier "derived" without the "(derived)" mark. For ruling.
- **The standard says its validator enforces what it states, and in six places it does not (findings 5 and 6).** The `x_` prefix (48 of the 55 entities and events tables here break it), the provenance header's "must" (32 of 222 name no address), the entity namespace (78 of 190), "only the series shape has a validator", a deferred vocabulary already enforced, "65 tables"; and "PJM data are internal; every other source is public" against 190 internal sources, 188 of them not PJM. Fixed in words.
- **The faults page says a failing value "is used for nothing"; 9 listed tables still use them (finding 7),** under the rule's hold for "a page open to visitors", which no page has been since 8 October. Fixed in words; applying the rule is for ruling. **The licenses page says no number of a held table is shown; `/data` prints the row counts and dates of the 32 held tables it lists (finding 8).** Fixed in words; holding them is for ruling.
- **Six branches fix words and move nothing (1, 2, 3, 5, 6, 8; finding 6's words ride on 5); four show a status, figure or data fault for ruling (7, 9, 10, 11).** Two data requests: the news index's row dated 1 December, and the nine held builds measured again on today's tables.

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/data/page.tsx` | `/data`: the lead; Coverage (the catalogue, one row a public table: sector, interval, first, last, refreshed, rows, source report, license, tier, download, the packages' calls or refusal), the tier note, the download note, the citation line; Pages (`lib/pages.ts`); Access (Redivis, the live set, the Python package); the three packages; the data dictionary (the standard's three shapes); the methods list |
| `site/lib/data.ts` (`catalogue`) | Reads the live set's `catalogue` (the anon key sees `license = 'public'` rows only) and keeps rows not marked `review` |
| `warehouse/supabase/load.py`, `live_set.yaml` | Write the catalogue from `coverage.csv`, less `catalogue_hold`; mark each row `in_live_set` yes, no or review (`review_hold`) |
| `site/lib/license.ts`, `site/data/license_status.json` | The hold: a table "license needed" from its day; its publishers in the hover |
| `site/lib/packages.ts`, `site/data/table_verdicts.json` | The packages' panels and citation; each table's verdict (public, internal, unsettled) and the refusal drawn in the tools cell |
| `site/app/data/faults/page.tsx`, `site/data/data_faults.json` | `/data/faults`: the counts, the meanings, the rule for impossible values, the table and each fault; the site copy of `warehouse/faults/faults.yaml` (built 2026-11-16T20:49:30Z, after the register's last change at 20:05 UTC) |
| `site/app/data/licenses/page.tsx`, `site/lib/licensesPage.ts` | `/data/licenses`: the held count and the publishers, the letters, the permissive publishers (`license_verdicts.csv`), then `docs/licenses.md` |
| `site/app/data/standard/page.tsx`, `site/app/data/methods/[slug]/page.tsx`, `site/lib/markdown.ts` | The standard and each method note rendered from the content bundle; a note's link to another is rewritten to its page |
| `warehouse/validate/erw_validate.py` | The validator the standard names |
| `warehouse/derived/impossible_hours.py`, `docs/methods/impossible_hours.md` | The rule the faults page states, and the nine tables it is held for |
| `docs/redivis/release-v1/tables.csv`, `release-v1-stanford/tables.csv`, `site/data/site.json` | Version 1's list for the dataset `/data` links (594 rows), the Stanford copy's (193), the Redivis address and its status line (checked 2026-09-26) |
| Read from the main copy, never written | 222 of the 708 tables' headers and first rows, and `news_index.csv` |

## How every number here was computed

- **The restatement:** `restate.py` (standard library and PyYAML) reads `coverage.csv`, `live_set.yaml`, the license files, the release lists, `sources.csv`, `faults.yaml`, `docs/methods/`, the standard and the validator's vocabulary, and writes the catalogue as the loader would write it and the anon key would read it, apart from `load.py`'s code: coverage's public rows, less `catalogue_hold`, each marked by the live set's regular expressions and `review_hold`. It assumes the loading machine holds every table, as the data machine does. `measures.py` and `measures2.py` answer one question a block.
- **The pages as drawn:** `draw_data.mjs`, run from `site/` with `register.mjs` (the site's own loaders and a stand-in for `components/Brand.tsx` and `next/navigation`), draws `/data` (its catalogue read answered from `make_catalogue.py`'s rows), `/data/faults`, `/data/licenses`, `/data/standard` (from the standard on disk) and two method pages. No request leaves the machine. `compare.py` sets each drawn cell against the restatement.
- Copies of the scripts and their printouts are in `docs/reviews/data-model-audit-2026-11-26/` (written to run from `runs/c10233/` of a worktree). No row of a held table is printed in them.
- **Not measured here:** the live catalogue itself (no request to the database), and the tables' rows against coverage on the data machine. The main copy holds 222 of the 708 tables, many restored from the archive days ago: 61 of the 104 listed tables it holds differ from coverage's count, which says this machine's copies are older, not that coverage is wrong (the loader refuses a coverage that does not describe the tables, `coverage_stale`).

## The arithmetic re-done

| Figure | The page | Restated | Gap |
|---|---|---|---|
| `/data`'s count | "111 public tables" | coverage's 591 public tables, less 443 under `catalogue_hold` and 37 loaded under `review_hold` | 0 |
| `/data`'s 111 rows, 12 cells each | table and "(derived)", sector, interval, first and last day, last run ("not recorded" for 2), rows, source report, license, tier, download (46 "Download CSV", 33 "Redivis", 32 "Held: license needed"), tools (75 calls, 36 "Not public") | the same from coverage, the hold and the verdicts | 0 in 1,332 cells. The 32 held tables' row counts are printed (finding 8) |
| `/data/licenses` | "49 tables are held from October 21, 2026"; NYISO 35, ISO-NE 30, MISO 28, then 15 news outlets and the Public Utility Commission of Texas 7 each; "119 publishers' sentences allow the ERW as it is ... 10 more allow the ERW as it is today" | 49 rows of `license_status.csv`, equal to the site copy field by field; all from 2026-10-21; all public in coverage; 280 verdicts, 129 "may be public", 119 also if commercial | 0 |
| `/data/faults` | "30 faults are recorded, touching 29 tables: 1 worked around, 3 corrected, 10 screened, 16 held as published. 23 carry a note of something not settled."; "8 held for approval, 11 open, 11 fixed"; "The register as of 2026-11-16"; 30 entries | `faults.yaml`: the same, and every field of every entry equal to the site copy | 0 |
| The methods list | 611 notes (this morning's bundle) | 615 public notes on disk (4 internal kept out by `build-content.mjs`); the 4 more are notes written today | 0 |
| The links of the method notes | 196 relative or site links | every target exists and none is an internal note | 0 |
| `docs/coverage.md` | 708 rows | the same 708 tables as `coverage.csv` | 0 |

## Each claim against the files and the code

| Claim | Where | What the files and code do | Verdict |
|---|---|---|---|
| "Every public table in the ERW." | `/data`'s lead | 111 of 591 public tables (443 `catalogue_hold`, 37 `review_hold`) | **Finding 1** |
| "with the source report and retrieval time of every row" | the lead | every table's header names its retrieval; 7 of the 107 listed tables on this machine have no `retrieved_at` column (`caiso_grid_emergencies`, `energy_deals`, `news_index`, `policy_reads`, three large-load tables) | **Finding 1** |
| "Internal tables, licensed for internal use only, are not listed." | the lead | row-level security serves `license = 'public'` only | **Right** |
| "Download CSV gives the rows the site's live set holds ... up to 500,000 rows"; a window "such as the last 35 days of prices" | the download note | `MAX_ROWS = 500_000`; `recent.days: 35` | **Right** |
| "The full history of every table, and the tables not in the live set, are on Redivis"; "Every ERW table, full history, versioned"; "The dataset holds every ERW table as an unreleased draft" (checked 2026-09-26) | the download note; Access; `site.json` | release list: 137 in v1, 402 "not yet in the dataset", 55 out; 7 of 33 Redivis links point at a draft without the table | **Finding 2** |
| "The ERCOT yearly history and the EIA-860M operating and planned generator tables are on Redivis only" | Access | the generator tables are in v1; `ercot_all_hub_prices_history` is "no longer in the draft" of the linked dataset (refused upload of 20 October) and is only on the Stanford copy | **Finding 2** |
| "Redivis dataset `energy_research_warehouse`, version v1" | the citation line | the packages' citation on the same page: "Redivis dataset `datapages.erw`" | **Finding 3** |
| A row's license | the License cell | "public" for 4 tables whose verdict is "unsettled" (the tools cell says "Not public (unsettled)"); "license needed" beside "unsettled" for 32 | **Finding 4** |
| "derived, computed by the ERW from other tables, with a method in the methods pages" | the tier note | every listed derived table is named by a bundled note; 3 tables of tier derived carry no "(derived)" mark (coverage's `derived` flag is "no") | Right in substance; the mark: **finding 4** |
| "How to cite ... each table's own line is in the release's table list" | the citation line | all 111 listed tables are in the list | **Right** |
| "`warehouse/validate/erw_validate.py` enforces the `series` rules below"; "a validator that enforces what this page states"; "Only the `series` shape has a connector and a validator today" | the standard, lines 5 to 9 | the validator checks all three shapes (since sessions 6 and 8), and does not check four rules the page states | **Finding 5** |
| "Source-specific extra columns go after the reserved ones and are prefixed `x_`" | the standard's general rules | a warning for series; not checked for entities and events; 48 of the 55 entities and events tables on this machine carry unprefixed columns (Decision 15 names `news_stories`'s `title` and `summary` itself) | **Finding 5** |
| The provenance header "must" name the organization, report, address, retrieval time and connector | the standard | the validator warns only when a file has no comment line; 32 of the 222 tables here name no `http` address in their header (20 model-extracted, 7 derived, 5 source) | **Finding 5** |
| An entity's namespace "is the `source` part of the file name" | the standard, shape (a) | not checked; 78 of the 190 series and entities tables here begin with another (`carbon_intensity_hourly`'s `eia930:`, `caiso_interconnection_queue`'s `caiso_queue:`, `eia860m_operating_generators`'s `eia860:`) | **Finding 5** |
| Deferred: "a controlled vocabulary for `variable`, `entity_type`, `event_type` and `status`, enforced by the validator" | the standard | `entity_type` and the entities' `status` are enforced since Decision 20 | **Finding 5** |
| "Session 29's consolidation ... puts the cap far away: 65 tables" | the standard | coverage holds 708 tables; the cap is 1,000 a dataset | **Finding 5** |
| "Unit strings come from a closed vocabulary ... A new unit is added here and to the validator together" | the standard's Units | the validator's 72 units are all in the standard; 14 are named only in the Decisions, not in the Units list | **Finding 5** |
| "PJM data are `internal`; every other source is `public`. A table is `internal` if any of its sources is." | the standard's License | 190 of the registry's 770 sources are internal, 188 not PJM; 49 public tables are held; `news_index` is public with internal sources by its own header line (Decision 16 (d)) | **Finding 6** |
| "A value that fails is used for nothing, and nothing is filled." | `/data/faults`, the rule | the nine tables of `impossible_hours.HELD` (all listed on `/data`) are built without the rule until a person approves | **Finding 7** |
| "Until then the pages in review that read such a table leave the affected figures out and say so." | `/data/faults` | true of `carbon_intensity_monthly` (`carbon_left_out.json`, the method's own section); the other eight not checked here | Not refiled |
| "A number read from a held table is not shown." | `/data/licenses` | `/data` prints each held table's row count (32 tables, 1,112,934 rows) and first and last day; `/data/faults` prints counts of ISO-NE's and NYISO's missing intervals | **Finding 8** |
| "A held table is not offered as a download on the site" | `/data/licenses` | the route refuses it (403) and `/data` draws "Held: license needed" | **Right** |
| "each is flagged public" | `/data/licenses` | all 49 are public in coverage | **Right** |
| The four letters and the ISO-NE draft | `/data/licenses` | each linked file exists | **Right** (whether one was sent is not in the files) |
| The rule for impossible values: a quarter from the median of the four hours around, a third to three times the grid's median, ten median absolute deviations and never under 5,000 MWh | `/data/faults` | `JUMP = 0.25`, `RANGE = (1 / 3, 3.0)`, `MADS, FLOOR = 10, 500.0` (10 x 500 = 5,000) | **Right** |
| The as-of dates | the faults register's date; each row's "Refreshed" | the register's date is its build; "Refreshed" is coverage's `last_run` (16 listed tables before 1 November, 3 before 1 October, the oldest 2026-09-26); `/data` gives no date for the catalogue itself | Right as stated; the catalogue's own date is not said (not a branch) |
| The news index's last day | the Last cell | 2026-12-01: one row, an industry event's listing dated at the event, five days after coverage was built | **Finding 9** (data) |

## What a data librarian's or a researcher's own record would hold that this does not

| Item | Size | From |
|---|---|---|
| The tables not listed, and why each is held back | 480 public tables (443 `catalogue_hold`, 37 `review_hold`) | `live_set.yaml` |
| Where each table's full history is today | release list: 137 in v1 on the linked dataset, 402 waiting for storage, 55 out; the Stanford copy 193 | the release lists |
| One dataset name and one version to cite, with a released version's date | two names, no version released | `site.json` (`released: false`) |
| A license per table that agrees with the license record | 4 public with an unsettled verdict | `table_verdicts.json` |
| The catalogue's own as-of date | none on the page | `coverage.csv` (written 2026-11-26 12:10 UTC on main) |
| Per-row provenance in every table | 7 of the 107 listed tables here lack `retrieved_at` | the tables' headers |

## Findings, largest effect first

| # | Severity | Finding | Effect | Fix | Branch |
|---|---|---|---|---|---|
| 1 | High | `/data` says it lists every public table, and every row's retrieval time | 111 of 591 public tables; 7 of 107 tables without a row's retrieval time | words | `wip/audit-data-1` |
| 2 | High | Redivis is said to hold every table's full history; 7 of 33 Redivis links point at a draft without the table | 402 of the release list's 594 not yet in the dataset; ERCOT's yearly history "on Redivis only" is not on the linked one | words | `wip/audit-data-2` |
| 3 | Medium | The page gives two dataset names to cite | `energy_research_warehouse` and `datapages.erw` | words; which to cite for ruling | `wip/audit-data-3` |
| 4 | Medium | A row's license, tools and tier cells disagree | 4 "public" rows not public by the record; 32 "license needed" rows called "unsettled"; 3 derived rows unmarked | for ruling (a listed license or status) | `wip/audit-data-7` (test only) |
| 5 | Medium | The standard says its validator enforces what it states; six rules or lines it does not, or no longer, hold | 48 of 55, 32 of 222, 78 of 190 tables here; two stale lines; 14 units outside the list | words | `wip/audit-data-4` |
| 6 | Low | The standard's license rule names PJM alone | 188 non-PJM internal sources; 49 held tables; one declared exception | words | `wip/audit-data-5` |
| 7 | Low | The faults page's rule is said to leave every failing value out; nine listed tables still use them | 9 tables; the method's measured effect (below) | words; applying it for ruling | `wip/audit-data-6`; `wip/audit-data-10` (test only) |
| 8 | Low | The licenses page says no number of a held table is shown; `/data` and `/data/faults` show counts and dates of held tables | 32 row counts and 64 dates; 3 counts on the faults page | words; holding them for ruling | `wip/audit-data-8`; `wip/audit-data-9` (test only) |
| 9 | Low | The news index's last row is dated 1 December | 1 of 20,852 rows; `/data`'s Last cell | data request | `wip/audit-data-11` (test only) |

Each finding's section, its test and its fix follow.

(The sections and the landing rows are completed below as each branch is made.)
