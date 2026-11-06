# Transport's share of us co2: the United States

Draft `scan-deep-2b91680ae020` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Transport's share of US energy-related CO2 was 37.3 percent of US energy CO2 in 2022, against 32.3 percent of US energy CO2 in 2001, the first year this measure counts.

![Transport's share of us co2, the United States](transport-co2-share-us-transport-co2-share.png)

**The figure by full year** (percent of US energy CO2): 2001: 32.3, 2002: 32.8, 2003: 32.7, 2004: 33.0, 2005: 33.3, 2006: 34.2, 2007: 33.8, 2008: 32.6, 2009: 33.9, 2010: 33.0, 2011: 33.3, 2012: 34.0, 2013: 33.5, 2014: 33.5, 2015: 35.0, 2016: 36.2, 2017: 36.8, 2018: 36.4, 2019: 37.4, 2020: 35.7, 2021: 36.9, 2022: 37.3.

**The tables and rows.** `eia_co2_state_annual`; the rows for the United States, region key `us_transport_co2_share` (the card's `hunt.region`), years 2001 to 2022. The yearly values: `transport-co2-share-us-transport-co2-share.csv`.

**Its strength.** The change is 5.61 typical yearly moves (a typical move is 0.9 percent of US energy CO2, 1.4826 times the median absolute change between full years). Holds in more than one year: 21 of the 21 full years after 2001 lie above 2001's value. Survives a change of window: from 2002 to 2022 the change is 4.5, from 2001 to 2021 it is 4.6. Sample large enough: 2001 holds 1 and 2022 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2002 to 2022 the change is 4.5, 90.3 percent of the change from 2001. At least one typical yearly move: the change is 5.61 typical yearly moves (0.9 percent of US energy CO2 a year, the median move between full years); the floor is 1.

**Its limits.** EIA's energy-related CO2 by state, which ends in 2022 in the ERW's table; it counts fuel burned, not the electricity a state imports.

**Reproduce.** `python transport-co2-share-us-transport-co2-share.reproduce.py <the table's CSV>` and `do transport-co2-share-us-transport-co2-share.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
