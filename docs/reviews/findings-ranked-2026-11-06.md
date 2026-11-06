# The findings hunt's drafts, ranked (6 November 2026)

Written by session 3020 (chain 164) with `warehouse/analysis/findings/deep/rank.py` from the 156 drafts this chain put on the review list (`public.scanner_drafts`, module `deep.*`, every one still a draft). Nothing here is approved; it is an order to read them in. Each draft is at `/internal/findings` with its chart, its tests, its CSV, its Python and Stata scripts, and in `docs/findings/<family>/`.

## The rubric and its reasoning

- **Consequence (1 to 3):** the candidate's scale, set when it was written: 3 a price shape, a spread worth more than a dollar a MWh over a year, a peak or a fleet in GW, a national share; 2 a region, a technology or a sub-market; 1 a curiosity.
- **Novelty (1 to 3):** 3 unless the ERW already shows the measure. 2 where a page or a weekly hunt pattern shows it for another place or cut (the battery page's spreads, the peak premium explorer's hours, the mix profile); 1 where a page shows it outright (/storage's fleet). The reason is written beside each such draft below.
- **Strength (2 or 3):** every draft passed the hunt's five tests; 3 when its change is at least two typical yearly moves, else 2.
- **Order:** the sum, highest first; ties by the strength in typical moves.

## The drafts by family

| Family | Drafts |
|---|---:|
| cross_family | 8 |
| demand | 12 |
| gas | 11 |
| generation_pipeline | 35 |
| oil_products_world | 18 |
| prices | 33 |
| queues_deals_datacenters | 27 |
| tariffs_policy | 12 |
| all | 156 |

## The twenty to read first

1. **generation_pipeline**, score 9 (consequence 3, novelty 3, strength 3; 121.0 typical moves). The nameplate capacity of batteries, the United States that entered service in the year and operates today was 16,372 MW in 2025, against 0 MW in 2010, the first year this measure counts. `scan-deep-dbdda8d8c6f2`
2. **generation_pipeline**, score 9 (consequence 3, novelty 3, strength 3; 66.0 typical moves). Nuclear's share of net generation in Vermont was 0.0 percent of net generation in 2025, against 76.1 percent of net generation in 2001, the first full year the ERW holds. `scan-deep-dc86397ca7c4`
3. **gas**, score 9 (consequence 3, novelty 3, strength 3; 56.4 typical moves). US pipeline exports of natural gas to Mexico was 2,423 Bcf in 2025, against 14 Bcf in 1973, the first full year the ERW holds. `scan-deep-fc2e875ea6e1`
4. **generation_pipeline**, score 9 (consequence 3, novelty 3, strength 3; 36.6 typical moves). Utility-scale solar's share of net generation in Nevada was 30.8 percent of net generation in 2025, against 0.0 percent of net generation in 2001, the first full year the ERW holds. `scan-deep-e6f61807b161`
5. **generation_pipeline**, score 9 (consequence 3, novelty 3, strength 3; 31.1 typical moves). Utility-scale solar's share of net generation in the United States was 6.8 percent of net generation in 2025, against 0.0 percent of net generation in 2001, the first full year the ERW holds. `scan-deep-74babf6df9f2`
6. **gas**, score 9 (consequence 3, novelty 3, strength 3; 30.1 typical moves). West Virginia's share of US marketed gas production was 8.3 percent of US marketed production in 2025, against 0.9 percent of US marketed production in 2001, the first full year the ERW holds. `scan-deep-0578ec6db1b6`
7. **generation_pipeline**, score 9 (consequence 3, novelty 3, strength 3; 28.4 typical moves). The gas-fired fleet's fuel per MWh in the United States was 8.30 MMBtu per MWh in 2024, against 10.84 MMBtu per MWh in 2001, the first full year the ERW holds. `scan-deep-e2d515f4e468`
8. **gas**, score 9 (consequence 3, novelty 3, strength 3; 28.0 typical moves). Pennsylvania's share of US marketed gas production was 17.8 percent of US marketed production in 2025, against 0.6 percent of US marketed production in 2001, the first full year the ERW holds. `scan-deep-0d768034cd5f`
9. **tariffs_policy**, score 9 (consequence 3, novelty 3, strength 3; 22.3 typical moves). The average residential electricity price in the United States was 172.6 USD per MWh in 2025, against 85.8 USD per MWh in 2001, the first full year the ERW holds. `scan-deep-3a7bd234ee53`
10. **queues_deals_datacenters**, score 9 (consequence 3, novelty 3, strength 3; 20.9 typical moves). The value of private data center construction put in place in the US was 49.74 USD billion in 2025, against 1.80 USD billion in 2014, the first full year the ERW holds. `scan-deep-dd585d3c607b`
11. **generation_pipeline**, score 9 (consequence 3, novelty 3, strength 3; 20.3 typical moves). The gas-fired fleet's fuel per MWh in Florida was 7.48 MMBtu per MWh in 2024, against 9.39 MMBtu per MWh in 2001, the first full year the ERW holds. `scan-deep-9fd4e326766e`
12. **queues_deals_datacenters**, score 9 (consequence 3, novelty 3, strength 3; 19.1 typical moves). Batteries' share of the MW requested in the United States was 29.7 percent of requested MW in 2024, against 0.0 percent of requested MW in 2005, the first year this measure counts. `scan-deep-1fd8bb1d1483`
13. **queues_deals_datacenters**, score 9 (consequence 3, novelty 3, strength 3; 19.1 typical moves). Data centers' share of US private nonresidential construction was 6.35 percent of private nonresidential construction in 2025, against 0.50 percent of private nonresidential construction in 2014, the first full year the ERW holds. `scan-deep-a1a72bdb3de0`
14. **oil_products_world**, score 9 (consequence 3, novelty 3, strength 3; 19.1 typical moves). Texas's share of US crude oil production was 42.2 percent of US crude production in 2025, against 20.0 percent of US crude production in 2001, the first full year the ERW holds. `scan-deep-deffa03e8721`
15. **tariffs_policy**, score 9 (consequence 3, novelty 3, strength 3; 18.9 typical moves). Retail electricity sales to the commercial sector in Texas was 174.7 TWh in 2025, against 87.9 TWh in 2001, the first full year the ERW holds. `scan-deep-cea999e8b1d3`
16. **oil_products_world**, score 9 (consequence 3, novelty 3, strength 3; 18.1 typical moves). Canada's share of US crude oil imports was 63.4 percent of US crude imports in 2025, against 30.9 percent of US crude imports in 1973, the first full year the ERW holds. `scan-deep-15ac3afd0745`
17. **oil_products_world**, score 9 (consequence 3, novelty 3, strength 3; 17.2 typical moves). Alaska's share of US crude oil production was 6.1 percent of US crude production in 2025, against 32.7 percent of US crude production in 2001, the first full year the ERW holds. `scan-deep-9fa18e56c335`
18. **queues_deals_datacenters**, score 9 (consequence 3, novelty 3, strength 3; 16.9 typical moves). The value of private electric power construction put in place in the US was 128.04 USD billion in 2025, against 16.39 USD billion in 1993, the first full year the ERW holds. `scan-deep-ee79f812b00a`
19. **generation_pipeline**, score 9 (consequence 3, novelty 3, strength 3; 16.4 typical moves). Wind's share of net generation in the United States was 10.4 percent of net generation in 2025, against 0.2 percent of net generation in 2001, the first full year the ERW holds. `scan-deep-f02c2bc8cd8a`
20. **generation_pipeline**, score 9 (consequence 3, novelty 3, strength 3; 15.7 typical moves). Coal's share of net generation in the United States was 16.6 percent of net generation in 2025, against 51.0 percent of net generation in 2001, the first full year the ERW holds. `scan-deep-c7c053517090`

## Every draft

| Rank | Score | C | N | S | Moves | Family | Candidate | Region | Draft |
|---:|---:|---:|---:|---:|---:|---|---|---|---|
| 1 | 9 | 3 | 3 | 3 | 121.0 | generation_pipeline | added_mw | add_battery_US | `scan-deep-dbdda8d8c6f2` |
| 2 | 9 | 3 | 3 | 3 | 66.0 | generation_pipeline | nuclear_share | state_nuc_VT | `scan-deep-dc86397ca7c4` |
| 3 | 9 | 3 | 3 | 3 | 56.4 | gas | mexico_exports | us_mexico | `scan-deep-fc2e875ea6e1` |
| 4 | 9 | 3 | 3 | 3 | 36.6 | generation_pipeline | solar_share | state_sun_NV | `scan-deep-e6f61807b161` |
| 5 | 9 | 3 | 3 | 3 | 31.1 | generation_pipeline | solar_share | state_sun_US | `scan-deep-74babf6df9f2` |
| 6 | 9 | 3 | 3 | 3 | 30.1 | gas | state_production_share | prod_WV | `scan-deep-0578ec6db1b6` |
| 7 | 9 | 3 | 3 | 3 | 28.4 | generation_pipeline | gas_heat_rate | hr_gas_US | `scan-deep-e2d515f4e468` |
| 8 | 9 | 3 | 3 | 3 | 28.0 | gas | state_production_share | prod_PA | `scan-deep-0d768034cd5f` |
| 9 | 9 | 3 | 3 | 3 | 22.3 | tariffs_policy | res_price | res_price_US | `scan-deep-3a7bd234ee53` |
| 10 | 9 | 3 | 3 | 3 | 20.9 | queues_deals_datacenters | dc_construction | us_dc_build | `scan-deep-dd585d3c607b` |
| 11 | 9 | 3 | 3 | 3 | 20.3 | generation_pipeline | gas_heat_rate | hr_gas_FL | `scan-deep-9fd4e326766e` |
| 12 | 9 | 3 | 3 | 3 | 19.1 | queues_deals_datacenters | storage_share | us_req_battery_share | `scan-deep-1fd8bb1d1483` |
| 13 | 9 | 3 | 3 | 3 | 19.1 | queues_deals_datacenters | dc_share | us_dc_share | `scan-deep-a1a72bdb3de0` |
| 14 | 9 | 3 | 3 | 3 | 19.1 | oil_products_world | state_crude_share | crude_TX | `scan-deep-deffa03e8721` |
| 15 | 9 | 3 | 3 | 3 | 18.9 | tariffs_policy | commercial_sales | com_sales_TX | `scan-deep-cea999e8b1d3` |
| 16 | 9 | 3 | 3 | 3 | 18.1 | oil_products_world | import_share | imp_CA | `scan-deep-15ac3afd0745` |
| 17 | 9 | 3 | 3 | 3 | 17.2 | oil_products_world | state_crude_share | crude_AK | `scan-deep-9fa18e56c335` |
| 18 | 9 | 3 | 3 | 3 | 16.9 | queues_deals_datacenters | power_construction | us_power_build | `scan-deep-ee79f812b00a` |
| 19 | 9 | 3 | 3 | 3 | 16.4 | generation_pipeline | wind_share | state_wnd_US | `scan-deep-f02c2bc8cd8a` |
| 20 | 9 | 3 | 3 | 3 | 15.7 | generation_pipeline | coal_share | state_cow_US | `scan-deep-c7c053517090` |
| 21 | 9 | 3 | 3 | 3 | 15.4 | generation_pipeline | coal_share | state_cow_NM | `scan-deep-fc5e1d762a8e` |
| 22 | 9 | 3 | 3 | 3 | 13.6 | generation_pipeline | added_mw | add_solar_US | `scan-deep-a222729a0c70` |
| 23 | 9 | 3 | 3 | 3 | 13.2 | oil_products_world | gas_premium | gasprem_R30 | `scan-deep-1304854e183c` |
| 24 | 9 | 3 | 3 | 3 | 12.5 | demand | top_days | ercot_ba | `scan-deep-fd75816434cd` |
| 25 | 9 | 3 | 3 | 3 | 12.4 | oil_products_world | us_liquids_share | us_world_liquids | `scan-deep-3bed96cc151a` |
| 26 | 9 | 3 | 3 | 3 | 11.9 | queues_deals_datacenters | hybrid_share | southeast_lbnl_hybrid | `scan-deep-60e6cbd9b000` |
| 27 | 9 | 3 | 3 | 3 | 11.8 | tariffs_policy | commercial_sales | com_sales_US | `scan-deep-2f409a77aca6` |
| 28 | 9 | 3 | 3 | 3 | 11.5 | generation_pipeline | gas_share | state_ng_DE | `scan-deep-879dc6e37a47` |
| 29 | 9 | 3 | 3 | 3 | 11.5 | gas | shale_share | us_shale | `scan-deep-d6e14ebad25b` |
| 30 | 9 | 3 | 3 | 3 | 11.0 | generation_pipeline | gas_share | state_ng_US | `scan-deep-9c2774360dec` |
| 31 | 9 | 3 | 3 | 3 | 10.6 | generation_pipeline | wind_share | state_wnd_SD | `scan-deep-169f53d4acf2` |
| 32 | 9 | 3 | 3 | 3 | 9.8 | cross_family | storage_per_solar | ercot_bat_solar | `scan-deep-f703dda8e911` |
| 33 | 9 | 3 | 3 | 3 | 8.4 | generation_pipeline | battery_hours | us_battery_hours | `scan-deep-05c99ca8013f` |
| 34 | 9 | 3 | 3 | 3 | 8.4 | queues_deals_datacenters | months_by_region | us_lbnl_months | `scan-deep-3a40649cbec1` |
| 35 | 9 | 3 | 3 | 3 | 8.2 | queues_deals_datacenters | months_by_type | us_type_wind_months | `scan-deep-462f0003f4c4` |
| 36 | 9 | 3 | 3 | 3 | 8.0 | oil_products_world | net_imports | us_net_imports | `scan-deep-10e0e2c5d386` |
| 37 | 9 | 3 | 3 | 3 | 7.5 | gas | power_share | us_power_burn | `scan-deep-7c1da7c0bbd9` |
| 38 | 9 | 3 | 3 | 3 | 7.2 | cross_family | storage_per_solar | us_bat_solar | `scan-deep-3ad64568fb85` |
| 39 | 9 | 3 | 3 | 3 | 7.1 | gas | lng_share | us_lng | `scan-deep-7c7ba78c393d` |
| 40 | 9 | 3 | 3 | 3 | 6.9 | tariffs_policy | res_price | res_price_HI | `scan-deep-3e07973c5f92` |
| 41 | 9 | 3 | 3 | 3 | 6.7 | cross_family | storage_per_solar | caiso_bat_solar | `scan-deep-c41ae534ead9` |
| 42 | 9 | 3 | 3 | 3 | 6.6 | generation_pipeline | nuclear_share | state_nuc_US | `scan-deep-55e4412f65bd` |
| 43 | 9 | 3 | 3 | 3 | 6.6 | queues_deals_datacenters | months_by_region | pjm_lbnl_months | `scan-deep-b087f09de0f6` |
| 44 | 9 | 3 | 3 | 3 | 6.0 | oil_products_world | import_share | imp_NI | `scan-deep-fea3cf0e9244` |
| 45 | 9 | 3 | 3 | 3 | 5.8 | cross_family | battery_per_peak | ercot_bat_peak | `scan-deep-6946a9ef098b` |
| 46 | 9 | 3 | 3 | 3 | 5.5 | oil_products_world | gasoline_crack | crack_gasoline | `scan-deep-960efb8eb1e1` |
| 47 | 9 | 3 | 3 | 3 | 4.8 | cross_family | battery_per_peak | us_bat_peak | `scan-deep-8a517c868c02` |
| 48 | 9 | 3 | 3 | 3 | 4.4 | demand | mean_day | ercot_ba | `scan-deep-f9e530bab496` |
| 49 | 9 | 3 | 3 | 3 | 4.2 | queues_deals_datacenters | withdrawn_share | us_lbnl_wd | `scan-deep-72e9a2889ce4` |
| 50 | 9 | 3 | 3 | 3 | 4.2 | cross_family | battery_per_peak | caiso_bat_peak | `scan-deep-8d4c08a1fc82` |
| 51 | 9 | 3 | 3 | 3 | 4.1 | prices | europe_gas_premium | us_europe_gas | `scan-deep-f01a569678ac` |
| 52 | 9 | 3 | 3 | 3 | 4.1 | demand | sub_p99 | pjm_sub_DOM | `scan-deep-19bbb7ecebde` |
| 53 | 9 | 3 | 3 | 3 | 3.8 | queues_deals_datacenters | hybrid_share | us_lbnl_hybrid | `scan-deep-55cf9c67bd30` |
| 54 | 9 | 3 | 3 | 3 | 3.5 | queues_deals_datacenters | months_by_type | us_type_solar_months | `scan-deep-1e1ec3f4c6cf` |
| 55 | 9 | 3 | 3 | 3 | 3.2 | demand | sub_mean | ercot_sub_FWES | `scan-deep-5d357242de6d` |
| 56 | 9 | 3 | 3 | 3 | 3.1 | tariffs_policy | saidi | saidi_NE | `scan-deep-1483006a7d41` |
| 57 | 9 | 3 | 3 | 3 | 3.1 | demand | sub_mean | pjm_sub_DOM | `scan-deep-99a9fa233018` |
| 58 | 9 | 3 | 3 | 3 | 3.1 | generation_pipeline | us_nuclear_capacity | us_nuclear_cap | `scan-deep-4fcc17900596` |
| 59 | 9 | 3 | 3 | 3 | 3.0 | demand | sub_p99 | ercot_sub_FWES | `scan-deep-fa9adfc32032` |
| 60 | 9 | 3 | 3 | 3 | 2.6 | demand | winter_vs_summer | ba_soco | `scan-deep-bc17ba25950a` |
| 61 | 9 | 3 | 3 | 3 | 2.5 | demand | top_days | us48 | `scan-deep-9c50aad59286` |
| 62 | 9 | 3 | 3 | 3 | 2.1 | queues_deals_datacenters | withdrawn_share | pjm_lbnl_wd | `scan-deep-93e08e83729d` |
| 63 | 8 | 2 | 3 | 3 | 74.6 | queues_deals_datacenters | requested_by_type | us_req_battery | `scan-deep-3f1caaff9a19` |
| 64 | 8 | 2 | 3 | 3 | 24.2 | queues_deals_datacenters | withdrawn_by_type | us_type_solar_wd | `scan-deep-58bdd2d65c59` |
| 65 | 8 | 2 | 3 | 3 | 22.4 | prices | residential_markup | state_res_CA | `scan-deep-36df813be89c` |
| 66 | 8 | 2 | 3 | 3 | 21.9 | tariffs_policy | res_over_ind | res_ind_gap_US | `scan-deep-45a2cdbdc53c` |
| 67 | 8 | 2 | 3 | 3 | 21.8 | queues_deals_datacenters | hosting_revenue | us_rev518 | `scan-deep-14b8c3d3809e` |
| 68 | 8 | 2 | 3 | 3 | 18.3 | prices | residential_markup | state_res_VT | `scan-deep-434f65fce867` |
| 69 | 8 | 2 | 3 | 3 | 17.5 | queues_deals_datacenters | request_size | us_type_solar_size | `scan-deep-806f7662cfe8` |
| 70 | 8 | 2 | 3 | 3 | 16.2 | generation_pipeline | turbine_kw | us_turbine_kw | `scan-deep-ca16b8ec9d96` |
| 71 | 8 | 2 | 3 | 3 | 15.8 | tariffs_policy | res_over_ind | res_ind_gap_MI | `scan-deep-25c23e4885ff` |
| 72 | 8 | 2 | 3 | 3 | 15.6 | prices | industrial_vs_citygate | state_ind_CA | `scan-deep-9305cfa9e8d7` |
| 73 | 8 | 2 | 3 | 3 | 15.2 | prices | industrial_vs_citygate | state_ind_MI | `scan-deep-71847f516518` |
| 74 | 8 | 2 | 3 | 3 | 13.7 | generation_pipeline | turbine_rotor | us_turbine_rotor | `scan-deep-4dd4f313b2f6` |
| 75 | 8 | 2 | 3 | 3 | 13.5 | generation_pipeline | res_pv_price | tts_res_CA | `scan-deep-af2dc7748c3c` |
| 76 | 8 | 2 | 3 | 3 | 13.1 | oil_products_world | us_ngpl_share | us_world_ngpl | `scan-deep-c17e0814cc1d` |
| 77 | 8 | 2 | 3 | 3 | 12.8 | queues_deals_datacenters | hosting_sites | est518_US | `scan-deep-64e34aef7b05` |
| 78 | 8 | 2 | 3 | 3 | 12.8 | generation_pipeline | hydro_share | state_hyc_VT | `scan-deep-5498dfb70ce7` |
| 79 | 8 | 2 | 3 | 3 | 12.6 | gas | flared_share | flare_LA | `scan-deep-4631e32a866a` |
| 80 | 8 | 2 | 3 | 3 | 12.6 | oil_products_world | pump_over_spot | us_pump_spot | `scan-deep-4ec5d417fc01` |
| 81 | 8 | 2 | 3 | 3 | 12.3 | generation_pipeline | coal_heat_rate | hr_coal_PA | `scan-deep-92152fa1deb6` |
| 82 | 8 | 2 | 3 | 3 | 12.1 | generation_pipeline | res_pv_price | tts_res_MA | `scan-deep-1684caf0fa14` |
| 83 | 8 | 2 | 3 | 3 | 11.6 | oil_products_world | sulfur_content | us_sulfur | `scan-deep-1df42fc6e86d` |
| 84 | 8 | 2 | 3 | 3 | 10.8 | gas | state_power_share | burn_NH | `scan-deep-998f86c36de8` |
| 85 | 8 | 3 | 2 | 3 | 10.4 | prices | cheapest_hour | ercot_HB_SOUTH | `scan-deep-2575e2a95070` |
| 86 | 8 | 2 | 3 | 3 | 10.1 | oil_products_world | supplied_gasoline | us_supplied_gasoline | `scan-deep-201f5379da4a` |
| 87 | 8 | 2 | 3 | 3 | 10.0 | gas | state_power_share | burn_PA | `scan-deep-776d5abbc30d` |
| 88 | 8 | 2 | 3 | 3 | 9.2 | oil_products_world | refining_capacity | us_refining_capacity | `scan-deep-5166e2ebeea5` |
| 89 | 8 | 2 | 3 | 3 | 9.1 | generation_pipeline | small_solar_ratio | state_dpv_MA | `scan-deep-bb58cb4d30cb` |
| 90 | 8 | 3 | 2 | 3 | 8.9 | prices | cheapest_hour | ercot_HB_NORTH | `scan-deep-246cb7930280` |
| 91 | 8 | 2 | 3 | 3 | 8.8 | tariffs_policy | net_metered | nem_US | `scan-deep-8b410b7a1fb4` |
| 92 | 8 | 2 | 3 | 3 | 8.0 | generation_pipeline | small_solar_ratio | state_dpv_US | `scan-deep-270472592e21` |
| 93 | 8 | 2 | 3 | 3 | 7.8 | queues_deals_datacenters | hosting_jobs | jobs518_CA | `scan-deep-4b922e23058f` |
| 94 | 8 | 2 | 3 | 3 | 7.8 | tariffs_policy | net_metered | nem_CA | `scan-deep-1902482e45f7` |
| 95 | 8 | 2 | 3 | 3 | 7.7 | gas | flared_share | flare_WY | `scan-deep-cb0428da3115` |
| 96 | 8 | 2 | 3 | 3 | 7.6 | queues_deals_datacenters | requested_by_type | us_req_solar | `scan-deep-cdf5f79c521a` |
| 97 | 8 | 2 | 3 | 3 | 7.1 | prices | lcfs_credit_price | us_ca_lcfs | `scan-deep-5f1311606943` |
| 98 | 8 | 2 | 3 | 3 | 6.8 | queues_deals_datacenters | hosting_sites | est518_CA | `scan-deep-651294f23fc1` |
| 99 | 8 | 2 | 3 | 3 | 6.4 | demand | sub_night_share | pjm_sub_BC | `scan-deep-0f5a1fecd0f8` |
| 100 | 8 | 2 | 3 | 3 | 6.3 | generation_pipeline | hydro_share | state_hyc_ID | `scan-deep-5b3aa3ba26bb` |
| 101 | 8 | 2 | 3 | 3 | 6.2 | prices | hour_to_hour_move | ercot_HB_HOUSTON | `scan-deep-4af800b86a3a` |
| 102 | 8 | 2 | 3 | 3 | 6.2 | queues_deals_datacenters | hosting_jobs | jobs518_US | `scan-deep-5ef3c6f444d9` |
| 103 | 8 | 2 | 3 | 3 | 5.9 | prices | carb_allowance_price | us_ca_allowance | `scan-deep-5671faf8f993` |
| 104 | 8 | 2 | 3 | 3 | 5.6 | oil_products_world | diesel_premium | us_diesel_premium | `scan-deep-e68a3453e8ec` |
| 105 | 8 | 2 | 3 | 3 | 5.6 | demand | sub_night_share | pjm_sub_CE | `scan-deep-d52decf44c60` |
| 106 | 8 | 2 | 3 | 3 | 5.4 | generation_pipeline | coal_heat_rate | hr_coal_US | `scan-deep-86882524bc40` |
| 107 | 8 | 2 | 3 | 3 | 5.2 | prices | hour_to_hour_move | ercot_HB_SOUTH | `scan-deep-e814d43a8641` |
| 108 | 8 | 2 | 3 | 3 | 5.1 | oil_products_world | api_gravity | us_api_gravity | `scan-deep-0607c5f8ab90` |
| 109 | 8 | 2 | 3 | 3 | 5.0 | cross_family | built_per_asked | us_battery_built_asked | `scan-deep-5f1d006e0f13` |
| 110 | 8 | 3 | 2 | 3 | 5.0 | prices | spread_4h | ercot_HB_WEST | `scan-deep-0ffe99affaf3` |
| 111 | 8 | 3 | 2 | 3 | 5.0 | generation_pipeline | solar_midday_share | ercot_mix | `scan-deep-aff73c06925b` |
| 112 | 8 | 3 | 2 | 3 | 4.7 | prices | daily_spread | ercot_HB_WEST | `scan-deep-a2e22707d072` |
| 113 | 8 | 3 | 2 | 3 | 4.5 | prices | midday_discount | ercot_LZ_WEST | `scan-deep-ec2251cf2ae7` |
| 114 | 8 | 2 | 3 | 3 | 4.2 | oil_products_world | jet_crack | crack_jet | `scan-deep-bb200e252fa1` |
| 115 | 8 | 2 | 3 | 3 | 4.2 | queues_deals_datacenters | request_size | us_type_wind_size | `scan-deep-b02935a8e929` |
| 116 | 8 | 2 | 3 | 3 | 4.1 | queues_deals_datacenters | request_size | us_type_battery_size | `scan-deep-6ca546fc88a0` |
| 117 | 8 | 3 | 2 | 3 | 4.0 | prices | daily_spread | ercot_HB_SOUTH | `scan-deep-de3c20a9ed97` |
| 118 | 8 | 2 | 3 | 3 | 3.9 | tariffs_policy | ami_share | ami_IL | `scan-deep-5d99205b850f` |
| 119 | 8 | 2 | 3 | 3 | 3.7 | tariffs_policy | ami_share | ami_US | `scan-deep-bd4ddaf8e303` |
| 120 | 8 | 2 | 3 | 3 | 3.5 | prices | power_vs_citygate | state_pow_NE | `scan-deep-8686ad3a7888` |
| 121 | 8 | 3 | 2 | 3 | 3.5 | prices | spread_4h | ercot_HB_HUBAVG | `scan-deep-e6952da61753` |
| 122 | 8 | 2 | 3 | 3 | 3.5 | prices | japan_lng_premium | us_japan_lng | `scan-deep-d6e2173a680c` |
| 123 | 8 | 2 | 3 | 3 | 3.5 | cross_family | built_per_asked | us_solar_built_asked | `scan-deep-a1b3df8569b3` |
| 124 | 8 | 2 | 3 | 3 | 3.2 | prices | power_vs_citygate | state_pow_WV | `scan-deep-3e515c514c2d` |
| 125 | 8 | 2 | 3 | 3 | 3.2 | queues_deals_datacenters | requested_by_type | us_req_gas | `scan-deep-58c11e815e84` |
| 126 | 8 | 2 | 3 | 3 | 3.2 | prices | brent_wti_spread | us_brent_wti | `scan-deep-602c1f95afe4` |
| 127 | 8 | 3 | 2 | 3 | 2.9 | generation_pipeline | solar_midday_share | caiso_mix | `scan-deep-42891ac362d0` |
| 128 | 8 | 2 | 3 | 3 | 2.7 | prices | da_above_rt_share | ercot_LZ_WEST | `scan-deep-fd76c0c06802` |
| 129 | 8 | 2 | 3 | 3 | 2.5 | oil_products_world | propane_to_crude | us_propane_crude | `scan-deep-479fe9a50745` |
| 130 | 8 | 3 | 2 | 3 | 2.5 | prices | midday_discount | ercot_LZ_SOUTH | `scan-deep-3da968045e4d` |
| 131 | 8 | 3 | 3 | 2 | 1.9 | oil_products_world | gas_premium | gasprem_SCA | `scan-deep-e4ec068bcbd3` |
| 132 | 8 | 3 | 3 | 2 | 1.7 | tariffs_policy | saidi | saidi_MO | `scan-deep-4d2d647be64d` |
| 133 | 8 | 3 | 3 | 2 | 1.6 | demand | winter_vs_summer | ba_tva | `scan-deep-9e2c143415fc` |
| 134 | 8 | 3 | 3 | 2 | 1.6 | demand | mean_day | us48 | `scan-deep-ae89247e0230` |
| 135 | 8 | 3 | 3 | 2 | 1.3 | queues_deals_datacenters | months_by_type | us_type_battery_months | `scan-deep-5cae45311577` |
| 136 | 7 | 3 | 1 | 3 | 14.6 | generation_pipeline | battery_fleet_mw | us_fleet_battery_operating_mw | `scan-deep-cace35476103` |
| 137 | 7 | 1 | 3 | 3 | 11.2 | queues_deals_datacenters | hosting_pay | pay518_US | `scan-deep-1f413dfcbd8e` |
| 138 | 7 | 3 | 1 | 3 | 9.2 | generation_pipeline | battery_fleet_mw | caiso_fleet_battery_operating_mw | `scan-deep-42c7b168c0a1` |
| 139 | 7 | 1 | 3 | 3 | 7.4 | queues_deals_datacenters | hosting_pay | pay518_NY | `scan-deep-5617da2c6d05` |
| 140 | 7 | 2 | 2 | 3 | 5.1 | prices | wide_spread_days | ercot_LZ_WEST | `scan-deep-7f9685056a5a` |
| 141 | 7 | 1 | 3 | 3 | 4.7 | generation_pipeline | reactor_outage_days | nuc_6152_2 | `scan-deep-74d24dc0ef94` |
| 142 | 7 | 2 | 2 | 3 | 3.5 | prices | wide_spread_days | ercot_LZ_NORTH | `scan-deep-e9841ce1dca1` |
| 143 | 7 | 2 | 3 | 2 | 1.8 | prices | henry_hub_volatility | us_henry_hub | `scan-deep-0226feeb5cde` |
| 144 | 7 | 3 | 2 | 2 | 1.7 | generation_pipeline | gas_evening_share | caiso_mix | `scan-deep-6deaba8ca881` |
| 145 | 7 | 3 | 2 | 2 | 1.7 | prices | midday_minus_night | ercot_LZ_WEST | `scan-deep-fafffdc2c9f0` |
| 146 | 7 | 2 | 3 | 2 | 1.6 | prices | winter_top_share | ercot_LZ_WEST | `scan-deep-6f0131013626` |
| 147 | 7 | 3 | 2 | 2 | 1.6 | prices | evening_premium | ercot_LZ_HOUSTON | `scan-deep-83ca4deea096` |
| 148 | 7 | 3 | 2 | 2 | 1.5 | prices | evening_premium | ercot_HB_SOUTH | `scan-deep-0ff3c59ac283` |
| 149 | 7 | 2 | 3 | 2 | 1.4 | gas | storage_outside | stor_salt | `scan-deep-d319970c5c19` |
| 150 | 7 | 2 | 3 | 2 | 1.3 | prices | da_above_rt_share | ercot_LZ_SOUTH | `scan-deep-8144236bc4fd` |
| 151 | 7 | 2 | 3 | 2 | 1.2 | prices | winter_top_share | ercot_LZ_NORTH | `scan-deep-7bfd2eb8c1b9` |
| 152 | 6 | 2 | 1 | 3 | 6.8 | generation_pipeline | fleet_hours | ercot_fleet_battery_operating_mwh_per_mw | `scan-deep-b65761b2cde3` |
| 153 | 6 | 2 | 1 | 3 | 6.2 | generation_pipeline | fleet_hours | us_fleet_battery_operating_mwh_per_mw | `scan-deep-2d084fa894ec` |
| 154 | 6 | 2 | 2 | 2 | 1.6 | prices | top_days_share | ercot_HB_HOUSTON | `scan-deep-992ff5bf34d9` |
| 155 | 6 | 1 | 3 | 2 | 1.3 | generation_pipeline | reactor_outage_days | nuc_6038_1 | `scan-deep-a76fd4282570` |
| 156 | 6 | 2 | 2 | 2 | 1.2 | prices | top_days_share | ercot_HB_SOUTH | `scan-deep-7dfd2bf8b8c6` |
