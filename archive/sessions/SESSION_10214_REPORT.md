# Session 10214 report: the consumption page (/demand) audited as a hostile expert would

Chain 710, part D, 26 November 2026, the old laptop, worktree `erw-c710-a`, branch `wip/audit-demand-doc`. Model spend USD 0. No table written, no lock, no live service, no web read.

## What was done

- `docs/reviews/demand-model-audit-2026-11-26.md` and its evidence folder: the ground, the default view re-done, one rule changed at a time, every claim against the code, what a forecaster would add, seven findings.
- The arithmetic is right: 87 of the default view's 91 figures equal from EIA-930's hours by an independent restatement; the other four explained to the digit; every whole-year value of the page's file equal (24,204 values and peak hours). The consumption view restates equal.
- Eight branches: words for landing `wip/audit-demand-1` (EIA's estimates inside Adjusted demand, MISO's 2025 peak), `-3` (the weather view is not "the same growth"), `-4` (the cell that grew most), `-5` (a sector is a billing class; estimates; losses), `-7` (the newest month moves); figures, not for landing, `-2` (MISO's peak on its own reports), `-6` (blank hours after the record), `-8` (a 2018 base).

## Decisions made without you

- The restatement uses EIA's workbooks of 3 October 2026 held on this machine; the page was built from those of 5 November. October 2026 came from EIA's hourly route as the main copy holds it, and where that lacks days the year so far was formed from the page file's own months.
- The consumption view was drawn from a fixture of the main copy's rows (the live set was not asked).
- The consumption section's title was left as it is (a test of session 239 holds it); the words went into its note.
- Finding 7 (one base year) is put as a ruling, not a words fault: the page's sentence about 2019 is true.

## For Samuel's ruling

- MISO's 2025 peak: EIA's estimate (120,343 MW, +3.21) or MISO's own highest report (118,106 MW, +1.29)? Default: left as it is.
- Blank hours counted to the workbook's last row (ERCOT 48) or to the newest hour used (24)? Default: left as it is.
- Growth on 2019 alone, or a second base beside it (on 2018 CAISO's 2025 is -0.74 against +4.45, MISO's -0.63 against +2.20)? Default: left as it is.

## Needs the key

- Nothing.

## Problems

- None of the hard rules broken to my knowledge. The first commit of the evidence folder was checked for em dashes just after it was made, not before (none found).
