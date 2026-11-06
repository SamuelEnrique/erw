# Days with a wide spread: ERCOT's West load zone (LZ_WEST)

Draft `scan-deep-7f9685056a5a` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The share of days at ERCOT's West load zone (LZ_WEST) whose highest hourly real-time price was at least USD 50 per MWh above its lowest was 84.1 percent of days in 2025, against 28.8 percent of days in 2015, the first full year the ERW holds.

![Days with a wide spread, ERCOT's West load zone (LZ_WEST)](wide-spread-days-ercot-lz-west.png)

**The figure by full year** (percent of days): 2015: 28.8, 2016: 23.2, 2017: 30.7, 2018: 54.0, 2019: 61.1, 2020: 46.7, 2021: 52.1, 2022: 79.7, 2023: 77.3, 2024: 73.2, 2025: 84.1.

**The tables and rows.** `ercot_zone_prices_history`; the rows for ERCOT's West load zone (LZ_WEST), region key `ercot_LZ_WEST` (the card's `hunt.region`), years 2015 to 2025. The yearly values: `wide-spread-days-ercot-lz-west.csv`.

**Its strength.** The change is 5.12 typical yearly moves (a typical move is 10.8 percent of days, 1.4826 times the median absolute change between full years). Holds in more than one year: 9 of the 10 full years after 2015 lie above 2015's value. Survives a change of window: from 2016 to 2025 the change is 60.9, from 2015 to 2024 it is 44.5. Sample large enough: 2015 holds 365 and 2025 holds 365 observations; the floor is 330. Half the change remains without the first year: from 2016 to 2025 the change is 60.9, 110.0 percent of the change from 2015. At least one typical yearly move: the change is 5.12 typical yearly moves (10.8 percent of days a year, the median move between full years); the floor is 1.

**Its limits.** A nominal line, not adjusted for inflation: the same real spread crosses it more easily in a later year.

**Reproduce.** `python wide-spread-days-ercot-lz-west.reproduce.py <the table's CSV>` and `do wide-spread-days-ercot-lz-west.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
