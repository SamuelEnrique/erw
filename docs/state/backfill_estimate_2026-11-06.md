# The deals and datacenter backfill, 27 October to 5 November 2026: the estimate (no run)

Energy Research Warehouse (ERW), session 3500, the desktop's fifth window (lab-desktop), 6 November 2026, Opus 5.5.

**Nothing was extracted.** The owner approved the backfill at USD 15 on 5 November, on condition that it runs only with the new extractor on main. `wip/2295-deals` (row 8 of `docs/state/landing_request_portable.md`) was not an ancestor of `origin/main` at any of ten checks from 20:50:53 to 21:36:03 UTC (`git fetch origin`, then `git merge-base --is-ancestor`, every five minutes for 45 minutes; main moved from `6094b647a` to `ae3a718a0` in that time). So this is the dry run alone, as the session's rule says.

## How it was read

- `scripts/deals_backfill.py --from 2026-10-27 --to 2026-11-05 --dry-run`, read at 21:36 UTC, in the worktree `erw-3500` of `wip/2295-deals` with `origin/main` (`ae3a718a0`) merged (head `5934be42c`, a clean merge; branch `wip/3500-backfill-dryrun`, not pushed).
- `--out-dir` pointed at the data machine's `warehouse/output` (its `news_stories.csv` retrieved 2026-11-05 23:26:45 UTC by `warehouse/news/ingest.py`); `checked.csv` of each extractor and `run_status.csv` from the worktree.
- The script calls no model and writes nothing. It prices each step by the median of its last ten successful runs in `run_status.csv`: scoring USD 0.000949 a story, the deal extractor USD 0.04351 a call (12 stories a call), the datacenter extractor USD 0.02370 a call (10 a call).
- The share of scored stories that reach each extractor is the share on the 14 days before 27 October: 0.106 the deal extractor, 0.057 the datacenter one; 1.07 stories a cluster. Every story of the window is unscored or not yet checked, so the extractors' story counts below are estimates from those shares.

## By day

The day's figures come from the script's own `plan()` applied to one day at a time. A part-batch rounds up to a whole call each day, so the days add up to more than the window run as one (120 calls, USD 3.19, against 110 calls, USD 2.93).

| Day | Stories in news_stories | Unscored | Score: calls, USD | Deals: stories (est.), calls, USD | Datacenters: stories (est.), calls, USD | Calls | USD |
|---|---|---|---|---|---|---|---|
| 2026-10-27 | 502 | 502 | 21, 0.48 | 53.1, 5, 0.22 | 28.9, 3, 0.07 | 29 | 0.77 |
| 2026-10-28 | 505 | 505 | 21, 0.48 | 53.4, 5, 0.22 | 29.0, 3, 0.07 | 29 | 0.77 |
| 2026-10-29 | 523 | 523 | 21, 0.50 | 55.3, 5, 0.22 | 30.1, 3, 0.07 | 29 | 0.79 |
| 2026-10-30 | 277 | 277 | 12, 0.26 | 29.3, 3, 0.13 | 15.9, 2, 0.05 | 17 | 0.44 |
| 2026-10-31 | 0 | 0 | 0, 0.00 | 0, 0, 0.00 | 0, 0, 0.00 | 0 | 0.00 |
| 2026-11-01 | 0 | 0 | 0, 0.00 | 0, 0, 0.00 | 0, 0, 0.00 | 0 | 0.00 |
| 2026-11-02 | 0 | 0 | 0, 0.00 | 0, 0, 0.00 | 0, 0, 0.00 | 0 | 0.00 |
| 2026-11-03 | 0 | 0 | 0, 0.00 | 0, 0, 0.00 | 0, 0, 0.00 | 0 | 0.00 |
| 2026-11-04 | 102 | 23 | 1, 0.02 | 2.4, 1, 0.04 | 1.3, 1, 0.02 | 3 | 0.08 |
| 2026-11-05 | 529 | 208 | 9, 0.20 | 22.0, 2, 0.09 | 12.0, 2, 0.05 | 13 | 0.34 |
| **Days added** | **2,438** | **2,038** | **85, 1.94** | **215.5, 21, 0.92** | **117.2, 14, 0.33** | **120** | **3.19** |

## The window as one run (the script's own output)

| Step | Stories | Calls | USD | From runs |
|---|---|---|---|---|
| score | 2038.0 | 82 | 1.93 | 10 |
| deals | 215.5 | 17 | 0.74 | 10 |
| datacenters | 117.2 | 11 | 0.26 | 10 |
| **Total** | | **110** | **2.93** | |

## What it says

- Either way the estimate is about a fifth of the approved USD 15.
- 31 October to 3 November have no story at all in `news_stories.csv`: the feeds were not read on those days, so the backfill cannot fill them. They need the feeds read again, which this script does not do.
- 4 November has 102 stories, 79 of them already scored; 5 November has 529, 321 scored. Neither extractor has checked any story of the window.
- `--run` runs the window as three steps (score, then deals, then datacenters), each over every unchecked story at once. It does not run one day at a time. A run of one day a time needs a decision (see the session's report).
