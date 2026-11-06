# Europe's non-household electricity by consumption band, 2017 to 2025 (Eurostat's nrg_pc_205_v)

Energy Research Warehouse (ERW), method note written in session 2829 (chain 144) for a table first written on 26 October 2026 (session 2820).

Tables: `eurostat_nonhousehold_bands_annual`

## Publisher and address

Eurostat (the Statistical Office of the European Union), "Non-household consumption volumes of electricity by consumption bands" (nrg_pc_205_v, `https://ec.europa.eu/eurostat/databrowser/view/nrg_pc_205_v/default/table`). The table reads the whole dataset from Eurostat's SDMX 2.1 dissemination API, with no key: `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_pc_205_v?format=SDMX-CSV&compressed=false`.

Source id `eurostat:nrg_pc_205_v`. Connector: `warehouse/connectors/eurostat_nonhousehold_bands.py` (session 2820), whose raw store is `warehouse/raw/eurostat_nonhousehold_bands/`. ec.europa.eu's robots file leaves `/eurostat/api/dissemination/` open and names no Claude agent (read 1631). The bands' names are the NRG_CONS codelist's (read 1634), written in ASCII. Session 2820 took it in place of MAVIR, whose robots files close every path (reads 1629 and 1630).

## Vintage and revision

Written by run `20261026T063158Z` (the write under the lock, offline), which read the file retrieved at 2026-10-26T06:30:20Z. Eurostat's last update, as the file gives it (no time zone), is 16/10/26 11:00:00.

## Shape and variables

Series, 2,013 rows, 37 countries, 2017 to 2025:
- `entity` `eurostat_nonhh_bands:<geo>:<band>`. The bands are MWH_LT20 (band IA, under 20 MWh a year), MWH20-499 (IB), MWH500-1999 (IC), MWH2000-19999 (ID), MWH20000-69999 (IE), MWH70000-149999 (IF) and MWH_GE150000 (IG, 150,000 MWh and over).
- `variable` `consumption_share`; `unit` pct: the band's share of the country's non-household consumption.
- `ts_utc` the year's 1 January; `freq` P1Y; `geo` ISO alpha-2 (EL is GR); `x_nrg_cons`, `x_flag` and `x_conf_status`.

These are the bands of Eurostat's non-household electricity prices (nrg_pc_205, in EUR, not taken): the volumes say how much of a country's use each price band stands for. Eurostat's EU and euro-area rows are blank in the file.

**Figures, 2025, band IG (150,000 MWh and over):** Norway 50.5747 per cent, Ireland 22.523, Germany 22.1774, France 16.4668, Poland 8.6398.

## Reading the source

- **The seven bands make 100** within 0.5 points in all 216 country years that give all seven, within 0.01 in each. A case off would be counted and kept.
- 56 zeros are kept. 249 blanks have no row. Kosovo is left out. Nothing is filled.
- The run stops, asking nothing, while Eurostat is paused. It also stops on:
  - a header not Eurostat's;
  - a frequency, product, unit or band not expected;
  - a value not a number, or outside 0 to 100;
  - a period not a year;
  - a key given twice.

## License

Public with acknowledgement: Eurostat's copyright notice, the verdict on record (read 280, session 2123). Cite: Eurostat, nrg_pc_205_v. In the release package; held from the live set.

## Cross-check

No held table gives consumption by band, so the bands' sum to 100 is the check (above). The bands' total volume is not given, so the shares cannot be turned into MWh against `eurostat_electricity_consumption_annual`.
