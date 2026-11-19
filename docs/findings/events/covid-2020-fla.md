# The covid-19 spring of 2020: Florida (EIA's region)

Draft `scan-deep-1b1fda59a791` of the findings hunt (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The mean hour of demand in Florida (EIA's region) from 1 March 2020 to 31 May 2020, the days /events gives to the COVID-19 spring of 2020, was 26,518 MW, 6.9 percent below the mean of the same days' mean hours in the other 6 years held, 2021 to 2026 (28,480 MW).

![The covid-19 spring of 2020, Florida (EIA's region)](covid-2020-fla.png)

**The figure by year** (the window's mean hour of demand, MW): 2020: 26,518, 2021: 26,752, 2022: 27,505, 2023: 28,875, 2024: 28,975, 2025: 29,290, 2026: 29,484.

**The tables and rows.** `eia930_ba_demand_hourly`; the authorities of Florida (EIA's region) summed by hour, the hours from 03-01 to 05-31 of each year. The yearly values: `covid-2020-fla.csv`.

**Its strength.** The gap is 2.86 typical spreads of the other years. The extreme of the years held: 2020's figure is 26,518 MW; the lowest other year's is 26,752 MW. Clear by a typical spread: the distance from the other years' mean is 1,962 MW against a typical spread of 685 MW. Sample large enough: 6 other years each hold at least 90 percent of the window's hours; 2020 holds 2058 of 2208. Holds against the median: the distance from the other years' median is 2,407 MW. Not one hour: a mean over the window's hours.

**Its limits.** EIA-930 demand as the authorities filed it, summed by region (an hour held only when every authority filing demand that month holds it); demand served during a load shed is load served, a floor on what was wanted; the same calendar days in UTC of the other years, not the weekday-aligned baseline of the /events pages.

**Reproduce.** `python covid-2020-fla.reproduce.py <eia930_ba_demand_hourly.csv>` and `do covid-2020-fla.reproduce.do` (Stata) recompute every year's figure; each names the expected values at its top, and the claim's mean of the other years.
