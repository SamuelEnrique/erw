# Session 8013 report (chain 505, lab-desktop, 19 November 2026, from 21:31 UTC)

Resumed chain 505 from `queue/done/550-resume-chain-505.md` (551 put back). The machine had lost power at about 20:20 UTC in the middle of part D1 (the owner's word, passed on by the other desktop window, erw-f8, which stood down).

## What a reader now sees

- **Stack i landed** (`3125fbde1`, 22:56 UTC): the project map (`/map`) has its proposed in-service dates back. The daily copy of 19 November had written none for all 3,684 positions; now 3,252 positions carry a date, as on 17 November. The Grid tool shows EIA's thirteen regions under its grid picker (`/grid?region=se` and the rest; the portable laptop's row 42). The resource map (`/resources`) carries the portable's fifth replicated layer and its fixes (row 43). Read on production at 1280 and 390 px: `/map`, `/grid?region=se` and `/resources` all open, with no sideways scroll and no console error. Snapshots `c505-deski-before2` against `c505-deski-after`: 0 differences on the 25 addresses (every page is in review), as expected.

- **Stack L landed** (`f10ebfbca`, 00:26 UTC on 20 November). Two new pages: `/industry` (energy use by industry) and `/ai-energy` (energy per AI query, as published). In the Grid tool, clicking an authority now opens "Its own facts": what it owns, what is planned, what it generates and its carbon intensity, its trading partners, its record demand and growth, and its large-load rows, with the region's sum in a fold. The map's areas can be colored by price as a reader's choice (carbon still opens): ERCOT is red at USD 54.09, SPP green at 31.93, NYISO and PJM blank with "license needed". `/demand?view=country` has a section "Forecast against actual" (for California against ERCOT: a mean miss of 4.53 against 2.40 percent of demand), with CAISO's and ERCOT's own wind and solar forecasts. From the old laptop: the findings audit on `/internal/findings` (row 54) and five new tour stops (row 55). Snapshots `c505-deskL-before` against `c505-deskL-after`: 0 differences. Every page named here was read on production at 1280 and 390 px, with no sideways scroll and no console error.

- **Stack M landed** (`601ff994f`, 01:43 UTC): the old laptop's four problem sets on the whole country. Snapshots: 0 differences. Data request 561's dated edition was built but not committed, because it fails tests 293 and 7534 (see the request's row).
- Requests 559 (migration 039 applied) and 560 (answered from the table) are done.

## Commits

- `339cafcd6` queue move; `551` resume file put back.
- `b0aea73c3`, `be245c0a1` (main): progress lines; data requests 554 to 556 and 30 marked done.
- `wip/c505-desk-i` `af961cead`: stack i (fix-map, stack h, the portable's rows 42 and 43).
- `wip/c505-req` `b5c51c184`: data requests 554 to 556 (`layer_notes_added.json`); `338d00522`: data request 30 (the archive keys revisions by vintage).
- `wip/c505-panel`: part C's panel (`/grid/authority/<code>`, `AuthorityFacts.tsx`), part D2 (`forecast/renewables.json`), part D3 ("Forecast against actual" on `/demand?view=country`), with tests and method notes.

## Each row's new state

- The power loss left `.git/refs/remotes/origin/wip/c505-industry` filled with zero bytes, and `git pull` failed ("bad object"). The file was copied to `runs/badref/` and removed; `git fetch` wrote it again. D1's tables were whole (archived at 20:12 UTC, manifest on main; the CSVs end on whole rows).
- `task/c505-fix-map` had failed on GitHub at 20:09 UTC: it no longer merged with main (`docs/state/page_files_regions.md`, two dated lines added on each side). Both kept in stack i.
- Portable row 42 (`cd7a504d4`) and row 43 (`1e3757f7b`) in stack i. Row 43's earlier failure (two tests on markup in `view.tsx`) is gone at that head. One conflict in `tests/test_session8603.py`: the desk's both-rules side kept, as stack f did.
- Old laptop row 33 (`wip/7535-play-battery`, 16 November) has an empty State cell, not "requested"; not landed.
- Data request 30: the archive keyed every series table by `(entity, variable, ts_utc)`, so a table whose header says `Revisions: kept, one row per vintage` came back from `restore.py` with one vintage a key. Before and after, from the local archive: `ferc714_planning_area_forecasts` 11,934 to 67,215 rows, `ferc714_forecast_growth` 38,332 to 198,354, `eia_steo_forecasts` 5,107 to 10,195, each now equal to `warehouse/output`. No archived line rewritten.
- Data requests 554 to 556: answered in a new file (the layers and `manifest.json` unchanged).

- Data requests 557 and 558 (the old laptop's findings audit, check 2): 48 of 48 hourly drafts and 47 of 47 FERC 714 drafts reproduce from this machine's whole tables.
- Part F: the GitHub daily prices job committed nothing to main from 16 to 19 November. Its merge tests failed in test 7014 (`75 != 0`, health.py's skip exit). Session 8009's fix reached main after the 14:00 UTC run of 19 November, so 20 November's run is the first with it (`queue/summary/2026-11-19-daily-prices-refused.md`).
- Part E4: the price file's replication gives 152 of 152. The cross-check against the operators' own published averages is not done. CAISO's market monitor publishes calendar-year and quarterly figures, and its monthly market performance page (April 2026, read after the robots file) gives day-ahead prices by load-aggregation point in charts only. No published hub average fits the file's windows, and the third-party monthly figures found do not count as the operators' own.

## Needs the key

- Nothing.

## Decisions made without you

- Took the resume file although the chain's last commit was only 70 minutes old: no other Claude process was running on the machine, and erw-f8 said Samuel confirmed the chain had stopped.
- Data requests 554 to 556 asked for changes to October layer files. Chain 505's rule is "add, never change", so the answers went into a new file, `site/data/resources/layer_notes_added.json`, as data request 553's did. The page code that would read it belongs to the portable laptop.
- Data request 30: fixed the archive's key for the three revisions tables, rather than uploading a copy to Redivis. Once the fix is on main, the old laptop's `restore.py --from-bucket` gives the whole table.
- Part D2 writes a page file only, with no table of its own. Its figures come from two public tables already in the warehouse, and a new table would need the whole registration (license record, v1, Redivis, catalogue) for no gain to the page.
- CAISO's whole-grid wind starts on 8 February 2024, because the three hubs are summed only for hours all three hold, and ZP26's wind (24 MW on average) starts then. Each hub's own figures start where that hub's data does.
- Part C's facts appear in the panel only where the whole-country index is held (the Grid tool), so `/network`'s panel is unchanged.
- Contract sections 12 (D2) went into the branch with the files, not to main ahead of them, so main gets no extra deploy.

## For Samuel's ruling

- The daily prices job's evening run counts the day done when the morning run's daily step passed, even when its merge tests then refused the commit, so a refused commit is not retried the same day. Counting only a "Daily prices <day>" commit would retry, but a retry can send the digest twice (session 61's reason for the gate). Default: the gate is unchanged.
- Where `/industry` and `/ai-energy` sit in the menu. Default: in no menu (they are reachable from the tour and by address).

- For leases where BOEM's two tables disagree on the lease type (OCS-A 0497, OCS-A 0506, OCS-G 37334 Provisional), which type a hover should show. Default: both, in the new file. The layer is unchanged.
