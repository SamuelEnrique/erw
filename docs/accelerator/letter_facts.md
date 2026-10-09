# The letter of intent: facts laid out against the call's sections

Session 139, 7 October 2026. Bullet points with their sources and no persuasive prose: the owner writes the letter.
Sources: `call_requirements.md` (the call, quoted), `evidence_pack.md` (the repository's facts, each with its path;
counted at commit `64d7b83`, before session 138), `large_load_pilot.md` (the gap and the pilot),
`../paper/related_projects_notes.md` (other projects), `archive/sessions/SESSION_138_REPORT.md` (the datacenter page).

## 0. Read first: what is and is not known about the call

- **The current call exists and its dates match yours.** 2026 Request for Proposals, issued 23 September 2026; letters
  of intent due 30 October 2026; invitations to submit a full proposal 11 November; full proposals due 15 December;
  projects start by June 2027 (`call_requirements.md`, section 1).
- **Its full text was not read.** The RFP is a Google Drive file behind a Stanford sign-in. The length limit, the
  letter's questions, the review criteria and the budget range of the 2026 call are therefore **not found**. A person
  with a Stanford account opens the link in `call_requirements.md`, section 0, and compares it with section 4.
- **The sections below follow the Fall 2025 call**, the newest whose full text is public (letters were due 3 November
  2025): eight questions, with limits of 150 words, one uploaded page, and four answers of 300 words. If the 2026
  questions differ, the facts move; they do not change.
- **Eligibility, quoted from the 2026 public pages:** "Stanford faculty members or Stanford and SLAC researchers who
  qualify as a principal investigator according to Stanford University policy"; and "Teams must include a designated
  postdoctoral researcher or student lead for the project to serve as the primary point of contact with the
  Accelerator for entrepreneurial development." A student is a required team role, not the principal investigator.
  **The letter needs a faculty principal investigator. None is named in the repository.**
- **Budget, 2025 call only:** "New project team grants are typically up to $150,000 for the first year of project
  funding", reassessed each year, up to three years. The 2026 figure was not found.
- **Screening, 2025 call:** letters are screened for eligibility and alignment; "We prioritize projects with the
  potential for large-scale impact (e.g., reducing greenhouse gas emissions by gigatons per year or improving the lives
  of one billion people) and speed (externalizing the solution from Stanford within 1-3 years)."
- **No open-science or data-sharing requirement was found in either year's text.**

## 1. Question 1: which flagship

- The call's eight areas: Biological Solutions, Climate Adaptation, Electricity and Grid Systems, Food and
  Agriculture, Greenhouse Gas Removal, Industry, Planetary Intelligence, Water (`call_requirements.md`, section 2).
- **Electricity and Grid Systems**, its target quoted: "Reduce gigatons per year of greenhouse gas emissions from the
  electricity sector globally by 2035 while driving toward zero-GHG, reliable, flexible, and affordable electricity for
  all by 2050."
- **Planetary Intelligence**, quoted: "Address gaps in observation and measurement through sensing technologies and
  artificial intelligence to provide data-driven actionable insights across all flagship destinations."
