# The policy monitor's audit, 6 November 2026 (chain 166, sessions 3054 to 3065)

Chain 166 (`queue/done/166-night-6-november-portable-window2-policy-monitor.md`) numbered its sessions 2260 to 2271; every number from 2260 to 3053 was taken on origin's main or a branch when it started, so it runs as sessions 3054 to 3065. This file is its faults file: the ground (session 3054), the audit of the stored actions (session 3055), and the rows each later session closes.

## Ground (session 3054)

Read on 6 November 2026, about 11:30 UTC. Counts are of the live set (`events` where `table_name` is `policy_actions` or `policy_reads`, read with the service key), which matched Redivis's own counts that hour (2,020 and 408 rows, `scripts/sync.py --check`). This laptop's own copies were a month behind (1,836 actions to 1 October, 234 reads to 5 October).

### 1. What the monitor is made of

The chain file names `warehouse/news/policy*.py` as the scorer and the actions' builder. No such file exists: the monitor's code is

| Path | What it does |
|---|---|
| `warehouse/connectors/policy_sources.py` | the actions' builder: the Federal Register API (DOE, FERC, EPA, NRC, BLM, Interior, Treasury, IRS), the NRC and DOE news feeds, the PUCT and CPUC news pages, into `policy_actions`; each Register document's printed text read once (session 157) |
| `warehouse/policy/score.py` | the score: the news scorer's prompt, rubric and schema (`warehouse/news/score.py`, `warehouse/news/rubric.md`) with one added note for policy (`POLICY_NOTE`), into `warehouse/policy/scores.csv` and the table's score columns |
| `warehouse/policy/reads.py` | the impact read of an action scored 5 or more, from the action's own text, a field kept only when its quotations stand word for word in that text (`policy_reads`, `policy_reads_evidence`) |
| `warehouse/policy/recheck.py`, `rule_reads.py` | session 157's rescoring against the source text; the one-line reads of `large_load_rules` |
| `warehouse/derived/policy_action_tags.py` | the four tags (large loads, interconnection, transmission cost, tariffs) by a written rule (`warehouse/config/policy_tag_rules.json`) |
| `warehouse/connectors/policy_monitor_refresh.py`, `warehouse/derived/policy_monitor_site.py` | FERC's and ten state commissions' open dockets on large loads (`large_load_rules`), and the site's files under `site/data/policy/` |
| `site/app/policy/` (`page.tsx`, `PolicyTable.tsx`, `WeekView.tsx`, `Paused.tsx`), `site/lib/policyreads.ts`, `policyweek.ts`, `policyweekdata.ts` | the page |
| `docs/methods/policy_monitor.md` (417 lines, thirteen sections), `docs/methods/policy_action_tags.md` | the method |

Decision recorded in the report: this chain's "files it owns" are read as these paths (the chain's intent: the policy scorer, the actions' builder and the page), and `warehouse/news/score.py` and `rubric.md`, which the news scorer shares, are not changed by it; a policy change to the prompt is made in `warehouse/policy/score.py`'s own note.

