# Chain of the morning of 22 October 2026: sessions 638 to 644, data machine (lab-desktop), unattended: more public sources

machine: data

Written by session 637, the last session of `queue/done/040-night-22-october-sources.md`, at the owner's instruction of 21 October 2026 ("write the next chain of new public sources and take it"; "if you run out of ruling-free work, probe another public source rather than idle"). Sessions 638 to 644 were free in every queue file and branch when this was written. The code machine's chain 036 holds session 607, and 608 and 609 are left for it. Session 635 counted `petroleum/pnp/refp`'s 2005 to 2014 window at 151,406 records.

Each source session follows chain 040's form:

- EIA's terms are record 1 (public);
- a probe, and a trial with `--out-dir` from the main checkout, whose saved pages the write reuses (`--offline`);
- a cross-check;
- `runs/write_table.sh`, `runs/finish_table.sh`, `runs/union_resolve.py`, `runs/s622/resolve_ours_plus.py` and `runs/release_replace.py` on the data machine;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released or uploaded on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/040-night-22-october-sources.md` hold, word for word, with its lessons. One is added from chain 040:

- **When EIA answers with errors and a run stops, the saved pages stay.** The next run, in the same session if its ceiling allows or in a later one, asks only for the missing pages. Never ask again for a page that is saved.

Read `docs/state/note_2026-10-27_night_sources_data.md` and sessions 631 to 636's reports first.

## Session 638: refinery production before 2015

Long end 1:30. Pulls: at most 40 requests.

- `python warehouse/connectors/eia_refinery_production.py --from 2005-01` (the early window session 635 added; 31 pages), the 2015 on pages reused.
- Cross-check: the PADDs against the U.S. and the districts against their PADD for the early years; the 2015 on rows unchanged.

## Session 639: the early years of crude imports and of natural gas liquids

Long end 1:30. Pulls: at most 25 requests.

- `eia_crude_imports_detail_monthly` from 2009-01 as an early window of its own (2009 and 2010, about 22,000 records), the 2011 on pages reused.
- `eia_ngl_production_monthly` before 2015 as an early window of its own, from the year the ceiling allows (said in the report).
- Cross-checks as sessions 636 and 629 did, for the early years; the later rows unchanged.

## Sessions 640 and 641: EIA-930's demand by sub-region, 2021

Long end 1:30 each. Pulls: at most 90 requests each.

- `python warehouse/connectors/eia930_subba.py --year 2021`: 640 saves pages to its ceiling, 641 writes `eia930_subba_demand_hourly_2021` from both sessions' pages. Add the two holds.
- Cross-check: against `ferc714_area_demand_2021`, the same seven parents.

## Sessions 642 and 643: two more sources

Long end 1:30 each. Pulls: at most 20 requests each.

- A public source the ERW does not hold, chosen by each session (EIA's route list, or a federal publisher whose robots file and terms allow it). Say why it was chosen.

## Session 644: the note, the next file, and the queue

Long end 1:00.

1. `docs/state/note_2026-10-28_sources_data.md`, in session 364's form.
2. The next file before the queue step: at least six sessions of public sources the ERW does not yet hold, numbered from the next free numbers (645 on, checked across `queue/` and every branch at the moment of the push). Commit and push it to main on its own, with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a task/ branch, not between 14:00 and 16:15 UTC.
4. Then `python scripts/chain_queue.py next`.
