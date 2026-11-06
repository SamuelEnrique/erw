# Session 3057: chain 166's fourth session (its 2263): one record an action

Personal laptop, second window, 6 November 2026, about 14:15 to 15:00 UTC. Opus 5.5. Branch `wip/3057-policy` cut from `wip/3056-policy`.

## What it did

- `warehouse/policy/records.py` (new): the documents of `policy_actions` that name one proceeding grouped into one record (union over proceeding ids; a repeat of a title within 45 days for a document with none), with every source of every document, a status history (a repeated notice is one step with every date), the record's status, next step, figure, highest significance; output in the events shape (`policy_action_records`), validated.
- `tests/fixtures/policy/records_3057.json` (30 stored rows, their records written from their own words), `tests/test_policy_records.py` (5 tests).
- The audit file: class 7 marked, a section "Session 3057".

## What it found

- On the fixture: 20 of 20 pairs together, none wrongly joined or apart.
- On the table (this laptop's copy, to the scratch folder): 2,020 documents make 1,495 records; 301 records hold 826 documents; the largest holds nine; the validator passes it (0 errors, 0 warnings).
- Two id forms would have joined unrelated documents had they counted: BLM's billing code (52 rows) and NRC plant dockets (`50-261`, 7 rows of four matters). Neither is a proceeding id.
- Tests: `test_policy_records.py` 5 passed, `test_policy_fields.py` 13 passed.

## Decisions made without you

- **A record is a proceeding**, read from the docket field: the chain's "deduplication across outlets and days" for a table of government documents. An EPA docket that holds several rulemakings (the steam electric guidelines: the deadline extension, its direct final rule and withdrawal, a later proposal) is one record, its history showing each.
- **A FERC docket's sub-number is dropped** (an amendment, -001, belongs to its -000); a hydro project's is kept (2538-106 and 2538-107 are two proceedings).
- **No new warehouse table, no daily step.** The script writes `policy_action_records` only when asked; the page's builder computes the records from `policy_actions`.

## For Samuel's ruling

- Whether `policy_action_records` should become a table of the warehouse (registered in coverage, licensed public, loaded to the live set), so that Ask and the downloads can read it.

## Cost

- Model: none (USD 0.00).
