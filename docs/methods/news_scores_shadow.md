# Shadow news scores: the stories scored again by a second model

Energy Research Warehouse (ERW), method note written in session 696 (chain 045) for a table first written on 29 September 2026.

Tables: `news_scores_shadow`

## Sources and builder

The ERW builds this table. Its input is the ERW's own `news_stories`: the stories the daily run had scored with its
Sonnet-class model. The builder is `warehouse/news/shadow.py` (session 30, Part B4), command `score`. It sends the same
stories to a second model, the shadow, named by the environment variable `SHADOW_MODEL` (`claude-haiku-4-5`), with the
same rubric (`warehouse/news/rubric.md`), system prompt, JSON schema and batching as `warehouse/news/score.py`: 40
stories a call (`warehouse/config/shadow.yaml`), day by day, with the two days before as the reference list for
duplicates. Temperature 0 is sent; Haiku takes no effort setting. Every call goes through `warehouse/llm.py` as step
`news_score_shadow`, so its cost is in `api_cost_ledger`. The purpose was to measure whether the cheaper model could
replace the first. The shadow's scores fed a shadow Digest and Roundup sent to one address only, never to subscribers.

Model-written columns (tier `model_extracted` in `coverage.csv`): `parties`, `mw`, `significance`, `ai_power_relevance`,
`sector`, `region`, `price_mentioned`, `headline`, `why` and `is_duplicate_of`; `cluster_id` is built from the model's
`is_duplicate_of` links. `event_date`, `source` and `source_url` are copied from `news_stories`.

## Vintage and revision

Appended, keyed on `event_id`; a story already scored by the same model is not sent again. The daily run
(`warehouse/run_daily.sh`, step `news_score_shadow`) scored the stories of the last 3 days. The shadow stops when
`SHADOW_MODEL` is unset or on its expiry date, 2026-10-06 (`shadow.yaml`). Session 206 removed `SHADOW_MODEL` from the
daily workflow (the owner's ruling of 12 October 2026: news scoring itself runs on Haiku now), so the step skips and the
table no longer grows. The last scoring run is `20261005T145932Z`.

Nine runs wrote the rows: `20260929T100758Z` 435, `20260929T102003Z` 1,940 (with the first, the session 30 backtest of
the last 30 days and the 50 eval-sample stories), `20260930T194926Z` 399, `20260930T215719Z` 365, `20260930T233806Z` 56,
`20261002T000201Z` 400, `20261003T143708Z` 400, `20261004T143649Z` 353, `20261005T145932Z` 400.

The copy on the data machine was restored from the Redivis draft by `scripts/sync.py`. Its header is still that of the
run of 4 October 2026 ("File holds 4348 rows ... to 2026-10-04T14:29:12Z"); its rows include the 400 of 5 October, as
`coverage.csv` counts them.

## Shape and variables

Events, `event_type` `shadow_score`. One row per story and shadow model. Key: `event_id`.

| Column | Meaning and unit |
|---|---|
| `event_id` | `shadow:<story_id>:<model_id>` |
| `event_date` | the story's publish time (UTC) |
| `parties` | the companies, people or places the model names, separated by `; ` |
| `mw` | MW the model read in the story, else empty |
| `source`, `source_url` | the outlet and the story's link |
| `story_id` | `news:<16 hex>`, the story's `event_id` in `news_stories` |
| `model_id` | the shadow model |
| `significance` | the rubric's score, an integer from 0 to 10 |
| `ai_power_relevance` | the rubric's AI and power score, an integer from 0 to 10 |
| `sector` | one of the scorer's sectors (`SECTORS` in `warehouse/news/score.py`, an enum of the schema) |
| `region` | the model's words for the place |
| `price_mentioned` | a price as the story states it, text, else empty |
| `headline`, `why` | the model's headline and one-line reason |
| `is_duplicate_of` | an earlier story the model marks as the same event, kept only when it is a known story and not itself |
| `cluster_id` | the story's cluster, from the duplicate links |
| `scored_at`, `run_id` | when and in which run the shadow scored it |

As of 23 October 2026: 4,748 rows, 4,748 stories (all in `news_stories`), `event_date` 2026-08-31T07:00:00Z to
2026-10-05T14:39:55Z, `scored_at` 2026-09-29T10:07:59Z to 2026-10-05T14:59:33Z. `model_id` is `claude-haiku-4-5` on every
row. 62 outlets (Reuters 1,050 rows, Bloomberg.com 776, Financial Times 709, WSJ 587). `significance` 0 on 2,237 rows,
highest value held 9. `ai_power_relevance` 0 on 4,321 rows; 7 or more (the digest's AI and power tag) on 253
(`7` 24, `8` 147, `9` 81, `10` 1). 21 sectors (`other` 2,834, `policy` 329, `oil` 245, `datacenter_power` 196). 164
distinct `region` values (`global` 2,540, `US` 726, `United States` 171). `mw` filled on 69 rows, `price_mentioned` on
367, `parties` on 2,401, `is_duplicate_of` on 270.

## License

The ERW verdict in `docs/licenses.md`: internal. The row reads: publishers "the outlets of news_stories"; verdict today
"not settled (needs written permission by default)"; not read "the outlets of news_stories"; flag in `coverage.csv`
internal; flag and verdict "not settled"; if the ERW sells anything "may be public"; ERW verdict "internal". The header
says the shadow's scores reach no public table, page or subscriber.

## Cross-check

Session 30 compared the backtest (2,375 stories, 84 calls, none failed; Haiku left out 1 story) with the published
scores, by `warehouse/news/shadow_agreement.py`:
- the day's top-10 clusters matched, mean over 21 days: 0.80; weighted by stories: 0.63;
- top-10 stories by significance, mean a day: 0.85;
- significance: Pearson 0.862, Spearman 0.809; mean absolute difference 0.80 points; exact 45.8 percent, within 1
  81.9 percent;
- AI and power tag (relevance 7 or more): agreement 97.5 percent, Cohen's kappa 0.64; tagged 61 by Sonnet, 113 by Haiku;
- cost: Haiku USD 0.00081 a story (measured); Sonnet USD 0.00263 a story (an estimate).

In the code: a score outside 0 to 10 is left out, and the run log names it.

## What it does not hold

- No published scores: they are in `news_stories`.
- No story titles or summaries.
- No human labels: the 50-story eval file had none when session 30 ran.
- No story scored after 5 October 2026, and no model other than `claude-haiku-4-5`.
