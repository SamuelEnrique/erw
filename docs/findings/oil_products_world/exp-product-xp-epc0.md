# What the us exports: crude oil

Draft `scan-deep-ea98c36eb6c9` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** US exports of crude oil was 3,961 thousand barrels a day in 2025, against 465 thousand barrels a day in 2015, the first full year the ERW holds.

![What the us exports, crude oil](exp-product-xp-epc0.png)

**The figure by full year** (thousand barrels a day): 2015: 465, 2016: 591, 2017: 1,158, 2018: 2,048, 2019: 2,982, 2020: 3,206, 2021: 2,963, 2022: 3,576, 2023: 4,082, 2024: 4,093, 2025: 3,961.

**The tables and rows.** `eia_petroleum_exports_by_destination`; the rows for crude oil, region key `xp_epc0` (the card's `hunt.region`), years 2015 to 2025. The yearly values: `exp-product-xp-epc0.csv`.

**Its strength.** The change is 6.30 typical yearly moves (a typical move is 555 thousand barrels a day, 1.4826 times the median absolute change between full years). Holds in more than one year: 10 of the 10 full years after 2015 lie above 2015's value. Survives a change of window: from 2016 to 2025 the change is 3,370, from 2015 to 2024 it is 3,628. Sample large enough: 2015 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2016 to 2025 the change is 3,370, 96.4 percent of the change from 2015. At least one typical yearly move: the change is 6.30 typical yearly moves (555 thousand barrels a day a year, the median move between full years); the floor is 1.

**Its limits.** EIA's exports by destination as published, the latest months preliminary; a destination is the first one shipped to, not always where the oil is used.

**Reproduce.** `python exp-product-xp-epc0.reproduce.py <the table's CSV>` and `do exp-product-xp-epc0.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
