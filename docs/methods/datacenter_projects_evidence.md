# Evidence sentences for the datacenter facilities

Energy Research Warehouse (ERW), method note written in session 696 (chain 045) for a table first written on 26 September 2026.

Tables: `datacenter_projects_evidence`

## Sources and builder

The ERW builds this table. Its input is the ERW's own `news_stories` (scored stories with sector `datacenter_power`). The
builder is `warehouse/datacenters/extract.py` (session 16, the datacenter power tracker, platform tool 4), run by the
daily sequence as the model step `datacenters` (`warehouse/run_daily.sh`). It writes two tables in one run: the public
`datacenter_projects` (entities, one row per facility) and this one, the internal table of evidence sentences.

The stories go by cluster, ten clusters a call, to the newest Sonnet-class model the API lists (`pick_model`, by
`created_at`), with a JSON schema. Every call goes through `warehouse/llm.py` as step `datacenters_extract`, so its cost
is in `api_cost_ledger`. For each facility the model returns, among other fields, `evidence` ("one sentence (or the
title) copied verbatim from the story that names the facility") and `story_id` (the story it is from).

Model-written columns (tier `model_extracted` in `coverage.csv`):
- `evidence`: the model's sentence, kept only when it is found, after normalising, in the cluster's titles and
  summaries; otherwise the row is not written and the run log names it.
- `story_id`: the model's choice, kept only when it is one of the cluster's stories; otherwise the cluster's first story.
- `facility_id` (and `entity_ids`): the facility the model's `same_as` points to, when the session 166 rule accepts it
  (the same operator, developer, site, or county or city in the same state); else a new facility.

The table carries no `model_id`. The model of each facility's first extraction is in `datacenter_projects`, column
`model_id`: `claude-sonnet-5-5` on 119 facilities and `claude-sonnet-5` on 31 (as of 23 October 2026).

## Vintage and revision

Appended. Each run adds a row for each facility a new story names, keyed on `event_id`; a row with the same key replaces
the earlier one. Rows from earlier runs are kept. The run of 22 October 2026 (`20261022T150250Z`) wrote 6 new rows and
kept 162. `--reextract` rebuilds both tables from every story already checked: the earlier copy is kept in
`warehouse/datacenters/history/` (one such copy, `datacenter_projects_evidence_before_20260927T043103Z.csv`). The
stories sent are listed in `warehouse/datacenters/checked.csv` and are not sent again.

## Shape and variables

Events, `event_type` `datacenter_evidence`. One row per facility and story. Key: `event_id`.

| Column | Meaning |
|---|---|
| `event_id` | `<facility_id>\|<story_id>` |
| `event_date` | the story's publish time (UTC), from `news_stories` |
| `event_type` | `datacenter_evidence` on every row |
| `parties`, `mw`, `price`, `currency`, `status` | empty on every row (the facility's fields are in `datacenter_projects`) |
| `entity_ids` | the facility, the same as `facility_id` on every row |
| `source` | the outlet, as `news_stories` names it |
| `source_url` | the story's link |
| `facility_id` | `datacenter:<16 hex>`, the `entity_id` of `datacenter_projects` |
| `story_id` | `news:<16 hex>`, the `event_id` of `news_stories` |
| `evidence` | the sentence, outlet text, whitespace collapsed |

As of 23 October 2026: 168 rows, `event_date` 2025-01-07T08:00:00Z to 2026-10-22T11:16:47Z (25 rows dated 2025, 143
dated 2026). 150 facilities: 136 with one row, 10 with two, 4 with three. Every facility of `datacenter_projects` (150)
has a row here. 167 stories, all of them in `news_stories`; one story names two facilities. 13 outlets: Data Center
Dynamics 81 rows, Reuters 41, Bloomberg.com 17, WSJ 10, Hart Energy 4, Heatmap News 3, Financial Times 3, Data Center
Knowledge 2, Data Center Frontier 2, Latitude Media 2, OilPrice.com 1, POWER Magazine 1, Natural Gas Intelligence 1.
The sentences run from 39 to 289 characters (median 71).

## License

The ERW verdict in `docs/licenses.md`: internal. The row reads: publishers "Bloomberg; Data Center Dynamics; Data Center
Frontier; Data Center Knowledge; Financial Times; Hart Energy; and 7 more"; verdict today "needs written permission";
decided by "Bloomberg; Data Center Dynamics; Data Center Frontier; Data Center Knowledge; and 9 more"; flag in
`coverage.csv` internal; flag and verdict "agrees"; if the ERW sells anything "needs a paid license"; ERW verdict
"internal". The header says: "Outlet text (a sentence of the story's title or summary); never shown publicly."

## Cross-check

- In the code: a sentence the model returns is kept only when it appears in the cluster's titles and summaries; a
  `story_id` outside the cluster is replaced by the cluster's first story; a `same_as` that fails the session 166 rule
  is refused and the facility is kept apart.
- Session 16 (`warehouse/datacenters/eval/spot_check_s16.csv`): 10 extractions judged field by field against the titles
  and summaries, 44 of 48 judgments correct. The evidence sentence was not judged on its own.

## What it does not hold

- No facility fields (operator, MW, status, place): they are in `datacenter_projects`.
- No model name and no `retrieved_at` column; the run is named in the header and the run log.
- No story text beyond the one sentence; titles and summaries stay in `news_stories`.
- No sentence the verbatim check refused, and no story outside sector `datacenter_power`.
- Nothing is shown publicly.
