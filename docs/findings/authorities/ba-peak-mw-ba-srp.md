# An authority's peak hour: the Salt River Project (SRP, EIA-930 balancing authority)

Draft `scan-deep-5cb264a55ad0` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The highest hour of demand of the Salt River Project (SRP, EIA-930 balancing authority) was 8,784 MW in 2025, against 7,347 MW in 2019, the first full year the ERW holds.

![An authority's peak hour, the Salt River Project (SRP, EIA-930 balancing authority)](ba-peak-mw-ba-srp.png)

**The figure by full year** (MW): 2019: 7,347, 2020: 7,714, 2021: 7,669, 2022: 7,629, 2023: 8,332, 2024: 8,356, 2025: 8,784.

**The tables and rows.** `eia930_ba_demand_hourly`; the rows for the Salt River Project (SRP, EIA-930 balancing authority), region key `ba_srp` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `ba-peak-mw-ba-srp.csv`.

**Its strength.** The change is 4.71 typical yearly moves (a typical move is 305 MW, 1.4826 times the median absolute change between full years). Holds in more than one year: 6 of the 6 full years after 2019 lie above 2019's value. Survives a change of window: from 2020 to 2025 the change is 1,070, from 2019 to 2024 it is 1,009. Sample large enough: 2019 holds 8,758 and 2025 holds 8,760 observations; the floor is 8,000. Half the change remains without the first year: from 2020 to 2025 the change is 1,070, 74.5 percent of the change from 2019. At least one typical yearly move: the change is 4.71 typical yearly moves (305 MW a year, the median move between full years); the floor is 1.

**Its limits.** EIA-930 as the authority filed it; an authority whose footprint changed (one that absorbed another) changes its figures with it; not adjusted for weather.

**Reproduce.** `python ba-peak-mw-ba-srp.reproduce.py <the table's CSV>` and `do ba-peak-mw-ba-srp.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
