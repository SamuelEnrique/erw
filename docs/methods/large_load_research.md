# The large-load research pass as tables (session 3937)

Energy Research Warehouse (ERW). Three events tables from the research pass that window P4 of the portable laptop made on 13 and 14 November 2026 (sessions 5300 to 5304), loaded by the data machine (chain 267) as `docs/state/data_requests_large_load.md` rows 1, 15 and 16 ask. The research's own method, its hosts' terms and its audit are in `docs/research/large_load/README.md`, `spotcheck_2026-11-13.md` and `audit_2026-11-14.md`.

## The tables

| Table | One row | Rows written | Held for a license |
|---|---|---:|---:|
| `utility_large_load_rules` | a utility's (or a state commission's) large-load rule | 100 | 22 |
| `utility_large_load_rule_changes` | a filing, order, effective date, amendment, denial, suspension or hearing, 15 August to 13 November 2026 | 94 | 4 |
| `state_large_load_laws` | a state law or bill of the 2025 and 2026 sessions | 27 | 1 |

Connector: `warehouse/connectors/large_load_research.py`. It reads the three files as committed (`utilities_2026-11-13.csv`, `changes_2026-11-13.csv`, `legislation_2026-11-13.csv`), makes no request and no model call, and refuses the whole write when a row lacks what it must hold (a unique id, a license of `public` or `internal`, an http source, a read date, a rule status of the six, a change date).

## What a row rests on

- **Every value is printed in a document,** and the row's cite columns hold the page or section and the words. The pass matched every cite in its document by code (1,699 for the rules, 364 for the changes, 295 for the laws) and five auditors read all 122 rules rows (21 values corrected).
- **The ISO or region column** (`x_iso_region`) is the ERW's classification, not a cited value.
- **`not published`** means the documents read do not state the value; it is written as printed.
- **`held: <registry>/<file>`** points to the ERW's own registry (`warehouse/sources/large_load_tariffs/`, `large_load_connection_rules/`), which holds the same value: the cell is left empty and the pointer kept in `x_held`.
- **`mw` is empty:** every size the files hold is a phrase ("50 MW of new or incremental load with a load factor of 85 percent or higher"), kept in `x_threshold_mw`.
- **Dates:** `event_date` is the status date (rules, laws) or the change's date where the documents print a day; seven changes print a month only, kept as printed in `x_date`, and those rows and the laws whose status date is not published are dated by the day the document was read (`x_date_kind`).

## The license, row by row

- **Public rows only are written** (the files' `license` column; the owner's ruling 4 of 6 November 2026: a commission's copy, a filed tariff book, an SEC filing, a grid operator's posted document or a legislature's own text is a public record). A table has one license, so a row whose only source asks written permission or allows personal use only is held, not written, and named in the table's header, as `utility_large_load_tariffs` holds its schedules.
- **In a public rules row,** the fields `internal_fields` names (those resting only on such a host) are left empty with their cites, and `x_withheld` names them (2 rows).
- **The ERW verdict is unsettled,** as for the registry tables (`large_load_connection_rules`, `utility_large_load_tariffs`): the publisher is many hosts, each row's own. So the tables are public in the warehouse and the package, and out of release v1.

## Not done here

- **Request row 17** (window A's operator documents that changed) and **rows 2 to 14** (changes to registry files) are edits of the registry, each its own session.
- **Texas S.B. 6** is withheld by the research itself (its copy sits on a path capitol.texas.gov's robots file disallows) and is not in the laws file.
