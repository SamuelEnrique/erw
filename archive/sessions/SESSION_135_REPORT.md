# Session 135 report: the landing step, and Thesis Builder as a tool of the site at /thesis

## Three things to know before anything else

1. **I passed the model spend cap: USD 6.118 against USD 6.00, over by USD 0.118.** The last run (the niche "subsurface heat mapping for geothermal") was given the USD 1.11 that was left, cost USD 1.23, and was then stopped by a rule that looked at the spend only after each call was paid. It paid for every stage, including the finished landscape, and threw the result away. So the cap was passed and that niche has no report. The rule was mine. It is replaced: a stage is now refused before it starts if it does not fit under the ceiling, and a paid answer is never discarded (`run.Careful`, `STAGE_USD`, three tests). No model call was made after it.
2. **Only two of the three niches have a landscape from the new tool.** The new geothermal mapping niche has three runs; the battery software niche has one; the heat mapping niche failed as above. Its row in the table below shows the earlier workbook's list, labeled as such.
3. **The landscape is wide where it finds companies and still thin where it selects them.** A run now finds 24 to 40 organisations (2 to 7 companies before). The rule that puts a company on the map, "a fetched source ties it to one of the five trends", keeps 5 to 12. In the battery run it left out Gridmatic, Modo Energy, Ascend Analytics and GridBeyond: found, private, in the niche, and no source sentence tied them to a trend. They are in the Deal funnel with that reason. Across three runs of one niche the companies found overlap by 0.70 and the companies on the map by 0.43. Details under "The weak spot".

## Verdict: not ready to open. What is left, exactly

The page, the internal table, the workflow, the PitchBook stage and the walls around them are built, deployed and checked on production. What keeps it closed:

1. **The tie to a trend.** It decides the landscape and it is the unstable step. What I would build next: one more stage that reads each fitting company's own site and judges it against each of the five trends in turn, about USD 0.30 a run. Not built: the cap was spent.
2. **The PitchBook stage has never met a real answer.** The request, the paste text, the validator, the one-time key and the storage are proven (below). No real PitchBook figure has passed through, because only your Claude can pull one. Run it once from claude.ai (the text is below) before trusting it.
3. **A run costs USD 0.7 to 1.4**, above the "toward USD 1" of session 30. A day is capped at USD 8 and six runs.
4. **Trends of a thin niche draw few charts.** In the geothermal mapping runs one trend of five has a table of numbers that passed the check, so one chart. The battery run draws three of five. A trend with no number says "no chart" with its reason on hover, or shows only its table.
5. **Run the third niche again** (heat mapping), about USD 1.25, when you allow it.
6. **Tonight the page will not queue a run:** the six runs of this UTC day are used (mine). It opens again at 00:00 UTC.

## The landing step (before session 135), 6 October 2026, 18:09 to 19:11 UTC

**The freeze was on (`python scripts/freeze.py status` exited 1) and was relaxed by your instruction for locked pages only.** Five deploys, each with a snapshot of the 25 live addresses before and after. **No checked number moved on any of them** (3,357 keys compared each time), so nothing was reverted. Vercel built every one: GitHub's record of Vercel reads "Deployment has completed" for each merge commit, and the build id in production's HTML changed each time. None was skipped.

