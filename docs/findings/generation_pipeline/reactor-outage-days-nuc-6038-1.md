# A reactor's outage days: McGuire, reactor 1

Draft `scan-deep-a76fd4282570` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The number of days on which at least half of McGuire, reactor 1's capacity was out was 26 days in 2025, against 85 days in 2007, the first full year the ERW holds.

![A reactor's outage days, McGuire, reactor 1](reactor-outage-days-nuc-6038-1.png)

**The figure by full year** (days): 2007: 85, 2008: 59, 2009: 0, 2010: 45, 2011: 36, 2012: 0, 2013: 46, 2014: 69, 2015: 7, 2016: 30, 2017: 24, 2018: 1, 2019: 37, 2020: 34, 2021: 0, 2022: 39, 2023: 41, 2024: 0, 2025: 26.

**The tables and rows.** `eia_nuclear_outages_generator_daily`; the rows for McGuire, reactor 1, region key `nuc_6038_1` (the card's `hunt.region`), years 2007 to 2025. The yearly values: `reactor-outage-days-nuc-6038-1.csv`.

**Its strength.** The change is 1.33 typical yearly moves (a typical move is 44 days, 1.4826 times the median absolute change between full years). Holds in more than one year: 18 of the 18 full years after 2007 lie below 2007's value. Survives a change of window: from 2008 to 2025 the change is -33, from 2007 to 2024 it is -85. Sample large enough: 2007 holds 365 and 2025 holds 365 observations; the floor is 330. Half the change remains without the first year: from 2008 to 2025 the change is -33, 55.9 percent of the change from 2007. At least one typical yearly move: the change is 1.33 typical yearly moves (44 days a year, the median move between full years); the floor is 1.

**Its limits.** EIA's daily estimate; refuelling outages fall every 18 or 24 months, so a reactor's years alternate, and the measure counts planned and forced days alike; only reactors that report all of 2007 and 2025 are counted.

**Reproduce.** `python reactor-outage-days-nuc-6038-1.reproduce.py <the table's CSV>` and `do reactor-outage-days-nuc-6038-1.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
