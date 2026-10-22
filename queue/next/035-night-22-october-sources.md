# Chain of the night of 21 to 22 October 2026: sessions 600 to 606, data machine (lab-desktop), unattended: more public sources

machine: data

Written by session 576, the last session of `queue/done/033-night-22-october-sources.md`, at the owner's instruction of 21 October 2026 ("write the next chain of new public sources and take it"; "if you run out of ruling-free work, probe another public source rather than idle"). Sessions 600 to 606 were free in every queue file and branch when this was written. The code machine's chain 034 holds 577 to 589, and 590 to 599 are left for it. Each route below answered EIA's metadata call on 21 October (session 576).

Each source session follows chain 033's form:

- EIA's terms are record 1 (public);
- a probe, and a trial with `--out-dir` whose saved pages the write reuses (`--offline`);
- a cross-check;
- `runs/write_table.sh`, `runs/finish_table.sh`, `runs/union_resolve.py` and `runs/release_replace.py` on the data machine;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released or uploaded on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/033-night-22-october-sources.md` hold, word for word, with its lessons. One is added from chain 033:

- **Before a queue file is pushed, check its queue number and its sessions against `queue/next`, `queue/done` and every branch at that moment** (session 561: another machine had taken 032 and 562 minutes before).

Read `docs/state/note_2026-10-25_sources_data.md` and sessions 570 to 575's reports first.

## Sessions 600 and 601: petroleum supply and disposition, the last products

Long end 1:30 each. Pulls: at most 30 requests each.

- Add the route's remaining products to `eia_petroleum_snd_monthly` as a third group (600) and, if they exceed one session's ceiling, a fourth (601), from 2015 on. Each group's request is its own, so the saved pages of the earlier groups are reused.
- Replace the table's release row after each write.
- Cross-check: the new series against `eia_product_supplied_monthly` where it holds them, and the earlier groups' rows unchanged.

## Session 602: EIA-930's demand by sub-region, hourly, the last 90 days

Long end 1:30. Pulls: EIA's API v2, route `electricity/rto/region-sub-ba-data`, hourly, at most 60 requests.

- Each sub-region's (subba) demand by hour for the last 90 whole days, as `eia930_subba_demand_hourly` (MW), with its parent balancing authority in the entity.
- EIA-930's own conventions apply as in the ERW's other EIA-930 tables: the hour's end as EIA gives it, set to the interval's start, with a check against data as session 5 did.
- Cross-check: the sub-regions summed by parent and hour against `eia930_all_demand` where the parent is one of its regions.

## Session 603: drilling activity

Long end 1:00. Pulls: EIA's API v2, route `petroleum/crd/drill`, monthly, at most 10 requests.

- Rotary rigs and wells drilled by area, as `eia_drilling_monthly`, in units the vocabulary holds (`count`).
- Cross-check: the areas sum to the U.S.

## Session 604: natural gas wells by state

Long end 1:00. Pulls: EIA's API v2, route `natural-gas/prod/wells`, annual (1989 to 2020), at most 10 requests.

- Producing gas wells by state, as `eia_gas_wells_annual` (`count`).
- Cross-check: the states sum to the U.S.

## Session 605: one more source

Long end 1:30. Pulls: at most 20 requests.

- A public source the ERW does not hold, chosen by the session (EIA's route list, or a federal publisher whose robots file and terms allow it). Say why it was chosen.

## Session 606: the note, the next file, and the queue

Long end 1:00.

1. `docs/state/note_2026-10-25_night_sources_data.md`, in session 364's form.
2. The next file before the queue step: at least six sessions of public sources the ERW does not yet hold, numbered from the next free numbers (607 on, checked across `queue/` and every branch at the moment of the push). Commit and push it to main on its own, with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a task/ branch, not between 14:00 and 16:15 UTC.
4. Then `python scripts/chain_queue.py next`.
