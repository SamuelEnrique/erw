# Session 3298: tool 15's rigor layer (llms.txt's catalogue, the package, the method notes)

Energy Research Warehouse (ERW). Personal laptop (portable-laptop), third window, 6 November 2026, Opus 5.5, unattended. Branch `wip/3298-package` (head `b788d3a6d`, cut from `origin/main` `6094b647a`, `origin/main` merged at `3a25f8135`); landing row 15 of `docs/state/landing_request_portable.md` (task `3295-package`, port 3395), pushed to main alone as `7286bcbae`. No site build, no landing gate, no data lock, no model call, nothing sent.

## Session number

- **3298**, the first free at or above 3295: 3283 to 3296 are named by `queue/next/204-day-22-november-data-large-load-continued.md` (chain 185's successor, on origin's main), 3297 by `wip/3297-askeval2`; 3298 by no commit, file or branch. 3300 upward are the desktop's.

## What was built

- **`scripts/build_llms.py`** writes the catalogue as the last section of `package/llms.txt` (`## 10. Every table`, between two marker lines), never by hand. Sources: `coverage.csv` (the list, period, granularity), the package's license record (`erw.licenses.build`: verdict, live-set window, the same list `erw/data/tables.csv` ships), `sources.csv` (publishers), the Redivis release records (`docs/redivis/release-v1-stanford/` then `release-v1/`: description, units), `build_coverage.method_notes()` (the method note, the rule `docs/coverage.md` uses), `redivis_uploads_stanford.csv` (the Redivis address) and `site/lib/pages.ts` (the pages). `--check` compares all but the date line.
- **`site/public/llms.txt` does not exist**, and there is no `llms-full.txt`: the site serves `/llms.txt` from `package/llms.txt` (`site/scripts/build-content.mjs` into `content/llms.json`; internal view only while in review). The catalogue went there.
- **Ask's prompt is unchanged**: `warehouse/chat/ask.py` cuts the catalogue from the briefing; `site/lib/chat/spec.json` is untouched; `check_spec.py` exits 0.
- **Kept fresh**: `build_coverage.py` runs the generator after every build (a failure is printed, coverage stands); `package/llms.txt` joins the commit lists of `daily-prices.yml` and `run_data_machine.sh`.
- **The test (part 4)**: `tests/test_session3298.py` fails when the catalogue's `Generated:` time is older than coverage.csv's newest `last_run`. It also checks that every table appears once, that public matches the package's public, the seven cells, held lines with no figure, that the method notes exist, that the pages include Ask and the periodicals, that the chat leaves the catalogue out, and that the file has no dash.
- **Package**: README section "The tables" and its test paragraph; `erw/__init__.py` and `api.tables()` docstrings name the catalogue. `build_tables.py --check`: 637 shipped, 637 in the record, 0 differ (before and after). Wheel `erw_energy-0.1.0-py3-none-any.whl` built offline, installed in a scratch venv (pandas 2.3.3 from the index), README example run as written from outside the repository with `ERW_DATA_DIR` on this laptop's tables: every line ran, 247 rows of Henry Hub for 2025 (the README's figure), `erw.tables()` 637.

## Tables listed

- **637**: **471 public**, **166 held** (114 internal, 52 unsettled; 42 of the 166 are the "license needed" rows of `license_status.csv`).
- Public downloads: 39 from the site's `/api/download` (live set), 421 from Redivis `datapages.erw` (draft until a person releases a version), 11 none yet: `energinet_dk_production_hourly`, `ercot_wind_solar_hsl_monthly`, `eurostat_gas_imports_monthly`, `eurostat_solid_fuels_monthly`, `ons_brazil_balance_hourly`, `sne_panama_electricity_annual`, `sne_panama_generation_monthly`, `statbank_moldova_electricity_monthly`, `statsmu_mauritius_electricity_annual`, `usbr_crsp_reservoirs_daily`, `usbr_mead_powell_daily`.
- 73 public tables have no unit in the release records (written "not recorded"); 39 descriptions are the source report (their recorded title is a restore note); 41 are cut at 220 characters, ending in "[...]".
- The pages: 34 (the periodicals, Ask, then each menu group). Size: 283,681 bytes (it was 55,212).

## Tests

- **Before, `package/tests` in the main checkout with this laptop's 115 local tables** (the README's line, as sessions 1035 and 1505 ran it): **stopped by Claude Code for low memory at about 74%**. Many failures in the first 29% (the progress line); the output was lost with the stop. Not started again.
- **Before, on the worktree without local tables**: 3 failed, 51 passed, 79 skipped. All 3 failed because the venv imported the main checkout's editable `erw`. With the branch's own `erw` on the path, 5 failed, each on a table the checkout lacks.
- **After**: the 5 were each read and skip with their tables named (`_needs`), none deleted: `test_public_functions_only_use_the_backend_interface` (an ISO-named table), `test_fetch_subsets_rows_by_time_and_node` (`iso_rtm_hub_prices`, `iso_dam_hub_prices`), `test_cite_names_every_report_even_from_earlier_runs` (`iso_rtm_hub_prices`), `test_eia860m_tables_one_vintage_and_the_right_statuses` (the three inventories), `test_old_names_work_through_the_map` (`eia930_all_demand`, `iso_trader_daily`, `iso_rtm_hub_prices`). `package/tests`: **49 passed, 84 skipped, 0 failed**.
- Repository tests that read llms.txt, the spec or the package's documents (3298, 1001, 1008, 1011, 207, 266, 267, 445, 535, 536, 65): 150 passed, 6 skipped. Test 536's five clean-install tests failed only under a PYTHONPATH I had set; without it, 5 of 5. The whole suite was not run (memory).
- **The 108 (now 150) local failures were not read one by one**: the run that shows them is the one that was stopped. They wait for a machine with the memory (the desktop, or this laptop with nothing else open).

