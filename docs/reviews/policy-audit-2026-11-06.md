# The policy monitor's audit, 6 November 2026 (chain 166, sessions 3054 to 3065)

Chain 166 (`queue/done/166-night-6-november-portable-window2-policy-monitor.md`) numbered its sessions 2260 to 2271; every number from 2260 to 3053 was taken on origin's main or a branch when it started, so it runs as sessions 3054 to 3065. This file is its faults file: the ground (session 3054), the audit of the stored actions (session 3055), and the rows each later session closes.

## Ground (session 3054)

Read on 6 November 2026, about 11:30 UTC. Counts are of the live set (`events` where `table_name` is `policy_actions` or `policy_reads`, read with the service key), which matched Redivis's own counts that hour (2,020 and 408 rows, `scripts/sync.py --check`). This laptop's own copies were a month behind (1,836 actions to 1 October, 234 reads to 5 October).

### 1. What the monitor is made of

The chain file names `warehouse/news/policy*.py` as the scorer and the actions' builder. No such file exists: the monitor's code is

| Path | What it does |
|---|---|
| `warehouse/connectors/policy_sources.py` | the actions' builder: the Federal Register API (DOE, FERC, EPA, NRC, BLM, Interior, Treasury, IRS), the NRC and DOE news feeds, the PUCT and CPUC news pages, into `policy_actions`; each Register document's printed text read once (session 157) |
| `warehouse/policy/score.py` | the score: the news scorer's prompt, rubric and schema (`warehouse/news/score.py`, `warehouse/news/rubric.md`) with one added note for policy (`POLICY_NOTE`), into `warehouse/policy/scores.csv` and the table's score columns |
| `warehouse/policy/reads.py` | the impact read of an action scored 5 or more, from the action's own text, a field kept only when its quotations stand word for word in that text (`policy_reads`, `policy_reads_evidence`) |
| `warehouse/policy/recheck.py`, `rule_reads.py` | session 157's rescoring against the source text; the one-line reads of `large_load_rules` |
| `warehouse/derived/policy_action_tags.py` | the four tags (large loads, interconnection, transmission cost, tariffs) by a written rule (`warehouse/config/policy_tag_rules.json`) |
| `warehouse/connectors/policy_monitor_refresh.py`, `warehouse/derived/policy_monitor_site.py` | FERC's and ten state commissions' open dockets on large loads (`large_load_rules`), and the site's files under `site/data/policy/` |
| `site/app/policy/` (`page.tsx`, `PolicyTable.tsx`, `WeekView.tsx`, `Paused.tsx`), `site/lib/policyreads.ts`, `policyweek.ts`, `policyweekdata.ts` | the page |
| `docs/methods/policy_monitor.md` (417 lines, thirteen sections), `docs/methods/policy_action_tags.md` | the method |

Decision recorded in the report: this chain's "files it owns" are read as these paths (the chain's intent: the policy scorer, the actions' builder and the page), and `warehouse/news/score.py` and `rubric.md`, which the news scorer shares, are not changed by it; a policy change to the prompt is made in `warehouse/policy/score.py`'s own note.

