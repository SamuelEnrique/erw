# A nuclear plant's time out: the Nine Mile Point Nuclear Station nuclear plant

Draft `scan-deep-bfccc073027e` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The mean share of the capacity of the Nine Mile Point Nuclear Station nuclear plant on outage over the year was 3.6 percent in 2025, against 8.7 percent in 2007, the first full year the ERW holds.

![A nuclear plant's time out, the Nine Mile Point Nuclear Station nuclear plant](nuc-out-share-nucf-2589.png)

**The figure by full year** (percent): 2007: 8.7, 2008: 6.3, 2009: 2.8, 2010: 7.2, 2011: 7.7, 2012: 18.2, 2013: 5.1, 2014: 8.7, 2015: 4.2, 2016: 7.2, 2017: 3.9, 2018: 7.1, 2019: 5.5, 2020: 6.4, 2021: 2.2, 2022: 8.2, 2023: 5.8, 2024: 6.5, 2025: 3.6.

**The tables and rows.** `eia_nuclear_outages_facility_daily`; the rows for the Nine Mile Point Nuclear Station nuclear plant, region key `nucf_2589` (the card's `hunt.region`), years 2007 to 2025. The yearly values: `nuc-out-share-nucf-2589.csv`.

**Its strength.** The change is 1.06 typical yearly moves (a typical move is 4.8 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 17 of the 18 full years after 2007 lie below 2007's value. Survives a change of window: from 2008 to 2025 the change is -2.7, from 2007 to 2024 it is -2.2. Sample large enough: 2007 holds 365 and 2025 holds 365 observations; the floor is 330. Half the change remains without the first year: from 2008 to 2025 the change is -2.7, 53.0 percent of the change from 2007. At least one typical yearly move: the change is 1.06 typical yearly moves (4.8 percent a year, the median move between full years); the floor is 1.

**Its limits.** EIA's daily nuclear outages by facility, as EIA compiles them from the NRC's daily status; a facility's capacity is as EIA lists it that day; a year's days are those every facility row holds.

**Reproduce.** `python nuc-out-share-nucf-2589.reproduce.py <the table's CSV>` and `do nuc-out-share-nucf-2589.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
