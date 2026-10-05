# Session 116 report: what Texas's storage resources offered day-ahead, the standing pull, the freeze as a file, the alerts

**Done, all four parts.** The offer curves of ERCOT's 60-Day DAM Disclosure are read from the 246 zips on this machine (no request): two new tables, `ercot_storage_dam_offers_daily` and `ercot_storage_dam_offers_monthly`, and one new section on the review page `/cost-of-power/battery/awards`. The standing pull of one zip a day is in the daily run under `warehouse/health.py`. The freeze is now a file, `REVIEW_FREEZE`, which I did not create. The chain watch counts any commit or push by the chain, and the wait alert is quiet for ten minutes after REPORT READY or CHAIN DONE. One deploy (run 37265670551, merged as `90456f5`), with the snapshot of the live pages before and after: 36 differences, every one the home page's latest prices or `/network`'s hourly refresh. No number on a live page changed because of this session; the 13 battery pages, `/terms` and About show no difference.

## Read these first

1. **Of the gap of USD 23.61 per kW between the model and the awards (January to July 2026): 9.70 is capacity that offered nothing day-ahead, 14.53 is capacity that was offered and not awarded, and price takes 0.62 off.** In shares: 41, 62 and minus 3 percent. The three add up exactly, because the middle one is the remainder.
2. **The 9.70 is an allocation, not a measurement, and the page says so.** 32.2 percent of the fleet's limit-hours carried no day-ahead offer of any kind (no energy curve, no ancillary offer); 6.5 points of that were resources on outage. I valued that share at the model's average (32.2 percent of 30.14). It assumes the hours and resources that offered nothing would have made what the model makes on average. The offers cannot test that.
3. **Almost all the energy that was "offered" was priced not to clear.** The curves offered to sell 10.7 MWh per MW per day at any price; 88 percent of it was priced above USD 1,000 per MWh and 92 percent above USD 100. At each hour's own day-ahead price they offered 0.41, and 0.39 was awarded. The award follows the curve: on 98.5 percent of the 879,837 resource-hours with a curve, the award is the curve's MW at that hour's price to within 0.1 MW.
4. **In ancillary services the fleet offered several times what it was awarded: 6 to 25 percent of offers were awarded.** In Responsive Reserve, ECRS and Non-Spin the unawarded offers, valued at the clearing price, are larger than that service's whole gap. In Regulation Up they cover 93 percent of it (3.73 of 4.02). In Regulation Down they cover a third (1.74 of 5.23): most of that gap is capacity the fleet did not offer to Regulation Down at all.
5. **Session 115's "netted USD 44.50 per MWh" is USD 45.16 on the page.** Both come from the same table. Session 115 divided the seven months' dollars by the seven months' MWh; the page now takes each month over its own MW first, as the per kW figures do. The price part of the gap uses 45.16.
6. **The standing pull has not yet asked ERCOT for anything.** I ran no real `--daily` here: the tests drive it against a stand-in server with real files. Its first real request is the daily run of 5 October, 14:00 UTC, on GitHub. What to look for is under "The standing pull".
7. **Two tables, not one.** The prompt said "ercot_storage_dam_awards_monthly or a sibling table". A day can only be added to a month if the days are kept, so there is a daily table (the store) and a monthly one (what the page reads).
8. **I changed three tests of session 114** that pinned the list of scheduled steps. They now set the standing pull aside by name and pin the rest as before (decision 6).

## The answer, in full

Whole months only, January to July 2026 (212 days), per kW of the fleet's MW. The model is `battery_stack_monthly`: a 2-hour battery on the day-ahead schedule at the hub average.

| Of the gap | USD per kW | Share |
|---|---|---|
| Capacity never offered day-ahead | 9.70 | 41% |
| Offered day-ahead and not awarded | 14.53 | 62% |
| Price | -0.62 | -3% |
| The gap: the model's 30.14 less the awards' 6.53 | 23.61 | 100% |

How each part is made:

