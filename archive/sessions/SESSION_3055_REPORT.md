# Session 3055: chain 166's second session (its 2261): the audit of the stored actions

Personal laptop, second window, 6 November 2026, 11:30 to 11:44 UTC (the commits' times). Opus 5.5. Branch `wip/3055-policy` cut from `wip/3054-policy`.

## What it did

- Drew 80 actions (every fifth of the newest 400 of the live set), fetched each one's own document into the scratch folder (the Register's API record and printed text, or the release page; 80 of 80 answered, one request every two seconds), and read each against its row.
- Wrote "The audit of the stored actions" in `docs/reviews/policy-audit-2026-11-06.md`: ten fault classes, numbered, each with its count in the sample and, where countable, in the table, and three quoted examples; and `docs/reviews/policy-audit-2026-11-06-sample.csv` (the 80 event ids with their classes).
- `scripts/sync.py --tables ^policy` (started in 3054) finished: this laptop's `policy_actions` (2,020), `policy_reads` (408), `policy_reads_evidence` (3,559) and `policy_action_tags` (38) restored from the archive.

## What it found

- The biggest gaps are fields the table never had: a dated next step stated by 59 of 80 documents, a status on none, a figure stated by 17, the instrument behind the four `action_type`s for 14.
- Sector "policy" (no sector) on 16 of 80 and 507 of the table; places missing on 6; bodies at the parent's level on 3 (45 or more of Interior's 85 rows are BOEM's or OSMRE's); 4 out of scope (all scored 0 to 2); the NRC's four weekly notices of one application held as four rows.
- The score is mostly right: 2 rows above their band, 1 borderline, none below.

## Decisions made without you

- **The sample is the newest 400's every fifth row**, as chain 156's deals audit sampled; it leans to FERC and the NRC as the table does.
- **The source text was fetched again** (the Register's printed texts are held only on the data machine's raw store); into the scratch folder, never the warehouse, at the connector's own pace and User-Agent.
- **A deadline stated as a period** ("within 30 days after...") counts as a stated next step but gives no date: the chain's rule that a date not in the text is empty.
- **The chain's body list** (FERC, NRC, DOE, EPA, Treasury and the IRS, BOEM, BLM, Congress, state commissions, ISO boards) was read as the level a reader filters by: a bureau (BOEM, OSMRE) is its own body, its department kept beside it.

## For Samuel's ruling

- Whether out-of-scope rows (class 9) should be dropped by the connector's routine list or only marked; this chain marks, never deletes.

## Cost

- Model: none (USD 0.00).
