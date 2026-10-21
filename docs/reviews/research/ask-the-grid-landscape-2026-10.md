# Ask the Grid, the US Energy-Data Landscape, and Where the ERW Can Win (as of October 20, 2026)

(Claude Research, run by Samuel inside the Energy Intelligence Platform project on 21 October 2026; kept verbatim as a source document for the roadmap v4 draft. Samuel's rulings of 21 October stand over its recommendations: no tool is cut, the ERW competes with Ask the Grid on the live views in parallel, and nothing is written for the public until the Digest and the Roundup are perfect.)

Ask the Grid is real, free to browse, moving fast and already covers most of tools 2, 7, 8 and 20 on your master plan, plus parts of 1, 3 and 4. The ERW should not try to out-ship it on live ISO data. Its defensible ground is narrower and more academic: open, citable, licensed downloads; editable economics models; and peer-reviewed analysis such as "Donor Grids and Taker Grids". None of the competitors I could verify offers that combination.

## TL;DR

- **Most of the trigger claims check out, with some drift.** Ask the Grid (Parisi Labs, NYC, founded 2026) runs an MCP server covering 8 markets with "356 datasets" and "15 typed tools". It uses OAuth 2.1, read-only bounded SQL, a 5-endpoint API, Metis probabilistic price forecasts and alerts, and 17 more North American grids live outside the MCP release, which makes 25. I could not find funding amount, investors, terms-of-service text, paid prices, rate-limit numbers or any ISO redistribution license.
- **The license problem is industry-wide, and nobody publicly claims to have solved it.** PJM bars redistribution without at least Associate Membership. MISO's site terms bar redistribution and automated access. ISO-NE warns that "non-personal use may violate copyright". Ask the Grid and Grid Status both republish PJM data publicly, but neither states an ISO license anywhere I could find. Your gate is a real constraint, not paranoia, and a clean license posture can be a differentiator.
- **What to build next, ranked by evidence (no cuts):** (1) the cost-of-power model plus the deal tracker (16, 6), because OpenAI is hiring a Power Trading Lead ($181,000 to $285,000 plus equity, at least 10 years in power trading, commodity risk management or utility strategy) alongside utility, infrastructure-finance and energy-policy leads, and nobody publishes open, editable economics; (2) the Redivis release and the Donor/Taker paper (15), for citability; (3) a datacenter tracker (4) built on the power side, because Epoch already gives away facility-level data for free; and (4) live-price surfaces (2, 7, 8), which are now commoditized by Ask the Grid and Grid Status.

## Key Findings (ranked by how much they should change what gets built next)

| Rank | Finding | Master-plan tools affected | Options it opens |
|---|---|---|---|
| 1 | Ask the Grid already ships a free live map, grid agent, LMP maps, hub-price pages, interconnection-queue maps, data-center asset pages, "Stories", a blog and an "Energy Wire" | 2, 7, 8, 20; partly 1, 3, 4 | Stop treating live ISO views as the flagship; consider consuming its MCP internally for research (subject to its unseen terms); differentiate on economics, citability, written synthesis |
| 2 | ISO terms (PJM, MISO, ISO-NE) restrict redistribution; no competitor publicly claims an ISO redistribution license[1] | 2, 5, 7, 8, 15, 19 | License strategy as a moat: ship EIA-930, ERCOT, CAISO, SPP and federal data openly now; pursue PJM Associate Membership or academic permission letters; publish your license audit as a public good |
| 3 | AI labs are hiring for hedging, utility deals, infrastructure finance and energy policy, not dashboards:[2] OpenAI's Power Trading Lead posting (reported by Bloomberg and TheNextWeb, Aug 10, 2026) sits on "the Power & Land team, inside datacenter design", pays $181,000 to $285,000 plus equity, requires "at least 10 years in power trading, commodity risk management or utility strategy", and covers "fixed-price supply, forwards, swaps and options" | 6, 16, 11, 12 | Prioritize the cost-of-power model and deal tracker, with assumptions shown |
| 4 | Epoch AI's free Frontier Data Centers Hub, launched Nov 4, 2025, owns facility-level AI data-center power estimates; Epoch's Head of Data & Trends Yafah Edelman: "Using satellite imagery, permits, and company filings, we've tracked these major facilities to reveal the actual build-out pace" (EIN Presswire) | 4 | Build the tracker on the power side (utility, ISO, interconnection, cost of power) and link to Epoch rather than duplicating it |
| 5 | Modo Energy owns paid BESS revenue benchmarks in ERCOT and other US ISOs[3][4] | Battery economics tool, 16, 18 | Calibrate your open battery model against Modo's published numbers; open and editable is the wedge |
| 6 | Grid Status has $8M of funding (Aug 2024, "led by Energize Capital, a venture firm backed by General Electric, Schneider Electric, and major energy developer Invenergy", per Canary Media), a 500k-row free API and 500+ datasets | 19, 15 | Do not build a competing data API; build citable releases (Redivis DOIs) and Stata/R/Python packages |
| 7 | Ask the Grid went from build to 560 datasets in roughly two months with a small team | All live-layer tools | Speed of a funded AI-native team means you lose feature races; academic credibility is the moat they cannot quickly copy |

## Details

### 1. Parisi Labs and Ask the Grid: verified facts

**Company and founders**
- Parisi Labs describes itself as building "world models for physical industry, starting with energy", with Ask the Grid as "our live system explorer for energy" and Metis as "our family of models" (askthegrid.com/about; parisi-labs.com).[5][6]
- F4 Fund's startup page lists Parisi Labs as NYC-based, "Founded 2026", "1-10 employees", stage "Seed", and James Lepage as co-founder (f4.fund/startups/parisi-labs).[7] *Inference:* being listed on an F4 Fund portfolio-style page suggests F4 is an investor, but no round amount or lead is disclosed there.
- Crunchbase lists the founders as James LePage, Matt Miller and Paul Hultgren, with LePage as Co-Founder and CEO (past role: Automattic, Head of AI) (crunchbase.com/organization/parisi-labs).[8] I could not verify Miller's or Hultgren's backgrounds from public sources in this pass.
- LePage's own CV site says he was Head of AI at Automattic (March to May 2026) and Eng Director, AI (Dec 2024 to March 2026). It also says he co-founded WPAI, "acquired by Automattic", and joined Parisi Labs as co-founder in May 2026 (j.cv).[9] Crunchbase also lists him as founder of CodeWP and Isotropic (crunchbase.com/person/james-lepage).[10] Syracuse University lists a James LePage '22 (Whitman) as a ShareClub co-founder (library.syracuse.edu).[11] *Inference:* this is likely the same person, given the "@isotropic" handle on his WordPress profile, but I have not confirmed it.[12]
- His background is AI and product, not energy. None of the sources I found shows a founder with power-markets or energy-economics training.

**Funding.** Not public. On Sep 3, 2026 LePage wrote that the bigger story would come "when we properly introduce the company, team, and funding" (x.com/jameswlepage).[13] Amount, round, date and lead are **not knowable from public sources** as of today.

**Hiring and team.** Team size is 1 to 10 (F4, Crunchbase).[7][8] A "Senior Full-Stack Product Engineer" role was posted 2026-09-08. The posting calls Ask the Grid "already a substantial live product" and says "We are a small team working across research, data, and product engineering" (zapply.jobs).[14] LePage's X bio says "making world models (hiring, dm)".[15]

**Launch timeline (what is verifiable)**
- LePage's Sep 3, 2026 post says "We've had a really fun month building @ask_the_grid", which implies building started around early August 2026. The post had 430 views (x.com/jameswlepage/status/2095312870254714977).[13]
- The GitHub repo "askthegrid-mcp" (MIT) was last updated Aug 20, 2026, with 0 stars and 0 forks shown (github.com/Parisi-Labs).[16]
- The MCP page shows a ChatGPT plugin-directory listing screenshot dated 2026-10-12 and says "Now in ChatGPT's plugin directory" (askthegrid.com/mcp).[17] It is also listed as a Glama MCP connector (glama.ai).[18]
- **Not verified:** domain registration date, Product Hunt launch, Hacker News launch, and trade-press coverage. I found only a Slashdot software directory listing (slashdot.org/software/p/Ask-The-Grid).[19]

**What the product exposes**
- **MCP:** "8 markets, 356 datasets, 15 typed tools; OAuth 2.1 · Streamable HTTP". There are per-market servers (ERCOT 73 datasets, CAISO 85, NYISO 59, PJM 70, SPP 85, MISO 84, ISO-NE 58, BPA 63) plus a global server at mcp.askthegrid.com/v1/global (askthegrid.com/mcp).[17]
  - The 15 tools are: search_data, describe_data, query_data ("Run bounded read-only SQL against ISO-approved tables"), query_grid_assets, get_live_grid_status, get_congestion_path, get_asset_profile, get_asset_intelligence (Enterprise), request_asset_hydration, get_asset_hydration_status, get_alert_capabilities, list_alerts, get_alert, create_alert and manage_alert.[17]
  - Security is described as "Allowlist + row caps. Bounded, rate-limited, audited."[17] No numeric rate limits are published.
  - The NYISO server page lists "protocol 2025-11-25" (askthegrid.com/mcp/nyiso).[20]
- **The "25 grids" claim checks out, with caveats.** The MCP FAQ says Duke Carolinas, Duke Progress East and West, Duke Florida, FPL, Southern, TVA, Baja California, AESO, IESO, CENACE, Hydro-Québec, BC Hydro, Manitoba Hydro, SaskPower, NB Power and IESO Nova Scotia "are live across the rest of Ask the Grid, outside this MCP release".[17] That is 17 plus 8, so 25. An older platform page snippet said "18 North American grids", so the count is moving.[21]
- **Dataset counts conflict across the site.** The MCP page says 356. The per-market MCP pages sum to 577, presumably because shared EIA, NOAA and asset tables are counted in each market. The About page says "560 datasets in the catalog".[5] The platform page lists ERCOT 50, CAISO 45, PJM 40, MISO 50, NYISO 51, ISO-NE 83, SPP 58, EIA 40, FERC 1, NOAA 5, BPA 13 and USGS 2 (askthegrid.com/platform).[21] Treat 356 as the MCP-scoped figure on Oct 20.
- **API (5 APIs):**
  - Forecast: GET /api/v1/grid/forecasts[22]
  - Data: GET /api/v1/catalog, and POST /api/v1/datasets/{id}/query[22][23]
  - Insights: GET /api/v1/insights[22]
  - Chat: POST /api/v1/agent/runtime/v1/session, streaming NDJSON[22]
  - Alerts: POST /api/v1/alerts, delivering by email, SMS, Slack or Teams[22]
  - Bearer-token auth, with an OpenAPI 3.1 document published (askthegrid.com/developers; askthegrid.com/catalog/ercot_load_forecast).[22]
- **Forecasts:** Metis 1 Preview gives probabilistic real-time price forecasts with p10, p50 and p90 bands. Price is in "Public preview, up to 2 days, 5-minute intervals" for ERCOT, NYISO, CAISO and PJM. Load, wind, solar and other generation are in "Private preview". The model card says "Weights are not distributed" and "Free with an account at major trading hubs and load zones; other locations come with a plan" (huggingface.co/Parisi-Labs/metis-1-preview; askthegrid.com/developers).[22][24]
- **History:** the catalog shows ERCOT DAM settlement point prices with 76.3M rows from 2017, and NYISO real-time ancillary prices from 2015 (askthegrid.com/catalog).[25]
- **Pricing tiers:** browsing is free, with a "Free workspace · no card" (askthegrid.com).[26] Paid tiers exist ("other locations come with a plan"; "Data services"; "Enterprise"), but **no list prices could be retrieved**. The pricing page was not reachable through my tools.
- **Written content:** "Stories", a blog (for example, a data-center interconnection-queue piece with ERCOT HB_WEST statistics), scheduled "Reports, written for you", and "Energy Wire" news (askthegrid.com/blog/interconnection-queue-data-center-clusters; askthegrid.com/platform).[21][27] Its schema describes itself as "A live market map, original research desk, and source-aware agent".[17]

**Terms of service and licensing.** Not retrieved. Every catalog dataset's structured data points "license" to askthegrid.com/terms (for example askthegrid.com/views/pjm-interconnection-queue), so the ToS is the de facto data license.[28][29] I **cannot quote its reuse, redistribution or citation clauses**.

I found **no public claim** that Parisi Labs holds PJM, NYISO, ISO-NE or MISO redistribution licenses. It nonetheless publishes PJM node LMPs and PJM Western Hub daily prices openly (askthegrid.com/views/pjm-real-time-lmp; askthegrid.com/views/pjm-western-hub-price).[30][31] The phrase "ISO-approved tables" in the MCP tool description is ambiguous: it may mean internally allowlisted tables, not ISO permission.

**Customers and usage.** No named testimonials or case studies were found. The MCP GitHub repo shows 0 stars and 0 forks. LePage's post claims the product "surfaced hundreds of thousands of dollars in potential value" in some planning use; this is self-reported and unverified.[13] The solutions pages target trading desks, utilities and co-ops, ISOs, asset owners, and data centers and large loads (askthegrid.com/mcp nav).[17]

### 2. ISO licensing facts relevant to the ERW's own gate

| ISO | Rule (verbatim or close paraphrase) | Source |
|---|---|---|
| PJM | Data Miner data "is for internal use only and redistribution... is strictly prohibited without an active PJM Membership. A minimum level of Associate Membership is required." The terms PDF says "Members may republish data, however non-members are specifically prohibited from republishing data." Non-members are limited to 6 connections per minute.[1][32][33] | pjm.com Data Miner page; pjm.com data-license-agreement PDF; dataminer2.pjm.com |
| MISO | "You may not modify, publish, transmit... reproduce, create derivative works of, distribute... any of the materials." Also bans "automated means, including... agents, robots, scripts, or spiders".[34] Pricing reports moved to the Data Exchange (which needs an account and acceptance of its own terms) from Dec 12, 2025.[35][36] | misoenergy.org legal page; MISO Data Exchange PDFs (via subagent) |
| ISO-NE | "Any duplication of the Content or non-personal use may violate copyright, trademark, and other laws"; permission is requested via info@iso-ne.com[37] | iso-ne.com/legal-privacy (search snippet, via subagent) |
| NYISO | Terms of use **not confirmed**. Only an interregional-map disclaimer was found.[38] | nyiso.com interregional disclaimer |

**What competitors do about it**
- **Grid Status:** its ToS claims "all Data is an original compilation protected by United States copyright laws". It requires attribution ("Powered by Grid Status" or "Data provided by Grid Status") and allows derivative works that are "sufficiently different" (gridstatus.io terms PDF, via subagent snippet).[39] No public ISO license or PJM membership claim was found.
- **Ask the Grid:** the license points to its own ToS; no ISO license claim was found.[40]
- **Yes Energy:** **not researched in this pass**, so I make no claim.

*Inference:* both startups appear to rely on the compilation-copyright plus attribution model rather than disclosed ISO licenses. If PJM enforced its terms, both would be exposed. Your audit (42 tables needing permission) is the conservative reading of the same documents.

### 3. Landscape (verified rows only)

| Provider | Coverage | Price | Audience | Funding | Visible gaps |
|---|---|---|---|---|---|
| Ask the Grid | 8 ISOs via MCP plus 17 other grids; prices, load, queues, assets, data centers, forecasts | Free browse, free workspace; paid prices unpublished | Traders, utilities, asset owners, data centers, AI-agent users | Undisclosed seed (F4 listed) | No published ToS terms found, no ISO license claim, no editable economics models, no gas/oil/capital/policy coverage, no academic citability (DOIs) |
| Grid Status | CAISO, ERCOT, PJM, MISO, NYISO, SPP, ISO-NE, IESO (plus AESO and EIA in the open library); 500+ datasets[41][42][43] | Free API tier of 500k rows a month; paid tiers unpublished in text[42][43] | Traders, utilities, analysts | $8M (Aug 21, 2024), led by Energize Capital, with Nat Friedman, Daniel Gross, Rayburn Electric, Evergreen; PitchBook lists Google Accelerator (Aug 27, 2026)[44][45] | Power-only; little written economics; attribution-required license |
| Modo Energy | BESS benchmarks and forecasts in GB, Europe, Australia and the US (ERCOT, CAISO, PJM, MISO and others)[3][46] | Paid (prices not public) | BESS owners, investors, lenders | £25M ($33M) Series B, Dec 2025: per Molten Ventures' Dec 9, 2025 RNS, "Molten has led a £25 million Series B round by investing £12.5 million", with ETF Partners, MMC Ventures and Fred. Olsen Ltd participating (TechFundingNews); £11.8M Series A, Nov 2023 | Storage-centric; paywalled models; not open or editable |
| Epoch AI Frontier Data Centers Hub | AI data centers: power, compute, cost, timelines, from satellite and permit data | Free[47] | Public, policymakers, investors, labs | Nonprofit (not researched) | Facility-centric; no grid-side, tariff or cost-of-power economics |

Sources:
- Grid Status: Canary Media; PR Newswire; github.com/gridstatus/gridstatusio; PitchBook.
- Modo Energy: ess-news.com; renewableenergyworld.com; modoenergy.com research.
- Epoch AI: epoch.ai.

Key datapoints:
- Grid Status had "about 10,000 users per month" and a seven-member team in Aug 2024, and Canary Media reported its users include "most of the country's interstate grid operators and largest energy project developers" (Canary Media).
- Modo's nowcast put ERCOT BESS 2025 revenue at "$29.4/kW". It also reports ERCOT arbitrage at 76% of BESS revenue in June 2025 (modoenergy.com).[48][49]
- Epoch's hub launched Nov 4, 2025 and estimates "$29B per gigawatt" of facility power (x.com/EpochAIResearch).[50] Its ranking puts Colossus 2 at about 946 MW of IT power as of October 2026 (epoch.ai/graphs).[51] The record single-site power capacity "has doubled every 10 months" (epoch.ai/data-insights).[52]

**Not verified in this pass, so I make no claims about pricing, funding or citation patterns:** Yes Energy, Enverus, Wood Mackenzie, S&P Platts, BNEF, Latitude Media, Heatmap, Canary Media (except as a source), Doomberg, Grid Brief, Volts, LBNL, NREL, Lazard, EIA products, Construction Physics, ZERO Lab/REPEAT, Grid Strategies, Energy Innovation, RMI, Ember, SemiAnalysis, Electricity Maps, WattTime, Kevala, Paces, Camus, Arbor, Tyba, Enact, Gridmatic, Amperon, Rebase, DCD, Data Center Map, Synergy, TD Cowen, DC Byte, Baxtel, and VC thesis citation patterns. My search budget ran out before I reached them. Treat this as an open gap, not as evidence that they are weak.

### 4. What labs need (evidence)

- **OpenAI** is hiring a Power Trading Lead on its "Power & Land team, inside datacenter design". The role pays $181K to $285K, needs 10+ years of experience, owns hedging across electricity and gas, and has no direct reports at first (Bloomberg; thenextweb.com).[53][54] It is also hiring a Clean Energy and New Technology Lead at $223K to $385K with 15+ years, working "closely with regulatory and policy teams" (datacenterdynamics.com).[55] A secondary source lists further roles: Utility and Power Project Lead, Infrastructure Finance Lead and Energy Policy Lead in DC (tftc.io); I did not see those postings directly.[2]
- **Anthropic** ("Build AI in America", published Jul 22, 2025) says "the U.S. AI sector is on track to require at least 50 gigawatts of electric capacity by 2028, much of which will be needed to train the world's most capable models". It projects 2 GW and 5 GW training sites for Anthropic in 2027 and 2028, and 20 to 25 GW of frontier training demand by 2028 (anthropic.com/news/build-ai-in-america; AI-360).
- **What these roles reach for:** forward power and gas curves, utility tariffs and large-load interconnection terms, PPA and deal comparables, cost-of-power at candidate sites, and policy and regulatory tracking.[56] *Inference:* none of the four verified providers publishes an open, assumption-visible cost-of-power or deal dataset. Ask the Grid and Grid Status are spot- and history-centric. Modo is storage-only. Epoch is facility-only.

## Recommendations (options, not cuts)

1. **License posture first (15, 19).** Launch publicly on data that is clean today: EIA-930, ERCOT, CAISO, SPP and federal sources. Apply for PJM Associate Membership, or seek an academic redistribution letter through Stanford, and request written NYISO, ISO-NE and MISO permission. Publish the license audit as a methodology page. *Inference:* it may become the most-cited thing on the site, because competitors are silent on it.
2. **Elevate 16 (cost of power) and 6 (deal tracker).** These map directly to the OpenAI power-trading, utility and infrastructure-finance roles. Build with Lazard hurdle rates shown and every assumption editable.
3. **Use Ask the Grid rather than race it.** Use its MCP for your own exploratory research, after reading /terms. Keep the ERW's live views (2, 7, 8) as thin thesis-chart views rather than general-purpose maps.
4. **Ship the Donor/Taker paper and the Redivis release before the Oct 30 LOI.** A DOI plus a peer-reviewable method is the one asset Ask the Grid, Grid Status and Modo do not have.
5. **Datacenter tracker (4): link to Epoch.** Add utility, ISO zone, interconnection-queue match and modeled cost of power per site.
6. **Calibrate the battery tool against Modo's ERCOT benchmarks** ($29.4/kW for 2025), and publish the reconciliation.[49]

## Caveats

- These items are **not knowable from public sources today**: Ask the Grid's ToS clauses, paid prices, rate limits, funding, investors, customer list and domain registration date; and whether any competitor holds ISO redistribution licenses.
- Ask the Grid's dataset and grid counts vary across its own pages (356, 560 and 577 datasets; 18 or 25 grids). The site is changing weekly.
- The OpenAI role list beyond the two directly reported postings comes from secondary aggregators.
- The F4-as-investor reading and the LePage–Syracuse identity link are inferences.
- About half the landscape requested (incumbents, newsletters, NREL and LBNL products, VC theses, citation evidence) was not researched in this pass.

## Sources

1. [PJM - Data Miner](https://www.pjm.com/markets-and-operations/etools/data-miner-2.aspx)
2. [OpenAI Hires Power-Trading Lead as Stargate's 10 GW Bet Gets Real](https://www.tftc.io/openai-power-trading-lead-stargate-data-center-energy)
3. [ERCOT battery storage in 2026: 7 things to watch - Research](https://modoenergy.com/research/en/ercot-battery-storage-2026-things-to-watch)
4. [How does battery storage work in US electricity markets? - Research](https://modoenergy.com/research/en/battery-storage-us-electricity-markets)
5. [About Ask the Grid](https://askthegrid.com/about)
6. [Parisi Labs](https://parisi-labs.com/)
7. [Parisi Labs](https://f4.fund/startups/parisi-labs)
8. [Parisi Labs - Crunchbase Company Profile & Funding](https://www.crunchbase.com/organization/parisi-labs)
9. [James LePage — Co-Founder at Parisi Labs](https://j.cv/)
10. [James LePage - Crunchbase Person Profile](https://www.crunchbase.com/person/james-lepage)
11. [LaunchPad alum Sam Hollander '21 and James LePage '22 selected for prestigious XRC Labs Accelerator - Syracuse University Libraries](https://library.syracuse.edu/news/launchpad-alum-sam-hollander-21-and-james-lepage-22-selected-for-prestigious-xrc-labs-accelerator/)
12. [James LePage (@isotropic)](https://profiles.wordpress.org/isotropic/)
13. [James LePage on X, Sep 3, 2026](https://x.com/jameswlepage/status/2095312870254714977)
14. [Senior Full-Stack Product Engineer - Parisi Labs](https://zapply.jobs/jobs/397cb57c-3a16-4e4c-af1d-57d357c94943/)
15. [James LePage (@jameswlepage) on X](https://x.com/jameswlepage?lang=en)
16. [Parisi Labs · GitHub](https://github.com/Parisi-Labs)
17. [Energy & Power Market MCP Server: Prices, Queues & Grid Data](https://askthegrid.com/mcp)
18. [Ask the Grid - MCP Connector](https://glama.ai/mcp/connectors/io.github.Parisi-Labs/askthegrid)
19. [Ask The Grid Reviews - 2026](https://slashdot.org/software/p/Ask-The-Grid/)
20. [NYISO MCP Server for New York Grid Data · Ask the Grid](https://askthegrid.com/mcp/nyiso)
21. [Platform: Live Grid Map, Grid Agent, Forecasts & Alerts · Ask the Grid](https://askthegrid.com/platform#monitor)
22. [Power Market API & MCP Server: Live US Grid Data](https://askthegrid.com/developers)
23. [Load Forecast (MTLF) — ERCOT dataset · Ask the Grid](https://askthegrid.com/catalog/ercot_load_forecast)
24. [Parisi-Labs/metis-1-preview · Hugging Face](https://huggingface.co/Parisi-Labs/metis-1-preview)
25. [Data Catalog · Ask the Grid](https://askthegrid.com/catalog)
26. [Ask the Grid: Live US Power Grid Map, Prices & Conditions](https://askthegrid.com/)
27. [How to read data-center clusters through the interconnection queue. · Ask the Grid](https://askthegrid.com/blog/interconnection-queue-data-center-clusters)
28. [Renewables Actuals — CAISO dataset · Ask the Grid](https://askthegrid.com/catalog/caiso_renewables_actual_hourly)
29. [PJM Interconnection Queue: Project Map and Status · Ask the Grid](https://askthegrid.com/views/pjm-interconnection-queue)
30. [PJM Western Hub Price: Today, This Week and This Month · Ask the Grid](https://askthegrid.com/views/pjm-western-hub-price)
31. [PJM LMP Map: Real-Time Prices by Node · Ask the Grid](https://askthegrid.com/views/pjm-real-time-lmp)
32. [Data Miner 2](https://dataminer2.pjm.com/)
33. [Agreement to Terms of use Data Miner 2](https://www.pjm.com/-/media/DotCom/etools/edatafeed/data-license-agreement-edata-feed-data-miner-2.ashx)
34. [MISO legal and privacy](https://www.misoenergy.org/meet-miso/legal-and-privacy/)
35. [MISO Data Exchange User Guide](https://cdn.misoenergy.org/MISO%20Data%20Exchange%20User%20Guide674561.pdf?v=20250124142839)
36. [MISO Data Exchange](https://cdn.misoenergy.org/MISO%20Data%20Exchange%20Information718679.pdf?v=20251107140508)
37. [Legal and Privacy](https://www.iso-ne.com/legal-privacy)
38. [Interregional Data Disclaimer Page - NYISO](https://www.nyiso.com/interregional-data-disclaimer-page)
39. [Grid Status Terms of Use](https://www.gridstatus.io/legal/terms_of_use.pdf)
40. [NYISO Interconnection Queue Map · Ask the Grid](https://askthegrid.com/views/nyiso-interconnection-queue)
41. [What is the gridstatus library? — gridstatus](https://opensource.gridstatus.io/en/stable/)
42. [GitHub - api-evangelist/gridstatus](https://github.com/api-evangelist/gridstatus)
43. [GitHub - gridstatus/gridstatusio](https://github.com/gridstatus/gridstatusio)
44. [Grid Status 2026 Company Profile: Valuation, Funding & Investors](https://pitchbook.com/profiles/company/533082-25)
45. [Grid Status lands $8M round led by Energize Capital](https://www.canarymedia.com/articles/clean-energy/grid-status-lands-8m-to-expand-its-open-source-mapping-of-the-us-grid)
46. [Modo Energy raises $33M and sets out AI ambitions - Energy Storage](https://www.ess-news.com/2025/12/03/modo-energy-raises-33m-and-sets-out-ai-ambitions/)
47. [Introducing the Frontier Data Centers Hub](https://epoch.ai/latest/introducing-the-frontier-data-centers-hub)
48. [How does a battery energy storage system make money? - Research](https://modoenergy.com/research/en/how-does-battery-energy-storage-make-money)
49. [Why were ERCOT battery revenues so low in 2025? - Research](https://modoenergy.com/research/en/why-were-ercot-battery-revenues-so-low-in-2025-weather-energy-arbitrage-builodout)
50. [Epoch AI on X: Announcing our Frontier Data Centers Hub](https://x.com/EpochAIResearch/status/1985788184245293153)
51. [Largest AI data centers ranked by power capacity, 2026](https://epoch.ai/graphs/largest-ai-data-centers-by-power-capacity)
52. [Largest AI data center power: doubling every 10 months](https://epoch.ai/data-insights/frontier-data-center-power)
53. [OpenAI Is Hiring a Power-Trading Lead for Its Data Center Portfolio - Bloomberg](https://www.bloomberg.com/news/articles/2026-08-10/openai-is-hiring-a-power-trading-lead-for-its-data-center-portfolio)
54. [OpenAI is hiring a power trader, because electricity is now a position on its books](https://thetechstreetnow.com/openai-is-hiring-a-power-trader-because-electricity-is-now-a-position-on-its-books/)
55. [OpenAI hiring for clean energy and new technology lead - DCD](https://www.datacenterdynamics.com/en/news/openai-hiring-for-clean-energy-and-new-technology-lead/)
56. [OpenAI Hires Power Trading Lead to Manage Energy Needs for AI Infrastructure](https://www.kucoin.com/news/flash/openai-hires-power-trading-lead-to-manage-energy-needs-for-ai-infrastructure)
