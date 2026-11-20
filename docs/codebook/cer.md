# Codebook: cer

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 3 public tables (3 series; tiers: 3 source); 0 documented in full.

- [`cer_electricity_trade`](#cer_electricity_trade): the Canada Energy Regulator, Canada's electricity trade with the U.S., a month, and each province's exports to each state, a year (session 887)
- [`cer_gas_trade`](#cer_gas_trade): the Canada Energy Regulator, Canada's natural gas trade with the U.S., a month: pipeline exports in total and by U.S. region, LNG exports, the export price, and historical imports (session 910)
- [`cer_pipeline_throughput`](#cer_pipeline_throughput): Canada Energy Regulator (CER), Pipeline Throughput and Capacity Data, the nine pipelines that cross the U.S. border (session 2169)

### `cer_electricity_trade`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1136.

- **Source:** cer:electricity_trade_summary Canada Energy Regulator, Electricity Trade Summary (compiled from the CER's monthly Commodity Statistics) (https://www.cer-rec.gc.ca/en/data-analysis/energy-commodities/electricity/statistics/electricity-trade-summary/)
- **Method note:** [`docs/methods/cer_electricity_trade.md`](../methods/cer_electricity_trade.md)
- **Cite as:** Canada Energy Regulator (CER). Electricity Trade Summary. Via the Energy Research Warehouse (ERW), table `cer_electricity_trade`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example cer_trade:AB:AR, cer_trade:AB:AZ, cer_trade:AB:CA; 93 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2010-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 199 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 12643262.0; 1086 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M, P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | CA, CA-AB, CA-BC, CA-MB, CA-NB, CA-NL, CA-NS, CA-NU, CA-ON, CA-QC, CA-SK | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 1136 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example Alberta to Arizona, Alberta to Arkansas, Alberta to California; 94 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | cer:electricity_trade_summary | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.cer-rec.gc.ca/en/data-analysis/energy-commodities/electricity/statistics/electricity-trade-summary/electricity-trades-summary-resume-echanges-commerciaux-electricite.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T05:02:35Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 1136 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `exports` |  | MWh | 937 | 2010-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `imports` |  | MWh | 199 | 2010-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `cer_gas_trade`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1427.

- **Source:** cer:natural_gas_trade_summary Canada Energy Regulator, Natural Gas Trade Summary (compiled from the CER's monthly Commodity Statistics) (https://www.cer-rec.gc.ca/en/data-analysis/energy-commodities/natural-gas/statistics/natural-gas-trade-summary/index.html)
- **Method note:** [`docs/methods/cer_gas_trade.md`](../methods/cer_gas_trade.md)
- **Cite as:** Canada Energy Regulator (CER). Natural Gas Trade Summary. Via the Energy Research Warehouse (ERW), table `cer_gas_trade`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | cer_gas_trade:CA, cer_gas_trade:CA:LNG, cer_gas_trade:CA:US_EAST, cer_gas_trade:CA:US_MIDWEST, cer_gas_trade:CA:US_WEST | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2010-01-01T00:00:00Z to 2025-12-01T00:00:00Z; 192 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 332410409.6888432; 1416 distinct | 0 |
| `unit` | The unit of the row's value | none | text | Mcf, USD/MMBtu | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 1427 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | Canada, LNG exports (gaseous equivalent), Canada, natural gas export price, Canada, natural gas import price, Canada, natural gas imports from the U.S., Canada, natural gas pipeline exports to the U.S., Canada, natural gas pipeline exports to the U.S. East, Canada, natural gas pipeline exports to the U.S. Midwest, Canada, natural gas pipeline exports to the U.S. West | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | cer:natural_gas_trade_summary | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.cer-rec.gc.ca/en/data-analysis/energy-commodities/natural-gas/statistics/natural-gas-trade-summary/natural-gas-trades-summary-resume-echanges-commerciaux-gaz-naturel.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T08:01:13Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-04-01T18:56:47Z | 0 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `export_price` |  | USD/MMBtu | 192 | 2010-01-01T00:00:00Z | 2025-12-01T00:00:00Z |
| `exports` |  | Mcf | 923 | 2010-01-01T00:00:00Z | 2025-12-01T00:00:00Z |
| `import_price` |  | USD/MMBtu | 156 | 2010-01-01T00:00:00Z | 2022-12-01T00:00:00Z |
| `imports` |  | Mcf | 156 | 2010-01-01T00:00:00Z | 2022-12-01T00:00:00Z |

### `cer_pipeline_throughput`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 408073.

- **Source:** cer:throughput_capacity Canada Energy Regulator, Pipeline Throughput and Capacity Data (open.canada.ca) (https://open.canada.ca/data/en/dataset/dc343c43-a592-4a27-8ee7-c77df56afb34)
- **Method note:** [`docs/methods/cer_pipeline_throughput.md`](../methods/cer_pipeline_throughput.md)
- **Cite as:** Canada Energy Regulator (CER), Open Government Licence - Canada. Pipeline Throughput and Capacity Data (nine cross-border pipelines). Via the Energy Research Warehouse (ERW), table `cer_pipeline_throughput`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example cer_pipe:alliance_pipeline:border:southeast, cer_pipe:alliance_pipeline:zone_2:southeast, cer_pipe:cochin_pipeline:ft_saskatchewan; 54 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2006-01-01T00:00:00Z to 2026-06-30T00:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -943910.533 to 209646227.9; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | m3/d | 0 |
| `freq` | How long the interval of the row is | none | text | P1D, P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 408073 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example Alliance pipeline, Border, Alliance pipeline, Zone 2, Cochin pipeline, Ft. Saskatchewan; 44 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | cer:throughput_capacity | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.cer-rec.gc.ca/open/energy/throughput-capacity/alliance-throughput-and-capacity.csv, https://www.cer-rec.gc.ca/open/energy/throughput-capacity/cochin-throughput-and-capacity.csv, https://www.cer-rec.gc.ca/open/energy/throughput-capacity/enbridge-mainline-throughput-and-capacity.csv, https://www.cer-rec.gc.ca/open/energy/throughput-capacity/foothills-throughput-and-capacity.csv, https://www.cer-rec.gc.ca/open/energy/throughput-capacity/keystone-throughput-and-capacity.csv, https://www.cer-rec.gc.ca/open/energy/throughput-capacity/mnp-throughput-and-capacity.csv, https://www.cer-rec.gc.ca/open/energy/throughput-capacity/southern-lights-throughput-and-capacity.csv, https://www.cer-rec.gc.ca/open/energy/throughput-capacity/tcpl-mainline-throughput-and-capacity.csv, https://www.cer-rec.gc.ca/open/energy/throughput-capacity/westcoast-throughput-and-capacity.csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T00:41:07Z, 2026-10-24T00:41:08Z, 2026-10-24T00:42:39Z, 2026-10-24T00:46:03Z, 2026-10-24T00:46:04Z, 2026-10-24T00:46:05Z, 2026-10-24T00:46:07Z, 2026-10-24T00:46:10Z, 2026-10-24T00:46:14Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-08-27T21:29:23Z, 2026-08-27T21:29:24Z, 2026-08-27T21:29:25Z, 2026-08-27T21:29:45Z, 2026-08-27T21:29:56Z, 2026-08-27T21:30:11Z, 2026-08-27T21:32:40Z, 2026-08-27T21:33:30Z | 0 |
| `x_company` | not yet written |  | text | Alliance Pipeline Ltd., Enbridge Pipelines Inc., Enbridge Southern Lights GP Inc. on behalf of Enbridge Southern Lights LP, Foothills Pipe Lines Ltd., Maritimes & Northeast Pipeline Management Ltd., PKM Cochin ULC, South Bow GP (Canada) Ltd., TransCanada PipeLines Limited (TCPL), Westcoast Energy Inc. | 0 |
| `x_direction` | not yet written |  | text | east, north, north-west, south, southeast, west | 414 |
| `x_trade_type` | not yet written |  | text | export, import, intracanada, intracanada / export | 414 |
| `x_latitude` | not yet written |  | number | 42.28 to 55.8643; 27 distinct | 180 |
| `x_longitude` | not yet written |  | number | -122.22 to -67.4545; 27 distinct | 180 |
| `x_reason` | not yet written |  | text | A, As previously indicated, the Canadian portion of the Cochin pipeline has a higher nameplate capacity (110,000 bpd) as compared to the US portion of Cochin (95,000 bpd). Now that a new receipt point at Maxbass, ND has been placed into service, the Canadian Cochin capacity is 110,000 bpd and is no longer restricted by the US Cochin nameplate capacity of 95,000 barrels per day., Capacity may vary month to month based on CER Regulatory Directive, Downstream Restrictions, Curtailment/Interruptions, Force Majeure and System Operating Factor, Capacity may vary month to month based on NEB Regulatory Directive, Downstream Restrictions, Curtailment/Interruptions, Force Majeure and System Operating Factor, DOWNSTREAM RESTRICTIONS, DOWNSTREAM RESTRICTIONS , CURTAILMENT/INTERRUPTION, DOWNSTREAM RESTRICTIONS , FORCE MAJEURE, NEB/REGULATORY DIRECTIVE, The Canadian portion of the Cochin pipeline has a higher nameplate capacity as compared to the US portion of Cochin. Since Kankakee, IL, USA is currently the sole receipt point into Cochin, the Canadian Cochin capacity is restricted by the US Cochin nameplate capacity of 95,000 barrels per day, The Canadian portion of the Cochin pipeline has a nameplate capacity of 110,000 bpd (17.49 10^3 m/3) but is restricted by the US portion of Cochin, which currently has a capacity of 105,000 bpd (16.69 10^3 m/3)., The Canadian portion of the Cochin pipeline has a nameplate capacity of 110,000 bpd (17.49 10^3 m/3) but is restricted by the US portion of Cochin, which currently has a capacity of 95,000 bpd (15.10 10^3 m/3). | 404537 |

Variables (6):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `available_capacity` |  | m3/d | 906 | 2007-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `capacity` |  | m3/d | 201956 | 2006-01-01T00:00:00Z | 2026-06-30T00:00:00Z |
| `committed_volume` |  | m3/d | 138 | 2015-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `nameplate_capacity` |  | m3/d | 468 | 2007-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `throughput` |  | m3/d | 204467 | 2006-01-01T00:00:00Z | 2026-06-30T00:00:00Z |
| `uncommitted_volume` |  | m3/d | 138 | 2015-01-01T00:00:00Z | 2026-06-01T00:00:00Z |

