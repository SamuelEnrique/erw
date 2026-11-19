# The findings worth Samuel's Stata run (chain 506, 19 November 2026)

Written by chain 506 on samueloldlaptop from the audit of every draft of `docs/findings/`: https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/findings-audit-2026-11-19.md. Nothing here is approved, posted or sent: each is a draft until Samuel runs its do-file in Stata and approves it. The chain's rules: https://github.com/SamuelEnrique/erw/blob/main/queue/done/506-day-19-november-oldlaptop-findings-audit-shortlist.md

## The audit in numbers

Every draft, 549: passed 364; not checked 95; passed after a fix 76; held (internal table) 13; withdrawn 1.
The 364 drafts of 19 November (chain 502), check 2: pass 255; not checked 108; fail 1.

## What the audit says about the morning's drafts

1. **The arithmetic holds.** Every morning draft that could be run here printed its own figures again, to the sixth decimal or within the draft's stated tolerance; the one draft withdrawn failed because its table gained a filing an hour after it was written, not because of a wrong step.
2. **The words did not hold as well as the numbers.** The sentence template wrote "was" after every subject (49 plural subjects mended), lost a word in two templates, and called a year "the first year this measure counts" where the table holds earlier years in 22 drafts (the scripts' own year windows); all are mended in the drafts, none by changing a figure.
3. **The Stata files kept Samuel's three rules everywhere**, but 12 of 549 did not do what their Python does (empty years not printed as zero, a missing magnitude counted, two names longer than Stata allows, a real zero dropped); they are mended and read, not run, since this machine has no Stata.
4. **What was not checked is named, not passed:** the 47 drafts on FERC 714 forecasts (the archive rebuilds that table short), the 13 on internal or held tables, and about 50 drafts on hourly EIA-930 tables (regions, tie lines, supply) and France's grid whose per-draft rebuild Claude Code stopped when the machine ran short of memory; every one of them is "not checked" with its reason in the audit.
5. **A reproduction is not a second source.** It reruns the hunt's own script on the ERW's own copy of a table; where a second route exists it was tried (part E), and Far West Texas demand left the sheet because ERCOT's own zone load differs from EIA-930's by 1.7 to 3.5 percent.

## How each finding is given

The sentence as the draft now says it; the figure as this machine's run printed it; the chart's file; what it is compared with; whether a publisher already printed it (part C: "seen in search results" means the page was not opened); the one thing that would make it wrong; the tables and their license; the do-file for the Stata run; the second route (part E); one line on why it matters as a fact. Readers: an investor in energy, a power trader, the energy lead of an AI lab. No more than six from one family.

## The 40

### 1. A sub-region's mean hour: Dominion Virginia Power zone (DOM, a sub-region of PJM)

- **Reader:** the energy lead of an AI lab
- **The sentence:** The mean hour of demand in Dominion Virginia Power zone (DOM, a sub-region of PJM) was 15,403 MW in 2025, against 11,687 MW in 2019, the first full year the ERW holds.
- **The figure:** 15,403 MW in 2025, against 11,687 in 2019, as this machine's run printed them (the draft's own: 15,403 and 11,687)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/demand/sub-mean-pjm-sub-dom.png
- **Compared with:** the same measure in 2019
- **Already known?** Known in part: EIA's Today in Energy (https://www.eia.gov/todayinenergy/detail.php?id=67664, 2026) gives the Dominion zone's summer peak of 23,905 MW in 2025, 23 percent above 2019; FactSet (https://insight.factset.com/data-center-power-demand-begins-to-surge-across-the-u.s, September 2025) says Dominion's average hourly load was up about 30 percent on 2019 through September 2025. Ours gives the full year: a mean hour of 15,403 MW in 2025 against 11,687 MW in 2019 (31.8 percent). Seen in search results, pages not opened.
- **The one thing that would make it wrong:** The zone's demand is as PJM reports it to EIA (EIA-930); a change of the zone's bounds or of PJM's reporting would move the level.
- **Tables and license:** `eia930_subba_demand_hourly_2019` (public; eia:electricity/rto/region-sub-ba-data); `eia930_subba_demand_hourly_2020` (public; eia:electricity/rto/region-sub-ba-data); `eia930_subba_demand_hourly_2021` (public; eia:electricity/rto/region-sub-ba-data); `eia930_subba_demand_hourly_2022` (public; eia:electricity/rto/region-sub-ba-data); `eia930_subba_demand_hourly_2023` (public; eia:electricity/rto/region-sub-ba-data); `eia930_subba_demand_hourly_2024` (public; eia:electricity/rto/region-sub-ba-data); `eia930_subba_demand_hourly_2025` (public; eia:electricity/rto/region-sub-ba-data)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/demand/sub-mean-pjm-sub-dom.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/demand/sub-mean-pjm-sub-dom.reproduce.py)
- **Second route:** No second route in the warehouse: it holds no PJM zone load of its own; EIA-930 subregion demand is the only source.
- **Why it matters, as a fact:** PJM's Dominion zone serves the largest concentration of data centers in the world (EIA, https://www.eia.gov/todayinenergy/detail.php?id=67664); the mean hour is the load that runs all year, not a peak.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 2. What a utility sells to commercial customers: Virginia Electric & Power Co in VA

- **Reader:** the energy lead of an AI lab
- **The sentence:** The retail electricity sales to commercial customers of Virginia Electric & Power Co in VA were 60.09 TWh in 2025, against 41.54 TWh in 2017, the first full year the ERW holds.
- **The figure:** 60.0882 TWh in 2025, against 41.5356 in 2017, as this machine's run printed them (the draft's own: 60.0882 and 41.5356)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/other_us/util-commercial-u861-19876-va.png
- **Compared with:** the same measure in 2017
- **Already known?** Known in part: EIA's Today in Energy (https://www.eia.gov/todayinenergy/detail.php?id=67664, May 2026) gives Virginia's commercial sales up nearly 30 million MWh from 2019 to 2025 using EIA-861M for 2025; no publisher found printing Virginia Electric and Power Company's own commercial sales by year. Ours: 60.09 TWh in 2025 against 41.54 TWh in 2017. Seen in search results, page not opened.
- **The one thing that would make it wrong:** EIA notes that changes in commercial and industrial sales from 2023 to 2024 largely reflect better reporting of data centers and crypto mining (Electric Power Annual, table 2.8): part of the rise may be customers moved into the commercial class, not new load; EIA-861M's 2025 months are preliminary.
- **Tables and license:** `eia861m_utility_sales_monthly` (public; eia:eia861m)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/other_us/util-commercial-u861-19876-va.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/other_us/util-commercial-u861-19876-va.reproduce.py)
- **Second route:** Agree: EIA-861 annual sales (table eia861_utility_sales, part A) give Virginia Electric and Power 41.60 TWh of commercial sales in 2017 and 60.09 in 2025, against the draft 41.54 and 60.09 from EIA-861M. The 2025 annual value equals the monthly sum exactly, so for 2025 the two may not be independent; 2017 is.
- **Why it matters, as a fact:** Virginia Electric and Power is the utility of the Dominion zone, and commercial is the class in which most data centers are billed.
- **The audit's row:** checks 1 fixed, 2 pass, 3 pass; changed: the sentence: "was" made "were" after the plural subject (the chart's line under the title, drawn into the PNG, still has the old words)

### 3. Solar in the tightest hours: ERCOT

- **Reader:** a power trader
- **The sentence:** Solar's output in ERCOT's tightest hours, as a share of its solar capacity, was 5.0 percent of solar capacity in 2025, against 71.1 percent of solar capacity in 2019, the first year the ERW's table holds.
- **The figure:** 5.022 percent of solar capacity in 2025, against 71.103 in 2019, as this machine's run printed them (the draft's own: 5.022 and 71.103)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/markets_operations/tight-solar-ercot-tight-solar.png
- **Compared with:** the same measure in 2019
- **Already known?** Known in part: Ascend Analytics (https://www.ascendanalytics.com/blog/emerging-energy-reliability-risks-and-needs-in-ercot-its-not-an-afternoon-problem-anymore) and Grid Status (https://blog.gridstatus.io/ercot-record-july-2026/) describe ERCOT's tightest hours moving to the evening when solar has faded; no publisher found printing solar's output in the tightest hours as a share of capacity. Ours adds the figure by year, 71.1 percent in 2019 against 5.0 percent in 2025. Seen in search results, pages not opened.
- **The one thing that would make it wrong:** The tightest hours are the ERW's own definition (table grid_stress_yearly, its method note); another definition of tight would give another share.
- **Tables and license:** `grid_stress_yearly` (public; erw:grid_stress)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/markets_operations/tight-solar-ercot-tight-solar.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/markets_operations/tight-solar-ercot-tight-solar.reproduce.py)
- **Second route:** No second route in the warehouse: the tightest hours exist only in grid_stress_yearly.
- **Why it matters, as a fact:** ERCOT's tightest hours are the hours in which scarcity prices are set; the figure is how much of the solar fleet is producing in them.
- **The audit's row:** checks 1 pass, 2 pass, 3 fixed; changed: the do-file: the variable is renamed "solar" before the reshape, whose name valuetight_solar_share_of_capacity_pct (38 characters) Stata refuses (32 at most)

