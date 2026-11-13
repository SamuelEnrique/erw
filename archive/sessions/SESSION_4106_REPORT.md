# Session 4106 report: FRED's series and their primary sources

Energy Research Warehouse (ERW). Chain 229, session 7 of 50, lab-desktop third window, 13 November 2026 10:52 to 11:00 UTC. Opus 5.5. Model spend USD 0. Branch `wip/4100-licenses`.

## FRED, series by series (`docs/state/data_requests_licenses.md`, rows 2 to 12)

- **Why:** FRED's terms (read 12) forbid storing its content without the Bank's consent. The ERW's four FRED tables are already retired (`warehouse/output/retired/`).
- **Already read from the primary source (6 rows, nothing to do):**
  - WTI, Brent and Henry Hub from EIA (RWTC, RBRTE, RNGWHHD) in `eia_fuel_spot_prices`;
  - the 2-, 10- and 30-year Treasury yields from the Board's H.15 (RIFLGFCY02_N.B, RIFLGFCY10_N.B, RIFLGFCY30_N.B, checked against the connector) in `frb_treasury_yields`;
  - nickel and uranium from the IMF's PCPS (PNICK, PURAN) in `imf_commodity_prices`.
- **Requested of window A (5 rows):**
  - three IMF codes (PCOALAU, PNGASEU, PNGASJP) added to `imf_pcps.py`'s `SERIES`;
  - the seven BLS price indexes (3 CPI, 4 PPI) by a BLS connector on the registered API. Neither EIA nor the Board publishes these indexes; BLS is their primary publisher.

## Read

- **BLS:** www.bls.gov answered HTTP 403 even to its robots file (read 1710), so no BLS page was asked. The request says the registered API is the route.

## Decisions made without you

- **The BLS indexes name BLS as their primary source,** not EIA or the Federal Reserve: neither publishes them. Naming a near substitute (EIA's average retail prices) would change what the series measure.
- **No data was written:** the rows are requests, and window A holds the data lock.

## For Samuel's ruling

- **The BLS connector:** a new table, needing a key and a public verdict from BLS's own terms (unread: 403). **Default: requested, not built** by this chain.
