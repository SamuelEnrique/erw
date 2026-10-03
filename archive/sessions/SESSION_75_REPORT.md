# Session 75 report: curtailment and the shoulder hours

Energy Research Warehouse (ERW), session 75, last of the overnight chain, on the portable laptop, 2026-10-03 from about 10:42 to 11:50 UTC, unattended. **Model spend: USD 0.00** (the cap was USD 0). No pull, no model call, no force push. Branch `wip/075-shoulder` on GitHub; it holds sessions 72 to 74 as well, so it is the whole night in one branch.

## To finish

```bash
# 1. The whole chain merges in one push, after the reviewer has seen tonight's site. Merge main first (the daily run's
#    commits), then push the last branch, which holds sessions 72, 73, 74 and 75 (and 69 and 71's report).
#    Before it: the battery game (session 72's "To finish", step 3) can go before or after; they do not touch the same files.
git checkout wip/075-shoulder
git fetch origin
git merge origin/main
git push origin wip/075-shoulder:task/075-shoulder

# 2. The two new tables the review pages read, into Supabase's live set (not done tonight: each load also writes the
#    table's row into the catalogue the live home page counts). After step 1 has merged:
python warehouse/lock.py acquire --task "storage_buildout_monthly and shoulder_hours_monthly into the live set" --minutes 20; echo "exit=$?"
python warehouse/supabase/load.py --only '^storage_buildout_monthly$' --only '^shoulder_hours_monthly$'; echo "exit=$?"
python warehouse/lock.py release

# 3. Then /shoulder against Supabase (as tonight against the stub, below)
cd site && npm run build && npx next start -p 3049 &
node scripts/check-values.mjs http://localhost:3049     # /shoulder is in its pages
```

Also in "To finish" of the earlier reports: session 72's game steps and its build-out load (the load above covers it), session 73's `/network` label, and session 74's CAISO rule change if you want it.

## In plain words

**The answer to the credit investor's question, as arithmetic on the average day of each month.** The page does not give an opinion.

- **Texas (ERCOT).**
  - **Length:** the evening shoulder has grown from about 4 hours (4.08 in 2021) to almost 6 (5.83 in 2025; 5.78 in 2026 to September). It starts near 18:00 every year. Since 2025 net load no longer falls back to its daily mean before midnight, so the shoulder as defined runs to midnight.
  - **Energy:** its MWh above the daily mean rose from 18,262 a day in 2021 to 44,163 in 2025 and 53,454 in 2026.
  - **The fleet:** 820.9 MW at the end of 2021, 18,204.5 MW in August 2026, holding 1.65 hours on average. It covers 1.58 hours of the shoulder at full power. To deliver all of the shoulder's above-mean energy at that power it would need **3.17 hours**: about twice its present duration, not eight hours.
- **California (CAISO), January 2019 to November 2025.**
  - **Length:** the shoulder shortened from 7.42 hours in 2021 to 5.45 in 2025, because it starts later as solar grows (16:35 on average in 2021, 18:33 in 2025). It runs to midnight in every month: in California, net load stays above its daily mean all evening.
  - **The fleet:** 2,493 MW in 2021 and 15,221 MW in November 2025, with a steady 3.4 to 3.6 hours. In 2025 the shoulder's above-mean energy would take **2.85 hours** at the fleet's power. By this arithmetic, **California's fleet already holds more than the average evening's shoulder needs above the mean**.
  - **Midday:** surplus (net load below its mean around midday) is about 62,555 MWh on the average 2025 day, and CAISO's own curtailment 11,232 MWh a day in 2025 (2,712 in 2019).
- **What the data supports about the 8-hour question:**
  - On the average day, neither grid needs 8-hour batteries to cover the evening shoulder above the daily mean. California's 4-hour-class fleet already covers it in energy terms; Texas's would need about 3 hours at today's power, twice what it has.
  - Both grids' shoulders are now cut at midnight by the definition, so the night's demand above the mean is not counted. Covering that would take more energy, and this page does not measure it.
- **What it does not support:**
  - Anything about the worst day, a cloudy week or a calm evening, which is where longer storage earns its case.
  - Anything about transmission, local constraints or capacity accreditation.
  - Anything about what gas, imports and demand response already do in those hours.
- **California's data:** EIA-930 through November 2025 only (session 73: EIA's California series changed on 16 December 2025), never mixed with CAISO's own series. Battery output in California is CAISO's own and held from August 2025 (shown where a month holds it for every hour); the page says which source each piece is.

## Part A: the table, `shoulder_hours_monthly`

`warehouse/derived/shoulder_hours.py`; method `docs/methods/shoulder_hours.md`.

