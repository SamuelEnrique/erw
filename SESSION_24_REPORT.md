# Session 24 report

Energy Research Warehouse (ERW), session 24, run 2026-09-28 (UTC). **API spend: USD 7.0098**, under the USD 10 stop:
- **Policy scoring:** USD 3.3295 (0.2931 for a first test of 160 actions, then 3.0364).
- **Impact reads:** USD 3.6803 (0.0553 for a first test of 4, then 3.4810, then 0.1440).

No key was printed or committed.

**Things to know first:**
- **The policy monitor exists (tool 12):**
  - `policy_actions` holds 1,819 energy actions since 2025-10-01, all scored with the news rubric; 227 score 5 or more.
  - `policy_reads` holds impact reads of 226 of them, each field kept only when its quoted words are in the action's own text.
  - A 15-read spot check found **59 of 62 kept fields correct**.
  - The site's `/policy`, the Roundup's Policy of the week and a Policy group in the digest show them.
- **FERC's own pages were not read.** ferc.gov and eLibrary answer a Cloudflare JavaScript challenge, and FERC's RSS files answer HTTP 403. FERC's actions come through the Federal Register: 850 rows.
- **The NWS keeps only about 7 days of station observations.** `weather_obs_hourly` asks for 30 days, holds 2026-09-21 to 2026-09-28, and grows as daily runs merge. The Boston forecast (KBOS) answered HTTP 503 four times; the other six stations have one.
- **One read was blocked by the permission check.** Early in this session a command to display `warehouse/news/score.py` (the file the prompt asks to read first) was denied by Claude Code's auto-mode classifier, labelled "out-of-place publication". I did not read the file by any other route. Task 2 imports the scorer's own `SYSTEM`, `SCHEMA`, `pick_model` and `PRICES`, whose shape I knew from reading part of the file earlier in the same session. If you want the file re-read, allow it and ask.

## What was built

| Task | Result | API cost (USD) | Commit |
|---|---|---|---|
| 1 | `warehouse/connectors/policy_sources.py`, `policy_actions` (1,819 rows) | 0 | `af0dfb3` |
| 2 | `warehouse/policy/score.py` and `reads.py`, `policy_reads` and its evidence table, spot check | 7.0098 | `3192479` |
| 3 | `/policy`, Policy of the week (Roundup and email), a Policy group in the digest | 0 | `c3ef119` |
| 4 | `warehouse/connectors/weather_nws.py`, the two weather tables, the `/grid` temperature overlay and degree days | 0 | `9e7ca41` |
| 5 | `docs/platform-tools.md` with 31 tools and a table by audience; `CLAUDE.md`, `README.md`, `docs/OVERVIEW.md`, `/about` | 0 | `fa3bfca` |
| 6 | Validator (112 of 112), coverage (112 tables), live set, briefing, chat spec, value check 704 of 704, screenshots, this report | 0 | final commit |

## Task 1: policy sources

Everything below is free and public, and every response is stored raw under `warehouse/raw/policy_sources/<run_id>/`.

| Source | Read | Rows |
|---|---|---|
| Federal Register API | Rules, proposed rules and notices of DOE (FERC is filed under it), FERC, EPA, NRC, BLM and Interior since 2025-10-01: 4,751 documents. EPA, BLM and Interior are kept only when the title, abstract or Register topics name an energy subject. Routine paperwork is left out: information collections, meetings, Sunshine Act notices, Privacy Act systems, FERC's combined notices of filings and similar. | 1,584 |
| NRC news (RSS) | Everything since 2025-10-01 in the feed | 159 |
| DOE newsroom (RSS) | Only the feed's window: the feed holds its latest 10 items | 10 |
| Texas PUC news page | Every dated item since 2025-10-01, including the Governor's releases on PUCT programs that the page lists | 36 |
| CPUC news (19 pages) | 180 items since 2025-10-01, 36 of them on energy (the CPUC also regulates rail, water and telecommunications); 31 remain after duplicate links are dropped and one is folded into a Register document | 31 |
| FERC news and eLibrary | Not read: Cloudflare challenge and HTTP 403 | 0 |

