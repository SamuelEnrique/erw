# The late january 2026 cold: the Southeast (EIA's region)

Draft `scan-deep-a4d189b0e77a` of the findings hunt (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The highest hour of demand in the Southeast (EIA's region) from 23 January 2026 to 2 February 2026, the days /events gives to the late January 2026 cold, was 47,809 MW, 23.2 percent above the mean of the same days' highest hours in the other 7 years held, 2019 to 2025 (38,801 MW).

![The late january 2026 cold, the Southeast (EIA's region)](cold-2026-se.png)

**The figure by year** (the window's highest hour of demand, MW): 2019: 41,445, 2020: 34,085, 2021: 37,652, 2022: 39,967, 2023: 37,184, 2024: 36,347, 2025: 44,925, 2026: 47,809.

**The tables and rows.** `eia930_ba_demand_hourly`; the authorities of the Southeast (EIA's region) summed by hour, the hours from 01-23 to 02-02 of each year. The yearly values: `cold-2026-se.csv`.

**Its strength.** The gap is 2.62 typical spreads of the other years. The extreme of the years held: 2026's figure is 47,809 MW; the highest other year's is 44,925 MW. Clear by a typical spread: the distance from the other years' mean is 9,008 MW against a typical spread of 3,432 MW. Sample large enough: 7 other years each hold at least 90 percent of the window's hours; 2026 holds 264 of 264. Holds against the median: the distance from the other years' median is 10,157 MW. Not one hour: the window's third-highest hour is 96.9 percent of its highest.

**Its limits.** EIA-930 demand as the authorities filed it, summed by region (an hour held only when every authority filing demand that month holds it); demand served during a load shed is load served, a floor on what was wanted; the same calendar days in UTC of the other years, not the weekday-aligned baseline of the /events pages.

**Reproduce.** `python cold-2026-se.reproduce.py <eia930_ba_demand_hourly.csv>` and `do cold-2026-se.reproduce.do` (Stata) recompute every year's figure; each names the expected values at its top, and the claim's mean of the other years.
