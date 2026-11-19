# A nuclear plant's time out: the Byron Generating Station nuclear plant

Draft `scan-deep-ea1c1945e985` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The mean share of the capacity of the Byron Generating Station nuclear plant on outage over the year was 3.1 percent in 2025, against 8.2 percent in 2007, the first full year the ERW holds.

![A nuclear plant's time out, the Byron Generating Station nuclear plant](nuc-out-share-nucf-6023.png)

**The figure by full year** (percent): 2007: 8.2, 2008: 6.0, 2009: 3.8, 2010: 3.0, 2011: 10.0, 2012: 8.3, 2013: 3.7, 2014: 6.6, 2015: 6.2, 2016: 5.4, 2017: 7.3, 2018: 3.0, 2019: 2.7, 2020: 5.7, 2021: 3.3, 2022: 4.2, 2023: 5.6, 2024: 3.7, 2025: 3.1.

**The tables and rows.** `eia_nuclear_outages_facility_daily`; the rows for the Byron Generating Station nuclear plant, region key `nucf_6023` (the card's `hunt.region`), years 2007 to 2025. The yearly values: `nuc-out-share-nucf-6023.csv`.

**Its strength.** The change is 1.81 typical yearly moves (a typical move is 2.8 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 16 of the 18 full years after 2007 lie below 2007's value. Survives a change of window: from 2008 to 2025 the change is -2.9, from 2007 to 2024 it is -4.5. Sample large enough: 2007 holds 365 and 2025 holds 365 observations; the floor is 330. Half the change remains without the first year: from 2008 to 2025 the change is -2.9, 56.9 percent of the change from 2007. At least one typical yearly move: the change is 1.81 typical yearly moves (2.8 percent a year, the median move between full years); the floor is 1.

**Its limits.** EIA's daily nuclear outages by facility, as EIA compiles them from the NRC's daily status; a facility's capacity is as EIA lists it that day; a year's days are those every facility row holds.

**Reproduce.** `python nuc-out-share-nucf-6023.reproduce.py <the table's CSV>` and `do nuc-out-share-nucf-6023.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
