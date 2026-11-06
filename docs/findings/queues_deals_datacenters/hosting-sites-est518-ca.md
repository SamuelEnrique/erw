# Data processing and hosting sites: California

Draft `scan-deep-651294f23fc1` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The number of data processing and hosting establishments in California was 2,698 establishments in 2023, against 2,097 establishments in 2012, the first full year the ERW holds.

![Data processing and hosting sites, California](hosting-sites-est518-ca.png)

**The figure by full year** (establishments): 2012: 2,097, 2013: 2,157, 2014: 2,098, 2015: 2,226, 2016: 2,297, 2017: 2,658, 2018: 2,619, 2019: 2,528, 2020: 2,534, 2021: 2,566, 2022: 2,532, 2023: 2,698.

**The tables and rows.** `census_cbp_hosting_annual`; the rows for California, region key `est518_CA` (the card's `hunt.region`), years 2012 to 2023. The yearly values: `hosting-sites-est518-ca.csv`.

**Its strength.** The change is 6.76 typical yearly moves (a typical move is 89 establishments, 1.4826 times the median absolute change between full years). Holds in more than one year: 11 of the 11 full years after 2012 lie above 2012's value. Survives a change of window: from 2013 to 2023 the change is 541, from 2012 to 2022 it is 435. Sample large enough: 2012 holds 1 and 2023 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2013 to 2023 the change is 541, 90.0 percent of the change from 2012. At least one typical yearly move: the change is 6.76 typical yearly moves (89 establishments a year, the median move between full years); the floor is 1.

**Its limits.** County Business Patterns counts establishments by their main activity, so a data center run inside another firm's establishment is not in it; the Census Bureau adds noise to protect respondents, and NAICS 518210's definition widened with the 2022 codes.

**Reproduce.** `python hosting-sites-est518-ca.reproduce.py <the table's CSV>` and `do hosting-sites-est518-ca.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
