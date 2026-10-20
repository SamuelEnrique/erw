# Session 323 report: the EIA annual file and the Grid cross-check

19 October 2026, from 21:08 UTC (the reading) and 22:59 UTC (the writes), unattended, on lab-desktop (the data machine), the third session of the chain of 19 October, daytime. Model spend USD 0.

## Read these first

- **The Electric Power Annual has no table by balancing authority**, so the annual figure is Form EIA-923's. The Annual's index (https://www.eia.gov/electricity/annual/) gives net generation by source, sector and state only; the words "balancing authority" are not on it. EIA-923's annual workbook names each plant's "Balancing Authority Code" and its year's "Net Generation (Megawatthours)".
- **`eia_annual_generation_ba`: 515 rows, 68 entities, 2023 to 2025** (EIA-923 Final files), net generation, storage net generation and plants, by balancing authority and year. **`eia_annual_crosscheck_ba`: 144 rows**, EIA-930's hourly sums against it for CISO, ERCO, ISNE, MISO, NYIS, PJM, SWPP and the Lower 48. Both validated, in coverage, archived, in the draft, loaded (`match ... 515`, `match ... 144`) for the Grid tool's decisions block, under `review_hold`.
- **The gaps (EIA-930 less EIA-923, percent of EIA-923, 2023 / 2024 / 2025):** CISO -9.18 / -8.35 / -8.72; ERCO -7.53 / -7.62 / -10.45; ISNE -6.51 / -5.52 / -4.91; MISO -6.29 / -5.52 / -6.68; NYIS -4.53 / -3.10 / -3.09; PJM +0.06 / -0.80 / -0.48; SWPP +3.04 / +2.62 / +3.05; US48 -4.27 / -4.38 / -4.76. EIA-930's missing hours (2 to 48 a year) explain none of it. The likely reasons are written as hypotheses, not EIA's statements: EIA-930 is what a balancing authority meters, EIA-923 each plant's own net generation (self-generation used on site among it); SPP meters plants EIA-923 codes elsewhere.
- **The Grid pack's question 5 is answered** in `docs/reviews/packs/grid.md` (section 4's row and the rulings paragraph). The page's words are the code machine's.

## What to review

1. `docs/methods/eia_annual_crosscheck.md`, especially the reasons' wording.
2. `warehouse/connectors/eia923_annual_ba.py`: `sums` (blank code is `none`; EIA's "State-Fuel Level Increment" rows are `state_fuel_increment`).

## Pulls against their ceilings

| Request | Address | Answer |
|---|---|---|
| 1 | https://www.eia.gov/electricity/data/eia923/ | 200, the zips by year |
| 2 | https://www.eia.gov/electricity/annual/ | 200, no table by balancing authority |
| 3 | https://www.eia.gov/electricity/data/eia923/archive/xls/f923_2023.zip | 200, 22,359,936 bytes |
| 4 | https://www.eia.gov/electricity/data/eia923/archive/xls/f923_2024.zip | 200, 22,755,334 bytes |
| 5 | https://www.eia.gov/electricity/data/eia923/xls/f923_2025.zip | 200, 23,340,452 bytes |

5 of 5. EIA-930's hours came from the workbooks this machine's daily run saved at 17:24 UTC (no request).

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py --what "session 323"` | 0 | |
| `eia923_annual_ba.py --from-raw ...` under the lock | 0 | 515 rows |
| `eia_annual_crosscheck.py`, first | 0 | its coverage step then exited 1: the "Derived from" line named the workbooks, which the builder reads as tables; moved to a line of their own |
| the same, again; `table_stores.py`; `load.py --only` both | 0, 0, 0 | match 144 and 515; sources 322 |
| snapshots `s323-before`/`after`, `s323b-before`/`after` | 0, 0 | 0 differences each |
| `tests.test_session323` | 0 | |

## Decisions made without you

1. **EIA-923 in place of the Electric Power Annual**, as the prompt allows when the Annual has no table by BA; the five requests were spent on the two index pages and three years (2023 to 2025, all Final).
2. **Storage counts in EIA-923's figure** (Page 1 Energy Storage, negative), since EIA-930's net generation carries batteries.
3. **The Lower 48 is EIA-923's sum over every code but `none`, `HECO` and `state_fuel_increment`.**

## For Samuel's ruling

- Whether the decisions block should show the gaps (the code machine's page), and in what words: the reasons are hypotheses.

## Files

- New: `warehouse/connectors/eia923_annual_ba.py`, `warehouse/derived/eia_annual_crosscheck.py`, `docs/methods/eia_annual_crosscheck.md`, `tests/test_session323.py`, this report; `warehouse/raw/eia923_annual/s323/` (not in git).
- Changed: `docs/reviews/packs/grid.md`, `warehouse/supabase/live_set.yaml`, `warehouse/metadata/build_coverage.py`, `coverage.csv`, `docs/coverage.md`, `sources.csv`, `archive_manifest.csv`, `redivis_uploads.csv`.
