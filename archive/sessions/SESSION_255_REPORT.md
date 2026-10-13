# Session 255 report: the large-load statements, public where it is safe

13 October 2026, 19:10 to 19:45 UTC, unattended, on lab-desktop (the data machine), the third and last of three sessions (251, 254, 255). Branch `task/255-large-load-public`. Model spend USD 0: no model call. Pulls: none, no request to anyone. Writes, under the data lock: two new internal tables, their coverage rows, the archive and the internal Redivis draft (nothing released). No load into the live set, no page.

## Read these first

- **341 of the 796 large-load statements rest on a document that is public by your rule, from 67 of the 113 entities.** They are in a new table, `large_load_public`: the entity, megawatts or a duration, the stage as one of the ERW's five classes, the date, the document's title, page and link. No quoted text. Flagged internal until you rule.
- **Every source document has a verdict:** `large_load_document_verdicts`, 427 rows. Of the statements' 301 documents, 145 are public (101 on a regulator's own docket, 28 on EDGAR, 16 of ERCOT's and CAISO's), 113 are not settled, 39 need permission or a license (PJM, NYISO, ISO-NE, SPP), 4 are a third party's copy. Of the waits table's 126 queue copies, none is public.
- **Three rulings decide another 154 statements.** 48 rest on a public filing whose address holds a filer's e-mail address (Kentucky) and are held out. 94 rest on a filed document read from the filer's own site, not the docket. 12 are a federal body's (Bonneville, the Congressional Research Service).
- **31 of the 341 rest on a third basis, kept apart:** ERCOT's and CAISO's own documents, whose terms session 205 read as "may be public". They are neither a regulatory nor an SEC filing. One filter (`public_basis`) drops them.
- **"How soon?" could show stated waits for six grids where it shows two today, megawatts by stage where it shows none, and something for regions outside the seven grids.** Below, by grid.

## What to review

- The rule and the counts on GitHub: https://github.com/SamuelEnrique/erw/blob/main/docs/methods/large_load_public.md
  1. "How a document is classed": seven classes, each with its verdict and its counts.
  2. "`large_load_public`": the columns, and the four bullets under them (no quoted text; the 48 held out; do not sum; the places).
  3. "What it would make public" and "What 'How soon?' could then say".
- The two tables are internal: on this machine (`warehouse/output/`) and in the draft of the internal Redivis dataset. They are not in this repository, not on the site and not in the live set.
- No page changed.

## What it would make public

341 statements (250 of megawatts, 91 of a duration), 67 entities in 55 groups, 124 documents. By basis: 239 from regulatory filings, 71 from SEC filings, 31 from ERCOT's and CAISO's documents.

| Grid | Entities | Statements | Megawatt figures | Durations | Of them a large load's wait |
|---|---|---|---|---|---|
| ERCOT | 5 | 67 | 55 | 12 | 12 (3 measured, 7 expected) |
| PJM | 17 | 72 | 42 | 30 | 28 (20 expected, 8 general) |
| CAISO | 6 | 48 | 25 | 23 | 3 (expected) |
| MISO | 14 | 43 | 39 | 4 | 2 |
| SPP | 7 | 19 | 16 | 3 | 3 (expected) |
| NYISO | 2 | 5 | 1 | 4 | 4 (2 expected, 2 general) |
| ISO-NE | 0 | 0 | 0 | 0 | 0 |
| More than one grid | 4 | 13 | 9 | 4 | 4 |
| None of the seven | 12 | 74 | 63 | 11 | 8 |

