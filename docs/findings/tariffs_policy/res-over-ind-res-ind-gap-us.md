# Homes against industry: the United States

Draft `scan-deep-45a2cdbdc53c` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The residential electricity price in the United States above the industrial price was 87.7 USD per MWh in 2025, against 35.4 USD per MWh in 2001, the first full year the ERW holds.

![Homes against industry, the United States](res-over-ind-res-ind-gap-us.png)

**The figure by full year** (USD per MWh): 2001: 35.4, 2002: 35.6, 2003: 36.1, 2004: 36.9, 2005: 37.1, 2006: 42.2, 2007: 42.5, 2008: 43.1, 2009: 46.8, 2010: 47.9, 2011: 49.1, 2012: 52.0, 2013: 52.4, 2014: 54.4, 2015: 57.5, 2016: 57.9, 2017: 60.2, 2018: 59.6, 2019: 62.1, 2020: 65.0, 2021: 65.0, 2022: 67.4, 2023: 79.9, 2024: 83.9, 2025: 87.7.

**The tables and rows.** `eia_retail_electricity_prices`; the rows for the United States, region key `res_ind_gap_US` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `res-over-ind-res-ind-gap-us.csv`.

**Its strength.** The change is 21.87 typical yearly moves (a typical move is 2.4 USD per MWh, 1.4826 times the median absolute change between full years). Holds in more than one year: 24 of the 24 full years after 2001 lie above 2001's value. Survives a change of window: from 2002 to 2025 the change is 52.1, from 2001 to 2024 it is 48.5. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 11. Half the change remains without the first year: from 2002 to 2025 the change is 52.1, 99.8 percent of the change from 2001. At least one typical yearly move: the change is 21.87 typical yearly moves (2.4 USD per MWh a year, the median move between full years); the floor is 1.

**Its limits.** EIA's figures as published, nominal dollars where a price; the latest months are preliminary.

**Reproduce.** `python res-over-ind-res-ind-gap-us.reproduce.py <the table's CSV>` and `do res-over-ind-res-ind-gap-us.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
