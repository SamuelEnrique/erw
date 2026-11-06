# Day-ahead above real time: ERCOT's West load zone (LZ_WEST)

Draft `scan-deep-fd76c0c06802` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The share of hours in which the day-ahead price at ERCOT's West load zone (LZ_WEST) was above the real-time price was 59.3 percent of hours in 2025, against 66.2 percent of hours in 2015, the first full year the ERW holds.

![Day-ahead above real time, ERCOT's West load zone (LZ_WEST)](da-above-rt-share-ercot-lz-west.png)

**The figure by full year** (percent of hours): 2015: 66.2, 2016: 66.0, 2017: 65.8, 2018: 68.3, 2019: 67.7, 2020: 69.4, 2021: 67.1, 2022: 68.9, 2023: 67.8, 2024: 61.1, 2025: 59.3.

**The tables and rows.** `ercot_zone_prices_history`; the rows for ERCOT's West load zone (LZ_WEST), region key `ercot_LZ_WEST` (the card's `hunt.region`), years 2015 to 2025. The yearly values: `da-above-rt-share-ercot-lz-west.csv`.

**Its strength.** The change is 2.67 typical yearly moves (a typical move is 2.6 percent of hours, 1.4826 times the median absolute change between full years). Holds in more than one year: 4 of the 10 full years after 2015 lie below 2015's value. Survives a change of window: from 2016 to 2025 the change is -6.6, from 2015 to 2024 it is -5.1. Sample large enough: 2015 holds 8,760 and 2025 holds 8,760 observations; the floor is 8,000. Half the change remains without the first year: from 2016 to 2025 the change is -6.6, 97.0 percent of the change from 2015. At least one typical yearly move: the change is 2.67 typical yearly moves (2.6 percent of hours a year, the median move between full years); the floor is 1.

**Its limits.** A count of hours, not of dollars: it says how often the day-ahead price was the higher, not by how much.

**Reproduce.** `python da-above-rt-share-ercot-lz-west.reproduce.py <the table's CSV>` and `do da-above-rt-share-ercot-lz-west.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
