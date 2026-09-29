# Session 13 report

Energy Research Warehouse (ERW), session 13, run 2026-09-26 (UTC). The human's rulings on sessions 11 and 12 were applied, with one exception, named first. Nothing was pushed. No key was printed or committed.

**One ruling not applied: CAISO's latest price keeps the label `lmp_rtm_5min`.**
- **The ruling** was to relabel it `lmp_rtm_15min`. It rested on my session 11 guess, and the source contradicts that guess.
- **The evidence:**
  - gridstatus's CAISO real-time call for 2026-09-26 returned 108 intervals, every one 5 minutes long by CAISO's own interval start and end fields, and 5 minutes apart.
  - The newest interval, fetched at 15:54:49 UTC, ran from 15:55 to 16:00 UTC. CAISO publishes each binding 5-minute price just before its interval begins.
  - The quarter-hour starts I saw in session 10 and 11 were coincidence.
- **Why not relabel:** a 15-minute label would put a wrong fact on the live board. PRIORITIES.md ranks a wrong answer above everything else.
- **Where it is recorded:** the evidence is in the header of `warehouse/connectors/latest_prices.py`, and `package/llms.txt` says the same (open question 1).

## What was built

| Task | Result | Commit |
|---|---|---|
| 1 | `package/llms.txt` rewritten (255 lines); `CLAUDE.md`, `ARCHITECTURE.md` and `docs/platform-tools.md` brought to the current state; `git+https` install lines | `9fe9aec` |
| 2 | CAISO label kept, with the evidence in the header; per-table SHA-256 in the Supabase loader; per-day backfills of four real-time and demand tables; validator, coverage and Supabase load | `1a66982` |
| 3 | Evaluation rerun with the new briefing: **28 of 30** (session 12: 27 of 30), **USD 0.0195 per question** (was 0.0433) | `282a155` |
| 3, follow-up | A tool bug found by the rerun, fixed after the results were committed (Task 3, below) | `9dcfb9b` |
| 4 | Digest check run: news ingest, scoring and brief; top 10 with sector and `ai_power_relevance` | `9b6deb1` |
| 5 | This report | final commit |

## Task 1: briefing and docs

- **`package/llms.txt`** (255 lines, under the 350 limit). It is also the chat's system briefing. It now covers:
  - the three shapes;
  - every table family, with the key EIA series IDs:
    - ISO live windows, and the ERCOT yearly history from 2015;
    - the derived peak premium;
    - EIA-930;
    - EIA petroleum, gas, retail and LNG series;
    - FRED;
    - capacity, carbon and shipping (internal);
    - EIA-860M and queue entities;
    - news events;
  - a table saying which table answers which question: history goes to the yearly and derived tables;
  - what is not in the warehouse;
  - ten pitfalls;
  - the license rule;
  - the three backends;
  - the site and the chat.
- **`CLAUDE.md`:**
  - the stack now has rows for Supabase, the site and the chat;
  - the layout names `warehouse/derived`, `news`, `metadata`, `redivis`, `supabase`, `chat`, `package/` and `site/`;
  - the run commands include the daily run, the loader, the chat and the site.
- **`ARCHITECTURE.md`:** the flow now runs through the loader, `latest_prices`, the site and `/ask`. It also says how the two chat front ends share one definition, and it adds three rows to "which document wins".
- **`docs/platform-tools.md`, the real status of tools 1, 2, 5, 15 and 20:**
  - built and run locally, not deployed;
  - the Redivis dataset is an unreleased draft;
  - **the public GitHub repository was at the session 5 commit `1615d1d`**, checked with `git ls-remote` during the session. *Corrected after the session:* that check showed which code was public, not whether workflows ran. The session 5 daily workflow was in fact running on GitHub, and it committed a data commit (`f049433`) at 17:43 UTC the same day. `main` was pushed after the session (`f5168e4`), so session 13's code and workflows are now on GitHub (see "Correction after the push" at the end).
