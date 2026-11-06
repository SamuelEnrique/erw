# What homes pay above citygate: Vermont

Draft `scan-deep-434f65fce867` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The mean residential gas price in Vermont above its citygate price was 16.98 USD per Mcf in 2025, against 6.54 USD per Mcf in 2001, the first full year the ERW holds.

![What homes pay above citygate, Vermont](residential-markup-state-res-vt.png)

**The figure by full year** (USD per Mcf): 2001: 6.54, 2002: 6.40, 2003: 5.90, 2004: 6.59, 2005: 6.60, 2006: 6.82, 2007: 7.85, 2008: 9.77, 2009: 9.54, 2010: 9.84, 2011: 10.18, 2012: 12.37, 2013: 11.95, 2014: 10.28, 2015: 10.62, 2016: 11.54, 2017: 11.57, 2018: 11.78, 2019: 11.86, 2020: 12.40, 2021: 12.62, 2022: 12.26, 2023: 14.82, 2024: 16.32, 2025: 16.98.

**The tables and rows.** `eia_gas_prices_state_monthly`; the rows for Vermont, region key `state_res_VT` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `residential-markup-state-res-vt.csv`.

**Its strength.** The change is 18.28 typical yearly moves (a typical move is 0.57 USD per Mcf, 1.4826 times the median absolute change between full years). Holds in more than one year: 22 of the 24 full years after 2001 lie above 2001's value. Survives a change of window: from 2002 to 2025 the change is 10.58, from 2001 to 2024 it is 9.77. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 10. Half the change remains without the first year: from 2002 to 2025 the change is 10.58, 101.3 percent of the change from 2001. At least one typical yearly move: the change is 18.28 typical yearly moves (0.57 USD per Mcf a year, the median move between full years); the floor is 1.

**Its limits.** Nominal dollars per thousand cubic feet; a mean of months, not weighted by the gas each month delivered, and EIA withholds some months for some states.

**Reproduce.** `python residential-markup-state-res-vt.reproduce.py <the table's CSV>` and `do residential-markup-state-res-vt.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
