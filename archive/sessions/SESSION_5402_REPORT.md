# Session 5402 report: chain 255, Research's cross-check table set to the cards of 12 November (Research row 6)

Energy Research Warehouse (ERW). Chain 255, portable laptop window P1, 13 November 2026, about 20:39 to 20:45 UTC. Opus 5.5. Model spend USD 0. Branch `wip/5072-read`.

- **The fault (my own, session 5073):** `docs/methods/crosschecks/automated_analysis.md` quoted the finding cards of 6 November while the page and `replication/analysis/page_figures.json` print those of 12 November. Session 5073 held only the three decision tools' tables to their page figures, so the drift passed its test.
- **Fixed:** every quoted figure set to the cards of 12 November: `siting_gigawatt`'s least all-in 41.04 (was 40.99) and its two years (323,536,168 and 369,243,514), the curtailment estimates (8,426 and 18,153 MWh a day; 634 and 994 MWh per GWh; 917 MW predicted), the flexible load's hub figures (42.41 and 32.54), the queue's 3,591 GW (was 3,509; the gap against the thesis +90 GW, +0.2 points) and its best technology's 53 percent. The gaps recomputed: -25.98 and -20.19 against Texas's industrial retail price.
- **The test:** `tests/test_session5073.py` gains a check that every figure a card prints (not held for a license) is quoted, as the page shows it, in that card's rows (at least 60), and the two new gaps. 22 tests, OK. Research faults row 6.

## Decisions made without you

- **The tests do not stop a landing when the data moves.** The datacenter's and Research's `page_figures.json` are rewritten by the data machine's daily run (`run_data_machine.sh`, PAGE_PATHS), and their cross-check tables are set by hand: a difference there is now a skip with its list and the instruction to set the table again (as test 3703 skips on a newer snapshot), Research's check strict while the file is written for 12 November, the day the table names. Session 5073's datacenter check would have failed every landing at the next daily run; it now skips. The battery's and the generator's figures files are fixed, so theirs still fail.

## For Samuel's ruling

- Nothing new.
