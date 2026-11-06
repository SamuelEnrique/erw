# Session 1472 report: fault 50, the deal of the week's words

Energy Research Warehouse (ERW), session 1472, chain 154, samueloldlaptop, 6 November 2026, 07:11 to 07:18 UTC. Model: Claude Opus 5.5 (this window's). Model spend USD 0. No warehouse data written; nothing sent or posted; no web request. Branch `wip/1472-periodicals`, cut from `origin/main` (every branch of chain 150 an ancestor of main).

## The fault

Row 50 of `docs/reviews/periodicals-faults-2026-11-05.md` (session 1468's dry run of W45):

- Faulted: "**Deal of the week, by US dollars:** USD 19 billion, TeraWulf, TeraWulf data center in Kentucky (other, 2026-11-05)."
- Written instead: "**Deal of the week, by US dollars:** USD 19 billion, TeraWulf data center in Kentucky (2026-11-05)."

## What it did, with commits

- `7e369a2eb`: `roundup.deal_words(r)` writes the row after its sum, for both the dollar and the MW forms: the parties (a party the asset already names, or a party named twice, left out), the asset, and in brackets the kind (not "other") and the date; "parties not stated" only when neither a party nor an asset is held. The opening number takes the row's text, so it reads the same.
- Tests: `Session1472DealWords` (the W45 row, the tracer's `five_keyed` reading it, three other rows); the 36 modules naming the Roundup pass.
- The faults file: row 50 fixed.

## Checks

| Check | Exit | Result |
|---|---|---|
| pytest over the 36 modules that name the Roundup | 0 | 706 passed, 9 skipped |
| `pytest tests/test_periodicals.py -k 1472` | 0 | 2 passed |

## Decisions made without you

- None.

## For Samuel's ruling

- None.
