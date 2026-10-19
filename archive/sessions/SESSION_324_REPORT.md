# Session 324 report: the licenses

19 October 2026, from 21:15 UTC (the lists) and 23:01 UTC (the writes), unattended, on lab-desktop (the data machine), the fourth session of the chain of 19 October, daytime. Model spend USD 0. Pulls: none. Nothing was sent to anyone.

## Read these first

- **The 44 disagreements of session 311: 0 remain open.** 41 are tables flagged public whose publisher asks for permission. A newer record settles them: the owner's ruling of 12 October (session 207) keeps the flag public and shows "license needed" from 21 October until a permission is recorded (`license_status.csv`). The document was right about each clause and wrong to call it open, so the document is corrected, in a new section "Settled by a ruling (session 324)". **No flag was turned internal.** Doing so would have stopped every daily run at its Redivis license check until a person moved the tables (`upload.py --check-license --fix`).
- **3 tables were flagged internal where the clause allows them.** `portwatch_chokepoint_transits` stays internal by the owner's default (item 12). Its line in the document says why: the IMF's terms (read 13) "prohibit bulk download of information by automated technology without explicit permission", and the table is a daily automated pull; commercial reuse needs copyright@imf.org. **`carb_auction_allowance_prices` and `rrc_lease_production_monthly` are now public (the clause wins):** CARB's from the State of California's conditions of use ("considered in the public domain"; CARB's own page was not read), the RRC's own permission for noncommercial use, unaltered. Each connector's License line, each table's header and the source registry say so. Both uploaded to the public Redivis draft (nothing released); neither is in the live set.
- **`docs/licenses.md` now: 204 tables; 142 agree, 42 settled by a ruling, 0 disagree, 19 not settled, 1 internal by the ERW's choice.** The three tables of sessions 322 and 323 joined.
- **For Samuel:** `docs/state/permissions_2026-10-19.md`, session 205's 42 permission tables by publisher (35 publishers), a box each, all empty. Since 12 October 3 have been retired and 2 have joined, so 41 show "license needed". Also `docs/state/unsettled_licenses_2026-10-19.md`: the 19 tables not settled, one line a publisher, with the page read and the sentence an email would need.

## Every change

| Table | Before | After | Why |
|---|---|---|---|
| 41 tables flagged public, permission asked (NYISO 30, ISO-NE 26, MISO 23, the news outlets, ...) | "DISAGREES: the flag is looser" | "ruled: license needed from 2026-10-21" | `license_status.csv`, the owner's ruling of 12 October |
| `portwatch_chokepoint_transits` | "DISAGREES: the flag is stricter" | "ruled: kept internal" | the owner's default of 19 October (item 12), the IMF's clause |
| `carb_auction_allowance_prices` | flag internal ("CARB terms ... unconfirmed") | flag public | read 10's clause |
| `rrc_lease_production_monthly` | flag internal ("no page read grants reuse") | flag public | read 19's clause (noncommercial; a sale needs permission) |

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py --what "session 324"` | 0 | |
| `runs/s324_flip.py`, `table_stores.py` on the two, under the lock | 0, 0 | validate, coverage, archive, Redivis draft |
| `load.py --only` the two | 1 | neither is in the live set: "no live-set table matches; nothing loaded" |
| snapshots `s324-before`, `s324-after` | 0 | 0 differences |
| `licenses.py tables --headers warehouse/output`, `write`, `check`, `status`; `license_state.py` | 0 each | 204 tables, 0 problems; 41 "license needed" |
| `release_v1.py`, `--check` | 0, 0 | 131 tables and 3 metadata tables in v1 (126 before), 41 held |
| tests 49 (RRC's pin follows), 205, 207, 248, 275, 324 | 0 | |

## Decisions made without you

1. **A ruling is a newer record.** The 41 keep their public flag; the document says what governs them.
2. **CARB's verdict rests on the State's page**, as session 311 read it; CARB's own page was not read in this session (no pulls).
3. **The RRC table goes public for the ERW as it is today** (it sells nothing); the document's "if the ERW sells anything" column still says written permission.

## For Samuel's ruling

- The permission boxes (`docs/state/permissions_2026-10-19.md`).
- The 19 unsettled (`docs/state/unsettled_licenses_2026-10-19.md`): send any of the drafted sentences, or accept public-records law as the ground.
- Moving the two newly public tables out of the internal Redivis dataset, where copies remain (`upload.py --check-license --fix` is a person's step).

## Files

- New: `docs/state/permissions_2026-10-19.md`, `docs/state/unsettled_licenses_2026-10-19.md`, `tests/test_session324.py`, `runs/s324_permissions.py` (not in git), this report.
- Changed: `scripts/licenses.py` (`RULED_INTERNAL`, `license_needed`, the settled section), `docs/licenses.md`, `warehouse/connectors/carbon_auctions.py`, `warehouse/connectors/rrc_production.py`, `warehouse/metadata/sources.csv`, `license_tables.csv`, `license_status.csv`, `site/data/license_status.json`, `docs/state/licenses_2026-10-21.md`, `docs/redivis/release-v1.md`, `docs/redivis/release-v1-runbook.md`, `docs/redivis/release-v1/`, `tests/test_session49.py`, `coverage.csv`, `docs/coverage.md`, `archive_manifest.csv`, `redivis_uploads.csv`.
