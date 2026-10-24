# Emissions and carbon intensity: method

Built in session 32 for the site's `/emissions`; extended in session 34 (the other six CO2 columns, intensity from 2018, the monthly table). Four tables:

| Table | Tier | What |
|---|---|---|
| `eia930_all_emissions` | source | EIA's hourly CO2 estimates for EIA-930, per balancing authority |
| `carbon_intensity_hourly` | derived | CO2 per MWh, hourly |
| `carbon_intensity_daily` | derived | CO2 per MWh, daily |
| `carbon_intensity_monthly` | derived | CO2 per MWh, monthly (session 34) |

## Where EIA publishes the estimates

Not in the EIA API v2, and not in the six-month bulk files (both checked in session 31). EIA publishes them only in the Hourly Electric Grid Monitor's per-balancing-authority workbooks, one per BA:

- `https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx`: CISO, ERCO, ISNE, MISO, NYIS, PJM, SWPP;
- `https://www.eia.gov/electricity/gridmonitor/knownissues/xls/Region_US48.xlsx`: the Lower 48.

These are the Grid Monitor's "download data by balancing authority" files. The app builds the path as `electricity/gridmonitor/knownissues/xls/` plus the code plus `.xlsx`, with `Region_` before a region's code.

**The workbooks' sheets:**

- **`Published Hourly Data`:** one row per hour from 2015-07-01. The first column is `BA` (`Region` in the US48 workbook); `UTC time` is the hour's end.
- **The same sheet's CO2 columns,** from 2018-07-01:
  - emission factors: `CO2 Factor: COL / NG / OIL`, in lbs/kWh;
  - `CO2 Emissions: COL / NG / OIL / Other`;
  - `CO2 Emissions Generated`, `Imported`, `Exported` and `Consumed`, in metric tons;
  - EIA's own intensities: `CO2 Emissions Intensity for Generated / Consumed Electricity`, in lbs/kWh.
- **Other sheets:** daily data, charts, known data issues, thresholds, and a `Notes` sheet that defines every column.

**EIA's method,** from the workbooks' `Notes` and "About the EIA-930 data" (`https://www.eia.gov/electricity/gridmonitor/about`):

- **Generated CO2** is the positive generation by fuel (coal, natural gas, petroleum, other) times an emission factor per fuel and BA, in lbs/kWh. The factor selection is described in EIA's FAQ: `https://www.eia.gov/tools/faqs/faq.php?id=74&t=11`.
- **Factors.** A BA with too little history gets a US factor; a region's factors are a weighted average of its BAs'.
- **Negative generation** gets no emissions.
- **Consumed CO2** is generated plus imported minus exported.
- EIA calls the data preliminary, "as-is".

## eia930_all_emissions (source)

`warehouse/connectors/eia930_emissions.py`, partition column `ba` (ciso, erco, isne, miso, nyis, pjm, swpp, us48), unit `tCO2` (metric tons of CO2, as EIA states them). Eight variables:

| Variable | EIA column | Since |
|---|---|---|
| `co2_emissions_generated` | `CO2 Emissions Generated`: all sources in the BA | session 32 |
| `co2_emissions_consumed` | `CO2 Emissions Consumed`: generated plus imported minus exported | session 32 |
| `co2_emissions_coal` | `CO2 Emissions: COL` | session 34 |
| `co2_emissions_natural_gas` | `CO2 Emissions: NG` | session 34 |
| `co2_emissions_oil` | `CO2 Emissions: OIL` | session 34 |
| `co2_emissions_other` | `CO2 Emissions: Other` | session 34 |
| `co2_emissions_imported` | `CO2 Emissions Imported` | session 34 |
| `co2_emissions_exported` | `CO2 Emissions Exported` | session 34 |

**Session 32 wrote two, session 34 the other six.** Session 32's ceiling (1.2 million new rows) held two. Session 34 added the six from the same saved workbooks, with no new download (`--from-raw`), under a ceiling of 4 million.

