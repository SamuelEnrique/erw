# Session 36A report: health, open items, and reopening the gate

Energy Research Warehouse (ERW), session 36A, run 2026-09-30 from about 04:15 to 06:00 UTC, unattended.

**API spend: USD 1.7314 against the USD 3 cap** (`ERW_SESSION=36A`, `ERW_SPEND_CAP_USD=3`). The ledger's 23 session 36A rows are the two calls allowed:

- **The Thesis Builder run:** USD 1.6400 (step `thesis`).
- **The CAISO scoped question:** USD 0.0914 (step `chat_grid`).

**What was and was not done:**

- **No data pull, re-pull or backfill.** Item 1 was replayed from a saved raw page. Item 7 read ISO, EIA and FERC pages as text only; nothing from them is stored in the warehouse.
- **Nothing added or removed:** no new table, no new page, nothing deleted from Redivis, no force push. `pypdf` was installed locally to read PDFs; it is not in the requirements.
- **All seven items are done,** each in its own commit. The items ran partly in parallel while coverage timings ran, so the commits landed in the order 1, 6, 7, 3, 5, 4, 2, then Part D.
- **Shipped:** live, routes 39 of 39 and values 1,490 of 1,490.

## 1. eia930_swpp_demand: the per-day rule: done

- **The change:** `eia930_swpp_demand` joins ERCO and NYIS demand in `PER_DAY` (session 13's rule). A day with a missing core hour is now a recorded gap, not a failed table.
- **Confirmed on the 2026-09-28 case,** replayed from the saved raw page of the 2026-09-29 00:57 local run (`warehouse/raw/eia930/20260929T005739Z/`, no request):
  - **Whole-window rule (before):** fails the table: `demand_forecast_mw: 53 of 72 hours (19 missing ...)`.
  - **Per-day rule (now):** writes 2026-09-26 and 2026-09-27 (24 hours of both variables each) and records 2026-09-28 as a gap (5 of 24 forecast hours).

**Gate forecast for the next daily run** (2026-09-30 14:00 UTC; none has run since the one that failed on 2026-09-29). The two failures that close the gate now should not recur:

- **Coverage:** session 33's fix lets `price_board_carbon`'s absent CARB input take its license from the previous coverage.
- **`eia930_swpp_demand`:** a day EIA leaves incomplete is now a gap, not a failure.

CARB's own failure is a known gap. So the run should pass the gate unless something new fails. What has not yet been proven on the runner:

- the session 34 steps running there for the first time: the emissions workbooks, the full intensity rebuild, the storage cycle after `caiso_outlook`, and `build_status` reading the emissions table;
- the new validator-report path (item 2);
- the package test step, now with a 4.3-million-row emissions table. It runs after the commit, so it cannot close the gate, but it could fail the job.

## 2. build_coverage.py: done

- **Streaming.** Large series tables (over 100 MB) are now read in one streamed pyarrow pass over the columns coverage needs, never as a whole frame.
- **Validation is most of the cost.** On the three largest tables it takes 310 s (emissions), 195 s (the ERCOT history) and 73 s (hourly intensity); their streamed facts take 40, 24 and 8 s.
- **So coverage reuses the validator's own reports.**
  - The daily run now keeps `erw_validate.py --json` output in `runs/validate_reports.json` and prints each file's verdict, errors and warnings.
  - `build_coverage.py --reports` reuses a table's report only when its file is older than the validator's start (`runs/validate_reports.json.started`). Otherwise it validates the table as before.
  - The validator and its blocking exit are unchanged.
  - A first version compared against the report file's own time, which would have reused a report for a file changed during validation (the Thesis Builder wrote `energy_companies` then). It was fixed before the commit and tested.

| Coverage build, this machine | Time |
|---|---|
| Before (session 33 code) | 15 min 00 s (13 min 44 s in session 34, a quieter machine) |
| Streaming alone | 13 min 30 s |
| Streaming and the validator's reports (the daily run's path) | **1 min 54 s** |

On the same tables the new code's `coverage.csv` and `docs/coverage.md` are identical to the old code's.

## 3. Supabase: the six CO2 variables: done, 90 days

- **What:** all eight variables of `eia930_all_emissions` are loaded for the last 90 days: 126,546 rows.
- **Size:** 335.6 MB before, **376.3 MB after** the load and VACUUM FULL. That is under the 380 MB line, so 90 days rather than 30.
- **After Part D's full load:** 376.4 MB, every table matched.

## 4. Thesis Builder: the wider research prompt: done

- **The change.** The scope research, the company research and the landscape call now keep in scope the adjacent drillers, plant or project developers and technology providers whose work supplies the niche or depends on it.
- **One run** with a new research pass on "subsurface heat mapping for geothermal": `docs/thesis/subsurface-heat-mapping-for-geothermal-session-36a.xlsx`.

