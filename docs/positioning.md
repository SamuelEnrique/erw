# Positioning: the ERW beside Grid Status and Electricity Maps

Energy Research Warehouse (ERW), session 189. Written and read on 11 October 2026 (2026-10-11).

## 1. What this document is

- A comparison of the ERW with two companies that publish electricity data: Grid Status and Electricity Maps.
- It says what each does, what the ERW does that was not found on their pages, where the ERW overlaps them on purpose, and where they are ahead.
- **The standard of evidence.**
  - Every statement about either company carries a marker such as [G4] or [E3]. The marker is a row of section 8: a page read on 11 October 2026, or a file.
  - Words in quotation marks are the page's own words, with link markup removed. Beside a repository pointer, quotation marks hold a section's name or the repository's own words.
  - A statement that could not be sourced from a page read that day is left out. Section 8.2 lists the pages that could not be read and what is therefore not said.
  - Every statement about the ERW carries a pointer into this repository: a page address, a document, a table or a script.
- **How to read "does not".** It means that the thing was not found on the pages read. Section 8 lists those pages. The companies have more pages than were read: the ceiling was 30 requests.
- **This is a dated reading.** Both companies change their products often. Before quoting this document, read the page again and change the date.
- The ERW has no connection with either company and is endorsed by neither.

## 2. Grid Status

### 2.1 What it does

- It describes itself in one line: "Monitor, analyze, and export power-market data across North American grid operators." [G2]
- Its stated mission: "Our mission is to provide accessible, actionable energy data to accelerate the energy transition." [G5]
- **Data.** Real-time and historical electricity data: locational marginal prices, load, generation and fuel mix, forecasts and interconnection queues, for nine grid operators (CAISO, ERCOT, MISO, PJM, NYISO, ISO-NE, SPP, IESO, AESO) and the EIA. [G2]
- **Two things carry the name.**

| | The open-source library `gridstatus` | The hosted Grid Status service |
|---|---|---|
| What it is | A Python library that fetches data "directly from North American independent system operators (ISOs), regional transmission organizations (RTOs), and the U.S. EIA" [G11] | A REST API, a Python client (`gridstatusio`) and a web application [G2] [G4] |
| The data | "Minimally processed data fetched directly from ISO and EIA sources" [G11] | "Hosted data with consistent column names, timestamp formats, and DST handling" [G11] |
| History | "Historical availability depends on each source's retention policy" [G11] | "Historical data queryable immediately" [G11] |
| Access | No account; most datasets need no key [G11] | "Grid Status API key with free and paid plans" [G11] |
| License | The three-clause BSD text, "Copyright 2022 James Max Kanter" [L1] | Not read (section 8.2) |

### 2.2 Its products, as its documentation lists them

| Group | Product | The documentation's description |
|---|---|---|
| Monitor | Grid Status Live | A view of wholesale energy markets by grid operator [G4] |
| Monitor | Insights Feed | "A live feed of analyst commentary" [G4]. "Each post is authored by our own Grid Status Markets team" [G9] |
| Monitor | Map, Interconnection Queue, ERCOT 4CP Monitor, Alerts, EIA Browser, Record Tracker, Trends | Maps of markets and grid infrastructure; project pipelines in the queues; coincident peak monitoring in ERCOT; notifications; EIA data; records; cumulative metrics [G4] |
| Analytics | Charts and Dashboards | Custom charts and dashboards on real-time and historical data [G4] |
| Analytics | Nodal Analysis | "Search and access the 75,000+ point database that powers the Nodal Price Map and analyze pricing nodes in North America." [G4] |
| Analytics | Constraint Analysis | "Analyze transmission congestion and get a constraint-level understanding of market outcomes across all North American ISOs/RTOs." [G4] |
| Analytics | Forecast Analysis | "An application to visualize how forecast vintages change and measure their accuracy over time." [G4] |
| Data | Data Catalog, Data Exporter | Every dataset with its source URL, frequency, primary key, an update log and a daily availability audit; CSV export [G8] |
| Data | API | A REST API with an OpenAPI specification; most endpoints need a key [G2]. Two rate-limit tiers: Basic (1 request a second, 600 an hour) and Standard (6 a second, 1,200 an hour) [G7] |
| Data | Snowflake | "Nearly all of our data is available on Snowflake within 1-2 minutes of being published via our API." [G10] |
| Service | Market Advisory Services | Calls with its Markets team. "Calls and email support are included in Enterprise subscriptions" [G9] |

