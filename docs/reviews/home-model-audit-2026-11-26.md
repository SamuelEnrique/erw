# The home page, the tour and the Thesis Builder: audited as a hostile first reader would

Session 10236, 26 November 2026, chain 710 (part D), the old laptop. Read as a fund analyst, or an AI lab's energy lead, arriving cold: someone who opens `/`, takes the tour to see whether the ERW is worth an afternoon, and is shown the Thesis Builder by a reviewer, and who wants to find the first sentence that is not true. In the form of `docs/reviews/data-model-audit-2026-11-26.md`.

- Nothing changed on main but this file and its folder of evidence (`docs/reviews/home-model-audit-2026-11-26/`). No table written, no lock taken, no default moved, no model called (`ERW_SPEND_CAP_USD=0` for every python run; no route or script that calls a model was run), no request to any service.
- Each finding's test is on its own branch, `wip/audit-home-<n>`. Branches that change only words are for landing (the rows at the foot); a branch whose fix would change what is drawn or stored carries the test only and is not for landing.
- **What is audited.** The home page `/` (`site/app/page.tsx`; the draft `/home/v2` is read only for what the tour says of it); the tour (`/tour`, `/tour/1` to `/tour/16`, `site/app/tour/`, `site/lib/tour.ts`, and the tour's line in `site/lib/pages.ts`); the Thesis Builder (`/thesis`, platform tool 27: `site/app/thesis/page.tsx`, `site/lib/thesis/`, `site/components/thesis/`, the three routes under `site/app/api/thesis/`, `warehouse/thesis/run.py` and its modules, migrations 024 to 026, `.github/workflows/thesis.yml`, the method note `docs/methods/thesis.md`, its line in `site/lib/pages.ts`). A claim about another tool that tonight's audit of that tool found false is a finding here only for these pages' own words, with the other audit cited.

## In short

- **The numbers are right.** Every figure the home page computes came out to the digit from the same rows in an independent restatement and again in the page as the site's own code draws it: the default battery's USD 81.40 per kW (October 2025 to September 2026 on this machine's table), ERCOT's 54,234 MW at 23:00 UTC on 12 November, 54,488.9 MW of batteries operating in the US and 18,204.5 MW in ERCOT, the three fuels' closes, the 11 of the findings figure. The tour's 16 stops and "about 10 minutes" (595 seconds), and its stops' own numbers (13 regions, 6 new; the 9 events; since 2019; since 2001), agree with their files. The Thesis Builder's gate gives the same verdict and reason as a restatement from the owner's rules on 100 of 100 inputs; on its five saved runs the funnel's counts, the landscape and the pipeline restate exactly (25 of 25 stage counts).
- **The home page's Digest block prints "no data" (finding 1).** The newest issue, of 12 November, is in the new form, with no "Top of the industry"; the block's link reads "The full Digest of ERW Daily Digest, 2026-11-12 and the archive". The link's words are fixed; reading the new form's "What moved" (5 stories) is for ruling.
- **Three of the five groups' words say more than their figures (findings 2 to 4).** "Every answer from the tables" is said of the Thesis Builder, whose reports rest on web pages and the EIA's and FRED's series; "11 findings" counts the catalogue's analyses, seven findings (three in two versions) and the impact study; "what a 100 MW, 4-hour battery in ERCOT earned" is the model's battery with perfect foresight of prices. Fixed in words.
- **The tour's Digest stop sends the reader to headings that are not there (finding 8),** "Top of the industry" and "ERW's Numbers Today": `/digest` has drawn no issue since 12 November, and the new form has no "Top of the industry". The tour's description says "Twelve stops ... about eight minutes" (16 and 10), its lead names 5 of the 9 later stops, and twice it says the home page "lists every tool by who it is for", which the home page has not done since session 300 (findings 9 and 10). Fixed in words.
- **The Thesis Builder's description promises a company map it no longer makes (finding 12).** Since 9 October a run searches for no company; the landscape, the funnel and the pipeline fill only from a provider's answer a person pastes. Its method note says a number not found in a cited source "is not shown"; the code prints it in any sentence of 40 characters or more, followed by "(not confirmed: ...)", 80 numbers in 49 texts of the five saved runs (finding 13). Fixed in words; hiding them is for ruling.
- **What a user's upload holds and where it goes is as the code says.** A Harmonic answer is stored whole with the run (internal table, SHA-256 of the pasted text); a PitchBook answer in the run's row under a one-time key; a Crunchbase answer is refused before it is read. No pasted text goes to a model. The niche typed goes to Anthropic's small model only when the rules cannot decide, and the run sends niche, stage and geography to the run's models. `/privacy` names none of this (listed for Samuel; it applies only to the internal view).
- **The spending guard caps a run at USD 1.00 and a day at USD 8.00, six runs a day; the gate's call at 40 an hour on one server instance.** A stage that costs more than its reserve is kept: the ceiling stops the next stage, not the call (two of the five saved runs, at the old ceiling, cost USD 1.42 and 1.14).
- **Eleven branches fix words and move no figure; two carry a test only, for ruling (the Digest's stories; the held grids' interval times on the strip); one shows the literal-number check's behaviour for ruling.** No data request. Nothing needs the key. No security weakness of high severity was found.

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/page.tsx` | `/`: the title; "Right now" (the newest real-time interval of each grid's main hub or zone from `latest_prices`, Henry Hub, WTI and Brent from `eia_fuel_spot_prices`); today's chart (the newest record of `docs/digest/charts/`); the five groups, each a line and one live number; the latest Digest's first five stories; the source line |
| `site/lib/batterystack.ts` | The Economics figure: the default battery (ERCOT, 4 hours, perfect foresight, 100 MW) from `battery_stack_monthly`, the last twelve whole months' total per kW |
| `site/lib/data.ts` (`latestPrices`, `newest`, `storageUnits`), `site/data/markets.json` | The strip's reads; the Grid figure (`eia930_all_demand`, `eia930:ERCO`); the Infrastructure and Games figures (`storage_capacity`, status operating, US and ERCOT) |
| `site/data/findings/catalogue.json`, `site/lib/analysisflow.ts` | The Analysis figure (the catalogue's length) and what the research flow says the catalogue holds |
| `site/components/Num.tsx` (`heldBy`), `site/lib/license.ts` | A held grid's figure drawn "license needed" |
| `site/lib/markdown.ts` (`topItems`, `digestTitle`, `digestChartDays`), `docs/digest/latest.md`, `docs/digest/charts/` | The Digest block and today's chart |
| `site/lib/tour.ts`, `site/app/tour/page.tsx`, `site/app/tour/[stop]/page.tsx`, `TourBar.tsx`; `site/scripts/check-tour.mjs` | The tour: 7 ruled stops and 9 later ones, each with its seconds, line, what to look at and the headings it quotes; the check that reads the headings on a built site |
| `site/lib/pages.ts` | One line a tool, drawn on `/about` and `/data`: the tour's and the Thesis Builder's lines |
| `site/app/thesis/page.tsx`, `site/lib/thesis/server.ts` | `/thesis`: not found without the internal view's cookie; the runs, the run's report in tabs, the providers' panel |
| `site/lib/thesis/niche.ts`, `nicheModel.ts`, `app/api/thesis/run/route.ts` | The gate on the niche (rules, curated table, one small model call when the rules cannot decide); the route that queues a run |
| `app/api/thesis/pitchbook/route.ts`, `app/api/thesis/provider/route.ts`, `site/lib/thesis/pitchbook.ts`, `providers.ts` | The two routes that take a pasted answer; the readers that check it |
| `warehouse/thesis/run.py`, `build.py`, `series.py`, `providers.py` | The runner (`thesis.yml` on GitHub's runner): the market run since session 169 (`COMPANY_SEARCH = False`), the literal-number check, the spending guard |
| `warehouse/supabase/migrations/024_thesis.sql`, `025_thesis_providers.sql`, `026_thesis_gate.sql` | The internal tables and the token-checked functions; six runs a day |
| `docs/methods/thesis.md` | The public method note (`/data/methods/thesis`) |
| Read from the main copy, never written | `eia930_all_demand`, `eia_fuel_spot_prices`, `storage_capacity` (snapshot retrieved 2026-09-29), `battery_stack_monthly` (2026-10-21), `iso_rtm_hub_prices` (only to answer the strip's read in the drawing) and the five saved runs in `thesis_state/` (6 October 2026, version 1) |

## How every number here was computed

- **The restatement:** `restate.py` (standard library) parses the tour's stops as data, counts and sums them, looks for every quoted heading in the site's sources and the Digest's newest issue, reads the stops' own numbers from their files, and restates the home page's five figures from the main copy's tables by the method notes' rules, not the site's code: the battery's window (a month counts at 90 percent of its days with revenue held; the window ends at the newest whole month whose eleven before it count) and sum; the newest hour; the operating units' MW rounded to a tenth. `thesis.py` writes the gate again from the owner's rules (its word lists read from `niche.ts` as data) and sets it beside the site's own gate (`gate_site.mjs`), restates each saved run's funnel from its rows by the selection rule, and reads the guard's constants.
- **The pages as drawn:** `draw.mjs`, run from `site/` with `register.mjs` (the site's own loaders and a stand-in for `components/Brand.tsx` and `next/navigation`), draws `/`, `/tour`, the 16 stops and six report tabs of a saved run, its database reads answered from the restatement's rows (`home_rows.json`). The strip's `latest_prices` is not held here: the drawing answers it with each main hub's newest hourly row of `iso_rtm_hub_prices`, so the strip is drawn but not restated. No request leaves the machine.
- Copies of the scripts and their printouts are in `docs/reviews/home-model-audit-2026-11-26/` (written to run from `runs/c10236/` of a worktree).
- **Not measured here:** the live figures themselves (no request to the database: the main copy's tables are older than the live set's, so the drawing and the restatement agree with each other on the same rows, not with today's page); the 15-minute strip; a run of the market form (no state of one is kept anywhere this machine can read, see the spending guard).

## The arithmetic re-done

| Figure | The page (drawn from the same rows) | Restated | Gap |
|---|---|---|---|
| Economics | "USD 81.40 per kW", "October 2025 to September 2026" | 81.40, the same window (`foresight_4h_`, ERCOT hub average, 1,419 rows) | 0 |
| Grid | "54,234 MW", "at 23:00 UTC on 2026-11-12, the newest hour held" | 54,234 at 2026-11-12T23:00:00Z | 0 |
| Infrastructure | "54,488.90 MW" | 1,137 operating units, 54,488.9 MW | 0 |
| Games | "18,204.50 MW" | 259 ERCOT units, 18,204.5 MW | 0 |
| Analysis | "11 findings" | 11 catalogue entries | 0 |
| The fuels | 3.0, 89.62, 92.14, 2026-11-11 | the same | 0 |
| Today's chart | 2026-11-12, `eia_state_generation_monthly`, the record's fact | the newest record, the same | 0 |
| The tour | "16 stops", "about 10 minutes", each stop's seconds | 7 + 9 landed; 595 seconds, 9.92 minutes, rounded 10 | 0 |
| The stops' numbers | thirteen regions, six new; the nine events; since 2019; since 2001 | `REGIONS` 13, `NEW_REGIONS` 6; `conditions/index.json` 9 events; base 2019; first year 2001 | 0 |
| The tour's description (`lib/pages.ts`) | "Twelve stops ..., about eight minutes" | 16 stops, about 10 minutes | **Finding 9** |
| The gate | the site's verdict and reason | the owner's rules, written again: 100 of 100 equal (40 typed inputs, 60 curated niches, all 60 of which pass) | 0 |
| The saved runs' funnels | five stage counts each, landscape and pipeline | restated from the funnel rows: 25 of 25 counts; landscape = tied; pipeline = min(10, tied at confidence 60 or more) in 5 of 5; every tied row under 60 says so | 0 |

## Each claim against the files and the code

| Claim | Where | What the files and code do | Verdict |
|---|---|---|---|
| "The live, citable record of the US energy system." | `/`'s title | every page is in review; no Redivis version is released (the data audit's findings 2 and 3) | The ERW's own line (CLAUDE.md); not refiled |
| "Each figure opens the price board ... Prices as each ISO and EIA publish them." | the strip | each figure links `/board`; the values are the tables' | **Right** |
| A held grid's price | the strip | `heldBy` draws "license needed" for NYISO, MISO and ISO-NE; the unit and "real time, the interval from <time>" of the held row are still printed | **Finding 6** |
| "Drawn by code from the scanner's strongest flag of the day" | today's chart | the record's `why`: "the strongest of the scanner's flags of the day that no Digest has shown ... the most related to the day's top stories" | Right in substance (the strongest not yet shown); not refiled |
| "What a 100 MW, 4-hour battery in ERCOT earned" | Economics | the model's battery with perfect foresight (`strat` "foresight"), per kW (the size does not enter); the battery audit's findings 2, 3, 6 and 10 (an idealised model, 3.71 hours at rated power) | **Finding 4** |
| "ERCOT's demand at ... the newest hour held" | Grid | the newest row of `eia930_all_demand` | **Right** |
| "Batteries operating in the US, nameplate power, from EIA's monthly generator inventory" | Infrastructure; Games ("in ERCOT") | status operating holds 20 units, 508 MW, EIA codes as standby or out of service (2 units, 200 MW in ERCOT); the storage audit's finding 6 for its own page | **Finding 5** |
| "In the research library today, each run with the inputs you choose", "findings" | Analysis | the catalogue's 11 entries are the research flow's "seven findings, three of them with two versions ... the impact study"; 14 card files | **Finding 3** |
| "Research on demand, a warehouse you can ask, the events, policy and the Thesis Builder, every answer from the tables." | Analysis's line | the Thesis Builder's reports are written from web search and the EIA's and FRED's series; it is internal | **Finding 2** |
| "The battery game and the EV game, the tour, a bill built line by line, and five problem sets for a class." | Games's line | `/play/battery`, `/play/ev`, `/tour`, `/learn/bill`, `/learn/problems` (five sets) | **Right** |
| "The weekday brief of energy news, scored and ranked"; the first five stories | the Digest block | `latest.md` (12 November, the new form) has no "Top of the industry": the block prints "no data"; the link reads "The full Digest of ERW Daily Digest, 2026-11-12" | **Finding 1** |
| "Every number on this page is read from the ERW's tables and checked against them" | the source line | the strip's and the groups' figures are checked (`Num`); the chart's fact is its table's; the Digest's stories, when drawn, carry the news's own numbers (2026-11-06: "$33.1 ..."; the new form's "USD 74 billion") | **Finding 7** |
| "16 stops ... about 10 minutes: the three tools, the grid, research, the price board and the daily digest, then the whole country: its regions, a storm across it, demand, trade and the resource map." | `/tour`'s lead | 9 later stops; the lead names 5 (not "Where energy goes", "Energy per AI query", "Every state", "Grid conditions") | **Finding 9** |
| "Twelve stops for a first visit, about eight minutes" | the tour's line, `lib/pages.ts` (on `/about` and `/data`) | 16 stops, about 10 minutes | **Finding 9** |
| "After the tour: the home page lists every tool by who it is for" | `/tour`; the last stop | since session 300 `/` shows the five groups by subject, not by audience (that is the draft `/home/v2`) | **Finding 10** |
| Stop 7: "Read \"Top of the industry\", then \"ERW's Numbers Today\"" | `/tour/7` | `/digest` draws today's issue only and has none since 12 November; the newest issue has no "Top of the industry" and "ERW's Numbers Today" only as a sub-heading of "More" | **Finding 8** |
| Stop 14: "The energy a query to an AI model uses, as each publisher printed it" | `/tour/14` | 5 of the 23 rows are a company's whole consumption in a year, 0 per token (the AI energy audit's finding 1); digits the publication printed are dropped (its finding 6, for ruling) | **Finding 11** (the tour's words only) |
| Stop 3: "how clean it is and how soon it can connect" | `/tour/3` | the carbon is a grid average (the datacenter audit's finding 6, words there); the tour claims nothing more | **Right** |
| Stops 1, 2: "whether that pays for building it"; "at a grid's main hub, month by month" | `/tour/1`, `/tour/2` | as the pages compute; their faults are the battery and generator audits' (20 November), not the tour's words | **Right** |
| Stop 8: "the thirteen regions EIA reports, six of them new to the site" | `/tour/8` | `REGIONS` 13, `NEW_REGIONS` 6 | **Right** |
| "Type a niche and get a sourced investment map of it: scope and definitions, trends, the company landscape, the deal funnel, the pipeline, capital, incumbents, risks and policy, every figure with its source." | the Thesis Builder's line, `lib/pages.ts` | `COMPANY_SEARCH = False` since session 169: the landscape, funnel and pipeline are connector tabs until a person pastes a provider's answer; the report is neutral ("never argues which company ... will win") | **Finding 12** |
| "A number is written only if it appears in a fetched source that its row cites. A figure that could not be found there is not shown." | `docs/methods/thesis.md` | `build.check_numbers`: a text under 40 characters becomes "not confirmed"; a longer one keeps the number and adds "(not confirmed: ...)"; 49 texts, 80 numbers in the five saved runs, drawn so in the report's tabs | **Finding 13** |
| "Companies come from three places: the ERW's own companies and deals tables, web search, and PitchBook"; "Which companies are on the map"; "The confidence score" | `docs/methods/thesis.md` | the note's own lead: "The ERW does not search for companies" since 9 October; these sections hold for runs written before | **Finding 14** |
| "The form refuses a sector ... before anything is spent ... for another input one small model call gives the narrower niches, and if it fails the rules decide alone." | `docs/methods/thesis.md` | `judge`: the table answers its topics with no call; the call is made when the rules refuse an input the table does not hold (for its chips) or cannot decide (5 of the 40 typed inputs here); on failure the rules decide | **Right** |
| "Runs and their results are kept in an internal table ... not published ... no download" | `docs/methods/thesis.md` | every grant on `thesis_runs` and `thesis_provider_results` revoked; the functions check the internal token; the page checks the cookie itself and is not found without it | **Right** |
| "The key in the request works once, for that run only." | `docs/methods/thesis.md` | `thesis_pitchbook_accept` sets `pitchbook_key = null` on use | **Right** |
| A Crunchbase answer "is not kept" | the provider route; the note | refused before the pasted text is read, hashed or logged | **Right** |
| "Costs: every model call is logged (api_cost_ledger, step thesis)" | `run.py`'s docstring (internal) | on GitHub's runner the ledger's file is discarded with the runner (the workflow says so); a market run keeps no state in the bucket either (`handle` is none); only `thesis_runs.usd` keeps the spend | An internal comment; the workflow says it plainly; not a branch |
| "one run stops at USD 1 ... the runs of a UTC day together at USD 8 ... at most six runs a day" | `thesis.yml` | `RUN_USD = 1.0`, `DAY_USD = 8.0`, `p_per_day` 6; a stage's overrun is kept and stops the next stage; the hand-run input says "(empty: 2)" and "at most 2" where the code caps at 1.00 | Right as a ceiling between stages; the hand-run words are internal; not a branch |

## What the user's upload holds, where it goes, what is stored

| What | Where it goes | What is stored, and where |
|---|---|---|
| The niche, stage and geography typed | The route (cookie and same origin); the gate's rules in the browser and on the server; Anthropic's small model (`claude-haiku-4-5`, the niche alone, at most 400 characters, in a JSON string marked as data) only when the rules cannot decide or refuse an input the table does not hold; then the runner's models (the niche, stage and geography in the system prompt) and Anthropic's web search | `thesis_runs`: the three fields, the status, the report, the request, the spend; with Run anyway, what the gate read (`gate`) |
| A PitchBook answer (pasted from the person's own Claude chat) | `POST /api/thesis/pitchbook` with the run's one-time key (no cookie; 60 an hour per address; 400 KB at most); checked strictly, then the database function | `thesis_runs.pitchbook`, its time; the key erased. Through the provider route: only the time and the SHA-256 of the pasted text, when it reads as exactly the stored answer |
| A Harmonic answer | `POST /api/thesis/provider` (cookie and same origin; 400 KB) | `thesis_provider_results`: the payload as the reader writes it out, the format, the time, the SHA-256 of the pasted text; once a run and provider |
| A Crunchbase answer | refused by name before the text is read | nothing |
| Any pasted answer | no model, provider or connector is called from either route | |

The runner's own files (its state, its ledger rows) are discarded with the runner for a market run. The internal view's cookie is the only credential of the page and the two cookie routes; the PitchBook route's credential is the key (43 characters, erased on use).

## The spending guard

| Cap | Value | Counted from | What it does not cap |
|---|---|---|---|
| A run | USD 1.00 (`RUN_USD`; `--max-usd` only lowers it) | the run's own meter (token prices plus USD 10 per 1,000 searches) | a stage that costs more than its reserve: `Careful.charge` keeps the paid answer and stops the next stage |
| A stage | reserves 0.45, 0.12, 0.12, 0.06, 0.12, 0.04 (sum 0.91) | the meter before the stage | the stage's own call |
| A UTC day | USD 8.00 (`DAY_USD`) | `thesis_runs.usd` of the day's runs | a run already started |
| Runs a day | 6 (`thesis_submit`, `p_per_day` default) | the day's rows | |
| The gate's call | 40 an hour on one server instance, 400 output tokens, no retry, 8 seconds, `THESIS_GATE_MODEL=0` switches it off | the instance's memory | the instances together; it is a row of the site's cost ledger (`site_thesis_gate`) |
| The ERW's daily cap of scheduled model steps (`health.py`) | | the cost ledger | the Thesis Builder's runs (their ledger rows stay on the runner) |

Two of the five saved runs (version 1, the old USD 2.00 ceiling) cost USD 1.42 and 1.14; no saved run of the market form exists to measure an overrun under today's ceiling.

## What a first reader's own check would hold that this does not

| Item | Size | From |
|---|---|---|
| The date of the Digest's newest issue on the home page | 12 November, 14 days before this audit | `docs/digest/` |
| The strip's interval beside each figure, and which grids are held | 3 of 6 held | `markets.json`, `license.ts` |
| A dated note of when each group's figure was read | the battery's window is printed; the inventory's month is not | `storage_capacity`'s header (retrieved 2026-09-29 on this machine) |
| For the Thesis Builder, a market run to read | none kept outside the internal table | `run.py` (`keep_in_bucket` for company runs only) |

## Findings, largest effect first

| # | Severity | Finding | Effect | Fix | Branch |
|---|---|---|---|---|---|
| 1 | Medium | The home page's Digest block prints "no data" and an odd link | 0 of 5 stories drawn; "The full Digest of ERW Daily Digest, 2026-11-12" | words (the link); the stories for ruling | `wip/audit-home-1`; `wip/audit-home-13` (test only) |
| 2 | Medium | "Every answer from the tables" is said of the Thesis Builder | one tool of the five named | words | `wip/audit-home-2` |
| 3 | Medium | "11 findings" counts analyses | 7 findings, 3 of them in two versions, and the impact study | words | `wip/audit-home-3` |
| 4 | Medium | "What a battery earned" is the model's battery with perfect foresight | the home's one dollar figure | words | `wip/audit-home-4` |
| 8 | Medium | The tour's Digest stop quotes two headings the page does not draw | 2 of 2 headings | words | `wip/audit-home-8` |
| 12 | Medium | The Thesis Builder's line promises a company map no run makes | 3 of its 10 named parts | words | `wip/audit-home-12` |
| 13 | Medium | The method note says an unconfirmed number is not shown | 80 numbers in 49 texts of 5 saved runs | words; hiding them for ruling | `wip/audit-home-14` (words); `wip/audit-home-15` (test only) |
| 5 | Low | "Operating" batteries hold EIA's standby and out-of-service units | 508 MW in the US, 200 MW in ERCOT | words | `wip/audit-home-5` |
| 6 | Low | A held grid's interval time is printed beside "license needed" | 3 grids | for ruling | `wip/audit-home-6` (test only) |
| 7 | Low | "Every number on this page is read from the ERW's tables" | the Digest's stories carry the news's numbers | words | `wip/audit-home-7` |
| 9 | Low | The tour's count and list | "Twelve stops, eight minutes" for 16 and 10; 4 of 9 later stops unnamed | words | `wip/audit-home-9` |
| 10 | Low | "The home page lists every tool by who it is for" | 2 places | words | `wip/audit-home-10` |
| 11 | Low | The AI energy stop calls every figure a query's | 5 of 23 rows are fleets | words | `wip/audit-home-11` |
| 14 | Low | The method note describes the company search as current | 3 sections | words | `wip/audit-home-16` |

(Branch numbers follow the order the branches were made, not the findings' numbers.)

## 1. The Digest block (Medium)

- **Where.** `site/app/page.tsx`, `Digest`; `site/lib/markdown.ts`, `topItems` and `digestTitle`; `docs/digest/latest.md`.
- **Why it is wrong.** The block reads the first five items under "## Top of the industry". The issue of 6 November was the last of that form; the issue of 12 November (the newest, `latest.md`) is "ERW Daily Digest" with "The opening number", "The numbers", "What moved", "More". So the block prints "no data for the digest: docs/digest/latest.md has no 'Top of the industry' section" under "The weekday brief of energy news, scored and ranked", and the title cleaner, written for "ERW's Energy Digest, ", leaves the whole title in the link: "The full Digest of ERW Daily Digest, 2026-11-12 and the archive". A first reader sees an empty block on the front page.
- **The test.** `tests/test_audit_home_1.py`: the newest issue has no "Top of the industry" (passes on main); the link's words name the issue's date only (fails on main).
- **The fix, words only.** The title cleaner also takes "ERW Daily Digest, ", so the link reads "The full Digest of 2026-11-12 and the archive", as it did for the old form.
- **For Samuel's ruling** (`wip/audit-home-13`, test only). The block reads the new form's "What moved" when "Top of the industry" is not there. Default "left as it is". The effect: 5 stories drawn instead of "no data" (the newest issue's "What moved" holds 5).

## 2. "Every answer from the tables" (Medium)

- **Where.** `site/app/page.tsx`, `GROUP_LINES.Analysis`.
- **Why it is wrong.** The line ends "and the Thesis Builder, every answer from the tables". A Thesis Builder report is written from web search and the EIA's and FRED's series (`execute_market`), with the policy monitor's table for policy; and the tool is internal: a visitor who follows it is not found. A fund analyst reading "every answer from the tables" would take its report as the warehouse's own numbers.
- **The test.** `tests/test_audit_home_2.py` (the runner's market research uses web search, `COMPANY_SEARCH` is False; passes on main; the words test fails on main).
- **The fix, words only.** "Research on demand, a warehouse you can ask, the events and policy, every answer from the tables; and the Thesis Builder, internal, whose market reports cite the web pages and public series they rest on."

## 3. "11 findings" (Medium)

- **Where.** `site/app/page.tsx`, the Analysis figure: `findings.length` of `site/data/findings/catalogue.json`, unit "findings", note "In the research library today, each run with the inputs you choose."
- **Why it is wrong.** The catalogue is what a person may ask for on `/research`, and the research flow (`lib/analysisflow.ts`) says what its 11 entries are: seven findings, three of them in two versions (ten ids), and the impact study. The figure counts versions and the impact study as findings.
- **The test.** `tests/test_audit_home_3.py`: 11 entries, 3 of them later forms (`_grids`, `_hourly`), 1 impact study (passes on main); the words test fails on main.
- **The fix, words only.** Unit "analyses"; note "Analyses you can run in the research library, each with the inputs you choose: seven findings, three of them in two versions, and the impact study." The figure stays 11.

## 4. "What a battery earned" (Medium)

- **Where.** `site/app/page.tsx`, the Economics note.
- **Why it is wrong.** The figure is `l12_kw:total` of the default inputs: the strategy is perfect foresight ("energy at the hourly real-time price and ancillary services at day-ahead prices, all known in advance", the battery page's own line), and the size does not enter a per-kW figure. "What a 100 MW, 4-hour battery in ERCOT earned" reads as a battery's earnings. The battery audit of 20 November found the model an idealised one (findings 2, 3 and 6) and its "4 hours" 3.71 at rated power (finding 10); those are its page's to say.
- **The test.** `tests/test_audit_home_4.py`: `inputsOf({})` is foresight (passes on main); the words test fails on main.
- **The fix, words only.** "What the model's 4-hour battery in ERCOT would have earned with perfect foresight of prices, <month> to <month>, per kW of power."

## 5. "Batteries operating" (Low)

- **Where.** `site/app/page.tsx`, the Infrastructure and Games notes.
- **Why it matters.** `storage_capacity`'s status operating holds EIA's codes OP, OA, OS and SB: on this machine's snapshot 20 units, 508.0 MW of the 54,488.9 are on standby or out of service (2 units, 200.0 MW of ERCOT's 18,204.5). The storage audit's finding 6 says so for `/storage`.
- **The test.** `tests/test_audit_home_5.py` (the codes in the status, where the table is held; the words fail on main).
- **The fix, words only.** "Batteries EIA lists as operating, standby and out-of-service units among them, nameplate power, from its monthly generator inventory." (and "in ERCOT" likewise).

## 6. A held grid's interval time (Low)

- **Where.** `site/app/page.tsx`, `RightNow`: the `when` line and the unit are drawn from the row whether or not `heldBy` holds the figure.
- **Why it matters.** NYISO's, MISO's and ISO-NE's figures print "license needed", and beneath each "USD/MWh" and "real time, the interval from <time>" of the held row (the drawing: MISO "license needed USD/MWh real time, the interval from 2026-10-03 04:00 UTC"). It describes the row rather than reads its value, as the data audit's finding 8 found on `/data`.
- **The test.** `tests/test_audit_home_6.py` (test only).
- **For Samuel's ruling.** Draw a held grid's figure with no unit and "real time" alone. Default "left as it is". The effect: 3 interval times and 3 units not drawn.

## 7. "Every number on this page" (Low)

- **Where.** `site/app/page.tsx`, the source line.
- **Why it is wrong.** The strip's and the groups' figures are `Num`s checked against their tables, and the chart's fact is its table's; the Digest's stories are the news as each outlet reported it (6 November's first five: "$33.1 ..."; 12 November's "What moved": "USD 74 billion", "USD 3", "USD 2.1 billion").
- **The test.** `tests/test_audit_home_7.py` (the words fail on main).
- **The fix, words only.** "Every figure of the strip and the five groups is read from the ERW's tables and checked against them, and today's chart from its table; the analyses are counted from the library's own catalogue; the Digest's stories are the news as each source reported it."

## 8. The tour's Digest stop (Medium)

- **Where.** `site/lib/tour.ts`, the stop `/digest`: `look` and `headings`.
- **Why it is wrong.** "Read \"Top of the industry\", then \"ERW's Numbers Today\"." `/digest` draws today's issue only, and there has been none since 12 November; the newest issue has no "Top of the industry" at all and "ERW's Numbers Today" only as a sub-heading of "More". `check-tour` would fail both on a built site.
- **The test.** `tests/test_audit_home_8.py`: the newest issue's headings (passes on main); the stop quotes no heading the newest issue lacks, and `/digest` draws "Archive" (fails on main).
- **The fix, words only.** "Read today's issue; when there is none yet, open the newest under \"Archive\" and read \"The opening number\", then \"The numbers\"." Its heading for the check: "Archive", which `/digest` draws every day.

## 9. The tour's count and list (Low)

- **Where.** `site/lib/pages.ts`, the tour's line (drawn on `/about` and `/data`); `site/app/tour/page.tsx`, the lead.
- **Why it is wrong.** The line says "Twelve stops for a first visit, about eight minutes"; the path has 16 stops, 595 seconds ("about 10 minutes" on the tour itself). The lead names five of the nine stops after the ruled seven and not "Where energy goes", "Energy per AI query", "Every state" or "Grid conditions".
- **The test.** `tests/test_audit_home_9.py` (16 stops, 595 seconds; the words fail on main).
- **The fix, words only.** The line drops the count it cannot keep ("Stops for a first visit, one page each ...") and names the later stops; the lead adds "where energy goes, the energy of AI, every state and grid conditions".

## 10. "Lists every tool by who it is for" (Low)

- **Where.** `site/app/tour/page.tsx` and `site/app/tour/[stop]/page.tsx` (the last stop).
- **Why it is wrong.** Since session 300 the home page shows the five groups of the menu by subject; the list by audience is the draft at `/home/v2`.
- **The test.** `tests/test_audit_home_10.py` (the home page names its five groups and reads no audience; the words fail on main).
- **The fix, words only.** "the home page shows the five groups of tools".

## 11. The AI energy stop (Low)

- **Where.** `site/lib/tour.ts`, the stop `/ai-energy`, `line`.
- **Why it is wrong.** "The energy a query to an AI model uses, as each publisher printed it": 5 of the page's 23 rows are a company's whole consumption in a year and none is per token (`docs/reviews/ai-energy-model-audit-2026-11-26.md`, finding 1; its finding 6, digits dropped, is for ruling there). Only the tour's words are refiled here.
- **The test.** `tests/test_audit_home_11.py` (passes on main for the rows; the words fail on main).
- **The fix, words only.** "The energy of AI as each publisher printed it, for a query, a training run or a company's whole fleet, with who measured it and how."

## 12. The Thesis Builder's line (Medium)

- **Where.** `site/lib/pages.ts`, `/thesis` (drawn on `/about` and `/data`).
- **Why it is wrong.** "Type a niche and get a sourced investment map of it: ... the company landscape, the deal funnel, the pipeline, ...". Since 9 October (`COMPANY_SEARCH = False`) a run makes the market report only; the landscape, funnel and pipeline say "Connect PitchBook or Harmonic to fill this" until a person pastes a provider's answer from their own account. The report is neutral by its own rule, so "investment map" overstates it too.
- **The test.** `tests/test_audit_home_12.py` (the switch and the connector tabs; passes on main; the words fail on main).
- **The fix, words only.** "Type a niche and get a sourced market report of it: scope and definitions, five trends each drawn with a real series, capital, incumbents, risks, policy and timing, every figure with its source; the company landscape, deal funnel and pipeline fill from a data provider's answer you paste from your own account. Internal."

## 13. "A figure that could not be found there is not shown" (Medium)

- **Where.** `docs/methods/thesis.md`, "Where a number comes from" and the placeholders' table; `warehouse/thesis/build.py`, `check_numbers`.
- **Why it is wrong.** `check_numbers` replaces a text under 40 characters (or one with no cited source) by "not confirmed"; a longer text keeps every number and adds "(not confirmed: <the numbers>)". In the five saved runs 49 texts print 80 numbers that way, in every tab but the funnel (drawn: "... 14.2 (not confirmed: 2026, 2, 25, 14.2)"). A market run's scope, timing and capital sentences pass the same check.
- **The test.** `tests/test_audit_home_14.py`: `check_numbers` with a stand-in run keeps a long sentence's number and marks it (passes on main); the note says so (fails on main).
- **The fix, words only.** The note says what the code does: a short cell is replaced by "not confirmed"; a sentence keeps its number and is followed by "(not confirmed: ...)", naming the numbers no cited source holds, so a reader sees both.
- **For Samuel's ruling** (`wip/audit-home-15`, test only). A sentence holding a number no cited source holds is not shown (as a trend's Fact already is). Default "left as it is". The effect on the saved runs: 49 texts of 5 runs (9, 10, 7, 10, 13) replaced by "not confirmed".

## 14. The company search, described as current (Low)

- **Where.** `docs/methods/thesis.md`: "Which companies are on the map", "The confidence score".
- **Why it is wrong.** "Companies come from three places: the ERW's own companies and deals tables, web search, and PitchBook (below)." The note's own lead says the ERW does not search for companies since 9 October; the selection rule and the confidence score describe the runs written before.
- **The test.** `tests/test_audit_home_16.py` (the words fail on main).
- **The fix, words only.** Each of the two sections says it describes a run written before 9 October 2026.

## The words branches drawn and read

(Filled in below as each branch is drawn.)

## Not covered, or left open

- **The live figures**: restated and drawn on the main copy's tables, which are older than the live set's; the 15-minute strip is not held here.
- **A market run**: no state of one is kept where this machine can read it; its report shape was read in the code (`market_report`) and the stand-in of `site/scripts/thesis-stub.mjs` was not drawn.
- **The pages in a browser**: drawn to HTML with the site's own code; no layout, no width of 390 px (the browser read of tonight walked `/`, `/tour` and `/thesis`).

## For Samuel: the words of /privacy (Samuel's own, not changed)

- `/privacy`, "What else the site stores", names the sign-up, Ask's questions and the battery game. It does not name the Thesis Builder's store (the niche, stage and geography typed; the report; a pasted PitchBook or Harmonic answer with the SHA-256 of the pasted text), or that the niche typed may go to a Claude model from Anthropic (the gate's call and the run). Only a person in the internal view can use the tool, so a visitor's privacy is unaffected; the page's words cover visitors.
- `/terms`: nothing on these three pages disagrees with it.

## Landing, rulings and data (returned to the chain's main session)

(Filled in below.)
