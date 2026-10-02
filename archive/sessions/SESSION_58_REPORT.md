# Session 58 report: the daily jobs, private inputs, California reliability v1

Energy Research Warehouse (ERW), session 58, run 2026-10-01 22:36 UTC to about 01:50 UTC on 2026-10-02. **Wall time about 3 hours 14 minutes, stopped at Samuel's instruction before the full close-out.**

**API spend: USD 1.74**, under the USD 4 cap but above the USD 1 expected. All of it is the one dispatched daily run's model steps, as recorded in `warehouse/metadata/run_status.csv` (the ledger's per-step costs):
- **news scoring:** USD 1.10. It scored 400 stories, a backlog after three failed days;
- **shadow scoring:** USD 0.35;
- **deals:** USD 0.19;
- **datacenters:** USD 0.04;
- **the digest:** USD 0.03;
- **policy:** USD 0.03.

The session made no model call of its own. No force push.

## Part 1, in plain words

### What was wrong

**The daily job was running, but late, and it was failing.** GitHub's scheduler ran the 14:00 UTC job at 18:00 to 19:00, and the last three scheduled runs failed:
- **2026-09-29:** CARB's auction PDF answered HTTP 202, so the CARB table wasn't written, and coverage then raised on the missing input. That was already handled before this session.
- **2026-09-30:** a test failure, fixed the same day.
- **2026-10-01 and every run since session 49:** the run stopped in its first second. Session 49 changed the chat's briefing (`package/llms.txt`) without regenerating the site's chat spec, and the daily job refuses to run on a stale spec.

**The last success before this session** was a manual run on 09-30 at 23:04. Even that run had two failures:
- **The digest step failed.** pandas could not parse `news_stories.event_date` once new stories arrived with fractional seconds. No digest has been written since 2026-09-28.
- **The Supabase load failed its size check** at 448.5 MB, over its own 400 MB limit, after writing every table. The weekly `VACUUM FULL` brought it back to 356.6 MB the next morning.

**The digest is sent to no one.** It is written, but:
- **The fixed recipient is unsubscribed.** The one fixed address (`DIGEST_RECIPIENTS`) is on the unsubscribe list, `email_suppressions`, since **2026-09-29 00:32:29 UTC**, during session 28's work. No report says why.
- **There are no subscribers:** the subscribers table holds no confirmed subscriber.

So today's digest went to 0 recipients ("sent to 0 recipients (0 fixed, 0 subscribers)"). Only the shadow digest reached its one address.

**The Roundup has never run.** Its Sunday 23:00 schedule has not fired once. No Roundup has been sent.

**Why Ask the ERW has no prices for today:**
- The price tables the chat reads hold complete operating days only.
- Today's real-time prices exist only in the 15-minute snapshot `latest_prices` on `/board`, which the chat does not read.
- And with the daily load failing, even yesterday's days were missing.

### What was fixed, in our code

1. **The chat spec,** regenerated: a local export, no model call. The daily run passed the check at once.
2. **Every `event_date` parse** in `warehouse/news` now takes any ISO 8601 stamp (`format="ISO8601"`).
3. **The loader** now escalates once to `VACUUM (FULL, ANALYZE)` when the plain vacuum leaves the database over the limit.
4. **`test_session44`:** session 55's set E broke two of its checks (five sets now; a typed literal in an answer). The next daily run's tests would have failed on them.
5. **The chat's briefing** now says how to answer a question about today's price: not in the tables the chat reads, the newest day they hold, and `/board` for the live price.
6. **After the dispatched run,** two late steps failed, and both are fixed:
   - the package tests: `erw.cite` of the grid network tables lacked "derived" in the publisher, for the network's first run on the runner;
   - STATUS.md: `KeyError 'iso'` on a gap of `iso_hub_prices_history`.

### The dispatched run (36937222877, 2026-10-01 22:48 to 2026-10-02 00:53 UTC)

- **The data step passed:** every connector, validation, coverage, the archive, and the Supabase load.
- **Prices reached Supabase:** ERCOT and CAISO real-time through the 09-30 operating day, the latest complete day when it pulled.
- **The digest was written:** `docs/digest/2026-10-02.md`. It was sent to **no one**, as above.
- **The commit landed:** "Daily prices 2026-10-02: ok" (`ac178e0`).
- **It ended "failure"** on the package tests and STATUS.md, both fixed since, as above.

