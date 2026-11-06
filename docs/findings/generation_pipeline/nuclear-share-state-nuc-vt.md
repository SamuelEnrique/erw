# Nuclear's share: Vermont

Draft `scan-deep-dc86397ca7c4` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Nuclear's share of net generation in Vermont was 0.0 percent of net generation in 2025, against 76.1 percent of net generation in 2001, the first full year the ERW holds.

![Nuclear's share, Vermont](nuclear-share-state-nuc-vt.png)

**The figure by full year** (percent of net generation): 2001: 76.1, 2002: 72.6, 2003: 73.7, 2004: 70.5, 2005: 71.2, 2006: 72.1, 2007: 80.8, 2008: 71.8, 2009: 73.6, 2010: 72.2, 2011: 72.4, 2012: 75.5, 2013: 70.4, 2014: 72.0, 2015: 0.0, 2016: 0.0, 2017: 0.0, 2018: 0.0, 2019: 0.0, 2020: 0.0, 2021: 0.0, 2022: 0.0, 2023: 0.0, 2024: 0.0, 2025: 0.0.

**The tables and rows.** `eia_state_generation_monthly`; the rows for Vermont, region key `state_nuc_VT` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `nuclear-share-state-nuc-vt.csv`.

**Its strength.** The change is 65.97 typical yearly moves (a typical move is 1.2 percent of net generation, 1.4826 times the median absolute change between full years). Holds in more than one year: 23 of the 24 full years after 2001 lie below 2001's value. Survives a change of window: from 2002 to 2025 the change is -72.6, from 2001 to 2024 it is -76.1. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 11. Half the change remains without the first year: from 2002 to 2025 the change is -72.6, 95.4 percent of the change from 2001. At least one typical yearly move: the change is 65.97 typical yearly moves (1.2 percent of net generation a year, the median move between full years); the floor is 1.

**Its limits.** EIA's monthly net generation as published, the latest months preliminary; a state's share counts what is generated in it, not what is used in it, and EIA withholds some plants' months.

**Reproduce.** `python nuclear-share-state-nuc-vt.reproduce.py <the table's CSV>` and `do nuclear-share-state-nuc-vt.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
