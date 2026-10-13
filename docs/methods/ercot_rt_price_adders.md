# ERCOT's real-time reserve price adders, by hour

Energy Research Warehouse (ERW), session 244 (13 October 2026). The table `ercot_rtm_price_adders`, written by
`warehouse/connectors/ercot_rt_adders.py`.

## What it is

From 1 June 2014 to 4 December 2025 ERCOT added a price to real-time energy whenever its operating reserves ran
short: the **operating reserve demand curve (ORDC)**. The fewer megawatts of reserve were left, the larger the
adder. It is ERCOT's scarcity signal: most hours it is
zero or a fraction of a cent, and in a few hours a year it is hundreds or thousands of dollars per megawatt-hour.
ERCOT publishes it for every run of its real-time dispatch (SCED, about every five minutes).

| Variable | ERCOT's name | What it is | Held |
|---|---|---|---|
| `rtorpa_mean`, `rtorpa_max` | RTORPA | Real-Time On-Line Reserve Price Adder: the ORDC adder paid on energy and on-line reserves | 1 June 2014 to 4 December 2025 |
| `rtoffpa_mean`, `rtoffpa_max` | RTOFFPA | Real-Time Off-Line Reserve Price Adder: the adder for reserves that are off-line | the same |
| `rtordpa_mean`, `rtordpa_max` | RTORDPA | Real-Time On-Line Reliability Deployment Price Adder: what ERCOT adds when its own out-of-market actions (reliability unit commitment, load resources, emergency response) held the price down | 25 June 2015 to 4 December 2025 |
| `rtrdpa_mean`, `rtrdpa_max` | RTRDPA | Real-Time Reliability Deployment Price Adder for energy, the same adder under the market design that began on 5 December 2025 | from 5 December 2025 |

- **The ORDC adders end on 4 December 2025.** On 5 December 2025 ERCOT began clearing energy and ancillary services
  together in real time. Scarcity is priced through the ancillary services' own demand curves from that day, and
  ERCOT's file no longer has an RTORPA or an RTOFFPA column. The table does not splice the two designs: `rtordpa` and
  `rtrdpa` are two variables, each under ERCOT's own name.
- Unit: USD per MWh. One row per variable and hour; `ts_utc` is the start of the hour, UTC. `entity` is
  `ercot:system`: the adders are system-wide, the same at every settlement point.

## Source

