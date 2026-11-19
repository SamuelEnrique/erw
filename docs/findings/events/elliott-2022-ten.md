# Winter storm elliott: Tennessee (EIA's region)

Draft `scan-deep-981d7817ada5` of the findings hunt (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The highest hour of demand in Tennessee (EIA's region) from 19 December 2022 to 29 December 2022, the days /events gives to Winter Storm Elliott, was 33,225 MW, 33.9 percent above the mean of the same days' highest hours in the other 7 years held, 2018 to 2025 (24,815 MW).

![Winter storm elliott, Tennessee (EIA's region)](elliott-2022-ten.png)

**The figure by year** (the window's highest hour of demand, MW): 2018: 22,240, 2019: 26,124, 2020: 25,592, 2021: 24,073, 2022: 33,225, 2023: 26,034, 2024: 25,623, 2025: 24,016.

**The tables and rows.** `eia930_ba_demand_hourly`; the authorities of Tennessee (EIA's region) summed by hour, the hours from 12-19 to 12-29 of each year. The yearly values: `elliott-2022-ten.csv`.

**Its strength.** The gap is 10.66 typical spreads of the other years. The extreme of the years held: 2022's figure is 33,225 MW; the highest other year's is 26,124 MW. Clear by a typical spread: the distance from the other years' mean is 8,410 MW against a typical spread of 789 MW. Sample large enough: 7 other years each hold at least 90 percent of the window's hours; 2022 holds 264 of 264. Holds against the median: the distance from the other years' median is 7,633 MW. Not one hour: the window's third-highest hour is 99.8 percent of its highest.

**Its limits.** EIA-930 demand as the authorities filed it, summed by region (an hour held only when every authority filing demand that month holds it); demand served during a load shed is load served, a floor on what was wanted; the same calendar days in UTC of the other years, not the weekday-aligned baseline of the /events pages.

**Reproduce.** `python elliott-2022-ten.reproduce.py <eia930_ba_demand_hourly.csv>` and `do elliott-2022-ten.reproduce.do` (Stata) recompute every year's figure; each names the expected values at its top, and the claim's mean of the other years.
