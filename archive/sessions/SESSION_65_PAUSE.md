# Session 65: paused

Energy Research Warehouse (ERW), session 65 (the revenue and cost stack), on the portable laptop. Paused on 2026-10-02 at about 17:45 UTC, on Samuel's instruction. Model spend USD 0.00. Nothing merged to main, no Supabase write, no Redivis upload, the data lock not taken, the finish step not run.

## Read this first: where the branch is pushed

The work is committed on the local branch `task/065-revenue-stack` and pushed to **`origin/wip/065-revenue-stack`**, not to `origin/task/065-revenue-stack`.

Why: `.github/workflows/code-branch.yml` runs on every push to `task/**` and, when the tests and the site build pass, merges the branch into main by itself. A push to `task/065-revenue-stack` would therefore merge to main and start a Vercel production deploy, which this session's hard rules forbid. `wip/<task>` is the repository's own name for unmerged work (`docs/machines.md`, "Interruption"); no workflow acts on it. Pushing to `task/065-revenue-stack` is in effect the merge, so it belongs to the finish step and is Samuel's call.

## Done (committed and pushed to the wip branch)

| Part | What | State |
|---|---|---|
| A | `warehouse/connectors/iso_capacity_prices.py` and the table `iso_all_capacity_prices` | Pulled and rebuilt from the saved files: 814 rows of the 5,000 ceiling (PJM 234, NYISO 424, MISO 130, ISO-NE 26). Validator pass (exit 0) in `runs/session65/iso_all_capacity_prices/` |
| A | MISO's 2026/27 posting | The link first used answers HTTP 403: MISO replaced that posting with a corrected one on 2026-05-22. The corrected posting, found in MISO's own document list, is read; the 403 was not worked around. The parser reads its layout (dollar signs, a footnote mark on ERZ) |
| B | `warehouse/connectors/ercot_as_prices.py` and the table `ercot_as_prices` | Complete: 335,972 rows of the 500,000 ceiling, 2018-01-01 to 2026-10-02, no day left out. Validator pass (exit 0) in `runs/session65/ercot_as_prices/` |
| C | `warehouse/connectors/caiso_as_prices.py` | Written and tested. The pull is in progress (below) |
| D1 | Gates are never piped (CLAUDE.md rule 7); the loader refuses a coverage that no longer describes the tables | Done, tested |
| D2 | The data lock's holder is the session, not the machine | Done, tested. Before: one token file per machine, so every session on the laptop passed the lock check with the first session's token |
| D3 | `warehouse/derived/dropped_rt_days.py`, outputs in `warehouse/output/analysis_internal/` | Done. The answer is still to be written into the report (numbers below) |
| D4 | The seller tab's two sentences read the first month and month count from the snapshot | Done; the site builds, `tsc` passes, the page lints clean |
| E | `warehouse/derived/energy_plus_capacity_1gw.py` and `warehouse/output/analysis_internal/energy_plus_capacity_1gw.csv` | Done (the table is below) |
| Tests | `tests/test_session65.py`, 39 tests, with real CAISO and ERCOT samples in `tests/fixtures/session65/` | Pass. The full run of `tests/` (297 tests) had one failure, the chat spec check, which passes since the spec was re-exported (its file rerun: 13 of 13); the full package run had two failures, both rerun and passing (two that had been failing since sessions 62 and 64 were brought in line with `build_coverage.py`'s own rules) |
| Docs | `docs/methods/capacity_and_ancillary.md`; Decision 37 in `docs/datastandard.md`; the three tables in `warehouse/metadata/sources.csv`, `build_coverage.py` and `package/llms.txt`; `site/lib/chat/spec.json` re-exported | Done |
| Fix | The raw-file cache did not find a document a source answered at a redirected address. OASIS redirects every PRC_AS request, so saved CAISO days were being asked for again | Fixed in `iso_prices.fetch_raw` (the file is listed under both addresses) and in the CAISO connector (it looks under the address OASIS answers at). Tested |

## In progress: the CAISO pull, and its checkpoint

- **Stopped cleanly** in the pause after a day was saved. No Python process is left running.
- **Checkpoint:** the raw files themselves. `warehouse/raw/caiso_as_prices/` holds 661 of the 762 operating days, 2024-09-01 to 2026-06-23 without a hole. Every saved file was checked against its manifest checksum after the stop (1,255 manifest rows, 0 bad), and the last one (2026-06-23) parses to 192 rows.
- **Left to pull:** 101 days, 2026-06-24 to 2026-10-02, about 11 minutes at one request every six seconds.
- **No CAISO table exists yet:** the connector writes the table once, after the last day. `runs/session65/caiso_as_prices/` holds logs only.
- **Three days have no data at the source:** 2025-04-06, 04-07 and 04-08 (OASIS answers "no data returned"). They will be gap rows in the run's status, not estimates.
- **One cost of the cache bug:** before the fix, the resumed run asked again for 2024-09-01 to about 2024-09-29 (some 29 days already held). Nothing was written from them twice.

## Left to do

1. Finish the CAISO pull (the exact command is below), then validate the table in its scratch directory and read the exit code.
2. Check the CAISO row count against the ceiling (expected about 146,000 rows of 500,000) and list its gap days.
3. Write `archive/sessions/SESSION_65_REPORT.md` in the form of sessions 61 to 64, with "To finish" first. Nothing else is owed before the report.
4. Not this session's: the finish step (Part F). It is documented in the report, never run here.

## The exact next step

From the repository root, on the branch `task/065-revenue-stack`:

```bash
python warehouse/connectors/caiso_as_prices.py --out-dir runs/session65/caiso_as_prices > runs/session65/caiso_pull.out 2>&1; echo "exit=$?"
python warehouse/validate/erw_validate.py runs/session65/caiso_as_prices/caiso_as_prices.csv > runs/session65/validate_caiso.out 2>&1; echo "exit=$?"
```

The first command reuses the 661 saved days and requests only the 101 that are missing. Run it alone: no other pull at the same time.

## Notes for the report (so nothing is re-derived)

**Rows against each ceiling.** `iso_all_capacity_prices` 814 of 5,000. `ercot_as_prices` 335,972 of 500,000. `caiso_as_prices` not yet written.

**Capacity gaps (status rows, not estimates).** MISO planning year 2023/24 and the annual auctions before it (MISO's document list holds no results posting for 2021/22 to 2023/24; the 2019 and 2020 postings are annual, with another layout, and are not read). MISO external zones for Fall 2025 and Summer 2026 (the posting prints a range). California's CPUC resource adequacy statistics were not pulled; the methods doc says what a person would need to do.

**Licenses.** `iso_all_capacity_prices` is internal as a whole: PJM, ISO-NE and MISO rows internal, NYISO rows public by the standing rule with a caution (its legal notice grants no license). `ercot_as_prices` and `caiso_as_prices` public. The quoted terms are in `docs/methods/capacity_and_ancillary.md`.

**D3, the left-out real-time days, on day-ahead prices** (`dropped_rt_days_summary.csv`):

| ISO | Window | Days left out | Their day-ahead mean less the kept days' of the same months | Day-ahead mean, kept days less all days |
|---|---|---|---|---|
| ISO-NE | 2024-09 to 2025-08 | 28 | -6.65 USD/MWh (median -3.01) | +0.46 |
| NYISO | 2024-09 to 2025-08 | 21 | -5.36 (median -6.56) | +0.05 |
| ISO-NE | 2025-09 to 2026-08 | 25 | +10.98 (median +1.27) | -0.09 |
| NYISO | 2025-09 to 2026-08 | 11 | +22.72 (median +2.97) | -0.60 |
| CAISO | either | 1 each | not testable: the day-ahead day is missing too | 0 |

In plain words: the days session 64 left out were cheaper than their months, so that year's real-time averages are not biased low. In the later year a few left-out days were stress days (ISO-NE 2026-02-03, NYISO 2026-07-03 and 2026-02-07), so those averages are likely a little low: under 1 USD/MWh over the year, about 5 to 6 USD/MWh in the worst month. The recommendation for partly complete days is still to be written; it is to be recommended, not applied.

**Part E, a flat 1 GW, September 2025 to August 2026** (`energy_plus_capacity_1gw.csv`; conversions in the file's header):

| Region | Capacity zone | Energy, USD | Capacity, USD | Sum, USD | Capacity share |
|---|---|---|---|---|---|
| CAISO | none | 249,062,342 | not held | not held | |
| ERCOT | none (energy-only) | 276,135,276 | not held | not held | |
| ISO-NE | Rest of Pool, else system-wide | 616,431,496 | 31,089,000 | 647,520,496 | 4.8% |
| MISO | Zone 6 (Indiana) | 413,371,403 | 56,788,160 | 470,159,563 | 12.1% |
| NYISO | New York City | 601,033,917 | 159,030,000 | 760,063,917 | 20.9% |
| NYISO | NYCA (statewide) | 601,033,917 | 53,590,000 | 654,623,917 | 8.2% |
| PJM | RTO | not held | 103,971,800 | not held | |
| SPP | none | 268,289,073 | not held | not held | |

**Known and not fixed.** `npx eslint` over the whole site exits 1 (8 errors in source files this branch does not touch, such as `app/companies/CompaniesTable.tsx`; the rest are in other folders). The changed page lints clean.

**For Samuel.**
- The push target (above): say whether the finish step should push to `task/065-revenue-stack`, which merges to main by itself once the checks pass.
- ISO-NE's and MISO's terms are read here as internal for capacity prices, while their hub prices are public in the ERW. One of the two readings needs a person's ruling.
- Whether NYISO's capacity rows may be shown alone.
- The three new tables are not in the daily run. Whether they should be refreshed daily is a later decision.
