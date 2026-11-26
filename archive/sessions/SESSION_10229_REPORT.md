# Session 10229 report: the learning pages audited (chain 710, part D)

26 November 2026, the old laptop, worktree `erw-c710-a`, unattended. Model spend USD 0. No table written, no lock taken, no live service asked, no web read, no default moved.

## What was done

- `/learn/problems` (platform tool 28: the five sets of the whole country, and set B's bill questions) and `/learn/bill` audited as an economics professor and a rate analyst would: `docs/reviews/problems-model-audit-2026-11-26.md`, evidence in `docs/reviews/problems-model-audit-2026-11-26/`.
- The arithmetic is right: 142 of 142 answer figures of 39 questions restated to the digit and in order; 503 of 503 keyed figures on the five pages equal a restated figure; the five default bills to the cent (PG&E both by its sixteen lines and by its total rates); B3 and B4 (26.91 USD, 11.72 percent; 23.70, 24.88) from the table.
- Seven findings: three Medium (the bill questions do not name their price; "not the power itself" false for Oncor; ratios worded to read backwards in Who trades with whom), four Low (legend and printed figures against the unrounded key, and no page says so; "computed when the page is built" on the page-file sets; two sentences the files contradict; a winter bill at September's price).
- Branches, each from origin/main, pushed: `wip/audit-problems-1` to `-5` (words, each drawn with the site's own code and read: pass), `wip/audit-problems-6` (a figure, test only), `wip/audit-problems-words` (the five merged, no conflict, drawn and read: pass).

## Decisions made without you

- The five live sets (A to E) were not restated: they read the live set. The two bill questions were restated from the main copy's `cost_of_power_monthly` (its September 2026 rows equal the live rows kept in `replication/bill/source_rows.csv`).
- Set B's page was drawn from the live reads kept on 16 November (a copy of the replay's stand-in, `draw_kept.mjs`), so its new words could be read without a request.
- Finding 1's fix changes a question's words, which `tests/test_session7534_problem_sets.py` compares with `replication/problem_sets/page_figures.json`: the kept file's two question strings were changed to the new words (no figure, no read).
- Finding 3 is ranked Medium though the old form can be read as the key does: the two readings give 0.60 and 1.66.
- The dated editions of 20 and 21 November keep the old words of findings 3 and 6 (frozen by design); not changed.
- The merged words branch was pushed though the five do not conflict, as the states audit did.

## For Samuel's ruling

- Finding 7, default "left as it is": value a seasonal California bill at its own season's wholesale months (or name the season beside the month). PG&E's share 11.72 to 8.08 percent (26.91 to 18.54 USD at the mean of the winter months held); September's price against the summer bill 10.26 percent. `wip/audit-problems-6`, `tests/test_audit_problems_6.py`.

## Needs the key

- Nothing.

## Rows returned to the main session

- Landing (words only): `wip/audit-problems-1` `e81079e68`, `-2` `95eb87907`, `-3` `3e1d0a97b`, `-4` `d2bbd7019`, `-5` `f13ad4022`, or merged `wip/audit-problems-words` `67e2ae39a`.
- Data request: the taxes and local fees on a San Francisco PG&E bill and a Dallas Oncor bill, each with its rate and source, to state the default bills and their wholesale share with them.
- For window A: `tests/test_session7534_problem_sets.py` (the replay's network hour, 2026-11-23 against the kept 2026-11-15) and `tests/test_session8901_problem_sets_country.py` (it expects no edition to hold the sets of the whole country; the editions of 20 and 21 November do) fail on origin/main `f904d2427` before any change.

## Problems

- One push of `wip/audit-problems-words` was refused by the remote ("failed") and went through on the second try.
- A first draft of finding 6's fix pointed to "question 5"; the page numbers the questions in the guide's order (the flows are question 4), found on the drawing and corrected before the commit.