**What an action is.** A row of `policy_actions` is a government document or release (a Register rule, proposed rule or notice, or an agency's news release), not a news story. Stories reach it only as links (`news_story_ids`, `news_story_urls`: a scored story that names the same docket, RIN or document number, or a title of the same content words within 21 days). The chain's steps written for stories (deduplication "across outlets", "30 stored stories") are read in that light: the record is the document, the outlets are its linked stories, and a duplicate is two documents or releases of one action.

### 2. The tables

`policy_actions` (events shape; 2,020 rows, 2025-10-01 to 2026-11-05). Columns: `event_id, event_date, event_type, parties, entity_ids, mw, price, currency, status, source, source_url, agency, action_type, title, abstract, docket, rin, fr_document_number, sector_tags, states, related_urls, news_story_ids, news_story_urls, first_paragraph, place_words, title_register, text_status, text_read_at, significance, sector, why, model_id, scored_at, model_recheck, model_rechecked_at, retrieved_at`.

| Field | Vocabulary on 6 November |
|---|---|
| `agency` | FERC 935, NRC 499, DOE 185, EPA 182, Interior 85, BLM 51, CPUC 38, PUCT 37, IRS 8 (Treasury: none kept yet) |
| `action_type` | notice 1,399, press_release 268, rule 198, proposed_rule 155 |
| `status` | the Register's action line as printed ("Final rule.", "Notice of availability.") or "news release": free text, not a status vocabulary |
| `docket` | filled on 1,688 rows |
| `states` | filled on 1,195 rows |
| `significance` | 0: 12, 1: 293, 2: 639, 3: 394, 4: 282, 5: 181, 6: 144, 7: 56, 8: 16, 9: 3 (400 at 5 or more; every row scored) |
| `sector` (the scorer's) | policy 507, nuclear 389, gas 301, renewables 287, generation 208, oil 87, other 68, lng 64, storage 44, transmission 21, grid_conditions 9, transport 9, power_prices 7, interconnection 5, geopolitics 5, capital 4, company 4, deal 1 |

Rows by ISO week (the event date): 2025-W40 16, W41 1, W42 3, W43 7, W44 2, W45 3, W46 9, W47 53, W48 76, W49 34, W50 30, W51 49, W52 19; 2026-W01 31, W02 31, W03 30, W04 33, W05 52, W06 30, W07 43, W08 37, W09 52, W10 29, W11 52, W12 40, W13 46, W14 37, W15 31, W16 43, W17 43, W18 41, W19 32, W20 51, W21 46, W22 47, W23 50, W24 40, W25 50, W26 49, W27 32, W28 33, W29 35, W30 29, W31 40, W32 53, W33 38, W34 33, W35 36, W36 30, W37 29, W38 39, W39 31, W40 22, W41 39, W42 28, W43 39, W44 38, W45 28 (to Thursday 5 November). The thin weeks of October and November 2025 are the news feeds' windows (a feed keeps its last items only); the Register is read in full from 1 October 2025.

`policy_reads` (408 rows, one per action read; dates 2025-10-01 to 2026-11-05). Columns: `event_id, event_date, event_type, parties, entity_ids, mw, price, currency, status, source, source_url, action_event_id, agency, action_type, title, significance, what_changes, affected_sectors, affected_isos, affected_states, direction_supply, direction_demand, direction_prices, direction_buildout, timeline, plain_read, fields_kept, fields_dropped, news_story_urls, model_id, read_at`. By week, 1 to 19 reads (2026-W41 the most).

`policy_reads_evidence` (3,559 rows, internal): `read_id, field, span, source_text_file`, one quotation a row.

**What the tables do not hold**, against the chain's list of fields: no instrument beyond the four `action_type`s (no order, guidance, approval, lease sale, bill, tariff filing or docket opening as such: a FERC order printed as a notice is a `notice`); no status vocabulary (proposed, final, effective, stayed, vacated, withdrawn); no effective date, comment deadline or hearing date as a field; no figure and unit as a field (`mw` and `price` are empty on every row); no next step; no evidence sentence for the action's own fields; no record that groups the documents of one action.

### 3. The scorer's prompt and vocabulary

`warehouse/policy/score.py` gives the news scorer (`warehouse/news/score.py`: `SYSTEM` with the rubric of `warehouse/news/rubric.md`, the JSON `SCHEMA`, the model `NEWS_SCORE_MODEL`, `claude-haiku-4-5` since session 206) the action's title and a summary (the abstract, else `first_paragraph`, else the status line, at most 600 characters), with the beat "policy" and `POLICY_NOTE`: "When the summary is empty, say what the title says and no more: do not infer what the document decides, whom it affects or why it matters from a company's name, an agency's name or a docket number, and choose the sector only from words the title itself holds." The schema returns `significance` (0 to 10), `ai_power_relevance`, `sector` (one of 21: oil, gas, lng, power_prices, generation, nuclear, renewables, storage, transmission, grid_conditions, interconnection, datacenter_power, deal, ppa, policy, capital, company, geopolitics, transport, hydrogen, other), `region`, `mw_mentioned`, `price_mentioned`, `parties`, `headline`, `one_line_why`, `is_duplicate_of`; the policy step keeps `significance`, `sector` and `why` only. The rubric's bands: 9 to 10 market-moving (a federal rule or court decision with industry-wide effect), 7 to 8 a state-level rule or hundreds of MW or millions of dollars, 4 to 6 a filing, a permit, a study with numbers, 1 to 3 minor, 0 not energy.

### 4. The pages

| Address | What it shows |
|---|---|
| `/policy` ("Every action, scored", the default view) | the lead (sources, the score and the read as hovers), the paused sources line, "This week in policy" (up to six actions of the last seven days at 5 or more, with the read's plain sentence or the scorer's why), "Every action" (`PolicyTable`: filters by agency, type, sector, state, significance and date, and the four tags; columns Date, Agency, Type, Title, Sector, Significance; a row opens to its read and sources; the count shown; the first 400 listed), the downloads of `policy_actions` and `policy_reads` (CSV with Python and Stata readers) |
| `/policy?view=week` ("What changed this week") | the actions of the last 7 and 30 days by body, topic and grid, with FERC's and the state commissions' proceedings from `site/data/policy/state_rules.json`, the dropped rows counted with why |
| `/data/methods/policy_monitor` | the method note |

Every page is `review` (`site/lib/release.ts`: `"/policy": "review"`). The site reads `policy_actions` from the live set's `events` table, eleven fields of `extra` (`agency, action_type, title, docket, sector_tags, states, significance, sector, why, related_urls, news_story_urls`) with `event_id, event_date, status, source_url`.

### 5. The policy steps' last runs (erw_health)

`queue/summary/*-health.md` lists a step only when it is not ok; the rows below are read from `erw_health` itself.

- `policy_score`: seven rows held, the newest five failed: 26 to 30 October (runs 40335571667, 40517022435, 40701642758, 40887150915, 41067951705), each "0 newly scored, 1959 of N scored" (N 1,960 to 1,991), cost USD 0.0000: the account's spending limit of 28 October to 1 November (session 2864's report) and the days before it; 10 and 12 October skipped at the daily model cap. No row since 30 October: a step that passes writes no row. On 6 November every one of the 2,020 actions carries a score, so the 32 left unscored on 30 October were scored by a later run.
- `policy_reads`: two rows, both skipped at the daily cap (10 and 12 October).
- `policy_sources`: no row (a pull step that passes writes none, and none failed).
- `policy_monitor_refresh` and `policy_monitor_site`: ok on each of 22 to 30 October and on 6 November 00:17 and 00:20 UTC (run 42120465428). No daily run recorded these steps on 31 October to 5 November.

### 6. The Digest's policy row

`warehouse/news/brief.py`, `policy_actions_lines`: the window's actions scored 5 or more, most significant first, three at most, as the Policy group's last lines. It reads `event_date`, `significance`, `title`, `agency`, `action_type` (and its four names: rule, proposed_rule, notice, press_release), `why` and `source_url`. The Roundup and `site/lib/digest.ts` read the line's text (", policy action): "). Every one of these keys keeps its name and meaning in this chain; a new field is added beside them.

The periodicals' faults file (`docs/reviews/periodicals-faults-2026-11-05.md`) has no open row on the policy actions: its row 5 ("the policy row takes a policy or capital story") and row 9 (a why line that restates the headline) are fixed in the Digest's code (f93754995, 41f12b20f), which this chain does not touch.

## The audit of the stored actions (session 3055)

**The sample.** Every fifth row of the newest 400 actions of the live set (ordered by `event_date` descending, then `event_id`), 80 rows from 14 August to 5 November 2026: FERC 33, NRC 20, DOE 10, EPA 8, BLM 3, CPUC 3, Interior 2, PUCT 1; notice 58, press_release 12, rule 8, proposed_rule 2. Each was read against its own document, fetched on 6 November 2026 into the session's scratch folder only (one request every two seconds, the connector's User-Agent): for a Register document its API record (`action`, `dates`, `effective_on`, `comments_close_on`, `agencies`, `type`) and its printed text; for a release its page. All 80 answered. Nothing was written to the warehouse. Row numbers below (r1 to r80) are the sample's order, newest first; the event ids are in `docs/reviews/policy-audit-2026-11-06-sample.csv`.

