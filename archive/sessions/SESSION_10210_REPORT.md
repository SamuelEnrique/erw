# Session 10210 report: the curtailment tracker audited

Chain 710, part D, the old laptop, 26 November 2026. Worktree `erw-c710-b`, branch `wip/audit-curtailment-doc`. The audit: `docs/reviews/curtailment-model-audit-2026-11-26.md`, its evidence in the folder of the same name.

## What was done

- `/curtailment` and `/curtailment/where-when` drawn to HTML with the site's own code (nine addresses), the two live reads answered from the main copy's tables (read only), every other request refused.
- The default view (CAISO, January to October 2026, a 4-hour battery) restated independently: 141 of 141 figures equal, the monthly table and the 78 days' totals too.
- "What it is worth" restated from CAISO's intervals and the hubs' prices, never replicated before: 86 of 88 hub, market and month cells agree (October 2026 at two hubs lacks 24 price hours on this machine).
- Nine rules changed one at a time and measured; every claim of the page and its hovers set against the code.
- Seven findings: 2 Major, 2 Moderate, 3 Minor. Four words branches for landing (2, 4, 5, 6), each drawn and read once more (pass); two figure branches with tests, not for landing (1, 3); one data request (7).
- The where-when trend legend is still wrong on main ("CAISO, the whole system: curtailment" over solar alone); the fix of 20 November (`4f3247287`) never landed; not redone.

## Branches

| Branch | Head | Kind | Test |
|---|---|---|---|
| `wip/audit-curtailment-1` | `d64aabbbf` | figure, for the owner | `tests/test_audit_curtailment_1.py` |
| `wip/audit-curtailment-2` | `c85a439e5` | words, for landing | `tests/test_audit_curtailment_2.py` |
| `wip/audit-curtailment-3` | `9b3cc05a2` | figure, for the owner | `tests/test_audit_curtailment_3.py` |
| `wip/audit-curtailment-4` | `74a068cc2` | words, for landing | `tests/test_audit_curtailment_4.py`, `site/scripts/test-curtailment-read.mjs` |
| `wip/audit-curtailment-5` | `ad090240b` | words, for landing | `tests/test_audit_curtailment_5.py` |
| `wip/audit-curtailment-6` | `c59d76994` | words, for landing | `tests/test_audit_curtailment_6.py` |

- Branches 2, 4, 5 and 6 merged onto origin/main together without a conflict in a trial; their tests and the site's read script (23 of 23) pass on the merge.

## Decisions made without you

- Words fixes 2, 4 and 6 add short sentences to the page's face, where session 144 kept every rule in the method note. Each is a sentence the page lacked about what a figure is; the face test of session 144 passes (its forbidden words refused "does not say", so finding 4's clause reads "not a count of").
- Finding 5 changes the where-when builder's hover words; the committed `where_when.json` keeps the old words until the data machine's next build. A built file was not edited by hand.
- Finding 6 moved its constant in a second commit so that it lands beside finding 4 without a conflict.
- Severity of finding 1 set Major (a licence matter), though the page is in review and no visitor sees it.

## For Samuel's ruling

- **Finding 1.** `/curtailment?grid=isone` and `?grid=nyiso` print hours under USD 5 (ISO-NE 1, NYISO 17) from `iso_hub_prices_history`, "license needed" since 21 October, in the summary and a headline. Remove them? Default: left as it is.
- **Finding 3.** "A flat load in those hours" counts every hour with any curtailment; from 2026 that is 80.5 percent of hours (55.6 in 2025). Count only hours with at least 100 MWh? 2026's figure 26.96 would become about 10.82 USD per MWh, 2025's 21.57 about 13.19. Default: left as it is.
- Row 3 of `curtailment-faults-2026-11-16.md` (Texas, 1 November, the doubled limit) still waits: the day row prints 21,817 MWh of wind below the limit, 6,392.8 of it from that hour.

## Needs the key

- Nothing. No model was called (spend USD 0).

## Problems

- Two trivial `python -c` calls (`print(1)` and `pass`) were run by mistake, against the chain's rule of no inline one-liners; no prompt followed and nothing was written. One Bash call used a here-string (`<<< ""`), also against the rule's spirit; it did nothing.
- One push of `wip/audit-curtailment-5` was refused by the remote ("failed") and went through on the second try.
- `iso_curtailment_monthly` on this machine ends in September 2026 for CAISO; the drawn "By month" table is the page on those rows.
