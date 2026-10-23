# Europe's renewable and waste electricity capacity by country and technology, a year from 1990 (Eurostat, nrg_inf_epcrw)

Energy Research Warehouse (ERW), method note written in session 2129 (chain 079) for a table first written on 23 October 2026 (session 2123, `archive/sessions/SESSION_2123_REPORT.md`).

Tables: `eurostat_renewable_capacity_annual`

## Publisher and address

Eurostat, "Electricity production capacities for renewables and wastes" (`nrg_inf_epcrw`), page `https://ec.europa.eu/eurostat/databrowser/view/nrg_inf_epcrw/default/table`. Read through Eurostat's SDMX 2.1 dissemination API (no key): the data set as SDMX-CSV, `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_inf_epcrw?format=SDMX-CSV&compressed=false` (4,481,272 bytes, 50,771 observations), and the SIEC codelist for the English names, `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/SIEC`. Source id `eurostat:nrg_inf_epcrw`. Both files are saved under `warehouse/raw/eurostat_res_capacity/`.

Connector: `warehouse/connectors/eurostat_res_capacity.py` (session 2123): `[--offline] [--out-dir DIR]`, two requests. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. `coverage.csv` gives the sector power.

## Vintage and revision

One run, `20261023T225654Z`, offline from the files retrieved at 2026-10-23T22:50:58Z; header: "Eurostat's last update 09/10/26 23:00:00" (9 October 2026). Every row carries that `retrieved_at`; `vintage` is empty. A later run replaces rows by their key and keeps rows it does not restate.

## Shape and variables

