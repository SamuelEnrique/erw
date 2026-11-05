# Chain of 24 October 2026: sessions 684 to 699, data machine (lab-desktop), unattended: chain 041's end, the Stanford draft whole, the EIA-861 faults, the siting gaps' second try

machine: data

Written by session 683, the last session of `queue/done/043-night-23-october-data-redivis-gaps.md`, at the owner's instruction for that chain ("write the next file before the queue step, at least fifteen sessions, machine: data"). Sessions 684 to 699 were free in every queue file and branch when this was written; a data chain that needs more numbers skips 700 to 849 (the code machine and the laptop) and goes on from 850. Model: Opus 5.5, high effort.

Read first: `docs/state/note_2026-10-24_data.md` (chain 043's note), sessions 660 to 683's reports, `docs/reviews/redivis-v1-release-note-2026-10-23.md`, `docs/reviews/siting-sources-2026-10-23.md`, `docs/reviews/siting-gaps.md` if the code machine has landed it, and chain 041's reports on `wip/638-644-sources` (sessions 638 to 640).

## Rules for every session

The rules of `queue/done/043-night-23-october-data-redivis-gaps.md` hold, word for word, with chain 040's and 041's lessons. Added from chain 043:

- **Per-table metadata patches conflict when two new tables land in one chain.** Write the tables first, then one combined `build_coverage.py --only` and archive for all of them, and one patch to the branch (`runs/c043/write_new_tables.sh` is the model). A derived table's `Derived from:` line holds table names only, and its run line starts `Retrieved:`.
- **Redivis's uploads are counted, request by request** (`runs/s661/counted.py`): `upload.py --target stanford --prove-by-listing` costs about 5 requests a table; the client's own wait costs about 13.
- **A heredoc with backslashes or apostrophes fails on this machine**: write the script with the Write tool and run the file.
- **The main checkout's files are put back after every run** that needed the branch's copies (the uploader, the validator, `coverage.csv`, `docs/licenses.md`), and `git status` in the main checkout is read before the session ends.

## Session 684: chain 041's session 641

Long end 1:30. Pulls: EIA's API v2, at most 90 requests. `python warehouse/connectors/eia930_subba.py --year 2021` from the main checkout with chain 041's connector (`wip/638-644-sources`), its saved pages reused (January to July were saved by session 640): the rest of 2021, then `eia930_subba_demand_hourly_2021` written, validated and archived. Cross-check against `ferc714_area_demand_2021`, the same seven parents. The holds as session 640 set them.

## Session 685: chain 041's sessions 642 and 643, one source

Long end 1:30. Pulls: at most 20 requests. A public source the ERW does not hold, chosen by the session (EIA's route list, or a federal publisher whose robots file and terms allow it), in chain 040's form; say why it was chosen.

## Session 686: chain 041 landed

Long end 1:30. Pulls: none. Chain 041's note (`docs/state/note_2026-10-28_sources_data.md`, sessions 638 to 641 and 685), then `wip/638-644-sources` merged with origin/main (chain 043 landed before it), the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch; not between 14:00 and 16:15 UTC.

## Session 687: the Stanford draft's metadata, refreshed

Long end 1:00. Pulls: Redivis's API only, at most 60 requests. `python warehouse/redivis/upload.py --target stanford --prove-by-listing grid_peak_vs_capacity` (a plain upload sends `erw_headers`, `erw_coverage` and `erw_sources` after the table), then `--reconcile`: every row `match`. The release note's state updated. Nothing released.

## Session 688: the package's whole remote test

Long end 1:30. Pulls: Redivis's API only, at most 100 requests. `ERW_REMOTE_TESTS=1 python -m pytest package/tests/test_backends_stanford.py -v -m remote` (11 tests, through the export read while streams are refused). A failure is fixed in the package with its test, or written down with its cause.

## Session 689: EIA-861M's aggregates

Long end 1:30. Pulls: none (the saved files). `eia861m_sales.py` leaves out EIA's aggregates by number (0, 88888, 99999) as well as by name, so the 2017 to 2021 rows of "Adjustment <year>" and "Total EPM" (9,360 a year each, session 674's note) leave the table: a trial with `--out-dir` from the saved files, the cross-check of the U.S. totals against EIA's own, then the table rewritten under the lock and archived. Unless the owner has ruled otherwise in the meantime.

## Session 690: EIA-861's empty provenance rows

Long end 1:00. Pulls: none. The 111 rows of `eia861_utility_sales` (`eia861:19784:WA:A:BPAT`, `eia861:40355:AZ:A:AZPS`, 2015 to 2025) with an empty `source_url` and empty `x_*` fields: traced to the run that wrote them, fixed from the saved zips, the header's "Years held" line made true. A test.

## Session 691: HIFLD's successor, probed

Long end 1:30. Pulls: at most 12 requests, two a host. EIA's U.S. Energy Atlas (`atlas.eia.gov`, its robots file and EIA's terms, record 1), and one other federal host that republishes HIFLD's electric layers if the Atlas does not: for substations and transmission lines, the layer, its license line, its size and its fields. `docs/reviews/siting-sources-2026-10-24.md`. No table.

## Sessions 692 and 693: transmission lines, substations

Long end 2:00 each. Pulls: at most 10 requests each, only if session 691's verdict allows. Each as chain 043's sessions 669 and 668 described (`hifld_transmission_lines`, `hifld_substations`; if the publisher is EIA, the names stay so that the code machine's session 718 finds them), validated, a cross-check, the sector rule, the holds, tests, registered. A refusal: the session writes what it found and probes nothing else.

## Session 694: large-load tariffs

Long end 2:30. Pulls: OpenEI, at most 400 requests, only if `OPENEI_API_KEY` is in `.env`. `warehouse/connectors/openei_large_load_tariffs.py` (session 670), first as a trial read against three utilities' own rate pages saved by the large-load rules' sessions, then the write. With no key: a public source the ERW does not hold, as session 685.

## Session 695: reserve margins

Long end 1:30. Pulls: NERC, at most 5 requests, only if the owner has recorded a reading of NERC's terms (`license_reads.csv` or `license_verdicts.csv`). Otherwise a public source the ERW does not hold, as session 685.

## Session 696: method notes for the older tables

Long end 1:30. Pulls: none. The 14 tables first written before 21 October that no note names (session 674's plan lists them: `battery_sourced_ranges`, `rrc_lease_production_monthly`, seven EIA petroleum and gas tables of September, and others), a note each in the form of sessions 674 to 678, with the `Tables:` line; the coverage page's Method column follows.

## Sessions 697 and 698: EIA-930's demand by sub-region, 2020

Long end 1:30 each. Pulls: at most 90 requests each. `python warehouse/connectors/eia930_subba.py --year 2020`: 697 saves pages to its ceiling, 698 writes `eia930_subba_demand_hourly_2020` from both sessions' pages. The two holds. Cross-check against `ferc714_area_demand_2020`.

## Session 699: the note, the next file, the landing and the queue

Long end 1:00. `docs/state/note_2026-10-25_data.md` in session 683's form. `python scripts/chain_queue.py list`: if nothing waits for this machine, the next file (at least fifteen sessions, machine: data, numbered from 850), pushed to main on its own with snapshots. Land this chain (merge origin/main, the whole suite, `scripts/freeze.py status`, rule 8's snapshots, a `task/` branch, not between 14:00 and 16:15 UTC). Then `python scripts/chain_queue.py next`.
