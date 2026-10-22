# Utility service territories: which utility serves each county

Energy Research Warehouse (ERW), method note written in session 667 (chain 043), for the All grids tab's question of which
utility serves a site.

Tables: `utility_service_territories`

## Publisher and file

U.S. Energy Information Administration (EIA), Form EIA-861 Annual Electric Power Industry Report: the workbook
`Service_Territory_<year>.xlsx` inside the year's zip, `https://www.eia.gov/electricity/data/eia861/zip/f861<year>.zip`,
linked from `https://www.eia.gov/electricity/data/eia861/`. Two sheets: `Counties_States` and `Counties_Territories`
(Puerto Rico and the other territories). Connector: `warehouse/connectors/eia861_territories.py`.

## Vintage and revision

One data year a run (`--year`; 2025 when written, from the zip `eia861_sales.py` saved on 21 October 2026, so session
667 made no request). The table is a snapshot: a run replaces it whole, so it holds one year. EIA's robots file disallows
`/archive/` (session 666), where EIA moves earlier years' zips; the connector refuses such an address rather than asking.

## Shape and columns

Entities, one row a utility, state and county pair, as EIA lists it:

- `entity_id` `eia861:<utility number>:<state>:<county>`; `entity_type` `utility`; `name` the utility's name as EIA writes
  it; `geo` `US-<state>`; `source` `eia:eia861_territory`; `vintage` `EIA-861 <year>`.
- `x_utility_number` (EIA's utility id, the key of `eia861_utility_sales` and of OpenEI's `eiaid`), `x_state`,
  `x_county` (EIA's county name, no FIPS code), `x_short_form` (`Y` when the utility filed EIA's short form),
  `x_data_year`, `x_sheet`.

When written: 11,893 pairs, 2,909 utilities, 56 states and territories. A year in the sheet other than the year asked,
a row without a state or a county, or a pair given twice stops the run.

## License

Public: a work of the U.S. government ("U.S. government publications are in the public domain", EIA's page, record 1
of `license_reads.csv`). Cite "U.S. Energy Information Administration, Form EIA-861".

## Cross-check (session 667)

Against `eia861_utility_sales` for 2025: of the 1,238 utilities with bundled sales (part A), 13 have no territory, all of
them third-party solar owners (Tesla, Sunrun, SunPower Capital and others), which hold no franchise area. The 303
utilities with sales and no territory are otherwise energy-only retailers (part B, 233) and power marketers (part D, 87).
The 1,680 utilities with a territory and no sales row are mostly short-form filers, whose sales EIA imputes and the
sales table leaves out.

## What it does not hold

- No boundary and no share: a utility "serves" a county when EIA lists the pair; a county served by three utilities has
  three rows and no split among them.
- No FIPS code, no balancing authority, no retail choice flag.
- One year only; earlier years are in EIA's archive, which its robots file disallows.
