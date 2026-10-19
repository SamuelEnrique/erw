# Session 307 report: the packs' data-side rulings

19 October 2026, 09:17 to about 09:40 UTC, unattended, on lab-desktop (the data machine), the third session of the chain of 19 October. Model spend USD 0.

## Read these first

- **OASIS now serves CAISO's prices from 6 July 2023, eight days older than session 273 found** (14 July 2023 on 14 October). Those eight days, both hubs, day-ahead and real-time, are in `iso_hub_prices_history`: 1,920 rows, every day complete, 27 requests of the 400 allowed. The probes of 8 January, 11 April, 27 May, 19 June, and 1, 4 and 5 July 2023 answered "No data returned for the specified selection"; 6 and 7 July were served. **Nothing older exists to pull.**
- **Datacenter 2c: TNMP's rider DCRF is one charge, so it is counted once.** The conditional total for Texas-New Mexico Power at 100 MW falls from USD 7.10 to 7.09 per MWh (0.0087; 0.87 at 1 MW). Sheet 141 (numbered 138.1) prints USD 635.58 "Per ESI ID" and "Per Meter" either side of one class name. Rate Schedule 6.1.1.1.5 (page 102) serves "one Point of Delivery and measured through one Meter", and the rider's formula divides each class's revenue by one set of billing determinants.
- **Generator 2c: EIA-930's CAISO wind rises with SunZia, so it appears to count that plant.** In September, EIA-930's figure rose 912 MW year on year and CAISO's own rose 1,219 MW. This is a finding in `generator_earns_algorithm.md`; no number changed. EIA-930's May to August 2026 hours are not held, so the May step itself was not seen.
- **Generator 3b and grid 5a were not done; for your ruling.** Berkeley Lab's one terms read, www.lbl.gov/disclaimer/, answered HTTP 404. For the Electric Power Annual, no file of generation by balancing authority could be identified without first reading EIA's table index, so nothing was sent. EIA's own explainer says the hourly sums do not match the Annual: distribution-connected generation is not in EIA-930 ([Today in Energy 65344](https://www.eia.gov/todayinenergy/detail.php?id=65344), from a web search, not read).
- **Datacenter 4a was already done:** `scarcity_hours_by_grid` is in the live set (178,886 rows, the same SHA-256; the loader skipped it).

## What to review

1. `warehouse/derived/texas_delivery_review.json` (`same_charge_as` on the per-meter row) and `warehouse/derived/datacenter_page.py` (rows so marked are left out and counted under "the same charge printed twice").
2. The new paragraph under 12.3 of `docs/methods/generator_earns_algorithm.md`.
3. `docs/methods/battery_stack.md`, "Only days the model solved count": the July 2023 notices (20, 25, 26 July) stay outside the model, which counts only whole months and has no reserve prices before 14 July.

## Pulls against their ceilings

| Pull | Ceiling | Used | Result |
|---|---|---|---|
| CAISO OASIS, DA and RT hub prices before 14 July 2023 | 400 | 27 (1 redirect, 1 probe of 13 July, 9 probes for the edge, 16 for the eight days) | 6 to 13 July 2023 written; the edge is 6 July |
| EIA Electric Power Annual, generation by BA | one file | 0 | no such file identified; nothing sent |
| Berkeley Lab's terms page | one read | 1 (and its robots file, which allows it) | HTTP 404, recorded as read 42 in `license_reads.csv` |
| TNMP tariff sheet 141 | one read | the copy held in `warehouse/raw/texas_delivery/` (6 October), no request | read; see above |

## The rulings

| Item | What was done |
|---|---|
| Generator 2c | the finding in the methods note; no number changed |
| Generator 3b | not recorded: the read answered 404; Berkeley Lab's verdict is as it was (read 14, HTTP 403 on 12 October) |
| Generator 9a | CAISO's history from 6 July 2023 (OASIS's edge). CAISO's notice days are in `battery_stack_stress_daily` (sessions 246 and 273: ten events from 15 August 2023); the new days add none (decision 3). `grid_stress_days` rebuilt: CAISO judged by price from 31 May 2024 (was 8 June), 58 stress days as before; loaded |
| Datacenter 2c | one charge, counted once: 41 delivery rows become 40 in `site/data/datacenter/texas_delivery.json`; TNMP's conditional total is 7.09 |
| Datacenter 4a | already in the live set |
| Grid 5a | not done (above) |

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py --what "session 307"` | 0 | |
| `hub_history.py backfill --iso caiso --start 2023-07-06 --until 2023-07-14` under the lock | 0 | 384 DAM and 1,536 RTM rows new, 0 replaced |
| `table_stores.py iso_hub_prices_history grid_stress_days` | 0 | Redivis count(*) 592,554 and 226 |
| `load.py --no-vacuum --only '^grid_stress_days$'`, and `'^scarcity_hours_by_grid$'` | 0, 0 | match 226; match 178,886 unchanged |
| `datacenter_page.py --out-dir runs/s307_dc` | 0 | the one TNMP row gone; the matrix and every other row equal |
| `scripts/licenses.py tables`, then `check` | 0, 0 | 201 tables, 0 problems (the two tables of session 306 added) |
| tests 140, 236, 246, 265, 273, 297, 298, 306 | 0 | 94 tests; four pins follow (41 to 40 rows, 7.10 to 7.09, the left-out count, the battery note's wording) |

## The landing

- freeze 0; before `s307-before` 09:37:00 UTC; merged origin/main (nothing new); pushed 09:37:07 (`65a28c7e`); deployment 7170432562 success 09:38:41; after `s307-after` 09:39:22; compare: **0 differences on 25 pages** (expected: every page is in review).
- A follow-up commit with session 308 carries `counted_once` in the delivery file (below).

## Decisions made without you

1. **TNMP's two lines are one charge** (pack option b): the schedule's one meter and one point of delivery, and the formula's one billing determinant a class. Reversible: remove `same_charge_as` from one row of the review file.
2. **The held copy of the tariff was read, not a new download**: the prompt allows one read, and the pack's option (c) is to read the sheet again on the data machine.
3. **The battery model is not rebuilt for the eight days:** it counts whole months from August 2023, and July 2023 is not whole.
4. **`capture.json` and the other files built from the history are left for the data machine's nightly run** to rebuild with the eight days.
5. **The decisions block's line is data, not page code:** `texas_delivery.json` now carries `counted_once` (the utility, the two units, the page and why); the block's figures follow the file on their own (7.09), and showing the line's words is the code machine's.
6. **No Electric Power Annual request:** the ceiling is one file, and the file was not known; spending it on an index would not have given the table.

## For Samuel's ruling

- Generator 3b: name Berkeley Lab's terms address (www.lbl.gov/disclaimer/ is 404), or let session 311's sweep find one.
- Grid 5a: name the EIA file (the Electric Power Annual seems to have no table by balancing authority), or allow EIA-923's plant-level annual generation summed by its balancing authority code.

## Files

- New: this report.
- Changed: `warehouse/derived/texas_delivery_review.json`, `warehouse/derived/datacenter_page.py`, `site/data/datacenter/texas_delivery.json`, `docs/methods/generator_earns_algorithm.md`, `docs/methods/battery_stack.md`, `docs/methods/stress_days.md`, `warehouse/derived/stress_days.py`, `docs/reviews/packs/datacenter.md`, `warehouse/metadata/license_reads.csv`, `license_tables.csv`, `coverage.csv`, `docs/coverage.md`, `archive_manifest.csv`, `redivis_uploads.csv`, tests 140, 236, 265, 273; session 306's report (its landing).