- **Never offered** = the model's total times the share of limit-hours with no offer. A limit-hour is a resource's High Sustained Limit for one hour. 91.6 million limit-hours in the seven months; 29.5 million carried no offer.
- **Price** = energy only. The fleet sold 0.39 MWh per MW per day and netted USD 45.16 on each; the model nets USD 37.67 on each MWh it discharges. The difference, on the fleet's volume, is minus 0.62: price narrows the gap. In ancillary services there is no price part: every awarded MW is paid the hour's one clearing price, the same price the model takes.
- **Offered and not awarded** = the gap less the other two.

### Capacity

| Share of the fleet's limit-hours, January to July 2026 | |
|---|---|
| No day-ahead offer of any kind | 32.2% |
| of it, status OUT (an outage) | 6.5 points |
| of it, not out and not offered | 25.7 points |
| An energy curve that offers to sell | 48.1% |
| An ancillary service offer | 62.8% |
| Any day-ahead award | 45.0% |

### Energy

| Offered to sell | MWh per MW per day | Share of all offered |
|---|---|---|
| at USD 0 per MWh or less | 0.04 | 0.4% |
| at USD 25 or less | 0.29 | 2.7% |
| at USD 50 or less | 0.60 | 5.6% |
| at USD 100 or less | 0.85 | 8.0% |
| at USD 250 or less | 0.99 | 9.3% |
| at USD 1,000 or less | 1.30 | 12.2% |
| at any price | 10.68 | 100% |
| at each hour's own day-ahead price | 0.41 | |
| Awarded: sold day-ahead | 0.39 | |
| The model's 2-hour battery: discharged | 1.81 | |

- The 10.68 is power offered hour by hour, not energy. ERCOT's file states no state of charge, so it cannot be read as MWh the fleet could have delivered.
- Even at USD 100 everywhere, the curves would have sold 0.85 MWh per MW per day, less than half the model's 1.81.
- The charging side is the same shape: the curves bid to buy 10.2 MWh per MW per day at some price, 0.30 at the hour's own price, and 0.28 was bought.

### Ancillary services

| Service | Offered, over limit-hours | Offered at or below the clearing price | Awarded | Awarded, share of offered | Awards, USD per kW | The model's | Gap | Offered and unawarded, at the clearing price |
|---|---|---|---|---|---|---|---|---|
| Regulation Up | 39.8% | 5.4% | 2.6% | 6.6% | 0.25 | 4.27 | 4.02 | 3.73 |
| Regulation Down | 34.4% | 2.6% | 2.1% | 6.0% | 0.13 | 5.36 | 5.23 | 1.74 |
| Responsive Reserve | 47.1% | 15.3% | 6.9% | 14.7% | 0.85 | 3.39 | 2.54 | 3.05 |
| ECRS | 40.4% | 11.3% | 4.9% | 12.2% | 0.54 | 1.10 | 0.56 | 2.98 |
| Non-Spin | 26.4% | 8.0% | 6.5% | 24.8% | 1.00 | 1.54 | 0.54 | 3.59 |

- **Do not add the last column.** A block can be priced for several services and awarded to one, so the services' unawarded values overlap. Counting each block once, ancillary offers came to 91 percent of limit-hours and awards to 23 percent.
- **It is not a forecast.** The unawarded offers are valued at the price that was set. Had they cleared, the price would have been lower.
- **Much of what was offered was priced far above the market.** The share of each service's offered capacity priced above USD 1,000 per MW: Regulation Down 45 percent, Non-Spin 37, Regulation Up 36, ECRS 24, Responsive Reserve 21.
- **Offered at or below the clearing price is about twice what was awarded** in Regulation Up, Responsive Reserve and ECRS. One reason is the overlap again: a block in the money for several services is counted under each and awarded to one. The tables do not say how much of the difference that explains.

### What the offers still cannot show

- **Why a resource offered nothing.** An outage is visible for 6.5 of the 32.2 points. For the rest the file gives no reason: state of charge, a real-time strategy, a contract, or ancillary services its scheduling entity arranged itself, which ERCOT discloses by entity and not by resource.
- **What that capacity did in real time.** It may have traded there. That is the SCED disclosure, not these tables.
- **How much energy stood behind the offered power.** No state of charge and no duration.
- **What the market would have paid had more cleared.**
- **Which service an unawarded block would have gone to.**
- **Whether the never-offered capacity would have made the model's average** (read first, 2).

