# The findings hunt of 19 November 2026: the plan (chain 502, session 8200)

Energy Research Warehouse (ERW), lab-desktop's second window, for Samuel. Chain file: `queue/done/502-day-19-november-desktop-window2-findings-industry.md`. Model spend: USD 0; no model is called, every sentence is written by the session and every figure in it is computed by code and pinned by its reproduction.

## How the ground was read

- `warehouse/metadata/coverage.csv` on origin/main of 19 November against the same file at `1ea4a6145` (the last change before 7 November 2026), by `runs/c502/ground.py`: a table is **added** when it was not in the old file, **widened** when its rows grew by half or its first month moved earlier.
- The notes of `docs/state/` from 10 to 18 November for what each table is, and `docs/methods/eia930_region_hourly.md` and `docs/methods/region_weather.md` for the 17 November tables.
- The drafts already written: `docs/findings/<family>/` (chain 164, 6 to 9 November), 12 families, 185 drafts with a reproduction each.

## What the hunt of 6 to 9 November already read (chain 164)

| Family folder | Drafts | What it read |
|---|---|---|
| `generation_pipeline` | 35 | EIA-930 mix, EIA-923, EIA-860M build-out, the pipeline, nuclear |
| `prices` | 33 | ISO hub prices, spreads, spark spreads, fuel closes |
| `queues_deals_datacenters` | 27 | ISO queues, deals, datacenter projects |
| `oil_products_world` | 18 | petroleum supply, imports by origin, PortWatch, crude |
| `demand` | 12 | EIA-930 daily demand by authority, sub-regions |
| `tariffs_policy` | 12 | large-load tariffs and rules as of 6 November, policy actions |
| `gas` | 11 | gas balance, storage, LNG, hubs |
| `coal_uranium_metals` | 8 | coal, uranium, metals |
| `cross_family` | 8 | two-family findings |
| `emissions_climate` | 7 | EIA-930 emissions, carbon |
| `markets_operations` | 7 | ancillary, operations |
| `other_us` | 7 | retail, other US series |

None of them read a region pair, a tie between two balancing authorities, a region's temperature, or the six regions outside the seven grids.

## What the warehouse gained since 7 November

### Added: 41 tables

| Family of this hunt | Tables | Span | Rows | License |
|---|---|---|---|---|
| 1. Who trades with whom | `eia930_region_pair_hourly` | 2018-07 to 2026-11-16 | 1,820,134 | public (EIA) |
| | `eia930_ba_interchange_hourly_2018` to `_2026` (nine tables) | 2018-07 to 2026-11-16 | 21,780,045 | public (EIA) |
| 2. The six regions; 5. Balancing authorities | `eia930_region_hourly` | 2018-07 to 2026-11-18 | 3,064,131 | public (EIA) |
| | `eia930_ba_demand_hourly` | 2018-07 to 2026-11-18 | 7,829,972 | public (EIA) |
| | `eia930_ba_supply_hourly` | 2018-07 to 2026-11-17 | 9,137,257 | public (EIA) |
| 3. Demand against temperature | `region_weather_hourly` | 2018-07 to 2026-11-07 | 879,553 | public (derived from NOAA, Census, EIA) |
| | `noaa_region_station_hourly_2018` to `_2026` (nine tables), `noaa_region_stations`, `census_county_population`, `eia_county_region` | 2018 to 2026 | 15,711,956 in the station tables | public |
| 6. Large loads | `utility_large_load_rules`, `utility_large_load_rule_changes`, `utility_large_load_queue_totals`, `state_large_load_laws` | 2010 to 2026-11-14 | 100, 94, 34, 27 | public (model-extracted, drafted before 16 November) |
| | `large_load_wait_summary` | 2026-07 to 2026-11-15 | 138 | internal |
| 7. Other | `ferc714_forecast_growth`, `ferc714_planning_area_forecasts` | 2007 to 2050 | 198,354; 67,215 | public |
| | `iso_hub_prices_history_2018` | 2018-07 to 2023-07 | 219,720 | public |
| | `caiso_outlook_demand` | 2018-07 to 2024-07 | 33,927 | public |
| | `ercot_peak_premium_node_monthly`, `ercot_storage_rt_offers_monthly` | 2026 | 17,472; 175 | public |
| | `forecast_tool_parameters`, `iso_reserve_margin_reports` | 2010 to 2026 | 768; 5 | public |
| | `datacenter_tracker_rollups` | 2026-11-15 | 592 | internal |
| | `deal_counterparties` | 2026-11-15 | 527 | public (model-extracted) |

### Widened: 15 tables

| Table | Before | Now | Family |
|---|---|---|---|
| `eia_steo_forecasts` | 5,088 rows from 2020 | 10,195 rows from 2009 | 7 |
| `iso_queue_statistics` | 1,511 | 8,990 | 7 |
| `cost_of_power_monthly`, `cost_of_power_carbon` | 2,304; 712 | 4,428; 1,391 | 7 (license needed: ISO-NE, MISO, NYISO rows) |
| `carbon_intensity_monthly` | 1,285 | 4,380 | 7 |
| `ercot_peak_premium_annual` | 2,016 | 4,032 | 7 |
| `eia_crude_first_purchase_prices` | 862 | 2,632 | 7 |
| `ercot_storage_rt_monthly`, `ercot_storage_dam_awards_monthly` | 329; 252 | 1,620; 1,244 | 7 |
| `hub_price_comparison` | 575 | 880 | 7 |
| `imf_commodity_prices` | 465 | 752 | 7 |
| `impact_tax_rules` | 49 | 130 | 7 |
| `large_load_connection_rules` | 39 | 85 | 6 |
| `utility_large_load_tariffs` | 13 | 83 | 6 |
| `energy_projects` | 39,917 | 39,917 (refreshed) | 7 |

