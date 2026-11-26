# The company database: the model audited as a hostile expert would

Session 10228, 26 November 2026, chain 710 (part D), the old laptop. Read as an analyst at a fund who screens companies with `/companies` and would quote a company's MW or its rank in a memo, and as a company's own investor-relations lead checking its entry. In the form of `docs/reviews/deals-model-audit-2026-11-26.md`.

- Nothing changed on main but this file and its folder of evidence (`docs/reviews/companies-model-audit-2026-11-26/`). No table written, no lock taken, no default moved, no model called, no request to any service.
- Each finding's test is on its own branch, `wip/audit-companies-<n>`. Branches that change only words are for landing (the rows at the foot); a branch whose fix would move a figure or add one carries the test only and is not for landing.
- Not repeated: the deals audit's finding 2 (the deals page's companies tab lists the held deals' parties under a decision that says nothing of a row is drawn); the companies faults of session 1878 and the review rows 17 to 23 that session 7001 fixed (the state tag, the power marketer split, the grid rule, kind and segment from public rows); the method note's own "What it cannot say". Where a measure here sizes one of them, it is cited, not refiled.
- **What is audited.** Platform tool 10 is two things: `/companies` and `/companies/<id>` (the directory, `company_directory`, `company_aliases`, `company_links`, built from the register tables and drawn from `site/data/companies/`), and the deals page's companies tab (`app/companies/view.tsx`, `CompaniesTable.tsx`, the table `energy_companies`). The page files were built on 16 November 2026 at 09:04 UTC; that build is what a visitor is served, and what is audited.

## In short

