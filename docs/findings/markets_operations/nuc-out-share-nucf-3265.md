# A nuclear plant's time out: the Oconee nuclear plant

Draft `scan-deep-52b977df2db1` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The mean share of the capacity of the Oconee nuclear plant on outage over the year was 3.0 percent in 2025, against 9.6 percent in 2007, the first full year the ERW holds.

![A nuclear plant's time out, the Oconee nuclear plant](nuc-out-share-nucf-3265.png)

**The figure by full year** (percent): 2007: 9.6, 2008: 11.2, 2009: 8.1, 2010: 7.8, 2011: 10.3, 2012: 9.0, 2013: 7.3, 2014: 6.5, 2015: 3.0, 2016: 6.5, 2017: 3.8, 2018: 6.2, 2019: 3.5, 2020: 5.8, 2021: 2.8, 2022: 7.2, 2023: 2.6, 2024: 5.9, 2025: 3.0.

**The tables and rows.** `eia_nuclear_outages_facility_daily`; the rows for the Oconee nuclear plant, region key `nucf_3265` (the card's `hunt.region`), years 2007 to 2025. The yearly values: `nuc-out-share-nucf-3265.csv`.

**Its strength.** The change is 1.62 typical yearly moves (a typical move is 4.1 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 16 of the 18 full years after 2007 lie below 2007's value. Survives a change of window: from 2008 to 2025 the change is -8.2, from 2007 to 2024 it is -3.6. Sample large enough: 2007 holds 365 and 2025 holds 365 observations; the floor is 330. Half the change remains without the first year: from 2008 to 2025 the change is -8.2, 125.3 percent of the change from 2007. At least one typical yearly move: the change is 1.62 typical yearly moves (4.1 percent a year, the median move between full years); the floor is 1.

**Its limits.** EIA's daily nuclear outages by facility, as EIA compiles them from the NRC's daily status; a facility's capacity is as EIA lists it that day; a year's days are those every facility row holds.

**Reproduce.** `python nuc-out-share-nucf-3265.reproduce.py <the table's CSV>` and `do nuc-out-share-nucf-3265.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