The large-load tables named in the chain file, as held today: `large_load_waits` (internal, 2,745 rows), `large_load_public` (public, 341), `large_load_connection_rules` (public, 85), `utility_large_load_tariffs` (public, 83), `large_load_statements` (internal, 798).

## A fault of the region table found on the way (for the first window's chain 501)

- `eia930_region_hourly` writes **no demand at all for the Carolinas, the Northwest, the Southeast and the Southwest**, and none for the Midwest before September 2022 or after part of 2025. Its rule sums a region only when every balancing authority of the region has a value, and each of those regions holds authorities that file generation but never demand (YAD, SEPA, AVRN, GRIF, DEAA, HGMA, GWA, WWA and the like). Net generation and total interchange are held for all thirteen.
- The Northwest's net generation and total interchange hold only 104 and 50 hours of 2020 (Puget Sound Energy's 2020 file is nearly empty).
- This hunt sums a region's demand itself from `eia930_ba_demand_hourly`: every authority the files place in the region that files demand in the month, the hour held only when all of them have a value after the demand fault rule (`warehouse/analysis/findings/deep/hourly930.py`, `region_demand`). Any page file of the six regions built from the region table's demand would be empty for four of them.

## A gap in the region temperatures found on the way (session 8203, for the data machine)

- `region_weather_hourly` writes a region's hour only when every one of its chosen stations holds one. Hours held in 2025 (of 8,760): Texas 5,084, none from late August to December; the Carolinas 5,843, none after September 2025 and none in 2026; Florida 7,042 (November 114, December 273); the Northwest 7,360 (November 246, December 284). Counted by `runs/c502/wx_hours.py`.
- Any page or finding that reads these regions' temperature for late 2025 reads nothing. The station that empties each region is in the connector's run log (`warehouse/connectors/noaa_region_weather.py`).

## Decisions this plan takes

- **EIA's regions and authorities named as EIA names them.** Chain 164's demand module never drafted an authority of MISO, SPP, NYISO or ISO-NE "whoever published the rows". The rows here are EIA's (public; `docs/licenses.md` lists every EIA-930 table as may be public, no license needed), and the chain file asks for all thirteen regions, so drafts name EIA's New York, New England, Midwest and Central regions and, at the tie level, MISO, SPP, NYISO and ISO-NE as EIA-930 balancing authorities. Under "For Samuel's ruling" in the note.
- **The form of chain 164, unchanged.** One sentence (the last full year against the first, 2019, the first full year these tables hold), the five tests of `hunt.test_claim`, the chart by `card_image.py`, the yearly CSV, `reproduce.py` and `reproduce.do`, the draft row in `public.scanner_drafts` (state draft, listed at `/internal/findings`) and its copy under `docs/findings/<family>/`. Nothing approved, nothing on `/research`.
- **Fault rules, one for all the families** (`hourly930.py`): a flow hour more than three times its year's 99th percentile of absolute values is dropped; a demand hour at or below zero or above three times its year's median is dropped.
- **Two sides.** A flow is drafted from one side's report only when the other side, where it holds 90 percent of both end years, moved the same way by half to twice as much; else the two sides' gap is the finding. Mid-Atlantic to Midwest is the case: PJM's report turned from a mean of minus 3,956 MW in 2019 to plus 2,454 MW in 2025 while MISO's moved by 97 MW.
- **No donor ledger.** No regression of imports on weather, no share of a shock covered by imports: family 1 is who sends to whom, how much, when, and how that changed.

## The families, in order, with the questions each asks

1. **Who trades with whom** (`trade`): each region pair's mean hourly flow in its standing direction; the share of hours, of summer hours and of winter hours it runs the other way; each region's net exports or imports over its demand and the hours it trades the other way; the largest ties between authorities; where the two sides' reports disagree, region pairs and ties.
2. **The six regions the site has never shown** (`regions`): the Southeast, Florida, the Carolinas, Tennessee, the Northwest, the Southwest: the year's peak hour, when it falls (month, hour), winter's peak against summer's, the mean hour's growth, the load factor, net generation against demand. What they burn: the hourly tables hold no fuel; EIA-930's fuel mix by authority in the ERW starts in August 2026 (`eia930_all_generation`), so the mix by year is read from EIA-923 by state where a region is close to its states, and said so.
3. **Demand against temperature** (`weather`): each region's coldest and hottest hours of the year and the demand in them; the demand of the hottest and coldest days against the year's mean, as the `/demand` page already reads temperature.
4. **The nine events of `/events`** (`events`): the event windows across all thirteen regions and their pairs, from the hourly tables.
5. **Balancing authorities one by one** (`authorities`): the largest movers in mean demand and peak, and net generation against demand.
6. **Large loads** (`large_load`): the filed tariffs, the connection rules, the waits (internal: "license needed") and the public statements.
7. **The rest**, largest tables first: the FERC 714 forecasts, the 2018 to 2023 hub price history, the widened STEO, queue statistics and carbon intensity, then the families with the fewest drafts (part D).

## The rubric for keeping a draft

- It passes all five tests of `hunt.test_claim`.
- Consequence first (the candidate's author sets 3 for a flow or share of demand, 2 for hours and report gaps), then the size of the change for a measure in MW or percent of demand, else the strength.
- One story is drafted once: a pair keeps its flow and at most one measure of hours against its direction; a tie whose region pair tells the same story is folded into the pair; a gap that only shows a reporting fix of a few MW is left out.
