# Session 25 report

Energy Research Warehouse (ERW), session 25, run 2026-09-28 (UTC). **API spend: USD 6.6299**, under the USD 15 stop:

| Item | USD |
|---|---|
| Today's digest regenerated in the new voice (headlines 0.0210, numbers summary 0.0072) | 0.0282 |
| One new fun fact | 0.0194 |
| First Thesis Builder smoke run, stopped on a warehouse-tool bug | 0.2419 |
| Second smoke run, stopped at its USD 1.50 cap | 1.5261 |
| Geothermal run | 2.4141 |
| Battery storage software run | 2.4002 |

A third start was stopped before its first call, to add the saved state, and cost nothing. No key was printed or committed.

**Things to know first:**
- **The ERW has a voice and a name.**
  - `docs/voice.md` is read into every writer's system prompt.
  - The products are ERW's Energy Digest, ERW's Roundup, ERW's Numbers Today and ERW's Numbers This Week, ERW's Fun Fact, ERW's Chart of the Week, and ERW's Policy of the Week.
  - The digest and the Roundup are signed "ERW".
  - A new original mark replaces the E favicon: a cardinal square whose stem and three bars form an E that is also a bar chart. It is in the header, the favicon, the emails and the chart PNGs.
- **Thesis Builder v0 works.**
  - Two runs cost USD 2.41 and 2.40 and took 21.3 and 11.5 minutes.
  - Every number is checked against the cited passages of its sources: 31 and 11 numbers failed and are written as "not confirmed".
  - The spot check found 8 of 10 company rows and 7 of 10 capital rows fully supported.
- **One content error recurs.** For public companies (Fluence, Stem), the Raised column holds a revenue figure. The builder was not changed after the check.

## What was built

| Task | Result | API cost (USD) | Commit |
|---|---|---|---|
| 1 | `docs/voice.md` and `warehouse/voice.py`; the ERW's names and signature; the ERW mark (`docs/brand/`); today's digest regenerated | 0.0476 | `5765109` |
| 2 | `warehouse/thesis/build.py`, `docs/methods/thesis_builder.md` | smoke runs 1.7680 | `c94876d` |
| 3 | Two runs, `docs/thesis/*.xlsx`, format review, spot check | 4.8143 | `2f4a36d` |
| 4 | `warehouse/thesis/connectors/`: base class and PitchBook, Harmonic, Crunchbase stubs; the bring-your-own-license rule | 0 | `61d6337` |
| 5 | Validator 113 of 113, coverage 113 tables (with `energy_companies`), briefing, chat spec, tools list, this report | 0 | final commit |

## Task 1: the voice and the name

- **The voice (`docs/voice.md`, one page):**
  - plain, precise, dry, warm at the edges, never hype;
  - the ERW speaks as an institution: "we" only where a sentence needs it, never "I";
  - no exclamation marks, no em dashes;
  - numbers before adjectives, every claim with its source;
  - ten before-and-after examples, from the 2026-09-28 digest and the 2026-W39 Roundup.
- **Who reads it:** `warehouse/voice.py` appends it to the system prompts of the digest (headlines and numbers summary; the Roundup uses the same), the fun fact, the chart-of-the-week note, the policy reads and the Thesis Builder.
- **Names, applied to:**
  - the digest and Roundup titles and section headings;
  - the emails (the headings, "ERW" as the signature, "All of ERW's Energy Digest");
  - the home section heading, the page titles of `/digest`, `/roundup`, `/analysis` and their date and week pages;
  - `pages.ts` labels, `/subscribe` and `/about` wording.
- **Old briefs still read.** The email parser and the value check accept both the old headings and the new ones. The builder's name remains only on `/about`, `/terms` and the paper citation, as before.
- **The mark:** `docs/brand/erw-mark.svg` and `erw-wordmark.svg` are plain SVG with no external assets.
  - The site header uses an inline wordmark component, and the favicon (`site/app/icon.svg`, replaced as the prompt asked) is the new mark.
  - The chart corner mark in `style.py` draws the same geometry, and the 2026-W39 chart and social PNGs were re-rendered with it.
  - Emails draw the mark in HTML, because mail clients strip inline SVG and data URIs.
- **Today's digest was regenerated:** "ERW's Energy Digest, 2026-09-28", 73 stories. Its fun fact is the Northeast blackout of 2003, from a stored Wikipedia source. It is signed ERW, and the email renders with the new names.

## Task 2: Thesis Builder v0 (tool 27)

`python warehouse/thesis/build.py "<niche>" [--stage] [--geography] [--max-usd 6]`. The full plan is in `docs/methods/thesis_builder.md`.

