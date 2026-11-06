# Solar in the tightest hours: ERCOT

Draft `scan-deep-5aaddd49168d` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Solar's output in ERCOT's tightest hours, as a share of its solar capacity, was 5.0 percent of solar capacity in 2025, against 71.1 percent of solar capacity in 2019, the first year the ERW's table holds.

![Solar in the tightest hours, ERCOT](tight-solar-ercot-tight-solar.png)

**The figure by full year** (percent of solar capacity): 2019: 71.1, 2020: 73.8, 2021: 71.4, 2022: 57.6, 2023: 48.7, 2024: 33.1, 2025: 5.0.

**The tables and rows.** `grid_stress_yearly`; the rows for ERCOT, region key `ercot_tight_solar` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `tight-solar-ercot-tight-solar.csv`.

**Its strength.** The change is 3.91 typical yearly moves (a typical move is 16.9 percent of solar capacity, 1.4826 times the median absolute change between full years). Holds in more than one year: 4 of the 6 full years after 2019 lie below 2019's value. Survives a change of window: from 2020 to 2025 the change is -68.8, from 2019 to 2024 it is -38.0. Sample large enough: 2019 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2020 to 2025 the change is -68.8, 104.1 percent of the change from 2019. At least one typical yearly move: the change is 3.91 typical yearly moves (16.9 percent of solar capacity a year, the median move between full years); the floor is 1.

**Its limits.** The ERW's derived grid_stress_yearly (EIA-930 hourly by source, EIA's generator inventory); the tightest hours are the year's hours of highest net load, and a grid whose capacity grew late in a year shows a share of a capacity it held only in part. 

**Reproduce.** `python tight-solar-ercot-tight-solar.reproduce.py <the table's CSV>` and `do tight-solar-ercot-tight-solar.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
