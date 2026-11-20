# What commercial customers pay, by state: Alaska

Draft `scan-deep-5756429d321d` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The average electricity price to the commercial sector of Alaska was 215.7 USD per MWh in 2024, against 93.2 USD per MWh in 1990, the first full year the ERW holds.

![What commercial customers pay, by state, Alaska](seds-price-comm-sd-ak.png)

**The figure by full year** (USD per MWh): 1990: 93.2, 1991: 95.1, 1992: 98.0, 1993: 98.1, 1994: 98.8, 1995: 98.1, 1996: 98.5, 1997: 99.1, 1998: 98.1, 1999: 95.8, 2000: 101.0, 2001: 106.0, 2002: 104.6, 2003: 104.9, 2004: 109.9, 2005: 115.6, 2006: 119.3, 2007: 121.9, 2008: 136.4, 2009: 144.6, 2010: 139.4, 2011: 151.0, 2012: 149.3, 2013: 155.8, 2014: 170.9, 2015: 174.4, 2016: 175.5, 2017: 188.9, 2018: 185.8, 2019: 198.0, 2020: 195.7, 2021: 196.1, 2022: 200.6, 2023: 208.7, 2024: 215.7.

**The tables and rows.** `eia_seds_state_energy`; the rows for Alaska, region key `sd_ak` (the card's `hunt.region`), years 1990 to 2024. The yearly values: `seds-price-comm-sd-ak.csv`.

**Its strength.** The change is 25.34 typical yearly moves (a typical move is 4.8 USD per MWh, 1.4826 times the median absolute change between full years). Holds in more than one year: 34 of the 34 full years after 1990 lie above 1990's value. Survives a change of window: from 1991 to 2024 the change is 120.6, from 1990 to 2023 it is 115.4. Sample large enough: 1990 holds 1 and 2024 holds 1 observations; the floor is 1. Half the change remains without the first year: from 1991 to 2024 the change is 120.6, 98.5 percent of the change from 1990. At least one typical yearly move: the change is 25.34 typical yearly moves (4.8 USD per MWh a year, the median move between full years); the floor is 1.

**Its limits.** EIA's State Energy Data System, the latest release; the newest year is revised with each release; a state's consumption, wherever the energy was produced. Nominal dollars; SEDS's price is the sector's revenue over its sales in the state, USD per MMBtu times 3.412.

**Reproduce.** `python seds-price-comm-sd-ak.reproduce.py <the table's CSV>` and `do seds-price-comm-sd-ak.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
