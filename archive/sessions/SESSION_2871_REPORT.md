# Session 2871 report: the large-load tariff registry, its shape

5 November 2026, about 21:30 to 21:40 UTC, on lab-desktop (the data machine), chain 147, unattended, done while session 2863's gate ran. Model spend USD 0. Pulls: none.

## Read these first

- **`utility_large_load_tariffs` is shaped to the name and columns the tab's builder already reads.** `siting_page.tariffs_file` (session 730, "written and tested, not wired") needs entity, variable, ts_utc, value, `x_eia_id`, `x_utility` and `x_sector`, and the variables energy_charge, demand_charge, fixed_charge and min_demand_mw. `tests/test_session2871.py` runs `tariffs_file` on the connector's own rows. It wires without a rename.
- **The registry:** `warehouse/sources/large_load_tariffs/<utility>_<schedule>.yaml`, one file a schedule. Each figure carries its value in the table's unit, its printed words (`x_printed`) and its page (`x_page`). The schedule's terms are in its own words: minimum bill, collateral, exit fee, ramp, term. The form is in the folder's README.
- **The connector** `warehouse/connectors/large_load_tariffs.py` makes no request. It refuses the whole write when any file lacks a page or the printed words for a figure, uses a variable outside its list, gives a malformed date, or a license other than public. A schedule printing a demand charge and its parts together is also refused.
- **The validator's `filing_cited` check:** a row of this table without `source_url`, or a `filed:` row without `x_page`, is an error. Decision 75 in `docs/datastandard.md`. No unit was added: USD/kW-month, USD/MWh, USD, MW, year, pct and month are all in the vocabulary.
- **`docs/methods/large_load_tariffs.md`** is started: what a row is, what is not done (nothing derived, no riders), the registry, the license, the OpenEI rows (session 670's connector, never run, writes the same table under `openei_urdb:*`), and the cross-checks.
- **Tests:** `tests/test_session2871.py`, 12 tests (with session 730's and 670's: 18 OK).

## Decisions made without you

- **A value is the printed figure converted only between units** (cents to dollars, kWh to MWh), with the printed words kept beside it. That is how a figure is "as the schedule prints it" and still wires to the tab's USD/MWh and USD/kW-month.
- **The same table name as OpenEI's connector,** with its own entities (`filed:`), so the two merge and never overwrite each other.

## Files

- On `wip/c147-data`: `warehouse/connectors/large_load_tariffs.py`, `warehouse/sources/large_load_tariffs/README.md`, `docs/methods/large_load_tariffs.md`, `warehouse/validate/erw_validate.py`, `docs/datastandard.md`, `tests/test_session2871.py`.
