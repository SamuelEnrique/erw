# Chain 087 on the personal laptop (23 October 2026, 20:05 to about 21:05 UTC): the note for Samuel

Energy Research Warehouse (ERW), session 2305, written on portable-laptop on 23 October 2026. Chain 087 (`queue/done/087-day-23-october-portable-map-tracker.md`, sessions 2300 to 2305) was written first by session 2300 on your instruction of about 20:05 UTC, committed alone, pushed to main and taken by name, then run unattended with a commit and a push after every step, beside two other Claude Code sessions on this machine (chain 086, sessions 2200 to 2205, the explorers; chain 088, sessions 2400 to 2405, the policy monitor and the games). Model Fable 5.1. Model spend USD 0. No warehouse data written; no request but GitHub, the ERW's own database (one read of the live set, and the probes) and nothing else; the site is in review and nothing of this chain is on production.

## First: what to know

1. **Everything asked for is coded, tested on fixtures and pushed, on one stack of branches; nothing is built or landed.** `wip/2305-map-tracker` carries sessions 2300 to 2305 (`wip/2300-map-tracker` to `wip/2304-map-tracker` under it, each pushed). The chain's rule allowed a build only on a database probe under 3 seconds with the build lock free: the probe passed four times in fourteen (2.58 to 2.62 s against 3.25 to 8.38 s), and each time it passed the lock was held by chain 088's session 2403 (from 20:43 UTC to past 21:00) or chain 086's 2203. One build was started at 20:44 and stopped by hand a minute later when the lock was found taken, before anything ran. Free memory ran 0.8 to 4.0 GB. So: no screenshots, no 390 px measure, no link check, no AccessLint (not installed on this machine), no gate. The exact commands are under "To finish".
2. **The project map's figures say where they come from** (session 2300). Every figure the page sums in the browser from its own copy of the tables carries `data-source` (tables, vintage, rule) and stands beside a hover tip with the same words; the Queues tab's charts are framed with their table and the ISO's queue table; the Resources tab's seven counts too. 37 tests on the file and a fixture, no browser.
3. **A hover on every mark and chart** (session 2301): the map's marks show the brand's card with the figure in mono and the source line, a state's hover counts the rows chosen; the tracker's two bars have a focusable card per figure and a table under them; the grids chart's groups, the power side's MW and ERCOT's large-load chart (moved to the shared chart, which has a hover and a table) the same.
4. **Bullock Gas and Liberty Thermal Energy Center will be on the tracker's power side** (session 2302): the read layer matches the pattern against the operator too; the live set holds both rows (vintage 2026-10-19); the page says "named a data center by its operator's name" and that the derived table follows at the data machine's next run. 16 fixture tests, and the two Python tests of the pattern pass. No warehouse write; the derived table's one-field change stays the desktop's.
5. **390 px, accessibility, links and the brand, from the code** (sessions 2303 and 2304): two heading levels fixed, one bare link's words, labels in sentence case, no 11 px text, grey field edges, square swatches, the facilities table's header rule. The browser measures wait for the build.
6. **The method notes are updated** (session 2305): `energy_projects.md` (the figures from the page's copy and their sources; the hover) and `datacenter_facilities.md` (the operator-name match; the hover and sources). `check-methods.mjs`: 553 of 553 figures named, 57 pages.
7. **No next file was written.** What waits is one build and one gate of the stack, which need the machine's conditions (a free lock, a probe under 3 s, 2 GB free), not work, and a file in `queue/next/` for this machine is taken the moment the queue step runs (chain 084's finding), which would have started the same wait again beside the two chains that hold the lock. The commands are below; one command queues them when you want.

## What each session did

| Session | Branch | What it did |
|---|---|---|
| 2300 | `wip/2300-map-tracker` (from main at `e1eaadf5`) | the chain file; the map's figures keyed with their source tips; `test-map-sources.mjs`; `check-map.mjs` extended |
| 2301 | `wip/2301-map-tracker` (stacked) | the hover on every mark and chart, both pages; `check-datacenters.mjs` extended |
| 2302 | `wip/2302-map-tracker` (stacked) | the operator-name match in the read layer; `test-queue-sites.mjs`; `check-values.mjs`'s `dcq|` keys over the same fields |
| 2303 | `wip/2303-map-tracker` (stacked) | the code scan's three fixes; the browser checks left for a build |
| 2304 | `wip/2304-map-tracker` (stacked) | the brand pass from the code; the build started and stopped (the lock) |
| 2305 | `wip/2305-map-tracker` (stacked); main (documents) | the two method notes; this note; the queue step |

