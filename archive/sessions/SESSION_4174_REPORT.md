# Session 4174 report: the held grids' public files, ready for a ruling

Energy Research Warehouse (ERW). Chain 245, session 9 of 16, lab-desktop third window, 13 November 2026, ending 12:46 UTC. Opus 5.5. Model spend USD 0. Branch `wip/4166-licenses`.

- **`scripts/held_public_files.py`** (new) lists the files of the held grids under `site/public/`, each with its size, grid, kind and board row status. It deletes nothing and has no mode that does. Test: `TheListForTheRuling` in `tests/test_session4109_public_site.py` (9 passed).
- **`docs/reviews/held-public-files-2026-11-13.md`:** the 138 files, what keeps them, and what a ruling would change.
- **Found:** 110 of the files belong to board rows of NYISO and ISO-NE that the board builder still fills (battery, day-ahead/real-time, peak and spark groups). The newest point is 5 November, after the hold of 21 October.
  - The page masks them when it draws (`holdRows` in `site/lib/board.ts`), but the files are served by address.
  - `board_page.py` blanks only a held grid's power hubs and reserves.
  - `page_keep.py` keeps a file only the old build has.
- **What a ruling would change** (not done): remove the files; build no file for a held grid's row in any group (`board_page.py`); never keep a held grid's file (`page_keep.py`); or bring those folders under the curtain (`site/proxy.ts`).

## Decisions made without you

- **Nothing deleted, no builder changed.** The deletion is the owner's to order, and the builders run on the data machine (window A).

## For Samuel's ruling

- **The 138 files and the builder's held rows** (the review file). **Default: left as they are** while every page is in review.
