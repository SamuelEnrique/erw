# Demand growth since 2019

One derived table, `eia930_demand_growth`, behind the page `/demand` ("Demand growth", in review), built by
`warehouse/derived/demand_growth.py`. No request is made: the builder reads workbooks the warehouse already holds.

**Weather is not removed.** A year's demand is what was metered that year, hot summer and cold snap included. Growth
between two years is the difference of what was metered, not of what a normal year would have been. A single heat wave
can set a peak; a mild year shows less growth than customers added.

## Input

EIA Form EIA-930 (Hourly Electric Grid Monitor), hourly demand, from the per-area workbooks the emissions connector
saves (`warehouse/raw/eia930_emissions/<run>/*_<BA>.xlsx`, sheet "Published Hourly Data"): EIA's "Adjusted demand" for
a balancing authority, and "Demand" for the Lower 48 region, whose workbook has no adjusted column. An hour is dated
by its start. Public domain.

**Areas:** the seven grid operators' balancing authorities (ERCO, CISO, PJM, MISO, SWPP, NYIS, ISNE) and the Lower 48
(US48). The larger balancing authorities outside the seven (TVA, Southern, Bonneville, Duke, Florida Power and Light
and others) are not here: the warehouse does not hold their hourly demand since 2019. It is the same public record and
can be added by a pull.

**California's late hours.** EIA dates California's hours of November 2023 to 2 December 2025 one hour late; they are
set back (`caiso_join.true_hours`) before anything is computed.

## Which hours are used

An hour is used when its demand is held, above zero, and within 25 percent of the median of the four hours around it
(the two before and the two after that are held). An hour that is not used is used for nothing; nothing is filled.

The last test is there because EIA's file holds faulty hours and a faulty high hour would be a year's peak. As built:

| Area | Blank | At or below zero | Apart from their neighbours | Examples |
|---|---|---|---|---|
| PJM | 27 | 0 | 7 | 224,345 MW at 18:00 on 13 July 2020 between hours near 140,000; 155,276 MW on the afternoon of 12 December 2019, which would have been 2019's peak |
| CAISO | 48 | 0 | 38 | hours of 12,000 to 14,000 MW between hours of 23,000, February to May 2019; the good hours between two faulty ones are left out with them |
| NYISO | 24 | 12 | 0 | hours of zero |
| SPP | 24 | 0 | 2 | 1,505 MW at 04:00 on 21 June 2025 |
| Lower 48 | 24 | 0 | 1 | 525,129 MW at 23:00 on 9 April 2020 |
| ERCOT, MISO, ISO-NE | 48, 24, 24 | 0 | 0 | |

A real hour does not stand a quarter away from its neighbours: the steepest ramps of these grids move about a tenth
in an hour.

**The Lower 48 has no peak.** Its demand is EIA's sum over every balancing authority, faulty hours included: PJM's
224,345 MW is inside the Lower 48's 776,575 MW of the same hour, which stands only 12 percent above the hours around
it and passes the test. The average of 8,760 hours does not move for such an hour; the peak would be that hour. So the
table writes the Lower 48's averages and no peak.

## The rows

Entity `eia930:<BA>`; `freq P1Y`; `ts_utc` the first day of the local year. The column `x_at` holds, for a peak, the
hour of the peak (its start, UTC).

| Variable | Unit | Meaning |
|---|---|---|
| `avg_demand_mw`, `hours_used`, `hours_in_year` | MW, count | the mean of the used hours of a whole year; written when at least 95 percent of the year's hours are used |
| `peak_demand_mw` | MW | the highest used hour of the year (`x_at`: when) |
| `avg_demand_growth_since_2019_pct`, `peak_demand_growth_since_2019_pct` | percent | against 2019 |
| `avg_demand_growth_yoy_pct` | percent | against the year before |
| `ytd_avg_demand_mw`, `ytd_peak_demand_mw`, `ytd_hours_used`, `ytd_hours_in_window` | MW, count | the same over 1 January to the end of the newest year's last whole month, written for every year, so that the partial year is compared with the same months |
| `ytd_avg_demand_growth_since_2019_pct`, `ytd_peak_demand_growth_since_2019_pct` | percent | against those months of 2019 |
| `avg_demand_mw_mMM` | MW | the mean of a calendar month (at least 95 percent of its hours used) |
| `avg_demand_mw_hHH` | MW | the mean of a local hour of the day over the year |
| `avg_demand_mw_mMM_hHH` | MW | one local hour of the day in one month (at least 90 percent of its hours used) |
| `growth_mw_...`, `growth_pct_...` (`_mMM`, `_hHH`, `_mMM_hHH`) | MW, percent | on the row of the last whole year: the change from 2019 |

The newest year is partial: it has the year-to-date rows and its months, and no annual average or peak.

