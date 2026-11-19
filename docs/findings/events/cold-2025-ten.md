# The january 2025 cold: Tennessee (EIA's region)

Draft `scan-deep-c6236cf5912b` of the findings hunt (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The highest hour of demand in Tennessee (EIA's region) from 17 January 2025 to 26 January 2025, the days /events gives to the January 2025 cold, was 35,086 MW, 24.5 percent above the mean of the same days' highest hours in the other 7 years held, 2019 to 2026 (28,173 MW).

![The january 2025 cold, Tennessee (EIA's region)](cold-2025-ten.png)

**The figure by year** (the window's highest hour of demand, MW): 2019: 27,801, 2020: 27,399, 2021: 22,524, 2022: 28,358, 2023: 26,062, 2024: 34,351, 2025: 35,086, 2026: 30,714.

**The tables and rows.** `eia930_ba_demand_hourly`; the authorities of Tennessee (EIA's region) summed by hour, the hours from 01-17 to 01-26 of each year. The yearly values: `cold-2025-ten.csv`.

**Its strength.** The gap is 2.68 typical spreads of the other years. The extreme of the years held: 2025's figure is 35,086 MW; the highest other year's is 34,351 MW. Clear by a typical spread: the distance from the other years' mean is 6,913 MW against a typical spread of 2,578 MW. Sample large enough: 7 other years each hold at least 90 percent of the window's hours; 2025 holds 240 of 240. Holds against the median: the distance from the other years' median is 7,285 MW. Not one hour: the window's third-highest hour is 96.6 percent of its highest.

**Its limits.** EIA-930 demand as the authorities filed it, summed by region (an hour held only when every authority filing demand that month holds it); demand served during a load shed is load served, a floor on what was wanted; the same calendar days in UTC of the other years, not the weekday-aligned baseline of the /events pages.

**Reproduce.** `python cold-2025-ten.reproduce.py <eia930_ba_demand_hourly.csv>` and `do cold-2025-ten.reproduce.do` (Stata) recompute every year's figure; each names the expected values at its top, and the claim's mean of the other years.
