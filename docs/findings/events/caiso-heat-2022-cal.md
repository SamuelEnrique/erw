# The september 2022 west heat wave: California (EIA's region)

Draft `scan-deep-2518036a5eca` of the findings hunt (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The highest hour of demand in California (EIA's region) from 31 August 2022 to 9 September 2022, the days /events gives to the September 2022 West heat wave, was 63,622 MW, 15.8 percent above the mean of the same days' highest hours in the other 8 years held, 2018 to 2026 (54,954 MW).

![The september 2022 west heat wave, California (EIA's region)](caiso-heat-2022-cal.png)

**The figure by year** (the window's highest hour of demand, MW): 2018: 48,414, 2019: 54,679, 2020: 58,097, 2021: 54,543, 2022: 63,622, 2023: 51,435, 2024: 58,612, 2025: 52,635, 2026: 61,214.

**The tables and rows.** `eia930_ba_demand_hourly`; the authorities of California (EIA's region) summed by hour, the hours from 08-31 to 09-09 of each year. The yearly values: `caiso-heat-2022-cal.csv`.

**Its strength.** The gap is 1.76 typical spreads of the other years. The extreme of the years held: 2022's figure is 63,622 MW; the highest other year's is 61,214 MW. Clear by a typical spread: the distance from the other years' mean is 8,668 MW against a typical spread of 4,939 MW. Sample large enough: 8 other years each hold at least 90 percent of the window's hours; 2022 holds 240 of 240. Holds against the median: the distance from the other years' median is 9,011 MW. Not one hour: the window's third-highest hour is 97.4 percent of its highest.

**Its limits.** EIA-930 demand as the authorities filed it, summed by region (an hour held only when every authority filing demand that month holds it); demand served during a load shed is load served, a floor on what was wanted; the same calendar days in UTC of the other years, not the weekday-aligned baseline of the /events pages.

**Reproduce.** `python caiso-heat-2022-cal.reproduce.py <eia930_ba_demand_hourly.csv>` and `do caiso-heat-2022-cal.reproduce.do` (Stata) recompute every year's figure; each names the expected values at its top, and the claim's mean of the other years.
