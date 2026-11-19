# Demand in the coldest hours: the Southwest (EIA's region)

Draft `scan-deep-9619f43f0ceb` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The mean demand of the Southwest (EIA's region) in the year's 50 coldest hours was 13,935 MW in 2025, against 12,772 MW in 2019, the first full year the ERW holds.

![Demand in the coldest hours, the Southwest (EIA's region)](cold-mw-wx-sw.png)

**The figure by full year** (MW): 2019: 12,772, 2020: 11,932, 2021: 11,628, 2022: 12,872, 2023: 13,258, 2024: 13,907, 2025: 13,935.

**The tables and rows.** `region_weather_hourly`, `eia930_ba_demand_hourly`; the rows for the Southwest (EIA's region), region key `wx_sw` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `cold-mw-wx-sw.csv`.

**Its strength.** The change is 1.52 typical yearly moves (a typical move is 768 MW, 1.4826 times the median absolute change between full years). Holds in more than one year: 4 of the 6 full years after 2019 lie above 2019's value. Survives a change of window: from 2020 to 2025 the change is 2,003, from 2019 to 2024 it is 1,136. Sample large enough: 2019 holds 8,708 and 2025 holds 8,628 observations; the floor is 8,000. Half the change remains without the first year: from 2020 to 2025 the change is 2,003, 172.2 percent of the change from 2019. At least one typical yearly move: the change is 1.52 typical yearly moves (768 MW a year, the median move between full years); the floor is 1.

**Its limits.** The region's temperature is the population-weighted mean of its chosen stations (docs/methods/region_weather.md); demand is the sum of its authorities that file it; a description of the year's extreme hours, not a model, and not adjusted for anything.

**Reproduce.** `python cold-mw-wx-sw.reproduce.py <the table's CSV>` and `do cold-mw-wx-sw.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
