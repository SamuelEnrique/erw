# Session 17 report

Energy Research Warehouse (ERW), session 17, run 2026-09-27 (UTC). **API spend this session: USD 0.0407**, far under the USD 15 stop. No key was printed or committed. The session merged GitHub's daily-run commit, then pushed.

**Three things to know first:**
- **Task 1 could not be built as written.** ERCOT publishes no list of large-load requests with MW, county, status and dates. The rule that created its status report (Protocol 3.2.7, NPRR1267) requires the report to aggregate requests, with at least three customers per category. Nothing was invented. Instead, a connector watches ERCOT's page weekly and fails loudly until a request-level file appears.
- **Task 2 stopped halfway.** The news backfill made all 1,512 queries (47,578 items, 0 failed), then Claude Code stopped it because the machine was critically low on memory. As its notice instructed, I did not restart it. Nothing was ingested, scored or extracted. The saved responses allow a restart without querying Google again (commands below).
- **The Supabase load was not attempted.** It was refused last session. The value check ran against what CI loaded, and all 254 values matched.

## What was built

| Task | Result | API cost | Commit |
|---|---|---|---|
| 1 | `warehouse/connectors/ercot_large_load.py`: watches ERCOT's Large Load Integration page; no table (no request-level source) | 0 | `9ccb885` |
| 2 | `ingest.py --backfill` and `--from-raw`; the backfill run stopped before scoring | 0 | `e5b2920` |
| 3 | "Energy Week": `warehouse/news/weekly.py`, the Monday workflow, `/weekly`, 2026-W39 | 0.0055 | `e1f4ca9` |
| 4 | Datacenter status rulings and re-extraction; exact-decimal means; `/weekly` value check; briefing, coverage and live set; platform tools 4 and 14 | 0.0298 + 0.0054 | `2deeeca` |
| 5 | Screenshots, STATUS.md, this report | 0 | final commit |

## Task 1: ERCOT large-load queue

**What I looked for:** the current ERCOT file, as the prompt says. What exists:
- **Protocol 3.2.7** (NPRR1267, approved 2025-07-31) requires a monthly Large Load Interconnection Status Report. It aggregates by location, load zone, TSP, load type, request date, energization date and size range, with at least three customers per category, because customer data is confidential.
- **The report ERCOT actually posts** is a slide deck, "Large Load Interconnection Status Update" (for example `https://www.ercot.com/files/docs/2026/03/12/March-TAC-Report.pdf`). Its numbers are chart images, not text, with no county and no request rows.
- **"ERCOT Monthly"** states queue totals in prose in only 2 of its 16 issues from February 2025 to June 2026 (November 2025 and April 2026). For example, April 2026: 445.8 GW applied by 2033, of which 321 GW with no studies submitted, 93.7 GW under ERCOT review, 22 GW with Section 9.5 requirements met, 5.9 GW observed energized, and 3.2 GW approved to energize but not operational. That is too irregular for a series.
- **The Large Load Integration page** links 3 spreadsheets: the Batch Zero Load Information Form, a FAQ, and an RFI exhibit list.

**Decision.** With no rows to publish, there is no `ercot_large_load_queue` table and nothing to merge into `datacenter_projects` or `energy_projects`. `ercot_large_load.py`:
- reads the Large Load Integration page each week and keeps it raw;
- looks for a spreadsheet named as a status report or queue;
- **if there is none**, fails with the reason above and writes nothing. This week's run did exactly that;
- **if one appears**, reads it into `ercot_large_load_queue`, requiring a county and a MW column, with a harmonized status mapped from ERCOT's status words.

It runs weekly in `run_daily.sh` beside the ISO queues. A coverage rule and a live-set rule are ready for the table.

**Expect a streak issue:** a connector failing three runs in a row opens a GitHub issue, so after three Mondays this one will open one. Close it, or rule it a known source gap, as for SPP and CARB.

## Task 2: news backfill