ERCOT, NP6-792-ER, "Historical Real-Time ORDC and Reliability Deployment Price Adders and Reserves" (report type
13231 on ERCOT's public reports site): one zip a year, each one Excel workbook with a sheet a month and a row per SCED
interval. ERCOT has posted it in three forms (2014 and half of 2015; 2015 to 4 December 2025; from 5 December 2025),
each read by its own header row. The current year's workbook is posted again every week.

- ERCOT posted two documents for 2015: a half-year one in the first form and the whole year in the second. The whole
  year is read. Session 244 compared the two for January to May: 43,532 intervals in each, the same stamps, and no
  difference in RTORPA or RTOFFPA.
- License: public. ERCOT's terms of use, item 5: "raw data provided in public portions of this website may be used,
  reproduced, and redistributed in compilations, charts, and analyses".

## From SCED intervals to hours

1. Each interval's stamp is Central time with ERCOT's repeated-hour flag, read to the second and turned into UTC.
2. An interval's value holds from its stamp to the next interval's stamp.
3. The hour's **mean** weights each value by the seconds it held within the hour. The hour's **max** is the largest
   value that held in it.
4. **Never filled.** A value holds for at most 15 minutes. An hour with a longer silence in it has seconds that no
   value covers, and an hour is written only when all 3,600 of its seconds are covered. An empty cell is not a value.
5. The first hour of each adder's record and its last (still open) are left out by the same rule.

Of the 1,313,747 intervals read on 13 October 2026, the median gap between stamps was 5.00 minutes, the 99th
percentile 5.20, and 37 gaps were longer than 15 minutes. That left out 42 of 100,920 hours of the ORDC adders, 37
hours of RTORDPA and 3 of RTRDPA; each is named in the run log.

**A check by hand.** The hour from 12:00 to 13:00 Central on 15 February 2021 (Winter Storm Uri): 14 intervals, the
time-weighted mean of RTORPA by hand 169.0334 USD/MWh, the table's `rtorpa_mean` 169.0334.

## Hours a year with an adder above zero

Central time. "Above zero" counts an hour when any SCED interval in it carried an adder above zero; the columns to
its right count hours whose mean reached that many dollars per megawatt-hour. 2014 begins on 1 June; 2025 ends on
4 December for the first three adders.

| Year | Hours held | RTORPA above zero | at least USD 1 | at least USD 10 | at least USD 100 | at least USD 1,000 | Year's mean, USD/MWh | Largest interval, USD/MWh |
|---|---|---|---|---|---|---|---|---|
| 2014 | 5,134 | 1,548 | 119 | 23 | 0 | 0 | 0.20 | 304.34 |
| 2015 | 8,757 | 2,463 | 325 | 84 | 16 | 0 | 0.91 | 932.24 |
| 2016 | 8,778 | 1,862 | 144 | 36 | 2 | 0 | 0.20 | 409.32 |
| 2017 | 8,758 | 1,824 | 167 | 27 | 3 | 0 | 0.17 | 700.12 |
| 2018 | 8,755 | 1,899 | 253 | 108 | 32 | 0 | 1.28 | 1,416.74 |
| 2019 | 8,755 | 2,384 | 494 | 246 | 92 | 12 | 6.22 | 4,850.23 |
| 2020 | 8,783 | 1,783 | 352 | 143 | 43 | 1 | 1.85 | 1,557.93 |
| 2021 | 8,752 | 1,564 | 240 | 134 | 70 | 21 | 7.05 | 7,200.71 |
| 2022 | 8,758 | 2,732 | 713 | 315 | 103 | 6 | 5.18 | 2,756.03 |
| 2023 | 8,759 | 1,735 | 291 | 105 | 18 | 0 | 0.92 | 1,648.67 |
| 2024 | 8,781 | 577 | 78 | 27 | 4 | 0 | 0.20 | 847.97 |
| 2025 | 8,108 | 267 | 15 | 4 | 1 | 0 | 0.07 | 4,969.39 |

| Year | RTOFFPA above zero | RTORDPA above zero | RTORDPA at least USD 100 | RTORDPA year's mean | RTRDPA above zero |
|---|---|---|---|---|---|
| 2014 | 1,007 | not published | | | |
| 2015 | 1,811 | 152 (from 25 June) | 0 | 0.01 | |
| 2016 | 1,075 | 651 | 1 | 0.09 | |
| 2017 | 933 | 322 | 3 | 0.13 | |
| 2018 | 1,058 | 374 | 0 | 0.08 | |
| 2019 | 1,553 | 161 | 9 | 2.16 | |
| 2020 | 1,178 | 201 | 0 | 0.01 | |
| 2021 | 849 | 1,112 | 108 | 64.55 | |
| 2022 | 1,212 | 2,019 | 17 | 1.73 | |
| 2023 | 916 | 1,060 | 2 | 0.74 | |
| 2024 | 417 | 1,081 | 0 | 0.23 | |
| 2025 | 224 | 1,812 | 0 | 0.40 | 23 (5 to 31 December, 647 hours held) |
| 2026 | ended | ended | | | 1,485 (to 10 October, 6,787 hours held) |

The counts are of the table as built on 13 October 2026 (`runs/session244/hours_by_year.csv` on the data machine).
`python runs/session244/checks.py warehouse/output/ercot_rtm_price_adders.csv` writes them again.

## What it cannot say

- **Nothing about reserves themselves.** ERCOT's file also carries the megawatts of reserve behind each adder (RTOLCAP,
  RTOFFCAP, PRC and others). They are in the raw workbooks and not in the table.
- **An hourly mean hides the interval.** Settlement is by 15-minute interval; an hour's mean of 100 can be one
  interval at 1,200. `_max` says how high it went, not for how long.
- **The curve changed.** ERCOT changed the ORDC's parameters more than once over these years. A year's hours are
  under that year's curve; the table carries no parameter, and this document does not list the changes (not checked
  against ERCOT's own record in session 244).
- **After 4 December 2025 there is no ORDC adder to compare.** The real-time ancillary service prices that replaced it
  are another report and are not in this table.

## Refresh

`warehouse/run_data_machine.sh` (the data machine's daily run): the list once a day, and a year's workbook only when
the list names one the table holds no row of. Ceiling: 1,000,000 rows.
