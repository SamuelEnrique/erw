# Session 3937 report: the large-load research pass as three tables

Energy Research Warehouse (ERW). Chain 267, data machine (lab-desktop), 14 November 2026, 10:46 to 10:57 UTC. Opus 5.5. Model spend USD 0. Requests: Redivis's API only (one `--tables` run); no publisher asked (the connector reads committed files).

## What was built (`docs/state/data_requests_large_load.md` rows 1, 15 and 16)

- **`warehouse/connectors/large_load_research.py`:** reads `docs/research/large_load/utilities_2026-11-13.csv`, `changes_2026-11-13.csv` and `legislation_2026-11-13.csv` (window P4, sessions 5300 to 5304) and writes three events tables. No request, no model call. A row missing what it must hold (unique id, license `public` or `internal`, an http source, a read date, a rule status of the six, a change date) stops the whole write.
- **`utility_large_load_rules`:** 100 of 122 rows written, 22 held for a license (named in the header). 2 public rows have cells withheld by their `internal_fields` (`x_withheld`); 11 rows keep a registry pointer in `x_held` in place of the value.
- **`utility_large_load_rule_changes`:** 94 of 98 written, 4 held. Seven changes print a month only: kept as printed in `x_date`, dated by the day read (`x_date_kind`).
- **`state_large_load_laws`:** 27 of 28 written, 1 held (Indiana HEA 1007, IN.gov's terms).
- **`mw` empty in all three:** every size is a phrase (`x_threshold_mw`).
- **Under the data lock:** written, validated (all three PASS), archived (100, 94 and 27 rows), in coverage. A tier rule (`model_extracted`: AI research sessions, every cite matched by code) and a sector rule (`power;datacenters`) in `build_coverage.py`.
- **The records:** `licenses.py tables`, `check` (0 problems), `write`, `status`; `release_v1.py` (the three held out of v1: their ERW verdict is unsettled, as the registry tables' is; the count line "54 tables of the public draft are held out"); `build_tables.py`; `build_llms.py`; the Redivis draft (100, 94, 27 rows; `erw_headers` 2,843 lines; nothing released).
- **The method:** `docs/methods/large_load_research.md`. **Test 3937** (6 tests). Tests 1008, 203, 237, 238, 275, 378, 410, 469, 505, 53, 67 with 3937 and 2924: 139 passed.
- **Not loaded into the live set:** not in `live_set.yaml`; no page reads them yet.

## Not done here

- **Rows 2 to 14 and 17** (edits to the ERW's registry files: Nevada's LLESA, Oncor's docket, I&M's collateral, Dominion's GS-5, SRP, Duke, the twelve files' licenses, PGE, Xcel, AEP Ohio, Ameren and Evergy, the PUCT's rule, PG&E's Rule 30; the operator documents that changed): each is a registry edit with its own license cell, left for the next sessions (file 272's data requests).

## Decisions made without you

- **One public table per dataset, held rows not written,** as `utility_large_load_tariffs` holds its schedules (ruling 4), in place of a second internal table per dataset.
- **The three tables are on test 4101's list** of public tables whose publisher has no single verdict (session 3938), beside `utility_large_load_tariffs` and `large_load_connection_rules`, on ruling 4's reasoning.

## For Samuel's ruling

- **The three research tables are flagged public under ruling 4** (each written row a commission's copy, a filed tariff book, an SEC filing, a grid operator's posted document or a legislature's text). Default: public, out of release v1 while their verdict is unsettled. If you rule otherwise, their header's license line turns them internal on the next write.
