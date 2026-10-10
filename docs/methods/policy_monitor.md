# The policy monitor: what is collected, from whom, and what a model reads into it

The policy monitor (`/policy`, in review) follows what federal regulators, state utility commissions and grid
operators do that moves the US energy system: rules, proposed rules, notices, orders and open proceedings. **Scope:
federal regulators, state commissions and grid operators only. There is nothing municipal in it**: no city or county
permit, zoning case or local hearing is collected, and a row whose shown words hold one is kept out of every file.

This note is the method of the whole monitor as it stands after session 157 (8 October 2026). The tag rule has its
own note ([`policy_action_tags.md`](policy_action_tags.md)); the block on `/cost-of-power` that shows some of the
same rows has its section in [`datacenter_cost.md`](datacenter_cost.md), "Rules in motion".

## 1. What is collected, from whom, how often

| Table | What a row is | From | How often |
|---|---|---|---|
| `policy_actions` | a rule, proposed rule or notice in the Federal Register, or a news release | the Federal Register's API for DOE, FERC, EPA, the NRC, the Bureau of Land Management, Interior and, since session 157, the Treasury and the IRS; the NRC's and DOE's news feeds; the news pages of the Texas and California commissions | every day (`warehouse/connectors/policy_sources.py`) |
| `policy_reads` | a model's impact read of an action rated 5 or more | the action's own text | every day (`warehouse/policy/reads.py`) |
| `policy_action_tags` | an action and one of four tags | a written rule over `policy_actions` | when the rule or the table changes |
| `large_load_rules`, `large_load_rules_internal` | a proceeding or an order on large loads, interconnection or transmission cost, with a sentence that is literally in a saved document | FERC and ten state commissions | every day since session 157 (`warehouse/connectors/policy_monitor_refresh.py`); first collected by hand in session 154 |
| `large_load_rule_reads` | a model's one-line read of such a row | the row's sentence and the saved text around it | when a session runs it |

EPA, BLM, Interior, Treasury and IRS documents are kept only when they name an energy subject; routine paperwork
(information collections, meeting notices, FERC's combined notices of filings) is left out. A Treasury or IRS
document must name the subject in its title or abstract by a narrower list of words (energy, electricity, fuel,
renewable, solar, wind, nuclear, hydrogen, carbon, oil, natural gas, coal, battery, critical minerals): the wider
list let in a home loan data rule on the word "utility". On 8 October 2026 the two agencies add **8 rows, all the
IRS's** (the section 45Z clean fuel credit, the section 45 and 45Y inflation factors, dyed fuel refunds, tribal
entities).

## 2. The printed text of a Federal Register action, read once

The Register's record of a document (its API) gives a title and, for most agencies, an abstract. **A FERC notice has
no abstract in the record** (834 of the 839 FERC notices held on 3 October), and a notice's title is often only the
applicant's name. Session 154's audit found the consequences: the place missing, a title cut short, a state read off
a company's name, tags empty, and the scorer rating a title. Since session 157 the connector reads each document's
**printed text** (the record's `raw_text_url`, plain text) **once**:

- It is kept by document number in `warehouse/raw/policy_sources/fr_text/` and never asked for twice. A run asks
  only for documents it does not hold: in that store, or already read in the table held (the runner has no raw
  store; the table carries what was read in `text_status`, `text_read_at`, `first_paragraph`, `place_words`).
- **`first_paragraph`**: the document's SUMMARY where it has one, else the first paragraph under its title (with the
  lettered items that follow a paragraph ending in a colon), at most 1,500 characters. Page marks, running heads,
  rule lines, footnotes, a notice's own date line and the heading's lines are not paragraphs.
