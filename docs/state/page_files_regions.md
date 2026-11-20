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

## 8. The natural resource map's layers (step D1)

The page "Where the resources are" already reads twelve resource layers and two offshore ones from `site/data/resources/layers/` through `site/data/resources/manifest.json` (session 146, `docs/methods/resource_layers.md`); under chain 501's rule those files are not changed, and a page reads them where they are. Step D1 adds one layer file and one table:

| File or table | Form | Meaning |
|---|---|---|
| `site/data/resources/coal_fields.json` | GeoJSON FeatureCollection, WGS 84, coordinates to 3 decimals, under 2 MB | the USGS coal fields of the conterminous United States (Open-File Report 2012-1205, East 2013): 602 polygons |
| `features[].properties` | `province`, `name`, `age`, `rank` (text, as USGS gives them), `area_km2` (km2, before simplification) | one coal field |
| top level | `built`, `tables` (`resource_layer_features`), `method`, `license` (`public`), `source`, `source_url`, `retrieved_at`, `source_sha256`, `simplify_tolerance_deg` | as section 1 |
| table `resource_layer_features` | entities, one row a cell, site or area | every cell (0.05 degrees) of the wind speed and the two solar grids, every site and area of the other resource layers, and the coal fields, each with `x_layer`, `x_value`, `x_unit`, `lat`, `lon` (`docs/methods/resource_layers_table.md`) |

Sample `properties` (first build, 544,878 bytes at a tolerance of 0.005 degrees): `{"province": "Interior", "name": "Northern Region", "age": "Pennsylvanian-Permian", "rank": "Medium and High Volatile Bituminous", "area_km2": 29776.9}`.

