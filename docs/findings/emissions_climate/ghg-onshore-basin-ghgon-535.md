# Emissions from oil and gas production: onshore oil and gas production in the Green River Basin

Draft `scan-deep-6a3a0490c23b` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The sum of the emissions reported for onshore oil and gas production in the Green River Basin was 1.45 million t CO2e in 2023, against 3.21 million t CO2e in 2015, the first full year the ERW holds.

![Emissions from oil and gas production, onshore oil and gas production in the Green River Basin](ghg-onshore-basin-ghgon-535.png)

**The figure by full year** (million t CO2e): 2015: 3.21, 2016: 3.27, 2017: 2.71, 2018: 2.68, 2019: 2.28, 2020: 1.99, 2021: 1.57, 2022: 1.71, 2023: 1.45.

**The tables and rows.** `epa_ghgrp_facility_emissions`; the rows for onshore oil and gas production in the Green River Basin, region key `ghgon_535` (the card's `hunt.region`), years 2015 to 2023. The yearly values: `ghg-onshore-basin-ghgon-535.csv`.

**Its strength.** The change is 4.37 typical yearly moves (a typical move is 0.40 million t CO2e, 1.4826 times the median absolute change between full years). Holds in more than one year: 7 of the 8 full years after 2015 lie below 2015's value. Survives a change of window: from 2016 to 2023 the change is -1.82, from 2015 to 2022 it is -1.50. Sample large enough: 2015 holds 1 and 2023 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2016 to 2023 the change is -1.82, 103.2 percent of the change from 2015. At least one typical yearly move: the change is 4.37 typical yearly moves (0.40 million t CO2e a year, the median move between full years); the floor is 1.

**Its limits.** EPA's Greenhouse Gas Reporting Program as the facilities reported it (facilities above its 25,000 t threshold); a facility that drops below it leaves the sum. The basin is the American Association of Petroleum Geologists' province.

**Reproduce.** `python ghg-onshore-basin-ghgon-535.reproduce.py <the table's CSV>` and `do ghg-onshore-basin-ghgon-535.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
