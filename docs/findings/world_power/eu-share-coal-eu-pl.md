# Europe's electricity: coal and manufactured gases: Poland

Draft `scan-deep-5d609057f264` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The share of coal and manufactured gases in the net electricity production of Poland was 51.1 percent in 2025, against 78.2 percent in 2017, the first full year the ERW holds.

![Europe's electricity: coal and manufactured gases, Poland](eu-share-coal-eu-pl.png)

**The figure by full year** (percent): 2017: 78.2, 2018: 77.9, 2019: 73.0, 2020: 69.2, 2021: 71.8, 2022: 70.3, 2023: 59.4, 2024: 55.2, 2025: 51.1.

**The tables and rows.** `eurostat_electricity_monthly`; the rows for Poland, region key `eu_pl` (the card's `hunt.region`), years 2017 to 2025. The yearly values: `eu-share-coal-eu-pl.csv`.

**Its strength.** The change is 4.59 typical yearly moves (a typical move is 5.9 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 8 of the 8 full years after 2017 lie below 2017's value. Survives a change of window: from 2018 to 2025 the change is -26.8, from 2017 to 2024 it is -23.1. Sample large enough: 2017 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2018 to 2025 the change is -26.8, 98.8 percent of the change from 2017. At least one typical yearly move: the change is 4.59 typical yearly moves (5.9 percent a year, the median move between full years); the floor is 1.

**Its limits.** Eurostat's monthly electricity statistics as published, the latest months provisional; net production; a year counts with all twelve months of every figure.

**Reproduce.** `python eu-share-coal-eu-pl.reproduce.py <the table's CSV>` and `do eu-share-coal-eu-pl.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