- **A column EIA leaves empty for a BA is not a variable of it,** as in `eia930.py`. ERCOT's oil column is empty in every hour, so ERCOT has no `co2_emissions_oil`. MISO's has values in 24 hours only, never a whole day that could be written.
- Net imported CO2 is `co2_emissions_imported` minus `co2_emissions_exported`, which equals consumed minus generated.

**Rules:**

- **Time:** `ts_utc` is EIA's UTC time minus one hour, the hour's start, as in every EIA-930 table.
- **Values:** EIA's floats, not rounded.
- **Completeness:** per UTC day, the rule of EIA-930 generation (session 6 ruling a, per day since sessions 13 and 16).
  - **The core pair** (generated, consumed): a day is written only when both have all 24 hours.
  - **The six others:** each is written for a day only when the core pair is complete that day and the variable has all 24 hours itself. Otherwise it is left out for that day alone, as a per-fuel generation series is.
  - Every day or variable-day left out is recorded as a gap in `warehouse/metadata/run_status.csv`. Nothing is filled.
  - Session 34 chose this over requiring all six together. Together, 15% of CAISO's days and every ERCOT and MISO day would have been lost, because EIA leaves the coal or oil column blank on them.
- **Raw and resume.**
  - Every workbook is saved under `warehouse/raw/eia930_emissions/<run_id>/` with its URL, Last-Modified and sha256.
  - Before downloading, the connector asks for the Last-Modified and reuses a saved copy with the same date, so an interrupted pull resumes and no file is downloaded twice.
  - The workbooks are read one at a time in openpyxl's streaming mode; the table is merged and written as a stream.
- **One pass (session 34).** Each workbook is read once. The columns the ERW uses are written to an extract beside the raw files, `warehouse/raw/eia930_emissions/<run_id>/<ba>_hours.csv`: the hour's start, EIA's Demand and Net generation, and the eight CO2 columns, as EIA wrote them, every hour from 2018-07-01.
  - The table's rows are built from the extract.
  - `carbon_intensity.py` takes its denominators from it.
  - `--from-extract` rebuilds rows from the newest extracts without opening a workbook.
- **Daily refresh.** The daily run reads the newest workbooks and merges their last 3 days on (entity, variable, ts_utc), all eight variables.

## carbon_intensity_hourly, carbon_intensity_daily and carbon_intensity_monthly (derived)

`warehouse/derived/carbon_intensity.py`, partition column `ba`, unit `kgCO2/MWh`.

| Variable | Formula |
|---|---|
| `intensity_generation` | `co2_emissions_generated x 1000 / Net generation` (the same workbook row): the CO2 of the power made in the BA, per MWh made |
| `intensity_demand` | `co2_emissions_consumed x 1000 / Demand` (the same workbook row): the CO2 of the power used in the BA, per MWh of demand |

- **The numerators** are `eia930_all_emissions`, the warehouse table.
- **The denominators, since session 34,** are the Demand and Net generation columns of the same EIA workbooks (sheet `Published Hourly Data`), from the emissions connector's extracts (the newest per BA). Session 32 used `eia930_all_generation` and `eia930_all_demand`, which keep about 30 days.
- **Which hours:** an hour is written when its CO2 value and a denominator above zero are both present.
- **Daily values** are energy-weighted, the day's CO2 over the day's MWh, over UTC days with all 24 hours.
- **Monthly values** (session 34) are the same over UTC calendar months whose every day is complete. A month with a missing day is left out, so SPP, whose file often leaves one CO2 column empty, has 45 months, and US48 has 97.
- **All three tables are rewritten whole each run.** If a BA has no extract, the run fails and writes nothing.

**Why the two differ: trade.** Demand is net generation minus net interchange. A BA that imports power made with more CO2 per MWh than its own has a higher demand intensity than generation intensity; one that exports its higher-CO2 power has the reverse. Without trade the two would be the same.

**Reach.** From 2018-07-02, like the emissions (session 34; before it, about 30 days). Session 34's rebuild: 1,119,244 hourly rows, 46,624 daily and 1,264 monthly.

