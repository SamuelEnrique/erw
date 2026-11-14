# Cross-checks: the Grid tool (`/grid`)

Energy Research Warehouse (ERW). Session 3709, chain 208, 6 November 2026. Roadmap item 2's cross-check table for the Grid tool: **each headline figure the page prints** against a figure a named publisher states. The headline figures are those of `replication/grid/page_figures.json`:

- the Network and Gravity tabs' figures for the hour shown (2026-11-03 23:00 UTC, the snapshot built 2026-11-05T23:09:35Z);
- the carbon intensity the network colors by and the Clean tab's monthly block prints;
- the Ask panel's stored answers;
- and, by their kind, the Mix tab's latest-hour figures (live reads, not in the comparison).

**Where the published figures come from.**

- EPA's eGRID2023 summary tables and EIA's answer on CO2 per kWh, read by session 3709 on 6 November 2026 after each host's robots file. Both are works of the United States government; the figures are quoted.
- ERCOT's market monitor's *2025 State of the Market Report*, read by session 3708.
- The rows of `docs/methods/grid_network.md`, "Cross-checks" (session 381, with the dates given there).

**Session 5073, 13 November 2026.** Every row sourced (a figure with no published counterpart names its own key in `replication/grid/page_figures.json` or the EIA-930 table the page reads), and the two intensities "not explained" until then explained by the generation EIA-930 leaves out (`eia_annual_crosscheck.md`); EPA's eGRID2023 summary tables were read again for ERCT's and NEWE's generation (EPA's robots file allows `/system/files/`). `tests/test_session5073.py` holds every gap to ours less theirs.

**The columns.** "Gap" is ours less theirs. "Reason" is one sentence, or "not explained". A figure with no published counterpart is said to have none.

## The network: each grid's ties and net exchange in the hour

