# France's grid: solar power: France

Draft `scan-deep-0d557825aa45` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The mean solar power in France over the year was 3,712 MW in 2025, against 1,419 MW in 2020, the first full year the ERW holds.

![France's grid: solar power, France](fr-mean-solar-fr.png)

**The figure by full year** (MW): 2020: 1,419, 2021: 1,595, 2022: 2,160, 2023: 2,535, 2024: 2,788, 2025: 3,712.

**The tables and rows.** `rte_eco2mix_france_halfhourly`; the rows for France, region key `fr` (the card's `hunt.region`), years 2020 to 2025. The yearly values: `fr-mean-solar-fr.csv`.

**Its strength.** The change is 4.12 typical yearly moves (a typical move is 557 MW, 1.4826 times the median absolute change between full years). Holds in more than one year: 5 of the 5 full years after 2020 lie above 2020's value. Survives a change of window: from 2021 to 2025 the change is 2,117, from 2020 to 2024 it is 1,369. Sample large enough: 2020 holds 17,564 and 2025 holds 17,515 observations; the floor is 15,000. Half the change remains without the first year: from 2021 to 2025 the change is 2,117, 92.3 percent of the change from 2020. At least one typical yearly move: the change is 4.12 typical yearly moves (557 MW a year, the median move between full years); the floor is 1.

**Its limits.** RTE's eCO2mix national data, final for past years and consolidated or real-time for the latest; mainland France; a mean over the half-hours held.

**Reproduce.** `python fr-mean-solar-fr.reproduce.py <the table's CSV>` and `do fr-mean-solar-fr.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