- The hosted API's stated advantages over reading the grid operators directly: faster querying, "Generally, more historical data availability", and "Continued availability even if any of the ISO sources go offline." [G6]

### 2.3 Who it serves

- The pages read name no customer.
- The products are addressed to people who work in wholesale power markets. The advisory service's example topics include "Asset-level DART optimization and basis management" and congestion risk. [G9]
- It sells: a "paid Grid Status subscription" opens historical date ranges in the catalog [G8], Enterprise subscriptions exist [G9], and paid Snowflake access follows "After signing a contract with Grid Status" [G10].
- **Not stated here:** its prices, plan limits beyond the rate limits, terms of use, customer count and funding. Its pricing and home pages could not be read (section 8.2).

## 3. Electricity Maps

### 3.1 What it does

- Its own description: "Electricity Maps brings together historical data, live grid signals, and forecasts in one platform for sustainability and power markets insights." [E2]
- **Two product lines on its home page** [E2]:
  - data for sustainability: "Clean, accurate, and structured grid data for integrating emissions insights and flexibility into your products and services" [E2];
  - forecasts for power markets: "Price and grid fundamentals forecasts for professionals seeking to manage and optimize their exposure to energy markets" [E2].
- **Signals** [E4]: electricity mix, cross-border net flows, total load, net load, carbon intensity, carbon-free percentage, renewable percentage, day-ahead market price, and a day-ahead price forecast.
  - The price forecast is marked "EUROPEAN COVERAGE EXCLUSIVELY" and is made "Using our own proprietary solar, wind and load forecasts as features". [E4]
- **Reach.** The pricing page says "We cover 130+ zones worldwide." [E3] The data page says "350+ Bidding zones available worldwide." [E4] The two figures differ; both are quoted as printed.
- **Time.** Data "from 10 years ago to 72 hours from now" [E4]. "All our data can be delivered with a 5-minute, 15-minute, and hourly granularity" [E5].
- **Access.** An API with five kinds of endpoint (`/past`, `/past-range`, `/history`, `/latest`, `/forecast`), a free interactive map, and a datasets portal [E2] [E6]. A free access tier is named "For academics & Home Assistant" [E6].

### 3.2 Its method

- "our data is attributional, location-based, and consumption-based" [E5]. It reports what is consumed in a grid, not only what is produced there.
- **Flow tracing.** Imports and exports are traced across connected grids: "This peer-reviewed scientific approach traces electricity flows across all interconnected grids" [E5].
- **Emission factors.** Two kinds: life-cycle and direct. The default is the IPCC's 2014 factors; for the United States it computes grid-specific factors from the EPA's eGRID. [E5]
- **Sources.** Government agencies, market operators and transmission system operators; the EIA is named for the United States. "Currently, we have 75 active parsers for real-time electricity mix data and 38 active parsers for exchange data." [E5]
- **Gaps and corrections.** "We estimate values to fill gaps." "We have a robust refetch policy, and we go back and update data corrections for up to 3 months." [E4]
- **Service level.** "we promise our service is up 99.9% of the time." [E4]

### 3.3 What is open and what is sold

- **Open:** the parsers. "A collection of parsers to collect and standardize electricity data such as production, exchanges and price from across the globe." "This repository is licensed under GNU-AGPLv3 since v1.5.0" [E7].
- **Not open:** the platform built on them. The README names "our flow-tracing algorithm, estimation models, forecast engine and much more" as the platform's, and says of the map: "In the past, the map frontend was open source, but we have since rewritten the app completely and moved it to our own platform" [E7].
- **Prices, as printed on the pricing page read on 11 October 2026.** "All prices per country, per year at hourly granularity." [E3]

