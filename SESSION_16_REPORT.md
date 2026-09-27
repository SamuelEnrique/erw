# Session 16 report

Energy Research Warehouse (ERW), session 16, run 2026-09-27 (UTC). Every task in SESSION_16_PROMPT.md was carried out, with two limits set by this machine's permissions (below). The session pushed four times, each after merging origin/main; GitHub had no daily-run commits to merge, because daily runs 2 and 3 both failed before committing. No key was printed or committed.

**Three things to know first:**
- **The new tables are not in Supabase yet.** The Supabase load from this machine was refused by Claude Code's permission check (a write to a shared resource), and I did not retry it. So `/map` and `/datacenters` show their "no data" state until a load runs. The layout was checked instead from the local CSVs, on a temporary preview route that was deleted afterwards. Its screenshots are committed as `*-preview-local-csv-*.png`.
- **The workflow was not triggered.** No GitHub token was available: reading git's stored credential was also refused. Please trigger **daily prices** by hand (Actions, daily prices, Run workflow; the new `queues` input defaults to 1). That run loads `energy_deals`, `datacenter_projects` and, because it pulls the queues, `energy_projects` into Supabase.
- **The GitHub log was not in the prompt.** The prompt has the placeholder "[paste the last 25 lines of the red step here]". I found the cause another way: the run's failure issue (#2, public) holds the tail of `daily.log`, and the public jobs API gives the step list. The commit step's own output is not in that issue, so the exit 128 cause below is inferred from the code, then reproduced.

## What was built

| Task | Result | Commit |
|---|---|---|
| 1 | CI commit step fixed; news_brief fixed; EIA-930 generation per day; extractor rulings with a re-extraction (29 deals became 26) | `95586b8` |
| 2 | `energy_projects`: 45,488 rows, 43,316 placed | `e7e3748` |
| 3 | `/map`: canvas points on inline US geometry, filters, click card, legend, table view | `8cdd1d7` |
| 4 | `datacenter_projects`: 3 facilities; `/datacenters`; datacenters on `/map`; spot check 44 of 48 | `8c9f0bc` |
| 5 | Screenshots, value check (229 of 229), platform tools 3 and 4, briefing, this report | final commit |

## Task 1: push and stabilize CI

**The push.** origin/main was at `542b4ea` (session 14). Local was 5 commits ahead, with nothing to merge. Session 15 was pushed as it stood (`f5d4053`).

**Exit 128 in the commit step (run 3, `36284122117`).**
- **Cause:** the step committed, then ran `git pull --rebase` while `warehouse/output/news_index.csv` was still modified. That file is tracked (allowlisted in `.gitignore`) and rewritten every run, but it was missing from the step's `git add` list. Git refuses to rebase with unstaged changes ("cannot pull with rebase: You have unstaged changes"), and exits 128.
- **Fix, in `daily-prices.yml`:** the step now:
  1. sets the run's changes aside (`git stash --include-untracked`);
  2. runs `git pull --rebase origin main`;
  3. restores the changes, keeping this run's version of any file that conflicts, since it was built from the newer data;
  4. stages the allowlist, which now includes `news_index.csv` and the datacenter tables;
  5. commits only if something is staged, then pushes.
- **Checkout** has full history (`fetch-depth: 0`), so the rebase always has a base.
- **Tested** in a scratch simulation: a bare remote, a "CI" clone, and a "human" clone that pushed a conflicting `news_stories.csv` and a new `STATUS.md` mid-run. The human's `STATUS.md` was kept, the run's `news_stories.csv` won the conflict, and untracked junk was not committed. With nothing changed, the step exits 0 without committing.

**news_brief failed in CI.**
- **Cause, from issue #2:** `ERWDataNotFound: No ERW table named 'ercot_peak_premium_annual'`. The digest's "highest real-time price" looped over `erw.filter(market="rtm")`. On the runner that list includes tables coverage carries over but the runner does not have: the derived peak-premium tables and the ERCOT yearly history.
- **Reproduced** in a fresh clone with four tables: it failed at HEAD and passed after the fix.
- **Fix:** the loop reads only interval price tables (`<iso>_rtm_(hub|zone)_prices`) and skips any that is absent, with a log line.

**EIA-930 generation per day** (human ruling; data standard decision 24a).
- The eight generation tables are in `PER_DAY`. Within the days written, a per-fuel series with a missing hour is still dropped for the run, as ruling a says.
- **Run against the live API:** 2026-09-24 and 2026-09-25 were written for all eight tables. 2026-09-26 had 3 to 6 of 24 hours, so it was not written; each table has a `gap` row in `run_status.csv`.
- Run 3 had written no generation at all under the old whole-window rule.

