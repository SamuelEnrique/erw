# Session 3941 report: the total interchange of November and December 2025

Energy Research Warehouse (ERW). Chain 267, data machine (lab-desktop), 14 November 2026, 09:36 to 09:49 UTC. Opus 5.5. Model spend USD 0. Requests: www.eia.gov's robots file (1, `runs/c267/s3941/probe.csv`), the six-month file (1), EIA's API (1 count by hand, then the connector's own: 1,692 rows pulled).

## What was found

- **The checkpoints:** `2025-11.csv` 334 rows and `2025-12.csv` 735, against about 2,200 a month. The API was asked again: it still answers 1,067 rows for the two months.
- **EIA's six-month file** `EIA930_BALANCE_2025_Jul_Dec.csv` (48,256,021 bytes, Last-Modified 13 November 2026 15:40 GMT, saved under `warehouse/raw/eia930_daily_total_interchange/sixmonth/`): its "Total Interchange (MW) (Adjusted)" summed over EIA's Eastern day **equals the API's daily value, rounded to the MWh, on 6,811 of 7,074 balancing authority days of July to October 2025 (96.3 percent)**, not on all. The others differ by EIA's later revisions: PACW 119 days (by thousands of MWh), SOCO 59, AECI 30, LGEE 20 (a few MWh). The file holds no region (CAL, CAR, CENT, FLA, MIDA, MIDW, NE, NW, NY, SE, SW, TEN, TEX, US48).

## The fix

- **The connector** (`eia930_daily_total_interchange.py`): a past month whose checkpoint holds fewer than 90 percent of the median rows a day of the other checkpoints (last two years) is asked again; each balancing authority day the API still lacks is taken from the six-month file, only when every hour of that Eastern day is there with a number (23, 24 or 25). Those rows carry the file as `source` and `source_url`; the header has a "Filled:" line.
- **Test 3941** (9 tests, made-up numbers): the short months found, February not short for its days, the fall-back day's 25 hours, a missing or blank hour left out, a fill never repeating an API day.
- **Rebuilt under the data lock:** 216,515 rows; **2,779 days filled** (1,521 in November, 1,258 in December); validated, archived (2,835 rows new or changed), in coverage. The table's citation names the file beside the API (`build_tables.py`).
- **The method:** `docs/methods/grid_network.md`, a paragraph before "Three measures".

## A loss this run made, from EIA's side

- **EIA's API now ends at 9 November** (yesterday's run reached 12 November), so the rebuild has no 10 to 12 November: **213 rows fewer**. The archive recorded them as 213 deleted keys (`restore.py` can bring them back). The next daily run asks the current month again.

## Decisions made without you

- **The six-month file fills the gap though it matches the API on 96.3 percent, not all, of the days compared:** it is EIA's own published series of the same form, every filled row names it, and no figure is made.
- **Regions stay absent** where the API lacks them: summing members would be an ERW figure, not EIA's.

## For Samuel's ruling

- **The prompt said the six-month files fill the gap "exactly".** On the days both hold they agree on 96.3 percent (EIA's revisions explain the rest). Default: filled as above, the difference said in the method.