### 4. The midday price: ERCOT's West load zone (LZ_WEST)

- **Reader:** a power trader
- **The sentence:** The midday real-time price at ERCOT's West load zone (LZ_WEST) was 48.9 percent of the all-hours mean in 2025, against 128.9 percent of the all-hours mean in 2015, the first full year the ERW holds.
- **The figure:** 48.9315 percent of the all-hours mean in 2025, against 128.949 in 2015, as this machine's run printed them (the draft's own: 48.9315 and 128.949)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/prices/midday-discount-ercot-lz-west.png
- **Compared with:** the same measure in 2015
- **Already known?** Known in part: Modo Energy (https://modoenergy.com/research/ercot-power-prices-2024-energy-arbitrage-ancillary-services-hub-load-zone-west-north-south-houston-panhandle) says West Texas prices sat below the hub from 9 AM to 4 PM in 2024 as solar rose; no publisher found printing the West zone's midday price as a share of its all-hours mean by year. Ours: 48.9 percent in 2025 against 128.9 percent in 2015. Seen in search results, page not opened.
- **The one thing that would make it wrong:** The midday window and the all-hours mean are the hunt's choices, on real-time prices; another window, or day-ahead prices, would give another share.
- **Tables and license:** `ercot_zone_prices_history` (public; ercot:NP4-180-ER;ercot:NP6-785-ER)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/prices/midday-discount-ercot-lz-west.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/prices/midday-discount-ercot-lz-west.reproduce.py)
- **Second route:** No second route in the warehouse for hourly real-time zone prices before 28 September 2026 (ercot_rtm_node_prices begins then).
- **Why it matters, as a fact:** A battery or a flexible load in West Texas earns, or saves, on the gap between midday prices and the rest of the day.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 5. The evening price: ERCOT's South hub (HB_SOUTH)

- **Reader:** a power trader
- **The sentence:** The evening real-time price at ERCOT's South hub (HB_SOUTH) was 161.0 percent of the all-hours mean in 2025, against 109.5 percent of the all-hours mean in 2015, the first full year the ERW holds.
- **The figure:** 160.994 percent of the all-hours mean in 2025, against 109.549 in 2015, as this machine's run printed them (the draft's own: 160.994 and 109.549)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/prices/evening-premium-ercot-hb-south.png
- **Compared with:** the same measure in 2015
- **Already known?** Known in part: Modo Energy (https://modoenergy.com/research/ercot-bess-operations-battery-dispatch-one-hour-two-hour-spread-compression-revenue-capture-eolian-engie-sced-offer-curves, June 2025) reports ERCOT's real-time top-bottom one-hour spread at 98 USD per MWh on average in 2024, 61 percent below 2023, as batteries grew; no publisher found printing the evening price as a share of the all-hours mean by year since 2015. Ours: 161.0 percent in 2025 against 109.5 percent in 2015 at the South hub. Seen in search results, page not opened.
- **The one thing that would make it wrong:** The evening window is the hunt's choice, on real-time prices at one hub; another window or hub gives another figure.
- **Tables and license:** `ercot_all_hub_prices_history` (public; ercot:NP4-180-ER;ercot:NP4-190-CD;ercot:NP6-785-ER;ercot:NP6-905-CD)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/prices/evening-premium-ercot-hb-south.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/prices/evening-premium-ercot-hb-south.reproduce.py)
- **Second route:** No second route in the warehouse for hourly real-time hub prices before 28 September 2026; ercot_hub_prices_daily holds daily means, not the evening hours.
- **Why it matters, as a fact:** The evening hours are the hours a battery charged at midday sells into; the premium is that gap as a share of the day's mean.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 6. The cheapest hour of the day: ERCOT's North hub (HB_NORTH)

- **Reader:** the energy lead of an AI lab
- **The sentence:** The mean local hour of the day's cheapest real-time hour at ERCOT's North hub (HB_NORTH) was 10.7 hours after local midnight in 2025, against 6.0 hours after local midnight in 2015, the first full year the ERW holds.
- **The figure:** 10.674 hours after local midnight in 2025, against 6.03562 in 2015, as this machine's run printed them (the draft's own: 10.674 and 6.03562)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/prices/cheapest-hour-ercot-hb-north.png
- **Compared with:** the same measure in 2015
- **Already known?** Known in part: E3's ERCOT market update (https://ethree.com/wp-content/uploads/2024/12/E3-2024-ERCOT-Market-Update.pdf) and Modo Energy (https://modoenergy.com/research/ercot-power-prices-2024-energy-arbitrage-ancillary-services-hub-load-zone-west-north-south-houston-panhandle, February 2025) describe a midday dip in ERCOT prices as solar grew; no publisher found printing the mean hour of the day's cheapest real-time hour by year. Ours: 10.7 hours after local midnight in 2025 against 6.0 in 2015 at the North hub. Seen in search results, pages not opened.
- **The one thing that would make it wrong:** A mean of daily cheapest hours hides days with two near-equal minima; a five-minute or day-ahead basis would give another hour.
- **Tables and license:** `ercot_all_hub_prices_history` (public; ercot:NP4-180-ER;ercot:NP4-190-CD;ercot:NP6-785-ER;ercot:NP6-905-CD)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/prices/cheapest-hour-ercot-hb-north.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/prices/cheapest-hour-ercot-hb-north.reproduce.py)
- **Second route:** No second route in the warehouse for hourly real-time hub prices before 28 September 2026.
- **Why it matters, as a fact:** The hour of the day in which power is cheapest is the hour a flexible load (training runs, cooling, charging) would move to.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 7. What a utility sells to commercial customers: Omaha Public Power District in NE

- **Reader:** the energy lead of an AI lab
- **The sentence:** The retail electricity sales to commercial customers of Omaha Public Power District in NE were 7.88 TWh in 2025, against 3.67 TWh in 2017, the first full year the ERW holds.
- **The figure:** 7.87521 TWh in 2025, against 3.66636 in 2017, as this machine's run printed them (the draft's own: 7.87521 and 3.66636)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/other_us/util-commercial-u861-14127-ne.png
- **Compared with:** the same measure in 2017
- **Already known?** Known in part: Nebraska Public Media (https://nebraskapublicmedia.org/en/news/news-articles/nebraskans-cope-with-rising-demand-prices-for-electricity/), citing OPPD, says data centers used 1 percent of OPPD's sales in 2018 and 21 percent in 2024; no publisher found printing OPPD's commercial sales by year. Ours: 7.88 TWh in 2025 against 3.67 TWh in 2017. Seen in search results, page not opened.
- **The one thing that would make it wrong:** EIA notes that changes in commercial and industrial sales from 2023 to 2024 largely reflect better reporting of data centers and crypto mining (Electric Power Annual, table 2.8): part of the rise may be customers moved into the commercial class, not new load; EIA-861M's 2025 months are preliminary.
- **Tables and license:** `eia861m_utility_sales_monthly` (public; eia:eia861m)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/other_us/util-commercial-u861-14127-ne.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/other_us/util-commercial-u861-14127-ne.reproduce.py)
- **Second route:** Agree: EIA-861 annual sales give Omaha Public Power District 3.67 TWh of commercial sales in 2017 and 7.88 in 2025, against the draft 3.67 and 7.88. The annual series jumps 42 percent from 2022 (3.80) to 2023 (5.39) in one year.
- **Why it matters, as a fact:** Omaha Public Power District says data centers used 21 percent of its sales in 2024 against 1 percent in 2018 (Nebraska Public Media); commercial is the class they are billed in.
- **The audit's row:** checks 1 fixed, 2 pass, 3 pass; changed: the sentence: "was" made "were" after the plural subject (the chart's line under the title, drawn into the PNG, still has the old words)

### 8. Who sends power to whom: Canada to New York

- **Reader:** a power trader
- **The sentence:** The mean hourly flow of power from Canada to New York (EIA's regions) was 211 MW in 2025, against 1,992 MW in 2019, the first full year the ERW holds.
- **The figure:** 211.028 MW in 2025, against 1,991.6 in 2019, as this machine's run printed them (the draft's own: 211.028 and 1,991.6)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/trade/pair-flow-rp-can-ny.png
- **Compared with:** the same measure in 2019
- **Already known?** Known in part: EIA's Today in Energy (https://www.eia.gov/todayinenergy/detail.php?id=63684, 2024) reports Hydro-Quebec's deliveries into New York falling in 2023 with drought; Grid Status (https://blog.gridstatus.io/more-hqs-than-answers-hydro-quebec-isone-nyiso-ties/) says NYISO's net trade with Canada in January to August 2025 was a quarter of 2022's. Ours gives the yearly mean hourly flow from Canada to New York, 211 MW in 2025 against 1,992 MW in 2019. Seen in search results, pages not opened.
- **The one thing that would make it wrong:** EIA-930 interchange as the regions report it; the reports of the two sides differ, and the draft uses EIA's region-pair series.
- **Tables and license:** `eia930_region_pair_hourly` (public; erw:eia930_ba_interchange_hourly)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/trade/pair-flow-rp-can-ny.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/trade/pair-flow-rp-can-ny.reproduce.py)
- **Second route:** In part: EIA-930 daily interchange between NYIS and the Canadian authorities (table eia930_daily_interchange) gives 1,991 MW on average in 2019 against the draft 1,992; for 2025 the daily table holds 318 of 365 days (265.8 MW on those days), so the two cannot be set side by side for 2025.
- **Why it matters, as a fact:** Imports from Quebec and Ontario have been a base of New York's supply; the figure is how much of that flow remains, hour by hour, on average.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 9. Hours a region trades the other way: New England (EIA's region), a net importer over 2019 to 2025

