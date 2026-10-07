# The gap, and a pilot of the missing dataset

Session 139, 7 October 2026. Facts only. Where a fact comes from a document outside the repository, its address is
given; where it comes from the pilot's files, the file is named. The pilot's table is internal and is not in this
repository (which is public): it is `warehouse/output/large_load_statements.csv` on the data machine, with the
passes' files and every downloaded document under `warehouse/raw/large_load_pilot/`. The few sentences quoted below
are from public documents and are here as examples, each with its address.

## 1. The gap, stated with the evidence found

**The claim tested:** no public dataset exists of how much large load is in line for power by place, or how long a new
large load waits.

**What a search on 7 October 2026 found** (`docs/paper/related_projects_notes.md`, section 3, where every line has its
address):

| What | Public? | What it holds | What it lacks |
|---|---|---|---|
| NYISO interconnection queue workbook, sheets "Load Projects" and "Load Project Tracking" | Yes | 74 load requests with request date, peak MW, end use, county, zone, status; megawatts by zone and status (New York Control Area total 14,473.1 MW) | New York only; no date of energization |
| Bonneville Power Administration interconnection request queue | Yes | 458 line and load requests since 2004 with request date, state, county, status, requested in-service date, MW | BPA's system only; lines and loads of every size together; no end use; no actual energization date |
| interconnection.fyi (GridTracker) | Free to browse, export paid, "All rights reserved" | 581 load requests, 90.84 GW, in 11 states | No rows for Texas, Virginia, Georgia, Ohio or Arizona; not openly licensed |
| ERCOT large load updates | Slide decks | System totals by date and status group (about 474 GW "seeking interconnection" as of June 2026) | No project list, no table by county or zone, not machine-readable |
| PJM load forecast, large load adjustments | Yes | Forecast adjustments to peak by transmission zone and year | A forecast accepted by PJM, not requests; no request dates, no waits |
| LBNL Queued Up | Yes | Generator and storage requests nationally | "does not include load interconnection requests" |

**So the claim, as the evidence supports it:**

1. **By place.** Two operators publish project-level load request lists (NYISO, BPA). For the places where most of the
   load is reported (Texas, Virginia, Georgia, Ohio, the PJM utilities), no public list by county, zone or utility was
   found; the figures are totals in slide decks, forecasts by zone, or filings with the place redacted.
2. **How long a load waits.** No public dataset of realized waits (request to energization) for large loads was found,
   for any grid. In the pilot's 107 documents one measured figure appears (ERCOT: an "average project delay of 180
   days", in its 2025 long-term load forecast report); everything else is a deadline, a horizon or the word
   "uncertain".
3. **One national file.** No single public, standardized, openly licensed dataset of large-load requests across
   operators and utilities was found.

