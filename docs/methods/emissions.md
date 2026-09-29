# Emissions and carbon intensity: method

Built in session 32 for the site's `/emissions`. Three tables:

| Table | Tier | What |
|---|---|---|
| `eia930_all_emissions` | source | EIA's hourly CO2 estimates for EIA-930, per balancing authority |
| `carbon_intensity_hourly` | derived | CO2 per MWh, hourly |
| `carbon_intensity_daily` | derived | CO2 per MWh, daily |

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

`warehouse/connectors/eia930_emissions.py`, partition column `ba` (ciso, erco, isne, miso, nyis, pjm, swpp, us48), unit `tCO2` (metric tons of CO2, as EIA states them). Two variables:

| Variable | EIA column |
|---|---|
| `co2_emissions_generated` | `CO2 Emissions Generated`: all sources in the BA |
| `co2_emissions_consumed` | `CO2 Emissions Consumed`: generated plus imported minus exported |

**Why only two.** Session 32's ceiling was 1.2 million new rows. Eight BAs from 2018-07-01 are about 72,000 hours each, so two variables make about 1.16 million rows; three would not fit.

- The by-fuel, imported and exported columns are not in the table.
- They are in the saved raw workbooks (`warehouse/raw/eia930_emissions/`), so adding them needs no new pull.
- Net imported CO2 is consumed minus generated.

**Rules:**

- **Time:** `ts_utc` is EIA's UTC time minus one hour, the hour's start, as in every EIA-930 table.
- **Values:** EIA's floats, not rounded.
- **Completeness:** per UTC day, as session 16's rule for EIA-930 generation. A day is written only when both variables have all 24 hours; otherwise it is left out and recorded as a gap in `warehouse/metadata/run_status.csv`.
- **Raw and resume.**
  - Every workbook is saved under `warehouse/raw/eia930_emissions/<run_id>/` with its URL, Last-Modified and sha256.
  - Before downloading, the connector asks for the Last-Modified and reuses a saved copy with the same date, so an interrupted pull resumes and no file is downloaded twice.
  - The workbooks are read one at a time in openpyxl's streaming mode; the table is merged and written as a stream.
- **Daily refresh.** The daily run reads the newest workbooks and merges their last 3 days on (entity, variable, ts_utc).

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
