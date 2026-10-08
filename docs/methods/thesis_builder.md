# Thesis Builder: method

Platform tool 27, v0, built in session 25. An internal command-line tool (`warehouse/thesis/build.py`) that maps one niche for an investor and writes one workbook in the Stanford format under `docs/thesis/`. Every company it finds is also merged into the public entities table `energy_companies`, the seed of the company database (tool 10).

## Input

A niche stated precisely (for example "subsurface heat mapping for geothermal"), and optionally a stage and a geography.

## The fixed research plan

1. **Research: three agentic passes** with the Claude API, using the newest Sonnet-class model the models list offers, chosen the way the news scorer chooses. Each pass has the API's web search tool and the ERW's four read-only warehouse tools (the chat's `list_tables`, `describe_table`, `query` and `compare`). The warehouse comes first for any energy number it holds.
   - **a. Scope, fundamentals and trends.**
   - **b. Companies, capital and incumbents.** This pass also reads `energy_deals`.
   - **c. Risks.** Web only.
2. **Sources.** Every web search result becomes a numbered source (S1, S2, ...) with its URL, title and the run date. Every passage the model cites from a result (the API's web citations) is kept with it. Every warehouse tool result becomes a numbered ERW source (E1, E2, ...).
3. **Structure:** one streamed call with a JSON schema holding every sheet (session 30; one call per sheet before), from the notes and the numbered sources only. Each row names the source ids it rests on. The prompt carries at most 3 cited passages of 300 characters per web source; the number check still reads every passage.
4. **Check.** A number is written only if it appears in the cited passages of the sources its row names, or in the ERW results it names. This is the chat's literal-number check (`warehouse/chat/ask.py`); a number that fails is written as "not confirmed" and logged. A row with no source is not written. Where the sources say nothing, the cell reads "not disclosed". An estimate is labelled "estimate" and shows its arithmetic, and its inputs pass the same check.
5. **Policy.** The Policy sheet is drawn from the ERW's `policy_actions` (matched on the niche's words, the most significant first), with the plain read from `policy_reads` where one was kept. The model only picks which actions bear on the niche.
6. **Charts.** A trend table whose values survive the check as numbers gets a native chart. When the model names an Automated Analysis template that fits the trend, its email-size chart is inserted with the template's source line.
7. **Costs.** Every model call is logged with its tokens, web searches and cost, and the run's total is logged and written on the Scope sheet. Cost is the model's token prices plus USD 10 per 1,000 searches, with a hard stop at `--max-usd` (default 6).
8. **The structure calls (sessions 30 and 34).** The sheets are written from the saved research in three calls: {scope, fundamentals, trends}, the landscape alone, and {capital, incumbents, risks, policy}. Session 34 gave the landscape its own call. On session 30's saved geothermal research it cost USD 0.1152 more (run total USD 1.3237 against 1.2253) and found the same 2 companies. The 7 of the earlier per-sheet run came from a different research pass: this pass's Scope sheet excludes drilling and plant developers (Quaise, XGS, Sage, Fervo), which the notes do name.

## The workbook (Stanford format)

- **Type and colour:** Georgia titles in cardinal `#8C1515`, cardinal header bars with white text, body text `#2E2D29`, and fog beige `#F7F3EA` on every other table row.
- **Layout:** column A is a narrow margin, and gridlines are off.
- **Sections:** each is a numbered "(1) SECTION" bar followed by a "Fact:" paragraph, a table and a chart where there is data, then a grey "Source(s):" line.

| Sheet | Contents |
|---|---|
| Scope | Definition, the value chain, the adjacent niches kept out of scope; the run's model, calls, searches, cost and time |
| Fundamentals | The framing numbers with their sources, the warehouse's first |
| Trends | Three to five numbered trends: a Fact, a table, a chart, the sources |
| Landscape | Every company found: name, one-line description, founders, stage, raised, location, the signal that surfaced it, sources, and a confidence score |
| Capital | Rounds, grants, project finance and M&A: dates, amounts, investors, sources |
| Incumbents | Large players and public comparables, with the metric that matters |
| Policy | The ERW's policy actions that bear on the niche, with their reads |
| Risks | What breaks the thesis, what is not known |
| Sources | Every URL and ERW source, its retrieval date, and the cells it supports |

## Company confidence (0 to 100)

The score is a rule, not the model's opinion:

- **Independent sources:** 20 points for each, counting up to three.
- **Recency of the latest source:** 20 points when it is from this year or last, 10 when it is two to three years old, and 0 when older or undated.
- **Primary confirmation:** 10 points when a primary source (the company, an investor, a filing) confirms the stage, and 10 more when one confirms the amount raised.

Each row states the clause behind its score, for example "2 independent sources, latest 2026; stage confirmed and raised not confirmed by a primary source".

## energy_companies

An entities table, public: name, one-line description, sector, niche tags, stage, raised, location, founders, website, source links, confidence and its clause, and first_seen.
- **Merging:** rows merge on name plus website domain. A company found again keeps its first_seen, gains the new niche tag and sources, and keeps the fields of the higher-confidence finding.
- **Content:** the fields are written by the ERW from public web sources; the table holds no text copied at length and no licensed data.

## Bring your own license

Licensed databases (PitchBook, Harmonic, Crunchbase and the like) are read only with the user's own credential, under the terms of the user's own account.

- **Interface:** `warehouse/thesis/connectors/` holds a base class, `LicensedConnector`, and one module per vendor. Each takes the credential from an environment variable (`PITCHBOOK_API_KEY`, `HARMONIC_API_KEY`, `CRUNCHBASE_API_KEY`) and returns rows in the Landscape and Capital shapes.
- **Where the rows go:** the builder calls every connector whose credential is set. Its rows go into that user's workbook only, marked "licensed, user's own account, not stored in the ERW".
- **Where they never go:** into `energy_companies`, any other ERW table, Supabase, Redivis, a log line or a file in git.
- **The credential:** never logged or stored, and not shown in a connector's repr or errors.
- **Status in v0:** the three connectors are stubs. Their mapping from the vendor's documented fields to the ERW's row shapes is written, but the API call is not; each raises `NotWired`, and the builder logs that and goes on. Wiring one means writing its `fetch_companies` and `fetch_rounds` against a real account.

The ERW holds no licensed data. A workbook built with a licensed connector is the user's, under their license, and is not committed to this repository.

## Cost (session 30)

Toward USD 1 a run:

- one automatic retry per call (the SDK's default is two);
- the research passes' system prompt and tools cached;
- the sheets written in one call, instead of eight that each sent the same 50,000 to 70,000 tokens of notes and sources;
- the cited passages per source capped in that prompt.

Every call is a row of `api_cost_ledger` (step `thesis`).

## The tool on the site (session 135)

**This note is internal.** From session 135 it is not built into the site (`site/scripts/build-content.mjs`, `INTERNAL_METHODS`): the research plan, the prompts and the scoring rule stay on the server. What a reader of `/thesis` may know is in `docs/methods/thesis.md`.

- **The page.** `/thesis` (in review). A niche, an optional stage and geography, and Run. The database queues a row in `public.thesis_runs` (migration 024, internal: row level security on, no policy, no grant to the public key) and dispatches `.github/workflows/thesis.yml`, which runs `warehouse/thesis/run.py` and writes the report into the row. The report is drawn in tabs. Nothing is merged into `energy_companies`; no workbook is written; there is no download.
- **The order of work** differs from v0: the scope and five trends are written first, because the landscape is chosen by them. Each trend must be about how the niche's own work is changing, so that a company can be said to serve it or not; a general fact about the wider industry is background, never a trend.
- **The landscape's sources.** (a) The warehouse: rows of `energy_companies` and `energy_deals` carrying the longest word of the niche's name, most matching words first, at most 40, each a numbered ERW source. (b) Web search by a stated query plan, built in code and saved with the run: six niche-level queries (the niche by name; recent rounds; seed and Series A; federal awards; accelerators and incubators; spinouts) and two per trend from the trend's own search phrases; each is run once, in order; then up to six searches for the headquarters of private companies no result located. (c) The PitchBook stage.
- **The selection rule is code** (`run.select`): found, then a private company, then fits the stage and geography asked for (a company whose location no source gives stops here), then tied to at least one of the five trends: that is the landscape. Since session 142 "tied to a trend" is not the model's opinion: it is the rule of `warehouse/thesis/tie.py`, set out in the next section. The pipeline map takes the landscape's companies with confidence 60 or more, in the rule's order (total score, then best kind of evidence, then name), at most ten. Every organisation found is a row of the funnel with the stage it reached and why it stopped. (Until session 142 this line read "tied by a source its row cites" and "most trends served first": the model's judgement, which gave 8, 12 and 9 companies in three runs of one niche.)
- **The confidence score** is the rule above, unchanged. A reader sees the number and one plain line (`run.confidence_note`) that names the evidence and never the points.
- **The PitchBook stage.** The run writes a request (the companies that reached "a private company", five lookups each, and a discovery search by the niche's name and the trends' phrases), a one-time key, and the text to paste into a Claude chat that has the user's own PitchBook connector. The answer comes back as JSON in the format `erw-pitchbook-1`, is validated by the site (`site/lib/thesis/pitchbook.ts`), accepted once under the key (`thesis_pitchbook_accept`), and kept on the run's row only. Every PitchBook figure is labeled where it is shown.
- **Stability** is measured by `warehouse/thesis/eval/stability.py` on saved states: the overlap of the companies several runs of one niche put on the landscape.
- **Spending.** One run stops at USD 2; the runs of a UTC day at USD 8 (`run.py`, counted from the internal table); the page queues at most six runs a day (counted by the database).

## The tie of a company to a trend (sessions 142 and 147)

**Internal, as the rest of this note.** A reader of `/thesis` is never told the order of evidence, the points, the thresholds or the tie-break; "why it is here" shows one source sentence with its publisher's domain. The rule is `warehouse/thesis/tie.py`: code only, no model, no network. Given the same saved evidence it returns the same landscape in the same order.

- **Order of evidence.** (1) The warehouse: the company's row of `energy_companies` and the rows of `energy_deals` that name it, read fresh at every run. (2) Fetched: the title of a search result, or a passage the search tool returned as cited, that names the company. (3) The web: a sentence of a page the run saved (below) that names the company.
- **Naming.** A text names the company when it holds its whole normalized name or its core name (the name without trailing generic words such as Energy or Technologies). A name of one word must have four letters or more, and the text must also hold a word of the niche's own name.
- **A trend's terms.** The words of its title and its two search phrases, four letters or more, or capitals of two or more (AI, DAS, DOE); lower case, a final "s" dropped; without stop words, the niche's own name words and four general words (system, method, public, high). A word of the company's own name is not a term for it.
- **Scoring.** A sentence supports a trend with 2 or more distinct terms, or every word of one phrase. Points: warehouse 3, fetched 2, web 1; plus 1 when the sentence is strong (a whole phrase, or 3 or more terms). A trend's score is the sum of the best sentence of each address, at most 3 addresses; the same sentence on two addresses counts once. Tied at 2 or more.
- **Tie-break.** Total score over the tied trends, then the best kind of evidence (warehouse, fetched, web), then the normalized name.
- **Duplicate names.** The same core name, or one core name the leading words of the other with website domains that do not differ; a short name leading two different companies merges with none; the longest name is kept.
- **Facts.** A company's kind, country, location and stage fit are the first values saved for it. A later different reading changes nothing and is listed as a disagreement.
- **What session 147 changed, and what it did not.** Until session 147 the web tier was the sentences the model QUOTED from a page, and what the model chose to quote moved the set (session 142: one company entered in the third run on a sentence of a page held since the day before). Now the web tier is read from the saved page: every sentence of a saved page that names the company, whichever row cited the page. A quoted sentence decides nothing: when it is on the saved page and names the company it is simply one of the page's sentences; when it is not on the saved page it is not evidence. The quotations are still saved, and each run's record says of each whether the saved page holds it (`tie.quote_check`). The points, the thresholds (2 terms, strong at 3, tied at 2, 3 addresses), the tie-break and the rule for duplicate names are as session 142 built them.
- **A sentence of a page** is a run of text inside one block of the page (a paragraph, a heading, a list item), cut at its sentence ends, of 12 to 500 characters (`PAGE_SENTENCE_MAX`). A longer run with no sentence end is a menu, a list or a table. This is a definition of the reading, new with the pages, and not one of the scoring thresholds.
- **Gaps the pages exposed (7 October 2026), left for the owner's ruling, not changed.** (1) A company whose whole name is made of the niche's own words is "named" by running text: "Geothermal Technologies" (geothermal.tech) was tied by two sentences about geothermal technologies in general, one of them naming the DOE Geothermal Technologies Office. (2) One quotation printed on two pages with two different attributions is two sentences to the rule, which counts the same sentence once only by its exact words: Quaise Energy is tied by one remark of its chief executive on two pages, and its two terms are "DOE" and "field" in "progress in the field". (3) A name of three letters is not matched alone ("XGS"), and a name written with and without a space is two companies ("Terra AI", "TerraAI"). (4) Session 142's two: "modelling" does not match "modeling"; an acronym is not joined to its full name.

## The pages a run cites (session 147)

The owner's instruction of 7 October 2026: "for each run, fetch in code the address of every web result the run cites, save the page text with its hash and retrieval date in the run's evidence store, and make the trend-matching rule read those saved sentences, not the model's quotations". The fetcher is `warehouse/thesis/pages.py`. No model takes part.

- **What is asked for.** Every web address the run's rows cite (a row's sources and the pages of its quoted sentences), then every address the rows already in the niche's store cite. Not every search result: only the cited ones.
- **How.** One plain GET a page. The only header set is the contact string, exactly `ERW research project, github.com/SamuelEnrique/erw`, as the User-Agent. No personal address, no cookie, no JavaScript, no login, no way round a CAPTCHA, a paywall or a browser check, and no archive or cache service in place of the page. A redirect is followed by hand, at most three times, each hop a counted request that passes every check again; a redirect to a login is recorded and left.
- **What is never asked for.** misoenergy.org and every outlet in `warehouse/metadata/paused_sources.csv`: recorded as "not fetched: paused". A PJM Data Miner or API address, and the site of a licensed database the tool reads only through the user's own account (pitchbook.com, crunchbase.com, harmonic.ai): "not fetched: licensed source needed". An address that is not a public web page (another port, an IP address, a local name). All are refused before any request, and again at each redirect.
- **robots.txt is honoured.** Each host's robots.txt is read once a day (it counts as a request) and its rules are kept in the store. An address the file disallows for all agents (the group `User-agent: *`; the longest matching rule wins, Allow wins a draw) is "not fetched: robots.txt". A robots.txt that cannot be read (401, 403, 429, a server error, no answer) closes the host: its pages are not requested. A host's own crawl delay is kept when it is longer than one second, up to 30.
- **The ceilings**, set in code and checked before each request: 150 addresses a run; 450 a session when the runs share a count file (`--fetch-count-file`); 2 MB a page; 20 seconds a request; at most one request a second to one host; 450 requests of any kind a run (pages, robots.txt files, redirect hops); ten minutes for a run's whole pull (the workflow's job has 40, and the pull comes after the paid calls). An address left by a ceiling gets no record and is asked for by a later run.
- **What is kept.** For each address: the page's text, the SHA-256 of what was received and of the text, the day retrieved (UTC), the HTTP status, the number of bytes, the final address after redirects, and the reason when it holds no text. A page that answers anything but 200 with text (HTML, plain text or a PDF) holds no sentence. A page longer than 2 MB is read to the limit, recorded as truncated, and holds no sentence. A PDF is read with `pdfplumber`, a page at a time.
- **The text of an HTML page** is its visible text, one line a block, without scripts, styles, navigation and footers; and what the page says of itself in its head: its description (the meta tag) and the headline, description and article body of its structured data (JSON-LD). Many news sites draw the article with JavaScript, which is never run: a plain GET of such a page shows menus and headlines, and the article stands in the head. (The first run of 7 October 2026 met this on renewablesnow.com. The reading was extended after that run and the pages already received were read again from their saved bytes, with no new request; each page's record carries the version of the reading, `extractor`.)
- **Again on a later day.** A page the store holds from the run's own day is not asked for again. One held from an earlier day is asked for again; when its text differs, the store keeps both versions with their days and hashes, and the run's record names the address.
- **Terms.** The publishers' terms are not read one by one (a run cites pages of dozens of sites). What stands in their place is what is stated here: one plain request a page with the declared contact string, robots.txt honoured, refusals left alone, the saved text kept in a private store, and on a page face only single sentences that name a company, each with its publisher's domain.

## The evidence store (session 147)

One store a niche, geography and stage (`warehouse/thesis/store.py`): every fetched source by address with the hash of its text and its date, every reported sentence, every row a run wrote, every page asked for, each host's robots.txt rules, and what the last run rested on.

- **Where.** A private Supabase storage bucket, `erw-thesis` (a bucket of its own, not a prefix of `erw-archive`, which is append-only and whose scripts list everything under it). The object is `evidence/<niche>__<geography>__<stage>.json.gz`, gzip of JSON, written whole and read whole. Before it is replaced, the object as it was is copied to `evidence/history/<niche>__<geography>__<stage>/<YYYYMMDDTHHMMSSZ>.json.gz`.
- **Credentials.** `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`, from the environment or `.env`, never printed. The workflow `thesis.yml` already gives the run both. The site's public key cannot read the bucket.
- **Reads are fresh, writes are checked.** A read just after a write was answered with the version before it for a few seconds (probed on 7 October 2026). Every read therefore carries a query of its own, and a write is believed only when the object reads back as written.
- **The fallback.** With no key (a test, a machine without it) the store is the local file, as before session 147. A write the bucket refuses is written to the local file and said so in the log. Every run's record says which store it used (`state["tie"]["store"]`, `store_kind`).
- **The warehouse tier on the runner.** `energy_companies.csv` and `energy_deals.csv` are in git (allowlisted in `.gitignore` in sessions 27 and 15, refreshed by the daily run's commit), so a checkout of `main` on the GitHub runner holds them and the warehouse tier is read there. Each run's record counts the rows it read (`state["tie"]["warehouse"]`).

## The data providers of the fetch stage (session 150)

**Internal, as the rest of this note.** The owner's instruction for session 150 (the chain of 7 and 8 October 2026): "Make the fetch stage provider-agnostic; beside erw-pitchbook-1 add erw-harmonic-1, built on what Harmonic's Claude connector returns (company enrichment, saved-search results for companies and investors, people), and erw-crunchbase-1 on Crunchbase's connector; the run records which provider supplied each figure and labels it in the report; /thesis lets the person choose the provider before copying the request text; the pending PitchBook request for run 20261006T193517Z-50a8be stays as is."

No provider, connector or model is called by any code of the ERW. A person copies a request into a Claude chat that holds the provider's connector under their own account, and pastes the answer back on `/thesis`. This section replaces nothing above: "Bring your own license" still describes the command-line stubs of session 25 (`warehouse/thesis/connectors/`), which stay unwired.

### The interface

A provider has: an id and a label, the request text it makes from a run, the format id it expects back, a reader (parser and validator) for what the person pastes, a mapping from its fields to the run's facts, and its terms line. The site holds it (`site/lib/thesis/providers.ts`, pure functions); the server holds the list of ids, labels, formats and terms lines (`warehouse/thesis/providers.py`), and `site/scripts/test-thesis-providers.mjs` checks that the two say the same.

| Provider | Format | The request text | The reader |
|---|---|---|---|
| PitchBook | `erw-pitchbook-1` | The text the run wrote and saved (`run.pitchbook_request`), handed back as it is. It is never made again by the page | `validatePitchbook` of `site/lib/thesis/pitchbook.ts`, the file of session 135, untouched |
| Harmonic | `erw-harmonic-1` | Made by the page when the person chooses Harmonic, from the companies and the discovery search the run saved in its request | `validateHarmonic` |
| Crunchbase | `erw-crunchbase-1` | Made by the page when the person chooses Crunchbase, from the same saved request | `validateCrunchbase` |

- **PitchBook is unchanged, and a test proves it byte for byte.** `tests/fixtures/session150/pitchbook_request_main.json` holds a request made by the code of main before this session (commit 7ae13c1); `tests/test_session150.py` makes it again with today's code and compares the bytes. `pitchbook_read_main.json` holds what the reader of main wrote out for session 135's own made-up answers; the node test reads the same pasted texts through the interface and compares the bytes. The one-time key, the route `POST /api/thesis/pitchbook` and the database function `thesis_pitchbook_accept` are as they were.
- **A run needs no new stage for a second provider.** The request of Harmonic or Crunchbase is made from what the run already saved, so every finished run that holds a request can be taken to any of the three, with no new run and no spend.
- **No key travels in the two new requests.** The one-time key is PitchBook's and works once. The answers of the other two are pasted on the internal page and stored by `POST /api/thesis/provider`, which answers only a browser in the internal view (the cookie), as `/api/thesis/run` does.
- **The choice on the page.** Three radio buttons in the panel of a finished run, PitchBook first and chosen when the panel opens. The request text and the label over it change with the choice. The answer box takes only the format of the provider chosen: given another provider's format it sends nothing and says, for example, `This answer is in the format "erw-harmonic-1", Harmonic's. The provider chosen is PitchBook, which takes "erw-pitchbook-1". Choose Harmonic above, or paste PitchBook's answer.` A provider whose answer the run holds reads "received" and cannot be chosen again.

### The documentation the two new formats rest on

Each page was asked for once, with a plain GET whose only header of ours was the User-Agent `ERW research project, github.com/SamuelEnrique/erw`, on 8 October 2026 (UTC), and saved with its SHA-256 under `runs/session150/docs/` in the main copy (not in git; `fetch_log.csv` there lists every request, kept or refused). 19 requests in all, 1,979,764 bytes, against a ceiling of 60 requests and 40 MB set in the script before the first request.

| Id | Page | Address | Retrieved (UTC) | SHA-256 of the bytes received |
|---|---|---|---|---|
| H1 | Harmonic MCP Server, Getting Started Guide | https://support.harmonic.ai/en/articles/12785899-harmonic-mcp-server-getting-started-guide | 2026-10-08T00:06:33Z | `cb1904e354ffc95f39a93ba8d9c1cb51138cb56a2a180b911e8045fffaf43cee` |
| H2 | Harmonic Data Fields | https://support.harmonic.ai/en/articles/6480774-harmonic-data-fields | 2026-10-08T00:08:20Z | `62fd92f7387a6a99a4573cab6deb3c30a2da96c647eb33cc41163089f23a2b3a` |
| HT | Harmonic Terms of Service | https://harmonic.ai/legal/terms-of-service | 2026-10-08T00:08:04Z | `6b8ce63d932543628efe82712bdd17d994a4c0ccd4568a1cbb00ed55114400cc` |
| C1 | Crunchbase MCP, Tool Reference | https://data.crunchbase.com/docs/tool-reference.md | 2026-10-08T00:07:04Z | `afa2d923599440c7208563d11a1f3fc6edec6fcda9b642a2978e29b5e32fb7a1` |
| C2 | Crunchbase Data Dictionary | https://data.crunchbase.com/docs/data-dictionary.md | 2026-10-08T00:07:55Z | `b12d902bbd7f8cf48a56cfd3b6e7c1d11bf844dc1985157af85c3e3f23ced7de` |
| C3 | Crunchbase API reference, Lookup an Organization (Advanced Financials Package) | https://data.crunchbase.com/reference/getorganization-2.md | 2026-10-08T00:07:57Z | `0b3436ada397b5d474eefd1b43f425522ba522061d57d8f70912c6721195f08c` |
| CT | Crunchbase License Agreement | https://data.crunchbase.com/docs/license-agreement.md | 2026-10-08T00:07:10Z | `75fdb70887941ece822b8c693626bf2922b46fcd1f9c67ce007f172c246e2b64` |

**What the documentation states, and what it does not.**

- **Harmonic's connector (H1).** The guide names the connector ("Under the Web tab, find Harmonic"), its address and its tools by category: enrichment tools ("Get rich info about companies, people, and investors. Deal data is available as an add-on"), search tools, lookup tools, saved search tools ("Get results from your saved searches across companies, people, and investors, including net-new results for subscribed searches"), network mapping, list management and custom data tools. **It names no tool one by one and shows no tool's output.** The request of `erw-harmonic-1` therefore asks for tools by these categories, in plain words, and names no tool.
- **Harmonic's fields (H2).** "A data dictionary of all fields in the Harmonic platform & API": the names, meanings and types of the company, people, investor and deal fields. H1 says the connector "acts as a secure proxy between your AI assistant and the Harmonic API". **Not verified against the connector:** that a tool's output carries these fields under exactly these names and nesting. No connector was called, and the API reference itself (console.harmonic.ai/docs) answers a plain request with an empty application shell, so it was not read. The first real answer a person pastes will show it: whatever does not match is kept as given under `not_mapped` and counted on the page.
- **Harmonic leaves open:** the currency of `funding.funding_total` and `funding.last_funding_total` (typed "Currency", no currency stated; the valuation fields say "in USD"), so the page shows those two as plain numbers with that remark on hover; the fields of an item of `people[]` and of `funding.investors[]` inside a company record (the format asks for people as person records, which H2 does document, and takes `funding.investors` only as a list of text); the name of an investor in an investor record (`details` is documented as an object with no fields listed), so a result of a saved search carries a `name` of the envelope's own beside its `record`; and every value of `stage`, `ownership_status`, `funding.last_funding_type` and `founding_date.granularity` (taken as text, shown as given).
- **Crunchbase's connector (C1).** The tool reference "documents every tool the Crunchbase MCP server exposes": `cb_expert_resolve_entity`, `cb_entity_autocomplete`, `cb_entity_get` (with `field_ids`, `card_ids`), `cb_search_query`, `cb_expert_build_search`, `cb_expert_query_answer`, `cb_reference`, the `cb_list_*` tools and `cb_metering_get_state`. It states that "Each entity in the results carries a `url` field linking to its Crunchbase profile." The request of `erw-crunchbase-1` asks for the resolution, lookup and search tools in plain words and forbids the list tools, which write.
- **Crunchbase's fields (C2, C3).** C2 lists every field with "the exact identifier returned by the API"; C3 holds the schema of an organization, a funding round and a person, with the shapes of a money value (`value`, `currency`, `value_usd`), a date with precision, an identifier and a link, and the cards of an organization (`founders`, `raised_funding_rounds` among them). Crunchbase's overview says "Everything available through the Crunchbase API is available through the MCP server". **Not verified against the connector:** the nesting in which `cb_entity_get` hands fields and cards back (C1 does not show it), which is why the envelope puts fields under `organization` and cards under `cards` by its own names.
- **Four entries of C2 carry a description that belongs to another field** (`closed_on`, `ipo_status`, `last_equity_funding_type`, `num_exits`). None of the four is mapped.

### The two formats

Both are an envelope of the ERW's own around records under the provider's own names. The envelope is checked strictly (a wrong format, another run, no date, no company list, a company with no name or no `found`, more than 300 companies, 100 additional companies or 400 KB is refused in plain words). **A record's content never refuses an answer:** a documented field is mapped only when its value has the documented shape; anything else (a field no page names, a documented field with another shape, an object with a key its schema does not have) is kept exactly as given under `not_mapped`, in its own nesting, and is never read as a fact. A null is no value.

`erw-harmonic-1`:

- `format`, `run_id`, `pulled_on` (YYYY-MM-DD).
- `companies[]`: `name` (the name asked), `found`, `company` (a Harmonic company record), `people[]` (Harmonic person records). A company not found keeps its name.
- `additional_companies[]`: the same, with `why` (the words of the search that matched).
- `saved_searches[]`: `name` (the saved search's name), `of` ("companies", "investors" or "people"), `results[]`, each a `name` and a `record` (a Harmonic company, investor or person record). Left out unless the person names saved searches in the request.

`erw-crunchbase-1`:

- `format`, `run_id`, `pulled_on`.
- `companies[]`: `name`, `found`, `organization` (the organization's fields under Crunchbase's field ids), `cards` (`founders`, `raised_funding_rounds`).
- `additional_companies[]`: the same, with `why`.

### The fields that are mapped, and where each is documented

**Harmonic, a company record (`company`, and the `record` of a result of a saved search of companies)**: 31 fields.

| Field | Shape accepted | Documented on |
|---|---|---|
| `id` | text or a whole number, kept as text | H2 |
| `entity_urn` | text | H2 |
| `name` | text | H2 |
| `legal_name` | text | H2 |
| `description` | text, cut at 1,200 characters | H2 |
| `short_description` | text, cut at 1,200 characters | H2 |
| `website.url` | text | H2 |
| `website.domain` | text | H2 |
| `founding_date.date` | a date or timestamp, kept as given | H2 |
| `founding_date.granularity` | text | H2 |
| `headcount` | a whole number, zero or more | H2 |
| `ownership_status` | text | H2 |
| `company_type` | text | H2 |
| `stage` | text | H2 |
| `location.location` | text | H2 |
| `location.city` | text | H2 |
| `location.state` | text | H2 |
| `location.country` | text | H2 |
| `headquarters` | text | H2 |
| `funding.funding_total` | a number, zero or more | H2 |
| `funding.num_funding_rounds` | a whole number, zero or more | H2 |
| `funding.investors` | a list of text | H2 |
| `funding.last_funding_at` | a date or timestamp, kept as given | H2 |
| `funding.last_funding_type` | text | H2 |
| `funding.last_funding_total` | a number, zero or more | H2 |
| `funding.funding_stage` | text | H2 |
| `funding.valuation_info.amount` | a number, zero or more | H2 |
| `funding.valuation_info.source` | text | H2 |
| `socials.linkedin.url` | text | H2 |
| `socials.crunchbase.url` | text | H2 |
| `socials.pitchbook.url` | text | H2 |

**Harmonic, a round of a company's `funding_rounds` (deal data)**: 9 fields.

| Field | Shape accepted | Documented on |
|---|---|---|
| `entity_urn` | text | H2 |
| `announcement_date` | a date or timestamp, kept as given | H2 |
| `funding_round_type` | text | H2 |
| `funding_amount` | a number, zero or more | H2 |
| `funding_currency` | text | H2 |
| `valuation_info.amount` | a number, zero or more | H2 |
| `post_money_valuation` | a number, zero or more | H2 |
| `source_url` | text | H2 |
| `completion_status` | text | H2 |

**Harmonic, an investor of a round (`funding_rounds[].investors[]`)**: 4 fields.

| Field | Shape accepted | Documented on |
|---|---|---|
| `investor_name` | text | H2 |
| `is_lead` | true or false | H2 |
| `entity_urn` | text | H2 |
| `investor_urn` | text | H2 |

**Harmonic, a person record (`people[]`, and the `record` of a result of a saved search of people)**: 7 fields.

| Field | Shape accepted | Documented on |
|---|---|---|
| `id` | text or a whole number, kept as text | H2 |
| `entity_urn` | text | H2 |
| `full_name` | text | H2 |
| `first_name` | text | H2 |
| `last_name` | text | H2 |
| `linkedin_headline` | text | H2 |
| `socials.LINKEDIN.url` | text | H2 |

**Harmonic, an entry of a person's `experience`**: 6 fields.

| Field | Shape accepted | Documented on |
|---|---|---|
| `title` | text | H2 |
| `department` | text | H2 |
| `company_name` | text | H2 |
| `is_current_position` | true or false | H2 |
| `start_date` | a date or timestamp, kept as given | H2 |
| `end_date` | a date or timestamp, kept as given | H2 |

**Harmonic, an investor record (the `record` of a result of a saved search of investors)**: 10 fields.

| Field | Shape accepted | Documented on |
|---|---|---|
| `id` | text or a whole number, kept as text | H2 |
| `entity_urn` | text | H2 |
| `type` | text | H2 |
| `aum_amount_usd` | a number, zero or more | H2 |
| `check_size_min_usd` | a number, zero or more | H2 |
| `check_size_max_usd` | a number, zero or more | H2 |
| `investment_count` | a whole number, zero or more | H2 |
| `exit_count` | a whole number, zero or more | H2 |
| `num_portfolio_companies` | a whole number, zero or more | H2 |
| `most_recent_investment_date` | a date or timestamp, kept as given | H2 |

**Crunchbase, an organization (`organization`)**: 29 fields.

| Field | Shape accepted | Documented on |
|---|---|---|
| `identifier` | Crunchbase's identifier object: value, permalink, uuid, entity_def_id, image_id, location_type | C3 |
| `uuid` | text | C2 |
| `permalink` | text | C2 |
| `name` | text | C2 |
| `legal_name` | text | C2 |
| `short_description` | text, cut at 1,200 characters | C2 |
| `description` | text, cut at 1,200 characters | C2 |
| `founded_on` | Crunchbase's date object: value, precision | C3 |
| `num_employees_enum` | text | C3 |
| `funding_total` | Crunchbase's money object: value, currency, value_usd | C3 |
| `equity_funding_total` | Crunchbase's money object: value, currency, value_usd | C3 |
| `last_funding_at` | a date or timestamp, kept as given | C2 |
| `last_funding_type` | text | C2 |
| `last_funding_total` | Crunchbase's money object: value, currency, value_usd | C3 |
| `funding_stage` | text | C2 |
| `num_funding_rounds` | a whole number, zero or more | C2 |
| `valuation` | Crunchbase's money object: value, currency, value_usd | C3 |
| `valuation_date` | a date or timestamp, kept as given | C2 |
| `location_identifiers` | a list of identifier objects | C3 |
| `founder_identifiers` | a list of identifier objects | C3 |
| `investor_identifiers` | a list of identifier objects | C3 |
| `num_investors` | a whole number, zero or more | C2 |
| `num_lead_investors` | a whole number, zero or more | C2 |
| `operating_status` | text | C2 |
| `status` | text | C2 |
| `company_type` | text | C2 |
| `website_url` | text | C2 |
| `website` | Crunchbase's link object: value, label | C3 |
| `url` | text | C1 |

**Crunchbase, a funding round (`cards.raised_funding_rounds[]`)**: 10 fields.

| Field | Shape accepted | Documented on |
|---|---|---|
| `identifier` | Crunchbase's identifier object: value, permalink, uuid, entity_def_id, image_id, location_type | C3 |
| `announced_on` | a date or timestamp, kept as given | C3 |
| `investment_type` | text | C3 |
| `money_raised` | Crunchbase's money object: value, currency, value_usd | C3 |
| `post_money_valuation` | Crunchbase's money object: value, currency, value_usd | C3 |
| `pre_money_valuation` | Crunchbase's money object: value, currency, value_usd | C3 |
| `lead_investor_identifiers` | a list of identifier objects | C3 |
| `investor_identifiers` | a list of identifier objects | C3 |
| `num_investors` | a whole number, zero or more | C3 |
| `url` | text | C1 |

**Crunchbase, a person (`cards.founders[]`)**: 7 fields.

| Field | Shape accepted | Documented on |
|---|---|---|
| `identifier` | Crunchbase's identifier object: value, permalink, uuid, entity_def_id, image_id, location_type | C3 |
| `name` | text | C3 |
| `first_name` | text | C3 |
| `last_name` | text | C3 |
| `primary_job_title` | text | C3 |
| `linkedin` | Crunchbase's link object: value, label | C3 |
| `url` | text | C1 |

113 fields in all: 67 of Harmonic's, 46 of Crunchbase's. `tests/test_session150.py` finds each one in its saved page on a machine that holds the pages, and checks the pages' hashes against this table.

### From a provider's fields to the run's facts

A fact is one named figure of a company. The three providers feed the same list of facts, so the same fact of two providers stands side by side.

| Fact | PitchBook (`erw-pitchbook-1`) | Harmonic | Crunchbase |
|---|---|---|---|
| Listed as | `pitchbook_name`, when it differs from the name asked | `name`, when it differs | `identifier` (its `value`), when it differs |
| Legal name | | `legal_name` | `legal_name` |
| Total raised | `total_raised_usd_m` | `funding.funding_total` (currency not stated by H2: shown as given) | `funding_total` (`value_usd`; else `value` with its currency) |
| Last round | `last_round`: type, date, size | `funding.last_funding_type` (else `funding.funding_stage`), `funding.last_funding_at`, `funding.last_funding_total` | `last_funding_type`, `last_funding_at`, `last_funding_total` |
| Lead investors of the last round | | the round of `funding_rounds` with the latest `announcement_date`: each `investor_name` whose `is_lead` is true | the round of `raised_funding_rounds` with the latest `announced_on`: `lead_investor_identifiers` |
| Post-money valuation | `last_round.post_valuation_usd_m` | that latest round's `valuation_info.amount` ("post-money valuation in USD") | `valuation` ("Latest post money valuation"), with `valuation_date` on hover |
| Valuation, announced or estimated | | `funding.valuation_info.amount`, with `funding.valuation_info.source` on hover | |
| Financing status | `financing_status` | | |
| Ownership status | | `ownership_status` | |
| Funding stage | | `stage` | `funding_stage` |
| Status | | | `status` (else `operating_status`) |
| Headquarters | `hq` | `location.city`, `location.state`, `location.country` (else `location.location`, else `headquarters`) | `location_identifiers` (their `value`s, in the order given) |
| Founded | `founded_year` | the year of `founding_date.date` | the year of `founded_on` |
| Employees | `employees` | `headcount` | `num_employees_enum`, read as its range ("c_00011_00050" is 11 to 50, as C3 lists the codes) |
| Founders | `founders` | the `full_name` of each person whose `title`, in the `experience` entry at this company, holds the word "founder" | `founder_identifiers` (else the names of `cards.founders`) |
| People | | up to ten people: `full_name` with that `title` | `cards.founders`: name with `primary_job_title` |
| Lead investors | `lead_investors` | | |
| Investors | `investors` | `funding.investors` | |
| Top five investors | | | `investor_identifiers` ("The top 5 investors with investments in this company, ordered by Crunchbase Rank": a different fact from a full list, so it has a name of its own) |
| Description | `description` | `short_description` (else `description`) | `short_description` (else `description`) |
| Website | | `website.url` | `website_url` (else `website`) |
| Funding rounds | | `funding.num_funding_rounds` | `num_funding_rounds` |
| Profile | | | `url` |

The other mapped fields (ids, URNs, links to social profiles, a round's own fields) are kept in the stored record and feed no fact yet. For the results of a saved search of investors or of people the page shows the mapped fields under Harmonic's own field names; a result of a saved search of companies is drawn with the facts above.

**Two readings in this table are the ERW's, not the provider's**, and are named so here: a "founder" is read from a title that holds the word; "the last round" of the deal data is the round with the latest date. Both are plain rules on documented fields, applied in code.

### Which provider supplied a figure, and where two differ

- **The stamp.** Every fact carries the provider's id, the format, the time its answer was pasted and the SHA-256 of the pasted text (the text as pasted, hashed by the route before anything is parsed). On the page each figure stands with the provider's name as a small label. The label's hover holds: the note stored with the answer ("Figures as returned from Harmonic through the user's own account; not checked by the ERW."), the terms line (below), the format, the time pasted, and the first twelve characters of the hash. Nothing of this is prose on the page face.
- **A figure with no provider** (everything the run itself found) keeps the label it had: its source ids, or its placeholder.
- **Disagreement.** Two values of one fact are compared only where they are of a kind that can be: an amount in US dollars to the dollar (total raised, post-money valuation), a year, a count, a count against a range (inside it or not), a place as text without case and punctuation, a set of names, and a round by its date (to the precision both give) and its amount. Where they differ the fact is marked "differs" on each provider's line, with the hover "The providers give this differently. Each value is shown as its provider gave it." Every value stays: none is averaged, none is preferred and none is dropped (`providers.disagreements`, which only names the facts to mark). Prose and the lists the providers define differently (description, people, the top five investors) are shown side by side and never marked.
- **Harmonic's amounts are compared as given.** H2 does not state their currency, so "18,200,000" from Harmonic is compared with PitchBook's "USD 18 million" as numbers. A difference of currency would show as a disagreement, which is the safe side: both values are on the page.
- **A run that holds PitchBook's answer alone is drawn exactly as before session 150.** The providers' column (`components/thesis/ProviderBlock.tsx`) replaces the PitchBook column only once the run holds another provider's answer.

### Where the answers are kept

- **PitchBook's answer stays on the run's row** (`thesis_runs.pitchbook`), stored by `thesis_pitchbook_accept` under the one-time key, as session 135 built it. Its record names no provider.
- **A record that names no provider is PitchBook's, in code** (`providerOf` on the site, `provider_of` on the server): this is how every request and answer written before this session is read, the pending request of run 20261006T193517Z-50a8be among them. Nothing stored is rewritten, and no test or script of this session reads that run.
- **Migration `025_thesis_providers.sql`** (written, **not applied**: the owner applies it) adds one internal table, `public.thesis_provider_results` (run, provider, format, time pasted, hash of the pasted text, payload), and two functions behind the internal token, `thesis_provider_accept` and `thesis_provider_results`. It alters nothing of `thesis_runs` and replaces none of migration 024's functions. One answer a provider and run: a second is refused, never merged. For PitchBook the table holds only the time and the hash (payload null), written after the answer itself has been stored by the old route and only when the pasted text reads as exactly the stored answer; an answer sent straight to the old route by a chat has no such row, and its label says the hash is not held.
- **Until the migration is applied** the page reads a finished run as before (the read of the new store fails, is logged and is passed over), the choice of provider and the request texts work, PitchBook's answer is accepted as before, and an answer of Harmonic or Crunchbase is refused with "The answer could not be stored."
- **Never public.** As with `thesis_runs`: row level security on, no policy, no grant to the public key, in no live set, no Redivis dataset and no download.

### Terms

Each provider's terms line says whose copy the data is, and quotes the provider's own sentence on redistribution where its public terms page answered a plain request. The line is the hover of the provider's label and of its radio button.

- **PitchBook:** "PitchBook figures here are your own licensed copy: brought by you from your own account, shown to you, and not published, redistributed or kept in the public warehouse. PitchBook's public terms page was not read: it answered a plain request with HTTP 403 on 8 October 2026." (https://pitchbook.com/terms-of-use, one request, a browser check; recorded and left.)
- **Harmonic** (HT, "Last Updated: December 9, 2025", section II.1, General Restrictions): "You will not (and will not allow anyone else to): [...] provide, sell, transfer, sublicense, lend, distribute, or otherwise allow others to access or use the Services or the data obtained through the Services;" The same page, on automated access: "You will not engage in any bulk downloading or automatic scraping of the materials in Harmonic Services." The ERW's code asks Harmonic for nothing; this session asked for nine of its public pages once each (six help articles, its terms, and two addresses of its API reference that answered with an empty application shell).
- **Crunchbase** (CT, License Agreement, "Redistribution of Data"): "Except as otherwise expressly set forth herein, Licensee may not license, sublicense, sell, offer to sell, distribute or otherwise provide any Crunchbase data to any third parties." Its Data Access Terms (https://data.crunchbase.com/docs/terms.md, effective 26 November 2024, SHA-256 `e28632dabb51b1822ef9409204b5d9ab53bb0d8f381b117917291e85e8da6cb7`) add, among the restrictions on a licensee: "(iii) use or allow the Crunchbase Materials to be used in a manner that makes it impossible for the Crunchbase Materials to be expunged". **For the owner's ruling:** which of the two documents governs a seat of Crunchbase's connector is not said on either page; and a stored answer can today be removed only by deleting its row by hand (it goes with its run), so a way to expunge one provider's answer from a run may be wanted before a Crunchbase answer is kept.

### What is not done

- No real answer of any provider has passed through: none could, since no connector may be called from here. The formats of Harmonic and Crunchbase are built from documentation and proven on made-up examples (`site/scripts/thesis-providers-fixtures.mjs`), as session 135's was.
- Harmonic's saved searches are asked for only by the names the person writes into the request; the page does not list a person's saved searches.
- The capital tab (rounds one by one) is not fed by the providers' round data: the rounds are stored with the answer and feed only the last round's lead investors and valuation.

## The owner's rulings of 8 October 2026 (session 158)

**Internal, as the rest of this note.** The owner's words: "for the Thesis Builder, a company name made of the niche's own words counts only when matched as a proper noun (capitalized, or with its domain, or in a list of companies), near-duplicate sentences count once, and data vendors' public pages are read but labeled as vendor pages in the report; Crunchbase answers are not kept until I rule on its terms." They close gaps (1) and (2) of session 147 above. No point, threshold, tie or tie-break changed: `TIERS` 3, 2, 1; `MIN_TERMS` 2; `STRONG_TERMS` 3; `STRONG_POINT` 1; `TIE_MIN` 2; `MAX_ADDRESSES` 3; the order of rule 4; the pipeline's 60 and 10; `STAGE_USD`. `tests/test_session158.py` asserts each, and the lines of `tie.py` that score, tie and order, word for word.

### A name made of the niche's own words (`tie.py`, rule 1)

- **Which names.** A name is made of the niche's own words when every word of it (normalized by `name_key`, each folded) is a word of the niche's own name (the words before its first comma, four letters or more, not a stop word), a term of one of the five trends (`trend_terms`), or one of the rule's generic or stop words (`GENERIC`, `STOP`), and at least one is a word of the niche's name or a trend's term. `tie.niche_own` and `tie.made_of_niche`. In the geothermal niche: "Geothermal Technologies" is; "Geothermal Radar", "Quaise Energy" and "Geothermal Strategy Partners" are not. A name of generic words alone ("Energy Technologies") is not either: it holds no word of the niche, and is matched as before.
- **How such a name is matched.** The text must hold the name's words, as before, and pass one of three tests (`tie.proper_noun`, tried in this order):
  1. **capital:** the name stands with the capitals the company's rows write it with, and is not part of a longer capitalized name. The word just before it (only spaces or a hyphen between) must not start with a capital, unless it is one of a fixed list of small words (The, In, And, For ...: `SMALL_WORDS`); the word just after it must not start with a capital, unless it is a legal form (Inc, LLC ...) or a role (CEO, Founder ...). "The DOE Geothermal Technologies Office" is not the company. Two limits: a name of one word that opens the sentence shows nothing by its capital; and in a heading written with every word capitalized (two or more words of four letters or more outside the name, none a small word, all starting with a capital) no capital shows a proper noun.
  2. **list:** the name, with its capitals, is one whole item of an enumeration of three or more (`LIST_MIN`) capitalized names standing side by side. The text is cut at each comma, semicolon, bar or bullet and at "and", "or" and "&"; an item is a capitalized name when it is one to six words that each start with a capital; the first item of a sentence may have other words before its name and the last may have other words after it. A table cell or list item that is the name alone is the first test.
  3. **domain:** the text holds the company's website domain (the row's website, or a domain written in the brackets of its name), or the page or fetched source the text is from is at that domain (or under it), or holds the domain in its text.
- The same test is applied wherever the rule asks whether a text names the company: a sentence of a saved page, a fetched title or cited passage, and the cells of a row of `energy_deals`. Every other company is matched as before (`names_norm`, untouched).
- **On record.** Each evidence line of such a company says which test counted it (`named`), and the run's state lists the company, its written name, its domains, the count by test and the sentences that held its words and were not counted, with five examples (`state["tie"]["name_rule"]`).
- **What it does not catch.** A heading or a label that is the name's words with capitals and something else after a colon ("Geothermal Technologies: grants") passes the first test. A real headline about the company written with every word capitalized fails it, and counts only by its domain or in a list.

### The same remark counts once (`tie.py`, rule 3)

- **A remark.** The words of a sentence in lower case with punctuation removed; when the sentence holds a quotation of 8 words or more (`NEAR_MIN_WORDS`), only the words inside its quotation marks: the words around a quotation say who spoke. `tie.remark`.
- **The same remark.** Two sentences are one remark when both have 8 words or more and the words they share, each counted as often as both hold it, are 90 percent or more (`NEAR_SAME`) of the words of the longer one. `tie.remark_share`, `tie.same_remark`. A short sentence inside a much longer one is therefore not the same remark.
- **Which copy counts.** As for the same sentence since session 142: of each address the best supporting sentence is taken, the addresses are read highest points first, then the higher tier, then the address a to z, and a sentence that is the same remark as one already counted is not counted. So the higher-tier copy is kept. An address whose best sentence is such a copy adds nothing for that trend, exactly as an address whose best sentence is the same sentence adds nothing.
- **On record.** Every merged pair is in the run's state with both addresses, both tiers and the share (`state["tie"]["near_duplicates"]`), and its count is in the run's log.
- Tested on the saved real pair: Quaise Energy's chief executive, one remark on energycapitalhtx.com ("... Carlos Araque, CEO and president of Quaise, said in a release.") and on quaise.com ("... said Carlos Araque, CEO and President of Quaise Energy."): share 1.0 inside the quotation marks. It was 1 + 1 = 2 points, tied; it is 1 point, not tied.

### Data vendors' public pages (`pages.py`, `vendor_pages.csv`, rule 7)

- A data vendor is a business that sells a database of companies, rounds or investors by subscription. The list is one file, `warehouse/thesis/vendor_pages.csv`, a row a domain with the vendor's name, the reason, the day first met and what was met: cbinsights.com, dealroom.co and sacra.com (their public pages held text in session 147), zoominfo.com and ventureradar.com (met in session 147, nothing received). A host matches when it is the domain or under it.
- **Read as any other page.** One plain request, the one header, robots.txt, the ceilings: nothing in the pull changes for them. The page's record carries the vendor's name, the run's tally lists the vendor pages cited and how many hold text.
- **Labeled.** Every sentence the rule reads from such a page (and every title or passage fetched from one) carries the vendor's name (`vendor` on the evidence line and on a scoring line). The label changes no point.
- **On the page.** When the sentence shown under "Why it is here" comes from one, the report's row carries `reason_vendor` and the page draws the short mark "vendor page" after the sentence, with the hover "This sentence is from a public page of a data vendor (NAME), not from the company or the press." Nothing else of this is on the page face.
- **Still refused before any request:** pitchbook.com, crunchbase.com, harmonic.ai (`LICENSED_HOSTS`), and misoenergy.org. They are not in the vendor file and a test holds them out of it.

### Crunchbase answers are not kept

- `NOT_KEPT` in `warehouse/thesis/providers.py` and in `site/lib/thesis/providers.ts` names the provider and the plain words: "Crunchbase answers are not kept until its terms are ruled on". A test on each side checks the two say the same.
- `POST /api/thesis/provider` refuses a request that names the provider with those words (400) before the pasted text is looked at, before a hash is made and before the database is asked; `checkPaste` refuses too, and an answer in Crunchbase's format pasted under another provider gets the same words. In Python no stamp can be made of such an answer (`providers.stamp` raises `NotKept`).
- On `/thesis` the choice lists Crunchbase with its button off and the mark "not yet available", those words on hover; its request text cannot be copied.
- Nothing stored is rewritten or removed, no migration was made, and the format, the request text and the reader of `erw-crunchbase-1` stay in the code: the ruling is lifted by removing the provider's line from the two lists. The database function of migration 025 itself does not refuse a Crunchbase row; the route is the gate.
- PitchBook and Harmonic are as they were.

### A run on the runner keeps what it paid for, and can hold the trends fixed (`store.py`, `run.py`, `thesis.yml`)

- The runner's files are discarded with it. Until session 158 a run there kept its report (in its row) and its evidence (in the bucket), and lost its state: the notes and the structured rows the model returned. Now a run whose evidence store is the bucket also writes its state as an object of the same private bucket, `states/<niche>_<run id>.json.gz`, written once and never replaced, with the run's own rows of the cost ledger in it; a run stopped at its spending limit or failed after a paid call writes `states/partial_<run id>.json.gz` the same way. A refusal of the bucket is logged and never costs the run.
- `run.py --landscape-from bucket:<name>` reads a saved state from `states/<name>.json.gz` before anything is paid for. With it `thesis.yml` can make the like-for-like run of sessions 142 and 147 on the runner: the inputs `niche`, `stage`, `geography`, `landscape_from`, `max_usd` and `session` start one run by hand, kept in `thesis_runs` as the page's runs are, with the same evidence store and the same pull. With `niche` empty the workflow does what it did: the page's runs are untouched.
