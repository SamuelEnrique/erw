# What an authority generates against what it uses: Grant County PUD (GCPD, EIA-930 balancing authority)

Draft `scan-deep-50b5c3098344` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The net generation of Grant County PUD (GCPD, EIA-930 balancing authority) as a percent of its demand was 128.6 percent in 2025, against 155.7 percent in 2019, the first full year the ERW holds.

![What an authority generates against what it uses, Grant County PUD (GCPD, EIA-930 balancing authority)](ba-gen-ratio-ba-gcpd.png)

**The figure by full year** (percent): 2019: 155.7, 2020: 188.1, 2021: 167.7, 2022: 167.7, 2023: 127.9, 2024: 119.0, 2025: 128.6.

**The tables and rows.** `eia930_ba_supply_hourly`, `eia930_ba_demand_hourly`; the rows for Grant County PUD (GCPD, EIA-930 balancing authority), region key `ba_gcpd` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `ba-gen-ratio-ba-gcpd.csv`.

**Its strength.** The change is 1.22 typical yearly moves (a typical move is 22.2 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 3 of the 6 full years after 2019 lie below 2019's value. Survives a change of window: from 2020 to 2025 the change is -59.5, from 2019 to 2024 it is -36.7. Sample large enough: 2019 holds 8,760 and 2025 holds 8,760 observations; the floor is 8,000. Half the change remains without the first year: from 2020 to 2025 the change is -59.5, 219.8 percent of the change from 2019. At least one typical yearly move: the change is 1.22 typical yearly moves (22.2 percent a year, the median move between full years); the floor is 1.

**Its limits.** EIA-930 as the authority filed it; an authority whose footprint changed (one that absorbed another) changes its figures with it; not adjusted for weather. Hours both are held.

**Reproduce.** `python ba-gen-ratio-ba-gcpd.reproduce.py <the table's CSV>` and `do ba-gen-ratio-ba-gcpd.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
