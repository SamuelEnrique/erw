# What industry pays, by state: Alaska

Draft `scan-deep-5508f13c2cbd` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The average electricity price to the industrial sector of Alaska was 193.1 USD per MWh in 2024, against 79.1 USD per MWh in 1990, the first full year the ERW holds.

![What industry pays, by state, Alaska](seds-price-ind-sd-ak.png)

**The figure by full year** (USD per MWh): 1990: 79.1, 1991: 82.2, 1992: 77.5, 1993: 81.9, 1994: 83.7, 1995: 83.8, 1996: 84.7, 1997: 74.8, 1998: 71.7, 1999: 73.2, 2000: 75.6, 2001: 76.1, 2002: 76.5, 2003: 78.6, 2004: 83.3, 2005: 92.9, 2006: 115.4, 2007: 126.3, 2008: 141.7, 2009: 131.5, 2010: 141.5, 2011: 157.1, 2012: 168.2, 2013: 158.3, 2014: 156.6, 2015: 145.2, 2016: 152.2, 2017: 163.4, 2018: 171.0, 2019: 169.4, 2020: 158.9, 2021: 168.5, 2022: 184.3, 2023: 187.0, 2024: 193.1.

**The tables and rows.** `eia_seds_state_energy`; the rows for Alaska, region key `sd_ak` (the card's `hunt.region`), years 1990 to 2024. The yearly values: `seds-price-ind-sd-ak.csv`.

**Its strength.** The change is 11.81 typical yearly moves (a typical move is 9.7 USD per MWh, 1.4826 times the median absolute change between full years). Holds in more than one year: 26 of the 34 full years after 1990 lie above 1990's value. Survives a change of window: from 1991 to 2024 the change is 111.0, from 1990 to 2023 it is 108.0. Sample large enough: 1990 holds 1 and 2024 holds 1 observations; the floor is 1. Half the change remains without the first year: from 1991 to 2024 the change is 111.0, 97.3 percent of the change from 1990. At least one typical yearly move: the change is 11.81 typical yearly moves (9.7 USD per MWh a year, the median move between full years); the floor is 1.

**Its limits.** EIA's State Energy Data System, the latest release; the newest year is revised with each release; a state's consumption, wherever the energy was produced. Nominal dollars; SEDS's price is the sector's revenue over its sales in the state, USD per MMBtu times 3.412.

**Reproduce.** `python seds-price-ind-sd-ak.reproduce.py <the table's CSV>` and `do seds-price-ind-sd-ak.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
