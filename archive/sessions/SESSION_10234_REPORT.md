# Session 10234 report: the chat over the warehouse audited (chain 710, part D)

- Worktree `C:\Users\lossa\Documents\erw-c710-b`, branch `wip/audit-ask-doc`, unattended on the old laptop. Model spend USD 0: no model called, no client of the provider built (stubs only), every python run under `ERW_SPEND_CAP_USD=0`. No request to a live service, no build, no browser, no table written, no lock taken.
- The audit: `docs/reviews/ask-model-audit-2026-11-26.md`, its evidence `docs/reviews/ask-model-audit-2026-11-26/`.
- The number check does what its code does and less than its note and the About page say: it traces a figure's magnitude to any number of any source (every tool result, every tool argument, the question), never to its row, grid, day or sign. Eight findings: one high (1), four medium (2, 3, 4, 6), three low (5, 7, 8). No security weakness of high severity; nothing held back.
- 45 stored answers re-scored by hand (the trader's twenty and the held-out set): every grade as stored.
- Branches pushed: `wip/audit-ask-1` to `-8`. Words only, for landing: 3, 4, 5, 6, 7 (4, 5 and 7 drawn with the site's own code, each read once more: pass). Behaviour, not for landing: 1, 2, 8. The words branches touch different files: no `wip/audit-ask-words` was needed.

## Decisions made without you

- The site's loop (`site/lib/chat/ask.ts`) was audited through its Python twin, which `tests/test_session1300.py` and `test_session1309.py` hold equal, and from its source; no node test of the loop was written.
- The general form was drawn with its state handed in (React's `useState` stood in for before the form is imported): a static draw shows only the empty box.
- The privacy page's identical sentence was fixed on the same branch as /terms (finding 7): one claim, two pages.
- The About page's scores were left as they stand; only "last asked" and the check's description changed, so no figure on the page moves.
- `test_session137.py::test_the_panels_own_tests_pass` fails on clean origin/main as on branch 5 (the board's ERCOT rows): not this session's, not mended.

## For Samuel's ruling

- Finding 1: whether the number check binds each figure to its row (entity, time, sign) and stops counting the model's own tool arguments as sources. Default: left as it is. Measured: dropping the question and the arguments from the sources would send back 80 of the 1,327 stored answers, nearly all right ones repeating the question's terms.
- Finding 2: whether `eval_loop.py` counts an errored question at what its client spent, and `llm.check_cap` keeps a reserve and refuses a cap while the ledger is off; and whether a visitor's ledger write is strict. Default: left as it is. Measured: 2 stored questions recorded at USD 0; no saved answer changes.
- Finding 8: whether a held grid's answer gets its own status and heading. Default: left as it is. Measured: 45 of 48 stored held-grid answers would change heading; no words change.

## Needs the key

- Any fix of findings 1, 2 (the site's half) or 8 is proved by asking the evaluation sets again, which calls the model: after 1 December 2026, when the key returns, and only on Samuel's word.
