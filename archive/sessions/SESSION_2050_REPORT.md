# Session 2050 report: the grid's resilience grants (DOE's GRIP selections)

23 October 2026, from 19:07 UTC, on lab-desktop (the data machine), the ninth session of `queue/done/059-night-24-october-data-storms-reactor-events-lng-climate.md`. Model spend USD 0. Pulls: 8 requests of 20 (www.energy.gov's robots file, asked again in a call of its own and read first, unchanged since session 2044; the GRIP program page; the GRIP projects page; the formula grants page at its old address and at a guessed new one, both HTTP 404; the three program pages). The trial and the write reused the saved pages (`--offline`). The write waited for the data lock, which chain 057's session 2024 held for its Redivis upload from 19:09 UTC, and took it at 19:24 UTC.

## Read these first

- **GRIP has moved from the Grid Deployment Office to the Office of Electricity:** its `/gdo/` addresses answer at `/oe/` ones.
- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `doe_grip_selections`, the 105 projects selected in GRIP's first two rounds, as the projects page lists them ("information available as of December 2024"): the applicant or selectee, the project, the program (Smart Grid Grants 58, Grid Resilience Utility and Industry Grants 31, Grid Innovation Program 16), the round (first 58, second 47), DOE's status (awarded 60, selected 44, withdrawn 1), the states, and the federal and recipient cost shares in dollars. The federal share is USD 7,684,585,944 in all.
- **The list is read from the page's own settings:** the page draws its table by script from `drupal-settings-json` (`datatableRows`), which the page carries; no other address is asked.
- **Each project's date is its round's announcement for its program,** read from the program's page: 18 October 2023 for the first round; 6 August 2024 (Grid Innovation Program) and 18 October 2024 (the other two) for the second.
- **The State and Tribal Formula Grants were not found:** the program's page answered 404 at its Grid Deployment Office address and at the Office of Electricity address tried; no other address was guessed.

## The cross-check

Each round's federal total against the amount DOE's announcements, as the program pages print them, give:

| Round and programs | Projects | Federal share summed | DOE's figure |
|---|---|---|---|
| First, all three | 58 | USD 3.466 billion | "up to $3.46 billion ... for 58 projects" |
| Second, Grid Innovation Program | 8 | USD 2.230 billion | "a $2.2 billion investment ... for eight projects" |
| Second, the other two | 39 | USD 1.990 billion | "nearly $2 billion for 38 projects" |
| All | 105 | USD 7.68 billion | "a total of $7.6 billion in funding for 105 selected projects" |

The second round's utility grants hold 15 projects where the program page says 14, and the round 39 where it says 38: the projects page's list includes one more than the announcement, which this session did not trace.

## Errors

- **The seeding script named a redirected page only by the address asked,** so the first offline trial could not find the projects page under its `/oe/` address; `runs/c059/seed_raw.py` now lists a redirected copy under both addresses, as the raw store's own alias does.

## Decisions made without you

- **An identifier of our own** (`doe_grip:<round>:<12 hex of the SHA-1 of program, applicant and project>`): DOE gives the selections none.
- **The announcement date as the event's date,** said in the header; no award date is published.
- **No formula grants table:** two addresses tried, none guessed further.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/doe_grip.py`, `tests/test_session2050.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_reads.csv` (191), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c059/s2050/`, `runs/license_reads/s2050/`, `runs/s2050*`, `warehouse/raw/doe_grip/`.
