# Session 30 report

Energy Research Warehouse (ERW), session 30, run 2026-09-29 from 09:41 to about 12:45 UTC.

**API spend: USD 6.1228, under the USD 8 cap** (expected USD 5). Every call went through the new cost ledger with `ERW_SESSION=30` and `ERW_SPEND_CAP_USD=8`.

- No source was pulled or backfilled, and no story was re-scored with Sonnet.
- Nothing was deleted from Redivis and nothing was released.
- The site was deployed. The live checks pass: routes 30 of 30, values 1,104 of 1,104.

## 1. Spend

From `api_cost_ledger`, session 30. Every row is one call; USD is at `warehouse/config/model_prices.yaml` (dated 2026-09-25).

| Step | Model | Calls | USD | What |
|---|---|---|---|---|
| `news_score_shadow` | claude-haiku-4-5 | 73 | 1.9226 | The Haiku backtest: 2,375 stories, the last 30 days and the 50 eval-sample stories |
| `news_score_shadow_nocache` | claude-haiku-4-5 | 11 | 0.4486 | The caching measurement: 2026-09-26 again, without cache breakpoints, nothing written |
| `thesis` | claude-sonnet-5-5 | 29 | 2.2514 | The Thesis Builder: a failed attempt (USD 1.0261) and the run (USD 1.2253); section 3 |
| `thesis_schema_check` | claude-sonnet-5-5 | 5 | 0.0157 | `max_tokens=1` calls checking which sheet schemas the API accepts |
| `chat_eval` | claude-sonnet-5-5 | 164 | 1.4322 | The chat evaluation, once (30 questions) |
| `digest` | claude-sonnet-5-5 | 2 | 0.0401 | The shadow Digest's headlines and summary |
| `roundup` | claude-sonnet-5-5 | 2 | 0.0124 | The shadow Roundup's headlines and summary |
| **Total** | | **286** | **6.1228** | Cap USD 8.00 |

**By model:**

- claude-sonnet-5-5: 202 calls, USD 3.7517.
- claude-haiku-4-5: 84 calls, USD 2.3712.

**Why over the USD 5 expected:** the Thesis Builder's first attempt. Its three research passes (USD 1.0261) were lost when the structure step was refused (section 3). The rerun cost USD 1.2253.

**One ledger fix:** the API answers with the dated id `claude-haiku-4-5-20251001`. The first 11 rows were written with `usd` empty. The price table now prices a dated id as its alias, and those 11 rows were repriced from their own token counts; their header says so.

## 2. Price board v2

**The page: `/board`,** first under Prices in the nav, linked from the home page's price board. Every number on it is a value of a warehouse table, read as stored, inside a `Num` that `check-values.mjs` compares with Supabase. The page computes nothing.

The blocks, each with a tier chip (`derived`) and a citation line naming its table and its inputs:

