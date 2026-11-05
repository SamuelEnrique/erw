# Jersey's electricity balance a year, 2023 to 2025 (the Government of Jersey's Energy Trends 2025)

Energy Research Warehouse (ERW), method note written in session 2597 (chain 128) for a table first written on 25 October 2026 (session 2594).

Tables: `je_jersey_electricity_annual`

## Publisher and address

The Government of Jersey (the Cabinet Office since the report for 2024, Statistics Jersey before), Energy Trends 2025, the electricity column of its energy balances: Table 5 (2025) and Appendix Tables A3 (2023, updated) and A5 (2024, updated): `https://www.gov.je/SiteCollectionDocuments/Government%20and%20administration/Energy%20Trends%202025.pdf`. One GET, no key. Source id `je_gov:energy_trends_2025_balances`. Connector: `warehouse/connectors/je_jersey_electricity.py` (session 2594), whose raw store is `warehouse/raw/statsje/`. www.gov.je's robots file names `*` with no rule (read 1163).

## Vintage and revision

Written by run `20261025T035028Z` (the write under the lock, offline), which read the report saved at 2026-10-25T03:47:14Z. `vintage` is its last-modified time, 2026-08-12T10:57:49Z. Each year's report has its own address and updates the two years before.

## Shape and variables

Series, 45 rows (15 rows of the balance times three years), 15 entities. `entity` `je:jersey:<item>`: production, net_imports, stock_change, primary_supply, statistical_difference, primary_demand, generation_transformation, own_use_and_losses, final_consumption, and the six sectors commercial, residential, road, air, marine and agriculture; `variable` `electricity`; `unit` MWh; `ts_utc` the year's first day; `freq` P1Y; `geo` JE; `node` the report's label; `x_table` the table (5, A3, A5); `x_toe` the figure as printed in tonnes of oil equivalent.

In 2025: net imports 609.6 GWh (92.2% of the balance's primary supply), on-island production 51.6, primary supply 661.1, own use and losses 45.5, final consumption 616.5 (residential 344.7, commercial 260.3).

**The unit.** The balances are in whole toe; the table states them in MWh at 11.63 MWh a toe, the factor the report uses itself ("2.4 GWh (209 toe)"). Each MWh figure carries its toe's rounding, at most 5.8 MWh. The statistical difference may be negative.

## Reading the source

- The run stops at once, asking nothing, while `statsje` or www.gov.je is paused.
- One request a run; `--offline` reads the saved report.
- **Each balance** is found by its title line ("Table 5: Energy Balance for Jersey, 2025; toe" and the two appendix titles), once each, the year taken from the title; its rows are the lines of four figures (liquid fuels, gas, electricity, total) after it on the page, a footnote number after a label removed; only the electricity figure is taken.
- **Checks** within 1 toe each year: production, net imports and stock change to primary supply; primary supply less the statistical difference to primary demand; the six sectors to final consumption.
- The run stops, and no file is written, for: a title found other than once, a year given twice, a row missing or given twice, a check missed.

Nothing is filled. Not taken: the other fuels' columns; the report's charts of longer trends.

## License

Internal. gov.je's Terms and conditions (read 1164): "Copyright protected material may be reproduced free of charge in any format or medium for research, private study or for internal circulation within an organisation."; public republication is not among the purposes. Verdict: needs written permission (the cautious reading; a question for the owner). The open data portal's Open Government Licence - Jersey does not reach these figures (no energy dataset there, read 1166). Held from the live set and from Redivis.

## Cross-check

EIA's world table holds no Jersey. Within the report, 2025's net imports (52,415 toe) are 92.2% of the balance's primary supply of electricity (56,848 toe); the report's text gives imports as 93% of the public electricity supply, a measure of its own (imports before transmission losses against the public supply).