The supported wording is "a search found none", not "none exists". The strict form of the claim ("no public dataset
exists") is false for New York and the Pacific Northwest and should not be written that way.

Not verified from primary documents: a law firm's page reports that FERC issued show cause orders on 18 June 2026 to
six grid operators on large-load integration rules. If so, the public record may change during a funded project.

## 2. The pilot

**Question.** Can the scattered statements be collected into one table with every number tied to the exact sentence
it came from?

**Entities.** Ten, chosen before the search as the utilities and operators believed to report the most datacenter
load in public filings: Dominion Energy Virginia, Georgia Power (Southern Company), Duke Energy, Entergy, PJM
Interconnection, Oncor Electric Delivery, CenterPoint Energy Houston Electric, American Electric Power, Exelon, ERCOT.
The choice was not a ranking from data, because no such ranking can be made (section 4).

**Method.** Two research passes of five entities each, by an AI research agent with web search, on 7 October 2026.
For each statement the document itself was downloaded, its text extracted, and the sentence checked by code to be a
literal substring of that text (white space normalized) with the megawatt or gigawatt figure in it. A candidate that
failed was kept in a rejects file with the reason. Nothing was summed, netted, converted or annualized across
statements. The stage is recorded in the document's own words.

**The rule.** No number without its sentence.

## 3. The result

| | Pass A (Dominion, Georgia Power, Duke, Entergy, PJM) | Pass B (Oncor, CenterPoint, AEP, Exelon, ERCOT) | Both |
|---|---|---|---|
| Documents opened | 58 | 49 | 107 |
| Documents that yielded a usable figure | 20 | 25 | 45 (42 percent) |
| Statements verified by code | 52 | 58 | 110 |
| Candidates rejected by the rule | 5 | 8 | 13 |
| Minutes searching and reading, by the agent's clock | 17.9 | 17.5 (first and second pass) | 35.4 |
| Minutes on the table, the checks and the notes | about 8 | 6.3 | about 14 |

Source: `timing.csv`, `documents.csv`, `statements.csv`, `rejects.csv` of each pass.

**The internal table, `large_load_statements`: 49 statements.** The owner asked for 30 to 50. The table takes at most
five for each entity, by a written rule (`warehouse/connectors/large_load_statements.py`): a row its collector marked
as resting on a third party's copy is not taken; within an entity the newest document first and, among a document's
figures, the largest first; a stage not yet held before one that repeats. Entergy has four (its documents state only
ranges). The other 61 verified statements are outside the table: 60 in `not_taken.csv`, and one whose figure
is spelled in words ("five gigawatts"), which fails the builder's digit check and stays in its pass's file. The table passes the ERW validator
(events shape, 0 errors, 0 warnings).

**How long each entity took** (minutes of the agent's clock for searching and reading; a person would need hours):

| Entity | Minutes | Documents opened | With a usable figure | Statements verified | In the table |
|---|---|---|---|---|---|
| Dominion Energy Virginia | 6.3 | 14 | 7 | 18 | 5 |
| Georgia Power (Southern Company) | 1.5 | 6 | 4 | 13 | 5 |
| Duke Energy | 1.8 | 8 | 2 | 8 | 5 |
| Entergy | 3.3 | 12 | 2 | 4 | 4 |
| PJM Interconnection (one row of its own; the rest are members' submissions PJM posts) | 5.0 | 18 | 5 | 9 | 5 |
| Oncor Electric Delivery | 7.9 (4.1 of them two timeouts) | 9 | 3 | 11 | 5 |
| CenterPoint Energy Houston Electric | 1.3 | 8 | 5 | 10 | 5 |
| American Electric Power | 0.8 | 4 | 4 | 9 | 5 |
| Exelon | 0.8 | 11 | 3 | 7 | 5 |
| ERCOT | 1.4 | 14 | 10 | 21 | 5 |

Pass B's counts by entity include its second pass (5.3 minutes across the five, not split by entity) and three
documents outside the five. AEP and Exelon rows that pass A found among PJM's posted submissions are counted under
PJM in the "verified" column and under their own entity in the table.

**Share of documents that yielded a usable figure, by kind of document** (both passes, `documents.csv`):

| Kind | Opened | Usable |
|---|---|---|
| Earnings presentation | 17 | 11 |
| Earnings release | 9 | 6 |
| Load forecast report (most are utilities' submissions to PJM's load analysis subcommittee) | 13 | 9 |
| Operator report | 18 | 8 |
| SEC filing (10-Q, 10-K, 8-K body) | 20 | 3 |
| Commission filing | 11 | 3 |
| Integrated resource plan | 4 | 1 |
| Rate case testimony | 1 | 0 |
| Other | 14 | 4 |

## 4. What the pilot showed

1. **It can be collected, with the sentence.** 110 statements from 45 documents in about 50 minutes of an agent's time,
   every one verified by code against the document held.
2. **The stages do not line up, so nothing can be summed.** Examples, each a row of the table:
   - Oncor, release of 6 August 2026: "approximately 282 gigawatts from data centers" in its "active transmission
     LC&I interconnection queue"; in the same release 44 gigawatts "expected to be eligible as base or studied load".
     `https://www.oncor.com/content/oncorwww/wire/en/home/newsroom/oncor-reports-second-quarter-2026-results.html`
   - ERCOT, board materials of 14 September 2026: 66.4 GW "conditionally included as base load", 127.9 GW as studied
     load, and "excluded load (302.2 GW, 373 projects)".
   - PPL Electric Utilities, submission to PJM of 29 September 2026: "Since Sept 2024, PPL has received over 240GW of
     large load interconnection requests", against 10,912 MW under a signed service or construction agreement.
     `https://www.pjm.com/-/media/DotCom/committees-groups/subcommittees/las/2026/20260929/20260929-item-5e---ppl.pdf`
   - Dominion Energy, submission to PJM of 29 September 2026: "Approximately 54GW of capacity under contract (ELOA,
     CLOA, ESA)", of which 11,997 MW is "Electric Service Agreements (ESA - Firm)".
   - Georgia Power, filing of 15 May 2026: a "total pipeline of economic development projects" of 76,200 MW against
     12,400 MW of "commitments".
   A request, a study, a letter of authorization and a signed agreement are different things, and each company draws
   the lines in its own place. ERCOT's figures also contain the Texas utilities' requests, so adding an operator and
   its utilities counts load twice.
3. **The words change within one company from quarter to quarter.** Exelon: "committed" (about 18 GW, May 2026) became
   "High Probability Load" (about 11 GW, July 2026). CenterPoint: "firmly committed" (April) became "eligible as base
   load or studied load" (July).
4. **What is easy to reach is investor material.** Earnings releases and decks are quarterly and recent, and SEC EDGAR
   serves them to a declared research agent. Planning filings, rate case testimony and integrated resource plans,
   where a stage has a legal meaning, mostly were not reached in an hour: commission sites are searched docket by
   docket, several refuse a script, and the first results are third parties' filings. Five of 107 documents were
   resource plans or testimony; one yielded a figure.
5. **Waiting time is the real gap.** One measured figure in 107 documents (above).
6. **Place is coarse.** The finest grain stated in words is the utility's service territory or a PJM zone. ERCOT's
   board deck names counties and megawatts, but as chart labels, which the rule cannot verify as sentences.
7. **The sentence rule earned its place.** Search summaries were wrong on a number or its date three times in pass A
   alone; each was caught because the sentence was not in the document. One ERCOT deck states one quantity two ways
   (127.9 GW on a page, 125.4 GW in a chart label).
8. **Half the usable material is slides.** A slide line verifies as literal text, but which bar or column a number
   belongs to is a person's reading, recorded in the row's notes.

## 5. What a full national build would require

Stated from the pilot's experience; none of this is built.

1. **A list of entities.** About 60 to 80: the seven grid operators and BPA, and the investor-owned and large public
   utilities with large-load activity. The pilot's ten took one research hour; it also showed that entities outside
   the ten (PPL, FirstEnergy) report figures as large as those inside.
2. **A document map per entity.** Where its figures appear and how often: the quarterly release and deck, the 10-Q
   paragraph, the annual resource plan, the load forecast docket, the operator's stakeholder committee. The pilot's
   notes hold this for the ten (`notes.md` of each pass, under each entity).
3. **A quarterly collection.** For investor material a pattern can read stable sentences (Oncor's two sentences have
   the same wording each quarter); for slides and dockets a person or a model reads and the code verifies. At the
   pilot's yield (42 percent of documents usable, about 2.4 verified statements a usable document) a quarter of 70
   entities is on the order of 700 documents opened and 700 statements.
4. **The dockets.** A person, or permissioned access, for the commission sites that refuse scripts (the pilot met
   Georgia, Virginia and North Carolina) and for the planning filings and testimony where stages are defined. This
   is the part an hour could not do and the part that carries the legal meaning.
5. **A stage vocabulary added beside the words, never in place of them.** A coarse class a person assigns (request or
   inquiry; study or engineering letter; financial commitment or construction letter; signed service agreement; under
   construction or energized), with the document's own words kept. Without it no two entities can be compared; with
   it they can be compared only within a class.
6. **Place.** County or zone where a document states it; the two public queues (NYISO, BPA) loaded as they are; the
   service territory otherwise. Geography files for utility territories already exist publicly.
7. **Waits.** Not collectable from statements. Measurable only from successive copies of a queue (NYISO and BPA
   publish request dates and status; saving each monthly file gives the date a status changed), or from data that
   utilities or operators would have to release. This needs time or partners, not search.
8. **Terms.** Each publisher's terms read and quoted before anything is published; the pilot read none one by one,
   which is why its table is internal.
9. **The ERW's existing frame.** The table is in the events shape and passed the validator on its first run; the
   source registry, the license field, the archive and the draft-then-release rule already exist.

## 6. Files

| File | Where | In git |
|---|---|---|
| `large_load_statements.csv`, 49 statements, internal | `warehouse/output/` | no |
| The two passes: `statements.csv`, `rejects.csv`, `documents.csv`, `timing.csv`, `notes.md`, the checking scripts, the documents as downloaded | `warehouse/raw/large_load_pilot/A` and `B` | no |
| `not_taken.csv`, the verified statements outside the table | `warehouse/raw/large_load_pilot/` | no |
| The builder and its rule | `warehouse/connectors/large_load_statements.py` | yes |
| The search for existing datasets | `docs/paper/related_projects_notes.md`, section 3 | yes |
