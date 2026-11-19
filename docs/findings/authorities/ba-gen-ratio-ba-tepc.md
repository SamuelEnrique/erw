# What an authority generates against what it uses: Tucson Electric Power (TEPC, EIA-930 balancing authority)

Draft `scan-deep-314ff537b8ce` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The net generation of Tucson Electric Power (TEPC, EIA-930 balancing authority) as a percent of its demand was 92.9 percent in 2025, against 73.0 percent in 2019, the first full year the ERW holds.

![What an authority generates against what it uses, Tucson Electric Power (TEPC, EIA-930 balancing authority)](ba-gen-ratio-ba-tepc.png)

**The figure by full year** (percent): 2019: 73.0, 2020: 68.6, 2021: 73.7, 2022: 71.0, 2023: 80.0, 2024: 102.1, 2025: 92.9.

**The tables and rows.** `eia930_ba_supply_hourly`, `eia930_ba_demand_hourly`; the rows for Tucson Electric Power (TEPC, EIA-930 balancing authority), region key `ba_tepc` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `ba-gen-ratio-ba-tepc.csv`.

**Its strength.** The change is 1.90 typical yearly moves (a typical move is 10.5 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 4 of the 6 full years after 2019 lie above 2019's value. Survives a change of window: from 2020 to 2025 the change is 24.3, from 2019 to 2024 it is 29.1. Sample large enough: 2019 holds 8,712 and 2025 holds 8,760 observations; the floor is 8,000. Half the change remains without the first year: from 2020 to 2025 the change is 24.3, 122.1 percent of the change from 2019. At least one typical yearly move: the change is 1.90 typical yearly moves (10.5 percent a year, the median move between full years); the floor is 1.

**Its limits.** EIA-930 as the authority filed it; an authority whose footprint changed (one that absorbed another) changes its figures with it; not adjusted for weather. Hours both are held.

**Reproduce.** `python ba-gen-ratio-ba-tepc.reproduce.py <the table's CSV>` and `do ba-gen-ratio-ba-tepc.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
