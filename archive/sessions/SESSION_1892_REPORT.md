# Sessions 1892 and 1893: the battery page's waiting month and the generator page's one window (chain 217, 13 November 2026)

Energy Research Warehouse (ERW). Chain 217, sessions 1892 and 1893, samueloldlaptop, unattended, Opus 5.5. Run by one agent in `erw-1892` on `wip/1892-windows`, cut from `wip/1883-board` (`30b5b3573`). About 01:00 to 01:40 UTC. The agent wrote no report; this one was written by session 1902 of chain 219 from the branch's commits and `runs/s1892/`. Faults 2 and 1 of session 1885's trader path walk (`docs/reviews/trader-path.md`), their site parts.

## What it did, with commits (branch head `b2723d272`, pushed)

- **Fault 2 (session 1892), `/cost-of-power/battery`, ERCOT:** October 2026 (29 of 31 days solved, 1 left out) was outside the headline, which ends September 2026, while the year chart and the income table called 2026 "10 months" (66.39 per kW) and `months.csv` marked the month "held: yes". `lib/batterystack.ts` `monthsOf` now passes its months through `settle`: a month at 90 percent that is not whole and newer than every whole month is not held, so the headline, the year chart, the income table, the averages, `months.csv`, the check keys and `price-years.mjs` take the same months. `months.csv` names the waiting month in a `#` line ("2026-10: 29 of 31 days solved and 1 left out, not yet whole: not held ..."). Method note in `docs/methods/battery_earns_algorithm.md`. `8268452b3`.
- **Fault 1 (session 1893), `/cost-of-power/seller`:** revenue and coverage read "Oct 2025 to Sep 2026" beside the capture card's "Nov 2025 to Oct 2026" and a capture chart of "2026, 10 months". Every capture figure on the page (card, sentence, results row, chart, the table of every hub, `tables.csv`) now takes the capture file's months up to the model's last month (`lib/capture.ts` `upTo` and `cutHub`; `model.ts` `capCut`); check keys end `@<month>`. ERCOT hub average, real time, solar: 23.27 against 32.17, Oct 2025 to Sep 2026. Where the capture file ends first, the card names both windows. `fad204f20`, `b2723d272` (the pins of `test_session235` and `test_session264` follow).

## Tests and the built page

- `tests.test_session1892` 7 OK, `tests.test_session1893` 7 OK, the rerun of the related files 19 OK, `test-decisions-195.mjs` 30 of 30 (its 28-of-31 check now expects the month not held).
- Built and read on a local build (`runs/s1892/read.out`, shots `runs/s1892/shots/`): the four battery addresses read "2026, 9 months held"; ERCOT's `months.csv` 2026-10 "no"; the seller's `tables.csv` capture rows "2025-10 to 2026-09".

## Decisions made without you

- (Session 1902) The report was written from the branch and the run folder, the agent having ended without one.

## For Samuel's ruling

- None new. The data machine's part of both faults stays: October whole in `battery_stack_monthly` and `merchant_revenue_monthly`.