- **By state** (a row once; a regulatory filing under its regulator's state): Texas 88 statements from 6 entities; California 48 from 6; Virginia 26 from 7; Pennsylvania 18 from 5; Georgia 16 from 1; Indiana 16 from 5; Missouri 16 from 5; Florida 11 from 3; New York 11 from 3; Michigan 10 from 2; South Carolina 10 from 1; Nebraska 9 from 3; Wisconsin 8 from 2; Arizona 6 from 2; Kentucky 6 from 3; Colorado 5 from 1; Louisiana 3 from 3; Iowa, Maryland, South Dakota and Utah 1 each; FERC 2. Under a list of several states: FirstEnergy 17, Exelon 7, American Electric Power 3, Southern Company 1.
- **By stage** (megawatts and durations together): request or inquiry 49; study or engineering 52; financial commitment 2; signed service agreement 27; under construction or energized 34; not classed 177.

## What "How soon?" could then say

Today the block "How long a large load waits" shows stated figures for two grids: New York (the New York ISO's) and Texas (ERCOT's and Oncor's).

1. **Stated waits for every grid but ISO-NE,** each a figure, who stated it, measured or expected, the document and its link: 12 for ERCOT, 28 for PJM, 4 for New York, 3 each for CAISO and SPP, 2 for MISO. PJM would have 28 stated waits and no measured one, and the page would say so.
2. **Megawatts by stage, entity by entity,** which the block does not show today: PJM 42 figures from 17 entities (4 at a signed service agreement, 2 under construction or energized); MISO 39 from 14 (12 at a signed agreement); ERCOT 55 from 5. Never a total: the rows do not add.
3. **Who is behind it:** "17 utilities, cooperatives and commissions in PJM state a figure in a public filing", with the count of documents and the newest date.
4. **Regions outside the seven grids** (the Southeast, Arizona, Colorado, Florida): 74 statements from 12 entities, where the page has nothing today.
- **What it could not say:** anything in a document's own words. 177 of the 341 rows are "not classed": the words that tell a signed agreement from a pipeline are the document's, and they are not in the table (ruling 4).
- **The page's New York figures would change source.** The New York ISO's own documents need written permission; New York's public rows are the utilities' filings at the Department of Public Service (5 statements).

## Checks

| What | Exit | Notes |
|---|---|---|
| `python scripts/precheck.py --what "session 255"` | 0 | six of six; on duty |
| `large_load_public.py --summary` (three times, as the rule was tightened) | 0, 0, 0 | 352, then 341 public rows: SPP's own documents came out (decision 3) |
| `lock.py run -- large_load_public.py` (twice) | 0, 0 | 427 verdicts, 341 public rows |
| `python warehouse/validate/erw_validate.py` on both tables | 0 | pass, pass |
| `lock.py run -- table_stores.py large_load_public large_load_document_verdicts` | 0 | the validator, the coverage rows (both `internal`), the archive, the draft of the internal Redivis dataset; nothing released |
| every public row against its statement | | 341 of 341: the entity, megawatts, date, title and address equal |
| `python -m unittest tests.test_session255` | 0 | 14 tests |
| `python -m unittest discover -s tests` | see "The landing" | |
| `python scripts/freeze.py status` | 0 | no freeze |

## Decisions made without you

1. **A verdict rests on the address.** A document is a regulatory filing when its address is a regulator's own docket or site (20 state commissions and boards, and FERC), and an SEC filing when it is on EDGAR. The same filing read from the filer's own site is "not settled": the address read is the filer's, and its terms were not (ruling 2).
2. **ERCOT's and CAISO's documents are public on a third basis,** session 205's read of their terms, and each row says so. Your rule names two kinds; these are neither (ruling 3).
3. **SPP's documents are not public.** Its terms allow copying today and ask for written consent for commercial use, and its tables are held by the ruling of 12 October. My first pass let them through as "may be public"; I took them out.
4. **A row whose address holds an e-mail address is held out** (48, all at the Kentucky commission). The document is public; the address is a person's (ruling 1).
5. **The stage is the ERW's class, not the document's words,** and the kind of load, the place and the time horizon as worded are left out. "No quoted text" taken strictly (ruling 4).
6. **A duration is the figure as written,** a number and its unit with its bound. One of the 91 is a clause of 84 characters and is replaced by "stated in words, not as a figure: see the document".
7. **A federal body's document waits for you.** A work of the United States government is in the public domain, but it is not one of the two kinds you named (ruling 5).
8. **The places are written by hand:** the states each of the 67 entities serves and its grid (`PLACE` in the code), from its service territory. A regulatory filing takes its state from its regulator. They are words for counting, not data from a table.
9. **The per-document verdicts are a table, not a file in git.** The repository is public; the list holds the addresses of two internal tables' documents, 21 of them with an e-mail address. The method note holds the counts.
10. **No request was made.** The Virginia commission is paused; its filings are public by the rule and nothing was asked of it. No publisher's terms page was read: the verdicts that need one are "not settled".
11. **Neither table is in the live set or the daily run.** `large_load_public` is rebuilt by one command when the statements table changes.

## For Samuel's ruling

1. The 48 statements on public Kentucky filings whose address holds a filer's e-mail address: publish them with the docket's address in place of the document's, or keep them out?
2. The 94 statements on a filed document read from the filer's own site (resource plans, tariff filings, testimony): public once the docket's copy is linked, or public as they are?
3. The 31 statements from ERCOT's and CAISO's own documents (terms read in session 205, "may be public"): in or out of the public table?
4. The stage in the document's own words (a phrase, 43 characters at the median) is left out as quoted text, and 177 of 341 rows are then "not classed". Allow the phrase?
5. The 12 statements from Bonneville and the Congressional Research Service: a federal work is in the public domain. Public?
6. `large_load_public` itself: make it public (the coverage flag, the public Redivis dataset, the live set, the page)?
7. The 190 statements on a company's or a public power body's own site, never read for terms (73 documents, 41 hosts): read their terms pages, one request each, as session 205 did for 40 publishers?
8. PJM's 73 statements (its load forecast reports) need a paid license by session 205's read. PJM is the grid with the most datacenter load: ask PJM, or take the same figures from the utilities' filings?

## Files

- New: `warehouse/derived/large_load_public.py`; `docs/methods/large_load_public.md`; `tests/test_session255.py`; this report.
- Changed: `warehouse/metadata/build_coverage.py` (two tier rules, one sector rule); `warehouse/supabase/live_set.yaml` (the two tables held out of the catalogue, their two sources held); the metadata the stores wrote (`coverage.csv`, `docs/coverage.md`, `sources.csv`, `archive_manifest.csv`, `redivis_uploads.csv`).
- On this machine, not in git: `warehouse/output/large_load_public.csv`, `warehouse/output/large_load_document_verdicts.csv`, `runs/session255/`.

## The landing of session 254

- Freeze: exit 0, no freeze. Main had moved (session 251's merge, `ceac3a77`); merged into the branch before the push.
- Before snapshot `s254-before`: 19:10:17 UTC, 25 pages, 0 failed. Pushed 19:10:24 UTC (`task/254-scarcity-signal`, `f206e443`).
- Check run 38452726907: success (its last update 19:20:32 UTC); it merged the branch as `5a44e65c` at 19:20:26 UTC. Deployment of `5a44e65c`: success at 19:22:36 UTC.
- After snapshot `s254-after`: 19:23:14 UTC, 25 pages, 0 failed. `compare s254-before s254-after`: exit 0, **0 differences in all**, on each of the 25 pages. Expected: session 254 added a builder, a rule, a test, a monthly step and a live-set rule for a table not yet loaded.

## The landing

- The before snapshot, the push, the check run, the merge, the deployment and the after snapshot with its comparison are in no committed file: this is the last session, and a commit to record them would be one more landing. They are in the closing message and in `runs/session255/landing.out`. Expected: 0 differences on the 25 pages (a builder, a rule, a test, hold lines for two tables that are not loaded, metadata; no page, no load).