- **Reader:** a power trader
- **The sentence:** The share of the year's hours in which New England, a net importer over 2019 to 2025, exported on net was 27.8 percent of hours in 2025, against 0.0 percent of hours in 2019, the first full year the ERW holds.
- **The figure:** 27.7803 percent of hours in 2025, against 0.045662 in 2019, as this machine's run printed them (the draft's own: 27.7803 and 0.045662)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/trade/region-against-rn-ne.png
- **Compared with:** the same measure in 2019
- **Already known?** Known in part: ISO New England's market monitor, Fall 2025 quarterly report (https://www.iso-ne.com/static-assets/documents/100032/a04_mc_2026_02_10-11_imm_fall_2025_qmr_presentation.pdf), says New England was a net exporter in the fall of 2025 for the first time in at least two decades, 33 MW an hour on average; EIA's Today in Energy (https://www.eia.gov/todayinenergy/detail.php?id=67105) counts days of net exports to Canada. Ours: the share of 2025's hours in which New England exported on net, 27.8 percent against 0.05 percent in 2019. Seen in search results, pages not opened.
- **The one thing that would make it wrong:** EIA-930 total interchange for New England, sign as reported; an hour of reporting error near zero flips the count.
- **Tables and license:** `eia930_region_hourly` (public; eia:gridmonitor/sixMonthFiles)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/trade/region-against-rn-ne.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/trade/region-against-rn-ne.reproduce.py)
- **Second route:** No second route in the warehouse: the only other interchange tables are daily, and a share of hours needs hours.
- **Why it matters, as a fact:** New England has bought power from Canada for decades; the figure is how often it now sends power out on net instead.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 10. Batteries against the peak: CAISO

- **Reader:** an investor in energy
- **The sentence:** The battery fleet of CAISO at the year's end, against the average GW of its ten highest days of demand, was 46.6 percent of peak-day demand in 2025, against 0.6 percent of peak-day demand in 2019, the first year both tables hold.
- **The figure:** 46.5676 percent of peak-day demand in 2025, against 0.554036 in 2019, as this machine's run printed them (the draft's own: 46.6193 and 0.554036)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/cross_family/battery-per-peak-caiso-bat-peak.png
- **Compared with:** the same measure in 2019
- **Already known?** Known in part: CAISO's market monitor (https://www.caiso.com/documents/2024-special-report-on-battery-storage-may-29-2025.pdf) and the IEA give batteries' share of energy at the peak hour (24 percent in 2024, IEA) and of energy in net peak hours (about 9 percent in 2024); no publisher found printing the fleet's capacity against the mean of the ten highest days. Ours: 46.6 percent in 2025 against 0.6 percent in 2019. Seen in search results, pages not opened.
- **The one thing that would make it wrong:** Capacity at the year's end set against demand on the ten highest days; batteries do not all run at full output at once, and the fleet table is EIA-860M's operating list.
- **Tables and license:** `storage_buildout_monthly` (public; erw:storage_buildout); `eia930_daily_demand` (public; eia930:daily_demand)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/cross_family/battery-per-peak-caiso-bat-peak.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/cross_family/battery-per-peak-caiso-bat-peak.reproduce.py)
- **Second route:** No second route in the warehouse: the fleet is EIA-860M and the peak days EIA-930; caiso_battery_storage begins in August 2025.
- **Why it matters, as a fact:** The share says how much of CAISO's heaviest demand its batteries could meet at full output for an hour.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 11. An authority's load factor: ERCOT (ERCO, EIA-930 balancing authority)

- **Reader:** the energy lead of an AI lab
- **The sentence:** The load factor of ERCOT (ERCO, EIA-930 balancing authority) (its mean hour of demand as a percent of its highest) was 66.6 percent in 2025, against 58.8 percent in 2019, the first full year the ERW holds.
- **The figure:** 66.6477 percent in 2025, against 58.762 in 2019, as this machine's run printed them (the draft's own: 66.6477 and 58.762)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/authorities/ba-load-factor-ba-erco.png
- **Compared with:** the same measure in 2019
- **Already known?** New as far as found: EIA's Today in Energy (https://www.eia.gov/todayinenergy/detail.php?id=63344, 2024) expected ERCOT's large flexible loads (mostly crypto mining and data centers) to use 54 billion kWh in 2025; no publisher found printing ERCOT's load factor by year. Ours: 66.6 percent in 2025 against 58.8 percent in 2019. Seen in search results, page not opened.
- **The one thing that would make it wrong:** EIA-930 demand for ERCOT with the hunt's fault rule (an hour above three times its year's median dropped); a single bad peak hour moves the ratio.
- **Tables and license:** `eia930_ba_demand_hourly` (public; eia:gridmonitor/sixMonthFiles)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/authorities/ba-load-factor-ba-erco.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/authorities/ba-load-factor-ba-erco.reproduce.py)
- **Second route:** Agree within 0.1 point: ERCOT own system load (table ercot_zone_load_hourly, from ERCOT native load files) gives a load factor of 66.603 percent in 2025 and 58.685 in 2019, against the draft 66.648 and 58.762 from EIA-930.
- **Why it matters, as a fact:** The load factor is the mean hour as a share of the highest: a higher one means demand is flatter across the year's hours.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 12. Building data centers: US private data center construction

- **Reader:** an investor in energy
- **The sentence:** The value of private data center construction put in place in the US was 49.74 USD billion in 2025, against 1.80 USD billion in 2014, the first full year the ERW holds.
- **The figure:** 49.737 USD billion in 2025, against 1.797 in 2014, as this machine's run printed them (the draft's own: 49.737 and 1.797)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/queues_deals_datacenters/dc-construction-us-dc-build.png
- **Compared with:** the same measure in 2014
- **Already known?** Known: the figure is the Census Bureau's own value put in place (Construction Spending, https://www.census.gov/construction/c30/historical_data.html); Statista (https://www.statista.com/statistics/1559548/private-sector-data-center-construction-completed-us) prints about 41 billion USD for 2025 from an earlier vintage, and an analysis of Census tables says data center spending passed office construction in December 2025. Ours: 49.74 billion USD in 2025 (current vintage). Seen in search results, pages not opened.
- **The one thing that would make it wrong:** Census revises the series each July; an earlier vintage gave about 41 billion USD for 2025 (Statista), so the figure holds for the vintage of 24 October 2026.
- **Tables and license:** `census_c30_construction_monthly` (public; census:c30_construction_spending)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/queues_deals_datacenters/dc-construction-us-dc-build.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/queues_deals_datacenters/dc-construction-us-dc-build.reproduce.py)
- **Second route:** Agree within the warehouse: the mean of Census's seasonally adjusted annual rates for 2025 is 49.71 billion USD against the sum of the not adjusted months, 49.74 (table as retrieved 24 October 2026, after Census's annual revision of July 2026). Statista, citing Census, gives about 41 billion for 2025: by its implied 2024 figure (about 31 billion against our 34.8) an earlier vintage.
- **Why it matters, as a fact:** Census's value put in place counts the money spent on data center buildings in the year, not projects announced.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 13. Electricity for commerce: Virginia

- **Reader:** the energy lead of an AI lab
- **The sentence:** The electricity sold to the commercial sector of Virginia was 78.7 TWh in 2024, against 28.1 TWh in 1990, the first full year the ERW holds.
- **The figure:** 78.7107 TWh in 2024, against 28.0818 in 1990, as this machine's run printed them (the draft's own: 78.7107 and 28.0818)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/demand/seds-elec-comm-sd-va.png
- **Compared with:** the same measure in 1990
- **Already known?** Known in part: EIA's Today in Energy (https://www.eia.gov/todayinenergy/detail.php?id=67664, 2026) says Virginia's commercial sales rose by nearly 30 million MWh from 2019 to 2025, faster than any state but Texas, tied to data centers; EPRINC (https://eprinc.org/virginia-electricity-demand-growth-the-case-of-data-centers/) gives 67.5 TWh of commercial demand in 2023. Ours adds the long view from EIA's State Energy Data System: 78.7 TWh in 2024 against 28.1 TWh in 1990. Seen in search results, pages not opened.
- **The one thing that would make it wrong:** EIA notes that changes in commercial and industrial sales from 2023 to 2024 largely reflect better reporting of data centers and crypto mining (Electric Power Annual, table 2.8): part of the rise may be customers moved between classes; SEDS figures are EIA estimates and are revised.
- **Tables and license:** `eia_seds_state_energy` (public; eia:seds)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/demand/seds-elec-comm-sd-va.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/demand/seds-elec-comm-sd-va.reproduce.py)
- **Second route:** Agree within 1 percent: EIA-861 annual sales summed over Virginia utilities (parts A and B) give 77.99 TWh of commercial sales in 2024, against the draft 78.7 from the State Energy Data System.
- **Why it matters, as a fact:** Virginia's commercial class carries most of its data centers (EIA); the 1990 figure is the state before them.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 14. The gas fleet's heat rate: the United States

