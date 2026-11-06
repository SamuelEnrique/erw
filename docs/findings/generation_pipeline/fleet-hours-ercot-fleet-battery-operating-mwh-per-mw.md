# The battery fleet's hours: ERCOT

Draft `scan-deep-b65761b2cde3` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The energy capacity per MW of the battery fleet in ERCOT at the year's end was 1.55 MWh per MW in 2025, against 0.38 MWh per MW in 2015, the first full year the ERW holds.

![The battery fleet's hours, ERCOT](fleet-hours-ercot-fleet-battery-operating-mwh-per-mw.png)

**The figure by full year** (MWh per MW): 2015: 0.38, 2016: 0.38, 2017: 0.40, 2018: 0.56, 2019: 0.94, 2020: 1.06, 2021: 1.29, 2022: 1.29, 2023: 1.43, 2024: 1.43, 2025: 1.55.

**The tables and rows.** `storage_buildout_monthly`; the rows for ERCOT, region key `ercot_fleet_battery_operating_mwh_per_mw` (the card's `hunt.region`), years 2015 to 2025. The yearly values: `fleet-hours-ercot-fleet-battery-operating-mwh-per-mw.csv`.

**Its strength.** The change is 6.79 typical yearly moves (a typical move is 0.17 MWh per MW, 1.4826 times the median absolute change between full years). Holds in more than one year: 9 of the 10 full years after 2015 lie above 2015's value. Survives a change of window: from 2016 to 2025 the change is 1.17, from 2015 to 2024 it is 1.06. Sample large enough: 2015 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2016 to 2025 the change is 1.17, 100.0 percent of the change from 2015. At least one typical yearly move: the change is 6.79 typical yearly moves (0.17 MWh per MW a year, the median move between full years); the floor is 1.

**Its limits.** EIA-860M's reported energy capacity; batteries that report no MWh are left out of the ratio.

**Reproduce.** `python fleet-hours-ercot-fleet-battery-operating-mwh-per-mw.reproduce.py <the table's CSV>` and `do fleet-hours-ercot-fleet-battery-operating-mwh-per-mw.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
