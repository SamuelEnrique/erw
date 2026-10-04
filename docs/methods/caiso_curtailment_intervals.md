# CAISO curtailment by interval and by reason, and its profile

Two tables behind the page `/curtailment/v2` ("Curtailment", version 2, in review):

| Table | Built by | What it is |
|---|---|---|
| `caiso_curtailment_intervals` | `warehouse/connectors/caiso_curtailment_intervals.py` | CAISO's wind and solar curtailment at the finest interval it publishes, by reason, from 2019. An approved pull (Samuel, 4 October 2026): ceiling 500,000 rows, USD 0. It holds 484,819 |
| `caiso_curtailment_profile` | `warehouse/derived/curtailment_profile.py` | the same by hour of the day, by month and by reason, and against battery charging in the same hours |

**What the data does not locate.** CAISO publishes one figure for its whole system: not the plant, not the node or
zone, and for a "local" curtailment not which line was congested. Nothing in either table says whether a battery at a
given place could have taken the power that was turned down.

## Sources and license

Both are the California ISO's, both public.

- **To 2025-12-31:** "Production and curtailments data" (`https://www.caiso.com/library/production-curtailments-data`),
  one workbook a year, sheet Curtailments: Date, Hour (hour ending, 1 to 24), Interval (1 to 12), Wind Curtailment and
  Solar Curtailment in MW, and from 2022 a Reason, Local or System (9,241 rows of 2022 have none; no workbook before
  2022 has the column). Only the five-minute intervals with a curtailment are listed. The two 2025 workbooks overlap
  (the second, a "one time bulk upload", repeats January to May): 25,848 rows are read once.
- **From 2026-01-01:** the Daily Renewable Report (`https://www.caiso.com/library/daily-renewable-reports`), one page
  a day. CAISO's note in the last workbook: "Please refer to the Daily Renewable Report in the future for 5 minute
  curtailment data." The report's five-minute curtailment series is wind and solar together; by fuel it gives the
  hour (`curt_hr_tot_<fuel>_<category>_<local|system>_mwh`). The table takes the hour by fuel. The five-minute series
  of the two together is not taken: it does not tell wind from solar, and it would carry the table past the pull's
  ceiling.

**License,** from CAISO's Privacy and Terms of Use (`https://www.caiso.com/privacy-terms-of-use`, read on
2026-10-04): the materials and information on its website "may be used by you provided that you keep intact all
copyright, trademark and other proprietary notices and that you credit the California ISO when using such materials
and/or information." Nothing in them forbids republishing. The tables are public; the page credits the California
ISO.

## `caiso_curtailment_intervals`

Entity `caiso:ISO`; `ts_utc` the interval's start, UTC. Only intervals with a curtailment above zero are written, as
in CAISO's workbooks.

| freq | Unit | Variables | Rows |
|---|---|---|---|
| `PT5M` | MW, the interval's average | `curtailed_<fuel>_mw` (no reason published), `curtailed_<fuel>_local_mw`, `curtailed_<fuel>_system_mw` | 463,166 |
| `PT1H` | MWh | `curtailed_<fuel>_<econ\|ss\|oi>_<local\|system>_mwh` | 15,989 |
| `P1D` | MWh | `curtailed_<fuel>_day_mwh`: one row for every day covered, zero included | 5,664 |

- **A five-minute MW** is the interval's average: its energy is MW x 5/60 MWh.
- **CAISO's categories from 2026,** in its report's words: "Economic - Local: Market dispatch of generators with
  economic bids to mitigate local congestion. Economic - System: ... to mitigate system wide oversupply. SelfSchCut -
  Local: Market dispatch of self-schedules to mitigate local congestion. SelfSchCut - System: ... system-wide
  oversupply. Operator Instruction - Local: Operator Instructions to mitigate local congestion. Operator Instruction -
  System: ... system-wide oversupply." The table writes them `econ`, `ss`, `oi`.
