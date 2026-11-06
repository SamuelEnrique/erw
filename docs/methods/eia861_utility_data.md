# EIA-861 utility data: each utility's NERC region, RTOs and activities

Energy Research Warehouse (ERW), method note written in session 877 (chain 047) for tables first written on 23 October 2026.

Tables: `eia861_utility_data`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-861 Annual Electric Power Industry Report, the utility data file
(`Utility_Data_<year>.xlsx` inside `f861<year>.zip`, sheets `States` and `Territories`), page
`https://www.eia.gov/electricity/data/eia861/`. The zips are the ones `eia861_sales.py` saved in `warehouse/raw/eia861/`
(rows retrieved 21 October 2026); session 867 made no request. Connector: `warehouse/connectors/eia861_utility_data.py`.

## Vintage and revision

Data years 2015 to 2025 when written (run `20261023T030550Z`). A run reads the years given with `--years` and writes the
table whole. 2015 to 2024 come from zips under EIA's `/archive/zip/`, 2025 from `/zip/`. EIA's robots file disallows
`/archive/` (session 666): such a year is read only from a zip already saved, never asked for.

## Shape and variables

Entities. One row is one row of EIA's sheet: one utility in one year, under one state.

- `entity_id` `eia861_utility:<utility number>:<state>:<year>`; `entity_type` `utility`; `name` the utility's name;
  `geo` `US-<state>`, or `US` for the 10 rows EIA gives with no state; `status_date` the data year's 1 January. The
  other standard columns (`lat`, `lon`, `capacity_mw`, `status`, `operator`) are empty.
- EIA's own fields: `x_utility_number`, `x_state`, `x_year`, `x_ownership` (EIA's words: Municipal, Cooperative, Retail
  Power Marketer, Investor Owned and others), `x_nerc_region` (the region as EIA writes it, not cleaned: it holds
  variants such as `MISO`, `ERCOT` and lower-case `serc`, and is empty in 3,365 rows), `x_short_form` (Y only in 2019,
  1,038 rows: EIA's 2019 files carry the short-form utilities).
- Flags, each as EIA gives it (Y, N or empty), no unit:
  - `x_nerc_<region>`: the other NERC regions the utility also operates in (`tre`, `frcc`, `mro`, `npcc`, `rfc`,
    `serc`, `spp`, `wecc`).
  - `x_rto_<rto>`: the RTOs it operates in (`caiso`, `ercot`, `pjm`, `nyiso`, `spp`, `miso`, `isone`, `other`).
  - Activities: `x_generation`, `x_transmission`, `x_buying_transmission`, `x_distribution`, `x_buying_distribution`,
    `x_wholesale_marketing`, `x_retail_marketing`, `x_bundled`, `x_alt_fuel_vehicle`, `x_alt_fuel_vehicle_2`.
- `x_rtos`: the RTOs marked Y, joined by `;` (an ERW field for reading; filled in 16,358 rows).

When written: 22,716 rows, 3,542 utilities. Rows a year: 2,273 to 2,296 from 2015 to 2018, 3,339 in 2019, 1,696 to
1,720 from 2020 to 2025.

## Reading the sheets

- Every column is found by its heading and the group heading above it ("Also operating in other NERC regions",
  "Operating in these RTOs", "Other activities"). EIA names a NERC region and an RTO both "SPP"; the group heading tells
  them apart.
- EIA's aggregates 88888 (Withheld) and 99999 (Adjustment) are not utilities and are left out, as `eia861_sales.py`
  leaves them.
- A flag stays as EIA gives it. N and an empty cell are kept apart (session 867's decision).
- A key given twice stops the run; none was found.
- EIA lists a utility once a year, under one state, though it may sell in several (the sales table has a row for each
  state).

## License

Public: a work of the U.S. government (EIA's copyright page, record 1 of `license_reads.csv`; `docs/licenses.md`: public,
agrees). Cite "U.S. Energy Information Administration, Form EIA-861".

## Cross-check (session 867)

- By utility and year, 99.0 percent of `eia861_utility_sales`' utilities are here. By utility, state and year only 62
  percent, since EIA lists one state.
- The ERCOT flag falls on Texas in 1,382 rows (of 1,716 marked Y; the rest are retail marketers registered elsewhere).
  CAISO's falls on California in 722 (of 1,001).

## What it does not hold

- A utility's other states: one state a year, as EIA lists it.
- EIA's aggregates 88888 and 99999.
- A cleaned NERC region: `x_nerc_region` is EIA's text.
- Years before 2015 (the saved zips start at 2015).