- **The arithmetic is right.** An independent restatement from the page files' links alone, by the method note's rules and the standard library, gives every figure of the default view and of three company pages (Florida Power & Light, Google, Constellation Energy Generation): 204,275 keys, every listed company's kind, segment, MW, counts, grids and dates, the default order of all 12,724, the filters' counts. 5 printed figures of these pages differ by 1 MW, because the page rounds a figure the builder already rounded to 0.1 MW (80 cells of the 12,724 rows, never more than 1 MW; not a branch). The order of states that tie is the input rows' order, not a rule (104 lists).
- **Policy actions are held, and the page still says it lists them (finding 1).** The lead and the directory line name "the policy actions' agencies"; since 13 November `policy_actions` is held, so no agency is listed (no company is of the kind "regulator"), the "Policy actions" column is 0 in all 12,724 rows, its order sorts nothing and the "Has: Policy actions" choice finds none, unmarked. Fixed in words.
- **The default order counts some plants twice, unsaid (finding 2).** The footprint adds a company's operated nameplate and its owned share of the same jointly owned generators: 106 companies, 360 generators, 62,736 MW counted twice. Without the double count 5 of the top 10 change places and PacifiCorp leaves them; 41 of the top 50 move. The column's hover says "summed, a sort key". Fixed in words; the order is for Samuel's ruling.
- **"958 rows" are 958 names in rows, and "13 tables held" means two things (finding 3).** The hold's sentence gives each held table's links as its rows: `energy_deals (958 rows)` against 583 rows, `policy_actions (3,249 rows)` against 2,127. The source line's "from 13 tables held" counts the 5 held for a license, which add nothing. Fixed in words.
- **A company is an operating company, not a group, and the page does not say so (finding 4).** Duke's 12 rows hold 60,830 operating MW (its largest row is sixth, 23,868 MW; summed it would be first); Constellation's 13 hold 32,154 MW over a row that holds the reactors and none of their MW and another that holds the MW and none of the reactors; NextEra Energy, Inc. lists 0 MW though Florida Power & Light names it as parent. 18 companies carry a parent. Fixed in words.
- **Smaller, all words.** The kind's hovers leave out "power marketer" (439 companies), and the Kind filter leaves them out too (finding 5; the filter is for ruling). The owned share's hover counts 651 owner rows that carry no MW, and "Headquarters state" is the owner's address on EIA-860's schedule 4, outside every state the company's rows name for 1,015 of 2,031 (finding 6). The companies tab's source note says its rows were found by the Thesis Builder from web sources; 541 of 562 are seeded from the deals (finding 7).
- **What an analyst's own number would hold:** group-level MW (the parent's sum), equity MW (owned share of every generator, not of jointly owned ones only), a ticker and its listing date (the directory holds none; 3 of the tab's rows name an exchange in free text), queue positions under the sponsor rather than the project company, and the figures as of the inputs' own dates (EIA-860M of September 2026; the ERCOT queue as the warehouse held it on 16 November, where coverage now holds a read of 23 November).
- **Seven branches fix words and move no figure (1 to 7); two show a figure for ruling (8, 9).** One data request: the page files rebuilt from the tables of 25 November, and the count of companies and MW that moves.

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/companies/page.tsx` | `/companies`: the lead and its hover (the hold's sentence), the filters (name, kind, segment, state, grid, has), the downloads, the count line, the table of 50 a page (company, kind, segment, states, operating, planned and queue MW, policy actions, footprint), the pages, the source line |
| `site/app/companies/[id]/page.tsx` | `/companies/<id>`: the lead, the facts (kind, segment, parent, EIA id, HQ state, grids, seen, match), its rows by table and the held counts, up to six headline numbers, operating MW by fuel, MW by year, deals by quarter (the hold's line while `energy_deals` is held), its rows (the newest 50 a table), its names |
| `site/app/companies/rows/*`, `[id]/rows/*` | The downloads: the index's rows of a query and a company's public links as CSV, with Python and Stata readers |
| `site/lib/companydb.ts` | The pure part: types, `queryOf`, `filterRows` (the order), `pageOf`, `statesCell`, `yearGroups`, `leadRows`, `basisOf` (each figure's hover), `KIND_ORDER`, the CSVs and readers |
| `site/lib/companydata.ts` | Reads `site/data/companies/index.json` and the 256 shards `c/<xx>.json` |
| `site/data/companies/` | Built 2026-11-16T09:04:33Z by `warehouse/derived/companies_page.py`: 12,724 listed of 14,033; 5 held tables and their link counts; 1,309 named only in held tables |
| `warehouse/derived/companies.py` | The builder of the three tables: mentions from 13 inputs, the normalization, the EIA id anchors, the reviewed aliases, the name groups, the kind, the segment, the parent, the footprint |
| `warehouse/derived/companies_page.py` | The page files: every figure, the kind and the segment from public links alone; a held link's row, name and figure left out, its count kept |
| `warehouse/companies/reviewed_aliases.csv` | The reviewed aliases with their evidence; 9 listed companies take their kind from it |
| `docs/methods/companies.md` | The method note (rules, columns, licenses, tracers, replication, what it cannot say) |
| `site/app/companies/view.tsx`, `CompaniesTable.tsx`, `site/lib/data.ts` (`companies`) | The deals page's companies tab: `energy_companies` from the live set, its filters (sector, niche, stage, state, confidence) and each row's details |
| `warehouse/companies/seed_from_deals.py`, `warehouse/thesis/build.py` | The two sources of `energy_companies`: 541 rows seeded from the deals' parties, 21 researched |
| `site/lib/pages.ts` | The directory line of `/companies` on the site's list of pages |
| Read from the main copy, never written | `energy_companies.csv` (562 rows, 25 November), and for row counts only `energy_deals.csv`, `datacenter_facilities.csv`, `datacenter_projects.csv`, `nyiso_interconnection_queue.csv`, `policy_actions.csv` |

The three company tables themselves (`company_directory.csv` and the rest) are not on this machine; the page files are, and they are what the pages draw.

## How every number here was computed

- **The pages as drawn:** `draw_companies.mjs`, run from `site/` with `register.mjs` (the site's own loaders and a stand-in for `components/Brand.tsx` and `next/navigation`), draws `app/companies/page.tsx` (no query, and `?has=policy`), `app/companies/[id]/page.tsx` for `eia-6452`, `eia-64846` and `eia-65506`, and the companies tab from the main copy's `energy_companies.csv` (`to_rows.py`). No request leaves the machine.
- **The restatement:** `restate.py`, standard library only, reads the shards' links and nothing the builder computed (no figure, fuel, year, kind, segment or state of a shard or of the index), and applies the note's rules. `compare.py` sets it against the index's figures for every listed company, the default order, the first page as drawn, the filters' counts as drawn and the three company pages as drawn.
- **One rule at a time and the claims:** `measures.py` (the double count, owned rows without MW, the double rounding, policy actions, held links against rows, the kind filter, families, near duplicates, the hold's reach, the HQ state, the ERCOT queue's statuses, `energy_companies`), `measures2.py` (the search's reach).
- Copies of the scripts and their printouts are in `docs/reviews/companies-model-audit-2026-11-26/` (written to run from `runs/c10228/` of a worktree). No row of a held table is printed in them: counts only.
- `nofig.py` sets each words branch's drawings against main's: every keyed figure (its key, raw value and drawn number) and every table cell.

## The arithmetic re-done

| Figure | The pages | Restated | Gap |
|---|---|---|---|
| The count line | "12,724 of 12,724 companies; page 1 of 255." | 12,724 listed (every company with a public link), 255 pages of 50 | 0 |
| The filters' counts | kind: IPP 5,143, utility 3,224, other 2,707, developer 1,192, power marketer 439 (not drawn: finding 5), operator 15, OEM 2, lab or hyperscaler 1, lender or investor 1; 10 segments (solar 3,277 ... nuclear 16); 56 states; 7 grids | the same, every one | 0 |
| Every listed company's figures (the index) | 12,724 rows: operating plants and MW, owned MW, planned MW, ERCOT queue positions and MW, reactors, policy actions, footprint, kind, segment, grids, links, first and last seen | the same | 0, except 3 footprints by 0.1 MW (the builder sums parts rounded to 0.1 MW) |
| The states of each company, most first | 12,724 lists | the same counts; 104 lists differ only in the order of states that tie (the input rows' order) | 0 in counts |
| The default order | footprint, then links, then id | the same for all 12,724 | 0 |
| The first page drawn | 50 rows: name, kind, segment, states, operating, planned, queue MW, policy actions (0), footprint | the same | 4 cells by 1 MW (double rounding: 14,425 against 14,424 and the like) |
| Florida Power & Light (`/companies/eia-6452`) | "utility, gas, in FL, TX, CA, GA. 475 public rows of 7 tables name it."; Operating 40,818 MW of 241 generators at 140 plants; Planned 969 of 13 plants; Owned share 1,148 of 5 generators; Reactors 4, 3,666 MW; MW by fuel (gas 26,891, 65.9%; solar 8,829, 21.6%; nuclear 3,914, 9.6%; storage 1,015, 2.5%; oil 166, 0.4%; other 3, 0.0%); 15 five-year groups of MW by year; rows by table; seen 1958-11-01 to 2027-10-01 (planned); match 0.90; 7 names with their counts | the same | the owned share 1,148 against 1,147 (1,147.488 rounded once; the page rounds 1,147.5) |
| Google (`/companies/eia-64846`) | "lab or hyperscaler, storage, in CA. 7 public rows of 2 tables name it; 101 held rows do too."; Operating 6 MW of 5 generators at 2 plants; solar 3 (46.7%), storage 3 (53.3%); MW by year 2021 to 2024; held: datacenter facilities 63, projects 11, deals 27; "27 rows of energy_deals name this company" | the same | 0 |
| Constellation Energy Generation (`/companies/eia-65506`) | "operator ... 25 public rows of 2 tables name it"; Reactors 21; parent Constellation Energy Corporation (NRC) | the same | 0 |

- **204,275 keys, 9 gaps, all of them rounding of 0.1 to 1 MW, and one choice the page does not draw** (`compare.out`). On all 12,724 rows the double rounding moves 80 printed cells by 1 MW (50 companies; `measures.json`, `double_rounding`): a figure a reader sees, under 1 MW, not a branch.
- **The kind and the segment** were restated from each link's own fields (EIA-861's ownership, EIA-860's sector, the queue role, the NRC role, the reviewed aliases' kind) by the note's order, written apart from `kind_for`: equal for all 12,724.
- **The published replication** (`replication/companies/replicate.py`) reads the tables, which this machine does not hold: not run. Its last result is 381,721 of 381,721 on 16 November (the method note).
- **What a visitor sees today**: the drawn pages hold no em dash.

## One rule changed at a time

Each line changes one choice and keeps every other. The base is the page files of 16 November 2026.

| Choice the pages make | The other choice | Worth | Said on the page? |
|---|---|---|---|
| The footprint adds operating MW and owned MW | leave out the owned share of a generator the company already counts whole | 360 generators at 106 companies, 62,736 MW; the first 10: 5 change places, PacifiCorp leaves for DTE Electric; the first 50: 41 move, 2 leave | no (finding 2) |
| The footprint adds owned MW at all | operating, planned and queue MW only | the first 10: 6 change places, Duke Energy Carolinas third, PacifiCorp leaves for RWE Americas; the first 50: 46 move, 4 leave | no (finding 2) |
| A company is one EIA id or one name | a group: the rows that share a parent or a name | Duke's 12 rows 60,830 operating MW (first, against Florida Power & Light's 40,818); Constellation's 13 rows 32,154; Entergy's 11 rows 29,057 and 17,893 planned; AES 14 rows 16,263; Calpine 24 rows 10,032; Vistra's 4 rows 370 | no (finding 4) |
| The Kind choices are `KIND_ORDER` | every kind the index counts | power marketer (439) offered | no (finding 5) |
| A held table adds nothing | (the hold, the owner's ruling of 12 October) | 1,309 companies not listed; 139 listed ones lose 539 links (deals 93, facilities 142, projects 14, NYISO queue 279, policy 11); every policy action | yes, the hold's sentence (its counts are links: finding 3) |
| Round to 0.1 MW in the files, then to 1 MW on the page | round once | 80 cells by 1 MW | no; not a branch |
| An owned share needs the generator in EIA-860M's operating list | (no other source of nameplate held) | 651 of 5,680 owner rows add no MW, at 337 companies | no (finding 6) |

## Each claim against the code

| Claim, or question | Where | What the code does | Verdict |
|---|---|---|---|
| "Every company the warehouse names in a public row: EIA's operators, owners and utilities, ERCOT's interconnection queue, the NRC's licensees and the policy actions' agencies" | the lead; the directory line ("the policy agencies") | `policy_actions` held since 13 November: no agency's link reaches the files | **Finding 1** |
| How one company is matched across sources | the lead's hover ("one EIA utility id where it has one, else one name as the rows write it"); the Match fact; each row's Match | an EIA id anchors every row with it (1.0); a reviewed alias (0.95); a name equal to one anchored company's (0.9); equal names (0.85); a company word added (0.7); two ids never merged | **Right as stated**. Rule 2's exception splits 8 ids (session 7001) |
| A subsidiary, a parent, a joint venture | the Parent fact; nothing on the index | a parent from the NRC's field, a deal's "X's Y" or the reviewed file, a second field; 18 listed companies have one (15 NRC, 3 reviewed), 11 linked to a listed row; a joint venture is a company of its own name (the NRC's "Energy Harbor Nuclear Generation LLC and Energy Harbor Nuclear Corp." is one row) | The parent's figures are never summed, and the index ranks operating companies: unsaid (**finding 4**) |
| Duplicates | a shared name gets its id beside it (session 1878) | 37 names carried by 74 rows, tagged; 98 groups of 202 rows agree once spaces, punctuation and legal forms are dropped, 96 of them pairs of EIA ids ("Constellation NewEnergy, Inc" and "Constellation New Energy Inc.") | **Right as stated**: two EIA ids are two companies by rule 2, and EIA keeps them apart. Not a branch |
| MW owned against operated against announced | the column heads, the headlines and their hovers | operating: nameplate of generators it operates, whole; owned: share of jointly owned generators only; planned: EIA-860M's planned generators it would operate; queue: live ERCOT positions; no announced MW (deals and facilities held) | Each **right as stated**, but the footprint adds operated and owned (**finding 2**) and an owned row with no MW is counted (**finding 6**) |
| A company's kind and segment, and who decided it | the Kind and Segment hovers; "Set by" on a company's page | rules on the rows' own fields, the reviewed file for lab or hyperscaler and OEM (9 companies), "other" where no rule applies (2,707, 21 percent) | **Right** in substance; the hovers omit power marketer (**finding 5**). No person decided a kind except through the reviewed file, and the hover says which rule set it |
| Ticker and listing data, and its date | none on `/companies`; the tab's Stage column | the directory holds no ticker, exchange or listing; 3 of the tab's rows name an exchange in the free-text stage, undated (the row's First seen is its date) | Not claimed, so not wrong; an analyst's first column is missing (below) |
| A row seeded from news against one from a register | the tab's paragraph and its source note; `/companies` | `/companies` is registers only (EIA, ERCOT, the NRC) while the news tables are held; the tab's 541 deal-seeded rows say "from deals; not yet researched" in each row, its note says the Thesis Builder found them | The note: **finding 7**. Each row: **right** |
| Held or internal rows reaching a public cell | the hold's sentence; the held counts on a company's page | the files hold no link, alias, kind basis, segment basis or parent basis from a held table (`measures.json`, `hold`: none); counts by table only; 10 of the 139 listed companies with held rows have a name no public row writes (the reviewed canonical name, "Google" among them) | **Right**: no held row reaches a cell. The counts are links, not rows (**finding 3**). The deals tab's own case is the deals audit's finding 2, not repeated |
| `company_directory` and the two other tables are "license needed" | `site/data/license_status.json`, the source line naming them | held whole because they hold the deals' and datacenters' links; the pages draw only their public links, which the hover of every figure says ("summed from the public rows of company_links") | Right in substance; the source line names three tables `/data` lists as held, and says only since this audit's finding 3 that it draws their public rows |
| The as-of date | the source line ("Built 2026-11-16"); "Seen" | the build day; each input as held that day (EIA-860M "as of September 2026" in its source line; EIA-860's owner file of 2025; EIA-861 and the territories of 2025; the ERCOT queue and the NRC's list undated in the page's sources) | Not said that the dates differ (**finding 3**) |
| "A date after the file's build is a planned month" | the Seen hover | `seenLast` marks "(planned)" when the last date passes the build day | **Right** |
| The search | "Every word typed must be in the company's name or in another name its rows give it" | the name and `aka`, which the builder cuts to six other names; no listed company has more than six (`measures2.json`) | **Right** |
| Queue MW | "ERCOT queue positions neither withdrawn nor completed" | live ERCOT positions (1,169 active links; 589 completed left out); NYISO held | **Right**. The positions sit under project companies, not sponsors (finding 4's measure: NextEra's two interconnection holding companies, 1,691 and 983 MW) |
| Reactors | "NRC power reactors it is the licensee or operator of: N MW as the NRC states them" | counted once a reactor, licensee or operator | **Right**; Florida Power & Light's 4 reactors are 3,666 MW by the NRC against 3,914 MW of nuclear nameplate in EIA-860M, as said |
| The grid | "the grids its plants' balancing authorities, its queue positions and EIA-861's RTO flags name" | the BA code, the queue's grid, an RTO flag only where the RTO serves the utility's state (session 7001) | **Right** |
| The deals by quarter | a company's page | while `energy_deals` is held, the line "N rows of energy_deals name this company" | Right in kind; N is links (finding 3's measure; per company not measured here) |

## What an analyst's or an investor-relations lead's own number would hold that this does not

| Item | Size | From |
|---|---|---|
| The group's MW | Duke 12 rows, 60,830 MW operating against its largest row's 23,868; Constellation 13 rows, 32,154; NextEra Energy, Inc. 0 MW on its own row; 18 companies with a parent | `measures.json`, `families`, `parents` |
| Equity MW (owned share of every plant) | EIA-860 schedule 4 lists jointly owned generators only: 2,047 companies with owner rows; a wholly owned plant operated by another company is in neither figure | the note; `measures.json` |
| A ticker, an exchange, a listing date, a market value | none in the directory; 3 of the tab's 562 rows name an exchange in free text, undated | `energy_companies` |
| The figures as of one date | EIA-860M of September 2026; the ERCOT queue and the NRC's list as held on 16 November; the page files 10 days older than the tables in coverage (EIA-860M read 25 November, the ERCOT queue 23 November) | coverage; the index's sources. Needs a rebuild (data request 1) |
| Queue MW under the sponsor | queue positions sit under project companies ("NextEra Energy Interconnection Holdings, LLC"); the CAISO, ISO-NE, MISO and SPP queues name no developer | the note, "What it cannot say" |
| Deals, datacenters, the NYISO queue and policy actions | 1,309 companies and 6,517 links held | the index |

## Findings, largest effect first

| # | Severity | Finding | Effect | Fix | Branch |
|---|---|---|---|---|---|
| 1 | Medium | Policy actions are held; the lead and the directory line still list the agencies; the column, its order and the "Has" choice show nothing, unmarked | every one of 12,724 rows shows 0; no regulator listed | words | `wip/audit-companies-1` (`15f65f3f3`) |
| 2 | Medium | The footprint, the default order, counts a jointly owned generator the company operates twice, unsaid on the page | 62,736 MW at 106 companies; 5 of the top 10 move | words; the order for ruling | `wip/audit-companies-2` (`0b1719d39`); `wip/audit-companies-8` (`af73f45bb`) |
| 3 | Low | The held counts are links called rows; "13 tables held" counts the 5 held for a license; the inputs' dates are not said | 958 "rows" of a 583-row table; 3,249 of 2,127 | words | `wip/audit-companies-3` (`98b9e1e0b`) |
| 4 | Low | A row is an operating or project company, not a group, and the page never says a parent's figures are not summed | Duke's 60,830 MW over 12 rows; NextEra's own row 0 MW | words | `wip/audit-companies-4` (`e5715da58`) |
| 5 | Low | The kind's hovers omit "power marketer", and the Kind choices do not offer it | 439 companies | words; the choice for ruling | `wip/audit-companies-5` (`d31fcc6be`); `wip/audit-companies-9` (`81f339980`) |
| 6 | Low | The owned share counts owner rows that carry no MW; "Headquarters state" is an address on a form | 651 of 5,680 owner rows; 1,015 of 2,031 addresses outside the company's states | words | `wip/audit-companies-6` (`8bc611e0a`) |
| 7 | Low | The companies tab's source note credits the Thesis Builder for rows seeded from the deals | 541 of 562 rows | words | `wip/audit-companies-7` (`553185f5e`) |

## 1. Policy actions are held, and the page still lists them (Medium)

- **Where.** `site/app/companies/page.tsx`: the lead, the "Policy actions" column and its order, the "Has" choice; `site/lib/pages.ts`, the line of `/companies`.
- **Why it is wrong.** Since 13 November 2026 `policy_actions` carries "license needed" (`site/data/license_status.json`, the Public Utility Commission of Texas's link policy); the page files of 16 November hold it among the five held tables (3,249 links). So no agency is listed (the index counts no regulator), every company's policy actions are 0, the order by policy actions is the footprint order, and the "Has: Policy actions" choice returns none (`index_policy` drawn: "0 of 12,724 companies match"), while the lead, the directory line and the choice say otherwise.
- **The test.** `tests/test_audit_companies_1.py`: the files hold the table as held and no company with a policy action (passes on main); the words test fails on main.
- **The fix on the branch, words only.** The lead names the agencies only while the table is not held, else says they are not listed; the column head carries a hover ("every company's count is 0 until a permission is recorded"); the choice reads "Policy actions (license needed)" and the held filters' hover says it finds none; the directory line and the method note say the same. No figure moves (`nofig.py`: 5,168 keyed figures and cells equal).

## 2. The default order counts some plants twice (Medium)

- **Where.** `site/app/companies/page.tsx`, the footprint column's hover ("operating, owned, planned and queue MW summed, a sort key"), the default order; `site/lib/companydb.ts`, the download's header; `warehouse/derived/companies_page.py`, `figures`.
- **Why it matters.** Operating MW is every generator the company operates, whole; owned MW is its share of each jointly owned generator. A jointly owned generator it also operates is in both: Florida Power & Light's St. Lucie unit 2 adds 919.2 MW of share to a unit already in its operating MW. In the files: 360 generators at 106 companies, 62,736 MW (of 261,762 owned MW in all). The method note says "a plant both operated and owned counts twice"; the page, whose first view is that order, does not. Without the double count 5 of the first 10 change places (Entergy Louisiana from seventh to fourth, Georgia Power from fourth to sixth) and PacifiCorp leaves them for DTE Electric; 41 of the first 50 move.
- **The test.** `tests/test_audit_companies_2.py`: the footprint is the four summed and Florida Power & Light's owner rows name a generator it operates (passes on main); the words test fails on main.
- **The fix on the branch, words only.** Each footprint cell's hover and the download's header say a jointly owned generator the company also operates counts twice; the method note gives the size. The order does not change.
- **For Samuel's ruling.** Default "left as it is". The other choice (`wip/audit-companies-8`, a test only): the footprint without the share of a generator the company counts whole; the effect as above. A third, operating, planned and queue MW only: 6 of the first 10 move, 46 of the first 50.

## 3. The held counts are links, and the dates are not said (Low)

- **Where.** `site/app/companies/page.tsx`: the hold's sentence (the lead's hover and the count line's), the source line, the lead's hover.
- **Why it is wrong.** `held_links` counts links, a company named in one row, and the page printed it as rows: `energy_deals (958 rows)` when the table held 583 rows (extracted 12 November), `policy_actions (3,249 rows)` against 2,127 (coverage, 25 November), `datacenter_facilities (486 rows)` against 458, `datacenter_projects (220 rows)` against 193. ("nyiso_interconnection_queue (1,604 rows)" is under the table's 1,814 because only 1,604 positions name a customer, `verify.py`.) The source line read "Built 2026-11-16 from 13 tables held": 5 of the 13 are "held for a license" in the sentence above it and add nothing; and the inputs are of different dates (EIA-860M of September 2026, the annual EIA files of 2025, the ERCOT queue and the NRC's list as last read), which nothing said.
- **The test.** `tests/test_audit_companies_3.py`: the held counts exceed the tables' rows (passes on main); the words test fails on main.
- **The fix on the branch, words only.** The sentence says links and what a link is; the source line says "from the public rows of 8 of the 13 tables it reads (5 held for a license add nothing)", each input as held that day with its own date; the lead's hover says "the warehouse's own tables". A company page's "101 held rows do too" counts links too; per company a link is nearly always a row (not measured here: the held tables' links are not in the files), so it is left.

## 4. A row is a company, not its group (Low)

- **Where.** `site/app/companies/page.tsx` (the index, its order); `site/app/companies/[id]/page.tsx` (the Parent and EIA id facts).
- **Why it matters.** The registers name operating utilities, plant operators and project companies, and the builder never sums a parent: a fund ranking "the largest" sees Florida Power & Light first while the 12 rows whose name begins "Duke" hold 60,830 operating MW; NextEra Energy, Inc. shows 0 MW; Constellation's reactors sit on "Constellation Energy Generation, LLC" (21 reactors, 0 MW) and their nameplate on "Constellation Nuclear" (23,798 MW, no parent, no reactor). The method note says so under "What it cannot say"; the page does not.
- **The test.** `tests/test_audit_companies_4.py`: Florida Power & Light names NextEra as parent, NextEra's row has no MW, Duke's rows exceed the first row (passes on main); the words test fails on main.
- **The fix on the branch, words only.** A hover on the count line ("A company, not its group"), and the Parent and EIA id hovers, say a parent's figures are not summed and a group's companies are rows of their own; the method note gives the sizes. Summing groups would need a source that states the ties, which the warehouse does not hold (no branch).

## 5. Power marketers are a kind the page does not name (Low)

- **Where.** The Kind hovers of both pages; `site/lib/companydb.ts`, `KIND_ORDER`; `page.tsx`, `opt`.
- **Why it is wrong.** Session 7001 added "power marketer" (EIA-861's retail and wholesale power marketers) to the builder's kinds; 439 listed companies have it and show it in the Kind column. The hovers list the kinds without it, and the Kind choices (the index's kinds in the order of `KIND_ORDER`, which lacks it) leave it out; an address with `?kind=power%20marketer` still filters them.
- **The test.** `tests/test_audit_companies_5.py`: the index counts 439, `KIND_ORDER` lacks it (passes on main); the words test fails on main.
- **The fix on the branch, words only.** Both hovers name power marketer and say "other" is where no rule applies; the index's hover says which kinds the choices do not offer, computed from `KIND_ORDER`, so it stays true whatever is ruled.
- **For Samuel's ruling.** Default "left as it is". The other choice (`wip/audit-companies-9`, a test only): "power marketer" in `KIND_ORDER`, and the choice "power marketer (439)" drawn.

## 6. The owned share and the owner's address (Low)

- **Where.** `site/app/companies/[id]/page.tsx`, the Owned share headline's hover and the "Headquarters state" fact; `site/lib/companydb.ts`, `basisOf`.
- **Why it is wrong.** An owner row's MW is the generator's EIA-860M nameplate times the percent owned; 651 of the 5,680 owner rows (337 companies) find no operating generator and carry no MW, yet the hover counts them ("of 5 jointly owned generators": Florida Power & Light's 1,148 MW is of 3). "Headquarters state" is the owner's address on EIA-860's schedule 4, an address on a form: for 1,015 of the 2,031 listed companies that have one it is none of the states their rows name.
- **The test.** `tests/test_audit_companies_6.py`: Florida Power & Light's 5 owner rows, 2 without MW (passes on main); the words test fails on main.
- **The fix on the branch, words only.** The hovers say a generator EIA-860M does not hold adds no MW and that the share is of jointly owned generators only; the fact reads "Owner's address state", its hover says what it is.

## 7. The companies tab's source note (Low)

- **Where.** `site/app/companies/view.tsx`, the source note under the table.
- **Why it is wrong.** "Found by warehouse/thesis/build.py from public web sources": 541 of the 562 rows (25 November) were seeded from the deals' parties by `warehouse/companies/seed_from_deals.py`; 21 were researched. The paragraph above the table says both. (That the tab shows the held deals' parties at all is the deals audit's finding 2, not repeated.)
- **The test.** `tests/test_audit_companies_7.py`: the copy in git holds more seeded rows than researched ones (passes on main); the words test fails on main.
- **The fix on the branch, words only.** The note names both sources and which rows each wrote.

## The words branches drawn and read

Each branch's pages were drawn with the site's own code (`draw_companies.mjs`): `/companies` (no query and `?has=policy`), the three company pages, and the companies tab from the main copy's `energy_companies.csv`. Each new sentence was found in the drawn text or hovers, and `nofig.py` found every keyed figure and cell equal to main's (5,168). No em dash in any drawing.

| Branch | Where the words are drawn | Read |
|---|---|---|
| `wip/audit-companies-1` | the lead; the column head's hover; the "Has" choice and its hover | pass: "The policy actions' agencies are not listed while policy_actions is held for a license."; "... so every company's count is 0 until a permission is recorded."; "Policy actions (license needed)"; "... so that choice finds none." |
| `wip/audit-companies-2` | each footprint cell's hover | pass: "... a sort key; a jointly owned generator the company also operates counts twice, whole in operating MW and for its share in owned MW" |
| `wip/audit-companies-3` | the hold's sentence; the source line; the lead's hover | pass: "energy_deals (958 links) ... a link being a company named in one of a table's rows (a row that names two companies is two links)."; "Built 2026-11-16 from the public rows of 8 of the 13 tables it reads (5 held for a license add nothing), each input as the warehouse held it that day, so a figure is as of its input's own date and the dates differ ..." |
| `wip/audit-companies-4` | the count line's new hover; Florida Power & Light's Parent and EIA id hovers | pass: "A parent's figures are not summed and a group's companies are rows of their own ..."; "... its figures are not summed with this company's, and its other companies are rows of their own."; "Another id is another company, even of the same group ..." |
| `wip/audit-companies-5` | the Kind hovers of both pages | pass: "... developer, operator, power marketer, other that the company's rows show ..."; "The choices here do not offer power marketer: such a company shows its kind in the table." |
| `wip/audit-companies-6` | Florida Power & Light's Owned share hover, its figure's hover, the address fact | pass: "... is counted here and adds no MW."; "Owner's address state ... an address on a form, not a stated headquarters ..." |
| `wip/audit-companies-7` | the companies tab's source note | pass: "Two sources: the rows marked "from deals; not yet researched" are the deals' parties, seeded by warehouse/companies/seed_from_deals.py ..." |
| `wip/audit-companies-words` (the seven merged) | every page above | pass: all 18 sentences drawn; 5,168 keyed figures and cells equal to main's |

- The seven merge onto origin/main of 26 November (`f904d2427`) with conflicts at three merges (3, 5 and 6), each two edits side by side in one paragraph or block (the lead, the method note's pages paragraph, the consts of 1 and 5, the facts of 4 and 6), resolved by keeping both: `wip/audit-companies-words` (`6a395e269`). Their tests with every test file that reads the changed files (`test_session1878`, `3304_companies`, `5160`, `7001_companies`, `239`, `282`, `319`, `329` and the 39 that read `site/lib/pages.ts`) pass on the merge: 574 passed, 23 skipped, 1 failed, `test_session156`'s node test of `/ask`, which fails the same way on origin/main (`t156_main.out`).

## Not covered, or left open

- **The three company tables.** `company_directory.csv` and the others are not on this machine: the tracers (`check_companies.py`) and the replication were not run. The audit restates the page files, which is what a visitor is served.
- **The page files' age.** Built 16 November; coverage holds newer reads of EIA-860M (25 November) and the ERCOT queue (23 November). What a rebuild moves is data request 1.
- **A held count per company** ("101 held rows do too") is of links; the held links are not in the files, so links against rows per company were not measured.
- **The pages in a browser**: drawn to HTML with the site's own code; no layout, no width of 390 px.

## Landing, rulings and data (returned to the chain's main session)

- **For landing (words only):** `wip/audit-companies-words` (`6a395e269`), the seven words branches merged (`-1` `15f65f3f3`, `-2` `0b1719d39`, `-3` `98b9e1e0b`, `-4` `e5715da58`, `-5` `d31fcc6be`, `-6` `8bc611e0a`, `-7` `553185f5e`); each drawn and read (pass); no figure moved.
- **For Samuel's ruling, default "left as it is":**
  - Finding 2, `wip/audit-companies-8` (`af73f45bb`), not for landing: the footprint without the share of a generator the company already counts whole: 62,736 MW at 106 companies out of the order; 5 of the first 10 change places, PacifiCorp leaves for DTE Electric; 41 of the first 50 move.
  - Finding 5, `wip/audit-companies-9` (`81f339980`), not for landing: "power marketer" offered among the Kind choices: one choice, "power marketer (439)", added.
- **Data request 1:** rebuild `site/data/companies/` from the tables of 25 November (`warehouse/derived/companies.py` under the lock, then `companies_page.py`), and report the companies listed, those named only in held tables, the held links by table, the first 10 by footprint, the double count (owner rows whose generator the company operates) and the count of companies whose operating, planned or queue MW moves by 1 MW or more.
- **Needs the key:** nothing.
