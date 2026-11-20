# The actual year against the forecast of 3 years before: peak: MISO (MISO; FERC 714 planning area 203)

Draft `scan-deep-5c07f11c3be5` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** How far the actual peak hour of MISO (MISO; FERC 714 planning area 203) ran above (+) or below (-) its own forecast for that year, filed 3 years before, was -7.7 percent in 2025, against -12.2 percent in 2019, the first year this measure counts.

![The actual year against the forecast of 3 years before: peak, MISO (MISO; FERC 714 planning area 203)](peak-vs-3y-xp3-miso.png)

**The figure by full year** (percent): 2019: -12.2, 2020: -14.4, 2021: -13.1, 2022: -11.5, 2023: -6.8, 2024: -9.6, 2025: -7.7.

**The tables and rows.** `eia930_ba_demand_hourly`, `ferc714_planning_area_forecasts`; the rows for MISO (MISO; FERC 714 planning area 203), region key `xp3_miso` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `peak-vs-3y-xp3-miso.csv`.

**Its strength.** The change is 1.47 typical yearly moves (a typical move is 3.0 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 4 of the 6 full years after 2019 lie above 2019's value. Survives a change of window: from 2020 to 2025 the change is 6.7, from 2019 to 2024 it is 2.6. Sample large enough: 2019 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2020 to 2025 the change is 6.7, 150.3 percent of the change from 2019. At least one typical yearly move: the change is 1.47 typical yearly moves (3.0 percent a year, the median move between full years); the floor is 1.

**Its limits.** FERC 714's forecast as the area filed it and EIA-930's demand as its balancing authority reported it; the two are not defined alike (losses, footprint), so the level of the gap means less than its move; a lone spike is dropped from the actual peak.

**Reproduce.** `python peak-vs-3y-xp3-miso.reproduce.py <the table's CSV>` and `do peak-vs-3y-xp3-miso.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
