# Cross-checks: What a datacenter pays (`/cost-of-power`)

Energy Research Warehouse (ERW). Session 3707, chain 208, 6 November 2026. Roadmap item 2's cross-check table for the datacenter page: **each headline figure the page prints** against a figure a named publisher states. The headline figures are the 14 of `replication/datacenter/page_figures.json`: the default case, ERCOT's North load zone `LZ_NORTH`, a flat load of 100 MW bought in real time, the last twelve months November 2025 to October 2026.

- **Where the published figures come from.**
  - ERCOT's market monitor's 2025 report gives the North zone's prices by year (Table 1, 2021 to 2025). Session 3708 read it on 6 November 2026; its robots file allows every path but `/wp-admin/`. It is quoted, not copied.
  - EIA's retail prices are the ERW's own copy of EIA's *Electric Power Monthly*, Table 5.6.A (`eia_retail_electricity_prices`, `eia:retail_price:TX:IND`, as held on this machine to July 2026).
  - The other rows are quoted from the method note's "Cross-checks" (`docs/methods/datacenter_pays_algorithm.md`) and its assumptions, read on the dates the note gives.
  - Nothing was fetched for this file.
- **The columns.** "Gap" is ours less theirs. "Reason" is one sentence, or "not explained". A figure with no published counterpart is said to have none.

| Headline figure (`page_figures.json` field) | Ours | Published figure | Source | Gap | Reason |
|---|---|---|---|---|---|
| Market energy, a flat load, the last twelve months, USD per MWh (`l12_usd_mwh`) | 34.07 (November 2025 to October 2026); over the nine months EIA's table holds, November 2025 to July 2026, the mean of the monthly flat prices is 32.40 | Texas, industrial customers, the mean of the same nine months: USD 67.02 per MWh (6.26 to 7.25 cents per kWh by month) | [EIA, *Electric Power Monthly*, Table 5.6.A](https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_a), as the ERW holds it (`eia_retail_electricity_prices`, `eia:retail_price:TX:IND`, 2025-11 to 2026-07) | -34.62 over the nine months | Ours is wholesale energy alone at one load zone; EIA's is what every industrial customer of the state paid for all of it: energy, delivery and charges |
| The same, one month | July 2026: 30.59 | Texas, industrial customers, July 2026: 7.07 cents per kWh, USD 70.70 per MWh | the same (the note's row, session 462) | -40.11 | The same |
| Cost for 100 MW, the last twelve months, USD (`l12_usd`) | 29,841,981 | No published counterpart | | | The first row times 100 MW times the hours held |
| Power per GPU-hour, USD (`gpu_hour`) | 0.0691 | No published counterpart | | | Arithmetic of the price and two assumptions (1.3 kW a GPU, NVIDIA's DGX H100; PUE 1.56, the Uptime Institute's survey), each cited in the note |
| GPUs that 100 MW powers (`gpus`) | 49,310 | No published counterpart | | | The same assumptions |
| Bought day-ahead, the same twelve months, USD per MWh (`da_usd_mwh`) | 35.70 | No published counterpart held | | | EIA's file of ICE hub prices, which the note sets beside SP15, NP15 and New England, was not read for ERCOT North |
| A bad month (2026-08), USD per MWh (`bad_usd_mwh`) | 37.88 | No published counterpart | | | A percentile of the page's own months |
| Hours at or above USD 1,000 per MWh, the last twelve months (`scarce_hours`) | 4 | No published counterpart held | | | ERCOT's market monitor counts scarcity by year in its state-of-the-market reports; none for these months is held |
| What a flat load of 100 MW paid in them, USD (`scarce_usd`) | 446,175 | No published counterpart | | | The page's own arithmetic over those hours |
| Carbon, the last twelve months at the grid's monthly average, kg CO2 per MWh (`co2_kg_mwh`) | 300.38 | No published counterpart held for these months | | | EPA's eGRID states ERCOT's annual output rate (subregion ERCT), but `egrid_subregions_annual` is not on this machine and no note quotes its 2023 figure; the session 3709 file (`grid.md`) sets ERCOT's intensity beside EIA's own |
| Tonnes of CO2 a year for 100 MW (`co2_tonnes`) | 263,102 | No published counterpart | | | The row above over a year of a 100 MW flat load |
| Hours of the hourly window (`window_hours`) | 10,160 | No published counterpart | | | A count of the page's own hours |
| A flat load's own hours over the window, kg CO2 per MWh (`window_kg_mwh`) | 309.84 | No published counterpart | | | The page's own weighting of the hourly intensity |
| Year 2016, a flat load, USD per MWh (`year_2016`) | 21.68 | No published counterpart held | | | ERCOT's market monitor's reports for 2016 and 2021 state its own load-weighted averages; none is held |
| Year 2021, a flat load, USD per MWh (`year_2021`) | 150.61 | The North load zone's load-weighted average real-time price, 2021: USD 221.52 per MWh | [Potomac Economics, *2025 State of the Market Report for the ERCOT Electricity Markets*, June 2026](https://www.potomaceconomics.com/wp-content/uploads/2026/06/2025-State-of-the-Market-Report-for-ERCOT.pdf), Table 1 (page 7), read by session 3708 on 6 November 2026 | -70.91 | Theirs weights each interval by the zone's load, and Winter Storm Uri's highest prices fell in hours of the highest load; ours is the flat mean of every hour |
| The same zone, 2022 to 2025, a flat load, from the page's hourly download | 62.93, 48.69, 26.41, 32.66 | The North zone's load-weighted averages: 77.30, 78.01, 30.42, 35.34 | the same | -14.37, -29.32, -4.01, -2.68 | The same weighting: the gap is large in years whose price spikes came in high-load hours (2023's August) and small in years without them |

## The largest gap, in one line

- **Wholesale energy against the industrial retail price: -34.62 USD per MWh over November 2025 to July 2026.** Delivery and charges are about half of what Texas industry paid. The page's "all-in" view (the All grids tab) adds transmission, and its method note says the retail figure is not the page's.

## Not compared, and why

- 13 of the 14 figures have no counterpart held, or none exists:
  - the GPU figures are arithmetic on cited assumptions;
  - the counts and percentiles are the page's own;
  - the day-ahead, scarcity, carbon and yearly figures have publishers (ICE through EIA, ERCOT's market monitor, EPA's eGRID) whose figures for these windows are not in the repository.
- The cost of capital and the years counted are assumptions; the note sets them beside the ATB and Lazard.
