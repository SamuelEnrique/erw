# Session 5073 report: chain 243, the five cross-check tables, every row sourced and explained, a test per table

Energy Research Warehouse (ERW). Chain 243, portable laptop window P1, 13 November 2026, about 19:15 to 20:15 UTC. Opus 5.5. Model spend USD 0. Branch `wip/5072-crosscheck` (on `wip/5072-requests`). Precheck passed (exit 0).

- **Every row sourced.** The rows of `docs/methods/crosschecks/*.md` whose published figure is "No published counterpart" had empty source and gap cells; each now names our own figure's key in `replication/<tool>/page_figures.json` (battery 14, generator 9, datacenter 12, Grid 6 rows) and "none" as its gap.
- **Every "not explained" row explained** (seven rows):
  - **Battery, the fall from 2024 to 2025** (-40.8 against the monitor's -37 percent): the market monitor's own figures (pages 22 and 23) give the fleet, per kW, energy about -8 percent and reserves past -63; ours fell -8.5 and -64.6, the same falls. The gap is the mix: ours took 57.5 percent of 2024's revenue from reserves; the fleet's falls give -37 percent only at about 52 percent or less. ERCOT's day-ahead reserve prices fell about 50 to 70 percent (`ercot_as_prices_monthly`, read from the live set).
  - **Research, ERCOT's battery fleet** (13,909 MW against "exceeded 17 GW"), its 2025 additions, its duration, and the solar additions: what each counts. ERCOT's is capacity approved to operate at its High Sustained Limit, more than 17,000 MW and 31,500 MWh (pages ii and 15); EIA-860M's is the operating inventory in ERCO. The difference, 3,091 MW and 9,921 MWh, lasts about 3.2 hours, the longer batteries built last.
  - **Grid, ERCOT's and ISO-NE's 2023 intensity against eGRID** (+10.09, -12.76): EIA-930 counts 7.53 and 6.51 percent less generation than Form EIA-923 (`eia_annual_crosscheck.md`); if what both count emits alike, what EIA-930 leaves out runs at about 209 kg per MWh in ERCOT (cleaner, so ours is higher) and 428 in ISO-NE (gas and oil, so ours is lower). The fixed factors are not separated; the row says so.
- **A new published figure:** the datacenter page's carbon (301.82, by demand) beside eGRID2023's ERCT rate (332.87): -31.05, mostly ERCOT's fall since 2023 on EIA-930's own figures (342.96 in 2023).
- **Reads of public hosts** (each robots file read first, both allow the paths): Potomac Economics, the 2025 report (8.8 MB, its text extracted to quote pages ii, 13, 15, 21 to 23); EPA, the eGRID2023 summary tables (Table 2's generation). Quoted, not copied; nothing committed of theirs. Reads of the live set with the anon key: `battery_stack_monthly`, `ercot_as_prices_monthly`, `storage_buildout_monthly`.
- **The notes' own tables** (battery 25 rows, generator 34, datacenter 8: Lazard's LCOS and LCOE, the ATB, EIA's retail and ICE prices, Modo Energy, E3, Tyba, the market monitors) were already complete; the test now holds them so.
- **Tests:** `tests/test_session5073.py` (new, 21 tests: a class per table; each "Ours" equal to the page's figure for every field of `page_figures.json`, each gap ours less theirs, every row with a source and no "not explained", each new reason's arithmetic) and `tests/test_session3707.py`: 28 passed, 0 failed.

## Decisions made without you

- The notes' assumption rows stay in the notes (one copy), held by the test, rather than copied into the cross-check files.
- Where a cause cannot be proven from held data (the Grid intensities, the fleet counts), the reason states the arithmetic and its one assumption.

## For Samuel's ruling

- Nothing new.
