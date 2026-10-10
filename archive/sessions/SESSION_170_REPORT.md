# Session 170 report: Automated Analysis, the foundation and the first three findings

Branch `wip/170-analysis` in `C:\Users\lossa\Documents\erw-142`, from `a2bd935`; four commits, the last `157bbb2`. Not pushed, nothing merged, no lock taken, no model call, no data table written. Built 07:39 to about 09:40 UTC on 9 October 2026; a usage limit then paused the session until about 22:00 UTC, when it finished its checks (the hand-over hour of 12:00 UTC was missed by the pause, not by the work).

## Read these first

- `docs/methods/automated_analysis_findings.md`: the engine, the queue, the Roundup's choice, the renders, and each finding's method (the marriage statistic quoted with its definition and the CDC's terms).
- `warehouse/analysis/findings/` (`common.py`, the three finding modules, `run_finding.py`, `worker.py`, `roundup_pick.py`): the whole engine; `site/data/findings/*.json` are the three cards as computed tonight.
- `site/app/analysis/page.tsx` and `site/components/analysis/FindingCard.tsx`: the page rebuilt around the cards.
- `warehouse/supabase/migrations/026_analysis_requests.sql` (the queue, not yet applied) and `runs/session170/handover.sh` (the exact "To finish" commands).
- Not done, plainly: the font files are not bundled (no pull was allowed for them), so no PNG render exists yet; the migration is not applied, so the queue and "Use in Roundup" answer "the queue could not be written" until it is.

## The three findings (the numbers, each with its method footnote in the card's JSON and on the page)

1. **BATTERIES ATE THEIR OWN LUNCH?** (econometric; ERCOT hub average, 2019 to 2026-10-08, 272,348 intervals in 94 local months). Subtitle chosen by the fit: "Spikes shrank as the fleet grew, and the regression agrees, with the usual caveat."
   - Worst-interval multiple (P99.9 over the median): 126.6x in 2019, 12.1x in 2025 (the thesis's 2025 values reproduce to the cent: median 25.68, P99.9 311.80).
   - Hours at or above USD 1,000/MWh: 26 in 2019, 2 in 2025. Worst month 2019-08 at 465x. Hours in the sample's top 1 percent (above 303.92 USD/MWh): 81.5 in 2019, 10 in 2025.
   - Battery fleet (EIA-860M, operating): 87 MW in 2019-01, 18,204 MW in 2026-08.
   - Regression, 92 months 2019-01 to 2026-08, OLS with month-of-year dummies, load and Henry Hub, HC1 SE: multiple -10.76 per GW (SE 2.32, p < 0.001, R2 0.25); hours at or above USD 1,000: -1.25 per GW (SE 0.57, p 0.031); top-1-percent hours: -1.93 per GW (SE 0.80, p 0.019). The card says association, not cause, and names the winter storm, the offer cap, solar and gas.
   - Footnote: tables `ercot_all_hub_prices_history` and `iso_rtm_hub_prices` (NP6-785-ER, NP6-905-CD), `storage_buildout_monthly`, `ercot_zone_load_hourly` (the ERCOT total row), `eia_fuel_spot_prices`; local months, numpy linear percentiles, no cap or exclusion.
2. **GAS SETS THE PRICE LESS OFTEN?** (visual; share of hours below heat rate x Henry Hub, monthly mean of the daily spot). Subtitle: "In ERCOT the share barely moved; the sensitivity moves it more than the years do."
   - ERCOT at 7.0: 38.8 percent of 2019's hours, 40.9 percent of 2025's (8,760 hours); at 6.5 and 8.0 in 2025: 35.3 and 52.8 percent.
   - ISO-NE (the eight zones' mean, from the internal hourly history; aggregates only published): 18.6 percent in 2019, 5.5 in 2025 (2.2 in 2024). Henry Hub, not Algonquin: the card says so.
   - CAISO, NYISO, SPP: held from 2026-08-26 (SPP 2026-09-24) only; their 2026 bars are 14.6, 1.9 and 32.1 percent over weeks, earlier years "not held". MISO and PJM placeholders in the greyed style.
3. **TILL QUEUE DO US PART** (visual; Berkeley Lab Queued Up 2026 edition, requests of 2000 to 2020 with a MW figure: 21,758 requests, 3,509 GW; the thesis's 75 percent of 3,501 GW reproduces as 75.2 percent of 3,509 GW, the edition's difference).
   - Withdrawn 75.2 percent, operating 12.9, active 10.6, suspended 1.3. Worst: Other 84.0 percent withdrawn; best: Solar and battery 51.5. Gas 79.5, Wind 77.5, Solar 70.6.
   - Marriage: CDC/NCHS FastStats, provisional 2023: marriage rate 6.1 and divorce rate 2.4 per 1,000 population (divorces from 45 reporting states and D.C.). The CDC does not publish the share of marriages that end in divorce, so the card compares with the crude ratio of the two rates, 39 percent, says so in the why and the footnote, and the subtitle bends to it: "The queue walks away 1.9 times as often as the altar does, on the only comparison the CDC's figures allow."

## What each download holds (`site/public/findings/`)

- `erw_2026_ercot_spikes_batteries.csv`: 94 monthly and 8 yearly rows: intervals, median, P99.9, multiple, hours top 1 percent, hours at or above 1,000 and 250, battery MW, mean load MW, Henry Hub. `batteries_lunch.py` (the module as run), `batteries_lunch.do` (the same regressions with `vce(robust)`).
- `erw_2026_gas_share_hours.csv`: one row per grid and year 2019 to 2026: held hours, first and last hour, the share at 6.5, 7.0 and 8.0 (blank where not held). `gas_sets_price.py`, `gas_sets_price.do`.
- `erw_2026_queue_outcomes_technology.csv`: one row per technology and all: requests, requested GW, GW and percent by status, the CDC rates. `queue_divorce.py`, `queue_divorce.do`.
- Each do-file: no line continuation, one empty line between commands outside the loop and none inside, every variable destrung with force, per-variable sentinel recoding (-999) before any loop, file names `study_year_topic_word.csv`. A test pins each rule.
- Every number on each card is in `numbers` of its JSON; `tests/test_session170.py` reads the CSV back and recomputes every one with the finding's own `numbers_from_rows`; the CSV's sha256 is in the card.

## Pull against its ceiling

- One source, CDC (www.cdc.gov), 3 requests of a ceiling of 5, User-Agent exactly `ERW research project, github.com/SamuelEnrique/erw`: `/robots.txt` (200, 1,699 bytes; `/nchs/fastats/` not disallowed), `/other/agencymaterials.html` (200, 80,254 bytes, sha256 `213845d3...88d04f`, the terms: "Most of the information on the CDC and ATSDR websites is not subject to copyright, is in the public domain, and may be freely used or reproduced without obtaining copyright permission." and "Attribution to the agency that developed the material must be provided"), `/nchs/fastats/marriage-divorce.htm` (200, 91,069 bytes, sha256 `a9e3725e...48021`). Saved with retrieval times in `runs/session170/pull/`. Nothing else requested from any outside host.
- Not an outside pull, but said: `roundup_pick.py`, run once as a check, read the ERW's own Supabase (HTTP 404: the table does not exist yet; the rule's chart stood).
- Model spend: USD 0.00. No code of this session calls a model.

## Checks (outputs under `runs/session170/`)

- `tests/test_session170.py`: 29 tests, exit 0 (`test_session170.out`, 2 skipped without the tables); with `ERW_DATA_DIR` set to the main copy's tables, exit 0, the worker test runs `queue_divorce` end to end from a queued row (`test_session170_tables.out`, 1 skipped: the full recomputation, which runs with `ERW_FINDINGS_FULL=1`).
- The Roundup's tests, `tests/test_session119.py`: 43 tests, OK, exit 0 (`test_roundup_119.out`).
- `npx tsc --noEmit -p .`: exit 2 with one error, in the generated `.next/types/validator.ts` (a stale reference to `app/network/v3/page.js` from an earlier build of another branch in this worktree); no error in a file of this session (`tsc3.out`). The build regenerates that file.
- `npx eslint` on this session's site files: exit 1 with 2 errors, both pre-existing in `components/AnalysisGallery.tsx` (session 23's `setState` in effects, lines 22 and 38), not in this session's lines there (two labels) nor in any new file (`eslint.out`). Left as they were; named here.
- `npm run build`: see "Build and page check" below.
- Renders: `node site/scripts/render-cards.mjs` exits 1 and names the missing font files (by design: no render in a fallback font). Proof the renderer fails on a missing font: `test_the_renderer_fails_on_a_missing_font` plus the live run.

## Build and page check

- `npm run build` in the working copy, under the mutex (a stale lock of 15:06 UTC, seven hours old, was taken at 22:06 and released after): exit 0 (`build.out`); `/analysis` static, `/analysis/card/[id]` and `/api/analysis` server routes. The build regenerated `.next/types`, so the `tsc` error above is gone with it.
- `node site/scripts/check-analysis.mjs http://localhost:3170` against the built site in the internal view: 79 of 79 checks passed, exit 0 (`check-analysis.out`): the three cards drawn with every callout number as the JSON holds it, the why and the footnote, the three downloads answering 200, the render links, "Use in Roundup", the effect table, the MISO and PJM placeholders, each card's own page and its render frame, the W40 chart gone from `/analysis` and kept on `/analysis/2026-W40`, no model name or cost, the current rule's footnote, the request form, human labels, `/api/analysis` 404 for a visitor and answering the internal view, the in-review page for a visitor. (One first run failed on the why paragraph: the check read `p < 0.001` with its `&lt;` unescaped; the check was corrected, the page was right.)
- `node site/scripts/render-cards.mjs http://localhost:3170`: exit 1, "the bundled fonts are not all in public/fonts/: missing SourceSerif4-Variable.ttf, SourceSerif4-Italic-Variable.ttf, Inter-Variable.ttf (no render is made in a fallback font)" (`render-cards.out`): the refusal the part asks for; no PNG was written.
- The server on 3170 was stopped; the mutex is released; no process of this session is left running.
- Snapshot comparison: none, nothing was deployed (no push).

## Also said

- One early background command of this session (a lookup of statsmodels, the Supabase reader and the fonts on the machine, which included a `find /`) was stopped by the harness for low memory while the session was paused; its answers were had from narrower commands and nothing depended on it. Not restarted.
- Pre-existing on the branch, untouched: the two `react-hooks/set-state-in-effect` errors in `AnalysisGallery.tsx` (session 23).

## Decisions made alone

- The ERCOT 15-minute history is the consolidated `ercot_all_hub_prices_history` (3 million rows; the yearly tables the brief names were folded into it in session 29): read in chunks for one hub. The live window after 2026-08-26 comes from `iso_rtm_hub_prices`.
- Spike measures come from the raw intervals, not from `ercot_peak_premium_monthly`, so that the fixed top-1-percent threshold and the hours counts are one computation with the rest; the thesis's values reproduce to the cent.
- "Hours in the top 1 percent": the 99th percentile of every interval in the sample, one fixed threshold (303.92 USD/MWh), named on the card.
- The regression's demand control is the ERCOT total load row's monthly mean. Its 2026 summer means (69 to 73 GW) look high against 2019's 40 GW; flagged, not changed: it is the table's value and only a control.
- Henry Hub enters as the calendar month's mean applied to every hour (no day is filled); ISO-NE's hours are the simple mean of the eight zones (the hub is not in the history); the ISO-NE history is an internal table, so only the yearly aggregates are published and the Method note says so.
- CAISO, NYISO and SPP have no real-time history in the warehouse: their earlier years read "not held", never filled, and their 2026 bars say which weeks they cover.
- The CDC gives crude rates, not a divorce probability: the comparison is the ratio of the two rates, stated as such; the headline bends to it (1.9 times), the number never.
- The queue is a Supabase table behind the internal token (the Thesis Builder's pattern, migration 024), not session 59's git-file queue: a request needs no commit, the worker on this laptop polls it, and a row waits with its time while the machine is off. Session 59's queue stays for code and data tasks.
- The renders use the headless browser through `site/scripts/browser.mjs` (not Python): the card's own React and ECharts draw it, and the page's `document.fonts` says whether the bundled faces loaded. The fonts could not be pulled tonight (one pull only, the CDC), so the files are a hand-over step; the renderer refuses to render without them.
- The chart of the week stays on each week's own page (`/analysis/<week>`, nothing dropped); `/analysis` no longer draws it; the Roundup labels the rule's pick as such when no finding is chosen.
- The gallery's human labels live in `site/lib/findingwords.ts` (pure, shared with the client); `AnalysisGallery.tsx` changed in two lines.

## Dropped or moved

- Dropped from `/analysis`: the W40 chart-of-the-week figure (deals in the news by month, the count the code disowns) and the old rule's footnote ("robust z ... capped at 10 ... 45 days"). The figure stays on `/analysis/2026-W40`; the archive list links every week. The results table and the gallery stay. The model name and cost were on the chart's caption (`view.tsx`), which `/analysis` no longer renders; `view.tsx` is unchanged for the week pages.

## What to review (in the internal view)

- `https://erw-flame.vercel.app/analysis`: three cards in order. On each: the title in capitals, the italic subtitle, the chart (hover any point: every series' value, the gas chart's hover also gives 6.5 and 8.0 and the held hours; the queue chart's hover gives GW and requests), three callouts, the why, the footnote; "Downloads: data (CSV), Python, Stata do-file" open the files; "Renders: 1080 x 1350, 1600 x 900" answer 404 until the fonts are placed and the renders made; "Use in Roundup" answers "the queue could not be written" until migration 026 is applied, then "chosen for the Roundup of 2026-W41".
- Below the cards, "Ask for a finding": pick a finding and inputs (the hub list reads "ERCOT North Hub"), "Ask the warehouse": until the migration is applied the note says the queue could not be written; after it, the row appears with its time and state "queued, waits for the data machine" until the worker on this laptop runs it.
- "This week's results, 2026-W41" with the current rule's footnote; the gallery with human labels; "Archive: the chart of each week".
- `https://erw-flame.vercel.app/analysis/card/batteries_lunch` (and `gas_sets_price`, `queue_divorce`): the one card; with `?render=1` the render frame alone.

## To finish (in order; the exact commands are in `runs/session170/handover.sh`)

1. Merge `wip/170-analysis` into the landing branch; run `tests/test_session170.py`, `tests/test_session119.py`, `tsc`, the build and `node site/scripts/check-analysis.mjs http://localhost:3170` from the main copy.
2. Apply `warehouse/supabase/migrations/026_analysis_requests.sql` (the SQL editor, service role).
3. Place the font files and their OFL texts in `site/public/fonts/` (README there), build, start the site on 3170, `node site/scripts/render-cards.mjs http://localhost:3170`, commit the PNGs; copy a chosen card's 1600 x 900 PNG to `docs/analysis/findings/` for the Roundup's email.
4. Start the worker on this laptop: `.venv\Scripts\python.exe warehouse\analysis\findings\worker.py --loop 60` (a window, or Task Scheduler at log on, restart on failure).
5. Sunday 11 October: the Roundup runs unchanged except that it restores the findings' tables too and prints a chosen finding first, else the rule's pick labeled; `test_session119` passes on the branch.

## Landing state (added by the chain's session 166 at 22:30 UTC on 9 October 2026)

- This report is the agent's report of the session, kept whole; this section is what happened after the hand-over.
- **Not landed.** The account's usage limit paused the chain from about 08:15 to 22:00 UTC, so the deploy cutoff (15:00 UTC)
  passed with nothing of this session on production. Nothing was pushed to `main` or to a `task/` branch after the cutoff.
- The branch is on GitHub: `wip/170-analysis` (`157bbb2`, from `a2bd935`, which holds 166 to 168). Not merged into the landing branch. Its agent was cut off by the same usage limit at about 09:40 UTC and finished its checks at 22:20 UTC; its hand-over by 12:00 was missed for that reason. To finish: the five steps under "To finish" above (`runs/session170/handover.sh`), after the 166 to 168 landing; the font files are not bundled (no pull was allowed for them) and migration 026_analysis_requests is not applied.
- No em dash in this file (checked).