- **Model:** the newest Sonnet-class model the API lists (`claude-sonnet-5`), with the web search tool `web_search_20260209` and the chat's four warehouse tools.
- **Research:** three passes: scope, fundamentals and trends; companies, capital and incumbents; risks. Every search result becomes a source S#, keeping the passages the API cites from it; every warehouse result becomes a source E#.
- **Structure:** one JSON call per sheet, then a literal-number check of every value against its cited sources. A value that fails is written as "not confirmed"; a row with no source is not written.
- **Output:**
  - the workbook, in the Stanford format;
  - `energy_companies`, merged on name plus website domain;
  - a saved state, so `--resume` can rebuild the workbook without new calls.

  Every call is logged with its tokens, searches and cost, and the run's total goes on the Scope sheet.
- **Company confidence** is a rule: 20 per independent source (up to 3), 20 or 10 for recency, and 10 each for a stage and an amount confirmed by a primary source. Each row states its clause.
- **Smoke runs found three things, all fixed before the real runs:**
  1. A warehouse tool raised a plain `ValueError` that `tools.run` does not catch. The builder now returns it to the model as a tool error.
  2. Research turns resent the whole history. They are now cached; in the second smoke run, turn inputs were read from the cache.
  3. The workbook writer had not run yet. It was tested offline with stand-in content (written to the scratchpad only, never to a table), and the saved state and `--resume` were added.
- **After run 1, the structure calls lost their cache.** Each sheet's JSON schema is part of the prompt prefix, so no cache matched and every call paid the cache-write premium. Run 2 ran without it.

## Task 3: the two runs

| Run | Cost (USD) | Time | Model calls | Web searches | Numbers not confirmed | Companies |
|---|---|---|---|---|---|---|
| subsurface heat mapping for geothermal | 2.4141 | 21.3 min | 21 | 23 | 31 | 8 |
| grid-scale battery storage software for merchant operators | 2.4002 | 11.5 min | 24 | 25 | 11 | 9 |

**Section counts** (the numbered "(n) SECTION" bars per sheet):

| Sheet | Geothermal | Battery storage software |
|---|---|---|
| Scope | 3 | 3 |
| Fundamentals | 1 | 1 |
| Trends | 5 (2 native charts, 2 Automated Analysis charts) | 5 (3 native charts, 2 Automated Analysis charts) |
| Landscape | 1 (8 companies) | 1 (9 companies) |
| Capital | 1 (18 rows) | 1 |
| Incumbents | 1 | 1 |
| Policy | 1 | 1 |
| Risks | 10 | 8 |
| Sources | 1 (the list; every URL, retrieval date, and the cells it supports) | 1 |

**Format review.** On every sheet of both workbooks:
- gridlines are off, column A is 2 wide, and titles are Georgia in cardinal;
- the header bars are cardinal with white text, and body text is 2E2D29;
- table rows alternate with fog beige;
- every section has a grey "Source(s):" line, except the Sources sheet.

One deviation from the rule that every section bar is followed by a "Fact:" paragraph: on the Scope sheet, the Value chain and Adjacent niches sections carry a table without one, and so does the Sources sheet. The Landscape Fact of the geothermal workbook opens with a warehouse number (4,049.2 MW of US geothermal nameplate, from EIA-860M through the warehouse tools), as the plan asks.

**Spot check.** `warehouse/thesis/eval/spot_check.py` samples rows at random (seed 25). It fetches each source now and searches it for the row's claims. When a publisher refuses the fetch (HTTP 403 at esgdive.com, fervoenergy.com and others), it searches the passages the search API returned instead, which the run stored. The verdicts are mine. The builder was not changed afterwards.

Company rows (5 per workbook):

| # | Workbook | Company | Checked against | Verdict |
|---|---|---|---|---|
| 1 | geothermal | Project InnerSpace | name, 16.6 million in research investments, nonprofit, Jamie Beard: all in S146 to S151 | Correct |
| 2 | geothermal | Mantle Reach Power | name in S128; stage and raised "not disclosed", as the one source says nothing | Correct |
| 3 | geothermal | Zanskar | Series C, 115 million, Carl Hoiland: in S21 to S26 and S73 | Correct |
| 4 | geothermal | Fervo Energy | public, 1.89 billion IPO (cited passage of S137, a 403 page), Tim Latimer | Correct |
| 5 | geothermal | Quaise Energy | Series B, 180 million: in S111 and S116 | Correct |
| 6 | battery software | Tyba | Series A, 13.9 million, Tyler Nisonoff: in S91 to S98 | Correct |
| 7 | battery software | FlexGen Power Systems | Series C, 100 million: in S133 to S140 | Correct |
| 8 | battery software | GridBeyond | Series D, 12 million (S73), Michael Phelan (S81) | Correct |
| 9 | battery software | Fluence Energy | public; Raised holds "Revenue of $2.3 billion for fiscal year 2025" | **Wrong column:** a revenue figure where the amount raised belongs |
| 10 | battery software | Stem, Inc. | public; Raised holds 2025 hardware revenue of 68.6 million | **Wrong column:** same error |

