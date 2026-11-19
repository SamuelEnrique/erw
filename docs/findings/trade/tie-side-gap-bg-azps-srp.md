# Where two authorities' reports on a tie disagree: Arizona Public Service (AZPS) and the Salt River Project (SRP)

Draft `scan-deep-6a037055fad9` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The mean absolute difference between the reports of Arizona Public Service (AZPS) and the Salt River Project (SRP) on their tie was 197 MW in 2025, against 3,004 MW in 2019, the first full year the ERW holds.

![Where two authorities' reports on a tie disagree, Arizona Public Service (AZPS) and the Salt River Project (SRP)](tie-side-gap-bg-azps-srp.png)

**The figure by full year** (MW): 2019: 3,004, 2020: 1,838, 2021: 119, 2022: 145, 2023: 112, 2024: 170, 2025: 197.

**The tables and rows.** `eia930_ba_interchange_hourly_2018`, `eia930_ba_interchange_hourly_2019`, `eia930_ba_interchange_hourly_2020`, `eia930_ba_interchange_hourly_2021`, `eia930_ba_interchange_hourly_2022`, `eia930_ba_interchange_hourly_2023`, `eia930_ba_interchange_hourly_2024`, `eia930_ba_interchange_hourly_2025`, `eia930_ba_interchange_hourly_2026`; the rows for Arizona Public Service (AZPS) and the Salt River Project (SRP), region key `bg_azps_srp` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `tie-side-gap-bg-azps-srp.csv`.

**Its strength.** The change is 41.47 typical yearly moves (a typical move is 68 MW, 1.4826 times the median absolute change between full years). Holds in more than one year: 6 of the 6 full years after 2019 lie below 2019's value. Survives a change of window: from 2020 to 2025 the change is -1,640, from 2019 to 2024 it is -2,833. Sample large enough: 2019 holds 8,640 and 2025 holds 8,760 observations; the floor is 8,000. Half the change remains without the first year: from 2020 to 2025 the change is -1,640, 58.5 percent of the change from 2019. At least one typical yearly move: the change is 41.47 typical yearly moves (68 MW a year, the median move between full years); the floor is 1.

**Its limits.** EIA-930 as each authority filed it, hours both hold, ties with a mean flow of at least 300 MW; which side is right is not known from these rows.

**Reproduce.** `python tie-side-gap-bg-azps-srp.reproduce.py <the table's CSV>` and `do tie-side-gap-bg-azps-srp.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
