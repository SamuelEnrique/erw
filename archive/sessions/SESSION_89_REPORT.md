# Session 89 report: the findings brief, and the MISO pause

**Two things are in this report: the findings brief (session 89), and your closing ruling, the pause of every MISO pull.** Both are on the branch `wip/089-findings`. **Neither is on main and nothing was deployed.** The MISO pause is therefore **not live yet**: the 15-minute run reads MISO every quarter of an hour and the daily run reads it at 14:00 UTC until you land the branch. The commands are first.

## To make the MISO pause live

```bash
# One push lands everything on this branch: the MISO pause, the findings brief and its test, and the reports of
# sessions 87, 88 and 89. A merge to main deploys the site, so the snapshots go around it (CLAUDE.md, rule 8).

git fetch origin
git checkout wip/089-findings
git merge origin/main                       # main moves at 14:00 UTC with the daily run's commit; merge it first
# Only if that merge reports a conflict in warehouse/metadata/sources.csv (the daily run rewrites the dates of the
# MISO rows this branch annotated): take main's file, put the pause note back on the twelve rows, and conclude.
git checkout origin/main -- warehouse/metadata/sources.csv
python -c "import sys; sys.path.insert(0, 'warehouse/connectors'); import iso_prices as ip; ip.update_sources([])"
git add warehouse/metadata/sources.csv && git commit --no-edit
python -m unittest tests.test_session89_miso_pause            # 14 tests; read its exit code

cd site && node scripts/snapshot-live.mjs take before-089 && cd ..

git push origin wip/089-findings:task/089-findings
# the workflow runs the tests and the site's checks, merges the branch into main, and Vercel deploys. When both are done:

cd site && node scripts/snapshot-live.mjs take after-089
node scripts/snapshot-live.mjs compare before-089 after-089
```

What that does and does not do:

- **From the merge on, no scheduled run requests MISO.** The 15-minute run and the daily run both run from main. Nothing else has to be run by hand, and no table has to be loaded.
- **To stop it before today's daily run, land it before 14:00 UTC.** I did not land it: you said a wip branch and no deploy.
- **Expect the home page's battery tile to read "not held" for up to 15 minutes after the deploy.** It did after each of the last two deploys tonight (sessions 87 and 88) and came back by itself both times. If it does, take the after-snapshot again a quarter of an hour later.
- **Expect the first visible effect on the home page within the hour, and it is meant:** the MISO card's "real time, interval starting ..." line stops advancing. See "What a visitor will see" below.
- **To lift the pause later:** delete MISO's row from `warehouse/metadata/paused_sources.csv`, put `miso` back in the `ISOS` list of `warehouse/run_daily.sh`, and move the MISO newsroom entry of `warehouse/news/feeds.yaml` from `paused_feeds` up into `feeds`.

**Read these three first:**

1. **The pause is one list that every MISO pull asks, not seven separate edits.** `warehouse/metadata/paused_sources.csv` holds MISO's row: the date, the reason, the sentence of its terms, who ruled, and what it waits for. Every connector that reaches MISO's servers asks that list first and makes no request while the row is there. Tests replace every way of making a request with a failure and run each MISO path: none is reached.
2. **Nothing of MISO's was deleted or rewritten.** Every table, every row, every page and every connector is as it was. The registry's twelve MISO rows gained a note in their `report` column and nothing else in the registry changed.
3. **The findings brief is written and every number in it is checked against the tables.** Session 89 itself was not merged to main either, for a reason of its own: the last two deploys each blanked a tile of the home page for a quarter of an hour.

Energy Research Warehouse (ERW), session 89, last of the night, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from about 05:05 to 05:50 UTC, unattended until your message at about 05:30. **Model spend: USD 0.00.** No pull, no table written, no model call, no force push. No request was made to MISO in this session. No instruction arrived for session 84: the night ran 82, 83, 85, 86, 87, 88 and 89. The data lock was not taken in this session and is free.

## The MISO pause

### The ruling, and why

Your ruling of 4 October 2026: pause all MISO pulls; take every MISO connector out of the daily run and the 15-minute run; do not run the new reserve connector again; keep every MISO table and page exactly as it is; record the pause in the source registry and the method notes.

The reason is the sentence session 85 found in MISO's terms (`https://www.misoenergy.org/meet-miso/legal-and-privacy/`): "You agree not use any automated means, including, without limitation, agents, robots, scripts, or spiders, to access, monitor, or copy any part of this Website or the App." The pause stands pending a review of those terms by a person.

### What reached MISO, and what each does now

