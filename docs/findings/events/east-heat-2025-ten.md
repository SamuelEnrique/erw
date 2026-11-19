# The june 2025 eastern heat wave: Tennessee (EIA's region)

Draft `scan-deep-ac47e568173b` of the findings hunt (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The highest hour of demand in Tennessee (EIA's region) from 20 June 2025 to 28 June 2025, the days /events gives to the June 2025 eastern heat wave, was 31,240 MW, 10.3 percent above the mean of the same days' highest hours in the other 7 years held, 2019 to 2026 (28,323 MW).

![The june 2025 eastern heat wave, Tennessee (EIA's region)](east-heat-2025-ten.png)

**The figure by year** (the window's highest hour of demand, MW): 2019: 27,092, 2020: 24,775, 2021: 28,376, 2022: 30,725, 2023: 27,631, 2024: 30,716, 2025: 31,240, 2026: 28,946.

**The tables and rows.** `eia930_ba_demand_hourly`; the authorities of Tennessee (EIA's region) summed by hour, the hours from 06-20 to 06-28 of each year. The yearly values: `east-heat-2025-ten.csv`.

**Its strength.** The gap is 1.53 typical spreads of the other years. The extreme of the years held: 2025's figure is 31,240 MW; the highest other year's is 30,725 MW. Clear by a typical spread: the distance from the other years' mean is 2,917 MW against a typical spread of 1,904 MW. Sample large enough: 7 other years each hold at least 90 percent of the window's hours; 2025 holds 216 of 216. Holds against the median: the distance from the other years' median is 2,864 MW. Not one hour: the window's third-highest hour is 99.8 percent of its highest.

**Its limits.** EIA-930 demand as the authorities filed it, summed by region (an hour held only when every authority filing demand that month holds it); demand served during a load shed is load served, a floor on what was wanted; the same calendar days in UTC of the other years, not the weekday-aligned baseline of the /events pages.

**Reproduce.** `python east-heat-2025-ten.reproduce.py <eia930_ba_demand_hourly.csv>` and `do east-heat-2025-ten.reproduce.do` (Stata) recompute every year's figure; each names the expected values at its top, and the claim's mean of the other years.
