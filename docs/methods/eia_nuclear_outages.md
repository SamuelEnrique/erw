# EIA's status of U.S. nuclear outages: the fleet, each plant and each reactor, a day

Energy Research Warehouse (ERW), method note written in session 675 (chain 043) for tables first written on 21 or 22 October 2026.

Tables: `eia_nuclear_outages_daily`, `eia_nuclear_outages_facility_daily`, `eia_nuclear_outages_generator_daily`

Connectors: `warehouse/connectors/eia_nuclear_outages.py` (session 513, the U.S. fleet), `warehouse/connectors/eia_nuclear_outages_facility.py` (session 516, by plant; two windows since session 523) and `warehouse/connectors/eia_nuclear_outages_generator.py` (sessions 548 and 549, by reactor).

## Publisher and report

U.S. Energy Information Administration (EIA), Status of U.S. Nuclear Outages, read through EIA's API v2. The report's page is `https://www.eia.gov/nuclear/outages/`. The three routes:

- `https://api.eia.gov/v2/nuclear-outages/us-nuclear-outages/data/?frequency=daily&data[]=capacity&data[]=outage&data[]=percentOutage&start=2007-01-01` (source code `eia:nuclear-outages/us-nuclear-outages`);
- `https://api.eia.gov/v2/nuclear-outages/facility-nuclear-outages/data/?frequency=daily&data[]=capacity&data[]=outage&data[]=percentOutage&start=<first day>[&end=<last day>]` (source code `eia:nuclear-outages/facility-nuclear-outages`);
- `https://api.eia.gov/v2/nuclear-outages/generator-nuclear-outages/data/?...` with the same parameters (source code `eia:nuclear-outages/generator-nuclear-outages`).

EIA estimates the outages from the Nuclear Regulatory Commission's daily power reactor status reports: each reactor's percent of full power, set against its capacity. The figures are EIA's as it publishes them. Pages hold 5,000 records, 3 seconds apart; a 429 or a 5xx is asked once more after 60 seconds. The key is read from `EIA_API_KEY` and redacted in every `source_url`.

## Vintage and revision rule

- All three tables cover 2007-01-01 to 2026-10-21, retrieved on 21 October 2026.
- The plant and reactor tables are read in two windows, 2007-01-01 to 2014-12-31 and 2015-01-01 to the newest day. `--from` and `--to` read one window instead.
- Every table is written with `ip.write_snapshot`: a run replaces the whole table, so a day EIA revises is replaced at the next run.
- Ceilings: 4 requests a run for the U.S. table (a saved page is reused only with `--offline`), 98 for each of the other two (about 50 to 60 pages a window; a page saved in `warehouse/raw` is reused unless `--fresh`; `--offline` asks nothing).

## Shape and columns

Series shape: `entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage`. `ts_utc` the day at 00:00:00Z; `freq` `P1D`; `geo` `US`; `market` and `vintage` empty.

Variables, the same in all three tables:

- `capacity` (`MW`): the capacity EIA counts for the day;
- `outage` (`MW`): the capacity out of service;
- `outage_share` (`ratio`): EIA's `percentOutage` divided by 100.

Entities:

- `eia_nuclear_outages_daily`: one entity, `eia_nuclear_outages:US`, node "U.S. nuclear fleet". 21,702 rows.
- `eia_nuclear_outages_facility_daily`: `eia_nuclear_outages:<facility>`, EIA's plant id (for example `eia_nuclear_outages:46`, Browns Ferry); node the plant's name. 66 plants, 1,312,872 rows.
- `eia_nuclear_outages_generator_daily`: `eia_nuclear_outages_gen:<facility>:<generator>`, EIA's plant and reactor ids (for example `eia_nuclear_outages_gen:46:1`); node the plant's name and the reactor, as "Browns Ferry, reactor 1". 107 reactors, 2,141,406 rows.

## License

ERW verdict: public, for all three. Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Status of U.S. Nuclear Outages")."

## Cross-check

None in the connectors. They check their own reading: the U.S. table's rows read must equal EIA's `total`; the plant and reactor tables read until a page comes back short, check that the pages run in day order, and stop if any day between the first and the last has no row. A unit outside the map (megawatts, percent) or a key given twice stops a run. The plant connector's comment says the per-day sums were checked against EIA's U.S. total in session 516's report; that check is not in the code.

## What it does not hold

- A blank has no row and nothing is filled. For the plant and reactor routes, EIA's `total` counts more rows than the data hold: on 21 October 2026 it counted 413,039 from 2015 on while the pages ended at 247,167, and for one day it counted 95 plants and returned 55, the plants whose figures are blank being left out of the data.
- No reason for an outage (refuelling, maintenance or forced) and no reactor status text: capacity and outage only.
- No day before 2007.
- These are EIA's estimates from the NRC's reports, not metered output.
