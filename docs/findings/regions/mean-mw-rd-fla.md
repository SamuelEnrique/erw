# The year's mean hour: Florida (EIA's region)

Draft `scan-deep-8d8de085a3e7` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The mean hour of demand in Florida (EIA's region) was 30,560 MW in 2025, against 27,821 MW in 2021, the first full year the ERW holds.

![The year's mean hour, Florida (EIA's region)](mean-mw-rd-fla.png)

**The figure by full year** (MW): 2021: 27,821, 2022: 29,187, 2023: 29,992, 2024: 30,260, 2025: 30,560.

**The tables and rows.** `eia930_ba_demand_hourly`; the rows for Florida (EIA's region), region key `rd_fla` (the card's `hunt.region`), years 2021 to 2025. The yearly values: `mean-mw-rd-fla.csv`.

**Its strength.** The change is 3.34 typical yearly moves (a typical move is 820 MW, 1.4826 times the median absolute change between full years). Holds in more than one year: 4 of the 4 full years after 2021 lie above 2021's value. Survives a change of window: from 2022 to 2025 the change is 1,374, from 2021 to 2024 it is 2,439. Sample large enough: 2021 holds 8,595 and 2025 holds 8,739 observations; the floor is 8,000. Half the change remains without the first year: from 2022 to 2025 the change is 1,374, 50.2 percent of the change from 2021. At least one typical yearly move: the change is 3.34 typical yearly moves (820 MW a year, the median move between full years); the floor is 1.

**Its limits.** EIA-930 as the balancing authorities report it; a region's demand is the sum of its authorities that file demand, an hour held only when all of them do; not adjusted for weather.

**Reproduce.** `python mean-mw-rd-fla.reproduce.py <the table's CSV>` and `do mean-mw-rd-fla.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