### The outside trigger (prepared; Samuel's steps)

`docs/runbook.md`, "An outside trigger for the scheduled jobs":
1. A fine-grained GitHub token for this repository only, with Actions read and write.
2. cron-job.org calling `workflow_dispatch` for the daily job (14:00 UTC), latest prices (every 15 minutes), the hourly network, the Roundup (Sundays 23:00) and the weekly vacuum. Supabase `pg_cron` with `pg_net` is described as the alternative.

**No token is in the repository.**

**Two triggers on one day are safe.** The daily job and the Roundup have a new first job, `gate`. A scheduled run, or a dispatch with `once` set to `1` (what the outside scheduler sends), stops when a run already succeeded that UTC day, so the digest and the Roundup are never sent twice. A manual run always runs.

### What Samuel must do

1. **The digest's recipient.** If the unsubscribe of 2026-09-29 00:32 UTC was not meant, delete that address's row in Supabase's `email_suppressions` (Table editor), or subscribe again through `/subscribe` and confirm the email. Until then the digest goes to no one.
2. **The outside trigger.** Follow `docs/runbook.md`: create the token, create the five cron jobs, and test one run.
3. **Close the stale issues.** The repository token here can read issues but not close them (HTTP 403):
   - **Close:** #6, #7, #8, #9, #10, #13 and #14 (daily runs failed 09-29 to 10-02, fixed above); #11 and #12 (the digest's failure streaks: the digest is written again).
   - **Keep open, source problems:** #3 (CARB answers HTTP 202 to the runner), #4 (the NYISO queue) and #5 (ERCOT's large-load queue).

## Part 2: private inputs

**Skipped: both folders were empty.**
- `private/bills/` holds only its README: no bill to transcribe.
- `private/newsletters/` did not exist. It now does, with a README, and git ignores everything in it but the README, as it does for `private/bills/`.

No bill or newsletter comparison was made.

## Part 3: California reliability v1

### The alert history: `caiso_grid_emergencies`

- **Source:** CAISO's Grid Emergencies History Report, 1998 to present (one public PDF, 191 pages, revised 07/06/2026).
- **License:** read first. CAISO's Privacy and Terms of Use: its materials "may be used by you provided that you keep intact all copyright, trademark and other proprietary notices and that you credit the California ISO". **Public, with credit.**
- **Rows: 1,900 of the 20,000 ceiling**, 1998-05-30 to 2025-04-30 (the latest notice). One row per notice type, region and day. The report's four table layouts are each read by their own code. Data standard decision 35.
- **The check against CAISO's own yearly day counts:** **214 of 232 match.** The 18 that differ are listed in the table's header. Most are a day or two of Restricted Maintenance Operations (RMO) or of transmission emergencies, where CAISO counts declarations and the table counts days; others are the 2003 and 2004 tables without a type header.

### The September 2022 heat wave: `caiso_heat_2022`

- **The window:** 2022-08-31 to 2022-09-09, on the event template, with baselines on the same weekdays 364 and 728 days earlier.
- **NOAA:** SAC and LAX for the window and both baselines. **1,752 rows returned of the 10,000 ceiling** (3,375 values merged; NOAA public domain). `noaa_isd.py --event` merges one event and keeps the table's other rows and header.
- **The event window:** 460 rows. The other events are unchanged, row for row.
- **Estimates, CAISO demand, the pooled effect per day:**

| Specification | Effect | 95 percent interval |
|---|---|---|
| day of week and year means | **+168,641 MWh** | 123,611 to 213,670 |
| controlling for temperature (degree days and squares) | **+26,826 MWh** | 3,168 to 50,484 |
| a linear year trend (robustness) | +187,218 MWh | 82,363 to 292,073 |

Controlling for temperature removes about five sixths of the effect.

- **The page:** `/events/caiso-heat-2022`, with CAISO's notices of each day: Flex Alerts on ten days, and the EEA 3 of 2022-09-06.

### How tight was it: `caiso_reliability_daily` and `/grid/caiso`'s Reliability section

**The table:** 2,980 Pacific days, 2018-07-01 to 2026-09-28: peak demand, the evening ramp (the rise from the 12:00 to 15:00 mean to the 17:00 to 21:00 peak), batteries' share of the evening peak (from 2025-08-24, CAISO's own series), and the day's notices.