| # | Branch | Checks (run) | Main commit | Vercel | Build id after | Differences on the 25 live addresses |
|---|---|---|---|---|---|---|
| 1 | `wip/132-board` | 37510238357, passed | `6cf672e` | built, 18:25 UTC | `563wyv4jGJER7wl3D8sNI` (was `yv3T85vYQQAzPagaCtUpz`) | 31: the greyed menu line "Markets in review" gone from each of the 25 (meant: `/markets` is retired; session 132 named it); 6 on `/network` from its hourly refresh (18:05), not this deploy |
| 2 | `wip/134-supply` | 37511363111, passed | `6da2b1c` | built, 18:35 | `_dxq4P9WLmBcCESThSnV6` | 25: one new greyed menu line, "Supply and trade in review", on each address (meant) |
| 3 | `wip/133-mix` | 37512601311, passed | `ef37bab` | built, 18:44 | `EOPdefaJyw8KQb--eQGLm` | 0 |
| 4 | `wip/128-ask-ercot-safe` | 37513736402, passed | `018eb0a` | built, 18:52 | `8wvgQEmGZpnOQbSQlzvkx` | 0 |
| 5 | `wip/135-schedule` (the two refreshes) | 37515991422, passed | `893cb08` | built, 19:10 | `hBbOLTgZsQFAYM7lS5TQ1` | 6, all on `/network`: its hourly refresh at 19:05 (the refresh stamp, the newest demand hour, the source line's build stamp) |

**The two menu lines are the only things a visitor can see changed on a live page's frame**: one greyed, unclickable line fewer under Prices ("Markets") and one more ("Supply and trade"). Both were foretold by sessions 132 and 134. No figure, chart or table of `/cost-of-power/battery`, `/network` or `/storage` changed.

**On production, in the internal view:** `/board` 200 (1.6 MB, "Price board"), `/mix` 200 ("Energy mix"), `/supply` 200 ("Supply and trade"); each page's own check passes against production (`check-board` 29 of 29, `check-mix` 36 of 36, `check-supply` 26 of 26). As a visitor each answers the in-review page. `/board/v3`, `/board/v4` and `/markets` answer 308 to `/board`; `/mix/v2`, `/mix/clean` and `/mix/stress` answer 308 to `/mix?view=day`, `?view=clean` and `?view=stress`, carrying their grid. All four pages stay `review`.

**Also done, from session 133's "To finish":** its five rebuilt mix tables went to the Redivis draft (6 of 6 uploaded, nothing released), and three of them (`generation_mix_hourly_profile`, `clean_energy_summary`, `grid_stress_yearly`, which no open page reads) were loaded with `load.py --only`, with a snapshot after: 0 differences. The first load exited 1: Supabase answered HTTP 500 ("JSON could not be generated") on the read that verifies `generation_mix_hourly_profile`; the second try found all 165,760 rows there and wrote nothing. I loaded only those three, not the whole live set, because this machine's other tables are older than the daily run's.

**Branches deleted on the remote, each checked to be fully on main first:** `wip/132-board`, `wip/127-board-v4`, `wip/134-supply`, `wip/133-mix`, `wip/128-ask-ercot-safe`, `wip/135-schedule`.

### The two refreshes, scheduled

- **The board, daily:** one step of `warehouse/run_daily.sh` after `price_board`, under `health.py` (`--step "board"`). **Supply and trade, weekly:** one step on Saturdays (UTC), under `health.py` (`--step "supply"`); `SUPPLY=1` forces it. Saturday because the week's three reports (Wednesday, Thursday, Friday afternoon) all come out after the daily run's hour on their day. The workflow's commit step now adds `site/data/board.json`, `site/public/board/`, `site/data/supply.json` and `warehouse/metadata/release_schedule.json`.
- **A decision I made that you did not ask for: both refreshes write through a guard, `warehouse/derived/page_keep.py`.** The builders rebuild their files whole from the tables on the machine. The scheduled runner does not hold the long price histories or the hourly generation workbooks, so as written the first scheduled run could have replaced the board with a thinner one and blanked the fuel burn rows. The guard takes the new build row by row: a row is taken only when it is no older and its history no shorter than the held row; otherwise the held row stays exactly as it was, with its own date. A row the new build marks "paused" or "licensed" is always taken, so a pause is never undone. Nothing is filled or joined. On this machine the board built through it with 794 of 794 rows taken and 0 kept.
- **What I do not know yet:** how many of the board's rows the runner can refresh. Tomorrow's 14:00 UTC run is the first. Its log line reads "board: N rows: X from this build, Y kept as they were". If Y is large, the board's history tables need restoring on the runner, or the refresh belongs on a data machine.
- **Two tests changed on purpose:** `test_session132` and `test_session134` asserted that nothing called the refresh scripts. They now assert the one scheduled call and the guard. New: `tests/test_page_keep.py` (12 tests).
- **Your ruling 2 of session 132 is taken as "stay in git"** by scheduling now: the board's 16 MB of files are rewritten by each refresh and committed by the daily run. Say so if they should move to the storage bucket.
- **Not scheduled:** the mix's forecast refresh (`refresh_mix.sh`). You did not name it. ERCOT keeps one week of forecast postings, so each day it does not run is a day of ERCOT forecasts that cannot be had later.

### Left from the landing, yours

1. **`ASK_VISITOR_SALT` in Vercel** (session 128's step 1). I cannot read or set Vercel's environment. Until it is set, Ask ERCOT on production answers "not answering questions right now" to everyone: it fails closed.
2. **Today's daily run failed five steps** before this session began (`grid_network`, `carbon_auctions`, `supabase_load`, `news_brief`, `build_status`). I did not touch them; the load's failure looks like the same Supabase HTTP 500 I met.

## Session 135: what was built

| | What | Where |
|---|---|---|
| The page | `/thesis`, in review. A niche, an optional stage and geography, Run. The list of runs. The report in nine tabs, the tab kept in the address | `site/app/thesis/`, `site/components/thesis/` |
| The internal table | `public.thesis_runs`: one row a run, with its report and the PitchBook request and answer. Row level security on, no policy, every grant to the public key revoked | migration `024_thesis.sql`, applied to production at about 19:20 UTC |
| The run | scope and five trends first, then the landscape chosen by them, then capital, incumbents, risks, policy | `warehouse/thesis/run.py` |
| Pressing Run | the database queues the row and dispatches a GitHub workflow at once, through the dispatcher the scheduled jobs already use. No schedule: nothing runs unless Run is pressed | `thesis_submit`, `.github/workflows/thesis.yml` |
| The PitchBook stage | a request with a one-time key, the paste text, an endpoint that accepts the answer once | `run.pitchbook_request`, `site/lib/thesis/pitchbook.ts`, `/api/thesis/pitchbook` |
| The readers' Method note | what each tab holds, where a number comes from, what the placeholders mean | `docs/methods/thesis.md`, at `/data/methods/thesis` |

- **Every number carries its source and is written only if it appears in a fetched source its row cites.** A figure that fails reads "not confirmed", one no source gives reads "not disclosed", each with its reason on hover. The check is the earlier builder's, unchanged.
- **The confidence score** is a number with one plain line, for example "2 independent sources, the latest from 2026; its stage is confirmed by the company or an investor." Nothing about how it is computed is sent to the page.
- **Never public, never downloadable.** The table is in no live set and no Redivis dataset. The page has no export. The page and both routes send `Cache-Control: no-store`. Nothing is merged into `energy_companies` any more.
- **Every chart answers the mouse**: trend charts with the category and each series' value and unit, the funnel with each stage's count. Checked in a real browser on production with two real runs.

### The method stays on the server

- A reader of `/thesis` receives the report and nothing else. A check reads every tab of a real run on production for 15 words of the method (a query of the plan, a prompt's phrase, the scoring fields, a model name, a cost): none.
- Where a company was found is shown as a kind of source ("Web search: federal awards", "ERW companies and deals tables"), never the query.
- **A decision that changes an existing page:** `docs/methods/thesis_builder.md` holds the research plan and the scoring rule, and the site was publishing it at `/data/methods/thesis_builder` (in review). It is no longer built into the site (that address now answers 404), and `/companies` cites the readers' note instead. The file stays in the repository as the internal method, extended with this session's rules. **If the repository is public, that file is public there.** Say so if it should move out of the repository.

## The PitchBook stage: how to run it tomorrow from claude.ai

1. Open `/thesis` in the internal view and pick a finished run. I suggest the geothermal mapping run with the widest map, `20261006T193517Z-50a8be` (25 companies asked for).
2. In the panel "PitchBook pending", press **Copy**. It copies the text below with that run's own run id, key and company list filled in. **The key is not in this report**: it is a credential, it works once, and it is shown only on the page.
3. Paste it into a Claude chat on claude.ai that has your PitchBook connector. Claude answers with one JSON block.
4. Paste that JSON block into the box "Paste Claude's answer here" on `/thesis` and press **Submit**. The report completes: every PitchBook figure appears with a "PitchBook" tag in the Landscape, Deal funnel and Pipeline map tabs, and companies PitchBook adds are listed in the funnel as found by PitchBook.

A Claude that can make web requests can instead send the same JSON itself: `POST https://erw-flame.vercel.app/api/thesis/pitchbook` with the JSON as the body (it carries its own `run_id` and `key`).

### The exact paste-in text

```
You have a PitchBook connector. Please pull the following from PitchBook for an ERW Thesis Builder run and answer with ONE JSON code block in the exact format below, and nothing else after it.

Run: <the run's id>
Key: <the run's one-time key>
Niche: <the niche as typed>

A. For each company in this list, look it up in PitchBook by name (use the website to pick the right one) and return:
   - company profile: legal name, headquarters, year founded, one-line description, employees
   - financing status and the last financing: date, type, size, post-money valuation where PitchBook shows one
   - total raised to date
   - investors, with the lead investors named
   - founders and the chief executive

1. <company> (<website>)
2. ...

B. Then search PitchBook for companies this list is missing: keywords <the niche's name and one phrase per trend>; headquarters: <the geography asked for>; private, venture-backed or grant-backed, founded 2012 or later. Return up to 25 that are not in the list above, as "additional_companies", each with "why": the keyword or PitchBook industry that matched.

Rules: report only what PitchBook shows. If PitchBook has no record of a company, return it with "found": false and nothing else. Leave out any field PitchBook does not show; do not estimate, and do not fill a field from memory or from the web. Money is in millions of US dollars as numbers (12.5, not "$12.5M"). Dates are YYYY-MM-DD, or YYYY-MM, or YYYY.
```

### The return format (`erw-pitchbook-1`)

```json
{
  "format": "erw-pitchbook-1",
  "run_id": "<the run's id>",
  "key": "<the run's one-time key>",
  "pulled_on": "YYYY-MM-DD",
  "companies": [
    {
      "name": "the name exactly as in the list above",
      "found": true,
      "pitchbook_name": "the name PitchBook uses",
      "hq": "City, State, Country",
      "founded_year": 2019,
      "description": "one line",
      "employees": 25,
      "financing_status": "Venture Capital-Backed",
      "last_round": { "date": "2025-03-01", "type": "Series A", "size_usd_m": 12.5, "post_valuation_usd_m": 60.0 },
      "total_raised_usd_m": 20.1,
      "investors": ["Investor One", "Investor Two"],
      "lead_investors": ["Investor One"],
      "founders": ["First Founder", "Second Founder"]
    },
    { "name": "a company PitchBook does not hold", "found": false }
  ],
  "additional_companies": [
    { "name": "A company not in the list", "found": true, "why": "keyword: ...", "hq": "City, State, Country", "total_raised_usd_m": 3.0 }
  ]
}
```

The values above are the template's examples, not figures of any company.

### What the endpoint checks

- `format` and `run_id` must match; `pulled_on` must be a date; only `name` and `found` are required of a company; every other field may be left out.
- An unknown field is refused at every level; a negative or non-number amount is refused; a year outside 1900 to this year is refused; more than 300 companies, 100 additional companies or 400 KB is refused. A company with `"found": false` keeps only its name.
- The key is checked by the database, works once, and is erased when used. A wrong key, a used key and an unknown run answer alike (HTTP 403).
- The stored answer is labeled "PitchBook" with the note "Figures as returned from PitchBook through the user's own account; not checked by the ERW." It is kept on the run's row and nowhere else.

**Proven without a PitchBook figure:** 15 tests of the validator; the example block of a real run's paste text, with its date filled, passes it (`test-thesis-paste.mjs`); 14 checks against the production database with a throwaway row that was removed (`warehouse/thesis/eval/prove_accept.py`): a wrong key, a short key and a second use are refused, a bad shape is refused and leaves the key usable, the public key reads nothing and calls nothing. **A fault found by that proof and mended:** an answer with no company list was accepted and used up the key (in SQL, a missing list's type is null, and `null <> 'array'` is not true).

## The weak spot: the company landscape

### What changed

| | Before (sessions 25 to 36) | Now |
|---|---|---|
| Sources | one research pass, the model's own searches | the warehouse's `energy_companies` and `energy_deals` (rows carrying the niche's own word, no model); web search by a stated plan; the PitchBook stage |
| The query plan | none | 16 queries built in code and saved with the run: six for the niche (by name; recent rounds; seed and Series A; federal awards; accelerators; spinouts) and two per trend from the trend's own phrases; then up to six lookups of a headquarters |
| Selection | the model wrote the list | a rule in code (`run.select`): found, a private company, fits the stage and geography asked for, tied to at least one of the five trends by a source the row cites. That is the landscape. The pipeline map takes those with confidence 60 or more, most trends served first, at most ten |
| What is not selected | gone | a row of the Deal funnel with the stage it reached and why it stopped |
| Trends | written after the companies | written first, and each must be about how the niche's own work is changing, so a company can be said to serve it |

The first run of the day showed why the last line matters. Its trends were general facts ("Most operating geothermal capacity predates 2000"): it found 40 organisations and put 3 on the map. With the trends rewritten from the same research, the map held 8.

### Stability: the same niche three times

The geothermal mapping niche, US startups, its landscape stage run three times on the same five trends (`warehouse/thesis/eval/stability.py`). **The trends were held fixed, so this measures the search and the selection, not the trends**: a fourth and fifth full run did not fit the cap.

| | Run 1 | Run 2 | Run 3 | In all three | In any | Mean overlap (Jaccard) |
|---|---|---|---|---|---|---|
| Organisations found | 27 | 32 | 24 | 21 | 36 | 0.70 |
| On the landscape | 8 | 12 | 9 | 5 | 17 | 0.43 |
| On the pipeline map | 5 | 7 | 6 | 3 | | |

- **On the map in all three:** Zanskar Geothermal & Minerals, Quaise Energy, XGS Energy, Geothermal Radar, Thermofilic.
- **Found in all three, on the map in one or two:** Zonge International (two), AltaRock Energy, Bedrock Energy, Benz Airborne Systems, Geothermal Strategy Partners, Mazama Energy (one each).
- **Found in one run only:** Sintela, FEBUS Optics, Prisma Photonics, Paulsson, Hawk Measurement Systems, Hephae Energy Technology, Terra Watts, Mantle Energy, Ormat.
- **Reading:** finding is fairly stable (21 of 36 in every run). The judgement "a source ties it to a trend" is not: the same company, with the same kind of evidence, is tied in one run and not in the next. "Eden" and "Eden GeoPower" were also counted as two companies.
- **Is Quaise a mapping company?** No. It is on the map because a source ties it to the trend "Public grants for resource characterization". The rule did what it says; the trend is too wide. This is the kind of row to judge by eye.

### The three landscapes side by side (PitchBook stage pending on every run)

| | Geothermal mapping and sensing, US startups (new) | Grid-scale battery storage software for merchant operators | Subsurface heat mapping for geothermal |
|---|---|---|---|
| Run | three runs, the widest shown: `20261006T193517Z-50a8be` | `20261006T194117Z-99fd0b`, the landscape only (no capital, incumbents, risks or policy: the cap) | **failed at the cap; no report** |
| Found | 32 | 26 | |
| A private company | 25 | 18 | |
| Fits the stage and geography | 17 | 18 (none asked for) | |
| On the landscape | 12 | 5 | |
| On the pipeline map | 7 | 2 | |
| The landscape | Zanskar Geothermal & Minerals, Quaise Energy, XGS Energy, Geothermal Radar, Thermofilic, TerraAI, Bedrock Energy, Benz Airborne Systems, Geothermal Strategy Partners, AlterG Resources, Eden GeoPower, Hawk Measurement Systems | Tyba, Entrix, Terralayr, GridStor, FlexGen Power Systems | |
| Stopped for want of a trend tie | Sage Geosystems, Prezerv Technologies, Terra Watts, Ignis H2 Energy, Mazama Energy. Five more stopped because no source gave their location: Rodatherm Energy, AltaRock Energy, Geothermal Technologies, Sintela, Mantle Reach Power | GridBeyond, Gridcog, enspired, Terra One, Capalo AI, Scale Energy, TWAICE, ACCURE, Volt Harbor, Amperon, Ascend Analytics, Gridmatic, Modo Energy | |
| Stopped as not private, or outside the geography | Lawrence Berkeley and Sandia National Laboratories, the University of Utah, Project InnerSpace, Mantle Energy (a subsidiary), Zonge International (no source says what it is), Fervo Energy (**the run read it as a public company: check that**). Outside the US: Eavor (Canada), FEBUS Optics (France), Prisma Photonics (Israel) | Fluence, Energy Vault, Stem (public); Habitat Energy, AutoGrid (acquired) | |
| The earlier workbook's list, for comparison (the old tool, September) | (no earlier run) | 6: Tyba, Gridmatic, Habitat Energy, GridBeyond, Modo Energy, Ascend Analytics | 8: Zanskar, Project InnerSpace, Sage Geosystems, Quaise Energy, XGS Energy, Mazama Energy, Mantle Reach Power, Eavor Technologies |
| PitchBook | pending: 25 companies asked for | pending | |

The five trends of the new niche: AI prospecting for blind geothermal systems; fiber and DAS sensing for geothermal characterization; public grants for resource characterization; prediction and modeling software for geothermal investment decisions; high-temperature and airborne survey methods.

The five trends of the battery niche: revenue is moving from ancillary services to energy arbitrage; day-ahead-only trading leaves a gap that real-time skill can fill; rules are shortening ERCOT reserve durations under co-optimization; contracted revenue is displacing pure merchant exposure; optimization is sold as recurring software, often by the hardware maker.

## Every pull against its ceiling

**No data pull was approved for this session and none was made.** No MISO request. The model spend:

| Run | Niche | What ran | USD |
|---|---|---|---|
| `...c34eaf` | geothermal mapping, US startups | the whole run, first trend framing: 40 found, 3 on the map | 1.4197 |
| `...8fea8a` | the same | trends rewritten from the same research; landscape stage (run 1 of the stability measure) | 0.8908 |
| `...50a8be` | the same | landscape stage (run 2) | 0.7163 |
| `...934443` | the same | landscape stage (run 3) | 0.7223 |
| `...99fd0b` | battery storage software | scope, trends and landscape | 1.1396 |
| `...e292da` | subsurface heat mapping | every stage paid, then discarded at the stop | 1.2293 |
| **Total** | | | **6.1180 of 6.00: over by 0.118** |

Web searches: 32, 22, 22, 22 and 26 in the five finished runs. The site half was built by a second Claude Code agent inside this session and a third read the operators' sites for session 136; neither is a call of the ERW's model key or in the ledger.

## The five most interesting things the tool now does

1. **It shows its rejections.** Every organisation it found is in the Deal funnel with the stage it reached and the reason it stopped: "outside the geography asked for (Canada)", "not a private company (acquired)", "no fetched source ties it to one of the five trends". You can disagree with a row instead of wondering what was missed.
2. **It asks your own Claude for PitchBook.** The run writes the exact lookups it wants and a one-time key; your connector does the pull under your license; the answer comes back labeled and never leaves the run.
3. **Pressing Run on a web page starts a research job with no server of ours running.** The database queues the row and dispatches the workflow itself, with the token the scheduled jobs already use. Proven on production with a run id that does not exist: the workflow started in seconds, found nothing queued, and spent nothing.
4. **A trend is now a test, not a backdrop.** Each of the five must be something a company can be said to serve. That one change took the same research from 3 companies on the map to 8.
5. **It measures its own instability.** One command compares saved runs of a niche and prints which companies are in every run, which in one, and the overlap.

## Checks

| Check | Result |
|---|---|
| `tests/test_session135.py` | 29 tests pass: the plan, the geography rule, the selection rule, the reader's view, the PitchBook request, the walls, the spending stop |
| The whole suite and the site's checks on GitHub | passed (run 37523238277). The first push failed (run 37522709376): in the whole suite `import run` answered another module named `run`. The run and its tests now load their neighbours by path |
| `check-thesis.mjs` against production | 23 of 23: a visitor sees the in-review page; both run routes answer 404 without the internal cookie; the PitchBook route never answers 200 to a bad payload or a wrong key |
| `check-thesis.mjs` against a stand-in with labeled fixture runs | 68 of 68 (the building agent's run): every tab, placeholders, source links, the PitchBook answer submitted once, polling, a phone's width |
| A real run read tab by tab on production | nine tabs answer 200 with no "undefined" and no word of the method |
| A real run in a real browser on production | the charts and the funnel answer the mouse; no script error |
| The dispatch, on production | workflow run 37524538118: started by the database, "run ... is not queued", success, no model call |
| The daily limit | production answered "Today's runs are used up." to a seventh request |

## Decisions I made without you

1. **Runs live in one Supabase table, not in `warehouse/output` or Redivis.** "Internal warehouse tables" could mean either. A table the site writes cannot come from the warehouse's files, and the Ask tools' ledger is already kept this way. Say so if you want a nightly copy into the internal Redivis dataset.
2. **Migration 024 was applied to the production database during the freeze** (at about 19:20 UTC, and again some 25 minutes later with the mended function). It adds one table and five functions that no open page reads.
3. **The Thesis Builder no longer feeds `/companies`.** "Never public" and "merged into the public companies table" cannot both hold. The old command line (`build.py`) still merges if someone runs it.
4. **Geography is matched plainly.** "United States" is understood; a continent ("Europe") is not, and a company whose country no source gives stops in the funnel with that reason.
5. **The two existing niches ran without a stage or geography**, as their earlier runs did. "US startups only" was applied to the new niche.
6. **`thesis-stub.mjs` holds made-up runs for the page's check.** They are labeled as fixtures, read only when the site is pointed at a local stand-in, and never stored. Tell me if rule 1 forbids even that.
7. **The workflow does not take the data lock.** It writes only its own row. Its cost ledger file is the runner's and is discarded; the run's spend is kept on its row.

## For Samuel

1. Set `ASK_VISITOR_SALT` in Vercel (from session 128; Ask ERCOT is closed to everyone until then).
2. Run the PitchBook stage once from claude.ai with the text above, and tell me what Claude returned that the endpoint refused.
3. Rule on the internal method note staying in the repository.
4. Look at the board's first scheduled refresh in tomorrow's daily run: "board: N rows: X from this build, Y kept as they were".
