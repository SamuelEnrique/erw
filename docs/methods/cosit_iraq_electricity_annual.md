# Iraq's electricity production by plant type, purchases, sales and losses a year, 2021 to 2024 (COSIT's electricity projects statistics)

Energy Research Warehouse (ERW), method note written in session 2667 (chain 133) for a table first written on 25 October 2026 (session 2661).

Tables: `cosit_iraq_electricity_annual`

## Publisher and address

The Central Statistical Organization, Iraq (COSIT), electricity projects statistics for 2024, Tables 1 to 3, from the Ministry of Electricity's figures. The workbook is `https://cosit.gov.iq/documents/industrial/water&electric/6.xlsx`, listed on the water and electricity projects page (`https://cosit.gov.iq/ar/industrial/electric-water`), no key. Source id `cosit_iq:electricity_projects_2024_tables_1_3`. Connector: `warehouse/connectors/cosit_iraq_electricity.py` (session 2661), whose raw store is `warehouse/raw/cosit_iq/`. cosit.gov.iq's robots file closes Joomla's system paths, `/images/` among them, and not `/documents/` (read 1358).

## Vintage and revision

Written by run `20261025T102043Z` (the write under the lock, offline), which read the workbook retrieved at 2026-10-25T10:17:11Z, last modified 23 February 2026. COSIT publishes a workbook a year, each giving four years.

## Shape and variables

Series, 56 rows, 14 entities, 2021 to 2024. `entity` `cosit:iq:<item>`:
- `steam`, `gas`, `diesel`, `hydro` and `generated` (`generation`, the Ministry's plants);
- `imports_investment` (imported energy and private, investment plants' energy, as COSIT gives them together), `kurdistan` (the energy received from the Kurdistan Region) and `purchased`, their total (`purchases`);
- `total` (`supply`);
- `sold` (`sales`);
- `losses_plants`, `losses_transmission`, `losses_distribution` and `losses_total` (`losses`: internal consumption and losses).

`unit` MWh, as published; `ts_utc` the year's first day; `freq` P1Y; `geo` IQ; `node` the row's English label.

The total was 127.6 TWh in 2021 and 165.6 TWh in 2024. In 2024:
- the Ministry's plants 96.6 (gas 58.3, steam 32.0);
- imports and investment 59.7, and the Kurdistan Region 9.3;
- 67.5 sold;
- internal consumption and losses 98.2, of them 82.0 on the distribution networks.

## Reading the source

- The run stops at once, asking nothing, while `cosit_iq` or cosit.gov.iq is paused.
- One request a run, saved and reused unless `--fresh`; `--offline` asks nothing.
- Each table is found by its English title on any sheet and read by its English labels, the last English column after the years. A table ends at the next table's header on the same sheet.
- The values in dinars, the counts of plants and of workers, and the rates of change are not taken.
- **Checks,** each within 1 MWh, in every year:
  - the plant types add to the energy generated, and imports and investment plus the Kurdistan Region to the purchased total;
  - generated plus purchased is the total, and the three losses add to theirs;
  - Table 1's figures equal Table 2's.
- The run stops for a table not found or found on two sheets, a row not in the map, given twice or missing, a value not a quantity, or a check missed.

Nothing is filled. Not taken: the workbooks of 2015 to 2023, whose tables differ in form; Tables 4 to 15 (by governorate and company).

## License

Internal. The footer (read 1360) reserves "the rights of the site's design and making" ("حقوق تصميم وتنفيذ الموقع محفوظة"), and no page read states terms of reuse for the statistics. Verdict: needs written permission, read as ZIMSTAT's copyright line (session 2495). Held from the release package and the live set.

## Cross-check

Against `eia_world_electricity_annual`'s Iraq:
- **Hydro:** 3.35, 2.65 and 1.38 TWh for 2021 to 2023 in both. For 2024 COSIT gives 3.49 and EIA 2.0.
- **Totals:** EIA's generation (149.7 TWh in 2024) counts private and Kurdistan plants as generation, while COSIT counts them as purchases with imports, so the totals cannot be compared directly.
