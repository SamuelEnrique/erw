# The EU's energy import origin concentration by fuel, 2015 to 2024 (Eurostat's nrg_ind_ioc)

Energy Research Warehouse (ERW), method note written in session 2829 (chain 144) for a table first written on 26 October 2026 (session 2827).

Tables: `eurostat_import_concentration_annual`

## Publisher and address

Eurostat (the Statistical Office of the European Union), "Energy import origin concentration index by fuel" (nrg_ind_ioc, `https://ec.europa.eu/eurostat/databrowser/view/nrg_ind_ioc/default/table`). The table reads two files from Eurostat's SDMX 2.1 dissemination API, with no key:
- the whole dataset, `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_ioc?format=SDMX-CSV&compressed=false`;
- the SIEC codelist, for the fuels' names.

Source id `eurostat:nrg_ind_ioc`. Connector: `warehouse/connectors/eurostat_import_concentration.py` (session 2827), whose raw store is `warehouse/raw/eurostat_import_concentration/`. ec.europa.eu's robots file leaves `/eurostat/api/dissemination/` open and names no Claude agent (read 1648).

## Vintage and revision

Written by run `20261026T070046Z` (the write under the lock, offline), which read the file retrieved at 2026-10-26T06:59:06Z. Eurostat's last update, as the file gives it (no time zone), is 15/07/26 23:00:00.

## Shape and variables

Series, 6,497 rows, the 27 EU members, 43 fuels, 2015 to 2024:
- `entity` `eurostat_ioc:<geo>:<SIEC code>`. The fuels are the total, electricity (E7000), natural gas (G3000), crude oil, natural gas liquids and the oil products, coal and its products, peat, heat, and the liquid biofuels.
- `variable` `import_origin_concentration`; `unit` index: 0 for imports spread over many origins, 1 for one origin.
- `ts_utc` the year's 1 January; `freq` P1Y; `geo` ISO alpha-2 (EL is GR); `x_siec`, `x_flag` and `x_conf_status`.
- Sector `power;gas;oil;coal`.

**Figures:**

| Country | Fuel | 2020 | 2024 |
|---|---|---|---|
| Germany | natural gas | 0.4944 | 0.3199 |
| Italy | natural gas | 0.2678 | 0.2194 |
| Poland | natural gas | 0.3650 | 0.3229 |
| Poland | electricity | | 0.4430 |
| Germany | electricity | | 0.3065 |

## Reading the source

- 1,034 values of 1 (one origin) are kept. There are no zeros and no blanks. Every value lies between 0 and 1, which stops the run otherwise. Nothing is filled.
- The run also stops, asking nothing, while Eurostat is paused, and on:
  - a header not Eurostat's;
  - a frequency, unit or fuel not expected;
  - a value not a number;
  - a period not a year;
  - a key given twice.

## License

Public with acknowledgement: Eurostat's copyright notice, the verdict on record (read 280, session 2123). Cite: Eurostat, nrg_ind_ioc. In the release package; held from the live set.

## Cross-check

Against `eurostat_gas_import_origin_annual` (session 2821), 2020:
- where one partner is all of a member's gas (Czechia and Latvia, Russia at 100 per cent), the gas index is 1.0;
- Germany's 0.4944 sits with Russia at 68.66 per cent and Norway at 23.79.
