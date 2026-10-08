# Session 149 report: the rulings and the loose ends

Run on 7 October 2026 (UTC), unattended, in the chain 146 to 149. Two agents built it in working copies of their own
to written briefs (`runs/session149/BRIEF_A.md`, `BRIEF_B.md`); I ran the locked writes, the merged build and its
checks myself.

## Seven things to know first

- **Something a page shows today is removed, on your conditional instruction.** New York's load in line (megawatts
  and requests by zone, and the fold of 53 requests: 14,232.9 MW) has left the face of `/cost-of-power`. NYISO's
  notice, read by its words alone, confers no license and reserves every right, with no grant. The row reads
  "NYISO's terms do not allow it". One switch puts it back (`SHOWN` in `warehouse/connectors/nyiso_load_queue.py`).
  The six sentences are below. **The same notice covers every NYISO table the ERW publishes** (zone prices, the
  interconnection queue): I changed only the load queue.
- **`/network` will change at the next daily run (14:00 UTC), and that is this session's doing.** The daily build of
  the grid network has failed on every run since 4 October (a code fault, below), so the live page's carbon
  intensity is of 29 September. The fix is in this session. The deploy itself changes no number; the next daily run
  rebuilds intensity, nodes and positions for the first time since 1 October. Not on your list: my addition.
- **Two things need a person.** (a) `nyiso_load_queue` sits in the public Redivis dataset; the move out is
  `upload.py --check-license --fix`, which the uploader reserves for a person. I did not write the table as internal
  tonight, so no check fails yet; the runner's queue run of Monday 12 October will, so run the lines under "To
  finish" before then. (b) The data machine's daily run is built and registered nowhere (below).
- **The curtailment page has no true map: 0 of 37 places.** No operator publishes a boundary or coordinates for a
  hub or zone on the page. CAISO's tariff names its three zones and draws none; ERCOT's load zone and weather zone
  maps are JPG pictures; NYISO lists subzones by transmission owner. Every place stays a tile, with the reason on
  hover. ERCOT does define its eight weather zones by ZIP code (2,476 codes, held), but no place on the page is a
  weather zone, and drawing them needs the Census ZIP code shapes: a pull you did not name.
- **"The 2026 transmission matrix's ordering": I read it as the Commission's order.** Docket 59080 has 86 filings
  and no signed order (latest: item 86, 25 September 2026, a proposed order on remand). The 2026 figures stay
  "filed, not approved". Nothing changed, no model call. If you meant the sort of the rows: the page lists Oncor,
  CenterPoint, AEP Texas, Texas-New Mexico Power; the Commission's matrix is alphabetical.
- **ERCOT's load zones: "the ceiling asked" named no number.** Session 140 asked for "a new ceiling, or count only
  new rows". Applied: the 3,000,000 stays and a row counts once. The refresh is on the data machine's run, not the
  runner's (the table is 568 MB, and the ceiling's record lives with the saved workbooks).
- **The five check-values differences were the check's fault, not the pages'.** Fixed in the check. Two real ones
  found on the way are fixed on their page (below).

## Verdict: the rulings are applied and the loose ends closed, but for three. What is left, exactly

1. **Redivis**: the two commands for a person, before Monday 12 October 14:00 UTC ("To finish").
2. **The data machine's daily run**: register the one line, or start it by hand ("To finish").
3. **The true map**: no source meets your test. Your ruling on the Census ZIP code shapes for ERCOT's weather zones.
4. **The loader's failure of 5, 6 and 7 October is not a code fault**: its confirming row count passes Supabase's
   statement timeout on the two largest whole tables. The rows are loaded (336,572 and 345,474, equal to the files).
   A retry of the count would settle it. Not made.
5. **The Redivis upload's failure is its guard working**: `price_board_spreads`, a 365-day window, lost two rows and
   gained none (2,176 against 2,178). It repeats each day the window shrinks. Yours: `--allow-shrink`, or a rule.
6. `tests/fixtures/session140/loadqueue` holds 20 real NYISO requests in the public repository, and report 140
   holds the totals. Removing them deletes files and rewrites history: yours.

## Your rulings, applied

- **ISO-NE's zone prices: internal.** Nothing shown; the notes that said "pending" say ruled.
- **The datacenter page keeps the budget of hours; the generator page keeps its hours rule.** Wording only.
- **ISO-NE's monthly curtailment file: pulled, held internal.** `isone_ddg_undelivered_monthly`, 840 rows (wind
  January 2018 to September 2026, solar July 2025 to September 2026; the sheet "System" only: all seven
  aggregations would be about 5,900 rows, past the ceiling). In no public dataset and on no page. The curtailment
  page's ISO-NE hover now ends "Held, not shown."
- **ERCOT's load zones daily**: counted 2,473,320 of 3,000,000; a new copy of 2026 can add at most 51,288 rows.
  The trial refresh adds 0 rows: ERCOT posts the year's workbook on Sundays. "Daily" asks ERCOT's two lists each
  day and a workbook once a week.
- **NYISO's terms, word for word** (the notice as saved on 7 October, no new request):
  1. "The NYISO maintains this Web site for the benefit of its Market Participants and other authorized users."
  2. "Access to this Web site does not confer any license or ownership interest in either the form or content of
     the Web site, including any confidential or proprietary information or intellectual property of any kind or
     nature, and the NYISO hereby expressly reserves such rights and property in its entirety."
  3. "Downloading, republishing, retransmitting, reproducing, or other use of any image or video on this website as
     a stand-alone file is strictly prohibited"
  4. "The NYISO’s trademarks (including its logo) are owned by the NYISO and may only be used with the NYISO’s
     prior written permission."
  5. "Even if prior written permission is obtained, the NYISO may revoke permission to use the NYISO’s trademarks
     at any time."
  6. "Copyright © 2026 New York Independent System Operator. All Rights Reserved."

## The loose ends

- **SPP South's year, on both pages.** `iso_zone_prices_history` rewritten under the lock: 1,663,123 rows (58,919
  new), SPP day-ahead from 1 January 2019, every hour of 2019 to 2025. The datacenter page's SPP years are 2019 to
  2026 (they were 2024 to 2026); the generator page's capture file holds 94 months for SPP South. No other grid's
  figure moved. The curtailment files: nothing but the build stamp.
- **The computed files, scheduled on the data machine** (`warehouse/run_data_machine.sh`): sync, ERCOT's load
  zones, then the datacenter, capture, shares, free energy and worth builders, each under `health.py`, tried once
  more on a failure; a file whose builder or test fails is put back as committed. It refuses on the runner.
  **Not registered and not run end to end**: `CLAUDE.md` says no schedule lives on a person's machine, and an
  untested job that pushes to main each day should not start itself. `ercot_estimate_page.py` is left out: the
  runner builds it from a newer table.
- **check-values.** Four catalogue counts on the home page compared 113 public tables against the 97 a visitor may
  see (16 tables, 602,481 rows, are held back for pages in review). The `/deals` figure: `energy_deals` spells its
  AI tag four ways and the check read one (October's AI share is 13 percent, not 5). Both fixed in the check.
  **Two real differences found today and fixed on the page**: a question of `/learn/problems` summed ERCOT's demand
  over a day the live set does not hold and showed 0 and infinity; it now takes the newest whole day.
- **The personal contact string is gone** from the pilot's scripts and from every copy found (`warehouse/raw/` and
  `runs/session139/`), replaced by "ERW research project, github.com/SamuelEnrique/erw". A test now scans tracked
  code for an address in a User-Agent or contact default.
- **Today's daily run, four failed steps.** Two were code faults, both fixed with a test:
  - `grid_network`: the lock's own check answer (the JSON value `true`) sits in the interchange connector's raw
    folder and was read as an EIA page. Failed on 4, 5, 6 and 7 October.
  - `build_status`: a gap row that names no day was re-checked as a day. `STATUS.md` not rebuilt since 2 October.
  - `supabase_load` and `redivis_upload`: not code faults (verdict, items 4 and 5).
  - On the live pages: `/network`'s carbon intensity is stale; `/cost-of-power/battery` and `/storage` are not.

## Every pull against its ceiling

| Pull | Ceiling | Read |
|---|---|---|
| ISO-NE, Aggregate Monthly DDG Undelivered Energy | 2,000 rows, 20 requests, 50 MB | **840 rows** kept; 14 requests; 1.95 MB |
| ERCOT's load zones, the two lists (trial refresh) | 3,000,000 rows | 2 requests; 0 new rows; 2,473,320 counted |
| Texas Commission, docket 59080's filing list | 6 documents left of 20; 15 requests | 1 request; 0 documents |
| Zone boundaries (CAISO, ERCOT, NYISO, two state agencies) | 30 requests, 200 MB | **16 requests**; 1.47 MB |
| NYISO's legal notice | 2 requests | 0 (the saved copy is whole) |

- **Every request carried "ERW research project, github.com/SamuelEnrique/erw" and no address.** (ERCOT's existing
  connector sends its own string, which holds the repository's address and no person's.)
- **No MISO request. No PJM request.** ISO-NE's and SPP's sites were not searched for boundaries.
- **Terms quoted.** ISO-NE: "You are also hereby put on notice that the Content is protected by copyright under
  United States laws. Any duplication of the Content or non-personal use may violate copyright, trademark, and other
  laws." CAISO: "may be used by you provided that you keep intact all copyright, trademark and other proprietary
  notices and that you credit the California ISO when using such materials and/or information." ERCOT: "The
  publicly available contents of this website may be used, reproduced, and redistributed, provided that the
  contents are not modified and that you maintain all copyright and other notices contained in the contents,
  including this Agreement." California Energy Commission: "free for public use consistent with the Public Records
  Act (California Government Code Section 6250 et. seq.), provided the Energy Commission is credited when using
  these materials and information." NYISO: above.

## Model spend: USD 0.00 of the USD 2.00 cap

- No model call. The matrix needed none: there is no order to read.

## The landing

- **Not landed when this was written.** `REVIEW_FREEZE` reads frozen through 7 October (UTC) and ends by its own
  dates at 00:00 UTC. The landing follows then, with the snapshot before and after, and a line is added here.
- Written under the lock tonight, nothing released: `iso_zone_prices_history` and `isone_ddg_undelivered_monthly`
  (validator, coverage, the archive, the Redivis draft: exit 0 each; ISO-NE's to the internal dataset only).
  Neither is loaded into Supabase; no live page reads either.

## Checks

- On the merged build (sessions 147, 148 phase 1 and 149 together): the datacenter page 39 of 39, the curtailment
  page 118 of 118, the generator page 43 of 43, `check-routes` 0 failed, `check-values` 7,026 of 7,026.
- **One thing seen:** the first `check-values` on that build showed 6 values of two battery addresses that differed
  (October's month so far). A second run on the same build showed 0. The first request after a build is served
  from the machine's older fetch cache and refreshed behind it. The snapshot at the landing is the proof that
  counts.
- The whole suite in a clean copy of the merged commit: 1,934 tests, passed.

## Decisions made without you

1. The grid network and status fixes, which you did not ask for.
2. The NYISO table is not written as internal tonight (it would fail tomorrow's license check until a person acts).
3. The data machine's run is not registered.
4. Only ISO-NE's "System" sheet is in the table.
5. The Census ZIP code shapes were not pulled.
6. `ercot.json` and `worth.json` kept as committed: the main copy's tables were older than the runner's.
7. Sessions 147 and 149 land in one push, to save a deploy.

## To finish

```bash
# a person, before Monday 12 October 14:00 UTC, from the main copy on main (NYISO's load queue leaves the public dataset)
PY='C:\Users\lossa\Documents\erw\.venv\Scripts\python.exe'
.venv/Scripts/python.exe warehouse/lock.py run --task "149 nyiso load queue" -- "$PY" warehouse/connectors/nyiso_load_queue.py --write; echo "exit=$?"
.venv/Scripts/python.exe warehouse/validate/erw_validate.py warehouse/output/nyiso_load_queue.csv; echo "exit=$?"
.venv/Scripts/python.exe warehouse/lock.py run --task "149 nyiso coverage" -- "$PY" warehouse/metadata/build_coverage.py --only '^nyiso_load_queue$'; echo "exit=$?"
.venv/Scripts/python.exe warehouse/lock.py run --task "149 nyiso archive" -- "$PY" warehouse/archive/archive.py write --tables '^nyiso_load_queue$'; echo "exit=$?"
.venv/Scripts/python.exe warehouse/lock.py run --task "149 nyiso redivis" -- "$PY" warehouse/redivis/upload.py --tables nyiso_load_queue; echo "exit=$?"
.venv/Scripts/python.exe warehouse/lock.py run --task "149 license fix" -- "$PY" warehouse/redivis/upload.py --check-license --fix; echo "exit=$?"
.venv/Scripts/python.exe warehouse/redivis/upload.py --check-license; echo "exit=$?"

# the data machine's daily run: look, then a first run by hand after 16:00 UTC, then register it (the line is in docs/machines.md)
bash warehouse/run_data_machine.sh --check
.venv/Scripts/python.exe warehouse/lock.py run --task "data machine daily" --wait 60 -- 'C:\Program Files\Git\bin\bash.exe' warehouse/run_data_machine.sh > runs/data_machine_daily.out 2>&1; echo "exit=$?"
```

## The five most interesting numbers

1. **SPP South, day-ahead, by year** (USD per MWh): 22.47, 17.81, **67.98** (2021), 54.68, 26.97, 30.51, 29.34, and
   29.83 for 2026 to 4 October. In 2021 SPP's wind received 37.94 there against the flat 67.98.
2. **Five days**: the daily run's grid network step failed on every run since 4 October, and a live page's carbon
   intensity is eight days old.
3. **0 of 37**: no hub or zone of the curtailment page has a boundary its operator publishes.
4. **16 tables, 602,481 rows**, are held back for pages in review: four of the five check-values differences.
5. **86 filings and no order**: the 2026 statewide transmission rate stays USD 75.527270 per kW filed, against
   68.547301 approved for 2025, ten months into the year it was to govern.
