# Session 1688 report: /learn/bill: every data cell has a header

Energy Research Warehouse (ERW), session 1688, chain 189, samueloldlaptop, 6 November 2026, 16:50 to 16:53 UTC. Model: Claude Opus 5.5 (the file names Fable 5.1). Model spend USD 0. No warehouse data written; nothing sent or posted. Branch `wip/1688-a11y`, cut from `origin/main`.

## What it did, with commits

- **The fix** (`site/app/learn/bill/BillCalc.tsx`): each row's first cell is a header.
  - A group row's cell is `<th scope="rowgroup">`.
  - Each line's name, the total's and the per-kWh's are `<th scope="row">`.
  - Their classes (`text-left`, `font-normal`) keep the look.
- **Tests**: `tests/test_session1688.py` (3 tests), and the seven older tests that read the page (sessions 53, 203, 239, 241a, 242, 288, 335), 88 tests in all.
- The file had not changed since 23 October (session 2403).

## Decisions made without you

- None.

## For Samuel's ruling

- None.
