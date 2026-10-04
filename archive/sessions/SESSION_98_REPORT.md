# Session 98 report: curtailment

**Built, on `wip/098-curtailment`, nothing deployed.** The approved pull was made: CAISO's wind and solar curtailment at the finest interval it publishes, by reason, from 2019, in 484,819 rows, under the ceiling of 500,000, at USD 0. On it, a derived table and the review page `/curtailment/v2` in the battery page's layout: by hour of the day, by month, by reason, against battery charging in the same hours, with what the data does not locate said above the tool. The page `/curtailment` is as it was.

## To make it live

```bash
# Nothing below was run. No preview address: GitHub recorded no Vercel deployment for this branch's push.

# 1. THE TWO TABLES into the warehouse's records. They exist only in warehouse/output on the old laptop today.
git fetch origin && git checkout wip/098-curtailment && git merge origin/main
python warehouse/validate/erw_validate.py warehouse/output/caiso_curtailment_intervals.csv warehouse/output/caiso_curtailment_profile.csv   # exit 0
python warehouse/metadata/build_coverage.py                                 # read its exit code
python warehouse/archive/archive.py --tables "caiso_curtailment_(intervals|profile)" write
python warehouse/redivis/upload.py --tables caiso_curtailment_intervals caiso_curtailment_profile     # a draft; releasing is your click
#    and in warehouse/supabase/live_set.yaml, under catalogue_hold, while the page is in review:
#      - caiso_curtailment_intervals
#      - caiso_curtailment_profile
#    then commit coverage.csv, sources.csv, docs/coverage.md, the live set and site/data/curtailment_profile.json.

# 2. THE PAGE, in review at /curtailment/v2. A push to a task branch redeploys the site; no live page changes:
python -m unittest tests.test_session98                                     # read its exit code
cd site && node scripts/snapshot-live.mjs take before-098 && cd ..
git push origin wip/098-curtailment:task/098-curtailment
cd site && node scripts/snapshot-live.mjs take after-098 && node scripts/snapshot-live.mjs compare before-098 after-098

# 3. AS THE CURTAILMENT PAGE, when you have used it: the old page holds SPP and ERCOT as well, so version 2 is
#    California's section of it, not its replacement. Either link the two as they are, or move version 2's content
#    under /curtailment's California heading; then set the page's line in site/lib/release.ts.

# 4. TO KEEP IT CURRENT (about 60 rows a day): after the curtailment connector in warehouse/run_daily.sh,
python warehouse/connectors/caiso_curtailment_intervals.py      # requests the workbooks and every 2026 report again: about 6 minutes
python warehouse/derived/curtailment_profile.py --snapshot
#    The connector stops before writing past 500,000 rows. At today's rate that is the summer of 2027: the ceiling
#    is the pull's, and raising it is yours. A lighter daily run (the last 14 reports only) is a small change.
```

**Read these four first:**

1. **The ceiling shaped one choice.** CAISO's five-minute record by fuel ends on 31 December 2025: its last workbook says "Please refer to the Daily Renewable Report in the future for 5 minute curtailment data." In that report the five-minute series is wind and solar together; by fuel it gives the hour. So from 2026 the table holds the hour by fuel (with CAISO's three categories, which the workbooks never had). I did not also take the 2026 five-minute series of the two together: it does not tell wind from solar, which is what you asked for, and with it the table would have passed 500,000 rows. If you want it, it is a second table and a higher ceiling.
2. **The table agrees with what the warehouse already held, to the thousandth of a MWh.** Every day's total of the new table equals `caiso_curtailment_daily` for the 5,662 fuel-days both hold. The new table adds the hour of the day and the reason; it does not change a daily figure.
3. **CAISO's file gives a reason from 2022, not from 2024.** The older connector's note says 2024. The 2022 workbook has the Reason column (9,241 of its rows blank) and 2023's has it on every row. So "local or system" reaches back two years further than the daily table uses. The daily table was not changed.
4. **Every day from 1 January 2019 to 2 October 2026 is held, and one of them nearly was not.** On 8 March 2026, the day the clocks went forward, CAISO's report still has 24 hourly values, by the clock, with zero in the hour that does not exist. My first reading wanted 23 and left the day out; it was 64,906 MWh, 8.38 percent of March's curtailment, which I found only when I checked a sentence of this report against the daily table. The values are now dated by their clock hour, and the day is in.

