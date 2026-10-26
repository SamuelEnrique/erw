# European electric vehicle recharging infrastructure, 2019 to 2025 (Eurostat's road_if_rchev)

Energy Research Warehouse (ERW), method note written in session 2801 (chain 142) for a table first written on 26 October 2026 (session 2804).

Tables: `eurostat_ev_recharging_annual`

## Publisher and address

Eurostat (the Statistical Office of the European Union), "Electric vehicle recharging pools, stations and points and their power output" (road_if_rchev, `https://ec.europa.eu/eurostat/databrowser/view/road_if_rchev/default/table`). The table reads two files from Eurostat's SDMX 2.1 dissemination API, with no key:
- the whole dataset, `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/road_if_rchev?format=SDMX-CSV&compressed=false`;
- the TRA_INFR codelist, for the recharging types' names.

Source id `eurostat:road_if_rchev`. Connector: `warehouse/connectors/eurostat_ev_recharging.py` (session 2804), whose raw store is `warehouse/raw/eurostat_ev_recharging/`. ec.europa.eu's robots file leaves `/eurostat/api/dissemination/` open and names no Claude agent (read 1599). The US counterpart is `afdc_ev_charging_state_annual` (session 2155).

## Vintage and revision

Written by run `20261026T033228Z` (the write under the lock, offline), which read the file retrieved at 2026-10-26T03:30:12Z. Eurostat's last update, as the file gives it (no time zone), is 13/10/26 23:00:00. Each figure is Eurostat's for the year it names. The ERW writes the year as its 1 January, as for its other annual tables, and does not read the figure as a stock on that day.

## Shape and variables

Series, 465 rows, 33 areas, 2019 to 2025:
- `entity` `eurostat_ev_recharging:<geo>`.
- `variable`:
  - `recharging_points`, `recharging_stations`, `recharging_pools` and `heavy_duty_pools` (pools dedicated to heavy-duty vehicles), each in `unit` count (Eurostat's NR);
  - `recharging_pools_power` and `heavy_duty_pools_power`, the pools' power output, in `unit` MW (Eurostat's kW divided by 1,000).
- `ts_utc` the year's 1 January; `freq` P1Y; `geo` ISO alpha-2 (Eurostat's EL is GR).
- `node` "<geo> <the TRA_INFR name>, <number or power output>"; `x_geo_code`, `x_tra_infr`, `x_unit`, `x_flag` and `x_conf_status` Eurostat's codes and flags.

Countries report from different years and not every measure:
- recharging points by 9 countries in 2019 and 31 in 2025, 33 in all;
- pools' power by 27;
- pools by 21;
- stations by 20;
- the heavy-duty items by 9.

Germany's figures run to 2024, France's from 2021.

**Figures:**

| Country | Variable | Year | Value |
|---|---|---|---|
| the Netherlands | recharging points | 2025 | 209,513 |
| France | recharging points | 2025 | 185,501 |
| Germany | recharging points | 2024 | 163,410 |
| Belgium | recharging points | 2024 | 111,500 |
| Belgium | recharging points | 2025 | 106,500 |
| Germany | recharging pools | 2024 | 52,020 |
| Germany | pools' power output, MW | 2024 | 6,211.711 |

Germany's pools averaged 119 kW in 2024. Belgium's fall from 2024 to 2025 is as published.

## Reading the source

- **36 observations carry Eurostat's flag `i`** (see Eurostat's metadata), kept in `x_flag`, among them every recharging point figure of Bulgaria, Denmark, Spain, Poland and Romania.
- **29 zeros are kept as Eurostat prints them,** all of them heavy-duty items: Estonia's before 2023, North Macedonia's, Malta's, and Greece's heavy-duty power in 2023. 2 blanks have no row. Nothing is filled.
- Countries kept: the EU's members, EFTA's and the official candidates; the United Kingdom is left out.
- The run stops, asking nothing, while Eurostat is paused. It also stops, filling nothing, on:
  - a header not Eurostat's;
  - a frequency not A;
  - a recharging type in a unit it is not read in;
  - a codelist without the four types;
  - a value not a number, or negative;
  - a period not a year;
  - a key given twice.

## License

Public with acknowledgement: Eurostat's copyright notice, the verdict on record (read 280, session 2123). Cite: Eurostat, road_if_rchev. In the release package; held from the live set.

## Cross-check

The ERW holds no other European recharging count. Points and stations are read against each other: in every country year that gives both, a station holds one or more points. The note's check script counts the country years where this fails.