- **Reader:** an investor in energy
- **The sentence:** The gas-fired fleet's fuel per MWh in the United States was 8.30 MMBtu per MWh in 2024, against 10.84 MMBtu per MWh in 2001, the first full year the ERW holds.
- **The figure:** 8.2976 MMBtu per MWh in 2024, against 10.8409 in 2001, as this machine's run printed them (the draft's own: 8.2976 and 10.8409)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/generation_pipeline/gas-heat-rate-hr-gas-us.png
- **Compared with:** the same measure in 2001
- **Already known?** Known in part: EIA's Today in Energy (https://www.eia.gov/todayinenergy/detail.php?id=32572) gives the gas fleet's heat rate at 8,471 Btu per kWh in 2006, falling 7 percent to 2015; EIA's Electric Power Annual table 8.2 (https://www.eia.gov/electricity/annual/html/epa_08_02.html) prints tested combined-cycle heat rates. Ours, fuel over generation from EIA-923: 8.30 MMBtu per MWh (8,298 Btu per kWh) in 2024 against 10.84 in 2001. Seen in search results, pages not opened.
- **The one thing that would make it wrong:** Fuel over generation summed from EIA-923 plant rows; plants that make heat for industry (combined heat and power) count fuel that is not all for power.
- **Tables and license:** `eia923_plant_fuel_annual` (public; eia:electricity/facility-fuel)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/generation_pipeline/gas-heat-rate-hr-gas-us.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/generation_pipeline/gas-heat-rate-hr-gas-us.reproduce.py)
- **Second route:** No second route in the warehouse: EIA-923 plant fuel is the only source of fuel and generation by plant for 2001 and 2024.
- **Why it matters, as a fact:** The fuel a gas fleet burns per MWh is its efficiency; with the gas price it sets the fleet's fuel cost per MWh.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 15. Lng's share of us gas: the United States

- **Reader:** an investor in energy
- **The sentence:** US LNG exports as a share of US dry gas production were 14.0 percent of dry production in 2025, against 0.1 percent of dry production in 2015, the first full year the ERW holds.
- **The figure:** 14.0222 percent of dry production in 2025, against 0.104861 in 2015, as this machine's run printed them (the draft's own: 14.0222 and 0.104861)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/gas/lng-share-us-lng.png
- **Compared with:** the same measure in 2015
- **Already known?** Known in part: EIA's Today in Energy (https://www.eia.gov/todayinenergy/detail.php?id=67484, 2026) gives US LNG exports of 15.1 Bcf a day in 2025, up 26 percent; no publisher found printing them as a share of dry production. Ours: 14.0 percent in 2025 against 0.1 percent in 2015. Seen in search results, page not opened.
- **The one thing that would make it wrong:** Dry production and LNG exports are EIA's monthly figures; 2025 months are preliminary and revised.
- **Tables and license:** `gas_balance_weekly` (public; erw:gas_balance_weekly)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/gas/lng-share-us-lng.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/gas/lng-share-us-lng.reproduce.py)
- **Second route:** No second route in the warehouse: EIA annual gas balance (eia_gas_balance_annual) has dry production but no LNG line.
- **Why it matters, as a fact:** The share is how much of the gas the United States produces now leaves by ship.
- **The audit's row:** checks 1 fixed, 2 pass, 3 pass; changed: the sentence: "was" made "were" after the plural subject (the chart's line under the title, drawn into the PNG, still has the old words)

### 16. Henry hub's daily move: Henry Hub, Louisiana

- **Reader:** a power trader
- **The sentence:** The median absolute daily change of the spot gas price at Henry Hub, Louisiana was 3.19 percent a day in 2025, against 2.01 percent a day in 1997, the first full year the ERW holds.
- **The figure:** 3.18841 percent a day in 2025, against 2.01344 in 1997, as this machine's run printed them (the draft's own: 3.18841 and 2.01344)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/prices/henry-hub-volatility-us-henry-hub.png
- **Compared with:** the same measure in 1997
- **Already known?** New as far as found: EIA prints the volatility of the Henry Hub front-month future (https://www.eia.gov/todayinenergy/detail.php?id=66984 gives the 2025 spot range, 2.65 to 9.86 USD per MMBtu); no publisher found printing the median absolute daily change of the spot price by year. Seen in search results, page not opened.
- **The one thing that would make it wrong:** Daily spot prices as EIA publishes them; days without a price are skipped, and a percentage move is larger at a low price level.
- **Tables and license:** `eia_fuel_spot_prices` (public; eia:natural-gas/pri/fut;eia:petroleum/pri/spt)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/prices/henry-hub-volatility-us-henry-hub.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/prices/henry-hub-volatility-us-henry-hub.reproduce.py)
- **Second route:** No second route in the warehouse: Henry Hub daily spot prices are only in eia_fuel_spot_prices.
- **Why it matters, as a fact:** The median daily move is the ordinary day's risk on the benchmark gas price, without the spikes.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 17. The gasoline crack: Gulf Coast conventional gasoline

- **Reader:** a power trader
- **The sentence:** The mean spread of Gulf Coast gasoline over WTI crude was 19.33 USD per barrel in 2025, against 2.04 USD per barrel in 1987, the first full year the ERW holds.
- **The figure:** 19.33 USD per barrel in 2025, against 2.03697 in 1987, as this machine's run printed them (the draft's own: 19.33 and 2.03697)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/oil_products_world/gasoline-crack-crack-gasoline.png
- **Compared with:** the same measure in 1987
- **Already known?** New as far as found: no publisher found printing the yearly mean of Gulf Coast gasoline spot less WTI; EIA's Today in Energy prints New York Harbor gasoline crack spreads (https://www.eia.gov/todayinenergy/detail.php?id=66964) and RBN Energy the Gulf Coast 3-2-1 spread (https://rbnenergy.com/daily-posts/analyst-insight/usgc-3-2-1-crack-spread-cools-remains-strong), both other measures. Seen in search results, pages not opened.
- **The one thing that would make it wrong:** Two spot series from EIA, on different bases (cents a gallon converted to dollars a barrel); a quality or location change in either series would move the spread.
- **Tables and license:** `eia_product_spot_prices` (public; eia:petroleum/pri/spt); `eia_fuel_spot_prices` (public; eia:natural-gas/pri/fut;eia:petroleum/pri/spt)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/oil_products_world/gasoline-crack-crack-gasoline.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/oil_products_world/gasoline-crack-crack-gasoline.reproduce.py)
- **Second route:** No second route in the warehouse: both spot series are only in eia_fuel_spot_prices.
- **Why it matters, as a fact:** The gap between Gulf Coast gasoline and WTI is the refiner's gross margin on gasoline before costs.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 18. Large-load tariffs: the minimum bill (a percent of contracted demand)

- **Reader:** the energy lead of an AI lab
- **The sentence:** The minimum bill (a percent of contracted demand), in the large-load tariffs the ERW holds, is 80 percent at the median of the 11 filings that state it (effective 2025 to 2027), from 75 percent (Duke Energy Carolinas, North Carolina) to 100 percent (South Carolina Public Service Authority, South Carolina).
- **The figure:** median 80.0, lowest 75.0, highest 100.0, filings 11; the draft says the same (the table as of run 20261119T131033Z) (this machine's run)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/large_load/tariff-min-bill-pct.png
- **Compared with:** 
- **Already known?** Known: Berkeley Lab's review of rate designs for large loads (https://eta-publications.lbl.gov/sites/default/files/2026-08/rate_designs_large_loads_2026.08.10.pdf, August 2026) gives a median minimum billing demand of 80 percent of contracted demand across the tariffs it reviewed; FactSet (https://insight.factset.com/minimum-billing-demand-a-key-component-in-u.s.-data-center-tariffs, November 2025) gives 80 to 100 percent. Ours: 80 percent at the median of 11 filings, from 75 to 100 percent. Seen in search results, pages not opened.
- **The one thing that would make it wrong:** The ERW's table of filed tariffs grows as filings are read (a draft on contract terms was withdrawn because one filing was added); a new filing moves the median.
- **Tables and license:** `utility_large_load_tariffs` (public; filed:large_load_tariffs)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/large_load/tariff-min-bill-pct.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/large_load/tariff-min-bill-pct.reproduce.py)
- **Second route:** Agree with the publisher: Berkeley Lab review of rate designs for large loads (August 2026) gives a median minimum bill of 80 percent of contracted demand, as ours.
- **Why it matters, as a fact:** The minimum bill is what a large load pays each month even if it uses less than it contracted.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 19. Co2 per mwh generated: ERCOT (ERCO, EIA-930 balancing authority)

