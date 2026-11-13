# Data requests from the licensing sweep (chain 229, lab-desktop third window)

Energy Research Warehouse (ERW). Written by chain 229 (`queue/done/229-day-13-november-desktop-window3-licenses.md`), from session 4102, 13 November 2026. The licensing sweep writes no warehouse data: each row is a change only the data machine's chain (window A, which holds the data lock) makes. Window A marks a row done with its commit.

| # | Requested (UTC) | Session | For | What | Why | State |
|---:|---|---|---|---|---|---|
| 1 | 2026-11-13 | 4102 | `warehouse/news/index.py` (the registry rows it writes to `warehouse/metadata/sources.csv`) | Fold an em or en dash in a news outlet's name to a hyphen before the name is written, and merge the row `IEA <en dash> International Energy Agency` (an en dash, first seen 2026-09-25) into `IEA - International Energy Agency` (a hyphen), its tables `news_index;news_stories` | The name is copied verbatim into `site/data/table_citations.json` and `docs/redivis/release-v1/tables.csv` whenever `package/tools/build_tables.py` or `warehouse/redivis/release_v1.py` runs; the repository writes no em or en dash | requested |

## FRED: each series's primary source (session 4106)

FRED's terms (read 12, https://fred.stlouisfed.org/legal/, 12 October 2026) say: "You may not, without the Bank's prior written consent: [...] Store, cache, or archive any portion of the FRED® Services or FRED® Content". The ERW's four FRED tables are retired (`warehouse/output/retired/`: `fred_daily_spot_prices`, `fred_treasury_yields`, `fred_imf_commodity_prices`, `fred_power_price_indexes_monthly`). Each series FRED republished has a primary publisher, named here with its own series id and address. A row whose series the ERW already reads from the primary source needs nothing; the others are requests for window A.