| Signal | Real-time, per country per year | Forecast |
|---|---|---|
| Day-ahead price | EUR 6,000 | Custom |
| Electricity mix | EUR 6,000 | Custom |
| Interconnector flows | EUR 6,000 | Custom |
| Total load | EUR 4,500 | Custom |
| Net load | EUR 4,500 | Custom |
| All grid signals (bundle) | EUR 18,000 | Custom |
| Carbon intensity | EUR 6,000 | Custom |
| Carbon-free energy percent | EUR 4,500 | Custom |
| Renewable energy percent | EUR 4,500 | Custom |
| All sustainability signals (bundle) | EUR 12,000 | Custom |

- Also on that page: "Ready to try the API for 14 days?", "Real-time data includes 3 months of trailing history.", and "Growth and early-stage companies may qualify for discounts up to 50%." [E3]

### 3.4 Who it serves

- Six groups on its home page: energy trading, battery and storage, data centers and IT, utility and industry, energy management, carbon accounting. [E2]
- "Electricity Maps has been working for 10 years with sustainability and energy professionals" [E2].
- **Not stated here:** customer names, customer count, funding, and its terms of use. No page read gave the first three as text; the terms page could not be read (section 8.2).

## 4. What the ERW does that was not found on their pages

Status words: **built** means the code, the table and the page exist in this repository. **In review** means a visitor cannot open the page today: every page of the site is `review` in `site/lib/release.ts` (session 166), and the internal view opens them (`docs/release-gate.md`).

### 4.1 Decisions: the cost-of-power tools

| Tool | The question it answers | Pointer | Status |
|---|---|---|---|
| What a datacenter pays, `/cost-of-power` | For a load the reader describes: what the power will cost, whether it will be there, how clean it is, how soon it can be had | `docs/methods/datacenter_cost.md` | built, in review |
| What a generator earns, `/cost-of-power/seller` | What a merchant solar, wind, battery or peaker plant earns by month, and whether that covers its debt; two scenarios on eight assumptions | `docs/methods/generator_earns_algorithm.md`, `merchant_revenue_monthly`, `site/lib/seller/finance.ts` | built, in review |
| What a battery earns, `/cost-of-power/battery` | What a grid battery of a given size and duration earns from energy and ancillary services together, and whether that covers its debt | `docs/methods/battery_stack.md`, `docs/methods/battery_earns_algorithm.md`, `battery_stack_monthly` | built for ERCOT and CAISO, in review |

- Each tool ends in a figure a lender or a buyer uses (debt coverage, a contract price, a cost per MWh), with every step written in its method note.
- **The nearest things on their pages.** Both companies serve the same people with other means. Grid Status offers advisory calls on asset-level optimization [G9]. Electricity Maps sells forecasts to battery and storage projects [E2]. No page read describes a public calculator of a project's revenue against its debt.

### 4.2 Findings: Automated Analysis

- **The weekly run.** A library of chart templates runs on the warehouse each week and a rule picks the chart of the week (`docs/methods/automated_analysis.md`, `warehouse/analysis/run.py`, `/analysis`).
- **Finding cards.** A finding is a question asked of the warehouse: a module in `warehouse/analysis/findings/` with its data, its method and, for the econometric ones, a regression with standard errors (`docs/methods/automated_analysis_findings.md`).
  - Every number on a card is recomputed from the card's own rows by a test.
  - Each card downloads its data, the Python that computed it and a Stata do-file.
  - Causal words are limited to what the design supports (`docs/voice.md`, "The finding card").
- **Status:** built, in review. A card with chosen inputs is computed by one laptop, and waits when that machine is off (`docs/methods/automated_analysis_findings.md`, "The queue").
- **The nearest thing on their pages.** Grid Status's Insights Feed is commentary written by its analysts [G9]. The ERW's findings are computed by code under a fixed rule, with the files to reproduce them. These are different products. This document does not say which is more useful.

### 4.3 The whole energy system in one warehouse

