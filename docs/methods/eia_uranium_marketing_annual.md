# EIA Uranium Marketing Annual Report: uranium bought by U.S. reactors, its price, enrichment and inventories

Energy Research Warehouse (ERW), method note written in session 905 (chain 049) for tables first written on 23 October 2026.

Tables: `eia_uranium_marketing_annual`

## Publisher and address

U.S. Energy Information Administration (EIA), Uranium Marketing Annual Report (Form EIA-858, Uranium Marketing Annual
Survey), its five summary workbooks linked from the page `https://www.eia.gov/uranium/marketing/`:
`xls/umartableS1afigureS1.xlsx` (S1a, uranium purchased), `xls/umartableS1bfigureS2.xlsx` (S1b, its weighted-average
price), `xls/umartableS2figuresS3n4.xlsx` (S2, feed deliveries, uranium loaded, enrichment services purchased and their
average price), `xls/umartableS3afigureS5.xlsx` (S3a, foreign purchases, foreign sales and commercial inventories) and
`xls/umartableS3bfigureS6.xlsx` (S3b, the weighted-average prices of foreign purchases and sales). Retrieved 23 October
2026, 06:59:52 to 06:59:53 UTC. Five requests, the connector's ceiling (session 904 also read the report's page: 6
requests of 20); the workbooks are saved in `warehouse/raw/eia_uranium_marketing/` and reused with `--offline`. EIA's
robots file allows `/uranium/marketing/`. Connector: `warehouse/connectors/eia_uranium_marketing.py`.

## Vintage and revision

Delivery years 2003 to 2025 when written (run `20261023T070136Z`). A run reads the five workbooks and writes the table
whole, one snapshot; `vintage` is empty. The first write replaced no earlier file (the previous file held 0 rows). EIA's
prices are not adjusted for inflation.

## Shape and variables

Series. One `entity`, `eia_uranium:us`, and a variable for each of EIA's columns, named by its meaning. `ts_utc` the
delivery year's 1 January, `freq` `P1Y`, `geo` `US`, `market` empty, `node` EIA's column heading as written, its footnote
letter included (`Spot contracts b`). The units `lb`, `SWU` and `USD/SWU` were added for this table (Decision 55 in
`docs/datastandard.md`).

| Variable | Unit | What it is |
|---|---|---|
| `purchased_<seller>` | `lb` | uranium bought by owners and operators of U.S. civilian nuclear power reactors (S1a; EIA's million pounds U3O8 equivalent times 1,000,000) |
| `price_purchased_<seller>` | `USD/lb` | its weighted-average price, dollars per pound U3O8 equivalent (S1b) |
| `feed_deliveries` | `lb` | feed deliveries by the owners and operators (S2) |
| `uranium_loaded` | `lb` | uranium in fuel assemblies loaded into U.S. civilian nuclear power reactors (S2) |
| `enrichment_us_origin`, `enrichment_foreign_origin`, `enrichment_total` | `SWU` | enrichment services purchased, by origin and in total (S2; EIA's million SWU times 1,000,000) |
| `enrichment_price` | `USD/SWU` | their average price (S2) |
| `foreign_purchases_us_suppliers`, `foreign_purchases_owners`, `foreign_purchases_total` | `lb` | foreign purchases by U.S. suppliers, by owners and operators, and in total (S3a) |
| `broker_purchases_from_foreign` | `lb` | U.S. broker and trader purchases from foreign suppliers (S3a) |
| `foreign_sales` | `lb` | foreign sales (S3a) |
| `inventories_us_suppliers`, `inventories_owners`, `inventories_total` | `lb` | uranium inventories owned by U.S. suppliers, by owners and operators, and total commercial inventories (S3a) |
| `price_<foreign purchase or sale>` | `USD/lb` | the weighted-average price of each foreign purchase and sale variable above (S3b) |

`<seller>` is `total`, `from_us_producers`, `from_us_brokers_traders`, `from_other_owners_suppliers` (EIA's "Purchased
from other owners and operators of U.S. civilian nuclear power reactors, other U.S. suppliers, (and U.S. government for
2007)"), `from_foreign_suppliers`, `us_origin`, `foreign_origin`, `spot` and `long_term`.

When written: 763 rows, one entity, 37 variables, 2003 to 2025. Most variables have all 23 years. The others: by origin
(`purchased_us_origin`, `purchased_foreign_origin` and their prices) none for 2019, 2020 and 2022; `enrichment_price`
from 2006; `broker_purchases_from_foreign` and its price none for 2013 and 2014; purchases from U.S. producers 8 years (to 2021),
from U.S. brokers and traders 19 years (to 2021), from other owners and suppliers 9 years (to 2022), their prices 8, 18
and 7 years. In 2025, owners bought 46.9 million pounds U3O8 equivalent at 58.46 USD/lb on average (spot contracts 75.83), and
enrichment cost 108.70 USD/SWU. The average price was 44.13 USD/lb in 2015 and 33.27 in 2020.

## Reading the sheets

- The heading row is the first of a sheet's first 12 rows whose first cell reads "Delivery year" or "Year".
- Each column is found by the start of its heading in the connector's map, not by position. A heading that matches no
  entry or more than one stops the run, and so does a count of columns other than the map's.
- A row is read when its first cell is a four-digit year; EIA's notes below are passed.
- Quantities in million pounds and million SWU are multiplied by 1,000,000; prices are kept as EIA gives them.
- A value EIA withholds ("W") or does not give ("-", "- -", "NA") has no row. Nothing is filled.
- A key (entity, variable, ts_utc) given twice stops the run.

## License

Public: a work of the U.S. government (EIA, record 1 of `license_reads.csv`; `docs/licenses.md`: public, agrees). Cite
"U.S. Energy Information Administration, Uranium Marketing Annual Report".

## Cross-check (session 904)

Within EIA's tables. EIA notes that totals may not equal the sum of their parts because of independent rounding.

- Enrichment by origin sums to the total in 23 of 23 years (within 0.001 million SWU), and inventories in 23 of 23
  (within 0.1 million pounds, EIA's last digit).
- Purchases by origin sum to the total within 0.5 percent in every year where both are given (20 years).
- Spot and long-term contracts together fall short of the total by up to 5.9 percent (2016); within 0.5 percent in only 9
  of 23 years. They exceed it in one year, 2021, by 0.1 million pounds (9.0 and 37.8 against 46.7). EIA does not break
  out the remainder; reported as found.

## What it does not hold

- The report's detailed tables (1 to 26: by supplier, origin country, pricing mechanism, contracts, enrichment country,
  sellers): the summary tables carry the long series; a later session can add them.
- A value EIA withholds or does not give, such as the years listed above.
- A single reactor, owner, state or supplier: one entity, the United States.
- The remainder between spot plus long-term contracts and the total, which EIA does not break out.
- Prices adjusted for inflation, and years before 2003.
