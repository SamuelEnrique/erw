# Electricity in what homes spend on energy: the United States

Draft `scan-deep-da4f4bfadd76` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Electricity's share of what households in the United States spend on energy was 73.3 percent of home energy spending in 2024, against 65.3 percent of home energy spending in 1990, the first year the ERW's table holds.

![Electricity in what homes spend on energy, the United States](home-electric-spend-home-elec-us.png)

**The figure by full year** (percent of home energy spending): 1990: 65.3, 1991: 66.2, 1992: 66.0, 1993: 66.2, 1994: 66.6, 1995: 68.5, 1996: 65.9, 1997: 65.6, 1998: 69.4, 1999: 68.2, 2000: 63.2, 2001: 61.7, 2002: 66.5, 2003: 62.3, 2004: 61.1, 2005: 59.7, 2006: 62.4, 2007: 62.3, 2008: 59.9, 2009: 65.2, 2010: 66.8, 2011: 66.9, 2012: 69.7, 2013: 68.1, 2014: 66.5, 2015: 71.6, 2016: 74.2, 2017: 72.2, 2018: 70.8, 2019: 70.9, 2020: 73.8, 2021: 71.2, 2022: 68.3, 2023: 70.3, 2024: 73.3.

**The tables and rows.** `eia_seds_residential_annual`; the rows for the United States, region key `home_elec_US` (the card's `hunt.region`), years 1990 to 2024. The yearly values: `home-electric-spend-home-elec-us.csv`.

**Its strength.** The change is 2.79 typical yearly moves (a typical move is 2.9 percent of home energy spending, 1.4826 times the median absolute change between full years). Holds in more than one year: 25 of the 34 full years after 1990 lie above 1990's value. Survives a change of window: from 1991 to 2024 the change is 7.1, from 1990 to 2023 it is 5.1. Sample large enough: 1990 holds 1 and 2024 holds 1 observations; the floor is 1. Half the change remains without the first year: from 1991 to 2024 the change is 7.1, 88.0 percent of the change from 1990. At least one typical yearly move: the change is 2.79 typical yearly moves (2.9 percent of home energy spending a year, the median move between full years); the floor is 1.

**Its limits.** EIA's State Energy Data System, nominal dollars; a share of spending moves with prices as much as with use.

**Reproduce.** `python home-electric-spend-home-elec-us.reproduce.py <the table's CSV>` and `do home-electric-spend-home-elec-us.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
