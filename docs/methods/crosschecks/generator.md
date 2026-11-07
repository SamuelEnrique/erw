# Cross-checks: What a generator earns (`/cost-of-power/seller`)

Energy Research Warehouse (ERW). Session 3707, chain 208, 6 November 2026. Roadmap item 2's cross-check table for the generator page: **each headline figure the page prints** against a figure a named publisher states. The headline figures are the 13 of `replication/generator/page_figures.json`: the default case, ERCOT, solar, 100 MW, priced at the hub average `HB_HUBAVG` in real time, the last twelve months October 2025 to September 2026.

- **Where the published figures come from.** Each is quoted from the method note's "Cross-checks" (`docs/methods/generator_earns_algorithm.md`), read on the dates it gives, after each host's robots file and terms. Nothing was fetched for this file.
- **The columns.** "Gap" is ours less theirs. "Reason" is one sentence, or "not explained". A figure with no published counterpart is said to have none.

| Headline figure (`page_figures.json` field) | Ours | Published figure | Source | Gap | Reason |
|---|---|---|---|---|---|
| Revenue, the last twelve months, USD per kW (`l12_kw`) | 59.85 | No published counterpart | | | No publisher's figure for the ERCOT solar fleet's merchant revenue per kW over these months is held |
| Long-run average, the last three full years, USD per kW a year (`three_kw`) | 102.24 | No published counterpart | | | The same |
| Long-run average, every full year held, USD per kW a year (`every_kw`) | 130.80 | No published counterpart | | | The same |
| Price received, USD per MWh (`price_received`) | 23.27 | No published counterpart held | | | Berkeley Lab's *Utility-Scale Solar* data file states solar's market value by ISO; it was not read for ERCOT, because the ruling on Berkeley Lab's terms is open (session 253) |
| Flat average over the same hours, USD per MWh (`flat_average`) | 32.17 | No published counterpart held | | | The same |
| Capture rate, percent of the flat average (`capture_rate`) | 72 | No published counterpart held | | | The same; for CAISO the note sets the capture rate beside Berkeley Lab's, which were read before the question was raised |
| Annual debt payments, USD (`debt_service`) | 7,078,769 | No published counterpart | | | Arithmetic of the page's capital cost (Lazard's midpoint), debt share and rate, each cross-checked in the note |
| Debt coverage, the last twelve months, times (`cover`) | 0.67 | The ATB's debt service coverage for utility-scale PV: 1.275 | [Annual Technology Baseline 2025, Financial Cases and Methods](https://atb.nlr.gov/electricity/2025/financial_cases_&_methods), "Financial Assumptions by Technology" (the note, read 21 October 2026) | -0.605 | The ATB's figure is the coverage a lender requires to size the debt; ours is what a merchant plant's last twelve months pay on Lazard's 60 percent debt |
| Energy sold, the last twelve months, MWh per MW (`l12_energy`) | 2,580 (a capacity factor of 29.5 percent) | Lazard's regional capacity factor for solar in ERCOT: 24 percent; utility-scale PV 20 to 30 percent | [Lazard, *Levelized Cost of Energy+*, June 2025](https://www.lazard.com/media/uounhon4/lazards-lcoeplus-june-2025.pdf), page 30 and LCOE v18.0, page 34 (the note) | +5.5 points against the ERCOT figure; inside the range | Ours is the ERCOT fleet's own output over its installed nameplate, which Lazard's assumed regional plant does not track |
| The same, against ERCOT's market monitor | 2,580 (29.5 percent) | "solar resources have an overall capacity factor of 23.8%" in 2025 | [Potomac Economics, *2025 State of the Market Report for the ERCOT Electricity Markets*, June 2026](https://www.potomaceconomics.com/wp-content/uploads/2026/06/2025-State-of-the-Market-Report-for-ERCOT.pdf), Chapter III, key insights (page 13), read by session 3708 on 6 November 2026 | +5.7 points | Ours is the fleet's output over EIA-860M's nameplate for October 2025 to September 2026; theirs is calendar 2025 over ERCOT's installed capacity, in a year when 6 percent of solar output was curtailed |
| The contract price at which coverage reaches 1.25 times, USD per MWh (`contract_price`) | 39.14 | Levelized cost of energy, utility-scale solar, unsubsidized: USD 38 to 78 per MWh | [Lazard, *Levelized Cost of Energy+*, June 2025](https://www.lazard.com/media/uounhon4/lazards-lcoeplus-june-2025.pdf), LCOE v18.0, page 8 (the note) | +1.14 to -38.86: inside the range, at its low end | Ours covers the debt 1.25 times and the fixed O&M only; Lazard's cost also returns 12 percent on the equity and pays taxes |
| NPV at the hurdle rate, USD million for 100 MW (`npv_million`) | -76.66 | No published counterpart | | | No publisher states a project NPV for this plant |
| Breakeven PPA price over the PPA term, USD per MWh (`breakeven_ppa`) | 58.36 | Levelized cost of energy, utility-scale solar, unsubsidized: USD 38 to 78 per MWh | [Lazard, *Levelized Cost of Energy+*, June 2025](https://www.lazard.com/media/uounhon4/lazards-lcoeplus-june-2025.pdf), LCOE v18.0, page 8 (the note) | +20.36 to -19.64: inside the range | Both are the price at which the equity earns 12 percent; ours is the ERCOT fleet's output at Lazard's midpoint costs with the ATB's 0.7 percent degradation, and Lazard's range spans sites and costs |
| The worst month (2024-02), USD for 100 MW (`worst_1_usd`) | 139,298.97 | No published counterpart | | | One month of the page's own fleet-shape revenue |

## The largest gaps, in one line each

- **Debt coverage: 0.67 against the ATB's 1.275.** A merchant solar plant's last twelve months do not pay a lender's required coverage on Lazard's 60 percent debt. The page's contract price (39.14) is what would.
- **Capacity factor: +5.5 points against Lazard's ERCOT figure.** The fleet's own output, not an assumed plant.

## Not compared, and why

- Nine of the 13 figures have no published counterpart: revenue per kW and its long-run averages, the debt payments, the NPV, the worst month, and the price received, the flat average and the capture rate.
- For the last three, the publisher that states them (Berkeley Lab) waits on the open ruling on its terms. Its CAISO figures in the note were read before that question was raised.
- The note's rows for CAISO, the gas peaker, wind and the assumptions (capital, O&M, life, heat rate, cost of capital, tax credits) are of other cases or are assumptions, not the default case's headline figures.
