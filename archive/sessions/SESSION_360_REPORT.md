# Session 360 report: EIA-930's adjusted series and the balance

20 October 2026, from 10:30 UTC, unattended, on lab-desktop (the data machine), the fourth session of the chain of 20 October, night. Model spend USD 0. Pulls: EIA's API 2 of the ceiling of 200 requests.

## Read these first

- **EIA's adjusted series do not close the balance, so nothing is switched and no ruling is needed on which series the Grid tool draws** (`docs/methods/eia930_balance.md`). EIA's own notes: an adjusted value is the reported value unless EIA imputed an anomaly. In 840 hours (13 September to 17 October 2026) EIA imputed nothing for six of the seven grids, and two hours of ISO-NE's demand and generation; every mean gap is the same reported and adjusted.
- **The pack's figures reproduce** (CAISO 3,199.1, PJM 2,042.1, MISO 1,397.9, SPP 978.1, ERCOT 1.6, NYISO 0.4 MW over its 360 hours; ISO-NE 0.0 against the pack's 0.7, EIA having revised since).
- **What remains, split in two:** CAISO's and MISO's ties sum to their own total interchange within 1 MW; their gap is total interchange against net generation minus demand (3,002.8 MW, 9.6 percent of demand; 1,430.1, 1.9 percent). SPP's total closes (26.0 MW) and its ties do not sum to it (1,023.2 MW, 2.9 percent, without two hours whose SPP to MISO tie reads minus 2,148,411 MW, 4 October 12:00 and 6 October 19:00 UTC). PJM has both kinds.
- **EIA's thresholds have no unit in its sheet.** Read as a percent of demand, only CAISO's total gap (277 of 840 hours) and SPP's two impossible hours pass them; read as MW, CAISO's, MISO's and PJM's gaps pass them in nearly every hour.
- **EIA's API holds no adjusted or imputed series** (its region data are D, DF, NG and TI only). They are in the workbooks EIA publishes for each grid, which this machine had saved the evening before: no further request was made.

## What to review

1. `docs/methods/eia930_balance.md` and its figures `docs/methods/eia930_balance.json`.
2. `warehouse/analysis/eia930_balance.py`; `tests/test_session360.py` (2 tests).
3. The Grid pack's item 3 (`docs/reviews/packs/grid.md`, section 6), one sentence added.

## Pulls against their ceilings

| Pull | Ceiling | Used |
|---|---|---|
| EIA's API | 200 | 2 (the facet "type" of `region-data`; the list of `electricity/rto` routes) |

## Checks

| What | Exit | Notes |
|---|---|---|
| `warehouse/analysis/eia930_balance.py` | 0 | three runs: the first summed the ties only where every neighbour column EIA's sheet names was held (some are never filled), so the tie gap came out empty; the second used the columns that hold data; the third added the MW reading of the thresholds |
| `tests.test_session360` | 0 | 2 tests |

## Decisions made without you

1. **The workbooks EIA publishes are read in place of the API** for the adjusted and imputed series, since the API does not hold them; the prompt's ceiling was for the API, and two requests were enough to show it.
2. **The window is the span the live interchange table holds** (840 hours to 17 October; the live table's own last hours lag a day), and the pack's 360 hours are reproduced beside it.
3. **The thresholds are reported under both readings**, percent of demand and MW, since EIA's sheet states none.
4. **SPP's two impossible hours are named and left in the data**: the screen for an hour of interchange is the pack's item 10, not tonight's.

## For Samuel's ruling

- None on the series: the adjusted series would draw the same figures. Whether to screen an hour of interchange for impossible values (SPP's two hours) is the Grid pack's item 10.

## Files

- New: `docs/methods/eia930_balance.md`, `docs/methods/eia930_balance.json`, `warehouse/analysis/eia930_balance.py`, `tests/test_session360.py`, this report.
- Changed: `docs/reviews/packs/grid.md`.