- Facts that bear on the choice: the ERW's tables are US power, gas, oil and storage data (Electricity and Grid
  Systems); the proposed project is a measurement gap closed by reading documents with a model and checking each
  figure by code (Planetary Intelligence's wording: "gaps in observation and measurement ... artificial intelligence").

## 2. Question 2: project title

- Not written here. Words the facts support: large load, datacenters, waiting for power, by place, an open dataset,
  each number with its sentence.

## 3. Question 3: the problem (2025 limit: 150 words)

- A search on 7 October 2026 found no national public dataset of how much large load is waiting for power by place,
  and no public dataset anywhere of how long a new large load waits (`large_load_pilot.md`, section 1).
- What exists: two project-level public load queues (NYISO, 74 requests, 14,473.1 MW; Bonneville, 458 line and load
  requests since 2004); system totals in ERCOT's slide decks; forecast adjustments by zone in PJM's load forecast; a
  commercial site with 581 load requests in 11 states and none for Texas, Virginia, Georgia, Ohio or Arizona.
- The national dataset of interconnection queues (LBNL Queued Up) covers generators and storage and says it "does not
  include load interconnection requests".
- The figures that are public are large and do not agree in kind: Oncor "approximately 282 gigawatts from data centers"
  in its queue against 44 gigawatts "expected to be eligible as base or studied load" (6 August 2026); ERCOT 66.4 GW
  "conditionally included as base load" and 302.2 GW "excluded" (14 September 2026); PPL "over 240GW of large load
  interconnection requests" against 10,912 MW under signed agreements (29 September 2026); Dominion "Approximately 54GW
  of capacity under contract", 11,997 MW of it firm service agreements (29 September 2026); Georgia Power a pipeline of
  76,200 MW against 12,400 MW of commitments (15 May 2026). Sources: the table `large_load_statements`; addresses in
  `large_load_pilot.md`, section 4.
- Who decides on these numbers today: utility planners, commissions approving generation and transmission, grid
  operators forecasting load, and companies choosing sites. No source is cited here for how they use them; that is
  the owner's to state.
- **Do not write "no public dataset exists".** It is false for New York and the Pacific Northwest. The supported
  wording is that a search found no national, standardized, public dataset, and none of realized waits.

## 4. Question 4: the proposed solution (2025 limit: one uploaded page, figures allowed)

**The core: a public, versioned dataset of large load in line for power, by place and stage, every number tied to
the sentence it came from.**

- **The pilot shows it can be collected** (`large_load_pilot.md`, sections 2 and 3): ten utilities and operators; 107
  documents opened; 45 yielded a usable figure (42 percent); 110 statements verified by code as literal sentences of
  the documents held; 13 candidates rejected by the rule; about 50 minutes of an AI research agent's time in all.
  The internal table `large_load_statements` holds 49 of them and passed the ERW validator.
- **The rule:** no number without its sentence. The document is downloaded, its text extracted, the sentence checked
  by code to be a literal substring with the figure in it. Search summaries were wrong on a number or a date three
  times in one pass; each was caught by the rule.
- **What the pilot showed about the design:** stages must be kept in each document's own words, with at most a coarse
  class added by a person; nothing can be summed across entities; an operator's figures contain its utilities'; the
  words change within one company from quarter to quarter (Exelon: "committed" about 18 GW in May 2026, "High
  Probability Load" about 11 GW in July).
- **What the pilot could not do in an hour:** planning filings, rate case testimony and integrated resource plans
  (5 of 107 documents, 1 usable), because commission sites are searched docket by docket and several refuse a script.
- **What a full national build needs** (`large_load_pilot.md`, section 5): a list of about 60 to 80 entities; a
  document map for each; a quarterly collection on the order of 700 documents and 700 statements at the pilot's yield;
  a person or permissioned access for the dockets; a stage vocabulary beside the words; place by county or zone where
  stated, with the two public queues loaded as they are; waits measured from successive copies of the public queues
  (NYISO and BPA publish request dates and status) or from data that utilities and operators would have to release;
  each publisher's terms read before anything is published.
- **Where it would live:** the ERW's existing frame. Three table shapes and one validator (`docs/datastandard.md`,
  `warehouse/validate/erw_validate.py`), a source registry with a license for each of 260 sources, an archive, and
  Redivis with a draft that only a person releases (`evidence_pack.md`, sections 2, 3 and 5).
- **What it would sit beside:** the page "What a datacenter pays" (`/cost-of-power`, built in session 138, locked):
  for a load the reader describes, what power costs by hub and year, when the grid is tight, how clean it is, and how
  long generators wait. Its rows "Large load in line, by region" and "How long a new large load waits" are the
  placeholders the dataset would fill.
- A figure, if one is uploaded: the pilot's statements by entity with the stage as worded (the table is internal; a
  figure made from it for the letter is the owner's decision, since it publishes the statements).

## 5. Question 5: why an Accelerator project (2025 limit: 300 words)

- The Accelerator's own words on what it funds: "technical and policy solutions with near-term potential to move
  outside of Stanford and scale to meet real-world sustainability challenges"; "We seek project ideas with
  transformative rather than incremental potential"; projects positioned "to scale beyond Stanford within three
  years" (`call_requirements.md`, section 2).
- Facts on stage: the warehouse exists and runs daily (198 tables, 36,948,751 rows, all passing the validator, as of
  the daily run of 9 October 2026: `warehouse/metadata/coverage.csv`; 177 tables and 24,434,036 rows on 7 October);
  1,475 tests were collected on 7 October before sessions 138 and 139 added theirs, 2,610 passed in a clean copy on 9
  October (session 165's landing); every site page is in review since 9 October 2026 (three were open to visitors until
  then); nothing has been released on Redivis (`evidence_pack.md`, sections 2, 5 and 6; `redivis_release_checklist.md`).
- Facts on what funding would be for, from the pilot: people's time on dockets and on the stage vocabulary, access to
  commission sites, review of publishers' terms, and time (waits can only be measured from successive copies of the
  queues). No budget is proposed here.
