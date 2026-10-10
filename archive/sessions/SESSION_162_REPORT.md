# Session 162 report: What a generator earns, deeper

Run on 9 October 2026 (UTC), 00:33 to 01:40, unattended, first of the chain 162 to 165. An agent built it in a
working copy of its own to a written brief (`runs/session162/BRIEF.md`); I merged, checked the merged build and
landed it with the other three sessions. The page is `/cost-of-power/seller`; it stays `review`.

## Three things to know first

- **A reading of yours I had to settle: "kept as a labeled upper bound".** Session 145's "added" figure is the plant
  at real-time prices plus the battery page's figure with reserves. The new pair is energy at day-ahead prices. So
  the kept figure is not a bound of the pair by arithmetic. The section therefore holds two rows under the one head
  "Added, not co-optimized: upper bound": one on a single footing, where the two added are a true bound, and
  session 145's own three figures, kept. At the default sizes the pair is below the kept figure in all 24 cases.
- **17 files of hourly day-ahead prices are plain public addresses** (`/seller/prices/<grid>_<year>.json`), so a
  visitor can fetch them while the page is locked. They hold public prices of the five grids' main hubs only, from
  public tables. Say if they should wait behind the lock.
- **The pasted profile is priced at the grid's main hub**, whatever hub is chosen on the page.

## Verdict: ready to open, for ERCOT and CAISO (the hybrid) and all five public grids (the table, the box)

What is left, exactly:

1. Your word on the two rows (above) and on the price files.
2. The hybrid is a table with a hover on every figure; it has no chart.
3. The builder is not scheduled: `hybrid.json` and the price files age as months are added.
4. NYISO, ISO-NE and SPP read "not modeled for this grid" for the hybrid: the battery model covers two grids.
5. Not looked at on a phone; `docs/platform-tools.md` not updated.

## (a) The hybrid, side by side

USD, 100 MW plant with a 100 MW 4-hour battery, October 2025 to September 2026, day-ahead prices:

| Grid, plant | Plant alone | Battery alone | Co-optimized pair | The two added (true bound) | Kept from session 145 (foresight) |
|---|---|---|---|---|---|
| ERCOT solar | 6,328,531 | 5,388,107 | 11,637,889 | 11,716,638 | 14,125,445 |
| ERCOT wind | 9,083,025 | 5,388,107 | 13,760,078 | 14,471,132 | 16,497,075 |
| CAISO solar | 2,983,312 | 3,904,562 | 6,872,641 | 6,887,873 | 10,749,512 |
| CAISO wind | 6,662,125 | 3,904,562 | 10,190,526 | 10,566,687 | 14,308,546 |

- The battery charges from the plant or the grid; the pair's export stays inside the plant's interconnection.
- Each day is solved with that day's day-ahead prices known: an upper bound for a schedule made the day before.
  The hover and the Method note say so.
- The browser's solver and the builder's agree to 4 parts in 100 billion.
- Days solved: ERCOT 364 of 365, CAISO 363. A day with an hour of price or output not held is left out, not filled.
- The battery page's numbers did not move: none of its files is touched (snapshot below).

## (b) Capture price by hub and year

- One table: 39 hubs and zones of five grids, 2019 to 2026 and the last twelve months, solar and wind, day-ahead
  and real time. **1,248 cells: 670 held, 578 not held**, each of those a short placeholder with its reason on hover.
- Hover on a held cell: the hub's simple average, the capture ratio, the hours held, the source. Partial years are
  marked. A click on a year sorts.
- MISO and PJM are two rows of words: "paused while terms are reviewed", "licensed source needed".

## (c) Your plant's profile

- 8,760 values (8,784 in a leap year), one a line or one numeric column. A wrong count, a negative, a gap or a
  non-number is refused with a plain sentence. Nothing is repaired.
- **In a real browser: one static price file is asked for before the paste; after the paste 0 requests, and the
  address, cookies and storage are unchanged.** The face says so in one line.
- Years offered: ERCOT and NYISO 2019 to 2025; CAISO, ISO-NE and SPP 2025.

## (d) Tests

- Capture price times generation equals revenue, for every plant, hub and year shown: passes.
- The pair never earns less than the plant alone; state of charge and power limits hold every hour; a battery of
  zero size gives the plant: passes.
- `tests/test_session162.py` with session 145's: 33 tests. `check-seller-deeper` 51 of 51 and `check-seller` 43 of
  43, on the merged build and on production's internal view.

## Nothing dropped

- Every block the page showed is where it was. Session 145's three hybrid figures are the table's second row, same
  numbers. Two blocks are new: "Capture price by hub and year" and "Your plant's profile".
- Two earlier checks changed on purpose: session 145's test and `check-seller.mjs` forbade the words "upper bound"
  on the face; both now allow exactly your label and nothing else.

## Pulls and spend

- **Pulls: none.** No request to any publisher. No MISO or PJM request.
- **Model spend: USD 0 of 0.** No code of the session calls a model.

## The landing and the snapshot (one landing for sessions 162 to 165)

- Pushed 01:30:08 UTC as `task/162-165-chain` (`1aa3d3c`): checks passed (run 37870073120), merged as `717ae0f`.
  **Vercel: "Deployment has completed"** at 01:37:50 UTC. No freeze. No force push.
- **Snapshot before** (`162_before`, 01:29:27) **and after** (`162_after`, 01:37:57), 25 addresses: **0 differences**;
  no checked number moved (3,357 keys). The charts of `/storage`: 0 differences. Nothing was reverted.
- On the landed commit: site build exit 0; `check-routes` 0 failed; `check-values` 7,003 of 7,034 match, 31 latest
  prices replaced by a newer interval inside 45 minutes. The whole suite in a clean copy: 2,610 tests, passed.
- As a visitor the page answers the in-review page.

## Decisions made without you

1. The two rows (above). 2. The hybrid is offered for wind as well as solar.
3. The interconnection limit is the plant's capacity, or its highest hour when higher (ERCOT's solar fleet reaches
   1.075 of nameplate, so a 100 MW plant's limit reads 107.50 MW).
4. No discharge in an hour priced below zero, so the browser solves a plain linear program. Cost: USD 5.92 per MW a
   year on CAISO's 8-hour battery, nothing elsewhere.
5. The profile is read in local standard time with no daylight saving shift.

## The five most interesting numbers

1. **0.7 percent against 4.9 percent**: what sharing one interconnection costs an ERCOT solar plant and an ERCOT
   wind plant with a 4-hour battery of their own size (USD 78,749 and 711,054).
2. **2.3 times**: a 4-hour battery lifts a California solar plant's day-ahead revenue from USD 2.98 million to 6.87
   million, for 100 MW with 100 MW.
3. **About 60 percent** of that battery's charging is the solar plant's own output (ERCOT 60.2, CAISO 60.5).
4. **95.18 to 26.85 USD per MWh**: ERCOT solar's day-ahead capture price at the hub average, 2021 to 2025.
5. **578 of 1,248**: cells of the hub-and-year table that are not held, each saying why.