Series, 49,313 rows. `entity` `eurostat_epcrw:<Eurostat geo code>:<SIEC code>`; `variable` net_capacity (Eurostat's CAP_NET_ELC, 36,400 rows), net_capacity_ac (CAP_NET_ELC_AC, 6,457) or net_capacity_dc (CAP_NET_ELC_DC, 6,456); `unit` MW; `freq` P1Y; `ts_utc` the year's 1 January, 1990 to 2024 (35 years); `geo` the ISO alpha-2 code (Eurostat's EL written GR), blank for the aggregates EU27_2020 and EA21; `node` the SIEC code's English name; `x_geo_code`, `x_siec`, `x_plant_tec`, `x_flag` and `x_conf_status` as Eurostat gives them (the last two empty in every row); `market` and `vintage` empty.

- 39 countries: the 27 member states, Iceland, Liechtenstein and Norway, and Albania, Bosnia and Herzegovina, Georgia, Moldova, Montenegro, North Macedonia, Serbia, Turkey and Ukraine; and Eurostat's aggregates EU27_2020 and EA21.
- 34 SIEC codes: solid biofuels (R5100), pure biogasoline, pure biodiesels, other liquid biofuels, biogases; hydro (RA100) and pure, run-of-river, mixed and pumped hydro; geothermal; wind (RA300), on shore, off shore; solar (RA400), solar thermal (RA410), solar photovoltaic (RA420) and 13 size and mounting classes of it; tide, wave, ocean; waste (W6000), industrial and municipal waste.
- The AC and DC ratings occur only for solar photovoltaic and its classes (11 codes), in 38 countries and EA21 (not in Ukraine or EU27_2020).
- 32,873 rows are zero (Eurostat's zeros, kept); no value is negative.

## Placing values in time

Eurostat's `TIME_PERIOD` is a year; `ts_utc` is that year's 1 January, UTC. The capacity is Eurostat's net maximum capacity for the year as each country reports it.

## What is and is not filled

- Kept: the EU's member states, EFTA's and the official candidate countries in Eurostat's file, and its aggregates. Left out, by Eurostat's terms for commercial reuse: the United Kingdom and Kosovo (1,458 observations).
- Every observation kept has a value (the file holds no blank value): the 49,313 rows are the 50,771 observations less the 1,458 left out.
- Values as published, zeros kept; nothing is filled, summed or converted. A header not Eurostat's, a unit not MW, a frequency not annual, a value that is not a number or a key twice stops the run.

## License

Header: "License: public with acknowledgement (Eurostat's copyright notice, https://ec.europa.eu/eurostat/web/main/help/copyright-notice). Cite: Eurostat, nrg_inf_epcrw. Eurostat bears no responsibility for this reshaping (the rows filtered by country and renamed, the values unchanged)." `license_verdicts.csv` records Eurostat, read 244: "may be public" for public and for commercial use. `docs/licenses.md`: "may be public", flag public, ERW verdict public.

## Checks (session 2129)

The figures in this note were computed from the rows of `warehouse/output/eurostat_renewable_capacity_annual.csv`, read past its 11 header lines, and from the saved SDMX-CSV (scripts in `runs/c079/s2129/`).

- 49,313 rows, `ts_utc` from 1990-01-01T00:00:00Z to 2024-01-01T00:00:00Z, as the header states. No (entity, variable, ts_utc) twice.
- Session 2123's cross-check (`runs/c079/s2123/cross.py`), run again: its output is identical to the saved `cross.out`.
  - EU27_2020 against the sum of the 27 member states, net capacity, 2015 to 2024: wind, hydro and solid biofuels differ by 0.0 MW at most; solar photovoltaic by up to 2,281.2 MW.
  - Against IRENA (`irena_capacity_annual`, 2015 to 2024): wind is 1.000 of IRENA in all five countries; solar photovoltaic 1.000 in Germany (91,204 MW in 2024 in both), 0.974 to 1.052 in France (25,299 against 25,673 in 2024), 0.993 to 0.999 in Spain, 1.000 to 1.014 in Italy, 1.000 to 1.100 in Poland. Computed again to the MW: wind differs by at most 0.005 MW in every country and year, Germany's solar by 0.
- EU27_2020 solar photovoltaic less the members' sum, year by year: 761.0 (2013), 1,900.0 (2014), 2,108.1 (2015: 85,344.1 against 83,236.0), 2,223.0, 2,281.2 (2017), 1,516.4, 1,557.4, 186.6 (2020), and 0.0 from 2021 to 2024. For wind, hydro and solid biofuels the difference is 0.0 in every year from 2010 to 2024.
- Of the 6,457 AC rows, 6,182 have a net capacity beside them; the net equals the AC rating in 5,776 and the DC rating in 4,760.

## Where the description and the data disagree

1. **EFTA and the aggregates, in the code and in the docstring.** The docstring names EFTA as "Iceland, Liechtenstein, Norway" and keeps "the two EU aggregates"; the code's lists also keep Switzerland (CH) and the aggregates EA20 and EA19. None of the three is in Eurostat's file (its geo codes are the 41 kept and UK and XK), so the data are not affected, but a future file that held them would be kept without the docstring saying so.

## The session report against the table

Every figure of `SESSION_2123_REPORT.md` checked against the table, the saved files and the rerun cross-check holds: 49,313 rows, 1990 to 2024, 39 countries and the two aggregates, 34 SIEC codes, Eurostat's last update of 9 October 2026, the UK and Kosovo left out, the 4.5 MB file of 50,771 observations, wind the same to the MW in the five countries, Germany's solar the same (91,204 MW in 2024), France's 25,299 against 25,673, ratios of 0.974 to 1.100, the EU27 total equal to its members for wind, hydro and solid biofuels and for solar from 2021, and 0.2 to 2.3 GW above them for solar from 2015 to 2020 (85,344 against 83,236 in 2015). The report's reason for that gap (an aggregate not recomputed after a revision) is not testable from the table. None found that does not hold.

Acted on in session 2129: the docstring now names Switzerland among EFTA's members and the euro area aggregates the code keeps; the data are unchanged (the file holds neither).

## What it does not hold

- Fossil and nuclear capacity, generation, the United Kingdom, Kosovo and countries outside the EU, EFTA and the candidates.
- Any total made here: EU27_2020 and EA21 are Eurostat's own.
