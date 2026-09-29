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
