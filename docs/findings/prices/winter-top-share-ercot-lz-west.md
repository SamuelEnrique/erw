# Winter's share of the dearest hours: ERCOT's West load zone (LZ_WEST)

Draft `scan-deep-6f0131013626` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The share of the year's dearest one percent of real-time hours at ERCOT's West load zone (LZ_WEST) that fell in December, January or February was 64.8 percent of the dearest hours in 2025, against 12.5 percent of the dearest hours in 2015, the first full year the ERW holds.

![Winter's share of the dearest hours, ERCOT's West load zone (LZ_WEST)](winter-top-share-ercot-lz-west.png)

**The figure by full year** (percent of the dearest hours): 2015: 12.5, 2016: 14.8, 2017: 35.2, 2018: 12.5, 2019: 0.0, 2020: 42.0, 2021: 100.0, 2022: 17.0, 2023: 1.1, 2024: 18.2, 2025: 64.8.

**The tables and rows.** `ercot_zone_prices_history`; the rows for ERCOT's West load zone (LZ_WEST), region key `ercot_LZ_WEST` (the card's `hunt.region`), years 2015 to 2025. The yearly values: `winter-top-share-ercot-lz-west.csv`.

**Its strength.** The change is 1.63 typical yearly moves (a typical move is 32.0 percent of the dearest hours, 1.4826 times the median absolute change between full years). Holds in more than one year: 7 of the 10 full years after 2015 lie above 2015's value. Survives a change of window: from 2016 to 2025 the change is 50.0, from 2015 to 2024 it is 5.7. Sample large enough: 2015 holds 8,760 and 2025 holds 8,760 observations; the floor is 8,000. Half the change remains without the first year: from 2016 to 2025 the change is 50.0, 95.7 percent of the change from 2015. At least one typical yearly move: the change is 1.63 typical yearly moves (32.0 percent of the dearest hours a year, the median move between full years); the floor is 1.

**Its limits.** About 88 hours a year: one cold spell can carry a year, and the year's December is not the same winter as its January.

**Reproduce.** `python winter-top-share-ercot-lz-west.reproduce.py <the table's CSV>` and `do winter-top-share-ercot-lz-west.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
