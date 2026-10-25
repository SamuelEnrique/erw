# European renewable energy shares, overall and in electricity, heating and cooling and transport, 2004 to 2025 (Eurostat's nrg_ind_ren)

Energy Research Warehouse (ERW), method note written in session 2759 (chain 139) for a table first written on 25 October 2026 (session 2762).

Tables: `eurostat_renewable_shares_annual`

## Publisher and address

Eurostat (the Statistical Office of the European Union), "Share of energy from renewable sources" (nrg_ind_ren, `https://ec.europa.eu/eurostat/databrowser/view/nrg_ind_ren/default/table`), the results of the SHARES tool under the Renewable Energy Directive. The table reads two files from Eurostat's SDMX 2.1 dissemination API, with no key:
- the whole dataset, every key: `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_ren/A...?format=SDMX-CSV&compressed=false`;
- the NRG_BAL codelist, for the shares' names.

Source id `eurostat:nrg_ind_ren`. Connector: `warehouse/connectors/eurostat_renewable_shares.py` (session 2762), whose raw store is `warehouse/raw/eurostat_renewable_shares/`. ec.europa.eu's robots file leaves `/eurostat/api/dissemination/` open and names no Claude agent (read 1508).

## Vintage and revision

Written by run `20261025T223442Z` (the write under the lock, offline), which read the file retrieved at 2026-10-25T22:32:49Z; Eurostat's last update, as the file gives it (no time zone), 15/09/26 23:00:00. The latest years are provisional (63 values flagged p) and revised the next year.

## Shape and variables

Series, 3,095 rows, 37 areas (`entity` `eurostat_renewable_shares:<geo>`), six variables, 2004 to 2025, in pct (per cent of the sector's gross final consumption, as Eurostat computes it under the directive: hydro and wind output normalised, multipliers in transport):
- `renewable_share_overall` (REN), `renewable_share_electricity` (REN_ELC), `renewable_share_heating_cooling` (REN_HEAT_CL), `renewable_share_transport` (REN_TRA);
- two newer items: `renewable_waste_heat_share_district_heating_cooling` (REN_WHC_DHEAT_DCL, 32 rows) and `waste_heat_share_heating_cooling` (REN_HEAT_CL_WHC, 28 rows).

`ts_utc` the year's 1 January; `freq` P1Y; `geo` ISO alpha-2 (Eurostat's EL is GR), blank for EU27_2020; `node` "<geo> share, <the NRG_BAL name>"; `x_geo_code`, `x_nrg_bal`, `x_flag` and `x_conf_status` Eurostat's codes and flags.

**Figures:** the EU27's overall share was 9.61 per cent in 2004, 17.42 in 2014 and 25.24 in 2024.

Countries kept: as `eurostat_electricity_production_annual` keeps them; Kosovo is left out.

## Reading the source

- A header not Eurostat's; a unit other than PC, a frequency other than A, or a share not in the six; a value not a number or below 0; or a key given twice stops the run.
- **A share above 100 is kept** and counted in the header: 25 values, Norway's electricity in 18 years, Iceland's in 4 and Albania's in 3. There the normalised renewable output exceeds the sector's consumption.
- A blank has no row; 37 zeros are kept; nothing is filled.

## License

Public with acknowledgement: Eurostat's copyright notice, the verdict on record (read 280, session 2123). Cite: Eurostat, nrg_ind_ren. In the release package; held from the live set.

## Cross-check

The electricity share against `eurostat_electricity_production_annual`'s renewables (RA000) over its total (TOTAL), per cent. The directive divides normalised output by consumption, and production is not normalised, so the two agree only where trade is small:

| Area | Year | Production's renewables / total | Directive share (here) |
|---|---|---|---|
| EU27 | 2014 | 29.3 | 28.6 |
| EU27 | 2024 | 47.1 | 47.5 |
| Poland | 2024 | 30.5 | 30.4 |
| Norway | 2024 | 97.9 | 115.1 |
| Sweden | 2024 | 69.4 | 88.1 |
| Denmark | 2024 | 88.9 | 79.7 |
