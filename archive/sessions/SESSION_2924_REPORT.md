# Session 2924 report: the connection rules

6 November 2026, about 05:40 to 05:46 UTC, on lab-desktop (the data machine), chain 153, unattended. Model spend USD 0. Pulls: none. Both documents were already on this machine: session 2905's fetch of ERCOT's Section 9 and session 2921's of PG&E's Rule 30.

## Read these first

- **`large_load_connection_rules` is written:** 26 rows (events, public), each a step a document states for connecting a large load, with its stated duration or date in its own words. Commit `18e56504f` on `wip/c153-data`.
  - **ERCOT Planning Guide, Section 9** (dated 11 July 2026), 22 steps. They include:
    - the 75 MW modification threshold (9.2.1(1)(b));
    - Form W by 10 July 2026 and to ERCOT by 24 July 2026 (9.2.2.1(2));
    - 2 and 3 Business Days for a classification notice and a dispute (9.3.1(2)(a)(i));
    - 7 Business Days to post security (9.3.1(2)(a)(ii));
    - the study report by 9 April 2027 (9.3.1(2)(b));
    - 90 days for the transmission plan (9.3.1(2)(d));
    - the short-circuit study 60 days before (9.3.1(3));
    - 10 Business Days for cost estimates (9.3.2(f));
    - the PCLR's capped energization, with no duration (9.6.1(1));
    - the legacy study's scoping and report steps (9.8.2, 9.9), with 180 days to cancellation and 365 days to restudy.
  - **PG&E Electric Rule No. 30** (interim, effective 4 December 2025), 4 steps: 18 months of fixed design standards, 20 business days to send the CCA a copy, 45 calendar days to pay an invoice, and a 10-year load forecast.
- **The registry:** `warehouse/sources/large_load_connection_rules/` (README, two files). **The connector:** `warehouse/connectors/large_load_connection_rules.py`; it makes no request. It refuses:
  - a duration not in the step's printed words;
  - a unit without a duration, or a unit not in its list;
  - a load size not printed;
  - a license other than public.
- **The write** (`runs/c147/write_table.sh`, under the data lock): validator PASS; coverage (sector power and datacenters, a rule added to `build_coverage.py`); archive run `20261106T054401Z-local`; sources.csv's new row.
  - The first run stopped at the coverage build (no sector rule) and put main's files back.
  - The metadata patch conflicted in sources.csv beside session 2921's row. It was resolved as the union (the new row and the branch's newer tariffs row); no marker is left, and each row is there once.
- **`docs/methods/large_load_connection_rules.md`** written. **Test** `tests/test_session2924.py`: 6 passed.
- **The siting gaps rows** "All | Time to connect | connection timelines by utility" and "ERCOT | Time to connect | the faster path for a controllable load" now have stated steps held. No step is summed into a time to connect (see the method). The faster path states no duration. Both rows stay open on the tab: no cell draws this table yet.

## Decisions made without you

- **An events table, durations in `x_` columns,** so no new unit (days, business days) was added to the standard.
- **No sum of steps into a time to connect:** the steps run in sequence, in parallel or on a condition.

## Errors

- **The resolution script first failed on the file's CRLF line ends, and `git add` then staged the file with its markers.** They were resolved in the same minute, before any commit. Nothing with a marker was committed.

## For Samuel's ruling

- None new.
