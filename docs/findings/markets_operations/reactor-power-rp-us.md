# How hard reactors run: the US reactor fleet

Draft `scan-deep-6e90345db863` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The mean daily power level of the US reactor fleet was 91.1 percent of full power in 2025, against 89.4 percent of full power in 2020, the first full year the ERW holds.

![How hard reactors run, the US reactor fleet](reactor-power-rp-us.png)

**The figure by full year** (percent of full power): 2020: 89.4, 2021: 90.2, 2022: 91.3, 2023: 90.8, 2024: 90.8, 2025: 91.1.

**The tables and rows.** `nrc_reactor_status`; the rows for the US reactor fleet, region key `rp_us` (the card's `hunt.region`), years 2020 to 2025. The yearly values: `reactor-power-rp-us.csv`.

**Its strength.** The change is 2.26 typical yearly moves (a typical move is 0.7 percent of full power, 1.4826 times the median absolute change between full years). Holds in more than one year: 5 of the 5 full years after 2020 lie above 2020's value. Survives a change of window: from 2021 to 2025 the change is 0.9, from 2020 to 2024 it is 1.4. Sample large enough: 2020 holds 366 and 2025 holds 362 observations; the floor is 330. Half the change remains without the first year: from 2021 to 2025 the change is 0.9, 55.4 percent of the change from 2020. At least one typical yearly move: the change is 2.26 typical yearly moves (0.7 percent of full power a year, the median move between full years); the floor is 1.

**Its limits.** The NRC's daily power reactor status as reported each morning; a reactor's day at 0 percent counts, a shut reactor leaves the fleet.

**Reproduce.** `python reactor-power-rp-us.reproduce.py <the table's CSV>` and `do reactor-power-rp-us.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