Reports: `archive/sessions/SESSION_2300_REPORT.md` to `SESSION_2305_REPORT.md`.

## Decisions made without you

- 2300: browser-computed figures carry `data-source` and a tip, not a check key (a key would be compared with a live table the page's copy lags by design); the Resources tab's counts, outside the chain's files, got the attribute and a title and nothing else; a `node_modules` junction in each worktree for the tests and the lint.
- 2301: the map's marks are on a canvas and not focusable, so the keyboard's path is the totals, the table and the card; the shared chart's hover is taken as the brand's and not restyled; the large-load chart moved from the plain line chart to the shared chart.
- 2302: the operator is the third field read, after the name and the fuel field; the pattern's words unchanged; the match kept in the row's `extra`; `check-values.mjs` changed in its `dcq|` branch alone.
- 2303: the heading fixes change the level and not the face; AccessLint not installed (a pull, and your choice of tooling here).
- 2304: the facilities table's header took the brand's ink rule where the shared table has a cardinal band; a label's weight is 500; the stopped build (its wait would have ended in an unlocked build).
- 2305: no build after a nine-minute wait on the lock (held since 20:43) with the probe over 5 s; no next file (above); this note is named for the chain (`_map`), because chain 086.s note of the same day took the plain name minutes earlier and the first save of this one overwrote it in the working tree before it was put back from main. The queue step took `queue/next/087-day-24-october-portable-explorers-gate.md`, chain 086.s own gate file for its branches, which your instruction for this chain forbids touching: the file was put back in `queue/next/` for the worker or chain 088.s queue step, and this chain says CHAIN DONE without running it.

## For Samuel's ruling

- The shared table's header band (`ToolTable`: cardinal with white text) against `docs/brand.md` section 5, and the shared section title in cardinal (`ToolSection`) against section 1: both move every page if changed (session 2304).
- Item 7 of `docs/reviews/deals-rulings-2026-10-23.md` still blocks every landing's `check-values` on `/digest/2026-10-21` (chain 084's note); the gate below may fail on it alone, in which case it lands nothing and says so.
- AccessLint on this machine: install it (a person's step) or run the audit from the old laptop or the desktop.

## To finish (on a probe under 3 s, the build lock free and 2 GB free; from the main checkout unless said; each its own command, its exit read)

```
cd C:\Users\samen\Documents\erw
.venv\Scripts\python.exe scripts\db_probe.py
.venv\Scripts\python.exe scripts\buildlock.py acquire s2305
.venv\Scripts\python.exe scripts\duty.py beat
cd ..\erw-2305\site && npm run build                     (stopped after 30 minutes; .env.local is in place)
npx next start -p 3305                                   (in the background)
node scripts\screenshots.mjs https://erw-flame.vercel.app --only map,datacenters     (before: production; copy to docs\brand\review-2304\before\)
node scripts\screenshots.mjs http://localhost:3305 --only map,datacenters            (after; copy to docs\brand\review-2304\after\)
node scripts\check-390.mjs http://localhost:3305 ..\..\erw\runs\s2305\390.json ..\..\erw\runs\s2305\shots --pages /map,/map?tab=queues,/map?tab=resources,/datacenters,/datacenters?view=grids
node scripts\check-links.mjs http://localhost:3305
node scripts\check-map.mjs http://localhost:3305
node scripts\check-datacenters.mjs http://localhost:3305
node scripts\check-queues.mjs http://localhost:3305
(stop the server)  cd ..\..\erw && .venv\Scripts\python.exe scripts\buildlock.py release s2305
```

A finding of `check-390` or `check-links` on the two pages is fixed on `wip/2305-map-tracker` (the pages' files first, a shared component only where the finding is its own), the screenshots committed under `docs/brand/review-2304/`, and the figures of `check-values-floor.json` for `/map`, `/map?tab=queues`, `/datacenters` and `/datacenters?view=grids` raised if the keys rose (never lowered). Then the gate:

```
.venv\Scripts\python.exe scripts\land_check.py --ref wip/2305-map-tracker --lock-as s2305 --port 3305
```

and the commands it prints: `freeze.py status`, the snapshot before, the push to `task/2305-map-tracker`, the snapshot after, `compare`, every difference listed. Once `wip/2305-map-tracker` is an ancestor of main, the six worktrees `erw-2300` to `erw-2305` and their branches are removed. AccessLint's `audit_live` on the five addresses, on a machine that has it.
