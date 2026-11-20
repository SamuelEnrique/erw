# Europe's electricity: natural gas: the European Union (27)

Draft `scan-deep-c207f3dad1c8` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The share of natural gas in the net electricity production of the European Union (27) was 16.8 percent in 2025, against 13.1 percent in 2017, the first full year the ERW holds.

![Europe's electricity: natural gas, the European Union (27)](eu-share-gas-eu-eu27-2020.png)

**The figure by full year** (percent): 2017: 13.1, 2018: 12.3, 2019: 15.1, 2020: 15.4, 2021: 13.9, 2022: 19.6, 2023: 17.0, 2024: 15.3, 2025: 16.8.

**The tables and rows.** `eurostat_electricity_monthly`; the rows for the European Union (27), region key `eu_eu27_2020` (the card's `hunt.region`), years 2017 to 2025. The yearly values: `eu-share-gas-eu-eu27-2020.csv`.

**Its strength.** The change is 1.56 typical yearly moves (a typical move is 2.4 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 7 of the 8 full years after 2017 lie above 2017's value. Survives a change of window: from 2018 to 2025 the change is 4.6, from 2017 to 2024 it is 2.2. Sample large enough: 2017 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2018 to 2025 the change is 4.6, 122.6 percent of the change from 2017. At least one typical yearly move: the change is 1.56 typical yearly moves (2.4 percent a year, the median move between full years); the floor is 1.

**Its limits.** Eurostat's monthly electricity statistics as published, the latest months provisional; net production; a year counts with all twelve months of every figure.

**Reproduce.** `python eu-share-gas-eu-eu27-2020.reproduce.py <the table's CSV>` and `do eu-share-gas-eu-eu27-2020.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
