# The largest ties between balancing authorities: Ontario's IESO (IESO) to MISO (MISO)

Draft `scan-deep-8b7c6e0ddc91` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The mean hourly flow of power from Ontario's IESO (IESO) to MISO (MISO) was 390 MW in 2025, against 1,076 MW in 2019, the first full year the ERW holds.

![The largest ties between balancing authorities, Ontario's IESO (IESO) to MISO (MISO)](tie-flow-bt-ieso-miso.png)

**The figure by full year** (MW): 2019: 1,076, 2020: 1,120, 2021: 952, 2022: 979, 2023: 850, 2024: 590, 2025: 390.

**The tables and rows.** `eia930_ba_interchange_hourly_2018`, `eia930_ba_interchange_hourly_2019`, `eia930_ba_interchange_hourly_2020`, `eia930_ba_interchange_hourly_2021`, `eia930_ba_interchange_hourly_2022`, `eia930_ba_interchange_hourly_2023`, `eia930_ba_interchange_hourly_2024`, `eia930_ba_interchange_hourly_2025`, `eia930_ba_interchange_hourly_2026`; the rows for Ontario's IESO (IESO) to MISO (MISO), region key `bt_ieso_miso` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `tie-flow-bt-ieso-miso.csv`.

**Its strength.** The change is 3.12 typical yearly moves (a typical move is 220 MW, 1.4826 times the median absolute change between full years). Holds in more than one year: 5 of the 6 full years after 2019 lie below 2019's value. Survives a change of window: from 2020 to 2025 the change is -731, from 2019 to 2024 it is -485. Sample large enough: 2019 holds 8,759 and 2025 holds 8,760 observations; the floor is 8,000. Half the change remains without the first year: from 2020 to 2025 the change is -731, 106.5 percent of the change from 2019. At least one typical yearly move: the change is 3.12 typical yearly moves (220 MW a year, the median move between full years); the floor is 1.

**Its limits.** EIA-930 as one of the two authorities filed it; a tie is read when its mean flow is at least 300 MW, and its other side moved the same way. A negative mean is a year power flowed the other way on balance.

**Reproduce.** `python tie-flow-bt-ieso-miso.reproduce.py <the table's CSV>` and `do tie-flow-bt-ieso-miso.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