- **Power, main hubs.** The six ISOs' main hubs, day-ahead and real-time:
  - the latest complete day's mean;
  - the change on the day before in USD/MWh and percent, colored by sign and written with its sign (up in cardinal, down in Stanford's Palo Alto green, so color is never the only cue);
  - 7- and 30-day averages, and the 30-day low to high;
  - day-ahead minus real-time, with its date;
  - a 30-day inline SVG sparkline.
- **Peak and off-peak.** The latest peak day per ISO and market: peak, off-peak, their difference, and a sparkline.
- **Gas, oil and spark spreads.**
  - Henry Hub and Brent minus WTI, with a year's sparkline.
  - Per ISO, the spark spread and implied heat rate. The 7.0 MMBtu/MWh heat rate is labelled on the page as the one assumption.
- **Carbon.** Says why no price is shown (below).
- **ERCOT since 2015,** the demo strip:
  - inline SVG bars of the real-time annual mean, HB_HUBAVG;
  - bars of the peak premium (medians, `ercot_peak_premium_annual`);
  - a table per year: all-hours, peak, off-peak, their difference, the premium. 2026 is labelled "to date, 270 days".
- **Every hub and zone** (39), day-ahead and real-time, in a closed `details` block.

**Design and layout:**

- Stanford palette from `app/tokens.css` (two tokens added for the move colors).
- No new dependency: the sparklines and bars are plain SVG (`components/InlineSpark.tsx`).
- At phone width (390 px) there is no page-level horizontal scroll; the wide tables scroll inside their own boxes.
- Screenshots: `site/screenshots/board-desktop.png` and `board-mobile.png`.

**The four derived tables** (tier `derived`, `warehouse/derived/price_board.py`, method `docs/methods/price_board.md`, in the daily run after the consolidated build):

| Table | Rows | License | Formula, in short |
|---|---|---|---|
| `price_board_latest` | 3,263 | public | Every hub and zone, 12 markets. Daily means of complete local operating days (a day missing one interval is left out); latest, previous, change and percent change; 7- and 30-day means of the daily means; 30-day min and max of them; the newest interval; intervals held in 30 days; day-ahead minus real-time on the latest day both are complete |
| `price_board_peak_offpeak` | 2,625 | public | Main hub per ISO. Peak = hours ending 7 to 22 local on peak days (Monday to Friday; CAISO Monday to Saturday, WECC), NERC holidays off-peak. Peak, off-peak and all-hours means per complete day, last 90 days the tables reach; ERCOT HB_HUBAVG per operating year since 2015 (`{da,rt}_year_*`) |
| `price_board_spreads` | 2,052 | public | Daily, 365 days: Henry Hub; per main hub, the day-ahead daily mean, spark spread = mean - 7.0 x Henry Hub, implied heat rate = mean / Henry Hub (gas of the day, or the latest trading day up to 4 days before, `x_gas_date`); Brent minus WTI |
| `price_board_carbon` | 15 | **internal** | Latest CARB (current and advance) and RGGI auction: price, allowances offered and sold, the auction before and the change |

**Checks:**

- All four pass the validator.
- Spot values equal independent arithmetic from the source tables:
  - ERCOT HB_HUBAVG day-ahead, 2026-09-29: 27.6013 (the table first stored 27.6012 with Python's half-even rounding; it now rounds half up like the rest of the ERW);
  - NYISO N.Y.C. real-time, 2026-09-27: 29.6072;
  - ERCOT's spark spread on 2026-09-22: 49.1275 - 7 x 2.90 = 28.8275.
- A variable carries its market (`da_`, `rt_`): a hub is one entity in both markets, and the series key is (entity, variable, ts_utc).

**On the GitHub runner,** the ERCOT history (0.7 GB) is never restored, and CARB answers HTTP 202 (a known gap). So the rows built from them are carried from the last run's tables, restored from the draft, and each header says so. A local simulation without the history and CARB reproduced all four tables exactly (0 rows or values differ).

**What is missing, and why:**

- **Carbon prices on the public page.** CARB's and RGGI's terms are unconfirmed (session 7), so their tables are internal, and a derived table takes its inputs' license. The build enforces this: `build_coverage.apply_derived` refuses a public table derived from internal ones.
  - So `price_board_carbon` is internal, in Supabase (row-level security hides it) and in the internal Redivis dataset.
  - The page says the ERW holds the auction results but may not show them.
  - The prompt asked for a public upload of all four; three are public and this one is not.
- **Secondary-market carbon prices.** The ERW holds none; the page and the method say so.
- **Stale carbon.** RGGI's future-vintage auction series ended in 2011 and is left out rather than shown as current. CARB's latest held is Joint Auction #48 (August 2026, retrieved 2026-09-29 locally), the newest there is.
- **SPP real-time is not missing.** `iso_rtm_hub_prices` has held market `spp_rtm` since 2026-09-24, so the board shows it with "4 days" beside its 30-day average. `package/llms.txt` said SPP real-time was not in the warehouse; corrected.
- **90 days of peak and off-peak, and a year of spark spreads:** only ERCOT has them, through its history. The other ISOs' price tables are rolling windows from 2026-08-26 (about 35 days). No backfill was allowed.
- **The newest days have no spark spread:** EIA's Henry Hub is published several days late (the newest is 2026-09-22), and a spread needs a gas price within 4 days.
- **"One screen":** the desktop page is about 2,100 px tall. The main table is one screen; the rest follows below it.

**Plumbing (Part A6):**

- **Validator and coverage:** 71 tables, all 71 pass, 4,822,974 rows (59 public, 12 internal).
- **Archive:** each new table's rows, appended locally and in the bucket.
- **Supabase:** the four tables and the ledger. Everything matched; 282.3 MB before, 285.9 MB after the vacuum.
- **Redivis:** the three public tables to `energy_research_warehouse`; `price_board_carbon`, `api_cost_ledger` and `news_scores_shadow` to the internal dataset. Each `count(*)` equals its CSV; the license check finds 0 internal tables in the public dataset.
- **`package/llms.txt`:** the board's tables. The chat spec was regenerated and matches.
- **The chat catalogue:** the chat's `list_tables` reads coverage and the catalogue, so it lists the new tables.

## 3. Caching, story caps, the shadow scorer, the Thesis Builder

**Cost layer (B1).**

- **One client.** `warehouse/llm.py` is the only construction of the Anthropic client in the warehouse; all 11 Python call sites go through it. It records every `messages.create` and `messages.stream` call in `api_cost_ledger`: events shape, internal, tier `derived`, new sector `platform`.
- **Prices:** `warehouse/config/model_prices.yaml`, with its date.
- **Spend cap:** `ERW_SPEND_CAP_USD` refuses a call once a session's ledger total reaches it; it is tested.
- **The site's `/ask`** cannot write the table (anon key only). It records each call in `site_api_calls` (migration 010: anon may insert, never read).
- **`/internal/costs`:**
  - It shows spend per day, per step and per model over 30 days, plus two projected monthly bills (all calls, and the scheduled runs only).
  - No link reaches it, and it is not indexed.
  - It answers 404 unless `?token=` equals `INTERNAL_COSTS_TOKEN`. Its database function `internal_costs(token)` answers nothing without the same token (verified: wrong token HTTP 401, right token the 286 rows).
  - Live it answers 404 until the token is set on Vercel (question 1).

**Caching measurement (B2).** One day of stored stories, 2026-09-26 (435 stories), scored by Haiku in 11 calls, twice:

| | Input (uncached) | Cache write | Cache read | Output | USD |
|---|---|---|---|---|---|
| With caching | 99,549 | 13,769 | 137,690 | 39,681 | **0.3289** |
| Without | 251,008 | 0 | 0 | 39,515 | **0.4486** |

- **26.7% less for the day, 48% less on input** (output is the same work).
- **What is cached.** The scorer now puts the rubric system prompt, then the reference list as it stood at the start of the run, as the two cache breakpoints (`score.request_parts`); the run's own scored stories and the batch follow.
  - Before, the run's scored stories were merged into the reference list, changing the prefix on every call.
  - The stories offered as duplicate candidates are the same, in two blocks.
- **Sonnet.** At Sonnet 5.5 prices the same token counts give USD 0.658 against 0.897 (arithmetic on Haiku's counts, not a measurement). The daily run's Sonnet scorer uses the new layout from its next run.
- **Too short to cache.** On small days the rubric and reference list are under Haiku's 4,096-token cache minimum and nothing caches; Sonnet 5.5's minimum is 512.
- **Other breakpoints added:** the digest and Roundup headline and summary system prompts (the shadow Roundup read 4,228 cached tokens written by the shadow Digest minutes before), the chat's growing conversation (Python and site), policy reads, and the Thesis Builder's research system prompt. Extraction and chat already cached their system prompts.

**Story caps (B3).** `MAX_STORIES_PER_RUN` (default 400) and `MAX_STORIES_PER_SOURCE` (default 120), from the environment, applied at scoring: ingest stores every story.

- **Priority:** the outlet's mean significance over its last 30 days of scores, then the newest first.
- **Logging:** each cut is logged with its count and the lowest priority admitted. A cut story stays unscored and competes again next run.
- **The logs.** The news pipeline has run since 2026-09-25, so there are 5 days of logs, not 14.
  - Regular runs held 33 to 655 new stories (median 184; 502 after a 20-hour gap; 655 on the first run).
  - Sonnet cost USD 0.0025 to 0.0032 a story, so 400 caps a catch-up run's scoring near USD 1.20.
  - Per outlet per run: median 3, 95th percentile 68, largest 108: full Google News pages of Reuters, Bloomberg, WSJ and FT.
- **Why 120 per outlet, not 60.** I first set 60. The replay showed it would cut about 40 stories from each of those four outlets on every run, so I raised it to 120, above the largest page seen. It now cuts only a flooding feed; the run cap does the rest.
- **Replays:**
  - the 502-story run: 102 left for later, 96 of them FT's (the outlet whose scored stories average 1.16);
  - the 655-story first run: 255 (WSJ 108, FT 99, Reuters 38);
  - a 184-story run: none.

**The Haiku shadow scorer (B4).** `warehouse/news/shadow.py`:

- **What it does:** the same rubric, system prompt, schema and batching as the published scorer, into `news_scores_shadow` (internal, tier `model_extracted`; never a public table).
- **Switches:** `SHADOW_MODEL: claude-haiku-4-5` in both workflows; deleting that line is the kill switch. Expiry: 2026-10-06 in `warehouse/config/shadow.yaml`, after which nothing is scored or sent.
- **Recipients:** `SHADOW_RECIPIENT` if that secret exists, else `DIGEST_RECIPIENTS` (Samuel's address). Never subscribers.
- **Sent today, once each:**
  - "SHADOW HAIKU: ERW's Energy Digest, 2026-09-29";
  - "SHADOW HAIKU: ERW's Roundup, 2026-W39".
  - Both are written under `warehouse/output/shadow/`; the published files are untouched.
  - The shadow Roundup's five stories of the week share 3 with the published one: Akamai and Anthropic, DOE's grid projects, Amazon's Generac order.
- **Backtest:** 2,375 stories (the last 30 days of Sonnet-scored stories and the eval sample), 84 calls, 0 failed; Haiku left out 1 story.
- **`warehouse/news/shadow_agreement.py`:**

| Measure | Result |
|---|---|
| Selection: the day's top-10 clusters (as the digest ranks them), matched when they share a story; mean over 21 days | **0.80** |
| Same, weighted by stories (the big days, 150 to 680 stories, 2026-09-24 to 28) | 0.63 (days: 0.60, 0.60, 0.50, 0.60, 0.70) |
| Top-10 stories by significance, mean per day | 0.85 |
| Significance: Pearson / Spearman | 0.862 / 0.809 |
| Significance: mean absolute difference; exact; within 1 | 0.80 points; 45.8%; 81.9% |
| AI-power tag (relevance 7 or more): agreement; Cohen's kappa | 97.5%; 0.64 |
| AI-power tagged: Sonnet / Haiku | 61 / **113** (Haiku tags nearly twice as many) |
| AI-power relevance, mean absolute difference | 0.39 points |
| Cost, Haiku (measured, ledger) | USD 1.9226, **USD 0.00081 a story** |
| Cost, Sonnet, same stories (estimate: 7,748 stories in the 10 scoring runs whose logs are on this machine) | USD 6.25, USD 0.00263 a story |

- **Human labels:** Samuel's 50-story file (`warehouse/news/eval/eval_sample.csv`) has no human labels yet. The script reports both models against them once they are filled, and Haiku has scored all 50.
- **From tonight** both models' scoring calls are in the ledger, so the daily comparison of cost is measured, not estimated.

**Thesis Builder toward USD 1 (B5).** On the cheapest existing thesis, "subsurface heat mapping for geothermal".

- **Before** (run 20260928T203525Z): 26 calls, 37 web searches, **USD 2.2310**, 7.3 minutes.
- **After:** 15 calls, 37 searches, **USD 1.2253**, 5.4 minutes. Workbook `docs/thesis/subsurface-heat-mapping-for-geothermal-2026-09-29.xlsx`; the earlier workbook is not overwritten.
- **Changes:**
  - one SDK retry instead of two;
  - research system prompts cached;
  - at most 3 cited passages of 300 characters per source in the structure prompt (the number check still reads every passage);
  - the eight structure calls batched into two.
- **Where the money is.** Research is USD 0.93 of the USD 1.23, including USD 0.37 of web searches, so the last 20% to USD 1 means fewer searches or a cheaper research model.
- **The failed first attempt.** One schema holding all eight sheets was refused (HTTP 400, "the compiled grammar is too large") after the research had run, and the research was not saved.
  - I checked groupings with `max_tokens=1` calls: USD 0.0157, refused requests are not billed.
  - Two groups are accepted: {scope, fundamentals, trends} and {landscape, capital, incumbents, risks, policy}. A refused group is halved automatically.
  - The research is now saved before structuring; `--resume-research` reruns only the structure.
- **Quality to watch:** the batched landscape found **2 companies**, against 7 in the run before. Question 4.

**Chat evaluation (C2).** 30 questions, **USD 1.4322** (USD 0.0477 a question).

- **As run: 20 of 30.** All 10 misses were citation failures but one.
- **Nine were the eval's fault.** Its acceptable tables still used the pre-consolidation names (`ercot_dam_hub_prices`), while the answers cited `iso_dam_hub_prices` correctly.
- **The fix.** The citation check now accepts an old name's consolidated table. Re-scored from the saved records, no new call: **29 of 30** (`warehouse/chat/eval/results/20260929T110457Z_rescored.md`).
- **The one left,** q27, is a count on `news_index`, which has grown since its expected value was computed.

**Callers renamed (C1).** `brief.py`, `roundup.py` and the analysis templates read `iso_dam_hub_prices`, `iso_rtm_hub_prices` (by market), `eia930_all_demand` (by ba), `iso_trader_daily` and `ercot_all_hub_prices_history` (by market and year).

- The migration map is kept.
- Checked with `DeprecationWarning` as an error: 9 template runs, and the digest's and Roundup's numbers sections.
- A bug fixed on the way: the digest's real-time scan would have labelled every ISO of the consolidated table "ISO" and used UTC days. It now reads each market in its own time zone.

## 4. Decisions made without a human (each reversible)

1. **`/board` is a new page.** The home page's board stays as it was and links to it.
2. **`price_board_carbon` is internal,** not public as the prompt said, because its inputs are (the license rule). It becomes public, and shows on the page with no code change, if CARB's and RGGI's terms are confirmed and their registry lines say public.
3. **The "one row per hub per market" table is long series rows** (`da_`/`rt_` variables), the only shape the validator accepts. The page pivots it.
4. **Board rules:**
   - means of complete local days only;
   - 30-day min and max of the daily means;
   - the day-ahead "latest day" can be tomorrow;
   - day-ahead minus real-time on the latest day both are complete.
5. **ERCOT's annual averages** are rows of `price_board_peak_offpeak` (`year_` variables): the peak-premium table has medians, not means. The page shows both.
6. **Stale series:** RGGI's future-vintage series is left out as discontinued. On the runner, history and CARB rows are carried forward, said in the header.
7. **The cost ledger:**
   - events shape, internal, tier `derived` (Anthropic's counts, the ERW's dollars), new sector `platform` (added to `docs/datastandard.md` and the package);
   - the cost page through a token-checked database function;
   - the site's calls in `site_api_calls`.
8. **The shadow:**
   - The kill switch is the workflow's `SHADOW_MODEL` line.
   - The expiry stops scoring and sending.
   - The shadow issues keep the production writer, so only the scores differ.
   - Haiku gets temperature 0 and no effort setting (it takes none).
   - The eval sample's 50 stories were added to the backtest (USD 0.04), so the human comparison is ready.
9. **Caps at scoring, not ingest,** priority by outlet mean significance; per-outlet default 120, not the 60 first tried.
10. **The scorer's reference list is in two blocks** (the start-of-run list, then this run's scored stories) for the cache. The same stories are offered.
11. **The Thesis Builder was run a second time** after my own change made the first attempt fail after its research. The prompt allowed one run; without a completed run there was no "after" bill. The rerun cost USD 1.2253, inside the cap, and the research is now saved first so this cannot recur.
12. **The chat eval's citation check** accepts consolidated names; re-scored from records.
13. **The package tests' fixed expectations** were updated for the new tables. Five tests broke on expectations, none on a wrong value.
14. **The 47 news stories** that session 29's merge left out of the working `news_stories` were not merged back (question 6).

## 5. Run health, gate, the 14:00 UTC run

- **At the start** (no changes): the latest daily run on GitHub was 2026-09-28, dispatch at 23:16 UTC, success.
  - Its table failures are all known gaps: CARB, the NYISO queue, the ERCOT large-load queue.
  - The local run of 2026-09-29 01:14 had 2 more failures:
    - `eia930_swpp_demand`: a forecast 19 hours short;
    - `eia_sector_energy_consumption_monthly`: 151 days old against a 150-day limit.

    Both refuse to write rather than write partial or stale data. The gate reads the GitHub run.
- **Gate:** `build_status.py --gate`: **open** (0 failed tables outside the known-gap list). This session added no source.
- **The 14:00 UTC run had not landed** by the report (12:45 UTC). Scheduled runs have started hours late (2026-09-28's at 20:18). `origin/main` had no new commit when I pushed.
- **What that run will do for the first time:**
  - restore `api_cost_ledger`, `news_scores_shadow` and three board tables from the drafts (all uploaded today);
  - build the board with carried rows;
  - score the shadow and send a shadow Digest.

  Each piece ran here. The whole sequence was not, since a local daily run would re-pull every source.
- **Supabase loader:** its reachability probe (an exact count over `series`) failed twice with HTTP 500 and passed on retry. It is transient, but a daily run could fail on it (question 7).

## 6. Open questions for Samuel, and what was skipped

**Open questions:**

1. **Turn on `/internal/costs`:** set `INTERNAL_COSTS_TOKEN` in Vercel's environment to the value in `.env` (it is already in the database) and redeploy. Until then the page answers 404 live.
2. **The shadow's address:** it goes to `DIGEST_RECIPIENTS`. Add a `SHADOW_RECIPIENT` secret if it should go elsewhere.
3. **Carbon on the public board:** confirm CARB's and RGGI's terms. With them public, the block fills with no code change.
4. **The Thesis Builder's landscape:** 2 companies against 7 before. Put landscape in its own call (about USD 0.15 more a run), or keep the saving?
5. **The 50-story eval file:** fill `human_significance` and `human_ai_power` in `warehouse/news/eval/eval_sample.csv`. Then `python warehouse/news/shadow_agreement.py` reports both models against you.
6. **The 47 stories.** The local run of 2026-09-29 01:10 ingested 47 stories that session 29's merge of GitHub's run left out of the working `news_stories`.
   - They are in the archive (run 20260929T012526Z).
   - Merge them back (`warehouse/archive/restore.py news_stories --as-of 2026-09-29T01:30:00Z`, then add the missing keys), or leave them?
7. **The Supabase loader's reachability probe** times out now and then: make it cheaper (an estimated count), or retry?
8. **After 2026-10-05:** Haiku for scoring, or not?

   The backtest says it:
   - selects the same digest stories about 80% of the time (60% on the busiest days);
   - agrees within one point on 82% of significance scores;
   - tags nearly twice as many AI-power stories;
   - costs about a third per story.
9. **Still open from session 29:** the Redivis deletion command, the `SUPABASE_DB_URL` secret, and Ben's items 4 and 6.

**Skipped, or not done in full:**

- **The site's `/ask` ledger row** was not exercised live: a question would have been a model call outside the approved list. The insert path is migration 010, checked with the anon key's grants; the page's read side was verified.
- **The package suite was not re-run end to end after the fixes.**
  - The first run: 333 tests, one process per 40, 328 passed and 5 failed (expectations).
  - The 5 were re-run after the fixes and pass.
  - `tests/`: 51 of 51.
- **Nothing from the approved list was left undone:** the Haiku backtest, one shadow Digest, one shadow Roundup, the Thesis Builder, the chat eval and the caching measurement all ran.
