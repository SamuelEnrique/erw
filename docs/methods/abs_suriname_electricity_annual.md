# Suriname's electricity a year: EBS's demand, generation and capacity, Staatsolie's generation (ABS's Environment Statistics 2024)

Energy Research Warehouse (ERW), method note written in session 2569 (chain 126) for a table first written on 25 October 2026 (session 2563).

Tables: `abs_suriname_electricity_annual`

## Publisher and address

The Algemeen Bureau voor de Statistiek in Suriname (ABS), its eleventh Milieustatistieken Publicatie / Environment Statistics Publication (December 2024, 452 pages), chapter 7, tables 7.1, 7.4, 7.8 and 7.9, whose sources are N.V. EnergieBedrijven Suriname (EBS) and Staatsolie: `https://statistics-suriname.org/wp-content/uploads/2024/12/Elfde-Milieustatistieken-pub-dec-2024.pdf` (23.4 MB). One GET, no key. Source id `abs_sr:milieustatistieken_2024_tables_7_1_7_4_7_8_7_9`. Connector: `warehouse/connectors/abs_suriname_electricity.py` (session 2563). statistics-suriname.org's robots file closes nothing and asks a crawl delay of 30 seconds (read 1066).

## Vintage and revision

Written by run `20261025T003517Z` (the write under the lock, offline), which read the publication saved at 2026-10-25T00:27:21Z. `vintage` is its last-modified time, 2024-12-31T08:40:24Z. The publication appears every two years, each at its own address.

## Shape and variables

Series, 56 rows, 9 entities. `ts_utc` the year's first day; `freq` P1Y; `geo` SR; `node` ABS's label (English part); `x_table` the table.

| `variable` | `entity` | Table | Years | Unit | 2023 |
|---|---|---|---|---|---|
| `demand` | `abs_sr:ebs:<category>`: `residential`, `commercial`, `industrial`, `other`, `total` | 7.4 | 2019 to 2023 | MWh (kWh divided by 1,000) | total 1,408.1 GWh |
| `net_generation`, `net_consumption` | `abs_sr:ebs` | 7.8 | 2019 to 2023 | MWh (billion kWh times 1,000,000) | 1,470 and 1,377 GWh |
| `generation` | `abs_sr:staatsolie:<plant>`: `afobaka_hydro`, `tout_lui_faut_thermal` (GWh times 1,000), `saramacca_backup` (MWh as given) | 7.9 | 2019 to 2023 | MWh | 937 GWh, 327 GWh, 218 MWh |
| `installed_capacity`, `available_capacity` | `abs_sr:ebs` | 7.1 | 2019 to 2021 | MW | 2021: 247.4 and 192.7 |

Table 7.4's total holds its four categories.

## Reading the source

- The run stops at once, asking nothing, while `abs_sr` or statistics-suriname.org is paused.
- One request a run (timeout 300 seconds); `--offline` reads the saved publication.
- **Each table** is found by its title line as printed above the table (the contents page prints the titles run together with others, so a full-line match finds the table's own), and read from its title to its "Bron" line. The years come from the title and must stand in the table's header line ("#", ABS's mark for revised figures, removed).
- **Table 7.8** prints its billions with a comma for 2019 to 2021 ("1,366") and a point for 2022 and 2023 ("1.377"): both are read as the decimal; every figure must fall between 0.5 and 5 billion kWh, and net consumption below net generation.
- **Table 7.9:** each plant's figures are on the line below its label, the unit (MWh or GWh) first.
- **Checks:** 7.4's categories to its total within 1 MWh each year; 7.1's available capacity not above its installed.
- The run stops, and no file is written, for: a title found other than once, a row or a plant's line missing, a figure count that is not the years', a check missed.

Nothing is filled. Not taken: the connections (7.2, 7.3), the sales by district (7.5: its total, 132.7 GWh in 2023, does not agree with table 7.4's 1,408.1 GWh), the prices (7.6, SRD), and 7.8's capacity in GW.

## License

Public. ABS's home page (read 1069): "Except where otherwise noted, content on this site is licensed under a Creative Commons Attribution 4.0 International license."; the publication notes no other license (its colophon: "Copyright December 2024 Algemeen Bureau voor de Statistiek (ABS)"). Verdict: may be public. Cited as ABS's, with EBS and Staatsolie as the tables' sources. In the release package; held from the live set.

## Cross-check

EIA's 2023 hydro generation for Suriname (900 GWh, `eia_world_electricity_annual`) against Afobaka's 937 GWh; EIA's total generation (1,731.5 GWh) against EBS's net generation (1,470 GWh): EIA's country covers more than EBS's grid.
