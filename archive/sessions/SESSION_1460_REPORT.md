# Session 1460 report: faults 28 and 29, the Roundup's five numbers without ids in the text

Energy Research Warehouse (ERW), session 1460, chain 150, samueloldlaptop, 6 November 2026, 04:34 to 04:41 UTC. Model: Claude Opus 5.5 (this window's). Model spend USD 0. No warehouse data written; nothing sent or posted; no web request. Branch `wip/1460-periodicals`, cut from `wip/1459-periodicals`.

## The faults

Faults 28 and 29 of `docs/reviews/periodicals-faults-2026-11-05.md`, "in part" after chain 149 (the ids, the template and the path stayed in the rows as the tracer's keys):

- Faulted (W43): "**Deal of the week, by US dollars:** USD 45 billion, Anthropic and Nscale, cloud computing deal (offtake, 2026-10-19; `energy_deals` deal:d7ed182372909e6d)."
- Written instead: "**Deal of the week, by US dollars:** USD 45 billion, Anthropic and Nscale, cloud computing deal (offtake, 2026-10-19)."
- Faulted (W44): "**From the chart of the week:** WTI spot price at Cushing, weekly mean: 107 USD/bbl in 2026-10-19 to 2026-10-25 (the week before: ...) (template `watch_wti`, `docs/analysis/2026-W44/chart_of_the_week.json`)."
- Written instead: the same row ending at "(the week before: the chart's latest period ends before this week)."; under the five, one line: "Tables: the deal of the week, `energy_deals` deal:...; the datacenter load, `datacenter_projects` ...; the chart's figure, template `watch_wti`, `docs/analysis/2026-W44/chart_of_the_week.json`."

## What it did, with commits

- `b363855b9`: `roundup.five_numbers` collects each row's key and returns the five rows, then a blank line and the Tables line. The email's `block` already draws a "Tables:" line at 12 px in grey (session 1445) and the page's `sourceTrail` closes it under "Sources" (session 1449), so neither changed. The opening number, which takes the deal's or the load's row text, loses the id with it. `scripts/check_roundup.py`: `five_keyed` reads a key from the Tables line, or from the row in an issue written before; the deal, the deal by MW, the load and the chart checks use it.
- Tests: `Session1460FiveKeys` (the tracer reads the three keys on the Tables line with their values; an issue in the old form is read as it was; no row holds an id, a template or a path; the email prints the line small and grey); `test_session806.TheFiveNumbers` and `TheFiveNumbers.test_each_line_in_the_checker_s_form` re-pinned to the new form.
- The faults file: rows 28 and 29 and a line for chain 150.

## Checks

| Check | Exit | Result |
|---|---|---|
| `pytest` over the 36 test modules that name the Roundup | 0 | 697 passed, 9 skipped |
| `check_roundup.five_checks` over the dry runs of sessions 1436 (W43, W44) and 1451 (W44), the old form | | each traced as before (W43: the price move, its change, US48, the deal, the load, the chart) |

## Found

- The five stored Roundups (`docs/roundup/2026-W39` to `W44`) hold no "The week in five numbers" section (written before session 806's shape); only the dry runs do. Nothing stored needs the old form, but it is read for the dry runs and for any issue written before this landing.
- A Bash heredoc dropped the backslashes of a test's `\n` escapes (as the memory note says); the class was removed and written again with the Edit tool before any commit.

## Decisions made without you

- The keys' line is named "Tables:" so the email and the page treat it as the existing source trail, rather than a new kind of line.

## For Samuel's ruling

- None.
