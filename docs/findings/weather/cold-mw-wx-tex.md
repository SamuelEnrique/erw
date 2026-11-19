# Demand in the coldest hours: Texas (EIA's region)

Draft `scan-deep-8387ce33c16e` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The mean demand of Texas (EIA's region) in the year's 50 coldest hours was 72,548 MW in 2024, against 53,077 MW in 2019, the first full year the ERW holds.

![Demand in the coldest hours, Texas (EIA's region)](cold-mw-wx-tex.png)

**The figure by full year** (MW): 2019: 53,077, 2020: 48,572, 2021: 58,998, 2022: 67,093, 2023: 60,398, 2024: 72,548.

**The tables and rows.** `region_weather_hourly`, `eia930_ba_demand_hourly`; the rows for Texas (EIA's region), region key `wx_tex` (the card's `hunt.region`), years 2019 to 2024. The yearly values: `cold-mw-wx-tex.csv`.

**Its strength.** The change is 1.62 typical yearly moves (a typical move is 12,001 MW, 1.4826 times the median absolute change between full years). Holds in more than one year: 4 of the 5 full years after 2019 lie above 2019's value. Survives a change of window: from 2020 to 2024 the change is 23,977, from 2019 to 2023 it is 7,320. Sample large enough: 2019 holds 8,288 and 2024 holds 8,110 observations; the floor is 8,000. Half the change remains without the first year: from 2020 to 2024 the change is 23,977, 123.1 percent of the change from 2019. At least one typical yearly move: the change is 1.62 typical yearly moves (12,001 MW a year, the median move between full years); the floor is 1.

**Its limits.** The region's temperature is the population-weighted mean of its chosen stations (docs/methods/region_weather.md); demand is the sum of its authorities that file it; a description of the year's extreme hours, not a model, and not adjusted for anything.

**Reproduce.** `python cold-mw-wx-tex.reproduce.py <the table's CSV>` and `do cold-mw-wx-tex.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
