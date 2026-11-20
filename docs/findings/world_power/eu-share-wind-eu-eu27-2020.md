# Europe's electricity: wind: the European Union (27)

Draft `scan-deep-d3e40795ebab` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The share of wind in the net electricity production of the European Union (27) was 17.7 percent in 2025, against 10.0 percent in 2016, the first full year the ERW holds.

![Europe's electricity: wind, the European Union (27)](eu-share-wind-eu-eu27-2020.png)

**The figure by full year** (percent): 2016: 10.0, 2017: 11.1, 2018: 11.6, 2019: 13.3, 2020: 15.1, 2021: 14.1, 2022: 15.9, 2023: 18.5, 2024: 18.5, 2025: 17.7.

**The tables and rows.** `eurostat_electricity_monthly`; the rows for the European Union (27), region key `eu_eu27_2020` (the card's `hunt.region`), years 2016 to 2025. The yearly values: `eu-share-wind-eu-eu27-2020.csv`.

**Its strength.** The change is 4.57 typical yearly moves (a typical move is 1.7 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 9 of the 9 full years after 2016 lie above 2016's value. Survives a change of window: from 2017 to 2025 the change is 6.6, from 2016 to 2024 it is 8.5. Sample large enough: 2016 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2017 to 2025 the change is 6.6, 85.2 percent of the change from 2016. At least one typical yearly move: the change is 4.57 typical yearly moves (1.7 percent a year, the median move between full years); the floor is 1.

**Its limits.** Eurostat's monthly electricity statistics as published, the latest months provisional; net production; a year counts with all twelve months of every figure.

**Reproduce.** `python eu-share-wind-eu-eu27-2020.reproduce.py <the table's CSV>` and `do eu-share-wind-eu-eu27-2020.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