- **Rows by agency:** FERC 850, NRC 467, EPA 164, DOE 146, Interior 75, BLM 50, PUCT 36, CPUC 31.
- **Columns:** agency, action type (rule, proposed rule, notice, news release), title, the Register's abstract, docket ids and RINs, document number, sector tags (keyword rules), states named, and links.
- **Deduplication:**
  - A news release reporting a Register document (same agency, similar title, within 30 days) is folded into it as a related link. One was folded.
  - Actions are linked to the scored `news_stories` that report them, by a docket, RIN or document number in the story, or a title with the same content words within 21 days: 12 actions.
  - The agencies' own feed items already in `news_stories` are linked by URL.
- **Runs daily** after the news index. `policy_actions` is restored from the Redivis draft in CI, so news releases older than a feed's window are kept.

## Task 2: scores and impact reads

- **Scoring (`warehouse/policy/score.py`)** uses the news scorer's own system prompt with the rubric, its schema and its model choice, imported from `warehouse/news/score.py`. Each item is the action's title and the Register's abstract, with the beat "policy". Scores are cached in `warehouse/policy/scores.csv` (in git), so an action is scored once.

  | Significance | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
  |---|---|---|---|---|---|---|---|---|---|---|
  | Actions | 7 | 575 | 577 | 274 | 159 | 77 | 95 | 40 | 11 | 4 |

- **Reads (`warehouse/policy/reads.py`)** cover actions scored 5 or more.
  - **The source text** is the Register's plain text of the document from its SUMMARY on (at most 9,000 characters), or the release's page or PDF. It is stored under `warehouse/raw/policy_reads/`.
  - **The model returns JSON:** what changes; who is affected (sectors, ISOs, states); the direction of effect on supply, demand, prices and buildout; the timeline; and a two-sentence plain read. Each field comes with exact spans.
  - **A field is kept only if** it has a span, every span is found word for word in the stored text, and every number in it is in its spans.
  - **Tables:** `policy_reads` (public: the kept fields and links) and `policy_reads_evidence` (internal: the spans).
- **Result:** 226 of 227 read; one answer was malformed JSON twice and is left for the next run.
  - All five fields kept: 97 reads.
  - Kept per field: who_affected 211, direction 206, timeline 201, what_changes 168, plain_read 161.
  - The commonest reason a field was dropped: a number not in its spans (plain_read 44, what_changes 34 in the main run), usually a date the model restated.
- **Spot check** of 15 reads drawn at random, field by field: **59 of 62 kept fields correct**. The extractor was not changed afterwards; the check is in `warehouse/policy/eval/spot_check_s24.csv`. The three errors:
  1. **NRC, Kemmerer construction permit review:** who_affected lists coal because the site is beside a coal plant.
  2. **NRC fee rule:** direction says prices down, reading a cut in licensing fees as a fall in energy prices.
  3. **TRISO-X draft EIS:** plain_read says "for the first time in the United States", which its spans do not state.

## Task 3: the site, the Roundup, the digest

