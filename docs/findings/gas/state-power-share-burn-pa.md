# A state's gas for power: Pennsylvania

Draft `scan-deep-776d5abbc30d` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The share of Pennsylvania's delivered gas that went to power plants was 61.6 percent of delivered gas in 2025, against 3.8 percent of delivered gas in 2001, the first full year the ERW holds.

![A state's gas for power, Pennsylvania](state-power-share-burn-pa.png)

**The figure by full year** (percent of delivered gas): 2001: 3.8, 2002: 8.0, 2003: 6.3, 2004: 11.5, 2005: 12.3, 2006: 16.1, 2007: 20.2, 2008: 20.0, 2009: 27.9, 2010: 30.3, 2011: 35.3, 2012: 42.9, 2013: 37.8, 2014: 37.3, 2015: 42.2, 2016: 46.8, 2017: 47.4, 2018: 45.3, 2019: 51.0, 2020: 58.6, 2021: 57.8, 2022: 57.4, 2023: 61.3, 2024: 62.2, 2025: 61.6.

**The tables and rows.** `eia_gas_consumption_state_monthly`; the rows for Pennsylvania, region key `burn_PA` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `state-power-share-burn-pa.csv`.

**Its strength.** The change is 10.01 typical yearly moves (a typical move is 5.8 percent of delivered gas, 1.4826 times the median absolute change between full years). Holds in more than one year: 24 of the 24 full years after 2001 lie above 2001's value. Survives a change of window: from 2002 to 2025 the change is 53.7, from 2001 to 2024 it is 58.4. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 11. Half the change remains without the first year: from 2002 to 2025 the change is 53.7, 92.8 percent of the change from 2001. At least one typical yearly move: the change is 10.01 typical yearly moves (5.8 percent of delivered gas a year, the median move between full years); the floor is 1.

**Its limits.** EIA's monthly figures as published, the latest months preliminary and EIA's estimates where a state does not report. Deliveries to the four sectors, not counting the gas pipelines and fields use themselves.

**Reproduce.** `python state-power-share-burn-pa.reproduce.py <the table's CSV>` and `do state-power-share-burn-pa.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
