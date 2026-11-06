# What industry pays against citygate: California

Draft `scan-deep-9305cfa9e8d7` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The mean industrial gas price in California against the state's citygate price was 7.85 USD per Mcf in 2024, against 0.47 USD per Mcf in 2001, the first full year the ERW holds.

![What industry pays against citygate, California](industrial-vs-citygate-state-ind-ca.png)

**The figure by full year** (USD per Mcf): 2001: 0.47, 2002: 1.74, 2003: 1.98, 2004: 1.85, 2005: 1.87, 2006: 2.54, 2007: 2.31, 2008: 2.82, 2009: 2.40, 2010: 2.21, 2011: 2.53, 2012: 2.30, 2013: 2.42, 2014: 2.79, 2015: 3.09, 2016: 3.80, 2017: 3.64, 2018: 3.86, 2019: 4.71, 2020: 4.54, 2021: 5.07, 2022: 5.73, 2023: 6.52, 2024: 7.85.

**The tables and rows.** `eia_gas_prices_state_monthly`; the rows for California, region key `state_ind_CA` (the card's `hunt.region`), years 2001 to 2024. The yearly values: `industrial-vs-citygate-state-ind-ca.csv`.

**Its strength.** The change is 15.64 typical yearly moves (a typical move is 0.47 USD per Mcf, 1.4826 times the median absolute change between full years). Holds in more than one year: 23 of the 23 full years after 2001 lie above 2001's value. Survives a change of window: from 2002 to 2024 the change is 6.12, from 2001 to 2023 it is 6.05. Sample large enough: 2001 holds 12 and 2024 holds 12 observations; the floor is 10. Half the change remains without the first year: from 2002 to 2024 the change is 6.12, 82.9 percent of the change from 2001. At least one typical yearly move: the change is 15.64 typical yearly moves (0.47 USD per Mcf a year, the median move between full years); the floor is 1.

**Its limits.** Nominal dollars per thousand cubic feet; many large industrial buyers buy gas directly and EIA's industrial price covers only the gas sold to them by utilities.

**Reproduce.** `python industrial-vs-citygate-state-ind-ca.reproduce.py <the table's CSV>` and `do industrial-vs-citygate-state-ind-ca.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