- **Install line:** `pip install "git+https://github.com/SamuelEnrique/erw.git#subdirectory=package"` is in `package/README.md` (with the backend extras) and `site/data/site.json`, and `/data` shows it. Tested with `pip download`: it builds from the public repository (then the session 5 copy; session 13's since the push). The README says a GitHub install needs `ERW_BACKEND` or `ERW_DATA_DIR`, because the tables are not in the package.

## Task 2: fixes

**CAISO:** see the top of this report. `site/lib/chat/spec.json` was regenerated after each briefing change.

**Per-table SHA-256 in `load.py`.**
- **How it works:** migration 004 (applied) adds `catalogue.rows_sha256`. The loader hashes each table's license and selected rows, and skips a table whose hash equals the stored one. It still reconciles `count(*)` for every table. A failed table gets a null hash, so the next run loads it in full.
- **Results:**

| Load | Tables skipped | Time | Database |
|---|---|---|---|
| First, after the backfills (stores the hashes) | 0 | 180 s | 244.9 MB |
| Second | 66 of 66 | 38 s | 244.9 MB |

- **Size:** 244.9 MB is under the 300 MB guard, so the loader exits 0 again. The space left by session 11's double load has been reclaimed since then, not by this session.

**Per-day completeness.**
- **The rule:** a new `per_day` mode in `iso_prices.py` (MISO real-time, ISO-NE 15-minute real-time) and `PER_DAY` in `eia930.py` (ERCO and NYIS demand) fetch and check each operating day on its own. Complete days are written. A day that fails is not written, keeps any earlier rows, and becomes a `gap` row in `run_status.csv`.
- **Changes to `run_status.py`:** it now keys on market too, so a table can have several gap rows per run, and it leaves gap rows out of failure streaks.
- **Results of the 30-day backfills:**

| Table | Before | After | Days not written (reason) |
|---|---|---|---|
| `miso_rtm_hub_prices` (hourly, MISO's own real-time LMP) | 3 days | 30 of 30 | none |
| `isone_rtm_zone_prices` (15-minute means) | 3 days | 24 of 30 | Sept 2, 11, 12, 13, 15, 25 (1 to 8 quarter hours of 5-minute prices missing) |
| `eia930_erco_demand` | 3 days | 28 of 30 | Sept 4, 5 (EIA's demand forecast missing 19 and 5 hours) |
| `eia930_nyis_demand` | 3 days | 28 of 30 | Sept 4, 5 (forecast missing 20 and 4 hours) |

- **MISO scope:** MISO has no 15-minute real-time table. Its 5-minute prices are not retrievable for 30 days without a key (connector docstring), so the MISO real-time table is hourly by design. "The thin real-time window" was that table.
- **Not in scope, and failed:** ISO-NE's hourly real-time table failed its 30-day run. ISO-NE served an empty file for 2026-09-25 (`EmptyDataError`), and the whole-window rule held: the table was left as it was. The daily run will retry it.
- **The gap rows' wording:** they read "incomplete data, no file written", which is misleading because the table was written. New gap rows say "day incomplete"; the rows already recorded were left as they are.

**Checks after the backfills:**
- The validator passed every table (exit 0), and coverage was rebuilt (81 tables).
- The Supabase load reconciled every table.
- Package suite: 386 passed, 3 failed. All three failures are Redivis comparisons of `news_index` and coverage. The Redivis draft still holds yesterday's 714 news rows, while today's ingest made 967, and nothing uploads to Redivis until the daily run.

**A flaky test, fixed.** `SupabaseBackend` paged through the 27,702 fuel-price rows without an ORDER BY. Postgres does not promise the same order on every request, so a page could repeat some rows and skip others. The test failed in the suite and passed alone.
- **Fix:** the backend now pages in each table's key order (`package/src/erw/remote.py`). The site's `describe_table` got the same fix.
- **Check:** the Supabase backend tests passed 16 of 16 afterwards.

## Task 3: the evaluation, rerun

**Setup.**
- **Questions:** the same 30.
- **Expected answers:** recomputed from today's tables into `warehouse/chat/eval/questions_s13.yaml`. Session 12's `questions.yaml` was left as it was.
- **Two expected answers changed with the data:**
  - q02: the MISO backfill holds a 1,452.65 USD/MWh spike inside the week asked about, so MISO, not ERCOT (337.72), is now the right answer;
  - q27: today's ingest added stories dated 2026-09-25, so the count went from 559 to 677.
- **Code:** no code in the loop or the check changed. The only change since the baseline run is session 12's em-dash normalization of model text, which scores nothing. `eval.py` and `expected.py` gained `--questions` and `--out`.
- **Run:** `20260926T163854Z`.

| Measure | Session 12 (old briefing) | Session 13 (new briefing) |
|---|---|---|
| Correct | 27 of 30 (90%) | **28 of 30 (93%)** |
| number | 25 of 28 | 26 of 28 |
| text | 28 of 28 | 28 of 28 |
| citation | 25 of 28 | 28 of 28 |
| refusal (right "not in the warehouse" or not) | 27 of 30 | 30 of 30 |
| Refused by the number check after a retry | 1 (q03) | 0 |
| Retried after the number check | 7 | 5 |
| Mean tool calls | 2.93 | 1.73 |
| Cost, total | USD 1.2996 | USD 0.5844 |
| Cost per question: mean / median / max | USD 0.0433 / 0.0269 / 0.1527 | **USD 0.0195** / 0.0119 / 0.0672 |
| Time per question: median / max | 11.4 s / 43.4 s | 6.8 s / 25.6 s |

**Per-question changes:**
- **Fixed by the new briefing:** q03, q07 and q08, all three session 12 failures.
  - q07 and q08: the briefing's table map sent the model to `ercot_rtm_hub_prices_2025` and `ercot_peak_premium_annual`, where the old briefing had sent it to the live table and to "not in the warehouse".
  - q03: this time the model wrote no extra numbers in its prose, so the check passed.
- **New failures:** q01 and q09.
- **Retries this run:** five, all descriptive numbers caught by the unchanged check: "15" (q03, q08, q12), "21" (q13) and "930" from "EIA-930" (q29). All five passed on the second draft.

**The two failures, verbatim.**

**q01** (expected 33.3904).

Question: "What was yesterday's average day-ahead price at ERCOT's HB_NORTH hub, over the ERCOT operating day (America/Chicago)?"

The model's calls: `query {"table": "ercot_dam_hub_prices", "aggregation": "mean", "entity": "HB_NORTH", "variable": "spp_dam", "start": "2026-09-25", "end": "2026-09-26", "tz": "America/Chicago"}`, made twice.

Answer:
> Yesterday's (2026-09-25) average day-ahead price at ERCOT's HB_NORTH hub was 37.84 USD/MWh, the mean of 24 hourly day-ahead settlement point prices over the ERCOT operating day in America/Chicago time (ercot_dam_hub_prices).

**q09** (expected 33.6487).

Question: "What was the average day-ahead LMP at the ISO-NE internal hub on 2026-09-24, New England local time?"

The model's calls:
1. `describe_table {"table": "isone_dam_zone_prices"}`
2. `query {"table": "isone_dam_zone_prices", "aggregation": "mean", "entity": "isone:.H.INTERNAL_HUB", "variable": "lmp_dam", "start": "2026-09-24", "end": "2026-09-25", "tz": "America/New_York"}`

Answer:
> The average day-ahead LMP at the ISO-NE internal hub (.H.INTERNAL_HUB) on 2026-09-24 (New England local day, America/New_York) was 34.01 USD/MWh, the mean of 24 hourly day-ahead LMP intervals (isone_dam_zone_prices).

**Both are the same tool bug, not a model error.**
- **The bug:** the model did exactly what the tool's description told it to. `tz` was described as setting "year/month/day/hour grouping and day boundaries", but the code applied it only to grouping: `start` and `end` were always read as UTC. So both answers are the mean of the UTC day, correctly computed and cited, for the wrong period.
- **Why the baseline passed:** in session 12, the model happened to write explicit UTC times for these two questions.
- **Fixed after the results were committed** (`9dcfb9b`), in `warehouse/chat/tools.py` and `site/lib/chat/tools.ts`:
  - a `start` or `end` without `Z` or an offset is now read in `tz`, with UTC as the default, so calls without `tz` are unchanged;
  - explicit `Z` and offsets are taken as given.
- **Checked:**
  - The q01 and q09 calls now return 33.390417 and 33.64875, the expected answers. The same calls without `tz`, or with explicit UTC bounds, return what they did before.
  - The TypeScript conversion passes 11 cases, including both daylight-saving days of 2026.
- **The 28 of 30 above was measured before the fix.** I did not rerun the evaluation: the task said to run it once.

## Task 4: digest check

**The run:**

| Step | Result |
|---|---|
| `ingest.py` | 253 new stories from 44 feeds |
| `score.py` | 253 of 253 scored by `claude-sonnet-5`, 11 calls, USD 0.8014 |
| `index.py` | `news_index` now 967 rows |
| `brief.py --out docs/digest/checks/2026-09-26T1614Z.md` | 291 scored energy stories in the 24 hours to 16:14 UTC, 269 clusters, USD 0.0145 |

- **`--out`, new this session:** it writes a check run to its own file. Without it, a second run on the same date would have overwritten the day's published digest (`docs/digest/2026-09-26.md`, written at 00:00 UTC) and `latest.md`.

**Top 10 of the check digest** (the 24 hours to 16:14 UTC; headlines are the digest's):

| # | Headline | Significance | Sector | ai_power_relevance |
|---|---|---|---|---|
| 1 | TotalEnergies makes final investment decision on Absheron field in Azerbaijan | 9 | gas | 0 |
| 2 | DOE selects 31 projects for $5.25 billion grid transmission initiative | 8 | transmission | 6 |
| 3 | Trump administration orders Colorado coal plant kept online to avoid blackouts | 7 | policy | 4 |
| 4 | Eaton to acquire Italy's COL Group for €810 million to expand grid business | 7 | transmission | 3 |
| 5 | Tennessee nuclear project nears US regulatory approval | 7 | nuclear | 3 |
| 6 | EU warns of energy price crisis, asks members to consider demand curbs | 7 | policy | 1 |
| 7 | FERC issues final environmental impact statement for Sabine Pass expansion project | 7 | lng | 1 |
| 8 | BP explored deal for Devon's Eagle Ford shale assets, sources say | 7 | oil | 0 |
| 9 | Tanker shortage drives oil-shipping rates higher as Canadian crude reaches Asia | 7 | oil | 0 |
| 10 | White House considers diesel export ban as prices keep rising | 7 | oil | 0 |

**For comparison, the published digest of 2026-09-26** (the 24 hours to 00:00 UTC; same stories and clusters, `ai_power_relevance` read from the same scored rows):

| # | Headline | Sig. | Sector | AI |
|---|---|---|---|---|
| 1 | Applied Digital plans $3.2bn AI data center in Alabama | 8 | datacenter_power | 9 |
| 2 | Problems emerge in Oracle's New Mexico AI data center project | 8 | datacenter_power | 9 |
| 3 | DOE funds 31 grid upgrade projects to speed data center connections | 8 | transmission | 8 |
| 4 | Anthropic signs $12 billion computing deal with Akamai | 8 | deal | 7 |
| 5 | Fervo Energy achieves first power at Utah geothermal plant | 8 | generation | 6 |
| 6 | Judge overturns Trump administration's cancellation of Solar for All program again | 8 | policy | 6 |
| 7 | Exxon nears preliminary deal to invest in Venezuela's oil fields | 8 | oil | 0 |
| 8 | AI-driven nuclear power push faces cost and regulatory hurdles | 7 | nuclear | 9 |
| 9 | Anthropic and OpenAI expand AI data center footprint amid financing challenges | 7 | datacenter_power | 9 |
| 10 | FERC rejects Oklo bid to reinstate project in PJM study cycle | 7 | interconnection | 8 |

**What this shows, for the human to judge:**

| | Published digest | Check digest |
|---|---|---|
| Sectors in the top 10 | 8 | 6 |
| Stories with ai_power_relevance 7 or more | 6 | 0 |
| `datacenter_power` stories | 3 | 0 |
| Mean ai_power_relevance | 7.1 | 1.8 |

- **Same rubric in both.** Every story in both windows was scored from 2026-09-25 21:30 UTC onward, well after the session 7 rubric (`b88ae79`). So the difference between the two top 10s is the news of each window, not a change in scoring.
- **The rubric's rule:** "An AI or datacenter angle earns no significance credit by itself: a story about AI or datacenters is scored on the same energy consequences (MW, dollars, counterparties, rules, prices) as any other story."
- **Most datacenter stories in the published top 10 carry those consequences:** a $3.2bn project, a $12 billion contract, 23 GW of interconnection.
- **Two are the ones to check:**
  - "Problems emerge in Oracle's New Mexico AI data center project" scored 8, and its scored fields name no MW or dollars (its why line says "execution risk");
  - "AI-driven nuclear power push faces cost and regulatory hurdles" scored 7, with neither.
- **Open question:** whether those two scores are acceptable is the human's call (open question 4).

## Decisions

1. **The CAISO ruling was not applied** (top of this report).
2. **Expected answers were recomputed into a new file** rather than overwriting session 12's. The data had changed under two questions, and a baseline file must stay as it was.
3. **The tool bug was fixed after the rerun, not before.** The task said to change no loop code for the rerun. Leaving a known wrong-period answer in the public `/ask` code would break the first rule of PRIORITIES.md, so the fix is a separate commit, dated after the results.
4. **Gap rows are their own status.** A gap day is not a failed run of the table, so it never feeds the three-run failure streak that opens a GitHub issue.
5. **The hash lives in Supabase**, not in a file in git: a CI run and a local run then compare against what the database actually holds.
6. **Check digests go to `docs/digest/checks/`.** The site's content builder reads only `docs/digest/YYYY-MM-DD.md`, so a check file never appears in the public archive.

## Errors hit

1. **Heredoc patches lost backslashes three times:** in a Python replacement for `load.py`, in one for `brief.py`, and in the regexes of `site/lib/chat/tools.ts`, where `\d` became `d`. The first two failed their `assert` and changed nothing. The third was caught by the 11-case unit check before the commit. Each was redone with the Edit tool or a script file.
2. **Two copies of the package suite ran at once.** A process I started with `&` kept running after its shell command returned. It was harmless, and both runs are reported above.
3. **The first `expected.py` patch failed its assert** on a line with an escaped newline, and was redone with the Edit tool.

## Rerun

```bash
python warehouse/connectors/iso_prices.py miso --days 30      # per-day completeness for RTM
python warehouse/connectors/iso_prices.py isone --days 30
python warehouse/connectors/eia930.py --days 30 --ba erco --ba nyis
python warehouse/metadata/run_status.py record && python warehouse/validate/erw_validate.py warehouse/output/*.csv
python warehouse/metadata/build_coverage.py && python warehouse/supabase/load.py
python warehouse/chat/eval/expected.py --out warehouse/chat/eval/questions_s13.yaml
python warehouse/chat/eval/eval.py --questions warehouse/chat/eval/questions_s13.yaml
python warehouse/news/brief.py --out docs/digest/checks/<time>.md
```

## Open questions for the human

1. **CAISO label:** confirm that `lmp_rtm_5min` stands, given the evidence above, or overrule it knowing that it is a 5-minute price.
2. **Push to GitHub.** *Done after the session* (`f5168e4`; see the correction below). Still open: the repository secrets both workflows now need.
3. **ISO-NE's hourly real-time table** failed its 30-day run on an empty file for 2026-09-25. Should it get per-day completeness too? The ruling named only the 15-minute table.
4. **Two datacenter stories** in the 00:00 digest scored 7 and 8 without the MW or dollar consequences the rubric asks for (Task 4). Tighten the rubric, or accept them?
5. **Rerun the evaluation after the tz fix?** It would measure the fixed tools; this session ran it once, as asked. The fresh question set for a narrower post-check (ruling) is still to be designed.

## Correction after the push (2026-09-26, after the session)

At the human's request, `main` was pushed after this report was committed.

**Two statements above were wrong, and are corrected where they stand:**
- that the public repository being at session 5 meant "the daily and 15-minute workflows are not running on GitHub";
- the same claim in `docs/platform-tools.md`.

**What was actually true:** the session 5 version of `.github/workflows/daily-prices.yml` had kept running on GitHub. At 17:43 UTC on 2026-09-26 it committed `f049433`: refreshed price tables, eight run logs, and updates to `coverage.csv`, `run_status.csv` and `sources.csv`. Its commit message records its results: ok for ercot, caiso, nyiso, miso and eia_fuels; failed for spp RTM, isone RTM and RTM_HOURLY, and eia930_us48_generation.

**How it was integrated:**
- **The conflict:** every file in that commit conflicts with sessions 6 to 13, because since session 9 the tables and logs are not tracked. An ordinary merge would also have overwritten the local, git-ignored tables with the session 5 workflow's versions, including this session's backfills.
- **The merge:** at the human's direction, `origin/main` was merged with `git merge -s ours` (`f5168e4`). The bot's commit stays in history and the tree is the local one. The SHA-256 of four local data and metadata files was the same before and after the merge, and the pushed tree is identical to `ebc2d19`.
- **Not carried into the tree:** the rows that GitHub run added to `run_status.csv`. They remain in `f049433`.
- **The push** was a fast-forward, with no force.

**What is live on GitHub now:**
- session 13's code;
- `daily-prices.yml`, at 14:00 UTC: the connectors, news, digest, validator, coverage, the Redivis draft upload and the Supabase load;
- `latest-prices.yml`, every 15 minutes: the Supabase `latest_prices` board.

**Repository secrets they read:**

| Workflow | Secrets |
|---|---|
| `daily-prices.yml` | `EIA_API_KEY`, `ANTHROPIC_API_KEY`, `PJM_API_KEY`, `REDIVIS_API_TOKEN`, `REDIVIS_OWNER`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` |
| `latest-prices.yml` | `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` |

A missing secret makes its step fail. Missing Supabase secrets make `latest-prices.yml` fail on every 15-minute run. Which secrets are set could not be checked from this machine (no `gh` CLI).

**Large files:** GitHub warned about large files on the push (`GH001`). They are data CSVs committed in sessions 6 to 8, before session 9 took the tables out of git. They are no longer in the tree but remain in the history. Removing them would rewrite published history, so they were left.
