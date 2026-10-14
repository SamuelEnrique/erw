# The large-load statements, public where it is safe

Energy Research Warehouse (ERW), session 255 (13 October 2026). Tables: `large_load_document_verdicts` and `large_load_public` (events, both **internal until the owner rules**). Code: `warehouse/derived/large_load_public.py`. No request was made to anyone: a verdict rests on a document's address, on its type as the statements table holds it, and on the terms session 205 read ([`docs/licenses.md`](../licenses.md)).

## The rule

The owner's, in session 255's prompt: **a public regulatory filing and an SEC filing state facts that may be republished as facts with a link; long quotation may not.**

- Session 205 gave each *table* a verdict from its publishers' terms. This gives each *source document* one, for the two large-load tables that are internal because their documents had not been read one by one: `large_load_statements` (796 statements, 301 documents) and `large_load_waits` (2,622 rows, 126 dated copies of four queues).
- A verdict is one of: **public**; **needs written permission** or **needs a paid license** (session 205's words for that publisher); **not settled** (the publisher's terms were not read, or the document is of a kind the rule does not name); **not public** (a third party's copy).

## How a document is classed

Read in this order; the first that fits decides.

| Class | How it is known | Verdict | Documents | Statements |
|---|---|---|---|---|
| Third party's copy | the statements table's own `source_flag` (a conference host's, a county's, a university's copy) | not public | 4 | 5 |
| SEC filing | the address is on EDGAR (`www.sec.gov`): an annual or quarterly report, or an earnings release or presentation furnished with a current report | **public** | 28 | 71 |
| Regulatory filing | the address is a regulator's own docket or site: 20 state commissions and boards and FERC (the list is `REGULATORS` in the code) | **public** | 101 | 287 |
| Read publisher's document | the address is the site of an operator whose terms session 205 read | ERCOT, CAISO: **public** (16 documents, 31 statements). PJM: needs a paid license (21, 73). NYISO, ISO-NE, SPP: needs written permission (18, 33) | 55 | 137 |
| Federal body's document | Bonneville Power Administration, the Congressional Research Service | not settled | 6 | 12 |
| Filed document, the filer's own copy | a commission filing, tariff filing, testimony, resource plan or SEC filing by its type, read from the filer's own site | not settled | 34 | 94 |
| Publisher's own document | anything else: a company's presentation or page, a public power body's report, a laboratory's | not settled | 73 | 190 |

- **Public: 145 documents, 389 statements.** Not settled: 113 documents, 296 statements. Permission or a license: 39 documents, 106 statements. Not public: 4 and 5.
- **ERCOT and CAISO are a third basis, kept apart.** They are neither of the two kinds the rule names. Session 205 read their terms and found "may be public" both as the ERW is today and if it sells anything; CAISO asks to be credited. Each such row says so in `public_basis`, so that the owner can rule the two kinds alone and drop these 31 by one filter.
- **SPP is not public here.** Its terms allow copying today and ask for written consent for any commercial use, and its tables are held by the ruling of 12 October 2026. SPP's own statements are public only where a regulator posts them (its status update on the Missouri commission's site).
- **A filed document on the filer's own site is not settled, though the same document on the docket would be public.** The address is what was read, and the filer's terms were not.
- **A federal body's document is not settled.** A work of the United States government is in the public domain (17 U.S.C. 105), but it is neither of the two kinds the rule names: it waits for the owner. A national laboratory's report is its contractor's, and is under "publisher's own document".
- **The Virginia commission is paused for automated requests** (`docs/methods/vascc_pause.md`). Nothing was asked of it. A link to its filing is not a request, and its 26 statements are public by the rule.

### The waits table: nothing is public

| Publisher | Copies | Rows | Verdict | Why |
|---|---|---|---|---|
| New York ISO | 30 | 486 | needs written permission | session 205's read of its legal notice: no license is conferred, all rights reserved |
| Alberta Electric System Operator (Canada) | 77 | 617 | needs written permission | its terms allow non-commercial, personal or educational use only (session 165) |
| Bonneville Power Administration | 17 | 1,514 | not settled | a federal body; its site states no terms; not one of the rule's two kinds |
| Grant County Public Utility District | 2 | 5 | not settled | its site states no terms of use (session 155) |

The page's measured waits stay what they are: aggregates only, in `site/data/datacenter/how_soon.json`.

## `large_load_document_verdicts`

Events, `event_type` `license_verdict`, one row a document: 427 rows (301 and 126).

- `source_url` the document's address; `parties` the regulator, the read publisher or the host; `status` the verdict; `document_class`, `verdict_basis` why; `of_table`; `host`; `document_title`, `document_type` as the statements table holds them; `regulator_state`; `rows` the table's rows that rest on it and `rows_public` those in `large_load_public`; `address_holds_email`; `event_date` the day of the verdict.
- **Internal.** It lists the documents of two internal tables, and 21 of the addresses hold a filer's e-mail address.

## `large_load_public`

Events, `event_type` `large_load_statement`, one row a figure a public document states: **341 rows** (250 of megawatts, 91 of a duration), from 124 documents, 67 entities in 55 groups.

| Column | What it is |
|---|---|
| `parties`, `entity_group`, `entity_type` | the entity, as the statements table names it |
| `mw`, `mw_low`, `mw_high` | megawatts (`row_kind` `mw`); a range in the two bounds |
| `duration_as_stated` | a duration (`row_kind` `wait`): the figure as written, a number and its unit with its bound ("up to", "at least", "approximately"). A figure of more than 48 characters is a clause of the document and is not copied: the field then reads "stated in words, not as a figure: see the document" (1 row) |
| `status`, `stage_class` | the stage, as one of the ERW's five classes (request or inquiry; study or engineering; financial commitment; signed service agreement; under construction or energized) or "not classed". **Not the document's words** |
| `wait_basis`, `wait_counted`, `load_scope` | the ERW's own reading of a duration: measured, expected or a general statement; whether it is a load's wait at all; whether it covers every distribution project |
| `event_date`, `event_date_basis` | the document's date |
| `document_title`, `document_type`, `page`, `source_url` | where the figure stands: the title, the page, the link |
| `public_basis` | SEC filing; public regulatory filing; publisher's terms read in session 205 |
| `regulator`, `state`, `grid` | the regulator whose docket holds the document and its state; else the states the entity serves; the grid of the page the entity is in |
| `source_flag` | the statements table's flag where the document speaks of another entity |
| `statement_id` | the row of `large_load_statements` it comes from |

- **No quoted text.** No sentence of a document; not the stage in the document's own words (`stage_as_worded`); not the kind of load, the place or the time horizon as worded; not the collecting pass's notes. What is left is a number, a date, a class, a title, a page and a link.
- **48 statements are held out though their document is public:** the address holds a filer's e-mail address as a folder name (the Kentucky commission's own public address). It is still a person's e-mail address. With them the table would hold 389 rows.
- **Do not sum** across rows or entities, as for the statements table: the entities count differently, a document often states a total and its parts, and an operator's figures hold its utilities'.
- **The places are words, not numbers.** `state` is the regulator's for a regulatory filing. For an SEC filing or an operator's document it is the states the entity serves, and `grid` is the grid of the page the entity is in, both written by hand in the code (`PLACE`, 67 entities) from each entity's own service territory.

