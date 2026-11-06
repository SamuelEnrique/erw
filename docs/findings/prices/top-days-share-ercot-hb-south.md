# The days that carry the spread: ERCOT's South hub (HB_SOUTH)

Draft `scan-deep-7dfd2bf8b8c6` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The share of the year's summed daily price spread at ERCOT's South hub (HB_SOUTH) that fell on its top tenth of days was 36.8 percent in 2025, against 57.5 percent in 2015, the first full year the ERW holds.

![The days that carry the spread, ERCOT's South hub (HB_SOUTH)](top-days-share-ercot-hb-south.png)

**The figure by full year** (percent): 2015: 57.5, 2016: 52.3, 2017: 47.2, 2018: 65.8, 2019: 76.8, 2020: 62.4, 2021: 73.2, 2022: 61.5, 2023: 73.7, 2024: 55.5, 2025: 36.8.

**The tables and rows.** `ercot_all_hub_prices_history`; the rows for ERCOT's South hub (HB_SOUTH), region key `ercot_HB_SOUTH` (the card's `hunt.region`), years 2015 to 2025. The yearly values: `top-days-share-ercot-hb-south.csv`.

**Its strength.** The change is 1.17 typical yearly moves (a typical move is 17.8 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 4 of the 10 full years after 2015 lie below 2015's value. Survives a change of window: from 2016 to 2025 the change is -15.5, from 2015 to 2024 it is -2.0. Sample large enough: 2015 holds 365 and 2025 holds 365 observations; the floor is 330. Half the change remains without the first year: from 2016 to 2025 the change is -15.5, 74.6 percent of the change from 2015. At least one typical yearly move: the change is 1.17 typical yearly moves (17.8 percent a year, the median move between full years); the floor is 1.

**Its limits.** A share of a sum of daily spreads in one hour each; it says how concentrated the spread is, not how much any asset earned.

**Reproduce.** `python top-days-share-ercot-hb-south.reproduce.py <the table's CSV>` and `do top-days-share-ercot-hb-south.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
