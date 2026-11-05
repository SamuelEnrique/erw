# EIA-860's owner, energy storage, solar, wind and multifuel schedules

Energy Research Warehouse (ERW), method note written in session 891 (chain 048) for tables first written on 23 October 2026.
The multifuel table, added in session 896, was added to the note in session 905 (chain 049).

Tables: `eia860_generator_owners`, `eia860_storage_generators`, `eia860_solar_generators`, `eia860_wind_generators`, `eia860_multifuel_generators`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-860 Annual Electric Generator Report, five files of the annual
zip: the owner file (`4___Owner_Y2025.xlsx`, sheet Ownership), the energy storage file (`3_4_Energy_Storage_Y2025.xlsx`,
sheets Operable, Proposed, Retired and Canceled), the solar file (`3_3_Solar_Y2025.xlsx`, sheets Operable, Retired and
Canceled), the wind file (`3_2_Wind_Y2025.xlsx`, sheets Operable, Retired and Canceled) and, since session 896, the
multifuel file (`3_5_Multifuel_Y2025.xlsx`, sheets Operable, Proposed, Retired and Canceled). The connector reads EIA's
page, `https://www.eia.gov/electricity/data/eia860/`, and takes the newest final year's zip it links outside `/archive/`.
When written: `https://www.eia.gov/electricity/data/eia860/xls/eia8602025.zip`, the zip session 873 saved in
`warehouse/raw/eia860_plants/` (retrieved 2026-10-23T03:33:49Z); session 885 made no request. Connector:
`warehouse/connectors/eia860_schedules.py`, one connector for the five tables, as they come from one zip; it reuses
`eia860_plants.py`'s page, zip and reader helpers (`eia860_plants_annual.md`).

EIA's robots file disallows `/archive/` (session 666), where EIA moves earlier years; they are not asked for. EIA's early
release (ER) zip is not read: only a final year.

## Vintage and revision

Data year 2025, EIA-860's final 2025 release (`vintage` 2025 on every row). Written by run `20261023T044808Z`; session
896's run `20261023T062106Z` wrote session 885's four tables again with the same number of rows, and the multifuel table first. A
snapshot: each run replaces each table whole with the newest final year the page links, so an earlier year is not kept.
Ceiling two requests a run (the page and the zip; a zip saved in `warehouse/raw/eia860_plants/` by `eia860_plants.py` is
reused).

## Shape and variables