Not drawn (no source this machine may read): uranium and critical-mineral deposits (USGS's `mrdata.usgs.gov` robots file disallows every path to every agent; ScienceBase disallows Claude by name).

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

## 10. `site/data/regions/authority/<code>.json` (chain 505, part C)

One file a balancing authority of `index.json` that files Form EIA-930 in the lower 48 (`us` and `files_eia930` true; code in lower case), and one a region (`authority/region-<code>.json`, the thirteen, the region's authorities summed where a sum is meaningful). Method: `docs/methods/authority_facts.md`. Builder: `warehouse/derived/authority_facts.py`, in the data machine's daily run. Every part carries `table` (the ERW table it is read from), `vintage` (the source's own period) and `source` (the publication in words). A part a source does not cover is present with `null` values and `why` in words, never a zero.

| Key | Unit or form | Meaning |
|---|---|---|
| `built`, `tables`, `method`, `license`, `code`, `name`, `region`, `level` | | as in the other files; `level` is `ba` or `region`; a region's file has `bas` (the authorities summed) |
| `owns.capacity_mw.<technology_group>` | MW | operating generators' capacity (EIA-860M `capacity_mw`, net summer) by the plant's balancing authority, by the ERW's technology group; `owns.generators` the count; `owns.total_mw` |
| `owns.largest_plants[]` | list of 10 | `{ plant_id, name, state, mw, technology_group, operator }`, largest first by the plant's operating capacity |
| `coming.additions[]` | list | `{ year, technology_group, mw, generators }`: planned generators by their planned operation year (EIA-860M planned sheet) |
| `coming.retirements[]` | list | `{ year, technology_group, mw, generators }`: operating generators with a planned retirement date, by its year |
| `coming.retired_recent[]` | list | `{ year, technology_group, mw, generators }`: generators EIA-860M lists as retired, by year |
| `burns.months` | `[first, last]` `YYYY-MM` | the twelve complete months read (Form EIA-930, the six-month files) |
| `burns.generation_mwh.<source>` | MWh | net generation by EIA's eight sources (`coal`, `natural_gas`, `nuclear`, `petroleum`, `hydro`, `solar`, `wind`, `other`), `storage` where filed; `burns.share_pct.<source>`; `burns.hours_held` |
| `burns.co2` | object or null part | `{ tco2_generated, intensity_kg_per_mwh }` from EIA's own hourly CO2 estimates over the same months (`eia930_all_emissions`, the seven ISOs and the Lower 48 only); else `null` with `why` |
| `trades.year` | year | the newest whole year of `ba_trade_partners` |
| `trades.partners[]` | list of up to 5 | `{ code, name, exchange_gross_mwh, net_import_mwh }`, largest gross exchange first |
| `trades.net_import_share_of_demand_pct` | percent | the authority's net imports as a share of its demand that year (`ba_trade_partners`); `null` with `why` where not held |
| `size.peak_mw`, `size.peak_at` | MW, UTC hour | the highest whole-day peak in the demand file (`demand/ba/<code>.json`, `daily`); `size.peak_local` the hour in the authority's time zone |
| `size.growth_since_2019_pct` | percent | the newest whole year's demand against 2019's, from the demand file's `growth`; `size.growth_year` |
| `large_loads.rows[]` | list | `large_load_public` rows whose grid or utility group lies in the authority: `{ date, group, row_kind, mw, mw_low, mw_high, document_title, source_url, stage_class }`, newest first; `large_loads.count`; `large_loads.how` says how the rows were placed |

## 11. `site/data/regions/forecast/<region>.json` and `forecast/ba/<code>.json` (chain 505, part D1)

The day-ahead demand forecast each authority files on Form EIA-930, beside the demand that came, from July 2018. Method: `docs/methods/forecast_error.md`. Builder: `warehouse/derived/forecast_error.py`, in the data machine's daily run. Tables: `eia930_forecast_error_hourly`, `eia930_forecast_error_daily`.

| Key | Unit or form | Meaning |
|---|---|---|
| `built`, `tables`, `method`, `license`, `code`, `name`, `level`, `region`, `tz` | | as in the other files; `level` is `ba` or `region` |
| `first_hour`, `last_hour` | UTC | the first and last hour with both a forecast and a demand |
| `overall` | object | `{ hours, mape_pct, wape_pct, bias_pct, mae_mw, bias_mw, screened_hours, screen }` over every hour not screened |
| `by_hour.<measure>` | array of 24 | `mape_pct`, `wape_pct`, `bias_pct`, `hours` by the local hour of day (0 is the hour starting at midnight) |
| `by_season.<DJF, MAM, JJA, SON>` | object | the measures over each season, with `words` |
| `by_year.<YYYY>` | object | the measures over each local year |
| `daily.days`, `daily.<measure>` | arrays | every whole local day (no hour missing or screened): `mape_pct`, `bias_mw`, `peak_forecast_mw`, `peak_demand_mw`, `peak_miss_pct` |
| `hottest_days[]`, `coldest_days[]` | list of 10 | `{ day, temp_f, mape_pct, bias_mw, peak_forecast_mw, peak_demand_mw, peak_miss_pct }` by the region's daily mean temperature; `weather` names the table and basis; `null` with `weather.why` where no weather is held |
| `events[]` | list of 9 | `{ event, title, start, end, hours, mape_pct, wape_pct, bias_pct, mae_mw, bias_mw, peak_forecast_mw, peak_demand_mw, peak_miss_pct }` over each event's window, local days |

Signs: a miss is the forecast less the demand; above zero the forecast was high.

## 12. `site/data/regions/renewables_forecast.json` (chain 505, part D2)

The operator's own day-ahead forecast of wind and solar output beside the output that came, for each grid that publishes both under a license `docs/licenses.md` lets a page show: CAISO (by trading hub, and the three hubs summed) and ERCOT (system-wide). Built from the warehouse's tables `caiso_wind_solar_forecast` and `ercot_wind_solar_forecast` (both public); no table of its own. Method: `docs/methods/renewable_forecast_error.md`. Builder: `warehouse/derived/renewable_forecast_error.py`, in the data machine's daily run.

| Key | Unit or form | Meaning |
|---|---|---|
| `built`, `tables`, `method`, `license` | | as in the other files |
| `grids[]` | list | one object a grid: `grid`, `region` (EIA's region it sits in), `code` (its EIA-930 code), `tz`, `table`, `forecast` (words: which of the operator's forecasts), `actual` (words), `entities` |
| `grids[].series.<wind or solar>` | object | the measures below for the grid as a whole (CAISO: an hour only when all three hubs hold both the forecast and the output) |
| `grids[].hubs.<hub>.<wind or solar>` | object | CAISO only: `overall` for each hub |
| `...overall` | object | `{ hours, mae_mw, bias_mw, wape_pct, bias_pct, forecast_mean_mw, actual_mean_mw }` over every hour holding both |
| `...first_hour`, `...last_hour` | UTC | the first and last hour holding both |
| `...by_hour` | arrays of 24 | `wape_pct`, `bias_mw`, `mae_mw`, `hours`, by the local hour of day |
| `...by_month.<YYYY-MM>` | object | the overall measures over each local month |
| `...daily` | arrays | every whole local day: `days`, `forecast_mwh`, `actual_mwh`, `miss_mwh`, `wape_pct` |
| `...events[]` | list of 9 | `{ event, title, start, end, hours, mae_mw, bias_mw, wape_pct }`; `hours` 0 and the measures `null` where the table does not reach the event |
| `not_held[]` | list | `{ grid, why }` for each other grid of the seven: why its forecast is not drawn |

Signs: a miss is the forecast less the output; above zero the forecast was high. `wape_pct` is the absolute misses summed over the output summed, in percent.

## 13. `site/data/regions/prices_map.json` (chain 505, part E2)

What power costs across the map: every hub and load zone whose day-ahead price a page may show, with the authority and region it sits in, for the "Price" switch of the Grid tool's map. Computed from the public price tables `warehouse/derived/price_compare.py` reads, with its reader, hourly rule and license and pause handling; no table of its own. Method: `docs/methods/prices_map.md`. Builder: `warehouse/derived/prices_map.py`, in the data machine's daily run.

| Key | Unit or form | Meaning |
|---|---|---|
| `built`, `tables`, `method`, `license`, `measures`, `rules` | | as in the other files; `measures` gives each measure's unit |
| `grids[]` | list | `{ grid, iso, ba, region, tz, state }`: `state` is `shown`, `held` (license needed) or `paused`, with `why` for the last two; `hubs` counts a shown grid's hubs and zones |
| `hubs[]` | list | one object a shown hub or zone: `entity`, `node`, `grid`, `ba`, `region`, `table`, `day` (the newest whole local day before the build's day), `day_avg`, `day_on_peak`, `day_off_peak`, `day_spread_top4_bottom4` (USD/MWh), `avg_30d`, `negative_share_30d_pct`, `avg_12m`, `negative_share_12m_pct`; a window short of 95 percent of its hours is `null` with `window_30d_why` or `window_12m_why` |
| `bas.<code>` | object | what the map colors an authority's area by: the grid's main hub (`hub`, the board's choice) and its measures, or `state` and `why` |

A held grid carries its key with no figure and the words "license needed".

## Changes

- 19 November 2026, session 8000: first version.
- 19 November 2026, session 8003: real samples for sections 1, 4, 6 and 7 from the first builds; section 6's values are whole megawatts; section 4's `storage` is null before July 2024; sections 8 (placeholder) and 9 (`site/data/industry.json`) added. No key of the first version moved.
- 19 November 2026, session 8004 (data request 327, section 3): the demand files also carry, in `weather`, `train` (the fit's years, 2019 to 2021), `metrics`, `labels`, `features` (the fit's terms), `degrees_from` (words for where the degrees come from) and `weather_table`; on an authority's file, `region`; and `alike.grid_file`. `growth.last_year` and `growth.ytd_through` are `null` for an authority whose demand stops before 2019 (its `growth.years` is empty). `alike.why` is a clause, not a sentence. The folder `demand/` is about 17 MB (13 region files and 58 authority files) on the first build.
- 19 November 2026, session 8004 (data request 324, section 2): `bas[]` also lists the Canadian and Mexican authorities of EIA's reference tables, which file no Form EIA-930 (`region` `CAN` or `MEX`, `first_hour` and `last_hour` `null`, `files` empty), so every code of `trade_matrix.json` has a name. Every `bas[]` item now carries `us` (EIA's "U.S. BA") and `files_eia930` (true for the lower 48's authorities, false for those across the border).
- 19 November 2026, session 8004 (data requests 323, 325 and 326, sections 5 and 7): each object of `region_pairs[]` and `ba_pairs[]` also carries `hours_a`, `hours_b`, `hours_both` (hours each side reported, and both), `months_held` (the Eastern months of the year holding a report from either side) and `months_in_year` (the months of that year the file holds); the file carries `first_month` and `upto`. `direction` is `none` when `mean_mwh` is exactly zero. `mean_mwh` is the sum of the year's monthly values of `interchange_pair_monthly`, each the mean of the two reports over the hours both reported, or the one side's report where the other reported no hour that month. A year is the sum of EIA's Eastern months of that year, as in the trade files. `trade/<region>.json` also carries `hours_in_month`; its hours arrays hold `0`, a count, for a month a side reported nothing, while its report arrays hold `null` there. A side that files nothing with EIA (Canada, Mexico) is a `null` report with `0` hours in both files. For a region pair the two files are meant to agree to the MWh: a pair's `a_report_mwh` for a year is minus the sum of that year's `neighbors.<b>.net_imports_mwh` in `trade/<a>.json`, and `b_report_mwh` the sum of `neighbors.<a>.net_imports_mwh` in `trade/<b>.json` (both are sums of the same hourly reports of `eia930_region_pair_hourly` over the same months; the first build agrees exactly for the Carolinas and the Southeast in 2019, 2025 and 2026). A difference is a fault.
- 19 November 2026, session 8006: section 8 written (the coal fields' file and the resource table; the existing layer files are read where they are).
- 19 November 2026, session 8009 (data requests 328 and 329, section 3; on `wip/c501-desk-b`, landing at the desk's next gate): `daily` writes a day's demand, peak and hour only when every hour of the local calendar day (23, 24 or 25) is used, so a record's first and last days, held only in part, are `null`; each of the seven grids' authority files (`demand/ba/erco.json`, `ciso`, `pjm`, `miso`, `swpp`, `nyis`, `isne`) carries `alike` in the regions' form (`region_avg_demand_mw` is that file's own average).
- 19 November 2026, session 8009 (data request 542, section 8; on `wip/c501-desk-b`): the coal fields also in the resource map's layer form, `site/data/resources/layers/coal_fields.json` (properties `name`, `kind`, `value` in square kilometres, `value_unit`, and `PROVINCE`, `NAME`, `AGE`, `RANK`), with its entry, `measure` included, in `site/data/resources/manifest_added.json`, a new file in `manifest.json`'s form (`built_at_utc`, `note`, `layers`, `missing`) that a page reads beside `manifest.json`, which is not changed; `missing` lists the uranium and critical-mineral layers not fetched.
- 19 November 2026, session 8009 (section 4; on `wip/c501-desk-b`): an hour of a mix file is held by the rule of `mix_profile.hours_of` applied to the region (every authority holds its net generation, the region's sources within 5 percent of its net generation, 15 percent for the Mid-Atlantic), where the first build applied it to each authority; no key moves, and the regions hold more months (the Mid-Atlantic 95 where it held 40, the Southwest 85 where it held 36).
- 19 November 2026, session 8010 (data requests 545 and 546, sections 3 and 6; on `wip/c501-desk-c`): each pair of an event file carries `flow_mw_a` (the first region's own report, MW, power from A to B) and `flow_mw_b` (the second's, turned to the same direction) beside `flow_mw`; each region's `weather` object carries `coverage`, `{ "<year>": { "hours_held", "hours_in_year", "share_pct" } }`, the hours of each local year its weather holds.
- 19 November 2026, session 8011 (data request 551, section 4; on `wip/c501-desk-d`): a source no authority of a region has printed in any held hour since July 2018 is `null` in that region's mix file (its `avg`, `<source>_mwh`, `<source>_share_pct` and hourly array), and the file names such sources in a new key, `sources_not_printed`.
- 19 November 2026, session 8011 (data request 552, section 8; on `wip/c501-desk-e`): in `layers/coal_fields.json` `value` is now in square miles (`value_unit` says so, the entry's `unit` too), with a new property `AREA_KM2`, the square kilometres; the entry's `notes_for_method` is the sentence without the method note's file name, which moves to a new key, `method_note`.
- 19 November 2026, session 8011 (data request 553, section 8; on `wip/c501-desk-g`): a new file, `site/data/resources/hover_fields_added.json`: `{ built_at_utc, note, layers: { <layer id>: { hover_fields: [[column, words]], name_column: { column, source_column, words, unit }, source_file, source_sha256, how } } }`, for `wind_capacity_factor` and `geothermal_hydrothermal_sites`, the two point layers `manifest.json` gives no `hover_fields`; a page uses a layer's list here when `manifest.json` gives none.
- 19 November 2026, session 8012 (chain 505, part C): section 10, every balancing authority's own facts (`authority/<code>.json`, `authority/region-<code>.json`); no key of another section moves.
- 19 November 2026, session 8012 (chain 505, part D1): section 11, the day-ahead demand forecast beside the demand that came (`forecast/<region>.json`, `forecast/ba/<code>.json`); no key of another section moves.
- 19 November 2026, session 8013 (chain 505, part D2): section 12, the operators' wind and solar forecasts beside the output (`renewables_forecast.json`); no key of another section moves.
- 19 November 2026, session 8013 (chain 505, part E2): section 13, what power costs across the map (`prices_map.json`); section 12's file is `renewables_forecast.json`, beside the folder `forecast/`, which keeps the region files alone. No key of another section moves.
