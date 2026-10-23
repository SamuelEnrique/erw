# EIA-923 Schedule 2 fuel receipts and costs by plant

Energy Research Warehouse (ERW), method note written in session 905 (chain 049) for tables first written on 23 October 2026.

Tables: `eia923_fuel_receipts`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-923, Schedule 2: the sheet "Page 5 Fuel Receipts and Costs" of
the workbook `EIA923_Schedules_2_3_4_5_M_<month>_<year>_<date>.xlsx`, inside the yearly zip `f923_<year>.zip`, page
`https://www.eia.gov/electricity/data/eia923/`. The zip is the one `eia923_monthly.py` saved in
`warehouse/raw/eia923_monthly/` (`https://www.eia.gov/electricity/data/eia923/xls/f923_2025.zip`, retrieved
2026-10-23T06:29:28Z); session 900 made no request. Connector: `warehouse/connectors/eia923_receipts.py`, which reads
the same zips under the monthly connector's name.

## Vintage and revision

January to December 2025 when written (run `20261023T064121Z`, workbook `EIA923_Schedules_2_3_4_5_M_12_2025_Final.xlsx`).
A run reads the years given with `--years` and writes the table whole. A year not saved is asked for at
`xls/f923_<year>.zip`, outside `/archive/`, which EIA's robots file disallows: one request a year.

## Shape and variables

Events, one row a delivery. EIA gives a delivery no id.

- `event_id` `eia923r:<plant id>:<year>-<month>:<hash>`, the hash the first 12 characters of the SHA-1 of the row's
  fields, joined with "|".
- `event_date` the receipt month's first day. `event_type` `fuel_receipt`. `parties` the supplier as EIA names it.
- `entity_ids`, `mw`, `price`, `currency` and `status` are empty. The fuel cost is in cents per MMBtu, which the events
  shape's price (per MWh) does not fit; it is kept in `x_fuel_cost`.
- `x_*` EIA's columns, its headings as names (lower case, other characters as `_`). EIA's YEAR is not kept;
  `x_month` is.

| Column | Unit | What it is |
|---|---|---|
| `x_plant_id`, `x_plant_name`, `x_plant_state` | | the plant |
| `x_operator_name`, `x_operator_id`, `x_balancing_authority_code` | | its operator and balancing authority |
| `x_purchase_type` | | C contract, S spot; T and NC as EIA gives them |
| `x_contract_expiration_date` | | the contract's expiry as EIA gives it (for example 1225; "." in 21,987 rows) |
| `x_energy_source`, `x_fuel_group` | | the energy source code and fuel group |
| `x_coalmine_type`, `x_coalmine_state`, `x_coalmine_county`, `x_coalmine_msha_id`, `x_coalmine_name` | | the coal mine |
| `x_supplier` | | the supplier (also in `parties`) |
| `x_quantity` | `x_quantity_unit` | the quantity received |
| `x_average_heat_content` | MMBtu per unit | heat content |
| `x_average_sulfur_content`, `x_average_ash_content`, `x_moisture_content` | percent by weight | sulfur, ash, moisture |
| `x_average_mercury_content`, `x_chlorine_content` | ppm | mercury, chlorine |
| `x_fuel_cost` | cents per MMBtu | EIA's FUEL_COST: all costs of purchase and delivery to the plant |
| `x_regulated` | | REG or UNR |
| `x_primary_transportation_mode`, `x_secondary_transportation_mode` | | the transport modes |
| `x_natural_gas_supply_contract_type`, `x_natural_gas_delivery_contract_type` | | the gas contract types |
| `x_reporting_frequency` | | M or A |

`x_quantity_unit` by fuel group, as EIA's layout states tons, barrels or Mcf: Coal and Petroleum Coke `short_ton`,
Petroleum `bbl`, Natural Gas and Other Gas `Mcf`.

When written: 36,733 receipts, 967 plants, 2025-01 to 2025-12. By fuel group: Natural Gas 27,537, Coal 6,616 (201
plants), Petroleum 2,543, Petroleum Coke 37; no Other Gas. `x_fuel_cost` is given on every row.

## Reading the sheets

- The heading row is the one, among the first ten, whose first cell is "YEAR". It must name the year, month, plant id,
  fuel group, supplier, quantity and fuel cost, and no heading twice; else the run stops.
- A row with no fuel group (EIA's footnotes) is read past. Only rows whose YEAR is the year asked are taken.
- A fuel group not in the unit map stops the run.
- A row repeated with every field the same is kept once and counted (chain 030's rule): 51 when written. EIA gives no
  delivery id, so two such rows may be two deliveries; the header says so.
- Two different rows under one id stop the run.
- Cells are read as text: runs of spaces become one, and a whole number is written without its decimal. Nothing is
  filled.

## License

Public: a work of the U.S. government (EIA, record 1 of `license_reads.csv`). Cite "U.S. Energy Information
Administration, Form EIA-923".

## Cross-check (session 900)

Against `eia_coal_receipts_annual` (session 875, EIA's coal API) by plant for 2025: the coal deliveries summed equal the
annual table within 1 percent for 145 of the 166 plants both hold, and within 5 percent for 147. In total there are
381.0 million short tons here against 372.4 million there, which leaves out records without a key. 201 plants received
coal here.

## What it does not hold

- An id of EIA's for a delivery: `event_id` is made from the row.
- A price per MWh: the cost is in `x_fuel_cost`, cents per MMBtu.
- The workbook's other pages: page 1 is in `eia923_plant_fuel_monthly`.
- EIA's footnote rows, and a second copy of a row repeated with every field the same.
- Years other than 2025 when written.