| Pull | Where it ran | Now |
|---|---|---|
| Hub prices, day-ahead and real-time (`iso_prices.py miso`) | the daily run | `miso` is out of the daily run's list; the connector itself refuses, so `ISOS=miso` would request nothing either |
| The latest real-time price (`latest_prices.py`) | the 15-minute run | MISO is skipped; the other five grids are read as before. MISO's last row in `latest_prices` stays |
| The interconnection queue (`iso_queues.py`) | the daily run, Mondays | skipped; the queue table stays |
| Planning Resource Auction results (`iso_capacity_prices.py`) | the daily run, the first of the month | skipped; MISO's rows in the capacity table are kept by the merge writer, and the table's header says the market is paused |
| Day-ahead reserve prices (`miso_as_prices.py`, session 85) | by hand | refuses to run. I ran it once more to see: it prints the pause and exits, no request |
| Hub price history (`hub_history.py`) | by hand | refuses MISO |
| The MISO newsroom feed (`feeds.yaml`) | the daily news ingest | moved out of the list the ingest reads and kept in the file under `paused_feeds`. A story of a MISO outlet that arrives through another search is not opened on MISO's site: resolving a link opens the page |

**Not paused, because they are not MISO's servers:** EIA's figures for the MISO balancing authority (EIA-930, EIA-860M), NOAA's weather stations, Berkeley Lab's queue data.

### What a visitor will see once it is live

Nothing is removed, so what a visitor sees is MISO's figures no longer moving.

- **The home page's MISO card keeps its last real-time price and the time of that interval, which ages.** Its seven-day line shortens by a day each day, and about a week after the last pull it becomes the card's "no data" line, because no MISO price of the last seven days is held. That is the one change on a live page, it is gradual, and it follows from the ruling. If you want the card to say "paused" instead of ageing into "no data", that is a small change to the home page and yours to ask for.
- Pages in review that show MISO's hub prices stop at the last day pulled; the tables derived from them gain no new MISO days.
- The queue map keeps MISO's queue as of its last weekly pull. The digest no longer carries MISO's newsroom feed.

### The record

- **The source registry** (`warehouse/metadata/sources.csv`): the six `miso:` reports and the six MISO news outlets, twelve rows, each carry in `report`: "[PAUSED 2026-10-04: MISO's terms forbid automated access; pulls paused pending a review of MISO's terms by a person (docs/methods/miso_pause.md)]". The registry's writer adds the note to any MISO row whoever writes the file, so a later run cannot drop it.
- **The method notes:** `docs/methods/miso_pause.md` is the note of record (the terms, what is paused, what is not, what a reader sees, how to lift it). A short paragraph at the top of each note that describes a MISO pull points to it: capacity and ancillary, price board, cost of power, trader view, energy projects, and `docs/price-sources.md`.
- **`CLAUDE.md`:** one line under the conventions, so that every later session knows a paused publisher is never requested.
- **The connector** `miso_as_prices.py` says in its own header that it is paused and why.

### Its tests

`tests/test_session89_miso_pause.py`, 14 tests, all pass: the list holds MISO with the terms quoted; the daily run's list has no MISO and the reserve connector is in no run; with every request replaced by a failure, the daily price connector, the queue, the capacity and the reserve connectors make no request for MISO and report the pause, and the 15-minute run calls the readers of the other grids and never MISO's; another grid's connector is not paused; no feed the ingest reads searches MISO's site; the registry's MISO rows carry the note and no other row does; the note survives a second write of the registry; nothing of MISO's was deleted.

Two older tests used MISO as a stand-in and were adjusted without changing what they test: session 65's "a failed market writes none of its rows" now fails ISO-NE instead of MISO, and session 85's test of the shared loop uses a made-up namespace.

## The findings brief

`docs/briefs/findings_2026-10-04.md`: the ten strongest findings in the warehouse on storage, duration, the evening shoulder, battery revenue, California's imports and the December 2025 data break. Each is one sentence, its number, its table and check key, and one caveat.

| | Subject | The finding | The number |
|---|---|---|---|
| 1 | Storage | The US battery fleet grew by 48 percent in twelve months | 54,489 MW in August 2026, 17,689 more than a year before |
| 2 | Duration | California builds four-hour batteries and Texas builds batteries of under two hours | 3.46 hours against 1.65 |
| 3 | Duration | Almost no battery in the country runs six hours or more | 129 MW of 54,489 |
| 4 | The evening shoulder | On the average evening Texas's shoulder asks about twice the hours its batteries hold | 3.17 hours needed, 1.65 held |
| 5 | The evening shoulder | On Texas's ten hardest evenings it asks four times | 6.58 hours on average, 8.61 at the worst |
| 6 | The evening shoulder | In California the batteries now match the average evening | 3.59 hours needed, 3.46 held |
| 7 | Battery revenue | A four-hour battery in Texas did not cover its debt on the last twelve months' prices | USD 81.40 per kW; coverage 0.88 times |
| 8 | Battery revenue | One month is more than half of everything that battery would have earned in Texas since 2018 | February 2021: 57 percent |
| 9 | California's imports | They swing with the season | 28.5 percent of demand in January 2026, 8.3 in August |
| 10 | The December 2025 data break | EIA's own figures for California no longer add up | Two measures of imports that agreed within a point differ by twelve in January 2026 |

