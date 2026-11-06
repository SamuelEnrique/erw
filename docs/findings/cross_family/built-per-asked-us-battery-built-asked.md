# Built against asked for: US battery

Draft `scan-deep-5f1d006e0f13` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The MW of US battery entering service in the year against the MW of US battery requested in the year was 7.0 percent of MW requested in 2024, against 0.0 percent of MW requested in 2010, the first year this measure counts.

![Built against asked for, US battery](built-per-asked-us-battery-built-asked.png)

**The figure by full year** (percent of MW requested): 2010: 0.0, 2011: 1.3, 2012: 18.2, 2013: 2.0, 2014: 1.3, 2015: 1.7, 2016: 3.2, 2017: 2.7, 2018: 1.0, 2019: 0.5, 2020: 1.1, 2021: 2.3, 2022: 2.8, 2023: 3.0, 2024: 7.0.

**The tables and rows.** `eia860m_operating_generators`, `lbnl_interconnection_queue`; the rows for US battery, region key `us_battery_built_asked` (the card's `hunt.region`), years 2010 to 2024. The yearly values: `built-per-asked-us-battery-built-asked.csv`.

**Its strength.** The change is 5.05 typical yearly moves (a typical move is 1.4 percent of MW requested, 1.4826 times the median absolute change between full years). Holds in more than one year: 14 of the 14 full years after 2010 lie above 2010's value. Survives a change of window: from 2011 to 2024 the change is 5.7, from 2010 to 2023 it is 3.0. Sample large enough: 2010 holds 1 and 2024 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2011 to 2024 the change is 5.7, 81.1 percent of the change from 2010. At least one typical yearly move: the change is 5.05 typical yearly moves (1.4 percent of MW requested a year, the median move between full years); the floor is 1.

**Its limits.** Two families in one figure: a year's requests and a year's completions are different projects (a completion's request is years older), so the figure compares two flows, not a success rate.

**Reproduce.** `python built-per-asked-us-battery-built-asked.reproduce.py <the table's CSV>` and `do built-per-asked-us-battery-built-asked.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
