# Session 1110 report: the number check lets nothing invented through

23 October 2026, about 19:30 to 20:30 UTC, on samueloldlaptop, unattended, on `wip/1110-ask` (cut from `wip/1109-ask`). Chain `queue/done/075-morning-23-october-code-ask-board.md`. Model spend USD 0. No database read, no web request.

## Read these first

- `warehouse/chat/ask.py` `is_name`, `unit_mismatches` (and `site/lib/chat/ask.ts` `isName`, `unitMismatches`, the same rules).
- `tests/fixtures/session1110/answers.json`: the six answers and what each check must return.

## What was done

- **Every figure in a wrong answer that no tool returned**, listed from session 320's run (the server's log of the number check, `runs/chain_oct19/s320/server.out`): `1000` in the eight per-kW first drafts (a conversion no tool returned; the check stopped it, rightly) and `930` in four first drafts (d01, d02, d05, d08: the form EIA-930 read as a figure; the check stopped right drafts). No final answer stated an untraced figure (session 539).
- **A name is not a figure.** Digits after a letter and a hyphen (EIA-930, EIA-860M, COVID-19) are no longer read as numbers, in either language. The four drafts' `930` now passes; a minus after a space or a bracket is still a minus; a date is still three numbers.
- **The unit.** A figure stated in a money unit (USD per MWh, per MW, per kW, per kWh, written with USD, US dollars, dollars or a `$` before it) must match a figure a tool returned in that unit. A tool number takes its unit from its own key (`..._usd_per_mw`, `value_usd_per_kw`), else from the nearest `unit` or single `units` above it. A draft is sent back only when every returned number it matches is in another unit (81,402.19 written as USD per kW when the tool gave USD/MW), with the problem named: "numbers stated in a unit no tool result gives them in". A number no result places in a unit (the question's text, a count, a result over mixed units) and a unit with no money or a compound unit (MWh per MW, USD per MW-month) are not judged: the check stops only what it can prove wrong. The rounding is the method's own: the precision the answer writes, as before.
- **The refusal's words.** On a second miss the answer is "The warehouse does not hold that figure: the numbers in my draft could not all be traced to a warehouse query. Try asking for one value, one table and one period at a time." (`REFUSAL` in `ask.py`, exported to `site/lib/chat/spec.json`). The retry stays one, with the mismatches named.

## What to review

1. `https://github.com/SamuelEnrique/erw/blob/main/tests/fixtures/session1110/answers.json`: the six answers, each with what the check returns.
2. `warehouse/chat/ask.py`, search `unit_mismatches`: the rule and its limits in the comment above it.

## Checks

- `node --import ./scripts/alias-register.mjs scripts/test-ask-1110.mjs` (in `site/`): exit 0, 5 of 5.
- `python -m unittest tests.test_session1110`: exit 0, 6 tests (both languages return the same on the six).
- The Ask test files of sessions 35, 92, 103, 121, 137, 143, 153, 156, 161, 168, 267, 302, 320, 1109, 1110: exit 0 (41 skipped, as on the base). Two old tests read a line of `ask.ts` word for word: session 143's early-words line is left as it was (the whole check, units included, still runs on every draft); session 161's `test-ask-speed.mjs` mend line now reads the new condition, so a figure in the wrong unit is never mended away.
- Em dashes in the changed files: 0.

## The landing

Lands with sessions 1108 to 1112 in one push.

## Decisions made without you

1. **The unit rule judges money units only, and only when every matching number is placed in another unit.** A broader rule (every unit, MW and MWh included) would send right answers back where a table writes a unit the tools do not carry. Reversible: one function in each language.
2. **The refusal's words changed** to begin with the chain's sentence, on `/ask` and every chat that uses the general refusal. Reversible: `REFUSAL` in `ask.py` and an export.

## For Samuel's ruling

- None new.
