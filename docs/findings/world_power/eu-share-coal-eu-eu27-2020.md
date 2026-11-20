# Europe's electricity: coal and manufactured gases: the European Union (27)

Draft `scan-deep-af6762084c7d` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The share of coal and manufactured gases in the net electricity production of the European Union (27) was 9.2 percent in 2025, against 20.9 percent in 2017, the first full year the ERW holds.

![Europe's electricity: coal and manufactured gases, the European Union (27)](eu-share-coal-eu-eu27-2020.png)

**The figure by full year** (percent): 2017: 20.9, 2018: 19.7, 2019: 15.0, 2020: 12.3, 2021: 14.2, 2022: 15.7, 2023: 11.7, 2025: 9.2.

**The tables and rows.** `eurostat_electricity_monthly`; the rows for the European Union (27), region key `eu_eu27_2020` (the card's `hunt.region`), years 2017 to 2025. The yearly values: `eu-share-coal-eu-eu27-2020.csv`.

**Its strength.** The change is 3.13 typical yearly moves (a typical move is 3.7 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 7 of the 7 full years after 2017 lie below 2017's value. Survives a change of window: from 2018 to 2025 the change is -10.6, from 2017 to 2023 it is -9.2. Sample large enough: 2017 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2018 to 2025 the change is -10.6, 90.2 percent of the change from 2017. At least one typical yearly move: the change is 3.13 typical yearly moves (3.7 percent a year, the median move between full years); the floor is 1.

**Its limits.** Eurostat's monthly electricity statistics as published, the latest months provisional; net production; a year counts with all twelve months of every figure.

**Reproduce.** `python eu-share-coal-eu-eu27-2020.reproduce.py <the table's CSV>` and `do eu-share-coal-eu-eu27-2020.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
