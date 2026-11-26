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

- **A wrong diagnosis, corrected within the session.** The replication's refit disagreed with the stored forecasts on 22 of 232 sample hours (up to 0.4 percent). I first blamed the builder's solver (running normal equations) and changed it to solve each window's own rows; the rebuilt forecasts were identical, so that was not the cause. The cause: the places that disagreed are exactly those whose demand holds hours at or below zero, which the builder takes as not held when it takes a day's mean, a rule the method note did not state. The note now states it (section 3), the replication follows it, and all 232 refits and all 17,995 score figures agree. The solver change is kept: it changed nothing at the shown precision and is the plainer method. The draft of this report, pushed at 12:20 UTC, gave the wrong cause; it is corrected here (the note's section 10 had not been pushed with it).
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
