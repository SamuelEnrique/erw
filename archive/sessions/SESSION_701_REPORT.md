# Session 701 report: the energy column of the All grids tab

22 October 2026, from 09:00 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-701` on `wip/701-allgrids`, cut from `wip/700-allgrids` because session 700 had not yet landed. Chain `queue/done/050-night-23-october-code-allgrids.md`, session 701. Model spend USD 0. No warehouse data written; no request to a publisher.

## Read these first

- **Every priced row now shows its day-ahead price over the last twelve whole months, for a flat load, with real time beside it where held.** The figures come from the page's own hourly files, through the same functions "Your load" uses.
  - `lib/datacenter.ts`'s `monthsRuled`, `lastTwelve`, `span` and `years` are handed to `lib/siting.ts` (`flatTwelve`), so there is one arithmetic for both views.
  - Each grid's main region bought day-ahead equals "Your load"'s own figure to the last digit: ERCOT LZ_NORTH 35.33, CAISO SP15 28.94, NYISO N.Y.C. 73.10, ISO-NE Internal Hub 74.19, SPP North 33.51. `tests/test_session701.py` holds this through `scripts/datacenter-ways.mjs`.
- **ERCOT nodes: HB_HUBAVG's twelve-month day-ahead price plus the node's mean daily day-ahead basis** over the same months (`node_basis_daily`), weighted by days held.
  - A node is drawn only with at least 90 percent of the window's days (the node basis method's own `NEAR`). That is 772 of 873; each of the other 101 says how many days it holds.
  - Real time is not held at the nodes for twelve months (23 days), and the tip says so.
- **The tip of each figure** gives the market, the window, the hours held, the last whole month and the last whole calendar year. Hover a figure (or focus it with the keyboard) to see its twelve months as the shared inline chart (`components/InlineSpark`).
- **Rows with no figure say why in ink, with the reason on hover**:
  - MISO: "paused";
  - PJM: "license needed";
  - ISO-NE's 8 zones: "not held" (twelve whole months in a row are not held for them);
  - ERCOT's four smaller load zones: no real-time figure, because their real-time months are not twelve in a row.
- **Keys**: `allgrids|energy|<row>|da`, `allgrids|energy|<row>|rt`, recomputed by `check-values.mjs` with the same functions (`site/scripts/siting-files.mjs`, `dc()`).

## What to review

1. Open `https://erw-flame.vercel.app/internal/open`, then `https://erw-flame.vercel.app/cost-of-power?view=allgrids` once landed.
2. The Energy column: e.g. "ERCOT HB_HUBAVG (hub)" reads 34.30, with "rt 32.20" beside it. Hover 34.30: the tip names October 2025 to September 2026, and the twelve months are drawn under it.
3. Open "Your load" for ERCOT LZ_NORTH, buying day-ahead (`/cost-of-power?grid=ercot&region=LZ_NORTH&buy=da`): the headline's USD per MWh is 35.33, the same as the All grids row "ERCOT LZ_NORTH".
4. Click "ERCOT nodes (873)" and hover any figure: the hub, the basis and the days held.
5. Screenshots: `docs/brand/review-701/` (before is session 700's build, after is this one, at 1280 and 390).

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `tests.test_session701`, `tests.test_session700` | 0 | 16 tests OK, 1 skip (the node table is not in a worktree; 700's run holds it) |
| `db_probe.py` | 0 | 0.71 s |
| `npm run build` (lock `s701`, beat) | 0 | no statement timeout |
| `check-values.mjs`, `CHECK_VALUES_PAGES=/cost-of-power?view=allgrids` | 0 | 830 of 830 |
| `check-existing-tab.mjs` production against the build | 0 | 588 keys on four addresses, 0 differences |

## The landing

With the sessions after it, in one push.

## Decisions made without you

1. **`lib/siting.ts` takes `lib/datacenter.ts`'s functions as an argument** rather than importing them. The pure files of `lib/` import nothing, so Node can run them as they are; this keeps that rule and the one arithmetic.
2. **The node rule of 90 percent of days** follows `node_basis.py`'s `NEAR`. The window is the hub's twelve whole months.
3. **The prices of ISO-NE and NYISO are drawn here as "Your load" draws them** (its files hold them, and it shows them today), so that the two views agree. See the ruling below.

## For Samuel's ruling

- `site/data/license_status.json` holds ISO-NE, MISO and NYISO prices as "license needed" from 20 October 2026. "Your load" still draws NYISO's and ISO-NE's prices from its own files (production today: N.Y.C. USD 68.49 real time), because its figures are not keyed by table. All grids follows it so the two views agree. If they should be held, both views should change together.

## Files

- Changed: `site/lib/siting.ts` (`flatTwelve`, `twelveOf`, `nodeEnergy`, `energyCell`, the energy keys), `site/lib/sitingdata.ts` (`SITING_DC`, the year files), `site/app/cost-of-power/AllGridsView.tsx` (the energy cell, its tip and sparkline), `site/scripts/siting-files.mjs` (`dc()`, `energy`), `site/scripts/check-values.mjs`.
- New: `tests/test_session701.py`, `docs/brand/review-701/`, this report.