## By month

Shares are of the month's limit-hours. No partial month is scaled.

| Month | Days | No offer of any kind | of it, on outage | Offer to sell energy | Ancillary offer | Any award | Energy offered at any price, MWh per MW per day | at USD 100 or less | at the hour's own price | sold | Ancillary offered, each block once, over limit | awarded over limit |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Dec 2025 | 26 of 31 | 28.9% | 4.9% | 56.2% | 66.0% | 46.5% | 12.68 | 0.88 | 0.30 | 0.30 | 90% | 23% |
| Jan 2026 | 31 of 31 | 27.3% | 5.2% | 52.5% | 66.3% | 48.2% | 11.70 | 0.73 | 0.35 | 0.34 | 95% | 25% |
| Feb 2026 | 28 of 28 | 30.1% | 5.2% | 47.6% | 64.8% | 47.9% | 10.74 | 0.94 | 0.41 | 0.39 | 98% | 26% |
| Mar 2026 | 31 of 31 | 31.3% | 5.5% | 46.9% | 64.2% | 47.2% | 10.33 | 0.97 | 0.46 | 0.45 | 94% | 23% |
| Apr 2026 | 30 of 30 | 34.5% | 7.9% | 46.2% | 60.5% | 44.1% | 9.92 | 0.80 | 0.41 | 0.39 | 87% | 23% |
| May 2026 | 31 of 31 | 34.9% | 9.8% | 46.4% | 59.8% | 43.8% | 10.51 | 0.82 | 0.40 | 0.38 | 87% | 24% |
| Jun 2026 | 30 of 30 | 32.9% | 6.2% | 48.4% | 62.6% | 42.3% | 10.49 | 0.86 | 0.39 | 0.37 | 87% | 22% |
| Jul 2026 | 31 of 31 | 33.2% | 5.2% | 49.0% | 62.2% | 43.1% | 11.05 | 0.87 | 0.45 | 0.42 | 88% | 20% |
| Aug 2026 | 5 of 31 | 31.1% | 5.3% | 51.1% | 62.5% | 45.4% | 11.70 | 0.95 | 0.50 | 0.49 | 89% | 20% |

The share with no offer rose from 27 percent in January to 33 to 35 percent from April on. The fleet's MW grew from 17,180 to 21,365 over those months.

## The tables

