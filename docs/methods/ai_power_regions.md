# Where the next gigawatts for AI can come from: one row of measures per ISO region

Energy Research Warehouse (ERW), method note written in session 2578 (chain 127) for a derived table first written in session 62. The method itself is the report's methods appendix, [`docs/reports/ai_gigawatts_methods.md`](../reports/ai_gigawatts_methods.md); this note names the table, gives its shape as held, and points there.

Tables: `ai_power_regions`

## Builder and inputs

`warehouse/derived/ai_power_regions.py` (session 62). No request is made. Source id `erw:ai_power_regions`. Its inputs, as its header names them: `cost_of_power_monthly`, `carbon_intensity_daily`, `iso_hub_prices_history`, `ercot_all_hub_prices_history`, `caiso_grid_emergencies`, `event_study_estimates`, Berkeley Lab's and the ISOs' interconnection queues, `eia930_daily_interchange` and `eia930_all_demand`.

## What a row is

Series: one row per ISO region and measure. `entity` `iso:<region>` (caiso, ercot, isone, miso, nyiso, pjm, spp); `x_window` the measure's period; `x_note` its event or snapshot. The unit is a flat 1 GW load for a year (8,760 GWh), and the year is September 2025 to August 2026.

- **Cost:** `flat_rt_price_usd_mwh`, `flat_da_price_usd_mwh`, `flat_1gw_cost_usd` (wholesale energy only).
- **Carbon:** `carbon_intensity_kg_mwh`, `flat_1gw_co2_t`.
- **Stress:** `scarcity_hours_200`, `scarcity_hours_1000`, `max_rt_hour_usd_mwh`, `emergency_days` (CAISO only), the largest event effect and which event it is.
- **Connection:** Berkeley Lab's active queue (MW, requests, median years to commercial operation, completion share) and the ISOs' own queues.
- **Reliance:** net imports against demand from EIA-930.

PJM's prices are licensed for internal use and not held, so PJM has no cost or price-stress measure.

## As held on 25 October 2026

Run `20261002T095758Z`, counted by code from the table read past its header lines: 187 rows, 7 entities, 31 variables, rows dated from July 2018 (a measure's window start) to 30 September 2026.

## License

Public: a derived table takes the most restrictive license of its inputs (Decision 23), here EIA, NOAA, the ISOs' public data, Berkeley Lab and GridTracker (CC BY 4.0). The licence record lists ISO-NE, MISO and NYISO among its sources as needing written permission (the owner's ruling of 21 October 2026 holds it from version 1 of the Redivis release).
