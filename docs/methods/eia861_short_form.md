# EIA-861 short form: the small utilities' revenue, sales and customers

Energy Research Warehouse (ERW), method note written in session 877 (chain 047) for tables first written on 23 October 2026.

Tables: `eia861_short_form`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-861 Annual Electric Power Industry Report, the short form file
(Form EIA-861S, `Short_Form_<year>.xlsx` inside `f861<year>.zip`, its first sheet, `861S`), page
`https://www.eia.gov/electricity/data/eia861/`. The zips are the ones `eia861_sales.py` saved in `warehouse/raw/eia861/`
(rows retrieved 21 October 2026); session 876 made no request. Connector: `warehouse/connectors/eia861_short_form.py`.

## Vintage and revision

Data years 2015 to 2018 and 2020 to 2025 when written (run `20261023T034323Z`). EIA gives no short-form file for 2019:
that year's short-form utilities are in EIA's main files (`eia861_utility_data` marks them, `x_short_form` Y in 1,038
rows of 2019). A run reads the years given with `--years` and writes the table whole; a year whose zip holds no
short-form file is logged and passed over. 2015 to 2024 come from zips under EIA's `/archive/zip/`, 2025 from `/zip/`.
EIA's robots file disallows `/archive/` (session 666): such a year is read only from a zip already saved, never asked
for.

EIA moved more utilities onto the short form in 2020. The file's sales are 27 to 28 TWh a year to 2018 and 87 to 93 TWh
from 2020, so a reader should not read the step as growth.

## Shape and variables

Series. `entity` `eia861_sf:<utility>:<state>:<balancing authority>` (the balancing authority empty where EIA gives
none). `ts_utc` the data year's 1 January, `freq` `P1Y`, `geo` `US-<state>`, `node` the utility's name.

| Variable | Unit | What it is |
|---|---|---|
| `total_revenue` | `USD` | the utility's total revenue (EIA's thousand dollars times 1,000) |
| `total_sales` | `MWh` | its total retail sales |
| `total_customers` | `count` | its total customers |

EIA's own fields: `x_utility_number`, `x_state`, `x_ownership` (Municipal, Cooperative, Political Subdivision, Investor
Owned, Federal, State), `x_ba_code`. The programs the utility marks, Y, N or empty as EIA gives them:
`x_water_heater`, `x_net_metering`, `x_demand_side_management`, `x_time_based_programs`. When written,
`x_water_heater` holds no Y or N: EIA's "." in 40,831 rows and empty in 3,339.

When written: 44,170 rows, 1,721 utilities, 1,780 entities. Utilities a year: 1,088 to 1,106 from 2015 to 2018, 1,666 to
1,685 from 2020 to 2025.

## Reading the sheet

- Every column is found by its heading, not by position. EIA spells "BA_Code" and "BA Code", "Water Heater" and
  "W_Heater"; both are read. A heading missing stops the run.
- EIA's aggregates 88888 and 99999 are left out, as `eia861_sales.py` leaves them.
- A cell EIA leaves "." has no row. Nothing is filled.
- A row EIA gives twice with every field the same is kept once. Two rows under one key with different figures have no
  key: both are left out whole and named in the header (chain 030's rule). When written, none.

## License

Public: a work of the U.S. government (EIA's copyright page, record 1 of `license_reads.csv`; `docs/licenses.md`: public,
agrees). Cite "U.S. Energy Information Administration, Form EIA-861".

## Cross-check (session 876)

`eia861_utility_sales` takes observed rows only and leaves out the short-form utilities, which EIA imputes there. None of
the short form's utility-state-years is in that table. The sales table's observed rows (parts A, B, D) plus the short
form reach 99.1 to 99.5 percent of EIA's U.S. retail sales from 2020 (2024: 3,952 of 3,975 TWh), against about 97
percent without the short form.

## What it does not hold

- 2019: EIA gives no short-form file.
- Sales, revenue or customers by sector: the connector reads EIA's total columns only.
- Rows added to `eia861_utility_sales`: this is a table of its own (session 853's rule: a table a page reads is not
  widened from another file).
- EIA's aggregates 88888 and 99999.
- Years before 2015 (the saved zips start at 2015).
