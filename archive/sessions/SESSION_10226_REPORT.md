# Session 10226 report: the contracts page audited as a hostile expert would

Chain 710, part D (in the form of part B), the old laptop, 26 November 2026. Worktree `erw-c710-a`, branch `wip/audit-contracts-doc`. Model spend USD 0; no request to any service; no table written; no lock taken.

## What was done

- `docs/reviews/contracts-model-audit-2026-11-26.md` and its folder of evidence: `/contracts` read as a power trader or a utility's risk manager would.
- The arithmetic is right: an independent restatement from the raw table gives every figure of the default view to the digit against the page drawn by its own code (40 of 40 figures, 8 of 8 words, 1,135 of 1,135 cells), for a load on 5 October and on 26 November 2026.
- The page holds no futures, forwards, curves, CFTC positions, capacity auction or ancillary prices: it reads FERC's Electric Quarterly Reports contract files only. The brief's questions on those had nothing to bite on and are said so.
- Six findings (one High, one Medium, four Low), each with a test on its own branch `wip/audit-contracts-1` to `-6`; all six fix words only, merge together with no conflict, and move no figure (restated again after the merge).

## Decisions made without you

- The default view was restated for two load days (the notes' 5 October and a load today), since the live set's window moves with each load and the live database was not read.
- Findings 1 (survivors) and the late filers were made one finding: both say the quarters listed are not a series of signings, and both fixes sit in the same two places.
- Tests read the main checkout's tables when this checkout has none (as `replication/contracts/copy_rows.py` does) and skip when the table is absent or is another retrieval. No test runs node; the drawings were made by hand with `runs/c10226/draw_contracts.mjs`.
- The decisions block (`Decisions.tsx`) was left untouched: its words are held word for word against the note's section 9 by a test, and no finding needed it.

## For Samuel's ruling

- Finding 1: read each quarter of execution from the file filed for it (history holds 2025 Q3 to 2026 Q1). Default "left as it is". Effect: 2025 Q3's energy, capacity and tolling rows 273 to 2,129; every product 1,393 to 2,976; 2025 Q4 311 to 2,209; 2026 Q1 396 to 701; the default view (2026 Q2) unchanged.
- Finding 2: draw the filer's description beside a number filed. Default "left as it is". Effect: no figure moves; up to 178 of 1,317 power numbers in the window (156 not 0) carry words of an index, LMP, adder, formula, escalation or percent; 1 in the default view.

## Needs the key

- Nothing. (Data requests, returned to the chain's main session: the live set's load day and first date for `ferc_eqr_contracts`, and whether FERC's 2026 Q3 file is pulled; the stored summary to carry the file's retrieval time.)
