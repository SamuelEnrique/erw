# Small-scale solar: the United States

Draft `scan-deep-270472592e21` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** EIA's estimate of small-scale solar generation in the United States, as a percent of the state's net generation, was 2.1 percent of net generation in 2025, against 0.3 percent of net generation in 2014, the first full year the ERW holds.

![Small-scale solar, the United States](small-solar-ratio-state-dpv-us.png)

**The figure by full year** (percent of net generation): 2014: 0.3, 2015: 0.3, 2016: 0.5, 2017: 0.6, 2018: 0.7, 2019: 0.8, 2020: 1.0, 2021: 1.2, 2022: 1.4, 2023: 1.8, 2024: 1.9, 2025: 2.1.

**The tables and rows.** `eia_state_generation_monthly`; the rows for the United States, region key `state_dpv_US` (the card's `hunt.region`), years 2014 to 2025. The yearly values: `small-solar-ratio-state-dpv-us.csv`.

**Its strength.** The change is 7.96 typical yearly moves (a typical move is 0.2 percent of net generation, 1.4826 times the median absolute change between full years). Holds in more than one year: 11 of the 11 full years after 2014 lie above 2014's value. Survives a change of window: from 2015 to 2025 the change is 1.8, from 2014 to 2024 it is 1.7. Sample large enough: 2014 holds 12 and 2025 holds 12 observations; the floor is 11. Half the change remains without the first year: from 2015 to 2025 the change is 1.8, 96.0 percent of the change from 2014. At least one typical yearly move: the change is 7.96 typical yearly moves (0.2 percent of net generation a year, the median move between full years); the floor is 1.

**Its limits.** An estimate EIA models from capacity, not a metered figure, and set against a total that does not include it.

**Reproduce.** `python small-solar-ratio-state-dpv-us.reproduce.py <the table's CSV>` and `do small-solar-ratio-state-dpv-us.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
