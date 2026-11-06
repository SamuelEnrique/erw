# Cross-checks: Automated Analysis (`/research`)

Energy Research Warehouse (ERW). Session 3708, chain 208, 6 November 2026. Roadmap item 2's cross-check table for Research: **each headline figure the page prints** against a figure a named publisher states. The headline figures are the 78 of `replication/analysis/page_figures.json`: the twelve current finding cards' callouts and this week's chart (the Roundup of 2026-W44, the rule's pick: WTI at Cushing).

- **Where the published figures come from.**
  - ERCOT's market monitor's *2025 State of the Market Report*, read by session 3708 on 6 November 2026. Its robots file allows every path but `/wp-admin/`; it is quoted, not copied (three requests: the robots file, the market's page, the report).
  - EIA's figures as the ERW's own tables hold them (`storage_buildout_monthly`, from EIA-860M; `eia_retail_electricity_prices`, from the *Electric Power Monthly*).
  - Figures the method notes already quote, with the dates given there.
- **The columns.** "Gap" is ours less theirs. "Reason" is one sentence, or "not explained". A figure with no published counterpart is said to have none. A figure the page prints as "license needed" (NYISO, ISO-NE) is not compared.

## Figures with a published counterpart

| Card and figure | Ours | Published figure | Source | Gap | Reason |
|---|---|---|---|---|---|
| `batteries_lunch_grids`: ERCOT's battery fleet (the callout is 2026-09, 19,195 MW); the same table at the end of 2025 | 13,909 MW, December 2025 (`storage_buildout_monthly`, `iso:ercot`, `battery_operating_mw`) | "Total energy storage capacity exceeded 17 GW" in 2025 | [Potomac Economics, *2025 State of the Market Report for the ERCOT Electricity Markets*, June 2026](https://www.potomaceconomics.com/wp-content/uploads/2026/06/2025-State-of-the-Market-Report-for-ERCOT.pdf), Chapter III, key insights (page 13) | at least -3,091 MW | Not explained: EIA-860M counts plants EIA records as operating, ERCOT's monitor counts resources in ERCOT's market; Modo Energy's count for 2025 (13.9 GW, quoted in `battery_earns_algorithm.md`) agrees with EIA's |
| The same, added during 2025 | 5,616 MW (`battery_operating_mw_net_added_12m`, December 2025) | "6.2 GW of solar, 7.3 GW of ESRs, 1.2 GW of wind, and 280 MW of gas turbines" entered in 2025 | the same, Chapter III (pages 13 and 15) | -1,684 MW | Not explained beyond the row above: the two count a plant from different dates (EIA's operating month, ERCOT's commercial operation) |
| The same, average duration | 1.55 hours (`battery_operating_mwh_per_mw`, December 2025) | "average duration increased from 1.67 hours to 1.83 hours" | the same (page 13) | -0.28 hours | Not explained: EIA's MWh is the energy reported to EIA-860M, ERCOT's duration its own registration |
| `peak_hour_grids`: ERCOT's solar fleet at the end of 2025 (the callout), and its growth in 2025 | 30,018 MW; 7,816 MW added in 2025 (`solar_operating_mw`, December 2024 22,201 to December 2025 30,018) | 6.2 GW of solar entered commercial operation in 2025 | the same (pages 13 and 15) | +1,616 MW for the year's additions | Not explained: the same difference of dates and scope as the batteries' |
| `negative_prices_west`: ERCOT West's negative hours, 2025 (the callout) | 638 hours; South 235, North 224, Houston 142 (the card's CSV, `erw_2026_negative_hours_hubs.csv`) | "the West zone experienced the highest number of intervals with negative prices ... of any load zone" in 2025 | the same, Chapter I.C (page 7) | the same order: West first | The monitor states the rank, not the count; ours is at the hubs, theirs at the load zones |
| `siting_gigawatt`: all-in for a 1 GW load, least and most (the callout) | 40.99 (HB_WEST) and 46.83 (LZ_AEN) USD per MWh | Texas, industrial customers, the mean of November 2025 to July 2026: USD 67.02 per MWh | EIA, *Electric Power Monthly*, Table 5.6.A, as the ERW holds it (`eia_retail_electricity_prices`, `eia:retail_price:TX:IND`) | -26.03 and -20.19 | The card's all-in holds energy, the four-peak transmission charge and capacity (none in ERCOT); EIA's retail price also holds distribution, retail costs and charges |
| `queue_divorce`: requested capacity withdrawn, 2000 to 2020 (the callout) | 75 percent of 3,509 GW | 75 percent of 3,501 GW, the owner's thesis (not a publisher) | `automated_analysis_findings.md`, "Cross-checks" (session 381) | +0.2 points; +8 GW | Berkeley Lab's 2026 edition of the queue data against the edition the thesis read |
| `queue_divorce`: the divorce rate over the marriage rate (the callout) | 2.4 / 6.1, 39 percent | 6.1 and 2.4 per 1,000 population, provisional 2023 | [CDC/NCHS FastStats, "Marriage and Divorce"](https://www.cdc.gov/nchs/fastats/marriage-divorce.htm), retrieved 9 October 2026 (`automated_analysis_findings.md`) | 0 | Quoted, not computed; the card's figure is their ratio |
| This week's chart, 2026-W44: WTI at Cushing, the weekly mean | 107.17 USD per barrel, the week of 2026-10-19 to 2026-10-25; up 7.24 from 99.93 | EIA's own daily spot price, the series the chart's mean is made of | `eia_fuel_spot_prices` (EIA's series RWTC) | none to compute | A mean of the publisher's own series reproduces it; it is held to its file by the replication, not checked against another publisher |

