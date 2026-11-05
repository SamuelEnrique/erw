# Energy news: the stories and the public index

Energy Research Warehouse (ERW), method note written in session 2564 (chain 126) for two tables first written in sessions 6 and 7 (the news ingest and its scoring, read by the Energy Digest, the Sunday Roundup and the datacenter and deal extractors).

Tables: `news_index`, `news_stories`

## Sources and builders

Three scripts in `warehouse/news/`, run by the daily sequence:

- `ingest.py` reads every feed of `warehouse/news/feeds.yaml` (the outlets' own RSS feeds and Google News searches; 43 feeds in the run of 24 October 2026) and writes `news_stories`, keeping titles, summaries (trimmed to 500 characters) and links, never article bodies. The feeds' responses are saved under `warehouse/raw/news/<run_id>/` (not in git). `--backfill` (session 17) reads past months through Google News searches, one month and one sector's terms at a time, a second apart.
- `score.py` asks a fixed Claude model for a JSON object per unscored story of the last days, under the rubric in `warehouse/news/rubric.md` placed verbatim in the system prompt, and writes the scores into the same rows. The model is `claude-haiku-4-5` since session 206 (the owner's ruling of 12 October 2026); every call goes through the cost ledger.
- `index.py` writes `news_index` from `news_stories`: every scored story, with the fields that are links, metadata or the model's own words.

## What a row is

One news story, in the events shape (`event_type` news). `event_id` is `news:` and 16 hex digits of the SHA-1 of the story's canonical address (scheme and host case, tracking parameters and fragments normalised); `event_date` is the feed's publish time, UTC (a story without one is skipped and counted in the run log).

## Columns

`news_stories`: the events columns (`event_id`, `event_date`, `event_type`, `parties`, `entity_ids`, `mw`, `price`, `currency`, `status`, `source`, `source_url`), then `title`, `summary`, `feed`, `feed_sector`, `feed_region`, `retrieved_at`; the scorer's `significance` and `ai_power_relevance` (0 to 10), `sector`, `region`, `price_mentioned`, `why`, `cluster_id`, `model_id`, `scored_at` and `headline` (the model's one-line headline, since session 7); and `google_news_url`, `url_resolved`.

`news_index`: `event_id`, `event_date`, `event_type`, `source`, `source_url`, `sector`, `region`, `significance`, `ai_power_relevance`, `cluster_id`, `headline`.

- **`source`** is the outlet: the feed's name, or for a Google News item the outlet named in its `<source>` element. **`source_url`** is the link the feed gives. A Google News link is followed once (session 7, ruling 3): where it lands on the outlet, `source_url` becomes the outlet's address and the Google link moves to `google_news_url`; otherwise the Google link stays and `url_resolved` says why ("no: ...").
- **`feed`** names the feed; a backfilled story's feed carries the query that found it ("<feed> [backfill <sector> <YYYY-MM>]"), while `feed_sector` stays the feed's own beat.
- **`cluster_id`** joins stories the model marks as one event (an `is_duplicate_of` chain).

## Deduplication

By canonical address, then by near-identical title (difflib ratio of at least 0.92 after lower-casing and removing an appended " - Outlet"), against the run and the stories already stored. The first copy seen is kept, the outlets' own feeds before Google News. A story already stored is never rewritten by the ingest, so its scores stay.

## As held on 25 October 2026

From the ingest run `20261024T145033Z` and the index run `20261024T145929Z`, counted by code from the tables:

- `news_stories`: 23,108 stories, 2025-01-01 to 2026-12-01, from 80 outlets; 10,906 found by the backfill; 17,440 scored (significance 0: 4,464; 1 to 3: 7,230; 4 to 6: 4,692; 7 to 10: 1,054) and 5,668 not scored; scored by `claude-sonnet-5` (8,120), `claude-sonnet-5-5` (5,678) and `claude-haiku-4-5` (3,642). 20,513 rows link through news.google.com, 20,508 of them marked unresolved. Every `event_id` is of the form above and unique.
- `news_index`: 17,447 rows, every `event_id` one of `news_stories`, 16,815 with a headline, 15,859 clusters. The sectors most given: other 7,523, policy 1,509, oil 1,178, geopolitics 963, company 914, datacenter_power 857.
- **Two things a reader should know.** Two stories of Data Center Knowledge's feed are dated 2026-11-17 and 2026-12-01, after the day they were read: the feed's own publish times, kept as given. And 7 rows of `news_index` carry scores that their rows of `news_stories` no longer hold (`scored_at` empty there; three of them are CTVC's); the index keeps what the run that wrote it read. Neither is changed here.

## License

`news_stories` is internal: its titles and summaries are the outlets' text, kept for scoring and linking, not for republication. `news_index` is public (session 7, ruling 4): only links, metadata and the model's own fields, no outlet text. `news_index` is in the live set (`warehouse/supabase/live_set.yaml`); `news_stories` is not.

## What they do not hold

- Article bodies, or any outlet text in `news_index`.
- A story without a publish time; a second copy of a story already held.
- Scores for stories the scorer has not reached (the 5,668 above, 4,341 of them found by the backfill).
