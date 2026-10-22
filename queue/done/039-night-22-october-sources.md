# Chain of the night of 22 October 2026: sessions 624 to 630, data machine (lab-desktop), unattended: more public sources

machine: data

Written by session 623, the last session of `queue/done/038-night-22-october-sources.md`, at the owner's instruction of 21 October 2026 ("write the next chain of new public sources and take it"; "if you run out of ruling-free work, probe another public source rather than idle"). Sessions 624 to 630 were free in every queue file and branch when this was written. The code machine's chain 036 holds session 607, and 608 and 609 are left for it. Each EIA route below answered EIA's metadata call on 22 October (session 623): `natural-gas/move/expc` and `natural-gas/move/impc` from 1973-01, `natural-gas/stor/cap` from 1989-01.

Each source session follows chain 038's form:

- EIA's terms are record 1 (public);
- a probe, and a trial with `--out-dir` from the main checkout, whose saved pages the write reuses (`--offline`);
- a cross-check;
- `runs/write_table.sh`, `runs/finish_table.sh`, `runs/union_resolve.py`, `runs/s622/resolve_ours_plus.py` and `runs/release_replace.py` on the data machine;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released or uploaded on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/038-night-22-october-sources.md` hold, word for word, with its lessons. One is added from chain 038:

- **When a metadata patch conflicts, read the hunks before resolving.** Two different tables' new lines: `runs/union_resolve.py`. Main's older line of a table the branch widened: `runs/s622/resolve_ours_plus.py <new table> <files>`. Then restore the release package from the branch (`git checkout HEAD -- docs/redivis docs/licenses.md warehouse/metadata/license_tables.csv`) and run `runs/finish_table.sh` again.

Read `docs/state/note_2026-10-26_night_sources_data.md` and sessions 617 to 622's reports first.

## Session 624: tanker and barge movements before 2010

Long end 1:00. Pulls: at most 25 requests.

- `eia_padd_rail_barge_movements_monthly` from tanker and barge's first month, as an early window of its own (as session 619 did for refinery capacity), the 2010 on pages reused. Probe the route's first month first.
- Cross-check: EP00 against crude plus products for the early years; the 2010 on rows unchanged.

## Session 625: natural gas exports and imports by country

Long end 1:30. Pulls: EIA's API v2, routes `natural-gas/move/expc` and `natural-gas/move/impc`, monthly, at most 30 requests.

- Volumes (`MMcf`) and prices (`USD/Mcf`) by country and point, as `eia_gas_trade_country_monthly`, from the year the ceiling allows (said in the report).
- Cross-check: the LNG export volumes against `eia_lng_exports_monthly` where both hold them; the countries against the U.S. total.

## Session 626: underground natural gas storage capacity

Long end 1:00. Pulls: EIA's API v2, route `natural-gas/stor/cap`, at most 15 requests.

- Capacity and working gas design capacity by state and the U.S. (`MMcf`), and field counts (`count`), as `eia_gas_storage_capacity_monthly` (or annual, as EIA gives it).
- Cross-check: the states against the U.S.; working gas in storage (`eia_gas_storage_state_monthly`) below working gas capacity.

## Sessions 627 and 628: EIA-930's demand by sub-region, 2023

Long end 1:30 each. Pulls: at most 90 requests each.

- `python warehouse/connectors/eia930_subba.py --year 2023`: 627 saves pages to its ceiling, 628 writes `eia930_subba_demand_hourly_2023` from both sessions' pages, as 620 and 621 did. Add the two holds.
- Cross-check: against `ferc714_area_demand_2023`, the same seven parents.

## Session 629: one more source

Long end 1:30. Pulls: at most 20 requests.

- A public source the ERW does not hold, chosen by the session (EIA's route list, or a federal publisher whose robots file and terms allow it). Say why it was chosen.

## Session 630: the note, the next file, and the queue

Long end 1:00.

1. `docs/state/note_2026-10-27_sources_data.md`, in session 364's form.
2. The next file before the queue step: at least six sessions of public sources the ERW does not yet hold, numbered from the next free numbers (631 on, checked across `queue/` and every branch at the moment of the push). Commit and push it to main on its own, with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a task/ branch, not between 14:00 and 16:15 UTC.
4. Then `python scripts/chain_queue.py next`.
