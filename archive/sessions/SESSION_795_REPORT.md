# Session 795 report: nodes that settle alike

22 October 2026, from 22:38 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-795` on `wip/795-allgrids` (cut from `wip/794-allgrids`). Chain `queue/done/065-late-22-october-code-allgrids-5.md`, session 795. Model spend USD 0. No warehouse data written; no request to a publisher. The read: the archive's copy of `node_basis_daily` on this machine.

## Read these first

- **The builder groups the nodes whose day-ahead basis is the same on every day `node_basis_daily` holds, with the same days**: exact equality of the table's values. 175 nodes fall in 77 groups, the largest of 5 (AE_RN with BCH_RN and MYR_ALL, for one).
- **A node's panel names the others in its group**, and says the table does not say why: "It settles at the same day-ahead prices as BCH_RN, MYR_ALL: the same basis to HB_HUBAVG on every day ... and the same days."
- **Session 723's pair is not a group.** BBREEZE_1_2 and ELSAUZ_ALL read the same to the cent over twelve months, but July 2026's means differ by 0.0001, so not every day is equal and the exact rule keeps them apart. The test's first example assumed otherwise and was corrected.
- **No figure moved**: the line adds words, no key.

## What to review

1. After the landing, `https://erw-flame.vercel.app/cost-of-power?view=allgrids&rows=nodes&node=ercot%3AAE_RN` (internal view): the line under the node's percentiles.
2. Shots: `docs/brand/review-795/`.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `warehouse/derived/siting_page.py --in-dir-first ...` | 0 | nodes.json rewritten (369 KB); 77 groups |
| `tests.test_session795`, `746`, `711` | 0 | OK (after the example's correction) |
| check-values on 796's build | 0 | 2,963 of 2,963 |

## The landing

Sessions 794 to 799 landed in one push: see `SESSION_799_REPORT.md`, "The landing".

## Decisions made without you

1. **Exact equality, every day**, and the same days. A near match (equal at two decimals) is not a group, since "settles at the same prices" must be true to the table.
2. **No reason given**: the table holds prices, not the reason two settlement points share them.

## For Samuel's ruling

- Nothing new.

## Files

- Changed: `warehouse/derived/siting_page.py` (`same`), `site/data/siting/nodes.json`, `site/lib/siting.ts` (`NodeRow.same`), `site/app/cost-of-power/AllGridsView.tsx` (the panel's line).
- New: `tests/test_session795.py`, `docs/brand/review-795/`, this report.
