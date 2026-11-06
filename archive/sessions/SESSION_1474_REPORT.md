# Session 1474 report: fault 52, the five numbers and the tables' floor

Energy Research Warehouse (ERW), session 1474, chain 154, samueloldlaptop, 6 November 2026, 07:16 to 07:22 UTC. Model: Claude Opus 5.5 (this window's). Model spend USD 0. No warehouse data written; nothing sent or posted; no web request. Branch `wip/1474-periodicals`, cut from `wip/1473-periodicals`.

## The fault

Row 52 of `docs/reviews/periodicals-faults-2026-11-05.md` (session 1468's dry run of W45): the five numbers took the deal (USD 19 billion, TeraWulf) and the load (702 MW, Google) from rows at confidence 0.55, under the tables' floor of 0.7 (`ROW_CONFIDENCE`, ruling item 11), so the Deals table below did not list the deal and the datacenter table printed the load as "not stated".

- Faulted: "**Deal of the week, by US dollars:** USD 19 billion, TeraWulf, ..." over a Deals table without it.
- Written instead (W45's rows): "**Deal of the week, by US dollars:** USD 938 million, Deutsche Bank and Rabobank and Return, Germany BESS portfolio (project finance, 2026-11-05)."; for the load, "no facility first reported this week with its MW passes the datacenter table's floor (1 under it)", with the next price move in its place as session 1446's stand-in does.

## What it did, with commits

- `16aa9c7f6`: `five_numbers` filters the week's deals and datacenter rows with `row_passes` (the tables' own floor) before it picks; when every row of the week is under the floor the row says so, with the count.
- Tests: `Session1474FiveReadTheFloor`. Three fixtures given a passing confidence (`test_session806`'s two tables, two frames of `test_periodicals`): their rows had no confidence column and would now fall under the floor.
- The faults file: row 52 fixed.

## Checks

| Check | Exit | Result |
|---|---|---|
| pytest over the 36 modules that name the Roundup | 0 | 711 passed, 9 skipped |

## Decisions made without you

- The five's floor is the tables' (0.7), not a lower one of their own: one figure, one rule.

## For Samuel's ruling

- None.
