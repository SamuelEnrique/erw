# Session 10218 report (chain 710, part D, the old laptop): the prices pages and the price heatmap audited

- The audit: `docs/reviews/prices-model-audit-2026-11-26.md`, its evidence in `docs/reviews/prices-model-audit-2026-11-26/`. Platform tool 8 (the Grid map's price colors, `/grid/prices-map`) and `/prices`, `/prices/<hub>`, `/prices/compare`.
- The arithmetic is right: the comparison's file 662 of 666 to the cent from the price tables (4: one CAISO carbon day not on this machine); the drawn compare page 450 of 456 (the same carbon); `/prices` and four hub pages 32 of 32 at a fixed render time; the map's file 145 of 152 to the cent from the page's hourly files (the 7 explained).
- Findings: 3 Medium (1 load zones said not compared, 2 the comparison lacks real-time hours the site holds, 3 the average is a flat load's, unsaid), 3 Low (4 held grid words on `/prices`, 5 the map legend gives no date, 6 a hub page's day-ahead window).
- Branches: words `wip/audit-prices-1`, `-3`, `-4`, `-5`, `-6`, merged as `wip/audit-prices-words` (no conflict); figure `wip/audit-prices-2` (not for landing). Each words branch's page drawn with the site's own code and read again: pass.
- Nothing written to any table; no model called; no request to any service; no default changed.

## Decisions made without you

- `/prices` was drawn on this machine's tables at 18:00 UTC on 12 November with `latest_prices` made from them, since the live page cannot be read here; each held grid was given one stand-in row (value 0) to see how the page draws it. No held grid's price was read from any table.
- For the comparison's restatement, the one local day of real time this machine's tables lack (15 October, CAISO's and ERCOT's hubs) was taken from the page's own hourly files, only inside October and only for hubs the file says held every hour; the run without it is kept too.
- The lead of `/prices/compare` names the grids shown from the file ("three grids, CAISO, ERCOT and SPP") rather than a fixed count.
- `site/scripts/test-compare-read.mjs` fails 12 of 73 on main (stale since sessions 7050 and 7052); left as it is, only the two checks finding 1 makes true were changed.

## For Samuel's ruling

- Finding 2: rebuild the comparison now (default: left as it is until the data machine's next run). It moves SPP North's October real time from "not held" to 34.35 and SPP South's to 25.30, ZP26's October real time 45.35 to 44.88, SPP North's twelve months 31.66 to 31.77.
- Finding 3: a load-weighted average beside the simple one (default: left as it is). +4.0 to +7.1 percent on the twelve months to October 2026.

## Needs the key

- Nothing.

## Problems

- One empty inline Python command (`python.exe -c ""`) was run by mistake inside a drawing command, against this chain's rule of no inline code. It did nothing; nothing else of the kind was run.
