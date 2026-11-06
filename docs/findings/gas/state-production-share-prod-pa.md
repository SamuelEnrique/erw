# A state's share of us gas: Pennsylvania

Draft `scan-deep-0d768034cd5f` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Pennsylvania's share of US marketed gas production was 17.8 percent of US marketed production in 2025, against 0.6 percent of US marketed production in 2001, the first full year the ERW holds.

![A state's share of us gas, Pennsylvania](state-production-share-prod-pa.png)

**The figure by full year** (percent of US marketed production): 2001: 0.6, 2002: 0.8, 2003: 0.8, 2004: 1.0, 2005: 0.9, 2006: 0.9, 2007: 0.9, 2008: 0.9, 2009: 1.3, 2010: 2.6, 2011: 5.5, 2012: 8.9, 2013: 12.7, 2014: 15.5, 2015: 16.7, 2016: 18.3, 2017: 18.7, 2018: 19.0, 2019: 18.9, 2020: 19.6, 2021: 20.5, 2022: 19.1, 2023: 18.4, 2024: 17.9, 2025: 17.8.

**The tables and rows.** `eia_gas_production_state_monthly`; the rows for Pennsylvania, region key `prod_PA` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `state-production-share-prod-pa.csv`.

**Its strength.** The change is 27.97 typical yearly moves (a typical move is 0.6 percent of US marketed production, 1.4826 times the median absolute change between full years). Holds in more than one year: 24 of the 24 full years after 2001 lie above 2001's value. Survives a change of window: from 2002 to 2025 the change is 17.0, from 2001 to 2024 it is 17.3. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 11. Half the change remains without the first year: from 2002 to 2025 the change is 17.0, 99.1 percent of the change from 2001. At least one typical yearly move: the change is 27.97 typical yearly moves (0.6 percent of US marketed production a year, the median move between full years); the floor is 1.

**Its limits.** EIA's monthly figures as published, the latest months preliminary and EIA's estimates where a state does not report. The US total is EIA's own US row.

**Reproduce.** `python state-production-share-prod-pa.reproduce.py <the table's CSV>` and `do state-production-share-prod-pa.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
