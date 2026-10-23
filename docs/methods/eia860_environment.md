# EIA-860's environmental schedules: boilers, cooling systems and emissions controls

Energy Research Warehouse (ERW), method note written in session 905 (chain 049) for tables first written on 23 October 2026.

Tables: `eia860_boilers`, `eia860_cooling_systems`, `eia860_emission_controls`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-860 Annual Electric Generator Report, the two environmental files
of the annual zip:

- `6_2_EnviroEquip_Y2025.xlsx`: sheets "Boiler Info & Design Parameters", "Emission Standards & Strategies" and "Cooling".
- `6_1_EnviroAssoc_Y2025.xlsx`: sheet "Emissions Control Equipment", and the association sheets "Boiler Generator",
  "Boiler Cooling", "Boiler Particulate Matter", "Boiler SO2", "Boiler NOx", "Boiler Mercury" and "Boiler Stack Flue".

The connector reads EIA's page, `https://www.eia.gov/electricity/data/eia860/`, and takes the newest final year's zip it
links outside `/archive/`. When written: `https://www.eia.gov/electricity/data/eia860/xls/eia8602025.zip`, the zip
session 873 saved in `warehouse/raw/eia860_plants/` (retrieved 2026-10-23T03:33:49Z); session 896 made no request.
Connector: `warehouse/connectors/eia860_environment.py`, one connector for the three tables, as they come from one zip.
It reuses `eia860_plants.py`'s page, zip and reader helpers (`eia860_plants_annual.md`) and `eia860_schedules.py`'s
status words and key rule (`eia860_schedules.md`).

EIA's robots file disallows `/archive/` (session 666), where EIA moves earlier years; they are not asked for. EIA's early
release is not read: only a final year.

## Vintage and revision

Data year 2025, EIA-860's final 2025 release (`vintage` 2025 on every row). Written by run `20261023T062130Z`. A
snapshot: each run replaces each table whole with the newest final year the page links, so an earlier year is not kept.
Ceiling two requests a run (the page and the zip; a zip saved in `warehouse/raw/eia860_plants/` by `eia860_plants.py` is
reused).

## Shape and variables

Entities. The standard columns: `entity_id, entity_type, name, geo, lat, lon, capacity_mw, status, status_date, operator,
source, source_url, retrieved_at, vintage`. Then, in every table, `x_plant_code`, `x_state` and `x_eia_status` (EIA's
status code), and after them every other column of EIA's sheets, its heading as a name, as EIA gives it. EIA's codes
and Y and N flags are kept as EIA gives them, not decoded. Costs are EIA's thousand dollars, named so in the column
(`x_total_cost_thousand_dollars`, `x_cost_total_thousand_dollars` and the rest).

`entity_type` is `equipment` in all three: a part of a plant that is neither a generator nor the plant (Decision 54 in
`docs/datastandard.md`, session 896).

| Table | `entity_id` | `name` | `source` |
|---|---|---|---|
| `eia860_boilers` | `eia860_boiler:<plant code>:<boiler id>` | the plant's name, "boiler" and the boiler id | `eia:eia860:boilers` |
| `eia860_cooling_systems` | `eia860_cooling:<plant code>:<cooling id>` | the plant's name, "cooling" and the cooling id | `eia:eia860:cooling` |
| `eia860_emission_controls` | `eia860_control:<plant code>:<equipment type>:<control ids>` | the plant's name and the equipment type | `eia:eia860:emission_controls` |

A control's `<control ids>` are the ids it carries, each as `<kind>_<id>` (kinds `particulate_matter`, `so2`, `nox`,
`mercury`), joined with `+`: for example `eia860_control:3:SN:nox_1` and
`eia860_control:3:EC:particulate_matter_4+mercury_4`. EIA gives no single id for one piece of equipment.

In all three, `geo` is `US-<plant state>`; the association and control sheets give no state, so it is taken from the
plant's rows in the boiler, standards and cooling sheets, and is `US` where there are none. `lat`, `lon` and
`capacity_mw` are empty. `operator` is EIA's Utility Name.

