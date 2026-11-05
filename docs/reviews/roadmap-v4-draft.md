# Roadmap v4: a draft from the two research reports of 21 October 2026

Energy Research Warehouse (ERW), session 450, the chain `queue/done/017-night-21-october-third.md`, written on the portable laptop (code role) on 21 October 2026 for the review of Wednesday. **A draft only: [docs/roadmap.md](../roadmap.md) does not change.** Only a person writes there; this file is what Samuel reads before deciding what v4 says.

## 0. What this reads, and how

- **The two reports.** [DR](research/deep-research-report.md) is Samuel's ChatGPT deep research of 21 October ("Roles at Anthropic, OpenAI, Sequoia, and a16z" and what to build and publish); [AG](research/ask-the-grid-landscape-2026-10.md) is Samuel's Claude Research of the same day ("Ask the Grid, the US Energy-Data Landscape, and Where the ERW Can Win"). Both are kept verbatim in the repository. Their claims are quoted as theirs; this session made no web request and checked none of them on the web.
- **What the ERW has today** was read with read-only git on `origin/main` (as `HEAD` of this branch, `wip/441-450-third`, which is `origin/main` plus the queue commit) and on the remote branches named. A path in a link exists on this branch; a link to github.com names its branch.
- **The twenty tools.** The chain names "the twenty tools" and "02_master_plan's tool table". No file of that name is in the repository (`git grep` finds "02_master" only in the chain files). [docs/platform-tools.md](../platform-tools.md) lists 31: the master plan's first 20, then 21 to 31, added in sessions 18 to 24. AG numbers the tools the same way (its tool 16 is the cost-of-power model, 6 the deal tracker, 15 downloads and methods, 19 data and API products), and the chain of 20 October calls tool 5 "the first signature explorer" and tool 9 the newsletter, as `docs/platform-tools.md` does. So this draft uses **tools 1 to 20 of [docs/platform-tools.md](../platform-tools.md)** as the master plan's twenty. Tools 21 to 31 are not ranked here; where one of them carries the work of a master-plan tool it is named (25, the email, under 1, 9 and 14; 26, Research, under 5).
- **The owner's standing rulings, kept over both reports.** No tool is cut. The site is not public. The Digest and the Roundup are the only two periodicals, and nothing else is written for the public until they are perfect (Samuel's ruling of 21 October, in the chain file). The ERW competes with Ask the Grid on the live views, in parallel, not by copying. AG's own header records the first three of these as standing over its recommendations ([AG, header](research/ask-the-grid-landscape-2026-10.md)).
- **Order words.** Each tool gets one of four places: **first** (this week's work), **second** (next, once a named blocker clears), **third** (kept current, no new feature), **later** (kept as it stands; no session this week). None is "cut".

## 1. The order in one table

| Place | Tools | The reason in one line |
|---|---|---|
| first | 1 Energy Digest, 14 Energy Roundup | Samuel's ruling: the two periodicals are perfect before anything else is written for the public |
| first | 16 cost-of-power model, 6 deal tracker | AG's strongest evidence: lab roles reach for hedging, deals and cost of power, and no verified provider publishes open, editable economics ([AG, TL;DR](research/ask-the-grid-landscape-2026-10.md#tldr); [AG, section 4](research/ask-the-grid-landscape-2026-10.md#4-what-labs-need-evidence)) |
| first | 15 data downloads and methodology, 19 data and API products | Both reports put the citable, open warehouse first ([DR, ranking 1](research/deep-research-report.md#risks-constraints-and-timing); [AG, Recommendations 1 and 4](research/ask-the-grid-landscape-2026-10.md#recommendations-options-not-cuts)) |
| second | 4 datacenter tracker, 12 policy monitor, 5 signature explorers | Each has AG evidence, and each waits on a named blocker: the license split by row, the policy sources' pauses, the explorers' landing |
| third | 2 price board, 7 grid stress, 8 price heatmap, 20 AI chat, 3 project map | AG finds the live views commoditized ([AG, Key Findings row 1](research/ask-the-grid-landscape-2026-10.md#key-findings-ranked-by-how-much-they-should-change-what-gets-built-next)); the owner's ruling keeps them, in parallel |
| later | 9 flagship newsletter, 13 report library, 10 company database, 11 capital flows, 17 economic forecasting, 18 predictive layer | Ruled behind the periodicals (9, 13), or no evidence in either report for moving them up (10, 11, 17, 18) |

## 2. The twenty tools, one by one

Each entry: what the two reports say (report and section), what the ERW has on main and on branches, and the recommendation.

### Tool 1: Energy Digest

- **The reports.** AG counts the Digest among the tools Ask the Grid "partly" covers, through its "Stories", blog and "Energy Wire" news ([AG, Key Findings row 1](research/ask-the-grid-landscape-2026-10.md#key-findings-ranked-by-how-much-they-should-change-what-gets-built-next); [AG, section 1, Written content](research/ask-the-grid-landscape-2026-10.md#1-parisi-labs-and-ask-the-grid-verified-facts)). DR does not name a daily brief; its "Newsletter" paragraph is a weekly one (tool 9) ([DR, Roadmap](research/deep-research-report.md#roadmap-what-to-build-and-publish-next-6-months)).
- **The ERW today.** On main: the page [site/app/digest](../../site/app/digest), the writer [warehouse/news/brief.py](../../warehouse/news/brief.py), the email [warehouse/news/email_digest.py](../../warehouse/news/email_digest.py) (tool 25), and twelve issues in [docs/digest](../digest) from 25 September to 20 October 2026. On a branch: session 402's audit and number checker ([scripts/check_digest.py on wip/402-s](https://github.com/SamuelEnrique/erw/blob/wip/402-s/scripts/check_digest.py)), not on main. Its story index `news_index` is held for a license from 21 October ([warehouse/metadata/license_status.csv](../../warehouse/metadata/license_status.csv)). Tonight's session 442 writes the audit of the last 14 issues on this branch.
- **Recommendation: first.** The owner's ruling puts it first, and AG's evidence that a news feed alone is already given away ("Energy Wire") says the Digest's difference must be its numbers traced to the warehouse, which is what session 402's checker and session 442's audit test.

### Tool 2: Real-time price board

- **The reports.** AG: Ask the Grid already ships "hub-price pages" and "LMP maps" free, so live-price surfaces are "now commoditized" ([AG, Key Findings row 1](research/ask-the-grid-landscape-2026-10.md#key-findings-ranked-by-how-much-they-should-change-what-gets-built-next); [AG, TL;DR](research/ask-the-grid-landscape-2026-10.md#tldr)); its option is to keep the live views as "thin thesis-chart views" ([AG, Recommendations 3](research/ask-the-grid-landscape-2026-10.md#recommendations-options-not-cuts)). DR does not name a price board.
- **The ERW today.** On main: [site/app/board](../../site/app/board) and [site/app/prices](../../site/app/prices), with the method [docs/methods/price_board.md](../methods/price_board.md). Three of its four derived tables (`price_board_latest`, `price_board_peak_offpeak`, `price_board_spreads`) are held for a license on ISO-NE, MISO and NYISO rows ([license_status.csv](../../warehouse/metadata/license_status.csv)). The board's ERCOT day-ahead tiles stopped on 15 October ([docs/state/review_2026-10-21_night_code.md](../state/review_2026-10-21_night_code.md), "Waiting for you" 4).
- **Recommendation: third.** Kept current and in parallel with Ask the Grid, as the owner ruled; this week's work is freshness and the holds, not a new feature, because AG's evidence is that a feature race on live prices is lost to a faster, funded team ([AG, Key Findings row 7](research/ask-the-grid-landscape-2026-10.md#key-findings-ranked-by-how-much-they-should-change-what-gets-built-next)).

### Tool 3: Energy project map

- **The reports.** AG: Ask the Grid ships "interconnection-queue maps" and a blog piece reading datacenter clusters through the queue, so tool 3 is "partly" covered ([AG, Key Findings row 1](research/ask-the-grid-landscape-2026-10.md#key-findings-ranked-by-how-much-they-should-change-what-gets-built-next); [AG, section 1, Written content](research/ask-the-grid-landscape-2026-10.md#1-parisi-labs-and-ask-the-grid-verified-facts)). DR: its third LinkedIn post overlays datacenter sites on a transmission map with interconnection queues, and it names Cleanview's paid project pipelines as the competitor ([DR, Roadmap, first posts 3](research/deep-research-report.md#roadmap-what-to-build-and-publish-next-6-months); [DR, Landscape](research/deep-research-report.md#energy-data-tools-and-analysis-landscape)).
- **The ERW today.** On main: [site/app/map](../../site/app/map) with its Queues tab (`QueuesView.tsx`, from `wip/348-map`, now on main) and [site/app/queues](../../site/app/queues); method [docs/methods/energy_projects.md](../methods/energy_projects.md). `energy_projects` is held for a license on its ISO-NE rows ([license_status.csv](../../warehouse/metadata/license_status.csv)).
- **Recommendation: third.** Kept as it stands; the queue work landed on 20 October, and neither report gives evidence that more map work would change a reader's decision this week.

### Tool 4: Datacenter power tracker

- **The reports.** AG ranks it fourth of what to build: Epoch AI's free Frontier Data Centers Hub "owns facility-level AI data-center power estimates", so the ERW should build "on the power side (utility, ISO, interconnection, cost of power) and link to Epoch rather than duplicating it" ([AG, TL;DR](research/ask-the-grid-landscape-2026-10.md#tldr); [AG, Key Findings row 4](research/ask-the-grid-landscape-2026-10.md#key-findings-ranked-by-how-much-they-should-change-what-gets-built-next); [AG, Recommendations 5](research/ask-the-grid-landscape-2026-10.md#recommendations-options-not-cuts)). DR names the free ElectricChoice tracker and Cleanview's paid pipelines, and advises "unique angles" over "raw pipelines" ([DR, Landscape](research/deep-research-report.md#energy-data-tools-and-analysis-landscape); [DR, Risks, Competitors](research/deep-research-report.md#risks-constraints-and-timing)).
- **The ERW today.** On main: [site/app/datacenters](../../site/app/datacenters), method [docs/methods/datacenter_facilities.md](../methods/datacenter_facilities.md). All four of its tables are held whole for a license from 21 October: `datacenter_facilities`, `datacenter_projects`, `datacenter_operator_sites` and `datacenter_queue_positions` ([license_status.csv](../../warehouse/metadata/license_status.csv)). Tonight's session 441 counts their rows by the license of each row's source, on this branch.
- **Recommendation: second.** The two reports agree here: the facility list is not the ERW's ground, the power side is. The blocker is the license: until session 441's split by row lands, the page shows nothing public, so the power-side fields come after it.

### Tool 5: Signature data explorers

- **The reports.** AG puts "peer-reviewed analysis such as 'Donor Grids and Taker Grids'" in the ERW's defensible ground and recommends shipping "the Donor/Taker paper and the Redivis release before the Oct 30 LOI" ([AG, opening](research/ask-the-grid-landscape-2026-10.md); [AG, Recommendations 4](research/ask-the-grid-landscape-2026-10.md#recommendations-options-not-cuts)). DR places "interactive tools/demos" fifth, in months 4 to 6 ([DR, Roadmap, suggested content order](research/deep-research-report.md#roadmap-what-to-build-and-publish-next-6-months)).
- **The ERW today.** On main: the first explorer, [site/app/explorer/ercot-peak-premium](../../site/app/explorer/ercot-peak-premium). On branches, not on main: sessions 403 to 405's three explorers ([ercot-peak-premium on wip/403-s](https://github.com/SamuelEnrique/erw/blob/wip/403-s/site/app/explore/ercot-peak-premium/page.tsx), [demand-growth on wip/404-s](https://github.com/SamuelEnrique/erw/blob/wip/404-s/site/app/explore/demand-growth/page.tsx), [interconnection on wip/405-s](https://github.com/SamuelEnrique/erw/blob/wip/405-s/site/app/explore/interconnection/page.tsx)). "Donor Grids and Taker Grids" is not a file or a title in the repository: `git grep -i donor` on main finds it only in AG. The nearest work is the Grid tool's gravity shape, where "a net importer sits nearer the center, a net exporter farther out" ([docs/methods/grid_network.md](../methods/grid_network.md), "The gravity shape").
- **Recommendation: second.** Land the three explorers as they stand once the database answers again; where the Donor/Taker paper lives, or whether it is still to be written, is Samuel's to say (below, "For Samuel").

### Tool 6: Energy deal tracker

- **The reports.** AG ranks it first with tool 16: OpenAI's Power Trading Lead posting ("fixed-price supply, forwards, swaps and options"), with utility, infrastructure-finance and energy-policy leads beside it, and "nobody publishes open, editable economics" ([AG, TL;DR](research/ask-the-grid-landscape-2026-10.md#tldr); [AG, Key Findings row 3](research/ask-the-grid-landscape-2026-10.md#key-findings-ranked-by-how-much-they-should-change-what-gets-built-next); [AG, Recommendations 2](research/ask-the-grid-landscape-2026-10.md#recommendations-options-not-cuts)). What those roles reach for includes "PPA and deal comparables" ([AG, section 4](research/ask-the-grid-landscape-2026-10.md#4-what-labs-need-evidence)). DR does not name a deal tracker; its nearest line is the finance angle among its differentiators ([DR, Roadmap, Differentiators](research/deep-research-report.md#roadmap-what-to-build-and-publish-next-6-months)).
- **The ERW today.** On main: [site/app/deals](../../site/app/deals), method [docs/methods/energy_deals.md](../methods/energy_deals.md). `energy_deals` is held whole for a license: its rows rest on news publishers ([license_status.csv](../../warehouse/metadata/license_status.csv)). On a branch since 5 October: session 130's power deals ([site/app/deals/v3 on wip/130-deals-v3](https://github.com/SamuelEnrique/erw/blob/wip/130-deals-v3/site/app/deals/v3/page.tsx)), not on main.
- **Recommendation: first, behind the license.** The evidence is the strongest in either report, but a deal list that rests on publishers who ask for permission cannot be shown. This week's work is the public-source subset (a company's own announcement, a regulator's filing) that session 441 sets out, so that the page can show those rows.

### Tool 7: Grid stress and real-time conditions

- **The reports.** AG: Ask the Grid ships "a free live map, grid agent", with live status through its MCP tools ([AG, Key Findings row 1](research/ask-the-grid-landscape-2026-10.md#key-findings-ranked-by-how-much-they-should-change-what-gets-built-next); [AG, section 1, What the product exposes](research/ask-the-grid-landscape-2026-10.md#1-parisi-labs-and-ask-the-grid-verified-facts)). DR notes that every major operator publishes near-real-time load and generation on its own dashboard ([DR, Landscape, Open data](research/deep-research-report.md#energy-data-tools-and-analysis-landscape)).
- **The ERW today.** On main: the Grid tool, one page with four tabs (Network, Mix, Clean, Gravity) and an Ask panel ([site/app/grid](../../site/app/grid)), method [docs/methods/grid_network.md](../methods/grid_network.md), review pack [docs/reviews/packs/grid.md](packs/grid.md).
- **Recommendation: third.** In parallel with Ask the Grid, as ruled; the Grid pack's remaining items of roadmap item 2 (a signed note, the cross-checks) are the work, not a new view.

### Tool 8: Regional power-price heatmap

- **The reports.** AG: "LMP maps" are among what Ask the Grid ships free, and it publishes PJM node prices without a stated ISO license ([AG, Key Findings row 1](research/ask-the-grid-landscape-2026-10.md#key-findings-ranked-by-how-much-they-should-change-what-gets-built-next); [AG, section 1, Terms of service and licensing](research/ask-the-grid-landscape-2026-10.md#1-parisi-labs-and-ask-the-grid-verified-facts)). DR's fifth item is "a map showing real-time LMP prices vs projected AI load" ([DR, Roadmap, suggested content order](research/deep-research-report.md#roadmap-what-to-build-and-publish-next-6-months)).
- **The ERW today.** No node price map on main. Node prices appear as the node basis on the economics pages ([site/app/cost-of-power/seller](../../site/app/cost-of-power/seller), session 353) and the battery page's storage nodes (session 355). The heat map rule is in [docs/brand.md](../brand.md), "Heat maps".
- **Recommendation: third, last of the live views.** PJM prices are not licensed to the ERW and MISO is paused ([AG, section 2](research/ask-the-grid-landscape-2026-10.md#2-iso-licensing-facts-relevant-to-the-erws-own-gate)); a nodal map of the grids the ERW may show is possible later, and nothing in either report says it would change a reader's decision this week.

### Tool 9: Flagship newsletter

- **The reports.** DR recommends a weekly or fortnightly newsletter it names "AI & Energy Dispatch" and ranks it fourth ([DR, Roadmap, Newsletter](research/deep-research-report.md#roadmap-what-to-build-and-publish-next-6-months); [DR, Risks, ranking](research/deep-research-report.md#risks-constraints-and-timing)). AG makes no newsletter recommendation.
- **The ERW today.** On main: the Digest and Roundup by email ([warehouse/news/email_digest.py](../../warehouse/news/email_digest.py), tool 25). On a branch: session 406's first issue ([docs/reviews/newsletter/issue-001.md on wip/406-s](https://github.com/SamuelEnrique/erw/blob/wip/406-s/docs/reviews/newsletter/issue-001.md)), which stays there unused by Samuel's ruling of 21 October.
- **Recommendation: later.** Samuel's ruling settles it: no newsletter of any kind; the master plan's tool 9 is carried by the Digest and the Roundup by email. DR's "AI & Energy Dispatch" is not taken.

### Tool 10: Energy-intelligence company database

- **The reports.** Neither names it. AG's lab roles point at deal comparables and counterparties, which a company table would serve ([AG, section 4](research/ask-the-grid-landscape-2026-10.md#4-what-labs-need-evidence)).
- **The ERW today.** On main: [site/app/companies](../../site/app/companies) and the seeders in [warehouse/companies](../../warehouse/companies); `energy_companies` is seeded from the Thesis Builder and the deal parties ([docs/platform-tools.md](../platform-tools.md), row 10). Tonight's session 443 writes `docs/reviews/companies-seed.csv` on this branch.
- **Recommendation: later.** It is seeded from the deals, so it follows tool 6's license split; no report evidence moves it up.

### Tool 11: Capital flows tracker

- **The reports.** AG lists tool 11 among those the lab roles touch (infrastructure finance) ([AG, Key Findings row 3](research/ask-the-grid-landscape-2026-10.md#key-findings-ranked-by-how-much-they-should-change-what-gets-built-next)). DR suggests one analysis of the "capital needed to expand U.S. grid by 50 GW" ([DR, Roadmap, Differentiators](research/deep-research-report.md#roadmap-what-to-build-and-publish-next-6-months)).
- **The ERW today.** No table and no page: only news stories tagged `capital` ([docs/platform-tools.md](../platform-tools.md), row 11).
- **Recommendation: later.** Capital flows are the financing rows of the deal tracker; they follow tool 6, and a new source for them is under the roadmap's hold on new sources ([docs/roadmap.md](../roadmap.md), "Holds").

### Tool 12: Policy and regulatory monitor

- **The reports.** AG: the lab roles reach for "policy and regulatory tracking", and OpenAI's clean energy lead works "closely with regulatory and policy teams" ([AG, section 4](research/ask-the-grid-landscape-2026-10.md#4-what-labs-need-evidence)). DR's fifth LinkedIn post is a policy angle on a FERC rule or a moratorium ([DR, Roadmap, first posts 5](research/deep-research-report.md#roadmap-what-to-build-and-publish-next-6-months)).
- **The ERW today.** On main: [site/app/policy](../../site/app/policy) and [warehouse/policy](../../warehouse/policy) (`policy_actions`, `policy_reads`); `policy_actions` is not among the 42 tables held ([license_status.csv](../../warehouse/metadata/license_status.csv)). The Virginia State Corporation Commission is paused ([docs/methods/vascc_pause.md](../methods/vascc_pause.md)).
- **Recommendation: second.** It is public today and serves what AG says the roles need; this week it is kept refreshed; more state dockets wait for the hold on new sources to be lifted.

### Tool 13: Deep-dive report library

- **The reports.** DR ranks long-form pieces second and drafts three titles ([DR, Roadmap, First long-form pieces](research/deep-research-report.md#roadmap-what-to-build-and-publish-next-6-months); [DR, Risks, ranking](research/deep-research-report.md#risks-constraints-and-timing)). AG notes that Ask the Grid already publishes "Stories" and "Reports, written for you" ([AG, section 1, Written content](research/ask-the-grid-landscape-2026-10.md#1-parisi-labs-and-ask-the-grid-verified-facts)).
- **The ERW today.** On main, in review: two drafts under [site/app/reports/draft](../../site/app/reports/draft) (`ai-gigawatts`, `shape-premium`).
- **Recommendation: later.** Samuel's ruling: no long-form piece until the Digest and the Roundup are perfect. DR's three titles are not taken; the drafts stay in review.

### Tool 14: Weekly state-of-energy brief (the Energy Roundup)

- **The reports.** As for tool 1: AG's "Energy Wire" and "Stories" partly cover written news ([AG, section 1, Written content](research/ask-the-grid-landscape-2026-10.md#1-parisi-labs-and-ask-the-grid-verified-facts)); DR's weekly newsletter is the nearest thing it names ([DR, Roadmap, Newsletter](research/deep-research-report.md#roadmap-what-to-build-and-publish-next-6-months)).
- **The ERW today.** On main: [site/app/roundup](../../site/app/roundup), [warehouse/news/roundup.py](../../warehouse/news/roundup.py), issues in [docs/roundup](../roundup) (2026-W39 to W41). Tonight's session 444 audits every issue on this branch.
- **Recommendation: first,** with tool 1 and for the same ruling; session 444's section on what the two periodicals share (the clustering, the scoring, the chart code) is where one fix lands in both.

### Tool 15: Data downloads and methodology

- **The reports.** DR's first priority is to "make a public release: document the data (sources, refresh cadence), publish an API or simple web interface" ([DR, Roadmap, top priority](research/deep-research-report.md#roadmap-what-to-build-and-publish-next-6-months)), ranked first ([DR, Risks, ranking](research/deep-research-report.md#risks-constraints-and-timing)). AG: build "citable releases (Redivis DOIs) and Stata/R/Python packages", and "publish the license audit as a methodology page" ([AG, Key Findings row 6](research/ask-the-grid-landscape-2026-10.md#key-findings-ranked-by-how-much-they-should-change-what-gets-built-next); [AG, Recommendations 1 and 4](research/ask-the-grid-landscape-2026-10.md#recommendations-options-not-cuts)).
- **The ERW today.** On main: [site/app/data](../../site/app/data), the download route [site/app/api/download](../../site/app/api/download), the release package [warehouse/redivis/release_v1.py](../../warehouse/redivis/release_v1.py), the license record [docs/licenses.md](../licenses.md). Version 1 on Redivis waits for a person's click and for Redivis storage, full at 10 GB ([docs/state/morning_2026-10-21_day.md](../state/morning_2026-10-21_day.md), "Waiting for you" 1). On a branch: session 410's catalogue agreement ([wip/410-s](https://github.com/SamuelEnrique/erw/blob/wip/410-s/archive/sessions/SESSION_410_REPORT.md)). Tonight's session 445 writes `docs/guide.md`, a reader's guide.
- **Recommendation: first.** The one place both reports agree on the top rank. The blockers are Samuel's: Redivis storage, Ben's organization, the release click.

### Tool 16: Cost-of-power model

- **The reports.** AG ranks it first: "Elevate 16 (cost of power) and 6 (deal tracker)... Build with Lazard hurdle rates shown and every assumption editable" ([AG, Recommendations 2](research/ask-the-grid-landscape-2026-10.md#recommendations-options-not-cuts)), and calibrate the battery against Modo's published ERCOT figure, "$29.4/kW" for 2025 ([AG, Recommendations 6](research/ask-the-grid-landscape-2026-10.md#recommendations-options-not-cuts); [AG, section 3](research/ask-the-grid-landscape-2026-10.md#3-landscape-verified-rows-only)). DR: its fourth post is the "projected cost to power 1 MW of new AI compute", and its second long-form piece models power costs by region ([DR, Roadmap](research/deep-research-report.md#roadmap-what-to-build-and-publish-next-6-months)).
- **The ERW today.** On main: three pages, [site/app/cost-of-power](../../site/app/cost-of-power) (the datacenter), [seller](../../site/app/cost-of-power/seller) (the generator) and [battery](../../site/app/cost-of-power/battery), with methods [battery_earns_algorithm.md](../methods/battery_earns_algorithm.md), [generator_earns_algorithm.md](../methods/generator_earns_algorithm.md) and [datacenter_pays_algorithm.md](../methods/datacenter_pays_algorithm.md) and review packs [battery.md](packs/battery.md), [generator.md](packs/generator.md), [datacenter.md](packs/datacenter.md). Lazard's hurdle rate is already the default, and every assumption already shows its default and source ([docs/roadmap.md](../roadmap.md), "Rulings", 12 October). Tonight's session 448 writes the cross-check rows against Lazard and NREL on this branch.
- **Recommendation: first.** AG's evidence is that this is the ERW's ground; the pages already do what AG asks. What remains is roadmap v2's item 2: the signed method notes and the cross-checks landed as checks. Modo's figure is a new source under the hold, so its use is Samuel's to rule.

### Tool 17: Economic forecasting tool (tax and jobs impact)

- **The reports.** Neither report mentions it.
- **The ERW today.** On main since 20 October: [site/app/impact/page.tsx](../../site/app/impact/page.tsx), method [docs/methods/economic_impact.md](../methods/economic_impact.md), review pack [docs/reviews/packs/impact.md](packs/impact.md).
- **Recommendation: later.** Landed and kept as it stands; no evidence in either report to move it.

### Tool 18: Predictive and scenario layer

- **The reports.** AG: Ask the Grid's Metis gives probabilistic price forecasts "free with an account at major trading hubs", and Modo sells BESS forecasts ([AG, section 1, Forecasts](research/ask-the-grid-landscape-2026-10.md#1-parisi-labs-and-ask-the-grid-verified-facts); [AG, Key Findings row 5](research/ask-the-grid-landscape-2026-10.md#key-findings-ranked-by-how-much-they-should-change-what-gets-built-next)). DR places an "AI-forecast model" last and warns to "keep prototypes simple" ([DR, Roadmap, suggested content order](research/deep-research-report.md#roadmap-what-to-build-and-publish-next-6-months); [DR, Risks, Technical risks](research/deep-research-report.md#risks-constraints-and-timing)).
- **The ERW today.** No forecast page. Scenarios live inside the economics pages (scenario A and B; the battery's scenario steps, [warehouse/derived/battery_scenario_steps.py](../../warehouse/derived/battery_scenario_steps.py)); the stress slider is in the Backlog ([docs/roadmap.md](../roadmap.md), "Backlog").
- **Recommendation: later.** A price forecast is given away at the hubs already; the scenario layer stays inside tool 16, as it is.

### Tool 19: Data and API products

- **The reports.** They disagree. DR: "publish an API or simple web interface" ([DR, Roadmap, top priority](research/deep-research-report.md#roadmap-what-to-build-and-publish-next-6-months)). AG: "Do not build a competing data API; build citable releases (Redivis DOIs) and Stata/R/Python packages" ([AG, Key Findings row 6](research/ask-the-grid-landscape-2026-10.md#key-findings-ranked-by-how-much-they-should-change-what-gets-built-next)).
- **The ERW today.** On main: the `erw` package ([package](../../package), with [package/llms.txt](../../package/llms.txt)), the download route ([site/app/api/download](../../site/app/api/download)), and Redivis as the store of record. No public API.
- **Recommendation: first, with tool 15, as packages and releases, not an API.** AG's reason is specific (Grid Status already gives a free 500,000-row API tier, [AG, section 3](research/ask-the-grid-landscape-2026-10.md#3-landscape-verified-rows-only)); DR's is general. Session 445's guide brings the package README and `llms.txt` to agree with the reader's path.

### Tool 20: AI chat over the warehouse

- **The reports.** AG: Ask the Grid runs a grid agent and an MCP server ("8 markets, 356 datasets, 15 typed tools"), and suggests using its MCP for the ERW's own research "after reading /terms" ([AG, section 1, What the product exposes](research/ask-the-grid-landscape-2026-10.md#1-parisi-labs-and-ask-the-grid-verified-facts); [AG, Recommendations 3](research/ask-the-grid-landscape-2026-10.md#recommendations-options-not-cuts)). DR: "a simple browser app querying your data" in months 4 to 6 ([DR, Roadmap, suggested content order](research/deep-research-report.md#roadmap-what-to-build-and-publish-next-6-months)).
- **The ERW today.** On main: [site/app/ask](../../site/app/ask) and [warehouse/chat](../../warehouse/chat) (four tools, a number check on every stated figure), and the Ask panel on every Grid tab ([site/app/grid](../../site/app/grid)). Session 320's thirty questions: 17 of 30 right ([docs/state/review_2026-10-20_code.md](../state/review_2026-10-20_code.md), "What landed").
- **Recommendation: third.** In parallel, not by copying: the ERW's difference is that every number the answer states must appear in a tool result. Using Ask the Grid's MCP is Samuel's to rule; neither AG nor session 413 could read its terms ([AG, section 1, Terms of service and licensing](research/ask-the-grid-landscape-2026-10.md#1-parisi-labs-and-ask-the-grid-verified-facts); [session 413's review on wip/413-s](https://github.com/SamuelEnrique/erw/blob/wip/413-s/docs/reviews/competitors/2026-10-20.md)).

## 3. This week, as the reports' evidence would have it

In the roadmap's own format ([docs/roadmap.md](../roadmap.md), "This week"), for Samuel to adopt, change or drop. The owner's standing rulings are kept as `rulings:` lines.

1. [ ] The Digest and the Roundup, perfect
   - machine: code
   - where: /digest, /roundup, warehouse/news/brief.py, warehouse/news/roundup.py, warehouse/news/email_digest.py
   - done: every fix of the ranked lists of sessions 442 and 444 landed with the test each names; 14 Digest issues in a row with every number traced to its table and key (session 402's checker on main); every Roundup issue the same
   - rulings: the Digest and the Roundup are the only two periodicals; nothing else is written for the public until they are perfect (21 October 2026)
2. [ ] The license posture, row by row, as a published method
   - machine: data
   - where: docs/licenses.md, warehouse/metadata/license_status.csv, warehouse/metadata/sources.csv, /data
   - done: the four held datacenter and deals tables split by row as session 441's method sets out, the public-source rows shown; the permission letters sent by Samuel and logged; the license audit readable as a method page on /data
   - rulings: the site is not public
3. [ ] The economics pages checked against published figures
   - machine: code
   - where: /cost-of-power, /cost-of-power/seller, /cost-of-power/battery, site/scripts/check-cross-checks.mjs
   - done: session 448's cross-check rows against Lazard and NREL landed as checks; the three method notes signed by Samuel (roadmap v2 item 2); the Modo calibration done or declined by Samuel's ruling
   - rulings: the hurdle rate and debt share of 12 October stand
4. [ ] The deal tracker on its public rows
   - machine: code
   - where: /deals, energy_deals
   - done: the deals whose only source is a public one (a company's own announcement, a regulator's filing) shown on /deals with their source; the held rows named as held
5. [ ] The citable release
   - machine: data
   - where: warehouse/redivis/, the Redivis dataset, /data, docs/guide.md
   - done: Redivis storage settled by Samuel; the dataset under Ben's organization; version 1 released by a person's click and cited on /data; session 445's guide on main
6. [ ] The live views kept current, in parallel
   - machine: code
   - where: /board, /prices, /grid, /ask
   - done: the database answers its heavier reads again; the board's ERCOT tiles current; no feature added to match Ask the Grid; each page states what it holds and under which license
   - rulings: the ERW competes with Ask the Grid on the live views, in parallel, not by copying
7. [ ] The loop runs itself (carried from v2 item 1 unchanged)
   - machine: code
   - where: scripts/planner.py, scripts/chain_queue.py, queue/next/, .github/workflows/
   - done: main green on every scheduled job for seven days; planner: on in this file; queue/next/ never empty for a week

### From v2 to this draft

| v2 item | In this draft |
|---|---|
| 1 The loop runs itself | 7, unchanged |
| 2 Five tools sellable | 3 (the economics pages); the Grid tool and Research stay under it, third and second |
| 3 Brand, full | not this week: neither report gives evidence on it; it stays in v2's wording until Samuel moves it |
| 4 Tooling | not this week: installed and used (session 401 on `wip/401-s`) |
| 5 Licensing sweep | 2, extended to the split by row |
| 6 Reliability | inside 6 (the database) and 7 |
| 7 Security closed, cookieless analytics | not this week; unchanged in v2 |
| 8 First users ready | not this week; the trader path is written ([docs/reviews/trader-path.md](trader-path.md)) and waits for its walkers |
| 9 Warehouse as citable record | 5 |
| 10 LOI | not an item: AG's "before the Oct 30 LOI" ([AG, Recommendations 4](research/ask-the-grid-landscape-2026-10.md#recommendations-options-not-cuts)) is Samuel's date to confirm |

## 4. Where the two reports disagree

1. **ISO data and licensing.** DR: "Using public data (EIA, ISOs, GIS shapefiles, etc.) is generally safe" ([DR, Risks, Data licensing](research/deep-research-report.md#risks-constraints-and-timing)). AG: PJM, MISO and ISO-NE restrict redistribution, and no competitor states an ISO license ([AG, section 2](research/ask-the-grid-landscape-2026-10.md#2-iso-licensing-facts-relevant-to-the-erws-own-gate)). The ERW's own record sides with AG: 42 tables held for a license from 21 October ([license_status.csv](../../warehouse/metadata/license_status.csv)), the figure AG quotes as "Your audit (42 tables needing permission)".
2. **An API.** DR: "publish an API or simple web interface" ([DR, Roadmap](research/deep-research-report.md#roadmap-what-to-build-and-publish-next-6-months)). AG: "Do not build a competing data API" ([AG, Key Findings row 6](research/ask-the-grid-landscape-2026-10.md#key-findings-ranked-by-how-much-they-should-change-what-gets-built-next)).
3. **Live maps.** DR's fifth item is a live LMP map against projected AI load ([DR, Roadmap, suggested content order](research/deep-research-report.md#roadmap-what-to-build-and-publish-next-6-months)). AG: live-price surfaces are commoditized; keep them as thin thesis-chart views ([AG, Recommendations 3](research/ask-the-grid-landscape-2026-10.md#recommendations-options-not-cuts)). The owner's ruling sits between: compete in parallel, not by copying.
4. **What comes second.** DR ranks long-form pieces second and a newsletter fourth ([DR, Risks, ranking](research/deep-research-report.md#risks-constraints-and-timing)); AG ranks the economics models and the deal tracker first and the citable release and paper second ([AG, TL;DR](research/ask-the-grid-landscape-2026-10.md#tldr)). Samuel's ruling of 21 October rules out the long-form piece and the newsletter for now, so AG's order governs this draft.
5. **Whom the work is for.** DR is written for a person's visibility to recruiters and investors ([DR, Playbook](research/deep-research-report.md#playbook-from-similar-successes)); AG for the ERW's place against named products ([AG, Key Findings](research/ask-the-grid-landscape-2026-10.md#key-findings-ranked-by-how-much-they-should-change-what-gets-built-next)). They name different competitors: DR, Cleanview, ElectricChoice and the legacy vendors ([DR, Landscape](research/deep-research-report.md#energy-data-tools-and-analysis-landscape)); AG, Ask the Grid, Grid Status, Modo and Epoch ([AG, section 3](research/ask-the-grid-landscape-2026-10.md#3-landscape-verified-rows-only)). Neither names the other's.
6. **When to launch.** DR: a public release in months 1 to 2 ([DR, Roadmap, suggested content order](research/deep-research-report.md#roadmap-what-to-build-and-publish-next-6-months)). AG: launch publicly on the data that is clean today ([AG, Recommendations 1](research/ask-the-grid-landscape-2026-10.md#recommendations-options-not-cuts)). The owner's standing ruling: the site is not public.

## 5. What neither report checked

1. **The ERW itself.** Neither report read the repository or the pages. DR speaks of "your warehouse" in general ([DR, Roadmap](research/deep-research-report.md#roadmap-what-to-build-and-publish-next-6-months)); AG uses one ERW figure (42 tables needing permission) and the tool numbers. What the ERW already does that AG recommends (Lazard's hurdle rate as the default, every assumption shown, a replication, Stata and Python readers) is in [docs/roadmap.md](../roadmap.md), "Rulings", and [docs/methods/battery_earns_algorithm.md](../methods/battery_earns_algorithm.md).
2. **The two periodicals against others.** Neither compares the Digest or the Roundup with another daily or weekly energy brief; AG lists the newsletters it did not reach (Heatmap, Latitude Media, Volts and others) ([AG, section 3](research/ask-the-grid-landscape-2026-10.md#3-landscape-verified-rows-only)).
3. **Lazard and NREL themselves.** AG lists both as not verified ([AG, section 3](research/ask-the-grid-landscape-2026-10.md#3-landscape-verified-rows-only)) while recommending Lazard's hurdle rates; tonight's session 448 checks the pages against them.
4. **Ask the Grid's terms.** AG could not retrieve them ([AG, Caveats](research/ask-the-grid-landscape-2026-10.md#caveats)), and session 413's reads answered 403 ([session 413's review, section 2, on wip/413-s](https://github.com/SamuelEnrique/erw/blob/wip/413-s/docs/reviews/competitors/2026-10-20.md)). Using its MCP waits on a person reading them.
5. **Epoch's terms.** AG recommends linking to Epoch's hub ([AG, Recommendations 5](research/ask-the-grid-landscape-2026-10.md#recommendations-options-not-cuts)) but did not research Epoch beyond the hub ("Nonprofit (not researched)", [AG, section 3](research/ask-the-grid-landscape-2026-10.md#3-landscape-verified-rows-only)); a link costs nothing, any reuse of its figures needs its terms read.
6. **The cost of a license.** Neither prices PJM Associate Membership or a permission letter; AG recommends applying ([AG, Recommendations 1](research/ask-the-grid-landscape-2026-10.md#recommendations-options-not-cuts)).
7. **The ERW's own blockers.** Neither knows of the Redivis storage limit or the database timeouts of 20 and 21 October ([docs/state/morning_2026-10-21_day.md](../state/morning_2026-10-21_day.md); [docs/state/review_2026-10-21_night_code.md](../state/review_2026-10-21_night_code.md)), which block items 5 and 6 above more than any competitor does.
8. **A reader.** Neither tested a page with a trader, a lab buyer or a researcher; the ERW's trader path is written and not yet walked ([docs/reviews/trader-path.md](trader-path.md)).
9. **DR's own sources.** DR carries no source list and no links: its figures (ElectricChoice's ~3,525 datacenters and 192 TWh a year, Cleanview's USD 9,000 to 10,000 a year and ~445 GW) and its names of people, roles and companies cannot be traced from the file ([DR, Landscape](research/deep-research-report.md#energy-data-tools-and-analysis-landscape); [DR, Roles](research/deep-research-report.md#roles-at-anthropic-openai-sequoia-and-a16z)). None should be quoted outside the project before a person checks it.

## 6. For Samuel

1. Adopt, change or drop this "This week" (section 3) as v4.
2. "Donor Grids and Taker Grids": where it is, or whether it is still to be written (tool 5).
3. Modo's ERCOT figure as a calibration of the battery page: a new source under the hold (tool 16).
4. Ask the Grid's MCP for the ERW's own research: only after a person reads its terms (tool 20).
5. AG's "before the Oct 30 LOI": whether that date stands, and what it needs (v2 item 10).
