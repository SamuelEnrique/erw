# The battery fleet's hours: the United States

Draft `scan-deep-2d084fa894ec` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The energy capacity per MW of the battery fleet in the United States at the year's end was 2.77 MWh per MW in 2025, against 0.61 MWh per MW in 2015, the first full year the ERW holds.

![The battery fleet's hours, the United States](fleet-hours-us-fleet-battery-operating-mwh-per-mw.png)

**The figure by full year** (MWh per MW): 2015: 0.61, 2016: 0.82, 2017: 1.13, 2018: 1.44, 2019: 1.70, 2020: 1.98, 2021: 2.66, 2022: 2.70, 2023: 2.71, 2024: 2.73, 2025: 2.77.

**The tables and rows.** `storage_buildout_monthly`; the rows for the United States, region key `us_fleet_battery_operating_mwh_per_mw` (the card's `hunt.region`), years 2015 to 2025. The yearly values: `fleet-hours-us-fleet-battery-operating-mwh-per-mw.csv`.

**Its strength.** The change is 6.25 typical yearly moves (a typical move is 0.35 MWh per MW, 1.4826 times the median absolute change between full years). Holds in more than one year: 10 of the 10 full years after 2015 lie above 2015's value. Survives a change of window: from 2016 to 2025 the change is 1.95, from 2015 to 2024 it is 2.12. Sample large enough: 2015 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2016 to 2025 the change is 1.95, 90.2 percent of the change from 2015. At least one typical yearly move: the change is 6.25 typical yearly moves (0.35 MWh per MW a year, the median move between full years); the floor is 1.

**Its limits.** EIA-860M's reported energy capacity; batteries that report no MWh are left out of the ratio.

**Reproduce.** `python fleet-hours-us-fleet-battery-operating-mwh-per-mw.reproduce.py <the table's CSV>` and `do fleet-hours-us-fleet-battery-operating-mwh-per-mw.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