- Facts on external parties: none is committed. The 2025 call: "Although external collaborators are not required for
  your project to be selected, it is an expectation that you will establish relationships with external collaborators
  early in the project."
- The ERW's infrastructure is adapted from the Item Response Warehouse, a Stanford project, with its owner's
  permission (`CLAUDE.md`).

## 6. Question 6: what makes it innovative (2025 limit: 300 words)

2025 criterion, quoted: "Transformative Potential / Innovation. Accelerator projects should be novel and ambitious in
scope. Reviewers will be familiar with target markets and will evaluate proposals in relation to existing solutions."

- **Against existing solutions** (`../paper/related_projects_notes.md`): LBNL Queued Up excludes load; NYISO and BPA
  cover their own systems; interconnection.fyi is free to browse, sells its export and reserves all rights; ERCOT and
  PJM publish totals and forecasts, not requests; commercial trackers (Cleanview, Aterio, Wood Mackenzie, GridTracker)
  were seen by name only and their fields, methods and prices were not read.
- **What is different in method:** every figure carries its sentence, document, page and address, and is checked by
  code; the stage is the document's wording; a public release is versioned with a DOI and each source's license is
  recorded per table.
- **What is not new, said plainly:** PUDL already publishes versioned, DOI-cited, validated federal energy data and is
  more rigorous on those filings; the queue data for generators exists; the ERW's price connectors are built on the
  gridstatus library.
- **Findings the same frame has already produced** (`evidence_pack.md`, section 8, each with its report and line):
  EIA's hourly California figures sat one hour late from 1 November 2023 to 2 December 2025; ERCOT's storage fleet was
  awarded USD 6.53 per kW day-ahead over January to July 2026, 22 percent of what a perfect-foresight model earns;
  solar's output in Texas's 100 tightest hours fell from 71.1 percent of its capacity in 2019 to 5.0 percent in 2025.
- From session 138: in 2023 a load that turned off in ERCOT's 100 dearest hours was off in 46 of the grid's 157
  tight hours; in 2025, in 3 of 140 (`SESSION_138_REPORT.md`).

## 7. Question 7: impact at scale (2025 limit: 300 words)

2025 criteria, quoted: "Impact ... Assessment will be based on (1) clarity of description of potential impact, (2)
intention and ability to quantify impact, (3) identification of beneficiaries." "Scalability ... the solution's
potential to scale ... whether through growth or replication".

- **Size of what is being measured, as the documents state it** (no sum is offered: the figures count different
  things and overlap): ERCOT "approximately 474 GW of Large Loads seeking interconnection, of which ~90% are data
  centers" as of June 2026 (`../paper/related_projects_notes.md`, section 3); Oncor 282 GW of data centers in its
  queue; PPL over 240 GW of requests; AEP about 195 GW of "active projects in the interconnection queue" and 69 GW of
  "contracted load growth through 2030"; Dominion about 54 GW under contract.
- **For scale against the system:** ERCOT's highest hour of demand in 2025 was 83,679 MW by its own file
  (`ercot_zone_load_hourly`); Far West Texas's average demand rose from 2,070 MW in 2015 to 7,478 MW in 2025
  (`SESSION_138_REPORT.md`).
- **Beneficiaries the facts name:** commissions and planners who approve generation and transmission against load
  forecasts; operators; researchers; companies siting load. How each would use it is not evidenced here.