- **`/policy`:**
  - a "this week in policy" strip (the week's actions scored 5 or more, with their plain reads);
  - a table filterable by agency, type, sector, state, significance (default 5 or more) and date;
  - each row expands to the read, the affected sectors, ISOs and states, the direction of effect, the timeline, the fields dropped and why, the source, docket or RIN, and the news stories.

  Added to `pages.ts` under Projects, next to Deals.
- **The Roundup's Policy of the week:** the week's highest-scored action (ties go to a final rule), with its read and the next two. The email carries it too. Tested on 2026-W39: DOE's "Speed to Power" investments across 26 states (significance 7).
- **The digest's By sector:**
  - Policy is now its own group, with the day's actions scored 5 or more under the policy stories.
  - The former "Policy and capital" group is now "Capital and companies".
  - Tested on 2026-09-26: three actions (DOE's Colorado coal order, NRC's Crane Clean Energy Center EA, CPUC's Liberty penalty).

## Task 4: weather

- **`warehouse/connectors/weather_nws.py`** reads api.weather.gov (no key; the User-Agent names the ERW and its repository), at one airport per ISO load center:
  - ERCOT KDFW, CAISO KLAX, NYISO KLGA, ISO-NE KBOS, PJM KPHL, MISO KIND (the ERW's MISO hub is INDIANA.HUB), SPP KOKC.
- **The two tables:**
  - `weather_obs_hourly`: the mean of the station's observations in each UTC hour. 2,346 rows, 2026-09-21 to 2026-09-28.
  - `weather_forecast_hourly`: the NWS hourly gridpoint forecast, about 156 hours. 1,872 rows; the vintage is the forecast's update time.
- **Units:** temperature in degF and wind in mph. **`mph` joins the unit vocabulary** (data standard decision 27; the validator and the standard updated together).
- **Refresh:** daily, restored from Redivis in CI so the observations accumulate past the API's week. Both tables are in the live set.
- **`/grid`:**
  - each ISO's 7-day demand chart carries the station's observed temperature on a second axis; the shared `TimeChart` gained a right axis;
  - a degree-days line per ISO gives CDD or HDD per UTC day, base 65 F, from the day's 24 hourly means;
  - a day short of 24 hours says "not computed", with the count;
  - the citation names the NWS.

## Task 5: the tool plan

`docs/platform-tools.md` has 31 tools with status:
- **Planned, new:** 27 Thesis Builder, 28 problem set builder, 29 Run the grid (with Rim Baltaduonis, research first), 30 case study builder (HBS format), and 31 energy meme generator.
- **Updated:** tool 12 (policy) and tool 7 (weather).

A second table groups the tools by audience: enthusiasts, investors, researchers, traders and educators.

The counts now read: 6 yes, 17 partial, 3 no, 5 planned.
- `/about` gains a "The platform" paragraph whose counts `build-content.mjs` reads from the file at build time.
- `CLAUDE.md` says 31 tools, five of them planned, and `README.md` points to the list.
- `docs/OVERVIEW.md` is regenerated: 112 tables, 19 pages, 23 live tools.

## Task 6

- **Validator:** 112 of 112 tables pass.
- **Coverage:** 112 tables. The five new tables: `policy_actions`, `policy_reads` and `policy_reads_evidence` (internal) under news, and the two weather tables under power.
- **Live set:** `policy_actions` (1,819), `policy_reads` (226) and both weather tables are loaded. The catalogue (112) and sources (149) match, and `pg_database_size` is 334.0 MB of 400.
- **Briefing:** `package/llms.txt` covers policy and weather.
- **Chat spec:** `site/lib/chat/spec.json` was regenerated, as `ARCHITECTURE.md` requires whenever `llms.txt` changes. Session 23 changed `llms.txt` without regenerating it.
- **Value check:** 704 of 704 values match Supabase (`/roundup`: 20 of 20).
- **Screenshots:** every page at 1280 and 390 px, plus `/policy`. It is long at the default filter (227 rows): the mobile capture is cut at 12,000 px of 39,209.

## Decisions made without a human

1. **FERC comes through the Federal Register.** FERC's site answers a JavaScript challenge, and working around it would defeat an access control.
2. **Routine Register paperwork is left out of the table,** and EPA, BLM and Interior are kept only on energy subjects.
3. **Every action is scored,** not a subset. It cost about USD 0.0018 per action.
4. **Temperature is stored in degF,** not the API's degC: degF is in the vocabulary and is the degree-day convention. mph was added for wind.
5. **Stations:** DFW for ERCOT, Indianapolis for MISO and Philadelphia for PJM. Each is one airport where the prompt asked for one.
6. **Degree days use UTC days,** matching `/grid`'s UTC days, and need all 24 hours.

## Open questions for a human

1. **FERC news and eLibrary:** is there an access route you would accept, such as an eLibrary API key or a data feed?
2. **Reads' dropped fields:** the number rule drops a field whose model text restates a date differently from its spans. Should dates be exempt when the date appears in the source text?
3. **The `score.py` read denied by the permission check:** allow it if you want the file reviewed again.
4. **State PUCs beyond Texas and California** are not covered.
