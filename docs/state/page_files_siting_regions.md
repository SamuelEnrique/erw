# Page files of "where the next gigawatts can go" (contract)

Written by session 11200 (chain 760, part B) on 28 November 2026, before any file lands, for the new section of the datacenter page's All grids tab (Samuel's ruling of 22 October 2026: it lives on that tab, not on a page of its own). The personal laptop (chain 780) builds the section against it. A shape that later has to change is changed here first, with a dated line at the foot saying what moved, and one line in `docs/state/landing_request_portable.md` saying so.

Builder: `warehouse/derived/siting_regions.py` (a daily step of the data machine). Method: `docs/methods/siting_regions.md` (internal, with a decisions block). Replication: `replication/siting_regions/`. Every file is written whole by the builder, from warehouse tables already held; no builder makes a request.

**No score, no rank, no advice.** Each count is what its publisher published, or a plain arithmetic of it (a share, a sum, a mean, a percentile, a count of hours) written in the method note. No composite, no weighting of one count against another, no "best region". How a reader sorts the places is the reader's choice on the page.

## The places

Three kinds, as the Grid tool (`site/data/regions/index.json`) and the forecast (`site/data/predict/`) already name them. No new list of places.

| Kind | Ids | Rule |
|---|---|---|
| `region` | `region-cal`, `region-car`, `region-cent`, `region-fla`, `region-mida`, `region-midw`, `region-ne`, `region-nw`, `region-ny`, `region-se`, `region-sw`, `region-ten`, `region-tex` | EIA's 13 regions, as `regions[]` of `site/data/regions/index.json` (members: its `bas`) |
| `operator` | `op-caiso`, `op-ercot`, `op-spp`, `op-miso`, `op-pjm`, `op-nyiso`, `op-isone` | the seven market operators, as the Grid and conditions pages name them (`ba`: CISO, ERCO, SWPP, MISO, PJM, NYIS, ISNE) |
| `ba` | `ba-<code lower case>` (`ba-soco`, `ba-tva`, `ba-duk`, ...) | every balancing authority of `bas[]` with `us` true and `active` true whose highest hourly demand in the last 12 whole months of `eia930_ba_demand_hourly` is at least 5,000 MW. The seven operators' own authorities are listed as operators, not again as `ba` |

## How a count is written (every file)

A count is a cell:

```json
{"v": 46.31, "unit": "USD/MWh", "period": "2025-11-01..2026-10-31", "src": "ercot_hub_prices", "held": null}
```