`status` is EIA's code as the data standard's word, read in capitals (EIA writes a few in lower case: `op`, `os`, `re`
among the boilers), the code kept as given in `x_eia_status`: OP, SB, OA, OS, and the environmental schedules' own SC
(cold standby) and OZ (operated only in the ozone season) `operating`; P, L, T, OT and PL `planned`; U, V, TS and CO (new
unit under construction) `under_construction`; RE `retired`; CN `withdrawn`; IP `suspended`. An empty code stays empty.
`status_date` is the month in service of an operating part and the month of retirement of a retired one (the first of
the month), else empty. The cooling sheet gives no retirement month, so a retired cooling system has no `status_date`.

EIA's own fields, beyond the three above:

| Table | Fields |
|---|---|
| all three | `x_utility_id`, `x_plant_name`, `x_steam_plant_type` |
| `eia860_boilers`, the design | `x_boiler_id`, `x_hrsg`, `x_boiler_status`, `x_type_of_boiler`, `x_inservice_month`, `x_inservice_year`, `x_retirement_month`, `x_retirement_year`, `x_firing_type_1` to `_3`, `x_max_steam_flow_thousand_pounds_per_hour`, `x_firing_rate_using_coal_0_1_tons_per_hour`, `x_firing_rate_using_petroleum_0_1_barrels_per_hour`, `x_firing_rate_using_gas_0_1_mcf_per_hour`, `x_firing_rate_using_other_fuels`, `x_waste_heat_input_million_btu_per_hour`, `x_primary_fuel_1` to `_4`, `x_turndown_ratio`, `x_efficiency_100_load`, `x_efficiency_50_load`, `x_air_flow_100_load_cubic_feet_per_minute`, `x_wet_dry_bottom`, `x_fly_ash_reinjection`, `x_new_source_review`, `x_new_source_review_permit`, `x_new_source_review_month`, `x_new_source_review_year` |
| `eia860_boilers`, the standards and strategies | sulfur: `x_regulation_sulfur`, `x_standard_sulfur_rate`, `x_standard_sulfur_percent_scrubbed`, `x_unit_sulfur`, `x_period_sulfur`, `x_compliance_year_sulfur`, `x_sulfur_dioxide_control_existing_strategy_1` to `_3`, `x_sulfur_dioxide_control_proposed_strategy_1` to `_3`; nitrogen oxides: `x_regulation_nitrogen`, `x_standard_nitrogen_rate`, `x_unit_nitrogen`, `x_period_nitrogen`, `x_compliance_year_nitrogen`, `x_nitrogen_oxide_control_existing_strategy_1` to `_3`, `x_nitrogen_oxide_control_proposed_strategy_1` to `_3`; particulates: `x_regulation_particulate`, `x_standard_particulate_rate`, `x_unit_particulate`, `x_period_particulate`, `x_compliance_year_particulate`; mercury: `x_regulation_mercury`, `x_compliance_year_mercury`, `x_mercury_control_existing_strategy_1` to `_3`, `x_mercury_control_proposed_strategy_1` to `_3` |
| `eia860_boilers`, the associations | `x_generator_ids`, `x_cooling_ids`, `x_pm_control_ids`, `x_so2_control_ids`, `x_nox_control_ids`, `x_mercury_control_ids`, `x_stack_flue_ids`: each a list of ids joined with `;` |
| `eia860_cooling_systems` | `x_cooling_id`, `x_cooling_status`, `x_inservice_month`, `x_inservice_year`, `x_cooling_type_1` to `_4`, `x_percent_dry_cooling`, `x_cooling_water_source`, `x_cooling_water_discharge`, `x_water_source_code`, `x_water_type_code`, `x_intake_rate_at_100_gallons_per_minute`, `x_chlorine_inservice_month`, `x_chlorine_inservice_year`, `x_pond_inservice_month`, `x_pond_inservice_year`, `x_pond_surface_area_acres`, `x_pond_volume_acre_feet`, `x_tower_inservice_month`, `x_tower_inservice_year`, `x_tower_type_1` to `_4`, `x_tower_water_rate_gallons_per_minute`, `x_power_requirement_mw`, `x_cost_total_thousand_dollars`, `x_cost_ponds_thousand_dollars`, `x_cost_towers_thousand_dollars`, `x_cost_chlorine_equipment_thousand_dollars`, `x_intake_distance_shore_feet`, `x_outlet_distance_shore_feet`, `x_intake_distance_surface_feet`, `x_outlet_distance_surface_feet` |
| `eia860_emission_controls` | `x_equipment_type`, `x_particulate_matter_control_id`, `x_so2_control_id`, `x_nox_control_id`, `x_mercury_control_id`, `x_acid_gas_control`, `x_status`, `x_inservice_month`, `x_inservice_year`, `x_retirement_month`, `x_retirement_year`, `x_total_cost_thousand_dollars` |

