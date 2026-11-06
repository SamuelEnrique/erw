# Session 2967 report: the explorers' and the trackers' figures checked

6 November 2026, about 10:34 UTC, on lab-desktop (the data machine), chain 157 (the owner's), unattended. Model spend USD 0. Pulls: none (the local build only; no check-values against production, the owner's ruling of 24 October).

## Read these first

- **check-values on the local build of this chain's branch** (the landing gate's, `782d5e2d`, port 3157): **7,812 of 7,812 values match**.
  - Its 2 failures are main's known floors (`/deals` and `/learn/problems/know-your-grid`; `runs/c147/cv_diff.py`: 0 new). They are not this chain's.
  - Session 2958's 19 `allgrids|queue|` keys are among the matched (CAISO's 3 rows, ERCOT's 14, SPP's 2).
- **The pages that draw a table this chain wrote or landed:**
  - the All grids tab (the queue line);
  - `/ask` and the board's Ask (chain 152's landing, checked by its own gate's check-values, 7,793 of 7,793).
  - The four derived tables are drawn nowhere else yet (session 2958).
- **The tab, read with the internal cookie on the same build:** the queue line on all 48 rows, 19 with a figure and 29 with their words. ISO-NE, NYISO and MISO read "license needed", PJM "not held". No blank. The server's HTML is one at 390 and 1280; the layout needs a browser, which did not connect.
- **The Ask evaluation's `runs.json`** is consistent: tests 1315, 1147 and 1304 pass with the 17 runs of both chains (session 2969's merge).

## Decisions made without you

- None.

## For Samuel's ruling

- None new.