## What it would make public (13 October 2026)

341 statements of 796, 67 entities of 113, 124 documents of 301. By basis: 239 from regulatory filings, 71 from SEC filings, 31 from ERCOT's and CAISO's own documents.

| Grid | Entities | Statements | Megawatt figures | Durations | Of them a large load's wait | Newest document |
|---|---|---|---|---|---|---|
| ERCOT | 5 | 67 | 55 | 12 | 12 (3 measured, 7 expected) | 18 September 2026 |
| PJM | 17 | 72 | 42 | 30 | 28 (20 expected, 8 general) | 7 August 2026 |
| CAISO | 6 | 48 | 25 | 23 | 3 (expected) | 24 September 2026 |
| MISO | 14 | 43 | 39 | 4 | 2 | 28 September 2026 |
| SPP | 7 | 19 | 16 | 3 | 3 (expected) | 21 August 2026 |
| NYISO | 2 | 5 | 1 | 4 | 4 (2 expected, 2 general) | 13 May 2026 |
| ISO-NE | 0 | 0 | 0 | 0 | 0 | |
| More than one grid | 4 | 13 | 9 | 4 | 4 | 30 July 2026 |
| None of the seven | 12 | 74 | 63 | 11 | 8 | 30 September 2026 |

- "A large load's wait": `wait_counted` yes and not a figure for every distribution project. 64 in all, from 30 entities: 3 measured, 45 expected, 15 general statements, 1 that says what happened and writes no duration.
- **By state** (a row once; an entity in several states under that list): Texas 88 statements from 6 entities; California 48 from 6; Virginia 26 from 7; Pennsylvania 18 from 5; Georgia 16 from 1; Indiana 16 from 5; Missouri 16 from 5; Florida 11 from 3; New York 11 from 3; Michigan 10 from 2; South Carolina 10 from 1; Nebraska 9 from 3; Wisconsin 8 from 2; Arizona 6 from 2; Kentucky 6 from 3; Colorado 5 from 1; Louisiana 3 from 3; Iowa, Maryland, South Dakota and Utah 1 each; federal (FERC) 2. Under a list of several states: FirstEnergy 17, Exelon 7, American Electric Power 3, Southern Company 1.

