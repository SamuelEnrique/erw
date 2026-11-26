# Session 10601 report (chain 730, lab-desktop second window): part F

26 November 2026, from about 12:00 UTC. Model spend: USD 0. No warehouse table written, no data lock taken.

## What a reader will see that was not there before (once row 5 lands and window E's page reads the files)

- **Tomorrow's peak:** each place's file has tomorrow's peak hour and peak demand, and the record of past peaks against the operator's (`series.demand.peak`). The ERW's peak is closer than the operator's in 5 of 29 places, and it names the peak hour exactly more often in 8.
- **Further ahead:** `site/data/predict/ahead.json` holds the demand forecast two to seven days ahead. All 145 place-horizons beat "the same hour a week ago" over the last two years, so all are shown.
- **A separate line "with the weather known":** the regression given the day's observed temperature. It is not a forecast and is never the headline. It shows that a perfect weather forecast would let the ERW beat the operator in 12 places instead of 8, and that in Texas, New England and BPAT the weather is less than half of the gap.
- **A fourth demand candidate, `regression_recent`:** the regression with the last hour read, the same hour the day before it, and the same hour two weeks before the target. The rule picks it in 28 of 29 places. The ERW's error falls everywhere it is chosen (TEX from 5.22 to 4.91 percent, SE from 6.81 to 6.37), but the operator still wins in the same 21 places. `ahead.json` uses the better of the two regressions at each horizon.
- **The price backtest as a file:** `run.py --out-dir` writes it, for data request 5.
- **The codebook:** 8 more variables carry their publisher's meaning: HURDAT2's record codes, Eurostat's flag `i` in three tables, Eurostat's supply diversity index, USPVDB's site types and z-score, NCEI's magnitude types, and TRI's PBT flag. They show on the method pages after the next codebook landing.

## Commits

- **Branch `wip/c730-predict-v2`, now at `739e54e70`.** Window A's desk landed its head `a5b483098` at 14:16 UTC (`f00acbd70`), and row 5 now asks for the newest head. Commits:
  - `7ff3d4d1d`: the solver, the peak, the horizons, `replicate.py` and tests;
  - `957fb7178`: the files with the peak;
  - `2f3d49091`: the price backtest file;
  - `ahead.json`;
  - `4b1b3ab6e`: the weather-known line;
  - `d7c5f4517`: `regression_recent`;
  - `739e54e70`: further ahead with the better regression.
- **Branch `wip/c730-codebook-labels` at `117ec035b`** (landing row 6): the method pages' codebook file with tonight's labels.
- **Main:**
  - the note on landing row 4 (window F's L1);
  - data request 6;
  - the method note's sections 10 to 13 (the replication and the zero-hour rule, the peak, further ahead, with the weather known);
  - four contract lines;
  - two notes for window E;
  - the codebook commits `43e3d4c1d` and `89b217e9e`;
  - chain 730's note `docs/state/note_2026-11-26_window2_c730.md`;
  - progress lines.

## Tests and checks

- **`tests/test_predict.py`:** 16 passed. They cover nothing read after the information cut at horizons 2, 3 and 7, and for the price; the ledger never rewritten; every place's score and peak; a held series holding no number; further-ahead horizons shown only where they beat the week-ago hour; and the weather line never being the forecast.
- **`replication/predict/replicate.py`:** 21,582 of 21,582 score figures equal, and 464 of 464 refits of the two regressions equal.
- **`tests/test_codebook.py`:** 7 of 7, with the tables.
- **The whole suite on `4b1b3ab6e`,** run under the build lock from 13:43 to 13:59 UTC: 10,327 passed, 555 skipped, 1 failed.
  - The failure is `tests/test_session6111_ask.py`: the ask evaluation's keys against Russian and Chinese tables on this machine.
  - It fails the same way on main (`7624724e7`), so it is not this branch's. Landing row 5 says so.
  - The later heads change only `warehouse/predict/`, its test and its files, and were not run whole again.

## Errors and how they were caught

- **A wrong diagnosis, corrected within the session.**
  - The replication's refit disagreed with the stored forecasts on 22 of 232 sample hours, by up to 0.4 percent.
  - I first blamed the builder's solver (running normal equations) and changed it to solve each window's own rows. The rebuilt forecasts were identical, so that was not the cause.
  - The real cause: the places that disagreed are exactly those whose demand holds hours at or below zero. The builder takes such an hour as not held when it takes a day's mean; the method note did not say so.
  - The note now states the rule (section 3), the replication follows it, and all 232 refits and all 17,995 score figures agree.
  - The solver change is kept: it changed nothing at the shown precision and is the plainer method.
  - The draft of this report, pushed at 12:20 UTC, gave the wrong cause. It is corrected here; the note's section 10 had not been pushed with it.
- **A second empty heredoc to Python** (the same mistake as in session 10600) hung waiting on standard input. I stopped it and nothing changed. No heredoc of any kind is used after it.
- **One long inline Python script.** The edit that taught `replicate.py` the new candidate was written as a long `python -c` command, which the chain's rules ask to keep out (scripts go in `runs/`). It worked, and the replication's result shows the edit is right, but it was against the rule. Every later edit used the Edit tool or a script file.
- **Row 6 was first written below the note at the foot of the landing file**, outside the table. It was moved into the table in the next commit.

## Decisions made without you

- **The flexible method (d) is not built.** Tried on TEX, CISO and SE, it lost to the regression by 9 to 16 percent out of sample; the note's bar was a 5 percent gain.
- **Net demand is not forecast:** the wind and solar forecasts held carry no publication time.
- **The further-ahead horizons** are counted from the last whole day read (h = 3 to 7, two to six days after tomorrow). Each is refit at its own horizon and shown only where the regression beats the week-ago hour.
- **The peak** of a method is the highest of its own hourly forecasts for the day, and the hour of it. It is scored on days whose every hour every method holds.
- **The weather-known line** gives each balancing authority its EIA region's temperature. It is scored only on the hours the temperature table holds (it ends on 7 November 2026), so its hour counts are smaller than the main scores'.
- **The cross-check is left open.** CAISO's market monitor's 2024 annual report prints no day-ahead load forecast error, and a search found no SPP figure.
- **Codebook entries left open after a read:** the value 5 of NCEI's zone type and its data source code (in neither NCEI format document); BART (not expanded on EPA's NEEDS page or in its chapter 4); USBR's region codes (only CGB appears on usbr.gov, as a mail code).

## For Samuel's ruling

- None.

## Needs the key

- Nothing.
