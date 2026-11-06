# What industry pays against citygate: Michigan

Draft `scan-deep-71847f516518` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The mean industrial gas price in Michigan against the state's citygate price was 4.56 USD per Mcf in 2025, against 0.95 USD per Mcf in 2001, the first full year the ERW holds.

![What industry pays against citygate, Michigan](industrial-vs-citygate-state-ind-mi.png)

**The figure by full year** (USD per Mcf): 2001: 0.95, 2002: 1.00, 2003: 0.55, 2004: 0.81, 2005: 0.61, 2006: 1.70, 2007: 1.53, 2008: 1.57, 2009: 2.16, 2010: 2.27, 2011: 2.22, 2012: 2.12, 2013: 2.40, 2014: 2.65, 2015: 2.55, 2016: 2.48, 2017: 2.76, 2018: 2.81, 2019: 3.35, 2020: 3.44, 2021: 3.29, 2022: 3.08, 2023: 4.61, 2024: 4.58, 2025: 4.56.

**The tables and rows.** `eia_gas_prices_state_monthly`; the rows for Michigan, region key `state_ind_MI` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `industrial-vs-citygate-state-ind-mi.csv`.

**Its strength.** The change is 15.24 typical yearly moves (a typical move is 0.24 USD per Mcf, 1.4826 times the median absolute change between full years). Holds in more than one year: 21 of the 24 full years after 2001 lie above 2001's value. Survives a change of window: from 2002 to 2025 the change is 3.56, from 2001 to 2024 it is 3.63. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 10. Half the change remains without the first year: from 2002 to 2025 the change is 3.56, 98.5 percent of the change from 2001. At least one typical yearly move: the change is 15.24 typical yearly moves (0.24 USD per Mcf a year, the median move between full years); the floor is 1.

**Its limits.** Nominal dollars per thousand cubic feet; many large industrial buyers buy gas directly and EIA's industrial price covers only the gas sold to them by utilities.

**Reproduce.** `python industrial-vs-citygate-state-ind-mi.reproduce.py <the table's CSV>` and `do industrial-vs-citygate-state-ind-mi.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
