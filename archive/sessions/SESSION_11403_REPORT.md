# Session 11403 report: chain 770, part B item 2, the equities audit

28 November 2026, the old laptop (code role), worktree `../erw-c770-c`. Read as an equity analyst: `/equities` and the price board's equities group. Model spend USD 0; no model call, no request to any service (EDGAR included), no table written, no lock, no build, no browser.

## What was made

- `docs/reviews/equities-model-audit-2026-11-28.md`: the audit (In short, the ground, the arithmetic re-done, the sample, held prices, one choice at a time, each claim against the code, ten findings, the rows for the main session).
- `docs/reviews/equities-model-audit-2026-11-28/`: every script and its printout (15 scripts, 15 printouts).
- Ten finding branches, each cut from origin/main and pushed:

| # | Branch | Head | Kind |
|---|---|---|---|
| 1 | `wip/audit-equities-1` | `c3a497089` | test only, for Samuel's ruling (High): three subsidiaries carry their parent's figures |
| 2 | `wip/audit-equities-2` | `bb7b879b1` | test only, for ruling: one business listed twice in a segment |
| 3 | `wip/audit-equities-3` | `6e9183fcb` | test only, for ruling: the SIC rule gives eight lists for nine names |
| 4 | `wip/audit-equities-4` | `62a5cd092` | test only, for ruling: capital spending's concept; debt and net income mix definitions |
| 5 | `wip/audit-equities-5` | `49f546757` | words, for landing: "Debt" named "Long-term debt" |
| 6 | `wip/audit-equities-6` | `b8310ca60` | words, for landing: the weightings named, not built; the method note holds their rule |
| 7 | `wip/audit-equities-7` | `82c073f49` | test only, for ruling: the weightings' rule leaves choices open |
| 8 | `wip/audit-equities-8` | `1f226e40d` | words, for landing: the downloads name the real builder |
| 9 | `wip/audit-equities-9` | `45e671ece` | words, for landing: the method note's first section; a data request for the source line |
| 10 | `wip/audit-equities-10` | `e6b58484f` | test only, a data request: "Silver Ores" for four coal miners |

## Key results

- The arithmetic is right: 307 of 307 newest periods, the default page's 14 marked numbers (drawn by the site's own code), 8 energy prices and 40 moves, all to the digit by an independent restatement.
- Every company is in its SIC rule's segments (307 of 307), every count right (15 of 15), no company by judgment.
- No held price in any equities file, any historical version of the list, board or price file, or any download.
- The weightings cannot be re-done: no code computes them (finding 6, finding 7).
- Sample, seed 11403: AVA, DEC, DINO, DK, EE, PR, PROP, PSX, RRC, SLB, WMB, XEL; 24 of 24 year-to-date checks agree; SLB matches its filing; the rest is data request 3.

## Tests run

- Each `tests/test_audit_equities_<n>.py` on its branch: passes. On main the words tests (5, 6, 8, 9) fail and the others pass, as designed.
- Branch 5: `tests/test_session10402_equities.py`, `10405`, `10408`, `10414` (43 passed, 1 skipped); `site/scripts/test-equities.mjs`, `test-equities-cells.mjs`, `test-equities-filed.mjs` (104, 24, 103 checks). Branch 6: the same suites and two scripts. Branch 8: the suites and `test-equities.mjs`. Branch 9: `tests/test_session10000_sec_edgar.py`.
- Merges checked by `git merge-tree`: 5 with 8, 5 with 6, 6 with 9: clean.
- Not run: the whole suite (the memory of this machine), the site build, check-routes, the snapshot: each words branch needs them at landing.

## Rows for the main session to write

Landing rows (words): branches 5, 6, 8 and 9, heads above. Data requests 1 to 5 and the five ruling lines: as written at the foot of the audit file, word for word.

## Decisions made without a human

- Page code was fixed on the words branches (site files), as chain 710's audits did; the builder and connector (the data machine's files) were not touched: their faults are data requests (findings 1, 4, 9, 10).
- Finding 1 is a data error, yet its fix moves figures: kept as a test and a ruling line by the rule, with a data request to establish the subsidiaries' own figures.
- "Silver Ores" (finding 10) was not verified against the SEC's own list of SIC codes: the SEC's site may not be requested from this machine.

## Slips

- None of the hard rules. A copy of the page-drawing script was placed in `site/scripts/` for one run (node resolves `react` from there) and removed at once; nothing of it was committed. The `site/node_modules` junction is removed before the end.