Energy Research Warehouse (ERW), session 98, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from about 10:34 to 11:10 UTC, unattended. **Model spend: USD 0.00.** One pull, the one named: 288 requests to `caiso.com` (the library page, 11 workbooks, the report index and its month pages, 275 daily reports, one sample report, and the terms page), all at USD 0. No model call, no force push, no deploy. The data lock was taken for each write (the longest about six minutes) and is free.

## The source and its license

California ISO, two public sources the warehouse already used at the daily level: "Production and curtailments data" (yearly workbooks, five-minute) and the Daily Renewable Report (one page a day). I read CAISO's Privacy and Terms of Use again today. The sentence that governs: the materials and information on its website "may be used by you provided that you keep intact all copyright, trademark and other proprietary notices and that you credit the California ISO when using such materials and/or information." Nothing in the terms forbids republishing, and nothing forbids automated access. Both tables are public; the tables' headers, the method note and the page credit the California ISO, and a test holds the credit on the page.

## The pull: `caiso_curtailment_intervals`

484,819 rows; passes the validator (exit 0, no warning). Connector: `warehouse/connectors/caiso_curtailment_intervals.py`. It asks the pause list before any request and stops before writing if the table would pass the ceiling; a test holds both.

| Rows | What | From |
|---|---|---|
| 463,166 | five-minute MW by fuel: with no reason (2019 to 2021 and part of 2022), local, or system | the workbooks, 2019-01-01 to 2025-12-31 |
| 15,989 | hourly MWh by fuel, by CAISO's category (economic bids, self-schedule cuts, operator instructions) and reason | 275 daily reports, 2026-01-01 to 2026-10-02 |
| 5,664 | one row a day and fuel, zero included, so that a day with no interval is known to be a day with none and not a day that is not held | both |

Only intervals with a curtailment are written, as in CAISO's own workbooks. The two 2025 workbooks overlap (the second is "a one time bulk upload" that repeats January to May): 25,848 rows are read once. On an autumn day the clock hour from 01:00 happens twice and the workbook does not say which: 29 rows are dated the first.

The workbooks are saved under `runs/session98/raw/` (277 MB, not in git) and the reports under `warehouse/raw/caiso_curtailment_intervals/20261004T103956Z/`. The table was rewritten four times from those saved files, with no further request, to fix the form of a timestamp, the file's header, the rounding of very small values and the day the clocks went forward.

## The derived table: `caiso_curtailment_profile`

6,124 rows, 93 months (January 2019 to September 2026); passes the validator (exit 0). By month: MWh by fuel; by CAISO's reason; from 2026 by its category; by local hour of the day. And for the thirteen months in which CAISO's own battery output is held (September 2025 to September 2026): the average day of curtailment and of battery charging, the two totals, and the share of the curtailed MWh that fell in hours in which the batteries were charging on balance.

What it says:

| Year | Solar curtailed, MWh | Wind, MWh | Local congestion, MWh | System-wide oversupply, MWh | No reason published, MWh | The hour with the most |
|---|---|---|---|---|---|---|
| 2019 | 921,684 | 43,557 | not published | not published | 965,241 | 12:00 |
| 2020 | 1,497,220 | 90,276 | not published | not published | 1,587,496 | 10:00 |
| 2021 | 1,426,326 | 78,477 | not published | not published | 1,504,803 | 12:00 |
| 2022 | 2,320,258 | 128,990 | 1,303,037 | 363,353 | 782,858 | 13:00 |
| 2023 | 2,508,923 | 150,602 | 2,070,695 | 588,831 | 0 | 13:00 |
| 2024 | 3,192,600 | 230,777 | 3,152,255 | 271,122 | 0 | 14:00 |
| 2025 | 3,482,323 | 283,305 | 3,143,397 | 622,231 | 0 | 14:00 |
| 2026, to September | 4,790,395 | 325,009 | 4,121,464 | 993,941 | 0 | 15:00 |

Nine months of 2026 hold more curtailment than all of 2025, and four fifths of it is for local congestion. The hour with the most has moved from midday to mid afternoon.

Against the batteries: in May 2026, 1,448,985 MWh was curtailed and the batteries took in 1,638,769 MWh; 98.65 percent of the curtailed MWh fell in hours in which the batteries were already charging. Over the thirteen months that share runs from 85.78 percent (August 2026) to 98.80 (October 2025). The page says, beside the number, what it does not mean: both are system totals, and that they fall in the same hours does not say the batteries could have taken what was turned down.

