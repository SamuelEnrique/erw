# An authority's load factor: NorthWestern Energy (Montana) (NWMT, EIA-930 balancing authority)

Draft `scan-deep-0575d94ee4a2` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The load factor of NorthWestern Energy (Montana) (NWMT, EIA-930 balancing authority) (its mean hour of demand as a percent of its highest) was 67.2 percent in 2025, against 73.4 percent in 2019, the first full year the ERW holds.

![An authority's load factor, NorthWestern Energy (Montana) (NWMT, EIA-930 balancing authority)](ba-load-factor-ba-nwmt.png)

**The figure by full year** (percent): 2019: 73.4, 2020: 72.3, 2021: 49.0, 2022: 68.6, 2023: 68.4, 2024: 65.8, 2025: 67.2.

**The tables and rows.** `eia930_ba_demand_hourly`; the rows for NorthWestern Energy (Montana) (NWMT, EIA-930 balancing authority), region key `ba_nwmt` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `ba-load-factor-ba-nwmt.csv`.

**Its strength.** The change is 2.08 typical yearly moves (a typical move is 3.0 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 6 of the 6 full years after 2019 lie below 2019's value. Survives a change of window: from 2020 to 2025 the change is -5.1, from 2019 to 2024 it is -7.6. Sample large enough: 2019 holds 8,685 and 2025 holds 8,754 observations; the floor is 8,000. Half the change remains without the first year: from 2020 to 2025 the change is -5.1, 83.0 percent of the change from 2019. At least one typical yearly move: the change is 2.08 typical yearly moves (3.0 percent a year, the median move between full years); the floor is 1.

**Its limits.** EIA-930 as the authority filed it; an authority whose footprint changed (one that absorbed another) changes its figures with it; not adjusted for weather. A lone spike is dropped first.

**Reproduce.** `python ba-load-factor-ba-nwmt.reproduce.py <the table's CSV>` and `do ba-load-factor-ba-nwmt.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
