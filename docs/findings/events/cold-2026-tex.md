# The late january 2026 cold: Texas (EIA's region)

Draft `scan-deep-2fcfc5e72653` of the findings hunt (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The highest hour of demand in Texas (EIA's region) from 23 January 2026 to 2 February 2026, the days /events gives to the late January 2026 cold, was 75,599 MW, 32.9 percent above the mean of the same days' highest hours in the other 7 years held, 2019 to 2025 (56,873 MW).

![The late january 2026 cold, Texas (EIA's region)](cold-2026-tex.png)

**The figure by year** (the window's highest hour of demand, MW): 2019: 54,656, 2020: 47,074, 2021: 51,607, 2022: 53,813, 2023: 65,552, 2024: 54,806, 2025: 70,603, 2026: 75,599.

**The tables and rows.** `eia930_ba_demand_hourly`; the authorities of Texas (EIA's region) summed by hour, the hours from 01-23 to 02-02 of each year. The yearly values: `cold-2026-tex.csv`.

**Its strength.** The gap is 4.14 typical spreads of the other years. The extreme of the years held: 2026's figure is 75,599 MW; the highest other year's is 70,603 MW. Clear by a typical spread: the distance from the other years' mean is 18,726 MW against a typical spread of 4,520 MW. Sample large enough: 7 other years each hold at least 90 percent of the window's hours; 2026 holds 264 of 264. Holds against the median: the distance from the other years' median is 20,943 MW. Not one hour: the window's third-highest hour is 98.4 percent of its highest.

**Its limits.** EIA-930 demand as the authorities filed it, summed by region (an hour held only when every authority filing demand that month holds it); demand served during a load shed is load served, a floor on what was wanted; the same calendar days in UTC of the other years, not the weekday-aligned baseline of the /events pages.

**Reproduce.** `python cold-2026-tex.reproduce.py <eia930_ba_demand_hourly.csv>` and `do cold-2026-tex.reproduce.do` (Stata) recompute every year's figure; each names the expected values at its top, and the claim's mean of the other years.