Entities. The standard columns: `entity_id, entity_type, name, geo, lat, lon, capacity_mw, status, status_date, operator,
source, source_url, retrieved_at, vintage`. Then, in every table, `x_plant_code`, `x_generator_id`, `x_state`,
`x_eia_status` (EIA's status code) and `x_sheet` (the sheet the row came from), and after them every other column of
EIA's sheet, its heading as a name, as EIA gives it. EIA's codes and Y and N flags are kept as EIA gives them, not decoded.

| Table | `entity_id` | `entity_type` | `name` | `capacity_mw` | `status_date` |
|---|---|---|---|---|---|
| `eia860_generator_owners` | `eia860_owner:<plant code>:<generator id>:<ownership id>` | `company` (an owner's share of one generator) | the owner's name | empty | empty |
| `eia860_storage_generators` | `eia860_storage:<plant code>:<generator id>` | `generator` | the plant's name | nameplate (MW) | see below |
| `eia860_solar_generators` | `eia860_solar:<plant code>:<generator id>` | `generator` | the plant's name | nameplate (MW) | see below |
| `eia860_wind_generators` | `eia860_wind:<plant code>:<generator id>` | `generator` | the plant's name | nameplate (MW) | see below |
| `eia860_multifuel_generators` | `eia860_multifuel:<plant code>:<generator id>` | `generator` | the plant's name | nameplate (MW) | see below |

In all five, `geo` is `US-<plant state>`, `lat` and `lon` are empty, `operator` is the reporting utility's name (EIA's Utility Name), and
`source` is `eia:eia860:owner`, `eia:eia860:energy_storage`, `eia:eia860:solar`, `eia:eia860:wind` or
`eia:eia860:multifuel`. A generator
table's plant and generator are the ones EIA-860M's tables name `eia860:<plant code>:<generator id>`.

`status` is EIA's code as the data standard's word: OP, SB, OA, OS `operating`; P, L, T, OT `planned`; U, V, TS
`under_construction`; RE `retired`; CN `withdrawn` (canceled); IP `suspended` (indefinitely postponed). In the owners
table it is the generator's status. In the generator tables, `status_date` is an operable generator's month of operation
and a retired one's month of retirement (the first of the month); it is empty for the proposed, the canceled and the
indefinitely postponed. A proposed generator's planned month is in `x_current_year`, `x_current_month`.

EIA's own fields, beyond the five above:

| Table | Fields |
|---|---|
| `eia860_generator_owners` | `x_utility_id` (the reporting utility), `x_owner_street_address`, `x_owner_city`, `x_owner_state`, `x_owner_zip`, `x_percent_owned` (EIA's fraction: 0.6 is 60 percent), `x_plant_name` |
| all four generator tables | `x_utility_id`, `x_county`, `x_technology`, `x_prime_mover`, `x_sector_name`, `x_sector`, `x_summer_capacity_mw`, `x_winter_capacity_mw`, `x_operating_month`, `x_operating_year`, `x_retirement_month`, `x_retirement_year` |
| `eia860_storage_generators` | `x_nameplate_energy_capacity_mwh`, `x_maximum_charge_rate_mw`, `x_maximum_discharge_rate_mw`, `x_storage_technology_1` to `x_storage_technology_4`, `x_nameplate_reactive_power_rating`, `x_storage_enclosure_type`; the uses: `x_arbitrage`, `x_frequency_regulation`, `x_load_following`, `x_ramping_spinning_reserve`, `x_co_located_renewable_firming`, `x_transmission_and_distribution_deferral`, `x_system_peak_shaving`, `x_load_management`, `x_voltage_or_reactive_power_support`, `x_backup_power`, `x_excess_wind_and_solar_generation`; the coupling: `x_ac_coupled`, `x_dc_coupled`, `x_dc_tightly_coupled`, `x_independent`; the units supported: `x_direct_support_of_another_unit`, `x_direct_support_plant_id_1` to `_3`, `x_direct_support_gen_id_1` to `_3`, `x_support_t_d_asset`; `x_current_month`, `x_current_year` |
| `eia860_solar_generators` | `x_lenses_mirrors`, `x_single_axis_tracking`, `x_dual_axis_tracking`, `x_fixed_tilt`, `x_bifacial`, `x_east_west_fixed_tilt`, `x_parabolic_trough`, `x_linear_fresnel`, `x_power_tower`, `x_dish_engine`, `x_other_solar_technology`, `x_azimuth_angle`, `x_tilt_angle`, `x_dc_net_capacity_mw`, `x_crystalline_silicon`, `x_thin_film_cdte`, `x_thin_film_a_si`, `x_thin_film_cigs`, `x_thin_film_other`, `x_other_materials`, `x_net_metering_agreement`, `x_net_metering_dc_capacity_mw`, `x_virtual_net_metering_agreement`, `x_virtual_net_metering_dc_capacity_mw` |
| `eia860_wind_generators` | `x_number_of_turbines`, `x_predominant_turbine_manufacturer`, `x_predominant_turbine_model_number`, `x_design_wind_speed_mph`, `x_wind_quality_class`, `x_turbine_hub_height_feet` |
| `eia860_multifuel_generators` | see "Session 896: the multifuel schedule" below |

When written:

- `eia860_generator_owners`: 5,680 rows, each owner's share of 4,018 jointly owned generators; 2,038 owner names. By the
  generator's status: operating 4,983, retired 415, under construction 109, planned 80, withdrawn 72, suspended 21.
- `eia860_storage_generators`: 1,782 rows (Operable 1,012, Proposed 607, Retired and Canceled 163). Operating 1,012,
  under construction 316, planned 291, withdrawn 97, retired 35, suspended 31. The operable hold 44,205 MW of nameplate
  and 121,192 MWh of energy capacity.
- `eia860_solar_generators`: 8,520 rows (Operable 8,011, Retired and Canceled 509). Operating 8,011, withdrawn 313,
  retired 160, suspended 36.
- `eia860_wind_generators`: 1,745 rows (Operable 1,573, Retired and Canceled 172). Operating 1,573, retired 102,
  withdrawn 54, suspended 16.

## Reading the sheets

- The heading row is the first of the sheet's first five rows that names "Plant Code"; a sheet without one stops the
  run. Every column is found by its heading, not by position, and a heading given twice stops the run. A sheet that
  lacks the plant code, plant name, state, generator id or status (and the ownership id and owner name in the owner
  file, the nameplate capacity in the others) stops the run.
- A row with no plant code is EIA's footnote and is read past.
- A status code not in the map above stops the run.
- A row EIA gives twice with every field the same is kept once. A key given twice with two different rows has no key:
  both are left out and named in the header (chain 030's rule). When written, no key was given twice.
- Values are written as read. In `x_owner_zip` a ZIP code that begins with 0 has lost its first digit (8540, 2458).

## License

Public: a work of the U.S. government (EIA, record 1 of `license_reads.csv`; `docs/licenses.md`: public, agrees for all
five tables). Cite "U.S. Energy Information Administration, Form EIA-860".

## Cross-check (session 885)

Against `eia860m_operating_generators` (EIA-860M, August 2026), by plant and generator:

- Storage: 1,010 of the 1,012 operable generators are there, with the same nameplate in 1,010 of 1,010.
- Solar: 8,009 of 8,011, all with the same nameplate.
- Wind: 1,564 of 1,573, the same nameplate in 1,563.
- EIA-860M's operating list is longer (10,008 solar generators against 8,011), since it runs eight months past the 2025
  year end.
- Owners: the shares of 4,014 of the 4,018 generators sum to 1; four do not as EIA gives them (Plant 341 CT5 sums to
  1.5; one sums to 0; two to 0.9). Recomputed from the table in session 891: the one that sums to 0 is plant 69201
  generator 11220, whose one owner's share is empty; the two at 0.9 are 69801 LW754 and 69802 BH448; and plant 70387
  BESS1 sums to 1.0009 (0.901 and 0.0999), counted with those that sum to 1.

## Session 896: the multifuel schedule

Session 896 added EIA-860's 3_5 multifuel schedule to the connector as a fifth table, `eia860_multifuel_generators`: the
generators that can burn more than one fuel, cofire, or switch between oil and gas. Read from the same zip
(`eia8602025.zip`, retrieved 2026-10-23T03:33:49Z), file `3_5_Multifuel_Y2025.xlsx`, sheets Operable, Proposed, Retired
and Canceled; no request made. Written by run `20261023T062106Z`.

It is read as the other generator tables are (the sections above): `entity_id`
`eia860_multifuel:<plant code>:<generator id>`, the same plant and generator EIA-860M's tables name
`eia860:<plant code>:<generator id>`; `entity_type` `generator`; `name` the plant's name; `capacity_mw` the nameplate;
`source` `eia:eia860:multifuel`; the same status map, `status_date`, and rules for footnotes, headings and keys.

EIA's own fields, beyond the five every table carries and those of all four generator tables: the fuels,
`x_energy_source_1`, `x_energy_source_2`, `x_multiple_fuels`; cofiring, `x_cofire_fuels`, `x_cofire_energy_source_1` to
`_6`; switching, `x_switch_between_oil_and_natural_gas`, `x_switch_when_operating`; the capacity with each fuel,
`x_net_summer_capacity_with_natural_gas_mw`, `x_net_winter_capacity_with_natural_gas_mw`,
`x_net_summer_capacity_with_oil_mw`, `x_net_winter_capacity_with_oil_mw`; the time to switch,
`x_time_to_switch_from_gas_to_oil`, `x_time_to_switch_from_oil_to_gas`; what limits switching,
`x_factors_that_limit_switching`, `x_storage_limits`, `x_air_permit_limits`, `x_other_limits`; and a proposed
generator's planned month, `x_current_month`, `x_current_year`. Codes and Y and N flags are kept as EIA gives them.

When written: 3,785 rows at 1,064 plants (Operable 2,847, Proposed 70, Retired and Canceled 868). Operating 2,847,
retired 835, planned 58, withdrawn 29, under construction 12, suspended 4. The operable hold 208,622.9 MW of nameplate;
every one is marked Y in `x_multiple_fuels`, 1,876 Y in `x_switch_between_oil_and_natural_gas` (909 N, 62 empty) and
1,588 Y in `x_cofire_fuels`. No key was given twice.

Each table's header names the session that first wrote it: 885 for the four, 896 for the multifuel table. The first
multifuel write named session 885, as the connector then wrote it for all five; this note's check found it, and session 905
wrote the five tables again with the session of each (the same rows).

Cross-check (session 896), against `eia860m_operating_generators` (EIA-860M, August 2026): 2,842 of the 2,847 operable
multifuel generators are in EIA-860M's list, all 2,842 with the same nameplate.

## What it does not hold

- EIA-860's other schedules: the 6_1 and 6_2 environmental schedules (session 896's `eia860_boilers`,
  `eia860_cooling_systems` and `eia860_emission_controls`, `eia860_environment.md`), and the generator file of the zip (generators are in `eia860m_operating_generators` and its siblings). The plant
  file is in `eia860_plants_annual`.
- Proposed solar and wind generators: their files, when written, have no Proposed sheet.
- Coordinates: `lat` and `lon` are empty (the plant's are in `eia860_plants_annual`).
- An owner's capacity in MW: only EIA's fraction owned.
- Earlier years, which EIA moves to `/archive/`, and the early release of a newer year.
