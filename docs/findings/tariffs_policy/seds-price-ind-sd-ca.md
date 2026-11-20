# What industry pays, by state: California

Draft `scan-deep-8094fe221198` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The average electricity price to the industrial sector of California was 215.3 USD per MWh in 2024, against 72.8 USD per MWh in 1990, the first full year the ERW holds.

![What industry pays, by state, California](seds-price-ind-sd-ca.png)

**The figure by full year** (USD per MWh): 1990: 72.8, 1991: 75.8, 1992: 75.9, 1993: 73.3, 1994: 70.9, 1995: 73.7, 1996: 69.6, 1997: 69.5, 1998: 64.9, 1999: 65.7, 2000: 71.4, 2001: 92.3, 2002: 98.1, 2003: 95.9, 2004: 92.7, 2005: 95.5, 2006: 100.9, 2007: 99.8, 2008: 100.9, 2009: 104.2, 2010: 98.0, 2011: 101.1, 2012: 104.9, 2013: 114.4, 2014: 123.4, 2015: 121.6, 2016: 119.2, 2017: 127.3, 2018: 132.0, 2019: 134.0, 2020: 142.7, 2021: 148.2, 2022: 170.9, 2023: 186.4, 2024: 215.3.

**The tables and rows.** `eia_seds_state_energy`; the rows for California, region key `sd_ca` (the card's `hunt.region`), years 1990 to 2024. The yearly values: `seds-price-ind-sd-ca.csv`.

**Its strength.** The change is 26.69 typical yearly moves (a typical move is 5.3 USD per MWh, 1.4826 times the median absolute change between full years). Holds in more than one year: 28 of the 34 full years after 1990 lie above 1990's value. Survives a change of window: from 1991 to 2024 the change is 139.4, from 1990 to 2023 it is 113.6. Sample large enough: 1990 holds 1 and 2024 holds 1 observations; the floor is 1. Half the change remains without the first year: from 1991 to 2024 the change is 139.4, 97.9 percent of the change from 1990. At least one typical yearly move: the change is 26.69 typical yearly moves (5.3 USD per MWh a year, the median move between full years); the floor is 1.

**Its limits.** EIA's State Energy Data System, the latest release; the newest year is revised with each release; a state's consumption, wherever the energy was produced. Nominal dollars; SEDS's price is the sector's revenue over its sales in the state, USD per MMBtu times 3.412.

**Reproduce.** `python seds-price-ind-sd-ca.reproduce.py <the table's CSV>` and `do seds-price-ind-sd-ca.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
