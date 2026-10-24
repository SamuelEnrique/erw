# Each grid's own scarcity signal, hour by hour

Energy Research Warehouse (ERW), session 254 (13 October 2026). Table: `scarcity_hours_by_grid` (derived, series, hourly, public). Code: `warehouse/derived/scarcity_hours_by_grid.py`. The datacenter page's second question, "Will the power be there?" ([`datacenter_pays_algorithm.md`](datacenter_pays_algorithm.md), 4.15), is the reader it was built for, and since session 280 reads it: `byGrid()` in `site/lib/datacenter/answers.ts` counts `rt_hour_ge_1000` and `own_signal` over the page's twelve months, each beside the hours held, for ERCOT and CAISO (session 254 wrote "No page reads it yet" here).

## Why

- The page counts an hour as short when the price is at or above USD 1,000 per MWh: one level for every grid (the owner's ruling of 12 October 2026). That count says what the market did. It does not say what the grid's operator said.
- Each operator has its own signal. ERCOT priced scarcity through an adder on real-time energy; CAISO declares an emergency. This table sets the two side by side, hour by hour, so that a page can say "the price was above USD 1,000 in 12 hours; the operator's own signal was on in 759".
- Where a grid's own signal is not held as a table, it is not in this table: nothing is inferred from prices.

## The table

One row per grid, hour and variable. `entity` is `iso:<grid>`; `ts_utc` is the hour's start; `unit` is `count`; `freq` is `PT1H`.

| Variable | What it is | `x_detail` |
|---|---|---|
| `rt_intervals_ge_1000` | The hour's 15-minute real-time intervals priced at or above USD 1,000 per MWh at the grid's hub, 0 to 4 | `held=<n>`: the intervals of the hour the warehouse holds |
| `rt_hour_ge_1000` | 1 when the mean of the hour's held real-time intervals is at or above USD 1,000, else 0. This is the page's count for the real-time market | |
| `da_hour_ge_1000` | 1 when the hour's day-ahead price is at or above USD 1,000, else 0 | |
| `own_signal` | The grid's own scarcity signal: 1 in force, 0 not. Written only for an hour the signal is held for | ERCOT: `rtorpa_mean=<USD per MWh>`. CAISO: every notice in force in the hour, `<type>@<region>`, joined by `;` |

- **An hour without a row is not held. It is not a zero.** A reader counts zeros from rows.
- **The level** is USD 1,000 per MWh, `LEVEL` in the code, the page's `SCARCITY_USD`.

## The window

- The 36 whole months before the month of the run, in each grid's standard time: for the run of October 2026, October 2023 to September 2026, 26,304 hours a grid.
- Standard time, not the clock on the wall, as the page counts its months: ERCOT's hours run from `2023-10-01T06:00:00Z` (Central standard, UTC-6), CAISO's from `2023-10-01T08:00:00Z` (Pacific standard, UTC-8).
- The table is rebuilt whole each run; the window moves when the month changes.

## The price count

| Grid | Hub | Real time | Day ahead | Held from |
|---|---|---|---|---|
| ERCOT | `HB_HUBAVG` | `ercot_all_hub_prices_history` (to 26 August 2026), then `iso_rtm_hub_prices`; market `ercot_rtm`, 15-minute | the same history, then `iso_dam_hub_prices`; market `ercot_dam` | the whole window |
| CAISO | `TH_SP15_GEN-APND` | `iso_hub_prices_history`, then `iso_rtm_hub_prices`; market `caiso_rtm`, 15-minute | `iso_hub_prices_history`, then `iso_dam_hub_prices`; market `caiso_dam` | 1 September 2024 |

- An interval held by both tables is read once, from the history.
- Only ERCOT's and CAISO's rows of the three `iso_` tables are read.
- The hubs are those of findings 8 and 9 (`batteries_lunch_grids`, `peak_hour_grids`). The datacenter page counts its own region's price from its own files; this table's price rows are the hub's, for setting beside the signal, and do not replace the page's count.

## Each grid's own signal

### ERCOT: its reserve adder above zero

- `ercot_rtm_price_adders`, entity `ercot:system`, variable `rtorpa_mean`: the hour's time-weighted mean of the Real-Time On-Line Reserve Price Adder, the adder of the operating reserve demand curve ([`ercot_rt_price_adders.md`](ercot_rt_price_adders.md)).
- `own_signal` is 1 when that mean is above zero, else 0. The mean itself is in `x_detail`, so a reader can set a higher level without another table: the datacenter page counts the adder at or above USD 100, because most hours above zero are fractions of a cent.
- **Held to 4 December 2025 and no longer.** ERCOT published the adder from 1 June 2014 to 4 December 2025. No `own_signal` row is written for a later hour. The reliability deployment adder its file carries since then is another thing and is not joined.

### CAISO: an EEA or an alert in force

- `caiso_grid_emergencies` (CAISO's Grid Emergencies History Report, refreshed in this session; the report's revision of 9 October 2026).
- `own_signal` is 1 when one of these notices was in force in any part of the hour, for any region: an Energy Emergency Alert (`eea_watch`, `eea1`, `eea2`, `eea3`) or an alert (`flex_alert`; and `alert`, `warning`, `stage1` to `stage3`, CAISO's notices before May 2022, none of which falls in the window).
- **Not the signal:** restricted maintenance operations (`rmo`) and transmission emergencies. A restricted maintenance notice asks plants to put off maintenance; a transmission emergency is local. They are named in `x_detail` for the hours they were in force, and the row's value stays 0.
- A notice's hours are its own "from" and "through" times (Pacific clock time, as CAISO prints them), turned into UTC. A notice printed on each day it covers is read once.
- **Held for every hour of the window:** the report is CAISO's whole history to the day it was revised, so an hour before that day with no notice is a 0, not a gap.

### Not in the table

- **NYISO, ISO-NE, SPP, MISO.** Their own signal is reserve shortage pricing; no table of those hours is held. Their price tables need a license from 21 October 2026 or are held (`warehouse/metadata/license_status.csv`), so their price count is not here either. Adding a grid is one entry in `GRIDS`.
- **PJM.** No PJM price is held.

## What the first run holds (13 October 2026, window October 2023 to September 2026)

| | ERCOT (`HB_HUBAVG`) | CAISO (`TH_SP15_GEN-APND`) |
|---|---|---|
| Hours in the window | 26,304 | 26,304 |
| Real-time hours held | 26,304 | 18,191 (from 1 September 2024) |
| Real-time hours at or above USD 1,000 | 12 (49 intervals) | 1 (11 intervals in 6 hours) |
| Day-ahead hours at or above USD 1,000 | 22 (January 2024: 4; May 2024: 4; January 2026: 14) | 0 |
| Own signal: hours held | 19,097 (to 4 December 2025) | 26,304 |
| Own signal: hours in force | 759 (2023, from October: 136; 2024: 430; 2025: 193) | 7 (an EEA Watch, 24 July 2024, 17:25 to 23:59 Pacific) |
| Hours with any notice in force | | 578 |

- **ERCOT, the two counts together.** In the 19,097 hours with both held, the price was at or above USD 1,000 in 11 and the adder was above zero in 10 of those 11. The adder was above zero in 759 hours in all: the signal is on far more often than the price count, which is why the page uses USD 100 for it.
- **ERCOT's twelve months of the page** (October 2025 to September 2026): 1,558 hours of the adder held, 1 October to 4 December 2025, the figure the datacenter page prints; 44 of them above zero.
- **CAISO.** One hour at or above USD 1,000 in 25 months of prices (27 August 2026), and one EEA in 36 months. The two do not overlap: the EEA Watch of 24 July 2024 is before CAISO's prices are held.

## On the Grid tool (session 1154, 23 October 2026)

The table's second reader: the Mix tab of `/grid`, the panel `grid_scarcity_<grid>` (`site/components/grid/ScarcityPanel.tsx`, `site/lib/scarcityStrip.ts`).

- **The window is the latest 30 days the table holds, not the 30 days before today** (session 1150's decision): the 30 standard-time days that end with the day of the newest hour held. For the run of October 2026 that is 1 to 30 September 2026 for both grids. The page names the newest hour and how many days before the page was drawn it was.
- **The strip:** the days across, the hour of day in the grid's standard time down. A cell for each hour with a `rt_hour_ge_1000` or `da_hour_ge_1000` row: filled where either is 1, faint where both are 0, hatched where neither is held. A square where `own_signal` is 1 (an hour whose own signal alone is held keeps a hatched cell and its square).
- **The hover:** the hour in standard time and in UTC, the variables at 1, `rt_intervals_ge_1000`, `own_signal`, and the highest price of the hour: the highest of the hub's 15-minute real-time prices in `iso_rtm_hub_prices` (variable `spp_rtm` for ERCOT's `HB_HUBAVG`, `lmp_rtm_15m_mean` for CAISO's `TH_SP15_GEN-APND`), where the live set holds them (about 35 days, so from 18 September 2026 for this window); for ERCOT, where it does not, the highest real-time price of ERCOT's local day, `rt_max` of `ercot_hub_prices_daily`, said as the day's; else none, said so. Each tip ends with the level and its source.
- **The figures under it**, each a check key: `series_sum|scarcity_hours_by_grid|<variable>|<start>|<end>|iso:<grid>` for the hours at 1 of `rt_hour_ge_1000`, `da_hour_ge_1000` and `own_signal` and for the intervals of `rt_intervals_ge_1000`; `series_n|scarcity_hours_by_grid|<variable>|<start>|<end>|iso:<grid>` (a key kind added in this session: the distinct hours the rows hold) for the hours held of each; `series_max|iso_rtm_hub_prices|<variable>|<start>|<end>|<hub>` for the highest 15-minute price held; and for ERCOT `series_max|ercot_hub_prices_daily|rt_max|<first day>|<day after the last>|ercot:HB_HUBAVG`.
- **CAISO's alert days** (session 1155): a triangle under each day of the strip with an Energy Emergency Alert or a Flex Alert in `caiso_grid_emergencies` that Pacific day (the notices this table's `own_signal` counts, by day rather than by hour), named in the cells' hover; restricted maintenance and transmission emergencies named under the strip and not marked. The keys and the day rule are in `california_reliability.md`, "On the Grid tool: the alert state".
- **ERCOT's notice days** (session 1174): a triangle under each day of the strip with a call on supply or demand in `ercot_grid_notices` that Central day (an EEA or rotating outages, a conservation appeal, a watch, an OCN for extreme weather: the rows the table counts, `x_counts` `yes`), named in the cells' hover; the days with a notice that is not a call (an Advisory on the control room's own tools, a test) named under the strip and not marked. ERCOT's own signal, the reserve price adder, is not held after 4 December 2025, so these days are the strip's only mark of ERCOT's own state since. The keys (`ercotn|ndays|call|...`, `ercotn|ndays|other|...`) and the day rule are in `ercot_grid_notices.md`, section 6.
- **The other grids** are not in the table, and the panel says why in one line: PJM "license needed" (no PJM price is held); MISO "paused" (since 4 October 2026, `miso_pause.md`); NYISO and ISO-NE "license needed" (their prices need a license from 21 October 2026); SPP "not in the table yet" (its hub prices are public; its own signal is not held as a table). The Lower 48 links ERCOT's and CAISO's.
- **The Lower 48 has no strip of its own** (session 1185, chain 091, 24 October 2026), and its line says why: this table counts a grid's hours at its own hub's price and its own operator's signal, and the Lower 48 has neither one hub nor one operator. The method defines no national scarcity measure, and none is made by adding up the grids: the table holds two of the seven, and an hour short in ERCOT is not an hour short in the Lower 48. Checked for the session: no other table of the live set holds a scarcity count, a reserve margin or an emergency signal for the Lower 48 by hour or by month.

## The panel's rules and decisions (chain 077, 23 October 2026)

What sessions 1155 to 1160 changed in the panel above, and the decisions behind it and behind session 1154's rules:

- **The look (session 1159).** The panel's title is drawn with the tool's `ToolSection`, as every other panel of the chain; "license needed", "paused" and "not in the table yet" have the Grid tool's one look for a held or missing figure (captions grey, upright, a dotted rule under words that hold a reason on hover), by a rule in `site/app/tokens.css` scoped to the tool. No word or figure moved.
- **The strip's day marks (session 1155)** are drawn by the shared `HeatChart` (`site/components/svgchart.tsx`) through an optional `colMarks`, off by default, so no other chart changes.
- **One read of CAISO's notices a page (session 1160).** The strip's alert days, the alert state, the Reliability section and the monthly mix all call `gridNotices()` (`site/lib/reliability.ts`); its rows are read and parsed once per render (React's `cache`), the same request and rows as before.
- **At 390 pixels (session 1158)** the strip keeps its hover (a tap is a pointer move) and its Chart | Table toggle carries every value; the table view scrolls in its own frame.

Decisions (chain 077):

- **The window is the latest 30 days held, not the 30 days before today**, because no warehouse data is written by the chain and the table's newest hour is 1 October 2026: a strip of the 30 days before 23 October would hold its first eight days and draw the rest as not held. The page names the newest hour and its age in days so the gap is read. The owner may ask for the last 30 days with the empty days drawn as not held, once the table is refreshed.
- **The days are the grid's standard-time days** (1 to 30 September 2026, not 2 September to 1 October in UTC days), because the table's own clock is standard time.
- **The price on hover is the hour's highest 15-minute real-time price** from `iso_rtm_hub_prices` where the live set holds it (from 18 September 2026), else for ERCOT the local day's highest (`ercot_hub_prices_daily`, said as the day's), else "no price of this hour is in the live set". No other table was read.
- **A cell is the price count and the own signal a square on it**, so an hour with only its own signal held keeps a hatched cell and its square.
- **`series_n` counts distinct hours**, as an hour written twice is one hour; the counts are `series_sum` of 0 or 1 values, which equal the per-hour reading while the table writes each hour once.
- **The constants are the panel's own** (`SCARCITY_TABLE`, `SCARCITY_LEVEL` and the hubs in `site/lib/scarcityStrip.ts`, held equal to `lib/datacenter/answers.ts`'s by the node test), so the Mix tab's license line does not gain that file's other tables.
- **The newest hour's age in days is not a key**: it is the clock against the page's drawing time, as the energy mix panel's age in hours.
- **SPP is "not in the table yet"**, not "license needed": its hub prices are public, and the table leaves it out because its own signal (reserve shortage pricing) is not held as a table ("Not in the table" above). Adding a grid is one entry in `GRIDS`, a builder change left for a later chain.

## The panel in chain 078 (24 October 2026)

Chain 078 in this note (sessions 1164 to 1177): 1174 (ERCOT's notice days on the strip, the bullet in "On the Grid
tool" above; the rule and the keys in `ercot_grid_notices.md`, section 6).

Decisions (session 1174):

- **One prop carries either grid's marks**: CAISO's line in `site/components/grid/ScarcityPanel.tsx` reads its days as
  `caiso` (renamed inside that line only), so `colMarks={alerts?.cols}`, pinned by `tests/test_session1155.py`, carries
  CAISO's or ERCOT's marks; CAISO's strip is drawn as before.
- **ERCOT's strip marks calls only**: a day with a notice that is not a call is named under the strip, never marked, as
  CAISO's restricted maintenance is.

## The panel in chain 091 (24 October 2026)

Chain 091 in this note (sessions 1178 to 1189): 1181 (a failed price read), 1182 (its file), 1183 (its anchor), 1184
(its method link), 1185 (the Lower 48's line, the last bullet of "On the Grid tool" above), 1186 (its keys under
check-values); written by session 1188 from their reports. Each rule in full is in `grid_network.md`, in the section of
the session's name.

- **A failed price read (session 1181)**: when `iso_rtm_hub_prices` could not be read, the strip said "No 15-minute
  price of these days is in the live set" and each cell's hover "No price of this hour is in the live set", and nothing
  for ERCOT's daily price; now each says the price could not be read (`site/lib/scarcityStrip.ts` takes the failed
  reads). A failed read of this table keeps the view's "working on it", as before.
- **Its file (session 1182)**: `erw_grid_scarcity_<grid>.csv`, each count of the strip with its hours held and its
  table, the provenance in its first lines.
- **Its anchor (session 1183)**: `#scarcity`, kept as it was on the panel's one section.
- **Its method (session 1184)**: the source line's link now opens "On the Grid tool (session 1154, 23 October 2026)"
  (`METHOD_SCARCITY` in `site/lib/gridAnchors.ts`), its words unchanged; the Lower 48's panel and a grid without a strip
  draw the line "Method: ..." at the panel's foot.
- **Under check-values (session 1186)**: the strip's `series_sum` and `series_max` keys of one window are read
  together, one request a group; `series_n|` reads one window a key, as before (no two keys of one window).

Decisions (chain 091):

- **An empty answer of a window stays what the table holds for it** ("No 15-minute price of these days is in the live
  set"); only a failed read says "could not be read" (session 1181).
- **The anchor `#scarcity` is kept**: links on the page point to it, and sessions 1155, 1159 and 1174 pin it (session
  1183).
- **The heading "On the Grid tool (session 1154, 23 October 2026)" is a link target**, its id held to
  `METHOD_SCARCITY` by `site/scripts/test-grid-methods.mjs`: a rename is made with the constant (session 1184).
- **No national strip is summed from the grids** (session 1185): the reason is the bullet above.

## Checks

- The validator: `python warehouse/validate/erw_validate.py warehouse/output/scarcity_hours_by_grid.csv`, pass.
- `tests/test_session254.py`: the window in standard time; a notice's hours across midnight UTC and across a clock change; a notice repeated by day read once; restricted maintenance named and not counted; the adder's hours after its last one not written; an interval in both price tables read once; the counts above against the table on the data machine (skipped where the table is not).
- By hand: the EEA Watch of 24 July 2024, 17:25 to 23:59 Pacific daylight time, is 00:25 to 06:59 UTC on 25 July, seven hours starting 00:00 to 06:00 UTC: the seven rows with `own_signal` 1.

## License

Public. A derived table inherits the most restrictive license of its inputs: ERCOT (raw data in public parts of its site may be redistributed in compilations and analyses) and CAISO (its materials may be used with credit to the California ISO). Credit: California ISO, Grid Emergencies History Report; ERCOT.