- **Reader:** the energy lead of an AI lab
- **The sentence:** The CO2 emitted per MWh generated by the generators of ERCOT (ERCO, EIA-930 balancing authority) was 315 kg CO2 per MWh in 2025, against 408 kg CO2 per MWh in 2019, the first full year the ERW holds.
- **The figure:** 315.408 kg CO2 per MWh in 2025, against 408.475 in 2019, as this machine's run printed them (the draft's own: 315.408 and 408.475)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/authorities/ba-co2-intensity-ba-erco.png
- **Compared with:** the same measure in 2019
- **Already known?** New as far as found: ERCOT's 2025 mix (renewables 37 percent, wind 23 and solar 14, Houston Chronicle and Energy Capital HTX, https://energycapitalhtx.com/ercot-2025-report-solar) is printed; no publisher found printing ERCOT's CO2 per MWh generated by year from EIA-930. Ours: 315 kg CO2 per MWh in 2025 against 408 in 2019. Seen in search results, pages not opened.
- **The one thing that would make it wrong:** Emissions are EIA's estimates by fuel for EIA-930 (not measured at the stack); a change in EIA's factors would move the level.
- **Tables and license:** `eia930_all_emissions` (public; eia:gridmonitor/knownissues/xls); `eia930_ba_supply_hourly` (public; eia:gridmonitor/sixMonthFiles)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/authorities/ba-co2-intensity-ba-erco.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/authorities/ba-co2-intensity-ba-erco.reproduce.py)
- **Second route:** No second route in the warehouse: EIA-930 emissions estimates are the only hourly CO2 by authority.
- **Why it matters, as a fact:** CO2 per MWh generated is the figure a buyer of grid power uses for the emissions of its load in that grid.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 20. Days with a wide spread: ERCOT's West load zone (LZ_WEST)

- **Reader:** an investor in energy
- **The sentence:** The share of days at ERCOT's West load zone (LZ_WEST) whose highest hourly real-time price was at least USD 50 per MWh above its lowest was 84.1 percent of days in 2025, against 28.8 percent of days in 2015, the first full year the ERW holds.
- **The figure:** 84.1096 percent of days in 2025, against 28.7671 in 2015, as this machine's run printed them (the draft's own: 84.1096 and 28.7671)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/prices/wide-spread-days-ercot-lz-west.png
- **Compared with:** the same measure in 2015
- **Already known?** Known in part: Modo Energy and EnergyGPS (https://www.energygps.com/Newsletter/b/Blog-Lonely-Star-Batteries-3435685) write that batteries still capture a positive spread every day while the ceiling has come down; no publisher found printing the share of days with a 50 USD spread by year. Ours: 84.1 percent of days in 2025 against 28.8 percent in 2015 in the West zone. Seen in search results, pages not opened.
- **The one thing that would make it wrong:** The 50 USD threshold is the hunt's choice, in nominal dollars, on real-time hourly prices; a different threshold gives another share.
- **Tables and license:** `ercot_zone_prices_history` (public; ercot:NP4-180-ER;ercot:NP6-785-ER)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/prices/wide-spread-days-ercot-lz-west.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/prices/wide-spread-days-ercot-lz-west.reproduce.py)
- **Second route:** No second route in the warehouse for hourly real-time zone prices before 28 September 2026.
- **Why it matters, as a fact:** A day with a 50 USD gap between its dearest and cheapest hour is a day a battery can earn on.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 21. The late january 2026 cold: Texas (EIA's region)

- **Reader:** a power trader
- **The sentence:** The highest hour of demand in Texas (EIA's region) from 23 January 2026 to 2 February 2026, the days /events gives to the late January 2026 cold, was 75,599 MW, 32.9 percent above the mean of the same days' highest hours in the other 7 years held, 2019 to 2025 (56,873 MW).
- **The figure:** 75,599 MW in 2026, against 54,656 in 2019, as this machine's run printed them (the draft's own: 75,599 and 54,656)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/events/cold-2026-tex.png
- **Compared with:** the same measure in 2019, the same days' highest hours in 2019 to 2025
- **Already known?** Known: ERCOT Monthly Operational Overview, January 2026 (https://www.ercot.com/files/docs/2026/02/18/ERCOT-Monthly-Operational-Overview-January-2026.pdf) gives a preliminary January peak of 75,572 MW on 26 January 2026, below the winter record of about 80,500 MW of February 2025; ours 75,599 MW. Ours adds the comparison with the same days of 2019 to 2025. Seen in search results, page not opened.
- **The one thing that would make it wrong:** The window is the days the ERW's /events page gives to the cold; a wider or narrower window moves the peak and the comparison years.
- **Tables and license:** `eia930_ba_demand_hourly` (public; eia:gridmonitor/sixMonthFiles)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/events/cold-2026-tex.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/events/cold-2026-tex.reproduce.py)
- **Second route:** Agree: ERCOT own system load (ercot_zone_load_hourly) gives a highest hour of 75,572 MW from 23 January to 2 February 2026 and a mean of 56,899 MW over the same days of 2019 to 2025 (32.8 percent above), against the draft 75,599 MW and 32.9 percent from EIA-930; ERCOT monthly overview prints 75,572 MW.
- **Why it matters, as a fact:** The highest hour in a cold spell is what the grid had to meet; ERCOT's own load gives the same hour within 0.04 percent.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 22. Winter storm elliott: the Carolinas (EIA's region)

- **Reader:** an investor in energy
- **The sentence:** The highest hour of demand in the Carolinas (EIA's region) from 19 December 2022 to 29 December 2022, the days /events gives to Winter Storm Elliott, was 44,630 MW, 24.3 percent above the mean of the same days' highest hours in the other 7 years held, 2018 to 2025 (35,902 MW).
- **The figure:** 44,630 MW in 2022, against 33,078 in 2018, as this machine's run printed them (the draft's own: 44,630 and 33,078)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/events/elliott-2022-car.png
- **Compared with:** the same measure in 2018, the same days' highest hours in 2018 to 2025
- **Already known?** Known in part: Utility Dive (https://www.utilitydive.com/news/duke-energy-apologizes-for-winter-storm-outages-as-ferc-nerc-open-investig/639583/) reports Duke rolling blackouts in the Carolinas during Elliott, the first there, and a FERC and NERC inquiry; no publisher found printing the Carolinas region highest hour against the same days of other years. Ours: 44,630 MW, 24.3 percent above the mean of 2018 to 2025. Seen in search results, page not opened.
- **The one thing that would make it wrong:** The Carolinas region is EIA's grouping of authorities (Duke's two and others), held only for hours when every authority reported; a missing authority drops the hour.
- **Tables and license:** `eia930_ba_demand_hourly` (public; eia:gridmonitor/sixMonthFiles)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/events/elliott-2022-car.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/events/elliott-2022-car.reproduce.py)
- **Second route:** No second route in the warehouse: the Carolinas region exists only in EIA-930; Duke figures cover Duke alone.
- **Why it matters, as a fact:** Winter Storm Elliott brought the first rolling blackouts in the Carolinas; the figure is how far that week's highest hour stood above the same days in other years.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 23. What us reactors pay for uranium: the United States

- **Reader:** an investor in energy
- **The sentence:** The average price US reactor owners paid for uranium was 58.46 USD per pound U3O8e in 2025, against 10.81 USD per pound U3O8e in 2003, the first year EIA's report holds.
- **The figure:** 58.46 USD per pound U3O8e in 2025, against 10.81 in 2003, as this machine's run printed them (the draft's own: 58.46 and 10.81)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/coal_uranium_metals/uranium-price-us-uranium-price.png
- **Compared with:** the same measure in 2003
- **Already known?** Known: EIA's Uranium Marketing Annual Report 2025 (https://www.eia.gov/uranium/marketing/, July 2026) gives the weighted-average price of 58.46 USD a pound U3O8e for 2025, 11 percent above 2024; the draft repeats EIA's headline. Seen in search results, page not opened.
- **The one thing that would make it wrong:** EIA's weighted average of what owners paid on delivery, spot and long-term contracts together; 2025 is preliminary in EIA's report.
- **Tables and license:** `eia_uranium_marketing_annual` (public; eia:uranium_marketing_annual)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/coal_uranium_metals/uranium-price-us-uranium-price.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/coal_uranium_metals/uranium-price-us-uranium-price.reproduce.py)
- **Second route:** Agree: EIA Uranium Marketing Annual Report 2025 prints 58.46 USD a pound for 2025; the draft 58.46 (search result, page not opened).
- **Why it matters, as a fact:** The price US reactor owners pay for uranium is a fuel cost of every US nuclear plant.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 24. Uranium of us origin: the United States

