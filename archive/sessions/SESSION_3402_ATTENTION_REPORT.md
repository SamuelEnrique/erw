# Session 3402 report: the first run over the corpus and the three tables written (chain 202)

6 November 2026, 19:52 to about 20:25 UTC, on lab-desktop, fourth window, chain 202, unattended, Fable 5.1. Model spend: the session's ledger total is in the table below (the cap, USD 3, stopped the run). Pulls: none; the model calls were the only requests.

## Read these first

- **The builder** is `warehouse/derived/attention_index.py`: from `news_stories` (every story, the weeks' denominators) and the classifier's rows (the jsonl files under `warehouse/raw/attention/`, plus the link table's own rows) it writes `attention_story_links` (events, one row a classified story, no outlet text), `attention_index_weekly` and `friction_index_weekly` (series, `P1W`), and the page's files `site/data/attention.json` and `site/public/attention/stories/<monday>.json`. `tests/test_session3402_attention_index.py` (8 tests) works every number of a ten-story corpus by hand.
- **The write** went through `runs/c202/write_table.sh` (chain 147's, for three tables): the data lock waited for, the builder, the validator on each table, `build_coverage.py --only`, the archive, the metadata patch to the branch. Its lines and the tables' counts are below.
- **The run** classified the newest stories first with Sonnet 5.5 under the session cap. A first run of 1,320 stories went to Haiku 4.5 by my mistake (the module's default model had not been switched; USD 0.38) and was stopped by me, its rows set aside in `runs/c202/haiku_rows/` and used only to measure the two models' agreement (docs/methods/attention.md).
- **The page** `/attention` (`site/app/attention/`) and its Analysis menu entry are written and type-check; its build and checks are sessions 3405 and 3406.
- **The method note** `docs/methods/attention.md` is drafted (its coverage figures are session 3404's to confirm).

## The run

| | |
|---|---|
| Model | claude-sonnet-5-5, prompt version 2 |
| Stories classified this session | 3,800 in 95 calls of 40 (19:58 to 20:14 UTC) |
| Cost a call of 40 | USD 0.0275 to 0.0281 |
| Stories a minute | about 240 |
| Session ledger total | USD 3.01 by the cap: USD 2.63 Sonnet, USD 0.38 the stopped Haiku run |
| Left unclassified | 17,709 stories (significance 0 excluded), every week before 2026-10-19 and the 2,164 oldest of that week |

After the cap the loop went on raising the ledger's refusal for each batch left (443 lines, no call sent, no cost); the classifier now stops at the first refusal.

## The write (20:14 UTC, `runs/c202/write_3402.log`, `done, fail=0`)

| Table | Rows | Validator | Note |
|---|---|---|---|
| `attention_story_links` | 3,800 | pass | 98 report opposition: political opposition 46, protest 18, other 13, lawsuit 10, rate case 6, moratorium 5; 1,773 about the US, 337 with a state (California 79, Texas 74, Michigan 16) |
| `attention_index_weekly` | 1,110 | pass | 135 entities (the corpus entity, 8 sectors by all, US and 31 states) |
| `friction_index_weekly` | 2,142 | pass | 134 entities |

- Coverage: public, `model_extracted`, sector `news;datacenters`, `derived` "no" (the `news_index` route: "Built from", not "Derived from"); the archive run `20261106T201455Z-local` took the three tables (7,052 rows) to the bucket and `warehouse/archive/`; the metadata patch applied to the branch with one row a table in coverage, sources and the manifest (no double).
- Sectors of the 3,800: not energy 1,617; oil and LNG 698; other energy 478; data centers 363; gas 188; transmission 126; nuclear 113; storage 112; solar and wind 105. No row needed a value emptied by code (`fixed` empty throughout).

**Coverage by week** (the `attention:corpus:all` entity):

| Week of | Stories held | Classified | Scored 0, unsent | Judged, percent of held |
|---|---|---|---|---|
| 2026-10-19 | 3,146 | 982 | 1,226 | 70.2 |
| 2026-10-26 | 2,342 | 2,299 | 43 | 100.0 |
| 2026-11-02 | 631 | 518 | 113 | 100.0 |
| 2026-11-16 | 1 | 1 | 0 | 100.0 (a feed-dated story) |

The page's files: `site/data/attention.json` (21 KB) and four week files under `site/public/attention/stories/` (1.3 MB together).

## Decisions made without you

- **The Haiku run stopped and its rows set aside.** The module's default model was Haiku 4.5 from the trial; the run started with it. I stopped a process of my own, kept the 1,320 rows outside every table, and used them for the agreement measure. The USD 0.38 is in the ledger under session 3402.
- **Newest stories first** under the cap, as the prompt says; the weeks before the cap's reach are named in the write's line and left for file 203.
- **A week's denominator** is its judged stories (classified plus the unsent significance-0 stories), not every story held, so a partly classified week's index is a share of what was judged; the corpus entity records both counts.
- **The page's files are written by the same run as the tables** (`--site-dir`), so the page's numbers and the tables' are one write.
- **The three tables enter the live set** (`live_set.yaml`) for the page's downloads and check-values; the load is session 3405's, under the lock.

## For Samuel's ruling

- Nothing new beyond session 3401's coverage-against-precision question.

## Next

Session 3403: the second run under its own cap (the next-oldest stories), the tables rewritten through the locked write, the coverage by week.
