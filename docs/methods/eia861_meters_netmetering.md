# EIA-861 advanced meters and net metering by utility

Energy Research Warehouse (ERW), method note written in session 877 (chain 047) for tables first written on 23 October 2026.

Tables: `eia861_advanced_meters`, `eia861_net_metering`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-861 Annual Electric Power Industry Report, the advanced meters
file (`Advanced_Meters_<year>.xlsx`, sheets `States` and `Territories`) and the net metering file
(`Net_Metering_<year>.xlsx`, its utility-level sheets only), inside `f861<year>.zip`, page
`https://www.eia.gov/electricity/data/eia861/`. The zips are the ones `eia861_sales.py` saved in `warehouse/raw/eia861/`
(rows retrieved 21 October 2026); session 869 made no request. Connector:
`warehouse/connectors/eia861_meters_netmetering.py`. The ERW's state tables from EIA stand beside them
(`eia_meters_state_annual`, `eia_net_metering_state_annual`).

## Vintage and revision

Data years 2015 to 2025 when written (run `20261023T032005Z`). A run reads the years given with `--years` and writes
each table whole. 2015 to 2024 come from zips under EIA's `/archive/zip/`, 2025 from `/zip/`. EIA's robots file
disallows `/archive/` (session 666): such a year is read only from a zip already saved, never asked for.

The net metering file changed its layout five times in eleven years. The variable names follow EIA's headings, so a name
changes where EIA's heading changed (below). The session 869 report places EIA's change from "customers" to
"installations" in 2023, the batteries from 2024, and the meters' customers with daily digital access and direct load
control from 2020. The table as written holds installations from 2021, batteries from 2023, and those two meter groups
from 2015.

## Shape and variables

Series. `entity` `eia861_am:<utility>:<state>:<balancing authority>` or `eia861_nm:<utility>:<state>:<balancing
authority>`; the balancing authority is empty where EIA gives none (net metering: every row of 2015 and 2016). `ts_utc`
the data year's 1 January, `freq` `P1Y`, `geo` `US-<state>`, `node` the utility's name. EIA's own fields:
`x_utility_number`, `x_state`, `x_ba_code`.

A variable is EIA's headings joined: the group (a meter kind, or a technology and its measure), then the sector
(`residential`, `commercial`, `industrial`, `transportation`, `total`). The unit is read from the heading: a count where
the heading names customers, installations, number or meters; else MWh where it names MWh; else MW where it names MW;
else a count. So "virtual customers, 1 MW and over" is a count, not MW (a first trial gave it MW; session 869 fixed it).

`eia861_advanced_meters` (40 variables a year, 45 in all):

| Variable group (then `_<sector>`) | Unit | Years |
|---|---|---|
| `number_amr_automated_meter_reading` | `count` | 2015 to 2025 |
| `number_ami_advanced_metering_infrastructure` | `count` | 2015 to 2025 |
| `number_home_area_network` | `count` | 2015 to 2025 |
| `number_non_amr_ami_meters` | `count` | 2015 to 2019 |
| `number_standard_non_amr_ami_meters` (EIA's heading from 2020) | `count` | 2020 to 2025 |
| `total_numbers_of_meters` | `count` | 2015 to 2025 |
| `energy_served_ami_mwh` | `MWh` | 2015 to 2025 |
| `customers_with_daily_digital_access` | `count` | 2015 to 2025 |
| `customers_with_direct_load_control` | `count` | 2015 to 2025 |

`eia861_net_metering` (60 variables in 2015, 80 a year from 2016 to 2022, 110 a year from 2023; 170 in all). Technologies
`photovoltaic`, `wind`, `other`, and the sum across them, `total` in 2015 and `all_technologies` from 2016:

| Variable group (then `_<sector>`) | Unit | Years |
|---|---|---|
| `<technology>_capacity_mw` | `MW` | 2015 to 2025 |
| `<technology>_customers` | `count` | 2015 to 2020 |
| `<technology>_installations` (EIA's new word for the same count) | `count` | 2021 to 2025 |
| `<technology>_energy_sold_back_mwh` | `MWh` | 2015 to 2025 |
| `photovoltaic_storage_capacity_mw` (storage paired with PV) | `MW` | 2016 to 2022 |
| `photovoltaic_storage_customers`, then `photovoltaic_storage_installations` | `count` | 2016 to 2020, 2021 to 2022 |
| `photovoltaic_virtual_capacity_mw`, `photovoltaic_virtual_customers` (virtual net metering) | `MW`, `count` | 2016 to 2022 |
| `photovoltaic_virtual_capacity_under_1_mw_mw`, `photovoltaic_virtual_capacity_1_mw_and_over_mw` | `MW` | 2023 to 2025 |
| `photovoltaic_virtual_customers_under_1_mw`, `photovoltaic_virtual_customers_1_mw_and_over` | `count` | 2023 to 2025 |
| `battery_pv_paired_` and `battery_not_pv_paired_` `battery_capacity_mw` | `MW` | 2023 to 2025 |
| the same two, `energy_capacity_mwh` | `MWh` | 2023 to 2025 |
| the same two, `installations` | `count` | 2023 to 2025 |

When written:

- `eia861_advanced_meters`: 497,838 rows, 2,932 utilities, 3,332 entities, 45 variables, 2015 to 2025.
- `eia861_net_metering`: 507,206 rows, 1,336 utilities, 2,507 entities, 170 variables, 2015 to 2025.
- Archived together: 1,005,044 rows.

2019 holds more rows than the years around it (advanced meters 56,874 against 42,312 to 46,082; net metering 104,960
against 32,504 to 46,235, 79 percent of them zero). EIA gives no short-form file for 2019, and its 2019 files carry the
short-form utilities.

## Reading the sheets

- Every column is found by its stacked headings, not by position (the reader of `eia861_programs.py`). EIA's "Utility
  Level Data" heading is dropped from the name.
- A column whose last heading is not a sector is read past and named in the header. When written, one in net metering:
  "photovoltaic / capacity mw / type", a text field.
- Net metering: only the utility-level sheets. EIA's TPO (third-party owned) and state-level sheets are aggregates and
  are not taken.
- EIA's aggregates 88888 and 99999 are left out, as `eia861_sales.py` leaves them.
- A cell EIA leaves "." has no row. Nothing is filled.
- A row EIA gives twice with every field the same is kept once. Two rows under one key with different figures have no
  key: both are left out whole and named in the header (chain 030's rule). When written, none in either table.

## License

Public: a work of the U.S. government (EIA's copyright page, record 1 of `license_reads.csv`; `docs/licenses.md`: public,
agrees for both tables). Cite "U.S. Energy Information Administration, Form EIA-861".

## Cross-check (session 869)

Against the ERW's state tables:

- AMI meters summed by state equal `eia_meters_state_annual` in all 255 state-years (2015 to 2019, the years in common).
- Net-metered PV capacity summed by state against `eia_net_metering_state_annual`: a median ratio of 1.0000, 77 percent
  within 1 percent. The state table carries EIA's state-level figures, which hold more than the utilities' rows.

## What it does not hold

- EIA's TPO and state-level net metering sheets (aggregates; the state figures are in `eia_net_metering_state_annual`).
- The text column "photovoltaic / capacity mw / type".
- One name for a measure across the years: a reader joins `customers` to 2020 with `installations` from 2021, and
  `total` in 2015 with `all_technologies` from 2016, by hand.
- EIA's aggregates 88888 and 99999.
- Years before 2015 (the saved zips start at 2015).
