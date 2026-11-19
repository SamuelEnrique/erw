# What industry pays, by state: the United States

Draft `scan-deep-54ac40855a5a` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The average electricity price to the industrial sector of the United States was 81.5 USD per MWh in 2024, against 47.5 USD per MWh in 1990, the first full year the ERW holds.

![What industry pays, by state, the United States](seds-price-ind-sd-us.png)

**The figure by full year** (USD per MWh): 1990: 47.5, 1991: 48.4, 1992: 48.4, 1993: 48.5, 1994: 47.8, 1995: 46.7, 1996: 46.0, 1997: 45.3, 1998: 44.8, 1999: 44.3, 2000: 46.4, 2001: 50.4, 2002: 48.8, 2003: 51.1, 2004: 52.5, 2005: 57.2, 2006: 61.5, 2007: 63.8, 2008: 69.4, 2009: 68.4, 2010: 67.9, 2011: 68.3, 2012: 66.9, 2013: 69.1, 2014: 71.2, 2015: 69.4, 2016: 67.9, 2017: 69.0, 2018: 69.4, 2019: 68.4, 2020: 66.9, 2021: 71.8, 2022: 83.3, 2023: 80.7, 2024: 81.5.

**The tables and rows.** `eia_seds_state_energy`; the rows for the United States, region key `sd_us` (the card's `hunt.region`), years 1990 to 2024. The yearly values: `seds-price-ind-sd-us.csv`.

**Its strength.** The change is 16.22 typical yearly moves (a typical move is 2.1 USD per MWh, 1.4826 times the median absolute change between full years). Holds in more than one year: 28 of the 34 full years after 1990 lie above 1990's value. Survives a change of window: from 1991 to 2024 the change is 33.2, from 1990 to 2023 it is 33.2. Sample large enough: 1990 holds 1 and 2024 holds 1 observations; the floor is 1. Half the change remains without the first year: from 1991 to 2024 the change is 33.2, 97.4 percent of the change from 1990. At least one typical yearly move: the change is 16.22 typical yearly moves (2.1 USD per MWh a year, the median move between full years); the floor is 1.

**Its limits.** EIA's State Energy Data System, the latest release; the newest year is revised with each release; a state's consumption, wherever the energy was produced. Nominal dollars; SEDS's price is the sector's revenue over its sales in the state, USD per MMBtu times 3.412.

**Reproduce.** `python seds-price-ind-sd-us.reproduce.py <the table's CSV>` and `do seds-price-ind-sd-us.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
