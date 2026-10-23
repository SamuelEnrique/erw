# EIA-861 delivery-only companies: Texas's wires utilities

Energy Research Warehouse (ERW), method note written in session 862 (chain 046) for a table first written on 23 October 2026.

Tables: `eia861_delivery_only`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-861 Annual Electric Power Industry Report. The file is
`Delivery_Companies_<year>.xlsx`, sheet "Delivery Companies", inside the annual zip `f861<year>.zip`. Page:
`https://www.eia.gov/electricity/data/eia861/`. Zips: `https://www.eia.gov/electricity/data/eia861/zip/f8612025.zip`
for 2025, and `https://www.eia.gov/electricity/data/eia861/archive/zip/f861<year>.zip` for 2020 to 2024. Connector:
`warehouse/connectors/eia861_delivery.py` (session 853). It reuses `eia861_sales.py`'s own reader (`sheet_rows`), since
the sheet has the layout of the sales file's part C rows. EIA calls the file "Delivery Companies"; the table keeps the
chain's name.

## Vintage and revision

Annual, 2020 to 2025 when written. The file starts with 2020; the 2015 to 2019 zips have none. Session 853 made no
request: it read the zips `eia861_sales.py` had saved in `warehouse/raw/eia861/` (retrieved 21 October 2026). EIA's
robots file disallows `/archive/` (session 666), so a year there is read only from a zip already saved. A run writes the
years it is given as a snapshot. Ceiling two requests a year (the page and the zip), none when both are saved.

## Shape and variables

Series. `entity` `eia861:<utility number>:TX:C:ERCO`, the same form as `eia861_utility_sales`; `ts_utc` the data year's
1 January; `freq` `P1Y`; `geo` `US-TX`; `node` the company's name. Extra columns, as the sales table: `x_utility_number`,
`x_state` (TX), `x_part` (C), `x_service_type` (Delivery), `x_ownership` (Investor Owned, Cooperative, Municipal),
`x_ba_code` (ERCO), `x_data_type` (O, observed). The rows' `source` is `eia:eia861`, the sales reader's; the header and
`sources.csv` name `eia:eia861:delivery_companies`.

| Variable | Unit | What it is |
|---|---|---|
| `<sector>_revenue` | USD (EIA's thousand dollars times 1,000) | delivery revenue |
| `<sector>_sales` | MWh | energy delivered |
| `<sector>_customers` | count | customers |

Sectors: `residential`, `commercial`, `industrial`, `transportation`, `total` (15 variables). Observed rows only; a "."
cell has no row; nothing is filled.

The companies (EIA utility number): AEP Texas Central Company (3278), AEP Texas North Company (20404), CenterPoint Energy
(8901), Oncor Electric Delivery Company LLC (44372), Texas-New Mexico Power Co (40051), Nueces Electric Cooperative
(13830), and the City of Lubbock (11292, 2024 and 2025 only). Six a year to 2023, seven from 2024.

When written: 546 rows, 7 companies, 2020 to 2025. 38 rows for each residential, commercial, industrial and total
variable; 30 for each transportation variable.

## License

Public: a work of the U.S. government (EIA's copyright page, record 1 of the license reads, `docs/licenses.md`). Verdict
in `docs/licenses.md`: public. Cite "U.S. Energy Information Administration, Form EIA-861".

## Cross-check (session 853)

- None of the 7 companies is in `eia861_utility_sales`: checked key by key in the run (`--check-sales`). A key in both
  tables would stop the run. So this table moves no figure that reads the sales table.
- In Texas the retail providers file as part D (power marketers, all in ERCOT). The energy the wires companies deliver
  is 1.03 to 1.04 times part D's ERCOT sales every year (2025: 350.7 against 338.3 TWh; 2020: 268.0 against 259.1). The
  rest is Lubbock's and Nueces's own retail customers among the deliveries.
- CenterPoint's delivery revenue: USD 2.42 billion in 2020 and 3.48 billion in 2025.

## What it does not hold

- Years before 2020: the earlier zips have no delivery companies' file.
- Delivery-only (part C) rows of other states: those are in EIA's sales file and in `eia861_utility_sales`
  (11,442 rows).
- Retail sales to the same Texas customers: the retail providers' part D rows are in `eia861_utility_sales`.
- Any cell EIA leaves as "."; nothing is filled.
