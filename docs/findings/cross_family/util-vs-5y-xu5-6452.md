# A utility's sales against its forecast of 5 years before: Florida Power & Light Company (EIA utility 6452, FERC 714 planning area 63; FL)

Draft `scan-deep-1880d7ad2ddf` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** How far the retail sales of Florida Power & Light Company (EIA utility 6452, FERC 714 planning area 63; FL) ran above (+) or below (-) the net energy its own filing of 5 years before forecast for that year, was 2.4 percent in 2025, against -11.9 percent in 2019, the first year this measure counts.

![A utility's sales against its forecast of 5 years before, Florida Power & Light Company (EIA utility 6452, FERC 714 planning area 63; FL)](util-vs-5y-xu5-6452.png)

**The figure by full year** (percent): 2019: -11.9, 2020: -6.7, 2021: -7.9, 2022: 5.1, 2023: 3.9, 2025: 2.4.

**The tables and rows.** `eia861m_utility_sales_monthly`, `ferc714_planning_area_forecasts`; the rows for Florida Power & Light Company (EIA utility 6452, FERC 714 planning area 63; FL), region key `xu5_6452` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `util-vs-5y-xu5-6452.csv`.

**Its strength.** The change is 6.15 typical yearly moves (a typical move is 2.3 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 5 of the 5 full years after 2019 lie above 2019's value. Survives a change of window: from 2020 to 2025 the change is 9.1, from 2019 to 2023 it is 15.8. Sample large enough: 2019 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2020 to 2025 the change is 9.1, 63.9 percent of the change from 2019. At least one typical yearly move: the change is 6.15 typical yearly moves (2.3 percent a year, the median move between full years); the floor is 1.

**Its limits.** EIA-861M's retail sales of the utility (every state it serves) against the net energy for load its FERC 714 filing forecast; net energy also holds losses and any wholesale load the area serves, so the level of the gap means less than its move; a year under half or over twice its forecast is left out.

**Reproduce.** `python util-vs-5y-xu5-6452.reproduce.py <the table's CSV>` and `do util-vs-5y-xu5-6452.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
