# What a utility sells: Oklahoma Gas & Electric Co in OK

Draft `scan-deep-9c377fff3c22` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The retail electricity sales of Oklahoma Gas & Electric Co in OK was 30.92 TWh in 2025, against 23.73 TWh in 2017, the first full year the ERW holds.

![What a utility sells, Oklahoma Gas & Electric Co in OK](util-total-u861-14063-ok.png)

**The figure by full year** (TWh): 2017: 23.73, 2018: 25.40, 2019: 25.80, 2020: 24.59, 2021: 25.10, 2022: 27.30, 2023: 27.22, 2024: 29.38, 2025: 30.92.

**The tables and rows.** `eia861m_utility_sales_monthly`; the rows for Oklahoma Gas & Electric Co in OK, region key `u861_14063_ok` (the card's `hunt.region`), years 2017 to 2025. The yearly values: `util-total-u861-14063-ok.csv`.

**Its strength.** The change is 3.53 typical yearly moves (a typical move is 2.04 TWh, 1.4826 times the median absolute change between full years). Holds in more than one year: 8 of the 8 full years after 2017 lie above 2017's value. Survives a change of window: from 2018 to 2025 the change is 5.53, from 2017 to 2024 it is 5.65. Sample large enough: 2017 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2018 to 2025 the change is 5.53, 76.8 percent of the change from 2017. At least one typical yearly move: the change is 3.53 typical yearly moves (2.04 TWh a year, the median move between full years); the floor is 1.

**Its limits.** EIA Form 861M as the utility filed it, in one state, its sales to the customers it serves; states with retail or community choice are not read; a utility that merged or changed its EIA number starts again under its new number; the latest year's months may be preliminary.

**Reproduce.** `python util-total-u861-14063-ok.reproduce.py <the table's CSV>` and `do util-total-u861-14063-ok.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
