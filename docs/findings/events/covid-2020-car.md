# The covid-19 spring of 2020: the Carolinas (EIA's region)

Draft `scan-deep-7a08a1e87143` of the findings hunt (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The mean hour of demand in the Carolinas (EIA's region) from 1 March 2020 to 31 May 2020, the days /events gives to the COVID-19 spring of 2020, was 20,644 MW, 9.4 percent below the mean of the same days' mean hours in the other 7 years held, 2019 to 2026 (22,773 MW).

![The covid-19 spring of 2020, the Carolinas (EIA's region)](covid-2020-car.png)

**The figure by year** (the window's mean hour of demand, MW): 2019: 23,021, 2020: 20,644, 2021: 22,220, 2022: 22,820, 2023: 22,293, 2024: 22,889, 2025: 22,901, 2026: 23,270.

**The tables and rows.** `eia930_ba_demand_hourly`; the authorities of the Carolinas (EIA's region) summed by hour, the hours from 03-01 to 05-31 of each year. The yearly values: `covid-2020-car.csv`.

**Its strength.** The gap is 10.89 typical spreads of the other years. The extreme of the years held: 2020's figure is 20,644 MW; the lowest other year's is 22,220 MW. Clear by a typical spread: the distance from the other years' mean is 2,130 MW against a typical spread of 196 MW. Sample large enough: 7 other years each hold at least 90 percent of the window's hours; 2020 holds 2208 of 2208. Holds against the median: the distance from the other years' median is 2,245 MW. Not one hour: a mean over the window's hours.

**Its limits.** EIA-930 demand as the authorities filed it, summed by region (an hour held only when every authority filing demand that month holds it); demand served during a load shed is load served, a floor on what was wanted; the same calendar days in UTC of the other years, not the weekday-aligned baseline of the /events pages.

**Reproduce.** `python covid-2020-car.reproduce.py <eia930_ba_demand_hourly.csv>` and `do covid-2020-car.reproduce.do` (Stata) recompute every year's figure; each names the expected values at its top, and the claim's mean of the other years.