| | `ercot_storage_dam_offers_daily` | `ercot_storage_dam_offers_monthly` |
|---|---|---|
| What | the fleet's sums for each operating day, 78 variables | the days of each month added up, 91 variables |
| Rows | 18,954 (243 days, 6 December 2025 to 5 August 2026, none missing) | 819 (9 months) |
| Tier, license | derived, public | derived, public |
| Validator | exit 0, 0 warnings | exit 0, 0 warnings |
| Coverage, source registry | yes (main's file with the two rows added; no other row moved) | yes |
| Archive | 18,954 rows, to `warehouse/archive` and the bucket | 819 rows |
| Redivis draft | 18,954 rows counted there; nothing released | 819 rows counted there; nothing released |
| Site's database | **not loaded** (`catalogue_hold`) | 819 rows; the catalogue row says "review"; no count a visitor sees includes it |

- **Source files:** `60d_DAM_ESR_Data` (each resource's Energy Bid/Offer Curve, up to ten points, with its limits, status and awards) and `60d_DAM_ESR_ASOffers` (up to five blocks an offer, each a quantity and a price for each service it is offered to). Both are in every zip from 6 December 2025.
- **How a curve is read:** straight lines between its points. The check that this is how ERCOT clears it is the 98.5 percent in read first, 3.
- **How blocks are counted:** added up. The award never exceeds the sum of a resource's blocks and often exceeds its largest block, so they are additive. There is one offer row for the upward services, linked, and one for Regulation Down.
- **Nothing is capped.** A resource's blocks sometimes add up to more than its limit. They are counted as printed. This is why "offered, over limit-hours" is a ratio and can pass 100 percent.
- **Offers with no resource row:** some resources offer in an hour where ERCOT's data file has no row for them, so there is no limit, status or award to set the offer beside. Those blocks are in `as_offer_mwh_unlisted` and in no other sum: 68,899 MWh over the seven months, 0.08 percent of the 82.9 million offered. My first trial treated this as a failed day and lost 44 of 243 days; I changed it (decision 3).
- **A cross-check before a month is written:** the month's days, resource-hours, energy sold and bought, and each service's awards in dollars must equal `ercot_storage_dam_awards_monthly`. If they differ the build stops.
- **Capacity is written in MWh** (the data standard's new Decision 41): a MW for an hour. Only `energy_sold_mwh` and `energy_bought_mwh` are energy.
- **Negative limits:** the 48 rows session 115 flagged with a negative HSL count as zero in `limit_mwh`.

## The standing pull

`python warehouse/connectors/ercot_dam_esr.py --daily`, started in `warehouse/run_daily.sh` by `soft_step ercot_storage_dam`, which runs it under `warehouse/health.py` through `warehouse/scheduled.py`.

Each run:

1. Reads the last operating day the row-level table holds, from its header.
2. Asks ERCOT for its file list (one request).
3. Asks for one zip at most: the first listed operating day after the last one held. A zip listed above 60 MB is not requested (they are 7 to 11 MB).
4. Checks the day's rows as the session 115 pull does and adds them to the end of `ercot_dam_esr_awards`. Every row already there is copied as it was.
5. Rebuilds `ercot_storage_dam_awards_monthly`, adds the day to `ercot_storage_dam_offers_daily` from the saved zip, and rebuilds `ercot_storage_dam_offers_monthly`.

What it will not do:

- **Never two zips in a run.** If a run does not happen, the tables are a day further behind than ERCOT's 60 until a person approves a second zip; the run prints a notice saying how many days wait (For Samuel, 1).
- **Never a request without the tables.** On GitHub's runner the four tables are first rebuilt from the ERW's archive; if one cannot be, the step is a skip with its reason.
- **Never the same failed day twice.** A day that fails a check gets no rows and a line in `warehouse/metadata/ercot_dam_esr_missing_days.csv`, which the daily workflow now commits; the next run goes on to the day after.
- **Never while ERCOT is paused.** It asks `iso_prices.paused("ercot")` before the list.
- **It does not stop the daily run.** It is a soft step: a failure is tried once more, recorded in `erw_health`, and the run goes on.

**What to look for in the first run (5 October, 14:00 UTC):**

- In `runs/daily_ercot_storage_dam.out`: `ercot_dam_esr_awards.csv: rows=1,84x,xxx added=7,xxx day=2026-08-06`. Or "ERCOT lists no operating day after 2026-08-05" if the day is not yet posted.
- The row-level table is 507 MB. The runner rebuilds it from the archive each day, as it already does for `eia930_daily_interchange` (499 MB). I did not time that rebuild for this table. If it is too slow or fails, the step is a skip and nothing is requested.
- The 1 November 2026 operating day (posted about 31 December) has a repeated hour at the clock change. Session 115's check refuses a repeated hour. If ERCOT prints that hour as two rows with one hour ending, the day will be recorded as failed and skipped. That is the existing rule, not a new one; I have not seen such a file.

**The session 115 ceiling of 3 GB is not counted against** by a daily zip (its manifest line says "requested daily"). The row ceiling of 9,000,000 still holds: at about 7,500 rows a day the table reaches it in about 2.6 years.

## The freeze rule

`CLAUDE.md` rule 9 no longer states dates. It says:

- A freeze begins when a file named `REVIEW_FREEZE` exists in the repository root. Nothing else declares one.
- The file holds two lines, `start: YYYY-MM-DD` and `end: YYYY-MM-DD` (UTC days, both included).
- Until the file exists there is no freeze, and a deploy with rule 8's snapshot is allowed. The same holds before its start and after its end.
- A file that cannot be read as two dates in order is a freeze until a person corrects or removes it.
- `python scripts/freeze.py status` says which holds: exit 0 no freeze, 1 frozen, 2 unreadable (so frozen).

**Two sentences are mine and not in the prompt:** "Only a person creates or removes the file", and that a session runs the command before a push that deploys. Strike either if you disagree. The command is not wired into the deploy workflow: a wrong wiring could block or allow a deploy wrongly, and I had no way to test it against a real freeze.

I did not create the file. No test pinned the old sentence. Two method documents and some comments under `site/` still say tables are held "while the live site is frozen for its reviewer"; they give the reason for holds that are still in place and state no dates, so I left them.

## The alerts

**The chain watch.** A save is now any of:

- a commit on any branch on GitHub, main included, that a scheduled workflow did not write (the 20 newest branches, 30 newest commits of each);
- the workflow's merge of a `task/` branch into main: the chain's own landing, though the bot writes it;
- a beat. Two git hooks in `scripts/githooks/` now send one at each commit and each push, only on the machine that marked the chain, in the background, always exiting 0.

The alert's line names the save: "a push to wip/x", "a commit on main", "the landing of task/x on main" or "a beat".

- Commits by `github-actions[bot]` are passed over (the daily run's metadata). A test checks that every workflow in the repository commits under that name.
- GitHub cannot say who pushed, so a person's commit from another machine during a chain also counts. `docs/machines.md` says so.
- **Installed on this machine:** `git config core.hooksPath scripts/githooks`. It was unset. `scripts/setup.ps1` and `scripts/setup.sh` install it on a new machine. Undo with `git config --unset core.hooksPath`.
- A git worktree sends no beat: it has no `.erw/`.

**The wait alert.** The hook reads the last 512 kB of the session's transcript. If the session's last words held REPORT READY or CHAIN DONE less than ten minutes ago, a wait for input (`idle_prompt`, `agent_needs_input`) is not sent.

- A wait for a permission is never quieted.
- A new prompt from the person after those words ends the quiet.
- A transcript that cannot be read quiets nothing: an alert too many, never one too few.

## The page

`/cost-of-power/battery/awards`, still in review. One section added after "Why the two differ": "Where the gap comes from: what was offered day-ahead". In order: the three parts and their sum; how each is made, with the allocation said plainly; energy by price band; the ancillary table with its two cautions; what the offers still cannot show.

- Every figure is computed from the tables when the page is drawn. No number is written into the page's code; a test checks for that.
- If the offers table cannot be read, the section says so and shows no number. Session 115's sections do not depend on it.
- "Earned" still appears only in "not what any battery earned".
- The method is `/data/methods/ercot_storage_dam_offers`, in review.

In this machine's build, in the internal view: the page answers 200 with 292 figures and says nowhere that a table could not be read; a visitor gets the in-review page.

## Deploy and snapshots

One push, to `task/116-storage-offers` at 04:57 UTC. Run 37265670551 passed (tests, site build, route check, the no-request check) and merged as `90456f5` at 05:03; production served the new section by 05:05. `python scripts/freeze.py status` before the push: exit 0, no freeze. Three snapshots of the 25 live pages: `before-116` (04:27 UTC, before any table was loaded), `after-116-load` (04:56, after the load, before the push), `after-116` (05:05, after the deploy).

`before-116` against `after-116`: **36 differences.**

| Page | Differences | What | Expected |
|---|---|---|---|
| `/` | 30 | the latest real-time prices of five hubs (ERCOT, CAISO, NYISO, SPP, ISO-NE): 10 numbers (5 keys gone, 5 new) and 20 lines of text: the prices, their interval lines, and four lines that count down with the clock ("6.0 days in the ERW table" to "5.9", "4.0" to "3.9") | yes: the 15-minute refresh. Not this session's |
| `/network` | 6 | "refreshed 03:05 UTC" became "04:05 UTC"; demand's newest hour 01:00 became 02:00 (two lines); the source line's build stamp | yes: the hourly refresh. Not this session's |
| `/cost-of-power/battery` and its 12 variants (both grids, 2, 4 and 8 hours, both strategies) | 0 | | |
| `/about`, `/storage`, the three seller pages, `/terms`, the four methods pages | 0 | | |

`before-116` against `after-116-load` (the load alone): 26 differences, all on `/`, all latest prices. `after-116-load` against `after-116` (the deploy alone): 36, 30 on `/` and the 6 of `/network`. **"Rows", "Last refresh", the count of tables, and the count of sources on `/terms` did not move:** the monthly table is under `review_hold`, the daily one under `catalogue_hold`, and the new source under `sources_hold`. No difference was unexpected.

On production after the deploy (`site/scripts/check-review-pages.mjs`, 05:05 UTC): in the internal view `/cost-of-power/battery/awards` answers 200 with 292 figures in its text and says nowhere that a table could not be read; `/data/methods/ercot_storage_dam_offers` answers 200; a visitor gets the in-review page for both.

`wip/115-storage-awards` is deleted on the remote: it had 0 commits not on main after this deploy, checked twice (session 115's report reached main with it).

## Tests and checks

- `tests/test_session116.py`, 19 tests, on a saved real sample (the rows of 14 resources, and of one that offered without a data row, for 6 and 7 December 2025, cut from ERCOT's own two files with every column):
  - **each day's sums equal the sum of ERCOT's rows,** computed again in exact decimals without the builder's code;
  - an offer above the limit is counted as printed; an offer with no data row moves no other sum;
  - the curve at eleven prices on a real curve of the file, and two points at one price;
  - a file of another day, a zip without the offers file, a repeated hour, and an offer in an hour with no clearing price each stop the day;
  - the month is its days added up; a disagreement with the awards table stops the build; a missing day is counted and nothing is filled;
  - **the standing pull asks for the list and one zip** when three days wait; the rows already in the table are unchanged; a failed day is written down and not asked for again; nothing is requested without the table, above 60 MB, or while paused;
  - the daily run starts it once, under health; the hold lists; MISO is still paused.
- `tests/test_session116_page.py`, 22 tests: the section's place, the identity computed from the tables, both cautions, no hardcoded figure, the page still in review, the live battery page's files as on main.
- `tests/test_session116_alerts.py`, 25 tests, and `tests/test_session116_freeze.py`, 7 tests.
- Every session's tests on this machine before the push: 1,025 ran, 18 skipped, **three failed**, all session 114's pins of the scheduled steps (decision 6). After the change, the files of sessions 91, 114, 115 and 116 passed here. I did not run all 1,025 again on this machine; GitHub's run did, in a clean checkout.
- In a clean checkout without the tables: sessions 116 (73 ran, 2 skipped), 115, 114, 108, 102 and 91, none failed.
- This machine's build of the site: exit 0. The route check: exit 0, 16 live pages and 98 in review as a visitor, 0 failed.
- The validator on the two tables: exit 0, 0 warnings.

## Errors and decisions

1. **The prompt arrived as a paste with no word outside it,** like session 115's. It opens with the answer session 115 had to ask for, so I did not ask again. It is kept verbatim in `archive/sessions/SESSION_116_PROMPT.md`.
2. **Two tables, and neither is the awards table** (read first, 7).
3. **My first trial lost 44 days to one check.** I had made an offer by a resource with no data row a reason to refuse the day. It is not an error in ERCOT's file, so it is now counted on its own (`as_offer_mwh_unlisted`).
4. **The first coverage build failed, exit 1.** I had written the monthly table's inputs with a comma where coverage wants a semicolon. I read the exit code, restored coverage from git, fixed the line, rebuilt and validated the table, and built coverage again: exit 0. Nothing was loaded on the failed build.
5. **Coverage was patched, not rebuilt,** as sessions 113 to 115 did: main's file with this session's two rows added.
6. **I changed three tests of session 114** (`tests/test_session114_part2.py`). They asserted that the scheduled steps are exactly session 114's and that only EIA's two connectors make a request. The standing pull is a new step that makes one, approved in the prompt. The tests now set it aside by name and pin everything else as before. Without the change the branch could not merge.
7. **A second copy of me wrote parts three and four, and a third wrote the page section,** while I built the tables. I read their code. On the page I had asked for "more than a battery could deliver" about the 10.7 MWh; the copy left it out because the file has no duration to support it, and it was right. I had also said Regulation Up's unawarded offers were as large as its gap; they are 93 percent of it, and the page computes which side each service falls on.
8. **The share-of-gap allocation is my choice** (read first, 2). The alternative was to give no dollar figure for "never offered". The prompt asked for one.
9. **No real run of the standing pull** (read first, 6). The prompt allowed part two's daily zip; I left the first one to the scheduled run so that today's zip is requested once, by the job that will request it every day.
10. **`run_status.csv`: two rows added by hand,** this session's two builds.
11. **No model call. Model spend USD 0.00.** No request to ERCOT or any publisher. MISO was not requested. No force push.
12. **I stopped the local site server by its process** (port 3049), as session 115 did.
13. **About 63 minutes, not 60.**

## To finish

Nothing is owed for this session's tables, page or code. This report is on `wip/116-storage-offers`; it reaches main with the next deploy.

Still owed from session 114 and not touched here: the cost ledger's rows of session 114.

The commands that ran, each with its exit code read:

```bash
PY="<the repository>/.venv/Scripts/python.exe"
python warehouse/lock.py run --task "ercot_storage_dam_offers" --minutes 15 --wait 15 -- "$PY" warehouse/derived/ercot_storage_dam_offers.py --from-zips   # exit 0
python warehouse/lock.py run --task "ercot_storage_dam_offers_monthly" -- "$PY" warehouse/derived/ercot_storage_dam_offers.py                              # exit 0 (after decision 4)
python warehouse/validate/erw_validate.py warehouse/output/ercot_storage_dam_offers_daily.csv warehouse/output/ercot_storage_dam_offers_monthly.csv        # exit 0
python warehouse/metadata/build_coverage.py                                                                                                               # exit 1, then exit 0; then runs/session115/patch_coverage.py
python warehouse/lock.py run --task "archive" -- "$PY" warehouse/archive/archive.py --tables "^ercot_storage_dam_offers_(daily|monthly)$" write            # exit 0
python warehouse/lock.py run --task "Redivis draft" -- "$PY" warehouse/redivis/upload.py --tables ercot_storage_dam_offers_daily                           # exit 0
python warehouse/lock.py run --task "Redivis draft" -- "$PY" warehouse/redivis/upload.py --tables ercot_storage_dam_offers_monthly                         # exit 0
python warehouse/lock.py run --task "live set" -- "$PY" warehouse/supabase/load.py --only '^ercot_storage_dam_offers_monthly$'                             # exit 0 (955.3 MB before, 955.8 after)
```

The data lock was taken for each write step and released after it; it is free now.

## For Samuel

1. **Whether a second zip in a day is allowed after a missed run.** As built, a run that does not happen leaves the tables a day further behind for good. One word from you and `--daily` can take two when two wait.
2. **Whether the allocation is the answer you want for "never offered"** (read first, 2). The measured fact is the 32.2 percent; the 9.70 is that share of the model's figure.
3. **Regulation Down is the service the fleet does not offer.** The model takes USD 5.36 per kW from it, a third of its ancillary money; the fleet was awarded 0.13 and its unawarded offers would add 1.74 at the clearing price. If the model's Regulation Down is not something a real battery offers day-ahead, that is a question about the model.
4. **The energy curves say the fleet does not sell energy day-ahead by choice:** 88 percent of what it offers is priced above USD 1,000. The real-time side (session 115's list) is where that energy would show.
5. **The first scheduled run of the standing pull** is today at 14:00 UTC. The health summary will say whether it added 6 August.
6. **The two sentences I added to rule 9** (the freeze rule section).

Energy Research Warehouse (ERW), session 116, on the old laptop (`samueloldlaptop`, data role), 2026-10-05 from about 04:07 UTC to about 05:10 UTC, unattended.
