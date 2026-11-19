# The june 2025 eastern heat wave: the Mid-Atlantic (EIA's region)

Draft `scan-deep-907fb96bc601` of the findings hunt (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The highest hour of demand in the Mid-Atlantic (EIA's region) from 20 June 2025 to 28 June 2025, the days /events gives to the June 2025 eastern heat wave, was 160,560 MW, 22.3 percent above the mean of the same days' highest hours in the other 7 years held, 2019 to 2026 (131,264 MW).

![The june 2025 eastern heat wave, the Mid-Atlantic (EIA's region)](east-heat-2025-mida.png)

**The figure by year** (the window's highest hour of demand, MW): 2019: 136,567, 2020: 124,821, 2021: 141,879, 2022: 129,047, 2023: 116,740, 2024: 147,976, 2025: 160,560, 2026: 121,815.

**The tables and rows.** `eia930_ba_demand_hourly`; the authorities of the Mid-Atlantic (EIA's region) summed by hour, the hours from 06-20 to 06-28 of each year. The yearly values: `east-heat-2025-mida.csv`.

**Its strength.** The gap is 2.63 typical spreads of the other years. The extreme of the years held: 2025's figure is 160,560 MW; the highest other year's is 147,976 MW. Clear by a typical spread: the distance from the other years' mean is 29,296 MW against a typical spread of 11,149 MW. Sample large enough: 7 other years each hold at least 90 percent of the window's hours; 2025 holds 216 of 216. Holds against the median: the distance from the other years' median is 31,513 MW. Not one hour: the window's third-highest hour is 98.9 percent of its highest.

**Its limits.** EIA-930 demand as the authorities filed it, summed by region (an hour held only when every authority filing demand that month holds it); demand served during a load shed is load served, a floor on what was wanted; the same calendar days in UTC of the other years, not the weekday-aligned baseline of the /events pages.

**Reproduce.** `python east-heat-2025-mida.reproduce.py <eia930_ba_demand_hourly.csv>` and `do east-heat-2025-mida.reproduce.do` (Stata) recompute every year's figure; each names the expected values at its top, and the claim's mean of the other years.
