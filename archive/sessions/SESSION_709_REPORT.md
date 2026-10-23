# Session 709 report: the ERCOT node set

22 October 2026, from 09:40 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-709` on `wip/709-allgrids` (cut from `wip/708-allgrids`). Chain `queue/done/050-night-23-october-code-allgrids.md`, session 709. Model spend USD 0. No warehouse data written; no request to a publisher.

## Read these first

- **"ERCOT nodes (873)" is now a virtual list** (`site/app/cost-of-power/AllGridsNodes.tsx`): the browser holds the rows in view and a dozen around them. The server draws the first 40 rows of the sort, each figure with its key.
- **Each row has only what differs from node to node**:
  - the node and its class;
  - its energy (HB_HUBAVG's figure under the profile plus its basis);
  - its basis to HB_HUBAVG;
  - its all-in figure;
  - its days held of the window.
- **No figure is drawn twice.** Everything every node shares is drawn once, above the list:
  - the four-peak charge, which a node pays on its hub's hours;
  - no capacity market;
  - ERCOT's time to connect, headroom and carbon;
  - what the node tables do not hold (a node's zone, settlement hub and TSP).
- **Sort by any column**: click a heading to sort by it, click again to reverse. A node with no figure goes last. The sort is said above the list and kept in the address (`nsort`, `ndir`).
- **The set adds no read**: every row comes from the site's own files (`nodeTable` in `lib/siting.ts`).
- **A type error was found by 712's build and mended on this branch**: the hub table's caption still tested for nodes inside the branch that draws hubs only.

## What to review

1. After the landing, open `https://erw-flame.vercel.app/cost-of-power?view=allgrids&rows=nodes` (internal view).
2. Read the two lines above the list (the shared figures, drawn once).
3. Click "Energy": the list sorts largest first and the address gains `nsort=energy&ndir=desc`. Click it again for smallest first.
4. Scroll the list: rows appear as they come into view.
5. Screenshots: `docs/brand/review-709/` (before is 705's build, after is 712's).

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `tests.test_session709` (873 rows; each figure the hub table's arithmetic; the sort, no figure last; virtual; shared once) and 700 | 0 | OK, 1 skip |
| built and checked on 712's branch (the node addresses, and one sorted by energy) | 0 | see 712's report |

## The landing

Landed with sessions 706 to 712 in one push, merged at 11:24 UTC (`8a54e3b4`); Vercel rate-limited the deploy at first and served it at 11:54 UTC; snapshots 0 differences: `SESSION_712_REPORT.md`, "The landing".

## Decisions made without you

1. **The node rows drop the columns that are the same at every node** and draw them once. The four-peak charge is one of them, because a node is charged on its hub's hours.
2. **A virtual list of plain rows**, not a table, so the browser holds a few dozen. The headings are buttons with `aria-sort`; 714 checks keyboard reach.

## For Samuel's ruling

- ERCOT's settlement point mapping (zone and hub) and its resource registration (TSP, county) would fill the node's zone, hub, utility and place. They are in the gaps file.

## Files

- Changed: `site/lib/siting.ts` (`nodeTable`, `sortNodes`, `NODE_SORTS`), `site/app/cost-of-power/AllGridsView.tsx` (`NodeShared`; the hub table only for hubs).
- New: `site/app/cost-of-power/AllGridsNodes.tsx`, `tests/test_session709.py`, this report.
