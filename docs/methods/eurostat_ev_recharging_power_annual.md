# European EV recharging points by power category, 2019 to 2025 (Eurostat's road_if_rchevpow)

Energy Research Warehouse (ERW), method note written in session 2815 (chain 143) for a table first written on 26 October 2026 (session 2813).

Tables: `eurostat_ev_recharging_power_annual`

## Publisher and address

Eurostat (the Statistical Office of the European Union), "Recharging points for electric vehicles by power category" (road_if_rchevpow, `https://ec.europa.eu/eurostat/databrowser/view/road_if_rchevpow/default/table`). The table reads the whole dataset from Eurostat's SDMX 2.1 dissemination API, with no key: `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/road_if_rchevpow?format=SDMX-CSV&compressed=false`.

Source id `eurostat:road_if_rchevpow`. Connector: `warehouse/connectors/eurostat_ev_recharging_power.py` (session 2813), whose raw store is `warehouse/raw/eurostat_ev_recharging_power/`. ec.europa.eu's robots file leaves `/eurostat/api/dissemination/` open and names no Claude agent (read 1622). The bands' names are the POWER codelist's (read 1624), written in the connector in ASCII. Its companion is `eurostat_ev_recharging_annual` (session 2804): points, stations and pools.

## Vintage and revision

Written by run `20261026T052353Z`, which read the file retrieved at 2026-10-26T05:21:38Z. Eurostat's last update, as the file gives it (no time zone), is 13/10/26 23:00:00. Each figure is Eurostat's for the year it names, written at the year's 1 January; the ERW does not read it as a stock on that day.

## Shape and variables

Series, 1,171 rows, 33 areas, 2019 to 2025:
- `entity` `eurostat_ev_power:<geo>:<POWER code>`. The codes are TOTAL, AC, DC, and the bands:
  - AC: AC_KW_LT7P4 (below 7.4 kW, slow, single-phase), AC_KW_LE7P4-LE22 (7.4 to 22 kW, medium-speed, three-phase), AC_KW_GT22 (above 22 kW, fast, three-phase);
  - DC: DC_KW_LT50 (below 50 kW, slow), DC_KW_LE50-LT150 (50 to 150 kW, fast), DC_KW_LE150-LT350 (150 to 350 kW, ultra-fast level 1), DC_KW_GE350 (350 kW and above, ultra-fast level 2).
- `variable` `recharging_points`; `unit` count (Eurostat's NR).
- `ts_utc` the year's 1 January; `freq` P1Y; `geo` ISO alpha-2 (EL is GR); `x_power`, `x_flag` (`i`: see Eurostat's metadata) and `x_conf_status`.

**Figures, 2025:**
- The Netherlands' 209,513 points were 202,611 AC (200,189 of them 7.4 to 22 kW) and 6,902 DC (684 of them 350 kW and above).
- France had the most points at 350 kW and above, 4,278.

## Reading the source

- **The parts against their whole, exactly,** in every country year that gives them:
  - the total against AC plus DC: 118 of 138;
  - AC against its three bands: 87 of 91;
  - DC against its four bands: 85 of 89.

  The others are kept as published and listed in the run log. Among them, France's parts are 986 to 1,246 above its total each year from 2021 to 2025, and Germany's total is 54 to 159 above its parts in 2019 to 2023.
- 98 zeros are kept. The United Kingdom is not in the file. Nothing is filled.
- The run stops, asking nothing, while Eurostat is paused. It also stops on:
  - a header not Eurostat's;
  - a frequency, unit or power code not expected;
  - a value not a number, or negative;
  - a period not a year;
  - a key given twice.

## License

Public with acknowledgement: Eurostat's copyright notice, the verdict on record (read 280, session 2123). Cite: Eurostat, road_if_rchevpow. In the release package; held from the live set.

## Cross-check

Against `eurostat_ev_recharging_annual`'s `recharging_points` (road_if_rchev): **this table's total equals it in all 157 country years both give,** the Netherlands' 209,513 in 2025 among them.
