# U.S. coal prices: sales price by market type and by rank, delivered price by sector, and trade price, a year

Energy Research Warehouse (ERW), method note written in session 677 (chain 043) for tables first written on 21 or 22 October 2026.

Tables: `eia_coal_prices_annual`, `eia_coal_delivered_price_annual`, `eia_coal_price_rank_annual`, `eia_coal_trade_price_annual`

Four connectors, one table each, all reading EIA's API v2 coal routes the same way: pages of 5,000 records, 3 seconds apart, the key from `EIA_API_KEY` (redacted in every `source_url`), only the `price` column asked.

## Publisher, report and address

| Table | Connector (session) | Report as the header names it | Address |
|---|---|---|---|
| `eia_coal_prices_annual` | `eia_coal_prices.py` (519) | Annual Coal Report, average sales price, `https://www.eia.gov/coal/annual/` | `https://api.eia.gov/v2/coal/market-sales-price/data/?frequency=annual&data[]=price&start=2001` |
| `eia_coal_delivered_price_annual` | `eia_coal_delivered_price.py` (553) | Quarterly Coal Report, consumption and quality, `https://www.eia.gov/coal/production/quarterly/` | `https://api.eia.gov/v2/coal/consumption-and-quality/data/?frequency=annual&data[]=price&start=2000` |
| `eia_coal_price_rank_annual` | `eia_coal_price_rank.py` (572) | Annual Coal Report, average sales price by rank, `https://www.eia.gov/coal/annual/` | `https://api.eia.gov/v2/coal/price-by-rank/data/?frequency=annual&data[]=price&start=2001` |
| `eia_coal_trade_price_annual` | `eia_coal_trade_price.py` (573) | Quarterly Coal Report, exports and imports, `https://www.eia.gov/coal/production/quarterly/` | `https://api.eia.gov/v2/coal/exports-imports-quantity-price/data/?frequency=annual&data[]=price&start=2000` |

The publisher of all four is the U.S. Energy Information Administration (EIA).

## Vintage and revision rule

From the headers: sales price by market type, years 2001 to 2024 (3,739 records of EIA's, 2,781 with a price); delivered price, 2000 to 2025 (7,839 records, 3,213 with a price); sales price by rank, 2001 to 2024 (3,454 records, 2,843 with a price); trade price, 2000 to 2025 (28,571 records, 24,623 with a price). The first year is fixed in each connector; none takes a `--from`.

Each table is written with `ip.write_snapshot`: a run replaces the whole table. A page an earlier run saved in `warehouse/raw/<connector>/` is reused unless `--fresh`; `--offline` asks nothing. A revised price at EIA reaches a table only through a page asked again. Ceilings a run: 6 (sales price), 26 (delivered), 8 (rank), 18 (trade). A read shorter than EIA's count stops the run.

## Shape

All four are series, `variable` `price`, unit `USD/short_ton` (EIA's dollars per short ton, factor 1), `ts_utc` the year's 1 January at 00:00:00Z, `freq` `P1Y`, `market` empty, `vintage` empty.

- `eia_coal_prices_annual`: `entity` `eia_coal_price:<stateRegionId>:<marketTypeId>`, for example `eia_coal_price:AL:OM`. Areas are producing states, EIA's coal regions (such as `APC` Appalachia Central, `PRB`) and `US`; market types `CAP` (captive), `OM` (open market) and `TOT` (total). 145 entities. `geo` `US-<state>` for a state, `US` for a region or the U.S. `node` EIA's area and market names.
- `eia_coal_delivered_price_annual`: `entity` `eia_coal_delivered:<location>:<sector>`, for example `eia_coal_delivered:AL:10`. Locations are a state, a census division (`NEW`, `MAT`, `ENC`, `WNC`, `SAT`, `ESC`, `WSC`, `MTN`, `PCC`, `PCN`, `90` the Pacific) or `US`. Sectors: `1` electric utility, `2` IPP non-CHP, `3` IPP CHP, `94` independent power producers (2 and 3), `98` electric power (all), `8` commercial and institutional, `9` coke plants, `10` other industrial. 228 entities. `geo` `US-<state>` for a state, `US` otherwise. `node` EIA's state and sector names.
- `eia_coal_price_rank_annual`: `entity` `eia_coal_price_rank:<stateRegionId>:<coalRankId>`, for example `eia_coal_price_rank:AL:BIT`. Ranks `BIT`, `SUB`, `LIG`, `ANT` and `TOT` (all). 128 entities. `geo` as for the sales price. `node` EIA's area and rank names.
- `eia_coal_trade_price_annual`: `entity` `eia_coal_trade:<exportImportType>:<coalRankId>:<countryId>:<customsDistrictId>`, for example `eia_coal_trade:Exports:STM:AD:NY_NY`. Types `Exports` and `Imports`; coal kinds `STM` (steam), `MET` (metallurgical), `COK` (coke) and `TOT`; 141 countries; 44 customs district codes, with `OTH` (other ports) and `TOT` (total). 3,460 entities. `geo` is `US` on every row (the code sets it so; the header's line on a state geo is copied from the other connectors). `node` the type, country, kind and district in EIA's names.

Levels repeat one another in every table (divisions their states, sectors 94 and 98 their parts, `TOT` its parts): a sum takes one level.

The rank and trade connectors would write a quarterly row (`freq` `P3M`) for a quarterly period; they ask annual data only, and every row is `P1Y`.

## License

ERW verdict: public for all four (`docs/licenses.md`). Headers: License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Annual Coal Report") for the sales price and the price by rank; cite "U.S. Energy Information Administration, Quarterly Coal Report" for the delivered price and the trade price.

## Cross-check

None in the connectors. Each stops on a unit not in its map, a record with a key field blank, a key given twice, or a read shorter than EIA's count.

## What it does not hold

- A figure EIA withholds has no row; nothing is filled.
- EIA's quantities in short tons (sales, deliveries, exports and imports) and the delivered coal's qualities are not taken: the unit vocabulary holds no short tons (session 519 took the sales price in place of coal production by mine for that reason).
- Coal receipts by plant and mine (session 553 took the delivered price in their place).
