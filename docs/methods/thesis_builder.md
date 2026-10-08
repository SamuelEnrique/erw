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