**In the site's database (the live set).** The daily and the monthly table are there as `warehouse/supabase/live_set.yaml` says (the last 100 days; every month). The hourly table is there for the last 430 days, hour by hour, both variables, all eight balancing authorities (session 245, the owner's ruling of 12 October 2026: at least 13 months; it was 35 days). 430 days hold 13 whole calendar months and the month under way, whatever the day and EIA's lag of a few days. With 430 days there, a read of the whole table since a date, in the key's order, was answered from the primary key and took about a second a page, and a cold database cancelled it at the three seconds the site's key is allowed (the emissions page drew "no data" in two blocks, and three landings' route checks failed on it on 13 October 2026). Migration 032 (session 250) gives that read an index of its own, `series_carbon_hourly_since`: 22 ms. A page that reads this table since a date for one balancing authority was never slow (6 ms). The whole history from 2018 is in the CSV, the archive and the Redivis draft.

**The check against session 32's version.** Each run also computes the intensity with the warehouse's `eia930_all_generation` and `eia930_all_demand` as denominators, over the hours those tables hold. It writes the difference in the tables' header and the run log, not as rows. Session 34's run covered 2026-08-26 to 2026-09-27:

- **Identical** for CAISO, MISO, PJM and SPP, both variables.
- **ERCOT and NYISO, generation:** one day differs, 2026-09-03 05:00 to 2026-09-04 04:00 UTC (24 hours), by up to 22.7 and 38.2 kgCO2/MWh. EIA revised net generation for that day after the warehouse's rolling pull took it; the workbooks, downloaded 2026-09-29, carry the revision.
- **ISO-NE:** one hour.
- **US48:** most hours, by a mean of 0.33 kgCO2/MWh (generation) and 0.26 (demand), at most 2.3 and 6.2.
- **Over all BAs:** mean absolute difference 0.157 kgCO2/MWh for generation and 0.034 for demand.

**Against EIA's own intensities.** EIA's workbooks divide by positive generation and by "consumed electricity" (generation by source plus imports minus exports), in lbs/kWh. These divide by the reported net generation and demand, in kg/MWh (1 lb/kWh = 453.59237 kg/MWh), so the two can differ slightly. EIA's intensity columns are not in the warehouse.

## On /emissions

Three blocks, and nothing is computed on the page:

- the latest hour of `carbon_intensity_hourly` per ISO, ranked;
- the last 24 hours per ISO, as one chart;
- since session 34, the monthly intensity of generation since 2018 per ISO (`carbon_intensity_monthly`), as one chart, with each ISO's first and latest complete month in figures.

## On the Grid tool's Clean tab, keyed (chain 107, session 1415)

Since session 237, `/emissions` redirects to the Clean tab of the Grid tool (`/grid?view=clean`), which draws the three blocks above from `site/components/grid/Emissions.tsx`, the grid in view marked in the ranking. Session 1151 keyed "The last 24 hours" (the table under its chart, `grid_clean24_<grid>`, defined in `grid_network.md`). The two other blocks are now named panels, every figure keyed, each with its file, its anchor and its method line, and the held rule written for all three:

- **"Carbon intensity now, ranked"** (`data-grid-panel="grid_carbonrank_<grid>"`, anchor `#carbon-now`): each ISO's latest hour of `carbon_intensity_hourly`'s `intensity_generation` and the same hour's `intensity_demand`, keyed `series|carbon_intensity_hourly|<entity>|<variable>|<ts_utc>` as the block has written them since this page's first version: 14 figures, each with its table, entity, variable and hour on hover (`site/lib/gridKeys.ts` `carbonTip`). The order is the lowest intensity of generation first, a tie in the order CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP (`carbonRanked`: the code that stood in the component, moved as it stood). The rank and the hour are words.
- **"Monthly since 2018"** (`grid_carbonmonth_<grid>`, anchor `#carbon-monthly`): each ISO's first and latest complete month of `carbon_intensity_monthly`'s `intensity_generation`, keyed `series|carbon_intensity_monthly|<entity>|intensity_generation|<month>` as before, the month on hover (`carbonMonthEnds`, the months the chart leaves out not counted); and the two figures of the chart's note, which had no key: the months left out of the chart, `fmt|n0|filecalc|carbon_left_out_n|carbon_left_out.json|intensity_generation` (`site/lib/mixViewCalc.ts` `leftOutCount` on the committed `site/data/carbon_left_out.json`: the length of the list of months the note writes after it, 13 today), and California's hours in a row without hydro, `fmt|n0|file|carbon_left_out.json|hydro_gap.hours` (the file's own value, 7,869). Both are checked against the committed file alone: no live-set row holds them. 16 figures.
- **The charts.** Both answer a hover with the period and each ISO's value in kg CO2/MWh: the last 24 hours with the hour (its start, UTC), the monthly chart with the UTC month (`x="month"`, session 416), through the shared chart's own card (`site/components/TimeChart.tsx`), and as a table under "Chart | Table". Their points are not keyed, as no chart of the tool is.
- **Files.** `erw_grid_carbonrank_<grid>.csv` (rank, ISO, hour, the two intensities) and `erw_grid_carbonmonth_<grid>.csv` (each ISO's first and latest month with their intensities; the note's two figures as `Figure:` lines of its header), written by `site/components/grid/PanelFile.tsx` from the cells the blocks draw.
- **Method.** One line under each block, "Method: the Clean tab's carbon blocks, keyed", which opens this section (`METHOD_EMISSIONS_BLOCKS` in `site/lib/gridAnchors.ts`, beside `EMISSIONS_ANCHOR`), drawn also when the read fails.
- **A failed read.** Each block's place, under its panel's name, says "no data for ...", with the reason (the words the block has had since session 32; session 1181's rule), and draws no figure: `site/scripts/test-grid-failed-reads.mjs` fails `carbon_intensity_hourly` and `carbon_intensity_monthly` three ways (a timeout past the retries, an HTTP 500, an empty answer).
- **Held grids.** Both tables are public in every status file (`site/data/license_status.json`). Should one become held, `site/lib/gridHeld.ts` `heldCarbonRow` (the rule of session 1403's `heldCarbon`, by entity) gives a held ISO's place "license needed" with the publishers on hover in all three blocks: not ranked, its line not drawn in either chart, its cells in the files "license needed". None is held today, so no figure moved.

**The count, and no figure moved.** On every Clean page (the seven ISOs whatever the grid in view): 30 keys in the two blocks, 2 more than the 28 they wrote. `site/scripts/same-figures.mjs` drew `/grid?grid=ercot&view=clean`, `caiso`, `us48` and `isone` with the code before and after on the same live answers (24 October 2026): on each page the list of figures before is kept whole and in order in the list after, the two keys of the note added, no held figure or error, and two panel names more. check-values reads no row for the two added keys (the committed file).

Decisions (chain 107, session 1415):

- **The section is in this note**, not in `grid_network.md`: no note is named for `carbon_intensity_*`, and this one defines the three tables and already held the page's section ("On /emissions").
- **The count of months left out is a `filecalc|` key** (`carbon_left_out_n`), not words: it is a number the page writes; the function is the length of the list the page writes after it, and it is named in `generation_mix_hourly.md` too, where every function of that kind is named.
- **The hours without hydro is a `file|` key**: it is the file's own value.
- **No key moved and no kind was added**: the ranked and monthly figures keep the keys they had and gain a source on hover (with the dotted underline the last 24 hours' figures have had since session 1151); the ranked table's note gained the sentence the last 24 hours' note has ("Hover a figure for its table, entity and hour.").
- **One method line for both blocks**, outside `GRID_ANCHOR` and `GRID_METHOD` (pinned by sessions 1183 and 1184), as sessions 1402 to 1414 did; **the anchors take no grid**: each block is drawn once a page.
- **The held rule covers the last 24 hours too**, the third block of the file, so that no held ISO's rows would be drawn anywhere on the tab.
- **The offline tests hold `carbon_intensity_monthly` now** (`site/scripts/fixtures/carbon_monthly.json`: its 636 rows of `intensity_generation`, read once with the anon key at 09:17 UTC on 24 October 2026), in the render stand-in and in `test-grid-files.mjs`: the older "How clean" block draws its four figures there too (the render case `view_clean`: 4 figures, the ranked table's 14 now its own panel's).
