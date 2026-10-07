# Session 139 report: the Stanford materials and a pilot of the missing dataset

Run on 7 October 2026 (UTC), unattended, the second and last session of the chain 138 to 139. Nothing here is a site
page. Everything is under `docs/accelerator/` and `docs/paper/`, with one internal table that is not in the repository.

## Seven things to know before anything else

1. **I pushed this session's deploy without taking a new before snapshot.** The command that should have taken it
   was chained behind a check that failed for an unrelated reason (my branch did not hold main's merge commit), and
   the push that followed it ran anyway. The snapshot I used as "before" is the one taken at 02:32:34 UTC, after
   session 138's deploy and six minutes before this push; GitHub shows no deployment between the two. Compared with
   the after snapshot (02:47:02 UTC): **0 differences on the 25 live addresses, 3,357 checked number keys.** The deploy
   changed documents, one connector, tests and metadata, and no page. The rule was still broken, and you should know.
2. **"No public dataset exists" is false, and the materials do not say it.** NYISO publishes a project-level queue of
   load requests (74 requests, with megawatts, county, zone, request date and status) and Bonneville a line and load
   queue (458 requests since 2004). What a search on 7 October did not find: any national, standardized, public
   dataset; any public list by place for Texas, Virginia, Georgia, Ohio or the PJM utilities; and any dataset, for any
   grid, of how long a large load waited. The letter's facts say "a search found none", and say why not to write more.
3. **The call was found and its dates are yours, but its full text is behind a Stanford sign-in.** Issued 23
   September 2026; letters 30 October; invitations 11 November; proposals 15 December; projects start by June 2027.
   The length, the questions, the criteria and the budget of the 2026 call were **not found**; the Fall 2025 call's
   are quoted in their place, labelled as an earlier call. Someone with a Stanford account must open the link and
   compare.
4. **The letter needs a faculty principal investigator, and a student is a required role, not the lead applicant.**
   Quoted from the 2026 public pages: "Stanford faculty members or Stanford and SLAC researchers who qualify as a
   principal investigator according to Stanford University policy", and "Teams must include a designated postdoctoral
   researcher or student lead". No principal investigator is named anywhere in the repository.
5. **The repository is public, so the pilot's table is not in it.** `large_load_statements` is on the data machine
   (`warehouse/output/`), in the archive and in the private Redivis dataset's draft. The documents under
   `docs/accelerator/` quote a handful of its sentences as examples, each from a public filing with its address; they
   are in the public repository because you asked for them there.
6. **The pilot verified 110 statements; the table holds 49.** You asked for 30 to 50. The table takes at most five an
   entity by a written rule (newest document first, its largest figure first, a new stage before a repeated one; a row
   resting on a third party's copy is not taken). The other 61 are kept beside it.
7. **Model spend was USD 0 of the USD 5 cap.** No code of the repository called a model. The research was done by
   this session's own agents with web search, which is not what the ledger counts; if you count it differently, that
   is what happened.

## Verdict

Nothing to open. **The materials are ready for you to write from; four things are left that only a person can do:**

1. Open the 2026 RFP with a Stanford sign-in and check the letter's sections, limits, criteria and budget against
   `docs/accelerator/call_requirements.md`, section 4.
2. Name the faculty principal investigator and the team; choose three external reviewers.
3. Decide whether any of the pilot's statements may appear in the letter or in a figure.
4. Decide whether the first Redivis release comes before the letter: `docs/accelerator/redivis_release_checklist.md`,
   17 of 41 items done, 13 not done, 11 waiting on you.

## What was asked for, and what was written

| | Asked | Written |
|---|---|---|
| (a) | The call's requirements for the letter, quoted; if not found, say so | `docs/accelerator/call_requirements.md`. The 2026 call: dates, eligibility, the eight areas and the submission system quoted from its public pages; length, questions, criteria, budget not found and said so. The Fall 2025 call (37 pages, public) quoted in full for those, labelled earlier |
| (b) | An evidence pack, facts only, each with its place in the repository | `docs/accelerator/evidence_pack.md`, ten sections and an eleventh for what sessions 138 and 139 changed: what the ERW is, its tables, sources and licenses, coverage by grid and year, the validator and tests, the tools, the known faults, the ten strongest findings with ten more, the cost of operation, what is not done |
| (c) | The gap with evidence; a pilot of ten entities, 30 to 50 statements, internal; how long each took, the share of documents that yielded a figure, what a national build needs | `docs/accelerator/large_load_pilot.md`; the table `large_load_statements`, 49 statements, internal; `warehouse/connectors/large_load_statements.py` (its rule) |
| (d) | The letter's facts against the call's sections, bullets with sources, no persuasion; the gap and the pilot as the core; a line on a PJM license | `docs/accelerator/letter_facts.md`, against the eight questions of the 2025 form, with what is not known at the top and what you must decide at the end |
| (e) | A paper outline: the question, what the ERW adds beside existing projects said honestly, the standard and validation as method, three demonstrations | `docs/paper/outline.md`, with `docs/paper/related_projects_notes.md` (fourteen projects and products, each fact with its address) |
| (f) | A checklist for a first citable Redivis release, done and waiting | `docs/accelerator/redivis_release_checklist.md`, 41 items |

## The pilot

| | Both passes |
|---|---|
| Entities | 10: Dominion Energy Virginia, Georgia Power, Duke Energy, Entergy, PJM, Oncor, CenterPoint, AEP, Exelon, ERCOT |
| Documents opened | 107 |
| Documents that yielded a usable figure | 45, or 42 percent |
| Statements verified by code against the document held | 110 |
| Candidates the rule rejected | 13 |
| In the internal table | 49 |
| An agent's minutes searching and reading | 35.4 |
| An agent's minutes on the table, the checks and the notes | about 14 |

**How long each took** (an agent's clock; a person would need hours): Dominion 6.3 minutes, Georgia Power 1.5, Duke
1.8, Entergy 3.3, PJM 5.0, Oncor 7.9 (4.1 of them two timeouts), CenterPoint 1.3, AEP 0.8, Exelon 0.8, ERCOT 1.4, and
a second pass of 5.3 minutes across the last five.

**Yield by kind of document:** earnings presentations 11 of 17, earnings releases 6 of 9, load forecast submissions 9
of 13, operator reports 8 of 18, SEC filings 3 of 20, commission filings 3 of 11, resource plans 1 of 4, rate case
testimony 0 of 1.

**What a full national build would require** (`large_load_pilot.md`, section 5): about 60 to 80 entities; a document
map for each; a quarterly collection on the order of 700 documents; a person or permissioned access for commission
dockets; a stage vocabulary kept beside the documents' own words; waits measured from successive copies of the two
public queues, or released by utilities; every publisher's terms read before anything is published.

**Nothing was summed across entities.** The table's header says DO NOT SUM, and why.

## Every pull against its ceiling

No data pull was approved for this session and none was made into a warehouse source table. **No MISO request. No PJM
data request** (PJM's public committee documents were read as documents; no Data Miner, no API).

- Web search and reading, for the call and the related projects.
- The pilot downloaded the 107 documents it opened (SEC EDGAR, utilities' and operators' public pages, commission
  sites), with a declared research agent on EDGAR. They are under `warehouse/raw/large_load_pilot/` (239 MB, not in
  git).
- The publishers' terms were not read one by one, which is why the table is internal.

## Model spend: USD 0 of the USD 5.00 cap

No call in the ledger for session 139. No stage was refused, because none was started. (Item 7 above.)

## The deploys

Freeze: on, relaxed by the chain prompt for locked pages. Neither deploy changes any page.

| Deploy | What | Before and after | Vercel |
|---|---|---|---|
| 1 | The documents, the table's builder, its test, the holds in `live_set.yaml`, metadata, session 138's report. Checks passed (run 37562914655), merged as `b09b8af` | Before: the snapshot of 02:32:34 UTC (item 1). After: 02:47:02 UTC. **0 differences**, 3,357 keys | "Deployment has completed" at 02:46:31 UTC |
| 2 | This report | Its snapshot is taken before and after, as the rule says. **If it shows any difference, a line is added at the very top of this report; no such line means 0 differences** | the same |

No table a live page reads was written. Nothing was loaded into Supabase. Nothing was released on Redivis.

## Checks

| Check | Result |
|---|---|
| `tests/test_session139.py` | 6 tests: no number without its sentence; a CAUTION row not taken; at most five an entity, newest and largest first, a new stage before a repeated one; a range kept as a range; the table internal, held off the live set and absent from the repository; every document in place with no em dash and saying what the evidence supports |
| The ERW validator on `large_load_statements` | exit 0: events shape, 0 errors, 0 warnings, 49 rows |
| Coverage (`--only`), the archive, the internal Redivis draft | exit 0 each: 49 rows; `count(*)` 49 in `energy_research_warehouse_internal`; nothing released |
| Each pass's own verification | 0 of 52 and 0 of 58 statements failed the literal-sentence check |
| The whole suite and the site's checks on GitHub | passed (run 37562914655) |

## The five most interesting numbers

1. **282 gigawatts in the queue, 44 expected to count.** Oncor, 6 August 2026: "approximately 282 gigawatts from data
   centers" in its transmission interconnection queue, and 44 gigawatts "expected to be eligible as base or studied
   load" in ERCOT's first batch study. ERCOT's highest hour of demand in 2025 was 83,679 MW.
2. **One measured wait in 107 documents.** ERCOT's 2025 long-term load forecast gives an "average project delay of 180
   days". Nothing else states how long a large load waited; everything else is a deadline, a horizon or the word
   "uncertain". This is the gap.
3. **30,000 MW of requests, 13,022.7 MW that paid for a study, 5,642 MW under binding contracts.** AEP Ohio, 13
   February 2026: one utility's funnel, in its own three stages, and the reason no two entities' figures can be added.
4. **42 percent of documents opened yielded a usable figure, and it took 35 minutes of search for ten entities.** The
   collecting is cheap. The reading of dockets, the stage vocabulary and the terms are what a project would pay for.
5. **Three times in one pass a search summary gave a wrong number or date, and the sentence rule caught each.** And
   in session 138 the model read one tariff figure from the wrong column of a nine-column table. A dataset of this
   kind is only as good as the line that can be shown for each figure.

## Decisions I made without you

1. **The ten entities were chosen before the search**, as those believed to report the most datacenter load, not
   ranked from data: no such ranking can be made across stages. The pilot found figures as large outside the ten (PPL
   "over 240GW" of requests; FirstEnergy "102 GW" of study requests); they are in the table under PJM, which posts
   them.
2. **The table takes 49 of 110 by rule**, so its content is not my choice row by row. Entergy has four: its documents
   state only ranges.
3. **Tier `model_extracted`**, because an AI agent read the documents, although every sentence was then checked by
   code.
4. **The table went to the archive and to the private Redivis dataset's draft**, as internal tables do. If "nothing
   published" meant not even that, it is one table to remove from one draft.
5. **The letter's facts follow the 2025 form's eight questions**, the newest that could be read.
6. **The paper outline's three demonstrations**: EIA-930 against CAISO's own data; the battery model against ERCOT's
   disclosed awards; the tight hours and what flexibility is worth (from session 138).
7. **The evidence pack and the checklist were counted before session 138**; each has a dated section for what the two
   sessions changed, instead of being recounted.
8. **Two holds were added to `warehouse/supabase/live_set.yaml`** so that the two internal tables of this chain and
   their sources stay off the site's catalogue and its terms page.

## Not done

- The 2026 RFP was not read (a sign-in).
- No integrated resource plan or rate case testimony was reached for seven of the ten entities.
- The commercial trackers' fields, methods and prices were not read.
- FERC's reported show cause orders of 18 June 2026 were not verified from a primary document.
- The publishers' terms for the pilot's documents were not read one by one.

## For Samuel

1. The four things under "Verdict".
2. Rule on the Texas tariffs' terms and ISO-NE's demand (session 138's report, top).
3. After 7 October: the two label changes of session 138's "To finish".
4. Delete the remote branches `wip/138-datacenter` and `wip/139-stanford` once the reports are on main, if I have not.
