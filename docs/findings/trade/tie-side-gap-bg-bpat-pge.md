# Where two authorities' reports on a tie disagree: the Bonneville Power Administration (BPAT) and Portland General Electric (PGE)

Draft `scan-deep-762769e65c49` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The mean absolute difference between the reports of the Bonneville Power Administration (BPAT) and Portland General Electric (PGE) on their tie was 521 MW in 2025, against 4 MW in 2019, the first full year the ERW holds.

![Where two authorities' reports on a tie disagree, the Bonneville Power Administration (BPAT) and Portland General Electric (PGE)](tie-side-gap-bg-bpat-pge.png)

**The figure by full year** (MW): 2019: 4, 2020: 4, 2021: 4, 2022: 31, 2023: 32, 2024: 34, 2025: 521.

**The tables and rows.** `eia930_ba_interchange_hourly_2018`, `eia930_ba_interchange_hourly_2019`, `eia930_ba_interchange_hourly_2020`, `eia930_ba_interchange_hourly_2021`, `eia930_ba_interchange_hourly_2022`, `eia930_ba_interchange_hourly_2023`, `eia930_ba_interchange_hourly_2024`, `eia930_ba_interchange_hourly_2025`, `eia930_ba_interchange_hourly_2026`; the rows for the Bonneville Power Administration (BPAT) and Portland General Electric (PGE), region key `bg_bpat_pge` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `tie-side-gap-bg-bpat-pge.csv`.

**Its strength.** The change is 187.38 typical yearly moves (a typical move is 3 MW, 1.4826 times the median absolute change between full years). Holds in more than one year: 6 of the 6 full years after 2019 lie above 2019's value. Survives a change of window: from 2020 to 2025 the change is 517, from 2019 to 2024 it is 31. Sample large enough: 2019 holds 8,711 and 2025 holds 8,760 observations; the floor is 8,000. Half the change remains without the first year: from 2020 to 2025 the change is 517, 99.9 percent of the change from 2019. At least one typical yearly move: the change is 187.38 typical yearly moves (3 MW a year, the median move between full years); the floor is 1.

**Its limits.** EIA-930 as each authority filed it, hours both hold, ties with a mean flow of at least 300 MW; which side is right is not known from these rows.

**Reproduce.** `python tie-side-gap-bg-bpat-pge.reproduce.py <the table's CSV>` and `do tie-side-gap-bg-bpat-pge.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
