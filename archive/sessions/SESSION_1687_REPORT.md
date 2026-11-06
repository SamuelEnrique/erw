# Session 1687 report: AccessLint on 47 more pages, and what its scrolling findings are

Energy Research Warehouse (ERW), session 1687, chain 189, samueloldlaptop, 6 November 2026, 16:40 to 16:50 UTC. Model: Claude Opus 5.5 (the file names Fable 5.1). Model spend USD 0. No warehouse data written; nothing sent or posted. A build of main (`3bf70c884`) in a clean worktree (`npm ci`, `site/.env.local` copied in, under `scripts/buildlock.py`), in the internal view.

## What it did

- **The pages**: 47 of the 78 paths in the route check's list that no session had read. They cover the hub price pages, `/data/standard`, the old explorer address, an analysis card and week, `/subscribe`, `/ask/ercot`, `/map/v2`, `/network/v3`, the seven grid pages and CAISO's alerts, six event pages, `/storage/buildout` and `/storage/owners`, `/severance` and its lease page, the v2 pages, the battery customer and the two games, the tour, `/learn/bill`, the five problems, the battery's awards page, `/mix/clean`, `/mix/stress`, and three methods pages. Those not read are 24 methods pages and the rest of the event pages, which share the layouts read.
- **One real fault**: `/learn/bill`, `adaptable/td-has-header` (serious). The bill table's group rows and its lines are all `<td>`, so a screen reader reads each amount with no name. Fixed by session 1688.
- **The scrolling-region findings are AccessLint's timing, not faults.** Six pages had them:
  - the event pages, one shared section;
  - `/storage/buildout`, inside a fold;
  - `/mix/stress`, two;
  - a methods page's four Markdown tables.

  This session opened three of those pages and read them 7 seconds after load. Every scrolling box was then a named region a keyboard can reach: `/mix/stress`'s two ("Evening ramp and lowest net load", "Dark, calm stretches"), the event page's ("What the estimates say"), and the methods page's four tables ("Table, 1 of 4" and on). `site/components/ScrollRegions.tsx` (sessions 412 and 583) marks them about 150 ms after load, and AccessLint reads before that. So these need no fix, and the next file says how to tell the two apart.
- The browser and the server were stopped.

## Decisions made without you

- No fix for the scrolling-region findings: the run-time marking covers them in any browser that runs scripts.

## For Samuel's ruling

- None.
