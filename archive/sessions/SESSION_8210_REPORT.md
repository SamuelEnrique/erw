# Session 8210 report (chain 502, lab-desktop second window)

19 November 2026, 12:16 to 12:22 UTC (read from the clock). Opus 5.5. Model spend: USD 0. Parts B and C checked at the start: both still waiting.

## Part D, third pass: cross_family, 9 drafts

- Two of this chain's families read together (`deep/cross502.py`): the seven ISO planning areas' FERC 714 forecasts and their balancing authorities' EIA-930 demand, on the method note's map. For each year 2019 to 2025, the actual peak hour (a lone spike dropped) and the actual yearly demand against what the area's filing of three and of five years before forecast for that year.
- Filings in the wrong unit (gaps of tens of thousands of percent in the energy forecasts of New York, CAISO, ISO New England and the Southwest Power Pool) are dropped: a year whose actual is under half or over twice its forecast is not read.
- The three strongest:
  - PJM's actual peak hour ran 5.7 percent above the forecast its filing of five years before made for 2025, against 8.7 percent below in 2019.
  - ISO New England's actual peak ran 7.6 percent below its five-year-old forecast in 2025, against 19.7 percent below in 2019.
  - PJM's actual yearly demand ran 6.1 percent above its five-year-old forecast in 2025, against 9.5 percent below in 2019.
- Every cross_family draft reproduces (17 of 17, chain 164's included); 9 of 9 new do-files hold.

## Code

- `warehouse/analysis/findings/deep/cross502.py` on `wip/8202-findings` (`91827ba93`).

## Needs the key

- Nothing.
