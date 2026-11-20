# Europe's electricity: wind: Finland

Draft `scan-deep-9b98b58b35f1` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The share of wind in the net electricity production of Finland was 27.9 percent in 2025, against 4.6 percent in 2016, the first full year the ERW holds.

![Europe's electricity: wind, Finland](eu-share-wind-eu-fi.png)

**The figure by full year** (percent): 2016: 4.6, 2017: 7.3, 2018: 8.7, 2019: 9.1, 2020: 11.7, 2021: 11.6, 2022: 16.7, 2023: 18.5, 2024: 25.0, 2025: 27.9.

**The tables and rows.** `eurostat_electricity_monthly`; the rows for Finland, region key `eu_fi` (the card's `hunt.region`), years 2016 to 2025. The yearly values: `eu-share-wind-eu-fi.csv`.

**Its strength.** The change is 5.91 typical yearly moves (a typical move is 3.9 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 9 of the 9 full years after 2016 lie above 2016's value. Survives a change of window: from 2017 to 2025 the change is 20.6, from 2016 to 2024 it is 20.4. Sample large enough: 2016 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2017 to 2025 the change is 20.6, 88.3 percent of the change from 2016. At least one typical yearly move: the change is 5.91 typical yearly moves (3.9 percent a year, the median move between full years); the floor is 1.

**Its limits.** Eurostat's monthly electricity statistics as published, the latest months provisional; net production; a year counts with all twelve months of every figure.

**Reproduce.** `python eu-share-wind-eu-fi.reproduce.py <the table's CSV>` and `do eu-share-wind-eu-fi.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