When written:

- `eia860_boilers`: 4,384 rows at 1,538 plants. Operating 3,034 (OP 2,931, OS 58, SB 30, SC 7, OA 1, and in lower case
  op 6, os 1), retired 1,313 (one written `re`), withdrawn 18, under construction 11 (CO 9, TS 2), planned 8 (PL). The
  lists: generators on 4,379 boilers, cooling systems on 2,669, particulate controls on 1,942, SO2 controls on 847, NOx
  controls on 1,667, mercury controls on 1,075, stacks on 2,553.
- `eia860_cooling_systems`: 1,797 rows at 923 plants. Operating 1,258 (OP 1,242, OS 10, SB 4, SC 2), retired 525,
  withdrawn 6, planned 4, under construction 4.
- `eia860_emission_controls`: 5,375 rows at 1,101 plants. Operating 3,712 (OP 3,575, OS 80, SB 45, SC 9, OZ 3), retired
  1,629, withdrawn 19, under construction 8 (CO 6, TS 2), planned 6, and one with no status. 1,339 carry more than one
  control id. The most frequent equipment types: SR 1,197, EK 830, ACI 485, BP 455, SN 401.

## Reading the sheets

- The heading row is the first of the sheet's first five rows that names "Plant Code"; a sheet without one stops the
  run. Every column is found by its heading, not by position, and a heading given twice stops the run.
- A row with no plant code is EIA's footnote and is read past.
- A boiler is its row of the design sheet, joined by plant and boiler with the standards sheet's columns that the design
  sheet does not carry. A boiler given twice in the standards sheet with two different rows stops the run.
- Each association sheet must hold one associated id beyond the plant, utility, boiler and steam plant type columns, or
  the run stops. A boiler's ids from each are sorted, the empty ones left out, and joined with `;`.
- A status code not in the map above stops the run.
- A row EIA gives twice with every field the same is kept once. A key given twice with two different rows has no key:
  both are left out and named in the header (chain 030's rule). When written, no key was given twice.
- Values are written as read. When written:
  - 24 controls carry no control id, their key ending in `:` (20 of them of type DSI).
  - One control row has no equipment type, no control id and no status: `eia860_control:50118::` (Hal C Weaver Power
    Plant). It is kept as EIA gives it.
  - 27 controls are at plants none of the boiler, standards or cooling sheets name: their `geo` is `US`, and their
    `x_plant_name` and `operator` are empty.
  - 233 operating boilers have no `status_date` (232 with no in-service month or year, one with a year and no month),
    and 54 retired boilers and 72 retired controls have no retirement month or year.

## License

Public: a work of the U.S. government (EIA, record 1 of `license_reads.csv`). Cite "U.S. Energy Information
Administration, Form EIA-860".

## Cross-check (session 896)

Against `eia860m_operating_generators` (EIA-860M, August 2026), by plant and generator:

- The 3,034 operating boilers' lists name generators 4,741 times, and 4,352 of those (91.8 percent) are in EIA-860M's
  operating list. Recomputed in session 905: the 4,741 count a generator once for each boiler that names it; they are
  2,296 distinct plant and generator pairs, of which 2,132 are in EIA-860M's list.
- Five boilers name no generator: `eia860_boiler:50474:AUX` (operating), `eia860_boiler:2158:6768`,
  `eia860_boiler:3443:7` and `eia860_boiler:675:7` (retired), and `eia860_boiler:56163:HRSG` (withdrawn).

## What it does not hold

- The flue gas particulate (FGP) and flue gas desulfurization (FGD) design details, and the stacks themselves (only
  their ids, in `x_stack_flue_ids`).
- EIA-860's other schedules: the multifuel schedule is in `eia860_multifuel_generators` (`eia860_schedules.md`), the
  generator file of the zip in `eia860m_operating_generators` and its siblings, the plant file in `eia860_plants_annual`.
- Coordinates and capacity: `lat`, `lon` and `capacity_mw` are empty (the plant's coordinates are in
  `eia860_plants_annual`).
- A decoding of EIA's codes (equipment types, fuels, strategies): they are kept as EIA gives them.
- Earlier years, which EIA moves to `/archive/`, and the early release of a newer year.