One data standard, three table shapes (`docs/datastandard.md`). What each table holds today is in `docs/coverage.md`. On this branch on 11 October 2026 `warehouse/metadata/coverage.csv` lists 198 tables: 164 public and 34 internal.

| Part of the system | Example tables |
|---|---|
| Power prices | `iso_dam_hub_prices`, `iso_rtm_hub_prices`, `ercot_all_hub_prices_history` |
| Demand, generation, interchange | `eia930_all_demand`, `eia930_all_generation`, `eia930_all_interchange` |
| Natural gas and oil | `eia_fuel_spot_prices`, `eia_gas_storage_weekly`, `eia_petroleum_supply_weekly` |
| Nuclear | `nrc_reactor_status` |
| Storage | `storage_capacity`, `battery_stack_monthly`, `ercot_as_prices` |
| Transmission and the network | `grid_network_links`, `eia930_all_interchange` |
| Projects and queues | `energy_projects`, `lbnl_interconnection_queue`, `datacenter_facilities` |
| Deals and companies | `energy_deals`, `energy_companies` |
| Policy | `policy_actions`, `policy_reads` |
| News | `news_index` |
| Weather | `noaa_grid_weather_hourly`, `weather_forecast_hourly` |

- **Their scope, on the pages read.** Grid Status: power markets and the EIA [G2]. Electricity Maps: electricity signals [E4]. No page read lists a table of deals, policy actions or news.
- **A limit of this statement.** Grid Status has an EIA Browser [G4] whose page was not read. It may hold fuel series.
- **The ERW's own gaps** are in `docs/platform-tools.md`: for example no table of capital flows (tool 11) and no PJM energy prices (tool 2).

### 4.4 A citable, versioned record

- **By design:** each table carries a provenance header and, per row, `source`, `source_url` and `retrieved_at` (`docs/datastandard.md`). Every row found new or changed is kept in an append-only archive (`warehouse/archive/README.md`). A person releases each version on Redivis after reading the difference (`ARCHITECTURE.md`, section 1a). `erw.cite()` writes the citation (`package/README.md`).
- **Today:** no Redivis version has been released, so there is no version to cite yet (`docs/state_2026-10-04.md`, item 9; `docs/platform-tools.md`, tool 15). Until that click, this is a design and a draft.
- **The nearest thing on their pages.** Grid Status's catalog gives each dataset its source URL and an update log [G8]. Electricity Maps describes refetching and corrections [E4]. No page read describes released, immutable versions of a dataset with a citation.

### 4.5 Questions answered from the tables

- `/ask` answers a question from the warehouse with four read-only tools. Every number in an answer must appear in a tool result (`ARCHITECTURE.md`, section 1; `warehouse/chat/`). Built, in review.
- Grid Status's "Ask the docs" searches its documentation [G2]. Whether either company answers questions over its data was not found on the pages read.

## 5. Where the ERW overlaps on purpose

### 5.1 Why

- The tools of section 4 need prices, the fuel mix and carbon figures as inputs.
- Every derived number must trace to a public source report (`CLAUDE.md`, non-negotiable 5). So the ERW holds its own copy, read from the publisher, with the report named on each row.
- A table the ERW publishes must be one its source allows to be redistributed (`README.md`, "License rule"). Whether either company's data could be republished is not known here: their terms were not read (section 8.2).

### 5.2 Topic by topic

