# Chain of the night of 22 October 2026: sessions 610 to 616, data machine (lab-desktop), unattended: more public sources

machine: data

Written by session 606, the last session of `queue/done/035-night-22-october-sources.md`, at the owner's instruction of 21 October 2026 ("write the next chain of new public sources and take it"; "if you run out of ruling-free work, probe another public source rather than idle"). Sessions 610 to 616 were free in every queue file and branch when this was written. The code machine's chain 036 holds session 607, and 608 and 609 are left for it. Each EIA route below answered EIA's metadata call on 22 October (session 606).

Each source session follows chain 035's form:

- EIA's terms are record 1 (public); BOEM's are record 86;
- a probe, and a trial with `--out-dir` whose saved pages the write reuses (`--offline`);
- a cross-check;
- `runs/write_table.sh`, `runs/finish_table.sh`, `runs/union_resolve.py` and `runs/release_replace.py` on the data machine;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released or uploaded on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/035-night-22-october-sources.md` hold, word for word, with its lessons. None is added from chain 035.

Read `docs/state/note_2026-10-25_night_sources_data.md` and sessions 600 to 605's reports first.

## Session 610: petroleum supply and disposition, the last eleven products

Long end 1:00. Pulls: at most 15 requests.

- Add the eleven products session 601 named (special naphthas, naphtha for petrochemical feedstock, residual fuel above 1% and below 0.31% sulfur, isobutylene, ethylene, aviation gasoline blending components, other hydrocarbons, hydrogen, catalyst coke, still gas) to `eia_petroleum_snd_monthly` as a fifth group, from 2015 on. The earlier groups' saved pages are reused.
- Replace the table's release row.
- Cross-check: the earlier groups' rows unchanged, and the new series against `eia_product_supplied_monthly` where it holds them.

## Session 611: BOEM's offshore production by lease (OGOR-B)

Long end 1:30. Pulls: at most 25 requests to `www.data.boem.gov`, the robots file read again first.

- Read BOEM's field layout and disposition code documents first (the PDFs the OGOR-B page links). Write down which codes are production and which are dispositions of it, quoting BOEM's words.
- If BOEM's documents say which codes make a lease's oil and gas production, write `boem_ogor_lease_production_monthly` (oil in `kbbl`, gas in `MMcf`, by lease and month, the years the session's pulls allow, newest first). If they do not say it plainly, write nothing and report the question for Samuel.
- Cross-check: the leases summed by month against EIA's Federal Offshore Gulf production (the Federal Offshore Gulf areas `eia_crude_production_state` and `eia_gas_production_state` hold, named in the report).

## Sessions 612 and 613: EIA-930's demand by sub-region, 2025

Long end 1:30 each. Pulls: EIA's API v2, route `electricity/rto/region-sub-ba-data`, hourly, at most 90 requests each.

- 2025's hours, January to June (612) and July to December (613), as one yearly table `eia930_subba_demand_hourly_2025`, written once after 613 (612 saves its pages, and 613 writes from both sessions' pages with `--offline`). If 612's pages already cover the year, 613 writes.
- Session 602's conventions hold: the hour's end set to the interval's start, missing hours counted in the header and never filled.
- Cross-check: the sub-regions summed by parent and hour against `eia930_all_demand`'s 2025 rows where it holds them.

## Session 614: refinery capacity

Long end 1:00. Pulls: EIA's API v2, route `petroleum/pnp/cap1`, annual (1982 to 2026), at most 15 requests.

- Operable capacity by area and process (atmospheric distillation and downstream units), as `eia_refinery_capacity_annual`, in units the vocabulary holds (`kbbl/d`, or the stream day unit as EIA gives it, named in the variable).
- Cross-check: the PADDs sum to the U.S., and January's U.S. operable capacity against `eia_refinery_weekly`'s operable capacity in that year's first weeks.

## Session 615: refinery inputs, monthly

Long end 1:30. Pulls: EIA's API v2, route `petroleum/pnp/inpt`, monthly, from 2015, at most 30 requests.

- Refinery and blender net inputs by product and area (the U.S., PADDs and refining districts), as `eia_refinery_inputs_monthly` (`kbbl` or `kbbl/d` as EIA gives them).
- Cross-check: the PADDs sum to the U.S., and the monthly crude input against the monthly mean of `eia_refinery_weekly`'s weekly crude input.

## Session 616: the note, the next file, and the queue

Long end 1:00.

1. `docs/state/note_2026-10-26_sources_data.md`, in session 364's form.
2. The next file before the queue step: at least six sessions of public sources the ERW does not yet hold, numbered from the next free numbers (617 on, checked across `queue/` and every branch at the moment of the push). Commit and push it to main on its own, with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a task/ branch, not between 14:00 and 16:15 UTC.
4. Then `python scripts/chain_queue.py next`.
