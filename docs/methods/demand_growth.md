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

Since session 152 demand growth is one page at one address, `/demand`, in review, with views kept in the address (two then; since session 239 a third, consumption, what `/consumption` showed, read from `eia_retail_sales_monthly` and `eia_sector_energy_consumption_monthly`):

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

## Session 331 (20 October 2026): downloads and the third view's note

Each view of `/demand` offers its tables under it, as the live set's CSV with a Python and a Stata reader of that CSV
(session 328's shared line): as metered, `eia930_demand_growth`; with the weather taken out, `eia930_demand_weather` and
the two NOAA tables; consumption, its two EIA tables. The consumption view has its own note now,
[consumption](consumption.md), linked from the view as the other two link theirs.

## The explorer (session 404, 21 October 2026)

A second page reads this table: `/explore/demand-growth`, in review and not in the menu, the second of the signature
explorers (platform tool 5, on the frame session 403 built for `/explore/ercot-peak-premium`). `/demand` stays as it
was. Where `/demand` reads the site's copy (`data/demand_growth.json`), the explorer reads the table's rows in the live
set, so every figure it shows is one row, with that row's check key (`series|eia930_demand_growth|<entity>|<variable>|<year>`),
and `scripts/check-values.mjs` reads it again on five views. It computes nothing.

Two filters, kept in the address:

| Filter | Values | Rows read |
|---|---|---|
| `grid` | `ercot`, `caiso`, `pjm`, `miso`, `spp`, `nyiso`, `isone`, `us48` (the slugs of `/demand`) | |
| `window` | `avg`, the whole year's average hour (the default) | `avg_demand_mw`, `avg_demand_growth_since_2019_pct`, `avg_demand_growth_yoy_pct`, `hours_used`, `hours_in_year` |
| | `peak`, the whole year's highest hour (none for the Lower 48) | `peak_demand_mw`, `peak_demand_growth_since_2019_pct` |
| | `ytd`, the year so far (the newest year against the same months of 2019) | `ytd_avg_demand_mw`, `ytd_avg_demand_growth_since_2019_pct`, `ytd_hours_used`, `ytd_hours_in_window` |
| | `m01` to `m12`, one calendar month | `avg_demand_mw_mMM` every year; `growth_pct_mMM`, `growth_mw_mMM` on the last whole year's row |
| | `h00` to `h23`, one local hour of the day over the year | `avg_demand_mw_hHH` every year; `growth_pct_hHH`, `growth_mw_hHH` on the last whole year's row |

A value the table does not hold falls back to the default (ERCOT, `avg`), with one line saying so.

**The headline chart.** No document of the ERW names a "thesis chart" for demand growth (the thesis charts named are the
ERCOT peak premium's). The explorer's first chart is this table's own headline figure: growth since 2019 for every grid,
in the window chosen, at the last whole year (the newest year for the year so far), largest first, drawn with the site's
bar chart (`components/tool/GroupedBars.tsx`). Under it: every grid's 2019 and latest demand and its growth (and, for a
month or an hour, the change in MW); the grid's growth by window along the years and its demand in the window by year
(`components/LineChart.tsx`); the grid's rows year by year.

**How old it is.** The table is held for review in the live set (`warehouse/supabase/live_set.yaml`, `review_hold`), so
the site's public catalogue does not list it; the explorer reads the catalogue's own row of the table
(`site/lib/explore/heldfresh.ts`) and states its last computation and the newest year it holds, and the end of the
year-to-date window from the table's header. No date is written by hand. For the same reason the downloads line says
the table is not in the site's live set and points to Redivis, as `/demand` does.

## The figures on the page and their keys

Each number `/explore/demand-growth` shows carries its key (`site/components/Num.tsx`), which `site/scripts/check-values.mjs`
checks against the live set and `site/scripts/check-methods.mjs` against this note (finished on the combined branch of
chain 015, 21 October 2026). The keys of a month's or an hour's window, which the table above writes as `mMM` and `hHH`:

- `eia930_demand_growth`, `avg_demand_mw_m<month>` and `avg_demand_mw_h<hour>`: the grid's average demand in the window,
  in MW: the headline "Average demand in ..." (its last whole year, with 2019 under it), the columns "2019, MW" and the
  last whole year's MW of the table "Every grid", and the MW column of the grid's table year by year
  (`site/lib/explore/demandgrowth.ts`, `WINDOWS`).
- `eia930_demand_growth`, `growth_pct_m<month>` and `growth_pct_h<hour>`: the growth since 2019 of the same window, in
  percent, on the last whole year's row only: the first headline and the column "Growth since 2019, percent" of the
  table "Every grid".
- `eia930_demand_growth`, `growth_mw_m<month>` and `growth_mw_h<hour>`: the change since 2019 of the same window, in MW,
  on the last whole year's row only: the column "Change, MW" of the table "Every grid".

## Decisions of the explorer (each dated, and reversible unless said)

The choices made on `/explore/demand-growth`, one line each with its session; session 404's are gathered here from "The explorer" above.

1. 2026-10-21, session 404: two filters in the address, `grid` and `window`; the default ERCOT and the whole year's average hour, the table's headline figure; a value the table does not hold falls back to the default and the page says so.
2. 2026-10-21, 404: no document names a thesis chart for demand growth, so the first chart is the table's own headline figure for every grid in the window chosen, each grid at its own latest year, largest first.
3. 2026-10-21, 404: the table is held for review in the live set, so the explorer reads the catalogue's own row of it for its age and says the table is not in the site's live set; weather is not removed, and the page says so.
4. 2026-10-21, 404: a growth is written with its sign outside the number; a MW figure whole.
5. 2026-10-23, session 2201: every figure carries its source in its hover (the table, the grid's name, the variable, the year, EIA-930 and this note), read from the figure's key by `site/lib/explore/source.ts`; the three headline numbers carry the same words in the brand's tip, the table figures the title alone.
6. 2026-10-23, 2201: the brand's bar chart (`site/components/tool/GroupedBars.tsx`, drawn on the server) is wrapped in `BarsHover.tsx`, a client component that draws the brand's hover card for the group under the pointer or the keyboard's arrows; the SVG, its `<title>` a group and every figure are as before, and the card's words are written on the server. The seller page and the datacenter grids view, which draw the same chart, gain the card the same way.
7. 2026-10-23, session 2204: on reading, nothing of the page's type, color, tables or charts stood outside `docs/brand.md` (`site/app/tokens.css` carries the explorer's frame to the brand); no change.

## The tool as a reader meets it (session 7508, 16 November 2026: the done line)

This section is the explorer `/explore/demand-growth` as a reader meets it: every view, the row each figure is, how it is written, the rule the rows are built by in full, the replication, what published figures stand against it, and the choices on the page. It completes the sections above and replaces none of them. Where the list "Decisions of the explorer" above and this section differ, this section is the page as it stands on `wip/7508-demand-growth`.

### What the page reads

One table, `eia930_demand_growth`, as it stands in the live set (held for review there, license public), and its header lines, for the end of the year-to-date window. It does not read `site/data/demand_growth.json` (that is `/demand`'s copy), the subregion table (`subregion_demand_growth.md`), the FERC Form 714 forecast table (`ferc714_forecast_growth.md`) or the weather-adjusted table. It holds no forecast. It computes nothing: every figure is one row, drawn with that row's check key.

### The views: 8 grids by 39 windows

Two choices in the address, `grid` and `window`; 312 views. With neither, ERCOT and `avg`. A value the table does not hold falls back to that default and one line says so.

Grids, in the page's order, with the table's entity: ERCOT `eia930:ERCO`, CAISO `eia930:CISO`, PJM `eia930:PJM`, MISO `eia930:MISO`, SPP `eia930:SWPP`, NYISO `eia930:NYIS`, ISO-NE `eia930:ISNE`, Lower 48 `eia930:US48`.

| Window | Words in a title | MW row | Growth row | Change row | Year read at |
|---|---|---|---|---|---|
| `avg` | average demand | `avg_demand_mw` | `avg_demand_growth_since_2019_pct` | none | the last whole year |
| `peak` | peak demand | `peak_demand_mw` | `peak_demand_growth_since_2019_pct` | none | the last whole year |
| `ytd` | average demand, the year so far | `ytd_avg_demand_mw` | `ytd_avg_demand_growth_since_2019_pct` | none | the newest year |
| `m01` to `m12` | average demand in January (to December) | `avg_demand_mw_mMM` | `growth_pct_mMM` | `growth_mw_mMM` | the last whole year |
| `h00` to `h23` | average demand at 00:00 local (to 23:00) | `avg_demand_mw_hHH` | `growth_pct_hHH` | `growth_mw_hHH` | the last whole year |

The last whole year of a grid is the newest year with an `avg_demand_mw` row (2025 today); its newest year is the newest with a `ytd_avg_demand_mw` row (2026). The year so far runs from 1 January to the end of the month the table's header names ("year to date: 1 January to the end of MM/YYYY"): October 2026 in the table of 6 November 2026. A year equal to the header's year is written "2026 so far (January to October)" in the year-so-far window.

### Every figure, in the page's order

For the grid G and the window W chosen, with L the year read at:

1. **First headline.** Growth since 2019: W's growth row of G at L, percent. Under it, W's MW row of G for 2019 and for L (in the year-so-far window the 2019 figure is that of the same months, and the line says "2019, January to October").
2. **Second headline.** W's MW row of G at L; under it, 2019's.
3. **Third headline.** For a month or an hour: W's change row at L, MW. In the year-so-far window: `avg_demand_growth_since_2019_pct` at the last whole year. Otherwise: `ytd_avg_demand_growth_since_2019_pct` at the newest year.
4. **The headline chart.** One bar a grid: W's growth row of each grid at that grid's own year read at; largest first, a grid with no row last and marked "not held"; the grid chosen is marked "shown below". A bar's hover: "ERCOT: +27.22 percent from 2019 to 2025".
5. **The table "Every grid".** One row a grid, in the page's order: W's MW row for 2019 and for the grid's year read at (the year is written beside the figure when it is not the chosen grid's), W's growth row, and for a month or an hour the change row.
6. **The second chart.** For G, one group a year, three bars: `avg_demand_growth_since_2019_pct`, `peak_demand_growth_since_2019_pct` and `ytd_avg_demand_growth_since_2019_pct` of that year; a year without a row has no bar. No figure is written on the bars: the three figures of a year are its hover ("ERCOT, 2025: average hour, whole year +27.22 percent; highest hour, whole year +12.16 percent; the year so far (January to October) +26.97 percent"). A series with no row for G (the peak, for the Lower 48) is not drawn.
7. **The third chart and the table year by year.** Every year G has W's MW row for: the MW; in `avg`, `peak` and `ytd` the growth row (2019 reads "base year"); in `avg` also `avg_demand_growth_yoy_pct`, `hours_used` and `hours_in_year`; in `ytd` also `ytd_hours_used` and `ytd_hours_in_window`. A month's table holds the newest year's month where the table has it (March 2026), with no growth: the table writes a month's growth on the last whole year's row only.

All three charts are the site's bar chart (`site/components/tool/GroupedBars.tsx`); the line of "The explorer" above that names `components/LineChart.tsx` for the third is out of date.

For the Lower 48 in the `peak` window the table holds no row: the three headline slots read "not held" (the third is the year so far), the third chart and the table year by year are not drawn, and a line says why.

### How a figure is written

MW and counts whole (half up), with separators. A percent to two decimals, always (session 7508: a whole percent was written "8" beside a bar's "8.00"). A growth, in percent or MW, with "+" before it when above zero. A figure the table does not hold reads "not held", with no unit beside it (session 7508). The page writes the table's own value; the replication recomputes each growth from the MW rows (rule 6 below) and finds the same value for all 770 growth figures the page can show.

### The rule in full

The sections "Input", "Which hours are used" and "The rows" above and `eia930_demand_growth.md` state the rule. Recomputing the table from EIA's workbooks from those words alone (session 7508, `replication/demand_growth/from_hourly.py`) needed four things they do not say; they are stated here.

1. An hour is dated by its start: EIA's "UTC time" is the hour's end, and one hour is taken off.
2. California: an hour whose start is from 2023-10-31T23:00Z to 2025-12-02T22:00Z is read one hour earlier. **Not said before:** the hour moved onto 2023-10-31T22:00Z meets the hour EIA wrote there; EIA's own hour stays and the moved one is dropped (found by trial: the other reading differs from the table on five rows of 2023). 2025-12-02T22:00Z is left empty.
3. An hour is used when it is held, above zero, within 25 percent of the median of those of the two hours before and the two hours after that are held and above zero (a neighbour that is blank or not above zero drops out and no further hour takes its place), and from a third of to three times the area's median hour. **Not said before:** "within 25 percent" is of the median (the hour less the median, over the median, at most 0.25 either way), and the test is run once on EIA's hours as written, not again on what is left.
4. Years, months and hours of the day are local clock time (Central for ERCO, MISO, SWPP; Pacific for CISO; Eastern for PJM, NYIS, ISNE, US48). A whole year is written at 95 percent of its hours used, a month at 95 percent, a month's hour of the day at 90 percent; an hour of the day over the year has no threshold of its own.
5. The year to date is 1 January to the end of the header's month, for every year, with the same 95 percent.
6. **Not said before:** a growth is computed from the means and peaks as the table writes them (MW to one decimal; a peak whole): percent to two decimals, a change in MW to one decimal. A peak's `x_at` is the first hour of the highest value.

### The replication

`replication/demand_growth/`, written from this note:

- `replicate.py`: every slot of text of every view, from the table alone (`table_rows.csv`: the 3,380 rows the page reads, as held on 16 November 2026), set beside the page drawn with the site's own code (`site/scripts/demand-growth-figures.mjs`). As run: "/explore/demand-growth: 35936 of 35936 slots of text on 315 views equal the replication's (3275 distinct checked figures; 770 of 770 growth figures recomputed from the MW rows)". Before the session's four fixes, 2,237 slots differed.
- `from_hourly.py` (with `extract_hours.py`): the table's rows from EIA's hourly demand, all eight areas, every year. As run on EIA's workbooks of 3 October 2026 (the newest on the code machine): "24060 of 24062 rows of 24116 equal the table's; 51 rows need hours after the workbooks' last (39 equal from EIA's hourly route); 3 not recomputed". The two that differ are the Lower 48's August and September 2026 (592,625.6 and 541,210.6 MW from the workbook of 3 October; 592,629.3 and 541,551.6 in the table, built from the workbook of 5 November): EIA revised its hours between the two. The 54 rows that need the hours of 4 to 31 October 2026 (each area's year so far of 2026 and its October) wait for the data machine, which holds the workbooks of 5 November (a data request row of session 7508). The hours left out since 2019 are those of the table "As built" above: 38 of CAISO, 7 of PJM, 2 of SPP, 1 of the Lower 48, 12 hours of zero of NYISO.
- `replicate.do`: the five headline figures in Stata, the expected values at its top.

### What published figures stand against (read 16 November 2026)

Each host's robots file and terms were read before its first request; none forbids the path asked. `ercot.com` was not asked (its robots file disallows the paths its documents are served from). The percents marked computed are session 7508's arithmetic on the publisher's cells. No figure of ours was adjusted.

| Ours | Published | Publisher, document, date | Difference, and why |
|---|---|---|---|
| Lower 48, average demand, 2019 to 2025: +7.03 percent | +7.05 percent (computed: 3,811,150 to 4,079,909 thousand MWh) | EIA, Electric Power Monthly, data for August 2026, table 5.1, sales to ultimate customers, all sectors | 0.02 points. Another measure (sales to customers in 50 states, not demand at the Lower 48's grid), from another EIA form (EIA-861M, not EIA-930) |
| Lower 48, 2024 to 2025: +2.73 percent | +2.63 percent sales (computed, the same table); generation +2.7 percent (computed: 4,309 to 4,425 billion kWh) | The same; EIA, Short-Term Energy Outlook, November 2026 (10 November 2026), table 7a | 0.10 and 0.0 points |
| Lower 48, January to August 2026 on the same months of 2025: +2.53 percent (computed from the monthly rows); the page's year so far, January to October, on 2019: +10.24 | Sales, January to August: +1.55 percent on 2025 (2,766,883 to 2,809,886), +9.46 on 2019 (computed) | EIA, Electric Power Monthly, table 5.1; by state, `eia_retail_sales_monthly` (EIA-861M) as held 5 November 2026 | Demand at the grid ran about 1 point ahead of sales in 2026. Not established why (sales are billed and reported later than the hours they cover; the page's window also runs two months further) |
| ERCOT, average demand, 2019 to 2025: +27.22 percent; 2024 to 2025: +5.57 | Texas retail sales: +24.20 percent; +5.51 (computed) | EIA, Form EIA-861M by state, `eia_retail_sales_monthly` | 3.0 points over six years, 0.06 on the year. ERCOT is not all of Texas, and sales leave out losses |
| NYISO: -2.73 percent; ISO-NE: -2.54; CAISO: +4.45 (2019 to 2025) | New York sales -1.26; New England +0.14; California -2.96 (computed) | The same | 1.5, 2.7 and 7.4 points. California's two figures have opposite signs: CAISO is not all of California, and no cause is established here (a row of the faults file) |
| Highest hour of each grid, 14 figures: the records before 2026 of ERCOT (85,544 MW, 20 August 2024), PJM (160,560, 23 June 2025), SPP (56,010, 21 August 2023), CAISO (51,104, 6 September 2022), ISO-NE (25,898), NYISO (31,857), and the seven highest hours of 2026 (ERCOT 91,075, 22 July; PJM 162,648, 2 July; SPP 57,964; CAISO 49,959; ISO-NE 25,289; NYISO 31,097; MISO 121,514) | 85.5, 160.6, 56.0, 51.1, 25.9, 31.9 GW; 91.1, 162.6, 58.0, 50.0, 25.3, 31.1, 121.5 GW, the same days | EIA, Today in Energy, "PJM, ERCOT, and SWPP all set peak load records this summer", 15 October 2026 | None at EIA's rounding, 14 of 14. EIA reads the same form; this checks the hours used and the screen, not the form (the 2026 peaks are `ytd_peak_demand_mw`, which the page does not draw) |
| PJM, highest hour: 152,315 MW (19 July 2019, the hour to 18:00) and 160,560 MW (23 June 2025, the hour to 18:00): +5.41 percent | Unrestricted peak 151,302 MW and 160,709 MW, the same days and hours: +6.22 percent (computed); metered 2025: 159,660 MW | PJM, 2026 PJM Load Forecast Report, 14 January 2026, tables F-1 and B-1 | +0.7 percent in 2019, -0.1 in 2025. EIA's balancing authority demand, not PJM's own unrestricted load (which adds back load it reduced) |
| PJM, average demand 2019 to 2024: +1.57 percent (800,260 to 815,087 GWh as mean MW times the year's hours) | Net energy 785,209 to 797,331 GWh: +1.54 percent (computed) | The same, table F-2 (its last year is 2024) | 0.03 points on the growth; our level is 1.9 to 2.2 percent above PJM's net energy |
| CAISO, highest hour: 43,849 MW (15 August 2019, from 17:00) and 43,860 MW (21 August 2025, from 18:00): +0.03 percent | 44,301 MW (15 August 2019, 17:50) and 44,506 MW (21 August 2025, 18:07): +0.46 percent (computed) | CAISO, California ISO Peak Load History, January 2026 | -1.0 and -1.5 percent: an hour's average against an instant, the same evenings |
| No forecast is held. For scale: the Lower 48 grew 1.14 percent a year from 2019 to 2025, ERCOT 4.09, PJM 0.88 (computed) | US sales +2.2 percent in 2026 and +1.5 in 2027 (computed from table 7b). PJM: summer peak +3.6 percent a year and net energy +5.3 percent a year over ten years. North America: summer peak "over 224 GW" higher in ten years. US: peak demand +166 GW in five years, "a 3.7% annual rate" | EIA, Short-Term Energy Outlook, November 2026. PJM, 2026 Load Forecast Report, page 6. NERC, 2025 Long-Term Reliability Assessment, January 2026, page 25. Grid Strategies, "Power Demand Forecasts Revised Up for Third Year Running, Led by Data Centers", November 2025, pages 3 and 22 | Nothing of ours stands against a forecast. The published forecasts are several times the growth metered since 2019 |

Nothing published stands against: a month's or an hour's growth by grid (the 36 windows `m01` to `h23`), the hours used, MISO's and SPP's average demand growth, and ERCOT's own count of its peak (its site was not asked; the figure "85,508 MW" in "The rows" above has no document named, and it is not on the page).

### What the tool does not hold

What "What the table does not hold" above lists, and: any forecast; the subregions and the planning areas (their own tables and notes); a second grid or a second window side by side on one view (the table "Every grid" is the comparison across grids; two windows are two addresses).

### The decisions on the page

`site/app/explore/demand-growth/Decisions.tsx`, drawn at the foot of every view: 16 choices, each with its default and its source on hover. The page computes nothing, so none is editable in place.

| Key | The choice | Default |
|---|---|---|
| `base-year` | growth is measured from 2019 | 2019 |
| `weather` | weather is not removed | as metered |
| `demand-series` | EIA's adjusted demand of the balancing authority; the Lower 48's demand | EIA-930 |
| `hours-used` | an hour is used when held, above zero, within 25 percent of its neighbours' median and inside the range | 25 percent |
| `whole-year` | a year and a month are written at 95 percent of their hours | 95 percent |
| `local-time` | the grid's own clock time | Central, Pacific, Eastern |
| `average-hour` | average demand is the mean of the hours used | the mean, MW |
| `peak-hour` | peak demand is the highest used hour, an hour's average | the hourly average |
| `lower-48-peak` | no peak for the Lower 48 | none |
| `year-so-far` | 1 January to the end of the last whole month, on the same months of 2019 | the header's month |
| `last-whole-year` | a month's or an hour's growth is read at the last whole year | the last whole year |
| `california-hours` | California's hours of November 2023 to 2 December 2025 are read one hour earlier | one hour |
| `areas` | eight areas; a balancing authority is not a state | the seven operators and the Lower 48 |
| `against-sales` | demand at the grid is not sales to customers | EIA's retail sales stated beside it |
| `opening` | the page opens on ERCOT and the whole year's average hour | ERCOT, `avg` |
| `as-written` | every figure is one row, MW whole, percent to two decimals, signed | no arithmetic |

### For the owner's ruling (each with the default taken)

1. A month the newest year already holds (March 2026) shows its MW and no growth, because the table writes a month's growth on the last whole year's row only. Default: left as it is, and said in the decisions.
2. California: CAISO's demand grew 4.45 percent from 2019 to 2025 while California's retail sales fell 2.96 percent. Default: both are stated in the decisions block; no figure changed; the data machine is asked to look at EIA's California demand series.
3. The grey lines under the charts, the sections and the headline numbers, and the freshness line's second sentence, are drawn grey by files every tool or every explorer shares. Default: not changed here.
4. The page compares grids in its table and chart; it has no second window beside the first. Default: not built.
5. PJM's Load Forecast Report is printed "For Public Use" on every page and linked from PJM's public page, while the file's own properties carry a label "Confidential - PJM Personnel Only". Default: its figures are cited.

## Read as its reader (session 7517, 16 November 2026)

Part B of chain 304 read the explorer as an AI lab's energy lead sizing a 300 MW site would (`docs/reviews/demand-growth-read-2026-11-16.md`, 12 rows). This section states what that read added to the page, by the same rules as the section above, which it completes and does not replace. The replication's lines above are as run by session 7508; the line as run after this session is at the end.

### Two figures added, one line changed

- **Figure 3a, the peak window only: the newest year's highest hour so far.** Under the three headlines, one line: `ytd_peak_demand_mw` of G at its newest year, in MW; `ytd_peak_demand_growth_since_2019_pct` of the same year, in percent; and `ytd_peak_demand_mw` of G for 2019, in MW. As drawn for PJM: "The highest hour of 2026 so far (January to October): 162,648 MW, +6.78 percent on the highest hour of the same months of 2019 (152,315 MW)." The line is not drawn where the table holds no such row (the Lower 48, which has no peak). The peak window reads these two variables beside its others; no other window does. The growth is computed from the two MW rows as rule 6 says (the replication recomputes it: 7 more growth figures, 777 in all). Before this, the record PJM set on 2 July 2026 and ERCOT's of 22 July 2026 were in the table and on `/demand`, and not on the explorer.
- **The second headline in the year-so-far window.** The line under it reads "2019, January to October: 91,744 MW", as the first headline's line does; it read "2019: 91,744 MW", which is not PJM's 2019 (91,354 MW over the whole year). The same column of the table "Every grid" is headed "2019, January to October, MW" in that window.
- **Where a forecast is held.** A line at the foot says the table holds no forecast and links the All grids tab of the datacenter cost page (`/cost-of-power?view=allgrids`), whose Headroom column draws ERCOT's firm peak for the coming summers (`ercot_cdr_reserve_margins`), CAISO's forecast peak (`iso_reserve_margin_reports`) and the revision of each operator's FERC Form 714 forecast (`ferc714_forecast_growth`). Its tip says how that tab's demand growth differs from this page's. No figure of those tables is drawn here.

### Three pages, one table

`/demand` reads `site/data/demand_growth.json`: all 24,116 values of that file equal the table's rows as held on 16 November 2026, so the two pages cannot differ on a figure both draw. The All grids tab reads the same file and computes one figure of its own from it: the mean demand of the last twelve months the file holds over the twelve before, each month weighted by its hours (`site/lib/siting.ts`, `demandGrowth`). That is a different period from this page's "on the year before" (`avg_demand_growth_yoy_pct`, one calendar year over the one before), and the two differ for the same grid:

| Grid | This page, 2025 on 2024, percent | All grids, November 2025 to October 2026 on the twelve months before, percent |
|---|---|---|
| ERCOT | +5.57 | +5.21 |
| PJM | +3.73 | +4.04 |
| CAISO | +0.24 | +5.18 |
| MISO | +2.96 | +2.76 |
| SPP | +3.55 | +5.01 |
| NYISO | +0.71 | +0.43 |
| ISO-NE | +1.02 | +2.78 |

The tab's peak of the last whole year (`grid_peak_vs_capacity`) is this table's `peak_demand_mw` of 2025 for all seven grids. `/datacenters` draws no figure of this table.

### California: the batteries' charging inside EIA's demand

Session 7508 found that CAISO's demand here grew 4.45 percent from 2019 to 2025 while California's retail sales fell 2.96 percent. Session 7512 (the read of `/shoulder`) found that EIA-930's demand for California counts the power the grid's batteries take to charge, and CAISO's own supply by fuel does not. This session put the two together, on the rows this machine holds (`replication/demand_growth/california_charging.py`, on `california_rows.csv` beside it):

1. A month's demand by EIA is this table's `avg_demand_mw_mMM` for `eia930:CISO`.
2. A month's charging is, on that month's average day by CAISO's own data (`shoulder_hours_monthly`, `iso:caiso_own`, `avg_battery_mw_hHH`), the sum over the hours whose figure is below zero, sign turned, divided by 24: MW on average. It is held from June 2025 (16 months, to September 2026).
3. A window of months is the mean of its months, each weighted by its days; growth is against the same months of 2019 by EIA; "less the charging" takes the charging off the newer year only. The charging of 2019 is not held: the fleet was 186 MW at the end of 2019 and 15,760 MW in December 2025 (`fleet_mw`).
4. Retail sales are the sum of the window's months (`eia_retail_sales_monthly`, `eia:retail_sales:CA:ALL`), against the same months of 2019.

| Window | Demand, on the same months of 2019 | The charging, MW | Demand less the charging | CAISO's own demand, on EIA's 2019 | Retail sales |
|---|---|---|---|---|---|
| June to December 2025 | +2.81 percent (26,383 to 27,124 MW) | 1,690 | -3.60 percent | -3.25 percent | -2.28 percent |
| January to August 2026 | +10.75 percent (24,282 to 26,893 MW) | 2,114 | +2.05 percent | +2.13 percent | -2.90 percent |

EIA's demand less CAISO's own is the charging to within 300 MW in 14 of the 16 months held. So: in the second half of 2025 the charging is more than all of the growth, and demand without it fell, as sales did, the two 1.3 points apart. In 2026 the charging is 81 percent of the growth and does not close the gap: 5 points are left. Two months carry most of what is left: March (EIA's March 2019 is 19,536 MW, under every later March the table holds by 9.6 percent or more and 11 percent under February and April of 2019, so March 2026 reads +26.56 percent, +15.55 without the charging; a data request of session 7517) and August 2026 (+12.63 percent, +5.10 without the charging). The whole year 2025 cannot be split this way: the charging of January to May 2025 is not held. The page's own hour windows show the same thing from the other side: from 2019 to 2025 CAISO's demand grew 11 to 14 percent at 08:00 to 11:00, when the fleet charges, and fell at 15:00 to 20:00.

The page's figure stays the table's (+4.45 percent): the decisions' line on sales states the charging beside it, with these figures, and the line on the demand series says that California's counts the charging. Which demand California's growth should stand on is the owner's to rule.

### The replication after this session

`replicate.py` writes the new line from this section's words and the second headline's line with its months. As run on 16 November 2026 on the page drawn with the site's own code: "/explore/demand-growth: 35943 of 35943 slots of text on 315 views equal the replication's (3296 distinct checked figures; 777 of 777 growth figures recomputed from the MW rows)". `california_charging.py` prints the two windows above; `tests/test_session7517_demand_growth_read.py` holds the decisions' words to it.
