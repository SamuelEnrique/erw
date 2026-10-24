# Session 2378 report: Canada's petroleum products by supply and disposition, a month (Statistics Canada, table 25-10-0081-01), the second own choice

24 October 2026, from 09:04 UTC, on lab-desktop (the data machine), the eighth session of `queue/done/112-day-13-november-data-sri-lanka-nigeria-ghana-jordan.md`, unattended. Precheck passed (`runs/c112/pre2378.out`). Model spend USD 0. Pulls: 2 of 20 to Statistics Canada, 7 to EIA's API (below).

## Read these first

- **EIA routes read first and left** (7 requests):
  - lease condensate ends in 2021, coalbed methane in 2019;
  - the residential and commercial price route gives the same series as the held `eia_gas_prices_state_monthly` (PRS and PCS by state);
  - the electricity routes not held are a state rankings summary (derivable) and the generator inventory (held through EIA-860M);
  - wellhead value and marketed production repeat the held production summary.
- **One public table:** `statcan_petroleum_products_monthly`, from Statistics Canada's table 25-10-0081-01, "Petroleum products by supply and disposition, monthly". It is written, validated, archived, in coverage (sector oil and products), and held from the live set and the release. 112,385 rows, 406 series, January 2019 to July 2026:
  - for Canada and each province and territory;
  - for 31 products, from natural gas liquids and their parts to gasoline, jet fuel, distillate, residual fuel, petroleum coke and asphalt;
  - eleven supply and disposition items: field, renewable and refinery production, imports, inter-regional receipts, adjustments, stock change, refinery inputs, exports, products supplied, ending stocks.
  - In m3, as StatCan publishes them (Decision 70's unit).
  - Each product carries its parent, and a product with parts is marked `x_total`.
  - 25,400 cells StatCan suppresses for confidentiality ("x") and 626 not available ("..") have no row.
- **Why this one:** the ERW holds StatCan's crude oil and gas supply (`statcan_oil_gas_supply_monthly`) and electricity tables, but not the refined products. Canada is the largest supplier of the United States' imported products.
- **License:** Statistics Canada's Open Licence, on record (public). The robots file asks a crawl delay of 2 seconds (kept) and names no AI agent (read 619).

## The cross-check (`runs/c112/s2378/cross.py`, `cross.out`; read past its header lines)

- **Parts against their product,** where every part is given:
  - natural gas liquids' four parts in 2,165 of 2,165 cells within 1 m3;
  - renewable fuels' two in 5,253 of 5,271 (5,262 within 0.5 per cent);
  - finished petroleum products' fourteen in 2,390 of 2,390.
- **The provinces against Canada** for finished products, where none is suppressed: 182 of 182 cells within 0.5 per cent.
- **Canada's finished motor gasoline supplied:** 43.18 million m3 (2019), 37.26 (2020), 43.19 (2025).

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www150.statcan.gc.ca | 2 of 20 | robots, the table's zip (1.65 MB); 3 s apart |
| api.eia.gov | 7 | four routes' metadata, a sample, two route lists |

## Errors

- **The docstring first named the held crude table wrongly** (`statcan_crude_supply_monthly`); corrected to `statcan_oil_gas_supply_monthly` before the write.

## Decisions made without you

- **StatCan's petroleum products chosen** after the EIA routes above proved stale or held.
- **Cubic metres kept,** StatCan's own unit.

## For Samuel's ruling

- None new.

## Files

- New:
  - `warehouse/connectors/statcan_petroleum_products.py`
  - `tests/test_session2378.py`
  - this report
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`
  - `warehouse/metadata/license_reads.csv` (619), `license_tables.csv`, `docs/licenses.md`
  - `docs/redivis/release-v1/`
  - the coverage, sources and archive manifest files
- On the data machine only: `runs/c112/s2378/`, `runs/license_reads/s2378/`.
