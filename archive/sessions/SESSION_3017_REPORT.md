# Session 3017 report: the drafts checked, the first part: every figure recomputed

6 November 2026, about 12:50 to 13:15 UTC, on lab-desktop, second window, chain 164 (the owner's), unattended. Model spend USD 0. Pulls: none.

## Read these first

- **All 156 drafts reproduce from their own scripts.** `warehouse/analysis/findings/deep/check.py` copies each `docs/findings/<family>/<slug>.reproduce.py` alone into an empty folder, so it reads nothing of the repository. It runs the script on the main checkout's tables and compares the printed figures with the expected line at the script's top, within 0.5 percent of the change. The drafts' own numbers are never read.

| Family | Drafts | Reproduce |
|---|---:|---:|
| prices | 33 | 33 |
| demand | 12 | 12 |
| generation_pipeline | 35 | 35 |
| gas | 11 | 11 |
| queues_deals_datacenters | 27 | 27 |
| tariffs_policy | 12 | 12 |
| oil_products_world | 18 | 18 |
| cross_family | 8 | 8 |
| all | 156 | 156 |

- **All 156 cards hold against their own files** (`deep/check_cards.py`, a read over `SUPABASE_DB_URL`):
  - The chart is the hunt's `flag_line`. Its points are the CSV file's full years and values, the marked point is the last full year, and the claim's years are the CSV's first and last.
  - The sentence names both years, the limits sentence is present, and all five tests passed.
  - The eight files are there, and both pictures are PNGs.
  - The state is still `draft`.
- **The count before and after the check: 156 and 156.** No draft was corrected or removed this session; the two corrections found earlier were made in session 3009.

## What it did

- **`deep/check.py`** and **`deep/check_cards.py`**, with `tests/test_session3017.py` (3 tests, passed).

## Decisions made without you

- **The hover is checked by construction.** The cards draw with the site's own `lib/discoverychart.ts`, which gives `flag_line` an axis tooltip with a formatter, as for every weekly hunt draft on main. The page itself was read on a local build in session 3018.

## For Samuel's ruling

- None new.
