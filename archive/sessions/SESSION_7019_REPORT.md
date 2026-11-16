# Session 7019 report: the done-line requests 2, 3, 5, 6, 8, 9, 19 to 23, 25, 28, 30, 31, 35 and 36

Energy Research Warehouse (ERW). Chain 301, data machine (lab-desktop), 16 November 2026. Opus 5.5. Model spend USD 0.

The GitHub daily run (43881234167) held the data lock through this session, so every request that writes a table was taken to its code, test and trial, and its write waits for the lock (`docs/state/progress_c301.md`).

## Done or answered

- **9.** `state_large_load_laws` is in the Redivis draft (27 rows, 14 November) and out of release v1 (its verdict unsettled): it left `/policy`'s downloads line; the laws block's own CSV stays (tests 332 and 7201).
- **2, 23, 3.** The severance screen's inputs (`rrc_lease_production_statewide` and the screen's files) are in none of the warehouse's stores: they are samueloldlaptop's; the rules file is on `wip/7502-severance`. Answered; reopen once the branch lands.
- **5, 28.** Wait for their branches to land, as the rows say.
- **19.** Migration `037_eqr_contract_terms.sql`: `internal_eqr_contracts` answers the row's period, increment and rate bounds. For a person to apply (`apply.py --only 037`).
- **20.** The stored EQR summary counts rows and priced rows by quarter, product group and delivery authority (test 7019_eqr_summary); stored at the next load.
- **21.** `site/data/eia930_ba_names.json`: EIA's 81 balancing authorities from its EIA-930 reference tables (saved raw; public domain); nothing of the internal EQR tables in it (test 7019_ba_names). 66 of the data machine's 99 delivery codes are EIA codes.
- **22.** For Samuel: serving one party's line would load `ferc_eqr_party_totals`, which session 102's rule keeps out of the live set. A function was written and taken back out.
- **6 and 25 (a).** The register of source faults has ERCOT's battery column's change of meaning (checked in EIA's workbook: no value below zero in 10,008 hours to 14 December 2025, 5,086 of 7,873 below zero from the 15th); the shoulder note has it and California's two demands beside the batteries' charging, June to November 2025 (a difference of definitions, stated in the note, not a source fault). The register's site copy waits for the lock (test 118 fails on this branch until then).
- **8.** The last working words reworded at the source (the research's notes, rows and legislation file); session 7009's pass had reached the other cells. The laws table and the page file wait for the lock.

## Code, tests and trials; the writes wait for the lock

- **36.** The peak premium's annual table carries `ytd_<variable>` for every year (test 7019_peak_ytd).
- **35.** `ercot_node_peak_premium.py`: the metrics for every settlement point by month from October 2026. Trial: 17,472 rows, 312 nodes; the six hubs' 168 October figures equal the hub table's. Its sector rule and release v1 line are in; the license record, the Redivis draft and the load follow the write.
- **31.** The awards and real-time tables by duration class (under 2 hours, 2 to 4, 4 and over, not seen in real time), each class a floor from the highest state of charge over the highest HSL seen in real time. Trial of the awards table: the classes add up to the fleet (August 2026: 336 resources, 21,422.7 MW); test 7019_esr_classes.
- **30.** `ercot_storage_rt_offers.py`: what the fleet offered to sell in real time at USD 0, 25, 50, 100, 250 and 1,000 per MWh or less and at any price, by month from February 2026, from the 208 saved 60-day SCED zips.
- **4** and **32** (from session 7017).

## Decisions made without you

- Row 22 left for you rather than lifting session 102's rule unasked.
- California's two demands are a difference of definitions and stand in the note, not in the register of source faults, whose rule is a publisher's faults only.
- The new EIA list is a site file, not a table, so that it needs no license or release registration.

## For Samuel's ruling

- Row 22 (above). Row 6's second variable (default: the column as published). Row 25 (b), a second set of variables (default: none).