**The fault classes, largest first.** "Table" counts are of all 2,020 rows where a field can be counted without reading the document.

| # | Fault | Sample (of 80) | Table | Open |
|---|---|---|---|---|
| 1 | A date the document states (an effective date, a comment, protest or intervention deadline, a hearing or a session) is held in no field | 61 (59 first counted, 62 in session 3056; r58 states no date) | every row: no date field but `event_date` | 3056: held for 56; 3125: 60 of 61, none kept that the text does not state; r57 gives a month only, kept as words |
| 2 | No status: `status` is blank, or is the Register's action line, never a status (proposed, final, effective, stayed, vacated, withdrawn) | 80 (35 blank, 33 of them FERC) | 917 blank, 901 of FERC's 935 | 3056: `action_status` on 80 of 80 (the fixture's 30 right) |
| 3 | A figure the document states as the action's own (MW, kV, Dth/d, USD) is held in no field: `mw` and `price` are empty | 17 (17 first counted, 16 in session 3056; r57 found in session 3126) | 2,020 empty | 3056: 12 of 16; 3126: 16 of 17, none on another row; r6's per-driver incentives are no total |
| 4 | Sector "policy", which names no sector: every row is policy; the action's sector stands in its text | 16 | 507 | 3056: the scorer's policy note names it; the rows held change when they are scored again (the desktop's, with the owner's approval) |
| 5 | The instrument is not held: `action_type` is the Register's category, so an order, a guidance, a lease sale or an award stands as a notice or a news release | 14 | the four types only | 3056: `instrument` names 14 of 14 (and the fixture's 30) |
| 6 | The place is missing or short where the text states it | 6 | not counted | open (the faults rows, 3073 on) |
| 7 | One action held as several rows (repeated notices, one exemption's two documents, a docket spelled two ways) | 3 | 406 docket ids stand on more than one row | 3057: one record a proceeding (`warehouse/policy/records.py`): r16's four weekly notices one step of the Pioneer record, r66 and r71 in it too; 2,020 documents make 1,495 records |
| 8 | The body at its parent's level (a bureau as "Interior", a governor's release as the PUCT's) | 3 | at least 45 of Interior's 85 rows carry a BOEM (33) or OSMRE (12) docket | 3056: `body` right on 3 of 3 (OSMRE, BOEM, Texas Governor) |
| 9 | Out of scope: not an energy action, or routine paperwork the connector means to leave out | 4 | not counted | open (the faults rows, 3073 on) |
| 10 | Significance above the rubric's band for what the document does | 2, and 1 borderline | not counted | open (the faults rows, 3073 on): the scorer must run again |

No fault was found in the title, the docket's presence or the event date of the 80. The impact reads (`policy_reads`) of the sampled actions that have one carry a `timeline` sentence that names the next step, so for the 5-or-more rows the date stands in prose; it is in no field of the action.

### 1. Dates held in no field (62 of 80)

24 Register documents carry the date in the Register's own record (`effective_on` or `comments_close_on`), three more in their DATES line or text only, 31 FERC notices in their text (FERC's record has neither field), four releases in their page. Session 3055 counted 59; reading the texts again in session 3056 found three it missed (r39 and r42, FERC comment deadlines of 23 November and 21 October; r66, an exemption "effective upon issuance", issued 28 August).

