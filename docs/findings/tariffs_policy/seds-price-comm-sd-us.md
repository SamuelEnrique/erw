# What commercial customers pay, by state: the United States

Draft `scan-deep-b4c932303b8a` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The average electricity price to the commercial sector of the United States was 127.5 USD per MWh in 2024, against 72.3 USD per MWh in 1990, the first full year the ERW holds.

![What commercial customers pay, by state, the United States](seds-price-comm-sd-us.png)

**The figure by full year** (USD per MWh): 1990: 72.3, 1991: 74.1, 1992: 75.6, 1993: 76.4, 1994: 76.3, 1995: 76.1, 1996: 75.6, 1997: 75.2, 1998: 73.3, 1999: 71.7, 2000: 73.4, 2001: 78.4, 2002: 77.8, 2003: 80.3, 2004: 81.7, 2005: 86.7, 2006: 94.6, 2007: 96.5, 2008: 102.6, 2009: 101.6, 2010: 101.9, 2011: 102.4, 2012: 100.9, 2013: 102.6, 2014: 107.4, 2015: 106.4, 2016: 104.3, 2017: 106.6, 2018: 106.7, 2019: 106.8, 2020: 105.9, 2021: 112.2, 2022: 124.1, 2023: 125.9, 2024: 127.5.

**The tables and rows.** `eia_seds_state_energy`; the rows for the United States, region key `sd_us` (the card's `hunt.region`), years 1990 to 2024. The yearly values: `seds-price-comm-sd-us.csv`.

**Its strength.** The change is 23.22 typical yearly moves (a typical move is 2.4 USD per MWh, 1.4826 times the median absolute change between full years). Holds in more than one year: 33 of the 34 full years after 1990 lie above 1990's value. Survives a change of window: from 1991 to 2024 the change is 53.4, from 1990 to 2023 it is 53.6. Sample large enough: 1990 holds 1 and 2024 holds 1 observations; the floor is 1. Half the change remains without the first year: from 1991 to 2024 the change is 53.4, 96.7 percent of the change from 1990. At least one typical yearly move: the change is 23.22 typical yearly moves (2.4 USD per MWh a year, the median move between full years); the floor is 1.

**Its limits.** EIA's State Energy Data System, the latest release; the newest year is revised with each release; a state's consumption, wherever the energy was produced. Nominal dollars; SEDS's price is the sector's revenue over its sales in the state, USD per MMBtu times 3.412.

**Reproduce.** `python seds-price-comm-sd-us.reproduce.py <the table's CSV>` and `do seds-price-comm-sd-us.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