- **Reader:** the energy lead of an AI lab
- **The sentence:** The share of the uranium bought for US reactors that was of US origin was 7.2 percent of uranium purchased in 2025, against 18.0 percent of uranium purchased in 2003, the first year EIA's report holds.
- **The figure:** 7.24947 percent of uranium purchased in 2025, against 18.0365 in 2003, as this machine's run printed them (the draft's own: 7.24947 and 18.0365)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/coal_uranium_metals/us-origin-uranium-us-uranium-origin.png
- **Compared with:** the same measure in 2003
- **Already known?** Known: EIA's Today in Energy (https://www.eia.gov/todayinenergy/detail.php?id=68044, 2026) says US-origin material was 7 percent of deliveries in 2025; ours 7.2 percent. The draft repeats EIA's own figure. Seen in search results, page not opened.
- **The one thing that would make it wrong:** Origin as reported by owners in EIA's survey; 2025 is preliminary.
- **Tables and license:** `eia_uranium_marketing_annual` (public; eia:uranium_marketing_annual)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/coal_uranium_metals/us-origin-uranium-us-uranium-origin.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/coal_uranium_metals/us-origin-uranium-us-uranium-origin.reproduce.py)
- **Second route:** Agree at the publisher precision: EIA prints 7 percent US-origin for 2025; the draft 7.2 (search result, page not opened).
- **Why it matters, as a fact:** The share says how much of the uranium bought for US reactors was mined in the United States.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 25. Coal by country: consumption: India

- **Reader:** an investor in energy
- **The sentence:** The coal consumption of India was 1,371.1 million short tons in 2024, against 107.8 million short tons in 1980, the first full year the ERW holds.
- **The figure:** 1,371.12 million short tons in 2024, against 107.796 in 1980, as this machine's run printed them (the draft's own: 1,371.12 and 107.796)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/coal_uranium_metals/wc-consumption-wc-ind.png
- **Compared with:** the same measure in 1980
- **Already known?** Known: the figure is EIA's own international series (republished by The Global Economy, https://www.theglobaleconomy.com/India/coal_production/, 1,371 million short tons for 2024); the IEA's Global Energy Review 2025 (https://www.iea.org/reports/global-energy-review-2025/coal) calls India's 2024 coal demand an all-time high. Seen in search results, pages not opened.
- **The one thing that would make it wrong:** EIA's international estimates in short tons; the IEA counts in tonnes of coal equivalent, so the two do not match unit for unit.
- **Tables and license:** `eia_world_coal_annual` (public; eia:international_bulk)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/coal_uranium_metals/wc-consumption-wc-ind.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/coal_uranium_metals/wc-consumption-wc-ind.reproduce.py)
- **Second route:** Agree: EIA international data as republished by The Global Economy give 1,371.1 million short tons for 2024; the same source as the draft, so not independent.
- **Why it matters, as a fact:** India's coal demand reached an all-time high in 2024, up about 5.5 percent (IEA, Global Energy Review 2025).
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 26. The power sector's co2 per mwh: the United States

- **Reader:** the energy lead of an AI lab
- **The sentence:** The power sector's CO2 per MWh generated in the United States was 362 kg CO2 per MWh in 2022, against 604 kg CO2 per MWh in 2001, the first year this measure counts.
- **The figure:** 362.127 kg CO2 per MWh in 2022, against 604.462 in 2001, as this machine's run printed them (the draft's own: 362.127 and 604.462)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/emissions_climate/power-co2-per-mwh-co2mwh-us.png
- **Compared with:** the same measure in 2001
- **Already known?** Known in part: EIA Today in Energy (https://www.eia.gov/todayinenergy/detail.php?id=53819) gives the carbon intensity of US generation at 854 pounds per MWh (387 kg) in 2020, down 18 percent from 2016; ours, from EIA power-sector CO2 and generation, 362 kg per MWh in 2022 against 604 in 2001. Seen in search results, page not opened.
- **The one thing that would make it wrong:** EIA's power-sector CO2 over its net generation, through 2022 (the table's latest year); 2023 onward is not in it.
- **Tables and license:** `eia_co2_state_annual` (public; eia:co2-emissions/co2-emissions-aggregates); `eia_state_generation_monthly` (public; eia:electricity/electric-power-operational-data)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/emissions_climate/power-co2-per-mwh-co2mwh-us.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/emissions_climate/power-co2-per-mwh-co2mwh-us.reproduce.py)
- **Second route:** No second route in the warehouse: EIA power-sector CO2 and generation are the only sources for 2022; EIA published 387 kg per MWh for 2020, a year the draft does not compare.
- **Why it matters, as a fact:** CO2 per MWh of the US power sector is the average emissions factor of grid power.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 27. Enrichment of us origin: the United States

- **Reader:** the energy lead of an AI lab
- **The sentence:** The share of the enrichment bought for US reactors that was done in the US was 22.8 percent of enrichment services in 2025, against 13.9 percent of enrichment services in 2003, the first year EIA's report holds.
- **The figure:** 22.8346 percent of enrichment services in 2025, against 13.8831 in 2003, as this machine's run printed them (the draft's own: 22.8346 and 13.8831)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/coal_uranium_metals/us-enrichment-share-us-enrich-origin.png
- **Compared with:** the same measure in 2003
- **Already known?** Known: EIA's Uranium Marketing Annual Report 2025 (https://www.eia.gov/uranium/marketing/) gives a US-origin share of enrichment of 23 percent in 2025; ours 22.8 percent. The draft repeats EIA's own figure. Seen in search results, page not opened.
- **The one thing that would make it wrong:** Origin as reported by owners in EIA's survey; 2025 is preliminary.
- **Tables and license:** `eia_uranium_marketing_annual` (public; eia:uranium_marketing_annual)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/coal_uranium_metals/us-enrichment-share-us-enrich-origin.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/coal_uranium_metals/us-enrichment-share-us-enrich-origin.reproduce.py)
- **Second route:** Agree: EIA Uranium Marketing Annual Report 2025 gives a US-origin enrichment share of 23 percent; the draft 22.8 (search result, page not opened).
- **Why it matters, as a fact:** The share of the enrichment bought for US reactors that was done in the United States; EIA prints 23 percent for 2025.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 28. What a region burns: coal: Georgia and Alabama (the core of EIA's Southeast region)

- **Reader:** an investor in energy
- **The sentence:** Coal's share of the net generation of Georgia and Alabama (the core of EIA's Southeast region) was 14.4 percent in 2025, against 60.2 percent in 2001, the first full year the ERW holds.
- **The figure:** 14.4272 percent in 2025, against 60.2307 in 2001, as this machine's run printed them (the draft's own: 14.4272 and 60.2307)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/regions/coal-share-st-se-cow.png
- **Compared with:** the same measure in 2001
- **Already known?** Known in part: Southern Company's key non-financial metrics (https://www.southerncompany.com/content/dam/southerncompany/sustainability/pdfs/key-non-financial-metrics.pdf) give coal at 17 to 20 percent of its system's generation in recent years; no publisher found printing Georgia and Alabama together by year. Ours, from EIA's state generation: 14.4 percent in 2025 against 60.2 percent in 2001. Seen in search results, page not opened.
- **The one thing that would make it wrong:** EIA's state generation summed for two states, not EIA's whole Southeast region; utility-scale generation only.
- **Tables and license:** `eia_state_generation_monthly` (public; eia:electricity/electric-power-operational-data)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/regions/coal-share-st-se-cow.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/regions/coal-share-st-se-cow.reproduce.py)
- **Second route:** No second route found for Georgia and Alabama together.
- **Why it matters, as a fact:** Georgia and Alabama are Southern Company's home states; the share is coal's place in their power.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 29. What a region burns: natural gas: Florida (the state)

- **Reader:** a power trader
- **The sentence:** Natural gas's share of the net generation of Florida (the state) was 73.0 percent in 2025, against 22.8 percent in 2001, the first full year the ERW holds.
- **The figure:** 72.9527 percent in 2025, against 22.8179 in 2001, as this machine's run printed them (the draft's own: 72.9527 and 22.8179)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/regions/gas-share-st-fla-ng.png
- **Compared with:** the same measure in 2001
- **Already known?** Known: EIA state profile for Florida (https://www.eia.gov/state/?sid=FL) gives natural gas about 75 percent of 2024 generation, and EIA Today in Energy (https://www.eia.gov/todayinenergy/detail.php?id=60221) 31 percent in 2002 and 75 percent in 2022; ours 73.0 percent in 2025 against 22.8 in 2001. Seen in search results, pages not opened.
- **The one thing that would make it wrong:** EIA's state net generation; small-scale solar is not in the denominator.
- **Tables and license:** `eia_state_generation_monthly` (public; eia:electricity/electric-power-operational-data)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/regions/gas-share-st-fla-ng.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/regions/gas-share-st-fla-ng.reproduce.py)
- **Second route:** In part: EIA state profile gives about 75 percent for 2024; the draft table gives 2025 (73.0); the two years differ.
- **Why it matters, as a fact:** Florida burns gas for most of its power, so its power demand is a large and steady draw on gas.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 30. What a region generates: solar: Arizona and New Mexico (the core of EIA's Southwest region)

- **Reader:** an investor in energy
- **The sentence:** Utility-scale solar's share of the net generation of Arizona and New Mexico (the core of EIA's Southwest region) was 14.0 percent in 2025, against 0.0 percent in 2001, the first full year the ERW holds.
- **The figure:** 13.9626 percent in 2025, against 0.000396 in 2001, as this machine's run printed them (the draft's own: 13.9626 and 0.000396)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/regions/solar-share-st-sw-sun.png
- **Compared with:** the same measure in 2001
- **Already known?** Known in part: Ember (https://ember-energy.org/latest-insights/solar-met-61-of-us-electricity-demand-growth-in-2025/) gives New Mexico solar rising from 7 to 17 percent over the 24 months to October 2025 (all solar); Climate Central gives wind and solar about 20 percent in Arizona. No publisher found printing utility-scale solar for Arizona and New Mexico together. Ours: 14.0 percent in 2025 against 0.0 in 2001. Seen in search results, pages not opened.
- **The one thing that would make it wrong:** Utility-scale only, from EIA's state data; rooftop solar is left out of both share and total.
- **Tables and license:** `eia_state_generation_monthly` (public; eia:electricity/electric-power-operational-data)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/regions/solar-share-st-sw-sun.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/regions/solar-share-st-sw-sun.reproduce.py)
- **Second route:** No second route found for Arizona and New Mexico together.
- **Why it matters, as a fact:** Arizona and New Mexico are the core of EIA's Southwest region; utility-scale solar's share of their generation.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 31. What businesses buy: the United States