| Headline figure | Ours | Published figure | Source | Gap | Reason |
|---|---|---|---|---|---|
| Net export or import over a grid's reporting ties, the hour shown (`net\|export`, `net\|import`), here ERCOT -219, CAISO -2,172, PJM 2,554, MISO -3,761, NYISO -2,231, ISO-NE -547, SPP 571 MW | the hour of 2026-11-03 23:00 UTC | EIA-930's demand less net generation for the same grid and hour | [EIA, Form EIA-930](https://www.eia.gov/opendata/browser/electricity/rto) | not computed for this hour | No published counterpart held for this hour: the copies of `eia930_all_demand` and `eia930_all_generation` on this machine end on 30 September 2026. The rows below are the same comparison in hours the warehouse held |
| The same, in the hour shown on 14 October 2026 (2026-10-12 03:00 UTC): ERCOT 128, ISO-NE 156, NYISO 2,120 MW of net import | 128, 156, 2,120 | 128, 156, 2,111 MW | the same, read through the live set on 14 October 2026 (`grid_network.md`, session 266's replication file) | 0, 0, +9 MW | The three grids whose ties close EIA's balance |
| The same hour, the four others: CAISO 6,591, MISO 1,561, PJM -1,544, SPP -437 MW | as stated | 7,058, 103, -1,462, -964 MW | the same | -467, +1,458, -82, +527 MW | For these four the interchange a grid reports does not close EIA's balance of its generation and demand, over 360 hours as in this one (`grid_network.md`) |
| A tie's flow from each side (`net\|tie`), the pair rule | MISO's report of its tie to SPP, 15 February 2021: 95,060 MWh | SPP's report of the same tie: 95,390 MWh | [EIA, Form EIA-930, interchange data](https://www.eia.gov/opendata/browser/electricity/rto/interchange-data), as held in `eia930_all_interchange` | -330 MWh (0.3 percent) | Two operators' reports of one flow; the network reads the code that sorts first |
| The hour shown, its age at the refresh (`net\|lag`) | 48 hours (2026-11-03 23:00 to the refresh of 2026-11-05 23:09 UTC) | The same newest hour in EIA's bulk file, read 13 October 2026: 53 hours behind | [EIA, Form EIA-930 bulk files](https://www.eia.gov/electricity/gridmonitor/) (`grid_network.md`, session 247) | not comparable: another day | The lag is EIA's publication, not the ERW's refresh; on 13 October both routes read the same hour |
| The largest net exporter of all balancing authorities (`net\|topexport`) | SRP, 2,634 MW | No published counterpart | ours only: `net\|topexport` in `replication/grid/page_figures.json` | none | EIA publishes each authority's interchange, not a ranking |
| The largest flow on a grid's ties (`net\|maxflow`), the ties reporting (`net\|ties`) | per grid, as the page prints them | No published counterpart | ours only: `net\|maxflow` and `net\|ties` in `replication/grid/page_figures.json` | none | Counts and maxima of EIA's rows; no publisher states them |

## The gravity shape: each grid's net generation

| Headline figure | Ours | Published figure | Source | Gap | Reason |
|---|---|---|---|---|---|
| Net generation, EIA-930, summed over 2025: ERCOT | 485.2 TWh | 541.8 TWh, Form EIA-923's plant rows summed by balancing authority | [EIA, Form EIA-923, 2025 final file](https://www.eia.gov/electricity/data/eia923/xls/f923_2025.zip) (`grid_network.md`, session 323) | -10.45 percent | Likely, not EIA's statement: EIA-930 is what the authority meters, EIA-923 each plant's own net generation, industrial self-generation used on site among it |
| The same, CAISO | 185.4 TWh | 203.1 TWh | the same | -8.72 percent | The same reason |
| The same, PJM | 873.8 TWh | 878.1 TWh | the same | -0.48 percent | Within 1 percent in each of 2023 to 2025 |
| The same, SPP | 302.1 TWh | 293.2 TWh | the same | +3.05 percent | EIA-930 higher: likely generation SPP meters from plants EIA-923 codes to another authority |
| The same, the Lower 48 (the shape's scale) | 4,280.5 TWh | 4,494.7 TWh | the same | -4.76 percent | The sum of the reasons above |
| Net generation in the hour shown, the import as a share (`series\|eia930_all_generation`, `calc\|pct`) | not held for 2026-11-03 23:00 on this machine | No published counterpart for the hour | ours only: EIA-930's rows as the page reads them (`eia930_all_generation`) | none | The page reads EIA's own rows; a share of them is the page's arithmetic |

## Carbon intensity: the network's colors and the Clean tab's months

The page prints `carbon_intensity_*` figures by hour and by month. No publisher states the same hours and months, so this table sets the same tables, energy-weighted over 2023 (the year eGRID2023 states), beside the year's published rates. Ours is computed from `carbon_intensity_hourly` (`intensity_generation`) and `eia930_all_emissions` (`co2_emissions_generated`): the year's CO2 over its MWh, each hour's MWh its CO2 over its intensity, over the hours both hold.

| Headline figure | Ours, 2023 | Published figure, 2023 | Source | Gap | Reason |
|---|---|---|---|---|---|
| ERCOT (ERCO), kg CO2 per MWh of generation | 342.96 (8,640 hours, 440.1 TWh) | 332.87: eGRID subregion ERCT, ERCOT All, CO2 total output emission rate 733.862 lb/MWh | [EPA, eGRID2023 Summary Tables, Table 1](https://www.epa.gov/system/files/documents/2025-06/summary_tables_rev2.xlsx), read 6 November 2026 | +10.09 | The generation EIA-930 leaves out (session 5073, arithmetic under one assumption): in 2023 EIA-930 counts 7.53 percent less of ERCOT's generation than Form EIA-923 (`eia_annual_crosscheck.md`), the plant data eGRID is built from (eGRID's ERCT 477.1 TWh, its Table 2, read again on 13 November 2026). If the generation both count emits alike in each, what EIA-930 leaves out runs at (332.87 - 0.9247 x 342.96) / 0.0753 = about 209 kg per MWh, cleaner than ERCOT's mean, so leaving it out lifts ours. EIA-930's CO2 is also estimated from generation by fuel with fixed factors (`docs/methods/emissions.md`); this arithmetic does not separate the two |
| ISO-NE (ISNE) | 231.85 (8,760 hours) | 244.61: eGRID NEWE, NPCC New England, 539.275 lb/MWh | the same | -12.76 | The same arithmetic: in 2023 EIA-930 counts 6.51 percent less of ISO-NE's generation than Form EIA-923 (`eia_annual_crosscheck.md`; eGRID's NEWE 102.7 TWh). If the generation both count emits alike, what EIA-930 leaves out runs at (244.61 - 0.9349 x 231.85) / 0.0651 = about 428 kg per MWh, the rate of gas and oil plants, so leaving it out lowers ours. The fixed factors (`docs/methods/emissions.md`) are not separated from it |
| CAISO (CISO) | 197.38 (8,712 hours) | 194.35: eGRID CAMX, WECC California, 428.464 lb/MWh | the same | +3.03 | CAMX is California's plants, not CAISO's area, and the two differ by the utilities outside CAISO |
| The Lower 48 (US48) | 348.57 (8,760 hours, 4,039.0 TWh, 1,407.9 million tonnes) | 348.00: eGRID U.S., 767.209 lb/MWh | the same | +0.57 | Within 0.2 percent |
| The same | 348.57 | 366.03: "about 1.53 billion metric tons" of CO2 over "about 4.18 trillion kilowatthours", "about 0.81 pounds of CO2 emissions per kWh" (every U.S. utility-scale plant) | [EIA, "How much carbon dioxide is produced per kilowatthour of U.S. electricity generation?"](https://www.eia.gov/tools/faqs/faq.php?id=74&t=11), last updated 11 December 2024, read 6 November 2026 | -17.46 | EIA's annual figure counts Alaska, Hawaii and every utility-scale plant from Form EIA-923's fuel use; ours is EIA-930's hourly estimate for the Lower 48 |

## The Mix tab's latest hour

| Headline figure | Ours | Published figure | Source | Gap | Reason |
|---|---|---|---|---|---|
| The latest hour's demand, net generation and each source's MW (`series\|eia930_all_*`) | EIA's own rows | No other publisher states the hour | ours only: EIA-930's rows as the page reads them (`eia930_all_demand`, `eia930_all_generation`) | none | A reproduction, not a check: the page prints EIA's rows as EIA publishes them |
| California's generation, EIA-930's | 22,618 MW, the mean of 888 hours from 2026-08-26 to 2026-10-02 | CAISO's own supply figure: 24,358 MW | [CAISO, Today's Outlook, supply](https://www.caiso.com/todays-outlook/supply), as held (`grid_network.md`) | -1,740 MW | EIA's solar reads 944 MW lower and its wind 473 MW lower than CAISO's own; the page draws CAISO's supply from 2025-12-16 (the one join) |

## The Ask panel's stored answers

| Headline figure | Ours | Published figure | Source | Gap | Reason |
|---|---|---|---|---|---|
| ERCOT, HB_HUBAVG, 2024, the mean of the daily real-time on-peak means (s302:q01) | 31.57 USD per MWh | ERCOT's load-weighted average real-time energy price, 2024: USD 32.41 per MWh | [Potomac Economics, *2025 State of the Market Report for the ERCOT Electricity Markets*, June 2026](https://www.potomaceconomics.com/wp-content/uploads/2026/06/2025-State-of-the-Market-Report-for-ERCOT.pdf), Table 1 (page 7) | -0.84 | Two measures of one year: ours is the hub's weekday 16-hour block, theirs every interval of the market weighted by load |
| The Lower 48's carbon intensity, the mean of 2024's and 2025's months (s302:q19, s267:q27) | 337.48 and 344.75 kg CO2 per MWh | No published counterpart for 2024 or 2025 held | ours only: `s302:q19` and `s267:q27` in `replication/grid/page_figures.json` | none | eGRID2023 and EIA's answer state 2023 (the carbon table above) |
| Every other stored answer | as `replication/grid/page_figures.json` lists them | No published counterpart held | ours only: `replication/grid/page_figures.json` | none | Each is a monthly figure of a table the ERW derives (`cost_of_power_monthly`, `merchant_revenue_monthly`, `iso_curtailment_monthly`), or a queue count; "license needed" for NYISO, ISO-NE and MISO |

## The largest gaps, in one line each

- **ISO-NE's 2023 intensity: 12.76 kg CO2 per MWh below eGRID's NEWE.** The 6.51 percent of generation EIA-930 leaves out would run at about 428 kg per MWh, a gas or oil plant's rate.
- **ERCOT's 2023 intensity: 10.09 above eGRID's ERCT.** The 7.53 percent of generation EIA-930 leaves out in 2023 would run at about 209 kg per MWh, cleaner than ERCOT's mean.
- **ERCOT's and CAISO's net generation: 10.45 and 8.72 percent below Form EIA-923.**
- **The Lower 48: within 0.2 percent of eGRID and 17.46 kg below EIA's all-plant answer.**
