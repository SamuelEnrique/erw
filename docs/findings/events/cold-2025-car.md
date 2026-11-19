# The january 2025 cold: the Carolinas (EIA's region)

Draft `scan-deep-d522305cdb18` of the findings hunt (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The highest hour of demand in the Carolinas (EIA's region) from 17 January 2025 to 26 January 2025, the days /events gives to the January 2025 cold, was 47,130 MW, 18.7 percent above the mean of the same days' highest hours in the other 6 years held, 2019 to 2024 (39,709 MW).

![The january 2025 cold, the Carolinas (EIA's region)](cold-2025-car.png)

**The figure by year** (the window's highest hour of demand, MW): 2019: 40,888, 2020: 38,702, 2021: 35,468, 2022: 40,566, 2023: 37,813, 2024: 44,816, 2025: 47,130.

**The tables and rows.** `eia930_ba_demand_hourly`; the authorities of the Carolinas (EIA's region) summed by hour, the hours from 01-17 to 01-26 of each year. The yearly values: `cold-2025-car.csv`.

**Its strength.** The gap is 3.26 typical spreads of the other years. The extreme of the years held: 2025's figure is 47,130 MW; the highest other year's is 44,816 MW. Clear by a typical spread: the distance from the other years' mean is 7,421 MW against a typical spread of 2,279 MW. Sample large enough: 6 other years each hold at least 90 percent of the window's hours; 2025 holds 240 of 240. Holds against the median: the distance from the other years' median is 7,496 MW. Not one hour: the window's third-highest hour is 98.6 percent of its highest.

**Its limits.** EIA-930 demand as the authorities filed it, summed by region (an hour held only when every authority filing demand that month holds it); demand served during a load shed is load served, a floor on what was wanted; the same calendar days in UTC of the other years, not the weekday-aligned baseline of the /events pages.

**Reproduce.** `python cold-2025-car.reproduce.py <eia930_ba_demand_hourly.csv>` and `do cold-2025-car.reproduce.do` (Stata) recompute every year's figure; each names the expected values at its top, and the claim's mean of the other years.
