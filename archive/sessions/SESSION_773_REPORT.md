# Session 773 report: a third card: where a battery's day swings most

22 October 2026, from 20:35 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-773` on `wip/773-allgrids` (cut from `wip/772-allgrids`). Chain `queue/done/064-night-22-october-code-allgrids-4.md`, session 773. Model spend USD 0. No warehouse data written; no request to a publisher. Written, never posted or sent.

## Read these first

- **"WHERE A BATTERY'S DAY SWINGS MOST"**, `/research/card/siting_battery_swing`, in review. It covers ERCOT's 195 storage nodes that hold at least 90 percent of the days the table holds, by their day-ahead intraday swing (746: each day's four dearest hours' mean less its four cheapest, 2025-10 to 2026-09).
  - **The range**: MOORE_FL_RN USD 34.22 per MWh, the narrowest, to PALACIOS_RN 105.86, the widest; median 49.31.
  - **PALACIOS_RN's mean is above its own 90th percentile** (10th 20.04, 90th 85.57): a few days' swing carries it, and the card says so.
  - **One chart**: the nodes counted by their swing, in steps of USD 10.
  - **The card says what the swing is not**: a battery's earnings (no losses, no cycling, no ancillary markets). No verdict.
- **Written by `site/scripts/siting-card.mjs`** (a third id) from `site/data/siting/nodes.json`; `--check` compares all three cards.
  - The days the table holds are read from the file (the most any node holds, 335 of 365), not written in.
- **The research topics**: "Power prices" now takes `node_basis_daily` (`/prices|node_basis/`, in `lib/researchrules.ts` and its mirror in test 238). Otherwise the card would fall under "Other tables", which test 238 forbids.
- **Checked**: the card's six figures read and equal (check-values, `/research` and the node list, 717 of 717; the one floor failing is `/research/card/gas_sets_price`, held, production the same). The new address has a floor of 6.

## What to review

1. After the landing, `https://erw-flame.vercel.app/research/card/siting_battery_swing` (internal view).
2. Shots: `docs/brand/review-773/` (1280, 390, the render frame).

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `node scripts/siting-card.mjs --check` | 0 | the three cards are the tab's figures |
| `tests.test_session773`, `720`, `734`, `258`, `238` | 0 | OK |
| `db_probe.py` (the build only on its 0) | 0 | |
| `npm ci`, `npm run build` (lock `s773`, beat) | 0 | |
| check-values, `CHECK_VALUES_PAGES=/research,/cost-of-power?view=allgrids&rows=nodes` | 1 | 717 of 717; the held floor of `gas_sets_price` only |

## The landing

Sessions 766 to 777 landed in one push at 21:13 UTC: see `SESSION_777_REPORT.md`, "The landing".

## Decisions made without you

1. **Storage nodes holding 90 percent of the table's days**, the tab's own rule for a twelve-month figure.
2. **A count by step of USD 10** rather than 195 bars, so the chart reads at 390.
3. **The other two cards' files kept as they were**: the script rewrote only their time.

## For Samuel's ruling

- Nothing new.

## Files

- Changed: `site/scripts/siting-card.mjs`, `site/lib/researchrules.ts`, `tests/test_session238.py`, `site/scripts/check-values.mjs` and `check-values-floor.json` (one address).
- New: `site/data/findings/siting_battery_swing.json`, `site/public/findings/siting_battery_swing.csv`, `tests/test_session773.py`, `docs/brand/review-773/`, this report.
