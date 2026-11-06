# U.S. crude oil field production by state, region and federal offshore area, a month

Energy Research Warehouse (ERW), method note written in session 677 (chain 043) for tables first written on 21 or 22 October 2026.

Tables: `eia_crude_production_state_monthly`

Connector: `warehouse/connectors/eia_crude_production_state.py` (session 527).

## Publisher and report

U.S. Energy Information Administration (EIA), Petroleum Supply Monthly, crude oil field production, read through EIA's API v2, route `petroleum/crd/crpdn`. The report's page is `https://www.eia.gov/petroleum/supply/monthly/`. The connector asks:

`https://api.eia.gov/v2/petroleum/crd/crpdn/data/?frequency=monthly&data[]=value&facets[process][]=FPF&start=2001-01`

in pages of 5,000 records, sorted by period and series, 3 seconds apart. The key is read from `EIA_API_KEY` and is redacted in every `source_url`.

## Vintage and revision rule

The header gives months 2001-01 to 2026-07: 25,644 records of EIA's, 25,644 with a value. Idaho's two series begin in 2007-01; every other series begins in 2001-01. `--from YYYY-MM` sets the first month (default `2001-01`).

The table is written with `ip.write_snapshot`: each run replaces the whole table with what the run read. A page an earlier run saved in `warehouse/raw/eia_crude_production_state/` is reused unless `--fresh`; `--offline` asks nothing. A revised figure at EIA reaches the table only through a page asked again. Ceiling: 20 requests a run. A read shorter than EIA's count stops the run.

## Shape

Series. One row per area, series and month.

- `entity`: `eia_crude_production:<area>:<series stem>`. The area is EIA's code: `S<state>` for a state, `NUS` for the U.S., `R10` to `R50` for the PADDs, `R3FM` the Federal Offshore Gulf of America, `R5F` the Federal Offshore Pacific, `RAKS` Alaska's south. The stem is EIA's series code less its unit digit, for example `eia_crude_production:SAK:MANFPAK`. Alaska holds two entities, the state (`MCRFPAK`) and its North Slope (`MANFPAK`), within it. Idaho's EIA series ids do not end in a unit digit, so Idaho holds two entities, `M_EPC0_FPF_SID_MBB` (the monthly volume) and `M_EPC0_FPF_SID_MBBL` (per day). 43 entities over 41 areas.
- `variable`: `field_production`, unit `kbbl` (EIA's thousand barrels in the month), and `field_production_per_day`, unit `kbbl/d` (thousand barrels a day). 12,822 rows of each.
- `ts_utc`: the month's first day at 00:00:00Z; `freq` `P1M`; `geo` `US-<state>` for a state, `US` for the U.S., the PADDs and the offshore areas; `market` empty.
- `node`: EIA's series name.
- `source`, `source_url`, `retrieved_at`; `vintage` empty.

A region is a sum of states and offshore areas: a sum over areas must take one level.

## License

ERW verdict: public (`docs/licenses.md`). Header: License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Petroleum Supply Monthly").

## Cross-check

None in the connector. It stops on a unit, process or area not in its map, on a key given twice, and on a read shorter than EIA's count.

## What it does not hold

- A figure EIA withholds has no row; nothing is filled.
- Only the field production process (`FPF`); no other crude oil supply process of the route.
- Months before 2001-01, unless a run is asked with an earlier `--from`.
