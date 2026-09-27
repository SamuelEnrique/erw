# Session 15 report

Energy Research Warehouse (ERW), session 15, run 2026-09-27 (UTC). Every task in SESSION_15_PROMPT.md was carried out, with one decision on the evidence sentences (below) and one limit on the final check (Task 5). Nothing was pushed. No key was printed or committed; the site reads Supabase with the anon key only.

**Two things to know first:**
- **The evidence sentences are not on the site.** The prompt asks for the evidence sentence in each deal's expanded row, and also makes `energy_deals` public with "no outlet text". An evidence sentence is outlet text, and the session 7 ruling keeps third-party news text internal. So the sentences are in an internal companion table, `energy_deals_evidence`, and the page says where they are and links every story.
- **The human's re-triggered daily run (on `542b4ea`) was running on GitHub during this session.** It ran session 14's code, which knows nothing of `energy_deals`, so its Supabase load removed that table's row from the catalogue. The deal rows themselves are untouched, and `/deals` reads them directly. The catalogue row comes back on the first CI run after session 15 is pushed.

## What was built

| Task | Result | Commit |
|---|---|---|
| 1 | `warehouse/deals/extract.py`; `energy_deals` (public) and `energy_deals_evidence` (internal); 29 deals from the backfill for USD 0.1881; in `run_daily.sh`, the CI commit, the live set and a new `deals` sector | `d50a54d` |
| 2 | `/deals`: filters, expandable rows, month summary; the live-set load; nav and home links | `0e746ca` |
| 3 | `/grid`: peak, forecast error, generation mix and 7-day demand for the Lower 48 and seven ISOs, with reasons from `run_status.csv` | `ee431c2` |
| 4 | Evaluation sample (all 29 deals), scorer, and a 10-deal spot check: 0.95 of field values correct | `b66667e` |
| 5 | Screenshots, the value check extended to both pages, tools 6 and 7 in `docs/platform-tools.md`, the fuel-color fix, this report | final commit |

## Task 1: the deal data (tool 6)