## The page, `/curtailment/v2`

Above the tool, in a bordered block: "The data does not say where." CAISO publishes one figure for its whole system: not the plant, not the node or zone, and for a local curtailment not which line was congested. Then: the panel (a year or one of its months), the summary sentence, three headline numbers; by hour of the day (solar and wind stacked); by month since 2019; by reason, by month, with a table by fuel and reason and, from 2026, CAISO's three categories in its own words; and against battery charging, the average day of a month as the curtailment's area under the charging line, with three numbers. For a year the battery comparison shows the newest month of it that holds the batteries, named, with links to the others; for a period before September 2025 it says "not held" and lists the months that are. Two folds: what the data does not locate or say (seven points), and how it is computed.

**Decision: a page beside the old one, as with the energy mix.** The old `/curtailment` holds SPP and ERCOT as well as California, by day and month; version 2 is California in depth. Replacing the file would have lost the other grids.

## Tests and checks

| Check | Result |
|---|---|
| `tests/test_session98.py` | 14 tests pass. The connector, with no request: an interval's start in summer, in winter and in the autumn hour that happens twice; a workbook made for the test read once across two workbooks, with and without a reason, zeros and years before 2019 left out; a daily report's rows; the report of the day the clocks go forward placed by the clock, and not written if it had a value in the hour that does not exist; a report of another day, a short array and a missing array, none written; the ceiling before the write and the pause before any request. The profile on rows made for the test: a month by hour, reason, category and battery; five-minute MW as energy; a month with too few days not written; a year as the sum of its months. The tables as built: under the ceiling; every day equal to the daily table; a day's five-minute MW adding up to its day row; April 2024 added again from the intervals by hand; the reasons adding up to each fuel's total. The site's copy equal to the table. In Node: the choices and what a period holds. `/curtailment` and the old connector unchanged against main |
| `site/scripts/check-curtailment-v2.mjs`, the built site | 60 checks pass: on eight periods every number the page marks equals the copy (17 to 29 a view), and no figure the copy lacks is on the page; 24 hours of the day and 93 months drawn twice; "no reason published" said for 2019; CAISO's categories only from 2026; the batteries compared for a month that holds them, the month named under a year, "not held" before September 2025; "the data does not say where" above the tool, and the credit; an address it does not understand opens the newest year; a visitor gets the in-review page with no number on it; `/curtailment` is as it was |
| Site: types, build, route check | exit 0 each; no statement cancelled. Route check: 111 of 111 pages, and 16 live with 95 in review as a visitor |
| `check-values.mjs` | exit 0: 7,530 of 7,530 values match |
| The validator on both tables | exit 0 |
| Sessions 94 to 98's tests, session 78's and the MISO pause's, together | 100 tests pass |
| A screenshot of May 2026 | looked at: the sentence, the hours, the months by fuel and by reason, the two tables, the batteries' day |

## Errors and decisions

- **Error, mine, caught by the validator:** the time each workbook was retrieved was written in a form the standard does not accept. Fixed and the table rewritten from the saved files.
- **Error, mine, caught by a test:** 855 hourly values smaller than a twentieth of a kWh were rounded to zero and written as rows of zero. Values now keep six decimals; the row count did not change.
- **Error, mine:** a rewrite that read the reports from an empty folder left the file's header describing the workbooks only. Rewritten from the right folder; the header now describes the file.
- **Error, mine, found while checking this report:** the day the clocks went forward was left out (the fourth point at the top).
- **Decision: a row for every day covered.** Without it a day with no curtailment and a day that is not held look the same.
- **Decision: the comparison with the batteries is by month, from September 2025,** because that is when CAISO's own battery output begins in the warehouse. EIA's battery figures for California would reach further back, but EIA's California series is the one that broke in December 2025; I did not mix the two.

## For Samuel

1. **The 2026 five-minute series of wind and solar together** (the first point above): a second table if you want it.
2. **The reason from 2022** (the third point): the daily table could carry local and system for 2022 and 2023 too. One line in the older connector; not changed tonight.
3. **The ceiling and the daily run** (step 4 above).
4. **Not in any cloud:** the two tables are only in `warehouse/output` on this machine until step 1 is run; the workbooks and the reports are on this machine's disk only.
