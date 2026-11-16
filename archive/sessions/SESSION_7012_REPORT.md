# Session 7012 report: where power is cheap, its replication and one fault (the done line's tool 19); gates c and d

Energy Research Warehouse (ERW). Chain 301, data machine (lab-desktop), 16 November 2026. Opus 5.5. Model spend USD 0.

## What was built

- **`replication/compare/replicate.py`**: every figure of `site/data/price_compare.json` recomputed from the hub and zone price tables by `docs/methods/hub_price_comparison.md` alone: 578 of 578 equal after its finding (commit `bfaecee94`).
- **Its finding** (`docs/reviews/price-compare-faults-2026-11-16.md` row 1): an hour whose four 15-minute prices sum to exactly zero was counted as below zero, or not, by the float sum's noise (ERCOT Houston, real time: 1.63 percent, 143 hours). `price_compare.hourly` now rounds an hour's mean to 9 places before any comparison (test 7012); the table and the file rebuilt: 1.62 percent, 142 hours. Row 2 (the windows end in September) is not a fault.
- **`replication/compare/replicate.do`**: five figures of ERCOT's twelve months in Stata (not run).

## Gates

- **Gate c** (the desk's rows and this chain's work) failed on tests 5161 and 7202 (twice). Both fixed in `bfaecee94`: test 5161 lists the large-load rules file the browser is handed; test 7202 closes the status files it reads (its ResourceWarning was the output's last line).
- **Gate d** (`844d2a169`, everything to session 7012) failed on one test, `test_session726` (the PJM row's utility, which data request 23 removed on purpose). Fixed in session 7009's commit `dc10d960f` on `wip/c301-more`; gated again as gate e.

## For Samuel's ruling

- None new.
