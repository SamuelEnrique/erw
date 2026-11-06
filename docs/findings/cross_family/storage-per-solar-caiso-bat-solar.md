# Storage beside solar: CAISO

Draft `scan-deep-c41ae534ead9` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The battery energy capacity in CAISO per MW of solar in operation at the year's end was 2.17 MWh per MW of solar in 2025, against 0.00 MWh per MW of solar in 2015, the first year the ERW's fleet table holds.

![Storage beside solar, CAISO](storage-per-solar-caiso-bat-solar.png)

**The figure by full year** (MWh per MW of solar): 2015: 0.00, 2016: 0.02, 2017: 0.03, 2018: 0.04, 2019: 0.04, 2020: 0.11, 2021: 0.56, 2022: 0.99, 2023: 1.36, 2024: 1.77, 2025: 2.17.

**The tables and rows.** `storage_buildout_monthly`; the rows for CAISO, region key `caiso_bat_solar` (the card's `hunt.region`), years 2015 to 2025. The yearly values: `storage-per-solar-caiso-bat-solar.csv`.

**Its strength.** The change is 6.69 typical yearly moves (a typical move is 0.32 MWh per MW of solar, 1.4826 times the median absolute change between full years). Holds in more than one year: 10 of the 10 full years after 2015 lie above 2015's value. Survives a change of window: from 2016 to 2025 the change is 2.15, from 2015 to 2024 it is 1.76. Sample large enough: 2015 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2016 to 2025 the change is 2.15, 99.5 percent of the change from 2015. At least one typical yearly move: the change is 6.69 typical yearly moves (0.32 MWh per MW of solar a year, the median move between full years); the floor is 1.

**Its limits.** EIA-860M's operating batteries and solar as the ERW counts them each month; batteries that report no MWh are left out.

**Reproduce.** `python storage-per-solar-caiso-bat-solar.reproduce.py <the table's CSV>` and `do storage-per-solar-caiso-bat-solar.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
