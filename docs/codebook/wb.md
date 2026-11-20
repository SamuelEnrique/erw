# Codebook: wb

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 2 public tables (2 series; tiers: 2 source); 2 documented in full.

- [`wb_commodity_prices_monthly`](#wb_commodity_prices_monthly): One World Bank Pink Sheet commodity's average price in one month, nominal US dollars.
- [`wb_electricity_access_annual`](#wb_electricity_access_annual): One economy's share of population with access to electricity in one year, the World Bank's World Development Indicators (EG.ELC.ACCS.ZS).

### `wb_commodity_prices_monthly`

One World Bank Pink Sheet commodity's average price in one month, nominal US dollars.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 11139.

- **Time:** ts_utc is the month's first day at 00:00:00Z (freq P1M).
- **Revisions:** A snapshot, replaced whole by each run; vintage is the workbook's Last-Modified time.
- **Source:** worldbank:pink_sheet World Bank, World Bank Commodity Price Data (The Pink Sheet) (https://www.worldbank.org/en/research/commodity-markets)
- **Method note:** [`docs/methods/wb_commodity_prices_monthly.md`](../methods/wb_commodity_prices_monthly.md)
- **Cite as:** World Bank. World Bank Commodity Price Data (The Pink Sheet). Via the Energy Research Warehouse (ERW), table `wb_commodity_prices_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: wb_pink:<series name as a slug> | none | text | wb_pink:aluminum, wb_pink:coal_australian, wb_pink:coal_south_african, wb_pink:copper, wb_pink:crude_oil_average, wb_pink:crude_oil_brent, wb_pink:crude_oil_dubai, wb_pink:crude_oil_wti, wb_pink:lead, wb_pink:liquefied_natural_gas_japan, wb_pink:natural_gas_europe, wb_pink:natural_gas_us, wb_pink:nickel, wb_pink:tin, wb_pink:zinc | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1960-01-01T00:00:00Z to 2026-09-01T00:00:00Z; 801 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.14 to 55385.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MMBtu, USD/bbl, USD/t | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Empty on every row: world markets | none | empty | no cell holds a value | 11139 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 11139 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The series' name as the workbook writes it, not a pricing node | none | text | Aluminum, Coal, Australian, Coal, South African, Copper, Crude oil, Brent, Crude oil, Dubai, Crude oil, WTI, Crude oil, average, Lead, Liquefied natural gas, Japan, Natural gas, Europe, Natural gas, US, Nickel, Tin, Zinc | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | worldbank:pink_sheet | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T09:58:30Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's Last-Modified time as the server sent it | none | utc time | 2026-10-02T18:57:55Z | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `price` | The commodity's monthly price, nominal US dollars: USD/bbl for crude oil, USD/t for coal and the metals, USD/MMBtu for natural gas and LNG | USD/MMBtu; USD/bbl; USD/t | 11139 | 1960-01-01T00:00:00Z | 2026-09-01T00:00:00Z |

### `wb_electricity_access_annual`

One economy's share of population with access to electricity in one year, the World Bank's World Development Indicators (EG.ELC.ACCS.ZS).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 5350.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** A snapshot, replaced whole by each run; vintage is the response's Last-Modified time as the connector records it.
- **Source:** worldbank:wdi_electricity_access The World Bank, World Development Indicators (Indicators API v2) (https://api.worldbank.org/v2/)
- **Method note:** [`docs/methods/wb_electricity_access_annual.md`](../methods/wb_electricity_access_annual.md)
- **Cite as:** World Bank. World Development Indicators (Indicators API v2): EG.ELC.ACCS.ZS. Via the Energy Research Warehouse (ERW), table `wb_electricity_access_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: wb:<ISO3 code> | none | text | for example wb:ABW, wb:AFG, wb:AGO; 215 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2000-01-01T00:00:00Z, 2001-01-01T00:00:00Z, 2002-01-01T00:00:00Z, 2003-01-01T00:00:00Z, 2004-01-01T00:00:00Z, 2005-01-01T00:00:00Z, 2006-01-01T00:00:00Z, 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.8 to 100.0; 868 distinct | 0 |
| `unit` | The unit of the row's value | none | text | pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: The World Bank's ISO2 country code (a country, not an ISO 3166-2 subdivision) | none | text | for example AD, AE, AF; 215 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 5350 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The economy's name, not a pricing node | none | text | for example Afghanistan, Albania, Algeria; 215 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | worldbank:wdi_electricity_access | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.worldbank.org/v2/country/all/indicator/EG.ELC.ACCS.ZS?format=json&date=2000:2025&per_page=20000 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T23:43:34Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-10-23T23:42:33Z | 0 |
| `x_indicator` | The World Bank's indicator id (EG.ELC.ACCS.ZS) | none | text | EG.ELC.ACCS.ZS | 0 |
| `x_region` | The World Bank's region group of the economy (the source's name: region) | none | text | East Asia & Pacific, Europe & Central Asia, Latin America & Caribbean, Middle East, North Africa, Afghanistan & Pakistan, North America, South Asia, Sub-Saharan Africa | 0 |
| `x_income` | The World Bank's income group of the economy (the source's name: incomeLevel) | none | text | High income, Low income, Lower middle income, Upper middle income | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `access_to_electricity` | Access to electricity, percent of population (EG.ELC.ACCS.ZS) | pct | 5350 | 2000-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

