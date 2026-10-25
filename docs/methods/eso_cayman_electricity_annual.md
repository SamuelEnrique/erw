# Grand Cayman's electricity a year since 1996: capacity, production and consumption by class (ESO's Compendium of Statistics 2024, Table 20.01)

Energy Research Warehouse (ERW), method note written in session 2639 (chain 131) for a table first written on 25 October 2026 (session 2633).

Tables: `eso_cayman_electricity_annual`

## Publisher and address

The Economics and Statistics Office of the Cayman Islands (ESO), Compendium of Statistics 2024, chapter 20, Energy and Water Supply, Table 20.01, "Electricity Production in Grand Cayman", whose source is Caribbean Utilities Company Ltd (CUC): `https://www.eso.ky/storage/right_page_docums/uploadFilePdf/458/Chapter%2020%20-%20Energy%20and%20Water%20Supply.XLS`, listed on the office's Energy and Water Supply page (`https://www.eso.ky/utilities.html`, dated 24 December 2025). One GET, no key. Source id `eso_ky:compendium_2024_table_20_01`. Connector: `warehouse/connectors/eso_cayman_electricity.py` (session 2633), whose raw store is `warehouse/raw/eso_ky/`. www.eso.ky's robots file names `*` with no rule (read 1282).

## Vintage and revision

Written by run `20261025T075425Z` (the write under the lock, offline), which read the workbook saved at 2026-10-25T07:51:22Z. `vintage` is its last-modified time, 2025-12-24T18:02:27Z. Each year's chapter has its own address and gives the series again.

## Shape and variables

Series, 174 rows, 6 entities, each year from 1996 to 2024. `entity` `eso:ky:<item>`:
- `capacity` (`variable` `capacity`, `unit` MW);
- `production` (`generation`, MWh);
- `residential`, `industrial_commercial`, `public_lighting` and `consumption_total` (`consumption`, MWh).

`ts_utc` the year's first day; `freq` P1Y; `geo` KY; `node` the table's column, its footnote stars removed.

In 1996: capacity 71.8 MW, production 309,717 MWh, consumption 281,449. In 2024: capacity 165.5 MW, production 760,200 MWh, consumption 749,337 (residential 406,886, industrial and commercial 338,192, public lighting 4,259). The table excludes private generators (its note). Hurricane Ivan lowered 2004's capacity to 95.43 MW and production to 433,379 MWh.

## Reading the source

- The run stops at once, asking nothing, while `eso_ky` or www.eso.ky is paused.
- One request a run; `--offline` reads the saved workbook (an `.XLS`, read with xlrd).
- **The sheet** ".01" is read by its title ("Electricity Production in Grand Cayman, ...") and its header row (Year, Capacity (Mws)*, Production (Mwhrs)**, Residential, Industrial/ Commercial, Public Lighting, Total, Percent Change).
- **The years:** every later row with a year is a year. The sheet's blank spacing rows, after the header and between groups of years, are skipped, and reading stops at the first other row (the note). The years must run without a gap, and each figure must be a number.
- **Check:** each year's three classes add to its total within 1 MWh.
- The run stops, and no file is written, for: the title or header found other than once, a header out of order, a text cell, a gap in the years, a check missed.

Nothing is filled. Not taken: the percent change; Table 20.02 (the Sister Islands, which ends in 2016); the census tables of lighting and cooking fuel; the water tables.

## License

Internal. ESO's home page (read 1283): "COPYRIGHT © 2026 ESO The Economics and Statistics Office. ALL RIGHTS RESERVED.", with no terms of reuse linked. Verdict: needs written permission. The figures are CUC's. Held from the live set and from Redivis.

## Cross-check

EIA's world table (`eia_world_electricity_annual`, read past its header lines) gives the Cayman Islands 704.1 GWh of generation and 702.0 GWh of consumption in 2024, against Grand Cayman's 760.2 and 749.3 from CUC. ESO's figures are higher, though they leave out the Sister Islands.
