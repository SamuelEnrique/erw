# Session 2064 report: the reactors' licenses and uprates (the NRC's lists)

23 October 2026, from 20:34 UTC, on lab-desktop (the data machine), a session of `queue/done/066-day-25-october-data-disasters-loans-drought-assistance.md`. Model spend USD 0. Pulls: 5 requests of 15 (www.nrc.gov's robots file, asked in a call of its own: for every reader it disallows only its search and two files; the license renewal and approved uprate pages, read by the probe; the same two through the connector's trial). The write reused the saved pages (`--offline`). The NRC's verdict (read 16, public) was read before.

## Read these first

- **One table written, validated, archived, in coverage (sectors power and uranium), in the release package, both holds:** `nrc_license_actions`, 236 events:
  - **64 renewed licenses** (the NRC's completed initial renewals, March 2000 to April 2026): each plant and units as the NRC writes them, the application's receipt, the renewed license's issue date (`event_date`), and the dates its units enter extended operation; Crystal River 3's application, withdrawn in 2013, is a row with status `withdrawn`, dated its receipt. The page's footnote marks (shut-down plants, Crystal River, Diablo Canyon's earlier application) are split from the cells and each row's notes kept in `x_note`.
  - **172 approved power uprates** (September 1977 to November 2021): plant, percent, MW thermal (`x_uprate_mwt`; `mw` is left empty, since these are not electric megawatts), type (73 measurement uncertainty recaptures, 65 stretch, 34 extended) and approval date.
- **The subsequent renewals are not taken:** the page lists them only as links (16 mentions), not in a table. A row's link cannot tell one kind from the other: Cooper's row (renewed 2010) links to Cooper's later subsequent application.

## The cross-check

- **The uprates' rows add to 24,146.2 MWt; the page's own total row prints 24,089** (and 8,030 MWe). No single row accounts for the 57.2 MWt; the header says both, and the table holds the rows as printed.
- **Plants against the ERW's reactor list** (`nrc_power_reactors`, 130 units), by name, `runs/c066/s2064/cross.py`: 54 of 64 renewals and 157 of 172 uprates match; the others are the NRC's other spellings of the same plants (ANO-2, TMI-1, WNP-2, H.B. Robinson, V.C. Summer, St. Lucie, LaSalle), not plants missing from the list.

## Errors

- **The first trial stopped on Crystal River 3's "****"**, a footnote mark in place of a date; the marks are now split off and read from the page's notes, and a row without an issue date must have a note saying the application was withdrawn.
- **Diablo Canyon's issue date is written with a four-digit year** (04/02/2026): both forms are read.
- **The first rule for subsequent renewals came from the rows' links,** which put Cooper's 2010 renewal among them; dropped (above).
- **The uprates' total check first stopped the run;** the publisher's total disagrees with its rows, so both are said instead.

## Decisions made without you

- **Initial renewals and approved uprates only;** the planned, pending and subsequent renewals and the expected uprates not taken.
- **Crystal River's withdrawn application kept as a row,** dated its receipt.
- **MW thermal kept in an `x_` column;** no conversion to electric megawatts.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/nrc_license_actions.py`, `tests/test_session2064.py` (4 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c066/s2064/`, `runs/license_reads/s2064/`, `runs/s2064*`, `warehouse/raw/nrc_license_actions/`.
