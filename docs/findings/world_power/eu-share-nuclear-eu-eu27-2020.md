# Europe's electricity: nuclear: the European Union (27)

Draft `scan-deep-589fcb48f186` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The share of nuclear in the net electricity production of the European Union (27) was 23.3 percent in 2025, against 27.4 percent in 2016, the first full year the ERW holds.

![Europe's electricity: nuclear, the European Union (27)](eu-share-nuclear-eu-eu27-2020.png)

**The figure by full year** (percent): 2016: 27.4, 2017: 26.3, 2018: 26.3, 2019: 26.7, 2020: 24.8, 2021: 25.5, 2022: 21.9, 2023: 22.8, 2024: 23.5, 2025: 23.3.

**The tables and rows.** `eurostat_electricity_monthly`; the rows for the European Union (27), region key `eu_eu27_2020` (the card's `hunt.region`), years 2016 to 2025. The yearly values: `eu-share-nuclear-eu-eu27-2020.csv`.

**Its strength.** The change is 3.98 typical yearly moves (a typical move is 1.0 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 9 of the 9 full years after 2016 lie below 2016's value. Survives a change of window: from 2017 to 2025 the change is -3.0, from 2016 to 2024 it is -3.9. Sample large enough: 2016 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2017 to 2025 the change is -3.0, 72.4 percent of the change from 2016. At least one typical yearly move: the change is 3.98 typical yearly moves (1.0 percent a year, the median move between full years); the floor is 1.

**Its limits.** Eurostat's monthly electricity statistics as published, the latest months provisional; net production; a year counts with all twelve months of every figure.

**Reproduce.** `python eu-share-nuclear-eu-eu27-2020.reproduce.py <the table's CSV>` and `do eu-share-nuclear-eu-eu27-2020.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
