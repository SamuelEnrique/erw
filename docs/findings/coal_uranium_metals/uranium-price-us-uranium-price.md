# What us reactors pay for uranium: the United States

Draft `scan-deep-0432d100ffa9` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The average price US reactor owners paid for uranium was 58.46 USD per pound U3O8e in 2025, against 10.81 USD per pound U3O8e in 2003, the first year EIA's report holds.

![What us reactors pay for uranium, the United States](uranium-price-us-uranium-price.png)

**The figure by full year** (USD per pound U3O8e): 2003: 10.81, 2004: 12.61, 2005: 14.36, 2006: 18.61, 2007: 32.78, 2008: 45.88, 2009: 45.86, 2010: 49.29, 2011: 55.64, 2012: 54.99, 2013: 51.99, 2014: 46.16, 2015: 44.13, 2016: 42.43, 2017: 38.80, 2018: 38.81, 2019: 35.59, 2020: 33.27, 2021: 33.91, 2022: 39.08, 2023: 43.80, 2024: 52.71, 2025: 58.46.

**The tables and rows.** `eia_uranium_marketing_annual`; the rows for the United States, region key `us_uranium_price` (the card's `hunt.region`), years 2003 to 2025. The yearly values: `uranium-price-us-uranium-price.csv`.

**Its strength.** The change is 9.67 typical yearly moves (a typical move is 4.93 USD per pound U3O8e, 1.4826 times the median absolute change between full years). Holds in more than one year: 22 of the 22 full years after 2003 lie above 2003's value. Survives a change of window: from 2004 to 2025 the change is 45.85, from 2003 to 2024 it is 41.90. Sample large enough: 2003 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2004 to 2025 the change is 45.85, 96.2 percent of the change from 2003. At least one typical yearly move: the change is 9.67 typical yearly moves (4.93 USD per pound U3O8e a year, the median move between full years); the floor is 1.

**Its limits.** EIA's Uranium Marketing Annual Report: what the owners and operators of US reactors bought, in pounds of U3O8 equivalent; EIA withholds some years' figures. Nominal dollars, long-term and spot contracts together.

**Reproduce.** `python uranium-price-us-uranium-price.reproduce.py <the table's CSV>` and `do uranium-price-us-uranium-price.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
