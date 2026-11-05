# Large loads' filed tariffs (`utility_large_load_tariffs`)

Energy Research Warehouse (ERW). Started by session 2871 (chain 147, 5 November 2026). The table records what a load
of 100 MW to 1 GW pays a utility to connect and take delivery, figure by figure, from the tariffs the utilities file
with their state commissions. Nobody publishes this in one table. The All grids tab of `/cost-of-power` reads it
through `site/data/siting/tariffs.json` (`warehouse/derived/siting_page.py`, `tariffs_file`, written by session 730
against this shape and not yet wired).

## What a row is

One figure that one schedule prints: the smallest load it takes, a demand charge, an energy charge, a fixed charge,
the shortest contract term, a minimum bill as a share, collateral or an exit fee stated in months. The row keys on the
schedule (`filed:<EIA utility id>:<schedule>`), the figure (`variable`) and the schedule's effective date (`ts_utc`).

## What is not done

- **Nothing is derived.** No all-in price, no sum of a schedule's demand charges, no estimate. Each value is the
  printed figure in the table's unit, converted only between units (cents to dollars, kWh to MWh, kW to MW). The
  printed words are kept beside it in `x_printed`, with the page in `x_page` and the document in `source_url`.
- **A figure the schedule does not print has no row.** A minimum bill stated in words, not as a share, stays in
  `x_min_bill` and gets no `min_bill_pct` row. The same goes for collateral, exit fees, ramp provisions and terms.
- **Riders are not added.** Fuel, transmission cost recovery and other riders change often and are filed apart from
  the schedule. A schedule's own charges are recorded; a rider is named in `x_term` when the schedule names it.

## The registry

`warehouse/sources/large_load_tariffs/` holds one YAML file a schedule (its README has the form). A session reads the
filed tariff after the host's robots file and terms, and writes each figure with its page and words. The connector
`warehouse/connectors/large_load_tariffs.py` makes no request. It checks every file (each figure has a page and its
words, units are from the list, the license is public, dates are well formed) and refuses the whole write if any file
fails. The validator refuses a row without `source_url`, or a filed row without `x_page` (check `filing_cited`).

## License

Public, row by row. A filed tariff is a public regulatory record, and each row cites the commission's copy. A utility
site whose terms bar the reader is not read; the commission's docket copy is.

## The OpenEI rows

`warehouse/connectors/openei_large_load_tariffs.py` (session 670) writes the same table from OpenEI's Utility Rate
Database, under entities `openei_urdb:*`, with derived figures (an hour-weighted energy charge, an all-in figure). It
has never run: no key is held. If it runs, its rows and these merge by key and neither overwrites the other's. The
tab's builder reads both kinds; the method of each row is its source's.

## Cross-checks

Each session that adds utilities checks one utility's demand charge against the revenue per kW that EIA-861 implies
for its largest class. The result is written as a check in the session's report, never as a correction to a row.
