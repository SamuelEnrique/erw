# Session 734 report: a second research card

22 October 2026, from 15:35 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-734` on `wip/734-allgrids` (cut from `wip/733-allgrids`). Chain `queue/done/062-day-23-october-code-allgrids-2.md`, session 734. Model spend USD 0. No warehouse data written; no request to a publisher. Written, never posted or sent.

## Read these first

- **"WHAT STEPPING OFF SAVES"**, `/research/card/siting_flexible`, in review: a 1 GW flexible compute load at ERCOT's 14 hubs and load zones, off at the four summer peaks and at or above USD 1,000 per MWh, against a flat load at the same row.
  - **Saved all-in**: USD 8.60 per MWh at LZ_SOUTH (the least) to 10.78 at LZ_CPS (the most).
  - **Hours given up**: 5 (LZ_SOUTH) to 15 (LZ_CPS) of the twelve whole months.
  - **At HB_HUBAVG**: USD 32.25 flexible against 42.13 flat.
  - **Most of each saving is the four-peak charge** (USD 7.83 at every ERCOT row), which a load off at the peaks does not pay; the rest is the dearest hours' energy. The why line says so, and test 734 holds it.
- **The same rules as 720's card**: written by `site/scripts/siting-card.mjs` from the tab's own functions (the script now writes both cards; `--check` compares both); one chart (flat and flexible all-in, paired bars) with its source line; three callouts; no verdict; `engine` named, so test 258 skips it.
- **The first card is unchanged**: the script rewrote only its time, and that rewrite was put back.

## What to review

1. After the landing, `https://erw-flame.vercel.app/research/card/siting_flexible` (internal view): the chart, the three callouts, the why line. Click "Table" for the rows.
2. `?render=1` for the 1080 by 1350 frame.
3. Shots: `docs/brand/review-734/` (the card at 1280 and 390, the render frame).

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `node scripts/siting-card.mjs --check` | 0 | both cards are the tab's figures |
| `tests.test_session734`, `720`, `258`, `238` | 0 | OK |
| `npm ci`, `npm run build` (lock `s734`, beat) | 0 | |
| check-values, `CHECK_VALUES_PAGES=/research/card/siting,/cost-of-power?view=allgrids&profile=flexible` | 0 | 537 of 537; the card's six figures read and equal; floor 6 added |

## The landing

With the next landing (735 onward).

## Decisions made without you

1. **ERCOT's rows only**: the four-peak charge, the larger part of what stepping off saves, is held for ERCOT alone.
2. **One script for both cards**, so a change to the tab's functions shows in both `--check`s at once.

## For Samuel's ruling

- Nothing new. A brand note: at 1280 two of the chart's labels touch (LZ_HOUSTON and HB_HOUSTON), as on 720's card. The chart is the shared component's, not this chain's.

## Files

- Changed: `site/scripts/siting-card.mjs`, `site/scripts/check-values.mjs` and `check-values-floor.json` (one address).
- New: `site/data/findings/siting_flexible.json`, `site/public/findings/siting_flexible.csv`, `tests/test_session734.py`, `docs/brand/review-734/`, this report.
