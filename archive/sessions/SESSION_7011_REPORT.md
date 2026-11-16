# Session 7011 report: the prices page's replication (the done line's tool 18)

Energy Research Warehouse (ERW). Chain 301, data machine (lab-desktop), 16 November 2026. Opus 5.5. Model spend USD 0.

## What was built

- **`replication/prices/replicate.py`**: `/prices` draws its prices from the live set at render time (the anon key); the script reads the same rows the same way and compares each with the warehouse's own tables: 74,258 of 74,258 live prices equal (commit `78f2de474`). It needs `SUPABASE_URL` (its origin) and `SUPABASE_ANON_KEY`; in a worktree, `.env` is read from the main checkout.
- **`replication/prices/replicate.do`**: five prices in Stata, expected values at its top (not run).
- The method notes `docs/methods/power_prices.md` and the price page's note name the replication.

## Faults found

- None.

## Landing

- In gate e, landed at `f4cc50518`.

## For Samuel's ruling

- None new.