**`ingest.py --backfill`:**
- **Queries:** every Google News feed in `feeds.yaml` (18 of them) keeps its `site:` filter and gets one sector's search terms (`BACKFILL_TERMS`: datacenter_power, deal, ppa, nuclear, lng, transmission, policy) and one month's `after:` and `before:` bounds, from 2025-10-01 to 2026-09-22. That is 1,512 queries, one at a time.
- **Filtering:** stories dated outside the range are dropped; the rest are deduplicated as in the daily ingest, by URL and near-identical title.
- **The cap:** at most 3,000 stories, taken round-robin over the 84 month-and-sector buckets, so the cap spreads over the whole year.
- **Provenance:** `feed` records the query that found each story, for example `Reuters energy (via Google News) [backfill lng 2026-01]`.

**A trial** (lng, January 2026, 18 queries) found 325 new stories, mostly from Bloomberg (98), Reuters (94), JPT (36) and the FT (28).

**The run (`20260927T033451Z`).** All 1,512 queries succeeded:

| Sector | Items |
|---|---|
| policy | 11,410 |
| transmission | 9,431 |
| deal | 8,588 |
| nuclear | 6,277 |
| datacenter_power | 5,427 |
| lng | 5,000 |
| ppa | 1,445 |
| **Total** | **47,578** |

While it was deduplicating, Claude Code stopped it for low memory. The stories are written only at the end, so `news_stories.csv` was untouched, and no digest was written. The raw responses are kept in `warehouse/raw/news/20260927T033451Z/`, which the 14-day prune will remove after 2026-10-11.

**Added so the work is not lost:** `--from-raw RUN_ID` rebuilds the same items from those saved responses, with no new queries. Tested: all 1,512 responses give the same 47,578 items in 84 buckets.

**Not reported, because the run did not reach them:** story, cluster, deal and facility counts, and cost.
- **Estimated cost:** about USD 5 to 6 to score 3,000 stories (at session 16's measured rate), plus about USD 2 to 3 for the two extractors.

**To finish,** when memory allows (the dedup step is the slow, heavy one):

    python warehouse/news/ingest.py --backfill --from-raw 20260927T033451Z
    python warehouse/news/score.py --days 400 --max-calls 70
    python warehouse/deals/extract.py --max-calls 200
    python warehouse/datacenters/extract.py --max-calls 100

## Task 3: Energy Week (tool 14)

**`warehouse/news/weekly.py`** writes `docs/weekly/YYYY-Www.md` and `latest.md` for an ISO week (Monday to Monday, UTC, cut at the run time):

| Section | What it holds |
|---|---|
| The five stories of the week | the highest-significance clusters. The model writes only the five headlines; the whys are the stories' scored why lines |
| Deals of the week | every `energy_deals` row dated in the week |
| Datacenter announcements | every `datacenter_projects` facility first reported in the week |
| Numbers of the week | read through `erw`, each with its table: the day-ahead average per ISO main hub over the ISO's local week, and the change from the week before (both weeks must be complete); the highest real-time price of the week, where, and how far each table reaches; Henry Hub, WTI and Brent (last close of the week, last close before it, change); US48 peak demand of the week and its hour |

**Schedule:** `.github/workflows/weekly-brief.yml` runs Mondays at 13:00 UTC, separate from the daily run. The runner has no tables, so it first restores the rolling windows from the Redivis draft and pulls the EIA fuel prices. It commits `docs/weekly` with the daily run's pull-then-commit step. Not yet run on GitHub.

**Site:** `/weekly` (the newest brief and an archive) and `/weekly/[week]`, with nav and home links.

**2026-W39 was generated** (to Sunday 04:42 UTC), after refreshing the local ISO and fuel tables:
- **Scale:** 845 stories in 747 clusters, 27 deals, 3 datacenter facilities.
- **Five stories:** TotalEnergies' Absheron FID; Oracle's force majeure; Applied Digital's Alabama datacenter; DOE's USD 1.9 billion for 31 grid projects; Anthropic's cloud deal with Akamai.
- **Day-ahead averages** fell against the prior week at MISO (-34.92), SPP (-12.48), ISO-NE (-8.18) and NYISO (-6.61), and rose at ERCOT (+1.94) and CAISO (+0.05).
- **The fuel closes** are those of Monday 2026-09-22, the newest EIA publishes.

## Task 4

**Datacenter status rulings.** The prompt now has an `applied` status (an application filed, not yet granted, which maps to the standard status planned). It also requires the words that state a status, as the code already did.

**Re-extraction:** `extract.py --reextract` over all 28 datacenter stories, 3 calls, USD 0.0298.
- **Counts:** 3 facilities before and 3 after.
- **Statuses:** before, permitted 1 and blank 2; after, applied 1, announced 1 and blank 1.
- **All three session 16 spot-check errors are fixed:**
  - Arevia Power went from permitted to applied;
  - its state went from blank to ID (Idaho), so it is now placed at the Ada County point;
  - Delta Forge 2 went from blank to announced.
- **Still wrong:** Arevia Power remains the operator as well as the developer, the third error from session 16.
- **Unchanged:** Oracle (New Mexico).
- **Kept:** the session 16 tables, in `warehouse/datacenters/history/`.

**Rounding fix.** The first value check found `/weekly` showing 44.29 for ISO-NE's prior week. Supabase gave 44.30, and the exact mean is 44.295: a float sum had landed just under the half.
- **Fix:** the digest and the weekly brief now compute day-ahead means in exact decimal arithmetic, rounded half up (`brief.mean2`), and the checker does the same.
- **Result:** the brief was regenerated (USD 0.0054). The weekly changes are now differences of the means as displayed.

**Value check.** `check-values.mjs` now parses `/weekly` and recomputes its 20 numbers from Supabase: 12 weekly day-ahead means, 6 fuel closes, the real-time peak, and the US48 peak with its hour.
- **Result: 254 of 254 values match**, including 20 of 20 on `/weekly` and 3 on `/datacenters`.
- **`/map` contributes none,** because Supabase has no `energy_projects` rows (next section).

**What GitHub's daily run 4 did** (manually dispatched on session 16's code; merged here):
- **The commit step succeeded,** so the session 16 fix works on GitHub.
- **It loaded:** `energy_deals` (27 rows) and `datacenter_projects` (3, the session 16 version).
- **It skipped `energy_projects`:** NYISO's queue answered HTTP 202 (the same response the CARB PDF gives), so an input was missing.
- **`supabase_load` exited 1.** The reason is in the run's log artifact, which needs a GitHub login.

