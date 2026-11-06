# Where us crude imports come from: Nigeria

Draft `scan-deep-fea3cf0e9244` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Nigeria's share of US crude oil imports was 2.2 percent of US crude imports in 2025, against 13.8 percent of US crude imports in 1973, the first full year the ERW holds.

![Where us crude imports come from, Nigeria](import-share-imp-ni.png)

**The figure by full year** (percent of US crude imports): 1973: 13.8, 1974: 20.0, 1975: 18.2, 1976: 19.2, 1977: 17.1, 1978: 14.3, 1979: 16.4, 1980: 16.0, 1981: 13.9, 1982: 14.7, 1983: 9.0, 1984: 6.0, 1985: 8.7, 1986: 10.4, 1987: 11.3, 1988: 11.9, 1989: 13.7, 1990: 13.3, 1991: 11.8, 1992: 10.9, 1993: 10.7, 1994: 8.8, 1995: 8.6, 1996: 7.9, 1997: 8.4, 1998: 7.9, 1999: 7.1, 2000: 9.6, 2001: 9.0, 2002: 6.4, 2003: 8.6, 2004: 10.7, 2005: 10.6, 2006: 10.3, 2007: 10.8, 2008: 9.4, 2009: 8.6, 2010: 10.7, 2011: 8.6, 2012: 4.8, 2013: 3.1, 2014: 0.8, 2015: 0.7, 2016: 2.6, 2017: 3.9, 2018: 2.3, 2019: 2.7, 2020: 1.1, 2021: 1.8, 2022: 1.5, 2023: 2.4, 2024: 2.3, 2025: 2.2.

**The tables and rows.** `eia_crude_imports_by_country`; the rows for Nigeria, region key `imp_NI` (the card's `hunt.region`), years 1973 to 2025. The yearly values: `import-share-imp-ni.csv`.

**Its strength.** The change is 5.99 typical yearly moves (a typical move is 1.9 percent of US crude imports, 1.4826 times the median absolute change between full years). Holds in more than one year: 43 of the 52 full years after 1973 lie below 1973's value. Survives a change of window: from 1974 to 2025 the change is -17.8, from 1973 to 2024 it is -11.5. Sample large enough: 1973 holds 12 and 2025 holds 12 observations; the floor is 11. Half the change remains without the first year: from 1974 to 2025 the change is -17.8, 153.5 percent of the change from 1973. At least one typical yearly move: the change is 5.99 typical yearly moves (1.9 percent of US crude imports a year, the median move between full years); the floor is 1.

**Its limits.** EIA's imports by country of origin, monthly thousand barrels a day summed over the year; a country's share of a total that itself changed.

**Reproduce.** `python import-share-imp-ni.reproduce.py <the table's CSV>` and `do import-share-imp-ni.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
