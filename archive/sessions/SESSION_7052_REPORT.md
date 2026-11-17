# Session 7052 report: desk stack c (portable row 38); done-line requests 209, 199, 239, 99, 142, 183, 189, 109

Energy Research Warehouse (ERW). Chain 370, data machine (lab-desktop), 17 November 2026. Opus 5.5. Model spend USD 0.

Precheck passed. Freeze: none.

## The landing desk

- **Gate l** (`db047b792`, `wip/c370-desk-c`, portable row 38) passed every step: suite, build, check-values (only the license holds' floors), routes, cross-checks, csp. Snapshot `before-db047b79` taken (25 pages, 0 checked numbers: every page is in review); pushed to `task/7052-desk` at 07:55 UTC (run 44042463853).

- **Desk stack c landed.** The checks of run 44042463853 passed, and its merge job lost a race to another push to main; the failed job was rerun once (the suite again on the moved main) and merged at `1dc009dad` (08:40 UTC). Snapshots `before-db047b79-b` (taken again after main moved), `after-db047b79`: **0 differences**. Portable row 38 marked landed.
- **What a reader now sees** (production, the internal cookie, headless Chrome): `/supply`, `/events/uri-2021` and `/events/caiso-heat-2022` at 1280 px and at 477 px (the narrowest window headless Chrome would open; 390 px was not reached): no page is wider than its window, with every fold open; the grids line of `/supply` breaks between grids (445 px at the narrow window). The one-point chart's axis and the wide tooltip were not exercised.

## Done-line requests

- **209, done.** ERCOT's Houston and North load zones in `cost_of_power_monthly`, from `ercot_zone_prices_history`, loaded.
- **199, done.** The Flex Alert scorecard's variant rows.
- **239, done.** Every battery-game level carries `fleet`: the grid's operating battery storage at the start of the level's month from the EIA-860M operating and retired generators (Uri, ERCO 2021-02: 21 units, 223.4 MW, 236.1 MWh; CISO 2026-07: 309 units, 17,110.7 MW). No level, date, price or shape moved.
- **99, done.** The EV prices rebuilt (August 2026 and the week of 9 November): the opening page reads $2,219, $844, $1,375, 3.6 years and $3,887; 104 of 104 prices equal to the tables, 5,141 of 5,141 figures inside. The worked examples keep the prices they were worked at.
- **142, done.** ERCOT's eight load zones in the hub price comparison (880 rows, loaded; the replication 454 of 454). The four non-competitive zones have no real-time price in the history's window: their real-time measures read lacking.
- **183, done.** The curtailment worth file's battery rule now says what it paid for what it took in (SP15 real time 2025: 23.62, 19.42 and 15.34 USD per MWh charged for 2, 4 and 8 hours).
- **189, done.** Berkeley Lab's workbook read (robots first); ERCOT types no withdrawn or suspended request as a hybrid, so its solar-with-storage shares are marked not comparable in the site's copy, with the United States' pair.
- **109, done.** `energy_projects` and the map's file carry a queue position's proposed in-service date.

## Later in the session

- **Gate m** (`783c0b2a5`) failed one test: `datacenter_page` (and `capture_price`) built their table lists from the comparison's, which request 142 had given the ERCOT zone history, so the history stood twice. Each now reads it once. **Gate n** (`ce8daa34b`, `wip/c370-data-n`) passed every step; pushed to `task/7052-data` at 09:17 UTC (run 44054287848). Snapshot `before-ce8daa34`.
- **Requests done:** 162 closed (CAISO's autumn-day files print 288 rows: one of the day's two 01:00 hours is not published); 150 and 151 (CAISO's five missing supply days pulled; every remaining gap named to its hours in `docs/reviews/supply-burn-gaps-2026-11-17.md`); 152 (CAISO's and SPP's cleared-energy days pulled); 262 (the weekly chart's source line: EIA-930 for the Lower 48, the ERW once); 263 (Wyoming's gas of July and August 2026 is EIA's figure as published); 180 (CAISO's October curtailment share over 31 days); 122 (`iso_prices.py --only-days`; SPP's ten days whole, loaded; the board rebuilt); 261 (the battery page's awards line, January to August 2026, with the note's table, the replication and the do-file); 201 (a new table, `caiso_outlook_demand`, the 39 alert days, registered and on the Redivis draft). 200 to Samuel's ruling (EIA's robots file disallows the archive that holds the earlier ICE years).
- **Part A's review rows:** 94 rows marked `data machine` in the 2026-11-16 read and faults files marked with their request's state and commit (fixed 65, answered 19, ruling 10); one stays open (a known gap never asked), and request 152's row was marked when it was done.
- **Desk stack d:** portable rows 39 (`wip/7603-datacenters-read`, `1837d6d1e`) and 40 (`wip/7610-fault-rows`, `f00c708c8`) merged without a conflict and folded into the chain branch for one gate (gate o, which waited on another session's build lock, was stopped before it took the lock).
- **Parts B and C:** all eight of this machine's tools were read by samueloldlaptop (sessions 7538 to 7545) and landed with desk stack b; every row of the claims file carries a read. Nothing is left for this machine.
- **The live set:** loads of `hub_price_comparison`, `iso_rtm_hub_prices` (655 rows past its 35-day window removed; every market's newest hour unchanged) and checks of `energy_projects` (refused, as it should be: this machine's inputs are older).

## Errors

- **A local rebuild of `energy_projects` reached the archive.** For request 109 I rebuilt the table here; the loader refused it (this machine's queue inputs are older than the live copy, which the GitHub daily builds), but the archive step had already written its 45,612 rows, among them 5,695 MISO and NYISO queue rows the committed table does not hold. The earlier table was put back and archived again (the 5,695 keys recorded as deleted); the live set was never written. The map file was rebuilt from the committed table with the new date joined in, so nothing else in it moved.
- Two of my done-line marks (rows 261 and 189) carried a `|` inside the text and split the table; fixed.

## Needs the key

- None.

## Decisions made without you

- See `docs/state/progress_c370.md`, session 7052.

## For Samuel's ruling

- **Request 200.** Download EIA's ICE files of 2018 to 2025 by hand for the connector's offline read? Default: not fetched (EIA's robots file disallows `/*archive/`).
- **Request 261.** A daily `--snapshot` step for the battery page's awards line? Default: not added (each month would move what tests 178 and 7505 pin).

- None new.
