# Every country's electricity (EIA's International Energy Statistics, the bulk file)

Energy Research Warehouse (ERW), method note written in session 918 (chain 051) for a table first written on 23 October 2026.

Tables: `eia_world_electricity_annual`

## Publisher and address

U.S. Energy Information Administration (EIA), International Energy Statistics, read from EIA's bulk download `https://www.eia.gov/opendata/bulk/INTL.zip` (one file, `INTL.txt`, one JSON line a series and one a category). The same statistics the API's route `international` serves; session 886's `eia_international_electricity_annual` reads the U.S., Canada and Mexico there. Connector: `warehouse/connectors/eia_intl_bulk.py` (session 909). Source id `eia:international_bulk`, so that the two connectors do not write each other's line of `sources.csv`.

## Vintage and revision

1980 to 2024 when written (run `20261023T075752Z`; the file retrieved 2026-10-23T07:54:07Z, last modified by EIA 19 October 2026). A snapshot: each run replaces the table whole. A run reuses the saved file unless `--fresh` (ceiling: one request); `--offline` asks nothing. Session 909 chose the bulk file because the API counts 399,208 electricity records from 1980, 80 pages of 5,000, against a ceiling of 20; the file holds the same 399,208 values.

## Shape and variables

Series. `entity` `eia_intl:<EIA area code>:<EIA product id>`, as session 886's table names them; `ts_utc` the year's 1 January; `freq` `P1Y`; `geo` empty (EIA's three-letter codes and its regions are its own, and no ISO 3166 code is guessed); `node` "<area>, <product>"; `x_area` the kind of area.

| Variable | Unit | What it is |
|---|---|---|
| `generation` | `MWh` | net generation by product (EIA's billion kWh times 1,000,000) |
| `capacity` | `MW` | installed capacity by product (EIA's million kW times 1,000) |
| `consumption`, `imports`, `exports`, `net_imports`, `distribution_losses` | `MWh` | electricity (product 2) only |

Products: 2 electricity, 27 nuclear, 28 fossil fuels (30 coal, 31 natural gas, 32 oil, 2890 other gases), 29 renewables (33 hydroelectricity, 34 non-hydroelectric renewables: 35 geothermal, 36 solar, tide, wave and fuel cell, 116 solar, 117 tide and wave, 37 wind, 38 biomass and waste), 82 hydroelectric pumped storage. The levels overlap: a sum takes one level.

`x_area`: `country` (219), `former` (7: CSK, DDR, DEUW, NLDA, SCG, SUN, YUG), `part` (2: HITZ the Hawaiian Trade Zone, USIQ the U.S. Pacific Islands) or `region` (35: WORL the world, the continents, OECD, OPEC, the EU and EIA's IEO regions). A sum over countries takes `country` and `former` only.

When written: 332,254 rows, 4,421 series, 263 areas (EIA's file has electricity series for 264 codes; one holds no figure). Generation 167,774 rows, capacity 109,749, each of the five trade and use variables about 11,000. The world in 2024: generation 30,664 TWh, capacity 9,758 GW.

## Reading the file

- Only annual series (`.A`) in billion kWh (`BKWH`) or million kW (`MK`) are taken: these are electricity's. EIA's copies of the same energy in quadrillion Btu, terajoules and tonnes of oil equivalent are not.
- A series id must have four parts (`INTL.<product>-<activity>-<area>-<unit>.<frequency>`); an activity (12 generation, 7 capacity, 2 consumption, 3 imports, 4 exports, 23 net imports, 9 distribution losses) or product not in the maps stops the run.
- An area's name is the part every one of its series' names ends with (EIA writes "<what>, <area>, Annual"); fewer than two names for an area stops the run. Checked by session 909 against the API's list of 268 areas: every name equal, but for a trailing space the API gives Timor-Leste.
- A value EIA leaves empty or marks ("NA", "--", "ie") has no row; nothing is filled. An (entity, variable, ts_utc) given twice stops the run.
- Negative values are kept as EIA gives them: pumped storage's net generation (2,404 rows), net imports (2,506) and one consumption figure (Sierra Leone, 2009, minus 1,900 MWh).

## License

Public: a work of the U.S. government (record 1 of `license_reads.csv`); cite "U.S. Energy Information Administration, International Energy Statistics".

## Cross-checks (sessions 909 and 918)

- The U.S., Canada and Mexico against session 886's table, read from the API: 4,131 rows in both, none in one only, every value and node equal.
- The world (WORL) against the countries and former countries summed, 1980 to 2024: total generation, total capacity, consumption and nuclear generation within 0.01 percent in every year, solar within 0.03 percent.
- Session 918, against the code and the table: the header's counts (series, areas by kind) are computed from the rows the run writes and match the table. Session 909's report gave 264 areas; it is corrected to 263.

## What it does not hold

- EIA's flags: the bulk file gives none, where the API flags values that round to zero (session 886's table keeps them).
- The energy of other products (oil, gas, coal, total energy), which the same file holds; chain 052's session 923 is to take oil and gas from it.
