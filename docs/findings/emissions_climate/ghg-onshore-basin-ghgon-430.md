# Emissions from oil and gas production: onshore oil and gas production in the Permian Basin

Draft `scan-deep-ff1b2d71d45d` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The sum of the emissions reported for onshore oil and gas production in the Permian Basin was 29.22 million t CO2e in 2023, against 13.56 million t CO2e in 2015, the first full year the ERW holds.

![Emissions from oil and gas production, onshore oil and gas production in the Permian Basin](ghg-onshore-basin-ghgon-430.png)

**The figure by full year** (million t CO2e): 2015: 13.56, 2016: 12.72, 2017: 15.80, 2018: 23.38, 2019: 32.08, 2020: 23.78, 2021: 23.30, 2022: 23.22, 2023: 29.22.

**The tables and rows.** `epa_ghgrp_facility_emissions`; the rows for onshore oil and gas production in the Permian Basin, region key `ghgon_430` (the card's `hunt.region`), years 2015 to 2023. The yearly values: `ghg-onshore-basin-ghgon-430.csv`.

**Its strength.** The change is 2.33 typical yearly moves (a typical move is 6.73 million t CO2e, 1.4826 times the median absolute change between full years). Holds in more than one year: 7 of the 8 full years after 2015 lie above 2015's value. Survives a change of window: from 2016 to 2023 the change is 16.49, from 2015 to 2022 it is 9.66. Sample large enough: 2015 holds 1 and 2023 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2016 to 2023 the change is 16.49, 105.3 percent of the change from 2015. At least one typical yearly move: the change is 2.33 typical yearly moves (6.73 million t CO2e a year, the median move between full years); the floor is 1.

**Its limits.** EPA's Greenhouse Gas Reporting Program as the facilities reported it (facilities above its 25,000 t threshold); a facility that drops below it leaves the sum. The basin is the American Association of Petroleum Geologists' province.

**Reproduce.** `python ghg-onshore-basin-ghgon-430.reproduce.py <the table's CSV>` and `do ghg-onshore-basin-ghgon-430.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
