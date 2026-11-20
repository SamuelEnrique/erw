# Coal piled at power plants: US power plants

Draft `scan-deep-f9d57631f536` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The coal held by US power plants at the end of December was 109.7 million short tons in 2025, against 161.6 million short tons in 2008, the first full year the ERW holds.

![Coal piled at power plants, US power plants](coal-stocks-dec-cst-us.png)

**The figure by full year** (million short tons): 2008: 161.6, 2009: 189.5, 2010: 174.9, 2011: 172.4, 2012: 185.1, 2013: 147.9, 2014: 151.5, 2015: 195.5, 2016: 162.0, 2017: 137.7, 2018: 102.8, 2019: 128.1, 2020: 131.4, 2021: 91.9, 2022: 88.9, 2023: 133.0, 2024: 127.8, 2025: 109.7.

**The tables and rows.** `eia_power_fuel_stocks_monthly`; the rows for US power plants, region key `cst_us` (the card's `hunt.region`), years 2008 to 2025. The yearly values: `coal-stocks-dec-cst-us.csv`.

**Its strength.** The change is 1.44 typical yearly moves (a typical move is 36.1 million short tons, 1.4826 times the median absolute change between full years). Holds in more than one year: 11 of the 17 full years after 2008 lie below 2008's value. Survives a change of window: from 2009 to 2025 the change is -79.7, from 2008 to 2024 it is -33.8. Sample large enough: 2008 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2009 to 2025 the change is -79.7, 153.8 percent of the change from 2008. At least one typical yearly move: the change is 1.44 typical yearly moves (36.1 million short tons a year, the median move between full years); the floor is 1.

**Its limits.** EIA's stocks at power plants of the electric power sector (code 98), coal excluding waste coal, at the end of December.

**Reproduce.** `python coal-stocks-dec-cst-us.reproduce.py <the table's CSV>` and `do coal-stocks-dec-cst-us.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
