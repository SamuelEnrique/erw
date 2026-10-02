# Where the next gigawatts for AI can come from: methods appendix

Energy Research Warehouse (ERW), session 62. A draft report, internal: `/reports/draft/ai-gigawatts?token=<INTERNAL_COSTS_TOKEN>`, not in the navigation, not indexed. The table is `ai_power_regions`, built by `warehouse/derived/ai_power_regions.py`. Tier: derived. Every number in the draft is a row of that table, shown with its check key; `site/scripts/check-values.mjs` compares each with Supabase.

## The question and the unit

**The question.** Where in the seven U.S. ISO regions could a new, large, steady load (a data center campus) be served:
- at the lowest wholesale cost;
- with the least carbon;
- on the least stressed grid;
- with the shortest wait to connect new supply;
- with the least reliance on neighbors?

**The unit.** A flat 1 GW: the same 1,000 MW in every hour of a year, 8,760 GWh. Real campuses are not perfectly flat, but they come close, and a flat load is the simplest one to compare across regions.

**The year.** September 2025 to August 2026: the latest twelve complete months that every price input holds.

## The measures

| Measure | Variable | From | How |
|---|---|---|---|
| Flat price, real time | `flat_rt_price_usd_mwh` | `cost_of_power_monthly` | the monthly `rt_simple_mean` (the mean of the hub's hourly real-time prices: what a flat load pays per MWh) weighted by `rt_hours`, over the year |
| Flat price, day-ahead | `flat_da_price_usd_mwh` | the same | `da_simple_mean`, weighted by `da_hours` |
| A flat 1 GW for a year | `flat_1gw_cost_usd` | the same | the real-time flat price times 8,760 MWh per MW times 1,000 MW: wholesale energy only |
| Carbon intensity | `carbon_intensity_kg_mwh` | `carbon_intensity_daily` | the mean of the year's daily consumption-based intensity (the CO2 of the generation the region used, imports included, per MWh of demand), over the days held (`carbon_days`) |
| A flat 1 GW's CO2 | `flat_1gw_co2_t` | the same | the intensity times 8,760 GWh |
| Scarcity hours | `scarcity_hours_200`, `scarcity_hours_1000` | `iso_hub_prices_history`; ERCOT `ercot_all_hub_prices_history` | the year's hours whose real-time hub price (the mean of the hour's 15-minute prices; MISO's hourly price) was at least USD 200 and 1,000/MWh; `rt_hours_seen` counts the hours held |
| Highest hour | `max_rt_hour_usd_mwh` | the same | the year's highest hourly real-time price |
| Emergency days | `emergency_days` | `caiso_grid_emergencies` | CAISO only: days with an ISO-wide Flex Alert or grid emergency, 2018-07 to 2025-04, as the Flex Alert scorecard reads them; no other ISO's notices are held |
| Largest event effect | `event_largest_effect_pct` | `event_study_estimates` | among the studied events (COVID-19 left out), the pooled effect on daily demand with the largest magnitude, as a percent of the event's counterfactual; temperature-controlled where held; `x_note` names the event |
| Active queue, Berkeley Lab | `lbnl_active_mw`, `lbnl_active_requests` | `lbnl_interconnection_queue` | requests with status active at the end of 2025, the region as Berkeley Lab assigns it |
| Time to connect | `lbnl_median_years_to_cod` | the same | the median of (online date less request date) over the requests that came online in 2018 to 2025 (`lbnl_cod_sample` of them) |
| Completion rate | `lbnl_completion_pct` | the same | the share of the requests made in 2000 to 2019 (`lbnl_cohort_requests`) that came online |
| Active queue, the ISO's own | `queue_active_mw` | `<iso>_interconnection_queue` | active MW in the ISO's queue as retrieved in late September 2026 (no PJM queue is held) |
| Net import share | `net_import_share_pct` | `eia930_daily_interchange`; demand from the EIA-930 workbook extract | minus the sum of the region's daily interchange with every neighbor (EIA's sign: positive when it exports), over the year's demand |
| Net import days | `net_import_days_pct` | the same | the share of the year's days on which the region's summed interchange was negative |
| Peak-day import share | `peak_import_share_pct` | the same | the mean net import share on the year's ten highest-demand days |
| Check on imports | `ng_check_import_share_pct` | the extract | (demand less net generation) over demand: EIA's own balance, which should agree with the pair sums |

## The hubs and regions

**The hubs** (one per region, as the cost-of-power model reads them):
- CAISO: SP15;
- ERCOT: the hub average;
- ISO-NE: the internal hub;
- MISO: Indiana Hub;
- NYISO: the New York City zone, which is dearer than upstate;
- SPP: SPP North.

**The balancing authorities:** CISO, ERCO, ISNE, MISO, NYIS, PJM, SWPP. Berkeley Lab's regions carry the same ISO names.

**PJM.** PJM's prices are licensed to the ERW for internal use only, and its hub prices are not held at all. PJM therefore has no cost or price-stress measure, and none is estimated. Its carbon, queue and import measures are from public EIA and Berkeley Lab data.

## What the measures leave out (the report says so too)

- **Delivered cost is wholesale energy only.** It leaves out:
  - capacity charges, which are large in PJM, ISO-NE, NYISO and MISO;
  - transmission and distribution;
  - ancillary services and taxes;
  - the hedges a real buyer signs.

  A flat load at a hub is not a contract price.
- **One year is one year.** 2025 to 2026's prices and scarcity hours reflect that year's weather and fuel prices.
- **The queues measure requests, not capacity that will be built.** Most requests are withdrawn: the completion rates say how many.
- **Interconnection time is for generators, not loads.** A data center's own connection runs through its utility, and its time is not in these data.
- **Permitting, local approval, land, water, and the utility's own load-interconnection process are out of scope.**
- **Imports** are net and daily. A region can import at its evening peak and export at noon on the same day.

## Sources and credits

- U.S. Energy Information Administration, Form EIA-930.
- The ISOs' public price and queue data (CAISO, ERCOT, ISO New England, MISO, NYISO, SPP).
- Lawrence Berkeley National Laboratory and GridTracker, Queued Up: 2026 Edition data file, licensed CC BY 4.0. The Queued Up data are by Lawrence Berkeley National Laboratory and GridTracker.
- NOAA NCEI (the event studies' weather).
