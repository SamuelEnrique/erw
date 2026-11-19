# Session 8013 report (chain 505, lab-desktop, 19 November 2026, from 21:31 UTC)

Resumed chain 505 from `queue/done/550-resume-chain-505.md` (551 put back). The machine had lost power at about 20:20 UTC in the middle of part D1 (the owner's word, passed on by the other desktop window, erw-f8, which stood down).

## What a reader now sees

- (filled in at each landing)

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

- For leases where BOEM's two tables disagree on the lease type (OCS-A 0497, OCS-A 0506, OCS-G 37334 Provisional), which type a hover should show. Default: both, in the new file. The layer is unchanged.