- **The day rows** say which days are held. A day with no interval row and a day row of zero had no curtailment; a day
  with no day row is not held. Every day from 2019-01-01 to 2026-10-02 is held.
- **The day the clocks go forward.** A daily report has 24 hourly values on that day too (8 March 2026), by the clock,
  with zero in the hour from 02:00 that does not exist. Each value is dated by its clock hour. A value in the hour that
  does not exist could not be placed, and the day would not be written.
- **The clock.** Date is the Pacific day; an interval starts at (Hour - 1) hours and (Interval - 1) x 5 minutes of the
  day's clock. On an autumn day the clock hour from 01:00 happens twice and the workbook does not say which: 29 rows
  are dated the first.
- **Checked against the table the site already had:** every day's total equals `caiso_curtailment_daily`, to the
  thousandth of a MWh, for the 5,662 fuel-days both hold.

## `caiso_curtailment_profile`

Entity `caiso:ISO`; `freq P1M`; `ts_utc` the first day of the Pacific month. A month is written when at least 90
percent of its days are held; its figures are sums over the days held, never scaled up.

| Variable | Unit | Meaning |
|---|---|---|
| `days_held`, `days_in_month` | count | |
| `curtailed_<fuel>_mwh` | MWh | wind, solar |
| `curtailed_<fuel>_local_mwh`, `_system_mwh`, `_unspecified_mwh` | MWh | by CAISO's reason; unspecified where none was published |
| `curtailed_<fuel>_econ_mwh`, `_ss_mwh`, `_oi_mwh` | MWh | from 2026: by CAISO's category |
| `curtailed_<fuel>_mwh_hHH` | MWh | the month's MWh in local hour HH |
| `battery_days_held` | count | the days both this table's input and `caiso_battery_storage` hold |
| `avg_curtailed_mw_hHH`, `avg_battery_charging_mw_hHH` | MW | the average day over those days: wind and solar curtailed, and what the batteries took in |
| `curtailed_mwh_battery_days`, `battery_charging_mwh` | MWh | the two over those days |
| `curtailed_while_charging_share_pct` | percent | the share of the curtailed MWh in hours in which the batteries were charging on balance |

**The batteries.** `caiso_battery_storage` is CAISO's five-minute battery output (Today's Outlook), held from 24
August 2025; positive is discharge. An hour of it is held with all twelve of its values. Charging is the part below
zero, as a positive number. The battery rows are written for a month in which at least 90 percent of the days are held
by both tables: September 2025 to September 2026, thirteen months.

**Both are system totals.** That curtailment and charging fall in the same hours does not say the batteries could
have taken what was turned down: a local curtailment is behind a congested line, and the file does not say which.

**A year on the page** is not a row of the table: the builder writes it into the site's copy as the sum of its months,
when every month of the year to date is held.

## Rebuilding

```bash
python warehouse/lock.py run --task "CAISO curtailment intervals" --minutes 40 -- <python> warehouse/connectors/caiso_curtailment_intervals.py
python warehouse/lock.py run --task "CAISO curtailment profile" --minutes 10 -- <python> warehouse/derived/curtailment_profile.py --snapshot
```

The connector stops before writing if the table would pass 500,000 rows. At about 60 rows a day it reaches the
ceiling in the summer of 2027; the ceiling is the pull's, and raising it is a person's decision.

## Checks

`tests/test_session98.py`: an interval's start from the workbook's Date, Hour and Interval, the autumn hour included; a
workbook's rows read once across two workbooks, with and without a reason; a daily report's rows, and a report of the
wrong day or with a short array not written; the ceiling; the tables as built (the day totals against
`caiso_curtailment_daily`, the profile's month against the intervals, added again by hand; the battery figures against
the battery table); the site's copy equal to the table; and the page's choices, run in Node.
`site/scripts/check-curtailment-v2.mjs`: every number the page shows, against the site's copy, on the built site.