The caveats that matter most: finding 4's measure is the generous one (a narrower measure of the same evenings asks 1.01 hours, and the brief gives that row beside it); findings 7 and 8 are the model's upper bound; finding 10's gap is a reporting change, not missing power.

**No finding without a row behind it.** The brief gives 34 check keys (32 different rows; two are cited twice). `tests/test_session89.py` reads every key and its stated value from the brief: for a `series|` key it finds the row in the table and compares; for a `bs|` key it runs the battery page's own code over the table's rows and compares. It also checks that every figure in a finding's "Number" line is the rounding of a value one of its keys gives, so no number is stated that a key does not carry. On this machine all the tables are held and all 34 match.

That check caught me once: I had written Texas's 18,204.5 MW as "18,205" and the test, rounding as Python does, said 18,204. A reader rounds a half up, and so does the site, so the test now rounds half up; the brief was right.

**Held back, and named at the foot of the brief with the reason:** the battery model on New York and SPP (every duration rule assumed, most of the result regulation); who owns the batteries (a reporting company is often a project company); the size of the correction to the seller tab's California solar (it is in session 82's report, not in a table). **Looked at and not used:** planned storage (64,458 MW; "planned" in EIA's inventory runs from approvals pending to under construction), California's carbon intensity after the join (three monthly rows so far), and battery revenue in California (held from September 2024 only).

**Why it is not on main.** Sessions 87 and 88 each deployed, and each deploy left the home page's battery tile reading "not held" for about a quarter of an hour (their reports). A merge to main redeploys the site whatever it changes. The brief is documents only, so I did not spend a third deploy on it. Your rule since then says the same: a live number moved unexpectedly, so no more deploys.

## Tests and checks

| Check | Result |
|---|---|
| `tests/test_session89.py` | 6 tests pass: the brief's form, its six subjects, every figure of a number line is one of its keys, each of the 28 `series|` keys is a row with that value, each of the 6 `bs|` keys is the page's own statistic |
| `tests/test_session89_miso_pause.py` | 14 tests pass (above) |
| The whole suite, here, on the final branch | 565 tests; one failure, old and known since session 82 (`test_session49`: `eia930_all_interchange` holds 151,632 rows against a ceiling of 150,000 on data machines; it skips on the runner) |
| `warehouse/run_daily.sh` | parses (`bash -n`, exit 0); its default list is ercot, caiso, nyiso, spp, isone |
| The runner | not run: the branch was not pushed to a task branch, by your instruction |
| The confirming snapshot of the home page | taken at 05:40 UTC for session 88's report: the battery tile reads 81.40 again; 4,098 checked numbers, as before that deploy |

## Errors and decisions

- **Decision: the pause and the brief are on one branch.** One push lands both, with the last three reports. If you want the pause without the brief, the pause is one commit (`ebcfe63`) and can be picked alone.
- **Decision: the registry's schema is unchanged.** The pause is a note in the existing `report` column, not a new column: the registry is loaded into Supabase and Redivis column for column, and a new column would have needed a migration and failed the next load without one.
- **Decision: the MISO newsroom feed is paused too.** It reads Google News, not MISO; but the ingest resolves each story's link, which opens the story on MISO's own site. That is a script reading MISO's website.
- **Decision: EIA's MISO figures are not paused.** They are EIA's files on EIA's servers.
- **`warehouse/news/ingest.py` holds one em dash**, in a pattern that strips them from headlines. It was there before; I added none. My edit script refused the file for it and I applied that one change separately, checking the count was the same before and after.
- **Two older tests failed on the pause** and were adjusted (above).

## For Samuel

The night, in one place. Sessions 82, 83, 85, 86, 87, 88 and 89 are done; 84 never arrived. On main and deployed: 82, 83, 85, 86, 87, 88. On `wip/089-findings`, not deployed: the findings brief, the MISO pause, and the reports of 87, 88 and 89. Five deploys after session 82's own three, each with its snapshots; no number changed in any; one tile of the home page was absent for about a quarter of an hour after each of the last two, and I stopped deploying.

What I would do first, in this order:

1. **Land the MISO pause** (the commands at the top), before 14:00 UTC if you want today's daily run to leave MISO alone.
2. **Fix the home tile on deploy** (session 87's report). What I measured: the tile's read takes 1.8 seconds on a cold database and 0.2 warm, with the public key, from this machine; the public key's limit is 3 seconds; the site's build asks for every page's rows at once.
3. **Set the Vercel token**: every page in review, including tonight's three new ones, waits behind it on production.
4. **The review of MISO's terms.** Two questions for it: may the ERW read the market report files at all, and may it republish them. The second also decides whether `miso_as_prices` and MISO's capacity prices stay internal.
