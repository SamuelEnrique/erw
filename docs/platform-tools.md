# Platform tools

The 20 tools of the energy intelligence platform the Energy Research Warehouse (ERW) serves, in build order, with the ERW tables or shapes each depends on and whether that data layer exists today. The ERW is the live, citable record of the US energy system; every tool reads it and none keeps a private copy of a source (`CLAUDE.md`).

Status: **yes** = the tables the tool needs exist and refresh daily; **partial** = some exist, the gap is named; **no** = the shape or source is not built. Table names are in `docs/coverage.md`, the authority on what exists. Update this file when a layer changes status.

| # | Tool | Depends on | Data layer today |
|---|---|---|---|
| 1 | Energy Digest: daily AI-curated news brief across the whole energy industry | events `news_stories` (scored); series price and fuel tables for "Numbers today" | **partial**: price and fuel tables exist; `news_stories`, scoring and the digest are built in session 6 |
| 2 | Real-time price board: power hubs, gas, oil, nuclear fuel, carbon, lithium, energy equities | series: `*_dam_*`, `*_rtm_*`, `eia_fuel_spot_prices` | **partial**: power hubs at six ISOs, Henry Hub, WTI, Brent; missing PJM, SPP real-time, nuclear fuel, carbon, lithium, equities |
| 3 | Energy project map | entities: plants, projects, interconnection queue positions (EIA-860, ISO queues), with lat/lon | **no**: the entities shape has no connector yet |
| 4 | Datacenter power tracker | entities: datacenters; events: datacenter power deals; series: `eia930_*_demand` | **partial**: hourly demand by ISO; no datacenter entities or deal events |
| 5 | Signature data explorers (live thesis charts, starting with ERCOT peak premium) | series: `ercot_dam_hub_prices`, `ercot_rtm_hub_prices`, `eia930_erco_generation`, `eia930_erco_demand` | **partial**: ERCOT prices and generation exist; `eia930_erco_demand` is missing on 30-day runs (EIA forecast gap) |
| 6 | Energy deal tracker: PPAs, offtakes, M&A, project finance, AI-power deals as a tagged subset | events: deals (parties, mw, price, status); `news_stories` as the discovery feed | **partial**: deal stories arrive through `news_stories` with sector `deal`/`ppa` and parties; no structured deal table |
| 7 | Grid stress and real-time conditions | series: `*_rtm_*`, `eia930_*_demand` (with forecast), `eia930_*_generation`; reserves, outages | **partial**: real-time prices at four ISOs, demand and forecast, generation mix; no reserves, outages or ancillary prices |
| 8 | Regional power-price heatmap | series: `*_dam_*`, `*_rtm_*` with geo per node | **partial**: hubs and zones at six ISOs; no PJM, no nodal detail, geo per node not refined |
| 9 | Flagship newsletter | events `news_stories` (scored), digests in `docs/digest/`; all series | **partial**: same as tool 1 |
| 10 | Energy-intelligence company database | entities: companies, counterparties, operators; events linking them | **no** |
| 11 | Capital flows tracker | events: financing, M&A, funds (amounts, parties); `news_stories` sector `capital` | **no**: only news stories tagged `capital` |
| 12 | Policy and regulatory monitor | events: filings, rules, orders (FERC, NRC, EPA, state PUCs, dockets); `news_stories` sector `policy` | **partial**: policy news feeds; no docket or filing events |
| 13 | Deep-dive report library | all shapes; citations through `erw.cite()` | **partial**: depends on tools above |
| 14 | Weekly state-of-energy brief | events `news_stories`; series over 7 days | **partial**: same as tool 1, weekly roll-up not built |
| 15 | Data downloads and methodology | every table, `docs/coverage.md`, `docs/datastandard.md`, `erw` package | **yes** locally (CSVs, coverage, standard, package); Redivis release not built |
| 16 | Cost-of-power model | series: power prices, fuel prices, generation mix; entities: plant heat rates and costs | **partial**: prices, fuels, mix; no plant entities |
| 17 | Economic forecasting tool: tax and jobs impact of energy projects | entities: projects; series: economic and tax data | **no** |
| 18 | Predictive and scenario layer | long history of every series | **partial**: 30 days of power data, fuel prices since 1986-1997 |
| 19 | Data and API products | Redivis (warehouse of record), Supabase live layer, `erw` package | **partial**: package reads local files; Redivis and Supabase not built |
| 20 | AI chat over the warehouse | `erw` package, `package/llms.txt`, Claude API | **partial**: package and briefing exist; no chat service |
