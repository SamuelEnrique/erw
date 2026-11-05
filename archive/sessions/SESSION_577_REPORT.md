# Session 577 report: the audits' remaining fixes that need no ruling

22 October 2026, about 23:45 (21 October) to 00:20 UTC, unattended, on samueloldlaptop (the code machine), in the worktree `C:/Users/lossa/Documents/erw-577` on `wip/577-s` (from `origin/wip/506-combined` at `4913f507`; origin/main had nothing newer). Chain `queue/done/034-night-22-october-code.md`, session 577. Model spend USD 0; no model called, no past issue rewritten, no warehouse data written, no web request, no `site/` change (so no build, no shots, no check-values).

## Summary

Of the 30 ranked fixes of the Digest audit and the Roundup audit of 21 October, 17 are landed whole (13 by session 470, 2 by session 402, 1 by 531, 1 by 533); 3 were finished here where session 470 had left half (Digest 8 and 9, Roundup 10); 1 is done by session 498 on chain 023's branch (Roundup 13, the trace); Digest 11 is half landed (470: no disasters) and its pun half waits for a ruling; Digest 10 is open (a source and two rulings); and session 470's seven wait for Samuel (Digest 1, 2, 6, 15, Roundup 3, 6, 7). The full table, fix by fix, is at the foot of each audit under "State on 22 October".

## What was done

