# A state's share of us crude: Texas

Draft `scan-deep-deffa03e8721` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Texas's share of US crude oil production was 42.2 percent of US crude production in 2025, against 20.0 percent of US crude production in 2001, the first full year the ERW holds.

![A state's share of us crude, Texas](state-crude-share-crude-tx.png)

**The figure by full year** (percent of US crude production): 2001: 20.0, 2002: 19.4, 2003: 19.4, 2004: 19.7, 2005: 20.7, 2006: 21.1, 2007: 21.1, 2008: 22.2, 2009: 20.4, 2010: 21.3, 2011: 25.6, 2012: 30.4, 2013: 33.9, 2014: 36.2, 2015: 36.7, 2016: 36.1, 2017: 37.3, 2018: 40.3, 2019: 41.4, 2020: 42.7, 2021: 42.2, 2022: 42.7, 2023: 42.4, 2024: 42.8, 2025: 42.2.

**The tables and rows.** `eia_crude_production_state_monthly`; the rows for Texas, region key `crude_TX` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `state-crude-share-crude-tx.csv`.

**Its strength.** The change is 19.09 typical yearly moves (a typical move is 1.2 percent of US crude production, 1.4826 times the median absolute change between full years). Holds in more than one year: 21 of the 24 full years after 2001 lie above 2001's value. Survives a change of window: from 2002 to 2025 the change is 22.8, from 2001 to 2024 it is 22.7. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 11. Half the change remains without the first year: from 2002 to 2025 the change is 22.8, 103.1 percent of the change from 2001. At least one typical yearly move: the change is 19.09 typical yearly moves (1.2 percent of US crude production a year, the median move between full years); the floor is 1.

**Its limits.** EIA's field production by state, the latest months estimated; the federal offshore is in the US total and in no state.

**Reproduce.** `python state-crude-share-crude-tx.reproduce.py <the table's CSV>` and `do state-crude-share-crude-tx.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