- **The title rule.** The record cuts a title short when it ends at a semicolon ("Gulf South Pipeline Company,
  LLC;") and the printed title begins with the same words and goes on; the printed title is then taken and
  `title_register` keeps the record's. Two rows of the table (2026-17632, 2026-17825). A printed heading that merely
  adds a line is left.
- **The place rule** (`states`). The place is read from the title, the abstract with the Register's topics and the
  first paragraph, after taking out what is not a place: (1) a company's name, a run of capitalised words ending in
  a company word, and the short name the document gives it in brackets ("Texas Eastern Transmission, LP (Texas
  Eastern)"); (2) the applicant named in the title before "; Notice", unless it is a public body, whose name states
  its place ("City of Chignik, Alaska"); (3) a postal address: a state followed by a ZIP code, a state in a
  street's name, Washington, DC, Rockville, Maryland; (4) a river, county, city, falls, lake or valley that carries
  a state's name, and a county in a list of counties ("Washington and Greene Counties, Pennsylvania"). **Where those
  three name no state**, the place is read from `place_words`: the first sentence in the opening 8,000 characters of
  the printed text that places something in a county, parish or borough of a state, or says a facility or project
  "is located" in one. A state agency's name ("the New Hampshire Department of Environmental Services") counts.
- **Tested on the saved real documents of both audit samples** (87 Register documents, `tests/fixtures/session157/`):
  the table held 54 of the 87 places as the document states them; the rule gives 85. The two it does not reach are
  rows whose state stood only in a company's name and which the audits had counted right for that reason.
- On the table of 8 October (1,637 Register rows, every one with its printed text read): 683 of the 1,605 rows held
  before change their `states` (582 gain a place, 76 change, 25 lose a state that stood only in a name); 1,012 of
  those 1,605 name a place, against 455 before; 175 rows take it from `place_words`. One row has no first paragraph
  (a document that opens a separate part of the Register, with a cover before its heading). The sector tag
  "hydrogen", which the keyword rule read off "hydrogen chloride", stands on 1 row, against 6.
- **Requests.** One request every two seconds by default, at most 300 a run (`--text-pause`, `--max-texts`), and it
  stops before each ceiling. **The Register's own limit is honoured.** In the session's first trial the connector
  asked at about one request a second, and after about 450 requests the Register answered **HTTP 429** (too many
  requests) to 170 in a row over two minutes while the loop, as first written, kept asking at the same pace. That
  was a fault of the first version and is fixed: an HTTP 429 is waited out as its `Retry-After` says (120 seconds
  where it names none, 300 at most), the pace is halved, the one document is asked for once more, and a second 429
  ends the asking for the run. A 429 is never written to a row. A redirect is never followed and an answer that is
  not a printed document is not kept (the Register sends unwanted automated requests to a check of its own). An
  address that holds an e-mail address is not requested. The User-Agent names the project and its repository and
  holds no person's address.
- **The Register's terms.** Its `robots.txt` (retrieved 2026-10-08T09:17:28Z, sha256
  `6c180c52aac5e205b870c129f0edc466413fe32eeefea40fefcde42464e8ba62`) reads, in whole: "User-Agent: * Disallow:
  /documents/current Disallow: /documents/email-a-friend Disallow: /articles/search Disallow: /documents/search
  Disallow: /public-inspection/search Disallow: /regulations/search Disallow: /my/ Disallow: /auth/" (and its
  sitemap). The API (`/api/`) and the printed texts (`/documents/full_text/`) are not among them. No page of terms
  of the Register was read: its developers page answered HTTP 302 to `unblock.federalregister.gov`, which was not
  followed, and one guessed address answered 404.

## 3. What a model reads into an action, and that it is a model's

Three fields of `policy_actions` and every field of `policy_reads` are **a model's**, never a regulator's, and the
page marks them so ("model's read"; the hover names the model).

- **The score** (`significance` 0 to 10, `sector`, `why`): the news scorer and its rubric
  (`warehouse/news/rubric.md`), given the action's title and a summary. Since session 157 the summary is the
  abstract, else the first paragraph of the printed text, else the status line, and one line is added to the
  scorer's instructions: "When the summary is empty, say what the title says and no more: do not infer what the
  document decides, whom it affects or why it matters from a company's name, an agency's name or a docket number,
  and choose the sector only from words the title itself holds."
- **The impact read** (`policy_reads`): for an action rated 5 or more, a model reads the action's own text (the
  printed text from its SUMMARY on, at most 9,000 characters; a release's own page) and returns what changes, who
  is affected (sectors, grid operators, states), the direction of the effect on supply, demand, prices and
  buildout, the timeline and a two-sentence plain read, each with one to three quotations. **A field is kept only
  if every quotation is found word for word in the text** and every number in it stands in the text read.
