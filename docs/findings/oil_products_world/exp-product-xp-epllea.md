# What the us exports: ethane

Draft `scan-deep-1622d4e19218` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** US exports of ethane was 577 thousand barrels a day in 2025, against 65 thousand barrels a day in 2015, the first full year the ERW holds.

![What the us exports, ethane](exp-product-xp-epllea.png)

**The figure by full year** (thousand barrels a day): 2015: 65, 2016: 95, 2017: 178, 2018: 256, 2019: 277, 2020: 271, 2021: 369, 2022: 419, 2023: 471, 2024: 487, 2025: 577.

**The tables and rows.** `eia_petroleum_exports_by_destination`; the rows for ethane, region key `xp_epllea` (the card's `hunt.region`), years 2015 to 2025. The yearly values: `exp-product-xp-epllea.csv`.

**Its strength.** The change is 6.79 typical yearly moves (a typical move is 75 thousand barrels a day, 1.4826 times the median absolute change between full years). Holds in more than one year: 10 of the 10 full years after 2015 lie above 2015's value. Survives a change of window: from 2016 to 2025 the change is 482, from 2015 to 2024 it is 422. Sample large enough: 2015 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2016 to 2025 the change is 482, 94.1 percent of the change from 2015. At least one typical yearly move: the change is 6.79 typical yearly moves (75 thousand barrels a day a year, the median move between full years); the floor is 1.

**Its limits.** EIA's exports by destination as published, the latest months preliminary; a destination is the first one shipped to, not always where the oil is used.

**Reproduce.** `python exp-product-xp-epllea.reproduce.py <the table's CSV>` and `do exp-product-xp-epllea.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
