# An authority's peak hour: Grant County PUD (GCPD, EIA-930 balancing authority)

Draft `scan-deep-c1984e18092f` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The highest hour of demand of Grant County PUD (GCPD, EIA-930 balancing authority) was 1,053 MW in 2025, against 846 MW in 2019, the first full year the ERW holds.

![An authority's peak hour, Grant County PUD (GCPD, EIA-930 balancing authority)](ba-peak-mw-ba-gcpd.png)

**The figure by full year** (MW): 2019: 846, 2020: 859, 2021: 947, 2022: 990, 2023: 978, 2024: 1,058, 2025: 1,053.

**The tables and rows.** `eia930_ba_demand_hourly`; the rows for Grant County PUD (GCPD, EIA-930 balancing authority), region key `ba_gcpd` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `ba-peak-mw-ba-gcpd.csv`.

**Its strength.** The change is 4.99 typical yearly moves (a typical move is 42 MW, 1.4826 times the median absolute change between full years). Holds in more than one year: 6 of the 6 full years after 2019 lie above 2019's value. Survives a change of window: from 2020 to 2025 the change is 194, from 2019 to 2024 it is 212. Sample large enough: 2019 holds 8,760 and 2025 holds 8,760 observations; the floor is 8,000. Half the change remains without the first year: from 2020 to 2025 the change is 194, 93.7 percent of the change from 2019. At least one typical yearly move: the change is 4.99 typical yearly moves (42 MW a year, the median move between full years); the floor is 1.

**Its limits.** EIA-930 as the authority filed it; an authority whose footprint changed (one that absorbed another) changes its figures with it; not adjusted for weather.

**Reproduce.** `python ba-peak-mw-ba-gcpd.reproduce.py <the table's CSV>` and `do ba-peak-mw-ba-gcpd.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
