# Session 4004 report: the third window's licenses (row 1) and the old laptop's row 10 (to `ed900cd13`)

Energy Research Warehouse (ERW). Chain 228, the desktop's second window, 13 November 2026 from 12:03 UTC. Opus 5.5. Model spend: USD 0.

## The gate: `wip/w2-4100-lic2`

- **What it holds:**
  - `57c5df6c9`, the licenses row's head `3ab353fcc` and its request file's commit;
  - `origin/main`;
  - `ed900cd13`, row 10's head at 11:47.
- **The first start (11:48) waited behind window A's gate.** It took the lock at 12:03, then stopped at its merge of main: window A's landing had changed `package/llms.txt`.
  - The conflict lay only inside the catalogue, which `scripts/build_llms.py` writes. Window 3 resolved the same conflict this morning by regenerating, so the same was done here.
  - `--check` exit 0; `licenses.py check`, `build_tables.py --check`, `release_v1.py --check` and `check_spec.py` exit 0.
  - The catalogue's tests (3298, 4101, 4109, 207, 378, 275, 205, 1001, 1008) pass.
- **The second start (12:09) took the lock at once** (`080bc12b`):
  - the suite: 8,716 tests OK, 382 skipped;
  - `npm ci`, the build and serve passed;
  - **check-values failed with two new failures, both from the hold of `policy_actions`** (`cv_diff`: 3 failures, 1 known, 2 new):
    - **`/policy?view=week`, `event_count|policy_actions|since|2026-10-14`: the page showed "0" where the live set holds 151. This is a real fault.** The count carries an `event_count|` key, and `Num`'s `heldBy` read a table from `event|` and `entity|` keys but not from `event_count|`. So the held table's count was drawn from its empty held rows as a number, where it should have said "license needed".
    - **`/policy`'s floor:** 0 checked numbers and 1 held mark against a floor of 10. This was expected: the row says `/policy` loses `policy_actions` and `policy_reads`.
  - The hand checks passed: check-routes, check-cross-checks and check-csp.
  - **Not landed.** The fix is small and plainly correct, so it was made on the licenses stack in `wip/w2-land-b` (session 4005), which holds rows 1 to 4. That branch is gated in place of this one.

## While it ran

- **The third window superseded rows 1 to 3 with row 4** (`wip/4150-licenses`), which holds them.
- **A fourth window asked for `wip/4200-forecast`** (row 1 of `landing_request_desktop_w4.md`, `/impact` as the forecast).
- **Row 10 moved to `88893595d`.**
- **These three are combined as `wip/w2-land-b`** for session 4005, from `origin/main`:
  - `docs/state/data_requests_licenses.md`: main's rows 16 to 26 kept, since the branch's side of the hunk was empty;
  - `package/llms.txt`'s catalogue written again;
  - the five checks exit 0;
  - the 15 changed test files with 4000, periodicals, 1903, 412 and 579: 382 tests OK.

## Decisions made without you

- **A generated file's conflict is resolved by running its generator,** as window 3 did for `package/llms.txt`.
- **A request file's conflict keeps main's rows** when the branch's side adds nothing.

## For Samuel's ruling

- None.
