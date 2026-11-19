# Session 8207 report (chain 502, lab-desktop second window)

19 November 2026, 12:02 to 12:09 UTC. Opus 5.5. Model spend: USD 0. Parts B and C checked at the start: both still waiting (`site/data/industry.json` not on main; `ai_energy_published` not in coverage).

## Family 7, the rest: 18 drafts (FERC 714 forecasts)

- `docs/findings/forecasts/`, loaded in state draft; second pass 18 of 18 reproduce; 18 of 18 do-files hold.
- `ferc714_planning_area_forecasts`: the yearly growth each filing forecasts for a planning area's summer peak, winter peak and net energy, from its first forecast year to its tenth; the newest filing against the first the ERW holds (2006); areas of at least 3,000 MW whose newest filing is 2024 or later.
- The three strongest:
  - ERCOT's 2025 filing forecasts its net energy growing 8.23 percent a year over the decade, against 2.10 percent in its 2006 filing.
  - Georgia Power's 2025 filing: net energy 7.08 percent a year, against 1.90 percent in its 2007 filing.
  - PJM's 2025 filing: net energy 5.54 percent a year, against 1.54 percent in 2006.

## The tables of the ground's family 7 not drafted, and why

- `iso_hub_prices_history_2018`: SPP North Hub only, and SPP is held (rulings of 12 October).
- `iso_queue_statistics` by entry year (ERCOT and CAISO, the public rows): the list the ERW holds starts thin (162 MW entering ERCOT's queue in 2013), so a trend by entry year measures the list's coverage more than the entries. Written and set aside (`runs/c502/dropped/family7.py`, not in git).
- `carbon_intensity_monthly`: the consumed intensity of ERCOT and MISO passes, but repeats family 5's CO2 per MWh generated for the same authorities.
- `utility_large_load_rules`, `state_large_load_laws`, `utility_large_load_queue_totals`: free text or an empty figure column (session 8206).
- `census_county_population`, `noaa_region_stations`, `eia_county_region`, `forecast_tool_parameters`: inputs to other tables, not facts of the energy system on their own.
- Tables with one date or one 2026 span (`datacenter_tracker_rollups`, `deal_counterparties`, `ercot_storage_*_monthly`, `ercot_peak_premium_node_monthly`, `iso_reserve_margin_reports`): no comparison over years to test.
- `eia_steo_forecasts`, `ercot_peak_premium_annual`, `eia_crude_first_purchase_prices`, `imf_commodity_prices`: their themes are chain 164's (ERCOT's price shape, crude, uranium); left to part D.

## Part A done

- Seven families, 158 drafts: trade 34, regions 27, weather 15, events 30, authorities 19, large loads 15, forecasts 18. Each reproduces from its own script.

## Code

- `warehouse/analysis/findings/deep/ferc714.py` on `wip/8202-findings` (`5edc09d21`).

## Needs the key

- Nothing.
