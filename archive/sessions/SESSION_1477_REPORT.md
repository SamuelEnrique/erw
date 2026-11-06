# Session 1477 report: one more dry run of each periodical (a free session), read and sent

Energy Research Warehouse (ERW), session 1477, chain 154 (a free fault session: rows 50 to 54 fixed by sessions 1472 to 1476, and the chain file sends a free session to one more dry run of each periodical), samueloldlaptop, 6 November 2026, 07:24 to 07:30 UTC. Model: Claude Opus 5.5 (this window's). **Model spend USD 0.0434** (the Digest USD 0.0268 + 0.0047, the Roundup USD 0.0073 + 0.0046; `ERW_SPEND_CAP_USD=4`, the ledger off). No warehouse data written; **two preview emails to the one fixed recipient** (07:27 UTC, "[preview, dry run 1477] ...", Resend ids `01a1afc0-f18f-7e50-b391-7356cb48ace1` and `01a1afc0-f6c2-77ca-bb04-6a212643ede8`); nothing posted. Branch `wip/1477-periodicals`, cut from `wip/1476-periodicals`.

## What it did

- The Digest of 6 November and the Roundup of W45 so far, with the code of sessions 1472 to 1476 (`runs/periodicals_dryrun/s1477/run.sh`): `news_stories` on main held no newer scored story (to 5 November 23:39 UTC), so the stories are session 1468's and the difference is the code's, and the model's.
- Read against the faults file: rows 50 to 54 fixed as written; two new rows, 56 and 57, in the model's headlines (sessions 1479 and 1480). Session 1476's report's clock time corrected.

## Found

- The headlines the model writes are not the same from run to run on the same stories ("a $4 Billion, 702 MW Bloom Energy fuel-cell project" at 06:16 UTC, "a 4 billion USD fuel-cell project, 702 MW" at 07:26 UTC), and are held to the literal-number check only: their sums and adjectives are not held to the voice (rows 56, 57).

## Decisions made without you

- Session 1478 lands sessions 1472 to 1477 before the headline faults, as the chain file sets the landings (every third session).

## For Samuel's ruling

- None.