## Method-note gaps (for the desktop's method-note sessions)

- **No public table lacks a method note**: 471 of 471 have one that exists (362 named after the table, 109 through a note's `Tables:` line). The 166 held have one too. No note fails to name its table, and none is under 800 bytes.
- **`docs/coverage.md`'s Method cell disagrees with the rule for 15 public tables**. The page is generated, and a carried-over line keeps its old cell, so the fix is the data machine's next full coverage build (or `with_method` refreshing a carried line's cell):
  - empty, where a note exists: `ercot_all_hub_prices_history` (iso_dam_hub_prices.md), `ercot_wind_solar_hsl_monthly` (ercot_wind_solar_hsl_hourly.md), `eurostat_crude_imports_monthly`, `flex_alert_effects` and `flex_alert_model` (flex_alert_scorecard.md), `gas_balance_weekly`, `generator_pipeline_by_grid`, `grid_stress_yearly` (grid_stress.md), `hagstofa_iceland_power_annual`, `iso_queue_snapshot_summary`, `nuclear_fleet_status`, `sne_panama_electricity_annual` and `sne_panama_generation_monthly` (sne_panama.md), `statsmu_mauritius_electricity_annual`;
  - a different note: `spp_as_quantities` links `reserve_quantities_nyiso_spp.md`; the rule now gives `spp_as_quantities.md`.

## Rule 8 (the push of row 15 to main)

- No freeze (`scripts/freeze.py status` exit 0). Before snapshot `s3298-row-before`: 25 pages, 0 failed (21:29 UTC). After `s3298-row-after` (21:30 UTC): `compare` exit 0, **0 differences on all 25 pages** (expected: both pushes touch only `docs/` and `archive/`, and every page is in review). That after was taken about 90 seconds after the push and may predate the deploy. A later after snapshot, covering this report's push too, is compared with the same before and given in the session's closing message.

## Decisions made without you

- Session 3298, not 3295: the first number no file, commit or branch names (3295 and 3296 are queue 204's).
- The catalogue lives in `package/llms.txt` (what `/llms.txt` serves), as its last section between markers. Sections 0 to 9, written by sessions, are kept (rule 3). No `site/public/llms.txt` or `llms-full.txt` was made.
- Ask's briefing leaves the catalogue out, which keeps the cost of a question and the evaluated prompt as they were.
- A held table's line reads "license needed (internal)" or "(unsettled)": the prompt's words, with the verdict. The ERW's own operating tables (`api_cost_ledger` and others) are listed the same way.
- "Public" is the package's verdict `public`. coverage.csv's `license` flag is not used: it still says public for the 42 tables held for a license.
- Description, when the release records hold none (or only a restore note): the publisher and report from `sources.csv`. Unit: from the release records, else "not recorded". Nothing read from local tables, so every machine writes the same file.
- Download: the site when the live set holds the table, else Redivis when `redivis_uploads_stanford.csv` records the upload, else "none yet".
- The generator runs inside `build_coverage.py`, and `package/llms.txt` is in the two daily commit lists, so the staleness test cannot fail main on the next coverage build. Every session that adds a table now commits `package/llms.txt` with coverage.
- The README example ran with `ERW_DATA_DIR` on local tables, not the live set or Redivis (no request). pip fetched pandas from the index for the scratch venv.
- The task name is `3295-package`, as the prompt gave it, though the session is 3298.

## For Samuel's ruling

- **Held tables are named in `/llms.txt`**, which the site serves (to the internal view only while in review). The site's rule since session 1014 keeps internal tables' names off it (`tests/test_session1008.py` checks the downloads' files). When `/llms.txt` opens to visitors, should the held names stay?
- **Size**: `/llms.txt` is now about 284 KB. The llms.txt convention keeps the index short and puts the long text in `llms-full.txt`. Should the catalogue move there?
- **Sections 2 to 7 are hand-written and older than the catalogue** (they date from about 113 tables). Rewrite them, trim them to the families, or leave them?
- **73 public tables have no unit in any committed record**: should their units be written into the release records (the desktop has the files)?
- **11 public tables have no download address yet** (listed above): upload to Redivis, or leave them until the release?

## To finish

- Land row 15 through the desktop's landing service (`scripts/land_check.py`, task `3295-package`, port 3395). It may conflict with row 12 in `warehouse/chat/ask.py`; the two changes are in different places. On any conflict in `package/llms.txt`, run `python scripts/build_llms.py`.
- Run `python -m pytest package/tests -q` on a machine with the memory, and read the local failures one by one.