| # | FRED series (retired table) | Primary source | Its series id | Its address | In the ERW today | Request | State |
|---:|---|---|---|---|---|---|---|
| 2 | DCOILWTICO (`fred_daily_spot_prices`) | U.S. Energy Information Administration, Spot Prices for Crude Oil and Petroleum Products, daily | RWTC | https://www.eia.gov/dnav/pet/hist/RWTCD.htm (API: https://api.eia.gov/v2/petroleum/pri/spt/, facet series RWTC) | yes: `eia_fuel_spot_prices`, entity `eia:wti_cushing` | none | covered |
| 3 | DCOILBRENTEU (`fred_daily_spot_prices`) | EIA, Spot Prices for Crude Oil and Petroleum Products, daily | RBRTE | https://www.eia.gov/dnav/pet/hist/RBRTED.htm (API facet series RBRTE) | yes: `eia_fuel_spot_prices`, entity `eia:brent` | none | covered |
| 4 | DHHNGSP (`fred_daily_spot_prices`) | EIA, Natural Gas Spot and Futures Prices, daily | RNGWHHD | https://www.eia.gov/dnav/ng/hist/rngwhhdd.htm (API: https://api.eia.gov/v2/natural-gas/pri/fut/, facet series RNGWHHD) | yes: `eia_fuel_spot_prices`, entity `eia:henry_hub` | none | covered |
| 5 | DGS2, DGS10, DGS30 (`fred_treasury_yields`) | Board of Governors of the Federal Reserve System, H.15 Selected Interest Rates, Treasury constant maturities | RIFLGFCY02_N.B, RIFLGFCY10_N.B, RIFLGFCY30_N.B (the Data Download Program's H15 package) | https://www.federalreserve.gov/releases/h15/ | yes: `frb_treasury_yields`, entities `frb:tcm_2y`, `frb:tcm_10y`, `frb:tcm_30y` | none | covered |
| 6 | PNICKUSDM (`fred_imf_commodity_prices`) | International Monetary Fund, Primary Commodity Price System (PCPS), monthly | PNICK | https://www.imf.org/en/Research/commodity-prices | yes: `imf_commodity_prices`, entity `imf:PCPS:PNICK` | none | covered |
| 7 | PURANUSDM (`fred_imf_commodity_prices`) | IMF, PCPS, monthly | PURAN | https://www.imf.org/en/Research/commodity-prices | yes: `imf_commodity_prices`, entity `imf:PCPS:PURAN` | none | covered |
| 8 | PCOALAUUSDM (`fred_imf_commodity_prices`) | IMF, PCPS, monthly (Australian thermal coal) | PCOALAU | https://www.imf.org/en/Research/commodity-prices (SDMX: https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.RES/PCPS/+/G001.PCOALAU.USD.M) | no | add PCOALAU to `SERIES` in `warehouse/connectors/imf_pcps.py` (its table `imf_commodity_prices`), under the IMF's terms (read 13; commercial reuse needs the IMF's permission) | requested |
| 9 | PNGASEUUSDM (`fred_imf_commodity_prices`) | IMF, PCPS, monthly (natural gas, EU) | PNGASEU | as row 8, code PNGASEU | no | add PNGASEU to `imf_pcps.py`'s `SERIES` | requested |
| 10 | PNGASJPUSDM (`fred_imf_commodity_prices`) | IMF, PCPS, monthly (LNG, Asia) | PNGASJP | as row 8, code PNGASJP | no | add PNGASJP to `imf_pcps.py`'s `SERIES` | requested |
| 11 | CUSR0000SEHF01, CUUR0000SEHF01, CUSR0000SEHF02 (`fred_power_price_indexes_monthly`) | U.S. Bureau of Labor Statistics, Consumer Price Index (electricity; utility piped gas service; U.S. city average, seasonally adjusted and not) | CUSR0000SEHF01, CUUR0000SEHF01, CUSR0000SEHF02 | https://data.bls.gov/timeseries/CUSR0000SEHF01 (and the others by id); the BLS Public Data API, https://api.bls.gov/publicAPI/v2/timeseries/data/ | no | a BLS connector by the registered API (a new table, with its source, sector and license rows). Neither EIA nor the Federal Reserve publishes these indexes; EIA's average retail prices (`eia_retail_electricity_prices`) are prices, not indexes. www.bls.gov answered HTTP 403 to the ERW's reader, even its robots file (read 1710, 13 November 2026): the API with a key is the route | requested |
| 12 | WPU0541, WPU0542, WPU0543, PCU22112211 (`fred_power_price_indexes_monthly`) | BLS, Producer Price Index (residential, commercial and industrial electric power by commodity; electric power generation, transmission and distribution by industry) | WPU0541, WPU0542, WPU0543, PCU22112211 | https://data.bls.gov/timeseries/WPU0541 (and the others by id); the same API | no | the same connector as row 11 | requested |

## Hosts whose robots files refuse Anthropic's agents by name (session 4107)

Read on 13 November 2026 by chain 229 before each terms page (`scripts/license_confirm.py robots`). The memory of session 2309 (OpenSTAT) is the rule: a host that allows `*` but refuses ClaudeBot or anthropic-ai by name is honoured. These hosts are fetched by the ERW's own code, so each is a request for window A to stop or reroute the fetch.

| # | Requested (UTC) | Session | For | What | Why | State |
|---:|---|---|---|---|---|---|
| 13 | 2026-11-13 | 4107 | `warehouse/connectors/release_schedule.py` (it reads `https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm`) | Stop reading www.cftc.gov, or read the release schedule from a host whose robots file allows it; `cftc_cot.py` reads `publicreporting.cftc.gov`, a different host whose robots file this chain did not read | www.cftc.gov's robots file (read 1716) names ClaudeBot and anthropic-ai with `Disallow: /` | requested |
| 14 | 2026-11-13 | 4107 | the news feeds (`https://heatmap.news/feeds/feed.rss`) | Drop Heatmap News's feed, or ask Heatmap | heatmap.news's robots file (read 1725) refuses anthropic-ai by name | requested |
| 15 | 2026-11-13 | 4107 | the news feeds (`https://www.datacenterdynamics.com/en/rss/`) | Drop Data Center Dynamics's feed, or ask DCD | www.datacenterdynamics.com's robots file (read 1721) refuses ClaudeBot and anthropic-ai by name | requested |

## Table headers whose "License:" line the record has overtaken (session 4155)

Read on 13 November 2026 from the data machine's table files (read only). Each header's own words say a publisher's terms are not read or not settled, where `docs/licenses.md` now holds a verdict. The flag does not change (no session loosens one); only the words of the header line, which the table's connector or builder writes.

| # | Requested (UTC) | Session | For | What | Why | State |
|---:|---|---|---|---|---|---|
| 16 | 2026-11-13 | 4155 | `makstat_macedonia_electricity_monthly` (its connector) | "License: internal until the licenses' round reads the State Statistical Office's terms" to say the terms are read: needs written permission ("© State Statistical Office", read 1780) | the header names a read that has happened | requested |
| 17 | 2026-11-13 | 4155 | `svk_sweden_production_hourly` | "internal until the licenses' round reads Svenska kraftnat's terms" to say: Svenska kraftnat's Data Service is CC BY 4.0 (read 1770); internal until the owner rules (`docs/licenses.md`, waiting for a ruling) | as row 16 | requested |
| 18 | 2026-11-13 | 4155 | `csp_latvia_electricity_monthly` | "no licence text read" to say: the CSB's media page allows reproduction with the CSB quoted as source (read 1771); internal until the owner rules | as row 16 | requested |
| 19 | 2026-11-13 | 4155 | `econtrol_austria_electricity_monthly` | "no reuse statement read" to say: E-Control asks to be named as the data source (read 1772), may be public as the ERW is today; internal until the owner rules | as row 16 | requested |
| 20 | 2026-11-13 | 4155 | `irena_capacity_annual` | "License: not settled (IRENA's terms ... answered with a challenge)" to say: needs written permission ("IRENA - International Renewable Energy Agency. All Rights Reserved.", read 342) | the verdict was written in session 2139 | requested |
| 21 | 2026-11-13 | 4155 | `usdm_drought_state_weekly` | "License: not settled (the Monitor's Permission page not yet read, session 2061)" to say: may be public (read 255) | the verdict exists; the flag is public and agrees | requested |
| 22 | 2026-11-13 | 4155 | `ferc714_area_demand_2006` to `_2025` (21 tables, `warehouse/connectors/ferc714_demand.py`) | add to the header's license line: PUDL's CC BY 4.0 read from its README (read 1688, chain 229); the flag waits for the owner's ruling | the header says only that FERC's page is unread | requested |

## More news feeds on hosts whose robots files refuse Anthropic's agents (session 4156)

| # | Requested (UTC) | Session | For | What | Why | State |
|---:|---|---|---|---|---|---|
| 23 | 2026-11-13 | 4156 | the news feeds (`https://oilprice.com/rss/main`) | Drop OilPrice.com's feed, or ask OilPrice.com | oilprice.com's robots file (read 1811) refuses ClaudeBot and anthropic-ai by name, `/rss/main` included | requested |
| 24 | 2026-11-13 | 4156 | the news feeds (`https://www.ans.org/news/feed/`) | Drop ANS Nuclear Newswire's feed, or ask ANS | www.ans.org's robots file (read 1815) refuses ClaudeBot and anthropic-ai by name, `/news/feed/` included | requested |
| 25 | 2026-11-13 | 4156 | the news feeds (`https://pv-magazine-usa.com/feed/`) | Drop pv magazine USA's feed, or ask pv magazine | pv-magazine-usa.com's robots file (read 1821) refuses ClaudeBot and anthropic-ai by name, `/feed/` included | requested |
| 26 | 2026-11-13 | 4156 | the news feeds (`https://www.utilitydive.com/feeds/news/`) | Read www.utilitydive.com's robots file before the next fetch; drop the feed if it refuses as its owner's www.industrydive.com does | www.industrydive.com's robots file (read 1812) refuses ClaudeBot and anthropic-ai by name; the feed's own host was not read by this chain | requested |

## Robots wildcards (session 4161)

| # | Requested (UTC) | Session | For | What | Why | State |
|---:|---|---|---|---|---|---|
| 27 | 2026-11-13 | 4161 | `warehouse/connectors/eia_ba_boundaries.py`, `warehouse/connectors/large_load_filings.py`, `warehouse/thesis/series.py` | Read a robots file's `*` and `$` as the usual convention does before a fetch (each connector its own copy, as `scripts/license_confirm.py`'s `wildcard_allows` does: the longest matching rule wins, Allow on a tie), and keep the stricter of that and `urllib.robotparser`'s answer | `urllib.robotparser` reads `*` and `$` literally: the Texas Comptroller's `Disallow: /*/` (read 2038) refuses nearly every path, yet the parser allows `/taxes/`. Chain 229's 196 page reads were checked again under the wildcard reading: none was refused | requested |