| Topic | The ERW's version | Grid Status | Electricity Maps | How the ERW's differs |
|---|---|---|---|---|
| Wholesale prices | Hubs and zones of six grids, day-ahead and real-time: `iso_dam_hub_prices`, `iso_rtm_hub_prices`, `iso_hub_prices_history`, `iso_zone_prices_history`; ERCOT hubs since 2015 in `ercot_all_hub_prices_history` | Locational marginal prices for nine grid operators [G2]; a nodal database of "75,000+" points [G4] | Day-ahead market price as a signal [E4] | Hubs and zones only, no nodes. A market is written only when every node has every interval; nothing is filled (`README.md`, "How it refreshes"). PJM is not held and MISO is paused (section 6) |
| Fuel mix | `eia930_all_generation` (EIA-930, hourly by balancing authority), `caiso_fuel_supply`, `state_generation_mix_monthly`; `/mix` | Generation and fuel mix [G2] | Electricity mix of consumption and generation [E4] | EIA's and CAISO's published figures, reshaped. Generation inside the grid; imports are not traced to their fuel (`docs/methods/clean_energy.md`) |
| Carbon intensity | `carbon_intensity_hourly`, daily and monthly, for seven grid operators and the Lower 48 from July 2018; `/emissions` | EIA data that includes emissions, by a changelog entry of 19 September 2023 [G4]. No carbon intensity product was found on the pages read | Flow-traced, consumption-based carbon intensity with life-cycle or direct factors, worldwide [E5] | Built from EIA's own hourly CO2 estimates. "Consumed" is EIA's figure: generated plus imported minus exported. Direct emissions only, EIA's factors (`docs/methods/emissions.md`) |
| Carbon-free share | `clean_energy_hourly`; `/mix` | Not found on the pages read | Carbon-free and renewable percentage of consumption [E4] | The share of the grid's own generation, not of what its customers used (`docs/methods/clean_energy.md`) |
| Demand and forecasts | `eia930_all_demand`: demand and EIA's day-ahead demand forecast as published | Load and load forecasts [G11]; forecast vintages compared [G4] | Total load and net load, with forecasts [E3] | The ERW holds forecasts others publish. It makes none |
| Flows between grids | `eia930_all_interchange`, `grid_network_links`; `/network` | Interchange charts for SPP, by a changelog entry of 3 August 2026 [G4] | Cross-border net flows [E4] | Interchange between US balancing authorities as EIA reports it |
| Interconnection queues | The queues of six grid operators, read through the `gridstatus` library; `lbnl_interconnection_queue`; `energy_projects`; `/queues`, `/map` | An Interconnection Queue application [G4] | Not found on the pages read | Joined with EIA's generator inventory and the datacenter table on one map (`docs/methods/energy_projects.md`) |

- **Gaps are handled in opposite ways.** Electricity Maps says: "We estimate values to fill gaps." [E4] The ERW never fills: a missing interval is recorded as a gap in `warehouse/metadata/run_status.csv` (`CLAUDE.md`, non-negotiable 1). Each choice suits its use: a control system needs a value in every interval; a cited record needs to show what the source did not publish.

### 5.3 The one dependency

The ERW depends on Grid Status's open-source library. It depends on nothing else of either company.

- **What is used.** The Python library `gridstatus`, version 0.36.0, pinned in `requirements.txt`.
- **Where.** Three connectors import it: `warehouse/connectors/iso_prices.py` (hub and zone prices), `warehouse/connectors/latest_prices.py` (the newest real-time price, every 15 minutes) and `warehouse/connectors/iso_queues.py` (the interconnection queues). `warehouse/connectors/hub_history.py` calls the first.
- **What it does there.** It requests each grid operator's own public report and parses it. The data are the grid operators'. No request goes to Grid Status's servers: the installed library's code names none of them [L1] (the search is in `scripts/check_positioning.py`).
- **How it is recorded.** Each row's `source` names the grid operator's report. Each file's header names the library and its version. Every raw response the library receives is saved (`warehouse/connectors/iso_prices.py`, "Raw capture").
- **Where it is not used.** Where the library's reading would break an ERW rule, the connector reads the report itself. Example: `warehouse/connectors/caiso_as_prices.py`, because the library's reader fills missing cells with zero (`docs/methods/capacity_and_ancillary.md`).
- **Under which license.** The three-clause BSD text, "Copyright 2022 James Max Kanter" [L1]. The ERW installs the library from PyPI and does not redistribute it. The third clause forbids using the holder's or contributors' names to endorse a derived product: the ERW claims no endorsement.
- **What is not used.** The hosted Grid Status API, its Python client `gridstatusio`, and any Grid Status dataset. Any Electricity Maps parser, API or dataset. A search of the repository's code for both names on 11 October 2026 found only the three imports above (the search is in `scripts/check_positioning.py`).
- **The risk.** A change in the library, or an end to its maintenance, would stop three connectors. `.claude/skills/erw-add-connector/SKILL.md` records the library bugs already worked around.

