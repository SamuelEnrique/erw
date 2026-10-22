# Session 717 report: the lab's path, walked

22 October 2026, from 11:40 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-717` on `wip/717-allgrids` (cut from `wip/716-allgrids`). Chain `queue/done/050-night-23-october-code-allgrids.md`, session 717. Model spend USD 0. No warehouse data written; no request to a publisher.

## Read these first

- **`docs/reviews/siting-path.md`**: the questions an infrastructure lead at a lab asks when siting a gigawatt, each cited to the research report (`docs/reviews/research/deep-research-report.md`). Each has its click path on the tab, walked on a build in the internal view with a load of 1,000 MW, with what the page showed and whether it answered. Screenshots: `docs/brand/review-717/`.
- **What it answered**:
  - The year all-in for two ERCOT sites (HB_WEST USD 321.9 million against LZ_NORTH USD 340.2 million at 1 GW, a datacenter).
  - What flexibility buys (HB_WEST all-in 30.64 against 40.83 flat).
  - Carbon over the hours run (CAISO NP15 92.9 kg for the electrolyzer).
  - Demand growth and generation coming by grid, the cheapest node (BBREEZE_1_2, 31.66 all-in), the gaps, and an address a reader can send.
- **What it answered in part**:
  - All-in only inside ERCOT: 14 rows. Every other grid lacks transmission or holds capacity under a license.
  - Time to connect is a generator's wait.
  - The utility is the state's largest seller, not the row's own.
- **Three things broke, and were mended** (no ruling needed):
  1. The sorted column was off the screen to the right; it is now drawn first.
  2. The line of the nodes' shared figures fell apart into blocks; it is one sentence now, each figure keyed.
  3. The node list's header kept a cardinal band; it now has the brand's grey header, and its figures are mono.
- **No figure moved**: check-values 2,487 of 2,487; the existing tab 0 differences.

## What to review

1. `docs/reviews/siting-path.md`: the ten steps, each with its address. Open any address on production after the landing, in the internal view.
2. `docs/brand/review-717/q1_allin_cheapest.png` against `q1_allin_cheapest_after.png` (the sorted column), and `q7_nodes_cheapest.png` against `q7_nodes_cheapest_after.png` (the shared line, the header).

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `tests.test_session717`, `709` (its pin follows the shared line), `710`, `714`, `237` | 0 | OK |
| `db_probe.py` | 0 | 0.73 s |
| `npm run build` (lock `s717`, beat), three times | 0 | |
| check-values, `CHECK_VALUES_PAGES=/cost-of-power` | 0 | 2,487 of 2,487 |
| `check-existing-tab.mjs`, production against the build | 0 | 0 differences |

## The landing

With sessions 713 to 721, or the next combined push (see the chain's note).

## Decisions made without you

1. **The walk's load is 1 GW**, the scale the report has the labs committing to. The default (100 MW) gives the same prices per MWh.
2. **The sorted column moves first**, rather than the table scrolling to it: a sent address then shows the figure it sorts by.

## For Samuel's ruling

- Nothing new. The walk's open items are session 713's gaps and session 716's page weight.

## Files

- New: `docs/reviews/siting-path.md`, `tests/test_session717.py`, `docs/brand/review-717/`, this report.
- Changed: `site/app/cost-of-power/AllGridsView.tsx` (`SharedLine`, the sorted column first), `site/app/tokens.css` (the node list's header and figures), `tests/test_session709.py` (its pin).