- **Three corrections of session 157**, in the reader's prompt and held by code (`reads.enforce`): a state only
  where the action applies (not an address, a filing room or a company's name: the place rule above is run on the
  text); a price direction of up or down only where the text speaks of prices, rates or bills; a sector only if its
  own keyword stands in the text read.
- **Why `what_changes` was blank in 55 of the 234 reads.** In 29 the field held a number that stood in the text but
  not in the field's own one to three quotations, and the check asked for the quotations; in 26 a quotation was not
  found word for word, most often for the Register's own typography (quote marks printed as two grave accents and
  two apostrophes, footnote marks, a word broken at a line end). The check now accepts a number that stands in the
  text read (and notes it), and reads the print's marks as a model copies them. After the recheck `what_changes` is
  blank in 12 of 234 and `plain_read` in 6 (39 before).

## 4. The recheck of session 157: what was made again from the source text, and what was not

On 8 October 2026 the model's fields were made again from the source text, in the owner's order of priority, under
a cap of USD 6.00 with the stop at USD 5.50 before each call (`warehouse/policy/recheck.py`; the record of every
changed value is `warehouse/policy/eval/recheck_s157_changes.csv`, 3,790 lines of before and after).

| What | Rows | Rechecked | Not rechecked | Source not reachable |
|---|---|---|---|---|
| Impact reads | 234 | 226 | 8 | 0 |
| Scores of Register actions that had been rated on a title alone | 853 | 853 | 0 | 0 |
| Scores of the other Register actions | 762 | 100 (the newest) | 662 | 0 |
| Scores of news releases | 238 | 0 | 238 | 0 |

- **Every row says which it is**: `policy_reads.recheck` and `policy_actions.model_recheck` hold "rechecked" (with
  the time), "not rechecked" or "source not reachable". An action first scored after the session with a summary or
  a first paragraph reads "scored on the source text"; a read first made after it, "read with the corrected reader".
