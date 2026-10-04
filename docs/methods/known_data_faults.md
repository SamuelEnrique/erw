# Known faults in source data

The table `known_data_faults` and the page `/data/faults` list every fault an ERW session has found in a publisher's
data: values that are wrong, missing, shifted in time or impossible. Session 103.

## What a fault is here

Something the publisher's data holds, not something the ERW did. In: EIA's California generation changing in one hour;
hours stamped one hour late; a fuel blank for ten months; hours of demand that did not happen; a day's interchange
larger than a grid's demand; a report with 24 hours on a 23-hour day. Out: a posting that is only late; a license
ruling; a publisher that is paused; a fault of the ERW's own code (those are fixed and tested, not listed).

## The register

`warehouse/faults/faults.yaml`, one entry per fault, written by a person or a session:

| Field | Holds |
|---|---|
| `id`, `title` | a short name and one line |
| `publisher`, `source` | who publishes it, and the source report in the ERW's registry |
| `first`, `last`, `dates_note` | the dates as recorded; `last` empty when it continues; the note says what is known when a day is not recorded |
| `status` | `screened` (left out by a stated rule), `corrected` (read as it should have been, by a stated rule), `worked_around` (another source is read for the period), `held_as_published` |
| `evidence` | what was measured, with its numbers |
| `tables` | every ERW table it touches |
| `erw_does` | what the ERW does about it, and where the rule is |
| `open` | what is not settled |
| `recorded_in` | the session report or method note that holds the measurement |

**Nothing is estimated.** Every figure in `evidence` is one a session measured and wrote down, or one the screening
rule measured on 2026-10-04 (`docs/methods/impossible_hours.md`). A date that is not recorded is left empty and said
to be so.

## The table

`warehouse/derived/data_faults.py` checks the register and writes it as a table in the events shape, one row per
fault. It computes nothing and requests nothing. The build fails when an entry lacks a field, names a table that is not
in the warehouse or a source that is not in the registry, or gives a date that is not one.

| Column | Holds |
|---|---|
| `event_id` | `data_fault:<id>` |
| `event_date` | the first day of the fault where a day is recorded; where none is, the day the register recorded it (`x_first` is then empty) |
| `event_type` | `data_fault` |
| `parties` | the publisher |
| `entity_ids` | the tables it touches, separated by `;` |
| `status` | as above |
| `x_title`, `x_first`, `x_last`, `x_dates_note`, `x_publisher_source`, `x_evidence`, `x_erw_does`, `x_open`, `x_recorded_in` | the register's fields |

License: public. It is the ERW's own account of its sources; each row names the publisher and the source report.

## As built, 4 October 2026

24 faults: 8 screened, 3 corrected, 1 worked around, 12 held as published. Sixteen are in EIA's Form EIA-930 (one of
them set against EIA-860M), five in CAISO's files, one in Berkeley Lab's queue file, one in FERC's quarterly reports,
and one in ISO-NE's and NYISO's real-time price files.

Two things the register corrected in what was believed before it was written:

- **New York's zero hours are not in 2019 and 2020.** They are in 2019 (one), 2024 (three), 2025 (two) and 2026 (six).
  The reports recorded "12 hours of zero" without dates; the rule gave the dates.
- **PJM has seven impossible hours, not two.** The two the reports name (12 December 2019 and 13 July 2020) and five
  more: one in April 2020, two in July 2020, one in August 2020 and one in November 2024.

## To add a fault

An entry in the register, then `python warehouse/derived/data_faults.py --snapshot` under the data lock, the validator,
coverage, the archive and the Redivis draft, as for any table. The page reads the site's copy
(`site/data/data_faults.json`).

## Tests

`tests/test_session103.py`: the register is sound (every field, every table in coverage, every source in the
registry, the dates); the table is the register, row for row; the site's copy holds the table's rows and counts; the
page reads the copy and is in review.
