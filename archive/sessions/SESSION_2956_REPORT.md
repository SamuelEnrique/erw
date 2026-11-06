# Session 2956 report: the weekly gas balance

6 November 2026, about 08:27 to 08:29 UTC, on lab-desktop (the data machine), chain 157 (the owner's), unattended. Model spend USD 0. Pulls: none.

## Read these first

- **`gas_balance_weekly` is written:** 40,507 rows (38,584 weekly, 1,923 monthly), public, commit `b850ed84c`.
  - **Weekly, by EIA's storage region:** working gas, the week's change (against the week exactly 7 days before), and the five-year minimum, maximum and average of the same ISO week, with the position in that range. 2010 to 16 October 2026.
  - **Monthly, the US:** dry production, imports, consumption, power burn, exports, LNG exports, the implied balance, and the LNG and power shares, to July 2026.
  - **Not held, so not derived:** weekly production, demand and LNG feedgas. A week has no implied balance of its own; the method note says so.
  - **Checks:** the five regions sum to the Lower 48 within 2 Bcf on all 877 weeks. The newest week, 16 October, is 3,644 Bcf: +77 on the week, 1.0 Bcf below the five-year average, at 61.9 percent of the five-year range.
  - **July 2026:** LNG exports were 14.7 percent of dry production, and power burn 55.2 percent of consumption.
- **The write:** validator PASS, coverage (sector gas), archive run `20261106T082840Z-local`. Method note `docs/methods/gas_balance_weekly.md`; test `tests/test_session2956.py`. Its first run failed on my own expected figures, which were corrected, not the code.
- **Keyed for the price board's gas group and the Digest's physical row:** the keys are listed by session 2957. Nothing is wired here.

## Decisions made without you

- **The table keeps its name, `gas_balance_weekly`,** though its balance is monthly: the weekly storage is its core, and the method says which part is which.

## For Samuel's ruling

- **Whether EIA's weekly supply and demand estimates should be pulled** (the Natural Gas Weekly Update's balance), so that a week gets its own balance.
