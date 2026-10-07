# Method: wind and solar curtailment by ISO

Energy Research Warehouse (ERW), session 18. Tables: `caiso_curtailment_daily`, `spp_curtailment_daily`, `ercot_wind_solar_hsl_daily` (series, daily, public) and `iso_curtailment_monthly` (derived, series, public). Code: `warehouse/connectors/curtailment.py`, `warehouse/derived/iso_curtailment_monthly.py`. The page that reads them: the site's `/curtailment` (platform tool 22, the curtailment tracker).

**The three ISOs' figures do not mean the same thing.** CAISO and SPP publish curtailment. ERCOT does not; the ERW's ERCOT figure is an estimate built from ERCOT's reported limits. MISO publishes nothing usable. Compare them with care, and never add them up as if they were one measure.

## What each ISO's figure means

| ISO | Table | What the number is | Whose number |
|---|---|---|---|
| CAISO | `caiso_curtailment_daily` | Wind and solar energy CAISO's market dispatch or operators cut, for local congestion or system-wide oversupply: economic bids dispatched down, self-schedules cut, and operator instructions | CAISO's |
| SPP | `spp_curtailment_daily` | Wind and solar energy curtailed by redispatch (congestion), by manual operator curtailment, and "curtailed for energy" (economic dispatch), per balancing authority area | SPP's |
| ERCOT | `ercot_wind_solar_hsl_daily` | Output below the High Sustained Limit (HSL): per hour, how far system-wide wind (or solar) output fell below the HSL the resources reported, summed over the day | the ERW's estimate, from ERCOT's figures |
| MISO | none | MISO publishes no curtailment series. Its market reports list hourly wind output ("Historical Hourly Wind Data") and nothing curtailed (checked 2026-09-27). Its market monitor reports curtailment yearly, in prose | none |
| NYISO, ISO-NE, PJM | none | Not checked in session 18 | none |

## CAISO

**Sources.**
- **Days before 2026-01-01:** "Production and curtailments data" (`https://www.caiso.com/library/production-curtailments-data`), one workbook per period. The Curtailments sheet lists every 5-minute interval with a curtailment, in MW, and since 2024 its reason, Local or System. The Production sheet gives 5-minute ISO solar and wind output in MW, among others. CAISO stopped publishing the workbooks as of June 2025. It then posted a one-time bulk file, named June to December 2025, that has no Production sheet and repeats the 2025 workbook's curtailment rows from 2025-01-01. The 2025 workbook's Production sheet covers the whole year.
- **Days from 2026-01-01:** the Daily Renewable Report (`https://www.caiso.com/library/daily-renewable-reports`), one HTML page per day. Its chart data are JavaScript arrays in the page: the day's hourly curtailment in MWh by fuel and by six categories (economic, self-schedule cut and operator instruction, each local or system), and 5-minute ISO solar and wind telemetry in MW.

**Computation.**
- A 5-minute MW value is 5/60 MWh. A day is the Pacific operating day, the date of the workbook's Date column or the report's chart date. It sits at 00:00:00Z of that date (Decision 11).
- **The workbooks overlap.** The "June to December 2025" file starts on 2025-01-01, so each interval is counted once, from the first workbook in name order that lists it. The session 18 run counted 25,848 curtailment intervals once that both files list.
- **A workbook day with no row for a fuel had none of it curtailed.** CAISO lists only the intervals with a curtailment, so every calendar day between a workbook's first and last curtailment is written, with 0 where nothing was listed.
- **Output** (`solar_generation_mwh`, `wind_generation_mwh`) is written only for a day with every 5-minute value: 288, or 276 or 300 on a daylight saving change day. The session 18 run dropped it for one day, 2019-12-09, which lacks some intervals. On a fall-back day the repeated hour's intervals carry the same local timestamps, and all 300 are counted. CAISO states that the curtailed energy is not counted in its production figures.
- **A report day** is written only from the report whose chart date is that day, and only if all six hourly category arrays for both fuels are complete.

**Variables:**
- `curtailed_solar_mwh` and `curtailed_wind_mwh`;
- `curtailed_<fuel>_local_mwh` and `curtailed_<fuel>_system_mwh`, where CAISO gives the reason (2024 on);
- `solar_generation_mwh` and `wind_generation_mwh`.