| Field | Type | What |
|---|---|---|
| `v` | number, string or `null` | the figure (a string only where the count is a time or a name, said in its row below) |
| `unit` | string | as the table names it (`USD/MWh`, `MW`, `MWh`, `hours`, `pct`, `count`, `years`, `kgCO2/MWh`, `UTC`) |
| `period` | string | the span the figure covers, `YYYY-MM-DD..YYYY-MM-DD` (UTC days, both included), or a single date or `YYYY` for a snapshot or a year |
| `src` | string | a key of the file's `sources` (below), for the hover |
| `held` | `null` or string | `null` when shown. When the figure is not shown, `v` is `null` and `held` gives the reason in plain words, beginning with one of: `license needed:` (a license holds it; `docs/licenses.md`), `paused:` (the publisher is paused; `warehouse/metadata/paused_sources.csv`), `not published:` (the publisher prints no such figure in the files read), `not held:` (the warehouse holds no table of it for this place yet), `not a market:` (no hub price: the place is not an organised market), `too few:` (below the method note's floor) |

Every file carries `sources`: one entry a source key, `{"table": "...", "publisher": "...", "license": "public" | "internal", "retrieved": "<the table's last retrieval, UTC>", "report": "<the publisher's report in words>"}`. A `license` of `internal` is never shown with a figure: such a count is written with `held` `license needed:`.

## 1. `site/data/siting/regions/index.json`

| Key | Type | Unit | Source table | License | Example |
|---|---|---|---|---|---|
| `built` | string | UTC | | | `"2026-11-28T12:00:00Z"` |
| `example` | boolean | | | | `false` (`true` only in the example file) |
| `contract`, `method`, `license` | string | | | | `"docs/state/page_files_siting_regions.md"`, `"docs/methods/siting_regions.md"`, `"public"` |
| `ba_floor_mw` | number | MW | | | `5000` |
| `ba_floor_period` | string | | `eia930_ba_demand_hourly` | public | `"2025-11-01..2026-10-31"` |
| `places[]` | list | | | | one entry a place, below |
| `places[].id`, `.kind`, `.code`, `.name` | string | | `site/data/regions/index.json` | public | `"ba-soco"`, `"ba"`, `"SOCO"`, `"Southern Company Services, Inc. - Trans"` |
| `places[].region` | string or `null` | | `site/data/regions/index.json` | public | `"SE"` (an operator: `null`) |
| `places[].regions` | list of strings | | the members' regions | public | `["MIDW", "CENT", "SW", "TEX"]` for `op-miso`; one item for a `ba` or `region` |
| `places[].operator` | string or `null` | | | | `"op-pjm"` for a `ba` inside a market; `null` otherwise |
| `places[].members` | list of strings | | `site/data/regions/index.json` | public | the authorities summed for a region; `["ERCO"]` for `op-ercot` |
| `places[].tz` | string | | `site/data/regions/index.json` | public | `"America/New_York"` |
| `places[].peak_mw` | number | MW | `eia930_ba_demand_hourly` | public | `40711.0`: the highest hour of `ba_floor_period` (a region: the highest hour of its members' summed demand) |
| `places[].ref_hub` | string or `null` | | the price tables | public | `"ercot:HB_HUBAVG"`: the hub `table.json` shows for the place (the method note names each); `null` where no hub price is public |
| `places[].file` | string | | | | `"ba-soco.json"` |
| `sections[]` | list | | | | the ten sections in order, each `{"id", "title", "counts": [{"key", "label", "unit"}]}`: the page can draw every section and column from it |

## 2. `site/data/siting/regions/<id>.json` (one file a place)

Top: `built`, `example`, `contract`, `method`, `license`, `id`, `kind`, `code`, `name`, `tz`, `members`, `sources` (above), `sections` (below). Each section has `status` (`shown`, or a reason in the words of `held` when nothing in it can be shown) and its counts. Lists are cut to the length named.

| Key (under `sections.`) | Type | Unit | Source table | License | Example |
|---|---|---|---|---|---|
| **`price`** | | | | | |
| `price.hubs[]` | list | | `ercot_all_hub_prices_history`, `iso_hub_prices_history`, `iso_dam_hub_prices`, `iso_rtm_hub_prices` | public for ERCOT, CAISO, SPP; PJM, NYISO and ISO-NE `license needed`; MISO `paused` | each hub of the place's operator held in the tables, both markets |
| `price.hubs[].hub_id`, `.hub`, `.operator`, `.market` | string | | | | `"ercot:HB_HUBAVG"`, `"ERCOT Hub Average"`, `"op-ercot"`, `"day-ahead"` or `"real-time"` |
| `price.hubs[].mean`, `.p95` | cell | USD/MWh | as above | as above | `{"v": 46.31, ...}`: the mean and the 95th percentile of the hourly prices (real time: the hour's mean of its intervals) over the last 12 whole months |
| `price.hubs[].hours_over_100`, `.hours_below_0`, `.hours` | cell | hours | as above | as above | `{"v": 312, ...}`: hours above USD 100, below zero, and hours held, same period |
| **`congestion`** | | | | | |
| `congestion.hubs[]` | list | | `price_congestion_monthly` | public (CAISO, SPP); the others `not published:` or as `price` | `{"hub_id", "hub", "congestion_share_pct": cell (pct), "congestion_mean": cell (USD/MWh)}` over the last 12 whole months, as `site/data/conditions/congestion.json` computes them |
| `congestion.top_by_hours[]`, `.top_by_cost[]` | list (10) | | `constraints_binding_monthly` | public (CAISO, SPP) | `{"name", "contingency", "hours", "cost", "abs_mean"}`: the operator's own constraint name; `hours` (hours bound), `cost` (USD/MWh times hours), `abs_mean` (USD/MWh), the last 12 whole months |
| `congestion.top_period`, `.top_src`, `.top_held` | string, string, `null` or string | | | | the period and source of both lists, and their reason when not shown |
| **`tightness`** | | | | | |
| `tightness.peak_mw`, `.peak_prior_mw` | cell | MW | `eia930_ba_demand_hourly` | public | the highest hour of the last 12 whole months, and of the 12 before |
| `tightness.peak_growth_pct` | cell | pct | `eia930_ba_demand_hourly` | public | `(peak_mw / peak_prior_mw - 1) * 100` |
| `tightness.peak_hour` | cell (string) | UTC | `eia930_ba_demand_hourly` | public | `"2026-08-20T21:00:00Z"` |
| `tightness.alerts`, `.watches`, `.emergencies`, `.alert_days` | cell | count, days | `grid_all_alerts` | public (CAISO, ERCOT, DOE) | notices of each kind as the operator names them (the method note maps each operator's words to the three), and days with any, last 12 whole months; others `not published:` |
| `tightness.out_mw_at_peak` | cell | MW | `generation_outages_hourly` | public (CAISO, SPP) | megawatts out of service in the peak hour, as published |
| `tightness.reserve_margin_pct`, `.reserve_target_pct` | cell | pct | `ercot_cdr_reserve_margins`, `iso_reserve_margin_reports` | public | the planning reserve margin the operator prints for the next summer, and the target or requirement it prints beside it; the period is the season it describes |
| **`queue`** | | | | | |
| `queue.active_mw`, `.active_projects` | cell | MW, count | `lbnl_interconnection_queue` | public | requests active at the edition's date (Berkeley Lab's "Queued Up", 2026 edition, through 2025), summed |
| `queue.by_fuel[]` | list | | `lbnl_interconnection_queue` | public | `{"fuel", "active_mw": cell, "active_projects": cell}`, fuels as Berkeley Lab cleans them |
| `queue.withdrawn_share_pct` | cell | pct | `lbnl_interconnection_queue` | public | requests withdrawn as a share of requests that reached an end (withdrawn or operating), entered 2000 to 2020, by megawatts |
| `queue.median_years_to_operation` | cell | years | `interconnection_durations` | public | the median from request to operation of projects operating 2021 to 2025 |
| **`large_load`** | | | | | |
| `large_load.rules_n`, `.smallest_threshold_mw` | cell | count, MW | `utility_large_load_rules` | public (the held rows `license needed:`) | rules of the place's utilities in the table, and the smallest load a rule applies to |
| `large_load.rules[]` | list | | `utility_large_load_rules` | public | `{"id", "utility", "state", "status", "threshold_mw", "contract_term", "collateral", "exit_fee", "study_timeline", "source_url"}`, each as the table holds it (text as printed; `null` where the document prints none) |
| `large_load.queue_totals[]` | list | | `utility_large_load_queue_totals` | public | `{"utility", "state", "date", "mw", "figure", "source_url"}`, the figure as printed with its date |
| `large_load.laws[]` | list | | `state_large_load_laws` | public | `{"state", "bill", "status", "title"}` for the states the place reaches |
| **`mix_carbon`** | | | | | |
| `mix_carbon.mix[]` | list | | `eia930_ba_supply_hourly` | public | `{"fuel", "share_pct": cell}`: each fuel's share of net generation over the last 12 whole months |
| `mix_carbon.intensity` | cell | kgCO2/MWh | `carbon_intensity_hourly` | public | the mean over the last 12 whole months (the demand basis, `intensity_demand`) |
| `mix_carbon.intensity_by_hour` | list (24) | kgCO2/MWh | `carbon_intensity_hourly` | public | the mean by hour of day in the place's clock, same period; `intensity_by_hour_period`, `intensity_by_hour_src`, `intensity_by_hour_held` beside it |
| **`imports`** | | | | | |
| `imports.net_import_share_pct` | cell | pct | `eia930_ba_interchange_hourly_<year>`, `eia930_ba_demand_hourly` | public | net imports as a share of demand over the last 12 whole months (negative: a net exporter) |
| `imports.net_import_share_peak_pct` | cell | pct | same | public | the same over the 100 highest-demand hours of that period |
| `imports.partners[]` | list (3) | | `eia930_ba_interchange_hourly_<year>` | public | `{"ba", "name", "net_import_mwh": cell}`: the three neighbours it took most from, net (a region or operator: neighbours outside it) |
| **`spare`** | | | | | |
| `spare.curtailed_wind_mwh`, `.curtailed_solar_mwh` | cell | MWh | `iso_curtailment_monthly` | public (CAISO, ERCOT, SPP) | curtailment as the operator publishes it, last 12 whole months; others `not published:` |
| `spare.negative_price_hours` | cell | hours | as `price` | as `price` | hours below zero at `ref_hub`, day-ahead, same period |
| **`forecast`** | | | | | |
| `forecast.operator_mape_pct`, `.erw_mape_pct`, `.hours` | cell | pct, hours | `site/data/predict/scores.json` (from `eia930_ba_demand_hourly`) | public | the mean absolute error, in percent of demand, of the operator's day-ahead demand forecast as filed on EIA-930, and of the ERW forecast, over the forecast's own scoring window; `not held:` for a place the forecast does not cover |
| **`datacenters`** | | | | | |
| `datacenters.facilities_n`, `.facilities_mw_stated` | cell | count, MW | `datacenter_facilities` | public | facilities held in the place, and the sum of the megawatts stated where a figure is stated (`facilities_mw_n`: how many state one) |
| `datacenters.projects_n`, `.projects_mw_stated` | cell | count, MW | `datacenter_projects` | public | announced projects held, the same way |
| `datacenters.list[]` | list (25) | | `datacenter_facilities`, `datacenter_projects` | public | `{"name", "operator", "state", "county", "mw", "status", "source_url"}`, the largest stated first |

How a place reaches a table: a `ba` by its EIA code; an `operator` by its `ba` code and by the operator's own id in the operator tables; a `region` by its member authorities (summed for demand and interchange, the members' utilities and states for the large-load tables). The states and utilities a place reaches, and the grid each datacenter is in, are read from the columns the tables already carry (`grid`, `x_iso_region`, `state`); the method note writes each mapping.

## 3. `site/data/siting/regions/table.json` (every place side by side)

| Key | Type | Unit | Source table | License | Example |
|---|---|---|---|---|---|
| `built`, `example`, `contract`, `method`, `license`, `sources` | | | | | as above |
| `columns[]` | list | | | | `{"key": "price.mean_da", "section": "price", "label": "Day-ahead price, mean", "unit": "USD/MWh"}` |
| `rows[]` | list | | | | one a place, in the order of `index.json` |
| `rows[].id`, `.kind`, `.name` | string | | | | `"op-ercot"`, `"operator"`, `"ERCOT"` |
| `rows[].v` | list | | | | one value a column, `null` where held |
| `rows[].cell` | object | | | | for each column index (as a string) that is not plainly shown: `{"period", "src", "held"}`; a column with no entry takes the period and source of `columns[].period` and `columns[].src` |
| `columns[].period`, `columns[].src` | string | | | | the common period and source of the column |

The columns (one value a place): `price.mean_da`, `price.p95_da`, `price.hours_over_100_da`, `price.hours_below_0_da`, `price.mean_rt` (at `ref_hub`); `congestion.share_pct` (at `ref_hub`); `tightness.peak_mw`, `tightness.peak_growth_pct`, `tightness.alert_days`, `tightness.out_mw_at_peak`, `tightness.reserve_margin_pct`; `queue.active_mw`, `queue.withdrawn_share_pct`, `queue.median_years_to_operation`; `large_load.rules_n`, `large_load.smallest_threshold_mw`; `mix_carbon.intensity`; `imports.net_import_share_pct`, `imports.net_import_share_peak_pct`; `spare.curtailed_wind_mwh`, `spare.curtailed_solar_mwh`; `forecast.operator_mape_pct`, `forecast.erw_mape_pct`; `datacenters.facilities_n`, `datacenters.projects_mw_stated`. Every value is a count of the place file's own; `table.json` computes nothing new.

## Example files

Pushed with this contract, each with `"example": true` and every value `null` with `held` `"not held: example file, written before the builder"`: `site/data/siting/regions/index.json` (three places, one of each kind), `site/data/siting/regions/op-ercot.json`, `site/data/siting/regions/table.json`. They are replaced whole by the builder's first run; no figure in them is real or invented.

## Dated lines
