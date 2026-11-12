# Session 1882: the Roundup's W45 faults, rows 59 to 76, fixed on fixtures (12 November 2026)

Energy Research Warehouse (ERW). Session 1882 of an unattended chain, samueloldlaptop, Opus 5.5, in the worktree `erw-1882` on `wip/1882-periodicals` (cut from the chain's unlanded head `badb61de5`). About 60 minutes. No model call, no e-mail, no Digest or Roundup run, no stored issue rewritten, no warehouse table written, no site build, nothing pushed to main or a `task/` branch.

## What it did

- Copied the newer faults file from the main checkout (`docs/reviews/periodicals-faults-2026-11-05.md`, session 1881's rows 59 to 78) into the worktree and worked the open rows in the order the prompt set. Read chain 131's v2 shape (`queue/done/131-night-25-october-code-periodicals-v2.md`), the rulings of 6 November and the existing tests of `roundup.py` before changing code.
- **Fixed, commit `7c75f237`** (`warehouse/news/roundup.py`, `warehouse/news/brief.py`):
  - Row 59: `roundup.cutoff_line` and `intro_span` take the Digest's rule (`brief.masthead_lines`, session 1444). W45 would read "Stories through 5 November, 18:08 ET, 23:08 UTC; the week's tables reach 5 November (each table's reach is under ERW's Numbers This Week)." and "for 2026-11-02 to 2026-11-08 (no story after 2026-11-05 is held)". The tables' reach is the newest hour the numbers read (the real-time tables and US48 demand).
  - Row 60: `weekend_empty_line`: "- No story of 7 or 8 November is held: the newest story the warehouse holds is of 5 November, 23:08 UTC."
  - Row 62: when the move leads, the subject is at most 90 characters and the headline clause has no figure and no "...": "ERW Weekly | Brent down 13.1% on the week; AEP and Google advance a Bloom Energy fuel-cell" (90). With no move, the old rule stands.
  - Row 72: `also_policy_line`: a failed why line no longer leaves a colon and a double space. The line closes "(NRC notice, published 2026-11-05). [Source](...)", and "Inc" gets its stop.
  - Row 73: `note_style` styles the chart note as the Roundup prints it ("47,682 MWh a day, down 6,318 from 54,000"). The stored chart record keeps the engine's note.
  - Row 71, in part: the cells read "120 of 168 hours held, no weekly mean" (Roundup) and "... hours held, no daily mean" (Digest).
- **Fixed, commit `50126625`** (`warehouse/news/roundup.py`):
  - Row 66: a financing reads by its roles: "USD 938 million, Deutsche Bank and Rabobank's financing of Return's Germany battery storage portfolio (2026-11-05)." BESS, PPA and SMR are now written out in words.
  - Row 67: the deals table prints no "other" type. A financing reads Buyer "Return (borrower)", Seller "Deutsche Bank, Rabobank (lenders)" (the extract's roles: `warehouse/deals/extract.py` line 144).
  - Row 69: "502,100 MW in the hour starting 2026-11-02 23:00 UTC, the highest of the 72 hours held (to 2026-11-04 23:00 UTC) [6]."
  - Row 70: the five's own Tables line, which the email prints, now names every mark its rows print: "Tables: [5] `eia_fuel_spot_prices` (EIA); [6] `eia930_all_demand` (EIA-930); the deal of the week, ...". `scripts/check_roundup.py` still finds its keys on that line (its tests pass).
- Faults file states updated in commit `70ae22ca`.

## Left open, and why

- 63, 64, 68: not reached. They need `evidence_gap` to look the named deal or plant up in `energy_deals`, `eia860m_planned_generators` and `energy_projects`, and the stand-in of row 68 builds on row 64's look-up.
- 65: `why_check` asking `new_things` of every why line changes the Digest's lines too. A count over the stored issues should come before the rule changes.
- 71, the real-time half: the line's form is parsed by `scripts/check_roundup.py` (RT) and `site/lib/digest.ts`. Dropping "spp_rtm" and "local" needs the checker and the page changed in the same commit.
- 74: `common.source_line` lists every publisher of the table. Naming the charted series' own publisher needs the derived table's source by entity, which `erw.sources` does not give.
- 75, 76: not reached.
- 66, the currency half: the story's EUR 835 million is not in the `energy_deals` row (`currency` is empty), so it is the extract's to fill (data machine).

## Tests

- `tests/test_session1882.py`: 28 tests, exit 0. Each builds the faulted line from a fixture and asserts the replacement.
- Every test file that imports or calls `roundup`, `brief` or `email_digest` (31 files, `tests/test_periodicals.py` and `tests/test_session*.py`), run together: exit 0, 671 passed, 4 skipped. The checker's tests (`test_periodicals`, `test_session498`, `test_session806`): exit 0.
- Four pinned assertions were changed because the rows change their lines: `test_periodicals.py` (the weekend source check, row 60; the deal of the week, row 66; the stand-in's line count, row 70) and `test_session806.py` (the five's Tables line, row 70).

## Decisions made without you

- When no move leads, the subject keeps its "..." cut at 70 characters (the existing test). The 90-character, no-figure rule applies to the clause after a move, which is the case row 62 quotes.
- The also line keeps the lower-case "[source]" after a why line that passes (an existing test pins it). The upper-case "[Source]" is used only after the closing stop.
- The Federal Register title's hyphen ("Application-Limited") is kept as published. Changing it to a comma would also break words like "Non-Hazardous".

## For Samuel's ruling

- None new.
