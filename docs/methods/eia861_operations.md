# EIA-861 operational data by utility

Energy Research Warehouse (ERW), method note written in session 891 (chain 048) for tables first written on 23 October 2026.

Tables: `eia861_operational_data`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-861 Annual Electric Power Industry Report, the operational data
file (`Operational_Data_<year>.xlsx`, sheets `States` and `Territories`), inside `f861<year>.zip`, page
`https://www.eia.gov/electricity/data/eia861/`. The zips are the ones `eia861_sales.py` saved in `warehouse/raw/eia861/`
(rows retrieved 21 October 2026); session 882 made no request. Connector: `warehouse/connectors/eia861_operations.py`.
The ERW's utility sales tables from EIA stand beside it (`eia861_utility_sales`, and `eia861_short_form` for the small
utilities).

## Vintage and revision

Data years 2015 to 2025 when written (run `20261023T043123Z`). A run reads the years given with `--years` and writes
the table whole. 2015 to 2024 come from zips under EIA's `/archive/zip/`, 2025 from `/zip/`. EIA's robots file
disallows `/archive/` (session 666): such a year is read only from a zip already saved, never asked for.

Utilities a year: about 2,290 from 2015 to 2018, 3,360 in 2019, about 1,715 from 2020. EIA moved the small utilities to
the short form from 2020 (as session 881 found for efficiency); `eia861_short_form` holds their sales. 2019 holds more
rows than the years around it (84,000 against 24,344 to 33,118 in the other years).

## Shape and variables

Series. `entity` `eia861_op:<utility>:<state>`, with no balancing authority: EIA gives one row for each utility and
state. `ts_utc` the data year's 1 January, `freq` `P1Y`, `geo` `US-<state>`, `node` the utility's name. EIA's own fields:
`x_utility_number`, `x_state`, `x_ownership` (EIA's ownership type), `x_nerc_region` (as EIA writes it: when written,
empty in 44,256 rows, and in some rows two regions or lower case) and `x_data_type` (O observed, I imputed; when written,
every row is O).

| Variable | Unit | What it is |
|---|---|---|
| `summer_peak_demand`, `winter_peak_demand` | `MW` | summer and winter peak demand |
| `net_generation` | `MWh` | source: net generation |
| `wholesale_purchases` | `MWh` | source: wholesale power purchases |
| `exchange_received`, `exchange_delivered`, `exchange_net` | `MWh` | source: exchange energy received, delivered, and net power exchanged |
| `wheeled_received`, `wheeled_delivered`, `wheeled_net` | `MWh` | source: wheeled power received, delivered, and net wheeled power |
| `transmission_by_others_losses` | `MWh` | source: losses of transmission by others |
| `total_sources` | `MWh` | total sources |
| `retail_sales` | `MWh` | disposition: EIA's "Retail Sales" (to 2024) and "Sales to Ultimate Customers" (2025), one variable |
| `sales_for_resale` | `MWh` | disposition: sales for resale |
| `furnished_without_charge`, `consumed_without_charge` | `MWh` | disposition: furnished without charge, consumed by the respondent without charge |
| `energy_losses` | `MWh` | disposition: total energy losses |
| `total_disposition` | `MWh` | total disposition |
| `revenue_retail_sales`, `revenue_delivery_customers`, `revenue_sales_for_resale` | `USD` | revenue from retail sales, delivery customers, sales for resale (EIA's thousand dollars times 1,000) |
| `revenue_credits_adjustments`, `revenue_transmission`, `revenue_other`, `revenue_total` | `USD` | revenue from credits or adjustments, transmission, other, and the total (EIA's thousand dollars times 1,000) |

Net figures can be negative. When written, 2,922 rows are below zero, most of them `transmission_by_others_losses`
(1,041), `revenue_credits_adjustments` (880), `revenue_other` (460) and `exchange_net` (407).

When written: 367,768 rows, 3,556 utilities, 3,628 entities, 25 variables, 2015 to 2025. All utilities' retail sales:
3,717.6 TWh in 2015, 3,610.9 in 2020, 3,931.7 in 2025.

## Reading the sheets

- Every column is found by its group (the top heading, carried right) and its own heading, not by position, so "Sales
  for Resale" (MWh) and "From Sales for Resale" (USD) cannot be confused. Each sheet must give all 25 figures, each
  once; else the run stops. A heading the map does not know stops the run.
- The Short Form column of 2019 on is read past, as `eia861_programs.py` reads it past.
- EIA's aggregates 88888 and 99999 are left out, as `eia861_sales.py` leaves them.
- A cell EIA leaves "." has no row. Nothing is filled.
- A row EIA gives twice with every field the same is kept once. Two rows under one utility and state with different
  values have no key: both are left out whole and named in the header (chain 030's rule). When written, none.

## License

Public: a work of the U.S. government (EIA's copyright page, record 1 of `license_reads.csv`; `docs/licenses.md`: public,
agrees). Cite "U.S. Energy Information Administration, Form EIA-861".

## Cross-check (session 882)

- Against `eia861_utility_sales`: each utility's retail sales here equal its total sales there (bundled and energy-only
  service; delivery-only left out, as EIA counts a sale once) within 0.1 percent in 20,794 of 20,801 utility-years,
  within 5 percent in 20,799. All utilities: 3,717.6 TWh in 2015 in both tables, 3,610.9 in 2020 in both, 3,931.7
  against 3,931.8 in 2025.
- Within each record, total sources equal total disposition in 22,594 of 22,596.

## What it does not hold

- The small utilities from 2020: EIA's short form (their sales are in `eia861_short_form`).
- A balancing authority.
- One spelling of the NERC region: EIA's, as it writes it.
- EIA's aggregates 88888 and 99999.
- Years before 2015 (the saved zips start at 2015).