- **What is not rechecked, and why.** The 8 reads are of releases of the Texas Governor's office listed on the
  commission's news page: that office is neither a federal regulator, a state commission nor a grid operator, and
  its site was not requested. The 238 news releases' scores: a release's text is not held, and fetching it was not
  a pull the session was given. The 662 other Register actions: the money did not reach them (they had an abstract,
  so their first score already rested on the source's own summary).
- **What changed.** Of the 953 scores made again, the rating changed in 667, the sector in 414. The actions that had
  been rated on a title alone rose from 1.91 to 2.99 on average; the 100 others, given the same summary as before,
  from 3.29 to 3.49 (the model is a newer one than most first scores used, so part of every change is the
  model's). **123 actions rose to 5 or more and 8 fell below it**: 352 actions are now at 5 or more, 124 of them
  without an impact read, which the daily reader will make. A reader of this page should know that a rating of 5 on
  a notice of application for a short gas lateral is the scorer's, by a rubric written for news.
- The reads' fields that changed, of the 226: states in 32 (most often a state taken out), sectors in 140, a price
  direction in 148 (most from blank to "unclear").
- **Spend: USD 5.3003 in the ledger for 273 calls** (226 reads USD 3.0577; 47 scoring batches USD 2.2426), and up
  to five further read calls that were paid for and lost to a fault (bounded at USD 0.11; see the session report).

## 5. The audit: 100 actions against their source documents

Sessions 154 and 157 each drew 50 actions by a stated seed (`random.Random(154)` and `random.Random(157)` over the
sorted ids, the second from those not in the first), saved before any fetch, and checked every field against the
source document: by code where code can settle it, by reading where it cannot. Every source was reachable. The
record is `warehouse/policy/eval/audit_s154_*` and `audit_s157_*`; the tools are `warehouse/policy/audit/`.

| Field | Errors in the new 50 | Errors in the 100 |
|---|---|---|
| date | 0 of 50 | 1 of 100 (1%) |
| agency | 1 of 50 (2%) | 2 of 100 (2%) |
| title | 0 of 50 | 1 of 100 (1%) |
| abstract | 1 of 50 (2%) | 2 of 100 (2%) |
| docket | 1 of 50 (2%) | 1 of 100 (1%) |
| action type, RIN, document number, source, address, status | 0 each | 0 each |
| **states** | **20 of 50 (40%)**: 17 missing, 3 wrong | **40 of 100 (40%)**: 35 missing, 5 wrong; 40 of the 66 whose document names a place |
| **sector tags** (the connector's keyword rule) | **28 of 50 (56%)** | **47 of 100 (47%)** |
| sector (a model's) | 5 of 50 (10%) | 8 of 100 (8%) |
| why (a model's) | 4 of 50 (8%) | 8 of 100 (8%) |
| significance (a model's) | 1 of 50 off the rubric | 2 of 100 |
| the read's price direction | 1 of 6 reads | 2 of 15 reads |
| the read's sectors; states | 0; 0 of 6 | 1; 1 of 15 |
| the read's other fields | 0 | 0 |

A rate on 50 or 100 rows is a small sample: 40 in 100 is 40 percent, about 31 to 50. These are the rates of the table
**as it was held on 3 October**, before the fixes: the fields copied from the Register are sound, the derived ones
were not. What the fixes do to them: of the 40 place errors, 33 are Register rows, and the place rule now gives all 33
as the document states them, while 2 rows that had been right only by a company's name lose their state (section
2: 85 of 87 right, against 54); the other 7 are news releases, whose text the connector does not read. 25 of the new sample's 28 tag errors are already changed by session 154's rules; the tag "hydrogen" read
off "hydrogen chloride" is fixed in session 157. The model's fields were made again as section 4 says.

### The same 100, read again after the recheck (session 164)

On 9 October 2026 the same 100 rows were read again as they stand in the table and in the live set
(`warehouse/policy/audit/audit_recheck_s164.py`; no request and no model call). A value that had not changed keeps
its finding. A changed `states` is set against the place the document names (`audit_states_truth.csv`). Other
changed values are settled by code where code can (a summary the audit recorded cut at 500 characters, a read that
now claims no direction, an empty field) and otherwise were read again by session 164's agent against the row's
title, summary and first paragraph, or the spans a read kept: 127 values, each with the words it rests on, in
`warehouse/policy/eval/audit_s164_judgments.csv`. An error is a value classed wrong, missing, not in the source,
unsupported or contradicted; a judgment (every significance; a kind read off FERC's project docket) is not counted.

| Field | Errors before | Errors now | What changed |
|---|---|---|---|
| date | 1 | 0 | the day in Washington |
| title | 1 | 0 | completed from the printed document |
| abstract | 2 | 0 | "NO X" is NOX |
| agency | 2 | 2 | two releases of the Texas Governor's office still carry the agency PUCT |
| docket | 1 | 1 | the Register's own record leaves out two ids |
| action type, RIN, document number, source, address, status | 0 each | 0 each | |
| **states** | **40** | **9** | 33 fixed from the printed text; 7 news releases still lack their place; 2 that were right only by a company's name lost it |
| **sector tags** (the keyword rule) | **47** | **2** | 45 fixed; 2 documents name their sector only in their text |
| sector (a model's) | 8 | 0 | all 8 were among the 50 rows rechecked |
| why (a model's) | 8 | 3 | 7 fixed; 1 not rechecked (a news release); 2 new in the rechecked lines |
| the read's price direction | 2 | 0 | both now claim no direction |
| the read's sectors; states | 1; 1 | 1; 1 | both old ones fixed; one new each ("transmission" from a company's name; New York dropped) |
| the read's other fields | 0 | 0 | |
| **All 1,850 checks** | **114 (6.2%), in 69 rows** | **19 (1.0%), in 18 rows** | copied or rule-made fields 94 to 14 of 1,400; a model's fields 20 to 5 of 450 |

Of the 100 actions, 50 had their score, sector and why made again from the source text (all 50 lines changed, 24
sectors, 36 scores: 34 up, 2 down, 5 across the line of 5) and 50 did not (37 Register actions the money did not
reach, 13 news releases). Of their 15 reads, 13 were rechecked. The two new errors in `why` are a line that calls
"small" a header "capable of wheeling up to 5,000,000 dekatherms per day" and a line that names a state the text
does not. A rate on 100 rows is a sample: 19 in 1,850 is 1.0 percent, about 0.6 to 1.6.

## 6. The tags

Four tags say which actions touch what a large load cares about: `large_load`, `interconnection`,
`transmission_cost`, `tax_credit`. A written rule that code applies (`warehouse/config/policy_tag_rules.json`,
**version 3**); no model reads a row. Version 3 keeps version 2's terms, exclusions and listed dockets unchanged,
reads the first paragraph of the printed text beside the title and the abstract, and counts the Treasury and the
IRS among the agencies in scope. An action whose title, abstract or first paragraph holds a municipal phrase is
never tagged. **The page applies the same file** to the rows it reads (`site/data/policy/tag_rules.json` is a copy,
byte for byte, and a test holds the Python rule and the page's rule to the same cases), so a new action is tagged
the day it arrives.

On the table of 8 October (1,875 actions): **22 actions carry a tag, 38 tag rows**: large load 13, transmission cost
12, interconnection 8, tax credit 5. Before (version 2 on 1,843 actions): 14 actions, 30 rows, no tax credit. The
eight new ones were each read: five IRS documents on the section 45, 45Y and 45Z credits, and three FERC notices
of gas pipeline projects whose first paragraph says the gas is for a data center's power plant.

## 7. The state commissions and FERC: the daily refresh, each regulator's terms, and what refuses

Each day, by plain request, the step asks each regulator's own open list for what is new in the dockets held and for
new dockets on four topics (large-load interconnection, large-load tariff, transmission cost allocation,
interconnection reform). A new row holds the regulator, the docket, the date, the status as worded, the address and
**a sentence that is literally in a saved document; where the list gives only a filing's title line, that line is
the sentence and the row says it is cut from the docket list. No model writes or shortens it.** Ceilings in the step
itself: **120 requests a day in all, one a second to a host**, and it stops before them. It is a soft step under
`warehouse/health.py`: a regulator's failure is recorded and never stops the run or the other regulators. **A
regulator that refuses a plain request is not requested at all.** `warehouse/config/policy_monitor_feeds.json`
names each list; the page shows a refusal's reason on hover (`site/data/policy/refresh.json`).

| Regulator | List asked each day | Its terms, word for word |
|---|---|---|
| Federal Energy Regulatory Commission | the Federal Register's API (rows carry the printed copy's address at govinfo.gov) | none read: **every ferc.gov page answers a browser check and is never requested** |
| Public Utility Commission of Texas | the Interchange filing list of each docket held, and the docket search by case style | "Although the content of PUCT web sites is available to the public, certain information on the PUCT web sites may be trademarked, service marked, or otherwise protected as the PUCT's intellectual property, and all PUCT content is protected by federal copyright laws." |
| **Virginia State Corporation Commission** | **not asked since 10 October 2026** (asked daily from 8 to 9 October: the docket search's case list and a case's document list) | "Information on the SCC website is public and should not be used for commercial purposes beyond its intended public availability. Permission is granted to make fair use of the contents of the SCC website. Attribution of the source of the information is encouraged." (read for the first time in session 157; its class is left "not quoted" until the owner rules). **Paused** (session 172, the owner's ruling of 9 October 2026): the commission's robots file ends `User-agent: *` / `Disallow: /`, so the step sends the commission nothing while `warehouse/metadata/paused_sources.csv` holds the `vascc` row (`docs/methods/vascc_pause.md`; the permission request to send is `docs/reviews/scc-permission-email.md`) |
| Indiana Utility Regulatory Commission | the weekly orders page | "Except as may otherwise be allowed by law (including but not limited to the Indiana Access to Public Records Law), the viewing, printing, or downloading of any content, graphic, form, or document from the Portal grants you only a limited, nonexclusive license for use solely by you for your own personal use, and not for republication, distribution, assignment, sublicense, sale, preparation of derivative works or other use." |
| Pennsylvania Public Utility Commission | each docket's page | "Persons requesting copies of public records maintained by the Commission must submit a written request to the Commission's Open Records Officer." |
| Georgia Public Service Commission | the docket's list of filings | "Request in writing by any person pursuant to the Georgia Open Records Act, O.C.G.A. Section 50-18-70, et seq." (and every page's footer, "All rights reserved.") |
| Arizona Corporation Commission | the eDocket record of each docket held | "In other words, much of the information you disclose to us becomes a matter of public record as required by law." |
| Oregon Public Utility Commission | the eDockets docket summary | "Most information collected by state government is assumed to be open to the public unless specifically exempted." |
| California Public Utilities Commission | the decisions list of each proceeding held | "In general, information presented on this web site, unless otherwise indicated, is considered in the public domain. It may be distributed or copied as permitted by law." |
| **Public Utilities Commission of Ohio** | **not asked** | none read. "Not refreshed: the commission's document viewer (dis.puc.state.oh.us/ViewImage.aspx) answers with a Google reCAPTCHA, and its main site puco.ohio.gov answered 404 to six plain requests on 8 October 2026, so no terms page could be read; the daily step requests neither host." |
| **Illinois Commerce Commission** | **not asked** | "Information collected and received through the Illinois Commerce Commission web site may become public record and therefore subject to disclosure under the Illinois Freedom of Information Act." Not refreshed: a docket's own page answered "Please, no robots or crawlers beyond this point." and a CAPTCHA; the daily step requests no page of the commission |

Each quotation's page, retrieval time and sha256 are in `warehouse/config/large_load_rule_terms.json` and the feeds
file. By those terms a regulator's rows are in the public table with their sentence (California, Oregon, Arizona,
Pennsylvania, Illinois) or in the internal one, where the page shows the row's facts, its link and the model's
read and never the regulator's sentence (Texas, Indiana, Georgia, and FERC, Virginia and Ohio until their terms are
ruled on): session 154's rule, unchanged. Also never requested: misoenergy.org (MISO is paused), scc.virginia.gov (Virginia's commission is paused since
10 October 2026, `docs/methods/vascc_pause.md`), PJM's Data Miner
and API, Arizona's two document hosts (HTTP 500; a certificate fault), Indiana's portal (a sign-in form).

The trial of 8 October: 55 requests of the 120, 5.4 MB, nine regulators asked, **no new row** (the lists had been
read by hand the same night). The first run on GitHub's runner, 8 October 2026 at 15:14 UTC: 39 requests of the 120,
5.3 MB, no new row, no regulator failed, two not requested (`warehouse/metadata/run_status.csv`).

### Ohio and Illinois: each host's robots file, read in session 164, and why no filing was requested

Session 164 was to read the public PDFs of the filings that Ohio's docket cards and Illinois's minutes name. Before
the first document of a host its `robots.txt` was saved and read (9 October 2026, 00:41 UTC;
`warehouse/raw/large_load_rules/D/raw/robots/`, hashes in `warehouse/config/large_load_rule_terms.json`). **No
document was requested from either host**: 0 of the 400 allowed.

- **Illinois Commerce Commission**, `https://icc.illinois.gov/robots.txt` (329 bytes), its first rule, word for word:
  "User-agent: *" "Disallow: /". Four robots are then named and allowed (Elastic-Crawler, Elastic,
  SiteimproveBot-Crawler, SiteimproveBot). Every path of the site is closed to this project's script, the minutes,
  the agendas and the terms page with it. **Session 154 had asked this host 80 times without reading the file** (the
  nine Illinois rows and the terms quoted above rest on those pages). The rows are kept as they are and marked as
  before; whether they stay, and whether a person may fetch the filings by hand, is the owner's to rule.
- **Public Utilities Commission of Ohio**, `https://dis.puc.state.oh.us/robots.txt` (1,045 bytes): one group of 40
  named robots and "Disallow: /". Among the names, word for word: "User-agent: anthropic-ai", "User-agent:
  Claude-Web", "User-agent: ClaudeBot" (and GPTBot, ChatGPT-User, CCBot, PerplexityBot, Scrapy and others). The file
  has no rule for other robots. This project's requests are made by an AI agent built on Anthropic's Claude, and
  what they fetch is read by a Claude model: a rule that names the asker is not got round by a request that carries
  another name, so no document was asked for (`ASKED_BY` in `warehouse/connectors/large_load_filings.py`; only the
  owner empties it). **Session 154 had asked this host 42 times for docket cards without reading the file.** The
  commission's own site still answers 404 to a plain request (`puco.ohio.gov/robots.txt`, its privacy notice, and
  `ohio.gov/robots.txt`, 9 October 2026), so **Ohio's terms are still not read** and nothing can be said of reuse.
- What each host's terms say about reuse: Illinois's privacy page (read in session 154) speaks of public records and
  disclosure and states no rule on reuse; Ohio's could not be read. Neither was read again in session 164.

So Ohio's 10 rows still hold the docket card's line and Illinois's 9 the minutes', agendas' or list's, with no page
for a docket card or an agenda. No model read anything in session 164 (USD 0.00 of the cap of USD 5.00).

## 8. What the page reads

`/policy` reads `policy_actions` and `policy_reads` from the live set, and five files under `site/data/policy/`
that `warehouse/derived/policy_monitor_site.py` builds without a request or a model: `tag_rules.json` (the rule),
`action_tags.json` (the tags the Python rule gives, with the first paragraph of an action tagged from it),
`grids.json` (the names by which a document names a grid operator; MISO shows "paused while terms are reviewed" and
no row), `state_rules.json` (every proceeding and order held, with the grid it is under) and `refresh.json` (each
regulator's list, whether it is asked, the reason if not, and the last run). The daily run rebuilds the last three
after the refresh step and **never writes a thinner file**: without the tables nothing is written, a file with
fewer rows or reads than the one held is refused, and a file that would only change its build time is left. No
live page (`/cost-of-power/battery`, `/network`, `/storage`) reads any of these tables or files.

### The first view, "Every action, scored" (session 164)

The first view lists every action of `policy_actions`, scored. Until session 164 a paragraph of method stood under
its lead; a page face carries no method, so each of its three sentences is now the hover of the words of the lead it
explains, and all three stand here, word for word:

- On "scored for significance": Significance uses the same rubric as the news digest.
- On "read for its impact": An impact read is written by a model from the action's own text, and each field is kept only when the exact words it rests on are found in that text; a blank field was dropped for that reason.
- On "FERC": FERC's own pages cannot be read automatically, so FERC appears through the Federal Register.

**The Tag filter and the chips (session 164).** The second view's windows end at thirty days, and the newest tagged
action can be older (on 9 October 2026 the newest of the 22 was of 4 September), so no tag chip could be seen there.
The first view holds the whole table, so it has a seventh filter, Tag, kept in the address (`/policy?tag=large_load`,
`interconnection`, `transmission_cost`, `tax_credit`, or `tag=any` for every tagged action). A tagged row shows a
chip a tag under its title; a chip's hover names the rule's version, the term that matched and the field it matched
in. The tags are the one rule's (section 6): the rule applied to the row as the view reads it (its title and its
docket), united with the tags the warehouse's run gave from the summary and the printed text
(`site/data/policy/action_tags.json`). Choosing a tag lifts the view's significance floor, so no tagged action is
hidden by it. `site/scripts/check-policy-tags.mjs` sees each of the four chips on a real row in a real browser.
The table `policy_action_tags` is not in the live set and the page does not need it there.

## 9. Limits

- A docket system cannot be proved complete from outside; the refresh searches for new dockets only where a list
  can be searched by a plain address (Texas, Virginia, FERC through the Register). Ohio's and Illinois's rows are
  as session 154 left them: session 164 read each host's robots file and requested no filing (section 7).
- 900 scores are still not rechecked against the source text (662 Register actions, 238 news releases whose text is
  not held), and each row says so.
- The place is what the document's own opening words name: a notice that names its place only deep in its text, or
  only in a company's name, has none.
- News releases are scored on their titles and their places are not read from their text.
- A rating, a sector, a why and every field of a read are a model's. The quotations hold a read to its text; they do
  not make it a regulator's statement.
