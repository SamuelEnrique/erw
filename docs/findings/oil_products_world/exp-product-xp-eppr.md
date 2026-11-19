# What the us exports: residual fuel oil

Draft `scan-deep-188786c7a181` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** US exports of residual fuel oil was 113 thousand barrels a day in 2025, against 326 thousand barrels a day in 2015, the first full year the ERW holds.

![What the us exports, residual fuel oil](exp-product-xp-eppr.png)

**The figure by full year** (thousand barrels a day): 2015: 326, 2016: 298, 2017: 308, 2018: 321, 2019: 229, 2020: 148, 2021: 97, 2022: 110, 2023: 125, 2024: 137, 2025: 113.

**The tables and rows.** `eia_petroleum_exports_by_destination`; the rows for residual fuel oil, region key `xp_eppr` (the card's `hunt.region`), years 2015 to 2025. The yearly values: `exp-product-xp-eppr.csv`.

**Its strength.** The change is 7.36 typical yearly moves (a typical move is 29 thousand barrels a day, 1.4826 times the median absolute change between full years). Holds in more than one year: 10 of the 10 full years after 2015 lie below 2015's value. Survives a change of window: from 2016 to 2025 the change is -185, from 2015 to 2024 it is -190. Sample large enough: 2015 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2016 to 2025 the change is -185, 86.7 percent of the change from 2015. At least one typical yearly move: the change is 7.36 typical yearly moves (29 thousand barrels a day a year, the median move between full years); the floor is 1.

**Its limits.** EIA's exports by destination as published, the latest months preliminary; a destination is the first one shipped to, not always where the oil is used.

**Reproduce.** `python exp-product-xp-eppr.reproduce.py <the table's CSV>` and `do exp-product-xp-eppr.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
