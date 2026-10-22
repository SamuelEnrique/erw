# Chain of the night of 22 October 2026: sessions 631 to 637, data machine (lab-desktop), unattended: more public sources

machine: data

Written by session 630, the last session of `queue/done/039-night-22-october-sources.md`, at the owner's instruction of 21 October 2026 ("write the next chain of new public sources and take it"; "if you run out of ruling-free work, probe another public source rather than idle"). Sessions 631 to 637 were free in every queue file and branch when this was written. The code machine's chain 036 holds session 607, and 608 and 609 are left for it. Session 629 probed `petroleum/pnp/oxy` (24 records a month, the U.S. and the PADDs).

Each source session follows chain 039's form:

- EIA's terms are record 1 (public);
- a probe, and a trial with `--out-dir` from the main checkout, whose saved pages the write reuses (`--offline`);
- a cross-check;
- `runs/write_table.sh`, `runs/finish_table.sh`, `runs/union_resolve.py`, `runs/s622/resolve_ours_plus.py` and `runs/release_replace.py` on the data machine;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released or uploaded on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/039-night-22-october-sources.md` hold, word for word, with its lessons. None is added from chain 039.

Read `docs/state/note_2026-10-27_sources_data.md` and sessions 624 to 629's reports first.

## Session 631: oxygenate plant production

Long end 1:00. Pulls: EIA's API v2, route `petroleum/pnp/oxy`, monthly, its whole history if the ceiling allows, at most 10 requests.

- Oxygenate plant production (fuel ethanol, MTBE and others) by PADD, as `eia_oxygenate_production_monthly` (`kbbl`, `kbbl/d`), made from session 618's connector.
- Cross-check: the PADDs against the U.S.; fuel ethanol against `eia_petroleum_snd_monthly`'s renewable plant production where both hold it.

## Session 632: crude oil imports by origin and destination

Long end 1:30. Pulls: EIA's API v2, route `crude-oil-imports`, monthly, at most 40 requests.

- Probe the route's facets and count first. Imports by country of origin, port and destination, and crude grade, as `eia_crude_imports_detail_monthly` (`kbbl`), from the year the ceiling allows (said in the report). A field the vocabulary cannot hold (API gravity, sulfur) is left out and named.
- Cross-check: the countries summed by month against `eia_crude_imports_by_country` where both hold them.

## Sessions 633 and 634: EIA-930's demand by sub-region, 2022

Long end 1:30 each. Pulls: at most 90 requests each.

- `python warehouse/connectors/eia930_subba.py --year 2022`: 633 saves pages to its ceiling, 634 writes `eia930_subba_demand_hourly_2022` from both sessions' pages. Add the two holds.
- Cross-check: against `ferc714_area_demand_2022`, the same seven parents.

## Session 635: refinery inputs and production before 2015

Long end 1:30. Pulls: at most 40 requests.

- `eia_refinery_inputs_monthly` and `eia_refinery_production_monthly` from 2005, each as an early window of its own (as sessions 619 and 624 did), the 2015 on pages reused. If the ceiling does not allow both, the inputs first.
- Cross-check: the PADDs against the U.S. for the early years; the 2015 on rows unchanged.

## Session 636: one more source

Long end 1:30. Pulls: at most 20 requests.

- A public source the ERW does not hold, chosen by the session (EIA's route list, or a federal publisher whose robots file and terms allow it). Say why it was chosen.

## Session 637: the note, the next file, and the queue

Long end 1:00.

1. `docs/state/note_2026-10-27_night_sources_data.md`, in session 364's form.
2. The next file before the queue step: at least six sessions of public sources the ERW does not yet hold, numbered from the next free numbers (638 on, checked across `queue/` and every branch at the moment of the push). Commit and push it to main on its own, with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a task/ branch, not between 14:00 and 16:15 UTC.
4. Then `python scripts/chain_queue.py next`.
