# Batteries against the peak: CAISO

Draft `scan-deep-8d4c08a1fc82` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The battery fleet of CAISO at the year's end, against the average GW of its ten highest days of demand, was 46.6 percent of peak-day demand in 2025, against 0.6 percent of peak-day demand in 2019, the first year both tables hold.

![Batteries against the peak, CAISO](battery-per-peak-caiso-bat-peak.png)

**The figure by full year** (percent of peak-day demand): 2019: 0.6, 2020: 1.5, 2021: 7.5, 2022: 13.4, 2023: 24.0, 2024: 32.8, 2025: 46.6.

**The tables and rows.** `storage_buildout_monthly`, `eia930_daily_demand`; the rows for CAISO, region key `caiso_bat_peak` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `battery-per-peak-caiso-bat-peak.csv`.

**Its strength.** The change is 4.20 typical yearly moves (a typical move is 11.0 percent of peak-day demand, 1.4826 times the median absolute change between full years). Holds in more than one year: 6 of the 6 full years after 2019 lie above 2019's value. Survives a change of window: from 2020 to 2025 the change is 45.1, from 2019 to 2024 it is 32.3. Sample large enough: 2019 holds 365 and 2025 holds 365 observations; the floor is 330. Half the change remains without the first year: from 2020 to 2025 the change is 45.1, 97.8 percent of the change from 2019. At least one typical yearly move: the change is 4.20 typical yearly moves (11.0 percent of peak-day demand a year, the median move between full years); the floor is 1.

**Its limits.** Two families in one figure: EIA-860M's operating batteries (the ERW's monthly fleet) over EIA-930's daily demand; a battery's MW is its discharge rate, not its energy, and a peak day's average GW is below its peak hour.

**Reproduce.** `python battery-per-peak-caiso-bat-peak.reproduce.py <the table's CSV>` and `do battery-per-peak-caiso-bat-peak.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