**Also:**
- `llms.txt` and the chat spec now describe the new datacenter statuses, the weekly brief, and the ERCOT large-load gap.
- Coverage and the live set have rules for `ercot_large_load_queue`.
- The validator passes every changed table, and coverage is rebuilt.
- `docs/platform-tools.md` has tools 4 and 14.

## Task 5

- **Screenshots:** `weekly-desktop.png` and `-mobile.png` (new), plus `datacenters-*` and `home-*` (re-shot).
- **STATUS.md** regenerated.

## Decisions

1. **No ERCOT large-load table and no merges** (Task 1): there is no request-level source, and aggregates cannot be placed on a map as projects.
2. **The weekly brief has its own workflow** at the requested hour. The daily run starts at 14:00, and putting the brief in it would move the brief's time.
3. **The backfill's queries come from the Google News feeds' `site:` filters,** plus sector terms, as the prompt says. `feed_sector` stays the feed's own beat, so the query's sector does not steer the scorer's sector.
4. **The Task 2 extractions would use the rulings of Task 4.** They never ran, so this had no effect.
5. **`run_status.csv` was merged as the union of rows,** and `sources.csv` by source, keeping every table of each.

## Errors hit

1. **The backfill was stopped for low memory** (above).
2. **Heredoc quoting broke two patches;** they were rewritten through files.
3. **Float rounding in the weekly means** (fixed, Task 4).
4. **Merge conflicts on `run_status.csv` and `sources.csv`,** resolved without dropping a row.

## Open questions for the human

1. **Finish the backfill** with the four commands in Task 2, before 2026-10-11 when the raw responses are pruned. Expect about USD 7 to 9.
2. **Run the daily workflow with queues when NYISO's queue answers** (it gave HTTP 202 today). Then `energy_projects` reaches Supabase and `/map` shows data. Also check why `supabase_load` exited 1 in run 4: its log is in the run's artifact.
3. **The ERCOT large-load watch will open a streak issue after three Mondays.** Keep it as a reminder, or rule it a known gap?
4. **The weekly workflow has not run on GitHub yet.** Its first scheduled run is Monday 2026-09-28 at 13:00 UTC; it needs the EIA, Anthropic and Redivis secrets the daily run uses.
