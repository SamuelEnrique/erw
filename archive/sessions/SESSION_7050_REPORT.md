# Session 7050 report: chain 370 begins; the desk's seven old-laptop rows gated; done-line requests 59, 69, 79, 80, 110, 119 to 122

Energy Research Warehouse (ERW). Chain 370, data machine (lab-desktop), 16 and 17 November 2026. Opus 5.5. Model spend USD 0.

Taken by chain 301's queue step (`e6b9450bb`) after chain 301's last session (7022) closed it. Precheck passed. Session numbers 7050 to 7052 free. Resume pointer `queue/next/380-resume-chain-370.md` pushed alone (`4d511ff2f`). Freeze: none.

## The landing desk

- Seven rows of the old laptop requested (29 `/events`, 30 `/grid/caiso/alerts`, 31 `/learn/bill`, 32 `/learn/problems`, 34 `/play/ev`, 35 `/map` read, 36 `/board` read), merged in one stack `wip/c370-desk-a` on main without a conflict.
- **Gate a** (`715e1b046`) failed 3 tests: the waits reader (test 188) read two tables of reports 7531 and 7534 that had no header row (rows copied from the request files) as paragraphs; each got its source file's header. Test 7534's two replays import the site's `react`, absent where the gate's suite runs; they now skip there, as the other node-reading tests do (they pass with the packages, checked).
- **Gate b** (`a8431f37d`): the suite passed (9,998 tests); check-values failed one figure of row 30's page: `/grid/caiso/alerts` writes a day's effect in USD whole under a million ("-479,791" for -479791.0043), and check-values expected two decimals. A whole-dollar rule added for that key.
- **Gate c** (`097c519a1`): started 00:32 UTC.
- Gate c failed the same figure: it is a `data-format="usd"` amount, read by check-values' own usd(); fixed at the cause (an amount under a million is also read as whole dollars; 395 of 395 on the page against gate c's build). Gate d failed test 315 (the line's pinned first term); fixed. **Gate e** (`8f10ebcfa`) passed every step; landed through `task/7050-desk` (run 44000977927) at `695d8f9f4`. Snapshots `before-8f10ebcf` and `after-8f10ebcf`: **0 differences** (expected: every page is in review). The rows marked landed (`79ea9acf0`): 0 differences.
- **Chain 370's branch** (`5926ae36f`) passed gate f and landed through `task/7050-data` (run 44008498501) at `0ab3ec772`: snapshots `before-5926ae36`, `after-5926ae36`, **0 differences**.

## Done-line requests

- **Marked, done in session 7022:** 30, 31, 35, 45, 47 (they had been left "requested").
- **69, done.** `cost_of_power_monthly` and its two companions rebuilt through October 2026 (ERCOT 744 of 744 hours; MISO 48, paused since 4 October), loaded, and built daily on the data machine from now (`dm_cost_of_power`, in the daily and weekly live loads; tests 247, 271).
- **59, done.** A CAISO notice whose frame names one date and two times ("10/1/2020 15:00:00 through 22:00:00") is that date's: the Flex Alert of 1 October 2020 (issued 30 September) moved to its day; the table written again (1,906 rows) and loaded (test 7050_flex_day).
- **79, done.** ERCOT's 14 November had every hour but EIA's early values (the evening discharge at 853 MW against 8,438 the day before; EIA's workbook held none of those hours yet). The cycle table now writes a day only 48 hours after its end, when the storage connector has asked EIA for it again (test 7050_storage_settle).
- **80, done.** EIA now holds ERCOT's battery hours of 4 to 8 November: pulled (`eia930_storage.py --since 2026-11-03`), the cycle rebuilt and loaded.
- **119, done.** The board's Henry Hub and spreads stood at 3 to 6 November because ISO-NE's heat rate, kept as "only the held file has it" (its prices held for license), anchored the set. A row the new build does not make now anchors nothing (test 3889); the board rebuilt: Henry Hub to 11 November, the spreads to 15 November.
- **120, answered.** EIA publishes the holiday repeats itself (11 November and 7 September 2026, from its API); said in `docs/methods/price_board.md`.
- **110, done at the cause** by session 7022's request 40 (ERCOT's milestones in the queue connector), from the runner's next pull.
- **121, ruling** (ruling 2: ERCOT's 7 and 8 November only through the frozen paths; not refilled). **122, checked in part** (11 November is SPP's own gap; the October days wait for a per-day option of the connector).
- **49, in part:** the live set holds the old laptop's build (2026-10-19T09:43:29Z, 29,953 rows); the replication comes with desk row 29. **99** waits for desk row 34's figure script. **109, open:** a queue position's proposed date through `energy_projects` and the map's file.
- After the desk landed: **49, done** (`replication/events/replicate.py` on the live set's build: 1,149 of 1,149 page figures, 2,890 of 2,890 rows, 186 of 186 estimates). **99, in part:** the rebuilt prices give 5,245 of 5,245 once the figure script stops reading the chart's crossing label as a money tick (fixed); the file is not committed because the new prices move the hand-worked examples tests 294 and 7536 pin, which must be recomputed with it.

## Errors

- A metadata patch conflicted on `package/llms.txt` and the commit took its markers (`f1c90087d`, the commit of request 59); the next commit (`6caff800e`) wrote the file again from the metadata. Every later carry leaves `llms.txt` out and writes it again.
- The data lock was held from 23:34 to 00:02 UTC for the writes above; no GitHub job was seen waiting on it.

## Snapshots

- Pushes to main of this session: the resume pointer (queue file); comparisons before and after the queue moves, 0 differences. The loads: `before-load7050`, no page live, every page in review.

## Needs the key

- None new.

## Decisions made without you

- Request 79: a day waits 48 hours after its end rather than carrying a count of hours (every hour was present; the count could not tell).
- Request 119: a row the new build does not make keeps its held values but anchors no set.
- The desk's two fixes to the laptops' files (headers in their reports, a skip in their test) were made here, as the desk's earlier fixes were.

## For Samuel's ruling

- None new.