- **Reader:** the energy lead of an AI lab
- **The sentence:** Retail electricity sales to the commercial sector in the United States were 1,503.3 TWh in 2025, against 1,083.1 TWh in 2001, the first full year the ERW holds.
- **The figure:** 1,503.31 TWh in 2025, against 1,083.07 in 2001, as this machine's run printed them (the draft's own: 1,503.31 and 1,083.07)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/tariffs_policy/commercial-sales-com-sales-us.png
- **Compared with:** the same measure in 2001
- **Already known?** Known: EIA Electric Power Monthly table 5.1 (https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_1, opened 19 November 2026) prints 1,503,310 thousand MWh of commercial sales for 2025 and 1,450,941 for 2024; the draft repeats EIA own total and sets it against 2001 (1,083.1 TWh).
- **The one thing that would make it wrong:** EIA's 2025 months are preliminary; EIA notes that 2023 to 2024 changes in commercial and industrial sales largely reflect better reporting of data centers and crypto mining (table 2.8).
- **Tables and license:** `eia_retail_sales_monthly` (public; eia:electricity/retail-sales)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/tariffs_policy/commercial-sales-com-sales-us.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/tariffs_policy/commercial-sales-com-sales-us.reproduce.py)
- **Second route:** Agree: EIA Electric Power Monthly table 5.1 (https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_1, opened 19 November 2026) gives 1,503,310 thousand MWh of commercial sales for 2025; the draft 1,503.3 TWh.
- **Why it matters, as a fact:** Commercial sales are the class most US data centers are billed in; EIA's own table 5.1 prints the same total.
- **The audit's row:** checks 1 fixed, 2 pass, 3 pass; changed: the sentence: "was" made "were" after the plural subject (the chart's line under the title, drawn into the PNG, still has the old words)

### 32. Europe's electricity: coal and manufactured gases: Greece

- **Reader:** an investor in energy
- **The sentence:** The share of coal and manufactured gases in the net electricity production of Greece was 5.3 percent in 2025, against 31.8 percent in 2017, the first full year the ERW holds.
- **The figure:** 5.29206 percent in 2025, against 31.8315 in 2017, as this machine's run printed them (the draft's own: 5.29206 and 31.8315)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/world_power/eu-share-coal-eu-el.png
- **Compared with:** the same measure in 2017
- **Already known?** Known: Ember European Electricity Review 2026 (https://ember-energy.org/EER2026) says Greece cut coal to about 5 percent of its electricity in 2025; ours, from Eurostat net production, 5.3 percent. The draft repeats Ember headline. Seen in search results, page not opened.
- **The one thing that would make it wrong:** Eurostat's 2025 months are provisional; coal here includes manufactured gases.
- **Tables and license:** `eurostat_electricity_monthly` (public; eurostat:nrg_cb_pem_nrg_cb_em)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/world_power/eu-share-coal-eu-el.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/world_power/eu-share-coal-eu-el.reproduce.py)
- **Second route:** Agree at the publishers precision: Ember gives about 5 percent and CCPI 5.4 percent for Greece coal in 2025; the draft 5.3 from Eurostat (search results, pages not opened).
- **Why it matters, as a fact:** Greece cut coal from about a third of its electricity to about a twentieth in eight years; Ember prints the same 2025 share.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 33. Cooling degree days: Texas (EIA's region)

- **Reader:** a power trader
- **The sentence:** The mean cooling degree days a day in Texas (EIA's region) (base 65 F, from its hourly temperature) was 9.94 degree days a day in 2024, against 8.93 degree days a day in 2019, the first full year the ERW holds.
- **The figure:** 9.9366 degree days a day in 2024, against 8.93395 in 2019, as this machine's run printed them (the draft's own: 9.9366 and 8.93395)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/weather/cdd-wd-tex.png
- **Compared with:** the same measure in 2019
- **Already known?** Known in part: ERCOT's Summer 2024 operational review (https://ercot.com/files/docs/2024/10/03/7-summer-2024-operational-and-market-review.pdf) ranks June to August 2024 the sixth hottest Texas summer since 1895, cooler than 2022 and 2023; no publisher found printing cooling degree days from EIA's regional hourly temperature. Ours: 9.94 degree days a day in 2024 against 8.93 in 2019. Seen in search results, page not opened.
- **The one thing that would make it wrong:** Computed from the ERW's hourly temperature for EIA's Texas region (a population-weighted set of stations), not NOAA's official degree days.
- **Tables and license:** `region_weather_hourly` (public; erw:region_weather_hourly)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/weather/cdd-wd-tex.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/weather/cdd-wd-tex.reproduce.py)
- **Second route:** No second route in the warehouse: the population-weighted regional temperature is the only hourly temperature for EIA regions.
- **Why it matters, as a fact:** Cooling degree days are the heat that drives Texas summer demand.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 34. Europe's electricity: solar: the European Union (27)

- **Reader:** an investor in energy
- **The sentence:** The share of solar in the net electricity production of the European Union (27) was 13.0 percent in 2025, against 3.8 percent in 2017, the first full year the ERW holds.
- **The figure:** 13.0051 percent in 2025, against 3.79508 in 2017, as this machine's run printed them (the draft's own: 13.0051 and 3.79508)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/world_power/eu-share-solar-eu-eu27-2020.png
- **Compared with:** the same measure in 2017
- **Already known?** Known: Ember's European Electricity Review 2026 (https://ember-energy.org/EER2026, January 2026) gives solar 13 percent of EU electricity in 2025 (369 TWh), from 11.1 percent in 2024; ours, from Eurostat's net production, is 13.0 percent. The draft repeats Ember's headline. Seen in search results, page not opened.
- **The one thing that would make it wrong:** Eurostat's monthly figures for 2025 are provisional and revised.
- **Tables and license:** `eurostat_electricity_monthly` (public; eurostat:nrg_cb_pem_nrg_cb_em)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/world_power/eu-share-solar-eu-eu27-2020.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/world_power/eu-share-solar-eu-eu27-2020.reproduce.py)
- **Second route:** Agree at the publisher precision: Ember gives 13 percent for EU solar in 2025; the draft 13.0 from Eurostat (search result, page not opened).
- **Why it matters, as a fact:** Solar's share of EU electricity, from Eurostat's own net production.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 35. Europe's electricity: net imports: Portugal

- **Reader:** a power trader
- **The sentence:** The net imports of electricity of Portugal as a percent of the electricity available to it were 17.7 percent in 2025, against -10.0 percent in 2016, the first full year the ERW holds.
- **The figure:** 17.6645 percent in 2025, against -9.97587 in 2016, as this machine's run printed them (the draft's own: 17.6645 and -9.97587)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/world_power/eu-net-imports-eu-pt.png
- **Compared with:** the same measure in 2016
- **Already known?** Known: Portuguese reports of 2025 (Energia Estrategica, https://energiaestrategica.com/renewables-set-new-record-in-portugal-covering-nearly-70-of-power-demand-in-2025/) say imports covered 17 percent of Portugal demand in 2025, down from 20 in 2024; ours, from Eurostat, 17.7 percent of electricity available. Seen in search results, page not opened.
- **The one thing that would make it wrong:** Eurostat's monthly balance; the April 2025 Iberian blackout month is in the year.
- **Tables and license:** `eurostat_electricity_monthly` (public; eurostat:nrg_cb_pem_nrg_cb_em)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/world_power/eu-net-imports-eu-pt.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/world_power/eu-net-imports-eu-pt.reproduce.py)
- **Second route:** In part: Portuguese sources give imports at 17 percent of demand in 2025; the draft 17.7 percent of electricity available (Eurostat), a different base.
- **Why it matters, as a fact:** Portugal's net imports, nearly all from Spain, are the share of its power it does not make.
- **The audit's row:** checks 1 fixed, 2 pass, 3 pass; changed: the sentence: "was" made "were" after the plural subject (the chart's line under the title, drawn into the PNG, still has the old words)

