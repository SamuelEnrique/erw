# Session 2415 report: notes for the three own choices, every point acted on; the merge with main; the Stanford draft

24 October 2026, from 11:06 UTC, on lab-desktop (the data machine), the tenth session of `queue/done/114-day-15-november-data-paraguay-panama-guatemala-namibia.md`, unattended. The notes were drafted by a helper beside sessions 2416 and 2417 and checked here. Precheck passed (`runs/c114/pre2415.out`). Model spend USD 0. Pulls: Redivis's API, 91 of 150 requests (below).

## Read these first

- **Three method notes, one for each own choice** (`eia_net_imports_monthly`, `eurostat_electricity_production_annual`, `statcan_generating_capacity_annual`), checked as session 960 checked its notes. Every point was acted on:
  - **EIA:**
    - 23 countries and territories carry EIA's area code in `x_partner`, not only the world and the groups. Session 2412's cross-check had left them out of the countries' sum. With them the gap to the world is a median of 1 kbbl/d and at most 109 kbbl/d (it said 6 and 120).
    - EIA gives no crude oil record where a partner has none, but a 0 for products and the total (11,553 and 10,390 zeros).
    - Puerto Rico and the U.S. Virgin Islands are partners, so the importer is the U.S. without them.
    - The U.S. is a net exporter in 75 of the 199 months, every month from October 2021. The report named two months only.
    - The usage line names `--out-dir`.
  - **Eurostat:**
    - The 49 country years whose TOTAL did not add were all batteries (BA100, 2020 to 2024). The check now adds them, and every country year agrees within 1 GWh (the largest gap 0.634 GWh).
    - 58 of the file's 75 products have values, and the table has rows for those only.
    - Fossil energy (FE) and bioenergy (BIOE) are totals whose parts disagree by equal and opposite amounts in 133 country years.
    - Hydro (RA100) leaves out pumped hydro, which is larger than it in 104 country years.
    - H8000 is Eurostat's undefined "Heat".
    - GEP is gross, the plants' own use included. The flag columns are blank in every row.
    - Switzerland and Liechtenstein are not in the file, Ukraine ends in 2020, and four candidates start between 2005 and 2014.
    - Session 2413's report omitted Iceland 2020 from its gross-below-net list; it is added.
  - **StatCan:**
    - 2012 has no figure: all 322 are marked .. in StatCan's file.
    - StatCan's notes are carried:
      - capacity is gross, at the generators' terminals before station service (note 3);
      - the survey grew from 400 to 1,200 establishments in 2015 (note 12);
      - solar below 100 kW counts only from 2024 (note 7).
    - Ontario's solar capacity falls from 2,295.9 MW (2017) to 1,409.9 MW (2019) while its generation rises; no note explains it.
    - The two requests were 11 seconds apart, not 2.
  - Each report is corrected in place and says so. All three tables were written again offline, with the same rows; the rewrites' metadata patches were resolved and deduplicated, and the Method cells are set.
- **The merge with main** (chains 110 and 113 landed; origin/main at 72cba70b):
  - Seven conflicts, resolved by `runs/c114/merge_resolve.py` (from chain 112's), the union resolver and the regenerated license record.
  - This chain's reads are renumbered from 636 to 695 to **703 to 762**, after main's 702, with the verdicts (the Secretaria 716, NamPower 734, Statistics Mauritius 741), the reports and the notes.
  - Test 205's bound: the conflict was resolved by hand. The two branches' raises had merged as one, so the bound was raised by 40 again; it now holds 762 reads.
  - `docs/coverage.md` held `eurostat_electricity_capacity_annual` twice, with and without its Method cell. Main's row, with the cell, was kept.
  - The release check (0 differences) and the record tests pass.
- **The Stanford draft** (`runs/c114/s2415/run.sh`, under the data lock from 11:28:27 UTC, the main checkout pulled to 1cf485c1 first):
  - A reconcile: 346 match, 46 mismatch, 5 not yet uploaded.
  - One plain upload of four public tables, proven by count, in 77 requests with the metadata tables (`erw_headers` 4,797 lines, `erw_coverage` 526, `erw_sources` 613):
    - this chain's three: `eia_net_imports_monthly` (65,501 rows), `eurostat_electricity_production_annual` (73,988) and `statcan_generating_capacity_annual` (5,952);
    - chain 113's `hagstofa_iceland_power_annual` (88), as chain 113's agent asked.
  - A reconcile: 350 match, 46 mismatch (the live tables' known drift), 1 not yet uploaded (chain 110's `eurostat_crude_imports_monthly`). Nothing released.
- **The draft script's shell was stopped by the harness for low memory** while the upload ran. The upload's python survived and finished, and was waited for, not stopped.
  - The data lock then lapsed: it was this session's at 11:33 UTC and free by 11:35.
  - By then main's copied files had been put back by another session's run in the gap (chain 117's agent reports its run touched nothing in the main checkout; chain 115's agent was asked). So the upload record's four new rows were lost.
  - They were rebuilt on the branch (`runs/c114/s2415/rebuild_record.py`) from upload.py's own `data_sha`, the rows the draft proved, and the upload process's start (11:30:42 UTC), as session 2331 rebuilt chain 108's.
  - Main's files were not touched by this session after the lock lapsed. Both running chains were told of the window.
- **`eurostat_crude_imports_monthly` was left out** of the draft. Its file is 176 MB, and an upload stopped mid-replace empties the draft table.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| redivis.com (and Supabase once) | 91 of 150 | reconcile (7), the upload (77), reconcile (7) |

## Errors

- **The draft's shell was stopped for low memory, the lock lapsed, and the record's rows were lost.** The rows were rebuilt as above. The memory note on killed shells now says to run an upload in the foreground.
- **Test 205's conflict stopped the resolver's first run.** It was resolved by hand, and the resolver run again.
- **Sessions 2412, 2413 and 2418's reports and headers carried the slips above.** Each is corrected in place and says so.

## Decisions made without you

- **The upload limited to four tables,** within the ceiling. Chain 110's 176 MB table is left for a draft run in the foreground.
- **The four record rows rebuilt** rather than uploaded again.

## For Samuel's ruling

- None new.

## Files

- New:
  - `docs/methods/eia_net_imports_monthly.md`, `eurostat_electricity_production_annual.md`, `statcan_generating_capacity_annual.md`
  - this report
- Changed:
  - `warehouse/connectors/eia_net_imports.py`, `eurostat_electricity_production.py`, `statcan_generating_capacity.py`
  - sessions 2412, 2413 and 2418's reports (corrections); sessions 2406 to 2418's reports and this chain's notes (renumbered reads)
  - `warehouse/metadata/redivis_uploads_stanford.csv` (four rows)
  - `tests/test_session205.py` (the bound)
  - the merge's files
- On the data machine only: `runs/c114/s2415/`, `runs/c114/merge_resolve.py`, `runs/c114/reads_mapping.json`.