- **Size:** 20,464 rows: 93 ERCOT months and 82 CAISO months, plus yearly rows (P1Y), so the page does no arithmetic.
- **Checks:** validator pass (0 errors, 0 warnings); in coverage (derived, public, power, CAISO;ERCOT, P1M;P1Y); archived; in the Redivis draft (Redivis's count equals the file's; `erw_headers` 1,782 lines); `--check-license` ok. Not in Supabase ("To finish", step 2).
- **Inputs:**
  - EIA-930 hourly demand, solar (SUN plus SNB), wind (WND plus WNB) and ERCOT's battery output, read from the per-BA workbooks already saved (no request);
  - `caiso_battery_storage`, `caiso_curtailment_daily` and `storage_buildout_monthly`.
- **Months left out:** one, CAISO September 2019 (26 of 30 days complete; the rule is 90 percent). Nothing was filled.
- **Definitions,** as on the page and in the method:
  - net load is demand less solar and wind;
  - the midday surplus is the run of hours around net load's low in which it is below its daily mean;
  - the evening shoulder runs from the first hour after solar's peak in which solar is below half that peak, to the first hour, after net load has risen above its daily mean, in which it is back at or below it (cut at midnight, and flagged, if it never is);
  - hours covered = the smaller of the shoulder's length and the fleet's MWh over its MW;
  - hours needed = the shoulder's MWh above the mean over the fleet's MW.

