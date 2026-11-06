# Session 3152: chain 186's seventh session (its 3152): the third sample's dates; the push

Personal laptop, second window, 6 November 2026, 15:11 to 15:15 UTC. Opus 5.5. Branch `wip/3152-policy` cut from `wip/3151-policy`.

## What it did

- `warehouse/policy/fields.py`, the date rules for the third sample's nine faults (a final rule's deadline, a scheduled or announced hearing, objections and hearing requests, compliance filings, a payment's due date), and two guards (a filing deadline on a date another step holds; a date a party asks, seeks, expects or plans for). A test with the third sample's words.
- `site/data/policy/monitor.json` rebuilt; the third sample's file records the session; the branch pushed (no request row: row 10 holds the code a landing needs, and the next row will name the newest branch).

## What it found

- Class 1 on the third sample: 52 of 52 rows (43 before). A first version took a filing deadline on the comments' own date (r61 of the fixture) and an applicant's requested date (r18), and the fixture's test caught the first; both guarded before the commit. On the archive's copy one more false step ("anticipates filing a response by June 30") was read and guarded. `test_policy_fields.py` 20 passed; Node 52 of 52; `check_policy.py` 303 of 303.

## Decisions made without you

- **A filing deadline that restates a comment deadline is not a second step.**

## For Samuel's ruling

- None new.

## Cost

- Model: none (USD 0.00).
