# The actual year against the forecast of 5 years before: peak: PJM (PJM; FERC 714 planning area 119)

Draft `scan-deep-0ecaaaeeddf1` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** How far the actual peak hour of PJM (PJM; FERC 714 planning area 119) ran above (+) or below (-) its own forecast for that year, filed 5 years before, was 5.7 percent in 2025, against -8.7 percent in 2019, the first year this measure counts.

![The actual year against the forecast of 5 years before: peak, PJM (PJM; FERC 714 planning area 119)](peak-vs-5y-xp5-pjm.png)

**The figure by full year** (percent): 2019: -8.7, 2020: -7.3, 2021: -2.5, 2022: -2.9, 2023: -3.4, 2024: 0.4, 2025: 5.7.

**The tables and rows.** `eia930_ba_demand_hourly`, `ferc714_planning_area_forecasts`; the rows for PJM (PJM; FERC 714 planning area 119), region key `xp5_pjm` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `peak-vs-5y-xp5-pjm.csv`.

**Its strength.** The change is 3.66 typical yearly moves (a typical move is 3.9 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 6 of the 6 full years after 2019 lie above 2019's value. Survives a change of window: from 2020 to 2025 the change is 13.0, from 2019 to 2024 it is 9.2. Sample large enough: 2019 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2020 to 2025 the change is 13.0, 90.1 percent of the change from 2019. At least one typical yearly move: the change is 3.66 typical yearly moves (3.9 percent a year, the median move between full years); the floor is 1.

**Its limits.** FERC 714's forecast as the area filed it and EIA-930's demand as its balancing authority reported it; the two are not defined alike (losses, footprint), so the level of the gap means less than its move; a lone spike is dropped from the actual peak.

**Reproduce.** `python peak-vs-5y-xp5-pjm.reproduce.py <the table's CSV>` and `do peak-vs-5y-xp5-pjm.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
