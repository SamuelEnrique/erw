# Session 10225 report: the events pages audited as a hostile expert would (chain 710, part D)

26 November 2026, the old laptop, worktree `erw-c710-b`. The audit: `docs/reviews/events-model-audit-2026-11-26.md`, its evidence in `docs/reviews/events-model-audit-2026-11-26/`.

## What was done

- Three views taken whole: Winter Storm Uri (the index's first card), CAISO's August 2020 heat wave, Winter Storm Elliott, and the index's three cards.
- Every figure they draw restated independently (numpy least squares and an own HC1 for the event study): 743 of 743 agree with the site's own code drawing the pages (Uri 246, CAISO 2020 213, Elliott 275, index 9). The arithmetic is right.
- Rules changed one at a time: where the weather terms are fitted, the weather's range, the window's edges, net demand on the outage days, the hydro gap, the price at the ceiling, Uri's calendar baseline.
- Nine findings: five words branches (1, 3, 5, 7, 8) and a merged `wip/audit-events-words`; four figure branches (2, 4, 6, 9), test only.
- Each words branch drawn to HTML with the site's own components and its words read again: pass; every figure file identical to main's.

## Decisions made without you

- The default event: the index has no address input, so its first card (Uri) was taken; CAISO 2020 and Elliott as the two others (load shed, many grids). COVID-19 not taken (window F's phone fix).
- "Out of bounds: the paper's": the region section's net imports, its pairs-against-imports hover and the pair table were not restated or touched.
- Each words branch rewrites the events pin (`site/scripts/pins/events-pages-8410.json`), since the pin holds the pages outside the region section byte for byte; the merged words branch rewrites it once.
- Data tests read the replication's public rows (`replication/events/window_rows.csv`, the same build as the warehouse's table) and the committed region files, so they run in any checkout.

## For Samuel's ruling (default for each: left as it is)

- Finding 2: print the weather share only where the event's weather lies inside the baseline's, or fit the weather on the baseline days alone: Uri 80.56 percent to none, CAISO 2020 70.47 to 63.86, PJM (Elliott) 65.33 to none.
- Finding 4: add California's net demand to CAISO 2020's page: five figures; by it 14 August (an outage day) is the highest of 14 to 19 August.
- Finding 6: approve the held hydro-gap rule for `event_window_daily`: CAISO 2020's 14 days of carbon intensity go (the page's 305.93 kg/MWh and its chart).
- Finding 9: Uri on the weekday baseline: the largest shortfall -186,530.50 MWh becomes -37,630.50.

## Needs the key

- Nothing: no live service, no model, spend USD 0.

## Problems

- One inline command slipped: an empty `python -I -c ""` appended to a listing command early in the session (it did nothing). A rule broken; no other inline code, no heredoc.
