# Coal piled at power plants: the power plants of Ohio

Draft `scan-deep-525a21b9fc5c` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The coal held by the power plants of Ohio at the end of December was 4.0 million short tons in 2025, against 7.4 million short tons in 2008, the first full year the ERW holds.

![Coal piled at power plants, the power plants of Ohio](coal-stocks-dec-cst-oh.png)

**The figure by full year** (million short tons): 2008: 7.4, 2009: 9.6, 2010: 9.1, 2011: 7.3, 2012: 6.3, 2013: 4.5, 2014: 6.6, 2015: 8.6, 2016: 8.0, 2017: 5.2, 2018: 2.8, 2019: 6.6, 2020: 4.7, 2021: 3.5, 2022: 1.7, 2023: 4.1, 2024: 4.2, 2025: 4.0.

**The tables and rows.** `eia_power_fuel_stocks_monthly`; the rows for the power plants of Ohio, region key `cst_oh` (the card's `hunt.region`), years 2008 to 2025. The yearly values: `coal-stocks-dec-cst-oh.csv`.

**Its strength.** The change is 1.26 typical yearly moves (a typical move is 2.7 million short tons, 1.4826 times the median absolute change between full years). Holds in more than one year: 13 of the 17 full years after 2008 lie below 2008's value. Survives a change of window: from 2009 to 2025 the change is -5.6, from 2008 to 2024 it is -3.2. Sample large enough: 2008 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2009 to 2025 the change is -5.6, 165.2 percent of the change from 2008. At least one typical yearly move: the change is 1.26 typical yearly moves (2.7 million short tons a year, the median move between full years); the floor is 1.

**Its limits.** EIA's stocks at power plants of the electric power sector (code 98), coal excluding waste coal, at the end of December.

**Reproduce.** `python coal-stocks-dec-cst-oh.reproduce.py <the table's CSV>` and `do coal-stocks-dec-cst-oh.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
