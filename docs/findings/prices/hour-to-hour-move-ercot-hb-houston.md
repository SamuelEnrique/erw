# The hour-to-hour move: ERCOT's Houston hub (HB_HOUSTON)

Draft `scan-deep-4af800b86a3a` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The median absolute hour-to-hour move of the real-time price at ERCOT's Houston hub (HB_HOUSTON) was 3.11 USD per MWh in 2025, against 1.05 USD per MWh in 2015, the first full year the ERW holds.

![The hour-to-hour move, ERCOT's Houston hub (HB_HOUSTON)](hour-to-hour-move-ercot-hb-houston.png)

**The figure by full year** (USD per MWh): 2015: 1.05, 2016: 1.08, 2017: 1.08, 2018: 1.29, 2019: 1.43, 2020: 1.19, 2021: 2.37, 2022: 4.25, 2023: 2.48, 2024: 2.37, 2025: 3.11.

**The tables and rows.** `ercot_all_hub_prices_history`; the rows for ERCOT's Houston hub (HB_HOUSTON), region key `ercot_HB_HOUSTON` (the card's `hunt.region`), years 2015 to 2025. The yearly values: `hour-to-hour-move-ercot-hb-houston.csv`.

**Its strength.** The change is 6.24 typical yearly moves (a typical move is 0.33 USD per MWh, 1.4826 times the median absolute change between full years). Holds in more than one year: 10 of the 10 full years after 2015 lie above 2015's value. Survives a change of window: from 2016 to 2025 the change is 2.03, from 2015 to 2024 it is 1.32. Sample large enough: 2015 holds 8,759 and 2025 holds 8,760 observations; the floor is 8,000. Half the change remains without the first year: from 2016 to 2025 the change is 2.03, 98.8 percent of the change from 2015. At least one typical yearly move: the change is 6.24 typical yearly moves (0.33 USD per MWh a year, the median move between full years); the floor is 1.

**Its limits.** A median of hourly moves in nominal dollars; it says how the typical hour moves, not how the rare spike does.

**Reproduce.** `python hour-to-hour-move-ercot-hb-houston.reproduce.py <the table's CSV>` and `do hour-to-hour-move-ercot-hb-houston.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
