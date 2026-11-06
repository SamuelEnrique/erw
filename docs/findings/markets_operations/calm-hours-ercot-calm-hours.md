# Calm hours: ERCOT

Draft `scan-deep-6b52a987779b` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The number of calm hours (wind and solar far below usual) in ERCOT was 592 hours in 2025, against 396 hours in 2019, the first year the ERW's table holds.

![Calm hours, ERCOT](calm-hours-ercot-calm-hours.png)

**The figure by full year** (hours): 2019: 396, 2020: 281, 2021: 296, 2022: 392, 2023: 425, 2024: 597, 2025: 592.

**The tables and rows.** `grid_stress_yearly`; the rows for ERCOT, region key `ercot_calm_hours` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `calm-hours-ercot-calm-hours.csv`.

**Its strength.** The change is 2.05 typical yearly moves (a typical move is 96 hours, 1.4826 times the median absolute change between full years). Holds in more than one year: 3 of the 6 full years after 2019 lie above 2019's value. Survives a change of window: from 2020 to 2025 the change is 311, from 2019 to 2024 it is 201. Sample large enough: 2019 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2020 to 2025 the change is 311, 158.7 percent of the change from 2019. At least one typical yearly move: the change is 2.05 typical yearly moves (96 hours a year, the median move between full years); the floor is 1.

**Its limits.** The ERW's derived grid_stress_yearly (EIA-930 hourly by source, EIA's generator inventory); the tightest hours are the year's hours of highest net load, and a grid whose capacity grew late in a year shows a share of a capacity it held only in part. Weather moves the count from year to year.

**Reproduce.** `python calm-hours-ercot-calm-hours.reproduce.py <the table's CSV>` and `do calm-hours-ercot-calm-hours.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
