# Session 2028 report: the grid's disturbances (DOE's electric emergency incident reports, Form DOE-417)

23 October 2026, from 18:04 UTC, on lab-desktop (the data machine), the first session of `queue/done/058-day-24-october-data-outages-fuels-mines-vehicles.md`, unattended, while another agent ran chain 057 on the same machine (the owner's instruction: each chain in its own worktrees and `wip/` branches, the data lock for every warehouse write, waited for with `scripts/duty.py beat`, the build lock before every build). Model spend USD 0. Pulls: 15 requests of 15 (below).

## Read these first

- **The queue first.** `chain_queue.py next --file 058-...` took this chain's file (commit `f0919baa`), pushed to main with snapshots `s2028q-before` and `s2028q-after`. Then the next file, `queue/next/059-night-24-october-data-storms-reactor-events-lng-climate.md` (sessions 2042 to 2055, machine: data, 14 sessions; 2042 to 2055 found unused on main and on chain 056's branch), committed alone and pushed (`7356b684`, snapshots `s2028n-before` and `s2028n-after`). Both compares: 0 differences on 25 pages. Vercel answered both pushes "Deployment rate limited, retry in 24 hours", so the live site did not change and the after snapshots were taken without waiting for a deploy.
- **The branch:** `wip/2028-2041-data` in the worktree `erw-c058`, cut from chain 056's unlanded `wip/2000-2013-data` (`b9b646d6`), so this chain's `license_reads.csv` rows follow chain 056's last (174). Chain 057 is unlanded and running; if both chains add the same numbers, the later to land renumbers at the merge (the chain's rule).
- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `doe_oe417_events`, 3,313 events reported on Form DOE-417 (formerly OE-417) from 2016 to 2025: 141, 150, 220, 278, 383, 387, 390, 316, 622 and 426 a year. Each row is a report: the day and time the event began and was restored (local, as printed), the area affected, the NERC region (to 2023; the 2024 and 2025 summaries print none), the alert criteria, the event types, the demand lost (1,872 rows with a number in MW; "Unknown" kept as printed) and the customers affected.
- **The old host is gone.** `www.oe.netl.doe.gov`, where the summaries lived, no longer resolves. DOE's DOE-417 site, `doe417.pnnl.gov` (built by Pacific Northwest National Laboratory for DOE's Office of Cybersecurity, Energy Security, and Emergency Response), has no robots file: its `/robots.txt` answers with the site's own page. Its script names the files `/summaries/<year>_Annual_Summary.xlsx` from 2024 and `.xls` before, and the same names with `.pdf`.
- **A defect in DOE's 2023 summary:** its 32 August rows print no begin date, in the workbook and in the PDF beside it, and their restoration dates fall in July (the PDF's August block repeats July rows, among them Shelby County's 1,200 MW and 216,000 customers). Those 32 rows are left out and counted in the table's header; none is given a day.
- **The cross-check** against the summaries DOE prints: the 2024 and 2025 workbooks print their own totals ("End of report - 622 total incident(s) for 2024", 426 for 2025), and the connector stops unless the rows read match them (they do). The 2023 PDF prints 348 rows that begin with a month: 316 in the table and the 32 left out, the same in every month. The six largest 2023 events by demand lost (Michigan 6,200 MW on 22 February, Michigan 5,800 MW on 25 March, Iowa and Minnesota 2,200 MW on 24 May, Gallia County 2,000 MW, Indiana County 1,711 MW, Shelby County 1,200 MW) are each in the PDF's row for that day with the same figure.
- **A figure to read with care, kept as printed:** 2024's two reports of 26 March (Hanover County, Virginia, and Virginia; Weather or natural disaster) each print a demand loss of 160,000 MW and 50,000 customers, several times Virginia's peak load; the summary prints them so, and the table keeps them. Each other year's largest lies between 4,500 MW (2017, Florida, Severe Weather) and 133,200 MW (2019, the Carolinas, Severe Weather).

## The pulls

1. `www.oe.netl.doe.gov/robots.txt`: no answer (the name does not resolve).
2. `www.energy.gov/robots.txt`: disallows only site machinery, admin and search paths.
3. `doe417.pnnl.gov/robots.txt`: no robots file (the site's page, HTML).
4. The site's script, `/assets/index-DByRIFD9.js`, read for the summaries' addresses.
5. to 14. The connector's trial: the ten yearly summaries, 2016 to 2025, saved in `warehouse/raw/doe_oe417/` and reused by the write (`--offline`).
15. The 2023 PDF summary, for the cross-check.

The three robots requests are reads 175 to 177 of `license_reads.csv`. The terms are DOE's (read 54: "Government information at DOE websites is in the public domain").

## Decisions made without you

- **`scripts/duty.py on` does not exist;** the prompt's step was run as `duty.py start --what "chain 058"`, and the precheck then marked the machine on duty for session 2028.
- **The branch cut from chain 056's,** not main, so the reads follow 174 (above).
- **Ten years, 2016 to 2025,** the most the ceiling allowed beside the robots files and the cross-check's PDF; the site offers 2000 to 2025. A later run can take the earlier years in one request each.
- **2023's August rows left out,** not dated by the month or the restoration day.
- **`event_type` is the first type a row lists.** From 2023 a row can list several ("Physical attack; Vandalism; Other"); all are in `x_event_types`, in order, and the words in `x_event_type_as_published`. The form's label for its comment box ("Additional Information/Comments (limit 250 characters):"), which the 2024 and 2025 summaries print among the types without any comment, is left out of `x_event_types`. The older years' combined names ("Severe Weather - Transmission Interruption") are kept as one type, as printed.
- **An event id is the row's place in its year's summary,** the rows left out counted, so an id does not shift when a row is left out.
- **A write script of this chain's own,** `runs/c058/write_table.sh` (on the data machine, from `runs/c045/write_table.sh`): it waits for the data lock a minute at a time with a duty beat between, and releases the lock only after the main checkout's metadata files are diffed and put back, so the other chain's write cannot land in this chain's patch.
- **Chain 059's sources** were chosen by this session among public ones the ERW does not hold (NOAA's Storm Events, the NRC's event notifications, DOE's LNG export authorizations, NOAA's Climate at a Glance, Oak Ridge's Transportation Energy Data Book, the SEC's XBRL frames for utilities' capital spending, DOE's grid resilience grants); a source chain 057 or 058 takes first is replaced by the session that meets it.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/doe_oe417.py`, `tests/test_session2028.py` (4 tests), this report; on main, `queue/next/059-night-24-october-data-storms-reactor-events-lng-climate.md`.
- Changed: `build_coverage.py` (the sector rule), `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_reads.csv` (175 to 177), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c058/` (the write script, the register and reads helpers, `s2028/`: the probe, the trial, the cross-check), `runs/license_reads/s2028/`, `runs/s2028*`, `warehouse/raw/doe_oe417/`.
