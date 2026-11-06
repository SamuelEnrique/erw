# A state's share of us gas: West Virginia

Draft `scan-deep-0578ec6db1b6` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** West Virginia's share of US marketed gas production was 8.3 percent of US marketed production in 2025, against 0.9 percent of US marketed production in 2001, the first full year the ERW holds.

![A state's share of us gas, West Virginia](state-production-share-prod-wv.png)

**The figure by full year** (percent of US marketed production): 2001: 0.9, 2002: 0.9, 2003: 0.9, 2004: 1.0, 2005: 1.1, 2006: 1.2, 2007: 1.1, 2008: 1.2, 2009: 1.2, 2010: 1.2, 2011: 1.6, 2012: 2.1, 2013: 2.9, 2014: 3.9, 2015: 4.6, 2016: 4.9, 2017: 5.2, 2018: 5.4, 2019: 5.9, 2020: 7.0, 2021: 7.2, 2022: 7.2, 2023: 7.7, 2024: 8.3, 2025: 8.3.

**The tables and rows.** `eia_gas_production_state_monthly`; the rows for West Virginia, region key `prod_WV` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `state-production-share-prod-wv.csv`.

**Its strength.** The change is 30.15 typical yearly moves (a typical move is 0.2 percent of US marketed production, 1.4826 times the median absolute change between full years). Holds in more than one year: 24 of the 24 full years after 2001 lie above 2001's value. Survives a change of window: from 2002 to 2025 the change is 7.4, from 2001 to 2024 it is 7.4. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 11. Half the change remains without the first year: from 2002 to 2025 the change is 7.4, 99.8 percent of the change from 2001. At least one typical yearly move: the change is 30.15 typical yearly moves (0.2 percent of US marketed production a year, the median move between full years); the floor is 1.

**Its limits.** EIA's monthly figures as published, the latest months preliminary and EIA's estimates where a state does not report. The US total is EIA's own US row.

**Reproduce.** `python state-production-share-prod-wv.reproduce.py <the table's CSV>` and `do state-production-share-prod-wv.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
