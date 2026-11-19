# What power plants report to epa: the power plants of Texas that report to EPA

Draft `scan-deep-73c169f77127` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The sum of the direct emissions reported by the power plants of Texas that report to EPA was 202.1 million t CO2e in 2023, against 230.7 million t CO2e in 2015, the first year the ERW holds.

![What power plants report to epa, the power plants of Texas that report to EPA](ghg-power-state-ghgpp-tx.png)

**The figure by full year** (million t CO2e): 2015: 230.7, 2016: 227.7, 2017: 232.9, 2018: 223.8, 2019: 212.3, 2020: 194.4, 2021: 200.1, 2022: 207.1, 2023: 202.1.

**The tables and rows.** `epa_ghgrp_facility_emissions`; the rows for the power plants of Texas that report to EPA, region key `ghgpp_tx` (the card's `hunt.region`), years 2015 to 2023. The yearly values: `ghg-power-state-ghgpp-tx.csv`.

**Its strength.** The change is 3.04 typical yearly moves (a typical move is 9.4 million t CO2e, 1.4826 times the median absolute change between full years). Holds in more than one year: 7 of the 8 full years after 2015 lie below 2015's value. Survives a change of window: from 2016 to 2023 the change is -25.5, from 2015 to 2022 it is -23.6. Sample large enough: 2015 holds 1 and 2023 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2016 to 2023 the change is -25.5, 89.4 percent of the change from 2015. At least one typical yearly move: the change is 3.04 typical yearly moves (9.4 million t CO2e a year, the median move between full years); the floor is 1.

**Its limits.** EPA's Greenhouse Gas Reporting Program as the facilities reported it (facilities above its 25,000 t threshold); a facility that drops below it leaves the sum.

**Reproduce.** `python ghg-power-state-ghgpp-tx.reproduce.py <the table's CSV>` and `do ghg-power-state-ghgpp-tx.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
