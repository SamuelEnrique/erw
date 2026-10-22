# Chain of the night of 22 October 2026: sessions 617 to 623, data machine (lab-desktop), unattended: more public sources

machine: data

Written by session 616, the last session of `queue/done/037-night-22-october-sources.md`, at the owner's instruction of 21 October 2026 ("write the next chain of new public sources and take it"; "if you run out of ruling-free work, probe another public source rather than idle"). Sessions 617 to 623 were free in every queue file and branch when this was written. The code machine's chain 036 holds session 607, and 608 and 609 are left for it. Each EIA route below answered EIA's data call on 22 October (session 616): `petroleum/pnp/refp` holds 182,999 records from 2015, `petroleum/pnp/cap1` 11,756 for 1982 to 1994.

Each source session follows chain 037's form:

- EIA's terms are record 1 (public); BOEM's are record 86;
- a probe, and a trial with `--out-dir` whose saved pages the write reuses (`--offline`);
- a cross-check;
- `runs/write_table.sh`, `runs/finish_table.sh`, `runs/union_resolve.py` and `runs/release_replace.py` on the data machine;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released or uploaded on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/037-night-22-october-sources.md` hold, word for word, with its lessons. One is added from chain 037:

- **A trial runs from the main checkout, never from the worktree.** Copy the branch's connector into `C:\Users\Shared\Documents\erw\warehouse\connectors\` and run it there, then put main's back (`git checkout --` for a tracked file, else remove it). Run from the worktree, a connector finds no saved pages and no `.env`. Session 610 did that and broke its ceiling (29 of 15).

Read `docs/state/note_2026-10-26_sources_data.md` and sessions 610 to 615's reports first.

## Session 617: petroleum supply and disposition, the fifth group

Long end 1:00. Pulls: at most 15 requests.

- Pull `GROUPS[4]` of `warehouse/connectors/eia_petroleum_snd.py`, the eleven small products, into `eia_petroleum_snd_monthly`, from 2015. The first four groups' saved pages are reused: run from the main checkout.
- Replace the table's release row.
- Cross-check: the first four groups' rows unchanged, and the new series against `eia_product_supplied_monthly` where it holds them.

## Session 618: refinery and blender net production by district, a month

Long end 1:30. Pulls: EIA's API v2, route `petroleum/pnp/refp`, monthly, from 2015, at most 40 requests.

- Net production by product and area (the U.S., PADDs and refining districts), as `eia_refinery_production_monthly` (`kbbl` and `kbbl/d`), made from session 615's `eia_refinery_inputs.py`.
- Cross-check: the PADDs against the U.S. and the districts against their PADD (areas from EIA's codes in the saved pages), and the U.S. and PADD series against `eia_petroleum_snd_monthly`'s `refinery_net_production`.

## Session 619: refinery capacity's early years, and BOEM's lease production from 1996

Long end 1:30. Pulls: at most 5 requests to api.eia.gov and 22 to www.data.boem.gov (its robots file read again first).

- `eia_refinery_capacity_annual` from 1982 (`--from 1982`, the 1995 on pages reused; the table is replaced, its release row too).
- `boem_ogor_lease_production_monthly` from 1996 (`--from 1996`, the 2015 on files reused: one run of more than 15 files needs the connector's ceiling raised for it, said in the report).
- Cross-checks: the PADDs against the U.S. for the early years; BOEM against EIA's Federal Gulf for 1996 to 2014.

## Sessions 620 and 621: EIA-930's demand by sub-region, 2024

Long end 1:30 each. Pulls: EIA's API v2, route `electricity/rto/region-sub-ba-data`, at most 90 requests each.

- `python warehouse/connectors/eia930_subba.py --year 2024`: 620 saves pages to its ceiling, 621 writes `eia930_subba_demand_hourly_2024` from both sessions' pages, as 612 and 613 did for 2025. A sector rule exists (`^eia930_subba_demand_hourly_\d{4}$`); the two holds are added.
- Cross-check: against `ferc714_area_demand_2024` as session 613 did, the same seven parents.

## Session 622: one more source

Long end 1:30. Pulls: at most 20 requests.

- A public source the ERW does not hold, chosen by the session (EIA's route list, or a federal publisher whose robots file and terms allow it). Say why it was chosen.

## Session 623: the note, the next file, and the queue

Long end 1:00.

1. `docs/state/note_2026-10-26_night_sources_data.md`, in session 364's form.
2. The next file before the queue step: at least six sessions of public sources the ERW does not yet hold, numbered from the next free numbers (624 on, checked across `queue/` and every branch at the moment of the push). Commit and push it to main on its own, with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a task/ branch, not between 14:00 and 16:15 UTC.
4. Then `python scripts/chain_queue.py next`.
