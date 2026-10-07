# Session 141 report: the missing dataset, from ten entities to forty

Run on 7 October 2026 (UTC), unattended, in the chain 140 to 145. Nothing here is a site page. One internal table,
not in the repository; a one-page summary under `docs/accelerator/`; the connector's rule extended and tested.

## Six things to know first

- **Your e-mail address was sent to outside sites in about 431 requests, and that was my mistake.** My brief pointed
  the research passes at the pilot's scripts, whose default contact string carries it (session 139's pilot sent it the
  same way; SEC EDGAR refuses a request without a contact). By each pass's own record: pass D 37 requests, all to
  sec.gov; pass E 130 (41 to sec.gov, 89 to state commissions and company investor sites); pass F about 113 (23 to
  sec.gov); pass H about 151, none to sec.gov (PJM, ten state commissions, ERCOT, company sites); passes C and G none
  (G refused on its own and read the filings from the companies' sites). I stopped it at 09:41 UTC; no request carried
  it after. No file of session 141 still holds it; the pilot's own scripts under `warehouse/raw/large_load_pilot/`
  still do (not in git). **Yours to rule: whether a contact address may be sent at all, and which.**
- **The table holds 434 statements from 38 of the 40 entities; nothing is published.** `large_load_statements` is on
  the data machine, in the archive and in the private Redivis dataset's draft, as session 139's was. It is not in the
  repository, the public dataset, the live set or any page.
- **A measured wait exists after all, in one filing.** Oncor, in its rate case: "the average interconnection time for
  the 79 retail transmission interconnections that were placed in service from January 1, 2022, through December 31,
  2024, was 825 days. The median time for those interconnections was 687 days." It covers all retail transmission
  interconnections, not only large loads, and only those finished. Everything else in 629 documents is a target, a
  plan or an expectation, except ERCOT's 180 days (the pilot's) and three general statements by Bonneville.
- **The five-stage mapping is the collecting agents' reading, not a person's review.** Every statement keeps its own
  stage words beside the class. 105 of the pilot's rows carry stage words no later pass placed: they read "not
  classed".
- **Model spend was USD 0 of the USD 10 cap.** No code of the repository called a model. The reading was done by this
  session's research agents, which is not what the ledger counts (as in session 139).
- **The cap of five statements an entity is gone.** The pilot took five because you asked for 30 to 50 statements.
  For forty entities the table takes every verified statement once. The rule is otherwise the pilot's.

## Verdict

Nothing to open. **The dataset is real at forty entities and still not publishable.** What is left, exactly:

1. Your ruling on the contact address (above).
2. **Each publisher's terms read and quoted** before any row is published: none was read one by one.
3. **A person's review of the 164 stage words** and their classes (`stage_vocabulary.csv` beside the passes' files).
4. **The dockets an agent cannot reach** (below): a person, or permissioned access.
5. **Waits cannot be collected from statements.** Three measured figures exist, from two Texas entities. New York's
   public queue prints no in-service date for any request (session 140's pull).
6. Decide whether rows that rest on a third party's host or words should be kept as flagged rows: 12 are held out
   (seven marked by their collector, among them the Georgia commission staff's testimony; five of Evergy's from a deck
   hosted by a university because Evergy's investor site refused).

## What was asked for, and what was built

- **Read the pilot and keep the rule:** kept. No number without its sentence; nothing summed across entities; the
  entity, document, date, address, megawatts, stage in the document's words, place and exact sentence on every row.
- **Forty entities, chosen by the pilot's method and listed:** the pilot's ten; SPP, California ISO (with the
  California Energy Commission's forecast it relies on), New York ISO, Bonneville, TVA, Omaha Public Power District;
  PPL, FirstEnergy, PSEG, AES, NiSource, DTE, Xcel, Ameren, Evergy, WEC, Alliant, CMS, Arizona Public Service, Salt
  River Project, Tucson Electric Power, NV Energy, PacifiCorp, Idaho Power, Portland General Electric, PG&E, NextEra
  (Florida Power & Light), CPS Energy, OGE, Black Hills. Chosen before the search, as those believed to report the
  most datacenter load; not a ranking. **MISO is not among them:** its site is not requested while paused.
- **Their most recent plans, testimony, forecasts, earnings filings and operator reports; PDFs read directly; the
  page recorded:** six passes; 329 PDFs listed, 315 read directly; 270 of the 434 statements carry the page of the
  PDF found by code. 189 statements come from resource plans, load forecasts, commission filings, tariff filings or
  testimony; 245 from investor material, operator reports and other documents.
- **The stage vocabulary:** five stages, the original words kept beside each (below).
- **A one-page summary for the letter:** `docs/accelerator/large_load_forty.md`.

## The numbers you asked for

| | The pilot | Now |
|---|---|---|
| Statements held in the table | 49 | **434** (401 megawatt figures, 33 durations) |
| Statements collected and verified by the passes | 110 | 450 (4 failed the table's own row check, 12 held out as a third party's) |
| Entities covered | 10 | **38 of 40** (none: Salt River Project, whose site refuses every plain request; OGE, whose documents state no megawatts) |
| Documents opened | 107 | **629** |
| Documents that yielded a usable figure | 45, 42 percent | **184, 29 percent** |
| An agent's minutes searching and reading | 35.4 | 157.5: about 3.9 an entity |
| Distinct "how long did it wait" figures | 1 | **3 measured** (Oncor's average and median; ERCOT's 180 days), 3 general statements of experience (Bonneville), 28 targets, plans or expectations |

- **Share of documents with a usable figure, by kind:** earnings presentation 32 of 59; operator report 28 of 57;
  load forecast report 18 of 35; earnings release 14 of 35; SEC filing 14 of 55; commission filing 21 of 72;
  integrated resource plan 23 of 103; large load tariff filing 8 of 41; rate case testimony 3 of 13; other 23 of 159.
  Planning documents were tried first this time, and they yield less often than investor material, as in the pilot.

### Time for each entity

Minutes are an agent's clock for searching and reading (a person would need hours). "Stages" are the classes its own
stage words reach, and whether its funnel can be placed.

| Entity | Minutes | Documents opened | With a usable figure | Statements in the table | Wait rows | Stages its words reach |
|---|---|---|---|---|---|---|
| PPL | 3.7 | 18 | 6 | 25 | 3 | 1 4 5 (placed in part) |
| FirstEnergy | 2.6 | 9 | 3 | 19 | 0 | 2 (one stage only) |
| Dominion Energy Virginia | 8.9 | 23 | 11 | 27 | 2 | 1 2 3 4 (placed) |
| Georgia Power (Southern Company) | 5.0 | 16 | 6 | 21 | 0 | 1 4 5 (placed in part) |
| Duke Energy | 6.0 | 23 | 5 | 14 | 0 | 1 2 3 4 (placed in part) |
| Entergy | 5.0 | 24 | 3 | 5 | 0 | 4 (one stage only) |
| PJM Interconnection | 5.7 | 20 | 5 | 1 | 0 | 2 3 4 (placed) |
| Oncor Electric Delivery | 9.9 | 21 | 7 | 21 | 2 | 1 3 4 5 (placed) |
| CenterPoint Energy Houston Electric | 2.2 | 12 | 5 | 10 | 0 | none (not placed) |
| American Electric Power | 3.1 | 14 | 7 | 20 | 0 | 1 3 4 (placed) |
| Exelon | 1.5 | 18 | 4 | 13 | 0 | 1 2 3 5 (placed) |
| ERCOT | 4.9 | 35 | 14 | 39 | 4 | 1 2 (placed in part) |
| Southwest Power Pool | 7.9 | 14 | 11 | 17 | 2 | 1 2 4 (placed) |
| California ISO | 1.2 | 7 | 5 | 15 | 1 | 1 4 (placed) |
| New York ISO | 2.2 | 15 | 4 | 8 | 2 | 1 2 5 (placed) |
| Bonneville Power Administration | 3.1 | 18 | 4 | 8 | 6 | 1 2 3 (placed) |
| Tennessee Valley Authority | 2.4 | 16 | 1 | 1 | 0 | none (not placed) |
| Omaha Public Power District | 2.6 | 25 | 3 | 2 | 0 | 1 (one stage only) |
| Public Service Enterprise Group | 1.5 | 8 | 2 | 8 | 0 | 1 2 3 5 (placed) |
| AES | 2.9 | 12 | 3 | 5 | 1 | 3 4 (placed in part) |
| NiSource | 2.7 | 10 | 4 | 13 | 0 | 4 (one stage only) |
| DTE Energy | 2.0 | 11 | 4 | 8 | 0 | 4 5 (placed in part) |
| Xcel Energy | 6.0 | 16 | 3 | 10 | 3 | 1 2 3 4 (placed in part) |
| Ameren | 3.4 | 18 | 7 | 18 | 0 | 1 2 3 4 (placed) |
| Evergy | 6.4 | 19 | 7 | 3 | 0 | 1 2 3 (placed in part) |
| WEC Energy Group | 1.6 | 10 | 2 | 7 | 0 | 4 5 (placed in part) |
| Alliant Energy | 1.4 | 9 | 4 | 6 | 0 | 1 4 5 (placed in part) |
| CMS Energy | 2.4 | 13 | 4 | 2 | 0 | 4 (one stage only) |
| Arizona Public Service | 4.3 | 19 | 4 | 7 | 0 | 1 (one stage only) |
| Salt River Project | 3.5 | 10 | 0 | 0 | 0 | none (not placed) |
| Tucson Electric Power | 1.5 | 17 | 6 | 6 | 0 | 1 4 (placed) |
| NV Energy | 5.1 | 21 | 4 | 20 | 1 | 1 2 3 4 (placed in part) |
| PacifiCorp | 3.4 | 19 | 4 | 13 | 4 | 1 2 4 5 (placed) |
| Idaho Power | 2.6 | 19 | 1 | 2 | 0 | 1 3 4 (placed in part) |
| Portland General Electric | 7.5 | 17 | 4 | 7 | 0 | 1 4 5 (placed) |
| Pacific Gas and Electric | 2.0 | 10 | 4 | 9 | 0 | 2 3 4 5 (placed in part) |
| NextEra Energy (Florida Power & Light) | 1.7 | 10 | 6 | 7 | 1 | 1 2 3 (placed in part) |
| CPS Energy | 1.6 | 10 | 1 | 9 | 1 | 1 2 4 (placed in part) |
| OGE Energy | 3.3 | 13 | 0 | 0 | 0 | 1 4 (placed) |
| Black Hills Corporation | 1.2 | 8 | 6 | 8 | 0 | 1 3 4 (placed in part) |

### The vocabulary, with its mapping

**The five stages.** 1 request or inquiry (asked or inquired; nothing studied, no money committed). 2 study or
engineering (a study under way or done, or an engineering letter or study agreement signed). 3 financial commitment
(money committed short of a service agreement: a construction letter, a deposit, collateral, an equipment
reservation). 4 signed service agreement. 5 under construction or energized. "none": a total across stages, a
forecast, or words that do not settle it.

- **164 stage words of 37 entities; 76 with the document's own definition; 129 placed on a stage, 35 on none.**
- **Funnels placed on the five stages: 15 of 40 whole; 16 in part** (some of the entity's words are on none); 6 with
  one stage only; 3 not at all (CenterPoint and TVA state no stage words; Salt River Project nothing). No entity's own
  order runs against the stages' order.

| Entity | Its stage words, in its order, each with the stage it is placed on |
|---|---|
| PPL | inquiry (1); suspect (1); prospect (none); imminent (none); announced (none); in advanced stages of planning (none); under signed electric service agreements (4); under construction (5) |
| FirstEnergy | Load Studies (Potential Additions, Not in Pipeline) (2); Pipeline (none); Contracted (none) |
| Dominion Energy Virginia | DP Request (delivery point request) in the large-load connec (1); Engineering Letter of Authorization (ELOA); 'Engineering Let (2); Construction Letter of Authorization (CLOA) (3); Electric Service Agreement (ESA) (4) |
| Georgia Power (Southern Company) | commitments (Contracts for Electric Service plus Requests fo (none); Technical Review (project stage in the report's attachment;  (1); large load economic development projects (the large load pip (1); Request for Service (Request for Electric Service, RFS) (none); Contract for Electric Service (4); broken ground (5) |
| Duke Energy | Advanced Development Projects (ESA, LA and LSP together) (none); Developing Pipeline (1); Late Stage Pipeline (LSP) (2); Letter Agreement (LA) (3); Electric Service Agreement (ESA) (4) |
| Entergy | executed agreements (for new power supply) (4) |
| PJM Interconnection | non-firm (large load adjustment request without an ESO or CC (2); firm: Construction Commitment (CC) (3); firm: Electric Service Obligation (ESO) (4) |
| Oncor Electric Delivery | transmission retail interconnection request (in the queue) (1); Interim Transmission/Substation Facility Extension Agreement (3); Transmission/Substation Facility Extension Agreement execute (4); advanced to the construction stage (5); completed and energized; placed in service (5) |
| American Electric Power | signed LOA and/or ESA (the only load in the forecast) (4); potential customers in various stages of inquiry or negotiat (1); signed ESAs; contracted (4); signed an LOA (HSL additions through 2030) (3) |
| Exelon | Excluded Requests (on the Total Large Load List, not meeting (1); Phase 1 engineering with a financial deposit (projects not s (2); signed Transmission Security Agreement (TSA), or a comparabl (3); in-service (5) |
| ERCOT | not included in Batch Zero (load that has not met sufficient (1); studied load (Batch Zero) (2); base load (Batch Zero), by one of seven eligibility paths: ( (none) |
| Southwest Power Pool | Potential / Pending Study (1); In Study (2); Added to Service Agreement (4) |
| California ISO | Group 3 – Inquiry (1); Group 2 – Active Application (1); Group 1 – Signed Agreement (4) |
| New York ISO | Project Scoping (1); SIS Pending (2); SIS in Progress (2); SIS Approved (2); Facilities Study Pending (2); Facilities Study in Progress (2); Under Construction (5) |
| Bonneville Power Administration | LLIR must be submitted, but no study required (1); Feasibility Study (2); System Impact Study (2); Facility Study (2); execution phase (agreements signed/funded) (3) |
| Omaha Public Power District | projected, unidentified future requests (none); prospective customer requests (1); current and potential load requests (1); firm customer commitments (none) |
| Public Service Enterprise Group | potential leads (1); Capacity Review (01 Initial Assessment) (2); Capacity Review Phase (January 2026 wording) (2); Feasibility Analysis Review Agreement (FAR) (02 Detailed Eng (2); New Business Phase (January 2026 wording) (2); Transmission Extension Agreement (TEA) (03 Construction / Fi (3); Existing (5) |
| AES | Other (none); Memorandum of Understanding (MOU) (3); Construction Commitment (CC) (3); Electric Service Obligation (ESO) (4) |
| NiSource | Developing Opportunities (none); Strategic Negotiations (none); GenCo Signed Capacity (4) |
| DTE Energy | additional pipeline opportunities (none); in advanced discussions (none); executed agreements (4); approved (by the MPSC) (4); construction started (5) |
| Xcel Energy | interconnection request (large load requests in its queue) (1); Feasibility Study (for a cluster) (2); System Impact Study (2); Facilities Study (2); Interconnection Agreement (IA) (3); Electric Services Agreement (ESA) (4); Additional Pipeline (none); Contracted / Under Construction (4) |
| Ameren | active data center opportunities (pipeline of prospective cu (1); interconnection queue: still awaiting formal study (2025 wor (1); completed studies, pending construction agreements (2025 wor (2); construction agreements executed (2025 words: Signed Constru (3); Electric Service Agreements (ESAs) signed (4) |
| Evergy | Tier 2 (1); Remaining Tier 1 Advanced Discussions (3); Tier 1 Active Operations and Signed ESAs (none); included in base load IRP planning (none); Path to Power: active queue (after a Letter of Agreement and (2) |
| WEC Energy Group | Site potential (none); Demand Forecasted (through 2030) (none); entered into a service agreement to obtain service under the (4); went into service (5) |
| Alliant Energy | Opportunities at various stages of exploration (1); Mature opportunities (none); ESA signed (4); ICR filed (4); ICR approved (4); Construction started (5); Load Ramp (5) |
| CMS Energy | Pipeline (Economic Development Pipeline) (none); Qualified (none); Advanced (none); Final Stages (none); agreement under the Large Load Tariff (4) |
| Arizona Public Service | uncommitted queue (1); Committed Load (none) |
| Tucson Electric Power | in the queue (1); further negotiations are ongoing (1); contracted customer demand (4) |
| NV Energy | interest inquiries (1); study phase (2); signed Rule 9 agreements (3); letter of intent (none); LLESA (4) |
| PacifiCorp | Large Load Requests (1); Load Service Evaluation (2); Contracted load (4); Energized (5) |
| Idaho Power | large load inquiries (1); other committed large load customers (3); special contract schedule, or ESA (4); additional firm load (none) |
| Portland General Electric | incremental large load requests (1); executed contracts (4); Under Construction (5); Current Operational Facilities (5) |
| Pacific Gas and Electric | Data Center Pipeline (scope of all stages) (none); Application & Preliminary Engineering (2); Final Engineering (3); Interconnection Construction Agreement (4); Construction (5) |
| NextEra Energy (Florida Power & Light) | large-load interest; inquiries (1); engineering study (engineering and system impact studies) (2); advanced discussions (none); reserve capacity (collateral; large-load transaction under F (3) |
| CPS Energy | Speculative New Customer Requests (1); Feasibility Study (2); Agreement Phase (none); Contracting Phase (In Process) (none); Under Contract (Contracted) (4) |
| OGE Energy | service requests from prospective customers (1); contract-signed stage (4) |
| Black Hills Corporation | data center pipeline (large-load demand pipeline) (1); growth pipeline (as said on the call) (1); agreement to reserve generation equipment (refundable advanc (3); definitive agreements (Large Power Contract Service Agreemen (4); in current financial plan (serving, ramping) (none) |

(Words are cut at 60 characters here; the full words, definitions and addresses are in `stage_vocabulary.csv`.)

### What a full national build would cost in hours

My estimates from the rates measured here, not measurements:

- **Each collection, by agents:** about 6 minutes an entity with the files; 70 entities are about 7 agent hours, under
  an hour of clock with six at once; about 1,100 documents opened.
- **Each collection, by a person:** the dockets an agent cannot reach, and a reading of the rows that are slide lines,
  chart labels or table rows (about a third): on the order of 20 to 25 hours.
- **Once:** a person's review of the stage words, and each publisher's terms read and quoted: on the order of 25
  hours.
- **Not buyable with hours:** the waits.

## What refused a plain request

- **Commissions:** Ohio (each document behind a CAPTCHA), Arizona (CAPTCHA), West Virginia, Michigan, Pennsylvania,
  Minnesota, Iowa, Illinois, Nevada (lists drawn by script or served by number), Oregon and California (no listing
  without a browser). Kentucky, Texas, Missouri, Wisconsin, South Carolina, Georgia and Virginia answered.
- **Company and operator sites:** srpnet.com, tva.com, duke-energy.com, Evergy's investor hosts, blackhillsenergy.com.
- **SEC EDGAR** refuses a request with no contact address.
- Nothing was forced: each is recorded in its pass's `documents.csv` and left.

## Every pull against its ceiling

- **No data pull was approved for this session and none was made into a warehouse source table.** The passes
  downloaded the 522 documents they opened (about 1.1 GB with the pilot's, under `warehouse/raw/`, not in git).
- **No MISO request** (its own site is never asked). **No PJM data request** (PJM's public committee documents were
  read as documents).

## Model spend: USD 0 of the USD 10.00 cap

- No call in the ledger for session 141. No stage was refused, because none was started.

## The landing

- **Landed in one push with session 140** (`task/140-datacenter`): checks passed (run 37610487112), merged as
  `bb33814`; Vercel "Deployment has completed" at 11:03:49 UTC.
- **Snapshot before** (10:54:07 UTC) **and after** (11:03:56 UTC): **0 differences** on the 25 live addresses, 3,357
  checked number keys. Nothing was reverted. Session 141 changes no page: a connector, two tests, one document.
- Freeze: on, ending today; the chain's prompt names the landing.

## Checks

- `tests/test_session141.py`: 9 tests (forty entities with the pilot's ten among them and no MISO; no number without
  its sentence, for megawatts and for durations; every verified statement taken once and a third party's copy not; a
  row of the table, an undated page filed on the day it was read and said so; the original words beside the class;
  which funnels can be placed; the table internal and absent from the repository; the summary in place).
- `tests/test_session139.py`: 6 tests; three assertions changed on purpose (the cap is now a parameter; forty groups).
- The ERW validator on the table: exit 0, events shape, 434 rows, 37 columns.
- Coverage (`--only`), the archive and the internal Redivis draft: exit 0 each; `count(*)` 434 in the private dataset's
  draft; nothing released.

## The five most interesting numbers

1. **825 days on average, 687 at the median**, for 79 retail transmission interconnections Oncor placed in service in
   2022 to 2024: the only measured wait a utility states in 629 documents.
2. **117,800 MW requested of Oncor in 2024 alone** (21,076 in 2022 and 23,279 in 2023), against 5,846 MW that had
   advanced to construction and 2,551 MW "completed and energized" from the requests of those three years.
3. **Georgia Power's pipeline reached 84,800 MW at 30 June 2026**, 15,600 MW of it committed across 32 customers; in
   that one quarter 6,800 MW entered the pipeline and 1,400 MW left it.
4. **California counts 23,278 MW of datacenter requests, of which 5,086 MW are signed**: the Energy Commission
   redefined its top group in 2025 from "studies completed or pending" to "signed agreement". Pacific Gas and
   Electric, a week after tightening its own stages, showed 12,710 MW with 140 MW in construction.
5. **15 of 40 funnels can be placed whole on five stages, and 29 percent of documents opened held a usable figure.**
   The collecting is cheap; the meaning of each stage, the terms and the waits are what remain.

## Decisions made without you

1. The research for this session ran while session 140's pulls were running, to save the night's hours.
2. The table takes every verified statement (the cap of five is a parameter now, off).
3. PPL's and FirstEnergy's submissions that PJM posts moved from PJM's group to their own.
4. A statement of a duration is a row of its own kind (`row_kind` wait), with megawatts empty.
5. A web page that prints no date is filed on the day it was read, and the row says so (five rows).
6. Six columns were added; the 49 rows of session 139's shape were rewritten with them empty and then replaced.
7. The stage vocabulary is kept beside the passes' files, not in the repository; the report and the summary carry
   the stage words and the counts.
8. The pilot's four Dominion rows marked as a third party's copy stay out of the table, although pass H found the
   same figures on the commission's own server: they need recording from that copy.
