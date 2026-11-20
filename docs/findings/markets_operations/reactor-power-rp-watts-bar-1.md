# How hard reactors run: the Watts Bar 1 reactor

Draft `scan-deep-3ee6d8b07b0c` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The mean daily power level of the Watts Bar 1 reactor was 68.5 percent of full power in 2025, against 90.1 percent of full power in 2020, the first full year the ERW holds.

![How hard reactors run, the Watts Bar 1 reactor](reactor-power-rp-watts-bar-1.png)

**The figure by full year** (percent of full power): 2020: 90.1, 2021: 89.6, 2022: 99.4, 2023: 91.6, 2024: 84.6, 2025: 68.5.

**The tables and rows.** `nrc_reactor_status`; the rows for the Watts Bar 1 reactor, region key `rp_watts_bar_1` (the card's `hunt.region`), years 2020 to 2025. The yearly values: `reactor-power-rp-watts-bar-1.csv`.

**Its strength.** The change is 1.88 typical yearly moves (a typical move is 11.5 percent of full power, 1.4826 times the median absolute change between full years). Holds in more than one year: 3 of the 5 full years after 2020 lie below 2020's value. Survives a change of window: from 2021 to 2025 the change is -21.1, from 2020 to 2024 it is -5.4. Sample large enough: 2020 holds 366 and 2025 holds 365 observations; the floor is 330. Half the change remains without the first year: from 2021 to 2025 the change is -21.1, 97.9 percent of the change from 2020. At least one typical yearly move: the change is 1.88 typical yearly moves (11.5 percent of full power a year, the median move between full years); the floor is 1.

**Its limits.** The NRC's daily power reactor status as reported each morning; a reactor's day at 0 percent counts, a shut reactor leaves the fleet.

**Reproduce.** `python reactor-power-rp-watts-bar-1.reproduce.py <the table's CSV>` and `do reactor-power-rp-watts-bar-1.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
