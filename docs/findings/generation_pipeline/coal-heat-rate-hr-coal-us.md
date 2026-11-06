# The coal fleet's heat rate: the United States

Draft `scan-deep-86882524bc40` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The coal-fired fleet's fuel per MWh in the United States was 11.02 MMBtu per MWh in 2024, against 10.63 MMBtu per MWh in 2001, the first full year the ERW holds.

![The coal fleet's heat rate, the United States](coal-heat-rate-hr-coal-us.png)

**The figure by full year** (MMBtu per MWh): 2001: 10.63, 2002: 10.56, 2003: 10.53, 2004: 10.58, 2005: 10.61, 2006: 10.58, 2007: 10.59, 2008: 10.60, 2009: 10.65, 2010: 10.66, 2011: 10.70, 2012: 10.76, 2013: 10.70, 2014: 10.66, 2015: 10.74, 2016: 10.76, 2017: 10.71, 2018: 10.72, 2019: 10.79, 2020: 10.91, 2021: 10.81, 2022: 10.94, 2023: 11.00, 2024: 11.02.

**The tables and rows.** `eia923_plant_fuel_annual`; the rows for the United States, region key `hr_coal_US` (the card's `hunt.region`), years 2001 to 2024. The yearly values: `coal-heat-rate-hr-coal-us.csv`.

**Its strength.** The change is 5.41 typical yearly moves (a typical move is 0.07 MMBtu per MWh, 1.4826 times the median absolute change between full years). Holds in more than one year: 16 of the 23 full years after 2001 lie above 2001's value. Survives a change of window: from 2002 to 2024 the change is 0.46, from 2001 to 2023 it is 0.37. Sample large enough: 2001 holds 1 and 2024 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2002 to 2024 the change is 0.46, 116.4 percent of the change from 2001. At least one typical yearly move: the change is 5.41 typical yearly moves (0.07 MMBtu per MWh a year, the median move between full years); the floor is 1.

**Its limits.** EIA-923's total fuel consumed, combined heat and power plants' useful heat included; a fleet that runs less often runs at less efficient loads.

**Reproduce.** `python coal-heat-rate-hr-coal-us.reproduce.py <the table's CSV>` and `do coal-heat-rate-hr-coal-us.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
