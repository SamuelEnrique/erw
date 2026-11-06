# Session 1459 report: fault 16, the stored fun facts in the issue's style

Energy Research Warehouse (ERW), session 1459, chain 150, samueloldlaptop, 6 November 2026, 04:30 to 04:34 UTC. Model: Claude Opus 5.5 (this window's). Model spend USD 0. No warehouse data written (the fact bank untouched); nothing sent or posted; no web request. Branch `wip/1459-periodicals`, cut from `wip/1458-periodicals`.

## The fault

Fault 16 of `docs/reviews/periodicals-faults-2026-11-05.md`, "in part" after chain 149 (session 1448 styled the facts the generator writes from now on; the bank's stored rows kept their text):

- Faulted: "ERCOT's real-time price at HB_WEST reached 9310.49 USD/MWh in a 15-minute interval in 2021 ... with 4266."
- Written instead: "ERCOT's real-time price at HB_WEST reached 9,310.49 USD/MWh in a 15-minute interval in 2021 ... with 4,266."

## What it did, with commits

- `6e773f052`: `funfact.issue_style(text)` puts the thousands separator in a fact's numbers (9310.49, 4266, 1700 MW); a year (an integer from 1000 to 2100 with no unit after it), a date's digits and an identifier are left. `write_item` styles the fact and its second half when a bank row becomes the day's item, before `check_record` reads it (the literal number check reads "9,310.49" and "9310.49" as one). The bank (`warehouse/news/facts/bank.csv`) keeps the text it was verified with; no stored item of a past issue is rewritten.
- Tests: `Session1459StoredFactsStyled` (the styles; every verified bank row, styled, passes its check, at least four rows change, the bank's text unchanged; the day's item, written into the test's own folder, prints "9,310.49 USD/MWh" and its markdown holds the item's fact, so `check_digest.py`'s "the Digest's fun fact is its item's" holds).
- The faults file: row 16's state and a line for chain 150.

## Checks

| Check | Exit | Result |
|---|---|---|
| `pytest tests/test_periodicals.py test_session176 test_session202 test_session470 test_session801 test_session807` | 0 | 232 passed, 1 skipped |

## Found

- Four verified bank rows change when styled (the HB_HOUSTON, HB_NORTH and HB_WEST peak rows and "1700 MW"); the others hold no bare number of four digits that is not a year.
- A Python heredoc turned the `\b` of one pattern into a backspace character when the file was first written; found by the first try and corrected (the memory note on heredocs holds for Python's strings too).

## Decisions made without you

- The rule for a year: an integer from 1000 to 2100 with no unit after it is a year and keeps its form; "2,021 MWh" would be styled.

## For Samuel's ruling

- None.