## What "How soon?" could then say

Today the section's block "How long a large load waits" shows stated figures for two grids, New York (the New York ISO's) and Texas (ERCOT's and Oncor's), each as a figure and a link from the internal table (`STATED_GROUPS` in `warehouse/derived/how_soon.py`). With `large_load_public` ruled public it could show, for the grid the address names:

1. **Stated waits for every grid but ISO-NE**, each a figure, who stated it, whether it is measured or expected, the document and its link: 12 for ERCOT, 28 for PJM, 4 for New York, 3 each for CAISO and SPP, 2 for MISO. PJM has no measured wait of its own on the page today; it would have 28 stated ones, none of them measured, and the page would say so.
2. **Megawatts by stage, entity by entity,** which the block does not show at all today: for PJM 42 figures from 17 entities, 4 of them at a signed service agreement and 2 under construction or energized; for MISO 39 from 14, 12 at a signed agreement. Never a total: the rows do not add.
3. **A line of who is behind it:** "17 utilities, cooperatives and commissions in PJM state a figure in a public filing", with the count of documents and the newest date.
4. **For a region outside the seven grids** (the Southeast, Arizona, Colorado), 74 statements from 12 entities, where the page has nothing today.

What it could not say from this table: anything the documents say in their own words (the stage as worded is what tells a signed agreement from a letter of intent within "not classed", 177 of the 341 rows); and nothing of New York's, Bonneville's or Alberta's measured queues.

## Checks

- The validator on both tables: pass.
- `tests/test_session255.py`: each class from its address and type; the Indiana folder; SPP held with its tables; an address with an e-mail address held out; no column of the public table is a column of the document's words; a duration capped at a figure; the verdict of every wait publisher; the counts above against the tables on the data machine (skipped where they are not).
- Every row of `large_load_public` set against its row of `large_load_statements` (`statement_id`): the entity, the megawatts, the date, the title and the address are equal in 341 of 341, and no column of the public table is one of the statements table's columns of the document's words.

## License

Both tables are **internal until the owner rules**. `large_load_public` is built so that it can be made public: facts with a link, no quotation, credit to the regulator, the SEC or the operator by the link itself (CAISO asks to be credited by name).

**Session 272: `large_load_public` is public, by the owner's ruling of 14 October 2026** ("facts with a link, no quoted text"). Its header says `License: public`; its source `erw:large_load_public` is public in `warehouse/metadata/sources.csv`; coverage flags it public though its input is internal (`PUBLIC_SELECTIONS` in `warehouse/metadata/build_coverage.py`: a public selection of an internal table, its rows and its columns chosen by the rule above); it is in the draft of the public Redivis dataset (nothing released: a person releases) and in the live set (the rule `^large_load_public$`, 341 rows, read through the `events` table with the anon key). The site reads it with `largeLoadStatements()` in `site/lib/largeloadpublic.ts`; the page that shows it is the code machine's. `large_load_document_verdicts` stays internal: it lists the documents of internal tables. The copy of `large_load_public` in the internal dataset's draft, put there in session 255, is left for a person to remove.
