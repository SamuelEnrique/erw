# Session 34 report

Energy Research Warehouse (ERW), session 34, run 2026-09-29 23:45 to 2026-09-30 02:30 UTC, unattended. **Wall time about 2 hours 45 minutes.** The time went to the workbook pass (12 minutes), coverage (14 minutes a build now), the archive (three runs, two fixes) and the package suite (13.5 minutes).

**API spend: USD 0.3903 against the USD 4 cap** (`ERW_SPEND_CAP_USD=4`, `ERW_SESSION=34`): three Thesis Builder calls, the ledger's only session 34 rows. The one approved model run; no other model call.

- **No pull:** every new row comes from files saved under `warehouse/raw/` or tables already in the warehouse.
- Nothing deleted from Redivis; nothing released; no force push; no new page; no gate code changed.
- All nine items are done, one commit each, then Part D.

## 1. /storage: CAISO from CAISO's own data: done

- **`storage_daily_cycle` gets CAISO rows** from `caiso_battery_storage`:
  - CAISO's Today's Outlook "Total batteries", 5-minute values averaged to hours, then the same five variables as the EIA-930 BAs;
  - complete Pacific days only;
  - entity `caiso:ISO`, `ba` `ciso`.
- **Marked by source:** the rows' `source` is `erw:storage_daily_cycle_caiso` (registered), with `source_url` the method's `#caiso` section.
- **Rows:** 398 days, 1,990 rows (2025-08-24 to 2026-09-27); the table now holds 13,896. The 11,906 EIA-930 rows are identical to before.
- **Check:** 2026-09-27 recomputed independently from the 5-minute file: 24,524.083 MWh out, 30,002.333 in, peak discharge 19:00, peak charge 11:00 (Pacific).
- **The page:** a CAISO row in the daily-cycle table, tagged "CAISO's data" with its own tier chip, and a CAISO line (hourly means) in both charts. The line has its own "source" chip and a citation of `caiso_battery_storage`.
- **Supabase** carries the last 32 days of `batteries_mw` (8,703 rows).
- **The daily run** now computes the cycle after `caiso_outlook`, so both inputs are fresh.

## 2. Battery energy capacity (MWh): done

**The EIA-860M workbook carries it.** The saved August 2026 workbook has "Nameplate Energy Capacity (MWh)" on its Operating and Retired sheets, not on Planned.

- **`energy_capacity_mwh`** added to:
  - the three `eia860m_*_generators` tables (empty in planned, since EIA gives none);
  - `storage_capacity`.
- **How:** the tables were rebuilt from the saved workbook with a new `eia860.py --from-raw 20260926T000340Z` (no pull; sha256 checked against the manifest). Every other column is identical to before, and `retrieved_at` stays the download's.
- **Fleet:**
  - operating: 1,137 units, 54,488.9 MW, **150,437.6 MWh** (every unit has a value);
  - retired: 8 units, 338.5 MW, 1,236.1 MWh;
  - planned and under construction: no MWh.
- **On `/storage`:** each status cell shows its MWh where EIA gives it, or "EIA-860M gives none". Each sum is a check key in `check-values.mjs`.

## 3. Thesis Builder: landscape in its own call: done

- **The change:** three structure calls instead of two:
  - {scope, fundamentals, trends};
  - landscape alone, with a line asking for every private company the notes name;
  - {capital, incumbents, risks, policy}.
- **Run once** on the geothermal thesis. I used `--resume-research` on session 30's saved research (`20260929T105904Z_research.json`) rather than a new research pass, for two reasons:
  - no new web search (the no-pull rule);
  - the only change measured is the separate call.
