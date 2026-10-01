# California reliability v1: method

Energy Research Warehouse (ERW), session 58. The "Reliability" section of `/grid/caiso` answers two questions:
- When has California's grid operator, CAISO, told the public the grid was short?
- How tight were its evenings, day by day?

The event page `/events/caiso-heat-2022` adds the September 2022 heat wave on the event template.

## 1. Every notice since 1998: `caiso_grid_emergencies`

**The source.** CAISO's *Grid Emergencies History Report (1998 to present)*, one public PDF:
- https://www.caiso.com/documents/grid-emergencies-history-report-1998-to-present.pdf
- 191 pages on 2026-10-01, with a revision date of 07/06/2026.

The connector is `warehouse/connectors/caiso_emergencies.py`. It reads every table of the report as CAISO drew it (with pdfplumber), in four layouts:

| Layout | Years | One row is |
|---|---|---|
| records | 2016 to now | one notice: date, region, time frame, event, reason (and the notice number and issue time where the page gives them) |
| matrix | 2005 to 2015 | one day, a column per notice type, the hours in the cell |
| stages | 1998 to 2004 | one emergency day, the Stage 1 to 3 columns (and 2004's transmission column) |
| day lists | 1998 to 2002 | the days of No Touch, Alert, Warning and Power Watch notices; each table's type is the label printed above it |

**The table.**
- One row per notice type, region and local (Pacific) day covered. A notice spanning several days is one row per day, because CAISO's own counts are "the total number of days that the event lasted".
- `event_type` is CAISO's type: `flex_alert`, `rmo`, `eea_watch`, `eea1` to `eea3`, `alert`, `warning`, `stage1` to `stage3`, `transmission_emergency`, `vlrp`, `load_interruption`.
- Two older names are filed under the newer ones CAISO's summary counts them as: Power Watch (to 2006) is a Flex Alert, and No Touch (to 2001) is RMO. The printed name is kept in `x_label`.
- Data standard decision 35. **1,900 rows**, 1998-05-30 to 2025-04-30 (the latest notice), against a ceiling of 20,000.

**The check against CAISO's own counts.** The report's pages 1 and 3 give the days per year and type. 2022 is split across the two: January to April on page 3, May onward on page 1.
- **214 of the 232 year-type counts match** the table's distinct days.
- The 18 that differ are listed in the table's header and the run log; nothing is adjusted. Most are a day or two of Restricted Maintenance Operations, or of transmission emergencies, where CAISO counts declarations (one per region or per notice) and the table counts days. In 2007, for example, the report's own "Total Declarations" line gives 18 RMO declarations over 13 days.
- 2003 and 2004 also differ in RMO, Alert and Warning. Those years' notices sit in tables without a type header, read from the page layout.
- And 2022 EEA2 (5 against 4) and transmission emergencies (10 against 11).

**License: public.** CAISO's Privacy and Terms of Use (https://www.caiso.com/privacy-terms-of-use) says its materials "may be used by you provided that you keep intact all copyright, trademark and other proprietary notices and that you credit the California ISO". Every page that shows the table credits "California ISO, Grid Emergencies History Report".

## 2. How tight was it: `caiso_reliability_daily` (derived)

`warehouse/derived/caiso_reliability.py` writes one row per variable and local day, 2018-07-01 to the latest complete day held: **2,980 days**.

| Variable | Entity | What it is |
|---|---|---|
| `peak_demand_mw`, `peak_hour` | `eia930:CISO` | the day's highest hour of demand served and its local start |
| `afternoon_mean_mw` | `eia930:CISO` | the mean of the hours starting 12:00, 13:00 and 14:00 (12:00 to 15:00) |
| `evening_peak_mw`, `evening_peak_hour` | `eia930:CISO` | the highest of the hours starting 17:00 to 20:00 (17:00 to 21:00) |
| `evening_ramp_mw` | `eia930:CISO` | the evening peak less the afternoon mean: the rise into the evening |
| `battery_mw_evening_peak` | `caiso:ISO` | CAISO's batteries' mean output over the evening peak hour (all twelve 5-minute intervals), 2025-08-24 on |
| `battery_share_pct` | `caiso:ISO` | that output over the evening peak's demand |
| `notices_<type>` | `caiso:ISO` | the day's notices of each type, from `caiso_grid_emergencies` |

**Sources.**
- **Demand** is EIA-930's for CAISO's balancing authority: EIA's own CISO workbook, sheet Published Hourly Data, the emissions connector's extract. It is the same hourly demand as `eia930_all_demand`, and each value is the hour's mean MW.
- **Batteries** are CAISO's Today's Outlook "Total batteries" (`caiso_battery_storage`), positive when discharging.
- **Completeness:** a day is written only when every hour is present (24, or 23 and 25 on the clock changes).

**What is not held yet.**
- **The day's available supply.** CAISO's Today's Outlook "available resources" is not in the warehouse, so peak demand is not set against supply. The prompt asked for it "where held"; it is held nowhere yet.
- **Batteries before 2025-08-24.**

**The first readings** (2026-10-01):
- The highest peak held is **51,104 MW on 2022-09-06**, the day of the EEA 3. The second is 49,959 MW on 2026-09-09.
- The steepest evening ramp is 12,519 MW, on 2023-08-27.
- Since 2025-08-24, batteries have supplied a median **22.9 percent** of the evening peak's demand, and up to 41.3 percent.

## 3. The September 2022 heat wave: `caiso_heat_2022`

**The window:** 2022-08-31 to 2022-09-09, CAISO (CISO), on the template of `caiso_heat_2020` (`warehouse/derived/event_window.py`). The baseline is the same weekdays 364 and 728 days earlier: 2021-09-01 to 09-10 and 2020-09-02 to 09-11.

**Weather.** NOAA ISD hourly at Sacramento (SAC) and Los Angeles (LAX), pulled for the window and both baselines: **1,752 rows returned** against a ceiling of 10,000, merged into `noaa_isd_hourly`.

**Estimates** (`warehouse/derived/event_study.py`), CAISO demand, the pooled effect per day:

| Specification | Effect | 95 percent interval |
|---|---|---|
| day of week and year means (`dow_year_mean_v1`) | **+168,641 MWh** | 123,611 to 213,670 |
| plus degree days at 65 F and their squares (`dow_year_temp_v1`) | **+26,826 MWh** | 3,168 to 50,484 |
| a linear year trend in place of the year effects (robustness) | +187,218 MWh | 82,363 to 292,073 |

Controlling for temperature removes about five sixths of the effect: the extra demand was mostly the heat itself.

**CAISO's notices of those days:** Flex Alerts on ten days, and EEA Watch, EEA 1, EEA 2 and the EEA 3 of 2022-09-06 (`caiso_grid_emergencies`).

## Check keys

- **Timeline cells:** `awe|days|<type>|<year>`. check-values counts the distinct days in Supabase's events table.
- **Daily figures:** series keys of `caiso_reliability_daily`.
- **The event page:** the keys of `event_window_daily` and `event_study_estimates`, as the other events.