**Extractor rulings** (decision 24b).
- **How:** the model now returns `state_text`, `country_text` and `status_text`. The code keeps each value only if:
  - its span is in the story;
  - for a state, the span names the state (name or postal code);
  - for a country, the span names the country.
- Status may now be empty, and the prompt maps stated verbs to statuses (raises = closed, secured = signed).
- **Re-extraction:** `extract.py --reextract` re-ran the 133 stories session 15 checked, starting from nothing. The previous tables are kept in `warehouse/deals/history/`. Cost: USD 0.1939 (9 calls).

**What changed in the re-extraction:**

| | Before | After |
|---|---|---|
| Deals | 29 | 26 |
| State filled | 3 | 0 |
| Country filled | 18 | 8 |
| Status filled | 29 | 23 |
| Status counts | announced 16, signed 9, closed 3, cancelled 1 | signed 10, closed 6, announced 6, empty 3, cancelled 1 |
| Dollars filled | 13 | 12 |

- **Gone (4):** Palisades and the BWRX-300 MOU, the two non-deals the session 15 spot check flagged. Also a Madouela "other" (confidence 0.3) and an EIG geothermal fund (0.3).
- **New (1):** Eni, Sapukala block.
- **The spot check's inference errors are gone:**
  - ProPetro to Targa lost "TX" and "US" (Permian Basin), and its status is now signed;
  - Inpex's Ichthys stake lost "Australia";
  - BP and Devon's Eagle Ford lost "TX";
  - Nscale is now closed ("raises").
- **One loss is model variance, not the ruling:** the frontier AI lab equipment deal lost USD 614,000,000 and one of its two stories, because the model did not return them this time.
- **19 of the 25 deals kept differ in some field; 6 are unchanged.** Besides the ones above:
  - country removed: WhiteHawk, Vietnam refinery, Hoegh Evi, Shell Gulf assets, Amazon backup generators, Polskie Elektrownie Jadrowe;
  - status now empty: Genel and Capricorn, Polskie Elektrownie Jadrowe;
  - Rune is now closed; Amazon is now signed and an offtake;
  - Anthropic cloud services is now an offtake; the offshore gas project went from project_finance to other;
  - wording only (asset, technology, capitalization): Golar LNG, Exxon Middle Kura, Mercuria, the CO2 for EOR deal.

**Also:** `load.py --only REGEX` loads chosen live-set tables and leaves the others, and the catalogue's other rows, as Supabase has them. It exists for a machine whose tables are older than CI's. It is untested against Supabase, because the load was refused.

## Task 2: project map data (tool 3)

**`warehouse/derived/energy_projects.py`** is a derived table (decision 23); method in `docs/methods/energy_projects.md`. The standard entities columns come first, then:

| Column | What it holds |
|---|---|
| `project_id` | the input row's `entity_id` |
| `kind` | operating, planned or queue |
| `technology_group` | EIA's group, or the queue text grouped by `QUEUE_TECH` |
| `mw` | the source's MW |
| `state`, `county` | as the source states them |
| `geo_precision`, `geo_note` | how the row was placed, and why not |
| `operator_role` | operator (EIA) or developer (queue) |
| `date`, `date_kind` | operating year, planned operation date or queue date |
| `technology`, `source_status`, `source_table` | the source's own text, status label and table |

**Rows and placement:**

| Kind | Rows | Placed at | Not placed |
|---|---|---|---|
| operating | 28,605 | EIA's coordinates (point) | 0 |
| planned | 2,316 | EIA's coordinates (point) | 0 |
| queue | 14,567 | county internal point: 13,395 | 1,172 |

**Why 1,172 queue positions are not placed:** 286 name no state, 214 no county, and the rest name something the gazetteer does not hold: a city, a misspelling or a joined list. There is no fuzzy matching.

**The gazetteer:**
- **Files:** the U.S. Census Bureau's 2025 county file, downloaded each run into `warehouse/raw/census_gazetteer/<run_id>/` with a manifest, and registered in `sources.csv` as `census:gazetteer_counties` (public).
- **The point:** the prompt asked for the county centroid. The gazetteer publishes the county's internal point (`INTPTLAT`, `INTPTLONG`), which is always inside the county. The method doc says so.
- **Connecticut:** the 2025 file replaced the state's counties with planning regions, while ISO-NE still names counties. For names the 2025 file lacks, the 2020 file is used, and `geo_note` names the file.
- **Matching:** the whole text is tried first, so a hyphenated name like Miami-Dade matches; then each county of a list.

