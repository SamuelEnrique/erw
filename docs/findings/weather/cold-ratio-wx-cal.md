# The coldest hours against the mean hour: California (EIA's region)

Draft `scan-deep-696631abc0dc` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The mean demand of California (EIA's region) in the year's 50 coldest hours as a percent of its mean hour was 87.8 percent in 2025, against 93.6 percent in 2019, the first full year the ERW holds.

![The coldest hours against the mean hour, California (EIA's region)](cold-ratio-wx-cal.png)

**The figure by full year** (percent): 2019: 93.6, 2020: 93.6, 2021: 94.9, 2022: 92.3, 2023: 94.3, 2024: 89.1, 2025: 87.8.

**The tables and rows.** `region_weather_hourly`, `eia930_ba_demand_hourly`; the rows for California (EIA's region), region key `wx_cal` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `cold-ratio-wx-cal.csv`.

**Its strength.** The change is 2.37 typical yearly moves (a typical move is 2.4 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 3 of the 6 full years after 2019 lie below 2019's value. Survives a change of window: from 2020 to 2025 the change is -5.9, from 2019 to 2024 it is -4.5. Sample large enough: 2019 holds 8,239 and 2025 holds 8,017 observations; the floor is 8,000. Half the change remains without the first year: from 2020 to 2025 the change is -5.9, 101.1 percent of the change from 2019. At least one typical yearly move: the change is 2.37 typical yearly moves (2.4 percent a year, the median move between full years); the floor is 1.

**Its limits.** The region's temperature is the population-weighted mean of its chosen stations (docs/methods/region_weather.md); demand is the sum of its authorities that file it; a description of the year's extreme hours, not a model, and not adjusted for anything.

**Reproduce.** `python cold-ratio-wx-cal.reproduce.py <the table's CSV>` and `do cold-ratio-wx-cal.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