1. r13, FERC, Sandy Hollow Power Company: "Deadline for filing comments, motions to intervene and protests: November 20, 2026 5:00 p.m." The row holds no date but 2026-10-26.
2. r25, NRC, AP1000 Design Certification Renewal: "The final rule is effective December 28, 2026, unless significant adverse comments are received by November 13, 2026". No date held.
3. r54, NRC, North Anna early site permit renewal: "A request for a hearing or petition for leave to intervene must be filed by November 10, 2026".

Session 3055 wrote here that four FERC blanket-authorization notices (r23, r37, r43, r59) state their deadline only as a period. That was wrong: each also states the date ("The deadline for filing protests, motions to intervene, and comments is 5:00 p.m. Eastern Time on December 8, 2026", r23); the period is the authorization's, which follows the deadline.

### 2. No status (80 of 80)

1. r2, r4 and every FERC notice of the sample: `status` blank (the Register's record has no action line for FERC).
2. r15, BLM, termination of an EIS: "The EIS effort described in the NOI is terminated immediately"; the row's status "Notice of termination." (the status word is withdrawn).
3. r25 (above): "Direct final rule and issuance of environmental assessment"; the status is final, effective on a date unless comments arrive.

### 3. Figures held in no field (16 of 80)

1. r63, FERC, Forza Pipeline EA: "Forza would lease 750,000 Dth/d of natural gas transportation".
2. r22, DOE release: "West Virginia Large Load Growth project will receive up to $50 million in DPA funding".
3. r61, FERC, DeepGreen Cook Inlet preliminary permit: "The estimated annual generation of the DeepGreen Project would be 100 megawatts".

Not every figure of a text is the action's: the DOE coal orders (r40, r46) state "17 gigawatts" of context, and session 3055 counted them (17); without them, and with r30's "79,303 dekatherms per day of incremental firm service" that it missed, the class is 16. Session 3056's rule keeps a figure only from the title or the document's opening paragraph, with its sentence as the evidence.

### 4. Sector "policy" (16 of 80)

1. r49, EPA, "Partial Repeal of the Carbon Pollution Standards for Fossil Fuel-Fired Electric Generating Units": sector policy (the text's sector: generation).
2. r64, EPA, small refinery exemptions under the Renewable Fuel Standard: sector policy (oil, fuels).
3. r17, EPA, Virginia's coal combustion residuals permit program: sector policy (generation, coal).

### 5. The instrument not held (14 of 80)

Orders 4 (r21, r40, r46, r66), guidance 4 (r19, r45, r73, r76), a lease sale 1 (r27), awards 5 (r20, r22, r41, r56, r79). Beyond these, "notice" covers at least six instruments in the sample (an application received, an environmental review step, a permit or license issued, a meeting or session, a decision on petitions, a board's appointment).

1. r40, DOE release, kept as press_release: "Secretary of Energy Chris Wright today issued an emergency order to prevent a Colorado coal plant from going offline".
2. r19, FERC, kept as notice: the Commission "has prepared a draft policy statement concerning the Commission's review of operational air emissions".
3. r27, Interior, kept as notice: "Notice of Availability of the Proposed Notice of Sale for the Cook Inlet Outer Continental Shelf Oil and Gas" lease sale.

### 6. Place missing or short (6 of 80)

1. r27, BOEM, Cook Inlet lease sale: `states` empty; the text says "Alaska".
2. r60, BLM, Southern Ute Mancos Shale programmatic EIS: `states` empty; the text: "the Southern Ute Indian Reservation in southwestern Colorado".
3. r68, NRC, NextEra and Dominion indirect transfer: `states` CT only; the text names "Dominion Energy South Carolina, Inc" and Virginia's plants (Surry, North Anna) beside Millstone.

The others: r8 (`states` empty; "issued to the City of Pelican, AK": the public-body rule reads "City of Chignik, Alaska", not a postal abbreviation), r39 ("in Valdez, Alaska"), r66 (the Pioneer exemption, empty, where r71 of the same project holds MI).

### 7. One action, several rows (3 of 80)

1. r16, NRC, Pioneer Units 1 and 2: "This is the fourth of four consecutive weekly notifications"; the table holds the four weekly notices as four rows (1, 8, 15 and 22 October), each scored 6.
2. r66 and r71: the Pioneer exemption (issued 28 August) and its environmental assessment (25 August), two rows of one decision.
3. The same docket spelled "Docket Nos. 50-616 and 50-617" (six rows) and "Docket Nos. 050-616 and 050-617" (two rows): a docket match misses them.

### 8. The body at its parent's level (3 of 80)

1. r14, kept as Interior: the document's agency is the "Office of Surface Mining Reclamation and Enforcement" (Wyoming Regulatory Program).
2. r27, kept as Interior: the Bureau of Ocean Energy Management's lease sale (docket BOEM-2026-0925).
3. r79, kept as PUCT: "Governor Abbott Announces More Than $795,000 In Grant Funding To Strengthen Electric Reliability In Northwest Texas" (the Governor's release on the commission's page).

### 9. Out of scope (4 of 80)

1. r26, DOE, "Senior Executive Service Performance Review Board" (a personnel appointment; scored 0).
2. r9, EPA, "Cross-Media Electronic Reporting: Announcement of Determination To Approve Authorized Program Revisions" (electronic reporting, no energy subject; scored 1, with 17 states).
3. r29, DOE release, "Genesis Mission Graduate Fellowship to Advance American Scientific Leadership" (a fellowship; scored 2).

The fourth: r3, DOE's "229 Boundary" for the SLAC laboratory (a security boundary). All four score 0 to 2, so none reaches a page's default view (5 or more).

### 10. Significance above its band (2 of 80, 1 borderline)

1. r78, FERC, PG&E Potter Valley: scored 5 for "notice of two additional public scoping sessions" (a meeting; the rubric's 1 to 3).
2. r21, FERC, storage developers against ISO New England: scored 5 for an order on the comment period ("request a shortened 10-day comment period"); the complaint itself is the action of weight, the shortening is procedural (3 to 4).
3. Borderline: r63, the Forza Pipeline EA, 7 (an EA is a review step, the rubric's 4 to 6; the 750,000 Dth/d it reviews is the 7 to 8 band's size).

None scored clearly below its band.

## Session 3056: the fields made precise

`warehouse/policy/fields.py` reads, for each action, from the Register's record (its `agencies`, `effective_on`, `comments_close_on`, now asked for in the listing) and the document's text: `body`, `instrument`, `action_status`, `dates` with `dates_evidence`, `next_step` with its date and evidence, `figure_value`, `figure_unit` and `figure_evidence`, `docket_ids`, `fields_from`. No model is called; a field neither states is empty. The connector adds the columns beside its own (`agency`, `action_type`, `status` and every key the Digest reads keep their names). The scorer's policy note gains one sentence on the sector (class 4).

- **The fixture** (`tests/fixtures/policy/actions_3056.json`, 30 of the 80, answers written from each text): body, instrument, status, dates, next step and figure each 30 of 30 (`tests/test_policy_fields.py`). Writing the answers found two of session 3055's readings wrong (r23's dated deadline, r8's end date), and they were corrected before the rules were graded.
- **Held out** (the other 50 of the 80, never used to write the rules): three faults found and fixed (the plural "emergency orders", an accepted application whose title names environmental issues, a rescheduled scoping session); after them, on all 80: dates held for 56 of the 62 rows that state one and on no other row; a figure for 12 of 16 and on no other row; the instrument named for 14 of 14; the body right for 3 of 3.
- **What is left of classes 1 and 3:** six rows whose dates the rules do not read (a CPUC forum's and the NRC hearing's dates in a release, r38 and r58; the water-quality "reasonable period" of r50 and r72 written as "One year, August 27, 2027"; FERC's procedural schedule of r57 by month only; r78's sessions), and four figures outside the opening paragraph (r6, r22, r29, r31).
- **The rows held** gain the fields when the connector next reads their text: on the data machine, every Register row whose printed text is in its store (`warehouse/raw/policy_sources/fr_text/`) is derived on its next run; a row read on the runner before this session keeps its text fields empty until then (`fields_from` says what each row's fields were read from).

## Session 3057: one record an action

`warehouse/policy/records.py` groups the documents that name one proceeding (a FERC docket with its amendments, a hydro project's numbered proceeding, an NRC docket ID, an EPA, DOE, BOEM, OSM or IRS docket, a RIN, a DOE LNG docket, an OSMRE program amendment) into one record, with every source of every document (the Register's pages, the folded releases, the linked news stories) and a status history in which a repeated notice is one step with every date. A billing code (BLM's `A2407-014-004-065516` on 52 rows of unrelated matters, OSMRE's on 14), an NRC plant's license docket (`50-261`, which spans exemptions, a renewal and a transfer) and a document number make no record; a document with no proceeding id joins only a repeat of its own title from its own body within 45 days.

- **The fixture** (`tests/fixtures/policy/records_3057.json`, 30 stored rows in nine records and seven alone, among them the billing-code and plant-docket traps): 20 of 20 pairs together, none wrongly joined, none wrongly apart (`tests/test_policy_records.py`).
- **On the table** (this laptop's copy, 2,020 rows, run to the scratch folder, never the warehouse): 1,495 records; 301 hold more than one document (826 documents); the largest holds nine (Pioneer, `nrc:NRC-2026-0265`: the application and its four weekly notices, the notice of intent for the environmental impact statement, the exemption's EA and the exemption). The validator passes the table as events (0 errors, 0 warnings).
- **"Across outlets"**: a row of this table is a government document, so outlets enter as sources: a release folded into its Register document (`related_urls`) and the news stories linked to it (`news_story_ids`, 40 rows hold one). The record carries all of them, once each.
- **Not wired into the daily run.** `policy_action_records` is not yet a table of the warehouse (coverage, licenses, the live set are the owner's to register); the page's builder computes the records from `policy_actions` at build time, and the script can write the table on the data machine when the owner asks.

## Session 3058: the impact read

`warehouse/policy/impact.py`: an action's impact read is one sentence, the model's clause of what changes (kept only when its quotation stands in the text word for word, every number in it stands there too, it is one sentence and holds no word of opinion) and then the table and page it bears on, chosen by written rules (`TABLE_RULES`, the method note's section 15), never by the model.

- **The map**: 30 of 30 on the fixture's actions (tables written from their texts, `tests/fixtures/policy/impact_tables_3058.json`). Read against 30 more of the audit's sample, four rules were wrong and are fixed: the NRC's biweekly notices and license transfers went to the new reactors' table (their texts name combined licenses), a reconductoring award to the large-load rules (its project is called "Large Load Growth"), a "new major license application" missed relicensing, an LNG terminal's scoping went to the pipelines.
- **The reads**: 60 stored actions (the fixture's 30 and 30 of the sample, the most significant first), 63 calls of Claude Sonnet 5.5, USD 0.45 (the cap was USD 2). 54 kept, 6 dropped: a quotation not in the text (3: r25's AP1000 rule, the NRC's Belews Creek hearing release, a Florida Gas blanket request), over 45 words (2), a number the text does not state (1: "15" members of a DOE board, counted by the model, not stated). Every kept sentence is in `docs/reviews/policy-impact-2026-11-06.csv` with its quotation, for the owner's reading.
- **Class 10** (significance above its band) is not changed by this session: it needs the scorer run again; it moves to the faults rows (3073 on).

## Session 3064: the second read

The audit's 80 actions read again with the chain's code (`warehouse/policy/fields.py`, `records.py`, as at `wip/3064-policy`), on the same documents fetched on 6 November (the Register's record and printed text, or the release's page). A fault counts after only where the row's new fields still show it. Classes 4, 9 and 10 change only when the rows are scored again or the connector's scope rule changes, neither of which this chain did.

| # | Fault | Before (of 80) | After (of 80) | What is left |
|---|---|---|---|---|
| 1 | A stated date held in no field | 61 | 1 (session 3125) | r57, a schedule given by month only ("May 2027"), kept as words; the five other rows of session 3064 held since session 3125, and r58, which states no date, out of the class |
| 2 | No status | 80 | 0 | `action_status` on every row; the fixture's 30 right |
| 3 | A stated figure held in no field | 17 | 1 (session 3126) | r6, a program's per-driver incentives ("Up to $20,300 toward the purchase"), not a total of the action |
| 4 | Sector "policy" | 16 | 16 | the scorer's note is changed; the rows change when they are scored again |
| 5 | The instrument not held | 14 | 0 | `instrument` names all 14 |
| 6 | The place missing or short | 6 | 6 | not addressed by this chain (the faults rows, 3073 on) |
| 7 | One action, several rows | 3 | 0 | r16, r66 and r71 are documents of one record, `nrc:NRC-2026-0265` |
| 8 | The body at its parent's level | 3 | 0 | OSMRE, BOEM, Texas Governor |
| 9 | Out of scope | 4 | 4 | not addressed (the faults rows) |
| 10 | Significance above its band | 2 | 2 | needs the scorer again (the faults rows) |

Of the 80 rows' 206 faults before (each row counted once a class), 38 are left: 6 of class 1, 4 of class 3, and the 28 of classes 4, 6, 9 and 10, which wait for a rescoring or the next chain's rows.

## Session 3125: the dates left of class 1

Four rules of `warehouse/policy/fields.py`, each with the document's own words as its test (`tests/test_policy_fields.py`, `test_the_dates_of_session_3125`): a water quality certification's deadline ("Reasonable Period of Time to Act on the Certification Request: One year, August 27, 2027", r50 and r72, a `decision_due`); the abbreviated months and weekdays of a release ("When: Tue., Oct. 13, 2026 at 1 p.m. (Virtual) Tue., Oct. 27, 2026", r38, two meetings); a date under a heading of its own ("Evening Scoping Session" then "Date: Tuesday, September 15, 2026", r78) and a comment period extended "to" a date (r78). Class 1 is now 60 held of 61: r57 gives its schedule by month only ("May 2027"), which stays words, as the chain's rule says; and r58, counted in session 3056, states no date at all (the NRC's release names no day for its hearing), so the class is 61, not 62. On the archive's copy of the table the rules add one step (51 steps, from 50) and no step to a row that states none; `scripts/check_policy.py` 288 of 288 ok. The second read's totals become 205 faults before and 33 left.

## Session 3126: the figures left of class 3

A third reading in `warehouse/policy/fields.py`'s `figure()`: where neither the title nor the opening paragraph states a figure, one of the text's first 9,000 characters, only in a sentence that states the action's own total ("for a total installed capacity of 2,980 kW", r31; "Total planned funding is up to $100 million", r29; "project will receive up to $50 million", r22), and only after those words; never a figure of context (tested with the coal orders' "17 gigawatts"). r57's "total installed capacity" of 0.55 MW, which session 3055 did not count, is found and is the project's own: class 3 is 17, 16 held. r6 (a CPUC release's per-driver incentives, "Up to $20,300 toward the purchase or lease of a new electric vehicle") is left: an amount each driver may receive is not a total of the action.

**A fault found on the way, since session 3056**: a sum written "$1.2 million," (a comma after the scale) lost its scale, so 13 records of the archive's copy read a million times too small (`ferc:CP27-4` 1.2 for USD 1.2 million, `ferc:CP26-527` 103 for USD 103 million, and eleven more). The pattern is fixed and tested; `site/data/policy/monitor.json` is rebuilt (212 figures, 13 values corrected); `check_policy.py` 288 of 288 ok. None of it had landed. The second read's totals become 206 faults before and 30 left.
