# Session 3827 report, with 3828: the Digest's story figure traced, and the counterparties table on the drafts

Energy Research Warehouse (ERW). Chain 218, data machine (lab-desktop), 13 November 2026 02:31 to 02:55 UTC. Opus 5.5. Model spend USD 0. Requests: Redivis's API, two `--tables` runs of one table.

## 3827, the Digest's story figure

- **The figure was right; the check read the wrong field.**
  - The issue of 12 November keys "USD 2.1 billion" to `digest_story|news_stories|news:808f73a07b2ad109|price`.
  - `<id>` is the story's cluster. `warehouse/news/brief.py` (`build_clusters`) takes a cluster's sum from the first non-blank `price_mentioned` of its stories, strongest first.
  - Here that is `news:f3e71677b34cfdb7` (significance 7, "$2.1 billion"). The cluster's own row, `news:808f73a07b2ad109`, has a blank `price` and "$2B".
- **`site/scripts/check-values.mjs` now reads the writer's rule** (`1b1c129da`): the cluster's stories by significance, then the earliest; the first non-blank `mw`, or the first non-blank `price_mentioned` in the issue's money style (`digestMoney`, as `brief.money_style`, without the "USD " the page reads off).
  - The other story row of the issue (`news:63369e9ec598452f`, 580 MW) passed before and passes the same way.
  - The issue of 12 November is not rewritten.
- **Proved at this chain's gate** on the issue's page; the result is in session 3839's report.

## 3828, the drafts for `deal_counterparties`

- **On both drafts, nothing released:** the warehouse's own public draft (count 510) and the Stanford draft (erw:b9wm). `erw_headers` gained its 7 header lines in each.
- **Its catalogue hold is lifted,** and it stays held from v1. The release list reads "on both drafts since 13 November".
- **Test 410 asked for one more record:** a listed table must be named by the source registry. `erw:energy_deals` now names `deal_counterparties`, and `warehouse/deals/counterparties.py` registers it with `seed_from_deals.py`'s entry word for word (the registry rewrites a row's words from each entry), so the runner keeps it.
- Tests 275, 410, 237, 1008, 378 and 505: 54, OK. Commit `d21a91745`.

## Decisions made without you

- **The check follows the writer, not the other way round:** the writer's rule (a cluster's strongest stated figure) is the Digest's documented rule; the check had assumed one row per key.

## For Samuel's ruling

- None.
