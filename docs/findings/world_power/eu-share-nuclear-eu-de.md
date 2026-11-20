# Europe's electricity: nuclear: Germany

Draft `scan-deep-28a4c5e17500` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The share of nuclear in the net electricity production of Germany was 0.0 percent in 2025, against 15.3 percent in 2016, the first full year the ERW holds.

![Europe's electricity: nuclear, Germany](eu-share-nuclear-eu-de.png)

**The figure by full year** (percent): 2016: 15.3, 2017: 12.5, 2018: 12.6, 2019: 13.1, 2020: 12.0, 2021: 12.6, 2022: 6.4, 2023: 1.5, 2024: 0.0, 2025: 0.0.

**The tables and rows.** `eurostat_electricity_monthly`; the rows for Germany, region key `eu_de` (the card's `hunt.region`), years 2016 to 2025. The yearly values: `eu-share-nuclear-eu-de.csv`.

**Its strength.** The change is 9.36 typical yearly moves (a typical move is 1.6 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 9 of the 9 full years after 2016 lie below 2016's value. Survives a change of window: from 2017 to 2025 the change is -12.5, from 2016 to 2024 it is -15.3. Sample large enough: 2016 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2017 to 2025 the change is -12.5, 82.2 percent of the change from 2016. At least one typical yearly move: the change is 9.36 typical yearly moves (1.6 percent a year, the median move between full years); the floor is 1.

**Its limits.** Eurostat's monthly electricity statistics as published, the latest months provisional; net production; a year counts with all twelve months of every figure.

**Reproduce.** `python eu-share-nuclear-eu-de.reproduce.py <the table's CSV>` and `do eu-share-nuclear-eu-de.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
