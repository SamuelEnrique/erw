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
- Data standard decision 35. **1,900 rows**, 1998-05-30 to 2025-04-30 (the latest notice), against a ceiling of 20,000. That was the report as session 58 read it. On 13 October 2026 (session 254; the report's revision of 9 October 2026): **1,906 rows**, to 2026-10-08. The six new rows are restricted maintenance notices of 9 and 10 September and 5 to 8 October 2026; CAISO printed no notice between 30 April 2025 and 9 September 2026.

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
- **The Grid tool's alert state and alert days** (session 1155, 23 October 2026): `awe|last|<group>|<day>`, the newest Pacific day on or before `<day>` with a notice of the group, written as the date (YYYY-MM-DD); and `awe|ndays|<group>|<from>|<to>`, the distinct Pacific days from `<from>` to `<to>`, both included, with one. A group is `any` (every type: `awe|last|any|<today>` is the table's newest notice day), `signal` (an Energy Emergency Alert or an alert: `eea_watch`, `eea1` to `eea3`, `flex_alert`, and `alert`, `warning`, `stage1` to `stage3` before May 2022, the set the scarcity table's `own_signal` counts), `eea`, `flex_alert`, `rmo` or `transmission_emergency`. check-values reads every row of the table once and recomputes each key by the page's own rule (`site/lib/caisoAlerts.ts`, `aweValue`); `site/scripts/test-caiso-alerts.mjs` holds the rule on a fixture of the real rows from 2022.
- **Daily figures:** series keys of `caiso_reliability_daily`.
- **The event page:** the keys of `event_window_daily` and `event_study_estimates`, as the other events.

## On the Grid tool: the alert state (session 1155, 23 October 2026)

The Mix tab of `/grid?grid=caiso` opens on the panel `grid_caisoalert_caiso` (`site/components/grid/CaisoAlertState.tsx`, `site/lib/caisoAlerts.ts`), read from `caiso_grid_emergencies` (the same read as the Reliability section).

- **Today** is the Pacific day the page was drawn. The table covers a day when it holds a notice of that day or a later one. For a day it covers, the panel says whether an Energy Emergency Alert or a Flex Alert is in force (the `signal` group above); for a later day it says the day is not held yet and names the table's newest notice day (`awe|last|any|<today>`), so "no alert today" is never said past what the report printed. On 23 October 2026 the newest notice is 2026-10-08.
- **The last alert:** the newest day with one (`awe|last|signal|<today>`), its types and regions (2024-07-24, an EEA Watch for the CAISO Grid); the last Flex Alert when it is another day (`awe|last|flex_alert|<today>`: 2022-09-09); the days with one this year (`awe|ndays|signal|<year>-01-01|<today>`).
- **Not alerts, named apart:** restricted maintenance operations (`awe|last|rmo|<today>`, and its days this year, `awe|ndays|rmo|...`) and transmission emergencies (`awe|last|transmission_emergency|<today>`), as `scarcity_hours_by_grid.md` keeps them out of the own signal.
- **The links:** to the Flex Alert scorecard (`/grid/caiso/alerts`), which links back to this panel and to the scarcity strip; to the alert days on the strip; to the Reliability section.
- **The alert days on the scarcity strip** (CAISO): a triangle under each day of the strip with a `signal` notice that Pacific day, each cell's hover naming the day's notices; the counts `awe|ndays|signal|<first day>|<last day>` and `awe|ndays|rmo|...` under it. A notice's day is CAISO's Pacific day, set on the strip's column of the same date (the strip's days are standard-time days: in summer the two share 23 of their 24 hours). The window of 1 to 30 September 2026 holds no alert day, so nothing is marked; restricted maintenance on 9 and 10 September is named, not marked.
- **The monthly mix** (`mixp=month`, CAISO): a month with an alert day is marked on the chart, its days in the mark's name; the alert days of the months drawn are one count (`awe|ndays|signal|<first month>|<last day of the newest month>`). The 24 months drawn on 23 October 2026 (September 2024 to September 2026) hold none, so nothing is marked. The hourly mix is withheld for CAISO (the session 118 ruling) and is not drawn, so it has nothing to mark.

## The alert state's decisions, and what came after it (chain 077, 23 October 2026)

What sessions 1158 to 1160 changed in the panel `grid_caisoalert_caiso` above, and the decisions behind session 1155's rules:

- **One read of the notices a page (session 1160).** `gridNotices()` in `site/lib/reliability.ts`, called with no bounds by the alert state, the scarcity strip, the Reliability section and the monthly mix, is read and parsed once per render (React's `cache`); Next's fetch cache already sent one request. The bounded form (the alerts page, the heat event page) is unchanged.
- **The face (session 1159).** The panel's dates and counts are set in the text's face, as the other panels' figures in running text; mono stays for figures in table cells and hover cards. No figure or word moved.
- **The scorecard links back.** `/grid/caiso/alerts` carries one line under its breadcrumb, linking this panel (`/grid?grid=caiso#caiso-alerts`) and the scarcity strip (`/grid?grid=caiso#scarcity`); nothing else on it changed.

Decisions (chain 077):

- **The state stands first on CAISO's Mix tab**, above the latest hour: a trader opening CAISO reads whether the grid is on alert before anything else. It moves the blocks below it down the page; no figure's value or key changes.
- **No line in the grid picker**: the picker is shared by the four tabs, and a CAISO line there would read the notices on every tab. The owner may ask for a static link there.
- **"Today" is the Pacific day the page was drawn** (`renderTime()`, the page is cached up to an hour), and the key carries the day (`awe|last|signal|<day>`), so check-values recomputes the same question whenever it runs.
- **A day is a key written as text** (`data-raw="2024-07-24"`): check-values already compares a figure that is not a number as text (session 315's rule).
- **"No alert today" is never said past the table**: a day after the newest notice is "not held yet", with the newest notice day beside it. The report's revision date (9 October 2026) is only in the CSV's header, not in the live set, so the page gives the newest notice day.
- **An alert is the scarcity table's own signal set**, so the strip's squares (by hour) and its triangles (by day) mean the same notices.
- **The scorecard's "Limits" line "CAISO's Grid Emergencies History Report runs to 2025-04-30" is stale** since the report's revision of 9 October 2026 (notices to 2026-10-08, none an alert after 2024); it was left as written, since session 1155 changed nothing else on that page, and is put to the owner (`docs/reviews/grid-rulings-2026-10-23.md`).
