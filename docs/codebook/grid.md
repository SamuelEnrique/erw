# Codebook: grid

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 5 public tables (5 series; tiers: 5 derived); 5 documented in full.

- [`grid_network_links`](#grid_network_links): One pair of balancing authorities in one hour of the last week held, the flow between them.
- [`grid_network_nodes`](#grid_network_nodes): One balancing authority's value of one measure of the grid network, over the last week held or, for the seven ISO authorities, in the latest hour held.
- [`grid_peak_vs_capacity`](#grid_peak_vs_capacity): One ISO grid's value of one measure setting its peak demand of the last whole year against the net summer capacity of its balancing authority's generators.
- [`grid_stress_days`](#grid_stress_days): One grid's stress day by one rule (the day's real-time price above the trailing 98th percentile, or an operator's emergency notice), with the day's mean real-time price at its main hub.
- [`grid_stress_yearly`](#grid_stress_yearly): One ISO grid's value of one measure of how hard the grid works in one local year (evening ramp, lowest net load, the tightest hours, dark and calm stretches).

### `grid_network_links`

One pair of balancing authorities in one hour of the last week held, the flow between them.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 26400.

- **Time:** ts_utc is the hour's start, UTC, from eia930_all_interchange; the window is the 168 hours ending one hour after the newest hour that table holds.
- **Revisions:** A rolling snapshot, deleted and written whole by each daily run of the builder; vintage is not filled.
- **Source:** erw:grid_network ERW derived table, grid network method (docs/methods/grid_network.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/grid_network.md)
- **Method note:** [`docs/methods/grid_network_links.md`](../methods/grid_network_links.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The grid network (warehouse/derived/grid_network.py). Via the Energy Research Warehouse (ERW), table `grid_network_links`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia930:<A>-<B>, A the code that sorts first | none | text | for example eia930:AECI-MISO, eia930:AECI-SIKE, eia930:AECI-SPA; 158 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-10-22T00:00:00Z to 2026-10-28T23:00:00Z; 168 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -4133.0 to 3134.0; 3598 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | empty | no cell holds a value | 26400 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 26400 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 26400 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:grid_network | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/grid_network.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T14:39:23Z, 2026-10-25T14:35:56Z, 2026-10-26T14:39:51Z, 2026-10-27T14:39:25Z, 2026-10-28T14:46:27Z, 2026-10-29T14:36:28Z, 2026-10-30T14:43:28Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 26400 |
| `ba` | The balancing authority (the grid operator of an area) in EIA's code, lowercase (ciso, erco, us48). Here: A, the authority of the pair whose code sorts first | none | text | for example aeci, aeso, ava; 55 distinct | 0 |
| `x_to_ba` | B, the other authority of the pair (the code that sorts second), EIA-930 code in lowercase | none | text | for example bpat, chpd, ciso; 50 distinct | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `flow_mw` | Flow between the two authorities in the hour, MW: positive when A exported to B; read from A's report, or from B's with the sign flipped in an hour A did not report | MW | 26400 | 2026-10-22T00:00:00Z | 2026-10-28T23:00:00Z |

### `grid_network_nodes`

One balancing authority's value of one measure of the grid network, over the last week held or, for the seven ISO authorities, in the latest hour held.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 84.

- **Time:** interchange_volume_mwh: ts_utc is the first hour of the 168-hour window (freq PT168H); demand_mw and intensity_generation: ts_utc is the start of the latest hour held, UTC (freq PT1H).
- **Revisions:** A rolling snapshot, rewritten whole by each build of the builder; vintage is not filled.
- **Source:** erw:grid_network ERW derived table, grid network method (docs/methods/grid_network.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/grid_network.md)
- **Method note:** [`docs/methods/grid_network.md`](../methods/grid_network.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The grid network (warehouse/derived/grid_network.py). Via the Energy Research Warehouse (ERW), table `grid_network_nodes`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia930:<code>, one per balancing authority in the window; EIA's regions and country totals are left out | none | text | for example eia930:AECI, eia930:AESO, eia930:AVA; 70 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-11-08T00:00:00Z, 2026-11-12T23:00:00Z, 2026-11-15T23:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 1266462.0; 83 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, kgCO2/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT168H, PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | empty | no cell holds a value | 84 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 84 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 84 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:grid_network | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/grid_network.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-15T14:59:29Z, 2026-11-16T14:37:54Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 84 |
| `ba` | The balancing authority (the grid operator of an area) in EIA's code, lowercase (ciso, erco, us48) | none | text | for example aeci, aeso, ava; 70 distinct | 0 |
| `x_name` | The authority's name as EIA writes it | none | text | for example Alberta Electric System Operator, Alcoa Power Generating, Inc. - Yadkin Division, Arizona Public Service Company; 70 distinct | 0 |
| `x_iso` | The ISO the authority is, where it is one of the seven (CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP) | none | text | CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP | 63: The authority is not one of the seven ISOs |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `demand_mw` | Demand in the latest hour held (the seven ISO authorities only) | MW | 7 | 2026-11-15T23:00:00Z | 2026-11-15T23:00:00Z |
| `intensity_generation` | Carbon intensity of generation in the latest hour held, kg of CO2 per MWh (the seven ISO authorities only) | kgCO2/MWh | 7 | 2026-11-12T23:00:00Z | 2026-11-12T23:00:00Z |
| `interchange_volume_mwh` | The sum over the window of the absolute hourly flow on every link of the authority | MWh | 70 | 2026-11-08T00:00:00Z | 2026-11-08T00:00:00Z |

### `grid_peak_vs_capacity`

One ISO grid's value of one measure setting its peak demand of the last whole year against the net summer capacity of its balancing authority's generators.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 56.

- **Time:** ts_utc is 1 January of the peak's year at 00:00:00Z (freq P1Y); x_at is the peak hour's start, UTC.
- **Revisions:** Rewritten whole by each run of the builder (a snapshot); vintage is not filled, and x_vintage holds the month of the EIA-860M list read.
- **Source:** eia:930 and eia:860m U.S. Energy Information Administration, Form EIA-930 Hourly Electric Grid Monitor and Form EIA-860M Monthly Update to the Annual Electric Generator Report
- **Method note:** [`docs/methods/grid_peak_vs_capacity.md`](../methods/grid_peak_vs_capacity.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Each grid's peak demand against its balancing authority's generators' net summer capacity (docs/methods/grid_peak_vs_capacity.md). Via the Energy Research Warehouse (ERW), table `grid_peak_vs_capacity`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: grid_peak_vs_capacity:<grid> (caiso, ercot, isone, miso, nyiso, pjm, spp) | none | text | grid_peak_vs_capacity:caiso, grid_peak_vs_capacity:ercot, grid_peak_vs_capacity:isone, grid_peak_vs_capacity:miso, grid_peak_vs_capacity:nyiso, grid_peak_vs_capacity:pjm, grid_peak_vs_capacity:spp | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.4857 to 213259.4; 56 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, pct, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 56 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The grid's name in capitals (CAISO, ERCOT, ISONE, MISO, NYISO, PJM, SPP), not a pricing node | none | text | CAISO, ERCOT, ISONE, MISO, NYISO, PJM, SPP | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:grid_peak_vs_capacity | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/grid_peak_vs_capacity.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T08:07:02Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 56 |
| `x_at` | The start of the peak hour, UTC | none | utc time | 2025-06-23T21:00:00Z, 2025-06-24T22:00:00Z, 2025-07-24T20:00:00Z, 2025-07-29T21:00:00Z, 2025-08-18T22:00:00Z, 2025-08-22T01:00:00Z | 49: Empty on every row but peak_demand_mw |
| `x_vintage` | The month of the EIA-860M generator list read (YYYY-MM) | none | text | 2026-08 | 0 |
| `x_states` | The states the grid's generators stand in, two-letter codes joined by semicolons | none | text | AR;CO;IA;KS;LA;MN;MO;MT;ND;NE;NM;OK;SD;TX, AR;IA;IL;IN;KY;LA;MI;MN;MO;MS;MT;ND;SD;TX;WI, AZ;CA;NM;NV, CT;MA;ME;NH;NY;RI;VT, DC;DE;IL;IN;KY;MD;MI;MN;NC;NJ;OH;PA;TN;VA;WV, NJ;NY, OK;TX | 0 |
| `x_split_states` | The states with more than 1 percent of their capacity in another balancing authority, joined by semicolons | none | text | AR;CO;IA;LA;MN;MO;MT;ND;NM;OK;SD;TX, AR;IA;IL;IN;KY;LA;MI;MO;MS;MT;ND;SD;TX, AZ;CA;NM;NV, IL;IN;KY;MI;MN;NC;NJ;TN, ME;NY, NJ, OK;TX | 0 |

Variables (8):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity_mw` | Net summer capacity of the generators in the EIA-860M list that began operating by the end of the peak's year | MW | 7 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `capacity_mw_listed` | Net summer capacity of every operating generator in the list (its month in x_vintage) | MW | 7 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `capacity_over_peak_pct` | capacity_mw less peak_demand_mw, as a percent of peak_demand_mw | pct | 7 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `capacity_solar_mw` | The solar part of capacity_mw (energy source SUN) | MW | 7 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `capacity_storage_mw` | The storage part of capacity_mw (energy source MWH) | MW | 7 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `capacity_wind_mw` | The wind part of capacity_mw (energy source WND) | MW | 7 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `peak_demand_mw` | The year's peak hour of demand, from eia930_demand_growth (x_at its start) | MW | 7 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `peak_to_capacity` | peak_demand_mw over capacity_mw, a ratio (not a planner's reserve margin) | ratio | 7 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `grid_stress_days`

One grid's stress day by one rule (the day's real-time price above the trailing 98th percentile, or an operator's emergency notice), with the day's mean real-time price at its main hub.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 282.

- **Time:** ts_utc is the grid's local day at 00:00:00Z (freq P1D).
- **Revisions:** A snapshot, replaced whole by each run of the builder; vintage is not filled.
- **Source:** erw:grid_stress_days ERW derived stress days of six grids by one rule (docs/methods/stress_days.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/stress_days.md)
- **Method note:** [`docs/methods/stress_days.md`](../methods/stress_days.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERW derived stress days of six grids by one rule (session 306). Via the Energy Research Warehouse (ERW), table `grid_stress_days`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: <iso>:<main hub> | none | text | caiso:TH_SP15_GEN-APND, ercot:HB_HUBAVG, isone:.H.INTERNAL_HUB, miso:INDIANA.HUB, nyiso:N.Y.C., spp:SPPNORTH_HUB | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-07-30T00:00:00Z to 2026-10-08T00:00:00Z; 241 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 7.3653 to 9002.0444; 282 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US, US-CA, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: <iso>_rtm: the real-time price | none | text | caiso_rtm, ercot_rtm, isone_rtm, miso_rtm, nyiso_rtm, spp_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | .H.INTERNAL_HUB, HB_HUBAVG, INDIANA.HUB, N.Y.C., SPPNORTH_HUB, TH_SP15_GEN-APND | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:PRC_INTVL_LMP, erw:ercot_hub_prices_daily, isone:rt_lmp_5min, miso:rt_lmp_final, nyiso:realtime, spp:RTBM-LMP-SL | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | http://mis.nyiso.com/public/csv/realtime/20240901realtime_zone_csv.zip, https://docs.misoenergy.org/marketreports/20240901_rt_lmp_final.csv, https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_hub_prices_daily.md, https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=PRC_INTVL_LMP&version=3&market_run_id=RTM&node=TH_NP15_GEN-APND,TH_SP15_GEN-APND&startdatetime=20230706T07:00-0000&enddatetime=20230707T07:00-0000, https://portal.spp.org/pages/rtbm-lmp-by-location, https://www.iso-ne.com/isoexpress/web/reports/pricing/-/tree/lmps-rt-five-min-final | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-19T22:57:38Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 282 |
| `x_reason` | Why the day is a stress day: price, notice, or price and notice | none | text | notice, price, price and notice | 0 |
| `x_event` | The event: stress days at most three days apart, named <grid>_stress_<first day>, or a named event's id when it holds a day of that event's window | none | text | for example caiso_stress_20230720, caiso_stress_20230725, caiso_stress_20230815; 120 distinct | 0 |
| `x_trailing_p98` | The threshold: the 98th percentile of the daily mean prices of the 365 days before the day | USD/MWh | number | 41.0236 to 442.1772; 178 distinct | 11: Fewer of the 365 days before were held than the rule needs (329), so no threshold was taken (a notice day) |
| `x_trailing_days` | The days held among the 365 before, over which the threshold is taken | count | integer | 14, 19, 20, 210, 224, 329, 330, 331, 332, 333, 334, 345, 350, 351, 352, 363, 364, 365, 40, 41, 42, 53, 54, 55 | 0 |
| `x_notices` | The kinds of CAISO's or ERCOT's notices issued that day, joined by semicolons | none | text | conservation_appeal, conservation_appeal;eea2;update;weather_watch, conservation_appeal;rotating_outages, conservation_appeal;weather_watch, eea1, eea_watch, ocn_weather, rmo, update, voluntary_conservation, weather_watch | 167: No notice that day (a stress day by price only) |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `stress_day` | The stress day's mean real-time price at the grid's main hub | USD/MWh | 282 | 2015-07-30T00:00:00Z | 2026-10-08T00:00:00Z |

### `grid_stress_yearly`

One ISO grid's value of one measure of how hard the grid works in one local year (evening ramp, lowest net load, the tightest hours, dark and calm stretches).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 2394.

- **Time:** ts_utc is the first day of the grid's local year at 00:00:00Z, a label (freq P1Y); the newest year is not whole. x_at is an hour's start, UTC.
- **Revisions:** Rebuilt whole by each run of the builder, so a year that no longer passes leaves the table; vintage is not filled.
- **Source:** erw:grid_stress EIA Form EIA-930 hourly demand and net generation by energy source, the per-BA workbooks (https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx), read by this run from warehouse/raw/eia930_emissions/20261004T021545Z/20261004T021550.248664Z_00002_CISO.xlsx; warehouse/raw/eia930_emissions/20261004T021545Z/20261004T021615.318504Z_00004_ERCO.xlsx; warehouse/raw/eia930_emissions/20261004T021545Z/20261004T021636.602873Z_00006_ISNE.xlsx; warehouse/raw/eia930_emissions/20261004T021545Z/20261004T021704.171793Z_00008_MISO.xlsx; warehouse/raw/eia930_emissions/20261004T021545Z/20261004T021728.227265Z_00010_NYIS.xlsx; warehouse/raw/eia930_emissions/20261004T021545Z/20261004T021753.302176Z_00012_PJM.xlsx; warehouse/raw/eia930_emissions/20261004T021545Z/20261004T021821.443138Z_00014_SWPP.xlsx; EIA-860M for installed capacity (https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx)
- **Method note:** [`docs/methods/grid_stress.md`](../methods/grid_stress.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. How hard each grid works by year: evening ramp, lowest net load, fuels in the tightest hours, dark and calm stretches (docs/methods/grid_stress.md). Via the Energy Research Warehouse (ERW), table `grid_stress_yearly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: iso:<grid> (caiso, ercot, isone, miso, nyiso, pjm, spp) | none | text | iso:caiso, iso:ercot, iso:isone, iso:miso, iso:nyiso, iso:pjm, iso:spp | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z, 2026-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -1341.5 to 856240.952; 1962 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, count, hour, pct, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US, US-CA, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 2394 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 2394 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:grid_stress | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/grid_stress.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-06T09:50:58Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 2394 |
| `x_at` | The hour a record or a stretch begins at, its start in UTC | none | utc time | 2019-01-01T19:00:00Z to 2026-09-10T02:00:00Z; 288 distinct | 2070: Empty on rows that are not a record (peak, net load peak or minimum, largest ramp) or the longest stretch |

Variables (46):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `calm_hours` | Dark, calm hours: wind and solar together under a tenth of their installed capacity of that month | count | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `calm_longest_fleet_energy_multiples` | The longest stretch's missing energy over the fleet's energy: how many times the fleet would have to be emptied | ratio | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `calm_longest_fleet_full_power_hours` | The longest stretch's missing energy over the fleet's power: the hours the whole fleet would discharge at full power to supply it | hour | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `calm_longest_fleet_mw` | The battery fleet's power in the longest stretch's first month | MW | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `calm_longest_fleet_mwh` | The battery fleet's energy in the longest stretch's first month | MWh | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `calm_longest_hours` | The length of the year's longest dark, calm stretch, hours (x_at its first hour) | hour | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `calm_longest_missing_mwh` | Over the longest stretch, the year's average wind and solar output less what they put out, summed over its hours | MWh | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `calm_stretches_ge24h` | Dark, calm stretches of a day or longer | count | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `capacity_coal_mw` | Installed coal capacity, the mean over the months of the 100 tightest hours | MW | 46 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `capacity_hydro_storage_mw` | Installed conventional hydro, pumped storage, battery and flywheel capacity together, the mean over the months of the 100 tightest hours | MW | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `capacity_natural_gas_mw` | Installed natural gas capacity (EIA's generator inventory, nameplate), the mean over the months of the 100 tightest hours | MW | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `capacity_nuclear_mw` | Installed nuclear capacity, the mean over the months of the 100 tightest hours | MW | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `capacity_solar_mw` | Installed solar capacity, the mean over the months of the 100 tightest hours | MW | 46 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `capacity_wind_mw` | Installed wind capacity, the mean over the months of the 100 tightest hours | MW | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `evening_ramp_3h_max_mw` | The year's largest rise of net load over three hours in the same evening window (x_at its start) | MW | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `evening_ramp_3h_max_share_of_peak_pct` | evening_ramp_3h_max_mw as a percent of the year's peak demand | pct | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `evening_ramp_max_mw_per_h` | The year's largest rise of net load from one hour to the next between the local hours starting 14:00 and 22:00, MW in one hour (x_at the hour the rise starts) | MW | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `evening_ramp_max_share_of_peak_pct` | evening_ramp_max_mw_per_h as a percent of the year's peak demand | pct | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `evening_ramp_median_mw_per_h` | The median over the year's days of each day's largest one-hour evening rise of net load | MW | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `hours_held` | The year's hours used | count | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `hours_in_year` | The year's hours to date | count | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `months_held` | The months with an hour used | count | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `net_load_min_mw` | The year's lowest hour of net load (x_at that hour) | MW | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `net_load_min_share_of_peak_pct` | net_load_min_mw as a percent of the year's peak demand | pct | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `net_load_min_wind_solar_share_pct` | Wind and solar over demand in the hour of the lowest net load, percent | pct | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `net_load_peak_mw` | The year's highest hour of net load, demand less wind less solar (x_at that hour) | MW | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `peak_demand_mw` | The year's highest hour of demand (x_at that hour) | MW | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `solar_reported` | 1 when the file reports solar in the year, else 0 | count | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `tight_coal_mw` | Mean coal output over the 100 tightest hours | MW | 46 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `tight_coal_share_of_capacity_pct` | Coal output in the 100 tightest hours over its installed capacity in each hour's month, mean percent | pct | 46 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `tight_hydro_mw` | Mean hydro output over the 100 tightest hours | MW | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `tight_hydro_storage_mw` | Mean hydro and storage output together over the 100 tightest hours | MW | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `tight_hydro_storage_share_of_capacity_pct` | Hydro and storage output in the 100 tightest hours over their installed capacity together, mean percent | pct | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `tight_natural_gas_mw` | Mean natural gas output over the 100 tightest hours | MW | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `tight_natural_gas_share_of_capacity_pct` | Natural gas output in the 100 tightest hours over its installed capacity in each hour's month, mean percent | pct | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `tight_net_load_mw` | The mean net load of the year's 100 tightest hours (the 100 used hours with the highest net load) | MW | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `tight_nuclear_mw` | Mean nuclear output over the 100 tightest hours | MW | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `tight_nuclear_share_of_capacity_pct` | Nuclear output in the 100 tightest hours over its installed capacity in each hour's month, mean percent | pct | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `tight_solar_mw` | Mean solar output over the 100 tightest hours | MW | 46 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `tight_solar_share_of_capacity_pct` | Solar output in the 100 tightest hours over its installed capacity in each hour's month, mean percent | pct | 46 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `tight_storage_mw` | Mean storage output over the 100 tightest hours | MW | 12 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `tight_wind_mw` | Mean wind output over the 100 tightest hours | MW | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `tight_wind_share_of_capacity_pct` | Wind output in the 100 tightest hours over its installed capacity in each hour's month, mean percent | pct | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `wind_reported` | 1 when the file reports wind in the year, else 0 | count | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `wind_solar_capacity_mw` | Installed wind and solar capacity at the year's end (or its last month held) | MW | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `wind_solar_mean_mw` | The year's average output of wind and solar together, over its used hours | MW | 54 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |

