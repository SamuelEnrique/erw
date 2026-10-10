# Session 163 report: how soon, the measured waits

Run on 9 October 2026 (UTC), 00:33 to 01:40, unattended, in the chain 162 to 165. An agent built it in a working
copy of its own to a written brief (`runs/session163/BRIEF.md`); I merged, rebuilt its file after session 165's
write, checked the merged build and landed it. The page is `/cost-of-power`; it stays `review`.

## Three things to know first

- **A ruling for you: the figure that rests on two requests.** "Request to in service" in New York is 2 requests.
  The page shows the count and the group's two ends, "2 requests: between 1,028 and 1,339 days", not each request's
  own range. Sessions 155 and 160 already print both ranges in their reports. One line hides every figure on fewer
  than 5 (`MIN_FOR_BOUNDS` in `warehouse/derived/how_soon.py`).
- **One page check failed on the merged build, and the fault was the check's.** After session 165's write the
  internal table holds Bonneville requests named "Data Center" and "New Load": words the page already uses. No
  request was on the page. The check now searches for the names of the entities the page shows (New York ISO and
  ERCOT: 71 names): 42 of 42.
- **No sentence of any entity is shown**: each stated figure stands as written, with who stated it and a link to
  the stater's own document.

## Verdict: ready to open as it stands

What is left, exactly:

1. Your ruling on the two-request figure.
2. Bonneville and Alberta (session 165) are on none of the page's grids, so the page does not show them. A line of
   `ENTITY_GRID` would place a new entity.
3. Stated waits are also held for CAISO (2), ISO-NE (4), SPP (2) and PJM (4, from PJM's own site): not shown, since
   you asked for New York and Texas.
4. The time spent in each status, in NYISO's own words (156 rows), is not on the page.

## What the page shows

New York, measured here, in days. Source on every hover: 37 dated copies of NYISO's queue workbook, 4 September 2014
to 11 September 2026; 73 requests followed.

| Stage | Measured (count) | Still waiting, a labeled lower bound (count) | Stated by NYISO |
|---|---|---|---|
| Request to the first study status | 21: median at least 26, at most 86 | 1: too few to show | 2 weeks |
| System impact study, pending to approved | 22: median at least 414, at most 680 | 32: at least 30 to 522 | nine months; 90-day (proposed) |
| Request to a signed agreement | none yet | 47: at least 105 to 2,881 | none held |
| First study status to a signed agreement | none yet | 46: at least 30 to 2,682 | none held |
| Request to under construction | 4: between 1,153 and 2,366 | 47: at least 105 to 2,881 | none held |
| Request to in service | 2: between 1,028 and 1,339 | 51: at least 105 to 3,636 | none held |
| Request to withdrawal | 6: median at least 322, at most 760.5 | none | none held |

Texas: "not measured here" (hover: 32 of ERCOT's reports read, 0 name a request). Beside it, ten figures of Texas's
own entities, each labeled whose it is, none ours:

- Oncor, measured by itself: 825 days average, 687 median (interconnections placed in service).
- ERCOT, measured by itself: approximately 220 days average delay against the in-service date.
- ERCOT, expected: 13, 15, 16 and 14 weeks for the batch study's four steps, each on its own row and never summed;
  ten Business Days; several months; a few days to many weeks.

Every other grid reads "not measured yet". MISO reads "paused while terms are reviewed". "Rules in motion" sits
beneath, unchanged.

## The summary sentence, written by code from the numbers

- New York: "New York: 2 requests followed from request to in service took between 1,028 and 1,339 days, and 51
  more are still waiting, at least 105 to 3,636 days so far (a lower bound); 22 requests followed through the system
  impact study from pending to approved took a median of at least 414 and at most 680 days, where New York ISO
  itself states nine months."
- Texas: "Texas: no wait is measured here (0 requests named in 32 of ERCOT's reports); measured by the entities
  themselves: ERCOT approximately 220 days (average), Oncor Electric Delivery 825 days (average) and 687 days
  (median)."
- CAISO: "CAISO: not measured yet."

## Only aggregates reach the page

- One file, `site/data/datacenter/how_soon.json` (about 14 KB): 7 stages, 13 stated figures, no request.
- The builder refuses to write a file that holds a request-level field or a request's name. The two tables stay
  internal: on no page, in no live set.
- After session 165's write I ran the builder again: the stamps and row counts changed, no figure did.

## Nothing dropped

- The section's five rows are as they were. The sixth, "How long a new large load waits", read "not published
  anywhere yet" for every grid; it now reads "measured, below", "not measured here" or "not measured yet".
- Earlier checks changed on purpose: `tests/test_session138.py` (the old words stand twice, not three times) and
  three lines of `check-datacenter.mjs`.

## Pulls and spend

- **Pulls: none.** **Model spend: USD 0 of 0.**

## Checks

- `tests/test_session163.py` 38 on the main copy after the write; `test-howsoon.mjs` 25; `check-how-soon` 42 of 42
  and `check-datacenter` 58 of 58 on the merged build; `check-how-soon` 42 of 42 on production's internal view.
- Each aggregate is worked again from the raw rows in a test; every number in the sentence is a number of the file.

## The landing and the snapshot (one landing for sessions 162 to 165)

- Pushed 01:30:08 UTC as `task/162-165-chain` (`1aa3d3c`): checks passed (run 37870073120), merged as `717ae0f`.
  **Vercel: "Deployment has completed"** at 01:37:50 UTC. No freeze. No force push.
- **Snapshot before** (`162_before`, 01:29:27) **and after** (`162_after`, 01:37:57), 25 addresses: **0 differences**;
  no checked number moved (3,357 keys). The charts of `/storage`: 0 differences. Nothing was reverted.
- The whole suite in a clean copy of the landed commit: 2,610 tests, passed. As a visitor the page answers the
  in-review page.

## Decisions made without you

1. A median on 5 or more; on 2 to 4 the count and the group's two ends; on 1 the count and "too few to show".
2. The block follows the grid the address names, as "Rules in motion" does.
3. Texas's stated figures are ERCOT's and Oncor's, the two session 160 listed.
4. No stated duration is converted to days, and nothing is called longer or shorter.
5. The page check narrowed to the entities shown (above).

## The five most interesting numbers

1. **414 to 680 days against "nine months"**: 22 system impact studies measured, beside NYISO's own expectation.
2. **2 against 51**: New York loads followed into service against those still waiting.
3. **0 of 32**: ERCOT's status reports that name a request.
4. **0 measured, 47 waiting**: no New York load has been seen to reach a signed agreement between two copies.
5. **About 14 KB**: all that reaches the page of the two internal tables.
