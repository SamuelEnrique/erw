# Gas vented and flared: Wyoming

Draft `scan-deep-cb0428da3115` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The share of Wyoming's gross gas withdrawals vented or flared was 4.46 percent of gross withdrawals in 2024, against 0.46 percent of gross withdrawals in 2001, the first full year the ERW holds.

![Gas vented and flared, Wyoming](flared-share-flare-wy.png)

**The figure by full year** (percent of gross withdrawals): 2001: 0.46, 2002: 0.71, 2003: 0.91, 2004: 0.87, 2005: 1.56, 2006: 1.50, 2007: 2.12, 2008: 1.70, 2009: 1.68, 2010: 1.67, 2011: 2.43, 2012: 2.04, 2013: 1.69, 2014: 1.36, 2015: 0.17, 2016: 0.63, 2017: 1.07, 2018: 0.52, 2019: 0.56, 2020: 4.10, 2021: 4.78, 2022: 4.52, 2023: 4.27, 2024: 4.46.

**The tables and rows.** `eia_gas_production_state_monthly`; the rows for Wyoming, region key `flare_WY` (the card's `hunt.region`), years 2001 to 2024. The yearly values: `flared-share-flare-wy.csv`.

**Its strength.** The change is 7.71 typical yearly moves (a typical move is 0.52 percent of gross withdrawals, 1.4826 times the median absolute change between full years). Holds in more than one year: 22 of the 23 full years after 2001 lie above 2001's value. Survives a change of window: from 2002 to 2024 the change is 3.76, from 2001 to 2023 it is 3.82. Sample large enough: 2001 holds 12 and 2024 holds 12 observations; the floor is 11. Half the change remains without the first year: from 2002 to 2024 the change is 3.76, 93.7 percent of the change from 2001. At least one typical yearly move: the change is 7.71 typical yearly moves (0.52 percent of gross withdrawals a year, the median move between full years); the floor is 1.

**Its limits.** EIA's monthly figures as published, the latest months preliminary and EIA's estimates where a state does not report. Venting and flaring are reported or estimated by the states, and EIA's series ends in 2024; states with less than 100 Bcf of gross withdrawals in their last whole year are not hunted.

**Reproduce.** `python flared-share-flare-wy.reproduce.py <the table's CSV>` and `do flared-share-flare-wy.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
