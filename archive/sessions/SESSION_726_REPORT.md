# Session 726 report: the utility's path, fixed

22 October 2026, from 15:16 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-726` on `wip/726-allgrids` (cut from `wip/725-allgrids`). Chain `queue/done/062-day-23-october-code-allgrids-2.md`, session 726. Model spend USD 0. No warehouse data written; no request to a publisher.

## Read these first

- **The Utility column names each figure's kind**, from EIA-861's service type:
  - delivery only (the wires) or energy only (a retailer's energy), beside the revenue per MWh; a bundled figure (energy and wires together) has no word.
  - PJM's row now reads "11.34 delivery only", and N.Y.C. "128.79 delivery only".
  - When the table is sorted by the utility, the sort's line says the column mixes three kinds and how to read them. The column's tip says so too.
- **The A and B panel subtracts only like from like**: each side's utility figure names its kind. Where the two kinds differ, "B less A" reads "not alike", with both kinds in its tip.
- **No figure changed.** One difference key is no longer drawn: the utility line of the checked address `a=ercot:HB_HUBAVG&b=nyiso:N.Y.C.`, an energy-only retailer against a wires utility. check-values reads 2,677 of 2,677, one fewer than 724's 2,678; the existing tab shows 0 differences from production.
- **Left for your ruling** (725): which utility a row names where the state's largest seller is an energy-only retailer.

## What to review

1. After the landing, `https://erw-flame.vercel.app/cost-of-power?view=allgrids&mw=1000&sort=utility&dir=asc&grid=pjm,caiso` (internal view): PJM's "11.34 delivery only" against CAISO's bundled figures. Read the sort's line.
2. `https://erw-flame.vercel.app/cost-of-power?view=allgrids&mw=1000&sort=utility&a=ercot%3ALZ_HOUSTON&b=pjm%3Agrid`: the panel's utility line, "not alike"; hover it.
3. Shots: `docs/brand/review-726/` (after); 725's are the before.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `tests.test_session726` | 0 | 2 OK (PJM and N.Y.C. delivery, SP15 bundled; the page's words) |
| `db_probe.py` | 0 | |
| `npm ci`, `npm run build` (lock `s726`, beat) | 0 | |
| check-values, `CHECK_VALUES_PAGES=/cost-of-power` | 0 | 2,677 of 2,677 |
| `check-existing-tab.mjs`, production against the build | 0 | every figure the same |

## The landing

Sessions 722 to 726 land together after 16:15 UTC (below, once done).

## Decisions made without you

1. **Kind words in ink, small, beside the figure**, not in grey (the owner's rule of 14 October), and no word for bundled, the usual case.
2. **"Not alike" rather than a difference** where the kinds differ: a delivery revenue less a bundled price is not a figure a reader can use.

## For Samuel's ruling

- Nothing new (725's item stands).

## Files

- Changed: `site/lib/siting.ts` (`SERVICE_WORDS`, `utilityKind`, `UTILITY_KINDS_LINE`, the column's tip), `site/app/cost-of-power/AllGridsView.tsx` (the two utility cells, the panel, the sort's line), `docs/methods/siting.md` (decision 20), `docs/reviews/siting-utility-path.md` (after).
- New: `tests/test_session726.py`, `docs/brand/review-726/`, this report.
