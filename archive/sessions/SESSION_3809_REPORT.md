# Session 3809 report: the Stanford draft, and the warehouse's own draft

Energy Research Warehouse (ERW). Chain 216, data machine (lab-desktop), 12 November 2026 21:13 to 21:20 UTC. Opus 5.5. Model spend USD 0. Requests: Redivis's API, two `--tables` runs of one table each (within memory's cost of about 28 and 6 a table).

## Read these first

- **`iso_reserve_margin_reports` is on both drafts, and nothing was released.**
  - The Stanford draft (erw:b9wm): "ok iso_reserve_margin_reports: CSV 5 rows, Redivis count(*) 5"; `erw_headers` 5,636 lines (8 for the table).
  - The warehouse's own public draft (`energy_research_warehouse`): 5 rows, count 5; `erw_headers` 2,782 lines. Test 410 requires a draft there for every table the live catalogue lists.
  - Both ran under the data lock (`lock.py run`), in the foreground, while the lock was free between the dispatched run and the scheduled one.
- **Its catalogue hold is lifted** (`warehouse/supabase/live_set.yaml`): it is on the drafts. It stays held from v1 (`release_v1.STORAGE_HELD`, its wording now "on the Stanford draft since 12 November"); v1's list is yours.
- **The records on `wip/c216-data`** (`dac7845d5`): `redivis_uploads_stanford.csv` and `redivis_uploads.csv` patched from the main checkout, which was put back; the release list rebuilt (`--check` 0 differences).
  - Tests 275, 410, 3798, 237, 1008, 378 and 505: 58, OK. Test 410 failed after the Stanford upload alone and passed after the warehouse's draft.
- **FERC-714's tables stay off,** their verdict unsettled (chain 212's ruling item 1).

## Decisions made without you

- **Uploaded to the warehouse's own draft as well as Stanford's.** The catalogue's rule (test 410) asks for it; a draft is not a release.

## For Samuel's ruling

- None new (v1's list: chain 215's item).
