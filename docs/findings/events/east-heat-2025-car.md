# The june 2025 eastern heat wave: the Carolinas (EIA's region)

Draft `scan-deep-d05447657902` of the findings hunt (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The highest hour of demand in the Carolinas (EIA's region) from 20 June 2025 to 28 June 2025, the days /events gives to the June 2025 eastern heat wave, was 44,754 MW, 10.7 percent above the mean of the same days' highest hours in the other 7 years held, 2019 to 2026 (40,440 MW).

![The june 2025 eastern heat wave, the Carolinas (EIA's region)](east-heat-2025-car.png)

**The figure by year** (the window's highest hour of demand, MW): 2019: 39,320, 2020: 36,613, 2021: 39,656, 2022: 42,006, 2023: 39,007, 2024: 43,640, 2025: 44,754, 2026: 42,837.

**The tables and rows.** `eia930_ba_demand_hourly`; the authorities of the Carolinas (EIA's region) summed by hour, the hours from 06-20 to 06-28 of each year. The yearly values: `east-heat-2025-car.csv`.

**Its strength.** The gap is 1.24 typical spreads of the other years. The extreme of the years held: 2025's figure is 44,754 MW; the highest other year's is 43,640 MW. Clear by a typical spread: the distance from the other years' mean is 4,314 MW against a typical spread of 3,484 MW. Sample large enough: 7 other years each hold at least 90 percent of the window's hours; 2025 holds 216 of 216. Holds against the median: the distance from the other years' median is 5,098 MW. Not one hour: the window's third-highest hour is 99.7 percent of its highest.

**Its limits.** EIA-930 demand as the authorities filed it, summed by region (an hour held only when every authority filing demand that month holds it); demand served during a load shed is load served, a floor on what was wanted; the same calendar days in UTC of the other years, not the weekday-aligned baseline of the /events pages.

**Reproduce.** `python east-heat-2025-car.reproduce.py <eia930_ba_demand_hourly.csv>` and `do east-heat-2025-car.reproduce.do` (Stata) recompute every year's figure; each names the expected values at its top, and the claim's mean of the other years.
