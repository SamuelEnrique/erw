# What commercial customers pay, by state: California

Draft `scan-deep-de3d0bce06a7` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The average electricity price to the commercial sector of California was 255.4 USD per MWh in 2024, against 89.8 USD per MWh in 1990, the first full year the ERW holds.

![What commercial customers pay, by state, California](seds-price-comm-sd-ca.png)

**The figure by full year** (USD per MWh): 1990: 89.8, 1991: 96.0, 1992: 99.2, 1993: 99.9, 1994: 103.7, 1995: 102.7, 1996: 96.3, 1997: 97.5, 1998: 92.0, 1999: 92.4, 2000: 98.6, 2001: 117.7, 2002: 129.7, 2003: 124.8, 2004: 116.4, 2005: 119.1, 2006: 128.9, 2007: 128.2, 2008: 125.5, 2009: 132.7, 2010: 131.0, 2011: 130.5, 2012: 134.1, 2013: 142.0, 2014: 156.2, 2015: 157.4, 2016: 150.7, 2017: 157.6, 2018: 163.4, 2019: 166.7, 2020: 175.3, 2021: 191.8, 2022: 218.1, 2023: 239.1, 2024: 255.4.

**The tables and rows.** `eia_seds_state_energy`; the rows for California, region key `sd_ca` (the card's `hunt.region`), years 1990 to 2024. The yearly values: `seds-price-comm-sd-ca.csv`.

**Its strength.** The change is 18.65 typical yearly moves (a typical move is 8.9 USD per MWh, 1.4826 times the median absolute change between full years). Holds in more than one year: 34 of the 34 full years after 1990 lie above 1990's value. Survives a change of window: from 1991 to 2024 the change is 159.4, from 1990 to 2023 it is 149.3. Sample large enough: 1990 holds 1 and 2024 holds 1 observations; the floor is 1. Half the change remains without the first year: from 1991 to 2024 the change is 159.4, 96.3 percent of the change from 1990. At least one typical yearly move: the change is 18.65 typical yearly moves (8.9 USD per MWh a year, the median move between full years); the floor is 1.

**Its limits.** EIA's State Energy Data System, the latest release; the newest year is revised with each release; a state's consumption, wherever the energy was produced. Nominal dollars; SEDS's price is the sector's revenue over its sales in the state, USD per MMBtu times 3.412.

**Reproduce.** `python seds-price-comm-sd-ca.reproduce.py <the table's CSV>` and `do seds-price-comm-sd-ca.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