| Run | Companies | Calls, searches | USD |
|---|---|---|---|
| Per-sheet run, 2026-09-28 | 7 | 26, 37 | 2.2310 |
| Session 30 (batched) | 2 | 15, 37 | 1.2253 |
| Session 34 (landscape alone, same research) | 2 | 16, 37 | 1.3237 |
| **Session 36A (wider scope, new research)** | **8** | 17, 41 | **1.6400** |

**What it found:**

- **Companies:** Zanskar Geothermal & Minerals, Project InnerSpace, Sage Geosystems, Quaise Energy, XGS Energy, Mazama Energy, Mantle Reach Power, Eavor Technologies.
- **Incumbents:** Ormat, Fervo, Baker Hughes, Nabors, SLB.
- **The scope now excludes only** shallow heat pumps, oil and gas seismic work with no geothermal customer, and grid-side items.
- `energy_companies` now has 356 rows.

## 5. The CAISO scoped question, once more: done

- **Asked** with the fixed loop: "How many MWh did CAISO's batteries discharge on the latest complete day, and how many did they charge?"
- **The answer:** CAISO's batteries discharged 24,524.083 MWh and charged 30,002.333 MWh on 2026-09-27, a Pacific operating day; round-trip ratio 0.817, energy out over energy in as reported.
- **Citation:** `storage_daily_cycle` (derived, CAISO rows from `caiso_battery_storage`).
- **Run:** 5 tool calls, no retry, **USD 0.0914**.
- **Check:** these are the figures session 34 recomputed independently from the 5-minute file.
- **Record:** `warehouse/chat/eval/results/20260930_36A_caiso.json`.

## 6. Datacenters to grids: done

**The rule,** in `docs/grids/grids.json` and `docs/methods/datacenter_facilities.md` ("Grid pages"). The page (`site/lib/grid.ts`) and `check-values.mjs` apply it alike:

1. a facility from an ISO's queue (member id `<iso>_queue:`) belongs to that ISO;
2. else, one whose `utility` a grid lists belongs to that grid;
3. else, the grid's state list.

**Utilities.** Only two of the 340 rows name a utility: OGE Energy (listed for SPP) and WEC Energy (MISO).

**Check keys** are now `griddc|<slug>|n` and `griddc|<slug>|mw`.

| Grid | Before | After | Placed by queue or utility |
|---|---|---|---|
| ERCOT | 37, 1,400 MW | 37, 1,400 MW | 2 (ERCOT queue) |
| CAISO | 35, 152 MW | 35, 152 MW | 0 |
| PJM | 58, 974 MW | 58, 974 MW | 0 |
| NYISO | 5, 0 MW | 5, 0 MW | 1 (NYISO queue) |
| ISO-NE | 1, 0 MW | 1, 0 MW | 0 |
| MISO | 11, 902 MW | 11, 902 MW | 1 (WEC Energy) |
| SPP | 10, 0 MW | 10, 0 MW | 1 (OGE Energy) |

No count changed: the five facilities the new rules place were already in their grid's states.

## 7. Written layer dates: done

Each dated event now carries an inline citation to a page whose text states the date. Checked by reading the page text (the PDFs with pypdf).

