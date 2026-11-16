# Session 7016 report: the done-line data requests 7, 10, 11, 24, 26, 27, 29 and 33; gates f and g

Energy Research Warehouse (ERW). Chain 301, data machine (lab-desktop), 16 November 2026. Opus 5.5. Model spend USD 0.

## The landing desk

- Gate f (`wip/c301-tail`, `f04c808e3`) failed on `test_session204` alone: the order of `scheduled.DATA_MACHINE` (session 7014 put the two profiles at its front). Fixed on `wip/c301-after` (the profiles at its end; the test lists them after the seven). Gate g (`4f2d076f5`) passed every step of `land_check.py` at 14:46 UTC; landing waits for 16:15 UTC (no landing between 14:00 and 16:15).
- Gate g's first start stopped at once: main had moved between the merge and the gate. Merged again and restarted.

## The data requests (`docs/state/data_requests_done_line.md`)

- **7, answered.** The battery awards, offers and real-time tables are current on this machine (built 15 and 9 November, rebuilt 16 November) and loaded; each holds through August 2026, the last whole month of ERCOT's 60-day disclosure.
- **29, done.** The node basis spans every day of the node pull (28 September to 15 November); its Coverage line, which said one week, corrected at the builder (`ercot_storage_realtime.py`); both tables rebuilt, validated, covered, archived, loaded (2,062 rows written). Snapshots `before-load7016` and `after-load7016`: 0 differences.
- **27, done at the cause.** The shoulder table and the shares took different days in a month short of one. The three months lacked CAISO output days: 8 March (the spring clock change), 21 August (CAISO's file holds no interval), 22 September (287 of 288). CAISO prints the missing hour of the spring change as twelve blank rows, and both Outlook connectors refused the day (`NonExistentTimeError`). They now drop wholly blank rows before reading the clock (a value in that hour still stops the day); `caiso_outlook.py` takes `--start` and `--end`; test 7016_caiso_spring. 8 March read for `caiso_fuel_supply` and `caiso_battery_storage`; the daily cycle, the shares and `iso_curtailment_monthly` rebuilt: March 2026 now 31 of 31 days, 774,414.884 MWh, the share 9.86 percent (9.31 before), the shoulder table's figure exactly. Snapshots `before-load7016b` to `after-load7016d`: 0 differences.
- **26, done.** 380 of 380 month figures of the shoulder table's fleet equal the storage buildout's, in the tables and the live set; test 7016_shoulder_fleet fails when they drift (it runs where the tables are held).
- **33, code done.** EIA-860M's sheets are read as printed (`keep_default_na=False`), so a generator id of NA is kept; a balancing authority of NA is still blank, said in the header; test 7016_eia860_na. The workbook of 24 October is not on this machine: the tables take it at the next vintage, not by a pull out of turn.
- **24, done.** EIA's monthly first purchase prices of Texas (`F003048__3`), Louisiana (`F003022__3`) and New Mexico (`F003035__3`) beside North Dakota, each id checked against EIA's area name by one API request; 590 months each through August 2026; the table in the live set (`full`), loaded, 2,632 rows. Snapshots `before-load7016e`, `after-load7016e`: 0 differences.
- **11, done.** The impact page's parameters recomputed from the four tables by `params.py`: all equal. One builder fault: `params.gas` refused because the table holds two STEO releases (24 history months); it reads the newest (test 7016_forecast_gas).
- **10, done.** `params.income` reads a credit printed in the deduction's column; Utah's $966 held as a credit. `/impact?tech=geothermal&state=ut&mw=86&start=2026`: state income tax over the life USD 23.4 million (28.4 before), by the page's own `run()` on both files (test 7016_utah_credit).

## Decisions made without you

- Utah's file entry was rewritten from the text the file itself stores, under the corrected rule, since the Tax Foundation page it was built from is not saved on this machine.
- Request 33's tables wait for the next EIA-860M vintage rather than a pull out of turn.

## For Samuel's ruling

- None new.
