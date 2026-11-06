# Chain of the night of 23 October 2026: sessions 881 to 894, data machine (lab-desktop), unattended: EIA-861's remaining utility files, the petroleum products' exports, plants' generators, the licenses' third round

machine: data

Written by session 867, the first session of `queue/done/047-night-23-october-data-utilities-plants.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). Sessions 881 to 894 were free in every queue file and branch when this was written (the code machine holds 700 to 749, the laptop 800 to 849, the old laptop 1000 on). Session 879 of chain 047 updated it at chain 047's end (23 October, about 04:05 UTC): session 892 first mends the Stanford draft's empty `ercot_wind_solar_hsl_hourly`; session 885 takes EIA-860's other schedules from the zip session 873 saved; a rule on Redivis caps. Model: Opus 5.5, high effort.

Each source session follows chain 040's form:

- the publisher's robots file asked alone and read before any other path of its host, and its terms (EIA's are record 1, public);
- a probe, and a trial with `--out-dir` from the main checkout, whose saved pages the write reuses (`--offline`);
- a cross-check;
- `runs/c045/write_table.sh`, `runs/c045/finish_table.sh` (or `finish_replace.sh`), `runs/c046/write_derived_pair.sh`, `runs/s622/resolve_ours_plus.py`, `runs/c046/take_theirs.py`, `runs/c045/keep_newest_row.py` and `runs/c045/method_cells.sh` on the data machine, each given the chain's worktree (`WT=`, `WTN=`);
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/047-night-23-october-data-utilities-plants.md` hold, word for word, with chain 046's lessons:

- **ERCOT's robots file disallows `/misapp` and `/misdownload`**: no session asks either path until the owner rules.
- **A new read of a publisher already in `license_reads.csv` gets a label of its own** (one row a publisher, `test_session205`; session 866).
- **A table that a page reads is never rewritten to add rows from another file**: a new file of the same form is a table of its own (session 853).
- **A request cap on the Redivis uploader stops between tables, never inside one**: the true replace deletes the draft's table first (session 880 left `ercot_wind_solar_hsl_hourly` empty that way). Budget whole tables: about 5 requests a table with `--prove-by-listing --tables`, about 15 for the header merge, about 57 for a plain upload.
- **Session 881 begins by writing `queue/next/049-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from 895), commits it alone and pushes it to main before any other work; session 894 updates it.

Read first: `docs/state/note_2026-10-27_data.md` (chain 047's note), sessions 867 to 880's reports, `docs/state/note_2026-10-26_data.md`, `docs/reviews/siting-gaps.md`.

## Session 881: each utility's energy efficiency (EIA-861 Energy_Efficiency)

Long end 1:30. Pulls: none (the saved EIA-861 zips). `Energy_Efficiency_<year>.xlsx` of every saved year, by utility, state and sector, a series table, beside `eia_energy_efficiency_state_annual`; cross-check: the utilities summed by state against that table.

## Session 882: each utility's operations (EIA-861 Operational_Data)

Long end 1:30. Pulls: none. `Operational_Data_<year>.xlsx`: each utility's summer and winter peak demand, its sources and dispositions of energy and its revenue by kind, a series table; cross-check: the utilities' retail sales against `eia861_utility_sales`' totals for the same utility and year.

## Session 883: distribution systems and dynamic pricing's other files

Long end 1:30. Pulls: none. `Distribution_Systems_<year>.xlsx` (distribution circuits, voltage optimization) and, if chain 047's session 868 did not take it, `Dynamic_Pricing_<year>.xlsx`, by utility.

## Session 884: the petroleum products' exports by destination

Long end 1:30. Pulls: EIA's API v2, route `petroleum/move/expc`, at most 20 requests. The products session 860 left out (distillate, finished gasoline, jet fuel, propane, residual fuel, ethane, petroleum coke), from 2015, as many as the ceiling allows, into `eia_petroleum_exports_by_destination` only if no page reads it, else a table of its own; cross-check: the products against EPP0's total.

## Session 885: EIA-860's other schedules

Long end 1:30. Pulls: none (session 873 saved `eia8602025.zip` under `warehouse/raw/eia860_plants/`). EIA-860M's tables already hold the generators; take the schedules they do not: the owners of jointly owned generators (`4___Owner`), and the energy storage, solar and wind details (`3_4_Energy_Storage`, `3_3_Solar`, `3_2_Wind`), each as a table of its own; cross-check each against `eia860m_operating_generators` by plant and generator.

## Sessions 886 and 887: EIA's international electricity, the U.S. and its neighbors

Long end 1:30 each. Pulls: EIA's API v2, route `international`, at most 20 requests each. Electricity generation, capacity and trade of Canada and Mexico (the U.S.'s interconnected neighbors), annual, as one series table.

## Session 888: the licenses' third round

Long end 1:30. Pulls: at most 20 requests, two a host. The publishers chains 046 and 047 did not reach (the state commissions' other pages where a link on a page already read names one; FERC only if its host answers without a challenge).

## Sessions 889 and 890: two more sources

Long end 1:30 each. Pulls: at most 20 requests each. A public source the ERW does not hold, chosen by each session; say why.

## Session 891: method notes for this chain's tables

Long end 1:00. Pulls: none.

## Session 892: the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 100 requests. First `ercot_wind_solar_hsl_hourly` (left empty in the draft by session 880); then this chain's public tables, uploaded with the true replace and the proof, in whole tables under the cap; then, if requests remain, the four remote tests session 864 fixed; `--reconcile`; the release note extended. Nothing released.

## Session 893: seven days of the data jobs

Long end 1:00. Pulls: GitHub's API, at most 30 requests (with this machine's token for reads). As chain 043's session 682: each data job's last seven days, each failure with its step and first error line; a fault of this repository's code fixed with its test.

## Session 894: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_2026-10-28_data.md`, in session 683's form.
2. `queue/next/049-*.md` (written by session 881) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC.
4. Then `python scripts/chain_queue.py next`.
