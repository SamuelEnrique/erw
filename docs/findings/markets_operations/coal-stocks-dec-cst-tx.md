# Coal piled at power plants: the power plants of Texas

Draft `scan-deep-c06cac21a85d` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The coal held by the power plants of Texas at the end of December was 10.5 million short tons in 2025, against 16.5 million short tons in 2008, the first full year the ERW holds.

![Coal piled at power plants, the power plants of Texas](coal-stocks-dec-cst-tx.png)

**The figure by full year** (million short tons): 2008: 16.5, 2009: 16.9, 2010: 17.0, 2011: 13.1, 2012: 16.5, 2013: 13.3, 2014: 13.1, 2015: 19.2, 2016: 13.8, 2017: 10.0, 2018: 6.0, 2019: 9.5, 2020: 9.6, 2021: 7.6, 2022: 7.9, 2023: 13.4, 2024: 12.4, 2025: 10.5.

**The tables and rows.** `eia_power_fuel_stocks_monthly`; the rows for the power plants of Texas, region key `cst_tx` (the card's `hunt.region`), years 2008 to 2025. The yearly values: `coal-stocks-dec-cst-tx.csv`.

**Its strength.** The change is 1.25 typical yearly moves (a typical move is 4.9 million short tons, 1.4826 times the median absolute change between full years). Holds in more than one year: 14 of the 17 full years after 2008 lie below 2008's value. Survives a change of window: from 2009 to 2025 the change is -6.4, from 2008 to 2024 it is -4.2. Sample large enough: 2008 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2009 to 2025 the change is -6.4, 105.8 percent of the change from 2008. At least one typical yearly move: the change is 1.25 typical yearly moves (4.9 million short tons a year, the median move between full years); the floor is 1.

**Its limits.** EIA's stocks at power plants of the electric power sector (code 98), coal excluding waste coal, at the end of December.

**Reproduce.** `python coal-stocks-dec-cst-tx.reproduce.py <the table's CSV>` and `do coal-stocks-dec-cst-tx.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
