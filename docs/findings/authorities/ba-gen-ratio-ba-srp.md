# What an authority generates against what it uses: the Salt River Project (SRP, EIA-930 balancing authority)

Draft `scan-deep-90f9e6ba2296` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The net generation of the Salt River Project (SRP, EIA-930 balancing authority) as a percent of its demand was 164.8 percent in 2025, against 210.6 percent in 2019, the first full year the ERW holds.

![What an authority generates against what it uses, the Salt River Project (SRP, EIA-930 balancing authority)](ba-gen-ratio-ba-srp.png)

**The figure by full year** (percent): 2019: 210.6, 2020: 209.9, 2021: 180.2, 2022: 170.8, 2023: 175.4, 2024: 167.9, 2025: 164.8.

**The tables and rows.** `eia930_ba_supply_hourly`, `eia930_ba_demand_hourly`; the rows for the Salt River Project (SRP, EIA-930 balancing authority), region key `ba_srp` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `ba-gen-ratio-ba-srp.csv`.

**Its strength.** The change is 5.13 typical yearly moves (a typical move is 8.9 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 6 of the 6 full years after 2019 lie below 2019's value. Survives a change of window: from 2020 to 2025 the change is -45.1, from 2019 to 2024 it is -42.7. Sample large enough: 2019 holds 8,760 and 2025 holds 8,760 observations; the floor is 8,000. Half the change remains without the first year: from 2020 to 2025 the change is -45.1, 98.5 percent of the change from 2019. At least one typical yearly move: the change is 5.13 typical yearly moves (8.9 percent a year, the median move between full years); the floor is 1.

**Its limits.** EIA-930 as the authority filed it; an authority whose footprint changed (one that absorbed another) changes its figures with it; not adjusted for weather. Hours both are held.

**Reproduce.** `python ba-gen-ratio-ba-srp.reproduce.py <the table's CSV>` and `do ba-gen-ratio-ba-srp.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