- **Quantifying impact:** the repository holds no estimate of emissions avoided or people reached, and none should be
  written from it. What can be counted: entities covered, statements with sentences, the share of each entity's
  megawatts with a place, the number of realized waits measured, downloads and citations of a released version.
- **Scaling by replication:** the pilot took 1 to 8 minutes of agent time an entity for investor material (35 minutes for ten); the
  dockets are the part that does not scale without people or access.
- **The call's wording to meet:** "reducing greenhouse gas emissions by gigatons per year or improving the lives of
  one billion people". The link from a dataset of load queues to either is an argument the owner must make; the
  repository supplies no number for it.

## 8. Question 8: work completed to de-risk (2025 limit: 300 words)

2025 criterion, quoted: "Feasibility. For a solution to scale successfully, it must first show evidence of traction.
Feasibility assessment will consider (1) team constitution, (2) technical, economic, and political feasibility, (3)
projected market demand and (4) any other key dynamics".

- **The warehouse runs.** 198 tables, 36,948,751 rows, 307 sources in the registry, 164 tables public and 34
  internal, all passing the validator (`coverage.csv`, `sources.csv`, the daily run of 9 October 2026; on 7 October:
  177 tables, 24,434,036 rows, 260 sources, 148 public and 29 internal). A daily run on GitHub Actions, a 15-minute
  price run, a weekly roundup (`CLAUDE.md`).
- **The gate works.** One validator in front of every table; 28 known faults in source data recorded with what was
  done (`evidence_pack.md`, section 7).
- **The pilot is done** (section 4 above), and its table is in the warehouse's standard shape, validated, archived
  and in the private Redivis dataset's draft.
- **Licensing is handled per source.** A publisher whose terms forbid automated access is paused (MISO, 4 October
  2026); tables whose terms forbid republishing are internal (29).
- **A model reads documents under a rule that code enforces.** Session 138: 73 figures read from four Texas tariffs,
  each kept only with its line found on the page, for USD 0.30 of model spend; one wrong column was caught by reading
  the page and is not shown.
- **Risks the facts show:** one maintainer; nothing released yet (the checklist: 17 of 41 items done, 11 waiting on
  the owner); publishers' terms (three of four Texas utilities' tariff figures are held unshown on their terms);
  commission sites that refuse scripts; the stage vocabulary is a judgment; FERC's reported show cause orders of 18
  June 2026 on large-load rules were not verified and could change what is public.
- **Team:** not in the repository. The letter needs the principal investigator, the student lead, and the team table.

## 9. A line on what a PJM data license would add

- PJM's hub and zone energy prices and ancillary prices are not held: "PJM data terms bar non-members from
  republishing" (`evidence_pack.md`, section 3, from `docs/price-sources.md`). Its capacity prices are held and
  internal. So `/cost-of-power` shows PJM as "licensed source needed", and the price comparison, the price board, the
  battery model and the cost of power have no PJM row.
- The pilot's largest utility figures outside Texas are in PJM (Dominion, PPL, AEP Ohio, Exelon's ComEd and PECO,
  FirstEnergy). With a license, the page would price a load in those zones, and the large-load dataset could be set
  beside prices in the grid where much of the reported load is.
- What a license costs and what it permits was not researched.

## 10. Team tables and reviewers (the 2025 form)

- "Project PI": name, email, Stanford department, link to profile. **Not known to the repository.**
- "Stanford Team Members": name, email, title, department, role in one sentence.
- "External Collaborators": name, email, organization, link, role in one sentence. None committed.
- "External Reviewers": "Please suggest three reviewers, external to Stanford, who would be qualified to evaluate your
  project." None is suggested here.

## 11. What the owner must do or decide before 30 October

1. Open the 2026 RFP with a Stanford sign-in and check sections, limits, criteria and budget against section 0.
2. Name the faculty principal investigator and confirm the student lead role.
3. Decide whether any of the pilot's statements may appear in the letter or its figure (the table is internal).
4. Decide whether the first Redivis release happens before the letter (`redivis_release_checklist.md`).
5. Choose three external reviewers.
