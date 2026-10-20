# The permission tables, for your emails of 14 October

Energy Research Warehouse (ERW), session 324, 19 October 2026. For Samuel: tick the box of each table your email of 14 October asked its publisher about. No record of those emails is in the repository (session 311 searched `docs/`, `archive/sessions/` and `warehouse/metadata/`), so every box is empty. Written by `runs/s324_permissions.py` from session 205's list (`docs/licenses.md` as first committed, 8d791cdc), `warehouse/metadata/license_status.csv` and the verdicts; nothing typed.

## Read these first

- **The 42 are session 205's**, the tables flagged public on 12 October whose publisher's sentence asks for permission: the list your emails of 14 October would have followed. A table under several publishers appears under each.
- **Since then 3 have been retired** (`fred_daily_spot_prices`, `fred_treasury_yields`, `price_board_stats`) **and 2 have joined** (`grid_stress_days`, `scarcity_hours_by_grid`), so 41 show "license needed" from 21 October (`license_status.csv`). The joiners are listed at the end.
- **A permission you hold turns a table back on:** write it into the table's row of `warehouse/metadata/license_status.csv` (`permission`, `permission_ref`), then `python scripts/licenses.py status` and land (`docs/state/licenses_2026-10-21.md`).

## By publisher

### NYISO (29 tables; write to: none named on the page)

- [ ] `ai_power_regions`
- [ ] `battery_stack_review_monthly`
- [ ] `clean_energy_hourly`
- [ ] `clean_energy_summary`
- [ ] `cost_of_power_carbon`
- [ ] `cost_of_power_hourly_profile`
- [ ] `cost_of_power_monthly`
- [ ] `datacenter_facilities`
- [ ] `datacenter_queue_positions`
- [ ] `event_study_estimates`
- [ ] `event_window_daily`
- [ ] `hub_price_comparison`
- [ ] `iso_hub_prices_history`
- [ ] `iso_rt_top_intervals`
- [ ] `iso_trader_daily`
- [ ] `iso_zone_prices_history`
- [ ] `merchant_revenue_monthly`
- [ ] `news_index`
- [ ] `nyiso_as_prices`
- [ ] `nyiso_dam_cleared_energy`
- [ ] `nyiso_dam_zone_prices`
- [ ] `nyiso_interconnection_queue`
- [ ] `nyiso_load_queue`
- [ ] `nyiso_rtm_zone_prices`
- [ ] `nyiso_zone_load_hourly`
- [ ] `price_board_latest`
- [ ] `price_board_peak_offpeak`
- [ ] `price_board_spreads`
- [ ] `price_board_stats` (retired since)

### ISO-NE (25 tables; write to: info@iso-ne.com (the page names it for permission to use a graph, chart or image); Participant Support, (413) 540-4220)

- [ ] `ai_power_regions`
- [ ] `clean_energy_hourly`
- [ ] `clean_energy_summary`
- [ ] `cost_of_power_carbon`
- [ ] `cost_of_power_hourly_profile`
- [ ] `cost_of_power_monthly`
- [ ] `datacenter_facilities`
- [ ] `datacenter_queue_positions`
- [ ] `energy_projects`
- [ ] `event_study_estimates`
- [ ] `event_window_daily`
- [ ] `hub_price_comparison`
- [ ] `iso_hub_prices_history`
- [ ] `iso_rt_top_intervals`
- [ ] `iso_trader_daily`
- [ ] `isone_dam_zone_prices`
- [ ] `isone_interconnection_queue`
- [ ] `isone_rtm_zone_prices`
- [ ] `isone_rtm_zone_prices_hourly`
- [ ] `merchant_revenue_monthly`
- [ ] `news_index`
- [ ] `price_board_latest`
- [ ] `price_board_peak_offpeak`
- [ ] `price_board_spreads`
- [ ] `price_board_stats` (retired since)

### MISO (21 tables; write to: not known: the page was not asked)

- [ ] `ai_power_regions`
- [ ] `clean_energy_hourly`
- [ ] `clean_energy_summary`
- [ ] `cost_of_power_carbon`
- [ ] `cost_of_power_hourly_profile`
- [ ] `cost_of_power_monthly`
- [ ] `datacenter_facilities`
- [ ] `datacenter_queue_positions`
- [ ] `event_study_estimates`
- [ ] `event_window_daily`
- [ ] `hub_price_comparison`
- [ ] `iso_dam_hub_prices`
- [ ] `iso_hub_prices_history`
- [ ] `iso_rtm_hub_prices`
- [ ] `iso_trader_daily`
- [ ] `merchant_revenue_monthly`
- [ ] `miso_interconnection_queue`
- [ ] `news_index`
- [ ] `price_board_latest`
- [ ] `price_board_peak_offpeak`
- [ ] `price_board_spreads`

### Bloomberg (4 tables; write to: none named for permissions in the sentences read)

- [ ] `datacenter_facilities`
- [ ] `datacenter_projects`
- [ ] `energy_deals`
- [ ] `news_index`

### Data Center Dynamics (4 tables; write to: no address on the page read)

