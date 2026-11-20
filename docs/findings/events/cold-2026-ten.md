# The late january 2026 cold: Tennessee (EIA's region)

Draft `scan-deep-20665fdde4b8` of the findings hunt (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The highest hour of demand in Tennessee (EIA's region) from 23 January 2026 to 2 February 2026, the days /events gives to the late January 2026 cold, was 32,685 MW, 21.8 percent above the mean of the same days' highest hours in the other 7 years held, 2019 to 2025 (26,837 MW).

![The late january 2026 cold, Tennessee (EIA's region)](cold-2026-ten.png)

**The figure by year** (the window's highest hour of demand, MW): 2019: 27,755, 2020: 22,704, 2021: 25,961, 2022: 27,809, 2023: 26,062, 2024: 25,899, 2025: 31,668, 2026: 32,685.

**The tables and rows.** `eia930_ba_demand_hourly`; the authorities of Tennessee (EIA's region) summed by hour, the hours from 01-23 to 02-02 of each year. The yearly values: `cold-2026-ten.csv`.

**Its strength.** The gap is 2.33 typical spreads of the other years. The extreme of the years held: 2026's figure is 32,685 MW; the highest other year's is 31,668 MW. Clear by a typical spread: the distance from the other years' mean is 5,848 MW against a typical spread of 2,510 MW. Sample large enough: 7 other years each hold at least 90 percent of the window's hours; 2026 holds 264 of 264. Holds against the median: the distance from the other years' median is 6,623 MW. Not one hour: the window's third-highest hour is 98.0 percent of its highest.

**Its limits.** EIA-930 demand as the authorities filed it, summed by region (an hour held only when every authority filing demand that month holds it); demand served during a load shed is load served, a floor on what was wanted; the same calendar days in UTC of the other years, not the weekday-aligned baseline of the /events pages.

**Reproduce.** `python cold-2026-ten.reproduce.py <eia930_ba_demand_hourly.csv>` and `do cold-2026-ten.reproduce.do` (Stata) recompute every year's figure; each names the expected values at its top, and the claim's mean of the other years.