| Grid | Event | Result | Source (text states the date) |
|---|---|---|---|
| ERCOT | 1970 formed | confirmed | ercot.com/news/mediakit/backgrounder ("Founded in 1970") |
| ERCOT | 2010-12-01 nodal market | confirmed | ERCOT 2010 financial statements, ercot.com/files/docs/2011/04/26/ercot_2010_financial_statements.pdf ("On December 1, 2010 ERCOT launched the Nodal market") |
| ERCOT | 2021-02-15 Uri load shed | confirmed | EIA, todayinenergy/detail.php?id=46836 ("ERCOT began implementing rotating outages at midnight on February 15") |
| CAISO | 1998-03-31 operations begin | confirmed | caiso.com/documents/rtofiling.pdf ("since its inception on March 31, 1998") |
| CAISO | 2014-11-01 Western EIM | confirmed | caiso.com market performance report, dec-2022 WEIM page ("On November 1, 2014 ... fully activated") |
| CAISO | 2020-08-14 rotating outages | confirmed | CAISO Final Root Cause Analysis ("two rotating outages ... on August 14 and 15, 2020") |
| PJM | 1927 pool | confirmed | pjm.com/about-pjm/who-we-are/pjm-history ("PJM began in 1927") |
| PJM | 2007-06-01 first RPM delivery year | **softened to 2007** | PJM Manual 18 states "began with the 2007/2008 Delivery Year" and a June 1 to May 31 year, but not the date itself |
| PJM | 2022-12-24 Winter Storm Elliott | confirmed | PJM Elliott report (emergency procedures on Dec. 23 and Dec. 24) |
| NYISO | **1999-12-01 start of operations** | confirmed | nyiso.com/faq ("took control of New York's electric power system on December 1, 1999"). NYISO's history page says only "established in 1999" |
| NYISO | 2003-08-14 blackout | confirmed | nyiso.com blog, "A Look Back at the Northeast Blackout of 2003" |
| NYISO | 2021-04-30 Indian Point | confirmed | EIA, todayinenergy/detail.php?id=47776 |
| ISO-NE | 1997 created | confirmed | iso-ne.com/about/who-we-are/our-history |
| ISO-NE | 2003-03-01 Standard Market Design | **softened to 2003** | our-history states 2003. ISO-NE's 2003 press release says "early Saturday morning" without a date |
| ISO-NE | 2008-02 first FCA | confirmed | our-history ("2008 In February, ISO holds first auction in new Forward Capacity Market") |
| MISO | 2001-12 first RTO | **made precise: 2001-12-20** | misoenergy.org miso-history ("on December 20, 2001") |
| MISO | 2005-04-01 markets open | confirmed | FERC staff report, ferc.gov/sites/default/files/2020-05/miso-06-30-05.pdf |
| MISO | 2013-12-19 MISO South | confirmed | FERC order, ferc.gov/sites/default/files/2020-05/E-4_84.pdf ("integration of the Entergy Operating Companies into MISO on December 19, 2013") |
| SPP | 1941 pool | confirmed | spp.org news, "SPP celebrates 20 years as an RTO" ("founded in 1941 by 11 electric utilities") |
| SPP | 2014-03-01 Integrated Marketplace | **softened to 2014** | SPP pages state "launched in 2014"; none I read states March 1 |
| SPP | 2021-02-15 Uri load shed | confirmed | SPP's comprehensive review of the February 2021 storm ("contributing to SPP's need to shed load each day", Feb. 15 and 16) |

## Part D: verify and ship

- **Validator:** 78 of 78 pass, all tables, through the new JSON path.
- **Coverage:** 78 tables, built in 1 min 54 s.
- **Archive:** 117 rows across 11 tables (session 33's 47 restored news stories reached the archive now).
- **Supabase:** 376.4 MB, every table matched.
- **Redivis drafts:** 6 tables uploaded (`api_cost_ledger`, `energy_companies`, headers, coverage, sources), each `count(*)` equal to its CSV. Nothing released.
- **License check:** 0 internal tables in the public dataset.
- **llms.txt:** notes the datacenter rule, the cited dates and the eight CO2 variables in the live set. The chat spec is regenerated and `check_spec` passes.
- **`tests/`:** 65 of 65. One fix: `test_session35.py` set `ERW_LEDGER=0` at import, which switched the ledger off for later tests and failed session 30's ledger test in a full run.
- **Site checks:** locally routes 39 of 39 and values 1,340 of 1,340; **live**, routes 39 of 39 and values 1,490 of 1,490.

## Decisions made without a human

1. **Coverage reuses the validator's reports** (item 2), beyond the streaming the prompt asked for. Streaming alone saved only 90 seconds.
2. **The PJM, ISO-NE and SPP dates** whose day no page states became year-only. Each keeps a citation to the page that states the year.
3. **FERC pages were cited** where they state a date (MISO). Automated requests get HTTP 403 on some FERC pages, but the two PDFs read fine.
4. **90 days, not 30, of the CO2 variables in Supabase** at 376.3 MB. The live set is now within 24 MB of the loader's 400 MB limit.
5. **The Thesis Builder's scope wording** is generic (drillers, developers and technology providers adjacent to any niche), not geothermal-specific.

## Run health and the gate

- **Gate: CLOSED,** unchanged. The latest GitHub daily run (2026-09-29) has 2 failures outside the known gaps: `coverage` and `eia930_swpp_demand`, both now fixed in code.
- **No daily job ran during the session.** Origin had no new commits at the push; the next run is 2026-09-30 14:00 UTC.
- **Forecast:** as in item 1, the gate should open with that run unless something new fails.

## Open questions

1. **Supabase headroom.** The live set is at 376.4 MB of 400. Growth from news, the ledger and the storage series will reach the limit within weeks. Raise `max_mb`, move to a paid tier, or trim a table's window?
2. **Package test step** on the runner, with the 4.3M-row emissions table and the 1.1M-row hourly intensity. Watch its time on the next run (limit 20 minutes).
3. **The Thesis Builder's 8 companies** are model-extracted. Spot-check them against their sources before they are shown.
4. **Utility names in `datacenter_facilities`** are rare (2 of 340). Ask the extraction to capture the serving utility, or keep the state fallback as the main rule?

## Skipped

- Nothing of the seven items.
- **Not re-proven:** the new validator-to-coverage path on the GitHub runner; that happens on the next daily run.
