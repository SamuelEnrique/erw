# Calm hours: PJM

Draft `scan-deep-b03457614699` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The number of calm hours (wind and solar far below usual) in PJM was 1,976 hours in 2025, against 1,492 hours in 2019, the first year the ERW's table holds.

![Calm hours, PJM](calm-hours-pjm-calm-hours.png)

**The figure by full year** (hours): 2019: 1,492, 2020: 1,548, 2021: 1,537, 2022: 1,340, 2023: 1,565, 2024: 1,799, 2025: 1,976.

**The tables and rows.** `grid_stress_yearly`; the rows for PJM, region key `pjm_calm_hours` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `calm-hours-pjm-calm-hours.csv`.

**Its strength.** The change is 1.75 typical yearly moves (a typical move is 277 hours, 1.4826 times the median absolute change between full years). Holds in more than one year: 5 of the 6 full years after 2019 lie above 2019's value. Survives a change of window: from 2020 to 2025 the change is 428, from 2019 to 2024 it is 307. Sample large enough: 2019 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2020 to 2025 the change is 428, 88.4 percent of the change from 2019. At least one typical yearly move: the change is 1.75 typical yearly moves (277 hours a year, the median move between full years); the floor is 1.

**Its limits.** The ERW's derived grid_stress_yearly (EIA-930 hourly by source, EIA's generator inventory); the tightest hours are the year's hours of highest net load, and a grid whose capacity grew late in a year shows a share of a capacity it held only in part. Weather moves the count from year to year.

**Reproduce.** `python calm-hours-pjm-calm-hours.reproduce.py <the table's CSV>` and `do calm-hours-pjm-calm-hours.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
