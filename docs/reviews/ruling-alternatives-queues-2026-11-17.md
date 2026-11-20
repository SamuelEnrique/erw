# Ruling alternatives: /queues, the interconnection queue (17 November 2026)

Session 7630 (portable-laptop, code role). The two lines of `docs/reviews/ruling-impact-queues-2026-11-17.md`, both built, each on its own branch from origin/main with a test that pins it, in order of size of change. **No branch asks to land; no default on main changed.** Model spend USD 0.

- **Build:** the worktree `erw-alt` (3,450 and 3,392 MB free before the two builds), served on port 3320 with the repository's `.env` and no model key, read cache-free with the internal cookie at 1280 px.
- **Tests:** the new test of each branch and every test file that names the page: 31 passed, 4 skipped, 199 subtests (both branches).

| # | Line | Branch | Figure before (origin/main) | Figure after (the other choice) | Files touched | Test | Screenshot |
|---|---|---|---|---|---|---|---|
| 1 | Give the headline "Request to operation" a second wait, the last three operation years as the All grids tab counts them | `wip/alt-queues-1` (`5404c40bf`) | `/queues?grid=pjm`: "3.15 years, median" over every year (1,181 of 1,192 dated requests); the other grids the same, one figure | Beside it: **"Of those that reached operation in 2023 to 2025: 5.94 years, median, over 169 requests" (+88.6 percent)**, the figure the All grids tab draws (71.3 months). Every grid: ERCOT 3.70 and 3.82 (+3.3 percent, 227 requests), CAISO 6.02 and 8.33, NYISO 4.61 and 7.27 (5 requests), SPP 4.06 and 7.05, MISO 3.04 and 4.87, the Southeast 3.79 and 4.97, the West 2.05 and 4.09; drawn for a grid's every-technology view where `connect.json` holds a median (ISO-NE's is not held) | `site/app/queues/page.tsx`, `tests/test_session7630_alt_queues_recent_wait.py` | `connect.json`: 2023 to 2025, at 5 requests or more; ERCOT 3.82, CAISO 8.33, NYISO 7.27, PJM 5.94 years; the page's rule | `docs/reviews/ruling-alternatives/queues-1-recent-wait-1280.png` |
| 2 | Reconcile storage in the queue to Berkeley Lab's summary ("approximately 749 GW") instead of the file's parts (552.7 GW) | `wip/alt-queues-2` (`fc50d7bf5`) | `/queues?grid=us`: no storage total drawn; the kinds table gives storage alone (385,330 MW) and solar with storage (503,794 MW, both parts together) | A line under the kinds table, US view only: **"Storage in the queue, every part: about 749 GW, Berkeley Lab's own summary"**, beside the file's parts, 552.7 GW (+196.3 GW, +35.5 percent), with the words that the grids' parts do not add up to it (the summary gives no split by grid or year) | `site/app/queues/page.tsx`, `tests/test_session7630_alt_queues_storage.py` | `queues.json` (built 17 November 2026): the US parts 552.7 GW; +196.3 and +35.5 percent; the page draws the line for the US alone | `docs/reviews/ruling-alternatives/queues-2-storage-reconciled-1280.png` |

## What the builds showed that the impact file did not

- **Line 2: the page drew no 552.7 GW.** The impact file names "storage's active MW (the US figure)" as the cell; origin/main draws storage alone and solar with storage as two rows, and the parts' sum nowhere. So the other choice adds a figure (and the parts' sum beside it) rather than replacing one.

## Decisions made without you

- **Line 1's second wait sits in the headline's note, under the all-years median**, not as a fifth headline number, so the headline row keeps its four figures on a phone.
- **Line 2's 749 GW is Berkeley Lab's own word, "approximately"**, written "about 749 GW"; its document is the 2026 edition's summary, as the impact file quotes it (not read again here).