**Share of available output curtailed** (on the page): (curtailed solar + curtailed wind) / (curtailed + produced solar and wind). It is given only for a period with every one of the four figures.

## SPP

**Source.** VER Curtailments (`https://portal.spp.org/pages/ver-curtailments`), 5-minute MW by balancing authority area (BAA): wind and solar redispatch curtailments, manual curtailments, and curtailed for energy. The files are annual zips of daily files to 2024 (`.../ver-curtailments?path=/<year>/<year>.zip`), then daily files (`.../<year>/<month>/VER-Curtailments-<yyyymmdd>.csv`).

**Computation.**
- MWh = MW x 5/60.
- A day is the Central (America/Chicago) date of each interval's start, from the file's GMT interval ending minus 5 minutes.
- A BAA's day is written only with every 5-minute interval of it (288, 276 or 300).
- **Entities:** `spp:SPP` and, since SPP's western expansion, `spp:SWPW`. Older files have no BAA column and are SPP's.
- **Variables:** `curtailed_<fuel>_redispatch_mwh`, `curtailed_<fuel>_manual_mwh`, `curtailed_<fuel>_economic_mwh` (SPP's "curtailed for energy"), and their sum `curtailed_<fuel>_mwh`.

**No share.** The ERW holds no SPP wind and solar output for the same intervals and areas, so the page gives no share for SPP.

## ERCOT

**Source.** ERCOT reports NP4-732-CD (wind) and NP4-745-CD (solar), "Power Production, Hourly Averaged Actual and Forecasted Values", read from ERCOT's public MIS document list. Each report covers the 48 hours before it, and the list keeps about a week of reports. From each: system-wide actual output (`SYSTEM_WIDE_GEN`) and system-wide HSL (`SYSTEM_WIDE_HSL`), hourly.

**Computation.**
- Per operating day (Central) and fuel:
  - `<fuel>_generation_mwh` = the sum of hourly GEN;
  - `<fuel>_hsl_mwh` = the sum of hourly HSL;
  - `<fuel>_below_hsl_mwh` = the sum over hours of max(0, HSL - GEN).
- An hour below zero (output above the limit) adds nothing.
- A day is written only with GEN and HSL for every hour (24, or 23 or 25). The newest report wins for an hour in two reports.
- **Why this is not curtailment.** HSL is the output a resource reports it could sustain. Output falls below it when ERCOT dispatches the resource down (congestion, economics, instructions), but also through ramping, telemetry, and the hourly averaging of both figures. ERCOT publishes no curtailment figure. The page calls this "output below HSL" and never "curtailment".
- **Share** (on the page): below-HSL MWh / HSL MWh, wind and solar together.
- **History** starts when the ERW began reading the list, in September 2026. Earlier days would need ERCOT's public API, which requires registration.

## Monthly (`iso_curtailment_monthly`, derived)

- For each entity and variable of the three daily tables, a month's value is the exact decimal sum of its daily values.
- It is written only when every day of the calendar month is present. A month with a day missing is left out, and the log names it. The month in progress is never written; the page shows it from the daily rows.
- Share columns are computed on the page from the monthly sums, as above.

## Live set

- **Daily tables:** Supabase holds the last 100 days of each (`live_set.yaml`, `select`). The page shows the last 90.
- **Monthly table:** held whole.
- **Redivis:** holds every table whole. The CI runner restores the daily tables and the monthly table from the Redivis draft before a run, because each run adds only the latest days.

## Session 144: one page, every share, free energy, worth

Since session 144 the site has one curtailment page, `/curtailment`. It holds what `/curtailment` and `/curtailment/v2` showed (the second address redirects to the first; the full method of California's five-minute record stays in [`caiso_curtailment_intervals.md`](caiso_curtailment_intervals.md)), and four things that are new: every monthly share, Texas by the hour, where power is priced near nothing, and what curtailed energy was worth. The page's face carries one line per grid saying whose number it is and no rule or caveat: they are all here. Code: `warehouse/derived/curtailment_shares.py`, `free_energy.py`, `curtailment_worth.py`, `ercot_estimate_page.py` (the site's files under `site/data/curtailment/`), `warehouse/connectors/ercot_wind_solar_history.py`, `site/lib/freeenergy.ts`, `site/lib/curtailment.ts`.

The sections above describe the tables as session 18 built them. Three of their statements are out of date and are corrected here, not erased: SPP now has a share (below); NYISO, ISO-NE and PJM have been checked (below); and the share is no longer computed on the page from the monthly sums, it is read from `shares.json`.

### What each grid's number is, in full

These paragraphs stood on the page until session 144. The face now keeps one line for each (`FACE` in `site/lib/freeenergy.ts`).

- **CAISO.** CAISO's own figure: wind and solar output its market dispatch or operators cut, for local congestion or system-wide oversupply, including self-schedules cut. Output is the ISO's wind and solar production, which does not include the curtailed energy.
- **SPP.** SPP's own figure: wind and solar curtailed by redispatch (congestion), by manual operator instruction, and "curtailed for energy" (economic dispatch), for the SPP balancing authority area. SPP's western area (SWPW) is in the table as its own entity. Until session 144 the ERW held no SPP wind and solar output for the same intervals and gave no share; it now builds one on EIA-930's hours (below). SWPW has no share: no hourly wind and solar output for it is held.
- **ERCOT.** ERCOT publishes no curtailment figure. This is the ERW's estimate: for each hour, how far system-wide wind and solar output fell below the High Sustained Limit (HSL) the resources reported, summed over the day. It includes curtailment and anything else that keeps output under the limit. The history starts in September 2026, when the ERW began reading ERCOT's reports, which it keeps for about a week.
- **MISO.** MISO publishes no wind or solar curtailment series. Its market reports list hourly wind output ("Historical Hourly Wind Data") but no curtailed or dispatched-down energy (checked 2026-09-27, misoenergy.org market reports). MISO's independent market monitor reports curtailment once a year, in its State of the Market report, not as data. Since 4 October 2026 MISO is paused while its terms are reviewed ([`miso_pause.md`](miso_pause.md)): the page names it and shows no number of it.
- **PJM.** Licensed source needed: the ERW shows no PJM figure without a license from PJM. No request was made.
- **NYISO and ISO-NE.** Session 18 had not checked them. Session 144 did: see "NYISO and ISO-NE" below.

### The share of available output

One definition for every grid that has one, written by `curtailment_shares.py` into `shares.json` and into five variables of `iso_curtailment_monthly` (`share_curtailed_pct`, `share_curtailed_mwh`, `share_output_mwh`, `share_hours_held`, `share_hours_in_month`):

- **The rule.** Curtailed MWh over curtailed plus wind and solar output MWh, over the days of the month both are held. A month is written only when those days hold at least 95 percent of the month's hours; the numerator is cut to the same days; one output source a month; nothing is scaled up to a whole month. A share cannot pass 100 percent. A month without a share carries the file's reason, which the page shows on hover.
- **CAISO.** The wind and solar energy CAISO reports curtailed, over that energy plus CAISO's own wind and solar output of the same days: the operator's figures on both sides. To 2025 the output is the Production sheet of its Production and curtailments workbook (five-minute). For December 2019 (the workbook lacks intervals of 9 December 2019) and from January 2026 (the Daily Renewable Report's five-minute output could be read for only 9 to 29 days a month) the output is CAISO's Today's Outlook supply by fuel (`caiso_fuel_supply_history`, `caiso_fuel_supply`). 149 of 149 months have a share.
- **SPP.** The wind and solar energy SPP reports curtailed in its balancing authority area, over that energy plus EIA-930's hourly wind and solar net generation for SPP (SWPP) in the same hours: the operator's curtailment over a denominator the ERW builds from EIA's hours. 97 months, from September 2018. Before that EIA-930 has no generation by source (to June 2018) or prints zero wind in 1,464 hours (July and August 2018); those 54 months have no share.
- **ERCOT.** Output below the High Sustained Limit over the High Sustained Limit, wind and solar together. The ERW's estimate, not a curtailment figure of ERCOT's, and not comparable with the two above.
- **A year's share** on the page is the same division over the months of the year that have a share (their curtailed MWh over their curtailed plus output MWh), never another denominator.
- **The days.** The page no longer divides the last 90 days by the Daily Renewable Report's output: that figure overstated against the monthly share (next paragraph). For Texas the days still carry "percent of the limit", from the daily table's own two columns.

**CAISO's two output sources disagree in 2026.** On the days both hold, Today's Outlook shows more output than the Daily Renewable Report: 11 to 20 percent more a month for solar and 2 to 33 percent more for wind. From June to December 2025 Today's Outlook and the workbook agree within 1 percent (solar) and 0.1 percent (wind). So the months of 2026 rest on Today's Outlook, and a share computed on the report's output would be higher. Which of the two is CAISO's settled figure is open. Until session 144 the page's "last 90 days, percent of available output" used the report's output; it is gone, and every share on the page is `shares.json`'s.

### California by the hour, by reason and against the batteries

These notes stood on `/curtailment/v2`.

- **The data does not say where.** CAISO publishes one figure for its whole system: not the plant, not the node or zone, and for a "local" curtailment not which line was congested. So nothing on the page says whether a battery at a given place could have taken the power that was turned down.
- **By hour of the day.** Each bar is everything curtailed in that hour of the day over the period, in Pacific time. To 2025 from CAISO's five-minute record (MW over five minutes, as MWh); from 2026 from its daily report, which gives the hour by fuel.
- **By month.** A month is held when at least 90 percent of its days are; its figure is the sum over the days held, never scaled up. The months of the period chosen are drawn at full strength.
- **By reason.** CAISO's two reasons. Local: turned down to relieve a congested line somewhere on the grid. System: turned down because the whole system had more supply than it could use or export. Its file gives a reason from 2022 (9,241 five-minute rows of 2022 have none), and nothing before.
- **Against battery charging.** CAISO's own battery output is held from late August 2025, so the comparison is by month from September 2025. Charging is what the batteries took in, as a positive number; an hour counts as a charging hour when they took in more than they gave back over the hour. Both are system totals: a battery charges where it stands, and a curtailment happens where it happens. That the two fall in the same hours does not say the batteries could have taken what was turned down.
- **What the data does not locate, or say.** Where: one figure for the whole system, no plant, no node, no zone, and for a local curtailment not the line that was congested. The reason before 2022, and for part of 2022. The five-minute detail by fuel from 2026: CAISO's daily report gives wind and solar apart only by the hour. A day whose report could not be read whole is not held, and is not counted as a day with none. What was not built or not bid: curtailment is output turned down, not output that never had a place.
- **How it is computed.** CAISO lists each five-minute interval with a curtailment, in MW; its energy is the MW over five minutes. From 2026 its daily report gives each hour's MWh by fuel and category. The intervals are added by hour of the day and by month in Pacific time; nothing is estimated or filled. Each day's total equals the daily table the site already had, for every day both hold.

### Texas: nine days, by the hour

The owner asked for ERCOT's hourly wind and solar production reports back to 2016, with the High Sustained Limit, system-wide and by region. That cannot be met from open data, and the page says so with placeholders instead of numbers:

- **What ERCOT publishes openly.** NP4-742-CD (wind) and NP4-745-CD (solar), "Hourly Averaged Actual and Forecasted Values by Geographical Region", each posted hourly and holding the 48 hours behind it. ERCOT's public list keeps 7 days of postings, so the open history is about nine days. Each has system-wide output and system-wide HSL, and output by region. **The actual HSL is system-wide only.** A region has its output and a "COP HSL", the limit resources planned in their Current Operating Plan: a plan, not the limit reported in the hour. It is never read and never stands in for the HSL. So a region has output and "no limit published".
- **The regions** are ERCOT's own: wind PANHANDLE, COASTAL, SOUTH, WEST, NORTH; solar CenterWest, NorthWest, FarWest, FarEast, SouthEast, CenterEast. They are not the eight weather zones of ERCOT's load reports, and no curtailment by weather zone can be built from open data.
- **The years.** PG7-126-M, "Hourly Aggregated Wind and Solar Output", one workbook a year: 2023, 2024 and 2025 are on the public list. System-wide output only, no HSL, no region. 2016 to 2022 are not openly published; the reports' archive needs an account and a subscription key and was never requested.
- **Tables.** `ercot_wind_solar_hsl_hourly` (system-wide output and HSL, and output by region, from 28 September 2026) and `ercot_wind_solar_output_hourly` (2023 to 2025). The page's file is `ercot.json` (`ercot_estimate_page.py`).
- **The estimate, by hour and day.** Output below HSL is max(0, HSL less output) for each hour, wind and solar each on its own. A day is the Central clock day and is whole when every one of its 23, 24 or 25 hours is held. Over the nine whole days from 28 September to 6 October 2026: wind 124,238 MWh below the limit of 2,337,502 (5.31 percent), solar 59,578 of 1,683,414 (3.54 percent).
- **A month** is written when at least 95 percent of its hours are held, over the hours held, never scaled up. September 2026 holds 72 of 720 hours and October is in progress, so the page reads "not held yet" for both, with the count on hover. October 2026 is the first month that can qualify, and only while the list is read at least once a week.
- **The solar morning and evening pattern.** System-wide solar output is above the system-wide HSL in the morning hours of every day held (44 of 219 hours, by up to 2,921 MW in the hour from 08:00 Central) and below it by about as much in the evening, as if the two hourly averages were not of the same minutes. Output below HSL counts the evening and not the morning: 29,190 MWh above against 59,578 MWh below over the nine days. So a large part of the solar estimate may be timing and not curtailment. Wind shows it far less (562 MWh above against 124,238 below). The page draws the hours above the limit beside the hours below it, by hour of the day, and nets nothing.
- **Against the daily table.** `ercot_wind_solar_hsl_daily` (session 18) reads the system-wide reports; the hourly table reads the reports by region. Over the 6 days both hold, the 36 day-figures differ by at most 0.12 MWh on sums near 200,000 MWh: the two reports print output 0.01 to 0.02 MW apart.
- **A correction of this note.** The session 18 section above names the solar report NP4-745-CD. The report it reads (report type 13483) is NP4-737-CD; NP4-745-CD is the solar report by region (21809). The table and its numbers are as they were.

### Where free energy is

`free_energy.py` writes `free_energy.json` from the public hub and zone prices the ERW holds, for ERCOT, CAISO, NYISO, ISO-NE and SPP. MISO is named and blank (paused while terms are reviewed) and so is PJM (licensed source needed).

- **The counts.** For a place and a window: the hours priced below zero, and the hours priced under USD 5 per MWh. The second includes the first, each hour once; the hours from zero to under USD 5 are the difference. A negative-price hour is never counted twice.
- **The hour.** Real time where the place holds it for 95 percent of the window, otherwise day-ahead; the page says which. An hour of real time is the mean of its four 15-minute prices and counts only when all four are held.
- **The windows.** The last whole month and the twelve months ending with it. A count is written only when 95 percent of the window's hours are held; otherwise the place reads "not held yet" with the hours held on hover. Months and hours of the day are in each grid's standard time, with no daylight saving shift.
- **The heatmap.** For one place, twelve months by twenty-four hours of the day: the hours under USD 5 in each cell. When the year is whole the cells add up to the year's count, because an hour is in one cell and no other. A cell with no hour held is grey and reads "not held", not zero.
- **The gap.** The mean price of the dearest place less the mean of the cheapest, over the hours every compared place holds on one market. It needs two places with 95 percent of the window.
- **The two pairs.** West Texas against Houston (the load zones when both are held, otherwise the hubs HB_WEST and HB_HOUSTON) and California north against south (NP15 against SP15), each over the hours both hold.
- **The schematic is not a map.** No latitude or longitude of a hub or zone is held anywhere in the warehouse or the site, and none was made up: a trading hub is a set of buses and a zone is an area, so a point for either is a choice a person makes. The page draws each grid's places as tiles shaded by their count, in order of the count, and says that it is a schematic. A true map needs a person to choose the points. (Session 149 replaced that last sentence with a rule: a place is mapped only where its operator publishes the boundary. See "Session 149" below.)

### What it is worth

`curtailment_worth.py` writes `worth.json`.

- **Which hours.** CAISO: `caiso_curtailment_intervals`, five-minute to 2025 and hourly from 2026, valued from September 2024, the first month the hub's prices are held. ERCOT: the estimate above, over the hours held, never a month. SPP: curtailment is held by day only (its five-minute files were summed by day when read and are not kept), so an hour's price cannot be matched to it and nothing is valued. NYISO and ISO-NE: no hourly series is held.
- **Value.** Each hour's curtailed MWh times the hub's price of that hour, summed; and that over the MWh, USD per MWh curtailed. Real time and day-ahead each on its own, at SP15 and NP15 (CAISO) and at the hub average and West hub (ERCOT). A month is written when the curtailment covers at least 90 percent of its days and the price at least 95 percent of its hours. An hour with no price is left out of both the MWh and the dollars, never priced at a guess. The value is negative when the energy was curtailed in hours priced below zero: it is what the energy would have fetched at the hub, not a loss anyone booked. The data does not locate a curtailment, so the hub's price stands for a place the data does not name.
- **Cheap hours.** Of the curtailed MWh with a price: the share in hours priced below zero, and the share in hours under USD 5 (which includes those below zero).
- **A flat load.** 1 MW running only in the hours with any curtailment pays the simple mean of those hours' prices, against the mean of every hour held. Energy only: no delivery, no demand charge, no reserve.
- **A battery of 2, 4 or 8 hours.** Per MW: in every interval with curtailment it charges at 1 MW, or at the curtailed MW when that is less, until it has taken in that many MWh that local day; then it stops. One cycle a day: what it takes in one day is assumed gone by the next. Energy taken in at the meter; round-trip losses are not credited, and nothing is said of where the battery stands.
- **Against the fleet.** CAISO's batteries (`caiso_battery_storage`, five-minute, from late August 2025), for a month in which both tables hold at least 90 percent of the days. The installed power of the fleet is not in that data: the scale is the fleet's highest five-minute charging rate of the month, a measured figure. "A fleet that size" is the battery rule at that power; "the fleet charged" is what the fleet took in during the hours with curtailment. The share is the first over the second. It is not bounded by 100 in either direction, and the fleet charges from the whole grid, not from curtailed plants. There is no ERCOT fleet figure: the overlay holds CAISO's batteries only.

### NYISO and ISO-NE

- **ISO-NE** publishes a monthly figure openly: ISO Express, "Aggregate Monthly DDG Undelivered Energy" (`https://www.iso-ne.com/isoexpress/web/reports/operations/-/tree/aggregate-monthly-ddg-undelivered-energy`), one workbook a year, wind from 2018 and solar from 2025, delivered and undelivered MWh of its dispatchable wind and solar plants. It is **not pulled and not shown**: ISO-NE's legal notice says "Any duplication of the Content or non-personal use may violate copyright, trademark, and other laws." About 1,000 rows at no cost; it needs a ruling on the terms. The page says what exists and shows no number.
- **NYISO** publishes no curtailment series in an open form. It prints monthly wind and solar curtailment in its "Operations Performance Metrics Monthly Report", a PDF: a document, not data. Not in the ERW.

### The face and its placeholders

- One line per grid says whose number it is: the operator's figure, or the ERW's estimate.
- A figure that is not held is a few words ("not held yet", "no limit published", "not in the ERW") with the reason on hover, read from the site's file. The page never shows "not computable" and never fills, scales or smooths a figure.
- Every chart answers the mouse with the value, its unit and the day, month or hour.
- Tests: `tests/test_session144.py`, `tests/test_session144_ercot.py`, `tests/test_session144_page.py`, `site/scripts/test-freeenergy.mjs` and, on the built site, `site/scripts/check-curtailment.mjs`.

## Session 149: a true map only where the operator publishes the boundary

The owner's rule (7 October 2026): the schematic of tiles becomes a true map only for the places whose grid operator openly publishes a boundary or coordinates, the centroid is derived from that boundary, and every other place stays a tile.

- **What counts as published.** A file of shapes, a table of coordinates, or a document that defines the place by named counties or other published shapes, from the operator itself or from a government agency that names the operator as its source. **What does not:** a picture of a map from which a line would have to be traced or guessed, a third party's file, a point somebody chose.
- **The mark of a mapped place.** When a place is mapped, the mark is the centre of the zone's published boundary, not a hub's location: the area-weighted centroid of the published shape, computed by `warehouse/connectors/zone_boundaries.py` and checked to lie inside the shape. A trading hub that is a set of buses with no published area is given no point.
- **The result on 7 October 2026: no place of the page meets the rule, so all 37 stay tiles.** Each tile says why on hover, and each grid's caption reads "no boundary published" with the reason on hover. Nothing was drawn, traced or placed by hand. The findings, each read by the builder from the file itself, are in `site/data/curtailment/zone_shapes.json` (its shape is documented at its top, for the map of resources to reuse):
  - **CAISO (NP15, SP15, ZP26, trading hubs).** CAISO's tariff, Appendix I, "ISO Congestion Management Zones" (effective 13 October 2000), names three active zones, Northern (NP15), Central (ZP26) and Southern (SP15), and gives no line, county or coordinate. The California Energy Commission's GIS catalogue returns no dataset for NP15; for CAISO it returns the balancing authority areas (retired), not the zones.
  - **ERCOT (four hubs and eight load zones).** ERCOT's maps page lists five maps, each an image (`ERCOT-Maps_Load-Zone.jpg`, `Weather.jpg` and three others), and no file of shapes, counties or coordinates. Of its weather zone map ERCOT says: "This map displays the various Weather Zones that exist within the ERCOT footprint, but it does not necessarily include all counties that have participation within the ERCOT market."
  - **ERCOT's weather zones are defined, and are not places of this page.** ERCOT's Load Profiling Guide, Appendix D, Profile Decision Tree (1 May 2024), worksheet `ZipToZone`, assigns 2,476 ZIP codes to the eight weather zones (Coast 478, East 224, Far West 247, North Central 616, North 177, South Central 370, South 213, West 150). One row, ZIP code 79097, carries the name "Far West" and the code "NORTH": it is held out of both zones and flagged. The lists are in `zone_shapes.json` under `definitions.ercot_weather_zones`. They are not drawn: no hub or load zone of the page is a weather zone, and the shapes of ZIP codes are not in the site's atlas (it holds states and counties). Building them needs the Census Bureau's ZIP Code Tabulation Areas, a pull the session's brief did not name.
  - **NYISO (eleven load zones).** NYISO's "Subzones by Transmission Owner" (page reference P-23) lists 23 subzones of the eleven zones by transmission owner, with no county, coordinate or shape. The New York State GIS Clearinghouse's catalogue returns no dataset for NYISO. NYISO's zone map is an image, and its legal notice says: "Downloading, republishing, retransmitting, reproducing, or other use of any image or video on this website as a stand-alone file is strictly prohibited". It was not downloaded.
  - **ISO-NE and SPP.** Their sites were not searched for a boundary file; their places stay tiles and say so. **MISO** ("paused while terms are reviewed") and **PJM** ("licensed source needed") were not requested.
- **The pull.** 16 requests of the 30 allowed and 1,472,952 bytes of the 200 MB allowed, each with the User-Agent `ERW research project, github.com/SamuelEnrique/erw` and nothing else. Two failed and were left: ERCOT's maps page once (the name did not resolve; the next request read it) and `https://www.ny.gov/terms-use` (HTTP 404). The raw files are under `warehouse/raw/zone_boundaries/<operator>/`, each with its row of `downloads.csv` (url, file, bytes, sha256, retrieved_at_utc, terms_url); every request, a failed one too, is a row of `warehouse/raw/zone_boundaries/requests.csv`.
- **Terms, word for word.**
  - CAISO, Privacy and Terms of Use (`https://www.caiso.com/privacy-terms-of-use`): "may be used by you provided that you keep intact all copyright, trademark and other proprietary notices and that you credit the California ISO when using such materials and/or information."
  - ERCOT, Terms of Use (`https://www.ercot.com/help/terms`): "The publicly available contents of this website may be used, reproduced, and redistributed, provided that the contents are not modified and that you maintain all copyright and other notices contained in the contents, including this Agreement."
  - NYISO, Legal Notice (`https://www.nyiso.com/legal-notice`): "Access to this Web site does not confer any license or ownership interest in either the form or content of the Web site, including any confidential or proprietary information or intellectual property of any kind or nature, and the NYISO hereby expressly reserves such rights and property in its entirety."
  - California Energy Commission, Conditions of Use (`https://www.energy.ca.gov/conditions-of-use`): "Most of these materials and information were generated, compiled, or assembled at public expense and are free for public use consistent with the Public Records Act (California Government Code Section 6250 et. seq.), provided the Energy Commission is credited when using these materials and information."
  - New York State: the terms address tried answered HTTP 404. Nothing of New York State's is shown; its catalogue and one document of its Department of Public Service (a picture of a map, not used) were read only as evidence that no boundary file exists.
- **To build it again:** `python warehouse/connectors/zone_boundaries.py --pull --build`. `--pull` asks only for files the raw store lacks, never for one a site refused, and stops before the ceiling.
- Tests: `tests/test_session149_map.py` and, on the built site, `site/scripts/check-curtailment.mjs` (a mapped place's centroid is checked to lie inside its boundary there too).
