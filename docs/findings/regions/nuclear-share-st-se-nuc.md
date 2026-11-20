# What a region generates: nuclear: Georgia and Alabama (the core of EIA's Southeast region)

Draft `scan-deep-5b6813a8c822` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Nuclear's share of the net generation of Georgia and Alabama (the core of EIA's Southeast region) was 32.5 percent in 2025, against 26.3 percent in 2001, the first full year the ERW holds.

![What a region generates: nuclear, Georgia and Alabama (the core of EIA's Southeast region)](nuclear-share-st-se-nuc.png)

**The figure by full year** (percent): 2001: 26.3, 2002: 24.3, 2003: 24.8, 2004: 24.8, 2005: 23.0, 2006: 22.9, 2007: 23.1, 2008: 25.1, 2009: 26.3, 2010: 24.7, 2011: 25.5, 2012: 27.2, 2013: 27.1, 2014: 26.8, 2015: 26.9, 2016: 27.0, 2017: 28.6, 2018: 26.9, 2019: 28.5, 2020: 29.6, 2021: 30.0, 2022: 28.2, 2023: 30.9, 2024: 32.7, 2025: 32.5.

**The tables and rows.** `eia_state_generation_monthly`; the rows for Georgia and Alabama (the core of EIA's Southeast region), region key `st_se_nuc` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `nuclear-share-st-se-nuc.csv`.

**Its strength.** The change is 3.56 typical yearly moves (a typical move is 1.8 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 14 of the 24 full years after 2001 lie above 2001's value. Survives a change of window: from 2002 to 2025 the change is 8.3, from 2001 to 2024 it is 6.4. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2002 to 2025 the change is 8.3, 132.2 percent of the change from 2001. At least one typical yearly move: the change is 3.56 typical yearly moves (1.8 percent a year, the median move between full years); the floor is 1.

**Its limits.** EIA's state net generation by fuel, all sectors; the states stand for the region and are not its footprint; the latest months are preliminary.

**Reproduce.** `python nuclear-share-st-se-nuc.reproduce.py <the table's CSV>` and `do nuclear-share-st-se-nuc.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
