# The portable laptop's window P1, chain 255: the five tools, read through and two more faults fixed (13 November 2026)

Energy Research Warehouse (ERW), session 5407, for Samuel. Chain 255 (`queue/done/255-day-16-november-portable-p1-five-tools-continued.md`), window P1 of the portable laptop, about 20:30 to 21:05 UTC, Opus 5.5. Sessions 5400 to 5408 (the file's 5418 note written as 5407 and its 5419 as 5408: the work ran out before the numbers did). Chain 243's note (`note_2026-11-13_portable_p1_c243.md`) holds the evening's first part.

- **Model spend: USD 0.** No warehouse data written; `site/lib/release.ts` untouched; nothing sent or posted.
- **Landing row 25** (`wip/5072-read`, holds row 24; row 24 marked "superseded by row 25"): `origin/main` merged, the stack's tests pass; its head moved at each session. Not yet landed.
- **The local build:** not tried (0.4 to 2.1 GB free all evening; chain 243's build was stopped by Claude Code for memory). Reads on production in the internal view instead.

## What changed

- **Research row 6 fixed (my own fault of session 5073):** the Research cross-check table quoted the cards of 6 November; it now holds those of 12 November, and the test holds every card figure the page prints to it.
- **The cross-check tests no longer stop a landing when the daily run moves the data:** the datacenter's and Research's figures files are rewritten every day; a difference with their hand-set tables is now a skip with its list, as test 3703 does.
- **Grid row 4 fixed:** MISO's hours read "GMT-5" beside the other grids' zone names; now "EST" (MISO keeps Eastern Standard Time all year).
- **The generator's table gains three published counterparts** from ERCOT's market monitor's 2025 report: solar's captured price ($21 per MWh beside our 23.27) and the gas peaker's 2025 net revenue ($52.59 per kW-year beside our 50.42) and peaker net margin (almost $79).
- **Step 6's reads done:** every battery case of both grids, the generator's other cases, the datacenter page's grids and views, Research's twelve cards, the Grid's eight grids: 61 pages since session 5076, at 1280 and 390, all clean by measure; the only differences found are battery row 10 and datacenter row 4 (the price years of 20 October, window A's).

## For window P3

- `tests/test_session137.py` `test_the_panels_own_tests_pass` fails on main (`site/scripts/test-ask-panel.mjs`, line 45).

## For Samuel's ruling

- The eight of chain 243's note stand, with their defaults.
