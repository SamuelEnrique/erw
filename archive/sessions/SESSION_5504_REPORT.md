# Session 5504 report: chain 269, item 4: the price years rebuild, a ready script and a request row

Energy Research Warehouse (ERW). Chain 269, portable laptop window P1, 14 November 2026, about 09:13 to 09:30 UTC. Opus 5.5. Model spend USD 0. Branch `wip/5500-closeout`.

- **The script:** `scripts/price_years_rebuild.py`, standard library only.
  - No flag: a check. The build into a temporary folder (`warehouse/derived/price_years.py --out-dir <tmp> --live`, no lock), then each default window (the last twelve months) set beside the live set's, read with the anon key. No table is written in the repository (the builder keeps its run log in `warehouse/output/logs`, not in git).
  - `--apply`, for window A on the data machine: refuses unless the role is `data` and `scripts/freeze.py status` exits 0; takes the data lock; runs the build, the validator on the one file, the coverage row (`build_coverage.py --only`) and the load (`load.py --only '^price_years_by_window$'`), each exit code read, the first failure stopping the rest; releases the lock in every case; reads the live set back and fails unless every default window equals the file's and every row is this run's. Rule 8's snapshot before and after only if one of the three pages is live (none is).
- **Its check run here** (09:16 UTC): 2,754 rows, 45 proofs equal (the battery's 18 configurations against the page's own stat and the live set, the generator's 12, the datacenter's 3). **134 default windows move**, the faults rows' among them: CAISO's 4-hour battery 79.31 to 79.80, `LZ_NORTH`'s flat load 33.73 to 34.07, CAISO's 28.58 to 29.72, each the page's own headline. ERCOT's battery (81.40) and the generator's solar (59.85) do not move. Output: `runs/pyr5504_check.out` in the main checkout.
- **The request:** `docs/state/data_requests_five_tools.md` row 5 (one command, what it does, the check's figures), row 4's state pointing to it. Both reach window A with this stack's landing; nothing waits on them here.
- **Test:** `tests/test_session5504.py` (14 tests, no network, no write): the comparison; the CSV and its proof line; the live read by origin, paged, with the anon key only; the order of the steps, a failure stopping what follows with the lock still released; a code machine and a freeze refused before any step; a load that does not read back is not proven; the snapshot only with a live page; the files named exist and the table is in the live set and not loaded as a union; the request row; no dash. 14 passed; the 6 older test files on the request file and the price years: 65 passed, 2 skipped.

## Decisions made without you

- The script checks the freeze although no page that reads the table is live: a freeze is a reviewer at the site, and the table feeds three pages in review.
- It loads the one table (`--only`), never the whole live set.

## For Samuel's ruling

- Ruling 2 (whether the build joins the data machine's daily run) stays open; the script is what either answer runs.
