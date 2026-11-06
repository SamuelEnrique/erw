# How long new batteries run: US batteries

Draft `scan-deep-05c99ca8013f` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The energy capacity per MW of the US batteries that entered service in the year was 2.86 MWh per MW in 2025, against 0.53 MWh per MW in 2015, the first year this measure counts.

![How long new batteries run, US batteries](battery-hours-us-battery-hours.png)

**The figure by full year** (MWh per MW): 2015: 0.53, 2016: 1.10, 2017: 2.32, 2018: 2.27, 2019: 2.70, 2020: 2.46, 2021: 2.88, 2022: 2.74, 2023: 2.73, 2024: 2.76, 2025: 2.86.

**The tables and rows.** `eia860m_operating_generators`; the rows for US batteries, region key `us_battery_hours` (the card's `hunt.region`), years 2015 to 2025. The yearly values: `battery-hours-us-battery-hours.csv`.

**Its strength.** The change is 8.42 typical yearly moves (a typical move is 0.28 MWh per MW, 1.4826 times the median absolute change between full years). Holds in more than one year: 10 of the 10 full years after 2015 lie above 2015's value. Survives a change of window: from 2016 to 2025 the change is 1.75, from 2015 to 2024 it is 2.23. Sample large enough: 2015 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2016 to 2025 the change is 1.75, 75.5 percent of the change from 2015. At least one typical yearly move: the change is 8.42 typical yearly moves (0.28 MWh per MW a year, the median move between full years); the floor is 1.

**Its limits.** EIA-860M's generators that operate today, by the year they entered service: a unit built and since retired is not counted, and the latest months are preliminary. A battery's MWh is its reported energy capacity, not what it delivers in a cycle; a year with less than 100 MW entering service is left out.

**Reproduce.** `python battery-hours-us-battery-hours.reproduce.py <the table's CSV>` and `do battery-hours-us-battery-hours.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
