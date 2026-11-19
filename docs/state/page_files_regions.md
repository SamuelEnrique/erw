# Page files of the whole country: the contract (chain 501, step B1)

Written by session 8000 (chain 501, lab-desktop) on 19 November 2026 for the three windows that code against these files: the desktop's second window (chain 502), the old laptop (chain 503) and the personal laptop (chain 504). Every file named here is new; no existing page file changes. A shape that has to change is changed in this file first, with a dated line under "Changes" saying what moved.

## Common rules

- **Folder:** `site/data/regions/`. File names use the lowercase EIA code (`demand/ten.json`, `demand/ba/tva.json`); inside a file every code is EIA's, uppercase (`TEN`, `TVA`).
- **Codes:** the thirteen regions of the lower 48 as EIA's EIA-930 names them: `CAL` California, `CAR` Carolinas, `CENT` Central, `FLA` Florida, `MIDA` Mid-Atlantic, `MIDW` Midwest, `NE` New England, `NW` Northwest, `NY` New York, `SE` Southeast, `SW` Southwest, `TEN` Tennessee, `TEX` Texas. Balancing authorities by their EIA-930 code (`TVA`, `PJM`, `BPAT`). The seven grids of the existing pages by their balancing authority code: `ERCO`, `CISO`, `PJM`, `MISO`, `SWPP`, `NYIS`, `ISNE`. Neighbours outside the lower 48 in trade files: `CAN` Canada, `MEX` Mexico.
- **Units:** power MW (EIA's MWh in an hour), energy MWh, shares and growth percent (`_pct`), temperatures degrees Fahrenheit. A key's unit is its suffix: `_mw`, `_mwh`, `_pct`, `_f`, `_hours`, `_days`.
- **Time:** `ts` and `_at` values are the hour's start in UTC (`2025-08-01T19:00:00Z`). Days, months and years are local to the region's or authority's time zone (`tz`, an IANA name), as in the seven grids' files; trade months are EIA's Eastern months, as in `ba_supply_monthly`.
- **Missing:** a figure that is not held is absent from an object, or `null` in an array at its position. Nothing is filled, interpolated or scaled.
- **Every file** carries `built` (UTC time of the build), `tables` (the warehouse tables it reads), `method` (the method note's path under `docs/methods/`) and `license` (`public` for every file here: EIA, NOAA, Census Bureau and HIFLD data are public domain).
- **Hourly arrays** are columnar: one `hours` object `{ "start": "<first ts>", "step_hours": 1, "n": <count> }` and arrays of `n` values, so the hour of position `i` is `start + i` hours.
- **Sources of generation** (the same eight as `site/data/mix/*.json`, in this order): `natural_gas`, `coal`, `nuclear`, `wind`, `solar`, `hydro`, `storage`, `other`. `hydro` is EIA's hydropower excluding pumped storage plus pumped storage; `storage` is battery, other and unknown energy storage (negative while charging); `other` is petroleum, geothermal, other and unknown fuel sources. Solar and wind include EIA's "with integrated battery storage" columns.

## 1. `ba_boundaries.json` (step B2)

A GeoJSON FeatureCollection, longitude and latitude in degrees (WGS 84), coordinates rounded to 3 decimals, simplified for the web; under 1.5 MB.

| Key | Unit or form | Meaning |
|---|---|---|
| `type` | `"FeatureCollection"` | |
| `built`, `tables`, `method`, `license` | | as above; `tables` is `["ba_boundaries"]` |
| `source`, `source_url`, `retrieved_at` | text, URL, UTC | the publisher's layer as read |
| `simplify_tolerance_deg` | degrees | the tolerance of the simplification |
| `bas_without_polygon` | list of codes | balancing authorities of EIA-930 with no polygon in the layer |
| `polygons_without_ba` | list of `{ "id", "name" }` | polygons of the layer that match no EIA-930 code |
| `features[]` | GeoJSON Feature | one a balancing authority; `geometry` Polygon or MultiPolygon |
| `features[].properties.code` | text | the EIA-930 code |
| `features[].properties.name` | text | EIA's name of the authority |
| `features[].properties.region` | text | its EIA region code |
| `features[].properties.source_id` | text | the polygon's own identifier in the layer |
| `features[].properties.area_km2` | km2 | the polygon's area before simplification |

Sample of `features[].properties` (TVA, from the first build; its geometry a MultiPolygon). On main since `792dbb50d` (19 November 2026): 67 features, `bas_without_polygon` BHBA, GLHB, HGMA, SIKE, SWPW and WAUE, `polygons_without_ba` four (Chugach, Hawaiian Electric, New Harquahala, Gridforce South), tolerance 0.01 degrees, 979,100 bytes.

```json
{"code": "TVA", "name": "Tennessee Valley Authority", "region": "TEN", "source_id": "18642", "area_km2": 200530.8}
```

## 2. `index.json` (step B3)

| Key | Unit or form | Meaning |
|---|---|---|
| `built`, `tables`, `method`, `license` | | as above |
| `regions[]` | object | one a region, in the order of the codes above |
| `regions[].code`, `.name` | text | EIA's code and name |
| `regions[].tz` | IANA name | the time zone its days are counted in (the zone of most of its demand) |
| `regions[].bas` | list of codes | the balancing authorities EIA places in it (active or retired since July 2018) |
| `regions[].grids` | list of codes | which of the seven grids are among its authorities |
| `regions[].first_hour`, `.last_hour` | UTC | the first and last hour of demand held for it |
| `bas[]` | object | one a balancing authority of the lower 48 that EIA-930 lists |
| `bas[].code`, `.name` | text | EIA's code and name |
| `bas[].region` | text | its region code |
| `bas[].tz` | IANA name | from EIA's time zone (Eastern, Central, Mountain, Arizona, Pacific) |
| `bas[].grid` | code or `null` | the seven grid it is, when it is one |
| `bas[].region_grids` | list of codes | the seven grids in its region (where it sits; not a market membership) |
| `bas[].generation_only` | true or false | EIA's "Generation Only BA" (it files no demand) |
| `bas[].active` | true or false | EIA's "Active BA" |
| `bas[].retired` | date or `null` | EIA's retirement date |
| `bas[].first_hour`, `.last_hour` | UTC | the first and last hour held (demand, or net generation for a generation-only authority) |
| `bas[].files` | list | which of `demand`, `mix` files exist for it |

Sample object of `bas[]` (TVA, from EIA's reference tables and `eia930_ba_demand_hourly`):

```json
{"code": "TVA", "name": "Tennessee Valley Authority", "region": "TEN", "tz": "America/Chicago", "grid": null, "region_grids": [], "generation_only": false, "active": true, "retired": null, "first_hour": "2018-07-01T05:00:00Z", "last_hour": "2026-11-17T05:00:00Z", "files": ["demand"]}
```

## 3. `demand/<region>.json` and `demand/ba/<code>.json` (step B4)

The measures and names of `site/data/demand_growth.json` (one area object) and `site/data/demand_weather.json` (one grid object), so the same components read them, and a daily series.

| Key | Unit or form | Meaning |
|---|---|---|
| `built`, `tables`, `method`, `license` | | as above |
| `code`, `name`, `tz`, `level` | | `level` is `region` or `ba` |
| `basis` | text | how the hourly demand was formed: `region_sum` (the sum of the region's balancing authorities that file demand, written for an hour only when every one of them holds it; generation-only authorities file none) or `ba` |
| `bas_summed` | list of codes | the authorities in the sum (regions only) |
| `screened` | `{ "blank", "not_positive", "jumps" }` hours | as `demand_growth.json`'s `screened` |
| `daily.days` | list of local dates | every local day from the first held to the last |
| `daily.demand_mwh` | MWh | the day's demand, only for a day with all its hours used, else `null` |
| `daily.peak_mw` | MW | the day's highest used hour, `null` as above |
| `daily.peak_at` | UTC | that hour's start |
| `daily.hours` | hours | how many of the day's hours were used |
| `growth` | object | `{ "base": 2019, "last_year", "ytd_through", "years": {...}, "at": {...} }`: the area object of `demand_growth.json`, its keys unchanged (`avg_demand_mw`, `peak_demand_mw`, `hours_used`, `avg_demand_mw_hHH`, `avg_demand_mw_mMM`, `avg_demand_mw_mMM_hHH`, `ytd_*`, `*_growth_since_2019_pct`, `avg_demand_growth_yoy_pct`, `growth_mw_*`, `growth_pct_*`, `*_growth_since_2019_mw`) |
| `weather` | object or absent | regions only: the grid object of `demand_weather.json`, its keys unchanged (`fit`, `holdout`, `years` with `energy`, `summer_peak`, `winter_peak`, `overnight_min`, each `actual`, `expected`, `growth_pct`, `weather_pct`, `unexplained_pct`, `uncertainty_pct`, `finding`), plus `weather_table`: `region_weather_hourly` |
| `alike` | object or absent | for a region that covers nearly the ground of one of the seven grids (`TEX` and `ERCO`, `NY` and `NYIS`, `NE` and `ISNE`, `MIDA` and `PJM`): `{ "grid", "years": { "<year>": { "region_avg_demand_mw", "grid_avg_demand_mw", "difference_pct" } }, "why" }`, both figures standing |

Sample objects (TEN, read from `eia930_region_hourly` by session 8000 with `demand_growth.summarize`):

```json
{"daily": {"days": ["2025-08-01"], "demand_mwh": [527352.0], "peak_mw": [25820.0], "peak_at": ["2025-08-01T19:00:00Z"], "hours": [24]}}
```

```json
{"growth": {"years": {"2025": {"avg_demand_mw": 19490.4, "hours_used": 8760, "hours_in_year": 8760, "peak_demand_mw": 35086.0, "avg_demand_mw_m07": 23739.3, "ytd_avg_demand_mw": 19630.7, "ytd_peak_demand_mw": 35086.0, "avg_demand_growth_since_2019_pct": 7.15, "peak_demand_growth_since_2019_pct": 18.66, "avg_demand_growth_yoy_pct": 3.56, "avg_demand_growth_since_2019_mw": 1300.9, "peak_demand_growth_since_2019_mw": 5518.0}}, "at": {"2025": {"peak_demand_mw": "2025-01-22T13:00:00Z"}}, "ytd_through": "2026-10"}}
```

The `weather` sample is the shape of `demand_weather.json`'s `grids.ERCO` (keys listed above); the region's own figures are written with its first build.

## 4. `mix/<region>.json` (step B5)

The form of `site/data/mix/*.json`, keys unchanged, plus the newest 35 days by hour.

| Key | Unit or form | Meaning |
|---|---|---|
| `grid`, `name`, `tz`, `built`, `join` (`null`), `first`, `upto` | | as `mix/*.json`; `grid` is the lowercase region code |
| `tables`, `method`, `license` | | as above |
| `sources` | list | the eight sources, in order |
| `months["YYYY-MM"].avg.<source>` | 24 MW values | the mean over the month's held days of each local hour |
| `months[...].avg.demand`, `.avg.net_generation` | 24 MW values | the same for demand and net generation |
| `months[...].<source>_mwh`, `.<source>_share_pct` | MWh, percent | the month's energy by source and its share of net generation |
| `months[...].net_generation_mwh`, `.days_held`, `.days_in_month`, `.side` (`"eia930"`) | | as `mix/*.json` |
| `years["YYYY"].avg.<source>` | 24 MW values | as `mix/*.json`'s `years` |
| `hourly.hours` | `{ "start", "step_hours", "n" }` | the newest 35 local days |
| `hourly.<source>`, `hourly.demand`, `hourly.net_generation`, `hourly.net_imports` | MW arrays | by hour; `net_imports` is total interchange with its sign turned (positive when the region imports) |

An hour is held when every balancing authority of the region that files net generation holds it and the sources add up to the net generation within 5 percent (the rule of `mix_profile.hours_of`); a month is written when at least 90 percent of its days are complete.

Generation by source comes from the new table `eia930_region_fuel_hourly` (it is not in `eia930_ba_supply_hourly`, which holds net generation and total interchange only; the new table reads the same saved six-month files, whose source columns chain 401 did not keep). `storage` is absent (null) before July 2024, when EIA's files have no storage columns.

Sample of `months["2025-08"]` without `avg` (TEN, first build); `avg.nuclear` begins `[7750.8, 7764.7, 7775.6, ...]`:

```json
{"side": "eia930", "natural_gas_mwh": 5169263.0, "natural_gas_share_pct": 34.45, "coal_mwh": 2386824.0, "coal_share_pct": 15.9, "nuclear_mwh": 5813603.0, "nuclear_share_pct": 38.74, "wind_mwh": 0.0, "wind_share_pct": 0.0, "solar_mwh": 302084.0, "solar_share_pct": 2.01, "hydro_mwh": 1311897.0, "hydro_share_pct": 8.74, "storage_mwh": 0.0, "storage_share_pct": 0.0, "other_mwh": 23102.0, "other_share_pct": 0.15, "net_generation_mwh": 15006773.0, "days_held": 31.0, "days_in_month": 31.0}
```

## 5. `trade/<region>.json` (step B6)

| Key | Unit or form | Meaning |
|---|---|---|
| `built`, `tables`, `method`, `license`, `code`, `name` | | as above; `tables` is `["eia930_region_pair_hourly"]` |
| `months` | list of `YYYY-MM` | EIA's Eastern months from 2018-07 |
| `net_imports_mwh` | MWh array | the region's net imports from all its neighbours, from its own side's reports, positive when it imports; `null` for a month with any neighbour short of half its hours |
| `neighbors.<code>.net_imports_mwh` | MWh array | net imports from that neighbour, the region's own report (sign turned so positive is an import) |
| `neighbors.<code>.their_report_mwh` | MWh array | the same flow as the neighbour reported it, same sign |
| `neighbors.<code>.gap_mwh` | MWh array | own report less theirs, over the hours both reported |
| `neighbors.<code>.hours_own`, `.hours_their`, `.hours_both` | hours arrays | the hours each side held |

Sample (CAR from the Southeast, August 2025, from `eia930_region_pair_hourly` row `CAR-SE`, whose value is power from CAR to SE: CAR imported):

```json
{"months": ["2025-08"], "neighbors": {"SE": {"net_imports_mwh": [501753.0], "their_report_mwh": [506389.0], "gap_mwh": [-2226.0], "hours_own": [744], "hours_their": [720], "hours_both": [720]}}}
```

(The pair table's `x_gap` is the first side less the second, 2,226 MWh over the 720 hours both held; turned to CAR's import sign it is -2,226.)

## 6. `events/<event>.json` (step B7)

One file for each of the nine events of `/events`, named by its event code (`uri_2021`, `covid_2020`, `caiso_heat_2020`, `caiso_heat_2022`, `elliott_2022`, `ercot_heat_2023`, `cold_2025`, `east_heat_2025`, `cold_2026`), the window and baseline days those pages already use (`event_window_daily` and `docs/methods/events.md`).

| Key | Unit or form | Meaning |
|---|---|---|
| `built`, `tables`, `method`, `license` | | as above |
| `event`, `title`, `start`, `end` | | the event code, the page's title, the window's first and last local day |
| `baseline` | text and list | how the baseline is formed (`same weekdays 364 and 728 days earlier`, or the event's own rule) and `baseline_offsets_days` |
| `hours` | `{ "start", "step_hours", "n" }` | every hour of the window (UTC) |
| `regions.<code>.demand_mw`, `.net_generation_mw`, `.net_imports_mw` | MW arrays | the region's hour; `net_imports_mw` positive when it imports |
| `regions.<code>.gen.<source>` | MW arrays | generation by source |
| `regions.<code>.baseline.<same keys>` | MW arrays | for each hour of the window, the mean of the same hour at each baseline offset that holds it |
| `pairs.<A-B>.flow_mw` | MW array | power from A to B (A before B by EIA's code), the first side's report where held, else the second's |
| `pairs.<A-B>.baseline_mw` | MW array | the baseline as above |

Values are whole megawatts. Sample (Uri, the 201st hour of the window): `hours` `{"start": "2021-02-07T05:00:00Z", "step_hours": 1, "n": 435}`, `baseline` "the same calendar days of 2019 and 2020", Texas's `demand_mw` 51402 against `baseline.demand_mw` 40754, `gen.natural_gas` 33203, and `pairs["CENT-TEX"].flow_mw` 823.

## 7. `trade_matrix.json` (step C4)

| Key | Unit or form | Meaning |
|---|---|---|
| `built`, `tables`, `method`, `license` | | `tables`: `interchange_pair_monthly`, `ba_trade_partners` |
| `years` | list | calendar years held |
| `regions` | list of codes | the thirteen and `CAN`, `MEX` |
| `region_pairs[]` | object | `{ "a", "b", "year", "a_report_mwh", "b_report_mwh", "mean_mwh", "gap_mwh", "direction" }`: power from a to b over the year by each side's report (sign: positive from a to b), their mean, a's less b's, and `a_to_b` or `b_to_a` by the mean |
| `ba_pairs[]` | object | the same for each pair of balancing authorities |
| `partners.<BA>.<year>` | object | `{ "by_gross": [codes], "by_net": [codes], "net_import_share_of_demand_pct" }` from `ba_trade_partners` |

Samples (first build): the Carolinas and the Southeast in 2025, and TVA's partners in 2025:

```json
{"a": "CAR", "b": "SE", "year": 2025, "a_report_mwh": -9183611.0, "b_report_mwh": -9270277.0, "mean_mwh": -9159008.5, "gap_mwh": 14073.0, "hours_a": 8662, "hours_b": 8713, "hours_both": 8616, "direction": "b_to_a"}
```

```json
{"by_gross": ["MISO", "PJM", "SOCO", "LGEE", "AECI", "DUK", "CPLW"], "by_net": ["MISO", "PJM", "SOCO", "LGEE", "AECI", "DUK", "CPLW"], "net_import_share_of_demand_pct": 4.868}
```

## 8. `site/data/resources/<layer>.json` (step D1)

Added with the layers of step D1; see the dated line under "Changes".

## 9. `site/data/industry.json` (step D2)

Not under `regions/`: one file for the page "Energy use by industry". Method: `docs/methods/industry_page.md`.

| Key | Unit or form | Meaning |
|---|---|---|
| `built`, `tables`, `method`, `license`, `sources` | | as above; `sources` names each part's publication |
| `monthly.months` | list of `YYYY-MM` | from 1973-01 |
| `monthly.by_source.<key>` | TBtu array | the industrial sector by source (Monthly Energy Review, Table 2.4): `total`, `end_use_total`, `coal`, `natural_gas`, `petroleum`, `renewables`, `electricity_retail_sales`, `electrical_system_losses`; `monthly.labels` gives each in words |
| `industries.industries.<naics>` | object | MECS 2022: `naics`, `name`, `rank_us_total` (three-digit industries), `by_region.<us, northeast, midwest, south, west>.<fuel>` TBtu (fuels: `total`, `net_electricity`, `natural_gas`, `coal`, `coke_and_breeze`, `residual_fuel_oil`, `distillate_fuel_oil`, `hgl`, `hydrogen`, `other`), `electricity_mwh.<region>.<component>` MWh |
| `industries.ranked_3_digit` | list | three-digit NAICS codes by 2022 total, largest first |
| `states_annual.years` | list | 1990 to 2024 |
| `states_annual.states.<ST>.consumption_tbtu.<source>` | TBtu array | SEDS: `total`, `end_use_total`, `coal`, `natural_gas`, `petroleum`, `electricity`, `renewables`, `wood_and_waste`, `hgl`, `distillate_fuel_oil`, `residual_fuel_oil`, `petroleum_coke`, `electrical_system_losses` (`US` is the nation) |
| `states_annual.states.<ST>.expenditures_usd.<source>` | USD array | `total`, `coal`, `petroleum`, `natural_gas`, `electricity` (nominal) |
| `states_annual.states.<ST>.price_usd_per_mmbtu` | USD/MMBtu array | the total average price |
| `electricity_sales_monthly.months`, `.states.<ST>` | MWh arrays | electricity sold to industrial customers, from 2001-01 (EIA-861M; `US` the nation) |
| `outlook` | object | AEO2026 projections: `release`, `years`, `cases` (id: name), `history_years`, `industries.<industry>.<series name>.<case>` TBtu arrays (industries: `refining`, `food`, `paper`, `bulk_chemicals`, `glass`, `cement_and_lime`, `iron_and_steel`, `aluminum`, `metal_based_durables`, `other_manufacturing`, `nonmanufacturing`) |

Samples (first build): June 2025 of `monthly.by_source`; Chemicals (NAICS 325) in MECS; Texas in 2023.

```json
{"total": 2617.221, "end_use_total": 2171.246, "coal": 68.042, "natural_gas": 851.268, "petroleum": 755.915, "renewables": 193.224, "electricity_retail_sales": 307.156, "electrical_system_losses": 445.975}
```

```json
{"naics": "325", "name": "Chemicals", "rank_us_total": 1, "by_region": {"us": {"coal": 63.0, "coke_and_breeze": 0.0, "distillate_fuel_oil": 8.0, "hgl": 16.0, "hydrogen": 94.0, "natural_gas": 2585.0, "net_electricity": 512.0, "other": 698.0, "total": 3976.0}}}
```

```json
{"consumption_tbtu": {"total": 7672.8, "natural_gas": 2550.695, "petroleum": 3780.276, "electricity": 539.946, "coal": 4.647, "renewables": 100.96}, "price_usd_per_mmbtu": 9.41}
```

## Changes

- 19 November 2026, session 8000: first version.
- 19 November 2026, session 8003: real samples for sections 1, 4, 6 and 7 from the first builds; section 6's values are whole megawatts; section 4's `storage` is null before July 2024; sections 8 (placeholder) and 9 (`site/data/industry.json`) added. No key of the first version moved.
