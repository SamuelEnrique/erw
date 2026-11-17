# Session 7052 report: desk stack c (portable row 38); done-line requests 209, 199, 239, 99, 142, 183, 189, 109

Energy Research Warehouse (ERW). Chain 370, data machine (lab-desktop), 17 November 2026. Opus 5.5. Model spend USD 0.

Precheck passed. Freeze: none.

## The landing desk

- **Gate l** (`db047b792`, `wip/c370-desk-c`, portable row 38) passed every step: suite, build, check-values (only the license holds' floors), routes, cross-checks, csp. Snapshot `before-db047b79` taken (25 pages, 0 checked numbers: every page is in review); pushed to `task/7052-desk` at 07:55 UTC (run 44042463853).

## Done-line requests

- **209, done.** ERCOT's Houston and North load zones in `cost_of_power_monthly`, from `ercot_zone_prices_history`, loaded.
- **199, done.** The Flex Alert scorecard's variant rows.
- **239, done.** Every battery-game level carries `fleet`: the grid's operating battery storage at the start of the level's month from the EIA-860M operating and retired generators (Uri, ERCO 2021-02: 21 units, 223.4 MW, 236.1 MWh; CISO 2026-07: 309 units, 17,110.7 MW). No level, date, price or shape moved.
- **99, done.** The EV prices rebuilt (August 2026 and the week of 9 November): the opening page reads $2,219, $844, $1,375, 3.6 years and $3,887; 104 of 104 prices equal to the tables, 5,141 of 5,141 figures inside. The worked examples keep the prices they were worked at.
- **142, done.** ERCOT's eight load zones in the hub price comparison (880 rows, loaded; the replication 454 of 454). The four non-competitive zones have no real-time price in the history's window: their real-time measures read lacking.
- **183, done.** The curtailment worth file's battery rule now says what it paid for what it took in (SP15 real time 2025: 23.62, 19.42 and 15.34 USD per MWh charged for 2, 4 and 8 hours).
- **189, done.** Berkeley Lab's workbook read (robots first); ERCOT types no withdrawn or suspended request as a hybrid, so its solar-with-storage shares are marked not comparable in the site's copy, with the United States' pair.
- **109, done.** `energy_projects` and the map's file carry a queue position's proposed in-service date.

## Errors

- **A local rebuild of `energy_projects` reached the archive.** For request 109 I rebuilt the table here; the loader refused it (this machine's queue inputs are older than the live copy, which the GitHub daily builds), but the archive step had already written its 45,612 rows, among them 5,695 MISO and NYISO queue rows the committed table does not hold. The earlier table was put back and archived again (the 5,695 keys recorded as deleted); the live set was never written. The map file was rebuilt from the committed table with the new date joined in, so nothing else in it moved.
- Two of my done-line marks (rows 261 and 189) carried a `|` inside the text and split the table; fixed.

## Needs the key

- None.

## Decisions made without you

- See `docs/state/progress_c370.md`, session 7052.

## For Samuel's ruling

- None new.
