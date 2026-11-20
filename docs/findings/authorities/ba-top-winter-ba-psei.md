# When an authority's peak hours fall: Puget Sound Energy (PSEI, EIA-930 balancing authority)

Draft `scan-deep-a67c82d1bd27` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The share of the 100 highest hours of demand of Puget Sound Energy (PSEI, EIA-930 balancing authority) that fell in January, February or December was 100.0 percent of the top hours in 2025, against 90.0 percent of the top hours in 2019, the first full year the ERW holds.

![When an authority's peak hours fall, Puget Sound Energy (PSEI, EIA-930 balancing authority)](ba-top-winter-ba-psei.png)

**The figure by full year** (percent of the top hours): 2019: 90.0, 2021: 94.0, 2022: 97.0, 2023: 66.0, 2024: 100.0, 2025: 100.0.

**The tables and rows.** `eia930_ba_demand_hourly`; the rows for Puget Sound Energy (PSEI, EIA-930 balancing authority), region key `ba_psei` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `ba-top-winter-ba-psei.csv`.

**Its strength.** The change is 1.69 typical yearly moves (a typical move is 5.9 percent of the top hours, 1.4826 times the median absolute change between full years). Holds in more than one year: 4 of the 5 full years after 2019 lie above 2019's value. Survives a change of window: from 2021 to 2025 the change is 6.0, from 2019 to 2024 it is 10.0. Sample large enough: 2019 holds 8,376 and 2025 holds 8,760 observations; the floor is 8,000. Half the change remains without the first year: from 2021 to 2025 the change is 6.0, 60.0 percent of the change from 2019. At least one typical yearly move: the change is 1.69 typical yearly moves (5.9 percent of the top hours a year, the median move between full years); the floor is 1.

**Its limits.** EIA-930 as the authority filed it; an authority whose footprint changed (one that absorbed another) changes its figures with it; not adjusted for weather. Months are UTC months; a lone spike is dropped first.

**Reproduce.** `python ba-top-winter-ba-psei.reproduce.py <the table's CSV>` and `do ba-top-winter-ba-psei.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
