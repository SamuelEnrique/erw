Session 3 of the Energy Research Warehouse (ERW). Read CLAUDE.md, ARCHITECTURE.md, docs/datastandard.md, SESSION_1_REPORT.md and SESSION_2_REPORT.md first. Same non-negotiables: real data only, fail loudly, no em dashes, never delete existing files, commit after each task, do not push.

TASK 1. Daily refresh workflow.
Write .github/workflows/daily-prices.yml, modeled on the IRW's metadata-pipeline.yml in ../irw-reference/.github/workflows/: runs every day at 14:00 UTC and on manual dispatch, sets up Python 3.12 (not 3.14, so the pinned gridstatus installs cleanly from requirements.txt), runs every ISO connector for the last 3 days, runs erw_validate on every output, and commits the updated CSVs, raw files excluded, directly to main with a message stating the run date and which ISOs succeeded or failed. A validator failure must fail the workflow. Make the connectors idempotent: a rerun appends new intervals and replaces intervals already present for the same entity, variable and ts_utc, and never duplicates rows. Add a test that proves this on a small fixture.

TASK 2. Regenerate coverage automatically.
Turn docs/coverage.md into a generated file: write warehouse/metadata/build_coverage.py that scans warehouse/output and writes both docs/coverage.md and warehouse/metadata/coverage.csv (one row per table: table, iso, market, n_nodes, interval, ts_min, ts_max, n_rows, source_report, last_run, validator_status). Run it at the end of the daily workflow. This is the ERW equivalent of the IRW's metadata.csv.

TASK 3. A skill for adding a source.
Write .claude/skills/erw-add-connector/SKILL.md, modeled on the IRW skills in ../irw-reference: when to use it, the exact steps to add a new ISO or data source (function in iso_prices.py, raw file saving, completeness rule, naming rule, validator, coverage, report), and the mistakes sessions 1 and 2 hit so they are not repeated. Add a SessionStart hook in .claude/settings.json that lists available skills, copied from the IRW's settings.json with the path fixed for this repo.

TASK 4. Local run of the workflow logic.
Run the exact sequence the workflow would run, locally, once, and confirm: no duplicate rows after a second run, coverage regenerated, validator passes. Record the row counts before and after.

TASK 5. Report.
Write SESSION_3_REPORT.md in the same format. Note that the workflow cannot be tested on GitHub until the human pushes and enables Actions, and give the two commands to do that. Final commit.