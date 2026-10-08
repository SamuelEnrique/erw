# Session 154 report: rules in motion for large loads

Run on 8 October 2026 (UTC), unattended. Six agents worked to written briefs under `runs/session154/`: one audited
the policy actions, three pulled the regulators' dockets, one built the tags, the tables, the reads and the ten
rules, one built the block on the page. I ran the locked writes, a trial of the fixed connector, the merged build
and the landing. Scope held throughout: federal regulators, state commissions and grid operators; nothing municipal.

## Six things to know first

- **A decision of mine for you to confirm: whose sentences the page shows.** You asked for each rule "with the
  exact sentence that states what it does". Every row holds its sentence, proved in the saved document. But the
  Texas commission's own policy says "all PUCT content is protected by federal copyright laws" and asks that
  permission to copy be requested; Indiana's terms give "a limited, nonexclusive license for use solely by you";
  Georgia's pages end "All rights reserved". For those, and for the three whose terms no agent could read (FERC,
  Virginia, Ohio), **the page shows the facts of each row (date, regulator, docket, status class, the link to the
  regulator's own document) and the model's one-line read, and not the regulator's sentence**; the full rows are in
  an internal table. Sentences are shown for California, Oregon, Arizona, Pennsylvania and Illinois. Two constants
  change it either way (`OFF_PAGE_REGULATORS`, `SHOW_SENTENCE_REGULATORS` in `warehouse/derived/rules_in_motion.py`).
- **FERC's sentences are withheld only because ferc.gov refused every page with a browser check**, so its terms
  could not be quoted. A FERC order is a work of the United States government. This is the one I most expect you to
  reverse: one line.
- **Only California's terms speak of reuse** ("It may be distributed or copied as permitted by law"). Oregon's,
  Arizona's, Pennsylvania's and Illinois's statements are about access to public records. I counted access as
  enough to show a sentence; if it is not, 30 rows move to the internal table by four words in one file.
- **"The 1,843 policy reads" are the policy actions.** `policy_actions` holds 1,843 rows; `policy_reads` holds 234.
  The 50 were drawn from the actions, and the 9 of them that have a read were checked there too.
- **The audit's fixes change 911 of the rows when the connector next runs, and the table is not rewritten yet.**
  The daily run at 14:00 UTC rewrites it: the runner holds the current news tables the links are made from; this
  machine's are days behind. No live page reads it.
- **Tax credits: no action is tagged, because no Treasury or IRS source is held.** The tag exists in the rule and
  matches nothing in the 1,843. Only 14 actions carry any of the four tags.

## Verdict: the block is built and locked; the table is small and honest; the audit found the derived fields weak

What is left, exactly:

1. **Your ruling on the sentences** (above), and on FERC's first.
2. **The dockets that refuse a plain request are thin.** Ohio's 10 rows hold the commission's docket-card summary
   of each filing (its documents sit behind a reCAPTCHA), and Illinois's 9 come from its meeting minutes, agendas
   and suspended-cases list (its docket page refuses robots). Each says what it is cut from. About 940 of Ohio's
   975 electric cases of 2025 and 2026 were not opened.
3. **A docket system cannot be proved complete from outside.** Each pass says how its list was found and what it
   knows it did not reach (named in each pass's `notes.md`): FERC's eLibrary (a form), several FERC compliance and
   rehearing orders, the adopted texts of four California resolutions, Arizona's scanned decisions.
4. **18 of 50 sampled actions lack a state the document names.** The place is in the document's first paragraph,
   which the connector does not request: about 850 requests to read once. Not a pull you named; not made.
5. **1,086 of 1,843 actions are scored on a title alone**, and the model's unsupported fields come from there. The
   prompt changes are written down; nothing was rescored (no model call for it).
6. A Treasury and IRS source, if tax credits are to be tagged at all.
7. The menu change and the grid network fix are still held until 18:00 UTC today (sessions 146 and 149).

## (a) Fifty policy actions against their source documents

- **The sample:** `random.Random(154).sample(sorted(event_id), 50)`, saved before any fetch. Every source was
  reachable: 0 of 50 missing, none swapped. 43 Federal Register documents (each checked against its API record and
  its printed text), 5 NRC releases, 1 California item, 1 release on the Texas commission's page.
- **940 checks, 53 errors, in 30 rows.**

| Field | Errors | Of |
|---|---|---|
| action type, docket, RIN, document number, source, address, status | 0 each | 50 |
| date, agency, title, abstract | 1 each | 50 |
| **states** | **20** (18 missing, 2 wrong) | 50; 20 of the 30 rows whose document names a place |
| **sector tags** (the connector's keyword rule) | **19** (17 missing, 2 wrong) | 50 |
| why (a model's) | 4 unsupported | 50 |
| sector (a model's) | 3 unsupported | 50 |
| significance (a model's) | 49 follow the rubric; 1 rests on a title the Register cuts short | 50 |
| the read's sectors, states, price direction | 1 unsupported each | 9 reads |
| the read's other fields | 0 | 9 reads |

- A rate on 50 is a small sample: 1 in 50 is 2 percent (about 0 to 11); 20 in 50 is 40 percent (about 28 to 54).
- **One cause is behind most of it:** a FERC notice has no abstract in the Register's record (834 of the 839 FERC
  notices held). The state is then missed or read off a company's name, the tags are empty, and the scorer rates a
  title. All 7 unsupported `why` and `sector` values are such rows.
- **Fixed in `policy_sources.py`, each with a test on a saved real document:**
  - tags by agency and FERC docket class (a certificate docket is gas; a project docket is hydropower);
  - an NRC or DOE release dated by the day in Washington, not the UTC day (24 of the feed's 167 items carried the
    next day);
  - West Virginia no longer also Virginia; Washington, DC not the state;
  - the Register's inline markup ("NO X");
  - a release of the Governor's office on the Texas commission's page names its issuer.
- **My trial of the fixed connector against the real sources** (its own routine pull, into a separate folder):
  exit 0, validator pass, 1,850 rows. Against the table held, 911 rows differ: sector tags 843, abstract 32, date
  23, parties 16, states 11.
- **Not fixed, and why:** the 18 missing states (item 4 above); 2 titles the Register's record cuts short; the
  model's 9 unsupported fields (both texts and the proposed prompt changes are in
  `warehouse/policy/eval/audit_s154_errors.csv` and the agent's notes; no row was edited).
- For your eye: `what_changes` is blank in 55 of the 234 reads, dropped by the reader's own number check.

## (b) The pull: proceedings and orders at FERC and ten commissions

| Pass | Regulators | Rows | Requests | Megabytes |
|---|---|---|---|---|
| A | FERC, Texas, Virginia | 52 | 149 | 130 |
| B | Ohio, Indiana, Pennsylvania, Illinois | 36 | 252 | 45 |
| C | Georgia, Arizona, Oregon, California | 30 | 104 | 114 |
| **All** | | **118 of the 20,000 allowed** | **505** | **290** |

- **116 rows taken, each proved a second time by the connector** (the sentence a literal substring of the saved
  text, with its page); 2 left out (an Oregon page with no date; an Illinois order whose docket the regulator's own
  words do not tie to it). 49 proceedings and 67 orders. Each with its docket number, date, status, address and
  sentence; a field a document does not state is empty.
- By regulator: Texas 18, Virginia 18, FERC 16, California 13, Ohio 10, Pennsylvania 9, Illinois 9, Indiana 7,
  Oregon 7, Arizona 5, Georgia 4.
- **What a sentence is cut from:** 87 from the document's own text; 29 from the regulator's own record (Ohio's
  docket cards 10, Illinois's minutes, agendas and list 9, Arizona's news releases 4, others 6). Flags: 12
  single-customer contracts, 4 California draft resolutions (their status reads "not stated", never "adopted"), 4
  rows whose docket number is not in their own document.
- **Two tables, by each regulator's terms:** `large_load_rules` (public, 43 rows) and `large_load_rules_internal`
  (73 rows). Neither is loaded; the page reads a site file.
- **Contact string: exactly "ERW research project, github.com/SamuelEnrique/erw". No address sent. No address
  holding a filer's e-mail was requested.** No request to misoenergy.org (MISO's order was read from ferc.gov's
  file), no PJM Data Miner or API.
- **Refused a plain request and left:** every ferc.gov page (browser check; the order files answered); Ohio's
  docketing system (reCAPTCHA) and puco.ohio.gov (404 to six requests); Illinois's docket page ("Please, no robots
  or crawlers beyond this point."); Arizona's document host (HTTP 500 three times; the host with a certificate
  mismatch was not requested).
- **Terms quoted** (each with its saved page's hash, in the Method note and
  `warehouse/config/large_load_rule_terms.json`):
  - California: "In general, information presented on this web site, unless otherwise indicated, is considered in
    the public domain. It may be distributed or copied as permitted by law."
  - Oregon: "Most information collected by state government is assumed to be open to the public unless
    specifically exempted."
  - Arizona: "In other words, much of the information you disclose to us becomes a matter of public record as
    required by law."
  - Pennsylvania: "Persons requesting copies of public records maintained by the Commission must submit a written
    request to the Commission's Open Records Officer."
  - Illinois: "Information collected and received through the Illinois Commerce Commission web site may become
    public record and therefore subject to disclosure under the Illinois Freedom of Information Act."
  - Texas: "all PUCT content is protected by federal copyright laws" (its link policy; the sentence in full is in
    the Method note).
  - Indiana: "Except as may otherwise be allowed by law (including but not limited to the Indiana Access to Public
    Records Law), the viewing, printing, or downloading of any content, graphic, form, or document from the Portal
    grants you only a limited, nonexclusive license for use solely by you".
  - Georgia: "Request in writing by any person pursuant to the Georgia Open Records Act, O.C.G.A. Section 50-18-70,
    et seq.", and every page's footer, "All rights reserved."
  - FERC, Virginia, Ohio: none could be read.
- The audit's own fetch: 101 requests, 8.1 MB, of 200 requests and 200 MB; and my trial of the connector's routine
  pull (the sources it reads every day).

## (c) The tags

- **The rule is written before it is run and published** (`docs/methods/policy_action_tags.md` and a file the code
  reads): for each tag its terms, the fields read, what excludes (gas pipelines' and telecommunications'
  "interconnection"; a tax credit that is not an energy credit), and that anything municipal is never tagged in.
- **14 of the 1,843 actions carry a tag; 30 tag rows**: transmission cost 12, large load 10, interconnection 8, tax
  credit 0. Each row names the term that matched and the field it matched in.
- Read by the agent: of the first version's tagged rows, 5 of 7 were right strictly; the rule was corrected once;
  then 14 of 14. 102 untagged rows read in all: no miss found.

## (d) "Rules in motion" on `/cost-of-power`, in "How soon"

| Grid | Rows | With a model's read | Sentence withheld |
|---|---|---|---|
| ERCOT | 8 | 8 | 8 |
| PJM | 41 | 38 | 25 |
| CAISO | 15 | 13 | 2 |
| NYISO | 3 | 2 | 2 |
| ISO-NE | 2 | 0 | 1 |
| SPP | 8 | 6 | 7 |
| MISO | "paused while terms are reviewed", no row | | |
| Federal, all grids (under each but MISO) | 5 | 2 | 1 |

- **In motion:** an open proceeding, or an order or rule of the last 12 months, from the two tables and from the
  tagged federal actions held. 48 rows in motion are on no grid: Oregon's, Arizona's and Georgia's have no
  organized market on the page; a row about one MISO utility is not placed.
- **Which grid sees a row, by a written rule:** an action whose words name an operator; a statewide rule under its
  state's operator; a row about one named utility under that utility's own operator (24 utilities listed with the
  source of each). **As first built, a Texas case of El Paso Electric sat under ERCOT and two of Southwestern
  Electric Power's did too: corrected before the landing** (8 rows moved).
- Each row: the date; the status as the regulator words it, else its class; the regulator and docket as a link to
  the source document; the one-line read with the mark "model's read" (its hover names the model and what the line
  was made from); the sentence, or the withheld phrase, with the page and topic on hover. Eight rows a group, the
  rest behind a fold. No method prose on the face.
- **PJM's rows are shown; PJM's prices still read "licensed source needed".** A PJM or MISO address shows, outside
  the block, exactly what the default address shows. The six rows of "How soon" are as they were.
- **The reads:** 87 of the 92 rows in motion have one; 5 read "no read yet" (the model returned no line from the
  text). Each is made only from the row's sentence and saved document; code rejects a line with a number its text
  lacks, and, for a withheld regulator, a line that repeats more than five consecutive words of the source.

## (e) The ten rules a datacenter buyer most needs to know this month

Chosen by a stated rule, from the 49 dockets in motion: this month first (a document of the last 31 days, or a date
within the next 31); then how directly it sets when or at what cost a large load is served; then breadth; at most
two a regulator; never a single-customer contract. Each read is a model's (claude-sonnet-5-5). A sentence is given
where its regulator's sentences are shown; all ten sentences are in `runs/session154/ten_full.md` on the data
machine.

1. **Texas, project 58481**, order adopting 16 TAC 25.194, 18 September 2026, decided.
   <https://interchange.puc.texas.gov/Documents/58481_218_1684654.PDF>, page 2. Model's read: a large load must
   sign an intermediate agreement, make disclosures and post financial security of $50,000 per megawatt before
   ERCOT can include it in an interconnection study.
2. **Virginia, PUR-2025-00160**, order, 9 September 2026, decided.
   <https://www.scc.virginia.gov/docketsearch/DOCS/8%23%24n01!.PDF>, page 10. Model's read: a cooperative's new
   large load rate schedule is approved, with weekly billing and security deposits for customers of 5,000 kW or
   more and 25 MW or more.
3. **Texas, docket 60332**, order, 2 October 2026 (the row states 9 October).
   <https://interchange.puc.texas.gov/Documents/60332_9_1689557.PDF>, page 2. Model's read: Southwestern Public
   Service would, if approved, split large transmission-level customers into sub-classes with commercial terms.
4. **Ohio, 26-0113-EL-ATA**, entry on rehearing, 30 September 2026, decided (from the docket card).
   <https://dis.puc.state.oh.us/CaseRecord.aspx?Caseno=26-0113&link=DIVA>. Model's read: rehearing requests from
   Google and two retail suppliers are rejected, leaving in place the earlier relief on standard service offer
   supply for data center customers.
5. **Ohio, 26-0755-EL-ATA**, a judge's entry, 18 September 2026, open (from the docket card).
   <https://dis.puc.state.oh.us/CaseRecord.aspx?Caseno=26-0755&link=DIVA>. Model's read: comments on Duke Energy
   Ohio's proposed data center tariff are due October 22, 2026; replies and motions to intervene November 12, 2026.
6. **Pennsylvania, M-2026-3065062**, notice, 22 September 2026, "Active" (the row states 14 October).
   <https://www.puc.pa.gov/pcdocs/1950903.pdf>, page 1. Sentence: "The Pennsylvania Public Utility Commission
   (Commission) will hold a Technical Conference regarding large computational load cost allocation on Tuesday,
   November 17, 2026" (the sentence goes on to the hour and the room). Model's read: the conference may inform
   later cost terms for datacenters; it sets no rules itself.
7. **FERC, EL26-72-000 (ISO New England)**, investigation opened 18 June 2026, open (from the Federal Register).
   <https://www.govinfo.gov/content/pkg/FR-2026-06-24/pdf/2026-12705.pdf>, page 1. No read yet: the model returned
   no line three times, since the notice's text does not speak of large loads.
8. **FERC, EL26-71-000 (CAISO)**, show cause order, 18 June 2026, open.
   <https://www.ferc.gov/sites/default/files/2026-06/EL26-71-000.pdf>, page 5. Model's read: may require CAISO and
   its transmission owners to add tariff rules on application, study, upgrade cost transparency, cost recovery
   agreements and co-location for large loads.
9. **Pennsylvania, M-2025-3054271**, order, 16 July 2026, "ORDER ENTERED: July 16, 2026".
   <https://www.puc.pa.gov/pcdocs/1940149.pdf>, page 10. Sentence: "That the Petition for Reconsideration or
   Clarification filed by the Energy Association of Pennsylvania, on May 27, 2026, at Docket No. M-2025-3054271, is
   withdrawn." Model's read: the model large load tariff order stays as issued.
10. **Virginia, PUR-2026-00011**, order, 12 May 2026, decided.
    <https://www.scc.virginia.gov/docketsearch/DOCS/8c5b01!.PDF>, page 3. Model's read: Dominion and the other
    participants must jointly file revised large load interconnection Standards, likely adding stronger site
    control and surety at queue entry, a public queue database and study timeline estimates.

- **A rule-made list has limits, and these are outside it by the limit of two a regulator or by date, not by
  weight** (each is a row of the tables): Texas's open proposal to replace the four coincident peak method for
  transmission costs with twelve (project 58000, 9 July 2026); Virginia's direction that Dominion file for a
  mandatory contribution toward defined transmission facilities (PUR-2026-00056, 31 July 2026); Oregon's denial of
  rehearing of its decision to establish an interconnection queue (UM 2377, order 26-309, 31 August 2026);
  California's extension of its large load rule case to 26 February 2027 (A.24-11-007, D.26-09-016); FERC's show
  cause orders for PJM and SPP (EL26-67, EL26-68).
- The page of the ten in the repository is `docs/accelerator/rules_in_motion.md`.

## Model spend: USD 0.7699 of the USD 4.00 cap (stop at 3.70)

- 141 calls, all for the one-line reads, one agent, the stop before each call; one call measured, then the plan
  written before each batch. No paid answer discarded. The 141 rows are in the main ledger (session 154: 0.769900).
- No other model call: the tags are a rule; the audit's judgments were read by the agent, not by code.

## The landing

- Pushed as `task/154-rules` (`ded6b34`): checks passed (run 37731496888), merged as `ae4f5d9`. The whole suite in
  a clean copy: 2,200 tests, passed.
- **Vercel built it:** "Deployment has completed" for `ae4f5d9` at 05:23:02 UTC on 8 October.
- **Snapshot before** (`154_before`, 05:15:30 UTC) **and after** (`154_after`, 05:23:10 UTC): **6 differences, all on
  `/network`, all its own hourly refresh at 05:05 UTC** (the refresh stamp, the newest demand hour from 02:00 to
  03:00 UTC, the source line's build stamp): expected, and not this deploy. **No checked number moved** (3,357
  keys). Nothing was reverted.
- **On production, in the internal view, the page's check passes 58 of 58** (39 before this session).
- `/cost-of-power` stays `review`. `site/lib/pages.ts`, `site/lib/supabase.ts` and everything the three live pages
  render or read are untouched. The freeze file is as you set it (ends 2026-10-08); the menu change is still held.
- Under the lock, nothing released and nothing loaded: four tables written (tags 30 rows, rules 43 and 73, reads
  87), validators, coverage, the archive, the Redivis drafts: exit 0 each. The four tables and their sources are in
  the live set's hold lists, so the loader takes none of them.

## Checks

- On the merged build: the page's check 58 of 58, the generator page 43, the curtailment page 118,
  `check-values` 7,009 of 7,009. `check-routes` passed on GitHub; **on this machine it flagged `/prices` twice** (25
  "no data" blocks against production's 17), a page this session does not touch: this machine's older build cache,
  as seen last night on other pages.
- `tests/test_session154.py` 52, `test_session154_page.py` 13, `test_session154_audit.py` 26; `test-rules.mjs` 41.
- **One test of session 153 changed:** its guard that the menu, the live set and the site's data files are "not in
  this session's changes" compared any later branch with main, and would have failed this landing and the held
  menu change. It now runs on session 153's own branch only.

## Decisions made without you

1. The sentences rule (first point), and access to public records counted as enough to show a sentence.
2. Ohio's docket cards and Illinois's minutes kept as rows, marked.
3. An address that holds a filer's e-mail in its path was not requested this session (your ruling on Kentucky's is
   still open).
4. The policy table is rewritten by the daily run, not by me; I trialled the fixed connector into a separate folder
   first, with its own routine requests.
5. Texas dockets under `txpuc:dockets`, one registry row a regulator.
6. Eight rows a group on the page, and a choice of all seven grids in the block.

## The five most interesting numbers

1. **USD 50,000 per megawatt**: the security Texas now requires before a large load enters an ERCOT
   interconnection study (project 58481, adopted 18 September 2026).
2. **0 errors in the fields copied from the Federal Register, 20 of 50 in `states` and 19 of 50 in the tags**: the
   copying is sound, the deriving was not.
3. **1,086 of 1,843 policy actions are scored on a title alone.**
4. **116 proceedings and orders from eleven regulators, 41 of them under PJM**, against 8 under ERCOT.
5. **14 of 1,843**: the policy actions held that touch large loads, interconnection or transmission cost. The
   rules that matter to a large load are in the commissions' dockets, not in the Federal Register.
