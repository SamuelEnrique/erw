# Bahrain's electricity, a year (EWA's Statistical Book 2024)

Energy Research Warehouse (ERW), method note written in session 2499 (chain 121) for a table first written on 24 October 2026 (session 2490).

Tables: `ewa_bahrain_electricity_annual`

## Publisher and address

The Electricity and Water Authority of the Kingdom of Bahrain (EWA), its Statistical Book 2024 (66 pages), linked from `https://www.ewa.bh/en/publications` and served from an S3 bucket: `https://ewa-new-website-ireland.s3.eu-west-1.amazonaws.com/uploads/book_2024_final_p_1.pdf`. One GET, no key. Source id `ewa:statistical_book`. Connector: `warehouse/connectors/ewa_bahrain_electricity.py` (session 2490). www.ewa.bh's robots file allows every path (read 814); the bucket answers HTTP 403 for a robots file, S3's answer for an object that is not there (read 818).

The session was planned for Qatar. Kahramaa's www.km.qa and km.qa served a firewall's "Request Rejected" page for their robots files (reads 810, 811), the Planning and Statistics Authority's www.psa.gov.qa did not answer (read 812), and www.data.gov.qa's robots file closes `/api/` and every download to all but Googlebot (read 813). Bahrain replaced it.

## Vintage and revision

2020 to 2024, written by run `20261024T162744Z` (the write under the lock, offline), which read the book saved at 2026-10-24T14:52:18Z (`retrieved_at`). `vintage` is its last-modified time, 2025-09-03T11:13:49Z. A saved book is reused unless `--fresh`; the next edition will have its own address.

## Shape and variables

Series, 135 rows, 16 entities, 10 variables. `entity` `ewa:bh:<item>`; `ts_utc` the year's 1 January; `freq` P1Y; `geo` BH; `node` and `x_label` the column as EWA heads it; `x_page` the book's page.

| Table (page) | `variable` | Items | Unit |
|---|---|---|---|
| Electricity Production from Power Stations and Other Sources (9) | `sent_out`; `net_imports`; `supply` | the six stations (Sitra, Riffa, Al-Hidd, Al-Ezzel, Al-Dur, Al-Dur 2); the GCC and ALBA links; `total` | MWh |
| Total Generated Electricity Units (10) | `sent_out` | `ewa_stations`, `ipp_stations` | MWh |
| Power Stations and Other Sources Installed Capacity (12) | `max_generation_capacity` (at 40 degrees C); `net_transfer_capacity`; `capacity_with_links` | the stations; the links; `total` | MW |
| Development of Maximum & Minimum Load (15) | `peak_load`, `minimum_load`, `installed_capacity` | `system` | MW |
| Electricity Consumption by Sectors (44) | `consumption` | domestic, commercial, industrial, agricultural, `total` | MWh |

- EWA gives energy in GWh (consumption in million kWh): each is multiplied by 1,000.
- A link's negative flow is power sent from Bahrain's grid to the link, as EWA notes under the table.
- Riffa's units sent out, and so EWA's own stations' (`ewa_stations`), are negative in 2022 to 2024 (-4.5, -5.4 and -7.5 GWh), as printed: the station drew more from the grid than it sent out. With the links' negative years, 14 values are below zero.
- `supply` is the stations' units sent out plus the links' net flows (2020: 17.62 TWh = 5,966 + 4,607 + 5,775 + 792 + 753 GWh sent out, less 223 and 50 GWh to the links).

| | 2020 | 2022 | 2024 |
|---|---|---|---|
| Supply, TWh | 17.62 | 18.66 | 19.87 |
| Peak load, MW | 3,662 | 3,708 | 3,900 |
| Consumption, TWh | 16.52 | 18.29 | 19.01 |

## Reading the source

- The run stops at once, asking nothing, while `ewa_bahrain_statistics`, the bucket or www.ewa.bh is paused.
- One request a run (timeout 180 seconds); `--offline` reads the saved book.
- **Finding the tables:** each page whose text holds one of the five English titles. The text is read with the characters drawn in white dropped: the book keeps an older edition's years in white under the visible ones (page 44 reads "20220014" for 2020 without the filter). Arabic-Indic digits (U+0660 to U+0669, U+06F0 to U+06F9) are read as their ASCII digits.
- **The rows:** the first five lines after a title that end in a year and hold only figures, "-" or percentages, the years 2020 to 2024 in order.
- **Checks that stop the run:** page 10's total and imports against page 9's sums (within 1 GWh); a table not found once, a row of another width, years not 2020 to 2024 in order, a key given twice.
- **Cells without a row:** "-" (none); a cell out of its table's form, counted in the header (one: 2023's commercial consumption, printed "5.348" in a table of whole numbers; the year's total, 16,423, equals the sectors' sum with 5,348).

Nothing is filled. Not taken: the load table's ratio and increase columns, the transmission network, the fuel tables, the water tables, the tariffs (BHD).

## License

Internal. EWA's terms of use (read 816): "This website contains materials which are owned by or licensed to us. ... Reproduction is prohibited other than in accordance with the copyright notice, which forms part of these terms and conditions." Verdict (session 2495): needs written permission. Held from the Redivis storage and the live set.

## Cross-checks (session 2490)

- Within the book: page 10's EWA and IPP production equal page 9's stations (2021: 400 GWh = Riffa 308 + Sitra 92; IPP 18,048 = Al-Dur 2, Al-Dur, Al-Ezzel and Al-Hidd); page 9's total equals its parts each year.
- `supply` over `owid_ember_electricity_annual`'s demand for Bahrain: 0.508 to 0.548 (2020 to 2024). Ember's demand includes the aluminium smelter ALBA's own generation, which EWA's grid figures do not; the ALBA link's flows are only the exchange with the grid.

## What it does not hold

- Years before 2020 (earlier books); monthly figures; ALBA's captive generation; prices (BHD).
