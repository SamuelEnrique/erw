# Session 3939 report: FRED's series from their primary sources

Energy Research Warehouse (ERW). Chain 267, data machine (lab-desktop), 14 November 2026, 10:43 to 10:47 UTC. Opus 5.5. Model spend USD 0. Requests: the IMF's data service 2 (the trial's data call, then the dataflow's structure), and the connector's own 1 under the lock; `runs/c267/s3939/probe.csv`.

`docs/state/data_requests_licenses.md`, the FRED section:

- **Rows 2 to 7** (WTI, Brent, Henry Hub from EIA; the 2-, 10- and 30-year Treasury yields from the Federal Reserve's H.15; nickel and uranium from the IMF): already covered.
- **Rows 8 to 10, done:** `imf_pcps.py` adds `PCOALAU`, `PNGASEU` and `PNGASJP` to the one request it makes. Names and units from the IMF's own structure (dataflow IMF.RES/PCPS, read this session): "Coal, Australia, US dollars per metric tonne", "Natural gas, EU, US dollars per million metric British thermal units of gas", "LNG, Asia, US dollars per million metric British thermal units of gas". The data answer itself carries no unit.
  - Written under the data lock: `imf_commodity_prices` 752 rows (eight series, 94 months each, January 2019 to October 2026), validated, archived, in coverage.
  - Test 132's fixture check kept to its five; with tests 207, 247 and 321: 77 passed.
  - The board reads a fixed list of five, so no page changes. The table is held from the live catalogue: no load.
  - The IMF's terms are unchanged (public with attribution; commercial reuse and bulk automated download need permission). The pull is still one request.
- **Rows 11 and 12 (BLS's CPI and PPI indexes): stopped.** Neither EIA nor the Federal Reserve publishes them. www.bls.gov refuses this reader (HTTP 403, read 1710), and the registered BLS API needs a key the repository does not hold (`.env` has none).

## Decisions made without you

- **The IMF's own names are the `node` words,** not FRED's ("Coal, Australia", not "Australian thermal coal").

## For Samuel's ruling

- **A BLS API key** (free registration) would let the CPI electricity and utility gas indexes and the four PPI series be read from BLS itself. Default: not read; FRED's copies stay retired.
