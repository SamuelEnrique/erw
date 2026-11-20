# The winter's mean temperature: Tennessee (EIA's region)

Draft `scan-deep-885c37505719` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The mean temperature of January, February and December in Tennessee (EIA's region) was 41.3 F in 2025, against 45.3 F in 2019, the first full year the ERW holds.

![The winter's mean temperature, Tennessee (EIA's region)](winter-temp-wt-ten.png)

**The figure by full year** (F): 2019: 45.3, 2020: 44.1, 2021: 44.7, 2022: 42.3, 2023: 47.8, 2024: 44.2, 2025: 41.3.

**The tables and rows.** `region_weather_hourly`; the rows for Tennessee (EIA's region), region key `wt_ten` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `winter-temp-wt-ten.csv`.

**Its strength.** The change is 1.03 typical yearly moves (a typical move is 3.9 F, 1.4826 times the median absolute change between full years). Holds in more than one year: 5 of the 6 full years after 2019 lie below 2019's value. Survives a change of window: from 2020 to 2025 the change is -2.8, from 2019 to 2024 it is -1.1. Sample large enough: 2019 holds 2,148 and 2025 holds 2,070 observations; the floor is 2,000. Half the change remains without the first year: from 2020 to 2025 the change is -2.8, 70.7 percent of the change from 2019. At least one typical yearly move: the change is 1.03 typical yearly moves (3.9 F a year, the median move between full years); the floor is 1.

**Its limits.** The region's population-weighted temperature, hours every chosen station holds; a year's winter is its own January, February and December.

**Reproduce.** `python winter-temp-wt-ten.reproduce.py <the table's CSV>` and `do winter-temp-wt-ten.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
