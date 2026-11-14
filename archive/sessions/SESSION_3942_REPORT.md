# Session 3942 report: noaa_grid_weather's ISD-Lite address

Energy Research Warehouse (ERW). Chain 267, data machine (lab-desktop), 14 November 2026, 09:49 to 09:53 UTC. Opus 5.5. Model spend USD 0. Requests: 7 (www.ncei.noaa.gov 3, noaa-isd-pds.s3.amazonaws.com 4), robots read first; `runs/c267/s3942/probe.csv`.

- **Robots:** www.ncei.noaa.gov allows `/pub/`; the bucket has no robots file (404).
- **The old address answers the wrong thing:** `www.ncei.noaa.gov/pub/data/noaa/isd-lite/2024/722590-03927-2024.gz` answered 200 after a redirect to `noaa-isd-pds.s3.amazonaws.com/index.html#isd-lite/`: the bucket's HTML index, 32,357 bytes. The connector's parser reads bytes that are not gzip as text, so a new download would have been parsed as an HTML page.
- **The new address:** `noaa-isd-pds.s3.amazonaws.com/isd-lite/data/<year>/<USAF>-<WBAN>-<year>.gz` (the bucket's listing; the test file 88,412 bytes). The station list `isd-history.csv` is still served at NCEI's address (2,914,601 bytes).
- **The fix:** `LITE` is the bucket's address; a year's file saved from the old address before the move (the 245 of `pull_2026-10-05`, all gzip) is reused as saved, never fetched again; a body that is not gzip is refused. The header names both addresses. Test 3942 (5 tests).
- **The trial** (the branch's connector from the main checkout, `--out-dir` in the scratchpad, no request): 528 saved files reused; 245 station rows, 1,913,253 hourly, 118,990 daily, the same counts as the run of 9 November.
- **Not rebuilt under the lock:** the rows are the same as the table's; only `source_url` would move (about 6.7 million rows across the four tables). The next weekly run writes it with the new code once the branch lands.
- **Seen, not changed:** the stations end at 2026-10-26 in both the run of 9 November and this trial (the Local Climatological Data tail did not move). The cause was not looked into here; left for the runs' session (3934).

## Decisions made without you

- **No rebuild of 6.7 million rows to move one address column;** the weekly run does it.

## For Samuel's ruling

- None.