1. **A why line ends with a stop before the figures** (Digest fix 8, its second half). New `brief.why_line`: `plain` (470's adjective cut), then `money_style`, then a stop when the line has none. Every why line of the Digest (top 10, By sector, AI and power, the policy actions) and of the Roundup (weekend, five of the week, the policy of the week and its two others) goes through it. "Escalation affecting global oil markets and prices parties: Iran." (20 October, top 8) now prints "...prices. parties: Iran."
2. **One money style in the why lines too** (Digest fix 9): session 470 styled the price field only; the why lines carried "$3.2bn", "$4.2B", "USD120 billion". They now print "USD 3.2 billion" and so on, with the article following the code ("a USD 800 million loan"). `MONEY` no longer reads a currency code inside a word ("fraud 5" printed "frAUD 5" before; "amateur 5", "amatEUR 5"). An earlier issue's sum printed in the new style is still read by `issue_items`, so `not_shown_before` keeps working (tested).
3. **The deals-by-month chart names deal types in words** (Roundup fix 10, its second half): `deals_by_month.LABEL`, "acquisition" for `m_and_a` as the tracker (`site/lib/deals2.ts`) and the Roundup's table say it; the legend and the note. The frame keeps the codes (it is data). The stored weeks under `docs/analysis/` are not touched; the next weekly run writes the words.
4. **The state of every fix**, at the foot of `docs/reviews/digest-audit-2026-10-21.md` and `roundup-audit-2026-10-21.md`, with where each landed.

The email (`email_digest.py`) reads the why lines from the page, so it carries items 1 and 2 with no change of its own.

## The 30 fixes, their state

| Audit, rank | State | Where |
|---|---|---|
| Digest 1, held prices | waiting: ruling | |
| Digest 2, the window | waiting: ruling | |
| Digest 3, 4, 5, 12, 16, 17 | landed | 470, on main |
| Digest 6, AI tie-break | waiting: ruling | |
| Digest 7, Google News | landed, no-ruling form | 470, on main |
| Digest 8, the voice | landed: adjectives 470 (on main), the stop 577 | `wip/577-s` |
| Digest 9, money style | landed: `detail` 470 (on main), why lines 577 | `wip/577-s` |
| Digest 10, chart of the day | open: in `daily_chart.py`; caveat needs a source, the floor and the drafts are rulings | |
| Digest 11, fun fact | disasters landed (470, on main); the pun half: ruling (below) | |
| Digest 13, 14 | landed | 402, on main |
| Digest 15, two minutes | waiting: ruling | |
| Roundup 1, 2, 4, 5, 9, 12 | landed | 470, on main (9 extended by 577) |
| Roundup 3, coverage charts | waiting: ruling; session 119 already excludes them | 119, on main |
| Roundup 6, 7 | waiting: ruling | |
| Roundup 8 | landed | 531, on main |
| Roundup 10, codes as words | landed: table 470 (on main), chart 577 | `wip/577-s` |
| Roundup 11 | landed | 533, on main |
| Roundup 13, the trace | done | 498, `wip/506-combined` (chain 023's landing) |

## Checks

Every gate redirected to a file under `C:/Users/lossa/Documents/erw/runs/chain_034/s577/`, never piped; the exit read before the next step.

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 577"` (main checkout) | 0 | on duty until 2026-10-22 15:50 UTC |
| `tests.test_session577` (first run) | 1 | 15 tests, 1 failure: the test's own wrong case ("gbp5" is a sum); case replaced |
| `tests.test_session577` | 0 | 15 tests OK |
| `money_style` on the code before the change (stash) | 0 | "frAUD 5 times over", "amatEUR 5 teams": the fault the new test pins |
| 470, 176, 192, 206, 532, 119, 182_flow, 232, 34, 63, 533, 577 (with two names that do not exist, 21 and 24) | 1 | 254 tests; the 2 errors are the two missing modules, no test failed |
| every test module that reads `roundup`, `brief`, `email_digest` or `deals_by_month` (36 modules, `wide_mods.txt`) | 0 | 575 tests OK, 9 skipped |
| em and en dashes in the changed files | 0 | none |
| whole suite, build, check-values, shots | not run | no `site/` change; the landing (session 589) runs the suite |

## Decisions made without you

1. The audits' fix 8 and 9 were finished in one function (`why_line`) rather than in `plain`, so `plain`'s pinned outputs (session 470's tests) stay as they were.
2. A policy action's impact read (`policy_reads.plain_read`) goes through `why_line` too, so it gets the stop and the money style like the why line it replaces.
3. "a USD" and "an AUD": the article follows the currency code as said, since "an $800MM" was right only for the dollar sign.
4. The chart legend says "acquisition" for `m_and_a`, the tracker's and the Roundup table's word, not the audit's "M&A".
5. Roundup 13 is counted done by session 498's `check_roundup.py` (76 equal, 4 revised, 4 gaps, 0 failed), though it is not on main until chain 023 lands.
6. Digest 10 is left open: it lives in `daily_chart.py`, and each of its three parts needs a source or a ruling.
7. Nothing was landed: the brief says session 589 lands the chain (the part's "Land" is read as that).

## For Samuel's ruling

- The pun half of Digest fix 11 (a pun that states a fact needs a source): a rule by pattern ("no wonder", "because", "since", "so") would refuse the 2 October pun and 2 of the bank's 8 other puns (the kWh pun, the Btu match); whether puns are held to that, or to their sources, is a wording ruling.
- Whether the no-model headlines (the publishers' own titles, said as such) may have the voice's adjectives cut ("Google enters massive 3.6-GW power deal", W41).
- Roundup fix 3 may be closed: session 119 (5 October) already keeps the coverage templates from the chart of the week; what is left is whether to divide them by scored stories.
- The seven rulings of session 470's list and the chart of the day's floor and caveat, unchanged.

## To finish

- Nothing for this session. Session 589 lands `wip/577-s` with the chain (the suite and the usual gate; no page changes, so the snapshot comparison should read 0 differences). The next Digest and Roundup written after the landing are the first to carry the changes.

## Files

- `warehouse/news/brief.py` (`why_line`, `MONEY`, the why lines of `main` and `policy_actions_lines`), `warehouse/news/roundup.py` (the why lines and the policy read), `warehouse/analysis/templates/deals_by_month.py` (`LABEL`) (changed).
- `tests/test_session577.py` (new).
- `docs/reviews/digest-audit-2026-10-21.md`, `docs/reviews/roundup-audit-2026-10-21.md` ("State on 22 October", appended).
- This report.