**An hour's demand is the average over the hour.** An operator's own record peak is measured over minutes and reads
a little higher: ERCOT's 2023 record is 85,508 MW; the hour here is 85,432.

**Texas, December 2025.** EIA's file is blank for ERCOT for parts of 5 to 14 December 2025 (24 hours of the year are
not used). 2025 holds 8,736 of 8,760 hours and is written.

## California across the break of December 2025

EIA's generation series for California changed on 16 December 2025 ([`eia930_caiso_break.md`](eia930_caiso_break.md)).
This table uses demand, a different series, and session 73 found that demand did not step. The builder checks it again
each run: the mean demand of the 28 days before the date of the join and of the 28 days from it, in 2025 and on the
same dates of each earlier year, and the second over the first.

| Year | 28 days before, MW | 28 days from the date, MW | Ratio |
|---|---|---|---|
| 2025 | 24,766.8 | 24,196.6 | 0.9770 |
| 2024 | 24,628.5 | 23,887.1 | 0.9699 |
| 2023 | 23,793.4 | 23,850.4 | 1.0024 |
| 2022 | 23,937.7 | 24,129.2 | 1.0080 |
| 2021 | 23,724.0 | 24,309.0 | 1.0247 |
| 2020 | 23,317.8 | 23,067.3 | 0.9893 |
| 2019 | 23,737.2 | 23,528.7 | 0.9912 |

2025's ratio lies inside the range of the six earlier years (0.9699 to 1.0247). Month on the year before, California's
demand was 1.5 percent up in December 2025 and 2.2 percent up in January 2026: no step. The check's rows are in the
site's copy and on the page for California.

## What the table does not hold

A weather adjustment; the larger balancing authorities outside the seven; who is using the power; demand served behind
the meter (rooftop solar lowers the demand a grid sees at midday); a forecast.

## On the page

Since session 152 demand growth is one page at one address, `/demand`, in review, with two views kept in the address:

- **As metered** (`/demand`, with `?area=` and `?rank=`): this table. It is what `/demand` showed before, chart for
  chart and number for number.
- **With the weather taken out** (`/demand?view=weather`, with `?figure=` and `?year=`): the table
  `eia930_demand_weather`, whose method is [demand growth with the weather taken out](demand_weather.md). It was built
  as a page of its own at `/demand/weather`, which redirects to the view.

No method or limitation is written out on the page face. What stood there in prose is now this note, and on the page
a few words that show the same sentence when the mouse rests on them:

| On the face before | Now |
|---|---|
| The boxed paragraph "Weather is not removed" | The words "Weather is not removed." with the paragraph as their hover, and a link to the second view |
| The fold "How it is computed" | "Which hours are used", under the chart of the years, with the rule as its hover; the rule in full is "Which hours are used" above. The counts of hours left out for the grid chosen (standing apart from their neighbours, at or below zero, blank) are shown beside it |
| The fold "What is not here" | "What the table does not hold" above, and the list below |
| The notes under the heat map, the ranking and California's check | "How to read the cells", "What is ranked" and "What this check is", each with the note as its hover |
| The reason the Lower 48 has no peak | "No peak is given for the Lower 48", with the reason as its hover |

What the page's fold "What is not here" listed, in full:

- A weather adjustment. Nothing is normalized to a typical year (the second view is that adjustment, with its own
  method and its own limits).
- The larger balancing authorities outside the seven grid operators (the Tennessee Valley Authority, Southern Company,
  Bonneville, Duke, Florida Power and Light and others): the warehouse does not hold their hourly demand since 2019.
  It is the same public EIA record and can be added by a pull.
- Who is using the power: data centers, industry, electrification and population are not told apart in a grid's demand.
- Demand served behind the meter. Rooftop solar lowers the demand a grid sees at midday, so a falling cell there can
  be more solar and not less use.
- The instant peak. An hour's figure is the average over the hour; an operator's own record peak is a few minutes and
  reads a little higher.
- A forecast.

Every chart answers the mouse: a bar, a cell or a mark shows its own figure with its unit beside the pointer.

## Rebuilding

```bash
python warehouse/lock.py run --task "demand growth" --minutes 15 -- <python> warehouse/derived/demand_growth.py --snapshot
python warehouse/derived/demand_growth.py --out-dir DIR      # a trial: nothing in warehouse/output
```

The table is rebuilt whole each run: the year-to-date window moves with the last whole month.

## Checks

`tests/test_session97.py`: the screen on hours made for the test (a spike, a zero, a real ramp kept); a year with too
few hours not written; the year to date over the same months; growth against 2019; the month-and-hour cells and their
change; the Lower 48 without a peak; the table as built against the workbook for one area, computed again by hand;
the site's copy equal to the table; the break check; and the page's choices and ranking, run in Node.
`site/scripts/check-demand.mjs`: every number the page shows, against the site's copy, on the built site.
