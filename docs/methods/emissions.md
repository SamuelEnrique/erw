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

## carbon_intensity_hourly and carbon_intensity_daily (derived)

`warehouse/derived/carbon_intensity.py`, partition column `ba`, unit `kgCO2/MWh`.

| Variable | Formula |
|---|---|
| `intensity_generation` | `co2_emissions_generated x 1000 / net_generation_mw` (`eia930_all_generation`): the CO2 of the power made in the BA, per MWh made |
| `intensity_demand` | `co2_emissions_consumed x 1000 / demand_mw` (`eia930_all_demand`): the CO2 of the power used in the BA, per MWh of demand |

- **Which hours:** an hour is written when its CO2 value and a denominator above zero are both in the warehouse.
- **Daily values** are energy-weighted, the day's CO2 over the day's MWh, over UTC days with all 24 hours.

**Why the two differ: trade.** Demand is net generation minus net interchange. A BA that imports power made with more CO2 per MWh than its own has a higher demand intensity than generation intensity; one that exports its higher-CO2 power has the reverse. Without trade the two would be the same.

**Reach.** `eia930_all_generation` and `eia930_all_demand` keep about 30 days, so the intensity tables reach back only that far, while the emissions go back to 2018-07-01. A longer intensity history needs a longer generation and demand history, not a new emissions pull.

**Against EIA's own intensities.** EIA's workbooks divide by positive generation and by "consumed electricity" (generation by source plus imports minus exports), in lbs/kWh. These divide by the reported net generation and demand, in kg/MWh (1 lb/kWh = 453.59237 kg/MWh), so the two can differ slightly. EIA's intensity columns are not in the warehouse.

## On /emissions

Two blocks, and nothing is computed on the page:

- the latest hour of `carbon_intensity_hourly` per ISO, ranked;
- the last 24 hours per ISO, as one chart.
