# U.S. crude oil imports by country of origin, destination and grade, a month

Energy Research Warehouse (ERW), method note written in session 677 (chain 043) for tables first written on 21 or 22 October 2026.

Tables: `eia_crude_imports_detail_monthly`

Connector: `warehouse/connectors/eia_crude_imports_detail.py` (session 632, finished in session 636).

## Publisher and report

U.S. Energy Information Administration (EIA), Company Level Imports, crude oil imports by country to destination (Form EIA-814), read through EIA's API v2, route `crude-oil-imports`. The report's page is `https://www.eia.gov/petroleum/imports/companylevel/`. The connector asks:

`https://api.eia.gov/v2/crude-oil-imports/data/?frequency=monthly&data[]=quantity&facets[originType][]=CTY&start=2011-01`

in pages of 5,000 records, sorted by period, origin, destination and grade, 3 seconds apart. The key is read from `EIA_API_KEY` and is redacted in every `source_url`.

## Vintage and revision rule

The header gives months 2009-01 to 2026-07, every month there, and records the access as `start=2009-01` "(to 2010-12, then from 2011-01)": the rows of 2009 and 2010 carry a `source_url` ending `end=2010-12`. Session 636 had left 2009 and 2010 (about 22,000 records) for an early window of its own, which chain 041's queue file names. The connector as it stands takes `--from` (default `2011-01`) and no end month, so a run with its default writes a table from 2011-01 only.

The table is written with `ip.write_snapshot`: each run replaces the whole table, and the header says the previous file held 154,779 rows. A page an earlier run saved in `warehouse/raw/eia_crude_imports_detail/` is reused unless `--fresh`; `--offline` asks nothing. A revised figure at EIA therefore reaches the table only through a page asked again. Ceiling: 19 requests a run.

EIA's count is larger than its pages hold (the header: EIA counts 191,815 records and its pages hold 183,393). The connector takes a short read only when every month from the first to the last has rows; a missing month stops the run.

## Shape

Series. One row per origin, destination, grade and month.

- `entity`: `eia_crude_imports:<originId>:<destinationId>:<gradeId>`, EIA's own ids, for example `eia_crude_imports:CTY_AE:PP_5:LSO`. Origins are countries (`CTY_` and a code; 61 in the table). Destinations are the U.S., a port PADD (`PP_`), a port state (`PS_`), a port (`PT_`), a refinery PADD, a refinery state or a refinery (513 in the table). Grades are `LSW`, `LSO`, `MED`, `HSW`, `HSO` (light sweet, light sour, medium, heavy sweet, heavy sour).
- `variable`: `imports`, unit `kbbl` (EIA's thousand barrels in the month, factor 1).
- `ts_utc`: the month's first day at 00:00:00Z; `freq` `P1M`; `geo` `US`; `market` empty.
- `node`: "<origin> to <destination> (<destination type>), <grade>" in EIA's names.
- `source`, `source_url`, `retrieved_at`; `vintage` empty.

The destinations nest (a refinery within its state and PADD, a port within its state and PADD, all within the U.S.): a sum takes one destination type.

## License

ERW verdict: public (`docs/licenses.md`). Header: License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Company Level Imports").

## Cross-check

None in the connector against another table. It checks its own completeness: every month from the first to the last must be present, a unit, origin type, destination type or grade not in its map stops the run, and so does a key given twice. Session 636's report compared the table with `eia_crude_imports_by_country` (all countries against the U.S. total, Saudi Arabia, Canada; median ratio 1.000 in each) outside the connector.

## What it does not hold

- EIA's region, OPEC and world origins: they are sums of the countries and are not taken.
- A blank has no row; nothing is filled.
- The records EIA counts beyond those its pages hold.
- Fields the vocabulary cannot hold, such as API gravity and sulfur, beyond the grade itself.