**Companies: 8 of 10 correct.**

Capital rows (5 per workbook):

| # | Workbook | Row | Checked against | Verdict |
|---|---|---|---|---|
| 1 | geothermal | Sage Geosystems, 2026-01, Series B, 97.0 million | S82 | Supported |
| 2 | geothermal | Fervo Energy, 2025-12-10, Series E, 462 million, led by B Capital | amount and date in S53's cited passage; "B Capital" in neither page nor passage | **Investor not supported** by its sources |
| 3 | geothermal | Bedrock Energy, 2023-10-11, seed, 8.5 million, led by Wireframe Ventures | S95 | Supported |
| 4 | geothermal | Quaise Energy, 2026-08-27, Series B final close, 180 million, led by Prelude Ventures | amount and date in S111; Prelude only in the first close's sources | **Investor not supported** by this row's sources |
| 5 | geothermal | Quaise Energy, 2026-07-07, Series B first close, 134 million, led by Prelude Ventures | S109, S110 | Supported |
| 6 | battery software | FlexGen, 2022-07-19, Series C, 100 million, Vitol | S140 | Supported |
| 7 | battery software | GridBeyond, 2024, Series C, 52 million EUR, Energy Impact Partners | amount and investors in S75's cited passage; 2024 not found | **Year not supported** |
| 8 | battery software | Tyba, 2025-02-06, Series A, 13.9 million, Energize Capital | S91, S93 | Supported |
| 9 | battery software | GridBeyond, 2026, Series D, 12 million, Samsung Ventures | S73 | Supported |
| 10 | battery software | Amperon, 2023-10-03, Series B, amount not confirmed, Energize Capital | company, year and investor in S115; the check withheld the amount | Supported (amount correctly withheld) |

**Capital: 7 of 10 fully supported; 3 carry one field (an investor or a year) their own sources do not state.** The number check only covers digits, so a name or a year in text passes it: the rule to add is a span check for investors and dates.

## Task 4: licensed connectors

`warehouse/thesis/connectors/`:
- **Interface:** `LicensedConnector` (a name, a credential environment variable, `landscape()` and `capital()` in the Landscape and Capital shapes) and `available()`, which instantiates the connectors whose credential is set.
- **Stubs:** `PitchBook`, `Harmonic` and `Crunchbase`, each mapping the vendor's documented fields to those shapes.
- **Not wired:** their API calls raise `NotWired`; the builder logs that and goes on.
- **The rows are marked** "licensed, user's own account, not stored in the ERW". They go to the workbook only, never to `energy_companies` or any store.
- **The credential** is never in a repr, log or error (tested).
- **The rule** is written in `docs/methods/thesis_builder.md` ("Bring your own license").

## Task 5

- **Validator:** 113 of 113 tables pass.
- **Coverage:** 113 tables. `energy_companies` (entities, public) is under deals, with 17 companies (8 geothermal, 9 battery software).
- **Briefing:** `package/llms.txt` gains `energy_companies`, and the chat spec was regenerated.
- **Tools list:** tool 27 is v0 (partial) and tool 10 is seeded. The counts now read 6 yes, 19 partial, 2 no, 4 planned, and `/about` reads them at build. `docs/OVERVIEW.md` was regenerated: 113 tables, 25 live tools.

## Decisions made without a human

1. **"ERW's Numbers This Week"** names the Roundup's numbers, alongside "ERW's Numbers Today", and "ERW's Policy of the Week" follows the pattern. The prompt named "ERW's Roundup" and the digest's four.
2. **Emails draw the mark in HTML,** not SVG, because mail clients strip inline SVG.
3. **The research plan has three passes and the structure has one call per sheet,** with the number check after. The web-search citations are the evidence, so the check reads the passages the API cited rather than a page fetched later.
4. **Workbooks are committed to `docs/thesis/`** (no licensed data in them). The saved states and chart images are git-ignored and rebuildable.
5. **`energy_companies` is not in the Supabase live set yet:** no page reads it.

## Open questions for a human

1. **Public companies' "Raised" column.** Should incumbents be kept out of Landscape (they are on Incumbents), or should Raised stay blank with a note when a company is public?
2. **Investor and date claims** are checked only as far as their digits. Should names and dates need a quoted span, as the fun facts and policy reads do?
3. **Licensed connectors:** wire them against a real account when one is available; the API calls are the only missing part.
4. **Cost:** about USD 2.40 a niche. Most of it is web search with dynamic filtering and the per-sheet structure calls, which cannot share a cache.
