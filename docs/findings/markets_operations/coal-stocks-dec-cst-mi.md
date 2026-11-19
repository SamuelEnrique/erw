# Coal piled at power plants: the power plants of Michigan

Draft `scan-deep-23e2258c353e` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The coal held by the power plants of Michigan at the end of December was 2.6 million short tons in 2025, against 7.7 million short tons in 2008, the first full year the ERW holds.

![Coal piled at power plants, the power plants of Michigan](coal-stocks-dec-cst-mi.png)

**The figure by full year** (million short tons): 2008: 7.7, 2009: 5.6, 2010: 6.9, 2011: 6.5, 2012: 6.7, 2013: 6.0, 2014: 7.0, 2015: 7.7, 2016: 6.0, 2017: 6.1, 2018: 4.4, 2019: 5.0, 2020: 4.9, 2021: 2.4, 2022: 3.1, 2023: 3.7, 2024: 3.3, 2025: 2.6.

**The tables and rows.** `eia_power_fuel_stocks_monthly`; the rows for the power plants of Michigan, region key `cst_mi` (the card's `hunt.region`), years 2008 to 2025. The yearly values: `coal-stocks-dec-cst-mi.csv`.

**Its strength.** The change is 4.68 typical yearly moves (a typical move is 1.1 million short tons, 1.4826 times the median absolute change between full years). Holds in more than one year: 16 of the 17 full years after 2008 lie below 2008's value. Survives a change of window: from 2009 to 2025 the change is -3.1, from 2008 to 2024 it is -4.4. Sample large enough: 2008 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2009 to 2025 the change is -3.1, 59.8 percent of the change from 2008. At least one typical yearly move: the change is 4.68 typical yearly moves (1.1 million short tons a year, the median move between full years); the floor is 1.

**Its limits.** EIA's stocks at power plants of the electric power sector (code 98), coal excluding waste coal, at the end of December.

**Reproduce.** `python coal-stocks-dec-cst-mi.reproduce.py <the table's CSV>` and `do coal-stocks-dec-cst-mi.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