- **Companies found: 2**, the same two as session 30 (Zanskar Geothermal & Minerals, Project InnerSpace).
- **Bill:** USD 0.3903 for the three calls (landscape alone USD 0.1152). Run total, with the saved research's USD 0.9334, is **USD 1.3237 against USD 1.2253**: USD 0.098 more for the same 2 companies.
- **Why not 7.** The separate call is not the cause. This research pass's Scope sheet excludes drilling and plant developers. Quaise, XGS, Sage and Fervo are named in the notes; Fervo lands on Incumbents. The 7 of the earlier per-sheet run came from a different research pass with a broader scope.
- Workbook: `docs/thesis/subsurface-heat-mapping-for-geothermal-session-34.xlsx`. `energy_companies` was re-merged (354 rows, the two rows' retrieval times updated).

## 4. Emissions: six more CO2 variables: done

**One pass.** The connector read each of the eight saved workbooks once, in 12 minutes, and wrote per-BA extracts: `warehouse/raw/eia930_emissions/20260930T000657Z/<ba>_hours.csv`. Each holds every hour from 2018-07-01: EIA's Demand and Net generation and the eight CO2 columns. Rows were built from the extracts (`--from-raw`, then `--from-extract`); item 5 read the same extracts. No workbook was opened twice.

**Rows added to `eia930_all_emissions`: 3,195,240, 79.9% of the 4,000,000 ceiling** (`--max-new-rows` enforces it before writing). The table has 4,317,384 rows; 0 earlier rows were replaced.

| Variable | Rows (all BAs) |
|---|---|
| `co2_emissions_coal` | 545,640 |
| `co2_emissions_natural_gas` | 560,808 |
| `co2_emissions_oil` | 405,576 (no ERCOT, no MISO) |
| `co2_emissions_other` | 561,072 |
| `co2_emissions_imported` | 561,072 |
| `co2_emissions_exported` | 561,072 |

**Completeness: the same rule, as EIA-930 generation applies it** (session 6 ruling a, per day since sessions 13 and 16):

- A day is written only when the core pair (generated, consumed) has all 24 hours.
- Each of the six is then written for that day only when it has all 24 hours itself.
- A column EIA leaves empty for a BA is not a variable of it: ERCOT's oil column is empty in every hour; MISO's has 24 values in 8 years.
- Gaps are in `run_status.csv`: 9 rows, one per BA and variable, with the count, for example CAISO coal, 275 days.

**Checks:**

- Values equal the extracts' (US48, 2019-03-01 00:00 and 2026-09-20 12:00, coal, gas, imported).
- EIA's identities hold to 1e-11 (PJM, every hour): generated = coal + gas + oil + other, and consumed = generated + imported - exported.
- The validator passes.

## 5. Carbon intensity from 2018-07: done

**Rebuilt:**

| Table | Rows | Before |
|---|---|---|
| `carbon_intensity_hourly` | 1,119,244 | 12,528 |
| `carbon_intensity_daily` | 46,624 | 522 |
| `carbon_intensity_monthly` (new) | 1,264 | none |

- **Denominators:** the workbooks' own Demand and Net generation, from the extracts.
- **Numerators:** `eia930_all_emissions`.
- **Monthly:** energy-weighted over UTC months whose every day is complete. US48 has 97 months and SPP 45, since SPP's file often leaves one CO2 column empty.

**The intensity comparison.** The warehouse-based (session 32) version is still computed each run over the hours `eia930_all_generation` and `eia930_all_demand` hold, and written to the tables' header, not as rows. Hours 2026-08-26 to 2026-09-27:

- **Identical** for CAISO, MISO, PJM and SPP, both variables.
- **ERCOT and NYISO, generation:** one day differs, 2026-09-03 05:00 to 09-04 04:00 UTC, by up to 22.7 and 38.2 kgCO2/MWh. EIA revised that day's net generation after the warehouse's rolling pull took it; the workbooks (downloaded 2026-09-29) have the revision.
- **ISO-NE:** one hour (2026-09-25 17:00).
- **US48:** most hours differ slightly: mean 0.33 kgCO2/MWh for generation (largest 2.3) and 0.26 for demand (largest 6.2).
- **All BAs:** mean absolute difference 0.157 (generation), 0.034 (demand).

**`/emissions`:** one new block, "Monthly since 2018": the monthly intensity of generation per ISO as one chart, with each ISO's first and latest complete month in figures (14 check keys).

## 6. erw.filter's facts cached on disk: done

- **Where:** `_local_columns` keeps each local file's distinct values in `~/.cache/erw/facts/` (or `ERW_CACHE_DIR`).
- **Validity:** while the file's modification time (ns) and size equal those recorded before the scan. A file that changes during its scan is not cached. `ERW_FACTS_CACHE=0` turns the cache off.
- **Timing of `erw.filter(node="HB_NORTH")`** on this machine:
  - **78.1 s before;**
  - 82.4 s on the first call, which writes the cache;
  - **0.3 s after**, also in a new process.
- **A test covers it:** the cache gives what a scan gives, a valid cache is read, and a newer file is scanned again.

## 7. Package tests: remote tests only on request: done

- Every test in `test_backends.py` carries the marker `remote`. `package/tests/conftest.py` skips them unless `-m remote` or `ERW_REMOTE_TESTS=1`.
- The default run skips all 32; `-m remote` collects all 32.
- The workflow keeps its 20-minute step, running `test_erw.py`, as before.

## 8. The shadow emails: confirmed, one guard added

**Confirmed from the code and the workflows:**

- **The published digest** (Sonnet's scores, `news_score`) goes through `email_digest.py --auto` to `DIGEST_RECIPIENTS` and every confirmed subscriber (`EMAIL_SUBSCRIBERS: "1"`, `EMAIL_TOKEN_SECRET`).
- **Then the SHADOW HAIKU digest** (`shadow.py digest`, `SHADOW_MODEL: claude-haiku-4-5`) goes to `SHADOW_RECIPIENT`, else `DIGEST_RECIPIENTS`. It never reads the subscriber list.
- **`roundup.yml`** does the same for the Roundup.
- **Expiry:** nothing shadow runs from 2026-10-06 (`shadow.yaml`); the last shadow digest is Monday 2026-10-05.
- **Samuel only:** locally `DIGEST_RECIPIENTS` is one address and `SHADOW_RECIPIENT` is unset. The GitHub secrets' values cannot be read (the token cannot list secrets), and no runner has sent a shadow yet: 2026-09-29's run failed before the email step.

**Fixed:** the shadow now goes to exactly one address. If the chosen list ever holds more, it sends nothing and says so.

**Tested:** `tests/test_session34.py` has 7 tests with fakes for Resend and the subscriber list, on real published issues: the recipients, the subject prefix, the expiry dates, the kill switch, and the order in both jobs.

## 9. Known gaps, PRIORITIES.md, run status: done

- **`run_status.csv`** now records the GitHub daily run of 2026-09-29 (run 36615905147), taken from its job log. The run failed at coverage before its commit, so it had left no row and the gate was reading 2026-09-28. 39 rows, runner `github`.
- **The CARB known gap's reason** now names the carry-forward (session 30) and the coverage fix (session 33). No table was added to or removed from the list.
- **`PRIORITIES.md`** says what counts for the gate after sessions 29 to 33:
  - a run that fails before its commit;
  - carried-forward tables;
  - the storage and emissions steps (gaps are not failures);
  - the package test step (after the commit, not a table).
- **Found and fixed: `build_status.py`** had crashed on every run since session 31. Gap rows of the partitioned tables (`ba`) broke it, and it would have counted emissions gaps as filled. It now reads each partitioned table once and checks its own core variables. `STATUS.md` rebuilt: 77 tables at the time, 789 recorded gap days, 11 filled, 778 open (mostly session 32's emissions days EIA left incomplete).

**Gate: CLOSED.** The latest GitHub daily run (2026-09-29) has 2 failures outside the known gaps:

- `coverage`: fixed in `670ba69`, not yet proven by a run;
- `eia930_swpp_demand`: 19 of EIA's SPP forecast hours missing.

This session added no source and no tool.

## Part D: verify and ship

- **Validator:** 78 of 78 tables pass.
- **Coverage:** 78 tables, all pass, 10,393,479 rows.
  - `carbon_intensity_monthly` got its sector and ISOs.
  - `storage_daily_cycle` lists CAISO.
  - A build now takes 14 minutes on this machine (4.3M emissions rows).
- **Archive:** 11 tables, 4,385,309 rows appended under the existing names plus the new `carbon_intensity_monthly`. The two runs: 20260930T012547Z-local and 20260930T015852Z-local. Two fixes were needed:
  - **The bucket refused objects over its size limit** (HTTP 413). A run's part over 45 MB compressed is now stored as numbered chunks; sync and pull know the names; restore reads a month's objects in name order.
  - **The table's hash index (69 MB)** is chunked behind a small pointer object.
  - **Removed from the bucket:** the three chunks of the failed attempt 20260930T014221Z-local, which no run log records.
  - Tests for both are in `tests/test_session34.py`.
- **Supabase:**
  - **321.0 MB before, 335.6 MB after** (limit 400).
  - The full load first reached **394.2 MB**. I trimmed the live set: `eia930_all_emissions` keeps only generated and consumed (the site reads nothing else), and `carbon_intensity_daily` keeps 100 days (the site does not read it). Redivis and the CSVs keep everything.
  - Every table matched.
- **Redivis drafts:** 25 tables, each `count(*)` equal to its CSV, including `eia930_all_emissions` 4,317,384, `carbon_intensity_hourly` 1,119,244 and `news_stories` 13,113. Nothing released.
  - Nine tables I did not change also uploaded, because their local data differed from the upload manifest. Their row counts are unchanged, except `news_stories` (+47, session 33's restored stories).
- **License check:** 0 internal tables in the public dataset.
- **`llms.txt` and the chat catalogue:** updated, the spec regenerated, `check_spec` passes.
- **Package tests (default set):** 315 passed, 32 skipped (remote), 13.5 minutes.
- **`tests/`:** 58 of 58 at Part D; with the two archive tests added later, `test_session34` has 9, all passing.
- **Local:** check-routes 32 of 32, check-values 1,237 of 1,237.
- **Deployed** by the push; live again: routes 32 of 32, values **1,237 of 1,237**, including the CAISO row, the MWh sums and the monthly intensities.

## Decisions made without a human (each reversible)

1. **Thesis Builder on the saved research,** not a new research pass. The no-pull rule, and it isolates the landscape call. The bill is compared as the saved research plus the new calls.
2. **Completeness per variable for the six,** under the core pair, as EIA-930 generation does. Requiring all six together would have lost every ERCOT and MISO day and 15% of CAISO's.
3. **A CO2 column EIA leaves empty for a BA is not a variable of it** (ERCOT and MISO oil). A history build's gap days are recorded one row per BA and variable, with counts.
4. **The extract holds every hour from 2018 on each read,** in the daily run too, so carbon intensity is rebuilt whole each day from `eia930_all_emissions` and the newest extract. If a BA has no extract, the tables are left as they are and the step fails.
5. **Monthly intensity** only for UTC months whose every day is complete. The warehouse-based check is logged and written in the header, not stored as rows.
6. **CAISO's daily cycle from hourly means** of the 5-minute data, so it compares with the EIA-930 BAs. Source id `erw:storage_daily_cycle_caiso`.
7. **The planned EIA-860M table gets an empty `energy_capacity_mwh`,** so the three tables share a schema.
8. **The shadow goes to one address only.**
9. **Recording the failed 2026-09-29 run from its job log,** which closes the gate: it is the latest daily run.
10. **The Supabase live-set trim,** and the removal of the failed archive attempt's three orphan chunks.

## Run health and the daily job

- **The daily job did not land** during the session. `origin/main` had no new commit; the next scheduled run is 2026-09-30 14:00 UTC. I pushed after checking.
- **What tomorrow's run does differently:**
  - it writes all eight CO2 variables for the last 3 days;
  - it rebuilds intensity from 2018;
  - it computes the storage cycle after `caiso_outlook`;
  - its build_status no longer crashes;
  - its coverage and archive steps take longer: coverage about 14 minutes here, inside the job's 180.

## Open questions for Samuel

1. **`eia930_swpp_demand`** fails when EIA leaves SPP's day-ahead forecast hours missing (19 on 2026-09-28). Add it to the known gaps, or give SPP demand the per-day rule that ERCO and NYIS demand have (session 13)?
2. **The Thesis Builder's landscape** is limited by the research pass's scope, not the call. Widen the research prompt to name adjacent drillers and developers, or keep the strict scope?
3. **`/ask` on the site reads Supabase,** which now holds only generated and consumed CO2. By-fuel questions there will find no rows. Accept, or load the six for a shorter window?
4. **The shadow's recipient on GitHub:** confirm `DIGEST_RECIPIENTS` is your single address, or add `SHADOW_RECIPIENT`.
5. **Coverage takes about 14 minutes** with the larger emissions table. Worth streaming it, as the tests now are?

## Skipped

- Nothing of the nine items.
- **Not run:** the remote backend tests (now opt-in) and a local end-to-end daily run (it would pull).
