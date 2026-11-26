# Session 10224 report (chain 710, part D: the industry page audited)

Old laptop, 26 November 2026, worktree `erw-c710-a`, branch `wip/audit-industry-doc`. Model spend USD 0; no live service, no web read, no table written, no default moved.

## What was done

- `/industry` audited as an industrial energy buyer, an economist of manufacturing energy use and a fund analyst would: `docs/reviews/industry-model-audit-2026-11-26.md`, evidence in `docs/reviews/industry-model-audit-2026-11-26/`.
- **The arithmetic is right:** an independent restatement from `site/data/industry.json` gives 535 of 535 marked figures of the default view (and 586 of 586 on a second set of choices), both orders and 8 labels; the file's Monthly Energy Review and Form EIA-861M months equal the main copy's tables value for value.
- Findings: 3 moderate, 5 low. Words: 1 (the sector and the survey count different things), 2 (electricity bought, not used), 3 (the average price is all fuels, per a smaller quantity than the total, not a tariff), 4 ("not held" with four codes; * is an estimate under 0.5), 5 (the decisions name every opening choice), 6 (the MECS note's "total primary energy" is end use). For ruling: 7 (one month against twelve), 8 (no share in any census region).
- Branches, each from origin/main, pushed: `wip/audit-industry-1` to `-6` (words, each drawn and read: pass), `wip/audit-industry-7` and `-8` (test only, not for landing), `wip/audit-industry-words` (the six merged, one conflict in the method note resolved by keeping both; drawn and read: pass; 40 tests and the site's render test 74 of 74).

## Decisions made without you

- The words fixes go in hovers and one lead hint, not new visible paragraphs, as the page's own style is; the headline label gains "by fuel".
- The price hover says "a smaller quantity than the total" and no more: what EIA leaves out of TEICD's quantity is EIA's rule, not read here (data request 2).
- No new figure is drawn by a words fix (no ratio in the lead hint): numbers went to the method note only.
- The builder's note words (`warehouse/derived/industry_page.py`) were changed with finding 4; they reach the file at the data machine's next build, and the page's hover no longer reads them.

## For Samuel's ruling (default "left as it is")

- Finding 7, `wip/audit-industry-7`: add twelve months on the twelve before beside the one-month change. Measured: total -1.9 and +0.4 percent; petroleum -6.6 and +0.8.
- Finding 8, `wip/audit-industry-8`: in a census region draw each share on the survey's own regional total. Measured: no share in any region today; the South's Chemicals would be 32.8 percent.

## Needs the key

- Nothing.

## Problems

- One drawing ran when free memory was 247,572 kB (under the 400,000 floor): the memory read and the node drawing were chained in one command, so the reading did not gate the run. Every later node run had its own memory read first (1.0 to 1.8 GB free).
- A stray copy to a path outside the worktree was in one command (`cp ... /tmp_none`); it failed with nothing written.
- `tests/test_session8012_industry.py` runs node with code on its command line, by its own design; it was run unchanged as one of the page's tests.