### 36. Europe's electricity: wind: Finland

- **Reader:** an investor in energy
- **The sentence:** The share of wind in the net electricity production of Finland was 27.9 percent in 2025, against 4.6 percent in 2016, the first full year the ERW holds.
- **The figure:** 27.9164 percent in 2025, against 4.6214 in 2016, as this machine's run printed them (the draft's own: 27.9164 and 4.6214)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/world_power/eu-share-wind-eu-fi.png
- **Compared with:** the same measure in 2016
- **Already known?** Known: Ember (https://ember-energy.org/latest-insights/european-electricity-review-2026/2025-at-a-glance/) gives wind 27 percent of Finnish electricity in 2025, a record; Renewables Finland (https://suomenuusiutuvat.fi/en/wind-power-statistics-2025/) 27.9 percent. Ours, Eurostat net production: 27.9 percent. Seen in search results, pages not opened.
- **The one thing that would make it wrong:** Eurostat's 2025 months are provisional; Finland's own statistics differ by a few tenths.
- **Tables and license:** `eurostat_electricity_monthly` (public; eurostat:nrg_cb_pem_nrg_cb_em)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/world_power/eu-share-wind-eu-fi.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/world_power/eu-share-wind-eu-fi.reproduce.py)
- **Second route:** Agree: Renewables Finland gives 27.9 percent for 2025; the draft 27.9 from Eurostat (search result, page not opened).
- **Why it matters, as a fact:** Wind's share of Finland's electricity, from Eurostat.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 37. The us share of world oil: the United States

- **Reader:** an investor in energy
- **The sentence:** The US share of world petroleum and other liquids production was 22.3 percent of world production in 2025, against 14.5 percent of world production in 1993, the first full year the ERW holds.
- **The figure:** 22.3223 percent of world production in 2025, against 14.4734 in 1993, as this machine's run printed them (the draft's own: 22.3223 and 14.4734)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/oil_products_world/us-liquids-share-us-world-liquids.png
- **Compared with:** the same measure in 1993
- **Already known?** Known in part: EIA's Today in Energy (https://www.eia.gov/todayinenergy/detail.php?id=67844, July 2026) gives US crude output of 13.6 million barrels a day in 2025, about 40 percent above Russia and Saudi Arabia; no publisher found printing the US share of world petroleum and other liquids. Ours: 22.3 percent in 2025 against 14.5 percent in 1993. Seen in search results, page not opened.
- **The one thing that would make it wrong:** EIA's international estimates; other producers' figures are estimated and revised.
- **Tables and license:** `eia_world_oil_monthly` (public; eia:international_bulk)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/oil_products_world/us-liquids-share-us-world-liquids.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/oil_products_world/us-liquids-share-us-world-liquids.reproduce.py)
- **Second route:** No second route found: no publisher printing the US share of world liquids.
- **Why it matters, as a fact:** The US share of world petroleum and other liquids production includes natural gas plant liquids, where the US leads.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 38. By country: dry natural gas exports: the United States

- **Reader:** an investor in energy
- **The sentence:** The dry natural gas exports of the United States were 7,707 billion cubic feet in 2024, against 49 billion cubic feet in 1980, the first full year the ERW holds.
- **The figure:** 7,707.04 billion cubic feet in 2024, against 48.731 in 1980, as this machine's run printed them (the draft's own: 7,707.04 and 48.731)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/gas/wog-gas-exports-wog-usa.png
- **Compared with:** the same measure in 1980
- **Already known?** Known: EIA Natural Gas Annual table 9 (https://www.eia.gov/naturalgas/Annual/pdf/table_009.pdf) gives 2024 LNG exports of 4,367 Bcf and pipeline exports of 3,339 Bcf (7,706 together); EIA Today in Energy (https://www.eia.gov/todayinenergy/detail.php?id=64844) calls the US the largest LNG exporter in 2024. Ours, EIA international data, 7,707 Bcf. Seen in search results, pages not opened.
- **The one thing that would make it wrong:** EIA's international data; 2024 is the latest year in the table.
- **Tables and license:** `eia_world_oil_gas_annual` (public; eia:international_bulk)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/gas/wog-gas-exports-wog-usa.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/gas/wog-gas-exports-wog-usa.reproduce.py)
- **Second route:** Agree: EIA Natural Gas Annual table 9 gives 4,367 Bcf of LNG and 3,339 Bcf by pipeline in 2024, 7,706 together; the draft 7,707 (search result, page not opened).
- **Why it matters, as a fact:** US dry gas exports by pipeline and as LNG together.
- **The audit's row:** checks 1 fixed, 2 pass, 3 pass; changed: the sentence: "was" made "were" after the plural subject (the chart's line under the title, drawn into the PNG, still has the old words)

### 39. How hard reactors run: the US reactor fleet

- **Reader:** the energy lead of an AI lab
- **The sentence:** The mean daily power level of the US reactor fleet was 91.1 percent of full power in 2025, against 89.4 percent of full power in 2020, the first full year the ERW holds.
- **The figure:** 91.0813 percent of full power in 2025, against 89.4421 in 2020, as this machine's run printed them (the draft's own: 91.0813 and 89.4421)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/markets_operations/reactor-power-rp-us.png
- **Compared with:** the same measure in 2020
- **Already known?** Known: EIA's nuclear explainer (https://www.eia.gov/energyexplained/nuclear/us-nuclear-industry.php) gives a 2025 capacity factor of 91 percent, and NukeWorker (https://www.nukeworker.com/outages/industry_stats.php), from the NRC's daily power reports, 91.38 percent; ours, the mean daily power level from the same NRC reports, 91.1 percent. Seen in search results, pages not opened.
- **The one thing that would make it wrong:** The NRC's daily power status in percent of each reactor's licensed power, averaged over reactors and days, not weighted by size.
- **Tables and license:** `nrc_reactor_status` (public; nrc:power_reactor_status)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/markets_operations/reactor-power-rp-us.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/markets_operations/reactor-power-rp-us.reproduce.py)
- **Second route:** Agree within 0.3 point: NukeWorker from the NRC daily reports gives 91.38 percent for 2025, EIA a 91 percent capacity factor; the draft 91.1.
- **Why it matters, as a fact:** The mean daily power level of the US fleet is the share of nuclear capacity that ran on an average day.
- **The audit's row:** checks 1 pass, 2 pass, 3 pass; nothing changed

### 40. Coal by country: exports: Indonesia

- **Reader:** an investor in energy
- **The sentence:** The coal exports of Indonesia were 614.8 million short tons in 2024, against 0.4 million short tons in 1980, the first full year the ERW holds.
- **The figure:** 614.82 million short tons in 2024, against 0.423883 in 1980, as this machine's run printed them (the draft's own: 614.82 and 0.423883)
- **The chart:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/coal_uranium_metals/wc-exports-wc-idn.png
- **Compared with:** the same measure in 1980
- **Already known?** Known: Statistics Indonesia, via The Coal Hub (https://thecoalhub.com/indonesian-coal-exports-up-by-over-8-percent.html) and Reuters reports, gives a record 557.8 million tonnes exported in 2024 (about 615 million short tons) and calls Indonesia the largest thermal coal exporter; ours, EIA international data, 614.8 million short tons. Seen in search results, page not opened.
- **The one thing that would make it wrong:** EIA's international estimate in short tons; Indonesia's ministry gives about 555 million tonnes and another of its counts 433 million, by other definitions.
- **Tables and license:** `eia_world_coal_annual` (public; eia:international_bulk)
- **For Samuel's Stata run:** https://github.com/SamuelEnrique/erw/blob/main/docs/findings/coal_uranium_metals/wc-exports-wc-idn.reproduce.do (the Python: https://github.com/SamuelEnrique/erw/blob/main/docs/findings/coal_uranium_metals/wc-exports-wc-idn.reproduce.py)
- **Second route:** Agree: Statistics Indonesia gives 557.76 million tonnes exported in 2024, which is 614.8 million short tons; the draft 614.8 (search result, page not opened).
- **Why it matters, as a fact:** Indonesia is the largest exporter of thermal coal (Reuters, via The Coal Hub); Statistics Indonesia's record 557.76 million tonnes for 2024 is the same figure in other units.
- **The audit's row:** checks 1 fixed, 2 pass, 3 pass; changed: the sentence: "was" made "were" after the plural subject (the chart's line under the title, drawn into the PNG, still has the old words)

## By family

| Family | On the sheet |
|---|---:|
| authorities | 2 |
| coal_uranium_metals | 5 |
| cross_family | 1 |
| demand | 2 |
| emissions_climate | 1 |
| events | 2 |
| gas | 2 |
| generation_pipeline | 1 |
| large_load | 1 |
| markets_operations | 2 |
| oil_products_world | 2 |
| other_us | 2 |
| prices | 5 |
| queues_deals_datacenters | 1 |
| regions | 3 |
| tariffs_policy | 1 |
| trade | 2 |
| weather | 1 |
| world_power | 4 |

