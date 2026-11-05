# Europe's nuclear fuel cycle facilities and nuclear heat, 2009 to 2024 (Eurostat's nrg_inf_nuc)

Energy Research Warehouse (ERW), method note written in session 2815 (chain 143) for a table first written on 26 October 2026 (session 2812).

Tables: `eurostat_nuclear_fuel_cycle_annual`

## Publisher and address

Eurostat (the Statistical Office of the European Union), "Nuclear energy facilities" (nrg_inf_nuc, `https://ec.europa.eu/eurostat/databrowser/view/nrg_inf_nuc/default/table`). The table reads two files from Eurostat's SDMX 2.1 dissemination API, with no key:
- the whole dataset, `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_inf_nuc?format=SDMX-CSV&compressed=false`;
- the PLANT_TEC codelist.

Source id `eurostat:nrg_inf_nuc`. Connector: `warehouse/connectors/eurostat_nuclear_facilities.py` (session 2812), whose raw store is `warehouse/raw/eurostat_nuclear_facilities/`. ec.europa.eu's robots file leaves `/eurostat/api/dissemination/` open and names no Claude agent (read 1620).

## Vintage and revision

Written by run `20261026T051746Z` (the write under the lock, offline), which read the file retrieved at 2026-10-26T05:15:23Z. Eurostat's last update, as the file gives it (no time zone), is 09/10/26 23:00:00.

## Shape and variables

Series, 4,247 rows, 40 areas, 8 items, 2009 to 2024:
- `entity` `eurostat_nuclear:<geo>`.
- `variable`:
  - `enrichment_capacity` (unit SWU, Eurostat's tSWU times 1,000);
  - `fresh_fuel_production` and `fresh_fuel_production_capacity`, `mox_fuel_production` and `mox_fuel_production_capacity`, `reprocessing_production` and `reprocessing_capacity` (uranium and plutonium), each in unit `t`, tonnes of heavy metal (Eurostat's THM);
  - `nuclear_heat_production` (unit MWh, Eurostat's ktoe times 11,630: a tonne of oil equivalent is 41.868 GJ, 11.63 MWh).
- `ts_utc` the year's 1 January; `freq` P1Y; `geo` ISO alpha-2 (EL is GR), blank for EU27_2020; `x_plant_tec` and `x_unit` Eurostat's codes; `x_flag` and `x_conf_status`.
- The sector is `power;uranium`, as the ERW's other nuclear tables.

**Figures, 2024:**
- Enrichment capacity: France 7,500,000 SWU, the Netherlands 5,000,000, Germany 3,500,000; the EU 16,000,000.
- France's fresh fuel production was 641 t of heavy metal, its MOX 82 t, its reprocessing 871 t.

France is the only country with reprocessing production in every year.

## Reading the source

- **Not written:** the annual average burnup of discharged fuel (BAA_IRRADF, GWd/tHM, 543 observations), a unit the ERW does not hold.
- Production against its plant's capacity, in 1,573 country-year-plant comparisons: none above.
- 3,610 zeros are kept (most countries have no fuel cycle plant). 31 blanks have no row. The United Kingdom, Kosovo and EA21 are left out.
- **France's 2024 nuclear heat (88,138 ktoe, flag p) is 2023's figure carried forward,** kept as published (below).
- The run stops, asking nothing, while Eurostat is paused. It also stops, filling nothing, on:
  - a header not Eurostat's;
  - an item or unit not expected, or an item in another unit;
  - a value not a number, or negative;
  - a period not a year;
  - a key given twice.

## License

Public with acknowledgement: Eurostat's copyright notice, the verdict on record (read 280, session 2123). Cite: Eurostat, nrg_inf_nuc. In the release package; held from the live set.

## Cross-check

Nuclear electricity over nuclear heat: `eurostat_electricity_production_annual`'s gross nuclear production (N900H) divided by this table's heat gives a plant's thermal efficiency. Over the 231 country years with heat above zero:
- **the median is 0.34** (5th to 95th percentile 0.33 to 0.37);
- France 2023: 338.2 TWh from 1,025.0 TWh of heat (0.33).

**France 2024: 380.5 TWh over the same 1,025.0 TWh (0.37),** because its 2024 heat repeats 2023's provisional figure.
