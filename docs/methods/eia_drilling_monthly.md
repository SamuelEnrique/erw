# U.S. drilling activity: rotary rigs and well service rigs in operation, a month

Energy Research Warehouse (ERW), method note written in session 677 (chain 043) for tables first written on 21 or 22 October 2026.

Tables: `eia_drilling_monthly`

Connector: `warehouse/connectors/eia_drilling.py` (session 603).

## Publisher and report

U.S. Energy Information Administration (EIA), crude oil and natural gas drilling activity, read through EIA's API v2, route `petroleum/crd/drill`. The report's page is `https://www.eia.gov/dnav/pet/pet_crd_drill_s1_m.htm`. The connector asks:

`https://api.eia.gov/v2/petroleum/crd/drill/data/?frequency=monthly&data[]=value&facets[process][]=XR0&facets[process][]=XRS&start=1973-01`

in pages of 5,000 records sorted by period and series, 3 seconds apart. The key is read from `EIA_API_KEY` and is redacted in every `source_url`.

## Vintage and revision rule

The header gives months 1973-01 to 2026-02: 3,828 records of EIA's, 3,431 rows. `--from YYYY-MM` sets the first month (default `1973-01`).

The table is written with `ip.write_snapshot`: each run replaces the whole table. A page an earlier run saved in `warehouse/raw/eia_drilling/` is reused unless `--fresh`; `--offline` asks nothing. A revised figure at EIA reaches the table only through a page asked again. Ceiling: 9 requests a run. A read shorter than EIA's count stops the run.

## Shape

Series. Six entities, one per EIA series.

- `entity`: `eia_drilling:<series>`, EIA's series id (one a process, kind and area):
  - `E_ERTRR0_XR0_NUS_C`, `E_ERTRR0_XR0_RUSON_C`, `E_ERTRR0_XR0_RUSOF_C`: crude oil and natural gas rotary rigs, the U.S., onshore and offshore, 1973-01 to 2026-02;
  - `E_ERTRRO_XR0_NUS_C` and `E_ERTRRG_XR0_NUS_C`: crude oil rotary rigs and natural gas rotary rigs, the U.S., 1987-08 to 2026-02;
  - `E_ERTS0_XRS_NUS_C`: active well service rigs, the U.S., 1973-01 to 2022-03.
- `variable`: `rotary_rigs` (process XR0, 2,840 rows) or `service_rigs` (process XRS, 591 rows), unit `count`.
- `ts_utc`: the month's first day at 00:00:00Z; `freq` `P1M`; `geo` `US`; `market` empty.
- `node`: EIA's series name.
- `source`, `source_url`, `retrieved_at`; `vintage` empty.

Areas NUS, RUSON (onshore) and RUSOF (offshore), and the oil and gas rigs within the total: a sum takes one level.

## License

ERW verdict: public (`docs/licenses.md`). Header: License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, crude oil and natural gas drilling activity").

## Cross-check

None in the connector. It stops on a unit, process or area not in its map, on a key given twice, and on a read shorter than EIA's count.

## What it does not hold

- A blank has no row; nothing is filled (3,828 records against 3,431 rows).
- Service rigs after 2022-03, and oil and gas rigs apart before 1987-08: EIA's series end or begin there in the table.
- Rigs by state or basin: the connector's map holds only the U.S., onshore and offshore areas, and an area outside it would stop the run.