**What an action is.** A row of `policy_actions` is a government document or release (a Register rule, proposed rule or notice, or an agency's news release), not a news story. Stories reach it only as links (`news_story_ids`, `news_story_urls`: a scored story that names the same docket, RIN or document number, or a title of the same content words within 21 days). The chain's steps written for stories (deduplication "across outlets", "30 stored stories") are read in that light: the record is the document, the outlets are its linked stories, and a duplicate is two documents or releases of one action.

### 2. The tables

`policy_actions` (events shape; 2,020 rows, 2025-10-01 to 2026-11-05). Columns: `event_id, event_date, event_type, parties, entity_ids, mw, price, currency, status, source, source_url, agency, action_type, title, abstract, docket, rin, fr_document_number, sector_tags, states, related_urls, news_story_ids, news_story_urls, first_paragraph, place_words, title_register, text_status, text_read_at, significance, sector, why, model_id, scored_at, model_recheck, model_rechecked_at, retrieved_at`.

| Field | Vocabulary on 6 November |
|---|---|
| `agency` | FERC 935, NRC 499, DOE 185, EPA 182, Interior 85, BLM 51, CPUC 38, PUCT 37, IRS 8 (Treasury: none kept yet) |
| `action_type` | notice 1,399, press_release 268, rule 198, proposed_rule 155 |
| `status` | the Register's action line as printed ("Final rule.", "Notice of availability.") or "news release": free text, not a status vocabulary |
| `docket` | filled on 1,688 rows |
| `states` | filled on 1,195 rows |
| `significance` | 0: 12, 1: 293, 2: 639, 3: 394, 4: 282, 5: 181, 6: 144, 7: 56, 8: 16, 9: 3 (400 at 5 or more; every row scored) |
| `sector` (the scorer's) | policy 507, nuclear 389, gas 301, renewables 287, generation 208, oil 87, other 68, lng 64, storage 44, transmission 21, grid_conditions 9, transport 9, power_prices 7, interconnection 5, geopolitics 5, capital 4, company 4, deal 1 |

Rows by ISO week (the event date): 2025-W40 16, W41 1, W42 3, W43 7, W44 2, W45 3, W46 9, W47 53, W48 76, W49 34, W50 30, W51 49, W52 19; 2026-W01 31, W02 31, W03 30, W04 33, W05 52, W06 30, W07 43, W08 37, W09 52, W10 29, W11 52, W12 40, W13 46, W14 37, W15 31, W16 43, W17 43, W18 41, W19 32, W20 51, W21 46, W22 47, W23 50, W24 40, W25 50, W26 49, W27 32, W28 33, W29 35, W30 29, W31 40, W32 53, W33 38, W34 33, W35 36, W36 30, W37 29, W38 39, W39 31, W40 22, W41 39, W42 28, W43 39, W44 38, W45 28 (to Thursday 5 November). The thin weeks of October and November 2025 are the news feeds' windows (a feed keeps its last items only); the Register is read in full from 1 October 2025.

`policy_reads` (408 rows, one per action read; dates 2025-10-01 to 2026-11-05). Columns: `event_id, event_date, event_type, parties, entity_ids, mw, price, currency, status, source, source_url, action_event_id, agency, action_type, title, significance, what_changes, affected_sectors, affected_isos, affected_states, direction_supply, direction_demand, direction_prices, direction_buildout, timeline, plain_read, fields_kept, fields_dropped, news_story_urls, model_id, read_at`. By week, 1 to 19 reads (2026-W41 the most).

`policy_reads_evidence` (3,559 rows, internal): `read_id, field, span, source_text_file`, one quotation a row.

**What the tables do not hold**, against the chain's list of fields: no instrument beyond the four `action_type`s (no order, guidance, approval, lease sale, bill, tariff filing or docket opening as such: a FERC order printed as a notice is a `notice`); no status vocabulary (proposed, final, effective, stayed, vacated, withdrawn); no effective date, comment deadline or hearing date as a field; no figure and unit as a field (`mw` and `price` are empty on every row); no next step; no evidence sentence for the action's own fields; no record that groups the documents of one action.

### 3. The scorer's prompt and vocabulary

`warehouse/policy/score.py` gives the news scorer (`warehouse/news/score.py`: `SYSTEM` with the rubric of `warehouse/news/rubric.md`, the JSON `SCHEMA`, the model `NEWS_SCORE_MODEL`, `claude-haiku-4-5` since session 206) the action's title and a summary (the abstract, else `first_paragraph`, else the status line, at most 600 characters), with the beat "policy" and `POLICY_NOTE`: "When the summary is empty, say what the title says and no more: do not infer what the document decides, whom it affects or why it matters from a company's name, an agency's name or a docket number, and choose the sector only from words the title itself holds." The schema returns `significance` (0 to 10), `ai_power_relevance`, `sector` (one of 21: oil, gas, lng, power_prices, generation, nuclear, renewables, storage, transmission, grid_conditions, interconnection, datacenter_power, deal, ppa, policy, capital, company, geopolitics, transport, hydrogen, other), `region`, `mw_mentioned`, `price_mentioned`, `parties`, `headline`, `one_line_why`, `is_duplicate_of`; the policy step keeps `significance`, `sector` and `why` only. The rubric's bands: 9 to 10 market-moving (a federal rule or court decision with industry-wide effect), 7 to 8 a state-level rule or hundreds of MW or millions of dollars, 4 to 6 a filing, a permit, a study with numbers, 1 to 3 minor, 0 not energy.

### 4. The pages

| Address | What it shows |
|---|---|
| `/policy` ("Every action, scored", the default view) | the lead (sources, the score and the read as hovers), the paused sources line, "This week in policy" (up to six actions of the last seven days at 5 or more, with the read's plain sentence or the scorer's why), "Every action" (`PolicyTable`: filters by agency, type, sector, state, significance and date, and the four tags; columns Date, Agency, Type, Title, Sector, Significance; a row opens to its read and sources; the count shown; the first 400 listed), the downloads of `policy_actions` and `policy_reads` (CSV with Python and Stata readers) |
| `/policy?view=week` ("What changed this week") | the actions of the last 7 and 30 days by body, topic and grid, with FERC's and the state commissions' proceedings from `site/data/policy/state_rules.json`, the dropped rows counted with why |
| `/data/methods/policy_monitor` | the method note |

Every page is `review` (`site/lib/release.ts`: `"/policy": "review"`). The site reads `policy_actions` from the live set's `events` table, eleven fields of `extra` (`agency, action_type, title, docket, sector_tags, states, significance, sector, why, related_urls, news_story_urls`) with `event_id, event_date, status, source_url`.

### 5. The policy steps' last runs (erw_health)

`queue/summary/*-health.md` lists a step only when it is not ok; the rows below are read from `erw_health` itself.

- `policy_score`: seven rows held, the newest five failed: 26 to 30 October (runs 40335571667, 40517022435, 40701642758, 40887150915, 41067951705), each "0 newly scored, 1959 of N scored" (N 1,960 to 1,991), cost USD 0.0000: the account's spending limit of 28 October to 1 November (session 2864's report) and the days before it; 10 and 12 October skipped at the daily model cap. No row since 30 October: a step that passes writes no row. On 6 November every one of the 2,020 actions carries a score, so the 32 left unscored on 30 October were scored by a later run.
- `policy_reads`: two rows, both skipped at the daily cap (10 and 12 October).
- `policy_sources`: no row (a pull step that passes writes none, and none failed).
- `policy_monitor_refresh` and `policy_monitor_site`: ok on each of 22 to 30 October and on 6 November 00:17 and 00:20 UTC (run 42120465428). No daily run recorded these steps on 31 October to 5 November.

### 6. The Digest's policy row

`warehouse/news/brief.py`, `policy_actions_lines`: the window's actions scored 5 or more, most significant first, three at most, as the Policy group's last lines. It reads `event_date`, `significance`, `title`, `agency`, `action_type` (and its four names: rule, proposed_rule, notice, press_release), `why` and `source_url`. The Roundup and `site/lib/digest.ts` read the line's text (", policy action): "). Every one of these keys keeps its name and meaning in this chain; a new field is added beside them.

The periodicals' faults file (`docs/reviews/periodicals-faults-2026-11-05.md`) has no open row on the policy actions: its row 5 ("the policy row takes a policy or capital story") and row 9 (a why line that restates the headline) are fixed in the Digest's code (f93754995, 41f12b20f), which this chain does not touch.
