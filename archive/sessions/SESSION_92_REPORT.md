# Session 92 report: Ask ERCOT, the reference version

**Built, on `wip/092-ask-ercot`, nothing deployed.** Ask developed fully for one grid. On the 44 ERCOT evaluation questions the reference version answers **44 of 44**; the chat as it was answers **17 of the 28** it was asked (61 percent). **Model spend: USD 4.82 of the USD 5.00 cap**, for testing only (USD 4.7632 in the cost ledger, and USD 0.0532 for one question through the site's own route).

## To make it live

```bash
# Nothing below was run. No preview address: GitHub recorded no Vercel deployment for this branch's push (your note says
# Vercel's deployment storage is full).

# 1. THE PAGE, in review. A push to a task branch redeploys the site, so the snapshots go around it. The live pages
#    do not change for a visitor: the link "Ask ERCOT about this view" is drawn only in the internal view while
#    /ask/ercot is in review (a browser check proves a visitor's battery page holds no trace of it).
git fetch origin && git checkout wip/092-ask-ercot && git merge origin/main
python -m unittest tests.test_session92                                    # read its exit code
cd site && node scripts/snapshot-live.mjs take before-092 && cd ..
git push origin wip/092-ask-ercot:task/092-ask-ercot
cd site && node scripts/snapshot-live.mjs take after-092 && node scripts/snapshot-live.mjs compare before-092 after-092

# 2. TO OPEN IT TO VISITORS, after you have used it: site/lib/release.ts,  "/ask/ercot": "live".  The link then shows
#    on the ERCOT views for everyone. Before that, decide 3.

# 3. THE SITE'S DATABASE DOES NOT HOLD EVERY ERCOT TABLE. The reference version was evaluated on this machine's
#    files, where all 26 tables are. The site reads the Supabase live set, which lacks five of them:
#      ercot_all_hub_prices_history  3,063,570 rows   hub prices 2015 to August 2026
#      ercot_as_prices                 336,092 rows   reserve prices since 2018
#      lbnl_interconnection_queue       38,201 rows   (3,757 of ERCOT)
#      storage_owners_monthly            9,540 rows   (held out of the live catalogue during the freeze)
#      merchant_revenue_monthly          8,335 rows
#    and ferc_eqr_contracts is internal, which the site's public key cannot read. Asked for one of these on the site,
#    the chat says the table is not in the site's live set. The two price tables are the ones that matter and the
#    large ones: about 3.4 million rows into a database of 508 MB. Your call. To load them whole:
#      warehouse/supabase/live_set.yaml: add '^ercot_all_hub_prices_history$' and '^ercot_as_prices$' under full
python warehouse/lock.py run --task "ask ercot tables" -- python warehouse/supabase/load.py --only '^(ercot_all_hub_prices_history|ercot_as_prices|lbnl_interconnection_queue|merchant_revenue_monthly)$'
#    A lighter way I would look at first: a daily summary of the hub prices (mean, minimum, maximum per hub, market and
#    day: about 51,000 rows) answers most price questions; it is a derived table to build.

# 4. THE COST LEDGER. The evaluation wrote 558 rows to warehouse/output/api_cost_ledger.csv on this machine. They are
#    not in coverage, the archive or the Redivis draft yet: that is a data commit to main, which this session could
#    not make. With the next one:
python warehouse/validate/erw_validate.py warehouse/output/api_cost_ledger.csv
python warehouse/metadata/build_coverage.py
python warehouse/lock.py run --task "ledger" -- python warehouse/archive/archive.py write api_cost_ledger
```

**Read these four first:**

1. **The comparison is fair to the old chat, and I made it fairer twice.** The old chat (`/ask?grid=ercot`) reads 20 tables. Where it gave the right number from another table that really holds it (the fleet's MW from the unit list, a year's mean price from the price board, Uri's highest price from the peak premium table), the set now accepts that table, and it is scored right. It was asked 28 of the 44 questions, not all: it costs USD 0.083 a question against the new one's USD 0.028, and the cap could not carry both arms whole. The 16 it was not asked each need a table outside its scope; they are listed, and counted neither way.
2. **The first whole run of the reference version scored 41 of 44, and it showed three faults, all fixed and all tested.** Half its answers (21) were sent back once by the number check for a number that was no claim at all: "15-minute", "4-hour", "EIA-860M", the days of a month. Two were refused for it. And one answer was wrong by a month: a monthly table grouped by year in Chicago time put each January in the year before. After the fixes: 44 of 44, 3 sent back. The third fault is in the general chat too, where I did not touch it ("For Samuel", 2).
3. **A chart never shows a number the model wrote.** Every query result carries an id; the answer names the results it rests on; the page draws the rows of those results as the tool returned them, with their table and source report. If the model names a result that no tool returned, the answer is sent back. A test runs the same tool results through the Python and the TypeScript versions and compares what they return.
4. **The general Ask page and the other grids' Ask pages are as they were.** The loop gained hooks whose defaults are the old behaviour; the specification exported for the site is byte for byte the committed one, and a test holds it there. `/ask?grid=ercot` still works as before too; when you approve the new page, pointing it at `/ask/ercot` is one line.

Energy Research Warehouse (ERW), session 92, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from 07:05 to about 08:05 UTC, unattended. No pull, no table built, no force push, no deploy. The data lock was held five times, for the evaluation runs (each model call writes the cost ledger), about 35 minutes in all, and released each time; it is free. Model: `claude-sonnet-5-5`, the newest Sonnet-class model in the API's list, as the existing chat chooses it.

## What Ask ERCOT is

| Asked | Built |
|---|---|
| Knows every ERCOT table | 26 tables, each read for ERCOT's rows only: hub prices (the history from 2015 and the newest weeks), reserve prices since 2018 and the reserve plan, hourly demand and generation by fuel (the newest weeks) and monthly demand since 2019, battery output and the fleet's daily cycle, `battery_stack_monthly` and its stress days, `storage_buildout_monthly`, `storage_owners_monthly`, the battery units, `shoulder_hours_monthly`, the events and their studies, `lbnl_interconnection_queue` and ERCOT's own queue, cost of power, merchant revenue, carbon intensity, the peak premium tables, and ERCOT's rows of `ferc_eqr_contracts` as internal. A guide in the system prompt gives each table's entities, variables, units and traps, so the model goes straight to a query: 3.3 tool calls a question, where the old chat used 6.7 |
| An answer that rests on a series returns a chart and a small table of the rows it fetched, each with its source | Yes: `record["series"]`, the rows of the query results the answer names. The page draws a line chart for values over time and a table for both kinds, each row with its table, and the source report beneath. If the model fetched a series and named none, the last one from a table it cites is shown and marked as chosen by default |
| Proposes two or three follow-up questions | Yes, on every answer, checked: two or three, each a question, no digit but a year unless a tool returned it. On the page they are buttons that ask themselves |
| Every ERCOT view can open it with that view's period and settings | Eight views carry the link: what a battery earns (duration, strategy, size), what a generator earns (asset, size), the shoulder hours (month), the storage build-out (measure, inventory month), who owns the batteries, the ERCOT grid page, the peak premium explorer, Winter Storm Uri (its dates). The settings go into the first message as the question's defaults, and the answer says which it used |
| Never states a number it did not fetch; says so when the warehouse does not hold the answer | The loop's own check, unchanged: every number in the answer must be in a tool result, the question, the context or a name it queried by; one retry; then refusal. 5 of 5 questions the tables cannot answer were answered "not in the warehouse", with what is missing and the nearest thing held |

**What it will not do, by design:** compute across two tables (the history ends 26 August 2026 and the newest weeks begin there: a mean over a month that spans both is two means, not one); rank the groups of a result (it can find the largest owner, not the fifth); speak for another grid.

## The evaluation

`warehouse/chat/eval/questions_ercot.yaml`: 44 questions, built by `ercot_expected.py`, which computes every expected number from the files with pandas and never through the tools. 22 lookups, 6 that need a series, 8 that join two tables, 5 the tables cannot answer, 3 that depend on the view the reader came from. Fixed date 2026-10-04. I built 57 and kept 44: the cap, again.

| | Before: the chat as it was | After: the reference version |
|---|---|---|
| Correct, of the questions asked | **17 of 28 (61%)** | **44 of 44 (100%)** |
| On the 28 both were asked | 17 | 28 |
| Lookups | 9 of 11 | 22 of 22 |
| Series | 2 of 4 | 6 of 6 |
| Joins of two tables | 1 of 5 | 8 of 8 |
| Not in the warehouse | 5 of 5 | 5 of 5 |
| From a view's context | 0 of 3 (it cannot be told the view) | 3 of 3 |
| Follow-ups on every answer | not offered | 44 of 44 |
| A series where asked for one | not offered | 6 of 6 |
| Sent back once by the check | 6 of 28 | 3 of 44 |
| Tool calls, mean | 6.68 | 3.30 |
| Cost a question | USD 0.0832 | USD 0.0278 |

The first whole run of the reference version, before the three fixes: 41 of 44, 21 sent back, USD 1.0653. The full table by question is `warehouse/chat/eval/results/ercot_summary.md`.

**Why the old chat fails where it fails.** Ten of its eleven wrong answers are "not in the warehouse" for a table it cannot read (the price history, the battery model, the shoulder, the cost of power) or a question that depends on a view. One is a real error: asked for the queue's active stand-alone batteries by Berkeley Lab's count, it answered from ERCOT's own queue, a different list.

**The cost, to the cent the ledger holds:**

| | USD |
|---|---|
| The reference version: a pilot of 4, the first whole run, the second whole run | 2.4278 |
| The chat as it was: a pilot of 2, then 21 questions, then 6 more | 2.3355 |
| One question through the site's own route, against the live database | 0.0532 |
| **Total** | **4.8165** |

558 model calls in the ledger under session 92. The cap was enforced by `warehouse/llm.py` (`ERW_SPEND_CAP_USD`), not by my counting.

## The three faults the first run found

1. **The number check is literal, and the model was not told.** "A 4-hour battery", "the 15-minute price", "EIA-860M" and "over 31 days" are each a run of digits no tool returned. Three changes. The rules now say the check is literal and how to write around it (durations in words, dates only as a tool returned them, no inferred counts, a source named in words). The names a query asks by count as fetched: the variable `foresight_4h_revenue_total_usd_per_mw` makes "4-hour" a fetched fact, and "6-hour" still is not. And my own table guide no longer names a source by its form number, which is what primed the model to repeat it.
2. **Two refusals of honest answers.** One named the "15-minute" price. The other had found that September's demand lacks 48 hours and named the days, which no row carries. Both pass now; the second gives the peak with its hour and says in words that hours are missing.
3. **A monthly table grouped by year in a time zone lost its January.** Rows of a day or longer are dated 00:00 UTC of their local period; read in Chicago time, 1 January falls on 31 December. The answer was off (405.4 against 413.6 kgCO2/MWh for 2019). Under the profile such rows are now grouped by their own label whatever time zone is passed.

## On the site

- `/ask/ercot` (in review): the question box, the answer, the series (chart and rows), the sources, the follow-ups, and above the box the view it was opened from.
- `site/lib/chat/ercot.ts` is the profile in TypeScript; `site/lib/chat/spec_ercot.json` is exported from `ercot.py` (`--export-spec`), as the general chat's is from `ask.py`.
- The route `/api/ask` takes `{profile: "ercot", context}`; without them it runs exactly the code it ran.
- **One real answer through the route** (the site's own code, the live database): "How has the operating battery fleet grown year by year since 2020?", opened from the build-out page. Answered in 11 seconds with 3 queries: 218.4 MW at the end of 2020 to 13,909.3 at the end of 2025 and 18,204.5 in August 2026, "using the page's Power, MW setting"; a series of 7 rows of `storage_buildout_monthly`; three follow-ups. Those are the table's values.

## Tests and checks

| Check | Result |
|---|---|
| `tests/test_session92.py` | 28 tests pass, none calls a model: the loop runs against a stand-in whose replies are scripted, the tools run for real. Result ids; the series is the tool's rows with their source; a series is returned by default when the model names none; a result id no tool returned is sent back, then refused; follow-ups (count, a question, no unfetched number, a year allowed); the number check is still the loop's; "not in the warehouse" keeps its follow-ups; the context is in the first message and its numbers count; each table is read for ERCOT's rows only; a table outside the scope is refused; the three faults above; the general chat's spec, defaults and a grid chat's request are as they were; the set's kinds and that the tools give the expected numbers; the site's profile against the Python one on the same tool results; the context's round trip through an address and what is refused as a view; the page is in review and the link is kept to the internal view |
| `site/scripts/check-ask-ercot.mjs`, a real browser (Edge) | 23 checks pass: a visitor's battery page holds no link and no text of one; `/ask/ercot` answers a visitor the in-review page; each of the eight views carries the link with its view and settings; five views of another grid carry none; the chat opens with the view named; a question in the address fills the box and is not asked by itself; an answer (a recorded one, no model call) is drawn as a chart with its rows, table and source; the follow-ups ask themselves with the same context |
| `scripts/check-no-request.mjs` (the existing proof) | pass: 0 requests |
| The whole suite, here | 644 tests; one failure, old and known (`test_session49`). Two others in the first run were mine and are fixed: my test file switched the cost ledger off for the whole process, which failed session 30's ledger test |
| Site: types, build, route check | exit 0 each (the route check on the second try: its first run found `/prices` with 28 "no data" against production's 25; production showed 28 minutes later; the count ages with MISO's paused prices, and no code of mine is on that page) |
| On the runner | not run: no push to a task branch |

## Errors and decisions

- **Decision: a new page, not a change to `/ask?grid=ercot`.** You asked that the other pages work exactly as today; the surest way to keep that true for all of them was to leave the route they share untouched for them.
- **Decision: the model is the one the chat already picks** (the newest Sonnet-class model). A larger model would have doubled the cost of both arms against a cap that already could not carry them whole.
- **Decision: 44 questions and a partial "before" arm**, both for the cap, both stated above.
- **Decision: the link is invisible to visitors while the page is in review.** A gated link leaves greyed text behind, which on the battery page would have changed a live page.
- **Decision: no table loaded.** The site's version would be whole with the two price tables in the live set, but that is 3.4 million rows into the database a reviewer's site reads, in a freeze.
- **Error, mine:** my first version of the series held a field the site's version did not; the comparison test found it.
- **A network timeout** (the lock's check, 30 seconds) cut one "before" question; it was asked again and is counted by its second record.

## For Samuel

1. **The site's database** ("To make it live", 3). Until the price history is there, the page on production answers most of what the evaluation asks about batteries, storage, the shoulder, events and cost, and says "not in this site's live set" for prices before the newest weeks, reserves and Berkeley Lab's queue.
2. **The January fault is in the general chat too.** `warehouse/chat/tools.py` and `site/lib/chat/tools.ts` group a monthly table by year in the time zone asked. The fix is the profile's flag made the default (two lines in each); I left it because you asked for the other pages to work exactly as they do today, and this changes an answer.
3. **Rate limit and cost on production.** The page shares the route's 10 questions an hour per address. At USD 0.03 a question that is a few dollars a day at most from one address; there is no daily ceiling across addresses.

## To copy the pattern to CAISO next

1. **Copy `warehouse/chat/ercot.py` to `caiso.py`** and change four things: `SCOPE` (start from `tools.GRIDS["caiso"]`), `CARDS`, the first line of `RULES` and rule 5's time zone (America/Los_Angeles). The class, the checks and the export need no change; better, move them into a shared `profile.py` that both import, now that two grids need the same code.
2. **List CAISO's tables and write a card for each.** Run `python warehouse/chat/look_tables.py <table>` to print each table's entities, variables, units and span. CAISO's own: `caiso_fuel_supply`, `caiso_battery_storage`, `caiso_curtailment_daily`, `caiso_as_prices`, the alert and emergency tables; and the shared ones with CAISO's rows: `battery_stack_monthly` (market caiso), `storage_buildout_monthly` and `shoulder_hours_monthly` (entities `iso:caiso` and `iso:caiso_own`), the events, the queue (region CAISO).
3. **Write the traps into the cards.** CAISO has two the model must be told: EIA's figures for California changed on 16 December 2025 (generation from CAISO's own data after that date, never mixed), and the shoulder table holds California twice (`iso:caiso` by EIA-930, `iso:caiso_own` by CAISO's data).
4. **Add each table's row filter** to `SCOPE["filters"]` and run the scope test (`TheScope` in `tests/test_session92.py`, with CAISO's entities): every table must return only CAISO's rows.
5. **Build the questions:** copy `ercot_expected.py`, keep the five kinds and the proportions, compute every expected number from the files.
6. **Run "after" first, whole, then fix what it shows, then run it again.** Budget about USD 0.03 a question and two whole runs. The three faults found here are already fixed in the shared code; expect CAISO's own.
7. **On the site:** export the spec (`--export-spec site/lib/chat/spec_caiso.json`), make `lib/chat/ercot.ts` take the grid as an argument, let the route accept `profile: "caiso"`, copy the page, and add the link to CAISO's views with `AskErcotLink` generalised to take the grid.
8. **Check which CAISO tables the live set holds** before promising anything on the site: the same gap as point 3 at the top.
