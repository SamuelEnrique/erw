# The largest ties between balancing authorities: the Los Angeles Department of Water and Power (LDWP) to the California ISO (CISO)

Draft `scan-deep-f5245faff4eb` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The mean hourly flow of power from the Los Angeles Department of Water and Power (LDWP) to the California ISO (CISO) was 444 MW in 2025, against 2,128 MW in 2019, the first full year the ERW holds.

![The largest ties between balancing authorities, the Los Angeles Department of Water and Power (LDWP) to the California ISO (CISO)](tie-flow-bt-ldwp-ciso.png)

**The figure by full year** (MW): 2019: 2,128, 2020: 2,081, 2021: 1,340, 2022: 955, 2023: 295, 2024: 216, 2025: 444.

**The tables and rows.** `eia930_ba_interchange_hourly_2018`, `eia930_ba_interchange_hourly_2019`, `eia930_ba_interchange_hourly_2020`, `eia930_ba_interchange_hourly_2021`, `eia930_ba_interchange_hourly_2022`, `eia930_ba_interchange_hourly_2023`, `eia930_ba_interchange_hourly_2024`, `eia930_ba_interchange_hourly_2025`, `eia930_ba_interchange_hourly_2026`; the rows for the Los Angeles Department of Water and Power (LDWP) to the California ISO (CISO), region key `bt_ldwp_ciso` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `tie-flow-bt-ldwp-ciso.csv`.

**Its strength.** The change is 3.71 typical yearly moves (a typical move is 454 MW, 1.4826 times the median absolute change between full years). Holds in more than one year: 6 of the 6 full years after 2019 lie below 2019's value. Survives a change of window: from 2020 to 2025 the change is -1,637, from 2019 to 2024 it is -1,912. Sample large enough: 2019 holds 8,760 and 2025 holds 8,712 observations; the floor is 8,000. Half the change remains without the first year: from 2020 to 2025 the change is -1,637, 97.2 percent of the change from 2019. At least one typical yearly move: the change is 3.71 typical yearly moves (454 MW a year, the median move between full years); the floor is 1.

**Its limits.** EIA-930 as one of the two authorities filed it; a tie is read when its mean flow is at least 300 MW, and its other side moved the same way. A negative mean is a year power flowed the other way on balance.

**Reproduce.** `python tie-flow-bt-ldwp-ciso.reproduce.py <the table's CSV>` and `do tie-flow-bt-ldwp-ciso.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