**How `warehouse/deals/extract.py` works:**
- **Eligible stories:** scored rows of `news_stories` with sector deal, ppa, capital, nuclear, generation, datacenter_power, lng, oil or gas, and significance 5 or more.
- **Batching:** stories go by cluster (score.py's clusters of stories about one event), 12 clusters per call, to the newest Sonnet-class model in the models list (`claude-sonnet-5`), with a JSON schema.
- **What comes back:** whether each cluster reports a specific transaction, and for each transaction every field the prompt lists.

**No number is inferred.**
- For every number (MW, MWh, dollars, price, term), the model returns the exact span of the title or summary it read it from.
- The code keeps the number only if the span is in that story's own text and parses to the same value, with unit words applied (GW, bn, million). A foreign-currency span never becomes dollars. Anything else becomes empty, and the run log names it.
- A unit check confirmed that 231 is rejected against "230 MW", while 1.2 GW becomes 1,200 MW and $3.2bn becomes 3,200,000,000.
- The evidence sentence must also appear verbatim in the story, or it is not kept.

**Deduplication.** Each call carries a reference list of the deals already extracted. The model marks a deal that is one of them (`same_as`), and that story's links are added to the existing deal. A deal can also point to an earlier deal in the same call.

**Outputs, in the events shape; both pass the validator:**

| File | Contents | License |
|---|---|---|
| `energy_deals` | `event_type` deal, the standard columns, then deal_type, buyer, seller, other_parties, asset, technology, state, country, mwh, dollars, price_value and price_unit (as stated), term_years, announced_date, date_basis, ai_power, confidence, story_ids, story_urls. The standard `price` column only for a price stated in USD/MWh | public, by its header, like `news_index` |
| `energy_deals_evidence` | one row per deal and story, with the evidence sentence | internal |
| `warehouse/deals/checked.csv` | every story sent, so the daily run sends only new ones | (a tracking file) |

**Plumbing:**
- `run_daily.sh` runs the extraction after scoring.
- The two tables join the git allowlist beside the news tables, and the workflow commits them with `checked.csv`, so the CI runner has them.
- `energy_deals` joins the Supabase live set.
- A `deals` sector was added in coverage, the package and the chat tools.

**The backfill.** News was brought current first: 184 new stories, scored for USD 0.5575. Then every scored story was checked: 1,151 stories, 133 eligible, in 104 clusters.

| | |
|---|---|
| Calls | 9 (none failed); plus one earlier trial call, USD 0.0285, whose output was set aside |
| Tokens | 31,206 in, 11,663 out, 17,728 cache read |
| **Cost of the backfill** | **USD 0.1881** |
| Deals | **29**, 7 of them reported by several stories (one merged across clusters) |
| Not kept | 2: an evidence sentence that was not verbatim in the story, and a term written "Over Seven Years", which the parser does not read as a number |

Only 29 deals exist because the ERW has scored news only since 2026-09-23.

**Deal counts by type:**

| Type | Deals |
|---|---|
| m_and_a | 7 |
| other | 6 |
| debt | 3 |
| equity_raise | 3 |
| joint_venture | 3 |
| fuel_supply | 2 |
| project_finance | 2 |
| nuclear_restart | 1 |
| ppa | 1 |
| smr | 1 |
| **Total** | **29** |

- **By status:** announced 16, signed 9, closed 3, cancelled 1.
- **Tagged AI or datacenter power:** 5.
- **Fields stated:** 13 deals state dollars, 1 states MW, none states a price.

**Two changes made before the backfill, never after the spot check:**
- **The schema was rejected** by the API: it caps nullable fields, and there were 19. Optional fields became strings, with an empty string for "not stated".
- **A rule on parties:** in a raise, debt or finance deal, the company raising the money is the seller and the investors or lenders are the buyer.

## Task 2: /deals

- **Summary strip,** for the current month: deals, MW announced (the page says from how many deals, since most state none), and the share tagged AI or datacenter power.
- **The table,** newest first, with filters in one row: deal type, technology, state, AI or datacenter power, status, and a date range.
- **Each row expands** to buyer, seller, other parties, MW and MWh, US dollars, price with its unit, term, date and its basis, model confidence, every story link, and a note on where the evidence sentence is.
- **Numbers** come from Supabase (`energy_deals` in `events`, anon key). A number a story does not state reads "not stated".
- **Links:** the nav and the home page link to `/deals` and `/grid`.

## Task 3: /grid (tool 7)

**What each region shows,** for the Lower 48 (the header row) and ERCOT, CAISO, PJM, MISO, SPP, NYISO and ISO-NE, from the EIA-930 tables in Supabase:
- yesterday's peak demand and its hour, in UTC and in the ISO's local time;
- EIA's day-ahead forecast for that hour, with the error in MW and as a percent of demand;
- the day's mean absolute forecast error;
- a 7-day chart of demand and forecast;
- the day's generation mix as a stacked bar by fuel.

A table view of every region's mix follows. Every chart cites its table.

**Colors:** eight fixed-order fuel colors from the dataviz reference categorical slots, in the site's one token file. The dataviz validator was run on the site's surface: every check passed, and three light slots are under 3:1 contrast, which is why the mix is also a table.

**Days,** checked while building:
- **Demand:** EIA-930 demand was refreshed for three days and is complete through 2026-09-26 in all eight tables, so "yesterday" is 2026-09-26.
- **Generation:** the eight generation tables were not written this run, because EIA has published only 51 to 54 of the window's 72 hours of total net generation.
- **What the page does then:** it shows each region's latest complete mix (2026-09-24, or 2026-09-25 for ERCOT and NYISO). It says which day and why, quoting the run's own record, for example: "run_status.csv, run 20260927T011111Z: RuntimeError: incomplete data, no file written for eia930_us48_generation: net_generation_mw: 51 of 72 hours".
- **The source of that text:** the content build now bundles `run_status.csv`'s EIA-930 gap and failure rows, as it bundles the digests.

## Task 4: the extraction evaluation

- **`warehouse/deals/eval/sample.py`** draws a sample stratified by deal_type: round-robin across types, with a fixed seed. **The table holds 29 deals, fewer than the 40 asked, so the sample is all 29**, covering every type.
- **`eval_sample.csv`** carries each deal's fields, its stories' titles and summaries, and a blank `<field>_ok` column per field for the human: 1 correct, 0 wrong, blank cannot tell. Also `is_deal_ok` (a real, specific transaction) and `dedup_ok` (its links are one deal).
- **`score.py`** scores a filled file: the precision per field, with filled and empty values apart.

**My spot check** (`spot_check_s15.csv`): 10 deals, one of each type (the sample's first round), each field judged against the stories' titles and summaries. An empty field is correct if the stories do not state it. The extractor was not changed afterwards.

| Field | Marked | Correct | Precision | Where wrong |
|---|---|---|---|---|
| is_deal | 10 | 8 | 0.80 | Palisades (an operational incident, not a transaction); a BWRX-300 MOU with unnamed partners in a news roundup |
| deal_type | 8 | 8 | 1.00 | |
| buyer | 8 | 8 | 1.00 | |
| seller | 8 | 8 | 1.00 | |
| other_parties | 8 | 8 | 1.00 | |
| asset | 8 | 8 | 1.00 | |
| technology | 8 | 8 | 1.00 | |
| state | 8 | 7 | 0.88 | "TX" inferred from "Permian Basin" (ProPetro to Targa) |
| country | 8 | 6 | 0.75 | "Australia" (Ichthys) and "US" (ProPetro) inferred, not stated |
| mw | 8 | 8 | 1.00 | |
| mwh | 8 | 8 | 1.00 | |
| dollars | 8 | 8 | 1.00 | |
| price | 8 | 8 | 1.00 | |
| term_years | 8 | 8 | 1.00 | |
| status | 8 | 6 | 0.75 | Nscale "raises" is closed, not announced; ProPetro "secured contracts" is signed, not announced |
| announced_date | 8 | 8 | 1.00 | |
| ai_power | 8 | 8 | 1.00 | |
| dedup | 8 | 8 | 1.00 | |
| **All fields** | **146** | **139** | **0.95** | |

**What the spot check shows:**
- **The number check held:** every number field is correct.
- **Where the model goes beyond the stated text:** it infers locations (state, country) from context, and it reads status too cautiously.
- **The two non-deals** were extracted with the lowest confidence (0.5 and 0.4).

## Task 5: screenshots, the value check, docs

**Screenshots**, in `site/screenshots/`:

| File | Height (CSS px) |
|---|---|
| `deals-desktop.png` | 1776 |
| `deals-mobile.png` | 2789 |
| `grid-desktop.png` | 4928 |
| `grid-mobile.png` | 8700 |

**The fuel-color fix.** The first `/grid` screenshot showed black bars. Tailwind 4 emits a theme variable only when a utility class uses it, and the fuel colors are read only through `var()` in SVG. The token block is now `@theme static`; the rebuilt CSS holds `--color-fuel-gas: #2a78d6`, and the re-shot page is in color.

**The value check.** `scripts/check-values.mjs` now reads `/deals` and `/grid` too. It has new independent queries for:
- the deals month count, MW and AI share;
- a deal's MW and dollars (with the short "6 billion" form compared exactly);
- a day's maximum and sum from a series table.

**Result: all 41 values on `/deals` and `/grid` match Supabase.** Across the site, 216 of 230 matched.
- **The 14 that did not** are all catalogue numbers on `/` and `/data`: table counts, row counts of the ISO tables, `news_index` rows, the newest run and the `energy_deals` catalogue row.
- **Why:** the GitHub daily run loaded Supabase after my build, with newer ISO windows and without `energy_deals`, so the page showed what Supabase held an hour earlier.

**The rerun that did not happen.** I intended to rerun the check once that run finished. But Claude Code stopped my local site server, and my wait on the GitHub run, because the machine was low on memory, and as instructed neither was restarted. So the check was not rerun on a settled database. At 01:29 UTC the GitHub run was still in progress.

**Docs:** `docs/platform-tools.md` has tools 6 and 7 with their real status.

## Decisions

1. **Evidence sentences are internal** (the top of this report). The public table carries the model's own fields and the links, as the prompt asks.
2. **A price goes in the standard `price` column only when stated in USD/MWh.** The events standard defines `price` per MWh. Any other price stays as stated, in `price_value` and `price_unit`.
3. **A deal's `event_date`** is the announced date when a story states one (`date_basis` stated), else the first story's publish time (first_story_published).
4. **The deal tables are in git,** like the news tables, so CI does not re-extract every story daily.
5. **The generation mix falls back to the latest complete day,** labeled, with the recorded reason. An empty bar would show less.
6. **I did not reload Supabase from this machine after the GitHub run's load,** because my local ISO tables are older than CI's, and a reload would overwrite newer data.

## Errors hit

1. **The first extraction call failed:** the schema had too many nullable fields for the API. Fixed before the backfill.
2. **Heredoc edits** lost a backslash in `build-content.mjs` and broke a sed-style edit. Fixed with the Edit tool.
3. **An old local server kept the port twice.** A rebuilt page also showed hour-old data from Next's fetch cache, which is keyed by URL and survives rebuilds. For local checking, the cache was moved aside (not deleted).
4. **Black fuel bars** (Task 5, fixed).
5. **The local site server and a wait loop were stopped for low memory** (Task 5).

## Open questions for the human

1. **Push session 15.** Until then, each CI run will drop `energy_deals` from the site's catalogue again, and will not extract deals.
2. **Mark `warehouse/deals/eval/eval_sample.csv`** (29 deals) and run `python warehouse/deals/eval/score.py warehouse/deals/eval/eval_sample.csv`. Should the extractor be told not to infer location or status beyond the stated words? The spot check found that is where it errs.
3. **EIA-930 generation** often lags demand by a day. Should the generation tables get the per-day completeness rule the demand tables have? Then `/grid` could show yesterday's mix on more days.
4. **The GitHub daily run** (`36284122117`) was still running at 01:29 UTC. Its first step passed the new secret check, so the secrets fix works on GitHub, and the 15-minute `latest prices` job ran on schedule for the first time at 00:53 UTC. Check the daily run's result and commit.
