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

<a id="cross-checks"></a>

## Cross-checks

Session 681 (chain 043): the code machine's stand-in for "which utility serves a site" was the largest industrial utility of the state by `eia861_utility_sales`. For each grid's main hub, a county its name points to (a choice made here: Harris for ERCOT's Houston hub, Los Angeles for SP15, New York for Zone J, Suffolk for the Mass Hub, Allegheny for PJM's Western Hub, Marion for the Indiana Hub, Sedgwick for SPP's North Hub), the utilities this table lists against that stand-in. No figure was moved.

| Our figure | Published figure | Source and date | Gap | Reason |
|---|---|---|---|---|
| Harris County, TX (ERCOT's Houston hub): CenterPoint Energy, Entergy Texas Inc., San Bernard Electric Coop, Inc | TXU Energy Retail Co, LLC, the largest industrial seller in TX in 2025 (47,232,447 MWh, part D) | docs/methods/eia861_utility_sales.md, `eia861_utility_sales`, 2025 | a different utility | TXU Energy Retail Co, LLC sells to industry as a retailer or marketer (part D) and holds no franchise territory; the county's wires belong to the utilities in our figure |
| Los Angeles County, CA (CAISO's SP15): City of Azusa, City of Burbank Water and Power - (CA), City of Glendale - (CA), City of Pasadena - (CA) and others | Pacific Gas & Electric Co., the largest industrial seller in CA in 2025 (18,763,491 MWh, part A, C) | the same | a different utility | Pacific Gas & Electric Co. serves 50 counties of CA, not Los Angeles: the state's largest industrial seller is not the hub county's utility |
| New York County, NY (NYISO's Zone J): Consolidated Edison Co-NY Inc | Niagara Mohawk Power Corp., the largest industrial seller in NY in 2025 (8,670,545 MWh, part A, C) | the same | a different utility | Niagara Mohawk Power Corp. serves 37 counties of NY, not New York: the state's largest industrial seller is not the hub county's utility |
| Suffolk County, MA (ISO-NE's Mass Hub): Massachusetts Bay Trans Authority, Massachusetts Electric Co, NSTAR Electric Company | Direct Energy Business, the largest industrial seller in MA in 2025 (2,457,018 MWh, part B) | the same | a different utility | Direct Energy Business sells to industry as a retailer or marketer (part B) and holds no franchise territory; the county's wires belong to the utilities in our figure |
| Allegheny County, PA (PJM's Western Hub): Borough of Pitcairn - (PA), Borough of Tarentum - (PA), Central Electric Coop, Inc - (PA), Duquesne Light Co and others | FirstEnergy Pennsylvania Electric Co, the largest industrial seller in PA in 2025 (21,055,412 MWh, part A, C) | the same | none: it serves the county | The state's largest industrial seller is among the utilities this table lists for the hub's county (with others), so the stand-in names a utility that serves it |
| Marion County, IN (MISO's Indiana Hub): AES Indiana, Duke Energy Indiana, LLC | Duke Energy Indiana, LLC, the largest industrial seller in IN in 2025 (9,222,628 MWh, part A) | the same | none: it serves the county | The state's largest industrial seller is among the utilities this table lists for the hub's county (with others), so the stand-in names a utility that serves it |
| Sedgwick County, KS (SPP's North Hub): Butler Rural El Coop Assn, Inc - (KS), City of Mount Hope - (KS), City of Mulvane - (KS), Evergy Kansas South, Inc and others | Evergy Kansas South, Inc, the largest industrial seller in KS in 2025 (3,257,541 MWh, part A) | the same | none: it serves the county | The state's largest industrial seller is among the utilities this table lists for the hub's county (with others), so the stand-in names a utility that serves it |
