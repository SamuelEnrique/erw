# Session 2249 (chain 156, deals and datacenters) report: the second read

6 November 2026, from about 10:52 UTC (while session 2242's gate ran; 2248's landing waits for it), portable-laptop (code role), unattended. Worktree `erw-2249` on `wip/2249-deals`, cut from `wip/2247-deals`. Model spend **USD 0.6512** (the two recordings: deals 10 calls USD 0.4258, facilities 7 calls USD 0.2254; measured). No ledger row. Nothing deployed; no warehouse data written.

- **The audit's sample extracted again** with the new code on its own stories, recorded (`tests/fixtures/*/recorded_2249.json`, with `stories_2249.json`), and graded by three readers on the first read's rubric; the grades and the tally in `docs/reviews/deals-audit-2026-11-06/`.
- **The counts before and after** (the audit file, "Session 2249"): deals: a non-deal kept 12 to 1; a party a description 7 to 0; MW missed 3 to 0; AI tag wrong 6 to 2; status missed 14 to 7; place missed 17 to 12; **stated deals with no row 0 to 6**. Facilities: two places in one row 3 to 0; MW basis unstated 14 to 1 wrong; status missed 9 to 2; confidence too low 6 to 0; stated facilities with no row 0 to 2.
- **The classes still above zero** are listed at the audit's end for the next file (session 2253 writes them into it).

## Decisions made without you

1. **Run early**: this session ran while session 2242's gate (the suite, then the build) held the machine, since its model calls and readers use little memory; session 2248's landing follows 2242's.
2. **No answers file for the second read's fixture**: its grading was the readers' (the rubric is in the folder's README); the recordings are kept so session 2260 onward can grade fixes against the same answers offline.

## For Samuel's ruling

1. The new prompt drops six stated deals the old kept (a plan with a named counterparty, a sale with no buyer named, a raise at a valuation): whether a deal with one named party and an unnamed other should be kept (the old rule) or not (the new); the next file's sessions take the answer either way.
