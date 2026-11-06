# Session 3153: chain 186's eighth session (its 3153): the third sample's instruments and statuses

Personal laptop, second window, 6 November 2026, 15:14 to 15:20 UTC. Opus 5.5. Branch `wip/3153-policy` cut from `wip/3152-policy`.

## What it did

- `warehouse/policy/fields.py`: notices for information collections and procedural schedules (after an accepted or tendered application); release titles read for a meeting ("to brief, discuss, hold, host"), an order ("extends, renews, grants", "issues" a licence or the like) and an approval ("approves, expands"); "Proposed ..." notices proposed, schedule notices scheduled. A test with the eight titles, and the permit rule named by its own pattern now that another approval rule stands before it.
- `site/data/policy/monitor.json` rebuilt; the third sample's file records the session.

## What it found

- Instruments and statuses 80 of 80 on the third sample (74 and 78 before); the fresh sample's three changes all right; the first sample's none. Two first wordings were wrong and fixed before the commit: the notice rule took an application "Tendered ... and Establishing Procedural Schedule" (the fixture's sample r57, the third sample's r74), and "issues" took "NRC Issues Annual Assessments" for an order. `test_policy_fields.py` 21 passed; Node 52 of 52; `check_policy.py` 303 of 303.

## Decisions made without you

- **A release that announces a decision is read as the decision's instrument** (an order, an approval), not as an announcement: the reader filters by what was decided.

## For Samuel's ruling

- None new.

## Cost

- Model: none (USD 0.00).
