# What a region generates: solar: the eight states of EIA's Northwest region (WA, OR, ID, MT, UT, WY, CO, NV)

Draft `scan-deep-be4dee164027` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Utility-scale solar's share of the net generation of the eight states of EIA's Northwest region (WA, OR, ID, MT, UT, WY, CO, NV) was 8.0 percent in 2025, against 0.0 percent in 2001, the first full year the ERW holds.

![What a region generates: solar, the eight states of EIA's Northwest region (WA, OR, ID, MT, UT, WY, CO, NV)](solar-share-st-nw-sun.png)

**The figure by full year** (percent): 2001: 0.0, 2002: 0.0, 2003: 0.0, 2004: 0.0, 2005: 0.0, 2006: 0.0, 2007: 0.0, 2008: 0.0, 2009: 0.1, 2010: 0.1, 2011: 0.1, 2012: 0.2, 2013: 0.3, 2014: 0.3, 2015: 0.5, 2016: 1.2, 2017: 2.0, 2018: 2.2, 2019: 2.5, 2020: 2.9, 2021: 3.5, 2022: 4.3, 2023: 5.4, 2024: 6.8, 2025: 8.0.

**The tables and rows.** `eia_state_generation_monthly`; the rows for the eight states of EIA's Northwest region (WA, OR, ID, MT, UT, WY, CO, NV), region key `st_nw_sun` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `solar-share-st-nw-sun.csv`.

**Its strength.** The change is 69.08 typical yearly moves (a typical move is 0.1 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 19 of the 24 full years after 2001 lie above 2001's value. Survives a change of window: from 2002 to 2025 the change is 8.0, from 2001 to 2024 it is 6.8. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2002 to 2025 the change is 8.0, 100.0 percent of the change from 2001. At least one typical yearly move: the change is 69.08 typical yearly moves (0.1 percent a year, the median move between full years); the floor is 1.

**Its limits.** EIA's state net generation by fuel, all sectors; the states stand for the region and are not its footprint; the latest months are preliminary. Small rooftop systems are not in this figure.

**Reproduce.** `python solar-share-st-nw-sun.reproduce.py <the table's CSV>` and `do solar-share-st-nw-sun.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
