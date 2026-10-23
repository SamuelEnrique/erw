# EIA-860's power plants, with each plant's wires owner

Energy Research Warehouse (ERW), method note written in session 877 (chain 047) for a table first written on 23 October 2026.

Tables: `eia860_plants_annual`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-860 Annual Electric Generator Report, plant file. The connector
reads EIA's page, `https://www.eia.gov/electricity/data/eia860/`, and takes the newest final year's zip it links outside
`/archive/`. When written: `https://www.eia.gov/electricity/data/eia860/xls/eia8602025.zip`, file
`2___Plant_Y2025.xlsx`. Connector: `warehouse/connectors/eia860_plants.py` (session 873).

EIA's robots file disallows `/archive/` (session 666), where EIA moves earlier years; they are not asked for. EIA's early
release (ER) zip is not read: only a final year.

## Vintage and revision

Data year 2025, EIA-860's final 2025 release (`vintage` 2025, `status_date` 2025-01-01 on every row). The zip was
retrieved 2026-10-23T03:33:49Z; the table was written 2026-10-23T03:34:16Z. A snapshot: each run replaces the table whole
with the newest final year the page links, so an earlier year is not kept. Ceiling two requests a run (the page and the
zip; a zip saved in `warehouse/raw/eia860_plants/` is reused). Session 873 made 4 of its 4 requests: the probe's page and
zip (its copy of the 23.6 MB zip was cut short at 20 MB), then the trial's page and zip, which the write reused.

## Shape and variables

Entities, one row a plant. Key `entity_id` `eia860_plant:<plant code>`. A plant code given twice stops the run.

Columns:

- `entity_type` `plant`; `name` the plant's name; `geo` `US-<state>`; `lat`, `lon` as EIA gives them (decimal degrees);
  `operator` the utility's name.
- `capacity_mw` and `status` are empty: the plant sheet gives neither (generators are in `eia860m_operating_generators`).
- `status_date` the data year's 1 January; `vintage` the data year; `source`, `source_url`, `retrieved_at`.
- `x_*`: every other column of EIA's sheet, its heading as a name, as EIA gives it (37 in all): `x_state`,
  `x_utility_id`, `x_street_address`, `x_city`, `x_zip`, `x_county`, `x_nerc_region`, `x_balancing_authority_code`,
  `x_balancing_authority_name`, `x_name_of_water_source`, `x_primary_purpose_naics_code`, `x_regulatory_status`,
  `x_sector`, `x_sector_name`, `x_ferc_cogeneration_status`, `x_ferc_cogeneration_docket_number`,
  `x_ferc_small_power_producer_status`, `x_ferc_small_power_producer_docket_number`,
  `x_ferc_exempt_wholesale_generator_status`, `x_ferc_exempt_wholesale_generator_docket_number`, `x_ash_impoundment`,
  `x_ash_impoundment_lined`, `x_ash_impoundment_status`, `x_transmission_or_distribution_system_owner`,
  `x_transmission_or_distribution_system_owner_id`, `x_transmission_or_distribution_system_owner_state`,
  `x_grid_voltage_kv`, `x_grid_voltage_2_kv`, `x_grid_voltage_3_kv` (kV), `x_energy_storage`, `x_natural_gas_ldc_name`,
  `x_natural_gas_pipeline_name_1`, `x_natural_gas_pipeline_name_2`, `x_natural_gas_pipeline_name_3`, `x_pipeline_notes`,
  `x_natural_gas_storage`, `x_liquefied_natural_gas_storage`. EIA's Y, N and X flags are kept as EIA gives them.

When written: 17,349 plants in 51 states (the 50 and DC), every key unique; 68 balancing authority codes. Sector: IPP
Non-CHP 11,552, Electric Utility 4,187, Commercial Non-CHP 515, Industrial CHP 441, Industrial Non-CHP 248, Commercial
CHP 221, IPP CHP 185. NERC region: WECC 4,230, SERC 3,466, NPCC 2,941, RFC 2,610, MRO 2,421, TRE 1,427, REC 1, none 253.
Empty: coordinates 28, county 23, balancing authority 289, wires owner 111, first grid voltage 141. In Texas, 1,522 of
1,533 plants name their wires owner (Oncor 426, AEP Texas Central 229, CenterPoint 212, TNMP 88, LCRA 71 and others).

## License

Public: a work of the U.S. government. EIA's terms (record 1 of the license reads, `docs/licenses.md`): its data "are in
the public domain and are not subject to copyright protection". Verdict in `docs/licenses.md`: public. Cite "U.S. Energy
Information Administration, Form EIA-860".

## Cross-check (session 873)

- 14,699 of the 14,767 plants of `eia860m_operating_generators` are here (99.5 percent), with the same county in every
  one.

## What it does not hold

- Generators, their capacity and status: EIA-860M already holds them (`eia860m_operating_generators` and its siblings);
  the generator file of the zip is not read.
- EIA-860's other sheets (owners, wind, solar, storage and the rest).
- Earlier years, which EIA moves to `/archive/`, and the early release of a newer year.
- A plant's ERCOT or other ISO node: the wires owner fills "a node's wires utility (TSP)" of `siting-gaps.md` only for a
  plant, not for a node.
