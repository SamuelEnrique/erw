# Togo's electricity a year (INSEED's national yearbook 2024, chapter 25, CEET's figures)

Energy Research Warehouse (ERW), method note written in session 2541 (chain 124) for a table first written on 24 October 2026 (session 2535).

Tables: `inseed_togo_electricity_annual`

## Publisher and address

The Institut National de la Statistique et des Etudes Economiques et Demographiques (INSEED), Togo, its Annuaire Statistique National 2024 (776 pages), chapter 25, tables 25.2 ("Achat et production d'energie") and 25.7 ("Ventes d'electricite"), both from the annual activity reports of CEET, the national utility: `https://inseed.tg/download/7668/`, listed on INSEED's home page. One GET, no key. Source id `inseed_tg:annuaire_2024_ch25`. Connector: `warehouse/connectors/inseed_togo_electricity.py` (session 2535). inseed.tg's robots file closes `/wp-admin/` only (read 993).

## Vintage and revision

2020 to 2024 (sales to 2023), written by run `20261024T211320Z` (the write under the lock, offline), which read the yearbook saved at 2026-10-24T21:01:30Z. The server states no last-modified time, so `vintage` is empty. Each year's yearbook has its own address.

## Shape and variables

Series, 55 rows, 11 entities. `entity` `inseed:tg:<item>`; `unit` MWh (INSEED's GWh times 1,000); `ts_utc` the year's first day; `freq` P1Y; `geo` TG; `node` and `x_label` INSEED's label.

| `variable` | Items | 2024, GWh |
|---|---|---|
| `purchases` | vra_tcn_sbee_nangbeto (through the CEB), sbee_crossborder, ecg_crossborder, snpt, total | 991.38 (983.53 through the CEB) |
| `gross_production` | ceet, contourglobal | 4.90, 530.51 |
| `net_production` | kep | 439.44 |
| `production` | amea | 120.65 |
| `sales` | low_voltage, medium_voltage, total | 1,500 in 2023; 2024 given as "-" |

## Reading the source

- The run stops at once, asking nothing, while `inseed_tg` or inseed.tg is paused.
- One request a run (timeout 300 seconds); `--offline` reads the saved yearbook. The run reads every page's text to find chapter 25 (about three minutes).
- **The pages:** each table's page holds its title, "RUBRIQUES" and "Source", and no row of dots (the chapter's list of tables).
- **By place, not by text:** each table is read from its page's words. The year headings 2020 to 2024 give the columns; a figure's words no more than 6 points apart make one cell ("1 351"); a cell belongs to the year whose heading's right edge is nearest its own (the figures are right-aligned); the words left of the first year make the label. The page's text alone cannot split "907,98 1 351 983,53".
- **Sums:** purchases' total within 0.2 GWh of its parts (2023's CEB purchase is printed "1 351"), sales within 1 GWh.
- The run stops, and no file is written, for: a table or its page not found, a label not in the map, a row missing, two cells under one year, a year heading missing, a figure of another form, a total that misses its parts.

A cell of "-" is not written. Nothing is filled.

## Not taken: table 25.1

Table 25.1's key figures differ from tables 25.2 and 25.7 of the same chapter: purchases of 1,720 GWh for 2022 and 1,975 GWh for 2023 (25.2: 916.26 and 1,360.05), energy sold of 1,705 GWh for 2023 (25.7: 1,500). Tables 25.2 and 25.7 each sum to their own parts; table 25.1 is not taken.

## License

Internal. INSEED's home page states "Copyright 2024 INSEED - Tous droits reserves" and links no terms of reuse (read 996). Verdict (session 2537): needs written permission. Held from the live set and from Redivis.

## Cross-checks (session 2535)

- `eia_world_electricity_annual`, Togo: the producers' sum is 823.7 GWh in 2022 against EIA's 899.9 GWh (92%) and 633.1 against 716.6 GWh in 2023 (88%); in 2024, 1,095.5 against 709.5 GWh, KEP's net production having risen from 148 to 439 GWh. CEET's purchases include the CEB's Nangbeto plant in Togo, so they are not EIA's imports.

## What it does not hold

- Years before 2020; months; CEET's own production by type in kWh (table 25.4, whose cells wrap); prices (XOF).
