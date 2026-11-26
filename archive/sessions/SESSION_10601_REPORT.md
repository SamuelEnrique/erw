# Session 10601 report (chain 730, lab-desktop second window): part F

26 November 2026, from about 12:00 UTC. Model spend: USD 0. No warehouse table written, no data lock taken.

## What a reader will see that was not there before (once row 5 lands and window E's page reads the files)

- Each place's file carries tomorrow's peak hour and peak demand, and the record of past peaks against the operator's (`series.demand.peak`).
- `site/data/predict/ahead.json`: the demand forecast two to seven days ahead, each horizon shown only where it has beaten "the same hour a week ago" over the last two years.
- Forecasts solved more exactly (below).

## Commits

- Branch `wip/c730-predict-v2`: `7ff3d4d1d` (the solver, the peak, the horizons, `replicate.py`, tests), then the rebuilt files (see the progress file for the head requested).
- Main: the landing-row note on row 4 (window F's L1), data request 6, the method note's section 10, progress lines.

## Errors and how they were caught

- **The regression's solver lost precision.** The replication written from the method note refitted sample days with plain least squares and disagreed on 22 of 232 sample hours, by up to 0.4 percent. The builder had solved each window from differences of running normal equations; it now solves each window's own rows. Every score figure (17,995 of them) had reproduced exactly before the fix, because the replication scored the stored forecasts; the refit is what caught it.
- A second empty heredoc to Python (the same mistake as in session 10600) hung on standard input; stopped, nothing changed. No heredoc of any kind is used after it.

## Decisions made without you

- **The flexible method (d) is not built:** tried on TEX, CISO and SE, it lost to the regression by 9 to 16 percent out of sample (the note's bar was a 5 percent gain).
- **Net demand is not forecast:** the wind and solar forecasts held carry no publication time.
- **The further-ahead horizons** are counted from the last whole day read (h = 3 to 7, two to six days after tomorrow), each refit at its own horizon; shown only where the regression beats the week-ago hour.
- **The peak** of a method is the highest of its own hourly forecasts for the day, and its hour; scored on days whose every hour every method holds.

## For Samuel's ruling

- None.

## Needs the key

- Nothing.
