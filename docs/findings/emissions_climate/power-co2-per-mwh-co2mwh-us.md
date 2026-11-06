# The power sector's co2 per mwh: the United States

Draft `scan-deep-653a6d6ac682` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The power sector's CO2 per MWh generated in the United States was 362 kg CO2 per MWh in 2022, against 604 kg CO2 per MWh in 2001, the first year this measure counts.

![The power sector's co2 per mwh, the United States](power-co2-per-mwh-co2mwh-us.png)

**The figure by full year** (kg CO2 per MWh): 2001: 604, 2002: 589, 2003: 593, 2004: 588, 2005: 592, 2006: 577, 2007: 580, 2008: 573, 2009: 543, 2010: 548, 2011: 527, 2012: 500, 2013: 501, 2014: 498, 2015: 466, 2016: 444, 2017: 429, 2018: 420, 2019: 389, 2020: 359, 2021: 375, 2022: 362.

**The tables and rows.** `eia_co2_state_annual`, `eia_state_generation_monthly`; the rows for the United States, region key `co2mwh_US` (the card's `hunt.region`), years 2001 to 2022. The yearly values: `power-co2-per-mwh-co2mwh-us.csv`.

**Its strength.** The change is 11.33 typical yearly moves (a typical move is 21 kg CO2 per MWh, 1.4826 times the median absolute change between full years). Holds in more than one year: 21 of the 21 full years after 2001 lie below 2001's value. Survives a change of window: from 2002 to 2022 the change is -227, from 2001 to 2021 it is -229. Sample large enough: 2001 holds 1 and 2022 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2002 to 2022 the change is -227, 93.6 percent of the change from 2001. At least one typical yearly move: the change is 11.33 typical yearly moves (21 kg CO2 per MWh a year, the median move between full years); the floor is 1.

**Its limits.** EIA's energy-related CO2 by state, which ends in 2022 in the ERW's table; it counts fuel burned, not the electricity a state imports. Two families in one figure: EIA's CO2 by state over its net generation; combined heat and power plants' heat is in the CO2 and not in the MWh.

**Reproduce.** `python power-co2-per-mwh-co2mwh-us.reproduce.py <the table's CSV>` and `do power-co2-per-mwh-co2mwh-us.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
