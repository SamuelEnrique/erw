# The actual year against the forecast of 3 years before: peak: ISO New England (ISNE; FERC 714 planning area 76)

Draft `scan-deep-8fd014fab959` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** How far the actual peak hour of ISO New England (ISNE; FERC 714 planning area 76) ran above (+) or below (-) its own forecast for that year, filed 3 years before, was -3.8 percent in 2025, against -17.2 percent in 2019, the first year this measure counts.

![The actual year against the forecast of 3 years before: peak, ISO New England (ISNE; FERC 714 planning area 76)](peak-vs-3y-xp3-isne.png)

**The figure by full year** (percent): 2019: -17.2, 2020: -14.0, 2021: -11.9, 2022: -16.0, 2023: -15.4, 2024: -10.2, 2025: -3.8.

**The tables and rows.** `eia930_ba_demand_hourly`, `ferc714_planning_area_forecasts`; the rows for ISO New England (ISNE; FERC 714 planning area 76), region key `xp3_isne` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `peak-vs-3y-xp3-isne.csv`.

**Its strength.** The change is 2.49 typical yearly moves (a typical move is 5.4 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 6 of the 6 full years after 2019 lie above 2019's value. Survives a change of window: from 2020 to 2025 the change is 10.2, from 2019 to 2024 it is 7.0. Sample large enough: 2019 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2020 to 2025 the change is 10.2, 75.8 percent of the change from 2019. At least one typical yearly move: the change is 2.49 typical yearly moves (5.4 percent a year, the median move between full years); the floor is 1.

**Its limits.** FERC 714's forecast as the area filed it and EIA-930's demand as its balancing authority reported it; the two are not defined alike (losses, footprint), so the level of the gap means less than its move; a lone spike is dropped from the actual peak.

**Reproduce.** `python peak-vs-3y-xp3-isne.reproduce.py <the table's CSV>` and `do peak-vs-3y-xp3-isne.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