## 6. Where they are ahead of the ERW

### 6.1 Grid Status

| Matter | Grid Status | The ERW |
|---|---|---|
| Grid operators | Nine, with PJM, MISO and two Canadian grids [G2] | Prices from six (`README.md`). PJM's energy prices are not held: "licensed source needed". MISO is paused: "paused while terms are reviewed" (`docs/methods/miso_pause.md`, `docs/voice.md`). No Canadian grid |
| Price detail | A nodal database of "75,000+" points; constraint-level congestion analysis [G4] | Hubs and zones only (`docs/platform-tools.md`, tool 8) |
| An API | A public REST API with an OpenAPI specification and a Python client [G2]; Snowflake delivery [G10] | "no public API" (`docs/platform-tools.md`, tool 19). A Python package that reads local files, the Redivis draft and the Supabase live set |
| Freshness | Data on Snowflake "within 1-2 minutes of being published via our API" [G10] | The newest real-time price every 15 minutes (`.github/workflows/latest-prices.yml`); the network page's interchange every hour (`.github/workflows/hourly-network.yml`); everything else once a day at 14:00 UTC (`.github/workflows/daily-prices.yml`) |
| History | "Historical data queryable immediately" [G11] | Uneven. ERCOT hubs from 2015; zones of CAISO, NYISO and SPP from 2019; hubs of the other grids from September 2024; the live price tables from 26 August 2026 (`docs/coverage.md`) |
| People | A Markets team that writes commentary and takes advisory calls [G9] | One builder, working in sessions with an AI assistant, as a Stanford independent study (`README.md`, "Lineage" and "Session log"; `CLAUDE.md`) |
| Working tools | Alerts, custom dashboards, a forecast-vintage tool [G4] | None of the three: `docs/tools.md` lists every tool |
| Commercial standing | It sells paid subscriptions, Enterprise subscriptions and contracts [G8] [G9] [G10]. The pages read give no customer count | No customer and no price. No page is open to visitors today (`site/lib/release.ts`) |

The ERW's price connectors are built on Grid Status's library (section 5.3). On reading grid operators' reports, the ERW follows; it does not lead.

### 6.2 Electricity Maps

| Matter | Electricity Maps | The ERW |
|---|---|---|
| Reach | Worldwide: "130+" zones [E3] or "350+" bidding zones [E4] | The United States (`CLAUDE.md`, "What the ERW is") |
| Forecasts | Its own, to 72 hours ahead [E4] | None of its own (`docs/platform-tools.md`, tool 18) |
| Carbon method | Flow tracing across connected grids; life-cycle factors; plant-level factors from eGRID in the United States [E5] | EIA's estimates, reshaped. No tracing of its own, no life-cycle factors (`docs/methods/emissions.md`) |
| Carbon freshness | Real-time and forecast signals [E3] | Hourly, as late as EIA publishes it. In the run of 10 October 2026, `carbon_intensity_hourly` ended on 7 October (`warehouse/metadata/coverage.csv`) |
| Granularity | 5-minute, 15-minute and hourly [E5] | Hourly for carbon and the fuel mix (`docs/coverage.md`) |
| Service | A stated uptime of 99.9 percent [E4]; an API with a 14-day trial [E3] | No service level. No public API |
| Standing | "working for 10 years" [E2]; a method it describes as peer-reviewed [E5] | Begun on 24 September 2026 (`README.md`, "Session log"). A paper is outlined, not written (`docs/paper/outline.md`) |

## 7. What we do not claim

