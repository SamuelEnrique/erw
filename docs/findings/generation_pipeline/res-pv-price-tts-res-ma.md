# What a home solar system costs: residential systems in Massachusetts

Draft `scan-deep-1684caf0fa14` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The median installed price of residential systems in Massachusetts was 3,916 USD per kW DC in 2023, against 8,025 USD per kW DC in 2009, the first full year the ERW holds.

![What a home solar system costs, residential systems in Massachusetts](res-pv-price-tts-res-ma.png)

**The figure by full year** (USD per kW DC): 2009: 8,025, 2010: 6,790, 2011: 6,000, 2012: 4,980, 2013: 4,975, 2014: 4,900, 2015: 4,893, 2016: 4,548, 2017: 4,060, 2018: 3,933, 2019: 3,460, 2020: 3,460, 2021: 3,460, 2022: 3,790, 2023: 3,916.

**The tables and rows.** `lbnl_tracking_the_sun`; the rows for residential systems in Massachusetts, region key `tts_res_MA` (the card's `hunt.region`), years 2009 to 2023. The yearly values: `res-pv-price-tts-res-ma.csv`.

**Its strength.** The change is 12.14 typical yearly moves (a typical move is 339 USD per kW DC, 1.4826 times the median absolute change between full years). Holds in more than one year: 14 of the 14 full years after 2009 lie below 2009's value. Survives a change of window: from 2010 to 2023 the change is -2,873, from 2009 to 2022 it is -4,235. Sample large enough: 2009 holds 1 and 2023 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2010 to 2023 the change is -2,873, 69.9 percent of the change from 2009. At least one typical yearly move: the change is 12.14 typical yearly moves (339 USD per kW DC a year, the median move between full years); the floor is 1.

**Its limits.** Nominal dollars; the ERW's unscreened median over the systems Berkeley Lab lists with a price, not Berkeley Lab's reported figure; a year with fewer than 500 priced systems is left out.

**Reproduce.** `python res-pv-price-tts-res-ma.reproduce.py <the table's CSV>` and `do res-pv-price-tts-res-ma.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
