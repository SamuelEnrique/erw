# What commercial customers pay, by state: Hawaii

Draft `scan-deep-1b1b2ad15b2e` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The average electricity price to the commercial sector of Hawaii was 381.8 USD per MWh in 2024, against 101.6 USD per MWh in 1990, the first full year the ERW holds.

![What commercial customers pay, by state, Hawaii](seds-price-comm-sd-hi.png)

**The figure by full year** (USD per MWh): 1990: 101.6, 1991: 103.1, 1992: 105.1, 1993: 116.7, 1994: 116.7, 1995: 121.6, 1996: 129.8, 1997: 132.6, 1998: 123.1, 1999: 127.4, 2000: 148.1, 2001: 148.5, 2002: 141.6, 2003: 150.2, 2004: 161.9, 2005: 190.4, 2006: 214.2, 2007: 219.1, 2008: 297.2, 2009: 218.6, 2010: 259.3, 2011: 323.7, 2012: 348.8, 2013: 340.6, 2014: 342.1, 2015: 269.3, 2016: 246.4, 2017: 267.7, 2018: 299.0, 2019: 292.3, 2020: 284.1, 2021: 308.8, 2022: 401.8, 2023: 390.3, 2024: 381.8.

**The tables and rows.** `eia_seds_state_energy`; the rows for Hawaii, region key `sd_hi` (the card's `hunt.region`), years 1990 to 2024. The yearly values: `seds-price-comm-sd-hi.csv`.

**Its strength.** The change is 17.99 typical yearly moves (a typical move is 15.6 USD per MWh, 1.4826 times the median absolute change between full years). Holds in more than one year: 34 of the 34 full years after 1990 lie above 1990's value. Survives a change of window: from 1991 to 2024 the change is 278.7, from 1990 to 2023 it is 288.7. Sample large enough: 1990 holds 1 and 2024 holds 1 observations; the floor is 1. Half the change remains without the first year: from 1991 to 2024 the change is 278.7, 99.4 percent of the change from 1990. At least one typical yearly move: the change is 17.99 typical yearly moves (15.6 USD per MWh a year, the median move between full years); the floor is 1.

**Its limits.** EIA's State Energy Data System, the latest release; the newest year is revised with each release; a state's consumption, wherever the energy was produced. Nominal dollars; SEDS's price is the sector's revenue over its sales in the state, USD per MMBtu times 3.412.

**Reproduce.** `python seds-price-comm-sd-hi.reproduce.py <the table's CSV>` and `do seds-price-comm-sd-hi.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