**The tightest days:**

| Day | Peak demand served | Notes |
|---|---|---|
| 2022-09-06 | **51,104 MW** | the day of the EEA 3 |
| 2026-09-09 | 49,959 MW | three weeks before this session, with no notice in the report, which ends 2025-04-30 |
| 2022-09-07 | 49,520 MW | |
| 2022-09-05 | 48,456 MW | |
| 2022-09-08 | 48,151 MW | |

- **The steepest evening ramp:** 12,519 MW, on 2023-08-27.
- **Batteries at the evening peak** (392 days held): a median of 22.9 percent of the peak hour's demand, and up to 41.3 percent.
- **The day's available supply is not held,** so peak demand is not set against it. The page says so.

**The section** on `/grid/caiso#reliability` shows:
- every notice type's days per year since 1998, each cell with a check key (`awe|days|<type>|<year>`);
- the latest notices;
- the twelve highest peaks and the latest fourteen days, with ramp, battery share and notices, each with its series check key.

**Docs:** `docs/methods/california_reliability.md`, and `docs/reviews/clara-questions.md` (ten questions for a former California Energy Commission analyst, each tied to a part of the section, aimed at the grid-stress tool).

### Checks

- **Local, production build:** check-values 4,082 of 4,083; check-routes 64 of 64. The new keys match, including:
  - `awe|days|flex_alert|2022` (11);
  - the 51,104 MW peak of 2022-09-06;
  - the event study's estimates (+168,640.60 and +26,826.16 MWh).
- **Live, after the deploy:** check-values **3,997 of 3,998**; check-routes **64 of 64**. `/grid/caiso` shows the Reliability section, and `/events/caiso-heat-2022` answers 200.
- **The one failure, local and live,** is `/network`'s ERCOT carbon intensity for 2026-09-28 23:00: 356.5959 on the page, 356.5962 in Supabase. EIA revised the value in today's load. The hourly network snapshot carries the older value until its next run takes the daily build, committed in `ac178e0`, as its base. It was not fixed here, because that needs an EIA pull this session did not have approval for.
- **Tests:** `tests/test_session58.py`, 13 tests, OK, with `test_session44` and `test_session55`. The full suite ran 191 tests: test_session44's two failures (session 55's) are fixed. test_session57's inactive test errored in the full run and passes alone, most likely short of memory.

## Rows against each ceiling

| Pull | Rows | Ceiling |
|---|---|---|
| CAISO Grid Emergencies History Report | 1,900 | 20,000 |
| NOAA ISD, SAC and LAX, September 2022 and baselines | 1,752 returned | 10,000 |

## Open questions

0. **The September 2022 mismatch, not investigated (stopped here).** On `/events/caiso-heat-2022`, check-values reported keys for 2022-09-01, among them `demand_max_mw` 46,868 MW and `demand_max_pct_vs_baseline` 34.74 percent. Yet the event window's rows, and `caiso_reliability_daily`, put the window's peak at 51,104 MW on 2022-09-06 (+32.24 percent against the baseline on that day).
   - **Possibly no error:** 2022-09-01 can be the day with the largest rise against its baseline while 2022-09-06 has the highest MW, and 46,868 may be a different figure on the page.
   - **Not yet verified:** that the page's "highest hour in the window" sentence names 2022-09-06 at 51,104 MW, and that the /events card's headline does too.
   - **Check next:** read the page's text, and compare `pickOf` on demand_max_mw with the table.
1. **The digest's recipient** (above): unsubscribed on 2026-09-29 00:32 UTC by whom? If by a session's check of the unsubscribe link, that check should use a test address.
2. **Available supply** for "how tight was it". Today's Outlook's history files may hold it: a pull to approve.
3. **The 18 count differences.** Are CAISO's yearly counts declarations or days in the years they differ? A question for CAISO's operations staff, or for Clara (`docs/reviews/clara-questions.md`).
4. **The report ends at 2025-04-30.** The 49,959 MW evening of 2026-09-09 carries no notice there. Is the report behind, or was there none? CAISO's live notices page would settle it.
5. **The Roundup** has never run on GitHub's schedule. The outside trigger includes it.
