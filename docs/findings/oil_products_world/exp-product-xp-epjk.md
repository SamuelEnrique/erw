# What the us exports: kerosene-type jet fuel

Draft `scan-deep-2cbabef143b0` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** US exports of kerosene-type jet fuel was 216 thousand barrels a day in 2025, against 168 thousand barrels a day in 2015, the first full year the ERW holds.

![What the us exports, kerosene-type jet fuel](exp-product-xp-epjk.png)

**The figure by full year** (thousand barrels a day): 2015: 168, 2016: 175, 2017: 184, 2018: 223, 2019: 220, 2020: 96, 2021: 107, 2022: 178, 2023: 173, 2024: 210, 2025: 216.

**The tables and rows.** `eia_petroleum_exports_by_destination`; the rows for kerosene-type jet fuel, region key `xp_epjk` (the card's `hunt.region`), years 2015 to 2025. The yearly values: `exp-product-xp-epjk.csv`.

**Its strength.** The change is 3.28 typical yearly moves (a typical move is 15 thousand barrels a day, 1.4826 times the median absolute change between full years). Holds in more than one year: 8 of the 10 full years after 2015 lie above 2015's value. Survives a change of window: from 2016 to 2025 the change is 41, from 2015 to 2024 it is 42. Sample large enough: 2015 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2016 to 2025 the change is 41, 84.8 percent of the change from 2015. At least one typical yearly move: the change is 3.28 typical yearly moves (15 thousand barrels a day a year, the median move between full years); the floor is 1.

**Its limits.** EIA's exports by destination as published, the latest months preliminary; a destination is the first one shipped to, not always where the oil is used.

**Reproduce.** `python exp-product-xp-epjk.reproduce.py <the table's CSV>` and `do exp-product-xp-epjk.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