- [ ] `datacenter_facilities`
- [ ] `datacenter_projects`
- [ ] `energy_deals`
- [ ] `news_index`

### Data Center Frontier (4 tables; write to: no address on the page read)

- [ ] `datacenter_facilities`
- [ ] `datacenter_projects`
- [ ] `energy_deals`
- [ ] `news_index`

### Financial Times (4 tables; write to: no address on the page read)

- [ ] `datacenter_facilities`
- [ ] `datacenter_projects`
- [ ] `energy_deals`
- [ ] `news_index`

### Hart Energy (4 tables; write to: no address on the page read)

- [ ] `datacenter_facilities`
- [ ] `datacenter_projects`
- [ ] `energy_deals`
- [ ] `news_index`

### Latitude Media (4 tables; write to: no address on the page read)

- [ ] `datacenter_facilities`
- [ ] `datacenter_projects`
- [ ] `energy_deals`
- [ ] `news_index`

### Natural Gas Intelligence (4 tables; write to: info@naturalgasintel.com)

- [ ] `datacenter_facilities`
- [ ] `datacenter_projects`
- [ ] `energy_deals`
- [ ] `news_index`

### POWER Magazine (4 tables; write to: no address on the page read)

- [ ] `datacenter_facilities`
- [ ] `datacenter_projects`
- [ ] `energy_deals`
- [ ] `news_index`

### Reuters (4 tables; write to: no address on the page read)

- [ ] `datacenter_facilities`
- [ ] `datacenter_projects`
- [ ] `energy_deals`
- [ ] `news_index`

### WSJ (4 tables; write to: djreprints.com (the Dow Jones Reprints website, named for licenses))

- [ ] `datacenter_facilities`
- [ ] `datacenter_projects`
- [ ] `energy_deals`
- [ ] `news_index`

### Data Center Knowledge (3 tables; write to: no address on the page read)

- [ ] `datacenter_facilities`
- [ ] `datacenter_projects`
- [ ] `news_index`

### Heatmap News (3 tables; write to: no address on the page read)

- [ ] `datacenter_facilities`
- [ ] `datacenter_projects`
- [ ] `news_index`

### ANS Nuclear Newswire (2 tables; write to: no address on the page read)

- [ ] `energy_deals`
- [ ] `news_index`

### Amazon Web Services (2 tables; write to: no address on the page read)

- [ ] `datacenter_facilities`
- [ ] `datacenter_operator_sites`

### Canary Media (2 tables; write to: no address on the page read)

- [ ] `energy_deals`
- [ ] `news_index`

### Digital Realty (2 tables; write to: no address on the page read)

- [ ] `datacenter_facilities`
- [ ] `datacenter_operator_sites`

### Equinix (2 tables; write to: no address on the page read)

- [ ] `datacenter_facilities`
- [ ] `datacenter_operator_sites`

### FRED (2 tables; write to: none named in the sentences read)

- [ ] `fred_daily_spot_prices` (retired since)
- [ ] `fred_treasury_yields` (retired since)

### Google (2 tables; write to: no address on the page read)

- [ ] `datacenter_facilities`
- [ ] `datacenter_operator_sites`

### JPT (2 tables; write to: no address on the page read)

- [ ] `energy_deals`
- [ ] `news_index`

### LNG Prime (2 tables; write to: its newsdesk)

- [ ] `energy_deals`
- [ ] `news_index`

### Meta (2 tables; write to: no address on the page read)

- [ ] `datacenter_facilities`
- [ ] `datacenter_operator_sites`

### Microsoft (2 tables; write to: no address on the page read)

- [ ] `datacenter_facilities`
- [ ] `datacenter_operator_sites`

### OilPrice.com (2 tables; write to: no address on the page read)

- [ ] `energy_deals`
- [ ] `news_index`

### Oracle (2 tables; write to: no address on the page read)

- [ ] `datacenter_facilities`
- [ ] `datacenter_operator_sites`

### Rigzone (2 tables; write to: no address on the page read)

- [ ] `energy_deals`
- [ ] `news_index`

### Switch (2 tables; write to: no address on the page read)

- [ ] `datacenter_facilities`
- [ ] `datacenter_operator_sites`

### Utility Dive (2 tables; write to: no address on the page read)

- [ ] `energy_deals`
- [ ] `news_index`

### Vantage Data Centers (2 tables; write to: no address on the page read)

- [ ] `datacenter_facilities`
- [ ] `datacenter_operator_sites`

### pv magazine USA (2 tables; write to: no address on the page read)

- [ ] `energy_deals`
- [ ] `news_index`

### CivicPlus (1 tables; write to: no address on the page read)

- [ ] `news_index`

### Hydrogen Insight (1 tables; write to: no address on the page read)

- [ ] `news_index`

## Joined since session 205 (not in your emails of 14 October)

- [ ] `grid_stress_days`: by ISO-NE; MISO; NYISO; license needed from 2026-10-21
- [ ] `scarcity_hours_by_grid`: by ISO-NE; MISO; NYISO; license needed from 2026-10-21