**By year** (means over the months held; the fleet at the year's last month that has one):

| Grid | Year | Months | Shoulder, hours | Starts (hour) | Runs to midnight, share of months | Above mean, MWh | Midday surplus, MWh | Fleet MW | Fleet hours | Covered, hours | Needed, hours | Curtailed, MWh a day |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ERCOT | 2019 | 12 | 3.92 | 18.08 | 0.00 | 14,852 | 55,915 | 107.2 | 0.94 | 0.78 | 148.53 | not held |
| ERCOT | 2021 | 12 | 4.08 | 18.08 | 0.00 | 18,262 | 49,251 | 820.9 | 1.29 | 1.23 | 49.93 | not held |
| ERCOT | 2023 | 12 | 4.75 | 18.00 | 0.00 | 26,718 | 49,175 | 4,173.5 | 1.43 | 1.32 | 9.49 | not held |
| ERCOT | 2024 | 12 | 5.17 | 18.08 | 0.25 | 34,608 | 46,826 | 8,293.8 | 1.43 | 1.45 | 6.15 | not held |
| ERCOT | 2025 | 12 | 5.83 | 18.08 | 0.92 | 44,163 | 50,900 | 13,909.3 | 1.55 | 1.50 | 4.21 | not held |
| ERCOT | 2026 (to September) | 9 | 5.78 | 18.22 | 1.00 | 53,454 | 61,873 | 18,204.5 (August) | 1.65 | 1.58 | 3.17 | not held |
| CAISO | 2019 | 11 | 7.45 | 16.55 | 1.00 | 35,896 | 39,211 | 185.7 | 2.90 | 2.75 | 203.75 | 2,712 |
| CAISO | 2021 | 12 | 7.42 | 16.58 | 1.00 | 41,298 | 48,321 | 2,492.9 | 3.55 | 3.56 | 32.03 | 4,118 |
| CAISO | 2023 | 12 | 6.67 | 17.33 | 1.00 | 41,380 | 56,771 | 8,107.4 | 3.42 | 3.51 | 6.88 | 7,303 |
| CAISO | 2024 | 12 | 5.75 | 18.25 | 1.00 | 37,218 | 56,632 | 11,746.3 | 3.48 | 3.45 | 3.78 | 9,366 |
| CAISO | 2025 (to November) | 11 | 5.45 | 18.55 | 1.00 | 37,723 | 62,555 | 15,221.3 | 3.42 | 3.44 | 2.85 | 11,232 |

(The page's table has every year from 2019. "Covered" is the mean of the monthly figures, so it can sit a little above the year-end fleet hours, as in CAISO 2021.)

**Flagged as implausible, or as the definition's limit, not the data's:**

1. **The shoulder runs to midnight in every California month and in most Texas months since 2025.** Net load stays above its daily mean all evening, so the end rule never fires before midnight. The night's above-mean energy is then not counted, and "hours needed" is a floor. A shoulder measured against another level, for example halfway between the daily mean and the evening peak, would be shorter and end inside the evening. That is a definition for you to rule on.
2. **"Hours needed" is enormous in early years** (CAISO 203.75 in 2019, ERCOT 148.53): those fleets were a few hundred MW. That is the arithmetic, not an error.
3. **ERCOT's midday surplus is large** (50,000 to 62,000 MWh on the average day) because net load's daily mean is pulled up by the evening and night. The surplus is measured against that same mean. Read it as a shape measure, not as energy that was wasted; ERCOT's curtailment is not held.

## Part B: the page, `/shoulder`, "The shoulder hours" (review)

The battery page's layout and session 67's shared components:

- the fog beige panel (grid; every month held, by year);
- one summary sentence, for example: "In July 2026, ERCOT's evening shoulder lasted 5 hours, from 19:00 to 24:00 (midnight); its batteries could run 1.65 hours at full power, covering 1.65 of them.";
- three headline numbers (the shoulder, the hours the fleet covers, the midday surplus with CAISO's curtailment where held);
- the average day by hour, with demand, net load, solar and battery output, the shoulder shaded and net load's daily mean dashed;
- by month since 2019, the shoulder's length and the hours the fleet covers;
- the table by year;
- folded: the definitions exactly as computed, and what this cannot see (the worst day, the transmission grid and local constraints, capacity accreditation, the rest of the supply stack, the choice of the mean);
- the grey source line, and links to `/cost-of-power/battery`, `/storage/buildout` and `/curtailment`.

The page states that "shoulder" is its own term. Every number is a row of the table with its check key, the hours of the day included. It is `review` in the release gate, in the menu (Prices, before "What a battery earns": the Grid menu is full), in `docs/tools.md`, and in check-routes' and check-values' pages.

## Tests and checks

| Check | Result |
|---|---|
| `tests/test_session75.py` | 7 tests: a hand-worked day (start 16:00, cut at midnight, the shoulder's MWh, the midday run of 9 hours), a shoulder ending when net load falls back, no rise means no shoulder, the fleet bound; on the built table, net load equals demand less solar and wind in every month and hour, the hours covered never exceed the fleet's MWh over its MW, and California stops before the break. OK |
| `python -m unittest discover -s tests` | 365 tests, OK (2 skipped), exit 0 |
| `npx tsc --noEmit` | exit 0 |
| `npm run build` | exit 0 |
| `check-routes`, both passes | exit 0: 80 of 80 with the cookie; 14 live and 66 in review as a visitor, 0 failed |
| `check-values` | exit 0: 6,579 of 6,618 match, and the 39 latest prices are reported as superseded by timing, 30 minutes behind (session 72's fix working as meant). `/shoulder` holds no number against Supabase until step 2 |
| `check-shoulder.mjs` against the built table (a stub serving `warehouse/output/shoulder_hours_monthly.csv`) | **1,044 of 1,044 checks**, 498 numbers equal the table's rows, 6 page variants |
| `test-battery-stack.mjs` (the battery page, the home page, the gate) | all assertions pass |
| Validator, coverage, archive, `--check-license` | exit 0 each |

Package tests were not rerun tonight after session 72's run: no package code changed since.

## Errors and decisions

- **Decision: the shoulder's end needs net load to have risen above its mean first.** The first version ended the shoulder at the first hour at or below the mean, which in California's winter was the very first hour (0-hour shoulders). The prompt says net load "falls back" to its mean, which needs it to have risen; the test covers both cases.
- **Decision: California from EIA-930 only, through November 2025.** CAISO's own supply data (session 73) starts in June 2025, too late for the history, and mixing it in would join two series silently.
- **Decision: the year-end fleet is the last month that has one.** EIA-860M ends in August 2026, and the first version showed 2026's fleet as "not held".
- **Decision: the page sits under Prices in the menu.** The Grid menu already has its eight items.
- **Decision: not loaded into Supabase** (the catalogue row the live home page counts); checked against a local stub of the built table instead.
- **Error, mine:** the first build used the unit `h`, which the validator's vocabulary does not hold (`hour`). Fixed before anything was uploaded.
- **Error, mine:** in the test, my own hand count of the midday run was one hour short (hour 8 is also below the mean). The code was right; the test now says why.
- **The data lock** was held about 10:48 to 11:02, 11:09 to 11:12 and 11:24 to 11:26 UTC, and released each time; **it is free**, well before 13:30 UTC.

## For Samuel

1. **"To finish"** above: one push merges the whole night; then the two review tables into the live set.
2. **The shoulder's definition:** against the daily mean it runs to midnight in California and now in Texas. Say if you want a second measure that ends inside the evening.
3. **The answer for the investor, as the data stands:** on the average day, California's fleet (about 3.4 hours) already holds more than its evening shoulder needs above the mean (2.85 hours at its power); Texas's (1.65 hours) would need about 3.2. Neither case points to 8-hour storage on the average day. The case for longer storage, if there is one, is in the worst days, which this page does not measure.
