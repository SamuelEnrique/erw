# The diversity index of the EU's energy supply, 1992 to 2024 (Eurostat's nrg_ind_di)

Energy Research Warehouse (ERW), method note written in session 2829 (chain 144) for a table first written on 26 October 2026 (session 2832).

Tables: `eurostat_supply_diversity_annual`

## Publisher and address

Eurostat (the Statistical Office of the European Union), "Diversity index of energy supply" (nrg_ind_di, `https://ec.europa.eu/eurostat/databrowser/view/nrg_ind_di/default/table`). The table reads the whole dataset from Eurostat's SDMX 2.1 dissemination API, with no key: `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_di?format=SDMX-CSV&compressed=false`.

Source id `eurostat:nrg_ind_di`. Connector: `warehouse/connectors/eurostat_supply_diversity.py` (session 2832), whose raw store is `warehouse/raw/eurostat_supply_diversity/`. ec.europa.eu's robots file leaves `/eurostat/api/dissemination/` open and names no Claude agent (read 1650).

## Vintage and revision

Written by run `20261026T070515Z` (the write under the lock, offline), which read the file retrieved at 2026-10-26T07:04:02Z. Eurostat's last update, as the file gives it (no time zone), is 16/12/25 23:00:00.

## Shape and variables

Series, 891 rows, the 27 EU members, 1992 to 2024:
- `entity` `eurostat_supply_diversity:<geo>`; `variable` `supply_diversity_index`; `unit` index (Eurostat's INX), written as given.
- `ts_utc` the year's 1 January; `freq` P1Y; `geo` ISO alpha-2 (EL is GR).
- Sector `power;gas;oil;coal`.

**The file gives the index without its method.** The ERW reads no direction into it ("more diverse" or "less"); Eurostat's metadata for nrg_ind_di defines it.

**Figures, 2024:** the lowest values are Czechia 0.1166, Austria 0.1230 and Finland 0.1292; the highest are Lithuania 0.3599, Malta 0.3478 and Greece 0.3360.

## Reading the source

- Every value lies between 0 and 1 (0.1166 to 0.5504), which stops the run otherwise. There are no blanks. Nothing is filled.
- The run also stops, asking nothing, while Eurostat is paused, and on:
  - a header not Eurostat's;
  - a frequency or unit not expected;
  - a value not a number;
  - a period not a year;
  - a key given twice.

## License

Public with acknowledgement: Eurostat's copyright notice, the verdict on record (read 280, session 2123). Cite: Eurostat, nrg_ind_di. In the release package; held from the live set.

## Cross-check

No held table gives the same index. It sits beside `eurostat_import_dependency_annual` (how much is imported) and `eurostat_import_concentration_annual` (how concentrated the imports' origins are), but none is read from another.
