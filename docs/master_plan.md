# Energy Intelligence Platform: Master Plan (20 Tools)

The full architecture and locked build order. This is the map every tool-build chat works from. Update tool status as each ships.

## The goal

Become the go-to public authority on the energy layer of AI (the "Dylan Patel of energy"), through a live, continuously updated platform. Bar: good enough that a top VC or a frontier AI lab wants to hire me.

## The four phases

- Establish the live spine (1-5): the machine that produces continuously updated intelligence, plus fast low-engineering wins.
- Extend the moat (6-8): proprietary live datasets almost no one maintains.
- Brand and analysis on the substrate (9-15): writing, company/capital/policy analysis, and synthesis, built on data that already exists.
- Differentiate (16-20): heavy proprietary models and the AI product, sitting on top of everything before them.

## The 20 tools, in build order

| # | Tool | Description | Status |
|---|------|-------------|--------|
| 1 | Energy news radar | AI-curated daily feed scanning energy and energy+AI news (deals, datacenter power, projects, PPAs, policy, filings), ranked and clustered by significance and tied to the thesis, so a reader sees what moved the world in two minutes. Not a raw RSS dump. | Not started |
| 2 | Real-time price board | One live dashboard for the prices that define the energy economy: wholesale power at key ISO hubs (ERCOT, PJM, CAISO), Henry Hub gas, uranium, carbon, lithium, curated energy equities, with spreads and moves at a glance. | Not started |
| 3 | Energy project map | Interactive map plotting every energy project, existing and planned: generation (gas, nuclear, solar, wind, geothermal), storage, and datacenter power builds, with status, capacity, developer, timeline. Visual centerpiece and core moat. | Not started |
| 4 | Datacenter power tracker | Live model of US datacenter power demand: operating and planned facilities, MW by region and operator, growth trajectory, load concentration. The single most sought-after dataset for AI labs and their investors. | Not started |
| 5 | Signature data explorers | Interactive, continuously refreshed versions of the analytical charts from my thesis (ERCOT peak-premium, demand growth, interconnection), turned from static images into filterable live tools. Proof of original quantitative analysis. | Not started |
| 6 | AI-power deal tracker | Structured, running database of every deal struck to power AI: nuclear restarts, SMR offtakes, gas buildouts, PPAs, behind-the-meter, with counterparties, MW, price where disclosed, and status. Highest-signal asset for the target audience. | Not started |
| 7 | Grid stress / real-time conditions | Live view of grid conditions across major ISOs: load vs capacity, scarcity and congestion signals, where the grid is tight now. Keeps the platform genuinely real-time and operationally useful. | Not started |
| 8 | Regional power-price heatmap | Map layer visualizing where power is cheap, expensive, and available, blending price-board and project-map data into a siting-decision tool. Answers where to put load and what power will cost there. | Not started |
| 9 | The flagship newsletter | Recurring deep-dive written analysis, the Dylan Patel core, synthesizing the live data into sharp, opinionated, citeable pieces. Launches after the data spine exists so every issue demonstrates the platform. | Not started |
| 10 | EI company database | Living, searchable directory of energy-intelligence startups (the illustrative-startups work made dynamic): what each does, stage, funding, thesis fit. The reference map of the sector. | Not started |
| 11 | Capital flows tracker | Tracker of venture, growth, PE, and infrastructure capital into energy intelligence, by segment, stage, and investor. Speaks directly to the VC audience. | Not started |
| 12 | Policy & regulatory monitor | Continuously updated watch on market-moving policy: permitting reform, tax credits and IRA provisions, tariffs, interconnection rules, state actions, with plain-language impact reads. Sets up the forecasting tools. | Not started |
| 13 | Deep-dive report library | Curated archive of long-form, thesis-quality reports designed to become the citeable reference on a question. The real resume and proof of sustained authority. | Not started |
| 14 | Weekly state-of-energy+AI brief | One-page executive digest synthesizing news, prices, deals, projects, and policy into the week's essential read. The highly shareable artifact that spreads through VC, lab, and policy networks. | Not started |
| 15 | Data downloads / methodology | Clean downloadable datasets plus transparent documentation of how each tool sources and computes its data. The rigor layer that earns sophisticated readers' trust. | Not started |
| 16 | Cost-of-power model | Model computing true cost of power ($/MWh) by region and source, translated into cost of running compute (per training run or datacenter). The economic calculation labs use to choose sites. First heavy model. | Not started |
| 17 | Economic forecasting tool | Forecasts downstream economic impact of energy projects: sales and property tax revenue, jobs, local effects, for regulators, utilities, and siting. Builds on my LSU/Dr. Greg Upton impact-modeling work. Widens audience into policy. | Not started |
| 18 | Predictive / scenario layer | Forward-looking projections of where power demand, prices, and buildout are heading under different scenarios (AI load growth, generation mix, policy shifts). Prediction is the highest form of authority; needs a mature data spine. | Not started |
| 19 | Data / API products | Paid, productized access to datasets, models, and dashboards via subscriptions and an API. The institutional-research business model. Viable once the data has proven its value. | Not started |
| 20 | AI chat over your data | Conversational interface (a mini-ChatGPT scoped to the whole platform) answering natural-language queries grounded in the proprietary data ("average disclosed PPA price for nuclear-to-datacenter deals this year?"). Last by design; only as good as the data beneath it, which by now is deep. The ultimate proof of building real AI product on a domain labs care about. | Not started |

## Standing principles

- Build in order; each tool reuses the data or audience of the ones before it.
- Ship a working v1, then improve. Momentum over perfection.
- Real, cited, live data only. Never fake or placeholder numbers as real.
- Shared clean data layers over one-off silos, so later tools plug in.
- Decide the stack at tool 1; keep it consistent after.
