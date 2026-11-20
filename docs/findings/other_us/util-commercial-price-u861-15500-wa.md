# What commercial customers pay: Puget Sound Energy Inc in WA

Draft `scan-deep-78d7e812ebe9` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The average price of electricity to commercial customers of Puget Sound Energy Inc in WA (revenue over sales, nominal) was 156.6 USD per MWh in 2025, against 99.4 USD per MWh in 2017, the first full year the ERW holds.

![What commercial customers pay, Puget Sound Energy Inc in WA](util-commercial-price-u861-15500-wa.png)

**The figure by full year** (USD per MWh): 2017: 99.4, 2018: 100.5, 2019: 97.9, 2020: 101.1, 2021: 108.6, 2022: 114.3, 2023: 125.5, 2024: 148.4, 2025: 156.6.

**The tables and rows.** `eia861m_utility_sales_monthly`; the rows for Puget Sound Energy Inc in WA, region key `u861_15500_wa` (the card's `hunt.region`), years 2017 to 2025. The yearly values: `util-commercial-price-u861-15500-wa.csv`.

**Its strength.** The change is 5.85 typical yearly moves (a typical move is 9.8 USD per MWh, 1.4826 times the median absolute change between full years). Holds in more than one year: 7 of the 8 full years after 2017 lie above 2017's value. Survives a change of window: from 2018 to 2025 the change is 56.1, from 2017 to 2024 it is 48.9. Sample large enough: 2017 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2018 to 2025 the change is 56.1, 98.1 percent of the change from 2017. At least one typical yearly move: the change is 5.85 typical yearly moves (9.8 USD per MWh a year, the median move between full years); the floor is 1.

**Its limits.** EIA Form 861M as the utility filed it, in one state, its sales to the customers it serves; states with retail or community choice are not read; a utility that merged or changed its EIA number starts again under its new number; the latest year's months may be preliminary. Nominal dollars.

**Reproduce.** `python util-commercial-price-u861-15500-wa.reproduce.py <the table's CSV>` and `do util-commercial-price-u861-15500-wa.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