## Figures with no published counterpart held

Each figure below is named; none has a figure another publisher states for the same measure, place and period in the repository's holdings or in the report read above.

| Card | Figures (callouts) | Why none |
|---|---|---|
| `batteries_lunch_grids` | ERCOT's worst-interval multiple, 2019 and 2025 (126.6x, 12.1x) | A statistic of the card's own (the year's worst 15 minutes over its median); NYISO's figures are "license needed" |
| `batteries_curtailment` | Curtailment on low and high charging days (8,539, 18,259 MWh a day); MWh curtailed per GWh charged (636, 1,006); the controlled estimate's error and R2 (161, 0.65) | Regressions of the card's own on CAISO's own curtailment and battery files; CAISO publishes the inputs, not these estimates |
| `batteries_curtailment_hourly` | Curtailment in 2025's charging hours, predicted and observed (923, 812 MW); the correlation and R2 (0.39, 0.15); hours at the charging ceiling with curtailment on, 2021 and 2025 (76, 171) | The same |
| `gas_sets_price` | ERCOT's hours below gas's fuel cost, 2019 and 2025 (38.8, 40.9 percent); 2025 at heat rates 6.5 and 8.0 (35.3, 52.8 percent) | ERCOT's monitor reports which fuel set the price in other terms; its 2025 report was not searched for an equal measure; ISO-NE's figures are "license needed" |
| `impact_study` | ERCOT North Hub before and from 7 February 2021 (21.46, 3,047.37 USD per MWh); the difference in differences and its error (3,016.40, 1,598.93) | A window of the card's own; the monitor's 2025 report gives 2021's year only (North zone USD 221.52, load-weighted); the control's figures (NYISO) are "license needed" |
| `negative_prices_west` | ERCOT Houston's negative hours, 2019 and 2025 (46, 142); West's share of held hours (3.5, 7.3 percent); West in 2019 (308) | The monitor states the West zone's rank (above), not the hours |
| `peak_hour_grids` | ERCOT's days peaking 17:00 to 21:59, 2019 and 2025 (24.9, 71.0 percent) | No publisher's count of the peak hour's local time is held; NYISO's figures are "license needed" |
| `queue_divorce` | Operating (13 percent); withdrawn, worst and best technology (84, 52 percent) | Berkeley Lab's report states its own shares; the ruling on Berkeley Lab's terms is open (session 253), so it was not read |
| `who_rescues_whom` | Authorities that flipped (6, 5); ERCOT's net flow (512 exported, 9,652 imported MWh a day); PacifiCorp East's (357 imported, 11,611 exported) | FERC and NERC's report on February 2021 states the event's operations, not these daily nets; not read |
| `siting_battery_swing` | The mean intraday swing, narrowest and widest (34.22, 105.86); the median and the count (49.31, 195); PALACIOS_RN's 10th and 90th percentiles (20.04, 85.57) | ERCOT's settlement point prices are the inputs; no publisher states these spreads |
| `siting_flexible` | Saved all-in, least and most (8.60, 10.78); hours given up (5, 15); all-in at HB_HUBAVG, flat and flexible (42.38, 32.50) | A load profile of the card's own |
| `siting_gigawatt` | A year at 1 GW, least and most (323,139,956, 369,228,563 USD); the median months to connect (45.80, 100.00) | The year is the all-in row above times 7,884,000 MWh; the months to connect are Berkeley Lab's queue data's, not in the card's download |
| This week's chart | The score: 87.5 percent of the 104 earlier changes smaller | A statistic of the rule's own |

## The largest gaps, in one line each

- **ERCOT's battery fleet at the end of 2025: 13,909 MW in EIA-860M against "exceeded 17 GW" in the monitor's report.** Not explained; Modo Energy's count agrees with EIA's.
- **A 1 GW load's all-in against Texas's industrial retail price: USD 20 to 26 per MWh below.** The retail price holds distribution and retail costs.
