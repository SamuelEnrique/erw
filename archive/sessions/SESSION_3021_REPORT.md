# Session 3021 report: the Stata files, read

6 November 2026, about 13:56 to 14:02 UTC, on lab-desktop, second window, chain 164 (the owner's), unattended. Model spend USD 0. Pulls: none.

## Read these first

- **A fault in six kinds of do-file, fixed before you run them:**
  - **What was wrong:** they ranked rows with `gsort year -x` and then ran `by year:`. As I understand Stata, `gsort` with a descending key does not mark the data as sorted, so `by year:` would stop with "not sorted". I cannot run Stata here to confirm it, so I fixed it by the safe form.
  - **The fix:** `generate double neg_x = -x` and `bysort year (neg_x): generate long rank = _n`. Same ranks, same figures, and the data marked as sorted.
  - **Where:**
    - the top tenth of days (prices)
    - the dearest one percent of hours (prices)
    - winter's dearest hours
    - demand's top days and its peak against the mean
    - winter against summer
    - batteries against the peak
  - **The 11 drafts whose files held it** were rebuilt under their own ids (`--replace`). Their figures are unchanged; their stored and documented do-files carry the fix.
- **Every do-file read against its Python script and your rules: 156 of 156 hold** (`deep/check_do.py`):
  - The `* Expected:` line at the top is the Python script's.
  - No line continuation, and one command per block.
  - Every import reads strings, and every destring says `force`.
  - No `gsort` before `by`, and no brace left from the code that wrote it.
  - Each file ends by listing year, measure and n.
- **Each kind of file was also read by eye against its generator** (the price hours, the daily spreads, the demand sub-regions' seven yearly imports, the state shares, the heat rates, the queue's dates, the cracks and the pump), and they take the same steps as the Python. Stata's `collapse (p99)` and numpy agree because the module uses Stata's percentile definition (session 3004).

## What it did

- **`deep/check_do.py`** and **`tests/test_session3021.py`** (2 tests). With the tests of the modules touched: 16 passed.

## Decisions made without you

- **No do-file was run.** This machine has no Stata. The expected figures at each file's top are what your run must print, within 0.5 percent of the change.

## For Samuel's ruling

- None new.
