# The january 2025 cold: Texas (EIA's region)

Draft `scan-deep-990976f24787` of the findings hunt (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The highest hour of demand in Texas (EIA's region) from 17 January 2025 to 26 January 2025, the days /events gives to the January 2025 cold, was 77,426 MW, 27.9 percent above the mean of the same days' highest hours in the other 7 years held, 2019 to 2026 (60,546 MW).

![The january 2025 cold, Texas (EIA's region)](cold-2025-tex.png)

**The figure by year** (the window's highest hour of demand, MW): 2019: 54,656, 2020: 48,548, 2021: 46,528, 2022: 63,504, 2023: 57,620, 2024: 77,370, 2025: 77,426, 2026: 75,599.

**The tables and rows.** `eia930_ba_demand_hourly`; the authorities of Texas (EIA's region) summed by hour, the hours from 01-17 to 01-26 of each year. The yearly values: `cold-2025-tex.csv`.

**Its strength.** The gap is 1.25 typical spreads of the other years. The extreme of the years held: 2025's figure is 77,426 MW; the highest other year's is 77,370 MW. Clear by a typical spread: the distance from the other years' mean is 16,880 MW against a typical spread of 13,450 MW. Sample large enough: 7 other years each hold at least 90 percent of the window's hours; 2025 holds 240 of 240. Holds against the median: the distance from the other years' median is 19,806 MW. Not one hour: the window's third-highest hour is 97.4 percent of its highest.

**Its limits.** EIA-930 demand as the authorities filed it, summed by region (an hour held only when every authority filing demand that month holds it); demand served during a load shed is load served, a floor on what was wanted; the same calendar days in UTC of the other years, not the weekday-aligned baseline of the /events pages.

**Reproduce.** `python cold-2025-tex.reproduce.py <eia930_ba_demand_hourly.csv>` and `do cold-2025-tex.reproduce.do` (Stata) recompute every year's figure; each names the expected values at its top, and the claim's mean of the other years.
