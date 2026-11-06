# Session 2882 report: the Stanford draft and the method notes

5 November 2026, about 22:28 to 22:40 UTC, on lab-desktop (the data machine), chain 147, unattended. Model spend USD 0. Pulls: Redivis's API only. The reconciles, before and after, and one upload of two tables come to well under the cap of 150, by the uploader's own costs (about 28 and 6 a table).

## Read these first

- **Method notes against code and table:** `large_load_tariffs.md` and `subregion_demand_growth.md` say what the connector and the builder do. Their rules are tested (`test_session2871`, `test_session2877`).
- **`--reconcile`, before:** 467 tables, 393 match and 74 differ. The differences are the days since each table's last upload: the runner's daily run had stopped since 30 October. 0 are missing from the draft.
- **Uploaded in a plain upload:**
  - `subregion_demand_growth`: 3,918 rows, Redivis count 3,918.
  - `erw_headers`: refreshed, 5,585 lines.
  - Run under the data lock with the branch's license record copied in for the one run, and main's put back after (`runs/c147/upload_stanford.sh`). Nothing was released.
- **`utility_large_load_tariffs` was refused,** as it should be. Its ERW verdict is unsettled:
  - The IURC's (IN.gov's) statewide terms are on record as "needs written permission" (license_verdicts.csv, session 311).
  - The Georgia PSC and the Oregon PUC have no verdict.
  - The table's own flag (public, the chain's rule for filed tariffs) and the verdict therefore disagree, and the uploader refuses an unsettled table.
- **`--reconcile`, after:** the same 467 tables and figures. The reconcile reads main's coverage, which does not hold this chain's tables until the branch lands.
- **`docs/state/redivis_v1_ready.md`, in five lines:** the draft, the package (137 tables), what is not in it, the one click, and what follows.

## Decisions made without you

- **The tariff table was left out of the draft.** The chain rules filed tariffs public, but the ERW's own record says IN.gov's terms need permission. A recorded verdict is not overridden without a ruling.

## For Samuel's ruling

- **`utility_large_load_tariffs`'s license.** The chain's rule: a filed tariff is a public regulatory record. The record: IN.gov needs written permission. Also needed: a read of the Georgia PSC's and the Oregon PUC's terms.

## Files

- On `wip/c147-data`: `docs/state/redivis_v1_ready.md`, this report.
- On the data machine only: `runs/s2882_*`, `runs/c147/upload_stanford.sh`.
