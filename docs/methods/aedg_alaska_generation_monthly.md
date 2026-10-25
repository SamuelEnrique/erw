# Alaska's electricity generation a month by service area and fuel, 2001 to 2021 (the Alaska Energy Data Gateway)

Energy Research Warehouse (ERW), method note written in session 2667 (chain 133) for a table first written on 25 October 2026 (session 2665).

Tables: `aedg_alaska_generation_monthly`

## Publisher and address

The Alaska Energy Data Gateway, run by the Alaska Center for Energy and Power (ACEP) at the University of Alaska Fairbanks, dataset "Monthly Electrical Generation By Community", version 3.0 (`https://akenergygateway.alaska.edu/explore/data/public_monthly_generation`). It is read whole as one JSON answer from `https://akenergygateway.alaska.edu/explore/data/public_monthly_generation/datasets/public_monthly_generation`, no key. Source id `aedg_ak:public_monthly_generation_v3`. Connector: `warehouse/connectors/aedg_alaska_generation.py` (session 2665), whose raw store is `warehouse/raw/aedg_ak/`.

The Gateway compiles the Alaska Energy Statistics workbooks, which draw on the Alaska Energy Authority's Power Cost Equalization (PCE) reports and on plants' reports to EIA. Its robots file closes `/search` to every reader, and `/` to GPTBot and some search engines' crawlers by name; the ERW's reader is not named (read 1367).

## Vintage and revision

Written by run `20261025T103939Z` (the write under the lock, offline), which read the answer retrieved at 2026-10-25T10:36:35Z (162,975 records). `vintage` is empty: the answer carries no date of its own. The dataset's page says it was published in 2026.

## Shape and variables

Series, 51,061 rows, 271 entities, each month from January 2001 to December 2021. `entity` `aedg:ak:<service area>:<fuel>`: the Gateway's `service_area_geom_id`, and its fuel type as a slug:
- `distillate_oil`, `residual_oil`, `waste_oil`, `jet_fuel`;
- `natural_gas`, `other_gas`, `landfill_gas`, `coal`;
- `hydro`, `wind`, `solar`;
- `wood_waste`, `agricultural_byproducts`, `other_biomass_liquids`;
- `storage` ("Electricity used for Energy Storage");
- `fuel_not_given`.

`variable` generation; `unit` MWh, as published; `ts_utc` the month's first day; `freq` P1M; `geo` US-AK; `node` the service area's first community in alphabetical order and how many others share its grid.

The 175 service areas make 5.81 TWh in 2001, 4.37 in 2011 and 5.12 in 2021. In 2021: natural gas 2.01, hydro 1.68, distillate oil 0.54, coal 0.50, waste oil 0.21, wind 0.14.

**Not all of Alaska.** EIA's state total in the ERW (`eia_state_generation_monthly`, `eia:generation:AK:ALL`) is 6.60 TWh for 2021 and 6.74 for 2001.

## Reading the source

- The run stops at once, asking nothing, while `aedg_ak` or akenergygateway.alaska.edu is paused.
- One request a run (about 38 MB), saved and reused unless `--fresh`; `--offline` asks nothing.
- **One row a service area, month and fuel.** The Gateway gives one record a community and reports each grid's generation for every community on it, so the figure repeats. The run keeps it once, and stops if a service area's communities disagree.
  - No plant set is under two service areas, so the rows can be summed without doubling a grid.
- **Kept as published:** 581 negative figures (net generation, and the storage row's own use), and 123 service-area months with the fuel left blank.
- **Not written:** records with no year (communities without data), and the PCE fuel price.
- The run stops for a count of records not the answer's total, fields not as above, a fuel not in the map, a year not of four digits, or a month not 1 to 12.

Nothing is filled.

## License

Public. The dataset's page (read 1368): "This work is licensed under CC-BY-4.0". Verdict: may be public. Cited as the page asks: "Alaska Center for Energy and Power (ACEP) at the University of Alaska Fairbanks (UAF). Monthly Electrical Generation By Community. Version v3.0. Alaska Energy Data Gateway, 2026." In the release package; held from the live set.

## Cross-check

The sums are compared with EIA's state totals above. The Gateway's service areas cover 78 per cent of EIA's figure for 2021 (5.12 of 6.60 TWh) and 86 per cent for 2001 (5.81 of 6.74).
