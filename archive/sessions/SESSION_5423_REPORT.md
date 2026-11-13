# Session 5423 report: chain 261, step 7, the five's accessibility read; Grid row 5 fixed (the read script's race)

Energy Research Warehouse (ERW). Chain 261, portable laptop window P1, 13 November 2026, about 21:11 to 21:16 UTC. Opus 5.5. Model spend USD 0. Branch `wip/5072-read` (the fix made on `wip/5072-fixes3` and moved onto it).

- **The tool:** `site/scripts/a11y-axe.mjs`, the site's own axe-core read of pages in the internal view (session 3778: AccessLint's live audit cannot carry the internal cookie, as `docs/tooling.md` says of pages in review), WCAG 2.0 to 2.2, A and AA; on production; 0.8 GB free (single-browser reads have run all evening at that).
- **1280:** the battery, the generator, the datacenter page, Research and the Grid: 0 rules broken on each.
- **390:** the same five and two variants (MISO's grid, CAISO's 8-hour day-ahead battery): 0 on each but `/grid` and MISO's view, `scrollable-region-focusable` (serious, 2 elements), the monthly mix table's scrolling box.
- **Not the page's (Grid row 5):** the box carries `tabindex="0"`, `role="region"` and its name four seconds after the load, and axe run after a 4-second wait finds nothing. The script ran axe straight after the load, before `components/ScrollRegions.tsx` (150 ms after it mounts) had marked it. **Fixed in the script:** it waits after each load (`A11Y_WAIT_MS`, default 2000); run again, 0 rules broken on `/grid`, MISO's view and `/cost-of-power` at 390. The detail mode's one failure (a null `document.body` straight after the load) is the same race.
- **Tests:** `tests/test_session5423.py` (new, 3 tests): OK. No other test reads the script.

## Decisions made without you

- The default wait, 2 seconds: a little over ten times the marking's delay, and short enough for a list of pages.

## For Samuel's ruling

- Nothing new: no finding on words or structure.
