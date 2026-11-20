# The covid-19 spring of 2020: the Mid-Atlantic (EIA's region)

Draft `scan-deep-e34f89d79574` of the findings hunt (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The mean hour of demand in the Mid-Atlantic (EIA's region) from 1 March 2020 to 31 May 2020, the days /events gives to the COVID-19 spring of 2020, was 76,469 MW, 8.3 percent below the mean of the same days' mean hours in the other 7 years held, 2019 to 2026 (83,417 MW).

![The covid-19 spring of 2020, the Mid-Atlantic (EIA's region)](covid-2020-mida.png)

**The figure by year** (the window's mean hour of demand, MW): 2019: 83,192, 2020: 76,469, 2021: 80,450, 2022: 83,351, 2023: 81,895, 2024: 83,616, 2025: 83,935, 2026: 87,484.

**The tables and rows.** `eia930_ba_demand_hourly`; the authorities of the Mid-Atlantic (EIA's region) summed by hour, the hours from 03-01 to 05-31 of each year. The yearly values: `covid-2020-mida.csv`.

**Its strength.** The gap is 8.03 typical spreads of the other years. The extreme of the years held: 2020's figure is 76,469 MW; the lowest other year's is 80,450 MW. Clear by a typical spread: the distance from the other years' mean is 6,949 MW against a typical spread of 865 MW. Sample large enough: 7 other years each hold at least 90 percent of the window's hours; 2020 holds 2208 of 2208. Holds against the median: the distance from the other years' median is 6,882 MW. Not one hour: a mean over the window's hours.

**Its limits.** EIA-930 demand as the authorities filed it, summed by region (an hour held only when every authority filing demand that month holds it); demand served during a load shed is load served, a floor on what was wanted; the same calendar days in UTC of the other years, not the weekday-aligned baseline of the /events pages.

**Reproduce.** `python covid-2020-mida.reproduce.py <eia930_ba_demand_hourly.csv>` and `do covid-2020-mida.reproduce.do` (Stata) recompute every year's figure; each names the expected values at its top, and the claim's mean of the other years.