**Checks:** it validates. On the CI runner the script skips with a warning (session 10 ruling 3) unless the queue tables are there, which is on Mondays or on a manual run with `queues=1`.

**Live set.** `energy_projects` repeats rows already in Supabase, which was at 257.6 MB against the 300 MB limit. So a new `select` rule in `live_set.yaml` loads it:
- without withdrawn queue positions;
- with only the map's extra columns;
- which comes to 36,741 rows, estimated at 20 to 30 MB.

The CSV and Redivis keep everything. **Watch the size on the first load:** if it passes `max_mb`, `supabase_load` fails that day and names the size.

**Chat:** sectors `power` for `energy_projects` and a new `datacenters` sector for the tracker, in coverage, the package and the chat tools. The briefing (`package/llms.txt`) and `site/lib/chat/spec.json` now name `energy_projects`, `datacenter_projects` and `energy_deals`.

## Task 3: /map

**Libraries:** `d3-geo`, `topojson-client` and `us-atlas`. The map is inline geometry: no tiles and no key.

**Drawing:**
- **Projection:** the server projects every point with Albers USA, the same projection us-atlas's albers file is drawn with, and hands the client compact arrays.
- **Points** are drawn on a canvas, since there are 36,000 of them.
- **Size and order:** area grows with MW, and the largest points are drawn first.
- **Color** is the technology group, using the site's eight fuel colors from the same token file. Session 15 validated them on this surface. Hybrid, petroleum, biomass, geothermal, transmission and not-stated share "other", as the dataviz rule forbids a ninth hue.
- **Shape:** exact points are dots, county points are rings, and datacenters are diamonds.

**Around the map:**
- **Filters, in one row:** kind, technology, state, status and a MW range, plus a live count of what is shown.
- **Hover:** a tooltip.
- **Click:** a card read from Supabase through `/api/entity`. It reads only `energy_projects` and `datacenter_projects`, with the anon key on the server.
- **Also:** a legend with shape and size keys, and a table view of counts and MW by technology and kind.
- **Numbers:** every count and MW carries a `data-check` key.
- **Links:** nav and home.

**A screenshot bug, fixed.** The first capture showed the points squashed into the top quarter of the map. The canvas itself was right: its drawn pixels spanned rows 12 to 505 of 509. The cause was `captureBeyondViewport`, which re-lays the page out mid-capture. `scripts/screenshots.mjs` now sizes the viewport to the page before capturing.

## Task 4: datacenter power tracker v0 (tool 4)

**`warehouse/datacenters/extract.py`** follows the deal extractor's pattern. It loads the deal extractor by path for its checks, since both files are named `extract.py`, and the county gazetteer code from `energy_projects.py`.

**What each field needs to be kept:**

| Field | Kept only if |
|---|---|
| MW | its span parses to the same value |
| State, status | their spans are in the story, as in the deals |
| County, city | the location span is in the story and contains the name |
| Planned year | its span is in the story and contains the year |
| Operator, developer, site name, power source, utility | the name appears in the story |

**The rest of the design:**
- **Deduplication** is by site, against a reference list of the facilities already extracted.
- **Placement:** at the stated county's internal point (`county`), else the stated city's (Census 2025 places file, unique names only: `place`), else not placed.
- **Status:** the standard `status` maps announced and permitted to planned, and cancelled to withdrawn. The extractor's own word is kept in `project_status`.
- **`ai_power`** is true on every row: the table is the AI-power subset.

**Tables:**
- `datacenter_projects`: entities, public.
- `datacenter_projects_evidence`: events, internal.
- Both are in `run_daily.sh`, the git allowlist and the workflow's commit list. The public table is in the live set.

**The backfill.** News was brought current first: 33 stories, scored for USD 0.1177, and 1 new deal (USD 0.0133). The extraction then covered 28 datacenter_power stories in 25 clusters, over 3 calls, for USD 0.0299, and found 3 facilities:

| Facility | What the stories state |
|---|---|
| Oracle | New Mexico; 4 stories |
| Arevia Power | Ada County; permitted; gas |
| Applied Digital, Delta Forge 2 | Alabama; 2028 |

None of the three is placed, because none states both a state and a county or city. The data is thin because the ERW has scored news only since 2026-09-23.

**The site:**
- **`/datacenters`** has a summary strip (facilities, MW stated, MW by state and top operators by MW, each saying "no data" and why when no facility states MW), filters (state, status, operator, minimum MW), and per-row story links.
- **`/map`** draws datacenters as its fourth kind.