- **Not a replacement** for either company. A trading desk that needs nodal prices within minutes needs Grid Status or a product like it. A system that shifts load by carbon signal needs Electricity Maps or a product like it.
- **Not more accurate.** No number of the ERW was compared with a number of either company for this document.
- **Not real-time.** Outside the 15-minute price board and the hourly network snapshot, the ERW is a daily record.
- **Not global, not nodal, and no forecasts of its own.**
- **Not yet citable in the strict sense.** No Redivis version is released (section 4.4).
- **Not open to visitors today.** Every page is in review (`site/lib/release.ts`).
- **No customers, no revenue, no service level.** Nothing in this repository records any of the three.
- **Not complete about them.** Their prices (Grid Status), terms of use (both), customers and funding were not read and are not stated. A thing not found on the pages read may still exist.
- **Not a partner.** The ERW uses one open-source library of Grid Status under its license. Neither company reviews or endorses the ERW, and neither was asked about this document.
- **Not permanent.** Section 4 lists what was not found on their pages on one day. Either company could add any of it.

## 8. Sources

### 8.1 Pages read on 11 October 2026

Every request was made on the morning of 11 October 2026 (UTC); the copies were fetched between 07:12 and 07:15 UTC. "Copy" is the first twelve characters of the SHA-256 of the copy kept during the session (in `runs/session189/pages/`, which git ignores: the copies are the publishers' text and are not republished here). A row with no copy was read through the fetch tool only.

| ID | Address | Read for | Result | Copy |
|---|---|---|---|---|
| G1 | `https://www.gridstatus.io/robots.txt` | Whether the host may be read | Allows every path | |
| G2 | `https://www.gridstatus.io/llms.txt` | Its own summary: data, grid operators, the API | Read | `8aedf2dece5a` |
| G3 | `https://docs.gridstatus.io/robots.txt` | Whether the host may be read | Allows every path | |
| G4 | `https://docs.gridstatus.io/llms.txt` | The index of its documentation: every product and its description | Read | `0de5d8c19a7d` |
| G5 | `https://docs.gridstatus.io/getting-started/readme.md` | Its stated mission | Read | `7a8390b4309e` |
| G6 | `https://docs.gridstatus.io/grid-status-api/getting-started.md` | The hosted API | Read | `387bb424e04e` |
| G7 | `https://docs.gridstatus.io/grid-status-api/rate-limits.md` | Rate limits | Read | `d6953ed94a7f` |
| G8 | `https://docs.gridstatus.io/data/data-catalog.md` | The catalog: source per dataset, history, audit | Read | `61eec412c55e` |
| G9 | `https://docs.gridstatus.io/monitor/insights-feed.md` | Analyst commentary and advisory | Read | `4dda52f4159d` |
| G10 | `https://docs.gridstatus.io/developers/snowflake-guides/getting-started.md` | Delivery through Snowflake | Read | `e5a6770467fc` |
| G11 | `https://raw.githubusercontent.com/gridstatus/gridstatus/main/README.md` | The open-source library against the hosted service | Read | `a8eaae82ab6d` |
| E1 | `https://www.electricitymaps.com/robots.txt` | Whether the host may be read | Allows every path | |
| E2 | `https://www.electricitymaps.com/` | What it is, product lines, who it serves | Read | `1d468be381c2` |
| E3 | `https://www.electricitymaps.com/pricing` | Prices, trial, history, zones | Read | `80697c0bb83c` |
| E4 | `https://www.electricitymaps.com/data` | Signals, reach, gaps, corrections, uptime | Read | `5ffa118e5a1f` |
| E5 | `https://www.electricitymaps.com/data/methodology` | Method: flow tracing, emission factors, sources | Read | `a8a237e96f6d` |
| E6 | `https://www.electricitymaps.com/platform/api` | The API and its free tier | Read | `249a18d09cf0` |
| E7 | `https://raw.githubusercontent.com/electricitymaps/electricitymaps-contrib/master/README.md` | What is open, and its license | Read | `84a98428895a` |
| E8 | `https://app.electricitymaps.com/robots.txt` | Whether the host may be read | Disallows `/auth` and `/locales` only | `c09aeee17e31` |
| E9 | `https://help.electricitymaps.com/robots.txt` | Whether the host may be read | Disallows three paths, none of them an article | `bffd3b315605` |

### 8.2 Pages that could not be read, and what is therefore not said

| Address | What happened | Not said in this document |
|---|---|---|
| `https://www.gridstatus.io/` | HTTP 403 to the fetch tool | Its home page's claims: customers, counts |
| `https://www.gridstatus.io/pricing` | HTTP 403 to the fetch tool. A second request returned the page's shell with no pricing text: the page is drawn by script | Grid Status's prices and plan limits |
| Grid Status's terms of use | Not requested: the same host draws its pages by script | What its terms allow |
| `https://www.electricitymaps.com/data-portal` | Redirects to `https://app.electricitymaps.com/datasets`, which answered HTTP 403 | Whether free historical files are offered, their years and license |
| `https://help.electricitymaps.com/en/articles/11750446-terms-of-service` | HTTP 403 | What its terms allow |
| `https://www.electricitymaps.com/llms.txt` | HTTP 404 | Nothing: the pages above were read instead |
| `https://raw.githubusercontent.com/robots.txt` | HTTP 404: the host has no robots file | Nothing |

Requests in all: 29 of a ceiling of 30 (`archive/sessions/SESSION_189_REPORT.md`).

### 8.3 The library on this machine

| ID | File | Read for |
|---|---|---|
| L1 | The `gridstatus` 0.36.0 distribution installed in the project's virtual environment: `gridstatus-0.36.0.dist-info/METADATA`, `gridstatus-0.36.0.dist-info/licenses/LICENSE` and the library's code (not in git; installed from PyPI by `requirements.txt`) | The version, the license text, and that the code names no server of Grid Status |

### 8.4 Repository files cited

| File | Cited for |
|---|---|
| `CLAUDE.md` | What the ERW is; the non-negotiables |
| `ARCHITECTURE.md` | How a dataset travels; the three stores; the chat |
| `README.md` | The license rule; the refresh; the lineage; the session log |
| `site/lib/release.ts` | Which pages a visitor can open |
| `docs/release-gate.md` | The internal view |
| `docs/platform-tools.md`, `docs/tools.md` | What is built, partial and planned; every tool of the site |
| `docs/coverage.md`, `warehouse/metadata/coverage.csv` | What each table holds and since when |
| `docs/datastandard.md` | Table shapes and provenance columns |
| `docs/state_2026-10-04.md` | No released Redivis version |
| `docs/voice.md` | The finding card; the two placeholder phrases |
| `docs/methods/datacenter_cost.md`, `docs/methods/generator_earns_algorithm.md`, `site/lib/seller/finance.ts`, `docs/methods/battery_stack.md`, `docs/methods/battery_earns_algorithm.md` | The three cost-of-power tools |
| `docs/methods/automated_analysis.md`, `docs/methods/automated_analysis_findings.md`, `warehouse/analysis/run.py`, `warehouse/analysis/findings/` | The weekly run and the finding cards |
| `docs/methods/emissions.md`, `docs/methods/clean_energy.md` | Carbon intensity and the carbon-free share |
| `docs/methods/energy_projects.md`, `docs/methods/capacity_and_ancillary.md`, `docs/methods/miso_pause.md` | The project map; where the library is not used; the MISO pause |
| `requirements.txt`, `warehouse/connectors/iso_prices.py`, `warehouse/connectors/latest_prices.py`, `warehouse/connectors/iso_queues.py`, `warehouse/connectors/hub_history.py`, `warehouse/connectors/caiso_as_prices.py` | The dependency on the `gridstatus` library |
| `.claude/skills/erw-add-connector/SKILL.md` | Library bugs worked around |
| `warehouse/archive/README.md`, `package/README.md`, `warehouse/chat/` | The archive; the citation; the chat |
| `warehouse/metadata/run_status.csv` | Where gaps are recorded |
| `.github/workflows/latest-prices.yml`, `.github/workflows/hourly-network.yml`, `.github/workflows/daily-prices.yml` | The schedules |
| `docs/paper/outline.md`, `docs/paper/related_projects_notes.md` | The paper's outline; an earlier reading of both companies (7 October 2026), not relied on here |
| `scripts/check_positioning.py` | The check of this document |
