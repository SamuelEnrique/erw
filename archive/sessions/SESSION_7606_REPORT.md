# Session 7606 report: Grid read as its reader

Energy Research Warehouse (ERW). Chain 305, part C, portable-laptop, 17 November 2026, about 08:15 to 08:30 UTC (between session 7605's two builds). Model spend: USD 0.

- **Checked first:** no Grid read on any branch; claimed as row 28 of the claims file.
- **The reader:** a utility's market analyst writing the Monday note on ERCOT. Five cases: the latest hour (54,008 MW at Nov 15, 5:00 PM CST, against 51,212 a week earlier); the mix in that hour (gas 53 percent, wind 24); the net import (145 MW over 2 ties, SPP 144 MW, 51 hours old); the records of 2026 (peak hour 91,075 MW on 22 July, solar 34,982 MW on 3 August); the batteries on 12 November (27,987 MWh discharged, 40,150 charged).
- `docs/reviews/grid-read-2026-11-16.md`: 5 rows, **no site fault**. Every shared figure agrees: the batteries with `/storage`, the largest supplier between the network card and the exchange view, the highest hours with `/demand` (56 of 56, the old laptop's read).
- For Samuel's ruling: ERCOT's own stated peak record is not set beside EIA-930's 91,075 MW (default unchanged; an option, a line with ERCOT's release, as the 2023 heat page does); the page's second line lists 24 tables with their licenses before any figure (default left).
- Needs the key: "Ask ERCOT about this view", about USD 0.02 a question (not measured).
- Commit: `12970b5de` on `wip/7603-datacenters-read`.