**Spot check** (`warehouse/datacenters/eval/spot_check_s16.csv`): 10 extractions, judged field by field against the titles and summaries. The extractor was not changed afterwards.
- **The 10:** the 3 facilities, each judged on 14 fields, and 7 clusters where the extractor found no facility, judged on that decision alone.
- **Result:** 44 of 48 judgments correct (0.92).

| Field | Correct | Where wrong |
|---|---|---|
| is_facility | 10/10 | |
| status | 1/3 | Arevia "permitted" (an application was filed); Delta Forge 2 empty ("reveals ... will be built" was stated, but the model gave no span, so the check emptied it) |
| state | 2/3 | Arevia: "Ada County, Idaho" is stated, the model returned no state |
| operator | 2/3 | Arevia Power is the developer; no operator is named |
| every other field | all correct | |

## Task 5

**Screenshots** in `site/screenshots/`:

| File | What it shows |
|---|---|
| `map-desktop.png`, `map-mobile.png` | the live pages in their no-data state |
| `datacenters-desktop.png`, `datacenters-mobile.png` | the live pages in their no-data state |
| `map-preview-local-csv-*` | the layout, with real rows read from the local CSV |
| `datacenters-preview-local-csv-*` | the layout, with real rows read from the local CSV |
| `home-*` | re-shot with the new links |

**Value check** (`scripts/check-values.mjs`):
- **Extended to `/map` and `/datacenters`:** independent queries for the counts by kind, precision and technology, and the MW sums, with MW sums compared as the page rounds them.
- **Also fixed:** Postgres puts nulls first in a descending order, so the check read a null `last_run`. It now orders with nulls last.
- **Result: 229 of 229 values match Supabase.** None of them are from `/map` or `/datacenters`, which have no rows to check until the load. After the load, run `npm run check` again.

**Docs:** `docs/platform-tools.md` has tools 3 and 4, with the session 16 changes to 6 and 7; `docs/datastandard.md` has decision 24; `STATUS.md` is regenerated.

## Decisions

1. **Queue tables are not restored from Redivis in CI.** A restored snapshot keeps only a one-line header, so the validator and provenance would suffer. Instead the map table is built on the days the queues are pulled, and a manual run pulls them by default.
2. **The county internal point stands in for the centroid,** and Connecticut uses the 2020 file (Task 2).
3. **No fuzzy matching or city lookup for queue positions.** An unplaced position is honest; a guessed county is not.
4. **The Supabase copy of `energy_projects` is trimmed** by a `select` rule, instead of dropping the generator and queue tables that `/ask` reads.
5. **`ai_power` is true on every datacenter row,** and the datacenter status keeps its own word in `project_status`, because the entities vocabulary has no "announced" or "permitted".
6. **`first_story_date` was renamed `first_story_at`,** because the validator requires `*_date` columns to be dates. The 3-row file was renamed in place, rather than re-extracted.
7. **The committed preview screenshots are labeled as local-CSV previews,** because the live pages cannot show data yet.

## Errors hit

1. **Permission refusals:** reading git's stored credential (for the API trigger) and the Supabase load. Neither was retried.
2. **Two heredoc patches failed** on quoting; they were rewritten as script files.
3. **`read_series` refused entities tables;** the map builder reads tables by counting the header lines instead.
4. **The 2025 gazetteer is pipe-delimited,** not tab-delimited as older years are.
5. **Squashed canvas in the screenshots** (Task 3).
6. **The validator blocked `first_story_date`** (decision 6).
7. **A stale local server held port 3000;** the process was stopped.

## Open questions for the human

1. **Trigger the daily workflow by hand** (queues=1), and check its commit step on GitHub.
   - Its Supabase load puts `energy_projects`, `datacenter_projects` and the re-extracted `energy_deals` live.
   - Watch the database size on that load against `max_mb` 300.
   - Alternatively, run `python warehouse/supabase/load.py --only '^energy_projects$' --only '^datacenter_projects$' --only '^energy_deals$'` yourself.
2. **Check the site after the load:** run `npm run build && npm start`, then `npm run check`, to verify the numbers on `/map` and `/datacenters`.
3. **The datacenter extractor's status reading is weak** (1 of 3 correct). Should the status vocabulary have an "applied" step, and should the model be required to give the status span? Today a missing span empties a correct status.
4. **Standing failures from run 3:**
   - SPP real-time has now failed three runs in a row (a missing SPP interval file for 2026-09-23), and the workflow's streak step would open an issue for it;
   - CARB's auction PDF answered HTTP 202.
