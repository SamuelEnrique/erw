# Session 10217 report: the policy and regulatory monitor audited as a hostile expert would

Chain 710, part D, the old laptop, 26 November 2026. Worktree `C:\Users\lossa\Documents\erw-c710-a`, branch `wip/audit-policy-doc`.

## What was done

- `docs/reviews/policy-model-audit-2026-11-26.md` and its evidence folder: the ground, every figure of `/policy?view=monitor` as it opens re-done from the page's own files by an independent restatement, one rule changed at a time, each claim against the code, what an expert would hold, eight findings.
- The arithmetic is right: 534 of 538 keys equal; the other four are the calendar's week, eight days where the hover said seven (finding 4).
- Findings: 2 Medium (the monitor draws a table held whole for the PUCT's releases; the fifteen large-load orders of FERC and the grid operators left the monitor's file on 20 November), 6 Low (records with no score hidden and the hover saying "scored below"; the eight-day week; "the last 90 days" that is a fixed window to 13 November; the note on status; the note on summed charts; three enacted laws whose own text says they took effect before the read).
- Six words branches (`wip/audit-policy-1` to `-6`), merged as `wip/audit-policy-words` (`c46d60804`): drawn with the site's own code, 10 of 10 new sentences read; no figure moves (538 of 538 page keys equal to main's).
- Five branches with a test only, not for landing: `wip/audit-policy-7` to `-11`.

## Decisions made without you

- The default audited is the monitor view: `/policy` as it opens draws "license needed" and no figure (its table is held), and the week view draws only three dockets.
- The fifteen large-load orders' loss is a data request, not a words fix: the builder still reads them; the daily run lacks the table.
- No figure branch for findings 4 and 5: their words fixes make the page say what it does.
- `site/scripts/test-large-load-read.mjs` row 6's window widened from 400 to 700 characters for the longer "enacted" hover (on `wip/audit-policy-6`).

## For Samuel's ruling (default "left as it is")

- Finding 1 (`wip/audit-policy-7`): hold the monitor as the first view is held (295 shown to none), or leave out the PUCT's rows (1,568 to 1,531 records; 295 to 284 shown). Already line 1 of the rulings of 17 November.
- Finding 3 (`wip/audit-policy-9`): show records with no score at the opening floor: 295 to 351.
- Finding 6 (`wip/audit-policy-10`): a status as of the page's day: Final 126 to 30, In effect 70 to 166.
- Finding 8 (`wip/audit-policy-11`): three enacted laws marked in effect: in effect 10 to 13, enacted 6 to 3.

## Needs the key

- Nothing.

## Problems

- One `git fetch` early in the session ran without `-c gc.auto=0`; its automatic upkeep tried to prune a stale worktree entry of the shared repository and was refused ("Permission denied" on `.git/worktrees/erw-1600`). The three chain 710 worktrees were checked and stand. Every later fetch and commit used `-c gc.auto=0`.
- A first commit of `tests/test_audit_policy_7.py` held a failing assertion (the hold read from the wrong part of the license file); fixed in the next commit on that branch.
- `site/scripts/test-allgrids-read.mjs` row 10 fails on main and on these branches alike (not touched here).
