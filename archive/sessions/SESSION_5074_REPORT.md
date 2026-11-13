# Session 5074 report: chain 243, the Python replication's parity with every do-file of the five tools

Energy Research Warehouse (ERW). Chain 243, portable laptop window P1, 13 November 2026, about 19:24 to 19:32 UTC (corrected by session 5075: this line said 20:15 to 21:00). Opus 5.5. Model spend USD 0. Branch `wip/5072-parity` (on `wip/5072-crosscheck`).

- **What existed.** Each tool has a Python replication that already meets the page's figures (`replication/<tool>/replicate.py`, tests 1487, 1489, 1491, 3701, 3703), and its do-files (nine: the public `erw_2026_<tool>_replication.do` of the three decision pages, `replication/<tool>/replicate.do` of the five, and the Grid's `replicate_ask.do`) were tested for the owner's Stata rules only. Nothing tied a do-file's figures to the Python's.
- **What is new, `tests/test_session5074.py`** (16 tests), so your Stata run confirms rather than unblocks:
  - **Battery, generator, datacenter:** the page's Python mirror (`site/public/<page>/erw_2026_<tool>_replication.py`, the do-file "step for step") is run on the public file; each of the 49 figures of `page_figures.json` (22, 13 and 14, each a check-values key or a named scenario figure) is read from the mirror's own printed line and meets the page within its tolerance; every line the mirror prints is a `display` of both do-files, with the same decimals and thousands separator; the values each `replicate.do` states in its header as the mirror's output are what it prints (the datacenter's by label only: its public file moves with the data machine's daily run).
  - **The one difference of words:** the datacenter mirror prints "hours of the hourly window the price and the intensity are both held", the do-file "hours of the hourly window" (it takes the price as held throughout, its comment says so). The test recomputes the do-file's step from the public carbon file: 10,151 hours and 309.54 kg per MWh, the mirror's two figures.
  - **Research:** every one of the figures `replicate.py` computes (at least 60) is set by `replicate.do` from a scalar it defines, for the same card and field, and every figure the do-file sets is one the page prints. The week's chart is `replicate.py`'s alone (it changes every week), as the do-file says.
  - **Grid:** every network and gravity figure is computed by `replicate.py` on the committed snapshot and meets the page; every family of check keys the page prints is built by `replicate.do`; each of the Ask figures is either stated by `replicate_ask.do` with the page's value and tolerance (at least 24) or named there as `replicate.py`'s (grouped queries, compares) or "license needed".
- **One gap closed:** the Grid's `replicate.do` did not build the network's carbon intensity per grid in the hour shown (7 page figures, `series|carbon_intensity_hourly|...`); it now does, from the hour's own row as `replicate.py` reads it, in the owner's rules. Not run (no Stata here). `docs/methods/grid_network.md`'s replication table says so.
- **Corrected:** session 5073's report said each robots file was read first; Potomac's was read by session 3708 on 6 November and again after this chain's fetch (it allows the path).
- **Tests:** the 15 files that touch the replications, the do-files and the cross-checks (1487 to 1492, 3701 to 3703, 3705, 3707, 3889, 5005, 5073, 5074): 113 tests, OK, 2 skipped (the tables are not on this laptop; the snapshot was rebuilt after the figures); the 21 files that read the Grid note: 180 tests, OK, 9 skipped.

## Decisions made without you

- The parity is held through the page's own Python mirror and the do-files' printed words, not by running Stata; the one step neither can share (the datacenter's price check per hour) is recomputed in the test.

## For Samuel's ruling

- **The do-files, run in Stata.** Default: "never run". When you run one, its printed lines should be the mirror's, line for line: `python site/public/<page>/erw_2026_<tool>_replication.py` prints them.
