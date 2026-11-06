# Enrichment of us origin: the United States

Draft `scan-deep-20b1b2a70f28` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The share of the enrichment bought for US reactors that was done in the US was 22.8 percent of enrichment services in 2025, against 13.9 percent of enrichment services in 2003, the first year EIA's report holds.

![Enrichment of us origin, the United States](us-enrichment-share-us-enrich-origin.png)

**The figure by full year** (percent of enrichment services): 2003: 13.9, 2004: 11.9, 2005: 9.2, 2006: 12.1, 2007: 10.4, 2008: 15.0, 2009: 23.8, 2010: 16.3, 2011: 16.4, 2012: 20.9, 2013: 31.4, 2014: 29.2, 2015: 31.8, 2016: 33.6, 2017: 43.4, 2018: 33.3, 2019: 39.8, 2020: 29.1, 2021: 19.0, 2022: 27.5, 2023: 28.3, 2024: 19.1, 2025: 22.8.

**The tables and rows.** `eia_uranium_marketing_annual`; the rows for the United States, region key `us_enrich_origin` (the card's `hunt.region`), years 2003 to 2025. The yearly values: `us-enrichment-share-us-enrich-origin.csv`.

**Its strength.** The change is 1.32 typical yearly moves (a typical move is 6.8 percent of enrichment services, 1.4826 times the median absolute change between full years). Holds in more than one year: 18 of the 22 full years after 2003 lie above 2003's value. Survives a change of window: from 2004 to 2025 the change is 11.0, from 2003 to 2024 it is 5.2. Sample large enough: 2003 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2004 to 2025 the change is 11.0, 122.6 percent of the change from 2003. At least one typical yearly move: the change is 1.32 typical yearly moves (6.8 percent of enrichment services a year, the median move between full years); the floor is 1.

**Its limits.** EIA's Uranium Marketing Annual Report: what the owners and operators of US reactors bought, in pounds of U3O8 equivalent; EIA withholds some years' figures. Separative work units (SWU).

**Reproduce.** `python us-enrichment-share-us-enrich-origin.reproduce.py <the table's CSV>` and `do us-enrichment-share-us-enrich-origin.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
