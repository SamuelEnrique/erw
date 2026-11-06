# Session 3141: chain 178's eighth session (its 3141): the fresh audit's dates

Personal laptop, second window, 6 November 2026, 14:41 to 14:44 UTC. Opus 5.5. Branch `wip/3141-policy` cut from `wip/3140-policy`.

## What it did

- `warehouse/policy/fields.py`, the date rules: comment words ("answers", "commenting"); a schedule's "--"; an hour without minutes or "p.m."; a meeting someone "will hold"; two new kinds, `filing_due` and `review_petition_due` (`site/lib/policymonitor.ts` has their words); a date being replaced ("to read") left out. A test with eight passages of the fresh audit's documents.
- `site/data/policy/monitor.json` rebuilt; the fresh audit's file corrected and the session recorded; session 3140's report time from its commit.

## What it found

- Class 1 on the fresh sample: 60 of 60 rows right. **My first pass of the audit had missed five rows** (court petitions' deadlines worded "must be filed ... by", an EA date in a schedule): the class was 13 faults of 60, not 8 of 59; the file says so.
- On the first sample: two more true deadlines and nothing else changed; on the archive's copy: 11 steps more (6 extended deadlines, read one by one, each right); `check_policy.py` 299 of 299; `test_policy_fields.py` 18 passed; Node 52 of 52.

## Decisions made without you

- **Two new kinds rather than stretching "comments due"**: a filing the action asks of someone (an applicant's amendments, a reporting deadline) and a court petition's deadline are not comments.

## For Samuel's ruling

- None new.

## Cost

- Model: none (USD 0.00).
