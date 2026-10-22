# Session 711 report: a node's panel

22 October 2026, from 09:45 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-711` on `wip/711-allgrids` (cut from `wip/710-allgrids`). Chain `queue/done/050-night-23-october-code-allgrids.md`, session 711. Model spend USD 0. No warehouse data written; no request to a publisher.

## Read these first

- **A node's name opens its panel** (the address's `node`, drawn by the server above the list).
- **What the panel shows**:
  - the node's daily day-ahead basis to HB_HUBAVG over October 2025 to September 2026: the 10th, 50th and 90th percentile of its days, with the days held (new in `nodes.json`, written by `siting_page.py` from `node_basis_daily`);
  - each month's mean basis in the shared inline chart.
  - For 7RNCHSLR_ALL (solar): -1.51, 1.28 and 6.36 USD per MWh over 334 days.
- **Three items are "not held", each with why on hover**:
  - **Four-peak exposure**: as every node, the charge on the hub's hours, drawn above the list. Its own price in the four intervals of summer 2025 is not held: `node_basis_daily` begins 1 October 2025, and it holds days, not intervals.
  - **The nearest planned generation by county**: no table of the warehouse places an ERCOT settlement point in a county.
  - **The county's transmission projects**: `texas_transmission_matrix` holds each wires utility's transmission cost of service and four-peak charge, not projects by county, and it is internal. The prompt's premise does not hold for that table.
- **Keys**: `allgrids|nodepct|<node>|10`, `50` and `90`. check-values reads `/cost-of-power?view=allgrids&rows=nodes&node=ercot%3A7RNCHSLR_ALL`.

## What to review

1. After the landing, open `https://erw-flame.vercel.app/cost-of-power?view=allgrids&rows=nodes` (internal view).
2. Click "7RNCHSLR_ALL" in the list. The panel opens above the list: the three percentiles, the chart and the three items. Hover each "not held". "Close" closes it.
3. Screenshots: `docs/brand/review-711/` (712's build).

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `tests.test_session711` (two nodes' percentiles recomputed from the table here; the panel's keys) and 700, 701 | 0 | OK, 1 skip |
| built and checked on 712's branch | 0 | see 712's report |

## The landing

Landed with sessions 706 to 712 in one push, merged at 11:24 UTC (`8a54e3b4`); Vercel rate-limited the deploy ("retry in 24 hours"), so production serves it later: `SESSION_712_REPORT.md`, "The landing".

## Decisions made without you

1. **The basis spread is three percentiles of days, and twelve monthly means** (the shared chart). The node file holds no hourly basis, and 873 nodes' days would be about 2 MB.
2. **The panel is drawn by the server from the address**, so each of its figures carries a key and the panel can be sent.

## For Samuel's ruling

- ERCOT's resource registration (a resource's county and TSP) would fill the panel's place, and the transmission projects by county would need a table of their own (the PUCT's CCN filings, say). Both are in the gaps file.

## Files

- Changed: `site/lib/siting.ts` (`pct`, `allgrids|nodepct`), `site/app/cost-of-power/AllGridsView.tsx` (`NodePanel`), `site/app/cost-of-power/AllGridsNodes.tsx` (a node opens its panel), `site/scripts/check-values.mjs`, `warehouse/derived/siting_page.py`, `site/data/siting/nodes.json`.
- New: `tests/test_session711.py`, this report.
