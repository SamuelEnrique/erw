# Session 3004 report: the landing service, then demand

6 November 2026, about 11:31 to 11:45 UTC, on lab-desktop, second window, chain 164 (the owner's), unattended. Model spend USD 0. Pulls: none.

## Read these first

- **The landing service: nothing to land.** Neither `docs/state/landing_request_portable.md` nor `docs/state/landing_request_oldlaptop.md` exists, on origin's main (`a68611f9a`) or on any branch. No branch was landed and production was not touched.
- **12 demand drafts added to the review list** (module `deep.demand`, state draft), from `warehouse/analysis/findings/deep/demand.py`, all on EIA-930:
  - **ERCOT's top ten days** averaged 1,675.5 GWh a day in 2025, against 1,418.7 in 2019 (strength 12.5). **Its mean day** was 1,339.2 GWh in 2025, against 1,051.1.
  - **The lower 48 states' top ten days** averaged 14,903.8 GWh a day in 2025, against 13,745.7 in 2019. Their mean day was 11,776.2, against 11,004.9.
  - **ERCOT's Far West sub-region:** its mean hour was 7,606 MW in 2025, against 3,682 MW in 2020. Its 99th-percentile hour was 8,763 MW, against 4,337.
  - **Dominion's zone of PJM (DOM):** its mean hour was 15,403 MW in 2025, against 11,687 MW in 2019. Its 99th-percentile hour was 22,436 MW, against 18,003.
  - **Winter against summer:** Southern Company's five highest winter days were 107.3 percent of its five highest summer days in 2025, against 90.7 percent in 2019. TVA's were 113.9 percent, against 101.2.
  - **Night demand:** in the BGE and ComEd zones of PJM, the mean from midnight to 6 AM rose to 86.9 and 88.0 percent of the all-hours mean in 2025, from 84.2 and 85.4 in 2019.
- **Six reproduction scripts** (three daily, three from the seven yearly sub-region tables) printed their expected figures exactly.

## What it did

- **`deep/demand.py`:** eight candidates. Four use the larger balancing authorities' daily demand plus the US48 total. Four use the sub-regions' hourly demand. The faults rule is the weekly hunt's: a day, or an hour, over three times its year's median is dropped, and so is a day under a third of it. 428 claims, 126 passed, 12 kept.
  - Every MISO, SPP, NYISO and ISO-NE sub-region (42 a candidate) is blocked.
- **`deep/builder.py`:**
  - **Ranking by size:** a candidate may rank its passing regions by the size of the change (`rank`). The demand candidates in MW or GWh do, so ERCOT and the US48 come before a small authority's steadier change. The Valley Electric Association's 95 MW was first by strength.
  - **Dry runs:** a dry run now writes its documents under `runs/deep/`, not `docs/findings/`. Six documents of an earlier dry run had to be removed by name.
- **The 99th percentile** is computed as Stata's `collapse (p99)` computes it (`averaged_inverted_cdf`), so the do-file and the Python agree.
- **Tests:** `tests/test_session3004.py` (3 tests), and session 3001's test updated for the dry run's new place. The chain's tests and session 258's: 38 passed.

## Decisions made without you

- **No single annual peak hour is a measure** (the weekly hunt's lesson of session 252: no measure is one interval of a year). The peaks are the year's ten highest days, and the 99th-percentile hour.
- **The larger authorities outside the ISOs are hunted.** Those are the ones whose 2025 median day was at least about 2.5 GW on average. Smaller respondents are left out, as the weekly hunt leaves them for their reporting faults.
- **Far West's p99 and mean are two drafts of one sub-region,** and so are DOM's. They are kept for the check sessions to fold if you prefer one.

## For Samuel's ruling

- None new.
