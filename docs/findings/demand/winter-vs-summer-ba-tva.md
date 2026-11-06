# Winter's top days against summer's: the Tennessee Valley Authority

Draft `scan-deep-9e2c143415fc` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The mean of the five highest winter days of demand in the Tennessee Valley Authority, against its five highest summer days, was 113.9 percent of the summer top days in 2025, against 101.2 percent of the summer top days in 2019, the first full year the ERW holds.

![Winter's top days against summer's, the Tennessee Valley Authority](winter-vs-summer-ba-tva.png)

**The figure by full year** (percent of the summer top days): 2019: 101.2, 2020: 101.8, 2021: 103.1, 2022: 107.7, 2023: 89.4, 2024: 119.8, 2025: 113.9.

**The tables and rows.** `eia930_daily_demand`; the rows for the Tennessee Valley Authority, region key `ba_tva` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `winter-vs-summer-ba-tva.csv`.

**Its strength.** The change is 1.63 typical yearly moves (a typical move is 7.8 percent of the summer top days, 1.4826 times the median absolute change between full years). Holds in more than one year: 5 of the 6 full years after 2019 lie above 2019's value. Survives a change of window: from 2020 to 2025 the change is 12.0, from 2019 to 2024 it is 18.6. Sample large enough: 2019 holds 365 and 2025 holds 365 observations; the floor is 330. Half the change remains without the first year: from 2020 to 2025 the change is 12.0, 94.8 percent of the change from 2019. At least one typical yearly move: the change is 1.63 typical yearly moves (7.8 percent of the summer top days a year, the median move between full years); the floor is 1.

**Its limits.** Five days a season: one cold spell or one heat wave can carry a year, and the year's December is not the same winter as its January.

**Reproduce.** `python winter-vs-summer-ba-tva.reproduce.py <the table's CSV>` and `do winter-vs-summer-ba-tva.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
