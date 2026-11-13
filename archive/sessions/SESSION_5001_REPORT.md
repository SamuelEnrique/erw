# Session 5001 report: the battery tool, read and its done line

Energy Research Warehouse (ERW). Chain 233, portable laptop window P1, 13 November 2026, about 09:55 to 10:05 UTC. Opus 5.5. Model spend USD 0.

## What was done

- The battery page's decisions block: `BATTERY_DECISIONS` (17 lines) in `site/lib/decisions.ts`, drawn by the shared `DecisionsBlock` with a new `open` option (the other two pages unchanged, closed). The note's section 12 is the same list word for word; the sign-off names it. `6c44c559`.
- The note's stale figures marked: 4.1, 4.3, 11.1 now carry the default since session 208 (USD 2,261,119, 2.63 times) beside the record of sessions 67 to 207. CAISO's start (3.2 and the derivation's docstring) is 1 August 2023 since session 273.
- Faults file: `docs/reviews/battery-faults-2026-11-13.md`, 6 rows: 3 fixed, 2 ruling, 1 not a fault.
- Built `wip/5000-battery` locally under the build lock (the first try failed: Turbopack does not follow a junction to the main checkout's `node_modules`; a copy was used). Build exit 0.
- Read at 1280 and 390, internal view: no sideways scroll, no console error, no broken text; the headline equals the replication.
- The same build read the other four tools (for their sessions): `/research` is 563 px wide at 390; the Grid page's decisions block holds no `data-decision` line; `/ask` and `/network` resolve into `/grid` already.
- Tests: 49 files that touch the battery page, its note, the decisions or the derivation: 669 passed, 32 skipped (exit 0).

## Decisions made without you

- The battery's decisions block is drawn open (a `details` with `open`), not as a fold, because of "nothing collapsed".
- The old 60 percent figures in the note stay as the record, with the current default beside each, as the note's own third paragraph already intends.
- The derivation's docstring date corrected (words only, no data written).

## For Samuel's ruling

- Row 4: the settings column's "Financing" fold starts closed while the text sends the reader to it. Default: leave closed.
- Row 5: the monthly node-spread fold under the income table. Default: leave it.
- The battery note is ready for your signature (`docs/methods/battery_earns_algorithm.md`, "Sign-off").
