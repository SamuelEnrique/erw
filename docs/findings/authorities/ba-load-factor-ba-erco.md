# An authority's load factor: ERCOT (ERCO, EIA-930 balancing authority)

Draft `scan-deep-44e0a89d8b9f` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The load factor of ERCOT (ERCO, EIA-930 balancing authority) (its mean hour of demand as a percent of its highest) was 66.6 percent in 2025, against 58.8 percent in 2019, the first full year the ERW holds.

![An authority's load factor, ERCOT (ERCO, EIA-930 balancing authority)](ba-load-factor-ba-erco.png)

**The figure by full year** (percent): 2019: 58.8, 2020: 58.5, 2021: 61.0, 2022: 61.6, 2023: 59.7, 2024: 61.7, 2025: 66.6.

**The tables and rows.** `eia930_ba_demand_hourly`; the rows for ERCOT (ERCO, EIA-930 balancing authority), region key `ba_erco` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `ba-load-factor-ba-erco.csv`.

**Its strength.** The change is 2.75 typical yearly moves (a typical move is 2.9 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 5 of the 6 full years after 2019 lie above 2019's value. Survives a change of window: from 2020 to 2025 the change is 8.2, from 2019 to 2024 it is 2.9. Sample large enough: 2019 holds 8,760 and 2025 holds 8,736 observations; the floor is 8,000. Half the change remains without the first year: from 2020 to 2025 the change is 8.2, 103.6 percent of the change from 2019. At least one typical yearly move: the change is 2.75 typical yearly moves (2.9 percent a year, the median move between full years); the floor is 1.

**Its limits.** EIA-930 as the authority filed it; an authority whose footprint changed (one that absorbed another) changes its figures with it; not adjusted for weather. A lone spike is dropped first.

**Reproduce.** `python ba-load-factor-ba-erco.reproduce.py <the table's CSV>` and `do ba-load-factor-ba-erco.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
