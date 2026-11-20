# What commercial customers pay: Northern Indiana Pub Serv Co in IN

Draft `scan-deep-7ea1d0afa8f1` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The average price of electricity to commercial customers of Northern Indiana Pub Serv Co in IN (revenue over sales, nominal) was 192.4 USD per MWh in 2025, against 132.6 USD per MWh in 2017, the first full year the ERW holds.

![What commercial customers pay, Northern Indiana Pub Serv Co in IN](util-commercial-price-u861-13756-in.png)

**The figure by full year** (USD per MWh): 2017: 132.6, 2018: 128.6, 2019: 129.9, 2020: 135.8, 2021: 145.1, 2022: 154.7, 2023: 160.5, 2024: 168.3, 2025: 192.4.

**The tables and rows.** `eia861m_utility_sales_monthly`; the rows for Northern Indiana Pub Serv Co in IN, region key `u861_13756_in` (the card's `hunt.region`), years 2017 to 2025. The yearly values: `util-commercial-price-u861-13756-in.csv`.

**Its strength.** The change is 5.89 typical yearly moves (a typical move is 10.2 USD per MWh, 1.4826 times the median absolute change between full years). Holds in more than one year: 6 of the 8 full years after 2017 lie above 2017's value. Survives a change of window: from 2018 to 2025 the change is 63.8, from 2017 to 2024 it is 35.7. Sample large enough: 2017 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2018 to 2025 the change is 63.8, 106.7 percent of the change from 2017. At least one typical yearly move: the change is 5.89 typical yearly moves (10.2 USD per MWh a year, the median move between full years); the floor is 1.

**Its limits.** EIA Form 861M as the utility filed it, in one state, its sales to the customers it serves; states with retail or community choice are not read; a utility that merged or changed its EIA number starts again under its new number; the latest year's months may be preliminary. Nominal dollars.

**Reproduce.** `python util-commercial-price-u861-13756-in.reproduce.py <the table's CSV>` and `do util-commercial-price-u861-13756-in.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
